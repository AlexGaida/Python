"""
Attribute module for finding, creating and setting transform attributes.
"""

# import maya modules
from maya import OpenMaya as om
from maya import cmds

# import local modules
import object_utils
import transform_utils

# define global variables
__version__ = "1.0.0"


class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise TypeError("%r object does not support item assignment" % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object does not support item deletion" % type(self).__name__)

    def __getattribute__(self, attribute):
        if attribute in ('clear', 'update', 'pop', 'popitem', 'setdefault'):
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attribute))
        return dict.__getattribute__(self, attribute)

    def __hash__(self):
        return hash(tuple(sorted(self.iteritems())))

    def fromkeys(self, sequence, v):
        return type(self)(dict(self).fromkeys(sequence, v))


class Attributes(om.MDagModifier):
    MAYA_STR_OBJECT = None
    SCALE_ATTRS = ['scaleX', 'scaleY', 'scaleZ']
    DEFAULT_ATTR_VALUES = {'translateX': 0.0,
                           'translateY': 0.0,
                           'translateZ': 0.0,

                           'rotateX': 0.0,
                           'rotateY': 0.0,
                           'rotateZ': 0.0,

                           'scaleX': 1.0,
                           'scaleY': 1.0,
                           'scaleZ': 1.0,

                           'visibility': 1
                           }

    LINEAR_ATTR_TYPES = (om.MFn.kDoubleLinearAttribute,
                         om.MFn.kFloatLinearAttribute)

    INTEGER_ATTR_TYPES = (om.MFnNumericData.kShort,
                          om.MFnNumericData.kInt,
                          om.MFnNumericData.kLong,
                          om.MFnNumericData.kByte)

    DOUBLE_ATTRS_TYPES = (om.MFnNumericData.kFloat,
                          om.MFnNumericData.kDouble,
                          om.MFnNumericData.kAddr)

    def __init__(self, maya_node="", all_attrs=False, keyable=False, custom=False, connected=False):
        super(Attributes, self).__init__()
        self.MAYA_M_OBJECT = object_utils.get_m_obj(maya_node)
        self.MAYA_MFN_OBJECT = object_utils.get_mfn_obj(maya_node)
        self.OBJECT_NODE_TYPE = self.MAYA_MFN_OBJECT.typeName()
        self.MAYA_STR_OBJECT = self.MAYA_MFN_OBJECT.name()
        # self.MAYA_STR_OBJECT = maya_node
        self.attr_data = {}
        self._hash = None

        self.DEFAULT_ATTRS = self.get_attribute_list()
        self.get_attributes(all_attrs=all_attrs, keyable=keyable, custom=custom, connected=connected)

        # get only the keyable custom attributes
        if keyable and custom and self.attr_data:
            new_data = {}
            for a_name in list(set(self.attr_data) - set(self.DEFAULT_ATTRS)):
                if self.is_attr_keyable(a_name):
                    new_data[a_name] = self.attr_data[a_name]
            self.attr_data = new_data

    def get_attribute_list(self):
        try:
            return tuple(set(cmds.listAttr(self.MAYA_STR_OBJECT)) - set(cmds.listAttr(self.MAYA_STR_OBJECT, ud=True)))
        except TypeError:
            return tuple(cmds.listAttr(self.MAYA_STR_OBJECT))

    def __get_reference_attributes(self):
        """
        Gets the reference attribute of the current node type specified.
        :return: <list> node type default attributes.
        """
        attr_list = []
        mfn_obj = om.MFnDependencyNode()
        ref_obj = mfn_obj.create(self.OBJECT_NODE_TYPE)
        for a_i in range(mfn_obj.attributeCount()):
            m_attr = om.MFnAttribute(mfn_obj.attribute(a_i))
            attr_list.append(m_attr.name())
        self.deleteNode(ref_obj)
        self.doIt()
        return attr_list

    def get_connections_src(self, find_node_type=om.MFn.kTransform, with_shape=om.MFn.kLocator, custom_attr=True):
        """
        get the connection source.
        :param find_node_type:
        :return: <dict> connected atrributes.
        """
        dag_iter = om.MItDependencyGraph(
            self.MAYA_M_OBJECT,
            om.MItDependencyGraph.kDownstream,
            om.MItDependencyGraph.kPlugLevel)
        dag_iter.reset()

        # iterate the dependency graph to find what we want.
        connections = {}
        while not dag_iter.isDone():
            cur_item = dag_iter.currentItem()

            if cur_item.hasFn(find_node_type):
                cur_fn = om.MFnDependencyNode(cur_item)
                cur_name = cur_fn.name()
                connections[cur_name] = []

                if with_shape:
                    fn_item = om.MFnDagNode(cur_item)
                    c_count = fn_item.childCount()
                    if c_count:
                        if fn_item.child(0).hasFn(with_shape):
                            for a_i in range(cur_fn.attributeCount()):
                                a_obj = cur_fn.attribute(a_i)
                                m_plug = om.MPlug(cur_item, a_obj)
                                if m_plug.isConnected() and m_plug.isKeyable():
                                    if not custom_attr:
                                        connections[cur_name].append(m_plug.name())
                                    else:
                                        if m_plug.name().split('.')[-1] not in self.DEFAULT_ATTRS:
                                            connections[cur_name].append(m_plug.name())
                else:
                    for a_i in range(cur_fn.attributeCount()):
                        a_obj = cur_fn.attribute(a_i)
                        m_plug = om.MPlug(cur_item, a_obj)
                        if m_plug.isConnected():
                            connections[cur_name].append(m_plug.name())

                # remove the empty key
                if not connections[cur_name]:
                    connections.pop(cur_name)

            dag_iter.next()
        return connections

    def set_attributes(self, attribute_name="", attribute_value=0.0, open_maya=False):
        """
        set attributes for this object.
        :param attribute_name: <str> attribute name to use to set the values.
        :param attribute_value: <float> numerical value valid for the attribute name given.
        :param open_maya: <bool> set the attribute using open maya.
        :return: <bool> True for success. <bool> False for failure.
        """
        if self.is_attr_connected(attribute_name) or self.is_attr_locked(attribute_name):
            return False

        if not open_maya:
            cmds.setAttr('{}.{}'.format(self.MAYA_STR_OBJECT, attribute_name), attribute_value)

        if open_maya:
            # allow the error to happen when the plug has not been found.
            o_plug = self.MAYA_MFN_OBJECT.findPlug(attribute_name)
            o_plug_attr = o_plug.attribute()
            o_plug_type = o_plug_attr.apiType()

            # rotational attributes
            if o_plug_type == om.MFn.kDoubleAngleAttribute:
                o_plug.setMAngle(om.MAngle(float(attribute_value)))

            # unit attributes
            if o_plug_type in self.LINEAR_ATTR_TYPES:
                num_type = om.MFnUnitAttribute(o_plug_attr).unitType()

                # integers
                if num_type in self.INTEGER_ATTR_TYPES:
                    o_plug.setDouble(float(attribute_value))

                # doubles
                if num_type in self.DOUBLE_ATTRS_TYPES:
                    o_plug.setInt(int(attribute_value))

            # numeric attributes
            if o_plug_type == om.MFn.kNumericAttribute:
                num_type = om.MFnNumericAttribute(o_plug_attr).unitType()
                # om.MFnNumericAttribute(o_plug_attr).unitType()

                # booleans
                if num_type == om.MFnNumericData.kBoolean:
                    o_plug.setBool(bool(attribute_value))

                # integers
                if num_type in self.INTEGER_ATTR_TYPES:
                    o_plug.setDouble(float(attribute_value))

                # doubles
                if num_type in self.DOUBLE_ATTRS_TYPES:
                    o_plug.setInt(int(attribute_value))
        return True

    def is_attr_locked(self, attr_str):
        """
        check if attribute is locked.
        :param attr_str: <str> attribute name.
        :return: <bool> True for yes, <bool> False for no.
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.isLocked()

    def is_attr_connected(self, attr_str):
        """
        check if attribute is locked.
        :param attr_str: <str> attribute name.
        :return: <bool> True for yes, <bool> False for no.
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.isConnected()

    def is_attr_connected_to(self, attr_str, plug_array=None, as_source=False, as_dest=False):
        """
        Check if the attribute is connected to the other plugs.
        :param attr_str:
        :param as_source:
        :param plug_array:
        :param as_dest:
        :return:
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.isConnectedTo(plug_array, as_source, as_dest)

    def attr_info(self, attr_str):
        """
        grab the attribute info
        :param attr_str:
        :return:
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.info()

    def is_attr_keyable(self, attr_str):
        """
        check if attribute is locked.
        :param attr_str: <str> attribute name.
        :return: <bool> True for yes, <bool> False for no.
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.isKeyable()

    def get_attributes(self, keyable=False, custom=False, all_attrs=False, connected=False):
        """
        get attribute names for this object.
        :return: <bool> True for success. <bool> False for failure.
        """
        for i in range(self.MAYA_MFN_OBJECT.attributeCount()):
            attrib = None
            a_obj = self.MAYA_MFN_OBJECT.attribute(i)
            p_type = a_obj.apiType()
            p_type_str = a_obj.apiTypeStr()
            m_plug = om.MPlug(self.MAYA_M_OBJECT, a_obj)
            attr_name = m_plug.name().split('.')[-1]

            # get only the attributes which are specified in the keyword parameters given.
            if connected and m_plug.isConnected():
                attrib = attr_name

            if keyable and m_plug.isKeyable() and not m_plug.isLocked():
                attrib = attr_name

            if custom:
                if attr_name not in self.DEFAULT_ATTRS:
                    attrib = attr_name
                else:
                    continue

            if all_attrs:
                attrib = attr_name

            if attrib:
                # attr_value = self.get_value(plug_name=attrib, type_name=p_type_str)
                # for whatever reason, it gets attributes that do not exist, so let's not consume these
                if not cmds.ls(m_plug.name()):
                    continue
                try:
                    attr_value = self.__get_attr_value(attr_obj=a_obj, api_type=p_type, attr_plug=m_plug)
                except RuntimeError:
                    print("[Attribute] :: {}, {} is invalid.".format(attrib, p_type_str))
                    continue

                try:
                    self.attr_data[attrib] = round(attr_value, 4)
                except TypeError:
                    self.attr_data[attrib] = attr_value
        return True

    def __get_attr_value(self, attr_obj=None, api_type=None, attr_plug=None):
        """
        grabs the local attribute value.
        :param attr_obj: <OpenMaya.MFnAttribute> OpenMaya.MFnAttribute function class.
        :param api_type: <int> OpenMaya.MFn.kAttribute integer type.
        :param attr_plug: <OpenMaya.MPlug> attribute plug.
        :return: <data> attribute value.
        """
        p_value = []
        attr_node, plug_name = attr_plug.name().split('.')

        # vector compound attributes
        if api_type in (om.MFn.kAttribute3Double, om.MFn.kAttribute3Float,
                        om.MFn.kCompoundAttribute, om.MFn.kAttribute4Double):
            if attr_plug.isCompound():
                p_value = cmds.attributeQuery(plug_name, node=attr_node, listChildren=True)

        # geometry <generic> attributes
        elif api_type == om.MFn.kGenericAttribute:
            p_value = attr_plug.asDouble()

        # time attributes
        elif api_type == om.MFn.kTimeAttribute:
            p_value = attr_plug.asDouble()

        # message attributes
        elif api_type == om.MFn.kMessageAttribute:
            p_value = None

        # rotational attributes
        elif api_type == om.MFn.kDoubleAngleAttribute:
            p_value = round(attr_plug.asMAngle().asDegrees(), 3)

        # distance attribute
        elif api_type in (om.MFn.kDoubleLinearAttribute, om.MFn.kFloatLinearAttribute):
            p_value = attr_plug.asMDistance().asCentimeters()

        # angle attribute
        elif api_type in (om.MFn.kDoubleLinearAttribute, om.MFn.kFloatLinearAttribute):
            p_value = attr_plug.asDouble()

        # typed attribute
        elif api_type == om.MFn.kTypedAttribute:
            at_type = om.MFnTypedAttribute(attr_obj).attrType()

            # matrix
            if at_type == om.MFnData.kMatrix:
                # p_value = om.MFnMatrixData(attr_plug.asMObject()).matrix()
                p_value = cmds.getAttr(attr_plug.name())

            # string
            if at_type == om.MFnData.kString:
                p_value = attr_plug.asString()

        # matrix
        elif api_type == om.MFn.kMatrixAttribute:
            # p_value = om.MFnMatrixData(attr_plug.asMObject()).matrix()
            p_value = cmds.getAttr(attr_plug.name())

        # numbers
        elif api_type == om.MFn.kNumericAttribute:
            at_type = om.MFnNumericAttribute(attr_obj).unitType()

            # boolean
            if at_type == om.MFnNumericData.kBoolean:
                p_value = attr_plug.asBool()

            # integer
            if at_type in self.INTEGER_ATTR_TYPES:
                p_value = attr_plug.asInt()

            # floats
            if at_type in self.DOUBLE_ATTRS_TYPES:
                p_value = round(attr_plug.asDouble(), 3)

        # enumeration
        elif api_type == om.MFn.kEnumAttribute:
            p_value = attr_plug.asInt()
        else:
            print(attr_node, plug_name, api_type, attr_obj.apiTypeStr())
        return p_value

    def freeze(self):
        return hash(tuple((k, self.attr_data[k]) for k in sorted(self.attr_data.keys())))

    @property
    def keys(self):
        return self.attr_data.keys()

    @property
    def values(self):
        return self.attr_data.values()

    @property
    def all_attrs(self):
        return self.get_attributes(all_attrs=True)

    @property
    def keyable(self):
        return self.get_attributes(keyable=True)

    @property
    def custom(self):
        return self.get_attributes(custom=True)

    @property
    def connected(self):
        return self.get_attributes(connected=True)

    def items(self):
        return self.attr_data.items()

    def get_connected_attr(self):
        """
        iterate and find connected attributes.
        :return: <list> connected attributes.
        """
        connected = []
        for attr_name in self.keys:
            full_attr_name = '{}.{}'.format(self.MAYA_STR_OBJECT, attr_name)
            connection = cmds.listConnections(full_attr_name, s=1, d=0)
            if connection:
                connected.append(attr_name)
        return connected

    def get_default_attr(self, attr_str=""):
        """
        return default attributes.
        :return: <float> default attribute.
        """
        try:
            return self.DEFAULT_ATTR_VALUES[attr_str]
        except KeyError:
            return 0.0

    def zero_attributes(self):
        """
        find and zero out non-zero attributes.
        :return: <bool> True for success.
        """
        non_zero_attrs = self.non_zero_attributes()
        for attr in non_zero_attrs:
            default_value = self.get_default_attr(attr)
            if self.is_attr_locked(attr):
                continue
            if self.is_attr_connected(attr):
                continue
            self.set_attributes(attr, default_value)
        return True

    def set_current_value(self, attr_name=""):
        """
        set the current attribute values.
        :param attr_name: <str> attribute name to set attributes to.
        :return: <bool> True for success.
        """
        if attr_name:
            attr_value = self.__dict__()[attr_name]
            self.set_attributes(attr_name, attr_value)
        else:
            for k_name, k_val in self.__dict__().items():
                self.set_attributes(k_name, k_val)
        return True

    def set_default_attr(self, attr_name=""):
        """
        sets the default attribute value to this objects' attribute.
        :param attr_name: <str> attribute name to set attributes to.
        :return: <bool> True for success.
        """
        attr_value = self.get_default_attr(attr_name)
        self.set_attributes(attr_name, attr_value)
        return True

    def non_zero_attributes(self):
        """
        identify which values are not their default values.
        :return: <dict> dictionary of non zero values.
        """
        non_zero = {}
        for k, v in self.items():
            if k not in'visibility' and k not in self.SCALE_ATTRS and v != 0.0:
                non_zero[k] = v
            if k in self.SCALE_ATTRS and v != 1.0:
                non_zero[k] = v
            if k in 'visibility' and v != 1.0:
                non_zero[k] = v
        return non_zero

    def scale_attr(self):
        """
        return the scale attribute.
        :return: <dict> scale attributes.
        """
        scale_attrs = {}
        for k_name, k_val in self.__dict__().items():
            if 'scale' in k_name:
                scale_attrs[k_name] = k_val
        return scale_attrs

    def copy_attr(self, attr_cls, non_zero=False, match_world_space=False):
        """
        copy the non-default attributes of one attribute class to another.
        :param non_zero: <bool> match only the non-zero attributes.
        :param match_world_space: <bool> copy the transforms if worldspace positions are not the same.
        :return: <True> for success.
        """
        target_tfm = transform_utils.Transform(attr_cls.MAYA_STR_OBJECT)
        source_tfm = transform_utils.Transform(self.MAYA_STR_OBJECT)

        if match_world_space:
            if source_tfm.world_matrix_list() != target_tfm.world_matrix_list():
                cmds.xform(self.MAYA_STR_OBJECT, m=target_tfm.world_matrix_list(), ws=1)
                return target_tfm.world_matrix_list(),

        # if the world spaces match, perform the operation to copy attributes.
        else:
            if non_zero:
                attrs = attr_cls.non_zero_attributes()
            else:
                attrs = attr_cls
            for attr, val in attrs.items():
                if attr in self.__dict__():
                    if self.is_attr_connected(attr) or self.is_attr_locked(attr):
                        continue
                    self.set_attributes(attr, val)
        return True

    def match(self, attr_cls):
        """
        match the attributes from one class to the attributes to the other class.
        :param attr_cls: <Class> Attribute Class.
        :return: <dict> attributes.
        """
        answer = {}
        for attr, val in attr_cls.items():
            if attr not in self.__dict__():
                continue
            answer[attr] = val
        return answer

    def __dict__(self):
        return self.attr_data

    def __getitem__(self, key_name):
        return self.attr_data[key_name]

    def __len__(self):
        return len(self.attr_data)

    def __repr__(self):
        return ', '.join('{}: {}'.format(key, value) for key, value in self.attr_data.items())

    def __iter__(self):
        return iter(self.attr_data)

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for pair in self.iteritems():
                self._hash ^= hash(pair)
        return self._hash

    def next(self):
        try:
            return iter(self.attr_data)
        except IndexError:
            raise StopIteration
