"""
Manipulating and traversing the Maya scene objects and connections.
"""

# import maya modules
from maya import cmds
from maya import OpenMaya as om
from maya import OpenMayaAnim as oma

# import local modules
import attribute_utils
import transform_utils

# define global variables
__node_types = {'nurbsCurve': om.MFn.kNurbsCurve, 'locator': om.MFn.kLocator}


def get_nice_name(object_name=''):
    """
    return a nice name from the object specified.
    :param object_name: <str> maya scene object name.
    :return: <str> nice name.
    """
    return '_'.join(object_name.split(':'))


def get_float_3_ptr():
    util = om.MScriptUtil()
    return util.asFloat3Ptr()


def get_unsigned_int_ptr(int_num=None):
    """
    returns an unsigned integer pointer object.
    :param int_num: <int> integer number to convert to a pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = om.MScriptUtil()
    util.createFromInt(int_num)
    return util.asIntPtr()


def get_unsigned_int(int_num=None):
    """
    returns an unsigned integer pointer object.
    :param int_num: <int> integer number to convert to a pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = om.MScriptUtil()
    util.createFromInt(int_num)
    return util.asInt()


def get_double_ptr():
    """
    returns an unsigned integer pointer object.
    :param int_num: <int> integer number to convert to a pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = om.MScriptUtil()
    util.createFromList([0.0, 0.0, 0.0], 3)
    return util.asDoublePtr()


def get_double4_ptr():
    """
    returns an unsigned integer pointer object.
    :param int_num: <int> integer number to convert to a pointer object.
    :return: <MScriptUtil.asIntPtr> integer pointer object.
    """
    util = om.MScriptUtil()
    return util.asDouble4Ptr()


def get_selected_node(single=True):
    """
    grabs the current name of the selected object.
    :return: <str> selected object. <str> empty list for failure.
    """
    if single:
        try:
            return cmds.ls(sl=1)[0]
        except IndexError:
            return ''
    return cmds.ls(sl=1)


def _get_m_object_name(m_object=om.MObject):
    """
    get the object name string.
    :param m_object: <OpenMaya.MObject> get the string of this object node.
    :return: <str> object name.
    """
    return om.MFnDependencyNode(m_object).name()


def get_object_types(find_str=""):
    """
    return a list of all OpenMaya object types.
    :return: <list> of object_type.
    """
    k_objects = filter(lambda k: k.startswith('k'), dir(om.MFn))
    return filter(lambda k: find_str in k, k_objects)


def get_m_anim_from_sel(object_node="", as_strings=False):
    """
    get animation curves from selected.
    :param object_node: <str> control object to get animation curve nodes from.
    :param as_strings: <bool> return string objects.
    :return: <list> anim curves.
    """
    if not object_node:
        object_node = get_selected_node()
    anim_nodes = {}
    anim_curve_nodes = get_connected_nodes(
            object_name=object_node, find_node_type=om.MFn.kAnimCurve, as_strings=as_strings,
            down_stream=False, up_stream=True, plug_level=True, node_level=False)
    for anim in anim_curve_nodes:
        if as_strings:
            anim_nodes[anim] = get_m_obj(anim)
        else:
            anim_nodes[get_m_object_name(anim)] = oma.MFnAnimCurve(anim)
    return anim_nodes


def get_m_object_name(m_object=None):
    """
    gets the name of the m object.
    :param m_object: <om.MObject> maya object.
    :return: <str> node name.
    """
    node_fn = om.MFnDependencyNode(m_object)
    return node_fn.name()


def get_scene_objects(name='', as_strings=False, node_type=''):
    """
    finds all objects in the current scene.
    :param as_strings: <bool> return a list of node strings instead of a list of OpenMaya.MObject(s).
    :param name: <str> get scene objects containing this name.
    :param node_type: <str> find this node type in the current scene.
    :return: <list> of scene items. <bool> False for failure.
    """
    scene_it = om.MItDependencyNodes()
    items = []
    while not scene_it.isDone():
        cur_item = scene_it.item()
        if not cur_item.isNull():
            if node_type:
                if node_type in cur_item.apiTypeStr().lower():
                    o_name = get_m_object_name(cur_item)
                    if name:
                        if name in o_name:
                            if as_strings:
                                items.append(o_name)
                            else:
                                items.append(cur_item)
                    elif not name and as_strings:
                        items.append(o_name)
                    elif not name and not as_strings:
                        items.append(cur_item)
            else:
                items.append(cur_item)
        scene_it.next()
    return items


def _confirm_fn_shape(m_object=None, m_type=None):
    """
    confirm the shape type for this object.
    :param m_object: <OpenMaya.MObject>
    :param m_type: <OpenMaya.MFn.kType>
    :return: <OpenMaya.MObject> if True, <NoneType> False if not.
    """
    fn_item = om.MFnDagNode(m_object)
    c_count = fn_item.childCount()
    if c_count:
        if fn_item.child(0).hasFn(m_type):
            return m_object
    return None


def get_parents(object_name=None, stop_at=''):
    """
    get parents
    :param object_name:
    :param stop_at:
    :return:
    """
    m_object = get_m_obj(object_name)
    fn_object = om.MFnDagNode(m_object)
    return_data = []
    par_count = fn_object.parentCount()
    if par_count:
        o_arr = om.MDagPathArray()
        fn_object.getAllPaths(o_arr)
        length = o_arr.length()
        for i in xrange(length):
            m_path = o_arr[i]
            p_node_ls = m_path.fullPathName().split('|')
            p_node_ls.reverse()
            for p in p_node_ls:
                return_data.append(p)
                if p == stop_at:
                    break
    return return_data


def _get_m_parent(m_object=None, find_parent='', with_shape='', as_strings=False):
    """
    finds the parent from the maya object provided.
    :param m_object: <OpenMaya.MObject> the object to get the parents from.
    :param find_parent: <str> find this parent from the object provided.
    :param with_shape: <str> find a parent containing this shape object.
    :return: <list> found objects.
    """
    fn_object = om.MFnDagNode(m_object)
    return_data = []
    par_count = fn_object.parentCount()
    if par_count:
        if isinstance(find_parent, (str, unicode)):
            o_arr = om.MDagPathArray()
            fn_object.getAllPaths(o_arr)
            length = o_arr.length()
            for i in xrange(length):
                m_path = o_arr[i]
                p_node_ls = m_path.fullPathName().split('|')
                found = filter(lambda x: find_parent in x.rpartition(':')[-1], p_node_ls)
                if found:
                    if as_strings:
                        return_data.extend(found)
                    else:
                        return_data.append(get_m_obj(found))
        elif isinstance(find_parent, (int, bool)):
            if as_strings:
                return_data.append(_get_m_object_name(fn_object.parent(0)))
            else:
                return_data.append(fn_object.parent(0))
    return return_data


def _get_m_child(m_object=None, find_child='', with_shape='', as_strings=False):
    """
    finds the child from the maya object provided.
    :param m_object: <OpenMaya.MObject> the object to get the parents from.
    :param find_child: <str> find this child from the object provided.
    :param with_shape: <str> find a child containing this shape object.
    :param as_strings: <bool> return as string objects instead.
    :return: <list> found objects.
    """
    fn_object = om.MFnDagNode(m_object)
    return_data = []
    if find_child:
        ch_count = fn_object.childCount()
        if ch_count:
            m_dag = om.MDagPath()
            fn_object.getPath(m_dag)
            m_iter = om.MItDag(om.MItDag.kBreadthFirst)
            m_iter.reset(m_dag)

            # iterate from the dag path provided
            while not m_iter.isDone():
                o_path = om.MDagPath()
                m_iter.getPath(o_path)
                ch_name = o_path.partialPathName()

                # return a child that matches a name
                if isinstance(find_child, (str, unicode)) and find_child in ch_name:

                    # find the shape associated with the node object node.
                    if with_shape:
                        fn_item = om.MFnDagNode(m_iter.item())
                        c_count = fn_item.childCount()
                        if c_count:
                            if fn_item.child(0).hasFn(__node_types[with_shape]):
                                return_data.append(ch_name)
                    else:
                        return_data.append(ch_name)

                # return all children
                elif isinstance(find_child, (bool, int)):
                    return_data.append(ch_name)
                m_iter.next()

    return return_data


def get_transform_relatives(object_name='', find_parent=False, find_child=False, with_shape='', as_strings=False):
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
        raise ValueError("[GetTransformRelatives] :: object_name parameter is empty.")
    if not find_parent and not find_child:
        raise ValueError("[GetTransformRelatives] :: Please supply either find_parent or find_child parameters.")

    # define variables
    return_data = []
    m_object = get_m_obj(object_name)

    if m_object:
        if find_parent:
            return_data.extend(_get_m_parent(
                m_object, find_parent=find_parent, with_shape=with_shape, as_strings=as_strings)
            )
        elif find_child:
            return_data.extend(_get_m_child(
                m_object, find_child=find_child, with_shape=with_shape, as_strings=as_strings)
            )
    return return_data


def get_connected_nodes(object_name="", find_node_type=om.MFn.kAnimCurve,
                        as_strings=False, find_attr="", down_stream=True,
                        up_stream=False, with_shape=None, plugs=False):
    """
    get connected nodes from node provided.
    :param object_name: <str> string object to use for searching from.
    :param as_strings: <bool> return as string objects instead.
    :param find_attr: <str> find the node containing this attribute name.
    :param find_node_type: <om.MFn> kObjectName type to find.
    :param down_stream: <bool> find nodes down stream.
    :param with_shape: <str> shape name.
    :param up_stream: <bool> find nodes up stream.
    """
    direction = None
    if up_stream:
        direction = om.MItDependencyGraph.kUpstream
    if down_stream:
        direction = om.MItDependencyGraph.kDownstream
    node = get_m_obj(object_name)
    dag_iter = om.MItDependencyGraph(
        node,
        find_node_type,
        direction)
    dag_iter.reset()

    # iterate the dependency graph to find what we want.
    found_nodes = []
    while not dag_iter.isDone():
        cur_item = dag_iter.currentItem()
        cur_fn = om.MFnDependencyNode(cur_item)
        cur_name = cur_fn.name()

        if find_attr:
            attrs = attribute_utils.Attributes(cur_item, custom=1)
            if attrs:
                find_relevant_attr = filter(lambda x: find_attr in x, attrs.keys)
                if find_relevant_attr:
                    if as_strings:
                        if with_shape:
                            if _confirm_fn_shape(cur_item, with_shape):
                                found_nodes.append(cur_name)
                        else:
                            found_nodes.append(cur_name)
                    else:
                        if with_shape:
                            if _confirm_fn_shape(cur_item, with_shape):
                                found_nodes.append(cur_item)
                        else:
                            found_nodes.append(cur_item)
        else:
            if as_strings:
                if with_shape:
                    if _confirm_fn_shape(cur_item, with_shape):
                        found_nodes.append(cur_name)
                else:
                    found_nodes.append(cur_name)
            else:
                if with_shape:
                    if _confirm_fn_shape(cur_item, with_shape):
                        found_nodes.append(cur_name)
                else:
                    found_nodes.append(cur_item)
        dag_iter.next()
    return found_nodes


def get_connected_anim(object_name=""):
    """
    get connected nodes from node provided.
    :param object_name: <str> string object to use for searching from.
    :param find_node_type: <om.MFn> kObjectName type to find.
    """
    anim_c = cmds.listConnections(object_name, s=1, d=0, type='animCurve')
    anim_b = cmds.listConnections(object_name, s=1, d=0, type='blendWeighted')
    anim_curves = []
    if not anim_c and anim_b:
        for blend_node in anim_b:
            anim_curves.extend(cmds.listConnections(blend_node, s=1, d=0, type='animCurve'))
        return anim_curves
    else:
        return anim_c


def get_connected_nodes_gen(object_name=""):
    """
    nodes generator.
    :param object_name: <str> string object to use for searching from.
    :param find_node_type: <om.MFn> kObjectName type to find.
    """
    node = get_m_obj(object_name)
    dag_iter = om.MItDependencyGraph(
        node,
        om.MItDependencyGraph.kDownstream,
        om.MItDependencyGraph.kPlugLevel)
    dag_iter.reset()

    while not dag_iter.isDone():
        yield dag_iter.currentItem()
        dag_iter.next()


def get_m_obj(object_str=""):
    """
    get MDagPath from MObject.
    :param object_str: <str> get the MObject from this parameter given.
    :return: <OpenMaya.MObject> the maya object.
    """
    if not object_str:
        raise ValueError('[Get MObject] :: No object specified.')
    try:
        om_sel = om.MSelectionList()
        om_sel.add(object_str)
        node = om.MObject()
        om_sel.getDependNode(0, node)
        return node
    except:
        raise RuntimeError('[Get MObject] :: failed on {}'.format(object_str))


def get_m_dag(object_str=""):
    """
    get MDagPath from MObject.
    :param object_str: <str> get the MObject from this parameter given.
    :return: <OpenMaya.MObject> the maya object.
    """
    if not object_str:
        raise ValueError('[Get MObject] :: No object specified.')
    try:
        om_sel = om.MSelectionList()
        om_sel.add(object_str)
        node = om.MDag()
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
        return om.MFnDependencyNode(get_m_obj(m_obj))
    elif isinstance(m_obj, om.MObject):
        return om.MFnDependencyNode(m_obj)


def get_mfn_dag(m_obj=None):
    """
    returns a function object node.
    :param m_obj: <MObject> m object node.
    :return: <MFnDependencyNode>
    """
    if isinstance(m_obj, basestring):
        return om.MFnDagNode(get_m_obj(m_obj))
    elif isinstance(m_obj, om.MObject):
        return om.MFnDagNode(m_obj)


def get_m_dag_path(m_obj=None):
    """
    returns a function object node.
    :param m_obj: <MObject> m object node.
    :return: <MFnDependencyNode>
    """
    if isinstance(m_obj, basestring):
        return om.MDagPath.getAPathTo(get_m_obj(m_obj))
    elif isinstance(m_obj, om.MObject):
        return om.MDagPath.getAPathTo(m_obj)


def get_mesh_points(object_name):
    """
    mesh points
    :param object_name: <str> find the vertices from this object.
    :return: <list> mesh vertex list.
    """
    mesh_fn, mesh_ob, mesh_dag = get_mesh_fn(object_name)
    mesh_it = om.MItMeshVertex(mesh_ob)
    mesh_vertexes = []
    print("[Number of Vertices] :: {}".format(mesh_fn.numVertices()))
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
    print("[Number of Vertices] :: {}".format(len(mesh_vertices)))
    nums = []
    for i in mesh_vertices:
        nums.append(i)
    return nums


def get_mesh_fn(target):
    """
    get mesh function set for the given target
    :param target: dag path of the mesh
    :return MFnMesh
    """

    if isinstance(target, str) or isinstance(target, unicode):
        slls = om.MSelectionList()
        slls.add(target)
        ground_path = om.MDagPath()
        slls.getDagPath(0, ground_path)
        ground_path.extendToShapeDirectlyBelow(0)
        ground_node = ground_path.node()
    elif isinstance(target, om.MObject):
        ground_node = target
        ground_path = target
    elif isinstance(target, om.MDagPath):
        ground_node = target.node()
        ground_path = target
    else:
        raise TypeError('Must be of type str, MObject or MDagPath, is type: {}'.format(type(target)))

    if ground_node.hasFn(om.MFn.kMesh):
        return om.MFnMesh(ground_path), ground_node, ground_path
    else:
        raise TypeError('Target must be of type kMesh')


def create_container(name=""):
    """
    creates container nodes. Only for containing controller utility nodes.
    :return: <bool> True for success. <bool> False for failure.
    """
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


def insert_transform(sel_obj='', name=''):
    """
    insert a transform object above this given object.
    :param sel_obj: <str> maya scene object name.
    :param name: <str> name the new group node.
    :return: <str> group name for success.
    """
    if not sel_obj:
        sel_obj = get_selected_node()
    if not sel_obj:
        return False
    if name:
        i_name = name
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
    keyable_attrs = attribute_utils.Attributes(object_name, keyable=1)
    keyable_attrs.zero_attributes()
    return True


def mirror_transforms(object_name=""):
    """
    mirror the transform controllers. **Must have corresponding left/ right naming.
    :param object_name: <str>
    :return: <bool> True for success.
    """
    if not object_name:
        object_name = get_selected_node(single=True)
    mirror_obj_name = ''
    if '_l_' in object_name:
        mirror_obj_name = object_name.replace('_l_', '_r_')
    if '_r_' in object_name:
        mirror_obj_name = object_name.replace('_r_', '_l_')
    p_object = get_transform_relatives(object_name, find_parent=True, as_strings=True)[0]
    p_mirror_object = get_transform_relatives(mirror_obj_name, find_parent=True, as_strings=True)[0]
    p_trm = transform_utils.Transform(p_object)
    matrix = p_trm.world_matrix()
    mirror_matrix = p_trm.mirror_matrix(matrix)
    cmds.xform(p_mirror_object, m=mirror_matrix, ws=1)
    return True


def create_locators():
    """
    create locators on position
    """
    for sl in cmds.ls(sl=1):
        locator_name = sl + '_loc'
        cmds.createNode('locator', name=locator_name + 'Shape')
        snap_to_transform(locator_name, sl, matrix=True)
    return True


def get_driver_object(object_name="", plugs=False):
    """
    return the driver object.
    :param object_name:
    :param plugs:
    :return:
    """
    m_obj = get_connected_nodes(object_name, find_node_type=om.MFn.kTransform, up_stream=True,
                                down_stream=False)
    m_object = m_obj[0]
    cur_fn = om.MFnDependencyNode(m_object)
    cur_name = cur_fn.name()

    connected_plugs = []
    for i in range(cur_fn.attributeCount()):
        a_obj = cur_fn.attribute(i)
        m_plug = om.MPlug(m_object, a_obj)
        connected_plugs.append(m_plug.name())
    if not plugs:
        return cur_name
    else:
        return connected_plugs


def set_ctrl_color(color='yellow'):
    """
    sets the color on the MFn.kNurbsCurve
    :param color: <str>, <list>, <list> color property.
    :return: <bool> True for success. <bool> False for failure.
    """
    for ctrl in cmds.ls(sl=1):
        cmds.setAttr(ctrl + 'Shape.overrideEnabled', 1)
        cmds.setAttr(ctrl + 'Shape.overrideRGBColors', 1)
        if isinstance(color, (str, unicode)):
            if color == 'yellow':
                cmds.setAttr(ctrl + 'Shape.overrideColorRGB', 1.0, 1.0, 0.0, type='double3')
            if color == 'blue':
                cmds.setAttr(ctrl + 'Shape.overrideColorRGB', 0.0, 0.0, 1.0, type='double3')
            if color == 'red':
                cmds.setAttr(ctrl + 'Shape.overrideColorRGB', 1.0, 0.0, 0.0, type='double3')
        elif isinstance(color, (list, tuple)):
            r, g, b = color
            cmds.setAttr(ctrl + 'Shape.overrideColorRGB', r, g, b, type='double3')
    return True


def zero_all_controllers():
    """
    zeroes out all the scene controllers.
    :return: <bool> True for success.
    """
    all_controllers = cmds.ls('*_ctrl')
    for ctrl_name in all_controllers:
        c_attr = attribute_utils.Attributes(ctrl_name, keyable=True)
        if c_attr.non_zero_attributes():
            c_attr.zero_attributes()
    return True


def set_joint_labels():
    """
    names the joint labels
    :return: <bool> True for success.
    """
    joints = cmds.ls('*_bnd_jnt', type='joint')
    for j_name in joints:
        cmds.setAttr(j_name + ".type", 18)
        if j_name.startswith('l_'):
            side = 'l'
            cmds.setAttr(j_name+".side", 1)
        if j_name.startswith('c_'):
            side = 'c'
            cmds.setAttr(j_name + ".side", 0)
        if j_name.startswith('r_'):
            side = 'r'
            cmds.setAttr(j_name + ".side", 2)
        if side:
            cmds.setAttr(j_name+'.otherType', j_name.replace(side, ''), type='string')
    return True


def mirror_object(control_name="", mirror_obj_name=""):
    """
    mirrors the selected object. If mirror object is not supplied, then mirror the supplied object directly.
    :param control_name: <str> controller object to get transformational values from.
    :param mirror_obj_name: <str> the object to receive mirror information.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not control_name:
        control_name = get_selected_node(single=True)
    if not control_name:
        return False

    # mirror the world matrix
    c_transform = transform_utils.Transform(control_name)
    w_matrix = c_transform.world_matrix()
    mir_matrix = c_transform.mirror_matrix(w_matrix)
    cmds.xform(control_name, m=mir_matrix, ws=1)
    rotation_values = cmds.xform(control_name, ro=1, q=1)
    # mirror rotate y
    rotation_values[1] *= -1

    # mirror rotate z
    rotation_values[2] *= -1

    if not mirror_obj_name:
        cmds.xform(control_name, ro=rotation_values)
    else:
        cmds.xform(mirror_obj_name, ro=rotation_values)
    return True


def get_plugs(o_node=None, source=True, ignore_unit_nodes=False):
    """
    get plugs
    :param o_node: <OpenMaya.MObject>, <str> object to find plugs from.
    :param source: <bool> if true, get the source plug connections.
    :param ignore_unit_nodes: <bool> ignores unit nodes if it encounters them.
    :return:
    """
    if not isinstance(o_node, om.MObject):
        o_node = get_m_obj(o_node)
    node_fn = om.MFnDependencyNode(o_node)
    plug_names = []
    for i in range(node_fn.attributeCount()):
        a_obj = node_fn.attribute(i)
        m_plug_array = om.MPlugArray()
        m_plug = om.MPlug(o_node, a_obj)
        m_plug.connectedTo(m_plug_array, source, not source)
        plug_array_len = m_plug_array.length()
        for idx in range(plug_array_len):
            plug = m_plug_array[idx]
            plug_name = plug.name()
            if not ignore_unit_nodes:
                plug_names.append(plug_name)
            elif ignore_unit_nodes:
                if plug_name.startswith('unitConversion') or plug_name.startswith('blendWeighted'):
                    plug_names.extend(get_plugs(plug_name, source=source))
    return plug_names


class Item(om.MObject):
    def __init__(self, *args):
        super(Item, self).__init__(*args)

    def name(self):
        return om.MFnDependencyNode(self).name()

    def type(self):
        return self.apiTypeStr()

    def source_plugs(self):
        return get_plugs(self, source=True)

    def destination_plugs(self):
        return get_plugs(self, source=False)
