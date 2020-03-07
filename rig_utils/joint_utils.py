"""
joint_utils.py manipulating and retrieving information from joints.
"""
# import standard modules
import re

# import maya modules
from maya import cmds

# import local modules
from maya_utils import object_utils
from maya_utils import transform_utils

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
    tfm = transform_utils.Transform(transform_name)
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
