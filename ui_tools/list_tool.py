from PySide2 import QtWidgets
import os
from importlib import reload
from maya_utils import ui_utils
ui = None
# local variables
__label = "Please choose the following files:"


def openUI(objects_list=[], label=__label):
    """Open UI.
    :param objects_list: <list> list of objects to display
    :param label: <str> the label to display on the UI
    """
    global ui
    if ui and not ui_utils.is_object_deleted(ui):
        ui.deleteLater()
    parent_window = ui_utils.get_maya_parent_window()
    ui = ListUI(parent=parent_window, objects_list=objects_list, label=label)
    ui.show()
    return ui


def get_list():
    return os.environ["__TEMP_FILES_LIST"].split(';')


def clear_cache():
    del os.environ["__TEMP_FILES_LIST"]


class ListUI(QtWidgets.QMainWindow):
    key_index = "{}: {}"

    def __init__(self, parent=None, objects_list=[], label=""):
        super(ListUI, self).__init__(parent)
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.addWidget(QtWidgets.QLabel(label))
        self.treeWidget = QtWidgets.QListWidget(self.centralwidget)
        # ...add test targets
        for idx, item in enumerate(objects_list):
            q_item = QtWidgets.QListWidgetItem(
                ListUI.key_index.format(idx, item))
            self.treeWidget.addItem(q_item)
            self.set_objects_from_list()
        self.verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)
        # ...
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.close_window = QtWidgets.QPushButton("Close Window")
        self.horizontalLayout.addWidget(self.ok_button)
        self.horizontalLayout.addWidget(self.close_window)
        self.ok_button.clicked.connect(self.return_selected_item)
        self.setCentralWidget(self.centralwidget)
        # ...
        self.treeWidget.setAlternatingRowColors(True)
        self.close_window.clicked.connect(self.deleteLater)

    def return_selected_item(self):
        item = self.treeWidget.currentItem()
        return item.text()

    def _get_item_list(self):
        items = []
        for idx in range(self.treeWidget.count()):
            item = self.treeWidget.item(idx).text()
            items.append(item)
        return items

    def set_objects_from_list(self):
        items = []
        for idx in range(self.treeWidget.count()):
            item = self.treeWidget.item(idx).text()
            items.append(item)
        items = ';'.join(items)
        os.environ["__TEMP_FILES_LIST"] = items

    def get_objects_from_list(self):
        return os.environ["__TEMP_FILES_LIST"].split(';')

    def __str__(self):
        self.return_selected_item()


# __name__
if __name__ == '__main__':
    openUI()
# ______________________________________________________________________________
# organizer tool
