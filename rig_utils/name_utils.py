"""
name_utils module for dealing anything related with naming.
"""

# import standard modules
import re

# import maya modules
from maya import cmds

# import local modules
from maya_utils import object_utils


def search_replace_name(objects_array, search_str="", replace_str=""):
    """
    search and replace selected objects.
    :param objects_array: <tuple> objects to replace names from.
    :param search_str: <str> the string to find.
    :param replace_str: <str> the string to replace with.
    :return: <tuple> array of renamed objects.
    """
    renamed_objects = ()
    for obj_name in objects_array:
        if search_str not in obj_name:
            continue
        renamed_objects += obj_name.replace(search_str, replace_str),
    return renamed_objects


def search_replace_objects_hierarchy(selected_objects, search_str="", replace_str=""):
    """
    search and replace all objects within the hierarchy.
    :param selected_objects: <tuple> array of objects to replace strings from.
    :param search_str: <str> the search string to replace.
    :param replace_str: <str> replace it with this name.
    :return: <tuple> renamed items.
    """
    named_items = ()
    for obj_name in selected_objects:
        hierarchy_name_array = object_utils.get_transform_relatives(obj_name, find_child=True, as_strings=True)
        replaced_names = search_replace_name(hierarchy_name_array, search_str, replace_str)
        named_items += tuple(map(cmds.rename, zip(hierarchy_name_array, replaced_names)))
    return named_items


def search_replace_hierarchy_in_selection(search_str="", replace_str=""):
    """
    replace names from selected objects.
    :param search_str: <str> the search string to replace.
    :param replace_str: <str> replace it with this name.
    :return: <tuple> renamed items.
    """
    selected_objects = object_utils.get_selected_node(single=False)
    return search_replace_objects_hierarchy(selected_objects, search_str=search_str, replace_str=replace_str)