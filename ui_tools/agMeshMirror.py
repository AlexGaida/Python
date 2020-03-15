"""
mesh mirror tool for dealing with mesh data and patterns.
"""
# import standard modules
import sys
from PySide2 import QtCore, QtGui, QtWidgets

# import maya modules

# import local modules
from maya_utils import mesh_utils


class Form(QtWidgets.QDialog):
    WIDGETS = {}

    def __init__(self, parent=False):
        super(Form, self).__init__(parent)
        self.setWindowTitle('agMeshMirror')

        self.WIDGETS['mirrorSelection'] = QtWidgets.QPushButton("Mirror Selection.")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.WIDGETS['mirrorSelection'])

        self.setLayout(layout)

        self.connect_buttons()

    def connect_buttons(self):
        self.WIDGETS['mirrorSelection'].clicked.connect(self.mirror_selection)

    @staticmethod
    def mirror_selection():
        mesh_utils.get_selected_vertices_mirror()


def open_tool():
    """
    opens the tool in whatever application we are using.
    :return: <bool> True for success.
    """
    form = Form()
    form.show()
    return True
