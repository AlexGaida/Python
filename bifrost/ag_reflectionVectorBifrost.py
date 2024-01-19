"""Understanding Maya Bifrost and the associated Maya's Python Commands to create a mirror transform vector math
Bifrost Graph is a compiled graoh, with what you see is akin to C++ source code.

Copyright 2024 Alexei Gaidachev

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# import maya modules
from maya import cmds

# define global functions
hide_channels = lambda x: [cmds.setAttr(x + '.' + a, k=False, lock=True) for a in [''.join((t, f,)) for t in 'trs' for f in 'xyz'] + ['v']]

def create_default_test():
    """creates a default plane for the mirror matrix
    """
    plane_node =cmds.polyPlane(w=1, h=1, sx=1, sy=1, ax=(0, 1, 0), cuv=2, ch=0)[0]
    # clean the node
    hide_channels(plane_node)
    set_display_referenced(plane_node)
    start_loc = create_locator_node(name="startLoc")
    set_translate_vector(start_loc, (1, 1, 0))
    mirror_loc = create_locator_node(name="mirrorLoc")
    hide_channels(mirror_loc)
    set_translate_vector(mirror_loc, (-1, 1, 0))
    base_loc = create_locator_node(name="BaseLoc")
    #...create a mirror reflection vector maya bifrost
    reflection_vector_node = create_reflection_vector_compound("mirror_vector")
    connect_attr(start_loc, "translate", reflection_vector_node, "source_vector")
    connect_attr(plane_node, "xformMatrix", reflection_vector_node, "plane_matrix")
    connect_attr(reflection_vector_node, "mirror_vector", mirror_loc, "translate")
    set_node_value(reflection_vector_node, "scale", 1.0)
    parent_node(reflection_vector_node, plane_node, start_loc, mirror_loc, base_loc)
    return plane_node

def parent_node(*args):
    """parent transform nodes
    """
    cmds.parent(args)

def set_node_value(node_name, node_attr, value):
    """set values to a node
    """
    cmds.setAttr("{}.{}".format(node_name, node_attr), value)

def create_mirror_vector(transform_node=None, selection=False):
    """creates a mirror vector based on either the selection or the transform node given, but not both
    :param transform_node: (str, ) transform node to use as the source vector to build mirror vector from
    :param selection: (bool, ) build the mirror vector from the selection
    """
    if selection:
        transform_node = cmds.ls(sl=True)
    if not transform_node:
        cmds.confirmDialog(message="Invalid selection, must specify a transform node.", cancelButton="Ok", title="Error")
        raise ValueError("Please select an object to create a mirror transform")
    #..raise error here if selection is invalid
    reflection_vector_node = create_reflection_vector_compound("mirror_vector")
    connect_attr(transform_node, "translate", reflection_vector_node, "source_vector")
    mirror_loc = create_locator_node(name="{}_mirrorLoc".format(transform_node))
    hide_channels(mirror_loc)
    connect_attr(reflection_vector_node, "mirror_vector", mirror_loc, "translate")

def connect_attr(source_node, source_attr, destination_node, destination_attr):
    """connect source attribute to the destination attribute
    :param source_node: (str, ) the source node name
    :param source_attr: (str, ) the source attribute name
    :param destination_node: (str, ) the destination node name
    :param destination_attr: (str, ) the destination attribute name
    """
    cmds.connectAttr("{}.{}".format(source_node, source_attr), "{}.{}".format(destination_node, destination_attr))

def set_translate_vector(node_name, vector=(0, 1, 0)):
    """sets the translation vector to the node name
    """
    cmds.xform(node_name, t=vector, ws=True)

def set_display_referenced(node_name):
    """sets the transform node to display referenced
    """
    cmds.setAttr(node_name + '.overrideEnabled', True)
    cmds.setAttr(node_name + '.overrideDisplayType', 2)
    return True

def create_locator_node(name="startLoc"):
    """creates the locator node
    :name: (str, ) the name to use for creating the locators
    """
    if not name.endswith('Shape'):
        name += 'Shape'
    cmds.createNode('locator', name=name)
    locator_node = cmds.listRelatives(name, p=True)[0]
    return locator_node

def test_system():
   """Test the bifrost mirror vector system
   """ 
   cmds.createNode('locator', name="startLocator")
   cmds.createNode('locator', name="mirrorLocator")

def create_reflection_vector_compound(name):
    """Creates a reflection vector using Maya bifrost
    :param name: (str, ) name the mirror vector bifrost compound node setup
    """
    bifrost_graph_node = create_bifrost_node(name)
    #...add input node ports
    add_input_node_input_port_type_float3(bifrost_graph_node, "source_vector")
    add_input_node_input_port_type_float(bifrost_graph_node, "scale")
    add_input_node_input_port_type_matrix(bifrost_graph_node, "plane_matrix")
    #...add output node ports
    add_output_node_output_port_type_float3(bifrost_graph_node, "mirror_vector")
    #...create 13 math nodes
    normal_vector_node = create_float3_node(bifrost_graph_node, "normalVector")
    set_float3_port_value(bifrost_graph_node, normal_vector_node, "value", (2, 0, 0))
    plane_matrix_node = create_SRT_to_matrix_node(bifrost_graph_node, "planeMatrix")
    plane_translate_node = create_matrix_to_SRT_node(bifrost_graph_node, "planeTranslate")
    mirror_source_node = create_matrix_to_SRT_node(bifrost_graph_node, "mirror_source")
    matrix_multiply_node = create_matrix_multiply_node(bifrost_graph_node)
    #...add node ports
    add_input_port_type_matrix(bifrost_graph_node, matrix_multiply_node, "plane_matrix")
    add_input_port_type_matrix(bifrost_graph_node, matrix_multiply_node, "transform")
    vector_subtract_node = create_subtract_node(bifrost_graph_node, "originalVector")
    #...add node ports
    add_input_port_type_float3(bifrost_graph_node, vector_subtract_node, "original_vector")
    add_input_port_type_float3(bifrost_graph_node, vector_subtract_node, "plane_vector")
    vector_multiply_node = create_multiply_node(bifrost_graph_node, "normalizedSourceVector")
    #...add node ports
    add_input_port_type_float3(bifrost_graph_node, vector_multiply_node, "translation")
    add_input_port_type_float3(bifrost_graph_node, vector_multiply_node, "original_vector")
    normalize_node = create_normalize_node(bifrost_graph_node)
    float_2_node = create_float_node(bifrost_graph_node, "scalar_value_2")
    set_float_port_value(bifrost_graph_node, float_2_node, "value", 2.0)
    vector_multiply2_node = create_multiply_node(bifrost_graph_node, "multiply_float3")
    #...add node ports
    add_input_port_type_float3(bifrost_graph_node, vector_multiply2_node, "normalizedVector")
    add_input_port_type_float3(bifrost_graph_node, vector_multiply2_node, "normal1")
    add_input_port_type_float3(bifrost_graph_node, vector_multiply2_node, "normal2")
    add_input_port_type_float(bifrost_graph_node, vector_multiply2_node, "scalar")
    vector_subtract2_node = create_subtract_node(bifrost_graph_node)
    #...add node ports
    add_input_port_type_float3(bifrost_graph_node, vector_subtract2_node, "mirror_vector")
    add_input_port_type_float3(bifrost_graph_node, vector_subtract2_node, "mirror_to_normal")
    vector_multiply3_node = create_multiply_node(bifrost_graph_node)
    #...add node ports
    add_input_port_type_float3(bifrost_graph_node, vector_multiply3_node, "normalized")
    add_input_port_type_float3(bifrost_graph_node, vector_multiply3_node, "scale")
    vector_addition_node = create_add_node(bifrost_graph_node)
    #...add node ports
    add_input_port_type_float3(bifrost_graph_node, vector_addition_node, "translation")
    add_input_port_type_float3(bifrost_graph_node, vector_addition_node, "plane_matrix")
    #...connect the nodes
    connect_nodes(bifrost_graph_node, normal_vector_node, "output", plane_matrix_node, "translation")
    connect_nodes(bifrost_graph_node, 'input', "plane_matrix", matrix_multiply_node, "plane_matrix")
    connect_nodes(bifrost_graph_node, plane_matrix_node, "transform", matrix_multiply_node, "transform")
    connect_nodes(bifrost_graph_node, matrix_multiply_node, "matrix", plane_translate_node, "transform")
    connect_nodes(bifrost_graph_node, plane_translate_node, "translation", normalize_node, "value")
    connect_nodes(bifrost_graph_node, "input", "plane_matrix", mirror_source_node, "transform")
    connect_nodes(bifrost_graph_node, "input", "source_vector", vector_subtract_node, "plane_vector")
    connect_nodes(bifrost_graph_node, mirror_source_node, "translation", vector_subtract_node, "original_vector")
    connect_nodes(bifrost_graph_node, vector_subtract_node, "output", vector_multiply_node, "original_vector")
    connect_nodes(bifrost_graph_node, normalize_node, "normalized", vector_multiply_node, "translation")
    #...attach to mirror formula
    connect_nodes(bifrost_graph_node, vector_multiply_node, "output", vector_multiply2_node, "normalizedVector")
    connect_nodes(bifrost_graph_node, float_2_node, "output", vector_multiply2_node, "scalar")
    connect_nodes(bifrost_graph_node, normalize_node, "normalized", vector_multiply2_node, "normal1")
    connect_nodes(bifrost_graph_node, normalize_node, "normalized", vector_multiply2_node, "normal2")
    connect_nodes(bifrost_graph_node, vector_multiply2_node, "output", vector_subtract2_node, "mirror_vector")
    connect_nodes(bifrost_graph_node, vector_subtract_node, "output", vector_subtract2_node, "mirror_to_normal")
    connect_nodes(bifrost_graph_node, "input", "scale", vector_multiply3_node, "scale")
    connect_nodes(bifrost_graph_node, vector_subtract2_node, "output", vector_multiply3_node, "normalized")
    connect_nodes(bifrost_graph_node, vector_subtract2_node, "output", vector_addition_node, "translation")
    connect_nodes(bifrost_graph_node, mirror_source_node, "translation", vector_addition_node, "plane_matrix")
    connect_nodes(bifrost_graph_node, vector_addition_node, "output", "output", "mirror_vector")
    return bifrost_graph_node

def connect_nodes(bifrost_node, source_noce, node_attr, destination_node, destination_node_attr):
    """connect the two node plugs
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr: (str, ) the source node attribure
    :param destination_node_attr: (str, ) the destination node attribute
    Example:
        vnnConnect "|bifrostGraph2|bifrostGraphShape2" ".matrix1" "/matrix_determinant.matrix" -copyMetaData;
    """
    cmds.vnnConnect(bifrost_node, "/"+source_noce + '.' + node_attr,  "/"+destination_node + '.' + destination_node_attr, copyMetaData=True)
    return True

def create_bifrost_node(name):
    """creates a new bifrost graph compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :return: (str, ) bifrost node to create node with
    """
    if cmds.objExists(name):
        return name
    bifrost_node = cmds.createNode("bifrostGraphShape", name="{}_reflectionVectorBifrostShape".format(name))
    return bifrost_node

def add_input_port(bifrost_node, input_attr_name, input_attr_type):
    """adds an input node attr name and type to the bifrost node
    :param bifrost_node:(str, ) bifrost compound node name
    """
    cmds.vnnNode(bifrost_node, "/input", createOutputPort=(input_attr_name, input_attr_type))

def change_port_type_matrix(bifrost_node, input_port_name):
    """changes the input/ output node port to type matrix
    :param bifrost_node:(str, ) bifrost compound node name
    :param input_port_name: (str, ) name the input port
    """
    cmds.vnnCompound(bifrost_node, "/", setPortDataType=(input_port_name, "Math::float4x4"))

def change_port_type_float3(bifrost_node, input_port_name):
    """changes the input/output node port to type float3
    :param bifrost_node:(str, ) bifrost compound node name
    :param input_port_name: (str, ) name the input port
    """
    cmds.vnnCompound(bifrost_node, "/", setPortDataType=(input_port_name, "Math::float3"))

def change_port_type_float(bifrost_node, input_port_name):
    """changes the input/output node port to type float
    :param bifrost_node:(str, ) bifrost compound node name
    :param input_port_name: (str, ) name the input port
    """
    cmds.vnnCompound(bifrost_node, "/", setPortDataType=(input_port_name, "float3"))

def add_output_node_output_port_type_float3(bifrost_node, node_attr_name):
    """creates an output node of type float3
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/output", createInputPort=(node_attr_name, "Math::float3"))

def add_input_node_input_port_type_float3(bifrost_node, node_attr_name):
    """adds an input port of type float3 to the compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/input", createOutputPort=(node_attr_name, "Math::float3"))

def add_input_node_input_port_type_float(bifrost_node, node_attr_name):
    """adds an input port of type float to the compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/input", createOutputPort=(node_attr_name, "float"))

def add_input_node_input_port_type_matrix(bifrost_node, node_attr_name):
    """adds an input port of type float to the compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/input", createOutputPort=(node_attr_name, "Math::float4x4"))

def add_input_port_type_matrix(bifrost_node, node_name, node_attr_name):
    """adds an input port of type float to the compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/{}".format(node_name), createInputPort=(node_attr_name, "Math::float4x4"))

def add_input_port_type_float(bifrost_node, node_name, node_attr_name):
    """adds an input port of type float to the compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/{}".format(node_name), createInputPort=(node_attr_name, "float"))

def add_input_port_type_float3(bifrost_node, node_name, node_attr_name):
    """adds an input port of type float to the compound node
    :param bifrost_node:(str, ) bifrost compound node name
    :param node_attr_name: (str, ) name the input port
    """
    cmds.vnnNode(bifrost_node, "/{}".format(node_name), createInputPort=(node_attr_name, "Math::float3"))

def create_float3_node(bifrost_node, name=""):
    """adds a float3 vector node
    :param bifrost_node:(str, ) bifrost compound node name
    :param bifrost_node: (str, )
    :return: (list, ) bifrost_node float3 node
    """
    float3_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Constants::Math,float3")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(float3_node, name))
        float3_node = name
    return float3_node

def create_subtract_node(bifrost_node, name=""):
    """adds a float3 vector node
    :param bifrost_node:(str, ) bifrost compound node name
    :param bifrost_node: (str, )
    :return: (list, ) bifrost_node float3 node
    """
    subtract_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,subtract")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(subtract_node, name))
        subtract_node = name
    return subtract_node

def create_add_node(bifrost_node, name=""):
    """adds an add node
    :param bifrost_node:(str, ) bifrost compound node name
    :param bifrost_node: (str, )
    :return: (list, ) bifrost_node float3 node
    """
    add_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,add")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(add_node, name))
        add_node = name
    return add_node

def create_multiply_node(bifrost_node, name=""):
    """adds a float3 vector node
    :param bifrost_node:(str, ) bifrost compound node name
    :param bifrost_node: (str, )
    :return: (list, ) bifrost_node float3 node
    """
    multiply_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,multiply")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(multiply_node, name))
        multiply_node = name
    return multiply_node

def create_normalize_node(bifrost_node, name=""):
    """adds a float3 vector node
    :param bifrost_node:(str, ) bifrost compound node name
    :param bifrost_node: (str, )
    :return: (list, ) bifrost_node float3 node
    """
    normalize_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,normalize")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(normalize_node, name))
        normalize_node = name
    return normalize_node

def create_float_node(bifrost_node, name=""):
    """adds a float3 vector node
    :param bifrost_node:(str, ) bifrost compound node name
    :param bifrost_node: (str, )
    :return: (list, ) bifrost_node float3 node
    """
    float_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Constants,float")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(float_node, name))
        float_node = name
    return float_node

def create_SRT_to_matrix_node(bifrost_node, name=""):
    """create ScaleRotateTranslate to Matrix node
    :param bifrost_node:(str, ) bifrost compound node name
    :param name: (str, ) the name to rename the node into
    :return: (str, ) matrix multiply node
    """
    srt_to_matrix_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,SRT_to_matrix")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(srt_to_matrix_node, name))
        srt_to_matrix_node = name
    return srt_to_matrix_node

def create_matrix_to_SRT_node(bifrost_node, name=""):
    """create ScaleRotateTranslate to Matrix node
    :param bifrost_node:(str, ) bifrost compound node name
    :param name: (str, ) the name to rename the node into
    :return: (str, ) matrix multiply node
    """
    matrix_to_srt_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,matrix_to_SRT")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(matrix_to_srt_node, name))
        matrix_to_srt_node = name
    return matrix_to_srt_node

def create_matrix_multiply_node(bifrost_node, name=""):
    """create matrix multiply node
    :param bifrost_node:(str, ) bifrost compound node name
    :param name: (str, ) the name to rename the node into
    :return: (str, ) matrix multiply node
    """
    matrix_multiply_node = cmds.vnnCompound(bifrost_node, "/", addNode="BifrostGraph,Core::Math,matrix_multiply")[0]
    if name:
        cmds.vnnCompound(bifrost_node, "/", renameNode=(matrix_multiply_node, name))
        matrix_multiply_node = name
    return matrix_multiply_node

def set_float3_port_value(bifrost_name, node_name, port_name, value=(0, 1, 0)):
    """set bifrost node's float3 value port
    """
    if isinstance(value[0], (int, float)):
        value = [str(x) for x in value]
    cmds.vnnNode(bifrost_name, "/{}".format(node_name), setPortDefaultValues=(port_name, "{%s}" % ','.join(value)))

def set_float_port_value(bifrost_name, node_name, port_name, value=1.0):
    """set bifrost node's float3 value port
    """
    cmds.vnnNode(bifrost_name, "/{}".format(node_name), setPortDefaultValues=(port_name, "{}".format(value)))
# ______________________________________________________________________________________________________________________
# ag_reflectionVectorBifrost.py