"""
blue print information module for writing and updating blueprint files.
"""

# import local modules
from maya_utils import file_utils

# define variables
BLUEPRINT = {}
default_blueprint_path = "D:/Work/Maya/blueprints"


def get_blueprints(dir_name=""):
    """
    initializes a glob search for all .JSON blueprint files.
    :return: <list> array of found files.
    """
    # if dir_name:
    #     return file_utils.get_files(dir_name)
    # return file_utils.get_files(default_blueprint_path)
    if dir_name:
        return file_utils.get_directories(dir_name, full_path=False)
    return file_utils.get_directories(default_blueprint_path, full_path=False)


def get_blueprint_file_name(creature_name):
    """
    grabs the blue print name from the creature name provided.
    :return:
    """
    return creature_name + '_blueprint'


def build_dir(creature_name):
    """
    builds the directory of the creature name provided.
    :param creature_name:
    :return:
    """
    dir_name = file_utils.concatenate_path(default_blueprint_path, creature_name)
    file_utils.build_dir(dir_name)
    return dir_name


def get_blueprint_path(creature_name):
    """
    gets the blueprint path from the folder selected and the blueprint name.
    :param creature_name:
    :return:
    """
    blueprint_dir = build_dir(creature_name)
    blueprint_name = get_blueprint_file_name(creature_name)
    return file_utils.concatenate_path(blueprint_dir, blueprint_name)


def update_blueprint(key_name, value):
    """
    updates the blueprint information.
    :param key_name: <str>
    :param value: <str>
    :return: <dict> dictionary information.
    """
    global BLUEPRINT
    BLUEPRINT.update({key_name: value})


def read_blueprint(creature_name):
    """
    reads the .JSON creature file.
    :param creature_name: <str> creature file name.
    :return: <dict> creature blueprint data.
    """
    blueprint_file_name = get_blueprint_path(creature_name)
    json_file = file_utils.JSONSerializer(file_name=blueprint_file_name)
    return json_file.read()


def write_blueprint(creature_name, data):
    """
    writes the creature blueprint at default file path
    :param creature_name: <str> creature file name.
    :param data: <dict> creature data.
    :return: <bool> True for success.
    """
    blueprint_file_name = get_blueprint_path(creature_name)
    print(blueprint_file_name, "Saved")
    json_file = file_utils.JSONSerializer(file_name=blueprint_file_name, data=data)
    json_file.write()
    return True


def get_file_blueprint():
    """
    gets the blueprint saved into this Maya File.
    :return:
    """
    return file_utils.get_internal_var_file_variable("creatureData")
