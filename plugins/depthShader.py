# depthShader.py

import sys
import math
import maya.api.OpenMaya as OpenMaya


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


# Plug-in information:
kPluginNodeName = 'pyMyDepthShader'
kPluginNodeClassify = 'utility/general'
kPluginNodeId = OpenMaya.MTypeId(0x870FE)

# Default attribute values
defaultNearDistance = 20.0
defaultFarDistance = 70.0
defaultNearColor = (1.0, 1.0, 1.0)  # (r,g,b) white
defaultFarColor = (0.0, 0.0, 0.0)  # (r,g,b) black
defaultGamma = 1.0
minGamma = 0.1
maxGamma = 5.0


##########################################################
# Plug-in
##########################################################
class depthShader(OpenMaya.MPxNode):
    ''' Creates a depth shader which renders in Maya's software renderer. '''
    # Define the static variables to which we will assign the node's attributes
    # in nodeInitializer() defined below.
    surfacePointAttribute = OpenMaya.MObject()
    nearDistanceAttribute = OpenMaya.MObject()
    farDistanceAttribute = OpenMaya.MObject()
    nearColorAttribute = OpenMaya.MObject()
    farColorAttribute = OpenMaya.MObject()
    gammaAttribute = OpenMaya.MObject()
    outColorAttribute = OpenMaya.MObject()

    def __init__(self):
        ''' Constructor. '''
        OpenMaya.MPxNode.__init__(self)

    def compute(self, pPlug, pDataBlock):
        '''
        Node computation method.
          - pDataBlock contains the data on which we will base our computations.
          - pPlug is a connection point related to one of our node attributes (either an input or an output).
        '''
        if (pPlug == depthShader.outColorAttribute):

            # Get the data handles corresponding to your attributes among the values in the data block.
            surfacePointDataHandle = pDataBlock.inputValue(depthShader.surfacePointAttribute)
            nearDistanceDataHandle = pDataBlock.inputValue(depthShader.nearDistanceAttribute)
            farDistanceDataHandle = pDataBlock.inputValue(depthShader.farDistanceAttribute)
            nearColorDataHandle = pDataBlock.inputValue(depthShader.nearColorAttribute)
            farColorDataHandle = pDataBlock.inputValue(depthShader.farColorAttribute)
            gammaDataHandle = pDataBlock.inputValue(depthShader.gammaAttribute)

            # Obtain the (x,y,z) location of the currently rendered point in camera coordinates.
            surfacePoint = surfacePointDataHandle.asFloatVector()

            # Since the camera is looking along its negative Z axis (the Y axis is
            # the up vector), we must take the absolute value of the Z coordinate
            # to obtain the point's depth.
            depth = abs(surfacePoint.z)

            # Get the actual near and far threshold values.
            nearValue = nearDistanceDataHandle.asFloat()
            farValue = farDistanceDataHandle.asFloat()

            # Find the proportion of depth between the near and far values.
            if ((farValue - nearValue) == 0):
                # Avoid a division by zero if the near and far values somehow have the same value.
                depthProportion = 0
            else:
                depthProportion = (depth - nearValue) / (farValue - nearValue)

            # Clamp the depthProportion value in the interval [0.0, 1.0]
            depthProportion = max(0, min(depthProportion, 1.0))

            # Modify the depth proportion using the gamma roll-off bias.
            gammaValue = gammaDataHandle.asFloat()
            depthProportion = math.pow(depthProportion, gammaValue)

            # Linearly interpolate the output color based on the depth proportion.
            outColor = OpenMaya.MFloatVector(0, 0, 0)
            nearColor = nearColorDataHandle.asFloatVector()
            farColor = farColorDataHandle.asFloatVector()

            outColor.x = nearColor.x + ((farColor.x - nearColor.x) * depthProportion)
            outColor.y = nearColor.y + ((farColor.y - nearColor.y) * depthProportion)
            outColor.z = nearColor.z + ((farColor.z - nearColor.z) * depthProportion)

            # Write to the output data.
            outColorDataHandle = pDataBlock.outputValue(depthShader.outColorAttribute)
            outColorDataHandle.setMFloatVector(outColor)
            outColorDataHandle.setClean()
        else:
            return OpenMaya.kUnknownParameter


##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():
    '''
    Creates an instance of our node plug-in and delivers it to Maya as a pointer.
    '''
    return depthShader()


def nodeInitializer():
    '''
    Defines the set of attributes for our node. The attributes
    declared in this function are assigned as static members to our
    depthShader class. Instances of depthShader will use these attributes
    to create plugs for use in the compute() method.
    '''
    # Create a numeric attribute function set, since our attributes will all be defined by numeric types.
    numericAttributeFn = OpenMaya.MFnNumericAttribute()

    # ==================================
    # INPUT NODE ATTRIBUTE(S)
    # ==================================
    # - The (x,y,z) point on the surface defined according to the camera's frame of reference.
    #   > (!) Important: the 'pointCamera' string relates to the samplerInfo maya node.
    #   > This value is supplied by the render sampler at computation time.
    depthShader.surfacePointAttribute = numericAttributeFn.createPoint('pointCamera', 'p')
    numericAttributeFn.storable = False
    numericAttributeFn.hidden = True
    depthShader.addAttribute(depthShader.surfacePointAttribute)

    # - The 'near' distance, i.e. the minimum distance threshold from the camera after which the
    #   pixel's color is modified by the depth of the point.
    #   > This value can be defined by the user, and is storable.
    global defaultNearDistance, defaultFarDistance
    depthShader.nearDistanceAttribute = numericAttributeFn.create('nearDistance', 'nd',
                                                                  OpenMaya.MFnNumericData.kFloat, defaultNearDistance)
    numericAttributeFn.storable = True
    numericAttributeFn.setMin(0.0)
    numericAttributeFn.setMax(defaultFarDistance)
    depthShader.addAttribute(depthShader.nearDistanceAttribute)

    # - The 'far' distance, i.e. the minimum distance threshold from the camera before which the
    #   pixel's color is modified by the depth of the point.
    #   > This value can be defined by the user, and is storable.
    depthShader.farDistanceAttribute = numericAttributeFn.create('farDistance', 'fd',
                                                                 OpenMaya.MFnNumericData.kFloat, defaultFarDistance)
    numericAttributeFn.storable = True
    numericAttributeFn.setMin(defaultFarDistance + 0.1)  # Add an epsilon value of 0.1 to avoid near distance overlap.
    numericAttributeFn.setMax(3 * defaultFarDistance)
    depthShader.addAttribute(depthShader.farDistanceAttribute)

    # - The 'near' color.
    #   > This value can be defined by the user using a color picker, and is storable.
    global defaultNearColor
    depthShader.nearColorAttribute = numericAttributeFn.createColor('nearColor', 'nc')
    numericAttributeFn.storable = True
    numericAttributeFn.default = (defaultNearColor[0], defaultNearColor[1], defaultNearColor[2])
    depthShader.addAttribute(depthShader.nearColorAttribute)

    # - The 'far' color.
    #   > This value can be defined by the user using a color picker, and is storable.
    global defaultFarColor
    depthShader.farColorAttribute = numericAttributeFn.createColor('farColor', 'fc')
    numericAttributeFn.storable = True
    numericAttributeFn.default = (defaultFarColor[0], defaultFarColor[1], defaultFarColor[2])
    depthShader.addAttribute(depthShader.farColorAttribute)

    # - The gamma value, or roll-off bias, which will affect how the color is interpolated between
    #   the near and far colors.
    #   > This value can be defined by the user using a slider, and is storable.
    global defaultGamma, minGamma, maxGamma
    depthShader.gammaAttribute = numericAttributeFn.create('gamma', 'g',
                                                           OpenMaya.MFnNumericData.kFloat, defaultGamma)
    numericAttributeFn.storable = True
    numericAttributeFn.setMin(minGamma)
    numericAttributeFn.setMax(maxGamma)
    depthShader.addAttribute(depthShader.gammaAttribute)

    # ==================================
    # OUTPUT NODE ATTRIBUTE(S)
    # ==================================
    # - The pixel color output.
    #   > This value is computed in our depthShader.compute() method, and should not be stored.
    depthShader.outColorAttribute = numericAttributeFn.createColor('outColor', 'oc')
    numericAttributeFn.storable = False
    numericAttributeFn.writable = False
    numericAttributeFn.readable = True
    numericAttributeFn.hidden = False
    depthShader.addAttribute(depthShader.outColorAttribute)

    # ==================================
    # NODE ATTRIBUTE DEPENDENCIES
    # ==================================
    #  - All the input attributes affect the computation of the pixel color output (outColor).
    depthShader.attributeAffects(depthShader.surfacePointAttribute, depthShader.outColorAttribute)
    depthShader.attributeAffects(depthShader.nearDistanceAttribute, depthShader.outColorAttribute)
    depthShader.attributeAffects(depthShader.farDistanceAttribute, depthShader.outColorAttribute)
    depthShader.attributeAffects(depthShader.nearColorAttribute, depthShader.outColorAttribute)
    depthShader.attributeAffects(depthShader.farColorAttribute, depthShader.outColorAttribute)
    depthShader.attributeAffects(depthShader.gammaAttribute, depthShader.outColorAttribute)


def initializePlugin(mobject):
    ''' Initializes the plug-in. '''
    mplugin = OpenMaya.MFnPlugin(mobject)
    try:
        mplugin.registerNode(kPluginNodeName,
                             kPluginNodeId,
                             nodeCreator,
                             nodeInitializer,
                             OpenMaya.MPxNode.kDependNode,
                             kPluginNodeClassify)
    except:
        sys.stderr.write("Failed to register node: " + kPluginNodeName)
        raise


def uninitializePlugin(mobject):
    ''' Unitializes the plug-in. '''
    mplugin = OpenMaya.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(kPluginNodeId)
    except:
        sys.stderr.write("Failed to deregister node: " + kPluginNodeName)
        raise
