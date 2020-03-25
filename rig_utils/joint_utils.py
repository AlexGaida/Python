"""
joint_utils.py manipulating and retrieving information from joints.
"""
# import standard modules
import re

# import maya modules
from maya import cmds
from maya import OpenMaya

# import local modules
from maya_utils import object_utils
from maya_utils import transform_utils
from maya_utils import curve_utils

# define local variables
JNT_SUFFIX = 'jnt'
BND_JNT_SUFFIX = 'bnd_{}'.format(JNT_SUFFIX)


def reload_selection(func):
    """
    a decorator that deselects and then selects again after the function is complete.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        objects = cmds.ls(sl=1)
        cmds.select(d=1)
        func(*args, **kwargs)
        cmds.select(objects)
    return wrapper


def joint_name(name="", idx=-1):
    """
    concatenate the strings to form a joint name.
    :param name: <str> the base name string to use.
    :param idx: <int> the number to concatenate into.
    :return: <str> the joint name.
    """
    if not name.endswith(JNT_SUFFIX):
        return '{}_{}'.format(name, JNT_SUFFIX)
    elif name and idx != -1:
        return '{}_{}_{}'.format(name, idx, JNT_SUFFIX)
    else:
        return name


def get_joints_from_selection():
    """
    the joints from current selection.
    :return: <tuple> array of joints from selection.
    """
    return tuple(cmds.ls(sl=1, type='joint'))


def get_joints():
    """
    get all joints in the scene.
    :return: <tuple> array of joints.
    """
    return tuple(cmds.ls(type='joint'))


def get_bnd_joints():
    """
    return only bound joints.
    :return: <tuple> filtered array of joints.
    """
    return filter(lambda x: x.endswith(BND_JNT_SUFFIX), get_joints())


def mirror_joints(joints=(), axis='YZ', behaviour=False, search_replace=('l_', 'r_')):
    """
    mirrors an array of joints
    :param joints: <list>, <tuple> array of joints.
    :param axis: <str> mirrors by this axis.
    :param behaviour: <bool> mirrors behaviour.
    :param search_replace: <tuple> (0,) find this string and replace it (1,)
    :return: <tuple> array of mirrored joints.
    """
    if not joints:
        joints = get_joints_from_selection()
    # get only the joint objects in our selection
    jnt_array = filter(object_utils.is_joint, joints)
    mirror_array = ()
    for jnt in jnt_array:
        if axis == 'XY':
            mirror_array += tuple(cmds.mirrorJoint(
                jnt, mirrorXY=True, mirrorBehavior=behaviour, searchReplace=search_replace))
        if axis == 'YZ':
            mirror_array += tuple(cmds.mirrorJoint(
                jnt, mirrorYZ=True, mirrorBehavior=behaviour, searchReplace=search_replace))
        if axis == 'XZ':
            mirror_array += tuple(cmds.mirrorJoint(
                jnt, mirrorXZ=True, mirrorBehavior=behaviour, searchReplace=search_replace))
    return mirror_array


def set_joint_labels():
    """
    names the bind joints through the labels for skinCluster weights.
    :return: <bool> True for success.
    """
    for j_name in get_bnd_joints():
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


@reload_selection
def create_joint_at_transform(transform_name="", name=""):
    """
    creates joints at the same position as the transform object.
    :param transform_name: <str> the transform name to get values from.
    :param name: <str> the name to use when creating joints.
    :return: <str> joint name.
    """
    if not name:
        jnt_name = joint_name(transform_name)
    else:
        jnt_name = name
    tfm = transform_utils.Transform(transform_name).world_translation
    cmds.joint(name=jnt_name)
    cmds.xform(jnt_name, m=tfm.inclusive_matrix_list(), ws=True)
    return jnt_name


@reload_selection
def create_joints(objects_array, name, bind=False):
    """
    create joints at transform objects.
    :param objects_array: <tuple> array of transform objects.
    :param name: <str> the name to use when creating the joints.
    :param bind: <bool> create bind joint name.
    :return: <tuple> array of joints.
    """
    names = ()
    for idx in range(len(objects_array)):
        if bind:
            names += '{}_{}_{}'.format(name, idx, BND_JNT_SUFFIX),
        else:
            names += '{}_{}_{}'.format(name, idx, JNT_SUFFIX),
    joints = ()
    for trfm_name, obj_name in zip(objects_array, names):
        joints += create_joint_at_transform(trfm_name, obj_name),
    return joints


def create_joints_at_selection(name):
    """
    creates the joints at selected transform objects.
    :param name: <str> the name to use when creating the joints.
    :return: <tuple> array of joints created.
    """
    objects = object_utils.get_selected_node(single=False)
    return create_joints(objects, name)


def create_bind_joints_at_selection(name):
    """
    creates the joints at selected transform objects.
    :param name: <str> the name to use when creating the joints.
    :return: <tuple> array of joints created.
    """
    objects = object_utils.get_selected_node(single=False)
    return create_joints(objects, name, bind=True)


def get_joint_hierarchy(base_joint_name=""):
    """
    get the joint hierarchy.
    :param base_joint_name:
    :return: <tuple> array of joint hierarchy.
    """
    return object_utils.get_children_names(base_joint_name, type_name='joint')


def get_joint_hierarchy_positions(base_joint_name=""):
    """
    get hierarchial positions array.
    :return: <tuple> positions array.
    """
    joint_hierarchy = get_joint_hierarchy(base_joint_name)
    positions_array = ()
    for jnt_name in joint_hierarchy:
        positions_array += transform_utils.Transform(jnt_name).get_world_translation_list(),
    return positions_array


@reload_selection
def create_dynamic_chain(base_joint_name="", name="", curve_degree=2):
    """
    creates a dynamic chain from the joint chain provided.
    :return:
    """
    joint_hierarchy = get_joint_hierarchy(base_joint_name)
    points_array = get_joint_hierarchy_positions(base_joint_name)
    print points_array
    curve_name = curve_utils.create_curve_from_points(points_array, degree=curve_degree, curve_name=name)
    # cmds.select(curve_name)
    # make the curve name dynamic
    # mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')

    # now make the spline Ik Handle
    # return curve_name


def create_joint(name="", num_joints=1, prefix_name="", suffix_name="", as_strings=False):
    """
    creates a joint and renames it.
    :param name: <str> the name of the joint to create.
    :param num_joints: the number of joints created.
    :param prefix_name: <str> the prefix name to use.
    :param suffix_name: <str> the suffix name to use.
    :return: <tuple> array of created joint objects.
    """
    if not name:
        name = 'joint'
    dag_mod = OpenMaya.MDagModifier()

    # Create the joint MObjects we will be manipulating.
    jnt_objects = ()
    for i in xrange(0, num_joints):
        if i == 0:
            # The first joint has no parent.
            jnt_obj = dag_mod.createNode('joint')
        else:
            # Assign the new joint as a child to the previous joint.
            jnt_obj = dag_mod.createNode('joint', jnt_objects[i - 1])
        if name:
            name = '{prefix}{name}_{idx}{suffix}'.format(prefix=prefix_name, name=name, idx=i, suffix=suffix_name)
            dag_mod.renameNode(jnt_obj, name)
            dag_mod.doIt()
        # Keep track of all the joints created.
        if not as_strings:
            jnt_objects += jnt_obj,
        else:
            jnt_objects += name,
    return jnt_objects
