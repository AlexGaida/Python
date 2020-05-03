"""
builds the arm rig
"""

# import local modules
from rig_utils import joint_utils
from rig_utils import name_utils

joint_1_name = "upper_arm"
joint_2_name = "elbow_arm"
joint_3_name = "hand_arm"


def get_names(name="", prefix_name=""):
    """
    get the names
    :param name:
    :param prefix_name:
    :return:
    """
    names = ()
    names += prefix_name + name + '_' + joint_1_name,
    names += prefix_name + name + '_' + joint_2_name,
    names += prefix_name + name + '_' + joint_3_name,
    return names


def build_arm(joint_1, joint_2, joint_3, name="", prefix_name="", suffix_name=""):
    """
    builds the arm rig from the 3 joints provided.
    :param joint_1: the upper arm joint.
    :param joint_2: the elbow joint.
    :param joint_3: the hand joint.
    :param name: <str> the base name to use.
    :param prefix_name: <str> the prefix name to use.
    :param suffix_name: <str> the suffix name to use.
    :return: <str> parent arm group.
    """
    # create joint
    joint_utils.create_joints_from_array((joint_1, joint_2, joint_3),
                                         get_names(name))
    joint_utils.create_joints_from_array((joint_1, joint_2, joint_3),
                                         get_names(name_utils.BND_JNT_SUFFIX_NAME + "_" + name))