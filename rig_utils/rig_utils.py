"""
rig utility module for building rig components.
"""


from maya import cmds


def build_stretch(start_joint, end_joint):
    """
    builds the joint as stretchy joint.
    :param start_joint:
    :param end_joint:
    :return:
    """
    cmds.setAttr("%s.jointOrientY" % listAllJointsInSelection[0], 0)

    # Creates the splineIK to the selected joint hierarchy.
    splineIk = cmds.ikHandle(startJoint=startJoint, endEffector=endJoint, sol="ikSplineSolver", numSpans=numberOfPoints,
                             scv=True, pcv=False, createCurve=True)
    splineCrvCvs = cmds.ls(splineIk[2] + '.cv[*]', flatten=True)

    sysGrp = cmds.group(splineIk[0], splineIk[2], name='sys_stretch_grp')

    # Adds the cluster locators.
    startPt = cmds.xform(splineCrvCvs[0], worldSpace=True, translation=True, query=True)
    lastPt = cmds.xform(splineCrvCvs[-1], worldSpace=True, translation=True, query=True)

    cvStartLocator = cmds.spaceLocator(name='start_loc')[0]
    cvEndLocator = cmds.spaceLocator(name='end_loc')[0]

    for eachScale in ['.localScaleX', '.localScaleY', '.localScaleZ']:
        print cvStartLocator + eachScale
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

    for eachJoint in listAllJointsInSelection[:-1]:
        translationX = cmds.getAttr(eachJoint + '.translateX')
        transXDiff = cmds.createNode('multiplyDivide', name='translationDifference')
        cmds.setAttr(transXDiff + '.operation', 1)
        cmds.setAttr(transXDiff + '.input1X', translationX)
        cmds.connectAttr(lengthDiff + '.outputX', transXDiff + '.input2X')
        cmds.connectAttr(transXDiff + '.outputX', eachJoint + '.tx')

    cmds.parent(selection, scaleGrp, ctlGrp, sysGrp, stretchLocGrp)
