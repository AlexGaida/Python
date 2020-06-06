"""
ikspline: set up the ik spline system between the start and end joint of the hierarchy.

"""

from maya import cmds
from rig_utils import control_utils
from maya_utils import object_utils

ik_spline_handle_attrs = {
    "dWorldUpAxis": 3,
    "dWorldUpVectorX": 1.00,
    "dWorldUpVectorEndX": 1.00,
    "dTwistValueType": 1.00,
    "dWorldUpVectorY": 0.00,
    "dWorldUpVectorEndY": 0.00,
    "dTwistEnd": 1}


def util_get_cvs(curve_name=""):
    return cmds.ls(curve_name + '.cv[*]', flatten=True)


def get_middle_cvs(spline_cv=()):
    return spline_cv[2:-2]


def get_middle_joints(start_joint):
    return object_utils.get_children_names(start_joint, type_name='joint')[1:-1]


def build_ik_spline(name="", start_joint="", end_joint="", number_of_spans=4):
    """
    creates the ik spline with the joints provided.
    This is old code.
    :param start_joint: <str> start joint name.
    :param end_joint: <str> end joint name.
    :param name: <str> name to use to create nodes with.
    :param number_of_spans: <int>
    """
    return_dict = dict()
    return_dict["locators"] = ()

    # Creates the spline ik to the selected joint hierarchy with the curve attached.
    spline_array = cmds.ikHandle(startJoint=start_joint, endEffector=end_joint, sol="ikSplineSolver",
                                 numSpans=number_of_spans, scv=True, pcv=False, createCurve=True)

    ik_handle, ik_effector, ik_curve = spline_array

    spline_cvs = util_get_cvs(ik_curve)

    # set the attributes on the spline ik handle
    for eAttr, eVal in ik_spline_handle_attrs.items():
        cmds.setAttr(ik_handle + "." + eAttr, eVal )

    spline_system_grp = cmds.group(ik_handle, ik_curve, name='sys_{0}_stretch_grp'.format(name))

    # Adds the cluster locators.
    start_point = cmds.xform(spline_cvs[0], worldSpace=True, translation=True, query=True)
    last_point = cmds.xform(spline_cvs[-1], worldSpace=True, translation=True, query=True)

    start_loc = cmds.spaceLocator(name='{0}_start_loc'.format(name))[0]
    end_loc = cmds.spaceLocator(name='{0}_end_loc'.format(name))[0]

    return_dict["locators"] += end_loc,
    return_dict["locators"] += start_loc,

    for eachScale in ['.localScaleX', '.localScaleY', '.localScaleZ']:
        cmds.setAttr('{0}Shape{1}'.format(start_loc, eachScale), 5)
        cmds.setAttr('{0}Shape{1}'.format(end_loc, eachScale), 5)

    cmds.xform(start_loc, ws=True, translation=start_point)
    cmds.xform(end_loc, ws=True, translation=last_point)

    cmds.cluster([spline_cvs[0], spline_cvs[1]], bindState=True, relative=True,
                 weightedNode=[start_loc, start_loc + 'Shape'])
    cmds.cluster([spline_cvs[-2], spline_cvs[-1]], bindState=True, relative=True,
                 weightedNode=[end_loc, end_loc + 'Shape'])

    ctrl_grp = cmds.group(start_loc, end_loc, name='loc_{0}_stretch_grp'.format(name))

    for index, eachLeftoverCVs in enumerate(get_middle_cvs(spline_cvs)):
        middle_loc = cmds.spaceLocator(name='middle_{1}{0}_loc'.format(index, name))[0]
        mid_pos = cmds.xform(eachLeftoverCVs, ws=True, translation=True, query=True)
        cmds.xform(middle_loc, ws=True, translation=mid_pos)

        cmds.cluster(eachLeftoverCVs, bindState=True, relative=True,
                     weightedNode=[middle_loc, middle_loc + 'Shape'])
        cmds.parent(middle_loc, ctrl_grp)

        return_dict["locators"] += middle_loc,

    # Set the ikSpline advanced twist controls.
    cmds.setAttr(ik_handle + '.dTwistControlEnable', 1)
    cmds.setAttr(ik_handle + '.dWorldUpType', 4)

    cmds.connectAttr(start_loc + '.worldMatrix[0]', ik_handle + '.dWorldUpMatrix')
    cmds.connectAttr(end_loc + '.worldMatrix[0]', ik_handle + '.dWorldUpMatrixEnd')

    # Add stretchiness element to the spline.
    arc_len = cmds.arclen(ik_curve, ch=1)

    # Adds scaleFactor setup.
    stretch_loc_grp = cmds.spaceLocator(name="stretchy_{0}IK_grp".format(name))[0]
    scale_grp = cmds.group(name="inherit_{0}_scale".format(name), em=True)
    cmds.setAttr("{0}.inheritsTransform".format(scale_grp), 0)
    cmds.scaleConstraint(stretch_loc_grp, scale_grp, mo=False)

    scale_factor = cmds.createNode('multiplyDivide', name='{0}_scaleFACTOR'.format(name))
    cmds.setAttr(scale_factor + '.operation', 2)
    cmds.connectAttr(arc_len + '.arcLength', scale_factor + '.input1X')
    cmds.connectAttr(scale_grp + '.scaleX', scale_factor + '.input2X')

    length_diff = cmds.createNode('multiplyDivide', name='{0}_lengthDifference'.format(name))
    cmds.setAttr(length_diff + '.operation', 2)
    cmds.connectAttr(scale_factor + '.outputX', length_diff + '.input1X')
    arc_dimension = cmds.getAttr(arc_len + '.arcLength')
    cmds.setAttr(length_diff + '.input2X', arc_dimension)

    # create a stretch factor for the middle joints.
    for ea_jnt in get_middle_joints(start_joint):
        translate_x_attr = cmds.getAttr(ea_jnt + '.translateX')
        trans_x_diff = cmds.createNode('multiplyDivide', name='{0}_translationDifference'.format(name))
        cmds.setAttr(trans_x_diff + '.operation', 1)
        cmds.setAttr(trans_x_diff + '.input1X', translate_x_attr)
        cmds.connectAttr(length_diff + '.outputX', trans_x_diff + '.input2X')
        cmds.connectAttr(trans_x_diff + '.outputX', ea_jnt + '.tx')

    # Create a controller for every locator
    return_dict["ik_controllers"] = control_utils.create_controls(
        return_dict["locators"], name, shape_name='cube',
        apply_constraints='parent', maintain_offset=True)

    # parent the systems into this group
    for ctrl_data in return_dict["ik_controllers"]:
        cmds.parent(ctrl_data['group_names'], stretch_loc_grp)
    cmds.parent(spline_system_grp, stretch_loc_grp)
    cmds.parent(ctrl_grp, stretch_loc_grp)
    cmds.parent(start_joint, scale_grp)
    return return_dict
