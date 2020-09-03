"""
wire_utils for managing and manipulating wire deformers in Maya.

"""

# import maya modules
from maya import OpenMaya
from maya import OpenMayaAnim

# import local modules
from maya_utils import object_utils
from maya_utils import mesh_utils


def is_wire(object_name):
    """
    return true if the node object is of type wire.
    :return: <bool>
    """
    return bool(object_utils.has_fn(object_utils.get_m_obj(object_name), 'wire'))


def get_connected_wire_names(mesh_obj):
    """
    get connected wire from this mesh
    :param mesh_obj:
    :return:
    """
    return object_utils.get_connected_nodes(mesh_obj,
                                            find_node_type='wire',
                                            down_stream=False,
                                            up_stream=True,
                                            as_strings=True)


def get_connected_wire(mesh_obj):
    """
    get connected wire from this mesh
    :param mesh_obj:
    :return:
    """
    return object_utils.get_connected_nodes(mesh_obj, find_node_type='wire', down_stream=False, up_stream=True)


def get_connected_mesh_shape(wire_node=""):
    """
    gets the connected mesh this wire is acting on.
    :param wire_node:
    :return:
    """
    return object_utils.get_connected_nodes(wire_node, find_node_type='mesh', down_stream=True, up_stream=False)


def get_scene_wires(as_strings=False):
    """
    returns a array of valid wire deformers in the scene.
    :return: <dict> {OpenMaya.MObject: <str> wire node.}
    """
    wires = {}
    mesh_array = object_utils.get_scene_objects(node_type='mesh')
    for mesh_obj in mesh_array:
        obj_name = object_utils.get_m_object_name(mesh_obj)
        blend_node = get_connected_wire(mesh_obj)
        if blend_node:
            if as_strings:
                wires[obj_name] = object_utils.get_m_object_name(blend_node[0])
            else:
                wires[obj_name] = blend_node[0],
    return wires


def get_deformer_fn(object_name=""):
    """
    get a wire deformer fn
    :param object_name: <str> object name to get get wireDeformer function set from.
    :return: <OpenMaya.MFnWireDeformer> object type.
    """
    m_wire_obj = None
    if object_utils.is_transform(object_name):
        shape_obj = object_utils.get_shape_name(object_name)[0]
        m_wire_obj = get_connected_wire(shape_obj)[0]
    elif is_wire(object_name):
        m_wire_obj = object_utils.get_m_obj(object_name)
    return OpenMayaAnim.MFnWireDeformer(m_wire_obj)

