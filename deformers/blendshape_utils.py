"""
blendshape_utils for managing and manipulating blendshapes in Maya.

inputGeomTarget ... stores the The target geometry input ... (type: geometry)
inputPointsTarget ... stores the Delta values for points in a target geometry ... (type: pointArray)
inputComponentsTarget ... stores the Component list for points in a target geometry ... (type: componentList)
"""

# import standard modules
from maya import cmds

# import maya modules
from maya import OpenMayaAnim
from maya import OpenMaya

# import local modules
from maya_utils import object_utils

# define local variables
origin = OpenMayaAnim.MFnBlendShapeDeformer.kLocalOrigin
world_origin = OpenMayaAnim.MFnBlendShapeDeformer.kWorldOrigin
front_of_chain = OpenMayaAnim.MFnBlendShapeDeformer.kFrontOfChain
normal_chain = OpenMayaAnim.MFnBlendShapeDeformer.kNormal


def is_blendshape(object_name):
    """
    return true if object is of type blendShape
    :return: <bool>
    """
    return bool(object_utils.has_fn(object_utils.get_m_obj(object_name), 'blendShape'))


def get_connected_blendshape_names(mesh_obj):
    """
    get connected blendshape from this mesh
    :param mesh_obj:
    :return:
    """
    return object_utils.get_connected_nodes(mesh_obj,
                                            find_node_type='blendShape',
                                            down_stream=False,
                                            up_stream=True,
                                            as_strings=True)


def get_connected_blendshape(mesh_obj):
    """
    get connected blendshape from this mesh
    :param mesh_obj:
    :return:
    """
    return object_utils.get_connected_nodes(mesh_obj, find_node_type='blendShape', down_stream=False, up_stream=True)


def get_connected_mesh_shape(blend_node=""):
    """
    gets the connected mesh this blend shape is acting on.
    :param blend_node:
    :return:
    """
    return object_utils.get_connected_nodes(blend_node, find_node_type='mesh', down_stream=True, up_stream=False)


def get_scene_blendshapes():
    """
    returns a array of blendshapes in the scene.
    :return:
    """
    blendshapes = {}
    mesh_array = object_utils.get_scene_objects(node_type='mesh')
    for mesh_obj in mesh_array:
        obj_name = object_utils.get_m_object_name(mesh_obj)
        blend_node = get_connected_blendshape(mesh_obj)
        if blend_node:
            blendshapes[obj_name] = blend_node[0],
    return blendshapes


def get_deformer_fn(object_name=""):
    """
    get a blendshape deformer fn
    :param object_name: <str> object name to get get blendShapeDeformer function set from.
    :return: <OpenMaya.MFnBlendShapeDeformer> object type.
    """
    m_blend_obj = None
    if object_utils.is_transform(object_name):
        shape_obj = object_utils.get_shape_name(object_name)[0]
        m_blend_obj = get_connected_blendshape(shape_obj)[0]
    elif is_blendshape(object_name):
        m_blend_obj = object_utils.get_m_obj(object_name)
    return OpenMayaAnim.MFnBlendShapeDeformer(m_blend_obj)


def round_blend_step(step):
    """
    get the blendshape weight value
    :param step:
    :return:
    """
    return int(step * 1000) / 1000.0


def get_base_object(blend_name=""):
    """
    gets the connected base object to this blendShape node.
    :param blend_name:
    :return:
    """
    return get_connected_mesh_shape(blend_name)


def create_blendshape(mesh_objects, name=""):
    """
    creates a new blendShape from the array of mesh objects provided
    :param mesh_objects: <tuple> array of mesh shapes.
    :param name: <str> name of the blendshape.
    :return: <OpenMayaAnim.MFnBlendShapeDeformer>
    """
    blend_fn = OpenMayaAnim.MFnBlendShapeDeformer()
    if isinstance(mesh_objects, (str, unicode)):
        mesh_obj = object_utils.get_m_obj(mesh_objects)
        blend_fn.create(mesh_obj, origin)
    elif len(mesh_objects) > 1 and isinstance(mesh_objects, (tuple, list)):
        mesh_obj_array = object_utils.get_m_obj_array(mesh_objects)
        blend_fn.create(mesh_obj_array, origin, front_of_chain)
    else:
        raise ValueError("Could not create blendshape.")

    if name:
        object_utils.rename_node(blend_fn.object(), name)
    return blend_fn


def add_target(targets_array, blend_name="", weight=1.0):
    """
    adds a new target with the weight to this blend shape.
    Maya has a fail-safe to get the inputTargetItem from 6000-5000
    :param targets_array: <tuple> array of mesh shapes designated as targets.
    :param blend_name: <str> the blendShape node to add targets to.
    :return:
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    targets_array = object_utils.get_m_shape_obj_array(targets_array)
    length = targets_array.length()
    # step = 1.0 / length - 1
    for i in xrange(0, length):
        # weight_idx = (i * step) * 1000/1000.0
        blend_fn.addTarget(base_obj, 0, targets_array[i], weight)
    return True


def remove_target(targets_array, blend_name="", weight=1.0):
    """
    removes a blendshape target.
    :return:
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    targets_array = object_utils.get_m_shape_obj_array(targets_array)
    length = targets_array.length()
    # step = 1.0 / length - 1
    for i in xrange(0, length):
        # weight_idx = (i * step) * 1000/1000.0
        blend_fn.removeTarget(base_obj, 0, targets_array[i], weight)
    return True


def get_targets(blend_name=""):
    """
    returns targets.
    :return:
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    obj_array = OpenMaya.MObjectArray()
    blend_fn.getTargets(base_obj, 0, obj_array)
    return object_utils.convert_obj_array_to_string_array(obj_array)


def delete_blendshapes(mesh_obj):
    """
    deletes all connected blendshape.
    :param mesh_obj:
    :return:
    """
    shape_obj = object_utils.get_shape_name(mesh_obj)[0]
    cmds.delete(get_connected_blendshape_names(shape_obj))


def get_point_data(blend_name=""):
    """
    grabs the weight data.
    :param blend_name:
    :return:
    """
    m_blend_obj = object_utils.get_m_obj(blend_name)
    m_blend_node_fn = object_utils.get_fn(m_blend_obj)

    m_plug = m_blend_node_fn.findPlug('inputTarget').elementByPhysicalIndex(0).child(0).elementByPhysicalIndex(0).child(
        0).elementByPhysicalIndex(0)

    # if connected, retrieves the input target object and queries his points
    if m_plug.child(0).isConnected():
        input_geom_obj = m_plug.child(0).asMObject()
        target_points = OpenMaya.MPointArray()
        mesh_fn = OpenMaya.MFnMesh(input_geom_obj)
        mesh_fn.getPoints(target_points)
        return target_points

    # if not connected, retrieves the deltas and the affected component list
    else:
        input_point_target = m_plug.child(1).asMObject()
        input_comp_target = m_plug.child(2).asMObject()

        # to read the offset data, I had to use a MFnPointArrayData
        points_fn = OpenMaya.MFnPointArrayData(input_point_target)
        target_points = OpenMaya.MPointArray()
        points_fn.copyTo(target_points)

        # read the component list data was the trickiest part,
        # since I had to use MFnSingleIndexedComponent to extract (finally), an MIntArray
        # with the indices of the affected vertices

        component_list = OpenMaya.MFnComponentListData(input_comp_target)[0]
        index_fn = OpenMaya.MFnSingleIndexedComponent(component_list)
        target_indices = OpenMaya.MIntArray()
        index_fn.getElements(target_indices)
        if target_indices.length() == target_points.length():
            return target_points
