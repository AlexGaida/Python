"""
Finally! A Working example found for Maya's viewport 2.0!!!!
Example locator template copied from Dilen Shah.
"""
import sys

from maya.api import OpenMaya
from maya.api import OpenMayaUI
from maya.api import OpenMayaRender


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


# plugin information
kPluginNodeName = "reflectionLocator"
kPluginNodeClassification = "drawdb/geometry/reflectionLocator"
kDrawRegistrantId = "reflectionNodePlugin"
kPluginNodeId = OpenMaya.MTypeId(0x819890)


# define local variables
defaultLineWidth = 1.0
defaultPlaneColor = (0.1, 0.5, 0.1, 1.0)
defaultOutputPoint = (-1.0, 1.0, 0.0)
defaultInputPoint = (1.0, 1.0, 0.0)


# Node implementation with standard viewport draw
class ReflectionLocatorNode(OpenMayaUI.MPxLocatorNode):
    # initialize parameters
    ui_type = 0
    line_width = 1.0

    @staticmethod
    def creator():
        """
        creates an instance of our node plugin and delivers it to Maya as a pointer object.
        :return:
        """
        return ReflectionLocatorNode()

    @staticmethod
    def initialize():
        """
        Defines the set of attributes for our node. The attributes
        declared in this function are assigned as static members to our
        depthShader class. Instances of ReflectionLocatorNode will use these attributes
        to create plugs for use in the compute() method.
        :return:
        """
        eAttr = OpenMaya.MFnEnumAttribute()
        nAttr = OpenMaya.MFnNumericAttribute()
        mAttr = OpenMaya.MFnMatrixAttribute()

        # plane shape
        ReflectionLocatorNode.ui_type = eAttr.create("locatorShape", "ls", 0)
        eAttr.addField("rect", 1)
        eAttr.addField("locator", 2)
        eAttr.addField("circle", 3)
        ReflectionLocatorNode.addAttribute(
            ReflectionLocatorNode.ui_type)

        # creates a vector attribute
        ReflectionLocatorNode.output_point = nAttr.createPoint('output', 'out')
        nAttr.storable = False
        nAttr.hidden = False
        nAttr.default = (defaultPlaneColor[0], defaultPlaneColor[1], defaultPlaneColor[2])
        ReflectionLocatorNode.addAttribute(
            ReflectionLocatorNode.output_point)

        # create a matrix attribute
        ReflectionLocatorNode.plane_matrix = mAttr.create("planeMatrix", "planeMatrix")
        ReflectionLocatorNode.addAttribute(
            ReflectionLocatorNode.plane_matrix)
        ReflectionLocatorNode.attributeAffects(
            ReflectionLocatorNode.plane_matrix, ReflectionLocatorNode.output_point)

        # create a reflected parentInverse attribute
        ReflectionLocatorNode.parent_inverse = mAttr.create("reflectedParentInverse", "rpi")
        mAttr.setDefault(OpenMaya.MMatrix.identity)
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.parent_inverse)
        ReflectionLocatorNode.attributeAffects(ReflectionLocatorNode.parent_inverse, ReflectionLocatorNode.output_point)

        # creates a vector attribute
        ReflectionLocatorNode.input_point = nAttr.createPoint('input', 'in')
        nAttr.storable = True
        nAttr.hidden = False
        nAttr.keyable = True
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.input_point)
        ReflectionLocatorNode.attributeAffects(
            ReflectionLocatorNode.input_point, ReflectionLocatorNode.output_point)

        # create a line width attribute to change the width of a line drawing
        global defaultLineWidth
        ReflectionLocatorNode.line_width = nAttr.create("lineWidth", "lw",
                                                        OpenMaya.MFnNumericData.kFloat, defaultLineWidth)
        nAttr.setMin(0.0)
        nAttr.storable = False
        nAttr.keyable = True
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.line_width)

        # create a color attribute
        global defaultPlaneColor
        ReflectionLocatorNode.plane_color = ReflectionLocatorNode.createColor('planeColor', 'pc')
        nAttr.storable = True
        nAttr.default = (defaultPlaneColor[0], defaultPlaneColor[1], defaultPlaneColor[2])
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.plane_color)

        # create a scale attribute
        ReflectionLocatorNode.scale = nAttr.create("scale", "scale", OpenMaya.MFnNumericData.kDouble, 1.0)
        nAttr.keyable = True
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.scale)
        ReflectionLocatorNode.attributeAffects(ReflectionLocatorNode.scale, ReflectionLocatorNode.output_point)

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)

    def compute(self, plug, data):
        return None

    def draw(self, view, path, style, status):
        return None


class ReflectionLocatorNodeData(OpenMaya.MUserData):
    """
    do not delete after draw.
    """
    def __init__(self):
        OpenMaya.MUserData.__init__(self, False)


class ReflectionLocatorNodeDrawOverride(OpenMayaRender.MPxDrawOverride):
    @staticmethod
    def creator(obj):
        return ReflectionLocatorNodeDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    def __init__(self, obj):
        OpenMayaRender.MPxDrawOverride.__init__(self, obj, ReflectionLocatorNodeDrawOverride.draw)

    def supportedDrawAPIs(self):
        return OpenMayaRender.MRenderer.kOpenGL | \
               OpenMayaRender.MRenderer.kDirectX11 | \
               OpenMayaRender.MRenderer.kOpenGLCoreProfile

    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        # verify data cache
        data = oldData
        if not isinstance(data, ReflectionLocatorNodeData):
            data = ReflectionLocatorNodeData()

        # access shape type
        ui_type = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.ui_type)
        data.ui_type = ui_type.asInt()

        # access plane matrix
        plane_matrix = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.plane_matrix)
        data.plane_matrix = plane_matrix.asMatrix()

        # access input point
        input_point = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.input_point)
        data.line_width = input_point.asPoint()

        # access output point
        output_point = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.output_point)
        data.line_width = output_point.asPoint()

        # access line width
        line_width = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.line_width)
        data.line_width = line_width.asFloat()

        # access the parent inverse
        parent_inverse = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.parent_inverse)
        data.parent_inverse = parent_inverse.asMatrix()

        # access plane color
        plane_color = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.plane_color)
        data.plane_color = plane_color.asColor()

        # access the objects' position
        data.plane_position = OpenMaya.MTransformationMatrix(
            plane_matrix).getTranslation(OpenMaya.MSpace.kPostTransform)

        # access the scale
        scale = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.scale)
        data.scale = scale.asFloat()
        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        """
        The Viewport 2.0 addUIDrawables(Draw) Function
        :param objPath: <OpenMaya.mDagPath> of the locator object.
        :param drawManager: <OpenMaya.MUIDrawManager>
        :param frameContext: <MFrameContext>
        :param data: <MUserData>
        :return: <None>
        """
        if not isinstance(data, ReflectionLocatorNodeData):
            return

        # rectangle
        if data.ui_type == 1:
            line_width = data.line_width
            rect_scale_x = 1.0
            rect_scale_y = 1.0
            is_filled = True
            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor((0.1, 0.5, 0.1, 1.0)))
            drawManager.rect2d(OpenMaya.MPoint(0, 0, 0), OpenMaya.MPoint(0, 1, 0),
                               rect_scale_x, rect_scale_y, is_filled)
            drawManager.endDrawable()

        # locator
        if data.ui_type == 2:
            line_width = data.line_width
            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor((0.5, 0.3, 0.4, 1.0)))
            drawManager.line(OpenMaya.MPoint(0, -1, 0), OpenMaya.MPoint(0, 1, 0))
            drawManager.endDrawable()

            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor((0.8, 0.3, 0.2, 1.0)))
            drawManager.line(OpenMaya.MPoint(-1, 0, 0), OpenMaya.MPoint(1, 0, 0))
            drawManager.endDrawable()

            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor((0.1, 0.5, 0.1, 1.0)))
            drawManager.line(OpenMaya.MPoint(0, 0, -1), OpenMaya.MPoint(0, 0, 1))
            drawManager.endDrawable()

        # circle
        if data.ui_type == 3:
            line_width = data.line_width
            radius = 2.0
            is_filled = True
            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor((0.1, 0.5, 0.1, 1.0)))
            drawManager.circle(OpenMaya.MPoint(0, 0, 0), OpenMaya.MPoint(0, 1, 0), radius, is_filled)
            drawManager.endDrawable()

        # draw the lines from the starting point to the plane point


def calculate_reflection_point(plane_matrix, reflected_parent_inverse, plane_pos, input_point, scale):
    """
    calculates the reflection point
    :param plane_matrix: <OpenMaya.MMatrix>
    :param reflected_parent_inverse: <OpenMaya.MMatrix>
    :param plane_pos: <OpenMaya.MVector>
    :param input_point: <OpenMaya.MVector>
    :param scale: <float>
    :return:
    """
    normal = OpenMaya.MVector(0.0, 1.0, 0.0)
    normal *= plane_matrix
    normal.normalize()

    orig_vector = OpenMaya.MVector(input_point - plane_pos)
    reflected_vector = OpenMaya.MVector(2 * ((normal * orig_vector) * normal) - orig_vector)
    reflected_vector.normalize()
    reflected_vector *= scale

    # calculate the reflected point position
    destination_point = plane_pos + reflected_vector

    # put the point into local space
    destination_point *= reflected_parent_inverse
    return destination_point


def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj, "Alex Gaidachev", "1.0", "Any")

    try:
        plugin.registerNode(kPluginNodeName,
                            kPluginNodeId,
                            ReflectionLocatorNode.creator,
                            ReflectionLocatorNode.initialize,
                            OpenMaya.MPxNode.kLocatorNode,
                            kPluginNodeClassification)
    except:
        sys.stderr.write("Failed to register node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            kPluginNodeClassification,
            kDrawRegistrantId,
            ReflectionLocatorNodeDrawOverride.creator)
    except:
        sys.stderr.write("Failed to register override\n")
        raise


def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)

    try:
        plugin.deregisterNode(kPluginNodeId)
    except:
        sys.stderr.write("Failed to deregister node\n")

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            kPluginNodeClassification, kDrawRegistrantId)
    except:
        sys.stderr.write("Failed to deregister override\n")
