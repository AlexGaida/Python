"""
taken from Autodesk Technical Help Documentation
"""

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim

kPluginCmdName = 'myJointChain'

# The length of the chain.
kLengthFlag = '-l'
kLengthLongFlag = '-length'
defaultLength = 3

jointDistance = 5  # the distance between two joints
jointOrientation = 20  # degrees.


##########################################################
# Plug-in
##########################################################
class JointChainCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def parseArgs(self, pArguments):
        ''' Parses the command's arguments. '''

        # Set the default chain length in case there are no arguments.
        global defaultLength
        self.length = defaultLength

        # Obtain the flag value, if the flag is set.
        argData = OpenMaya.MArgParser(self.syntax(), pArguments)
        if argData.isFlagSet(kLengthFlag):

            # Get the value associated with the flag as an integer.
            flagValue = argData.flagArgumentInt(kLengthFlag, 0)

            # Make sure this value is larger than the default length.
            if flagValue > defaultLength:
                self.length = flagValue

    def doIt(self, pArguments):
        ''' Command Execution. '''

        # Parse the passed arguments.
        self.parseArgs(pArguments)

        # Create an instance of an MDagModifier to keep track of the created objects,
        # and to undo their creation in our undoIt() function.
        self.dagModifier = OpenMaya.MDagModifier()

        # Create the joint MObjects we will be manipulating.
        self.jointObjects = []
        for i in range(0, self.length):
            if i == 0:
                # The first joint has no parent.
                newJointObj = self.dagModifier.createNode('joint')
            else:
                # Assign the new joint as a child to the previous joint.
                newJointObj = self.dagModifier.createNode('joint', self.jointObjects[i - 1])
            # Keep track of all the joints created.
            self.jointObjects.append(newJointObj)

        # Create the inverse kinematic effector MObject. The effector is a child of the last joint object.
        # The [-1] index is a Python-specific way of referring to the last item in a list.
        self.effectorObj = self.dagModifier.createNode('ikEffector', self.jointObjects[-1])

        # Invoke the command's redoIt() function to actually create and manipulate these objects.
        self.redoIt()

    def redoIt(self):
        ''' Create and manipulate the nodes to form the joint chain. '''

        # Perform the operations enqueued within our reference to MDagModifier.
        self.dagModifier.doIt()

        # =======================================
        # JOINT MANIPULATION
        # =======================================
        # We can now use the function sets on the newly created DAG objects.
        jointFn = OpenMayaAnim.MFnIkJoint()

        for i in range(1, len(self.jointObjects)):
            jointFn.setObject(self.jointObjects[i])
            # We set the orientation for our joint to be 'jointOrientation' degrees, to form an arc.
            # We use MFnIkJoint.setOrientation() instead of MFnTransform.setRotation() to let the
            # inverse-kinematic handle maintain the curvature.
            global jointOrientation
            rotationAngle = OpenMaya.MAngle(jointOrientation, OpenMaya.MAngle.kDegrees)
            jointFn.setOrientation(
                OpenMaya.MEulerRotation(rotationAngle.asRadians(), 0, 0, OpenMaya.MEulerRotation.kXYZ))

            # We translate the joint by 'jointDistance' units along its parent's y axis.
            global jointDistance
            translationVector = OpenMaya.MVector(0, jointDistance, 0)
            jointFn.setTranslation(translationVector, OpenMaya.MSpace.kTransform)

        # =======================================
        # IK HANDLE MANIPULATION
        # =======================================
        # We will use the MEL command 'ikHandle' to create the handle which will move our joint chain. This command
        # will be enqueued in our reference to the MDagModifier so that it can be undone in our call to MDagModifier.undoIt().

        # Obtain the DAG path of the first joint.
        startJointDagPath = OpenMaya.MDagPath()
        jointFn.setObject(self.jointObjects[0])
        jointFn.getPath(startJointDagPath)

        # Obtain the DAG path of the effector.
        effectorDagPath = OpenMaya.MDagPath()
        effectorFn = OpenMayaAnim.MFnIkEffector(self.effectorObj)
        effectorFn.getPath(effectorDagPath)

        # Enqueue the following MEL command with the DAG paths of the start joint and the end effector.
        self.dagModifier.commandToExecute(
            'ikHandle -sj ' + startJointDagPath.fullPathName() + ' -ee ' + effectorDagPath.fullPathName())

        # We call MDagModifier.doIt() to effectively execute the MEL command and create the ikHandle.
        self.dagModifier.doIt()

    def undoIt(self):
        ''' Undo the command. '''
        # This call to MDagModifier.undoIt() undoes all the operations within the MDagModifier.
        # Observe that the number of calls to MDagModifier.undoIt() does not need to match the number of calls to MDagModifier.doIt().
        self.dagModifier.undoIt()

    def isUndoable(self):
        ''' This function must return True to indicate that it is undoable. '''
        return True


##########################################################
# Plug-in initialization.
##########################################################
def cmdCreator():
    ''' Creates an instance of the command. '''
    return OpenMayaMPx.asMPxPtr(JointChainCommand())


def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    syntax = OpenMaya.MSyntax()
    syntax.addFlag(kLengthFlag, kLengthLongFlag, OpenMaya.MSyntax.kDouble)
    return syntax


def initializePlugin(mobject):
    ''' Initializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write('Failed to register command: ' + kPluginCmdName)
        raise


def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write('Failed to unregister command: ' + kPluginCmdName)
        raise


##########################################################
# Sample usage.
##########################################################
'''
# Copy the following lines and run them in Maya's Python Script Editor:

import maya.cmds as cmds
cmds.loadPlugin( 'jointChain.py' )
cmds.myJointChain( length=4 )
'''