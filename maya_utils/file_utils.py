"""
Creating and reading file objects, as well as manipulating the maya files.
"""

#import standard modules
import sys
import os
import xml

# import maya modules
from maya import cmds


def open_current_file():
    cmds.file(cmds.file(q=1, loc=1), o=1, f=1)

