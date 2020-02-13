"""
module for programmatically loading plugins
"""

# import maya modules
from maya import cmds


# import standard modules
import sys
import os

# define global variables
RELATIVE_PATH = os.path.dirname(__file__)
PLUG_IN_PATH = os.path.join(RELATIVE_PATH, 'plugins')


def find_plugins():
    return iter(os.listdir(PLUG_IN_PATH))


def load_plugins():
    for plug in find_plugins():
        cmds.loadPlugin(plug, quiet=True)
        print('[PluginLoad] :: Loaded plugin: {}.'.format(plug))
