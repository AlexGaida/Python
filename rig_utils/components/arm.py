"""
builds the arm rig
"""

# import local modules
from rig_utils import joint_utils
from rig_utils import name_utils
from rig_utils import control_utils
from rig_utils import constraint_utils
from rig_utils import node_utils
from maya_utils import object_utils
from maya_utils import attribute_utils

# define variables
joint_1_name = "upper_arm"
joint_2_name = "elbow_arm"
joint_3_name = "hand_arm"


def get_names(name="", prefix_name=""):
    """
    get the names for the arm component
    :param name: <str> base name.
    :param prefix_name: <str> prefix name.
    :return: <tuple> array of names.
    """
    names = ()
    names += prefix_name + name + '_' + joint_1_name,
    names += prefix_name + name + '_' + joint_2_name,
    names += prefix_name + name + '_' + joint_3_name,
    return names


def get_joint_positions(joint_1, joint_2, joint_3):
    # create joint
    positions = ()
    for jnt in (joint_1, joint_2, joint_3):
        positions += object_utils.get_object_transform(jnt, t=True),
    return positions


def build(joint_1, joint_2, joint_3, name="", prefix_name="", suffix_name=""):
    """
    builds the arm rig from the 3 joints provided.
    :param joint_1: <str> the upper arm joint.
    :param joint_2: <str> the elbow joint.
    :param joint_3: <str> the hand joint.
    :param name: <str> the base name to use.
    :param prefix_name: <str> the prefix name to use.
    :param suffix_name: <str> the suffix name to use.
    :return: <str> parent arm group.
    """
    # create joint
    positions = get_joint_positions(joint_1, joint_2, joint_3)

    bnd_joints = joint_utils.create_joints_from_arrays(
        positions, get_names(name + "_" + name_utils.BND_JNT_SUFFIX_NAME), parented=True)
    ik_joints = joint_utils.create_joints_from_arrays(
        positions, get_names(name + "_" + name_utils.IK_JNT_SUFFIX_NAME), parented=True)
    fk_joints = joint_utils.create_joints_from_arrays(
        positions, get_names(name + "_" + name_utils.FK_JNT_SUFFIX_NAME), parented=True)

    # reorient joints
    joint_utils.orient_joints(bnd_joints, primary_axis='x')
    joint_utils.orient_joints(ik_joints, primary_axis='x')
    joint_utils.orient_joints(fk_joints, primary_axis='x')

    fk_name = name + '_fk'
    for fk_joint in fk_joints:
        fk_ctrl = control_utils.create_control_at_transform(fk_joint, name=fk_name)
        constraint_utils.parent_constraint(fk_ctrl['controller'], fk_joint)

    ik_name = name + '_ik'
    # return controller and group_names keys
    ik_ctrl = control_utils.create_control_at_transform(ik_joints[-1], name=ik_name, shape_name='sphere')

    # add the ik/fk switch
    ik_fk_attr = object_utils.attr_add_float(ik_ctrl['controller'], 'IkFk')
    object_utils.attr_set_min_max(ik_ctrl['controller'], 'IkFk')

    # create the ikHandle
    ik_handle = joint_utils.create_ik_handle(ik_joints)
    constraint_utils.point_constraint(ik_ctrl['controller'], ik_handle)

    # parent constrain the joints.
    constraints = ()
    for idx in xrange(3):
        constraints += object_utils.do_parent_constraint((ik_joints[idx], fk_joints[idx]),
                                                         bnd_joints[idx], maintain_offset=False),
        cnst_attr = attribute_utils.Attributes(constraints[idx], custom=True)
        first_attr = cnst_attr.custom.keys()[0]
        second_attr = cnst_attr.custom.keys()[1]

        # create the switch and attach it to the constraints created
        node_utils.create_binary_switch(ik_fk_attr, driven_attr_0=first_attr, driven_attr_1=second_attr)
    return ik_handle
