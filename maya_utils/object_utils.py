"""
Manipulating and traversing the Maya scene objects and connections.
Lesson in data science:
    # everything up to but not including index 3
    print(z[:3])

    # index 1 to end of list
    print(z[1:])

line = re.sub(r'''
  (?x) # Use free-spacing mode.
  <    # Match a literal '<'
  /?   # Optionally match a '/'
  \[   # Match a literal '['
  \d+  # Match one or more digits
  >    # Match a literal '>'
  .    # Match any single character except '\n'
  ^    # Match if string starts with a character
  $    # Match of string ends with a character
  *    # Match a pattern of zero or more occurrences
  +    # Match one or more occurrences of a pattern at the left
  ?    # Match zero or one occurrence of the patter at the left
  |    # Alternation "or" operator
  ()   # Grouping sub-patterns, match any strings inside parentheses
  ''', '', line)
"""
# import standard modules
import re
import collections
import string


# import maya modules
from maya import cmds
from maya import OpenMaya as OpenMaya
from maya import OpenMayaAnim as OpenMayaAnim


# define local variables
node_types = {
    'nurbsCurve':           OpenMaya.MFn.kNurbsCurve,
    'locator':              OpenMaya.MFn.kLocator,
    'mesh':                 OpenMaya.MFn.kMesh,
    'nurbsSurface':         OpenMaya.MFn.kNurbsSurface,
    'unitConversion':       OpenMaya.MFn.kUnitConversion,
    'blendWeighted':        OpenMaya.MFn.kBlendWeighted,
    'transform':            OpenMaya.MFn.kTransform,
    'follicle':             OpenMaya.MFn.kFollicle,
    'dag':                  OpenMaya.MFn.kDagNode,
    'joint':                OpenMaya.MFn.kJoint,
    'ikHandle':             OpenMaya.MFn.kIkHandle,
    'effector':             OpenMaya.MFn.kIkEffector,
    'component':            OpenMaya.MFn.kComponent,
    'lattice':              OpenMaya.MFn.kLattice,
    'blendShape':           OpenMaya.MFn.kBlendShape,
    'animCurve':            OpenMaya.MFn.kAnimCurve,
    'set':                  OpenMaya.MFn.kSet,
    'camera':               OpenMaya.MFn.kCamera,
    'skin':                 OpenMaya.MFn.kSkin,
    'skinCluster':          OpenMaya.MFn.kSkinClusterFilter,
    'tweak':                OpenMaya.MFn.kTweak,
    'bend':                 OpenMaya.MFn.kDeformBend,
    'squash':               OpenMaya.MFn.kDeformSquash,
    'cluster':              OpenMaya.MFn.kCluster,
    'deltaMush':            OpenMaya.MFn.kDeltaMush,
    'wire':                 OpenMaya.MFn.kWire,
    'sculpt':               OpenMaya.MFn.kSculpt,
    'wrap':                 OpenMaya.MFn.kWrapFilter,
    'shrinkWrap':           OpenMaya.MFn.kShrinkWrapFilter,
    'lambert':              OpenMaya.MFn.kLambert
}

# define private variables
__verbosity__ = 0


def vprint(*args):
    """
    print only if verbosity is > 0.
    :param args: array items.
    :return: <None>
    """
    if __verbosity__:
        print(args)


def flatten(array):
    """
    flatten list generator.
    :param array: <tuple>, <list> array of objects to flatten.
    :return: <str> item.
    """
    for el in array:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def select_object(object_name):
    """
    selects an item.
    """
    return cmds.select(object_name)


def selection_order(func):
    """
    selection order decorator
    :param func: <functionObject> the function object to run
    :return: <functionWrapper>
    """
    def wrapper(*args, **kwargs):
        set_pref = 0
        select_pref = cmds.selectPref(trackSelectionOrder=1, q=1)
        if not select_pref:
            set_pref = 1
            cmds.selectPref(trackSelectionOrder=1)
        # run function
        answer = func(*args, **kwargs)
        if set_pref:
            cmds.selectPref(trackSelectionOrder=select_pref)
        return answer
    return wrapper


def compare_array_lengths(array_1, array_2):
    """
    compare the array lengths from array_1, to array_2
    :param array_1:
    :param array_2:
    :return: <bool> True for yes. <bool> False for no.
    """
    return len(array_1) == len(array_2)


def get_dag(object_name="", shape=False):
    """
    returns a dag path object.
    :param object_name: <str> object to get dag path from.
    :param shape: <bool> returns the OpenMaya.MDag() shape instead.
    :return: <OpenMaya.MDagPath>
    """
    m_sel = OpenMaya.MSelectionList()
    if not shape:
        m_sel.add(object_name)
    elif shape:
        shapes_len = get_shapes_len(get_m_obj(object_name))
        if shapes_len > 0:
            for i in range(shapes_len):
                m_sel.add(get_shape_name(object_name)[i])
        elif not shapes_len and not has_fn(get_shape_name(object_name), 'transform'):
            m_sel.add(object_name)
    m_dag = OpenMaya.MDagPath()
    m_sel.getDagPath(0, m_dag)
    return m_dag


def get_selection_iter():
    """
    returns the selection iterator.
    :return:
    """
    models = OpenMaya.MSelectionList()
    for model in cmds.ls(transforms=True):
        models.add(model)
    return OpenMaya.MItSelectionList(models)


def array_to_mit_selection(array):
    """
    returns an OpenMaya MItSelectionList from the array objects provided.
    """
    mit_sel = OpenMaya.MSelectionList()
    for obj in array:
        mit_sel.add(obj)
    return OpenMaya.MItSelectionList(mit_sel)


def get_m_selection(objects_array=(), as_strings=False):
    """
    return active selection list.
    :return:
    """
    m_list = OpenMaya.MSelectionList()
    if not objects_array:
        OpenMaya.MGlobal.getActiveSelectionList(m_list)
    elif objects_array:
        map(m_list.add, objects_array)
    if as_strings:
        m_string_array = list()
        m_list.getSelectionStrings(m_string_array)
        return m_string_array
    return m_list


def get_m_selection_iter(objects_array=()):
    """
    gets an selection list iter.
    :param objects_array: <tuple> or <list> array of items to add.
    :return: <OpenMaya.MItSelectionList>
    """
    m_list = OpenMaya.MSelectionList()
    if not objects_array:
        OpenMaya.MGlobal.getActiveSelectionList(m_list)
    else:
        for obj_name in objects_array:
            m_list.add(obj_name)
    mIt_list = OpenMaya.MItSelectionList(m_list)
    return mIt_list


def iterate_items(objects_array=()):
    """
    iterate through the selected items. Retrieve the MDagPath and MComponent objects.
    :return: <tuple> array of selected items.
    """
    m_iter = get_m_selection_iter(objects_array)
    items = ()
    while not m_iter.isDone():
        m_dag = OpenMaya.MDagPath()
        m_component = OpenMaya.MObject()
        m_iter.getDagPath(m_dag, m_component)
        items += m_dag, m_component,
        m_iter.next()
    return items


def get_shape_dag(object_name=""):
    """
    returns the dagNode of the object.
    :param object_name:
    :return:
    """
    if not object_name:
        object_name = get_selected_node()
    return get_dag(object_name, shape=True)


def get_shape_fn(object_name=""):
    """
    :return: the shape fn object from the string object provided.
    """
    if not object_name:
        object_name = get_selected_node()
    m_shapes = get_m_shape(get_dag(object_name))
    shape_array = ()
    for shape in m_shapes:
        shape_array += get_fn(shape),
    return shape_array


def get_shape_name(object_name="", shape_type=""):
    """
    :return: the shape name.
    """
    if not object_name:
        object_name = get_selected_node()
    return get_m_shape(get_m_obj(object_name), shape_type=shape_type, as_strings=True)


def get_shape_obj(object_name="", shape_type=""):
    """
    returns a objects' shape OpenMaya.MObject.
    :param object_name: <str> the object name to get shape object from.
    :param shape_type: <str> shape type to return, else, return any shape.
    :return: the shape OpenMaya.MObject.
    """
    if not object_name:
        object_name = get_selected_node()
    return get_m_shape(get_m_obj(object_name), shape_type=shape_type, as_strings=False)


def is_exists(object_name):
    """
    check if the object name exists, or OpenMaya.MObject is valid.
    :param object_name: <str>, <OpenMaya.MObject> the object to check.
    :return: <bool> True, yes it exists. <bool> False, no it does not exist.
    """
    try:
        m_obj = get_m_obj(object_name)
    except RuntimeError:
        return False
    return not m_obj.isNull()


def is_shape_locator(object_name):
    """
    check if the object name has nurbs curve shape object.
    :param object_name: <str> the object to check shape type from.
    :return: <bool> True for yes, <bool> False for no.
    """
    return bool(get_shape_name(object_name, shape_type="locator"))


def is_shape_curve(object_name):
    """
    check if the object name has nurbs curve shape object.
    :param object_name: <str> the object to check shape type from.
    :return: <bool> True for yes, <bool> False for no.
    """
    return bool(get_shape_name(object_name, shape_type="nurbsCurve"))


def is_shape_follicle(object_name):
    """
    check if the object name has follicle shape object.
    :param object_name: <str> the object to check shape type from.
    :return: <bool> True for yes, <bool> False for no.
    """
    return bool(get_shape_name(object_name, shape_type="follicle"))


def is_shape_mesh(object_name):
    """
    check if the object name has mesh shape object.
    :param object_name: <str> object name to check.
    :return: <bool> True for yes, <bool> False for no.
    """
    return bool(get_shape_name(object_name, shape_type="mesh"))


def is_joint(object_name):
    """
    confirm if the object is a joint type.
    :param object_name: <str>, <OpenMaya.MObject> the object to check.
    :return: <bool> is of type joint.
    """
    return bool(has_fn(get_m_obj(object_name), 'joint'))


def is_dag(object_name):
    """
    confirm if the object is of a dag type.
    :param object_name: <str>, <OpenMaya.MObject> the object to check.
    :return: <bool> is of type dag.
    """
    return bool(has_fn(get_m_obj(object_name), 'dag'))


def is_set(object_name):
    """
    confirm if the object provided is of MFnSet type.
    :param object_name: <str>, <OpenMaya.MObject> the object to check.
    :return: <bool> is of type MfnSet.
    """
    return bool(has_fn(get_m_obj(object_name), 'set'))


def is_transform(object_name):
    """
    confirm if the object is of a transform type.
    :param object_name: <str>, <OpenMaya.MObject> the object to check.
    :return: <bool> is of type transform.
    """
    return bool(has_fn(get_m_obj(object_name), 'transform'))


def is_shape_camera(object_name):
    """
    confirm if the object has a camera shape type.
    :param object_name: <str>, <OpenMaya.MObject> the object to check.
    :return: <bool> is of type camera.
    """
    return bool(get_shape_name(object_name, shape_type="camera"))


def is_shape_nurbs_surface(object_name):
    """
    check if the object name has nurbs surface shape object.
    :param object_name: <str> object name to check.
    :return: <bool> True for yes, <bool> False for no.
    """
    return bool(get_shape_name(object_name, shape_type="nurbsSurface"))


def is_shape_nurbs_curve(object_name):
    """
    check if the object name has nurbs curve shape object.
    :param object_name: <str> object name to check.
    :return: <bool> True for yes, <bool> False for no.
    """
    return bool(get_shape_name(object_name, shape_type="nurbsCurve"))


def is_attr_locked(object_node, attr_str):
    """
    check if attribute is locked.
    :param object_node: <str> object node name.
    :param attr_str: <str> attribute name.
    :return: <bool> True for yes, <bool> False for no.
    """
    return get_plug(object_node, attr_str).isLocked()


def is_attr_connected(object_node, attr_str):
    """
    check if attribute is connected.
    :param object_node: <str> object node name.
    :param attr_str: <str> attribute name.
    :return: <bool> True for yes, <bool> False for no.
    """
    return get_plug(object_node, attr_str).isConnected()


def is_attr_source(object_node, attr_str):
    """
    check if attribute is source of connections.
    :param object_node: <str> object node name.
    :param attr_str: <str> attribute name.
    :return: <bool> True for yes, <bool> False for no.
    """
    return get_plug(object_node, attr_str).isSource()


def attr_info(object_node, attr_str):
    """
    get plug info
    :param object_node: <str> object node name.
    :param attr_str: <str> attribute name.
    :return: <bool> True for yes, <bool> False for no.
    """
    return get_plug(object_node, attr_str).info()


def is_attr_keyable(object_node, attr_str):
    """
    check if attribute is keyable.
    :param object_node: <str> object node name.
    :param attr_str: <str> attribute name.
    :return: <bool> True for yes, <bool> False for no.
    """
    return get_plug(object_node, attr_str).isKeyable()


def check_object_type(object_name="", object_type=""):
    """
    compare two objects' types.
    :param object_name: <str> the object to check shape type from.
    :param object_type: <str> the object type to check.
    :return: <bool> True for success. <bool> False for failure.
    """
    return cmds.objectType(object_name) == object_type


def get_nice_name(object_name=''):
    """
    return a nice name from the object specified.
    :param object_name: <str> maya scene object name.
    :return: <str> nice name.
    """
    return '_'.join(object_name.split(':'))


def get_k_space(space='world'):
    """
    get the OpenMaya.MFn.kSpace index type object.
    :param space: <str> the space to get.
    :return: <int> index type.
    """
    if space == 'world':
        return space_k_world()
    elif space == 'object':
        return space_k_object()
    elif space == 'transform':
        return space_k_transform()
    else:
        raise NotImplementedError(
            "[GetKSpace] :: {}, is invalid.".format(space))


def space_k_world():
    """
    :return: MSpace.kWorld
    """
    return OpenMaya.MSpace.kWorld


def space_k_object():
    """
    :return: MSpace.kObject
    """
    return OpenMaya.MSpace.kObject


def space_k_transform():
    """
    :return: MSpace.kTransform
    """
    return OpenMaya.MSpace.kTransform


class ScriptUtil(OpenMaya.MScriptUtil):
    ptr = None
    matrix_om = OpenMaya.MMatrix()

    def __init__(self,
                 as_double_ptr=False,
                 as_float_ptr=False,
                 as_float2_ptr=False,
                 as_double2_ptr=False,
                 as_double3_ptr=False,
                 as_float3_ptr=False,
                 as_int_ptr=False,
                 as_uint_ptr=False,
                 matrix_from_list=()):
        """Use this class for setting and retrieving variables from a memory address.

        Args:
            as_double_ptr: (bool)
            as_float_ptr: (bool)
            as_float2_ptr: (bool)
            as_double2_ptr: (bool)
            as_double3_ptr: (bool)
            as_float3_ptr: (bool)
            as_int_ptr: (bool)
            as_uint_ptr: (bool)
            matrix_from_list: (bool)
        Usage:
            double_util = object_utils.ScriptUtil(0.0, as_double_ptr=True)
            curve_fn.getParamAtPoint(point, double_util.ptr, 0.001, OpenMaya.MSpace.kObject)
            return double_util.get_double()

        """
        super(ScriptUtil, self).__init__()
        if as_double_ptr:
            self.createFromDouble(0.0)
            self.ptr = self.asDoublePtr()
        if as_float_ptr:
            self.createFromDouble(0.0)
            self.ptr = self.asFloatPtr()
        if as_float2_ptr:
            # self.createFromDouble(*a)
            self.ptr = self.asFloat2Ptr()
        if as_double2_ptr:
            self.createFromList([0.0, 0.0], 2)
            self.ptr = self.asDouble2Ptr()
        if as_double3_ptr:
            self.createFromList([0.0, 0.0, 0.0], 3)
            self.ptr = self.asDouble3Ptr()
        if as_float3_ptr:
            self.createFromList([0.0, 0.0, 0.0], 3)
            self.ptr = self.asFloat3Ptr()
        if as_int_ptr:
            if isinstance(as_int_ptr, int):
                self.ptr = self.createFromInt(as_int_ptr)
            else:
                self.ptr = self.asIntPtr()
        if as_uint_ptr:
            self.ptr = self.asUintPtr()
        if matrix_from_list:
            self.matrix_from_list(*matrix_from_list)

    def execute(self, function=()):
        function[0](*[self.ptr] + list(function[1:]))

    def as_float(self):
        return self.ptr.asFloat()

    def as_float2(self):
        return self.ptr.asFloat2()

    def as_float3(self):
        return self.ptr.asFloat3()

    def as_double(self):
        return self.ptr.asDouble()

    def as_int(self):
        return self.ptr.asInt()

    def get_double(self):
        return self.getDouble(self.ptr)

    def get_float(self):
        return self.getFloat(self.ptr)

    def get_float3_item(self, r=0, c=0):
        return self.getFloat3ArrayItem(self.ptr, r, c)

    def get_float2_item(self, r=0, c=0):
        return self.getFloat2ArrayItem(self.ptr, r, c)

    def get_int(self):
        return self.getInt(self.ptr)

    def double_array_item(self, idx=0):
        return self.getDoubleArrayItem(self.ptr, idx)

    def float_array_item(self, idx=0):
        return self.getFloatArrayItem(self.ptr, idx)

    def matrix_from_list(self, matrix_list=()):
        self.createMatrixFromList(matrix_list, self.matrix_om)

    @property
    def as_matrix(self):
        return self.matrix_om

    def __repr__(self):
        return self.ptr


def get_world_position(object_name):
    """
    world position
    :param object_name: <str> object node to extract position from
    :return: <list> world position
    """
    position = cmds.xform(object_name, ws=True, t=True, q=True)
    return position


def get_relative_position(object_name):
    """
    world position
    :param object_name: <str> object node to extract position from
    :return: <list> world position
    """
    position = cmds.xform(object_name, ws=False, t=True, q=True)
    return position


def get_world_matrix(object_name):
    """
    gets the world position
    :param object_name: <str> object node to extract matrix from
    :return: <list> world position matrix
    """
    matrix = cmds.xform(object_name, ws=True, q=True, m=True)
    return matrix


def get_relative_matrix(object_name):
    """
    gets the world position
    :param object_name: <str> object node to extract matrix from
    :return: <list> world position matrix
    """
    matrix = cmds.xform(object_name, ws=False, q=True, m=True)
    return matrix


def get_unsigned_int_ptr(int_num=None):
    """
    returns an unsigned integer pointer object.
    :param int_num: <int> integer number to convert to a pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = OpenMaya.MScriptUtil()
    util.createFromInt(int_num)
    return util.asIntPtr()


def get_unsigned_int(int_num=None):
    """
    returns an unsigned integer pointer object.
    :param int_num: <int> integer number to convert to a pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = OpenMaya.MScriptUtil()
    util.createFromInt(int_num)
    return util.asInt()


def get_double_ptr():
    """
    returns an unsigned integer pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = OpenMaya.MScriptUtil()
    util.createFromList([0.0, 0.0, 0.0], 3)
    return util.asDoublePtr()


def get_double4_ptr():
    """
    returns an unsigned integer pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = OpenMaya.MScriptUtil()
    return util.asDouble4Ptr()


@selection_order
def get_selected_node(single=True):
    """
    grabs the current name of the selected object.
    :param single: <bool> if False, get selection array.
    :return: <str> selected object. <str> empty list for failure.
    """
    if single:
        try:
            return cmds.ls(os=1, fl=1)[0]
        except IndexError:
            return ''
    return tuple(cmds.ls(os=1, fl=1))


def get_selected_components():
    """
    return the selected components
    :return: <tuple> array of components.
    """
    return tuple(cmds.ls(sl=1, flatten=True))


def connect_attr(src_attribute="", dst_attribute=""):
    """
    perform connection
    :return: <bool> True for success. <bool> False for failure.
    """
    if not cmds.isConnected(src_attribute, dst_attribute):
        cmds.connectAttr(src_attribute, dst_attribute)
    return True


def get_connections_source(object_name=""):
    """
    get a list of source connections from the object specified.
    :param object_name: <str> object to check.
    :return: <tuple> source connections.
    """
    return tuple(cmds.listConnections(object_name, source=True, destination=False, plugs=True))


def get_connections_destination(object_name=""):
    """
    get a list of destination connections from the object specified.
    :param object_name: <str> object to check.
    :return: <tuple> destination connections.
    :return:
    """
    return tuple(cmds.listConnections(object_name, source=False, destination=True, plugs=True))


def get_m_obj_array(objects=()):
    """
    returns the objects as MObjectArray
    :param objects:
    :return: <OpenMaya.MObjectArray>
    """
    m_array = OpenMaya.MObjectArray()
    for idx, obj in enumerate(objects):
        if is_exists(obj):
            m_array.insert(get_m_obj(obj), idx)
    return m_array


def get_m_shape_obj_array(objects=()):
    """
    returns the objects as MObjectArray
    :param objects:
    :return:
    """
    m_array = OpenMaya.MObjectArray()
    for obj in objects:
        m_array.append(get_shape_obj(obj)[0])
    return m_array


def convert_obj_array_to_string_array(object_array):
    """
    returns the string version of the MObjectArray
    :return:
    """
    objects = ()
    try:
        for i in range(len(object_array)):
            objects += get_m_object_name(object_array[i]),
    except TypeError:
        for i in range(object_array.length()):
            objects += get_m_object_name(object_array[i]),
    return objects


def rename_node(object_name, this_name):
    """
    renames the object name to this name.
    :param object_name:
    :param this_name:
    :return: <str> modified name.
    """
    m_dag_mod = OpenMaya.MDagModifier()
    m_dag_mod.renameNode(get_m_obj(object_name), this_name)
    m_dag_mod.doIt()
    return this_name


def delete_node(object_name):
    """
    delete the object if it exists in the scene.
    :param object_name:
    :return:
    """
    try:
        if cmds.objExists(object_name):
            cmds.delete(object_name)
        else:
            return False
    except TypeError:
        OpenMaya.MGlobal.displayWarning(
            "[UnableToRemove] :: {}".format(object_name))
    return True


def remove_node(object_name):
    """
    removes the node(s) form the Maya scene.
    :param object_name: <str> object node to remove.
    :return: <bool> True for success.
    """
    m_dag_mod = OpenMaya.MDagModifier()
    if isinstance(object_name, (list, tuple)):
        array = get_m_obj_array(object_name)
        for i in range(array.length()):
            m_dag_mod.deleteNode(array[i])
            try:
                m_dag_mod.doIt()
            except RuntimeError:
                # object  already deleted
                continue
    elif isinstance(object_name, str) and is_exists(object_name):
        node = get_m_obj(object_name)
        m_dag_mod.deleteNode(node)
        m_dag_mod.doIt()
    return True


def get_m_object_name(m_object=OpenMaya.MObject):
    """
    get the object name string.
    :param m_object: <OpenMaya.MObject> get the string of this object node.
    :return: <str> object name.
    """
    return OpenMaya.MFnMFnDependencyNode(m_object).name()


def get_plug(object_name, attr_str):
    """
    get the MPlug from object attribute name.
    :param object_name: <str> object name to get the MFnPlug from.
    :param attr_str: <str> attribute name to find.
    :return: <OpenMaya.MPlug>
    """
    return get_fn(get_m_obj(object_name)).findPlug(attr_str, False)


def get_object_types(find_str=""):
    """
    return a list of all OpenMaya object types.
    :return: <list> of object_type.
    """
    k_objects = filter(lambda k: k.startswith('k'), dir(OpenMaya.MFn))
    return filter(lambda k: find_str in k, k_objects)


def get_m_anim_from_sel(object_node="", as_strings=False):
    """
    get animation curves from selected.
    :param object_node: <str> control object to get animation curve nodes frOpenMaya.
    :param as_strings: <bool> return string objects.
    :return: <list> anim curves.
    """
    if not object_node:
        object_node = get_selected_node()
    anim_nodes = {}
    anim_curve_nodes = get_connected_nodes(
        object_name=object_node, find_node_type=OpenMaya.MFn.kAnimCurve, as_strings=as_strings,
        down_stream=False, up_stream=True)
    for anim in anim_curve_nodes:
        if as_strings:
            anim_nodes[anim] = get_m_obj(anim)
        else:
            anim_nodes[get_m_object_name(
                anim)] = OpenMayaAnim.MFnAnimCurve(anim)
    return anim_nodes


def get_m_object_name(m_object=None):
    """
    gets the name of the m object.
    :param m_object: <OpenMaya.MObject> maya object.
    :return: <str> node name.
    """
    node_fn = OpenMaya.MFnDependencyNode(m_object)
    return node_fn.name()


def compare_objects(object_1, object_2, fn=False, shape_type=False):
    """
    compare two objects
    :param object_1: <str>
    :param object_2: <str>
    :param fn: <bool> compare function set.
    :param shape_type: <bool> compare shape function set.
    :return: <bool> True for success. <bool> False for failure.
    """
    object_1 = get_m_obj(object_1)
    object_2 = get_m_obj(object_2)
    if fn:
        return get_fn(object_1) == get_fn(object_2)
    if shape_type:
        return get_shape_name(object_1) == get_shape_name(object_2)
    return False


def get_scene_objects(name='', as_strings=False, node_type='', find_attr='', dag=False):
    """
    finds all objects in the current scene.
    :param as_strings: <bool> return a list of node strings instead of a list of OpenMaya.MObject(s).
    :param name: <str> get scene objects containing this name.
    :param node_type: <str> find this node type in the current scene.
    :param find_attr: <str> find this attribute in the objects found in scene.
    :param dag: <bool> if set to True, get only the transform items.
    :return: <list> of scene items. <bool> False for failure.
    """
    scene_it = OpenMaya.MItDependencyNodes()
    items = ()
    while not scene_it.isDone():
        cur_item = scene_it.item()
        if not cur_item.isNull():
            if as_strings:
                o_name = get_m_object_name(cur_item)
            else:
                o_name = cur_item
            if dag and has_fn(cur_item, 'dag'):
                if node_type and has_fn(cur_item, node_type):
                    if name and name in o_name:
                        items += o_name,
                    else:
                        items += o_name,
                elif not node_type:
                    items += o_name,
            elif not dag:
                if node_type and has_fn(cur_item, node_type):
                    if name and name in o_name:
                        items += o_name,
                    else:
                        items += o_name,
                elif not node_type:
                    items += o_name,
        scene_it.next()

    # filter all items that contains this attribute name
    if find_attr:
        items = filter(lambda x: has_attr(x, find_attr), items)

    # flatten the resultant array
    return tuple(flatten(items))


def check_fn_shape(m_object=None, m_type=None):
    """
    confirm the shape type for this object. Only checks the first child for shape.
    :param m_object: <OpenMaya.MObject>
    :param m_type: <OpenMaya.MFn.kType>
    :return: <OpenMaya.MObject> if True, <NoneType> False if not.
    """
    # confirm the incoming parameter is an MObject
    m_object = get_m_obj(m_object)
    fn_item = OpenMaya.MFnDagNode(m_object)
    c_count = fn_item.childCount()
    if c_count:
        return fn_item.child(0).hasFn(m_type)
    elif not c_count:
        return m_object.hasFn(m_type)
    return None


def type_exists(shape_type):
    """
    checks if the shape type name is valid.
    :param shape_type: <str> the shape type to check.
    :return: <bool> True for yes. <bool> False for no.
    """
    return shape_type in node_types


def check_shape_type_name(m_object=None, shape_type=None):
    """
    checks the shape name.
    :param m_object: <OpenMaya.MObject>
    :param shape_type: <str> shape type name.
    :return: <bool> True for yes. <bool> False for no.
    """
    m_object = get_m_obj(m_object)
    if type_exists(shape_type):
        return check_fn_shape(m_object, m_type=node_types[shape_type])
    return False


def get_parents(object_name=None, stop_at=''):
    """
    get parents
    :param object_name: <OpenMaya.MObject>
    :param stop_at: <str> stop at when found this name.
    :return: <tuple> parent object names.
    """
    m_object = get_m_obj(object_name)
    fn_object = OpenMaya.MFnDagNode(m_object)
    return_data = ()
    par_count = fn_object.parentCount()
    if par_count:
        o_arr = OpenMaya.MDagPathArray()
        fn_object.getAllPaths(o_arr)
        length = o_arr.length()
        for i in xrange(length):
            m_path = o_arr[i]
            p_node_ls = m_path.fullPathName().split('|')
            p_node_ls.reverse()
            for p in p_node_ls:
                if p:
                    return_data += p,
                if p == stop_at:
                    break
    return return_data


def convert_list_to_str(array_obj):
    """
    change the array object into a string object.
    :param array_obj: <tuple>, <list> array object to convert.
    :return: <str> object.
    """
    if isinstance(array_obj, (tuple, list)) and len(array_obj) == 1:
        return array_obj[0]
    return array_obj


def convert_str_to_list(array_obj):
    """
    change the array object into a string object.
    :param array_obj: <tuple>, <list> array object to convert.
    :return: <str> object.
    """
    if isinstance(array_obj, (str, unicode)) and len(array_obj) == 1:
        return array_obj,
    return array_obj


def get_fn(m_object):
    """
    returns the fn object from the m_object supplied.
    :param m_object: <OpenMaya.MObject> to get function class frOpenMaya.
    :return: <OpenMaya.MFn<ClassType> specific object fn type.
    """
    m_object = convert_list_to_str(m_object)
    if type_str(m_object) == 'mesh':
        return OpenMaya.MFnMesh(m_object)
    elif type_str(m_object) == 'nurbsCurve':
        return OpenMaya.MFnNurbsCurve(m_object)
    elif type_str(m_object) == 'nurbsSurface':
        return OpenMaya.MFnNurbsSurface(m_object)
    elif type_str(m_object) == 'camera':
        return OpenMaya.MFnCamera(m_object)
    elif type_str(m_object) == 'joint':
        return OpenMayaAnim.MFnIkJoint(m_object)
    elif type_str(m_object) == 'ikHandle':
        return OpenMayaAnim.MFnIkEffector(m_object)
    elif type_str(m_object) == 'lambert':
        return OpenMaya.MFnLambertShader(m_object)
    else:
        return OpenMaya.MFnDependencyNode(m_object)


def type_str(m_object):
    """
    get OpenMaya.MObject type as string.
    :param m_object: <OpenMaya.MObject>
    :return: <str> api type name.
    """
    return OpenMaya.MFnDependencyNode(m_object).typeName()


def type_int(m_object):
    """
    get OpenMaya.MObject type as an integer.
    :param m_object: <OpenMaya.MObject>
    :return: <int> api type.
    """
    return OpenMaya.MFnDependencyNode(m_object).type()


def has_fn(item_name, shape_type):
    """
    check if the MObject provided has this type.
    :param item_name: <OpenMaya.MObject> the object to check the type.
    :param shape_type: <str>, <OpenMaya.MFn.kType> the type id.
    :return: <bool> True for type is match. <bool> for no match.
    """
    try:
        base_strings = (str, unicode)
    except NameError:
        base_strings = str,
    item_name = get_m_obj(item_name)
    if isinstance(shape_type, base_strings):
        if shape_type not in node_types:
            return False
        return item_name.hasFn(node_types[shape_type])
    if isinstance(shape_type, int):
        return item_name.hasFn(shape_type)


def has_attr(item_obj, attr_name):
    """
    check if the current object has this attribute name.
    :param item_obj: <object> item object to find the attribute in.
    :param attr_name: <str> the attribute name to find in the item object.
    :return: <bool> True attribute has been found. <bool> False, no attribute found.
    """
    if not item_obj:
        return False
    if isinstance(item_obj, (str, unicode)):
        item_obj = get_m_obj(item_obj)
    return Item(item_obj).has_plug(attr_name)


def get_shapes_len(m_object=None):
    """
    returns the number of shapes children.
    :return:
    """
    fn_item = OpenMaya.MFnDagNode(m_object)
    ch_shapes = ()
    ch_count = fn_item.childCount()
    if ch_count:
        for i in range(ch_count):
            ch_item = fn_item.child(i)
            if has_fn(ch_item, 'transform'):
                continue
            ch_shapes += i,
    return len(ch_shapes)


def get_m_shape(m_object=None, shape_type="", as_strings=False):
    """
    get the MObject children object(s).
    :param m_object: <OpenMaya.MObject> the MObject to get children frOpenMaya.
    :param shape_type: <str> get only shapes of this type.
    :param as_strings: <bool> return as string name array.
    :return: <tuple> array of shape objects.
    """
    return_items = ()
    fn_item = OpenMaya.MFnDagNode(m_object)
    ch_count = fn_item.childCount()
    if ch_count:
        for i in range(ch_count):
            ch_item = fn_item.child(i)
            if shape_type and not has_fn(ch_item, shape_type):
                continue
            if has_fn(ch_item, 'transform'):
                continue
            if as_strings:
                return_items += OpenMaya.MFnDependencyNode(ch_item).name(),
            elif not as_strings:
                return_items += ch_item,
    elif not ch_count:
        if has_fn(m_object, shape_type):
            return_items += m_object,
    return return_items


def get_m_parent(m_object=None, find_parent='', with_shape='', as_strings=False):
    """
    finds the parent from the maya object provided.
    :param m_object: <OpenMaya.MObject> the object to get the parents frOpenMaya.
    :param find_parent: <str> find this parent from the object provided.
    :param with_shape: (Not Implemented) <str> find a parent containing this shape object.
    :param as_strings: <bool> get results as strings.
    :return: <list> found objects.
    """
    fn_object = OpenMaya.MFnDagNode(m_object)
    return_data = ()
    par_count = fn_object.parentCount()
    if par_count:
        if isinstance(find_parent, (str, unicode)):
            o_arr = OpenMaya.MDagPathArray()
            fn_object.getAllPaths(o_arr)
            length = o_arr.length()
            for i in range(length):
                m_path = o_arr[i]
                p_node_ls = m_path.fullPathName().split('|')
                found = filter(
                    lambda x: find_parent in x.rpartition(':')[-1], p_node_ls)
                if found:
                    if as_strings:
                        return_data += found,
                    else:
                        return_data += get_m_obj(found),
        elif isinstance(find_parent, (int, bool)):
            if as_strings:
                return_data += get_m_object_name(fn_object.parent(0)),
            else:
                return_data += fn_object.parent(0),
    return return_data


def get_m_child(m_object=None, find_child=True, with_type='', with_shape='', transform=False, as_strings=False):
    """
    finds the child from the maya object provided.
    :param m_object: <OpenMaya.MObject> the object to get the parents frOpenMaya.
    :param find_child: <str> find this child from the object provided.
    :param with_shape: <str> find a child containing this shape object.
    :param transform: <bool> get transform objects only.
    :param as_strings: return objects as strings.
    :return: <list> found objects.
    """
    fn_object = OpenMaya.MFnDagNode(m_object)
    return_data = ()
    ch_count = fn_object.childCount()
    if ch_count:
        m_dag = OpenMaya.MDagPath()
        fn_object.getPath(m_dag)
        m_iter = OpenMaya.MItDag(OpenMaya.MItDag.kBreadthFirst)
        m_iter.reset(m_dag)

        # iterate from the dag path provided
        while not m_iter.isDone():
            o_path = OpenMaya.MDagPath()
            m_iter.getPath(o_path)
            ch_node = o_path.node()
            if as_strings:
                ch_item = o_path.partialPathName()
            else:
                ch_item = ch_node

            # return a child that matches a name
            if isinstance(find_child, (str, unicode)) and find_child in o_path.partialPathName():
                # find the shape associated with the node object node.
                if with_shape:
                    fn_item = OpenMaya.MFnDagNode(m_iter.item())
                    c_count = fn_item.childCount()
                    if c_count:
                        for ch_i in xrange(c_count):
                            if fn_item.child(ch_i).hasFn(node_types[with_shape]):
                                return_data += ch_item,
                else:
                    if transform:
                        if has_fn(ch_node, 'transform'):
                            return_data += ch_item,
                    else:
                        return_data += ch_item,

            # return all children
            else:
                if transform:
                    if has_fn(ch_node, 'transform'):
                        return_data += ch_item,
                else:
                    return_data += ch_item,
            m_iter.next()
    return return_data


def get_children_obj(object_name, type_name=''):
    """
    return all children from this object name.
    :param object_name: the object to get children objects from.
    :param type_name: filter only the children of this type.
    :return: <tuple> child objects.
    """
    m_obj = get_m_obj(object_name)
    children = get_m_child(m_obj, transform=True)

    if not type_name:
        return children

    proper_children = ()
    for ch in children:
        if not has_fn(ch, type_name):
            continue
        proper_children += ch,
    return proper_children


def get_children_names(object_name, type_name=''):
    """
    return all children from this object name.
    :param object_name: the object to get children objects from.
    :param type_name: filter only the children of this type.
    :return: <tuple> child objects.
    """
    m_obj = get_m_obj(object_name)
    children = get_m_child(m_obj, transform=True, as_strings=True)

    if not type_name:
        return children

    proper_children = ()
    for ch in children:
        if not has_fn(get_m_obj(ch), type_name):
            continue
        proper_children += ch,
    return proper_children


def get_parent_name(object_name):
    """
    finds the parent node.
    :param object_name: <str> object to get the parent relative transform from.
    :return: <str> parent object node.
    """
    return get_transform_relatives(object_name, find_parent=True, as_strings=True)


def get_parent_obj(object_name):
    """
    finds the parent node.
    :param object_name: <str> object to get the parent relative transform from.
    :return: <str> parent object node.
    """
    return get_transform_relatives(object_name, find_parent=True, as_strings=True)


def get_transform_relatives(object_name='', find_parent='', find_child=False, with_shape='', as_strings=False):
    """
    get parent/ child transforms relative to the object name provided.
    :param object_name: <str> object name to search from in the scene.
    :param find_parent: <str>, <bool>, <int>
                        find the first parent or find this parent relative to the object name provided.
    :param find_child: <str>, <bool>, <int>
                        find all children or find this child relative to the object name provided.
    :param with_shape: <str> find the transform containing this shape.
    :param as_strings: <bool> return the data as string objects instead.
    :return: <dict> return a dictionary of items.
    """
    # transform_objects = get_scene_objects(node_type='kTransform')
    if not object_name:
        raise ValueError(
            "[GetTransformRelatives] :: object_name parameter is empty.")
    if not find_parent and not find_child:
        raise ValueError(
            "[GetTransformRelatives] :: Please supply either find_parent or find_child parameters.")

    # define variables
    return_data = ()
    m_object = get_m_obj(object_name)

    # transform relatives can only work on kDagNode type
    if not has_fn(m_object, 'dag'):
        return ()

    if m_object:
        if find_parent:
            return_data += tuple(get_m_parent(
                m_object, find_parent=find_parent, with_shape=with_shape, as_strings=as_strings)
            )
        elif find_child:
            return_data += tuple(get_m_child(
                m_object, find_child=find_child, with_shape=with_shape, as_strings=as_strings, transform=True)
            )
    return return_data


def get_connected_nodes(object_name="", find_node_type='animCurve',
                        as_strings=False, find_attr="", down_stream=True,
                        up_stream=False, with_shape=None, search_name="",
                        breadth=False, plug_level=True, node_level=False, depth=False):
    """
    get connected nodes from node provided.
    :param object_name: <str> string object to use for searching frOpenMaya.
    :param as_strings: <bool> return as string objects instead.
    :param find_attr: <str> find the node containing this attribute name.
    :param find_node_type: <OpenMaya.MFn> kObjectName type to find.
    :param down_stream: <bool> find nodes down stream.
    :param with_shape: <str> shape name.
    :param up_stream: <bool> find nodes up stream.
    :param breadth: <bool> find adjacent nodes.
    :param search_name: <str> search for this name. ** Not Implemented!
    """
    direction = None
    if down_stream:
        direction = OpenMaya.MItDependencyGraph.kDownstream
    if up_stream:
        direction = OpenMaya.MItDependencyGraph.kUpstream
    if breadth:
        direction = OpenMaya.MItDependencyGraph.kBreadthFirst
    if depth:
        direction = OpenMaya.MItDependencyGraph.kDepthFirst

    if plug_level:
        level = OpenMaya.MItDependencyGraph.kPlugLevel
    if node_level:
        level = OpenMaya.MItDependencyGraph.kNodeLevel

    if isinstance(object_name, (list, tuple)):
        node = object_name[0]
    if isinstance(object_name, (str, unicode)):
        node = get_m_obj(object_name)
    elif isinstance(object_name, OpenMaya.MObject):
        node = object_name
    elif isinstance(object_name, OpenMaya.MFnMesh):
        node = object_name.node()

    # find the node type associated with the string
    if find_node_type and isinstance(find_node_type, str):
        find_node_type = node_types[find_node_type]

    if find_node_type:
        dag_iter = OpenMaya.MItDependencyGraph(
            node,
            find_node_type,
            direction,
            level)
    else:
        dag_iter = OpenMaya.MItDependencyGraph(
            node,
            direction,
            level)
    dag_iter.reset()

    # iterate the dependency graph to find what we want.
    found_nodes = ()
    while not dag_iter.isDone():
        cur_item = dag_iter.currentItem()
        cur_fn = OpenMaya.MFnDependencyNode(cur_item)
        cur_name = cur_fn.name()
        if find_attr:
            # attrs = attribute_utils.Attributes(cur_name, custom=1)
            attrs = cmds.listAttr(cur_name)
            if attrs:
                find_relevant_attr = filter(lambda x: find_attr in x, attrs)
                if find_relevant_attr:
                    if as_strings:
                        if with_shape:
                            if check_fn_shape(cur_item, with_shape):
                                found_nodes += cur_name,
                        else:
                            found_nodes += cur_name,
                    else:
                        if with_shape:
                            if check_fn_shape(cur_item, with_shape):
                                found_nodes += cur_item,
                        else:
                            found_nodes += cur_item,
        else:
            if as_strings:
                if with_shape:
                    if check_fn_shape(cur_item, with_shape):
                        found_nodes += cur_name,
                else:
                    found_nodes += cur_name,
            else:
                if with_shape:
                    if check_fn_shape(cur_item, with_shape):
                        found_nodes += cur_name,
                else:
                    found_nodes += cur_item,
        dag_iter.next()
    return tuple(found_nodes)


def get_connected_anim(object_name=""):
    """
    get connected nodes from node provided.
    :param object_name: <str> string object to use for searching frOpenMaya.
    :param find_node_type: <OpenMaya.MFn> kObjectName type to find.
    """
    anim_c = cmds.listConnections(object_name, s=1, d=0, type='animCurve')
    anim_b = cmds.listConnections(object_name, s=1, d=0, type='blendWeighted')
    anim_curves = ()
    if not anim_c and anim_b:
        for blend_node in anim_b:
            anim_curves += tuple(cmds.listConnections(blend_node,
                                 s=1, d=0, type='animCurve'))
        return anim_curves
    else:
        return anim_c


def get_connected_nodes_gen(object_name=""):
    """
    nodes generator.
    :param object_name: <str> string object to use for searching frOpenMaya.
    """
    node = get_m_obj(object_name)
    dag_iter = OpenMaya.MItDependencyGraph(
        node,
        OpenMaya.MItDependencyGraph.kDownstream,
        OpenMaya.MItDependencyGraph.kPlugLevel)
    dag_iter.reset()

    while not dag_iter.isDone():
        yield dag_iter.currentItem()
        dag_iter.next()


def get_upstream_connected_nodes_gen(object_name=""):
    """
    nodes generator.
    :param object_name: <str> string object to use for searching frOpenMaya.
    """
    node = get_m_obj(object_name)

    dag_iter = OpenMaya.MItDependencyGraph(
        node,
        OpenMaya.MItDependencyGraph.kUpstream,
        OpenMaya.MItDependencyGraph.kPlugLevel)
    dag_iter.reset()

    while not dag_iter.isDone():
        yield dag_iter.currentItem()
        dag_iter.next()


def get_m_obj(object_str):
    """
    get MDagPath from MObject.
    :param object_str: <str> get the MObject from this parameter given.
    :return: <OpenMaya.MObject> the maya object.
    """
    try:
        string_array = (str, unicode)
    except NameError:
        string_array = str,
    if isinstance(object_str, string_array):
        try:
            om_sel = OpenMaya.MSelectionList()
            om_sel.add(object_str)
            node = OpenMaya.MObject()
            om_sel.getDependNode(0, node)
            return node
        except:
            raise RuntimeError(
                '[Get MObject] :: failed on {}'.format(object_str))
    return object_str


def get_m_dag(object_str=""):
    """
    get MDagPath from MObject.
    :param object_str: <str> get the MObject from this parameter given.
    :return: <OpenMaya.MObject> the maya object.
    """
    if not object_str:
        raise ValueError('[Get MObject] :: No object specified.')
    try:
        om_sel = OpenMaya.MSelectionList()
        om_sel.add(object_str)
        node = OpenMaya.MDagPath()
        om_sel.getDagPath(0, node)
        return node
    except:
        raise RuntimeError('[Get MObject] :: failed on {}'.format(object_str))


def get_mfn_obj(m_obj=None):
    """
    returns a function object node.
    :param m_obj: <MObject> m object node.
    :return: <MFnDependencyNode>
    """
    if isinstance(m_obj, basestring):
        return OpenMaya.MFnDependencyNode(get_m_obj(m_obj))
    elif isinstance(m_obj, OpenMaya.MObject):
        return OpenMaya.MFnDependencyNode(m_obj)


def get_mfn_dag(m_obj=None):
    """
    returns a function object node.
    :param m_obj: <MObject> m object node.
    :return: <MFnDependencyNode>
    """
    if isinstance(m_obj, basestring):
        return OpenMaya.MFnDagNode(get_m_obj(m_obj))
    elif isinstance(m_obj, OpenMaya.MObject):
        return OpenMaya.MFnDagNode(m_obj)


def get_m_dag_path(m_obj=None):
    """
    returns a function object node.
    :param m_obj: <MObject> m object node.
    :return: <MFnDependencyNode>
    """
    if isinstance(m_obj, basestring):
        return OpenMaya.MDagPath.getAPathTo(get_m_obj(m_obj))
    elif isinstance(m_obj, OpenMaya.MObject):
        return OpenMaya.MDagPath.getAPathTo(m_obj)


def get_mesh_points(object_name):
    """
    mesh points
    :param object_name: <str> find the vertices from this object.
    :return: <list> mesh vertex list.
    """
    mesh_fn, mesh_ob, mesh_dag = get_mesh_fn(object_name)
    mesh_it = OpenMaya.MItMeshVertex(mesh_ob)
    mesh_vertexes = []
    vprint("[Number of Vertices] :: {}".format(mesh_fn.numVertices()))
    while not mesh_it.isDone():
        mesh_vertexes.append(mesh_it.position())
        mesh_it.next()
    return mesh_vertexes


def get_mesh_points_cmds(object_name):
    """
    Mesh points
    :param object_name:
    :return:
    """
    mesh_vertices = cmds.ls(object_name + '.vtx[*]', flatten=1)
    vprint("[Number of Vertices] :: {}".format(len(mesh_vertices)))
    nums = []
    for i in mesh_vertices:
        nums.append(i)
    return nums


def get_selected_objects_gen():
    """
    returns a generator object for selected items.
    :return:
    """
    return iter(get_selected_node(single=False))


def get_mesh_fn(target):
    """
    get mesh function set for the given target
    :param target: dag path of the mesh
    :return <OpenMaya.MFnMesh>, mesh shape fn, <OpenMaya.MObject> shape object, <OpenMaya.MDagPath> the dag path.
    """

    if isinstance(target, str) or isinstance(target, unicode):
        slls = OpenMaya.MSelectionList()
        slls.add(target)
        ground_path = OpenMaya.MDagPath()
        slls.getDagPath(0, ground_path)
        ground_path.extendToShapeDirectlyBelow(0)
        ground_node = ground_path.node()
    elif isinstance(target, OpenMaya.MObject):
        ground_node = target
        ground_path = target
    elif isinstance(target, OpenMaya.MDagPath):
        ground_node = target.node()
        ground_path = target
    else:
        raise TypeError(
            'Must be of type str, MObject or MDagPath, is type: {}'.format(type(target)))

    if ground_node.hasFn(OpenMaya.MFn.kMesh):
        return OpenMaya.MFnMesh(ground_path), ground_node, ground_path
    else:
        raise TypeError('Target must be of type kMesh')


def create_container(name="", nodes=()):
    """
    creates container nodes. Only for containing controller utility nodes.
    :param name: <str> the name to create.
    :param nodes: <tuple> the array of nodes to lock in a container. If left empty, the container will add ndoes in.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not nodes:
        nodes = get_selected_node(single=False)
    if not nodes:
        return False
    if not cmds.objExists(name):
        cmds.container(name=name)
    if cmds.objectType(name) == 'container':
        for node in nodes:
            cmds.container(name, edit=True, addNode=node)
    else:
        return False
    return True


def set_object_transform(object_name, m=(), t=(), ws=True):
    """
    sets the object transformation values.
    :param object_name: <str> object name to use.
    :param m: <list> matrix list.
    :param t: <list> translation list.
    :param ws: <bool> worldSpace boolean.
    :return: <None>
    """
    if m:
        return cmds.xform(object_name, m=m, ws=ws)
    if t:
        return cmds.xform(object_name, t=t, ws=ws)


def get_object_transform(object_name, m=False, t=False, ws=True):
    """
    sets the object transformation values.
    :param object_name: <str> object name to use.
    :param m: <list> matrix list.
    :param t: <list> translation list.
    :param ws: <bool> worldSpace boolean.
    :return: <None>
    """
    return cmds.xform(object_name, m=m, t=t, ws=ws, q=1)


def snap_to_transform(source="", target="", matrix=False, translate=False, rotation=False):
    """
    grabs matrix information from target and applies to source transform.
    :param source: <str> source object name.
    :param target: <str> target object name.
    :param matrix: <bool> transfer the matrix values only.
    :param translate: <bool> transfer the translate values only.
    :param rotation: <bool> transfer the rotate values only.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not source:
        source = get_selected_node(single=False)[0]
    if not target:
        target = get_selected_node(single=False)[-1]
    if not source or not target:
        return False
    if matrix:
        s_xform = cmds.xform(target, m=1, ws=1, q=1)
        cmds.xform(source, m=s_xform, ws=1)
    if translate:
        s_xform = cmds.xform(target, t=1, ws=1, q=1)
        cmds.xform(source, t=s_xform, ws=1)
    if rotation:
        s_xform = cmds.xform(target, ro=1, q=1)
        cmds.xform(source, ro=s_xform)
    return True


def insert_transform(sel_obj='', name='', suffix_name=''):
    """
    insert a transform object above this given object.
    :param sel_obj: <str> maya scene object name.
    :param name: <str> name the new group node.
    :param suffix_name: <str> if provided, appends a suffix alternative name to the selected object.
    :return: <str> group name for success.
    """
    if not sel_obj:
        sel_obj = get_selected_node()
    if not sel_obj:
        return False
    if name:
        i_name = name
    elif suffix_name:
        i_name = sel_obj + '_{}'.format(suffix_name)
    else:
        i_name = sel_obj + '_par'
    mat = cmds.xform(sel_obj, q=1, ws=1, m=1)
    if not cmds.ls(i_name):
        grp = cmds.group(name=i_name, em=1)
        p_object = get_transform_relatives(sel_obj, find_parent=True)
        cmds.xform(grp, m=mat)
        cmds.parent(sel_obj, grp)
        if p_object:
            p_name = get_m_object_name(p_object[0])
            if p_name != 'world':
                cmds.parent(grp, p_name)
    return i_name


def zero_transforms(object_name=""):
    """
    zero out transformational values on the transform provided.
    :param object_name: <str> maya object name.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not object_name:
        return ValueError("[ZeroTransforms] :: Please provide object_name parameter.")
    # keyable_attrs = attribute_utils.Attributes(object_name, keyable=1, custom=0)
    keyable_attrs = cmds.listAttr(object_name, k=True, ud=False)
    # keyable_attrs.zero_attributes()
    for key_attr in keyable_attrs:
        cmds.setAttr(object_name + '.' + key_attr, 0)
    return True


def get_driver_object(object_name="", plugs=False):
    """
    return the driver object.
    :param object_name: <str> object name to get driver object frOpenMaya.
    :param plugs: <bool> find plugs from the object name.
    :return: <str>, <tuple> based on arguments given.
    """
    m_obj = get_connected_nodes(object_name,
                                find_node_type=OpenMaya.MFn.kTransform,
                                up_stream=True,
                                down_stream=False)
    m_object = m_obj[0]
    cur_fn = OpenMaya.MFnDependencyNode(m_object)
    cur_name = cur_fn.name()

    connected_plugs = ()
    for i in range(cur_fn.attributeCount()):
        a_obj = cur_fn.attribute(i)
        m_plug = OpenMaya.MPlug(m_object, a_obj)
        connected_plugs += m_plug.name(),
    if not plugs:
        return cur_name
    else:
        return connected_plugs


def get_plugs(o_node=None, source=True, ignore_nodes=(), ignore_attrs=(), attr_name=""):
    """
    get plugs
    :param o_node: <OpenMaya.MObject>, <str> object to find plugs frOpenMaya.
    :param source: <bool> if true, get the source plug connections.
    :param ignore_nodes: <bool> ignores select nodes and continues with the loop.
    :param ignore_attrs: <bool> ignores these attributes,
                                so no MayaNodeEditorSavedTabsInfo.tabGraphInfo[1].nodeInfo[49].dependNode
    :param attr_name: <str> get connection from this attribute only.
    :return:
    """
    if not isinstance(o_node, OpenMaya.MObject):
        o_node = get_m_obj(o_node)
    node_fn = OpenMaya.MFnDependencyNode(o_node)
    plug_names = ()
    for i in range(node_fn.attributeCount()):
        a_obj = node_fn.attribute(i)
        m_plug = OpenMaya.MPlug(o_node, a_obj)
        # m_plug_type_name = a_obj.apiTypeStr()
        m_plug_name = m_plug.name()
        if attr_name:
            if attr_name not in m_plug_name:
                continue
        if ignore_attrs:
            if [a for a in ignore_attrs if a in m_plug_name]:
                continue
        # print(m_plug_name, "isArray: ", m_plug.isArray(), "isCompound", m_plug.isCompound())
        m_plug_array = OpenMaya.MPlugArray()
        m_plug.connectedTo(m_plug_array, source, not source)
        plug_array_len = m_plug_array.length()
        for idx in range(plug_array_len):
            plug = m_plug_array[idx]
            plug_name = plug.name()
            plug_node = plug.node()
            if not ignore_nodes:
                plug_names += plug_name,
            elif ignore_nodes:
                if [ig for ig in ignore_nodes if has_fn(plug_node, ig)]:
                    plug_names += get_plugs(plug_name, source=source,
                                            ignore_nodes=ignore_nodes),
                else:
                    plug_names += plug_name,
    return plug_names


class Item(OpenMaya.MObject):
    NODE = None

    def __init__(self, *args):
        args = get_m_obj(*args),
        super(Item, self).__init__(*args)
        self.update_node_variable()

    def update_node_variable(self):
        self.NODE = OpenMaya.MFnDependencyNode(self)

    @property
    def node(self):
        return self.NODE

    def name(self):
        return self.node.name()

    def type(self):
        return self.apiTypeStr()

    def has_plug(self, attribute_name=""):
        """
        check if attribute exists for this node.
        :param attribute_name: <str> the attribute string to compare and check.
        :return: <bool> True for yes. <bool> False for no.
        """
        return filter(lambda x: attribute_name in x, self.get_plug_names(full_name=False))

    def source_plugs(self):
        """
        get all incoming connection plugs.
        :return: <tuple> array of plug names.
        """
        return get_plugs(self, source=True)

    def destination_plugs(self, ignore_nodes=()):
        """
        get all outgoing connection plugs.
        :return: <tuple> array of plug names.
        """
        return get_plugs(self, source=False, ignore_nodes=ignore_nodes)

    @property
    def attr_count(self):
        """
        count the number of available attributes for this node.
        :return: <int> attribute count.
        """
        return self.node.attributeCount()

    def get_plugs(self, name=''):
        """
        return an array of available plug objects by this item.
        :return: <tuple> plug arrays.
        """
        plugs = ()
        for a_i in range(self.attr_count):
            a_obj = self.node.attribute(a_i)
            a_plug = OpenMaya.MPlug(self, a_obj)
            if name and name in a_plug.name():
                plugs += a_plug,
            else:
                plugs += a_plug,
        return plugs

    def get_plug_obj(self, name=''):
        """
        return an attribute MObject by name.
        :param name: <str> get the plug object by this name.
        :return: <tuple> the plug object.
        """
        return self.get_plugs(name)

    def get_plug_names(self, full_name=True):
        """
        return an array of available plug objects by this item.
        :return: <tuple> plug arrays.
        """
        plugs = ()
        for a_i in range(self.attr_count):
            a_obj = self.node.attribute(a_i)
            if full_name:
                plugs += OpenMaya.MPlug(self, a_obj).name(),
            else:
                plugs += OpenMaya.MPlug(self,
                                        a_obj).name().rpartition('.')[-1],
        return plugs

    @staticmethod
    def split_attr_names(array_items=()):
        """
        split the attribute names from their dot separators.
        :return: <tuple> modified attribute array items.
        """
        return tuple([a.rpartition('.')[-1] for a in array_items])

    def filter_plugs_by_name(self, search=""):
        """
        filters the plug names by name.
        :param search: <str> the string name to filter the array with.
        :return: <tuple> array of filtered items.
        """
        return filter(lambda x: search in x, self.get_plug_names(full_name=False))

    def filter_plugs_by_regex(self, search="", ignore_case=False, dot_all=False, verbose=False):
        """
        filters the plugs by regex.
        :return: <tuple> filtered objects.
        """
        return self.filter_array_by_regex(self.get_plug_names(
            full_name=False), search=search, ignore_case=ignore_case, dot_all=dot_all, verbose=verbose)

    def filter_source_plugs_by_regex(self, search="", ignore_case=False, dot_all=False, verbose=False):
        """
        filters the source plugs by regex.
        :return: <tuple> filtered objects.
        """
        return self.filter_array_by_regex(
            self.source_plugs(), search=search, ignore_case=ignore_case, dot_all=dot_all, verbose=verbose)

    def filter_source_plugs_by_name(self, search=""):
        """
        filters the incoming plugs by name.
        :return: <tuple> array of filtered plug names.
        """
        return filter(lambda x: search in x, self.source_plugs())

    def filter_destination_plugs_by_regex(self, search="", ignore_case=False, dot_all=False, verbose=False):
        """
        filters the outgoing plugs by regex.
        :return: <tuple> filtered objects.
        """
        return self.filter_array_by_regex(
            self.destination_plugs(), search=search, ignore_case=ignore_case, dot_all=dot_all, verbose=verbose)

    def filter_source_plugs_by_name(self, search=""):
        """
        filters the outgoing plugs by name.
        :return: <tuple> array of filtered plug names.
        """
        return filter(lambda x: search in x, self.destination_plugs())

    @staticmethod
    def filter_array_by_regex(array_objects=(), search="", ignore_case=False, dot_all=False, verbose=False):
        """
        filters the array of names by regex.
        :param array_objects: <tuple> array of objects to filter from.
        :param search: <str> the string name to filter the array with.
        :param ignore_case: <bool> adds re.IGNORECASE flag to the re.compile
        :param dot_all: <bool> adds re.IGNORECASE flag to the re.compile
        :param verbose: <bool> adds re.VERBOSE flag to the re.compile
        :return: <tuple> array of filtered items.
        """
        if ignore_case:
            re_search = re.compile(search, re.I)
        elif dot_all:
            re_search = re.compile(search, re.S)
        elif verbose:
            re_search = re.compile(search, re.X)
        else:
            re_search = re.compile(search)
        return filter(lambda x: re_search.search(x), array_objects)

    def compare(self, m_obj=None):
        """
        compare against another MObject.
        :param m_obj: <OpenMaya.MObject>
        :return: <bool> True for good match. <bool> False for no match.
        """
        return compare_objects(self, m_obj, fn=True)


def create_node(node_type, node_name=""):
    """
    creates this node name.
    :param node_type: <str> create this type of node.
    :param node_name: <str> create a node with this name.
    :return: <str> node name.
    """
    if not cmds.objExists(node_name):
        return cmds.createNode(node_type, name=node_name)
    return node_name


def create_locator(name="", position=()):
    """
    creates the locator node.
    :param name: <str> name to use when creating a locator.
    :param position: <tuple> the position to set the transform node to.
    :return: <str> node.
    """
    node = create_node("locator", name+"Shape")
    # returns as locator shape, so we need to get the transform node.
    if has_fn(node, 'locator'):
        node = get_transform_relatives(
            node, find_parent=True, as_strings=True)[0]
    if position and len(position) == 3:
        set_object_transform(node, t=position)
    elif position and len(position) > 3:
        set_object_transform(node, m=position)
    return node


def create_group(name="", position=(), objects=()):
    """
    creates an empty transform group.
    :param name: <str> name to use when creating a group.
    :param position: <tuple> the position to set the transform node to.
    :param objects: <tuple> the objects to add to the empty group.
    :return: <str> transform node.
    """
    node = create_node("transform", name)
    if position and len(position) == 3:
        set_object_transform(node, t=position)
    elif position and len(position) > 3:
        set_object_transform(node, m=position)
    if objects:
        do_parent(objects, node)
    return node


def do_parent_constraint(master_obj, slave_obj, maintain_offset=True):
    """
    perform parent constraint
    :param master_obj: <str> driver object
    :param slave_obj: <str> driven object
    :param maintain_offset: <bool> let the child object maintain its offset when constrained to the master.
    :return: <str> parent constraint node.
    """
    return cmds.parentConstraint(master_obj, slave_obj, mo=maintain_offset)[0]


def do_pole_vector_constraint(master_obj, slave_obj):
    """
    perform parent constraint
    :param master_obj: <str> driver object
    :param slave_obj: <str> driven object
    :return: <str> parent constraint node.
    """
    return cmds.poleVectorConstraint(master_obj, slave_obj)[0]


def do_scale_constraint(master_obj, slave_obj, maintain_offset=True):
    """
    perform scale constraint
    :param master_obj: <str> driver object
    :param slave_obj: <str> driven object
    :param maintain_offset: <bool> let the child object maintain its offset when constrained to the master.
    :return: <str> scale constraint node.
    """
    return cmds.scaleConstraint(master_obj, slave_obj, mo=maintain_offset)[0]


def do_point_constraint(master_obj, slave_obj, maintain_offset=True):
    """
    perform point constraint
    :param master_obj: <str> driver object
    :param slave_obj: <str> driven object
    :param maintain_offset: <bool> let the child object maintain its offset when constrained to the master.
    :return: <str> point constraint node.
    """
    return cmds.pointConstraint(master_obj, slave_obj, mo=maintain_offset)[0]


def do_parent(child_obj, parent_obj):
    """
    perform parenting.
    :param child_obj: <str> child string object.
    :param parent_obj: <str> parent string object.
    :return: <bool> False if failure.
    """
    try:
        return cmds.parent(child_obj, parent_obj)
    except RuntimeError:
        cmds.warning(
            "[Could not parent: {} -> {}]".format(child_obj, parent_obj))
        return False


def do_connections(source_obj_attr, target_obj_attr):
    """
    perform connections from the source object attribute to the target object attribute
    :param source_obj_attr: <str> the source object.
    :param target_obj_attr: <str> the target object.
    :return: <bool> True for success. <bool> False for failure.
    """
    try:
        cmds.connectAttr(source_obj_attr, target_obj_attr, force=True)
    except RuntimeError:
        return False
    return True


def do_set_attr(source_node_attr, value):
    """
    set the attribute to the source node.
    :param source_node_attr: <str>
    :param value: <inputValue> the value to set on the attribute.
    :return: <bool> True for success. <bool> False for failure.
    """
    if isinstance(value, (int, float)):
        cmds.setAttr(source_node_attr, value)
        return True
    if isinstance(value, (list, tuple)):
        cmds.setAttr(source_node_attr, value, type="double3")
        return True
    if isinstance(value, (str, unicode)):
        cmds.setAttr(source_node_attr, value, type="string")
        return True
    return False


def unlock_attribute(source_attr):
    return cmds.setAttr(source_attr, l=False)


def lock_attribute(source_attr):
    return cmds.setAttr(source_attr, l=True)


def get_mdg_modifier():
    return OpenMaya.MDagModifier()
# ______________________________________________________________________________________________________________________
# object_utils.py
