"""
rigbuilding module for modular building of rigs.
This is the main UI module for the rig builder.
Contains two most important widgets:
0. Menu bar to add items to the entire main window.
1. The information widget.
2. The Module collection widget.
"""
# import standard modules
import sys
import os

# import local modules
import build_utils
from maya_utils import ui_utils

# import qt modules
from PySide2 import QtWidgets, QtGui, QtCore


# define local variables
parent_win = ui_utils.get_maya_parent_window()
builder_win = None


class MainWindow(QtWidgets.QMainWindow):
    if __name__ == '__main__':
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            height = 400
            width = 400

            # add the widgets to the layouts.
            self.main_layout = QtWidgets.QHBoxLayout()
            self.module_form = ModuleForm()
            self.information_form = InformationForm()
            self.main_layout.addWidget(self.module_form)
            self.main_layout.addWidget(self.information_form)

            # add a menu bar
            self.menu_bar_data = self.setup_menu_bar()

            # resize the main window
            self.resize(height, width)

            # connect triggers
            self.menu_bar_data["addModule"].triggered(self.add_module)

        def setup_menu_bar(self):
            """
            creates a menu bar for this main window
            :return: <bool> True for success.
            """
            menu_data = {}
            menu_bar = QtWidgets.QMenuBar()
            menu_data["addModule"] = menu_bar.addMenu("Add Module")
            menu_data["toggleVis"] = menu_bar.addMenu("Toggle Verbosity")
            menu_data["menuBar"] = menu_bar
            self.setMenuBar(menu_bar)
            return menu_data

        def add_module(self):
            return ModuleDialog(parent=self)


class ModuleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ModuleDialog, self).__init__(parent)

        # class variables
        self.modules = self.get_available_modules()


class ModuleForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ModuleForm, self).__init__(parent)

    def add_button(self):
        return QtWidgets.QPushButton("Build All")


class InformationForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(InformationForm, self).__init__(parent)


class ModuleWidget(QtWidgets.QHBoxLayout):
    """
    the module widget form layout.
    can be anything from a single script to a transform object.
    """
    def __init__(self, parent=None, module_name=""):
        super(ModuleWidget, self).__init__(parent)
        # pyside widgets
        self.icon = None
        self.q_text = None
        self.button = None
        self.version = 0000
        self.version_combo = None

        # class variables
        self.module_data = self.find_module_data(module_name)

        # initialize the widgets
        self.create()
        self.initialize_icon()
        self.populate_versions()
        self.populate_label()

    def add_version(self):
        """
        adds a QComboBox.
        :return: <QtGui.QComboBox>
        """
        return QtWidgets.QComboBox()

    def add_text(self):
        """
        adds a QLabel text widget.
        :return: <QtGui.QPushButton>
        """
        return QtWidgets.QLabel()

    def add_button(self):
        """
        adds a push button.
        :return: <QtGui.QPushButton>
        """
        return QtWidgets.QPushButton("Build")

    def add_icon(self):
        """
        adds an empty 64x6x icon.
        :return: <QtGui.QIcon>
        """
        return QtGui.QIcon(build_utils.empty_icon)

    def create(self):
        self.icon = self.add_icon()
        self.q_text = self.add_text()
        self.version_combo = self.add_version()
        self.button = self.add_button()
        self.addWidget(self.icon)
        self.addWidget(self.text)
        self.addWidget(self.version)
        self.addWidget(self.button)
        return True

    def find_module_data(self, module_name):
        return build_utils.find_module_data(module_name)

    def populate_versions(self):
        for mod, data in self.module_data:
            self.version_combo.addItems(data.keys())
        return True

    def populate_label(self):
        label_name = self.module_data.keys()[0]
        self.q_text.setText(label_name)
        return True

    def initialize_icon(self):
        self.icon.pixmap()

    def connect_button(self):
        self.button.clicked.connect()

    def get_module_name(self):
        return self.q_text.text()

    def get_module_version(self):
        return self.version_combo.itemText(0)

    def get_module(self):
        module_name = self.q_text.text()
        module_version = self.get_module_version()
        build_utils.get_rig_module(module_name, module_version)


def open_ui():
    global builder_win
    builder_win = MainWindow(parent=parent_win)
    builder_win.show()
    return builder_win
