import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya

class arrayTest(OpenMayaMPx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0x00000012) #change this number to something unique

    input1VecAttr = OpenMaya.MObject()
    output1WgtAttr = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == arrayTest.output1WgtAttr:
        #calculations here
        #get inputs
        dataHandleInput = dataBlock.inputValue(arrayTest.input1VecAttr)
        inVal = dataHandleInput.asFloat()

        #get ouput array
        arrayDataHandle = OpenMaya.MArrayDataHandle(dataBlock.outputArrayValue(arrayTest.output1WgtAttr))
        myBuilder = OpenMaya.MArrayDataBuilder(arrayTest.output1WgtAttr, 0)

        for i in range(arrayDataHandle.elementCount()):
            #arrayDataHandle.next()
            output = inVal/(i+1)
            #output = inVal + outValue

            myElementHandle = OpenMaya.MDataHandle(myBuilder.addElement(i))
            myElementHandle.setFloat(output)

        arrayDataHandle.set(myBuilder)
        arrayDataHandle.setAllClean()

        dataBlock.setClean(plug)

    else:
        return OpenMaya.kUnknownParameter

def creator():
    return OpenMayaMPx.asMPxPtr(arrayTest())

def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    arrayTest.input1VecAttr = nAttr.create("input", "in", OpenMaya.MFnNumericData.kFloat)
    #nAttr.setConnectable(1)
    #nAttr.setArray(1)
    #nAttr.setUsesArrayDataBuilder(1)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    arrayTest.addAttribute(arrayTest.input1VecAttr)

    nAttr = OpenMaya.MFnNumericAttribute()
    arrayTest.output1WgtAttr = nAttr.create("Output", "out", OpenMaya.MFnNumericData.kFloat)
    #nAttr.setConnectable(0)
    nAttr.setArray(1)
    nAttr.setUsesArrayDataBuilder(1)
    nAttr.setReadable(1)
    nAttr.setWritable(0)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    arrayTest.addAttribute(arrayTest.output1WgtAttr)

    arrayTest.attributeAffects(arrayTest.input1VecAttr, arrayTest.output1WgtAttr)

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'Author', '1.0')
    try:
        plugin.registerNode('arrayTest', arrayTest.kPluginNodeId, creator, initialize)
    except:
        raise RuntimeError, 'Failed to register node'


def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(arrayTest.kPluginNodeId)
    except:
        raise RuntimeError, 'Failed to register node'