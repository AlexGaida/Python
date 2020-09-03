"""
rig utility module for building rig components.
"""
# import standard modules
import string

# import maya modules
from maya import cmds
from maya import OpenMaya

# import local modules
from maya_utils import object_utils
from maya_utils import transform_utils
from maya_utils import math_utils
from maya_utils import mesh_utils
from deformers import skincluster_utils
reload(object_utils)
reload(skincluster_utils)
reload(mesh_utils)
reload(math_utils)
# local variables
letters = string.ascii_uppercase


def aim_nodes(forward, up, driven_obj, number=1):
    """Creates an aim constraint system using the maya node objects
    :param forward: <str> the aim transform object.
    :param up: <str> the up transform object.
    :param driven_obj: <str> the driven transform object.
    :param number: <int> the duplication number to append to the name.
    :return (tuple): constructed nodes.
    """
    # create the point matrix vector nodes
    driven_vector_node = cmds.createNode('vectorProduct', name='aim_vec_{}'.format(number))
    up_vector_node = cmds.createNode('vectorProduct', name='up_vec_{}'.format(number))
    forward_vector_node = cmds.createNode('vectorProduct', name='forward_vec_{}'.format(number))

    for vec_node in (driven_vector_node, up_vector_node, forward_vector_node):
        # set the vector product to point matrix operation
        cmds.setAttr(vec_node + '.operation', 4)
        cmds.setAttr(vec_node + '.normalizeOutput', True)

    # connect the world matrix to the vector product matrix input
    for transform_node, vec_node in zip(
            (forward, up, driven_obj), (driven_vector_node, up_vector_node, forward_vector_node)):
        cmds.connectAttr(transform_node + '.worldMatrix[0]', vec_node + '.matrix')

    # make a forward plus minus average node to make a non-origin vector
    forward_vector_avg_node = cmds.createNode('plusMinusAverage', name="forward_vector_{}".format(number))
    # set the average node to subtraction operation
    cmds.setAttr(forward_vector_avg_node + '.operation', 2)
    cmds.connectAttr(forward_vector_node + '.output', forward_vector_avg_node + '.input3D[0]')
    cmds.connectAttr(driven_vector_node + '.output', forward_vector_avg_node + '.input3D[1]')

    # create the plus minus average node between the driven vector and up
    up_vector_avg_node = cmds.createNode('plusMinusAverage', name='up_vector_{}'.format(number))
    # set the plus minus average node to subtraction operation
    cmds.setAttr(up_vector_avg_node + '.operation', 2)
    cmds.connectAttr(up_vector_node + '.output', up_vector_avg_node + '.input3D[0]')
    cmds.connectAttr(driven_vector_node + '.output', up_vector_avg_node + '.input3D[1]')

    # create the cross product node to create a perpedicular axis between the up and the forward vector
    z_up_cross_vector_node = cmds.createNode('vectorProduct', name='z_up_cross_x_{}'.format(number))
    cmds.setAttr(z_up_cross_vector_node + '.normalizeOutput', True)
    # set the vector product node to cross product operation
    cmds.setAttr(z_up_cross_vector_node + '.operation', 2)
    cmds.connectAttr(up_vector_avg_node + '.output3D', z_up_cross_vector_node + '.input1')
    cmds.connectAttr(forward_vector_avg_node + '.output3D', z_up_cross_vector_node + '.input2')

    # create a four by four matrix node and connect everything together
    # think of this as plugging in values to the cmds.xform matrix list output
    four_by_four_matrix_node = cmds.createNode('fourByFourMatrix', name='fbfMatrix_{}'.format(number))

    # connect the aim vector to the four by four matrix node
    cmds.connectAttr(forward_vector_avg_node + '.output3Dx', four_by_four_matrix_node + '.in00')
    cmds.connectAttr(forward_vector_avg_node + '.output3Dy', four_by_four_matrix_node + '.in01')
    cmds.connectAttr(forward_vector_avg_node + '.output3Dz', four_by_four_matrix_node + '.in02')

    # connect the up vector to the four by four matrix node
    cmds.connectAttr(up_vector_avg_node + '.output3Dx', four_by_four_matrix_node + '.in10')
    cmds.connectAttr(up_vector_avg_node + '.output3Dy', four_by_four_matrix_node + '.in11')
    cmds.connectAttr(up_vector_avg_node + '.output3Dz', four_by_four_matrix_node + '.in12')

    # connect the Z ^ UP cross product node to the four by four matrix node
    cmds.connectAttr(z_up_cross_vector_node + '.outputX', four_by_four_matrix_node + '.in20')
    cmds.connectAttr(z_up_cross_vector_node + '.outputY', four_by_four_matrix_node + '.in21')
    cmds.connectAttr(z_up_cross_vector_node + '.outputZ', four_by_four_matrix_node + '.in22')

    # finally, connect the driven object translate to the four by four matrix node
    cmds.connectAttr(driven_obj + '.translateX', four_by_four_matrix_node + '.in30')
    cmds.connectAttr(driven_obj + '.translateY', four_by_four_matrix_node + '.in31')
    cmds.connectAttr(driven_obj + '.translateZ', four_by_four_matrix_node + '.in32')

    # connect the output of the four by four matrix to the decompose matrix node
    decompose_node = cmds.createNode('decomposeMatrix', name='aim_decompose_{}'.format(number))
    cmds.connectAttr(four_by_four_matrix_node + '.output', decompose_node + '.inputMatrix')
    cmds.connectAttr(decompose_node + '.outputRotate', driven_obj + '.rotate')

    return (driven_vector_node, up_vector_node, forward_vector_node, forward_vector_avg_node, up_vector_avg_node,
            z_up_cross_vector_node, four_by_four_matrix_node, decompose_node)

def get_joint_hierarchy(start_joint):
    joints = cmds.listRelatives(start_joint, c=True, ad=True, type='joint') + [start_joint]
    joints.reverse()
    return joints


def pole_vector_system(pole_vector_transform="", ik_handle=""):
    """
    setup pole vector constraint for an ikhandle with matrix nodes

    ik_handle: <str> maya ikhandle (RPSolver and ikSpringSolver) name
    pole_vector_transform: <str> pole vector control name
    Returns:
    """
    if not cmds.nodeType(ik_handle)=='ikHandle':
        return OpenMaya.MGlobal.displayError('{node} is not an ikHandle'.format(node=ik_handle))
    startJoint = cmds.ikHandle(ik_handle, q=True, startJoint=True)

    # create all necessary nodes needed for pole vector math
    pos = cmds.createNode('pointMatrixMult', name='{node}_wpos_pmm'.format(node=startJoint))
    cm  = cmds.createNode('composeMatrix', name='{node}_wpos_cm'.format(node=startJoint))
    im  = cmds.createNode('inverseMatrix', name='{node}_wpos_im'.format(node=startJoint))
    mm  = cmds.createNode('multMatrix', name='{node}_pole_position_mm'.format(node=ik_handle))
    pole= cmds.createNode('pointMatrixMult', name='{node}_pole_position_pmm'.format(node=ik_handle))

    # ikHandle is setting rotation value on startJoint, we can't connect worldMatrix right away.
    # in order to avoid cycle, Compose world space position for start joint with pointMatrixMult node
    # connecting position attribute and parentMatrix will give us worldSpace position
    cmds.connectAttr('{node}.translate'.format(node=startJoint), '{node}.inPoint'.format(node=pos))
    cmds.connectAttr('{node}.parentMatrix[0]'.format(node=startJoint), '{node}.inMatrix'.format(node=pos))

    # now composeMatrix from output, so we can inverse and find local position from startJoint to pole control
    cmds.connectAttr('{node}.output'.format(node=pos), '{node}.inputTranslate'.format(node=cm))
    cmds.connectAttr('{node}.outputMatrix'.format(node=cm), '{node}.inputMatrix'.format(node=im))
    cmds.connectAttr('{node}.worldMatrix[0]'.format(node=pole_vector_transform), '{node}.matrixIn[0]'.format(node=mm))
    cmds.connectAttr('{node}.outputMatrix'.format(node=im), '{node}.matrixIn[1]'.format(node=mm))

    # now connect outputs
    cmds.connectAttr('{node}.matrixSum'.format(node=mm), '{node}.inMatrix'.format(node=pole))
    cmds.connectAttr('{node}.output'.format(node=pole), '{node}.poleVector'.format(node=ik_handle))
    return True


def build_stretch(start_joint, end_joint, num_of_cvs=6, forward_axis='x'):
    """
    builds the joint as stretchy joint from the starting joint to the end joint.
    :param start_joint:
    :param end_joint:
    :return:
    """
    joint_list = get_joint_hierarchy(start_joint)
    cmds.setAttr("%s.jointOrientY" % joint_list[0], 0)

    # Creates the splineIK to the selected joint hierarchy.
    splineIk = cmds.ikHandle(startJoint=start_joint, endEffector=end_joint,
                             sol="ikSplineSolver", numSpans=num_of_cvs,
                             scv=True, pcv=False, createCurve=True)
    splineCrvCvs = cmds.ls(splineIk[2] + '.cv[*]', flatten=True)

    sysGrp = cmds.group(splineIk[0], splineIk[2], name='sys_stretch_grp')

    # Adds the cluster locators.
    startPt = cmds.xform(splineCrvCvs[0], worldSpace=True, translation=True, query=True)
    lastPt = cmds.xform(splineCrvCvs[-1], worldSpace=True, translation=True, query=True)

    cvStartLocator = cmds.spaceLocator(name='start_loc')[0]
    cvEndLocator = cmds.spaceLocator(name='end_loc')[0]

    for eachScale in ['.localScaleX', '.localScaleY', '.localScaleZ']:
        cmds.setAttr('{0}Shape{1}'.format(cvStartLocator, eachScale), 5)
        cmds.setAttr('{0}Shape{1}'.format(cvEndLocator, eachScale), 5)

    cmds.xform(cvStartLocator, ws=True, translation=startPt)
    cmds.xform(cvEndLocator, ws=True, translation=lastPt)

    cmds.cluster([splineCrvCvs[0], splineCrvCvs[1]], bindState=True, relative=True,
                 weightedNode=[cvStartLocator, cvStartLocator + 'Shape'])
    cmds.cluster([splineCrvCvs[-2], splineCrvCvs[-1]], bindState=True, relative=True,
                 weightedNode=[cvEndLocator, cvEndLocator + 'Shape'])

    for eachClusterCv in [splineCrvCvs[0], splineCrvCvs[1], splineCrvCvs[-2], splineCrvCvs[-1]]:
        splineCrvCvs.remove(eachClusterCv)

    ctlGrp = cmds.group(cvStartLocator, cvEndLocator, name='ctl_stretch_grp')
    for index, eachLeftoverCVs in enumerate(splineCrvCvs):
        cvMiddleLocator = cmds.spaceLocator(name='middle{0}_loc'.format(index))[0]
        midCvPosition = cmds.xform(eachLeftoverCVs, ws=True, translation=True, query=True)
        cmds.xform(cvMiddleLocator, ws=True, translation=midCvPosition)

        cmds.cluster(eachLeftoverCVs, bindState=True, relative=True,
                     weightedNode=[cvMiddleLocator, cvMiddleLocator + 'Shape'])

        cmds.parent(cvMiddleLocator, ctlGrp)

    # Set the ikSpline advanced twist controls.
    cmds.setAttr(splineIk[0] + '.dTwistControlEnable', 1)
    cmds.setAttr(splineIk[0] + '.dWorldUpType', 4)

    cmds.connectAttr(cvStartLocator + '.worldMatrix[0]', splineIk[0] + '.dWorldUpMatrix')
    cmds.connectAttr(cvEndLocator + '.worldMatrix[0]', splineIk[0] + '.dWorldUpMatrixEnd')

    # Add stretchiness element to the spline.
    arcLen = cmds.arclen(splineIk[-1], ch=1)

    # Adds scaleFactor setup.
    stretchLocGrp = cmds.spaceLocator(name="stretchyIK_grp")[0]
    scaleGrp = cmds.group(name="inheritSCALE", em=True)
    cmds.setAttr("{0}.inheritsTransform".format(scaleGrp), 0)
    cmds.scaleConstraint(stretchLocGrp, scaleGrp, mo=False)

    scaleFactor = cmds.createNode('multiplyDivide', name='scaleFACTOR')
    cmds.setAttr(scaleFactor + '.operation', 2)
    cmds.connectAttr(arcLen + '.arcLength', scaleFactor + '.input1X')
    cmds.connectAttr(scaleGrp + '.scaleX', scaleFactor + '.input2X')

    lengthDiff = cmds.createNode('multiplyDivide', name='LengthDifference')
    cmds.setAttr(lengthDiff + '.operation', 2)
    cmds.connectAttr(scaleFactor + '.outputX', lengthDiff + '.input1X')
    arcLenNumber = cmds.getAttr(arcLen + '.arcLength')
    cmds.setAttr(lengthDiff + '.input2X', arcLenNumber)

    for eachJoint in joint_list[:-1]:
        translationX = cmds.getAttr(eachJoint + '.translate{}'.format(forward_axis.upper()))
        transXDiff = cmds.createNode('multiplyDivide', name='translationDifference')
        cmds.setAttr(transXDiff + '.operation', 1)
        cmds.setAttr(transXDiff + '.input1X', translationX)
        cmds.connectAttr(lengthDiff + '.outputX', transXDiff + '.input2X')
        cmds.connectAttr(transXDiff + '.outputX', eachJoint + '.t{}'.format(forward_axis))
    # cmds.parent(scaleGrp, ctlGrp, sysGrp, stretchLocGrp)


def get_param_u(transform_obj="", point=(), curve_name=""):
    """
    retrieves the parameter U values from the curve specified from a point in space.
    :param point: <tuple> array of X, Y, Z point coordinates.
    :param transform_obj: <str> the transform_object to get translation point location data from.
    :param curve_name: <str> the name of the curve to be used.
    :return: <float> parameter double attribute value.
    """
    if transform_obj:
        point = transform_utils.get_world_position(transform_obj)
    point = OpenMaya.MPoint(*point)
    curve_fn = object_utils.get_shape_fn(curve_name)[0]
    double_util = object_utils.ScriptUtil(0.0, as_double_ptr=True)
    is_point_on_curve = curve_fn.isPointOnCurve(point)
    if is_point_on_curve:
        curve_fn.getParamAtPoint(point, double_util.ptr, 0.001, OpenMaya.MSpace.kObject)
    else:
        # MFnNurbsCurve::closestPoint(MPoint const &,double *,double,MSpace::Space,MStatus *) const
        point = curve_fn.closestPoint(point, double_util.ptr, 0.001, OpenMaya.MSpace.kObject)
        curve_fn.getParamAtPoint(point, double_util.ptr, 0.001, OpenMaya.MSpace.kObject)
    return double_util.get_double()


def build_sinusoidal_system(transform_object="", drive_axis='z', driver_attr=''):
    """
    builds the system with the transform object provided.
    :param transform_object: <str> the transform object to hook up to.
    :param drive_axis: <str> the axis to drive this transform object from.
    :param driver_attr: <str> driver attribute to drive the sinusoidal system.
    :return: <bool> True for success.
    """
    # build the nodes for proper hookups
    axis_value = cmds.getAttr(transform_object + '.t' + drive_axis)
    additive_node = cmds.createNode('addDoubleLinear', name=transform_object + '_additiveOutput')
    clamp_node = cmds.createNode('clamp', name=transform_object + '_clamp')
    cmds.setAttr(clamp_node + '.maxR', 1.0)
    cmds.setAttr(additive_node + '.input2', axis_value)

    trans_mult = cmds.createNode('multDoubleLinear', name=transform_object + '_translateMult')
    cmds.setAttr(trans_mult + '.input1', axis_value)

    mult_node = cmds.createNode('multiplyDivide', name=transform_object + '_mult')
    cmds.setAttr(mult_node + '.input2X', 180)
    euler_to_quat = cmds.createNode("eulerToQuat", name=transform_object + '_quat')

    # make connections
    cmds.connectAttr(additive_node + '.output', clamp_node + '.inputR')
    cmds.connectAttr(driver_attr, mult_node + '.input1X')
    cmds.connectAttr(mult_node + '.outputX', euler_to_quat + '.inputRotateX')
    cmds.connectAttr(euler_to_quat + '.outputQuatW', transform_object + '.scaleX')
    cmds.connectAttr(euler_to_quat + '.outputQuatW', transform_object + '.scaleY')

    cmds.connectAttr(trans_mult + '.output', additive_node + '.input1')
    cmds.connectAttr(euler_to_quat + '.outputQuatX', trans_mult + '.input2')

    # make the final connection
    cmds.connectAttr(clamp_node + '.outputR', transform_object + '.t' + drive_axis)
    return True


def build_sinusoidal_eye_system(joints=(), driver_attr=""):
    """
    builds the sinusoidal eye system with the joints provided
    :param joints: <tuple, list> array of transform objects, Most notably, joints.
    :param driver_attr: <str> transform_object.attribute.
    :return:
    """
    for jnt in joints:
        build_sinusoidal_system(jnt, driver_attr=driver_attr)
    return True


def create_multiplier(driver_attr="", max_value=0.0, name=""):
    """
    create multiplier
    :param driver_attr: <str> the multiplier attribute value.
    :param max_value: <float>
    :param name: <str>
    :return: <str> the new attribute.
    """
    mult = cmds.createNode("multiplyDivide", name=name+'_multiplier')
    cmds.setAttr(mult + '.operation', 2) # divide
    cmds.setAttr(mult + '.input2X', max_value)
    cmds.connectAttr(driver_attr, mult + '.input1X')

    # create new multiplier attribute
    node_name = driver_attr.split('.')[0]
    attr_name = 'multiplier'
    cmds.addAttr(node_name, at='float', ln=attr_name, dv=0.0)
    cmds.setAttr(node_name + '.' + attr_name, k=1)

    # make clamp
    clamp_node = cmds.createNode('clamp', name=name + "_multClamp")
    cmds.setAttr(clamp_node + '.maxR', 1.0)
    cmds.connectAttr(mult + '.outputX', clamp_node + '.inputR')

    # make final connection
    cmds.connectAttr(clamp_node + '.outputR', node_name + '.' + attr_name)
    return node_name + '.' + attr_name


def pythagorem_unit_system(driver_attr="", driven_attr="", name=""):
   """
   take the x offset value and output the result into the driven attribute.
   float $x = pow(joint1.translateZ, 2);
   joint1.y = sqrt(1 - $x);
   :param driver_attr: <float> the x-value attribute.
   :param driven_attr: <str> optional, the y-value attribute output connection.
                            If not given, a separate attribute will be created.
   :param name: <str> the name to use when creating nodes.
   :return: <bool> True
   """
   mult = cmds.createNode('multiplyDivide', name=name + '_pythPower')
   cmds.setAttr(mult + '.operation', 3) # power
   cmds.connectAttr(driver_attr, mult + '.input1X')
   cmds.setAttr(mult + '.input2X', 2)

   subtract = cmds.createNode('plusMinusAverage', name=name + '_pythSubtract')
   cmds.setAttr(subtract + '.input1D[0]', 1)
   cmds.setAttr(subtract + '.operation', 2) # subtract
   cmds.connectAttr(mult + '.outputX', subtract + '.input1D[1]')

   sqrt = cmds.createNode('multiplyDivide', name=name + '_pythSqrt')
   cmds.setAttr(sqrt + '.operation', 3) # power
   cmds.setAttr(sqrt + '.input2X', 0.5)
   cmds.connectAttr(subtract + '.output1D', sqrt + '.input1X')

   # final connection
   cmds.connectAttr(sqrt + '.outputX', driven_attr)

   return True


def setup_spherical_joint_system(joint_name="", driver_attr="",
                                 driven_attrs=(), max_value=0.0, name="", normalize=False):
    """
    creates the spherical joint system.
    :example:

        from rig_utils import rig_utils
        reload(rig_utils)
        # joints = cmds.ls(sl=1)
        for jnt in joints:
            rig_utils.setup_spherical_joint_system(jnt, driver_attr="translateZ", driven_attrs=('scaleY', 'scaleX'), max_value=1.0, name=jnt)
            scale_factor_value = cmds.getAttr(jnt + '.scaleFactor')
            rig_utils.setup_translation_factor(driver_attr="pSphere1.value", driven_attr=jnt + ".translateZ", multiplier_value=scale_factor_value, name=jnt)

    :param joint_name: <str> the joint to create attributes to.
    :param driver_attr: <str> the driver attribute to connect from.
    :param driven_attrs: <tuple> Optional array, the driven attributes to connect to.
    :param max_value: <float> creates the system based on the maximum translation value of the joint system.
    :param name: <str> the name to use when creating nodes.
    :param normalize: <bool> normalize the scalar output.
    :return:
    """
    if not max_value:
        raise ValueError("[Incorrect max_value parameter] :: No maximum value entered, and cannot equal to 0.0.")
    node_attr = create_multiplier(joint_name + '.' + driver_attr, max_value=max_value, name=name)

    cmds.addAttr(joint_name, at='float', ln='scaleFactor', dv=0.0)
    cmds.setAttr(joint_name + '.scaleFactor', k=1)
    scale_factor_attr = joint_name + '.scaleFactor'

    pythagorem_unit_system(node_attr, scale_factor_attr, name=name)

    if driven_attrs:
        if normalize:
            # normalize the values
            norm = cmds.createNode('multiplyDivide', name=name + '_pythNormalize')
            cmds.setAttr(norm + '.operation', 2) # divide
            cmds.connectAttr(scale_factor_attr, norm + '.input1X')
            cmds.setAttr(norm + '.input2X', cmds.getAttr(scale_factor_attr))
            for driven_attr in driven_attrs:
                cmds.connectAttr(norm + '.outputX', joint_name + '.' + driven_attr, f=1)
        else:
            for driven_attr in driven_attrs:
                cmds.connectAttr(scale_factor_attr, joint_name + '.' + driven_attr, f=1)
    return True


def create_multiplier_factor(driver_attr="", name=""):
    """
    creates the driver attribute
    :param driver_attr:
    :param name:
    :return:
    """
    node_name = driver_attr.split('.')[0]
    mult_factor_attr = node_name + '.multiplier_factor'
    cmds.addAttr(node_name, at='float', ln='multiplier_factor', dv=0.0)
    cmds.setAttr(node_name + '.multiplier_factor', k=1)

    drive_value = cmds.getAttr(driver_attr)

    mult = cmds.createNode('multiplyDivide', name=name + '_multiplierFactor')
    cmds.setAttr(mult + '.operation', 2) # divide
    cmds.setAttr(mult + '.input2X', drive_value)
    cmds.connectAttr(driver_attr, mult + '.input1X')

    # final connection
    cmds.connectAttr(mult + '.outputX', mult_factor_attr)
    return mult_factor_attr


def setup_translation_factor(driver_attr="", driven_attr="", multiplier_value="", name=""):
    """
    sets up the translation factor by a multiplier value.
    :param driver_attr:
    :param driven_attr:
    :param name:
    :param multiplier_value:
    :return:
    """
    # node_name = driven_attr.split('.')[0]
    mult_factor_attr = create_multiplier_factor(driven_attr, name=name)
    mult = cmds.createNode('multDoubleLinear', name=name)
    cmds.connectAttr(mult_factor_attr, mult + '.input1')
    cmds.connectAttr(driver_attr, mult + '.input2')

    driven_value = cmds.getAttr(driven_attr)
    # scale_factor_value = cmds.getAttr(node_name + '.scale_factor')

    mult_value_node = cmds.createNode('multDoubleLinear', name=name + '_valueMultiplier')
    cmds.connectAttr(mult + '.output', mult_value_node + '.input1')
    cmds.setAttr(mult_value_node + '.input2', 1 - multiplier_value)

    add_node = cmds.createNode('addDoubleLinear', name=name + "_addMultiplier")
    cmds.connectAttr(mult_value_node + '.output', add_node + '.input1')
    cmds.setAttr(add_node + '.input2', driven_value)

    clamp = cmds.createNode('clamp', name=name + '_clampMultiplier')
    cmds.setAttr(clamp + '.maxR', 1)
    cmds.connectAttr(add_node + '.output', clamp + '.inputR')

    # final connections
    cmds.connectAttr(clamp + '.outputR', driven_attr)


def setup_normalized_point_constraint(start_ctrl="", end_ctrl="", driven_transforms=()):
    """
    normalized transform setup
    :return:
    """
    length = float(len(driven_transforms))
    for i, trfm in enumerate(driven_transforms):
        multiplier = float(i) / length
        reverse_mult_value = 1.0 - multiplier
        cnst = cmds.pointConstraint((start_ctrl, end_ctrl, trfm), mo=False)[0]
        start_value, end_value = cmds.listAttr(cnst, ud=1)
        cmds.setAttr(cnst + '.' + start_value, multiplier)
        cmds.setAttr(cnst + '.' + end_value, reverse_mult_value)


def setup_variable_point_constraint(start_ctrl="", end_ctrl="", driven_transforms=()):
    """
    normalized transform setup based on unit distances from eachother.
    :return:
    """
    for trfm in driven_transforms:
        start_distance = math_utils.magnitude(start_ctrl, trfm)
        end_distance = math_utils.magnitude(trfm, end_ctrl)
        cnst = cmds.pointConstraint((start_ctrl, end_ctrl, trfm), mo=False)[0]
        start_value, end_value = cmds.listAttr(cnst, ud=1)
        cmds.setAttr(cnst + '.' + start_value, end_distance)
        cmds.setAttr(cnst + '.' + end_value, start_distance)


def clamp_translation(node, driven_attr="", max_value=0.0):
    """
    clamp the specified translation axis.
    :param driven_attr:
    :param max_value:
    :return:
    """
    inc_connection = cmds.listConnections(node + '.' + driven_attr, s=1, d=0, plugs=True)[0]
    clamp = cmds.createNode('clamp', name=node + "_translationClamp")
    cmds.setAttr(clamp + '.maxR', max_value)
    cmds.connectAttr(inc_connection, clamp + '.inputR')

    # final connection
    cmds.connectAttr(clamp + '.outputR', node + '.' + driven_attr, f=1)


def create_sphere(axis=(0.0, 0.0, 1.0), divisions=20, name="guideSphere", radius=1.0):
    """
    creates the sphere
    :param axis:
    :return:
    """
    return cmds.polySphere(name=name, subdivisionsHeight=divisions, subdivisionsAxis=divisions,
                           subdivisionsX=divisions, subdivisionsY=divisions, axis=axis, radius=radius)


def create_sphere_joints(sphere_mesh="", forward_axis='z', name=""):
    """
    creates the joints at the sphere center.
    :return:
    """
    if not name:
        name = "eyeball"
    if not sphere_mesh:
        sphere_mesh, sphere_shape = create_sphere()
    axes = ('x', 'y', 'z')
    joint_orients = ((0.0, 0.0, 0.0), (0.0, -90.0, 0.0), (90.0, 0.0, 90.0))
    # return edge loop by axis value
    edge_loops = mesh_utils.get_edge_loop_points_at_axis(sphere_mesh, axis=forward_axis)
    cmds.xform(sphere_mesh, ws=1, m=1, q=1)

    # create the main joint
    main_jnt = cmds.joint(name=name + 'Base', orientation=joint_orients[axes.index(forward_axis)])

    # set the transform matrix value
    transform = cmds.xform(sphere_mesh, ws=1, m=1, q=1)
    cmds.xform(main_jnt, m=transform)

    index = 0
    joints = {}
    positions = edge_loops.keys()
    positions.sort()
    for position in positions:
        if index > 0:
            vtxs = edge_loops[position]
            names = map(lambda vtx: mesh_utils.get_index_name(sphere_mesh, vtx), vtxs)
            center_position = math_utils.get_center(names)
            edge_loop_jnt = cmds.joint(name=name + letters[index-1] + '_jnt', r=1)
            if index > 1:
                cmds.parent(edge_loop_jnt, main_jnt)
            cmds.xform(edge_loop_jnt, t=center_position, ws=1)
            joints[edge_loop_jnt] = names
        index += 1

    # parent the main joint to the world
    cmds.parent(main_jnt, world=True)

    # skin the sphere
    skin_name = skincluster_utils.apply_skin(sphere_mesh, joints.keys(), name=name + '_skin')[0]
    cmds.select(sphere_mesh + '.vtx[*]')
    cmds.skinPercent(skin_name, transformValue=[(main_jnt, 1.0)])
    for jnt, ids in joints.items():
        cmds.select(ids)
        cmds.skinPercent(skin_name, transformValue=[(jnt, 1.0)])
    cmds.select(d=1)
    return [main_jnt] + sorted(joints.keys())


def construct_eye_rig(radius=1.0):
    sphere_mesh, sphere_shape = create_sphere(radius=radius)
    joints_list = create_sphere_joints(sphere_mesh)
    distance = math_utils.magnitude(joints_list[0], joints_list[-1])
    # exclude the first and last joints
    for jnt in joints_list[1:-1]:
        setup_spherical_joint_system(jnt, driver_attr="translateZ", driven_attrs=('scaleY', 'scaleX'),
                                     max_value=distance, name=jnt, normalize=True)

    # now install the point constraints
    setup_variable_point_constraint(joints_list[0], joints_list[-1], driven_transforms=joints_list[1:-1])

    # clamp the translations
    for jnt in joints_list[1:-1]:
        clamp_translation(jnt, driven_attr='translateZ', max_value=distance)
    return True
