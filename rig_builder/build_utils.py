"""
added build utility module for managing the rig_builder ui functionality.
"""

# import standard modules
import sys
import posixpath
import os

# import local modules
from maya_utils import file_utils

# define local variables
this_dir = file_utils.get_this_directory()
parent_dir = file_utils.get_this_directory_parent()
rig_modules_dir = posixpath.join(parent_dir, 'rig_modules')


def get_rig_modules_list():
    return os.listdir(rig_modules_dir)
