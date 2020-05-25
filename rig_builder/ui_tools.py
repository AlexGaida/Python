"""
ui_tools module for adding ui elements to a widget.
"""
# import qt module
from maya_utils.ui_utils import QtWidgets
from maya_utils.ui_utils import QtCore
from maya_utils.ui_utils import QtGui


class ModuleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ModuleDialog, self).__init__(parent)

        # class variables
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addStretch(1)


class LineEdit(QtWidgets.QWidget):
    def __init__(self, parent=None, label="", placeholder_text=""):
        super(LineEdit, self).__init__(parent)

        # class variables
        self.label = label
        self.placeholder_text = placeholder_text
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
        self.widgets["lineEdit"].setPlaceholderText(self.placeholder_text)
        main_layout.addWidget(self.widgets["labelWidget"])
        main_layout.addWidget(self.widgets["lineEdit"])
        self.setLayout(main_layout)
        return self.widgets

    def get_text(self):
        """
        return information from the line edit.
        :return: <str> gets the information from the line edit widget
        """
        return str(self.widgets["lineEdit"].text())

    def set_text(self, value):
        """
        populates the lineEdit with information.
        :param value:
        :return:
        """
        if not isinstance(value, str):
            value = "{}".format(value)
        return str(self.widgets["lineEdit"].setText(value))


class AttributeLabel(LineEdit):
    def __init__(self, parent=None, label="", placeholder_text=""):
        self.widgets = {}
        self.label = label
        self.placeholder_text = label

        # now instantiate the LineEdit class
        super(AttributeLabel, self).__init__(parent)
        self.widgets["lineEdit"].setReadOnly(True)


class GetNameWidget(QtWidgets.QDialog):
    def __init__(self, parent=None, label="Renamer", text=""):
        super(GetNameWidget, self).__init__(parent)
        self.result = ""
        self.line = LineEdit(label="Rename", placeholder_text=text)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.line)

        button_layout = QtWidgets.QHBoxLayout()
        # button_group = QtGui.QButtonGroup()
        layout.addLayout(button_layout)

        # sets the default button at confirm
        button = QtWidgets.QPushButton("Confirm")
        button.setDefault(True)
        button.setFocus()

        # adds the cancel button
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


class Label(QtWidgets.QLabel):
    """
    a custom QLabel that emits a named signal
    """
    named = QtCore.Signal()

    def __init__(self, parent=None, label=""):
        super(Label, self).__init__(parent)
        self.label = label
        self.setText(label)

    def change_text(self, name):
        self.setText(name)
        self.named.emit()


class ModulesList(QtWidgets.QDialog):
    """
    lists all available modules.
    """

    def __init__(self, parent=None, list_items=()):
        super(ModulesList, self).__init__(parent)
        self.selected_item = None

        self.list_items = list_items

        vertical_layout = QtWidgets.QVBoxLayout()
        self.list_widget = QtWidgets.QListWidget()
        vertical_layout.addWidget(self.list_widget)

        horizontal_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        horizontal_layout.addWidget(self.ok_button)
        horizontal_layout.addWidget(self.cancel_button)

        vertical_layout.addLayout(horizontal_layout)

        self.list_widget.addItems(self.list_items)

        self.create_connections()

        self.setLayout(vertical_layout)
        self.setWindowTitle("Modules List")

    def get_list_selection(self, args):
        self.selected_item = args.text()

    def ok_ui(self):
        """

        :return:
        """
        self.close()
        self.deleteLater()

    def cancel_ui(self):
        """
        close this ui.
        :return: <bool> True for success.
        """
        self.ok_ui()
        self.selected_item = False
        return True

    def create_connections(self):
        """
        creates the necessary connections.
        :return: <bool> True for success.
        """
        self.ok_button.clicked.connect(self.ok_ui)
        self.cancel_button.clicked.connect(self.cancel_ui)

        # connect list widget
        self.list_widget.itemClicked.connect(self.get_list_selection)
        return True

    @property
    def result(self):
        return self.selected_item
