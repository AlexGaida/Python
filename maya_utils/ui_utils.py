"""
Ui Utility modules for managing user interfaces with Maya window.
"""

# import maya modules
from maya import cmds
from maya import mel

# import maya modules
from maya import OpenMayaUI
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

# import PySide modules
from shiboken2 import isValid
from shiboken2 import wrapInstance
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtGui import QStandardItemModel
from PySide2.QtGui import QStandardItem
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt

# import local modules
import object_utils


class MessageBox(QtWidgets.QDialog):
    def __init__(self, message=None, **kwargs):
        super(MessageBox, self).__init__()

        complete = QtWidgets.QMessageBox
        complete.information(self, "Error", message, QtWidgets.QMessageBox.Ok)

        self.setStyleSheet("QDialog {background-color: #CC3300}")

        self.deleteLater()
        self.close()


def is_window_exists(window_name=""):
    """
    returns a boolean if the window exists.
    :param window_name: <str> window name.
    :return: <bool> window exists.
    """
    return cmds.window(window_name, exists=1)


def get_maya_parent_window():
    """
    returns the object of the Maya's parent window.
    :return: <PySide.QObject> Maya Main Window
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QtWidgets.QMainWindow)


def is_object_deleted(widget_obj):
    """
    checks if the object is deleted.
    :return: <bool> True for yes. <bool> False for no.
    """
    return isValid(widget_obj)


def close_window(window_name):
    """
    closes a maya window.
    :return: <bool> True for successful deletion. <bool> False window not deleted.
    """
    if is_window_exists(window_name):
        cmds.deleteUI(window_name)
        return True
    return False


def find_control(maya_ui_object):
    """
    get the control from the widget string provided.
    :return: <PySide.QtWidgets.QWidget>
    """
    try:
        widget = mel.eval('string $tempString = {}'.format(maya_ui_object))
    except RuntimeError:
        # RuntimeError: Error occurred during execution of MEL script,
        # Invalid use of Maya object.
        pass
    ptr = OpenMayaUI.MQtUtil.findControl(widget)
    return wrapInstance(long(ptr), QtWidgets.QWidget)


class WidgetHierarchyTree(MayaQWidgetBaseMixin, QtWidgets.QTreeView):
    """
    taken from Autodesk Development Page:
    https://help.autodesk.com/view/MAYAUL/2017/CHS/?guid=__files_GUID_3F96AF53_A47E_4351_A86A_396E7BFD6665_htm
    Also exists in devkit pythonScripts.widgetHierarchy.py
    """
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(WidgetHierarchyTree, self).__init__(*args, **kwargs)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QWidget)

        self.populateModel()

    def populateModel(self):
        # Create the headers
        self.columnHeaders = ['Class', 'ObjectName', 'Children']
        myModel = QStandardItemModel(0, len(self.columnHeaders))
        for col, colName in enumerate(self.columnHeaders):
            myModel.setHeaderData(col, QtCore.Qt.Horizontal, colName)

        # Recurse through child widgets
        parentItem = myModel.invisibleRootItem()
        self.populateModel_recurseChildren(parentItem, self.rootWidget)
        self.setModel(myModel)

    def populateModel_recurseChildren(self, parentItem, widget):
        # Construct the item data and append the row
        classNameStr = str(widget.__class__).split("'")[1]
        classNameStr = classNameStr.replace(
            'PySide2.', '').replace('QtGui.', '').replace('QtCore.', '').replace('QtWidgets.', '')

        items = [QStandardItem(classNameStr),
                 QStandardItem(widget.objectName()),
                 QStandardItem(str(len(widget.children())))
                 ]
        parentItem.appendRow(items)

        # Recurse children and perform the same action
        for childWidget in widget.children():
            self.populateModel_recurseChildren(items[0], childWidget)


def open_skin_paint_tool():
    """
    ArtPaintSkinWeightsToolOptions; changeSelectMode -object; select -add dress_M_geo;
    :return:
    """
    node = object_utils.get_selected_node()
    object_utils.is_shape_mesh(node)
    mel.eval("ArtPaintSkinWeightsToolOptions; changeSelectMode -object; select -add {};".format(node))