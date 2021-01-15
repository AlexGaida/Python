"""

rig-building module for modular construction of rigs uses to load and save blueprints for data management.
The data is created and stored by the creation of guide joints themselves. The guide joints have the module information.
This is the main UI module for the rig builder.
Contains two most important widgets:
0. Menu bar to add items to the entire main window.
1. The information widget.
2. The Module collection widget.

Information:
    This is still in its infancy. Please do not use.

"""
# import standard modules
from pprint import pprint

# import local modules
import module_form
import information_form
import main_window
import build_utils
import blueprint_utils
import ui_stylesheets
from maya_utils import ui_utils
from maya_utils import file_utils

# import qt modules
from maya_utils.ui_utils import QtWidgets
from maya_utils.ui_utils import QtCore
from maya_utils.ui_utils import MayaQWidgetBaseMixin


# define local variables
parent_win = ui_utils.get_maya_parent_window()
title = "Rig Builder"
object_name = title.replace(" ", "")
modules = build_utils.get_available_modules()
proper_modules = build_utils.get_proper_modules()

# define private variables
__version__ = "0.0.1"

# icons
buttons = {"empty": build_utils.empty_icon,
           "red": build_utils.red_icon,
           "green": build_utils.green_icon,
           "yellow": build_utils.yellow_icon
           }
debug = False

# reloads
reload(build_utils)
reload(module_form)
reload(information_form)


def debug_print(*args, **kwargs):
    """
    debugging print
    :param args:
    :param kwargs:
    :return:
    """
    if not debug:
        return 1
    if 'pp' in kwargs:
        pprint(args)
        return 0
    return 0


def get_file_blueprint():
    """
    gets the blueprint saves into this Maya File
    :return: <dict> creature data
    """
    creature_data_dict = build_utils.get_file_creature_data()
    return creature_data_dict


def save_blueprint(creature_name, data):
    """
    saves the blueprint file into the creature name specified
    :param creature_name: <str> name of the blueprint to save
    :param data: <dict> blueprint creature data
    """
    blueprint_utils.write_blueprint(creature_name, data)
    file_utils.update_internal_file_variables("creatureData", data)


def close_ui():
    """
    closes the builder User Interface
    """
    ui_utils.close_window(object_name)


def open_ui():
    """
    Opens the builder User Interface
    :return: <PySide.QtMainWindow>
    """
    close_ui()
    builder_win = main_window.MainWindow(parent=parent_win)
    builder_win.show()
    return builder_win


# ______________________________________________________________________________________________________________________
# rig_builder.py
