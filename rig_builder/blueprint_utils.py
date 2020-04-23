"""
blue print information module for writing and updating blueprint files.
"""
from maya_utils import file_utils

# define variables
BLUEPRINT = {}
default_blueprint_path = "D:/Work/Maya/blueprints"


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


def write_blueprint(creature_name, data):
    blueprint_file_name = get_blueprint_path(creature_name)
    json_file = file_utils.JSONSerializer(file_name=blueprint_file_name, data=data)
    json_file.write()

