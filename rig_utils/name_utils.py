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
re_numbers = re.compile("\d+")

JNT_SUFFIX_NAME = 'jnt'
GUIDE_JNT_SUFFIX_NAME = '__guide_jnt'
BND_JNT_SUFFIX_NAME = 'bnd_{}'.format(JNT_SUFFIX_NAME)


def get_name_count(name, suffix_name=""):
    """
    queries and returns the name in scene.
    :param name: <str> check this name.
    :param suffix_name: <str> suffix name.
    :return: <int> names found.
    """
    transforms = cmds.ls(type='transform')
    collector = ()
    for t_obj in transforms:
        if t_obj.startswith(name) and t_obj.endswith(suffix_name):
            collector += t_obj,
    return len(collector)


def get_start_name(name, prefix_name=""):
    """
    gets the start name.
    :return: <str> start name.
    """
    return '{prefix}{name}'.format(prefix=prefix_name, name=name)


def get_start_name_with_num(name, prefix_name="", suffix_name=""):
    """
    grabs the start name with the number attached.
    :param name: <str> use this name.
    :param prefix_name: <str> use this prefix name.
    :param suffix_name: <str> use this suffix name.
    :return: <str> return the start name.
    """
    start_name = get_start_name(name, prefix_name=prefix_name)
    # check if there is a number already in the name provided.
    if not re_numbers.findall(start_name):
        i = get_name_count(start_name, suffix_name=suffix_name)
        return '{start_name}_{idx}'.format(start_name=start_name, idx=i)
    else:
        return start_name


def get_guide_name(prefix_name="", name="", suffix_name=""):
    """
    get the guide joint name. Checks to see if the name already exists, if so, append the number.
    :param prefix_name: <str> prefix name.
    :param name: <str> actual name.
    :param suffix_name: <str> name after the name.
    :return: <str> guide joint name.
    """
    start_name = get_start_name(name, prefix_name=prefix_name)
    if not re_numbers.findall(start_name):
        i = get_name_count(start_name, suffix_name=suffix_name)
        return '{start_name}_{idx}__{suffix}'.format(start_name=start_name, idx=i, suffix=suffix_name)
    else:
        return '{start_name}__{suffix}'.format(start_name=start_name, suffix=suffix_name)


def get_bound_name_array(prefix_name="", name="", length=1):
    """
    return an array of bound joint names.
    :param prefix_name: <str> prefix name.
    :param name: <str> the base name.
    :param length: <int> length of created names.
    :return: <tuple> joint names array.
    """
    bound_names = ()
    start_name = get_start_name(name, prefix_name=prefix_name)
    for index in xrange(length):
        bound_names += '{name}_{idx}_{suffix}'.format(name=start_name, idx=index, suffix=BND_JNT_SUFFIX_NAME),
    return bound_names


def get_name_array(prefix_name="", name="", length=1):
    """
    gets the names array.
    :param prefix_name:
    :param name:
    :param length:
    :return:
    """
    names = ()
    start_name = get_start_name(name, prefix_name=prefix_name)
    for index in xrange(length):
        names += '{name}_{idx}'.format(name=start_name, idx=index),
    return names


def get_guide_name_array(prefix_name="", name="", length=1):
    """
    gets the guide name array.
    :param prefix_name: <str> prefix name.
    :param name: <str> the main name to use.
    :param length: <int> use this length to get the counting names.
    :return: <tuple> guide joint names.
    """
    guide_names = ()
    start_name = get_start_name(name, prefix_name=prefix_name)
    for index in xrange(length):
        guide_names += '{name}_{idx}__{suffix}'.format(name=start_name, idx=index, suffix=GUIDE_JNT_SUFFIX_NAME),
    return guide_names


def get_joint_name_array(name, length=1, bind_name=False):
    """
    return an array of joint array names.
    :param name: <str> the name to use when creating the array of names.
    :param length: <int> the length to go for.
    :param bind_name: <bool> if set True, creates joints with bind joint name.
    :return: <tuple> array of names.
    """
    names = ()
    for idx in xrange(length):
        if bind_name:
            names += '{}_{}_{}'.format(name, idx, BND_JNT_SUFFIX_NAME),
        else:
            names += '{}_{}_{}'.format(name, idx, JNT_SUFFIX_NAME),
    return names


def replace_guide_name_with_bnd_name(guide_jnt_name):
    """
    replaces the guide joint name with the bound name.
    :param guide_jnt_name: <str> joint name.
    """
    if "__" in guide_jnt_name:
        return guide_jnt_name.rpartition("__")[0] + '_bnd_jnt'
    return True


def get_bound_joint_name(prefix_name="", name="", suffix_name="bnd"):
    """
    returns the name of the bound joint.
    :param prefix_name: <str> prefix name.
    :param name: <str> actual name.
    :param suffix_name: <str> name after the name.
    :return: <str> bound joint name.
    """
    start_name = get_start_name(name, prefix_name=prefix_name)
    if not re_numbers.findall(start_name):
        i = get_name_count(start_name, suffix_name=suffix_name)
        return '{start_name}_{idx}_bnd_jnt'.format(start_name=start_name, idx=i)
    else:
        return '{start_name}_bnd_jnt'.format(start_name=start_name)


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

