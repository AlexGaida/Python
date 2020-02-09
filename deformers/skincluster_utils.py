"""
Querying, getting and setting skincluster information.
"""
# import maya modules
from maya import cmds
from maya import OpenMaya

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
    :param shape_name: <str> the object name to start the search from.
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
    :param object_name: <str> object name to get the name from.
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
    :param source_mesh: <str> the source mesh to get the influences and weights from.
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
