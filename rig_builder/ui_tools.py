"""
ui_tools module for adding ui elements to a widget.
"""

# import qt module
from PySide2 import QtWidgets


class ModuleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ModuleDialog, self).__init__(parent)

        # class variables
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addStretch(1)


class LineEdit(QtWidgets.QWidget):
    def __init__(self, parent=None, label=""):
        super(LineEdit, self).__init__(parent)

        # class variables
        self.label = label
        self.widgets = {}
        self.build()

    def build(self):
        """
        builds the widget box
        :return: <QtWidget>
        """
        main_layout = QtWidgets.QHBoxLayout(self)
        self.widgets["labelWidget"] = QtWidgets.QLabel(self.label)
        self.widgets["lineEdit"] = QtWidgets.QLineEdit()
        main_layout.addWidget(self.widgets["labelWidget"])
        main_layout.addWidget(self.widgets["lineEdit"])

        self.setLayout(main_layout)
        return self.widgets

    def get_info(self):
        """
        return information from the line edit.
        :return: <str> gets the information from the line edit widget
        """
        return str(self.widgets["lineEdit"].text())


class RenameWidget(QtWidgets.QDialog):
    def __init__(self, parent=None, label="Renamer"):
        super(RenameWidget, self).__init__(parent)
        self.result = ""

        self.line = LineEdit(label="Rename")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.line)

        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)
        button = QtWidgets.QPushButton("Confirm")
        cancel = QtWidgets.QPushButton("Cancel")
        button.clicked.connect(self.rename_call)
        cancel.clicked.connect(self.close_ui)
        button_layout.addWidget(button)
        button_layout.addWidget(cancel)

        self.setWindowTitle(label)

        self.setLayout(layout)

    def close_ui(self):
        self.close()
        self.deleteLater()

    def rename_call(self):
        self.result = self.line.widgets['lineEdit'].text()
        if self.result:
            self.deleteLater()
        else:
            QtWidgets.QMessageBox().information(self, "Empty field.", "Please fill in the edit field.")

    def open_ui(self):
        self.show()
