"""
name_utils module for dealing anything related with naming.
"""
# import standard modules
import re

# import maya modules
from maya import cmds

# import local modules
from maya_utils import object_utils

# define local variables
re_brackets = re.compile(r"\[?\]?")
# re_brackets = re.compile("[|]")


def search_replace_brackets_name(name):
    """
    replaces the brackets with an empty string.
    :param name:
    :return: <str> string without brackets.
    """
    return re_brackets.sub('', name)


def search_replace_names(objects_array, search_str="", replace_str=""):
    """
    search and replace selected objects.
    :param objects_array: <tuple> objects to replace names from.
    :param search_str: <str> the string to find.
    :param replace_str: <str> the string to replace with.
    :return: <tuple> array of renamed objects.
    """
    renamed_objects = ()
    for idx, obj_name in enumerate(objects_array):
        if search_str and search_str not in obj_name:
            continue
        elif search_str and search_str in obj_name:
            renamed_objects += obj_name.replace(search_str, replace_str),
        else:
            renamed_objects += '{}_{}'.format(replace_str, idx),
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
        replaced_names = search_replace_names(hierarchy_name_array, search_str, replace_str)
        named_items += tuple(map(cmds.rename, zip(hierarchy_name_array, replaced_names)))
    return named_items


def search_replace_hierarchy_in_selection(search_str="", replace_str=""):
    """
    replace names from selected objects. replaces names in hierarchy
    :param search_str: <str> the search string to replace.
    :param replace_str: <str> replace it with this name.
    :return: <tuple> renamed items.
    """
    selected_objects = object_utils.get_selected_node(single=False)
    return search_replace_objects_hierarchy(selected_objects, search_str=search_str, replace_str=replace_str)


def search_replace_in_selection(search_str="", replace_str=""):
    """
    replace names from selected objects.
    :param search_str: <str> the search string to replace.
    :param replace_str: <str> replace it with this name.
    :return: <tuple> renamed items.
    """
    selected_objects = object_utils.get_selected_node(single=False)
    names = search_replace_names(selected_objects, search_str, replace_str)
    for sel_obj, name in zip(selected_objects, names):
        cmds.rename(sel_obj, name)
    return names


def rename_objects(name="", suffix_name=""):
    """
    replace the names with enumeration.
    :return: <bool> True for success.
    """
    selected_objects = object_utils.get_selected_node(single=False)
    new_names = ()
    for idx, obj_name in enumerate(selected_objects):
        # hierarchy_name_array = object_utils.get_transform_relatives(obj_name, find_child=True, as_strings=True)
        new_name = '{}_{}_{}'.format(name, idx, suffix_name)
        new_names += new_name,
        cmds.rename(obj_name, new_name)
    return new_names

