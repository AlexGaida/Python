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

# import qt modules
from PySide2 import QtWidgets, QtGui, QtCore


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)


class ModuleForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ModuleForm, self).__init__(parent)


class InformationForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(InformationForm, self).__init__(parent)


class ModuleWidget(QtWidgets.QHBoxLayout):
    def __init__(self, parent=None, text_label=""):
        super(ModuleWidget, self).__init__(parent)

    def add_version(self):
        return QtWidgets.QComboBox()

    def add_text(self):
        return QtWidgets.QLabel()

    def add_button(self):
        return QtWidgets.QPushButton()

    def add_icon(self):
        return QtGui.QIcon()

    def create(self):
        icon = self.add_icon()
        text = self.add_text()
        version = self.add_version()
        button = self.add_button()
        self.addWidget(icon)
        self.addWidget(text)
        self.addWidget(version)
        self.addWidget(button)
        return True
