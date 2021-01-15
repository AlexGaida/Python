"""
    Module for managing control color utilities
"""
# import standard modules
import ast, posixpath

# import maya modules
from maya import cmds

# import local modules
import file_utils


# local variables
python_dir = file_utils.get_this_directory_parent(3)
color_level_file = posixpath.join(python_dir, 'RigModules', 'color_plan.json')


def get_color_plans():
    """
    retrieve the color plans for the nurbs controller
    :return: <dict> color plans
    """
    color_plans = file_utils.read_json_file(color_level_file)
    # we need to reinterpret the json file
    interpreted_color_plans = {}
    for level in color_plans:
        interpreted_color_plans[level] = {}
        for color_name in color_plans[level]:
            color_value = color_plans[level][color_name]
            color_value = ast.literal_eval(color_value)
            interpreted_color_plans[level][color_name] = color_value
    return interpreted_color_plans


color_plans = get_color_plans()


def set_color_by_name(object_name, color_name, color_level=None):
    """
    set the color by the name
    :param object_name: <str> the object node to set the color to
    :param color_name: <str> the color name to use to set the control color
    :param color_level: <int> the color level to set on the current color name
    """
    if not color_level:
        color_level = 0
    color_level_name = "level_{}".format(color_level)
    color_data = color_plans[color_level_name]
    color_value = color_data[color_name]
    set_rgb_color_by_color_value(object_name, color_value)


def set_rgb_color_by_color_value(object_name, color_value):
    """
    sets the nurbs curve rgb colors
    :param object_name:  <str> the control node name to change the rgb colors
    :param color_value: <tuple> set the colors
    """
    cmds.setAttr(object_name + ".overrideEnabled", 1)
    cmds.setAttr(object_name + ".overrideRGBColors", 1)
    for color_channel, color_value in zip("RGB", color_value):
        cmds.setAttr(object_name + '.overrideColor{}'.format(color_channel), color_value)


def get_rgb_color_value(controller_node):
    """
    returns the rgb color
    :param controller_node:
    :return: <tuple> rgb color
    """
    r = cmds.getAttr(controller_node + ".overrideColorR")
    g = cmds.getAttr(controller_node + ".overrideColorG")
    b = cmds.getAttr(controller_node + ".overrideColorB")
    return r, g, b,


# ______________________________________________________________________________________________________________________
# nurbs_color_utils.py
