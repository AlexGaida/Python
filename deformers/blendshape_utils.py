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
    return true if the node object is of type blendShape.
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
        blend_fn.create(mesh_obj, origin, normal_chain)
    elif len(mesh_objects) > 1 and isinstance(mesh_objects, (tuple, list)):
        mesh_obj_array = object_utils.get_m_obj_array(mesh_objects)
        blend_fn.create(mesh_obj_array, origin, normal_chain)
    else:
        raise ValueError("Could not create blendshape.")

    if name:
        object_utils.rename_node(blend_fn.object(), name)
    return blend_fn


def find_blend_shape_index(target_name="", blend_name=""):
    """
    finds the index where the target resides.
    :param target_name:
    :param blend_name:
    :return:
    """
    shape_names = get_shapes(blend_name)
    for idx, shape in enumerate(shape_names):
        if target_name in shape:
            return idx
    return False


def add_in_between_target(shape_name, blend_name="", target_index=0, existing_target_name="", weight=0.5):
    """
    adds an in-between target.
    :param shape_name: <str> the in between shape to add.
    :param blend_name: <str> the blendShape to add.
    :param existing_target_name: <str> the existing target shape to find.
    :param target_index: <int> the target index to use when adding shapes.
    :param weight: <float> the weight value of the in between shape.
    :return:
    """
    # find the existing target index on the blend shape
    if not target_index:
        target_index = find_blend_shape_index(existing_target_name, blend_name=blend_name)
    if type(target_index) == bool:
        raise ValueError("[AddInBetweenTarget] :: No valid index found with name: {}".format(existing_target_name))
    # we need to round the weight step value
    return add_target(shape_name, blend_name, weight=weight, index=target_index)


def add_in_between_target_array(shapes_array, blend_name=""):
    """
    add in between targets to a blendShape node.
    :param shapes_array: <tuple>, <list> array of mesh shapes to add the in-betweens.
    :param blend_name: <str> the blendShape name to add targets to.
    :return: <bool> True for success. <bool> False for failure.
    """
    length_of_shapes = float(len(shapes_array) - 1)
    for idx, shape_name in enumerate(shapes_array):
        # we need to round the weight step value to no more than 3 significant digits
        weight_step = idx * int((1.0 / length_of_shapes) * 1000) / 1000.0
        add_in_between_target(shape_name, blend_name, weight=weight_step)
    return True


def remove_in_between_target(shape_name, blend_name="", target_index=0, existing_target_name="", weight=0.5):
    """
    removes an in-between target.
    :param shape_name: <str> the in between shape to add.
    :param blend_name: <str> the blendShape to add.
    :param existing_target_name: <str> the existing target shape to find.
    :param target_index: <int> the target index to use when adding shapes.
    :param weight: <float> the weight value of the in between shape.
    :return:
    """
    # find the existing target index on the blend shape
    if not target_index:
        target_index = find_blend_shape_index(existing_target_name, blend_name=blend_name)
    if type(target_index) == bool:
        raise ValueError("[AddInBetweenTarget] :: No valid index found with name: {}".format(existing_target_name))
    return remove_target(shape_name, blend_name, weight=weight, index=target_index)


def add_target(targets_array, blend_name="", weight=1.0, index=0):
    """
    adds a new target with the weight to this blend shape.
    Maya has a fail-safe to get the inputTargetItem from 6000-5000
    :param targets_array: <tuple> array of mesh shapes designated as targets.
    :param blend_name: <str> the blendShape node to add targets to.
    :param weight: <float> append this weight value to the target.
    :param index: <int> specify the index in which to add a target to the blend node.
    :return:
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    if isinstance(targets_array, (str, unicode)):
        targets_array = targets_array,
    targets_array = object_utils.get_m_shape_obj_array(targets_array)
    length = targets_array.length()
    if not index:
        index = get_weight_indices(blend_fn.name()).length() + 1
    # step = 1.0 / length - 1
    for i in xrange(0, length):
        # weight_idx = (i * step) * 1000/1000.0
        blend_fn.addTarget(base_obj, index, targets_array[i], weight)
    return True


def remove_target(targets_array, blend_name="", index=0, weight=1.0):
    """
    removes a blendshape target.
    :return:
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    if isinstance(targets_array, (str, unicode)):
        targets_array = targets_array,
    targets_array = object_utils.get_m_shape_obj_array(targets_array)
    length = targets_array.length()
    # step = 1.0 / length - 1
    for i in xrange(0, length):
        # weight_idx = (i * step) * 1000/1000.0
        blend_fn.removeTarget(base_obj, index, targets_array[i], weight)
    return True


def get_targets_at_index(blend_name="", index=0):
    """
    returns targets.
    :param blend_name: <str> the name of the blendShape node.
    :param index: <int> shape index.
    :return: <tuple> string array of targets at index.
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    obj_array = OpenMaya.MObjectArray()
    blend_fn.getTargets(base_obj, index, obj_array)
    return object_utils.convert_obj_array_to_string_array(obj_array)


def get_shapes(blend_name=""):
    """
    returns a dictionary data of all shapes from this blend shape object.
    :return: <tuple> array of shapes and targets.
    """
    shapes = ()
    indices = get_weight_indices(blend_name=blend_name)
    for i in xrange(indices.length()):
        shapes += get_targets_at_index(blend_name, indices[i])
        # shapes += get_target_item_index(blend_name, i)
    return shapes


def get_weight_indices(blend_name=""):
    """
    get the weight indices from the blendShape name provided.
    :param blend_name: <str> the name of the blendShape node.
    :return: <OpenMaya.MIntArray>
    """
    blend_fn = get_deformer_fn(blend_name)
    int_array = OpenMaya.MIntArray()
    blend_fn.weightIndexList(int_array)
    return int_array


def get_num_weights(blend_name=""):
    """
    get the weight indices from the blendShape name provided.
    :param blend_name: <str> the name of the blendShape node.
    :return: <OpenMaya.MIntArray>
    """
    return get_deformer_fn(blend_name).numWeights()


def get_target_item_index(blend_name="", index=0):
    """
    get the weight indices from the blendShape name provided.
    :param blend_name: <str> the name of the blendShape node.
    :param index: <int> the index of blendShape weights.
    :return: <OpenMaya.MIntArray>
    """
    blend_fn = get_deformer_fn(blend_name)
    base_obj = get_base_object(blend_name)[0]
    m_tgt_array = OpenMaya.MIntArray()
    blend_fn.targetItemIndexList(index, base_obj, m_tgt_array)
    return m_tgt_array


def delete_blendshapes(mesh_obj):
    """
    deletes all connected blendshape.
    :param mesh_obj:
    :return:
    """
    shape_obj = object_utils.get_shape_name(mesh_obj)[0]
    cmds.delete(get_connected_blendshape_names(shape_obj))


def get_base_objects(blend_name=""):
    """
    return the base objects associated with this blend shape node.
    :param blend_name: <str> the name of the blendShape node.
    :return: <tuple> array of base objects
    """
    m_obj_array = OpenMaya.MObjectArray()
    blend_fn = get_deformer_fn(blend_name)
    blend_fn.getBaseObjects(m_obj_array)
    return object_utils.convert_obj_array_to_string_array(m_obj_array)


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
