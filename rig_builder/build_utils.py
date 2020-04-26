"""
Added build utility module for managing the rig_builder ui functionality.
"""

# import standard modules
import sys
import posixpath
import os

py_version = None
if sys.version_info.major == 2:
    py_version = 2
    import imp
elif sys.version_info.major == 3:
    py_version = 3
    import importlib

# import local modules
from maya_utils import file_utils
import blueprint_utils

# define local variables
this_dir = file_utils.get_this_directory()
parent_dir = file_utils.get_this_directory_parent(2)
rig_modules_dir = posixpath.join(parent_dir, 'rig_modules')
rig_icons_dir = posixpath.join(parent_dir, 'rig_builder', 'icons')
blueprint_path = blueprint_utils.default_blueprint_path

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

    # try:
    if py_version == 2:
        fp, pathname, description = imp.find_module(module_file, [rig_modules_dir])
        rig_module_name = imp.load_module(module_file, fp, pathname, description)
    elif py_version == 3:
        module_data = importlib.util.find_spec(module_file)
        rig_module_name = module_data.loader.load_module()
    # except ImportError:
    #     print("[Module Not Loaded] :: {}".format(module_file))
    #     return False

    # instantiate the chosen serializer file class
    module_class_name = get_module_class_name(rig_module_name)
    return getattr(rig_module_name, module_class_name)


def get_available_modules():
    """
    grabs the currently available modules for us to use.
    :return: <list> available modules.
    """
    return [x for x in os.listdir(rig_modules_dir)
            if "template" not in x
            if "__init__" not in x
            if ".pyc" not in x]


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
        if not mod.endswith('.pyc'):
            continue
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
    # module_name_v0000.py --> module_name, _v0000.py --> _v0000
    return posixpath.splitext(module_name.split('_v')[-1])[0]


def extract_name(module_name):
    """
    extracts the module name.
    :param module_name:
    :return: <str> the module name without the version.
    """
    return module_name.split('_v')[0]


def add_extension(file_name, ext='py'):
    """
    adds an extension name to the file_name.
    :param file_name: <str> the file name to check for extension.
    :param ext: <str> add this extension to the file name.
    :return: <str> file name with valid extension.
    """
    if not file_name.endswith(ext):
        return file_name + '.{}'.format(ext)
    return file_name


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
    finds this module in the rig_modules directory and returns the name and version associated with the file.
    :param module_name: <str> the name of the module to find.
    :return: <dict> module data.
    """
    module_data = {}
    modules = find_files(module_name, by_name=True)
    for mod in modules:
        version = extract_version(mod)
        mod_name = extract_name(mod)
        module_instance = get_rig_module(mod_name, version)
        module_data = __update_module_data(module_name, {version: module_instance}, data_dict=module_data)
    return module_data


def set_creatures_path(path):
    """
    set the creature building path.
    :return:
    """
    os.environ('BLUEPRINTS_PATH', path)


def get_file_creature_data():
    """
    gets the blueprint saves into this Maya File.
    :return:
    """
    file_data = file_utils.get_internal_var_file_variable("creatureData")
    if file_data:
        return file_data[0]


def save_blueprint(creature_name, data):
    """
    saves blueprint files
    :return:
    """
    return blueprint_utils.write_blueprint(creature_name, data)


def get_blueprints():
    """
    returns a list of avaliable blueprint JSON files.
    :return:
    """
    return blueprint_utils.get_blueprints()
