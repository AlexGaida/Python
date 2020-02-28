"""
This is the cleanup module for clearing the Maya scene with stuff we don't want.
"""
# import maya modules
from maya import cmds
from maya import mel

# import local modules
from maya_utils import object_utils

# define global variables
FUNCTIONS = ['normalize_skin_weights',
             'zero_controls']


def normalize_skin_weights():
    for skin_node in cmds.ls(type='skinCluster'):
        cmds.skinCluster(skin_node, e=1, fnw=1)
    return True


def zero_controls():
    object_utils.zero_all_controllers()
    return True


def delete_unused():
    mel.eval('MLdeleteUnused;')


def run_cleanup_functions():
    for clean_func in FUNCTIONS:
        eval(clean_func)()
    return True
