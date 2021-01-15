"""
blue print information module for writing and updating blueprint files.
"""
# import standard modules
import os

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
    if dir_name:
        blueprints = file_utils.get_directories(dir_name)
        return blueprints
    blueprints = file_utils.get_directories(default_blueprint_path)
    return blueprints


def get_blueprint_file_name(creature_name):
    """
    grabs the blue print name from the creature name provided.
    :return:
    """
    blueprint_file_name = creature_name + '_blueprint'
    return blueprint_file_name


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
    blueprint_path = file_utils.concatenate_path(blueprint_dir, blueprint_name)
    return blueprint_path


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
    blueprint_data = json_file.read()
    return blueprint_data


def delete_blueprint_dir(file_name):
    """
    deletes blueprint directory from the file name path.
    :param file_name: <str> file_name.
    """
    file_dir = file_utils.directory_name(file_name)
    file_utils.remove_directory(file_dir)


def delete_blueprint(creature_name):
    """
    removes this file and directory from disk.
    """
    blueprint_file_name = get_blueprint_path(creature_name)
    json_file = file_utils.JSONSerializer(file_name=blueprint_file_name)
    json_file.delete()
    delete_blueprint_dir(json_file.FILE_NAME)


def open_blueprint_dir(creature_name):
    """
    opens the blueprint directory
    :param creature_name: <str> creature name for append path.
    """
    blueprint_dir = build_dir(creature_name)
    print("[Opening Creature Dir] :: {}".format(blueprint_dir))
    os.startfile(blueprint_dir)


def open_blueprint_file(creature_name):
    """
    opens the blueprint directory
    :param creature_name: <str> creature name for append path.
    """
    blueprint_file_name = get_blueprint_path(creature_name)
    json_file = file_utils.JSONSerializer(file_name=blueprint_file_name)
    print("[Opening Creature File] :: {}".format(json_file))
    os.startfile(json_file.file_name)


def write_blueprint(creature_name, data):
    """
    writes the creature blueprint at default file path
    :param creature_name: <str> creature file name.
    :param data: <dict> creature data.
    :return: <bool> True for success.
    """
    blueprint_file_name = get_blueprint_path(creature_name)
    json_file = file_utils.JSONSerializer(file_name=blueprint_file_name, data=data)
    json_file.write()
    return True


def get_file_blueprint():
    """
    gets the blueprint saved into this Maya File.
    :return: <dict> file blueprint
    """
    file_blueprint = file_utils.get_internal_var_file_variable("creatureData")
    return file_blueprint

# ______________________________________________________________________________________________________________________
# blueprint_utils.py
