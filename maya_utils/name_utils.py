"""
    name_utils module for dealing anything related with naming
"""
# import standard modules
import re, json, posixpath

# import maya modules
from maya import cmds

# import local modules
from maya_utils import file_utils, object_utils

# define local variables
re_first_underscore = re.compile("^_")
re_brackets = re.compile(r"\[?\]?")
re_capitals = re.compile('[A-Z][^A-Z]*')
re_lowers = re.compile('[a-z]*')
re_numbers = re.compile("\d+")
naming_convention_file = posixpath.join(
    file_utils.get_this_directory_parent(3),
    'RigModules', 'naming_convention.json')


def get_naming_conventions():
    """
    get the names data dictionary
    :return: <dict> names json dictionary data
    """
    with open(naming_convention_file, 'r') as f:
        names_data = json.load(f)
    return names_data

naming_conventions = get_naming_conventions()


def incorporate_standard_naming_conventions():
    """
    grab the naming convention and make part of the locals() of this module
    """
    globs = globals()
    for k, v in naming_conventions["standard"].items():
        globs[k] = v

incorporate_standard_naming_conventions()


def get_naming_plan(convention=None):
    """
    get the naming plan
    :return: <str> naming plan
    """
    if not convention:
        convention = 'standard'
    conventions = naming_conventions[convention]
    naming_plan = conventions['naming_plan']
    return naming_plan


def get_classification_name(name_type, convention='standard'):
    """
    returns the name of the type and classification
    :param name_type: <str> the type of name to retrieve
    :param convention: <str> convention classification standard
    :return: <str> classification name
    """
    names_group = naming_conventions[convention]
    if name_type in names_group:
        name_type = names_group[name_type]
    return name_type


def get_name(name, index=None, letter="", side_name="", suffix_name="",
             prefix_name="", direction_name="", naming_convention=None):
    """
    generic name structure concatenation
    :param name: <str> the base name to use
    :param suffix_name: <str> the suffix name to append to the base name
    :param prefix_name: <str> the prefix name to append to the main name
    :param direction_name: <str> directional name to append to the main name
    :param index: <int> the index to use for the name
    :param side_name: <str> the side name to use
    :param letter: <str> the letter to append to the name
    :param naming_convention: <str> Default: None, use a different naming convention
    :return: <str> return the modified name
    """
    if not naming_convention:
        naming_convention = 'standard'
    naming_plan = get_naming_plan(convention=naming_convention)
    naming_plan = naming_plan.replace("{base_name}", name)
    if index is not None:
        naming_plan = naming_plan.replace("{index}", str(index))
    else:
        naming_plan = naming_plan.replace("{index}", "")
    if letter:
        letter = letter.upper()
        naming_plan = naming_plan.replace("{letter}", letter)
    else:
        naming_plan = naming_plan.replace("{letter}", "")
    if side_name:
        side_name = get_classification_name(side_name, convention=naming_convention)
        naming_plan = naming_plan.replace("{side_name}", side_name)
    else:
        naming_plan = naming_plan.replace("{side_name}", "")
    if suffix_name:
        suffix_name = get_classification_name(suffix_name, convention=naming_convention)
        naming_plan = naming_plan.replace("{suffix_name}", suffix_name)
    else:
        naming_plan = naming_plan.replace("{suffix_name}", "")
    if prefix_name:
        naming_plan = naming_plan.replace("{prefix_name}", prefix_name)
    else:
        naming_plan = naming_plan.replace("{prefix_name}", "")
    if direction_name:
        naming_plan = naming_plan.replace("{direction_name}", direction_name)
    else:
        naming_plan = naming_plan.replace("{direction_name}", "")
    naming_plan = naming_plan.replace("___", "_")
    naming_plan = naming_plan.replace("__", "_")
    naming_plan = re.sub(r'^_', '', naming_plan)
    return naming_plan


def deconstruct_name(name_string, naming_convention=None):
    """
    deconstruct the name.
    :param name_string: <str> name string deconstruction
    :return: <str>
    """
    naming_plan = get_naming_plan(convention=naming_convention)
    return True


def get_letter_string(name_str):
    """
    Get letter string from the name argument provided.
    :return: <str> letter string.
    """
    split_names = name_str.split('_')
    for split_name in split_names:
        if len(split_name) == 1:
            return split_name
    return ''


def get_side_string(name_str):
    """
    Get side string
    :param name_str:
    :return: <str> the the side name string.
    """
    left_name = get_classification_name('left')
    right_name = get_classification_name('right')
    center_name = get_classification_name('center')
    split_names = name_str.split('_')
    for split_name in split_names:
        if split_name.startswith(left_name + '_'):
            return split_name
        elif split_name.startswith(right_name + '_'):
            return split_name
        elif split_name.startswith(center_name + '_'):
            return split_name
    return True


def get_base_name_string(name_str, side_string=None):
    """
    Gets the base name
    :param name_str:
    :return: <str> the base name string.
    """
    if not side_string:
        side_string = get_side_string(name_str)
    if side_string:
        side_string = get_classification_name(side_string)
    name_tokens = name_str.split('_')
    side_idx = name_tokens.index(side_string)
    base_name = name_tokens[side_idx + 1]
    return base_name


def get_node_type(object_name):
    """
    returns the suffix_name from the node type provided
    :param object_name: <str> the object name to get the node type from
    :return: <str> suffix_name
    """
    object_type_name = cmds.nodeType(object_name)
    return object_type_name


def split_name_from_object_type_name(object_type_name):
    """
    get titled names from the object name
    :param object_type_name:
    :return: <str> type key str
    """
    titled_names = re_capitals.findall(object_type_name)[0]
    titled_names = titled_names.lower()
    lower_names = re_lowers.findall(object_type_name)[0]
    type_key_str = lower_names + '_' + titled_names
    return type_key_str


def get_name_count(name, suffix_name=""):
    """
    queries and returns the name in scene
    :param name: <str> check this name
    :param suffix_name: <str> suffix name
    :return: <int> names found
    """
    transforms = cmds.ls(type='transform')
    collector = ()
    for t_obj in transforms:
        if name in t_obj and t_obj.endswith(suffix_name):
            collector += t_obj,
    return len(collector)


def get_prefix_name(name, prefix_name=""):
    """
    gets the start name
    :return: <str> start name
    """
    prefix_name = '{prefix}{name}'.format(prefix=prefix_name, name=name)
    return prefix_name


def get_start_name_with_num(name, prefix_name="", suffix_name=""):
    """
    grabs the start name with the number attached
    :param name: <str> use this name
    :param prefix_name: <str> use this prefix name
    :param suffix_name: <str> use this suffix name
    :return: <str> return the start name
    """
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    if not re_numbers.findall(start_name):
        i = get_name_count(start_name, suffix_name=suffix_name)
        return '{start_name}_{idx}'.format(start_name=start_name, idx=i)
    else:
        return start_name


def get_guide_name(prefix_name="", name="", suffix_name=""):
    """
    get the guide joint name. Checks to see if the name already exists, if so, append the number
    :param prefix_name: <str> prefix name
    :param name: <str> actual name
    :param suffix_name: <str> name after the name
    :return: <str> guide joint name
    """
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    if not re_numbers.findall(start_name):
        i = get_name_count(start_name, suffix_name=suffix_name)
        return '{start_name}_{idx}__{suffix}'.format(start_name=start_name, idx=i, suffix=suffix_name)
    else:
        return '{start_name}__{suffix}'.format(start_name=start_name, suffix=suffix_name)


def get_bound_name_array(prefix_name="", name="", length=1):
    """
    return an array of bound joint names
    :param prefix_name: <str> prefix name
    :param name: <str> the base name
    :param length: <int> length of created names
    :return: <tuple> joint names array
    """
    bound_names = ()
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    bind_jnt_suffix_name = get_classification_name('bound_joint')
    for index in range(length):
        bound_names += '{name}_{idx}_{suffix}'.format(name=start_name, idx=index, suffix=bind_jnt_suffix_name),
    return bound_names


def get_suffix_name_array(prefix_name="", name="", suffix_name="", length=1):
    """
    return an array of bound joint names
    :param prefix_name: <str> prefix name
    :param name: <str> the base name
    :param length: <int> length of created names
    :param suffix_name: <str> suffix name string
    :return: <tuple> joint names array
    """
    bound_names = ()
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    joint_suffix_name = get_classification_name('joint')
    if joint_suffix_name not in suffix_name:
        suffix_name += '_{}'.format(joint_suffix_name)
    for index in range(length):
        bound_names += '{name}_{idx}_{suffix}'.format(name=start_name, idx=index, suffix=suffix_name),
    return bound_names


def get_name_array(prefix_name="", name="", length=1):
    """
    returns an array of names from the parameters given
    :param prefix_name: <str> prefix name before the main name
    :param name: <str> the base name
    :param length: <int> the array of length
    :return: <tuple> names array
    """
    names = ()
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    for index in range(length):
        names += '{name}_{idx}'.format(name=start_name, idx=index),
    return names


def get_guide_name_array(prefix_name="", name="", length=1):
    """
    gets the guide name array
    :param prefix_name: <str> prefix name
    :param name: <str> the main name to use
    :param length: <int> use this length to get the counting names
    :return: <tuple> guide joint names
    """
    guide_names = ()
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    guide_joint_suffix_name = get_classification_name('guide_joint')
    for index in range(length):
        guide_names += '{name}_{idx}__{suffix}'.format(name=start_name, idx=index, suffix=guide_joint_suffix_name),
    return guide_names


def get_joint_name_array(name, length=1, bind_name=False):
    """
    return an array of joint array names
    :param name: <str> the name to use when creating the array of names
    :param length: <int> the length to go for
    :param bind_name: <bool> if set True, creates joints with bind joint name
    :return: <tuple> array of names
    """
    names = ()
    for idx in range(length):
        bind_joint_suffix_name = get_classification_name('guide_joint')
        joint_suffix_name = get_classification_name('joint')
        if bind_name:
            names += '{}_{}_{}'.format(name, idx, bind_joint_suffix_name),
        else:
            names += '{}_{}_{}'.format(name, idx, joint_suffix_name),
    return names


def replace_guide_name_with_bnd_name(guide_jnt_name):
    """
    replaces the guide joint name with the bound name
    :param guide_jnt_name: <str> joint name
    """
    if "__" in guide_jnt_name:
        return guide_jnt_name.rpartition("__")[0] + '_bnd_jnt'
    return True


def get_bound_joint_name(prefix_name="", name="", suffix_name="bnd"):
    """
    returns the name of the bound joint
    :param prefix_name: <str> prefix name
    :param name: <str> actual name
    :param suffix_name: <str> name after the name
    :return: <str> bound joint name
    """
    start_name = get_prefix_name(name, prefix_name=prefix_name)
    if not re_numbers.findall(start_name):
        i = get_name_count(start_name, suffix_name=suffix_name)
        return '{start_name}_{idx}_bnd_jnt'.format(start_name=start_name, idx=i)
    else:
        return '{start_name}_bnd_jnt'.format(start_name=start_name)


def search_replace_brackets_name(name):
    """
    replaces the brackets with an empty string
    :param name:
    :return: <str> string without brackets
    """
    return re_brackets.sub('', name)


def search_replace_names(objects_array, search_str="", replace_str=""):
    """
    search and replace selected objects
    :param objects_array: <tuple> objects to replace names from
    :param search_str: <str> the string to find
    :param replace_str: <str> the string to replace with
    :return: <tuple> array of renamed objects
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
    search and replace all objects within the hierarchy
    :param selected_objects: <tuple> array of objects to replace strings from
    :param search_str: <str> the search string to replace
    :param replace_str: <str> replace it with this name
    :return: <tuple> renamed items
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
    :param search_str: <str> the search string to replace
    :param replace_str: <str> replace it with this name
    :return: <tuple> renamed items
    """
    selected_objects = object_utils.get_selected_node(single=False)
    return search_replace_objects_hierarchy(selected_objects, search_str=search_str, replace_str=replace_str)


def search_replace_in_selection(search_str="", replace_str=""):
    """
    replace names from selected objects
    :param search_str: <str> the search string to replace
    :param replace_str: <str> replace it with this name
    :return: <tuple> renamed items
    """
    selected_objects = object_utils.get_selected_node(single=False)
    names = search_replace_names(selected_objects, search_str, replace_str)
    for sel_obj, name in zip(selected_objects, names):
        cmds.rename(sel_obj, name)
    return names


def rename_objects(name="", suffix_name=""):
    """
    replace the names with enumeration
    :return: <bool> True for success
    """
    selected_objects = object_utils.get_selected_node(single=False)
    new_names = ()
    for idx, obj_name in enumerate(selected_objects):
        new_name = '{}_{}_{}'.format(name, idx, suffix_name)
        new_names += new_name,
        cmds.rename(obj_name, new_name)
    return new_names

# ______________________________________________________________________________________________________________________
# name_utils.py
