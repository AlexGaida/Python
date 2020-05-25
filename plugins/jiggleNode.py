# import standard modules
import math
import sys

# import maya modules
from maya import OpenMayaMPx
from maya import OpenMaya

# define local variables
kNodeId = 0x00001234
kPluginName = 'jigglePoint'


class JigglePoint(OpenMayaMPx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(kNodeId)

    aOutput = OpenMaya.MObject()
    aGoal = OpenMaya.MObject()
    aDamping = OpenMaya.MObject()
    aStiffness = OpenMaya.MObject()
    aTime = OpenMaya.MObject()
    aParentInverse = OpenMaya.MObject()
    aJiggleAmount = OpenMaya.MObject()

    def __init__(self):
        super(JigglePoint, self).__init__()
        self._initialized = False
        self._currentPosition = OpenMaya.MPoint()
        self._previousPosition = OpenMaya.MPoint()
        self._previousTime = OpenMaya.MTime()
        self._currentTime = OpenMaya.MTime()

    def compute(self, plug, data):
        if plug != JigglePoint.aOutput:
            return OpenMaya.kUnknownParameter

        # get inputs
        damping = data.inputValue(self.aDamping).asFloat()
        stiffness = data.inputValue(self.aStiffness).asFloat()
        goal = OpenMaya.MPoint(data.inputValue(self.aGoal).asFloatVector())
        currentTime = data.inputValue(self.aTime).asTime()
        parentInverse = data.inputValue(self.aParentInverse).asMatrix()
        jiggleAmount = data.inputValue(self.aJiggleAmount).asFloat()

        if not self._initialized:
            self._currentPosition = goal
            self._previousPosition = goal
            self._previousTime = currentTime
            self._initialized = True

        # we now need to check if the time step is 1 frame
        timeDifference = currentTime.Value() - self._previousTime.value()
        if timeDifference > 1.0 or timeDifference < 0.0:
            self._initialized = False
            self._previousTime = currentTime
            return None

        velocityVector = (self._currentPosition - self._previousPosition) * (1.0 - damping)
        newPosition = self._currentPosition + velocityVector
        goalForce = (goal - newPosition) * stiffness
        newPosition += goalForce

        # get the states for next computation
        self._previousPosition = OpenMaya.MPoint(self._currentPosition)
        self._currentPosition = OpenMaya.MPoint(newPosition)
        self._currentTime = OpenMaya.MTime(currentTime)

        # determine how much jiggle you want
        newPosition = goal + ((newPosition - goal) * jiggleAmount)

        # get the local space matrix
        newPosition *= parentInverse

        hOutput = data.outputValue(JigglePoint.aOutput)
        outVector = OpenMaya.MFloatVector(newPosition.x, newPosition.y, newPosition.z)
        hOutput.setMFloatVector(outVector)
        hOutput.setClean()
        data.setClean(plug)


def creator():
    """
    creates the Maya object.
    :return: <OpenMayaMPx.MPxPtr> MPx pointer object.
    """
    return OpenMayaMPx.asMPxPtr(JigglePoint())


def initialize():
    """
    creates the node attributes.
    :return: <MStatus>
    """
    nAttr = OpenMaya.MFnNumericAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()
    mAttr = OpenMaya.MMatrixAttribute()

    # creates a vector attribute
    JigglePoint.aOutput = nAttr.createPoint('output', 'out')
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    JigglePoint.addAttribute(JigglePoint.aOutput)

    # creates a vector attribute
    JigglePoint.aGoal = nAttr.createPoint('goal', 'goal')
    JigglePoint.addAttribute(JigglePoint.aGoal)
    JigglePoint.attributeAffects(JigglePoint.aGoal, JigglePoint.aOutput)

    # creates a switch to turn on and off the jiggling.
    JigglePoint.aJiggleAmount = uAttr.create('jiggle', 'jiggle', OpenMaya.MFnUnitAttribute.kFloat, 0.0)
    uAttr.setKeyable(True)
    uAttr.setMin(0.0)
    uAttr.setMax(1.0)
    JigglePoint.addAttribute(JigglePoint.aJiggleAmount)
    JigglePoint.attributeAffects(JigglePoint.aJiggleAmount, JigglePoint.aOutput)

    # creates a time attribute to stop the ball from continuously jiggling after stopping.
    JigglePoint.aTime = uAttr.create('time', 'time', OpenMaya.MFnUnitAttribute.kTime, 0.0)
    JigglePoint.addAttribute(JigglePoint.aTime)
    JigglePoint.attributeAffects(JigglePoint.aTime, JigglePoint.aOutput)

    JigglePoint.aDamping = nAttr.create('stiffness', 'stiffness', OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JigglePoint.addAttribute(JigglePoint.aDamping)
    JigglePoint.attributeAffects(JigglePoint.aDamping, JigglePoint.aOutput)

    JigglePoint.aDamping = nAttr.create('damping', 'damping', OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JigglePoint.addAttribute(JigglePoint.aDamping)
    JigglePoint.attributeAffects(JigglePoint.aDamping, JigglePoint.aOutput)

    JigglePoint.mParentInverse = mAttr.create("parentInverse", "parentInverse")
    JigglePoint.addAttribute(JigglePoint.aParentInverse)


def initializePlugin(mObject):
    """
    initialize the plugin.
    :param mObject:
    """
    mPlugin = OpenMayaMPx.MFnPlugin(
        mObject, 'Alex Gaidachev :: Code From ChadVernon CGCircuit Series', '1.0', 'Any')
    try:
        mPlugin.registerNode(kPluginName, JigglePoint.kPluginNodeId, creator, initialize)
    except:
        sys.stderr.write('Failed to register node: %s\n' % kPluginName)
        raise


def uninitializePlugin(mObject):
    """
    uninitialize the plugin.
    :param mObject:
    """
    mplugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(JigglePoint.kPluginNodeId)
    except:
        sys.stderr.write('Failed to unregister node: %s\n' % kPluginName)
        raise
