"""
joint_utils.py manipulating and retrieving information from joints.
"""
# import standard modules
import re

# import maya modules
from maya import cmds

# import local modules
from maya_utils import object_utils

# define local variables
JNT_SUFFIX = 'jnt'


def is_joint(arg):
    """
    checks if the incoming argument is of type joint.
    :param arg: <str> check this argument.
    :return: <bool> True for success. <bool> False for failure.
    """
    if isinstance(arg, (str, unicode)):
        return cmds.objectType(arg) == 'joint'
    return False


def get_joints_from_selection():
    """
    the joints from current selection.
    :return: <tuple> array of joints from selection.
    """
    return cmds.ls(sl=1, type='joint')


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
    jnt_array = filter(is_joint, joints)
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
    names the joints through the labels for skinCluster weights.
    :return: <bool> True for success.
    """
    joints = cmds.ls('*_bnd_jnt', type='joint')
    for j_name in joints:
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
