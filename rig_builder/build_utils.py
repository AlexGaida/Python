"""
Added build utility module for managing the rig_builder ui functionality.
"""
# import standard modules
import sys, posixpath, os

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
parent_dir = file_utils.get_this_directory_parent(3)
rig_modules_dir = posixpath.join(parent_dir, 'RigModules')
rig_icons_dir = posixpath.join(parent_dir, 'Python', 'rig_builder', 'icons')
blueprint_path = blueprint_utils.default_blueprint_path

red_icon = posixpath.join(rig_icons_dir, 'red.PNG')
yellow_icon = posixpath.join(rig_icons_dir, 'yellow.PNG')
green_icon = posixpath.join(rig_icons_dir, 'green.PNG')
empty_icon = posixpath.join(rig_icons_dir, 'empty.PNG')


def get_rig_modules_list():
    return os.listdir(rig_modules_dir)


def module_file_name(module_name, module_version):
    """

    :param module_name:
    :param module_version:
    :return:
    """
    return module_name + '_v' + module_version


def get_module_class_name(module_name):
    """
    returns the name of the module's class object
    :param module_name: <str> module name
    :return: <str> module class name
    """
    module_class_name = module_name.class_name
    return module_class_name


def get_rig_module(module_name, module_version):
    """
    find and return the rig module file
    :param module_name: <str> name
    :param module_version: <str> version
    :return: <str> rig_module_file
    """
    module_file = module_file_name(module_name, module_version)
    if py_version == 2:
        fp, pathname, description = imp.find_module(module_file, [rig_modules_dir])
        rig_module_name = imp.load_module(module_file, fp, pathname, description)
    elif py_version == 3:
        module_data = importlib.util.find_spec(module_file)
        rig_module_name = module_data.loader.load_module()
    module_class_name = get_module_class_name(rig_module_name)
    rig_module_file = getattr(rig_module_name, module_class_name)
    return rig_module_file


def get_available_modules():
    """
    grabs the currently available modules for us to use
    :return: <list> available modules
    """
    available_modules = [x for x in os.listdir(rig_modules_dir)
                         if "template" not in x
                         if "__init__" not in x
                         if ".pyc" not in x]
    return available_modules


def get_proper_modules():
    """
    returns proper module name
    :return: module data
    """
    mod_data = ()
    prebuild_name = ""
    available_modules = get_available_modules()
    print('-->', available_modules)
    for mod in available_modules:
        if not mod:
            continue
        if "PreBuild" in mod:
            prebuild_name = mod.split('_v')[0]
            continue
        if "_v" in mod:
            prebuild_name += mod.split('_v')[0]
        if prebuild_name:
            mod_data += prebuild_name,
    return mod_data


def find_files(module_name, by_name):
    """
    find the modules by the parameter instruction.
    :param module_name: <str> find the file
    :param by_name: <str> do a search in the rig modules directory using name comparison.
    :return: <list> files found by name
    """
    modules = os.listdir(rig_modules_dir)
    found_files = ()
    for mod in modules:
        if not mod.endswith('.py'):
            continue
        if mod.startswith(module_name):
            found_files += mod,
    return found_files


def extract_version(module_name):
    """
    extract the version number from the module name provided.
    :param module_name: <str> the module to find version in.
    :return: <int> version number.
    """
    version_name = posixpath.splitext(module_name.split('_v')[-1])[0]
    return version_name


def extract_name(module_name):
    """
    extracts the module name.
    :param module_name:
    :return: <str> the module name without the version.
    """
    module_name = module_name.split('_v')[0]
    return module_name


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


def __update_module_data(key_name, value_name, data_dict):
    """
    update the module data_dict variable. Inserts the key name to the dictionary if there isn't one.
    :param key_name: <str> the key name to change,
    :param value_name: <valueType> value to change
    :param data_dict: <dict> data dictionary to update the module data with
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
    finds this module in the RigModules directory and returns the name and version associated with the file.
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


def reload_modules():
    """
    calling imp.load_module again actually reloads the module.
    :return: <bool> True for success.
    """
    proper_modules = get_proper_modules()
    for module_name in proper_modules:
        modules = find_files(module_name, by_name=True)
        for mod in modules:
            version = extract_version(mod)
            mod_name = extract_name(mod)
            get_rig_module(mod_name, version)
    return True


def set_creatures_path(path):
    """
    set the creature building path.
    """
    os.environ['BLUEPRINTS_PATH'] = path


def get_file_creature_data():
    """
    gets the blueprint saves into this Maya File.
    :return: <dict> creature data.
    """
    creature_data = file_utils.get_internal_var_file_variable("creatureData")
    return creature_data


def save_blueprint(creature_name, data):
    """
    saves blueprint files
    :return:
    """
    return blueprint_utils.write_blueprint(creature_name, data)


def get_blueprints():
    """
    returns a list of available blueprint JSON data files.
    :return: <tuple> array of blueprints.
    """
    return blueprint_utils.get_blueprints()

# ______________________________________________________________________________________________________________________
# build_utils.py
