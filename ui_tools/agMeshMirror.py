"""
mesh mirror tool for dealing with mesh data and patterns.
"""
# import standard modules
import sys

# import Qt modules
from PySide2 import QtWidgets

# import local modules
from maya_utils import mesh_utils

# define global variables
window_title = 'agMeshMirror'
open_windows = {}


class Form(QtWidgets.QDialog):
    WIDGETS = {}

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle(window_title)

        self.WIDGETS['mirrorSelection'] = QtWidgets.QPushButton("Mirror Selection.")
        self.WIDGETS['selectChangedVerts'] = QtWidgets.QPushButton("Select Changed Vertices.")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.WIDGETS['mirrorSelection'])
        layout.addWidget(self.WIDGETS['selectChangedVerts'])

        self.setLayout(layout)

        self.connect_buttons()

    def connect_buttons(self):
        self.WIDGETS['mirrorSelection'].clicked.connect(self.mirror_selection)
        self.WIDGETS['selectChangedVerts'].clicked.connect(self.select_shanged_vertices)

    @staticmethod
    def select_shanged_vertices():
        mesh_utils.get_selected_vertices_mirror()

    @staticmethod
    def mirror_selection():
        mesh_name, index_array = mesh_utils.get_selected_components()
        mesh_utils.select_indices(mesh_name, index_array)

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
    open_windows[window_title] = Form()
    open_windows[window_title].show()
    return open_windows
