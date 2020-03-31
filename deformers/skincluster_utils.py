"""
Querying, getting and setting skincluster information.
"""
# import maya modules
from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim

# import local modules
from maya_utils import object_utils
from maya_utils import file_utils

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


def get_skin_data(mesh_obj=None):
    """
    Returns a dictionary of skinCluster influences and weights.
    :param mesh_obj: <OpenMaya.MObject> the mesh shape name.
    :return: <dict> skinCluster values. <bool> False for failure.
    """
    weights = {}
    skin_fn, skin_name = get_skin_cluster(mesh_obj)

    # get the MDagPath for all influence
    inf_dag_arr = OpenMaya.MDagPathArray()
    skin_fn.influenceObjects(inf_dag_arr)

    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    inf_ids = {}
    influences = []
    weights["influences"] = []
    for x in xrange(inf_dag_arr.length()):
        inf_path = inf_dag_arr[x].fullPathName()
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
    for v_id in xrange(weight_list_plug.numElements()):
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


def normalize_weights(skin_name="", mesh_name="", influences=()):
    """
    Normalizes the weights.
    :return: <bool> True for success. <bool> False for failure.
    """
    # unlock influences used by skincluster
    for inf in influences:
        cmds.setAttr('%s.liw' % inf)

    # normalize needs turned off for the prune to work
    skinNorm = cmds.getAttr('%s.normalizeWeights' % skin_name)
    if skinNorm != 0:
        cmds.setAttr('%s.normalizeWeights' % skin_name, 0)
    cmds.skinPercent(skin_name, mesh_name, nrm=False, prw=100)

    # restore normalize setting
    if skinNorm != 0:
        cmds.setAttr('%s.normalizeWeights' % skin_name, skinNorm)


def save_to_file(mesh_obj):
    """
    writes the skinCluster data into a JSON file type.
    :param mesh_obj: <str> the mesh object to query the skinCluster data from.
    :return: <str> the written skinCluster JSON file.
    """
    data = get_skin_data(mesh_obj)
    skin_file = file_utils.get_path(file_utils.get_maya_workspace_dir(), mesh_obj)
    ft = file_utils.JSONSerializer(skin_file, data)
    ft.write()
    return skin_file


def read_from_file(mesh_obj):
    """
    reads the skinCluster data into a JSON file type.
    :param mesh_obj: <str> the mesh object to find the file from the workspace directory.
    :return: <dict> the skinCluster information data.
    """
    data = get_skin_data(mesh_obj)
    skin_file = file_utils.get_path(file_utils.get_maya_workspace_dir(), mesh_obj)
    ft = file_utils.JSONSerializer(skin_file, data)
    return ft.read()


def set_skin_data(mesh_obj=None, weights={}):
    """
    Using the  dictionary provided, set the skinCluster weights.
    :param mesh_obj: set weights to this object.
    :param weights: <dict> weight dictionary data.
    :return: <bool> True for success.  <bool> False for failure.
    """
    skin_fn, skin_name = get_skin_cluster(mesh_obj)
    if not skin_fn:
        skin_name = create_skin_cluster(mesh_obj, weights['influences'])[0]
    normalize_weights(skin_name, mesh_obj, weights['influences'])

    for vert_id, weightData in weights['weights'].items():
        weight_attr_plug = '%s.weightList[%s]' % (skin_name, vert_id)
        for inf_id, infValue in weightData.items():
            weight_attr = '.weights[%s]' % inf_id
            cmds.setAttr(weight_attr_plug + weight_attr, infValue)
    print("Weights set on: {}".format(skin_name))
    return True
