"""
    # load this file as a plugin then execute this code in a python script editor tab
    import maya.cmds as cmds
    sphere = cmds.polysphere()
    pnode = cmds.createnode( 'pynode' )
    cmds.move(1.2, 3.4, 4.5, sphere[0], os=true, wd=true )

    cmds.connectattr( (sphere[0] + '.translatex'), (pnode + '.inputs[0]'), f=true )
    cmds.connectattr( (sphere[0] + '.translatey'), (pnode + '.inputs[1]'), f=true )
    cmds.connectattr( (sphere[0] + '.translatez'), (pnode + '.inputs[2]'), f=true )
    cmds.getattr( (pnode + '.output[0]') )
    cmds.getattr( (pnode + '.output[1]') )
    cmds.getattr( (pnode + '.output[2]') )
"""
import pymel.core as pm

import sys
from maya import OpenMaya
from maya import OpenMayaMPx as ommpx

kPluginNodeTypeName = "pyArray"
kNodeId = OpenMaya.MTypeId(0x87000)

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtGui
from PySide2 import QtWidgets
QPushButton = QtWidgets.QPushButton
QSizePolicy = QtWidgets.QSizePolicy


class pynode(ommpx.MPxNode):

    inputs = OpenMaya.MObject()
    output = OpenMaya.MObject()

    def __init__(self):
        ommpx.MPxNode.__init__(self)

    # def compute(self, plug, datablock):
    #
    #     if (plug == pynode.output) and plug.iselement():
    #
    #         # version 1.0
    #         # this is ineffective and buggy because it goes through all the output plugs even if they
    #         # dont exist yet
    #         """
    #         # get the input handle
    #         datahandle = datablock.inputarrayvalue( pynode.inputs )
    #
    #         # get output handle
    #         outputhandle = datablock.outputarrayvalue( pynode.output )
    #
    #         numelements = datahandle.elementcount()
    #
    #         # iterate through input array and set the output array
    #         for i in range(numelements):
    #
    #             datahandle.jumptoelement(i)
    #             handle = datahandle.inputvalue()
    #             result = handle.asfloat()
    #
    #             outputhandle.jumptoelement(i)
    #             outdatahandle = outputhandle.outputvalue()
    #             outdatahandle.setfloat( result )
    #
    #         datablock.setclean( plug )
    #         """
    #
    #
    #         # version 2.0
    #         # this only checks on the plug that has been changed
    #         # get the input handle
    #         datahandle = datablock.inputarrayvalue(pynode.inputs)
    #
    #         # get output handle
    #         outputhandle = datablock.outputarrayvalue(pynode.output)
    #
    #         # get the element index
    #         index = plug.logicalindex()
    #
    #         # position the arrays at the correct element.
    #         datahandle.jumptoelement(index)
    #         outputhandle.jumptoelement(index)
    #
    #         # copy the input element value to the output element.
    #         outputhandle.outputvalue().setfloat(datahandle.inputvalue().asfloat())
    #
    #

    def compute(self, plug, datablock):
        if (plug == pynode.inputs) and plug.isElement():
            # get the input handle
            datahandle = datablock.inputArrayValue(pynode.inputs)
            numelements = datahandle.elementCount()

            # get output handle and its array data builder
            outputhandle = datablock.outputArrayValue(pynode.output)
            outputbuilder = outputhandle.builder()

            # do some really expensive setup code.

            # iterate through input array and set the output array
            for i in range(numelements):
                datahandle.jumpToElement(i)
                handle = datahandle.inputValue()
                result = handle.asFloat()

                try:
                    outputhandle.jumpToElement(i)
                    outdatahandle = outputhandle.outputValue()
                except:
                    outdatahandle = outputbuilder.addElement(i)

                outdatahandle.setfloat(result)
                outputhandle.set(outputbuilder)

            else:
                return OpenMaya.kUnknownParameter

        if (plug == pynode.output) and plug.isElement():
            # get the input handle
            datahandle = datablock.inputArrayValue(pynode.inputs)

            # get output handle
            outputhandle = datablock.outputArrayValue(pynode.output)

            # get the element index
            index = plug.logicalIndex()

            # position the arrays at the correct element.
            datahandle.jumpToElement(index)
            outputhandle.jumpToElement(index)

            # copy the input element value to the output element.
            outputhandle.outputValue().setFloat(datahandle.inputValue().asFloat())
        else:
            return OpenMaya.kUnknownParameter


def nodeCreator():
    return ommpx.asMPxPtr(pynode())


def nodeInitializer():
    nattr = OpenMaya.MFnNumericAttribute()
    pynode.inputs = nattr.create("inputs", "in", OpenMaya.MFnNumericData.kFloat, 0.0)
    nattr.setArray(1)
    nattr.setStorable(1)
    pynode.addAttribute(pynode.inputs)

    nattr = OpenMaya.MFnNumericAttribute()
    pynode.output = nattr.create("output", "out", OpenMaya.MFnNumericData.kFloat, 0.0)
    nattr.setArray(1)
    nattr.setStorable(1)
    nattr.setWritable(1)
    pynode.addAttribute(pynode.output)

    pynode.attributeAffects(pynode.inputs, pynode.output)


def AEtemplateString(nodeName):
    templStr = ''
    templStr += 'global proc AE%sTemplate(string $nodeName)\n' % nodeName
    templStr += '{\n'
    templStr += 'editorTemplate -beginScrollLayout;\n'

    templStr += '	editorTemplate -beginLayout "General Attributes" -collapse 0;\n'
    templStr += '		editorTemplate -addControl "subdivisions";\n'
    # ....
    templStr += '		editorTemplate -addSeparator;\n'
    templStr += '		editorTemplate -addControl "flipAngle";\n'
    templStr += '		editorTemplate -addSeparator;\n'
    templStr += '		editorTemplate -addControl "twist";\n'
    templStr += '	editorTemplate -endLayout;\n'

    templStr += 'editorTemplate -addExtraControls; // add any other attributes\n'
    templStr += 'editorTemplate -endScrollLayout;\n'
    templStr += '}'
    return templStr


def initializePlugin(m_object):
    mplugin = ommpx.MFnPlugin(m_object)
    try:
        mplugin.registerNode(kPluginNodeTypeName, kNodeId, nodeCreator, nodeInitializer)

    except:
        sys.stderr.write("failed to register node: %s" % kPluginNodeTypeName)
        raise
    OpenMaya.MGlobal.executeCommand(AEtemplateString(kPluginNodeTypeName))


def uninitializePlugin(m_object):
    mplugin = ommpx.MFnPlugin(m_object)
    try:
        mplugin.deregisterNode(kNodeId)
    except:
        sys.stderr.write("failed to deregister node: %s" % kPluginNodeTypeName)
        raise
