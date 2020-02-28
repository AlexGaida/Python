"""
module for dealing with deformers in Maya.
"""
# import maya modules
from maya import mel
from maya import cmds
from maya import OpenMaya as OpenMaya

# import local modules
from maya_utils import object_utils


def load_deformer_weights(file_name="", deformer_name=""):
    """
    loads the deformer weights
    :param file_name: <str>
    :param deformer_name: <str>
    :return: <bool> True for success.
    """
    cmds.deformerWeights(file_name, path=dir, deformer=deformer_name, im=1)
    return True


def save_deformer_skin_weights(skin_name="", directory_path_name=""):
    """
    saves the deformer skin weights.
    :param skin_name: <str>
    :param directory_path_name: <str> The directory path to save the skin weights to.
    :return: <bool> True for success.
    """
    cmds.deformerWeights(skin_name + '.skinWeights', path=directory_path_name, ex=1, deformer=skin_name)
    return True


def add_object_to_deformer(object_name="", deformer_name=""):
    """
    add an object to a specified deformer.
    :param object_name: <str> the object to add to a deformer set.
    :param deformer_name: <str> the deformer to use.
    :return: <bool> True for success.
    """
    return cmds.deformer(deformer_name, edit=True, g=object_name)


def remove_object_to_deformer(object_name="", deformer_name=""):
    """
    add an object to a specified deformer.
    :param object_name: <str> the object to add to a deformer set.
    :param deformer_name: <str> the deformer to add an object to.
    :return: <bool> True for success.
    """
    return cmds.deformer(deformer_name, edit=True, g=object_name, rm=True)


def add_selected_objects_to_deformer(deformer_name=""):
    """
    add selected objects to a specified deformer.
    :param deformer_name: <str> the deformer to add objects to.
    :return:
    """
    objects = object_utils.get_selected_node(single=False)
    for obj_name in objects:
        add_object_to_deformer(obj_name, deformer_name)
    return True


def get_m_object(object_name=""):
    return object_utils.get_m_obj(object_name)


def get_fn_shape(m_object=None, get_all=False):
    """
    get the shape from the object.
    :param m_object: <OpenMaya.MObject>
    :param get_all: <bool> get all child objects.
    :return: <OpenMaya.MObject> if True, <tuple> of list objects.
    """
    try:
        fn_item = OpenMaya.MFnDagNode(m_object)
    except TypeError:
        fn_item = OpenMaya.MFnDagNode(get_m_object(m_object))
    c_count = fn_item.childCount()
    collection = []
    if c_count:
        if not get_all:
            return fn_item.child(0)
        else:
            for c_i in xrange(c_count):
                collection.append(fn_item.child(c_i))
    return tuple(collection)


def get_all_fn_shapes(m_object=None):
    return get_fn_shape(m_object=m_object, get_all=True)


def get_mesh_fn(object_name=""):
    """
    returns a OpenMaya.MFnMesh() object.
    :param object_name: <str> object name to get the MeshFn class.
    :return: <OpenMaya.MFnMesh> object.
    """
    return OpenMaya.MFnMesh(get_fn_shape(object_utils.get_m_obj(object_name)))


def get_connected_blendshape_nodes(object_name="", as_strings=True):
    """
    grabs all the connected blendShape nodes.
    :param object_name: <str>
    :param as_strings: <bool>
    :return: <tuple> connected blend shape objects
    """
    collection = []
    for m_set in get_connected_object_sets(object_name):
        blend_node = object_utils.get_connected_nodes(m_set,
                                                      find_node_type=OpenMaya.MFn.kBlendShape,
                                                      up_stream=True,
                                                      down_stream=False,
                                                      as_strings=as_strings)
        if blend_node:
            collection.append(blend_node[0])
    return tuple(collection)


def get_connected_skincluster_nodes(object_name="", as_strings=True):
    """
    grabs the connected blendShape node.
    :param object_name: <str>
    :param as_strings: <bool>
    :return: <tuple> connected skin cluster objects
    """
    collection = []
    for m_set in get_connected_object_sets(object_name):
        skin_node = object_utils.get_connected_nodes(m_set,
                                                     find_node_type=OpenMaya.MFn.kSkinClusterFilter,
                                                     up_stream=1,
                                                     down_stream=0,
                                                     as_strings=as_strings)
        if skin_node:
            collection.append(skin_node[0])
    return tuple(collection)


def get_connected_object_sets(object_name=""):
    """
    grabs the connected blendShape node.
    :param object_name:
    :return:
    """
    return object_utils.get_connected_nodes(get_fn_shape(object_name),
                                            find_node_type=OpenMaya.MFn.kSet,
                                            up_stream=True,
                                            down_stream=False)


def get_deform_object_set_items(object_name=""):
    """
    get set items from deformer sets.
    :param object_name:
    :return:
    """
    for deform_set in get_connected_object_sets(object_name):
        m_sel = OpenMaya.MSelectionList()
        OpenMaya.MFnSet(deform_set).getMembers(m_sel, True)
        for i in xrange(m_sel.length()):
            node = OpenMaya.MObject()
            print m_sel.getDependNode(i, node)
            print object_utils._get_m_object_name(node)


def get_name(m_object=None):
    """
    grabs the string name of the MObject provided.
    :param m_object: <OpenMaya.MObject> the MObject to convert to a string name.
    :return: <str> node name.
    """
    return object_utils.get_m_object_name(m_object)


def extract_mesh_deltas(skin_mesh_name="", corrected_mesh_name=""):
    """
    extracts deltas from the mesh provided.
    :return: <str> corrective mesh name.
    """
    return mel.eval("extractDeltas -s {} -c {}".format(skin_mesh_name, corrected_mesh_name))


def get_blend_shape_name(object_name=''):
    return object_name + '_blend'


def create_blend_shape(mesh_name='', deform_order='', origin='local'):
    """
    creates a blend shape named by the mesh name provided.
    :param mesh_name: <str> the mesh name to attach blend shape to.
    :param deform_order: <str> the deformation order of attaching the blend shape to.
    :param origin: <str> 'local' or 'world'.
    :return: <str> blend shape name.
    """
    blend_name = get_blend_shape_name(mesh_name)
    if cmds.ls(blend_name):
        return blend_name
    if deform_order == 'after':
        return cmds.blendShape(mesh_name, name=blend_name, origin=origin, after=True)[0]
    elif deform_order == 'before':
        return cmds.blendShape(mesh_name, name=blend_name, origin=origin, before=True)[0]
    elif deform_order == 'parallel':
        return cmds.blendShape(mesh_name, name=blend_name, origin=origin, parallel=True)[0]
    elif deform_order == 'split':
        return cmds.blendShape(mesh_name, name=blend_name, origin=origin, split=True)[0]
    elif deform_order == 'foc':
        return cmds.blendShape(mesh_name, name=blend_name, origin=origin, foc=True)[0]
    else:
        return cmds.blendShape(mesh_name, name=blend_name, origin=origin)[0]


def add_target_shape(mesh_name="", target_mesh="", target_name="", target_value=1.0):
    """
    adds a target blend shape shape to this mesh.
    :param mesh_name: <str> the mesh name to attach blend shape to.
    :param target_mesh: <str> the target mesh.
    :param target_name: <str> the blendShape target attribute name.
    :param target_value: <float>
    :return: <str> blendShape name, attribute target.
    """
    blend_node = get_connected_blendshape_nodes(mesh_name)
    if not blend_node:
        blend_node = create_blend_shape(mesh_name, deform_order='before', origin='local')
    if blend_node:
        blend_node = blend_node[0]
    target_index = len(get_blendshape_targets(blend_node)) + 1
    if target_name:
        if not cmds.objExists(target_name):
            cmds.rename(target_mesh, target_name)
    cmds.blendShape(blend_node, edit=True, t=(mesh_name, target_index, target_name, target_value))
    return blend_node


def get_blend_target_attribute(mesh_name="", blend_node="", target_name=""):
    """
    get the blend shape target attribute.
    :param mesh_name: <str> mesh object name.
    :param target_name: <str> blendshape target name.
    :param blend_node: <str> optionally, blend shape node can be directly specified.
    :return: <str> blendShape target attribute name.
    """
    if not blend_node:
        blend_node = get_connected_blendshape_nodes(mesh_name)[0]
    return filter(lambda x: x[0].startswith(target_name), get_blendshape_targets(blend_node))


def get_blendshape_targets(blend_node=""):
    """
    return blend shape weight targets with respective indices.
    :param blend_node: <str> the blend shape node to check.
    :return: <tuple> weight name, index, weight value.
    """
    weight_attr = blend_node + '.weight'
    list_weight_inputs = cmds.listAttr(weight_attr, m=1)
    weight_value = cmds.getAttr(weight_attr)[0]
    shape_indices = range(1, len(list_weight_inputs or []) + 1)
    print(list_weight_inputs, shape_indices, weight_value)
    if shape_indices:
        return tuple(zip(list_weight_inputs, shape_indices, weight_value))
    else:
        return 0,


def remove_blendshape_target(mesh_name="", blend_name="", shape_name="", shape_index=""):
    """
    removes the blendshape target.
    :param mesh_name:
    :param blend_name:
    :param shape_name:
    :param shape_index:
    :return:
    """
    cmds.blendShape(blend_name, edit=True, remove=True, t=(mesh_name, shape_index, shape_name, 1.0))
