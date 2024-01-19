"""
Querying, getting and setting skincluster information.
"""
# import standard modules
import time

# import maya modules
from maya import cmds
from maya import utils
from maya import OpenMaya
from maya import OpenMayaAnim

# import local modules
from maya_utils import object_utils
from maya_utils import file_utils
from maya_utils import mesh_utils

# define private variables
__version__ = "1.0.0"

def get_mesh_shape(mesh_name=""):
    """
    returns the mesh shape object name from the mesh transform name provided.
    :param mesh_name: <str> mesh transform object name.
    :return: <str> mesh shape name.
    """
    return object_utils.get_shape_name(mesh_name, 'mesh')[0]

def get_connected_skin_cluster(shape_name=""):
    """
    gets the connected skin cluster name.
    :param shape_name: <str> the object name to start the search frOpenMaya.
    :return: <str> skin cluster node name.
    """
    return object_utils.get_connected_nodes(
        shape_name,
        find_node_type=OpenMaya.MFn.kSkinClusterFilter,
        down_stream=False,
        up_stream=True,
        as_strings=True)

def get_attached_skincluster(mesh_name=""):
    """
    grabs the skin cluster node from the mesh transform provided.
    :param mesh_name: <str> mesh transform object name.
    :return: <str> skin cluster node name.
    """
    return get_connected_skin_cluster(
        get_mesh_shape(
            mesh_name)
    )

def get_mesh_from_skin(skin_name=""):
    """
    return the name of the mesh_object from skincluster object.
    :param skin_name:
    :return:
    """
    mesh_obj = object_utils.get_connected_nodes(skin_name,
                                                find_node_type='mesh',
                                                up_stream=False, depth=True)
    return object_utils.get_m_object_name(mesh_obj[0])

def get_mesh_fn_from_skin(skin_name=""):
    """

    :param skin_name:
    :return:
    """
    return OpenMaya.MFnMesh(object_utils.get_connected_nodes(skin_name, find_node_type='mesh',
                                                             up_stream=False, depth=True)[0])

def get_mesh_dag_from_skin(skin_name=""):
    """
    return the mesh dag path from skin cluster name provided.
    :param skin_name:
    :return:
    """
    return object_utils.get_m_dag(get_mesh_from_skin(skin_name))

def restore_dag_pose(influences=()):
    """
    restores the dag pose from the influences given.
    :param influences: <list> the influence objects to acting on the skin cluster.
    :return: <bool> True for success. <bool> False for failure.
    """
    try:
        cmds.dagPose(influences, restore=True, g=True, bindPose=True)
    except RuntimeError:
        return False
    return True

def get_existing_influences(skin_name=""):
    """
    find existing influences acting on the skin cluster.
    :param skin_name: <str> the skin cluster to add influences to.
    :return: <list> skin influences.
    """
    return cmds.ls(cmds.skinCluster(skin_name, query=True, weightedInfluence=True), l=True)

def add_influences(skin_name="", influences=[]):
    """
    adding influences to the designated skin cluster.
    :param skin_name: <str> the skin cluster to add influences to.
    :param influences: <list> the influence objects to add to the skin cluster.
    :return: <bool> True for success.
    """
    current_influences = get_existing_influences(skin_name)
    new_influences = tuple(set(current_influences) - set(influences))

    # add the objects not part of the current influences to the skin cluster provided.
    for influence in new_influences:
        cmds.skinCluster(
            skin_name,
            edit=True,
            addInfluence=influence,
            weight=0.0
        )
    return True

def copy_skin_weights(source_skin="", target_skin=""):
    """
    copy the skin weights from one to another.
    :param source_skin: <str> the source skin cluster.
    :param target_skin: <str> the destination skin cluster.
    :return: <bool> True for success.
    """
    cmds.copySkinWeights(sourceSkin=source_skin,
                         destinationSkin=target_skin,
                         noMirror=True,
                         surfaceAssociation="closestComponent",
                         influenceAssociation=["closestJoint", "oneToOne", "label"],
                         normalize=True)
    return True

def get_skin_name(object_name=""):
    """
    creates a new skin cluster name from the object provided.
    :param object_name: <str> object name to get the name frOpenMaya.
    :return: <str> new skin name.
    """
    return object_name + '_Skin'

def apply_skin(object_name="", influences=(), name=""):
    """
    creates the skin cluster object to the objects specified in the parameters given.
    :param object_name: <str> the mesh object to bind the influences to.
    :param influences: <list> list of influences to bind the geometry to.
    :param name: <str> name of the skin cluster created.
    :return: <list> skinCluster node.
    """
    if not isinstance(influences, (list, tuple, set)):
        influences = list(influences)
    return cmds.skinCluster(influences,
                            object_name,
                            name=name,
                            bindMethod=1,
                            skinMethod=0,
                            dropoffRate=3.5,
                            obeyMaxInfluences=1)

def create_skin_cluster(mesh_name="", influences=[]):
    """
    creates the skin cluster object to the mesh object provided.
    :param mesh_name: <str> the mesh to create skin cluster on.
    :param influences: <list> list of influences to add to the new skin cluster.
    :return: <bool> True for success.
    """
    skin_name = get_attached_skincluster(mesh_name)
    if not skin_name:
        return apply_skin(mesh_name, influences, name=get_skin_name(mesh_name))
    return skin_name

def copy_skincluster(source_mesh="", target_mesh=""):
    """
    copies the skincluster from the source skin name, to the target skin name.
    :param source_mesh: <str> the source mesh to get the influences and weights frOpenMaya.
    :param target_mesh: <str> the target mesh to add influences and weights to.
    :return: <bool> True for success.
    """
    # define variables
    source_skin = get_attached_skincluster(source_mesh)
    source_influences = get_existing_influences(source_skin)
    if not source_skin:
        return False
    target_skin = get_attached_skincluster(target_mesh)
    if target_skin:
        add_influences(target_skin, source_influences)
    else:
        target_skin = create_skin_cluster(target_mesh, source_influences)
    # copy the skins
    copy_skin_weights(source_skin[0], target_skin[0])
    return True

def skin_as():
    """
    selection based skin transfer.
    :return: <bool> True for success.
    """
    source_object_name = cmds.ls(sl=1)[0]
    destination_objects = cmds.ls(sl=1)[1:]
    for dest_obj in destination_objects:
        copy_skincluster(source_object_name, dest_obj)
    return True

def get_skin_fn(skin_name=""):
    """
    Get the <MFnSkinCluster> class type from name prov_ided.
    :param skin_name: <str> skin cluster node name.
    :return: <MFnSkinCluster> for success. <bool> False  for failurre.
    """
    if not skin_name:
        return False
    # get the MFnSkinCluster for clusterName
    m_selection = OpenMaya.MSelectionList()
    m_selection.add(skin_name)
    m_cluster = OpenMaya.MObject()
    m_selection.getDependNode(0, m_cluster)
    return OpenMayaAnim.MFnSkinCluster(m_cluster)

def get_all_skin_nodes():
    """
    Given a mesh name, find the skinCluster node connection.
    :return: <str> skinCluster for success. <bool> False for failure.
    """
    m_iterator = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst)
    while not m_iterator.isDone():
        m_obj = m_iterator.currentItem()
        m_dag_fn = OpenMaya.MFnDagNode(m_obj)
        if OpenMaya.MFn.kSkin == m_obj.apiType():
            return m_dag_fn.fullPathName()
        m_iterator.next()

def get_skin_cluster(source_obj=None):
    """
    Grabs the  skin cluster from the node specified.
    :param source_obj: <OpenMaya.MObject> start iteration from this source node.
    :return: <str> skin cluster node name. <False> for failure.
    """
    mesh_shapes = object_utils.get_shape_obj(source_obj)
    for mesh_shape in mesh_shapes:
        skin_obj = object_utils.get_connected_nodes(mesh_shape,
                                                    find_node_type='skinCluster',
                                                    up_stream=True, depth=True)
        if skin_obj:
            return OpenMayaAnim.MFnSkinCluster(skin_obj[0]), OpenMaya.MFnDependencyNode(skin_obj[0]).name()
    return False, False

def get_skin_cluster_old(source_obj=None):
    """
    Grabs the  skin cluster from the node specified.
    :param source_obj: <OpenMaya.MObject> start iteration from this source node.
    :return: <str> skin cluster node name. <False> for failure.
    """
    m_it_graph = OpenMaya.MItDependencyGraph(object_utils.get_shape_obj(source_obj)[0],
                                             OpenMaya.MItDependencyGraph.kUpstream,
                                             OpenMaya.MItDependencyGraph.kPlugLevel)
    while not m_it_graph.isDone():
        cur_item = m_it_graph.currentItem()
        m_depend_node = OpenMaya.MFnDependencyNode(cur_item)
        if cur_item.hasFn(OpenMaya.MFn.kSkin):
            return OpenMayaAnim.MFnSkinCluster(cur_item), m_depend_node.name()
        if cur_item.hasFn(OpenMaya.MFn.kSkinClusterFilter):
            return OpenMayaAnim.MFnSkinCluster(cur_item), m_depend_node.name()
        m_it_graph.next()
    return False, False

def get_m_plug(in_obj=None, in_plug_name=None):
    """
    Gets a node's plug as an MPlug.
    :param in_obj: <OpenMaya.MObject> the mObject class to find the plugs frOpenMaya.
    :param in_plug_name: <str> the attribute to find.
    """
    if not in_obj or not in_plug_name:
        return False
    depend_fn = OpenMaya.MFnDependencyNode(in_obj)
    return depend_fn.findPlug(in_plug_name)

def connect(source_obj, source_plug_name, destination_obj, destination_plug_name):
    """
    Perform the connection process.
    :param source_obj: <MObject> Source object.
    :param destination_obj: <MObject> Destination object.
    :param source_plug_name: <str> The plug name to connect frOpenMaya.
    :param destination_plug_name: <str> The plug name to connect frOpenMaya.
    """
    source_plug = get_m_plug(source_obj, source_plug_name)
    destination_plug = get_m_plug(destination_obj, destination_plug_name)
    mg_mod = OpenMaya.MDGModifier()
    mg_mod.connect(source_plug, destination_plug)
    mg_mod.doIt()

def get_influences(skin_name="", full_names=False):
    """
    get influence objects from this skin cluster name.
    :param skin_name: <str> skin cluster node name.
    :param full_names: <bool> return full path names.
    :return: <tuple> indices, <tuple> influences
    """
    influences = ()
    ids = ()

    skin_fn = get_skin_fn(skin_name)
    inf_dag_arr = OpenMaya.MDagPathArray()
    skin_fn.influenceObjects(inf_dag_arr)
    for x in xrange(inf_dag_arr.length()):
        inf_id = int(skin_fn.indexForInfluenceObject(inf_dag_arr[x]))
        ids += inf_id,
        if full_names:
            inf_path = inf_dag_arr[x].fullPathName()
        else:
            inf_path = inf_dag_arr[x].partialPathName()
        influences += inf_path,
    return ids, influences,

def unlock_influences(skin_name=""):
    """
    unlocks all influences
    :return: <bool> True for success.
    """
    influences = get_influences(skin_name=skin_name)[1]
    for inf in influences:
        cmds.setAttr('{}.liw'.format(inf), 0)
    return True

def get_skin_data(mesh_obj=None, full_names=True):
    """
    Returns a dictionary of skinCluster influences and weights.
    :param mesh_obj: <OpenMaya.MObject> the mesh shape name.
    :param full_names: <bool> write the file with full path names.
    :return: <dict> skinCluster values. <bool> False for failure.
    """
    weights = {}
    skin_fn, skin_name = get_skin_cluster(mesh_obj)
    if not all((skin_fn, skin_name)):
        return False
    # get the MDagPath for all influence
    inf_dag_arr = OpenMaya.MDagPathArray()
    skin_fn.influenceObjects(inf_dag_arr)
    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    inf_ids = {}
    influences = []
    weights["influences"] = []
    for x in range(inf_dag_arr.length()):
        if full_names:
            inf_path = inf_dag_arr[x].fullPathName()
        else:
            inf_path = inf_dag_arr[x].partialPathName()
        inf_id = int(skin_fn.indexForInfluenceObject(inf_dag_arr[x]))
        inf_ids[inf_id] = x
        influences.append(inf_path)
    weights["influences"] = influences
    # get the MPlug for the weightList and weights attributes
    weight_list_plug = skin_fn.findPlug('weightList')
    weights_plug = skin_fn.findPlug('weights')
    weight_list_attr_plug = weight_list_plug.attribute()
    weights_attr = weights_plug.attribute()
    weight_int_arr = OpenMaya.MIntArray()
    # the weights are stored in dictionary, the key is the vert id,
    # the value is another dictionary whose key is the influence id and
    # value is the weight for that influence
    weights["weights"] = {}
    for v_id in range(weight_list_plug.numElements()):
        weight_values = {}
        # tell the weights attribute which vertex id it represents
        weights_plug.selectAncestorLogicalIndex(v_id, weight_list_attr_plug)
        # get the indicies of all non-zero weights for this vertex
        weights_plug.getExistingArrayAttributeIndices(weight_int_arr)
        # create a copy of the current weights_plug
        inf_plug = OpenMaya.MPlug(weights_plug)
        for inf_id in weight_int_arr:
            # tell the inf_plug it represents the current influence id
            inf_plug.selectAncestorLogicalIndex(inf_id, weights_attr)
            # add this influence and its weight to this verts weights
            try:
                weight_values[inf_ids[inf_id]] = inf_plug.asDouble()
            except KeyError:
                # assumes a removed influence
                pass
        weights["weights"][v_id] = weight_values
    return weights

def normalize_weights(skin_name):
    """
    normalizes skin weights.
    :param skin_name:
    :return:
    """
    return cmds.skinCluster(skin_name, e=True, fnw=True)

def prune_weights(skin_name="", mesh_name="", influences=()):
    """
    Normalizes the weights.
    :return: <bool> True for success. <bool> False for failure.
    """
    # unlock influences used by skincluster
    for inf in influences:
        cmds.setAttr('%s.liw' % inf, 0)
    # normalize needs turned off for the prune to work
    skinNorm = cmds.getAttr('%s.normalizeWeights' % skin_name)
    if skinNorm != 0:
        cmds.setAttr('%s.normalizeWeights' % skin_name, 0)
    cmds.skinPercent(skin_name, mesh_name, nrm=False, prw=100)
    # restore normalize setting
    if skinNorm != 0:
        cmds.setAttr('%s.normalizeWeights' % skin_name, skinNorm)

def check_namespace(name=""):
    """
    replaces the colon with a hyphen
    :param name:
    :return: <str> name.
    """
    if ':' in name:
        return '-'.join(name.split(':'))
    return name

def check_hyphen(name=""):
    """
    replaces the hyphen with a colon.
    :param name:
    :return: <str> name.
    """
    if '-' in name:
        return ':'.join(name.split(':'))
    return name

def save_to_file(mesh_obj='', file_dir=""):
    """
    writes the skinCluster data into a JSON file type.
    :param mesh_obj: <str> the mesh object to query the skinCluster data from.
    :return: <str> the written skinCluster JSON file.
    """
    if not mesh_obj:
        mesh_obj = object_utils.get_selected_node()
    data = get_skin_data(mesh_obj)
    file_name = check_namespace(mesh_obj)
    if not file_dir:
        file_dir = file_utils.get_maya_workspace_data_dir()
    skin_file = file_utils.get_path(file_dir, file_name)
    ft = file_utils.JSONSerializer(skin_file, data)
    ft.write()
    print("Weights saved: {}\n".format(ft.FILE_NAME))
    return skin_file

def save_selected_objects_to_file():
    """
    save the mesh objects' skins to directory.
    :return:
    """
    for node in object_utils.get_selected_node(single=False):
        save_to_file(node)
    return True

def load_selected_objects_from_file():
    """
    save the mesh objects' skins to directory.
    :return:
    """
    for node in object_utils.get_selected_node(single=False):
        data = read_from_file(node)
        set_skin_data(node, data)
    return True

def read_from_file(mesh_obj, file_dir=""):
    """
    reads the skinCluster data and applies it to mesh.
    :param mesh_obj: <str> the mesh object to find the file from the workspace directory.
    :param file_dir: <str> use a different path directory if the workspace directory proves invalid.
    :return: <dict> the skinCluster information data.
    """
    if not file_dir:
        file_dir = file_utils.get_maya_workspace_data_dir()
    file_name = check_namespace(mesh_obj)
    skin_file = file_utils.get_path(file_dir, file_name)
    ft = file_utils.JSONSerializer(skin_file)
    return ft.read()

def verify_influences(weights={}):
    """
    verifies the influences and creates new joints to attach skincluster to.
    :param weights: <dict> weight dictionary data.
    :return: <list> created new joints.
    """
    new_inf = ()
    for influence in weights['influences']:
        if not cmds.objExists(influence):
            cmds.createNode('joint', name=influence)
            new_inf += influence,
    return new_inf

def set_skin_data(mesh_obj=None, weights={}):
    """
    Using the  dictionary provided, set the skinCluster weights.
    :param mesh_obj: set weights to this object.
    :param weights: <dict> weight dictionary data.
    :return: <bool> True for success.  <bool> False for failure.
    """
    # verify influences and create joints that do not exist
    verify_influences(weights=weights)

    skin_fn, skin_name = get_skin_cluster(mesh_obj)
    if not skin_fn:
        skin_name = create_skin_cluster(mesh_obj, weights['influences'])[0]
    prune_weights(skin_name, mesh_obj, weights['influences'])

    for vert_id, weightData in weights['weights'].items():
        weight_attr_plug = '%s.weightList[%s]' % (skin_name, vert_id)
        for inf_id, infValue in weightData.items():
            weight_attr = '.weights[%s]' % inf_id
            cmds.setAttr(weight_attr_plug + weight_attr, infValue)
    print("Weights set on: {}".format(skin_name))
    return True

def set_skin_file_data(mesh_obj='', file_dir=""):
    """
    sets the skin data from file.
    :param mesh_obj:
    :return:
    """
    if not mesh_obj:
        mesh_obj = object_utils.get_selected_node()
    skin_data = read_from_file(mesh_obj, file_dir=file_dir)
    set_skin_data(mesh_obj, skin_data)
    return True

def get_skin_attributes(skin_name=""):
    skin_fn = get_skin_fn(skin_name)
    normalize_plug = skin_fn.findPlug("normalizeWeights", False)
    normalize = normalize_plug.asInt()
    return normalize

def get_weights(skin_name=""):
    """
    gets the skin weights information from skin cluster name as a MDoubleArray.
    :param skin_name: <str> skin cluster name.
    :return: <OpenMaya.MDoubleArray>
    """
    mesh_dag = get_mesh_dag_from_skin(skin_name)
    vertex_comp, vertex_comp_fn = get_all_vertex_components(mesh_dag)
    indices = OpenMaya.MIntArray()
    vertex_comp_fn.getElements(indices)
    skin_fn = get_skin_fn(skin_name)
    element_count = indices.length()
    influence_indices = get_influence_indices(skin_name)
    influence_count = len(influence_indices)
    #...get the weights through OpenMaya
    weights = OpenMaya.MDoubleArray(element_count * influence_count, 0.0)
    skin_fn.getWeights(mesh_dag, vertex_comp, influence_indices, weights)
    return weights

def set_weights(skin_name="", array_weights=None, undo_weights=None, normalize=True):
    """
    funtion call for setting MFnSkinCluster weights with undo.
    Note:
        the normalize flag is a lie.
    :param skin_name: <str>
    :param array_weights: <OpenMaya.MDoubleArray>
    :param undo_weights: <OpenMaya.MDoubleArray>
    :param normalize: <bool>
    :return: <bool> True for success.
    """
    mesh_dag = get_mesh_dag_from_skin(skin_name)
    vertex_comp, vertex_comp_fn = get_all_vertex_components(mesh_dag)
    skin_fn = get_skin_fn(skin_name)
    influence_indices = get_influence_indices(skin_name)
    skin_fn.setWeights(mesh_dag, vertex_comp, influence_indices, array_weights, normalize, undo_weights)
    return True

def get_influence_indices(skin_name):
    """
    gets the influence indices of all influences of the given skin cluster node.
    :param skin_name: <str> skin cluster node.
    :return: <list> array of all influence indices.
    """
    influence_indices = OpenMaya.MIntArray()
    dag_paths = get_influence_dag_paths(skin_name)
    for idx in range(dag_paths.length()):
        influence_indices.append(idx)
    return influence_indices

def get_influence_count(skin_name):
    """
    return the influence count from the skin cluster name provided.
    :param skin_name:
    :return:
    """
    return len(get_influence_indices(skin_name))

def get_influence_dag_paths(skin_name):
    """
    get influence dag paths.
    :param skin_name:
    :return:
    """
    skin_fn = get_skin_fn(skin_name)
    dag_paths = OpenMaya.MDagPathArray()
    skin_fn.influenceObjects(dag_paths)
    return dag_paths

def get_influence_locks(skin_name):
    """
    get influence locks.
    :param skin_name: <str> skin cluster name.
    :return:
    """
    dag_paths = get_influence_dag_paths(skin_name)
    num_influences = dag_paths.length()
    locks = {}
    for idx in range(num_influences):
        influence_obj = dag_paths[idx].node()  # MObject
        influence_fn = OpenMaya.MFnDependencyNode(influence_obj)
        lock_plug = influence_fn.findPlug("liw", False)
        if not lock_plug.isNull():
            locks[idx] = lock_plug.asBool()
    return locks

def get_all_vertex_components(mesh_dag):
    """
    get component MObject for all vertex components of the given mesh.
    :param mesh_dag: dagPath of the mesh object.
    :return: OpenMaya.MObject vertexComponents, MFnSingleIndexedComponent
    """
    comp_fn = OpenMaya.MFnSingleIndexedComponent()
    vtx_comp = comp_fn.create(OpenMaya.MFn.kMeshVertComponent)  # MObject
    mesh_fn = OpenMaya.MFnMesh(mesh_dag)  # MFnMesh
    num_vertices = mesh_fn.numVertices()  # NumVertices
    comp_fn.setCompleteData(num_vertices)  # sets the data as complete
    return vtx_comp, comp_fn

def get_num_vertices(skin_name):
    """
    return the number of vertices
    :param skin_name:
    :return:
    """
    mesh_dag = get_mesh_dag_from_skin(skin_name)
    mesh_fn = OpenMaya.MFnMesh(mesh_dag)  # MFnMesh
    num_vertices = mesh_fn.numVertices()  # NumVertices
    return num_vertices

def get_influence_vertices(skin_name, jnt_name=""):
    """
    returns the influence vertices of the mesh.
    :param skin_name: <str> skincluster node name.
    :param jnt_name: <str> joint name.
    :return: <OpenMaya.MIntArray> affected vertex indices array.
    """
    skin_fn = get_skin_fn(skin_name)
    m_dag = object_utils.get_m_dag(jnt_name)
    weights_array = OpenMaya.MDoubleArray()
    sel = OpenMaya.MSelectionList()
    skin_fn.getPointsAffectedByInfluence(m_dag, sel, weights_array)
    indices = OpenMaya.MIntArray()
    dag_path = OpenMaya.MDagPath()
    comp_obj = OpenMaya.MObject()
    sel_iter = OpenMaya.MItSelectionList(sel, OpenMaya.MFn.kMeshVertComponent)
    while not sel_iter.isDone():
        sel_iter.getDagPath(dag_path, comp_obj)
        if not comp_obj.isNull():
            mesh_vertex_iter = OpenMaya.MItMeshVertex(dag_path, comp_obj)
            while not mesh_vertex_iter.isDone():
                indices.append(mesh_vertex_iter.index())
                mesh_vertex_iter.next()
        sel_iter.next()
    return indices

def get_influence_vertices_iter(skin_name, jnt_name=""):
    """
    returns the influence vertices of the mesh.
    :param skin_name: <str> skincluster node name.
    :param jnt_name: <str> joint name.
    :return: <OpenMaya.MIntArray> affected vertex indices array.
    """
    skin_fn = get_skin_fn(skin_name)
    m_dag = object_utils.get_m_dag(jnt_name)
    weights_array = OpenMaya.MDoubleArray()
    sel = OpenMaya.MSelectionList()
    skin_fn.getPointsAffectedByInfluence(m_dag, sel, weights_array)
    sel_iter = OpenMaya.MItSelectionList(sel, OpenMaya.MFn.kMeshVertComponent)
    return sel_iter

def get_index_by_name(skin_name, joint_name):
    """
    gets the joint index from skin cluster provided.
    :param skin_name: <str> skin cluster name.
    :param joint_name: <str> joint name.
    :return: <int> influence index of the joint name.
    """
    jnt_list = cmds.listConnections(skin_name + '.matrix')
    return jnt_list.index(joint_name)

def get_weights_from_vertex_index(skin_name, component_index=0, weights_array=None):
    """
    returns the weight values from component number
    :param skin_name: <str> skin cluster node name.
    :param component_index: <int> non-zero vertex index.
    :param weights_array: <OpenMaya.MDoubleArray> optional parameter for passing in the weights array for optimization.
    :return: <list> weight values
    """
    if not weights_array:
        weights_array = get_weights(skin_name)
    start_slice, end_slice = get_array_slices_from_vertex_index(skin_name, component_index)
    return weights_array[start_slice:end_slice]

def get_array_slices_from_vertex_index(skin_name, component_index=0):
    """
    returns the weight values from component number
    :param skin_name: <str> skin cluster node name.
    :param component_index: <int> non-zero vertex index.
    :return: <list> weight values
    """
    dag_paths = get_influence_dag_paths(skin_name)
    num_influences = dag_paths.length()
    start_slice = num_influences * component_index
    end_slice = start_slice + num_influences
    return start_slice, end_slice

def __set_transfer_weights(skin_name, index, current_weights, source_index, destination_index, transfer_weights):
    """
    a separate function call for maya python threading
    :return:
    """
    weights = get_weights_from_vertex_index(skin_name, index, weights_array=current_weights)
    start_slice, end_slice = get_array_slices_from_vertex_index(skin_name, index)
    src_weight = weights[source_index]
    dest_weight = weights[destination_index]
    transfer_weights.set(0.0, start_slice + source_index)
    transfer_weights.set(dest_weight + src_weight, start_slice + destination_index)
    return transfer_weights

def get_weight_list_length(skin_name=""):
    """
    returns the length of the skincluster weights list
    :param skin_name:
    :return:
    """
    num_influences = get_influence_count(skin_name)
    num_vertices = get_num_vertices(skin_name)
    return num_influences * num_vertices

def get_num_threads(skin_name="", max_threads=20):
    """
    returns the number of threads relative to the length of the skinning weight list
    :param skin_name:
    :return:
    """
    num_influences = get_influence_count(skin_name)
    num_vertices = get_num_vertices(skin_name)
    num_of_work_per_thread = num_vertices / max_threads

def set_skinweight_value_at_components(skin_name="", joint_name="", component_ids=(), skin_value=1.0):
    """
    sets the skincluster value at joint name provided. Default is 1.0
    :param skin_name:
    :param joint_name:
    :param component_ids:
    :param skin_value:
    :return:
    """
    # collect current data
    mesh_name = get_mesh_from_skin(skin_name)
    names = map(lambda vtx: mesh_utils.get_index_name(mesh_name, vtx), component_ids)
    sel_iter = object_utils.array_to_mit_selection(names)
    current_weights = get_weights(skin_name)
    source_index = get_index_by_name(skin_name, joint_name)
    dag_path = OpenMaya.MDagPath()
    comp_obj = OpenMaya.MObject()
    # copy the weights array, doing it this way shaves off 4.5 seconds
    transfer_weights = OpenMaya.MDoubleArray()
    transfer_weights.copy(current_weights)
    # putting the iteration here shaves off 1 second of computational time
    while not sel_iter.isDone():
        sel_iter.getDagPath(dag_path, comp_obj)
        if not comp_obj.isNull():
            # convert the dag selection into a mesh vertex component unsigned integer index
            mesh_vertex_iter = OpenMaya.MItMeshVertex(dag_path, comp_obj)
            while not mesh_vertex_iter.isDone():
                index = mesh_vertex_iter.index()
                if index in component_ids:
                    start_slice, end_slice = get_array_slices_from_vertex_index(skin_name, index)
                    # src_weight = weights[source_index]
                    transfer_weights.set(skin_value, start_slice + source_index)
                    mesh_vertex_iter.next()
        sel_iter.next()
    set_weights(skin_name, array_weights=transfer_weights, undo_weights=current_weights, normalize=True)

def transfer_skin_weights_from_joint_to_joint(skin_name="", from_jnt_name="", to_jnt_name="", specific_indices=()):
    """
    moves the skin weight data from a source joint to another target joint.
    The number of values should equal to the number of components * the number of indices in the influence indices array

    all the values of the first component are listed, then second and so on.
    :Example:
        influences: [7, 10]
        [component_1 weight for influence 7, component_1 weight for influence 10, component_2 weight for influence 7, component_2 weight for influence 10 ]

    :param skin_name: <str> skin cluster name.
    :param from_jnt_name: <str> from joint name.
    :param to_jnt_name: <str> to joint name.
    :return: <bool> True for success. <bool> False for failure.
    """
    # st = time.time()
    # unlock all skin joints first.
    unlock_influences(skin_name=skin_name)
    # collect current data
    sel_iter = get_influence_vertices_iter(skin_name, from_jnt_name)
    current_weights = get_weights(skin_name)
    source_index = get_index_by_name(skin_name, from_jnt_name)
    destination_index = get_index_by_name(skin_name, to_jnt_name)
    dag_path = OpenMaya.MDagPath()
    comp_obj = OpenMaya.MObject()
    # copy the weights array, doing it this way shaves off 4.5 seconds
    transfer_weights = OpenMaya.MDoubleArray()
    transfer_weights.copy(current_weights)
    # en = time.time()
    # print('variables :: {}'.format(en-st))
    # putting the iteration here shaves off 1 second of computational time
    while not sel_iter.isDone():
        sel_iter.getDagPath(dag_path, comp_obj)
        if not comp_obj.isNull():
            # convert the dag selection into a mesh vertex component unsigned integer index
            mesh_vertex_iter = OpenMaya.MItMeshVertex(dag_path, comp_obj)
            while not mesh_vertex_iter.isDone():
                index = mesh_vertex_iter.index()
                if specific_indices and index in specific_indices:
                    weights = get_weights_from_vertex_index(skin_name, index, weights_array=current_weights)
                    start_slice, end_slice = get_array_slices_from_vertex_index(skin_name, index)
                    src_weight = weights[source_index]
                    dest_weight = weights[destination_index]
                    transfer_weights.set(0.0, start_slice + source_index)
                    transfer_weights.set(dest_weight + src_weight, start_slice + destination_index)
                    mesh_vertex_iter.next()

                else:
                    weights = get_weights_from_vertex_index(skin_name, index, weights_array=current_weights)
                    start_slice, end_slice = get_array_slices_from_vertex_index(skin_name, index)
                    src_weight = weights[source_index]
                    dest_weight = weights[destination_index]
                    transfer_weights.set(0.0, start_slice + source_index)
                    transfer_weights.set(dest_weight + src_weight, start_slice + destination_index)
                    mesh_vertex_iter.next()
        sel_iter.next()
    # en = time.time()
    # print('transfer weights :: {}'.format(en-st))
    # st = time.time()
    # finally set the weights with the weight transfer data
    set_weights(skin_name, array_weights=transfer_weights, undo_weights=current_weights, normalize=True)
    # en = time.time()
    # print('set weights :: {}'.format(en-st))
# ________________________________________________________________________________________________
# skincluster_utils.py