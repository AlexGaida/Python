# import maya modules
import shiboken2
from PySide2 import QtGui, QtWidgets
from maya import OpenMayaUI


class MessageBox(QtWidgets.QDialog):
    def __init__(self, message=None, **kwargs):
        super(MessageBox, self).__init__()

        complete = QtWidgets.QMessageBox
        complete.information(self, "Error", message, QtWidgets.QMessageBox.Ok)

        self.setStyleSheet("QDialog {background-color: #CC3300}")

        self.deleteLater()
        self.close()


def get_maya_parent_window():
    """
    returns the object of the Maya's parent window.
    :return: <PySide.QObject> Maya Main Window
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QMainWindow)
