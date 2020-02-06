# import maya modules
from PySide2 import QtGui, QtWidgets


class MessageBox(QtWidgets.QDialog):
    def __init__(self, message=None, **kwargs):
        super(MessageBox, self).__init__()

        complete = QtWidgets.QMessageBox
        complete.information(self, "Error", message, QtWidgets.QMessageBox.Ok)

        self.setStyleSheet("QDialog {background-color: #CC3300}")

        self.deleteLater()
        self.close()
