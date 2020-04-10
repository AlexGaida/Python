import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as omMPx
import math

kPluginNodeTypeName = "SoftIKConstraint"
kPluginNodeClassify = 'utility/general'
kPluginNodeId = OpenMaya.MTypeId(0x81081)


class SoftIKConstraint(omMPx.MPxConstraint):
    matA = OpenMaya.MObject()
    matB = OpenMaya.MObject()
    matC = OpenMaya.MObject()
    matInv = OpenMaya.MObject()
    soft = OpenMaya.MObject()
    output = OpenMaya.MObject()
    pointX = OpenMaya.MObject()
    pointY = OpenMaya.MObject()
    pointZ = OpenMaya.MObject()
    magRetrieved = 0
    chainLength = 0

    # e=2.71828

    def __init__(self):

        omMPx.MPxConstraint.__init__(self)

    def compute(self, plug, data):

        if plug == SoftIKConstraint.output:

            softVal = data.inputValue(SoftIKConstraint.soft).asFloat()
            inverseWorldMatrix = data.inputValue(SoftIKConstraint.matInv).asMatrix()
            transformAWorldMatrix = data.inputValue(SoftIKConstraint.matA).asMatrix()
            transformBWorldMatrix = data.inputValue(SoftIKConstraint.matB).asMatrix()

            vecAwm = OpenMaya.MPoint() * transformAWorldMatrix
            vecBwm = OpenMaya.MPoint() * transformBWorldMatrix
            vecAB = vecAwm - vecBwm
            currentLength = getMagnitude(vecAB)

            if self.magRetrieved == 0:
                transformCWorldMatrix = data.inputValue(SoftIKConstraint.matC).asMatrix()
                vecCwm = OpenMaya.MPoint() * transformCWorldMatrix
                vecAC = vecAwm - vecCwm
                vecCB = vecCwm - vecBwm
                self.chainLength = getMagnitude(vecAC) + getMagnitude(vecCB)
                self.magRetrieved = 1

            if softVal == 0:
                ratioOfLength = 1
            else:
                affectedLength = self.chainLength * softVal
                unnafectedLength = self.chainLength - affectedLength

                # create a falloff based on where the unnafected length ends. The function creates a curve all the way from 0 to max length but the result is forced to become linear where the unnafected length applies.
                if currentLength <= unnafectedLength:
                    fractionOfLength = currentLength
                else:
                    fractionOfLength = affectedLength * (1 - math.exp(
                        (unnafectedLength - currentLength) / affectedLength)) + unnafectedLength
                ratioOfLength = fractionOfLength / currentLength
            worldPosition = OpenMaya.MVector((vecAwm * (1.0 - ratioOfLength)) + OpenMaya.MVector(vecBwm * ratioOfLength))
            localPosition = worldPosition * inverseWorldMatrix

            outHandle = data.outputValue(SoftIKConstraint.output)
            outHandleX = outHandle.child(SoftIKConstraint.pointX)
            outHandleY = outHandle.child(SoftIKConstraint.pointY)
            outHandleZ = outHandle.child(SoftIKConstraint.pointZ)
            outHandleX.setMDistance(OpenMaya.MDistance(localPosition.x))
            outHandleY.setMDistance(OpenMaya.MDistance(localPosition.y))
            outHandleZ.setMDistance(OpenMaya.MDistance(localPosition.z))

            data.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter


def getMagnitude(vector):
    magnitude = math.sqrt((vector.x * vector.x) + (vector.y * vector.y) + (vector.z * vector.z))
    return magnitude


def nodeCreator():
    return omMPx.asMPxPtr(SoftIKConstraint())


def nodeInitializer():
    inputMatrix = OpenMaya.MFnMatrixAttribute()
    softAttr = OpenMaya.MFnNumericAttribute()
    outputAttr = OpenMaya.MFnUnitAttribute()
    compoundOutputAttr = OpenMaya.MFnNumericAttribute()

    SoftIKConstraint.matB = inputMatrix.create("HandleDriverWorldMatrix", "hcwm")
    inputMatrix.setHidden(1)
    SoftIKConstraint.matA = inputMatrix.create("ChainDriverWorldMatrix", "cdwm")
    inputMatrix.setHidden(1)
    SoftIKConstraint.matC = inputMatrix.create("MiddleJointWorldMatrix", "mjwm")
    inputMatrix.setHidden(1)
    SoftIKConstraint.matInv = inputMatrix.create("HandleParentInverseMatrix", "hpim")
    inputMatrix.setHidden(1)
    SoftIKConstraint.soft = softAttr.create("SoftIKValue", "sik", OpenMaya.MFnNumericData.kFloat, 0)
    softAttr.setMin(0)
    softAttr.setMax(1)
    softAttr.setChannelBox(1)

    # scene scale independent output
    SoftIKConstraint.pointX = outputAttr.create("outputX", "outx", OpenMaya.MFnUnitAttribute.kDistance, 0)
    outputAttr.setWritable(0)
    SoftIKConstraint.pointY = outputAttr.create("outputY", "outy", OpenMaya.MFnUnitAttribute.kDistance, 0)
    outputAttr.setWritable(0)
    SoftIKConstraint.pointZ = outputAttr.create("outputZ", "outz", OpenMaya.MFnUnitAttribute.kDistance, 0)
    outputAttr.setWritable(0)
    SoftIKConstraint.output = compoundOutputAttr.create("Output", "out", SoftIKConstraint.pointX,
                                                        SoftIKConstraint.pointY, SoftIKConstraint.pointZ)
    compoundOutputAttr.setWritable(0)
    compoundOutputAttr.setHidden(1)

    SoftIKConstraint.addAttribute(SoftIKConstraint.matA)
    SoftIKConstraint.addAttribute(SoftIKConstraint.matB)
    SoftIKConstraint.addAttribute(SoftIKConstraint.matC)
    SoftIKConstraint.addAttribute(SoftIKConstraint.matInv)
    SoftIKConstraint.addAttribute(SoftIKConstraint.soft)
    SoftIKConstraint.addAttribute(SoftIKConstraint.output)

    SoftIKConstraint.attributeAffects(SoftIKConstraint.matA, SoftIKConstraint.output)
    SoftIKConstraint.attributeAffects(SoftIKConstraint.matB, SoftIKConstraint.output)
    SoftIKConstraint.attributeAffects(SoftIKConstraint.matC, SoftIKConstraint.output)
    SoftIKConstraint.attributeAffects(SoftIKConstraint.matInv, SoftIKConstraint.output)
    SoftIKConstraint.attributeAffects(SoftIKConstraint.soft, SoftIKConstraint.output)


def initializePlugin(mobject):
    print "> Initialising SoftIK Plugin"
    fnPlugin = omMPx.MFnPlugin(mobject)
    fnPlugin.registerNode(kPluginNodeTypeName, kPluginNodeId, nodeCreator, nodeInitializer, omMPx.MPxNode.kDependNode,
                          kPluginNodeClassify)


def uninitializePlugin(mobject):
    print "> Uninitialising SoftIK Plugin"
    fnPlugin = omMPx.MFnPlugin(mobject)
    fnPlugin.deregisterNode(kPluginNodeId)