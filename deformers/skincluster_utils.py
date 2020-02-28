"""
Querying, getting and setting skincluster information.
"""
# import maya modules
from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim

# import local modules
from maya_utils import object_utils

# define private variables
__version__ = "1.0.0"


def get_mesh_shape(mesh_name=""):
    """
    returns the mesh shape object name from the mesh transform name provided.
    :param mesh_name: <str> mesh transform object name.
    :return: <str> mesh shape name.
    """
    return object_utils.get_transform_relatives(
        mesh_name, find_child=True, with_shape='mesh', as_strings=True)[1]


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


def restore_dag_pose(influences=[]):
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


def apply_skin(object_name="", influences=[], name=""):
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

    target_skin = get_attached_skincluster(target_mesh)
    if target_skin:
        add_influences(target_skin, source_influences)
    else:
        target_skin = create_skin_cluster(target_mesh, source_influences)
    # copy the skins
    copy_skin_weights(source_skin[0], target_skin[0])
    return False



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


def get_all_skin_nodes():
    """
    Given a mesh name, find the skinCluster node connection.
    :return: <str> skinCluster for success. <bool> False for failure.
    """
    m_iterator = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kSkin)
    while not m_iterator.isDone():
        m_obj = m_iterator.currentItem()
        m_dag_fn = OpenMaya.MFnDagNode(m_obj)
        if OpenMaya.MFn.kSkin == m_obj.apiType():
            return m_dag_fn.fullPathName()
        m_iterator.next()


def get_mobject_sel():
    """
    Returns a list of selected objects' MObject.
    :return: <list> of MObjects.
    """
    objects = []
    m_sel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(m_sel)
    m_it_sel_ls = OpenMaya.MItSelectionList(m_sel)
    while not m_it_sel_ls.isDone():
        m_obj = OpenMaya.MObject()
        m_it_sel_ls.getDependNode(m_obj)
        objects.append(m_obj)
        m_it_sel_ls.next()
    return objects


def get_skin_cluster(source_obj=None):
    """
    Grabs the  skin cluster from the node specified.
    :param source_obj: <OpenMaya.MObject> start iteration from this source node.
    :return: <str> skin cluster node name. <False> for failure.
    """
    m_it_graph = OpenMaya.MItDependencyGraph(source_obj,
                                             OpenMaya.MItDependencyGraph.kUpstream,
                                             OpenMaya.MItDependencyGraph.kPlugLeve)
    while not m_it_graph.isDone():
        cur_item = m_it_graph.currentItem()
        m_depend_node = OpenMaya.MFnDependencyNode(cur_item)
        if cur_item.hasFn(OpenMaya.MFn.kSkin):
                return m_depend_node, m_depend_node.name()
        m_it_graph.next()
    return False


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


def get_skin_dict(shape_name=""):
    """
    Returns a dictionary of skinCluster influences and weights.
    :param shape_name: <str> the mesh shape name.
    :return: <dict> skinCluster values. <bool> False for failure.
    """
    weights = {}
    m_skin = object_utils.get_m_obj(shape_name)
    skin_name, skin_fn = get_skin_cluster(m_skin)

    # get the MDagPath for all influence
    inf_dag_arr = OpenMaya.MDagPathArray()
    vertex_arr = OpenMaya.MArrayDataHandle()
    skin_fn.influenceObjects(inf_dag_arr)

    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    inf_ids = {}
    influences = []
    weights["influences"] = []
    for x in xrange(inf_dag_arr.length()):
        inf_path = inf_dag_arr[x].fullPathName()
        inf_id = int(inf_dag_arr.indexForInfluenceObject(inf_dag_arr[x]))
        inf_ids[inf_id] = x
        influences.append(inf_path)
    weights["influences"] = influences

    # get the mesh vertices and id  components
    weights["vertices"] = 0
    OpenMaya.MItMeshVertex(vertex_arr)
    indices = vertex_arr.elementCount()
    weights["vertices"] = indices
    single_index_component = OpenMaya.MFnSingleIndexedComponent()
    vertex_component = single_index_component.create(OpenMaya.MFn.kMeshVertComponent)
    single_index_component.addElements(indices)

    # get the MPlug for the weightList and weights attributes
    weight_list_plug = skin_fn.findPlug('weightList')
    weights_plug = skin_fn.findPlug('weights')
    weight_list_attr_plug = weight_list_plug.attribute()
    weights_plug = weights_plug.attribute()
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
            inf_plug.selectAncestorLogicalIndex(inf_id, weights_plug)

            # add this influence and its weight to this verts weights
            try:
                weight_values[inf_ids[inf_id]] = inf_plug.asDouble()
            except KeyError:
                # assumes a removed influence
                pass
        weights["weights"][v_id] = weight_values


def normalize_weights(skin_name="", mesh_name="", influences=[]):
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
        cmds.setAttr('%s.normalizeWeights' % mesh_name, skinNorm)


def set_weights(skin_fn=None, weights={}):
    """
    Using the  dictionary provided, set the skinCluster weights.
    :param skin_fn: <OpenMayaAnim.MFnSkinCluster> the skin cluster function set.
    :param weights: <dict> weight dictionary data.
    :return: <bool> True for success.  <bool> False for failure.
    """
    m_int_array = OpenMaya.MIntArray()
    skin_fn.influenceObjects(m_int_array)
    skin_name = object_utils.get_m_object_name(skin_fn)

    for vert_id, weightData in weights.items():
        weight_list_attr_plug = '%s.weightList[%s]' % (skin_name, vert_id)
        for inf_id, infValue in weightData.items():
            weight_attr = '.weights[%s]' % inf_id
            cmds.setAttr(weight_list_attr_plug + weight_attr, infValue)
    return True
