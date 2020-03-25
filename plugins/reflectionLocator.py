"""
Finally! A Working example found for MPxLocator using Maya's viewport 2.0!!!!
Whooooo!
"""
# import standard modules
import sys

# import maya 2.0 modules
from maya.api import OpenMaya
from maya.api import OpenMayaUI
from maya.api import OpenMayaRender


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


# define plugin information
kPluginNodeName = "reflectionLocator"
kPluginNodeClassification = "drawdb/geometry/reflectionLocator"
kDrawRegistrantId = "reflectionNodePlugin"
kPluginNodeId = OpenMaya.MTypeId(0x819890)


# define local variables
defaultLineWidth = 1.0
defaultPlaneColor = (0.2, 0.5, 0.5, 1.0)
defaultOutputPoint = (-1.0, 1.0, 0.0)
defaultInputPoint = (1.0, 1.0, 0.0)
defaultScaleValue = 1.0


# Node implementation with standard viewport draw
class ReflectionLocatorNode(OpenMayaUI.MPxLocatorNode):
    plane_matrix = OpenMaya.MObject()
    plane_position = OpenMaya.MObject()
    reflected_parent_inverse = OpenMaya.MObject()
    input_matrix = OpenMaya.MObject()
    input_point = OpenMaya.MObject()
    scale = OpenMaya.MObject()

    @staticmethod
    def creator():
        """
        creates an instance of our node plugin and delivers it to Maya as a pointer object.
        :return:
        """
        return ReflectionLocatorNode()

    def postConstructor(self):
        """
        run the process after the node has been created.
        :return:
        """
        node_fn = OpenMaya.MFnDependencyNode(self.thisMObject())
        node_fn.setName("reflectionLocatorShape#")

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
        eAttr.default = 2
        ReflectionLocatorNode.addAttribute(
            ReflectionLocatorNode.ui_type)

        # creates a vector attribute
        global defaultOutputPoint
        ReflectionLocatorNode.output_point = nAttr.create('output', 'out', OpenMaya.MFnNumericData.k3Double)
        nAttr.storable = False
        nAttr.hidden = False
        nAttr.default = (defaultOutputPoint[0], defaultOutputPoint[1], defaultOutputPoint[2])
        ReflectionLocatorNode.addAttribute(
            ReflectionLocatorNode.output_point)

        # creates a vector attribute
        global defaultInputPoint
        ReflectionLocatorNode.input_point = nAttr.create('input', 'in', OpenMaya.MFnNumericData.k3Double)
        nAttr.storable = True
        nAttr.hidden = False
        nAttr.keyable = True
        nAttr.default = (defaultInputPoint[0], defaultInputPoint[1], defaultInputPoint[2])
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.input_point)
        ReflectionLocatorNode.attributeAffects(
            ReflectionLocatorNode.input_point, ReflectionLocatorNode.output_point)

        # create a matrix attribute
        ReflectionLocatorNode.plane_matrix = mAttr.create("planeMatrix", "planeMatrix")
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.plane_matrix)
        ReflectionLocatorNode.attributeAffects(ReflectionLocatorNode.plane_matrix, ReflectionLocatorNode.output_point)

        # create a reflected parentInverse attribute
        ReflectionLocatorNode.parent_inverse = mAttr.create("reflectedParentInverse", "rpi")
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.parent_inverse)
        ReflectionLocatorNode.attributeAffects(ReflectionLocatorNode.parent_inverse, ReflectionLocatorNode.output_point)

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
        ReflectionLocatorNode.plane_color = nAttr.createColor('planeColor', 'pc')
        nAttr.storable = True
        nAttr.default = (defaultPlaneColor[0], defaultPlaneColor[1], defaultPlaneColor[2])
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.plane_color)

        # create a scale attribute
        global defaultScaleValue
        ReflectionLocatorNode.scale = nAttr.create("scale", "scale", OpenMaya.MFnNumericData.kDouble, defaultScaleValue)
        nAttr.keyable = True
        ReflectionLocatorNode.addAttribute(ReflectionLocatorNode.scale)
        ReflectionLocatorNode.attributeAffects(ReflectionLocatorNode.scale, ReflectionLocatorNode.output_point)

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)

    def compute(self, plug, data):
        """
        computes the reflection point output_point plug.
        :param plug:
        :param data:
        :return: <NoneType>
        """
        if plug == ReflectionLocatorNode.output_point or \
                        plug == ReflectionLocatorNode.input_point or \
                        plug == ReflectionLocatorNode.scale:
            plane_matrix    = data.inputValue(ReflectionLocatorNode.plane_matrix).asMatrix()
            plane_position  = OpenMaya.MTransformationMatrix(plane_matrix).translation(OpenMaya.MSpace.kPostTransform)
            input_point     = data.inputValue(ReflectionLocatorNode.input_point).asVector()
            scale           = data.inputValue(ReflectionLocatorNode.scale).asDouble()

            reflection_point = calculate_reflection_point(plane_matrix, plane_position, input_point, scale, as_vector=True)

            h_output = data.outputValue(ReflectionLocatorNode.output_point)
            h_output.setMVector(reflection_point)
            h_output.setClean()
            data.setClean(plug)
        return None

    def draw(self, view, path, style, status):
        """
        old draw style, we'll leave this empty in case it comes in useful in the future (which is never.)
        :param view:
        :param path:
        :param style:
        :param status:
        :return: <NoneType>
        """
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
        data.plane_matrix = OpenMaya.MFnMatrixData(plane_matrix.asMObject()).matrix()

        # access input point
        input_point = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.input_point)
        data.input_point = get_vector_value(input_point)

        # access output point
        output_point = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.output_point)
        data.output_point = get_vector_value(output_point)

        # access line width
        line_width = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.line_width)
        data.line_width = line_width.asFloat()

        # access the parent inverse
        # parent_inverse = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.parent_inverse)
        # data.parent_inverse = OpenMaya.MFnMatrixData(parent_inverse.asMObject()).matrix()

        # access plane color
        plane_color = OpenMaya.MPlug(objPath.node(), ReflectionLocatorNode.plane_color)
        data.plane_color = get_vector_value(plane_color)

        # access the objects' position
        data.plane_position = OpenMaya.MTransformationMatrix(
            data.plane_matrix).translation(OpenMaya.MSpace.kPostTransform)

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
        # float variable
        line_width = data.line_width
        # tuple variable
        plane_color = data.plane_color

        # rectangle
        if data.ui_type == 1:
            rect_scale_x = 1.0
            rect_scale_y = 1.0
            is_filled = False
            position = OpenMaya.MPoint(0, 0, 0)
            normal = OpenMaya.MVector(0, 0, 1)
            up = OpenMaya.MVector(0, 1, 0)
            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor(plane_color))
            # For 3d rectangle, the up vector should not be parallel with the normal vector.
            drawManager.rect(position, normal, up, rect_scale_x, rect_scale_y, is_filled)
            drawManager.endDrawable()

        # locator
        if data.ui_type == 2:
            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor(plane_color))
            drawManager.line(OpenMaya.MPoint(0, -1, 0), OpenMaya.MPoint(0, 1, 0))
            drawManager.endDrawable()

            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor(plane_color))
            drawManager.line(OpenMaya.MPoint(-1, 0, 0), OpenMaya.MPoint(1, 0, 0))
            drawManager.endDrawable()

            drawManager.beginDrawable()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor(plane_color))
            drawManager.line(OpenMaya.MPoint(0, 0, -1), OpenMaya.MPoint(0, 0, 1))
            drawManager.endDrawable()

        # circle
        if data.ui_type == 3:
            radius = 2.0
            is_filled = True
            position = OpenMaya.MPoint(0, 0, 0)
            normal = OpenMaya.MVector(0, 1, 0)
            drawManager.beginDrawable()
            drawManager.beginDrawInXray()
            drawManager.setLineWidth(line_width)
            drawManager.setLineStyle(drawManager.kSolid)
            drawManager.setColor(OpenMaya.MColor(plane_color))
            drawManager.circle(position, normal, radius, is_filled)
            drawManager.endDrawInXray()
            drawManager.endDrawable()

        # draw the lines from the starting point to the plane point
        # draw from the input point to the plane point
        drawManager.beginDrawable()
        drawManager.setLineWidth(line_width)
        drawManager.setLineStyle(drawManager.kSolid)
        drawManager.setColor(OpenMaya.MColor(plane_color))
        drawManager.line(OpenMaya.MPoint(data.input_point), OpenMaya.MPoint(data.plane_position))
        drawManager.endDrawable()

        # draw from the plane point to the output point
        drawManager.beginDrawable()
        drawManager.setLineWidth(line_width)
        drawManager.setLineStyle(drawManager.kSolid)
        drawManager.setColor(OpenMaya.MColor(plane_color))
        drawManager.line(OpenMaya.MPoint(data.plane_position), OpenMaya.MPoint(data.output_point))
        drawManager.endDrawable()


def get_vector_value(in_plug):
    """
    grab the vector values and store them as a tuple
    :param in_plug: <OpenMaya.MPlug>
    :return: <tuple> XYZ vector values.
    """
    vector_result = ()
    if in_plug.isCompound:
        # get the compound numeric attribute vector
        for c in xrange(in_plug.numChildren()):
            ch_item = in_plug.child(c)
            api_type = OpenMaya.MFnNumericAttribute(ch_item.attribute()).numericType()
            if api_type in (OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble):
                vector_result += ch_item.asDouble(),
        return vector_result


def calculate_reflection_point(plane_matrix, plane_pos, input_point, scale, as_vector=False):
    """
    calculates the reflection point
        R = 2(N * L) * N - L
    :param plane_matrix: <OpenMaya.MMatrix>
    :param plane_pos: <OpenMaya.MVector>
    :param input_point: <OpenMaya.MVector>
    :param scale: <float>
    :param as_vector: <bool> return as an MVector output value.
    :return: <OpenMaya.MVector>
    """
    normal = OpenMaya.MVector(0.0, 1.0, 0.0)
    normal *= plane_matrix
    normal.normalize()

    # calculate the original vector
    orig_vector = OpenMaya.MVector(input_point - plane_pos)

    # get opposing vector through double cross product
    opposing_vector = normal * (2 * (normal * orig_vector))
    opposing_vector -= orig_vector

    # now multiply it by the scalar value
    opposing_vector *= scale

    # calculate the reflected point position
    vector = plane_pos + opposing_vector
    if as_vector:
        return vector
    return vector.x, vector.y, vector.z


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
