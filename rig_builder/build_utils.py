"""
Added build utility module for managing the rig_builder ui functionality.
"""

# import standard modules
import sys
import posixpath
import os
import imp

# import local modules
from maya_utils import file_utils

# define local variables
this_dir = file_utils.get_this_directory()
parent_dir = file_utils.get_this_directory_parent()
rig_modules_dir = posixpath.join(parent_dir, 'rig_modules')
rig_icons_dir = posixpath.join(this_dir, 'icons')

red_icon = posixpath.join(rig_icons_dir, 'red.PNG')
yellow_icon = posixpath.join(rig_icons_dir, 'yellow.PNG')
green_icon = posixpath.join(rig_icons_dir, 'green.PNG')
empty_icon = posixpath.join(rig_icons_dir, 'empty.PNG')


def get_rig_modules_list():
    return os.listdir(rig_modules_dir)


def module_file_name(module_name, module_version):
    return module_name + '_v' + module_version


def get_module_class_name(module_name):
    return module_name.class_name


def get_rig_module(module_name, module_version):
    """
    find and return the rig module file.
    :param module_name:
    :param module_version:
    :return:
    """
    module_file = module_file_name(module_name, module_version)
    print("[Loading Module] :: {}".format(module_file))

    try:
        fp, pathname, description = imp.find_module(module_file, [rig_modules_dir])
        rig_module_name = imp.load_module(module_file, fp, pathname, description)
    except ImportError:
        print("[Module Not Loaded] :: {}".format(module_file))
        return False

    # get the class name
    module_class_name = get_module_class_name(rig_module_name)

    # instantiate the chosen serializer file class
    return eval("{}.{}".format(rig_module_name, module_class_name))


def get_available_modules():
    """
    grabs the currently available modules for us to use.
    :return: <list> available modules.
    """
    return [x for x in os.listdir(rig_modules_dir) if "template" not in x]


def find_files(module_name, by_name=True):
    """
    find the modules by the parameter instruction.
    :param module_name:
    :param by_name: do a search in the rig modules directory using name comparison.
    :return:
    """
    modules = os.listdir(rig_modules_dir)
    found = ()
    for mod in modules:
        if by_name:
            if mod.startswith(module_name):
                found += mod,
    return found


def extract_version(module_name):
    """
    extract the version number from the module name provided.
    :param module_name: <str> the module to find version in.
    :return: <int> version number.
    """
    return module_name.split('_v')[-1]


def __update_module_data(key_name, value_name, data_dict={}):
    """
    update the module data_dict variable.
    :param key_name: <str>
    :param value_name: <valueType>
    :param data_dict: <dict>
    :return: <dict> updated dictionary.
    """
    if key_name not in data_dict:
        if not isinstance(value_name, dict):
            data_dict[key_name] = None
        elif isinstance(value_name, dict):
            data_dict[key_name] = {}

    if not isinstance(value_name, dict):
        data_dict[key_name] = value_name
    elif isinstance(value_name, dict):
        data_dict[key_name].update(value_name)
    return data_dict


def find_module_data(module_name):
    """
    finds this module in the rig_modules directory and returns the name and version associated.,
    :param module_name: <str> the name of the module to find.
    :return: <dict> module data.
    """
    module_data = {}
    modules = find_files(module_name, by_name=True)
    for mod in modules:
        version = extract_version(mod)
        module_instance = get_rig_module(mod, version)
        module_data = __update_module_data(module_name, {version: module_instance}, data_dict=module_data)
    return None
