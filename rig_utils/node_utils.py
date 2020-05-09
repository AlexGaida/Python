"""
node_utils: for managing and constructing node behaviours in Maya.
"""

# import maya modules
from maya import cmds


def create_binary_switch(name='', driver_attr="", driven_attr_0="", driven_attr_1=""):
    """
    creates a binary switch for the controller object.
    :return: <str> blendColors node.
    """
    blend_node = cmds.createNode('blendColors', name=name)
    # setting the value of the first condition switch
    cmds.setAttr(blend_node + '.color1R', 1.0)
    cmds.setAttr(blend_node + '.color1G', 0.0)
    cmds.setAttr(blend_node + '.color1B', 0.0)

    # setting the value of the second condition switch
    cmds.setAttr(blend_node + '.color1R', 0.0)
    cmds.setAttr(blend_node + '.color1G', 1.0)
    cmds.setAttr(blend_node + '.color1B', 0.0)

    # now connect the result
    cmds.connectAttr(driver_attr, blend_node + '.blender')
    cmds.connectAttr(blend_node + '.outputR', driven_attr_0)
    cmds.connectAttr(blend_node + '.outputG', driven_attr_1)
    return blend_node
