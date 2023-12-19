"""

    Utility script for managing the items in the maya Outliner

"""
# import standard modules
import ast, posixpath

# import local modules
from . import file_utils

# import maya modules
from maya import cmds

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


def set_outliner_color_value(object_name, value):
    """
    sets the objects outliner color by value
    :param object_name: <str> the object name to change the outliner color to
    :param value: <tuple> the value to change the outliner color with
    """
    outliner_color_attr = object_name + '.outlinerColor'
    if not cmds.getAttr(outliner_color_attr):
        cmds.setAttr(outliner_color_attr, True)
    cmds.setAttr(object_name + '.outlinerColor', *value, type='double3')


def turn_off_outliner_color(object_name):
    """
    sets the objects outliner color by boolean
    :param object_name:
    :return:
    """
    outliner_color_attr = object_name + '.outlinerColor'
    cmds.setAttr(outliner_color_attr, False)


def set_outliner_color_by_name(object_name, color_name, color_level=0):
    """
    sets the objects outliner color by name
    :param object_name: <str> node object name
    :param color_name: <str> color name
    :param color_level: <int> color integer level
    :return:
    """
    if not color_level:
        color_level = 0
    color_level_name = "level_{}".format(color_level)
    color_value = color_plans[color_level_name][color_name]
    set_outliner_color_value(object_name, color_value)

# ______________________________________________________________________________________________________________________
# outliner_utils.py
