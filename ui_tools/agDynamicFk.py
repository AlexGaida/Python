"""
mesh mirror tool for dealing with mesh data and patterns.
"""
# import standard modules
import sys
from PySide2 import QtCore, QtGui, QtWidgets

# import local modules
from maya_utils import object_utils
from maya_utils import ui_utils

# reloads
reload(ui_utils)

# define global variables
window_title = 'agDynamicFk'
open_windows = {}


class Form(QtWidgets.QDialog):
    WIDGETS = {}

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle(window_title)

        h_layout = QtWidgets.QHBoxLayout()
        self.WIDGETS['controllerLineEdit'] = QtWidgets.QLineEdit("Please enter the controller name.")
        self.WIDGETS['controllerLineEdit'].setReadOnly(True)
        self.WIDGETS['lineEditAddButton'] = QtWidgets.QPushButton(" <<< ")
        h_layout.addWidget(self.WIDGETS['controllerLineEdit'], 0)
        h_layout.addWidget(self.WIDGETS['lineEditAddButton'], 1)
        layout = QtWidgets.QVBoxLayout()

        layout.addLayout(h_layout)

        self.WIDGETS['performDynamicFk'] = QtWidgets.QPushButton("Make selection dynamic.")
        layout.addWidget(self.WIDGETS['performDynamicFk'])

        self.setLayout(layout)

        self.connect_buttons()

    def connect_buttons(self):
        self.WIDGETS['lineEditAddButton'].clicked.connect(self.populate_controller)
        self.WIDGETS['performDynamicFk'].clicked.connect(self.construct_dynamic_fk)

    def construct_dynamic_fk(self):
        """
        make a dynamic fk chain through selection.
        :return:
        """
        controller_text = self.WIDGETS['controllerLineEdit'].text()
        print(controller_text)

    def populate_controller(self):
        """
        populates the controller text edit box.
        :return:
        """
        selected_object = object_utils.get_selected_node(single=True)
        self.WIDGETS['controllerLineEdit'].setText(selected_object)

    def close(self):
        self.close()
        self.deleteLater()


def open_it():
    """
    opens the tool in whatever application we are using.
    :return: <bool> True for success.
    """
    global open_windows
    if window_title in open_windows:
        open_windows[window_title].close()
    open_windows[window_title] = Form(parent=ui_utils.get_maya_parent_window())
    open_windows[window_title].show()
    return open_windows
