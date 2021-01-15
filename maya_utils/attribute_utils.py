"""
    Attribute module for finding, creating and setting transform object attributes
"""

# import maya modules
from maya import OpenMaya
from maya import cmds

# import local modules
import object_utils
import transform_utils


def get_attribute_query(object_name, attribute_name):
    """
    query the attribute type of the node and attribute name in question
    :param attribute_name: <str>  attribute node name
    :param object_name: <str> object node name
    :return: <str> attribute node type name
    """
    return cmds.attributeQuery(attribute_name, node=object_name, at=True)


def get_custom_attributes(object_name="", full_name=False):
    """
    return an array of custom attributes
    :param object_name: <str> object name to pass through
    :param full_name: <bool> returns the full name of the attribute
    :return: <list> custom attributes found for this object
    """
    cnst_attr = Attributes(object_name, custom=True)
    if not full_name:
        return cnst_attr.custom.keys()
    else:
        return map(lambda x: "{}.{}".format(object_name, x), cnst_attr.custom.keys())


def get_keyable_attributes(object_name=""):
    """
    return an array of keyable attributes
    :param object_name: <str> node string name
    :return: <list> keyable attributes found for this object
    """
    cnst_attr = Attributes(object_name, keyable=True)
    return cnst_attr.keyable.keys()


def get_connected_attributes(object_name=""):
    """
    return an array of connected attributes
    :param object_name: <str> node string name
    :return: <list> connected attributes found for this object
    """
    cnst_attr = Attributes(object_name, keyable=True)
    return cnst_attr.connected.keys()


def get_all_attributes(object_name=""):
    """
    return an array of keyable attributes
    :param object_name: <str> node string name
    :return: <list> all attributes found for this object
    """
    cnst_attr = Attributes(object_name, keyable=True)
    return cnst_attr.all_attrs.keys()


def attr_connect(attr_src, attr_trg):
    """
    connect the attributes from the source attribute to the target attribute
    :param attr_src: <str> source attribute
    :param attr_trg: <str> target attribute
    :return: <bool> True for success. <bool> False for failure
    """
    if not cmds.isConnected(attr_src, attr_trg):
        cmds.connectAttr(attr_src, attr_trg)
    return True


def attr_get_default_value(object_name, attribute_name):
    """
    get the default value
    :param object_name: <str> node name
    :param attribute_name: <str> attribute name
    :return: <float> default value
    """
    node_attr = attr_name(object_name, attribute_name)
    default_value = cmds.addAttr(node_attr, query=True, dv=True)
    return default_value


def attr_add_float(object_name, attribute_name, min_value=None, max_value=None, default_value=None):
    """
    add the new attribute to this node
    :param object_name: <str> valid node name
    :param attribute_name: <str> valid attribute name
    :param min_value: <float> if given, will edit the attributes's minimum value
    :param max_value: <float> if given, will edit the attribute's maximum value
    :param default_value: <float> default_value
    :return: <str> new attribute name
    """
    node_attr = attr_name(object_name, attribute_name)
    if not cmds.objExists(node_attr):
        cmds.addAttr(object_name, at='float', ln=attribute_name)
        cmds.setAttr(node_attr, k=1)
    if not isinstance(min_value, type(None)):
        cmds.addAttr(node_attr, edit=True, min=min_value)
    if not isinstance(max_value, type(None)):
        cmds.addAttr(node_attr, edit=True, max=max_value)
    if not isinstance(default_value, type(None)):
        cmds.addAttr(node_attr, edit=True, defaultValue=default_value)
        cmds.setAttr(node_attr, default_value)
    return node_attr


def attr_float_set_default(object_name, attribute_name, default_value):
    """
    change the default value of an attribute
    :return:
    """
    node_attr = attr_name(object_name, attribute_name)
    cmds.addAttr(node_attr, edit=True, defaultValue=default_value)
    cmds.setAttr(node_attr, default_value)


def list_user_attributes(node_name):
    """
    Lists all custom attributes
    :param node_name:
    :return: <list> attribute names
    """
    attribute_list = cmds.listAttr(node_name, ud=True)
    return attribute_list


def remove_attr(node_name, attribute_name):
    """
    Remove an attribute.
    :param node_name: <str>
    :param attribute_name: <str> attribute name to remove from node
    """
    cmds.deleteAttr(node_name + '.' + attribute_name)


def attr_add_str(node_name, attribute_name, value):
    """
    Add an attribute to the module name
    :param node_name: <str> maya node name
    :param attribute_name: <str> maya attribute name
    :param value: <str> attribute value
    :return:
    """
    if not cmds.objExists(attr_name(node_name, attribute_name)):
        cmds.addAttr(node_name, dt='string', ln=attribute_name)
        cmds.setAttr(attr_name(node_name, attribute_name), value, type='string')
    attr_str = attr_name(node_name, attribute_name)
    return attr_str


def attr_set_min_max(node_name, attribute_name, min=0.0, max=1.0):
    """
    sets the minimum and maximum limits on the attribute.
    :param node_name: <str> valid node name.
    :param attribute_name: <str> valid attribute name.
    :param min: <float> sets the minimum value of this attribute.
    :param max: <float> sets the maximum value of this attribute.
    :return: <bool> True for success. <bool> False for failure.
    """
    return cmds.addAttr(attr_name(node_name, attribute_name), min=min, max=max, edit=True)


def attr_get_value(node_name, attribute_name):
    """
    add the new attribute to this node.
    :param node_name: <str> valid node name
    :param attribute_name: <str> valid attribute name.
    :return: <str> new attribute name.
    """
    return cmds.getAttr(attr_name(node_name, attribute_name))


def attr_name(object_name, attribute_name, check=False):
    """
    concatenate strings to make an attribute name.
    checks to see if the attribute is valid.
    :return: <str> attribute name.
    """
    attr_str = '{}.{}'.format(object_name, attribute_name)
    if check and not cmds.objExists(attr_str):
        raise ValueError('[AttrNameError] :: attribute name does not exit: {}]'.format(attr_str))
    return attr_str


def attr_set(object_name, value, attribute_name=""):
    """
    set the values to this attribute name.
    :param object_name: <str> the object node to set attributes to.
    :param attribute_name: <str> the attribute name to set value to.
    :param value: <int>, <float>, <str> the value to set to the attribute name.
    :return: <bool> True for success.
    """
    if '.' in object_name:
        return cmds.setAttr(object_name, value)
    return cmds.setAttr(attr_name(object_name, attribute_name), value)


def attr_split(a_name):
    """
    split the attribute name into their respective strings
    :param a_name: <str> attribute name.
    :return: <tuple> node name, attr name.
    """
    return tuple(a_name.split('.'))


class Attributes:
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
    LINEAR_ATTR_TYPES = (OpenMaya.MFn.kDoubleLinearAttribute,
                         OpenMaya.MFn.kFloatLinearAttribute)
    INTEGER_ATTR_TYPES = (OpenMaya.MFnNumericData.kShort,
                          OpenMaya.MFnNumericData.kInt,
                          OpenMaya.MFnNumericData.kLong,
                          OpenMaya.MFnNumericData.kByte)
    DOUBLE_ATTRS_TYPES = (OpenMaya.MFnNumericData.kFloat,
                          OpenMaya.MFnNumericData.kDouble,
                          OpenMaya.MFnNumericData.kAddr)

    def __init__(self, maya_node="", all_attrs=False, keyable=False, custom=False, connected=False):
        self.MAYA_M_OBJECT = object_utils.get_m_obj(maya_node)
        self.MAYA_MFN_OBJECT = object_utils.get_mfn_obj(maya_node)
        self.OBJECT_NODE_TYPE = self.MAYA_MFN_OBJECT.typeName()
        self.MAYA_STR_OBJECT = self.MAYA_MFN_OBJECT.name()
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
        mfn_obj = OpenMaya.MFnDependencyNode()
        ref_obj = mfn_obj.create(self.OBJECT_NODE_TYPE)
        for a_i in range(mfn_obj.attributeCount()):
            m_attr = OpenMaya.MFnAttribute(mfn_obj.attribute(a_i))
            attr_list.append(m_attr.name())
        self.deleteNode(ref_obj)
        self.doIt()
        return attr_list

    def get_connections_src(self, find_node_type=OpenMaya.MFn.kTransform, with_shape=OpenMaya.MFn.kLocator, custom_attr=True):
        """
        get the connection source.
        :param find_node_type:
        :return: <dict> connected atrributes.
        """
        dag_iter = OpenMaya.MItDependencyGraph(
            self.MAYA_M_OBJECT,
            OpenMaya.MItDependencyGraph.kDownstream,
            OpenMaya.MItDependencyGraph.kPlugLevel)
        dag_iter.reset()

        # iterate the dependency graph to find what we want.
        connections = {}
        while not dag_iter.isDone():
            cur_item = dag_iter.currentItem()

            if cur_item.hasFn(find_node_type):
                cur_fn = OpenMaya.MFnDependencyNode(cur_item)
                cur_name = cur_fn.name()
                connections[cur_name] = []

                if with_shape:
                    fn_item = OpenMaya.MFnDagNode(cur_item)
                    c_count = fn_item.childCount()
                    if c_count:
                        if fn_item.child(0).hasFn(with_shape):
                            for a_i in range(cur_fn.attributeCount()):
                                a_obj = cur_fn.attribute(a_i)
                                m_plug = OpenMaya.MPlug(cur_item, a_obj)
                                if m_plug.isConnected() and m_plug.isKeyable():
                                    if not custom_attr:
                                        connections[cur_name].append(m_plug.name())
                                    else:
                                        if m_plug.name().split('.')[-1] not in self.DEFAULT_ATTRS:
                                            connections[cur_name].append(m_plug.name())
                else:
                    for a_i in range(cur_fn.attributeCount()):
                        a_obj = cur_fn.attribute(a_i)
                        m_plug = OpenMaya.MPlug(cur_item, a_obj)
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
        if self.is_attr_locked(attribute_name):
            return False

        if not open_maya:
            try:
                cmds.setAttr('{}.{}'.format(self.MAYA_STR_OBJECT, attribute_name), attribute_value)
            except RuntimeError:
                # RuntimeError: setAttr: 'ankleFk_lf_ctrl.rig_info' is not a simple numeric attribute.
                # Its values must be set with a -type flag. #
                pass

        if open_maya:
            # allow the error to happen when the plug has not been found.
            o_plug = self.MAYA_MFN_OBJECT.findPlug(attribute_name)
            o_plug_attr = o_plug.attribute()
            o_plug_type = o_plug_attr.apiType()

            # rotational attributes
            if o_plug_type == OpenMaya.MFn.kDoubleAngleAttribute:
                o_plug.setMAngle(OpenMaya.MAngle(float(attribute_value)))

            # unit attributes
            if o_plug_type in self.LINEAR_ATTR_TYPES:
                num_type = OpenMaya.MFnUnitAttribute(o_plug_attr).unitType()

                # integers
                if num_type in self.INTEGER_ATTR_TYPES:
                    o_plug.setDouble(float(attribute_value))

                # doubles
                if num_type in self.DOUBLE_ATTRS_TYPES:
                    o_plug.setInt(int(attribute_value))

            # numeric attributes
            if o_plug_type == OpenMaya.MFn.kNumericAttribute:
                num_type = OpenMaya.MFnNumericAttribute(o_plug_attr).unitType()
                # OpenMaya.MFnNumericAttribute(o_plug_attr).unitType()

                # booleans
                if num_type == OpenMaya.MFnNumericData.kBoolean:
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

    def is_attr_source(self, attr_str):
        """
        check if attribute is source of connections.
        :return:
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.isSource()

    def get_source(self, attr_str):
        """
        check if attribute is source of connections.
        :return:
        """
        o_plug = self.MAYA_MFN_OBJECT.findPlug(attr_str)
        return o_plug.source().name()

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
        self.attr_data = {}
        for i in range(self.MAYA_MFN_OBJECT.attributeCount()):
            attrib = None
            a_obj = self.MAYA_MFN_OBJECT.attribute(i)
            p_type = a_obj.apiType()
            p_type_str = a_obj.apiTypeStr()
            m_plug = OpenMaya.MPlug(self.MAYA_M_OBJECT, a_obj)
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
            elif not custom:
                if attr_name not in self.DEFAULT_ATTR_VALUES:
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
        return self.attr_data

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
        if api_type in (OpenMaya.MFn.kAttribute3Double, OpenMaya.MFn.kAttribute3Float,
                        OpenMaya.MFn.kCompoundAttribute, OpenMaya.MFn.kAttribute4Double):
            if attr_plug.isCompound():
                p_value = cmds.attributeQuery(plug_name, node=attr_node, listChildren=True)

        # geometry <generic> attributes
        elif api_type == OpenMaya.MFn.kGenericAttribute:
            p_value = attr_plug.asDouble()

        # time attributes
        elif api_type == OpenMaya.MFn.kTimeAttribute:
            p_value = attr_plug.asDouble()

        # message attributes
        elif api_type == OpenMaya.MFn.kMessageAttribute:
            p_value = None

        # rotational attributes
        elif api_type == OpenMaya.MFn.kDoubleAngleAttribute:
            p_value = round(attr_plug.asMAngle().asDegrees(), 3)

        # distance attribute
        elif api_type in (OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute):
            p_value = attr_plug.asMDistance().asCentimeters()

        # angle attribute
        elif api_type in (OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute):
            p_value = attr_plug.asDouble()

        # typed attribute
        elif api_type == OpenMaya.MFn.kTypedAttribute:
            at_type = OpenMaya.MFnTypedAttribute(attr_obj).attrType()

            # matrix
            if at_type == OpenMaya.MFnData.kMatrix:
                # p_value = OpenMaya.MFnMatrixData(attr_plug.asMObject()).matrix()
                p_value = cmds.getAttr(attr_plug.name())

            # string
            if at_type == OpenMaya.MFnData.kString:
                p_value = attr_plug.asString()

        # matrix
        elif api_type == OpenMaya.MFn.kMatrixAttribute:
            # p_value = OpenMaya.MFnMatrixData(attr_plug.asMObject()).matrix()
            p_value = cmds.getAttr(attr_plug.name())

        # numbers
        elif api_type == OpenMaya.MFn.kNumericAttribute:
            at_type = OpenMaya.MFnNumericAttribute(attr_obj).unitType()

            # boolean
            if at_type == OpenMaya.MFnNumericData.kBoolean:
                p_value = attr_plug.asBool()

            # integer
            if at_type in self.INTEGER_ATTR_TYPES:
                p_value = attr_plug.asInt()

            # floats
            if at_type in self.DOUBLE_ATTRS_TYPES:
                p_value = round(attr_plug.asDouble(), 3)

        # enumeration
        elif api_type == OpenMaya.MFn.kEnumAttribute:
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
            # if self.is_attr_connected(attr):
            #     continue
            if self.get_source(attr):
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

# ______________________________________________________________________________________________________________________
# attribute_utils.py
