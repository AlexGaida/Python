"""
Finally! A Working example found for Maya's viewport 2.0!!!!
Whoooo!
"""

import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender


# Node implementation with standard viewport draw
class TemplateLocator(OpenMayaUI.MPxLocatorNode):
    id = OpenMaya.MTypeId(0x82307)
    drawDbClassification = "drawdb/geometry/templateLocator"
    drawRegistrantId = "templateLocatorId"
    node = "templateLocator"

    @staticmethod
    def creator():
        return TemplateLocator()

    @staticmethod
    def initialize():
        nAttr = OpenMaya.MFnNumericAttribute()
        TemplateLocator.inputTime = nAttr.create("rainbowColors", "rc", OpenMaya.MFnNumericData.kTime)
        nAttr.setWritable(1)
        nAttr.setStorable(1)
        nAttr.setKeyable(1)
        TemplateLocator.addAttribute(TemplateLocator.input1VecAttr)

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)

    def compute(self, plug, data):
        return None

    def draw(self, view, path, style, status):
        return None


## Viewport 2.0 override implementation

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class TemplateLocatorData(OpenMaya.MUserData):
    def __init__(self):
        # this is here to keep the locator after the draw process
        OpenMaya.MUserData.__init__(self, False)


class TestNodeDrawOverride(OpenMayaRender.MPxDrawOverride):
    @staticmethod
    def creator(obj):
        return TestNodeDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    def __init__(self, obj):
        OpenMayaRender.MPxDrawOverride.__init__(self, obj, TestNodeDrawOverride.draw)

    def supportedDrawAPIs(self):
        # add supports for both GL and DX
        return OpenMayaRender.MRenderer.kOpenGL | OpenMayaRender.MRenderer.kDirectX11 | OpenMayaRender.MRenderer.kOpenGLCoreProfile

    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        # Retrieve data cache (create if does not exist)
        data = oldData
        if not isinstance(data, TemplateLocatorData):
            data = TemplateLocatorData()
        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        # Viewport 2.0 addUIDrawables(Draw) Function
        locatordata = data
        if not isinstance(locatordata, TemplateLocatorData):
            return
        drawManager.beginDrawable()

        textColor = OpenMaya.MColor((1.0, 1.0, 1.0, 1.0))
        drawManager.setColor(textColor)

        drawManager.text(OpenMaya.MPoint(0, 1, 0), "3D SPACE TEXT", OpenMayaRender.MUIDrawManager.kLeft)

        textColor = OpenMaya.MColor((0.5, 0.3, 0.4, 1.0))
        drawManager.setColor(textColor)

        drawManager.text2d(OpenMaya.MPoint(500, 500), "2D SPACE TEXT", OpenMayaRender.MUIDrawManager.kLeft)

        drawManager.endDrawable()


def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj, "Dilen Shah", "1.0", "Any")

    try:
        plugin.registerNode(TemplateLocator.node, TemplateLocator.id, TemplateLocator.creator, TemplateLocator.initialize,
                            OpenMaya.MPxNode.kLocatorNode, TemplateLocator.drawDbClassification)
    except:
        sys.stderr.write("Failed to register node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(TemplateLocator.drawDbClassification,
                                                                 TemplateLocator.drawRegistrantId,
                                                                 TemplateLocator.creator)
    except:
        sys.stderr.write("Failed to register override\n")
        raise


def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)

    try:
        plugin.deregisterNode(TemplateLocator.id)
    except:
        sys.stderr.write("Failed to deregister node\n")
        pass

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            TemplateLocator.drawDbClassification, TemplateLocator.drawRegistrantId)
    except:
        sys.stderr.write("Failed to deregister override\n")
        pass