from PySide2 import QtWidgets
import os
from importlib import reload
from maya_utils import ui_utils
reload(ui_utils)
# Imports
ui = None


def openUI(targets_list=[]):
    '''
    Open UI.
    '''
    global ui
    if ui:
        ui.deleteLater()
    parent_window = ui_utils.get_maya_parent_window()
    ui = OrganizerUI(parent=parent_window, targets_list=targets_list)
    ui.show()
    return ui


def get_organized_list():
    return os.environ["__TEMP_TARGETS_LIST"].split(';')


def clear_cache():
    del os.environ["__TEMP_TARGETS_LIST"]


class OrganizerUI(QtWidgets.QMainWindow):
    key_index = "{}: {}"

    def __init__(self, parent=None, targets_list=[]):
        # Init:
        super(OrganizerUI, self).__init__(parent)
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.addWidget(QtWidgets.QLabel(
            "Please organize the targets in an descending order:"))
        self.treeWidget = QtWidgets.QListWidget(self.centralwidget)
        # ...add test targets
        for idx, item in enumerate(targets_list):
            q_item = QtWidgets.QListWidgetItem(
                OrganizerUI.key_index.format(idx, item))
            self.treeWidget.addItem(q_item)
            self.set_targets_from_list()
        self.verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.up_button = QtWidgets.QPushButton("Up")
        self.down_button = QtWidgets.QPushButton("Down")
        self.remove_button = QtWidgets.QPushButton("Remove")
        self.close_window = QtWidgets.QPushButton("Close Window")
        self.verticalLayout.addWidget(self.close_window)
        self.horizontalLayout.addWidget(self.up_button)
        self.horizontalLayout.addWidget(self.down_button)
        self.horizontalLayout.addWidget(self.remove_button)
        self.up_button.clicked.connect(self.re_organize_item_up)
        self.down_button.clicked.connect(self.re_organize_item_down)
        self.remove_button.clicked.connect(self.remove_item)
        self.setCentralWidget(self.centralwidget)
        # ...
        self.treeWidget.setAlternatingRowColors(True)
        self.close_window.clicked.connect(self.deleteLater)

    def re_organize_item_up(self):
        item = self.treeWidget.currentItem()
        items = self._get_item_list()
        selected_item = item.text()
        cur_item_idx = items.index(selected_item)
        if cur_item_idx == 0:
            return None
        else:
            items.pop(cur_item_idx)
            items.insert(cur_item_idx - 1, selected_item)
        self.treeWidget.clear()
        text = selected_item.split(': ')[-1]
        for idx, item in enumerate(items):
            item = item.split(': ')[-1]
            if text in item:
                found_idx = idx
            q_item = QtWidgets.QListWidgetItem(
                OrganizerUI.key_index.format(idx, item))
            self.treeWidget.addItem(q_item)
        items = self._get_item_list()
        cur_item_idx = items.index(OrganizerUI.key_index.format(
            found_idx, selected_item.split(': ')[-1]))
        self.treeWidget.setCurrentRow(cur_item_idx)
        self.set_targets_from_list()

    def re_organize_item_down(self):
        item = self.treeWidget.currentItem()
        items = self._get_item_list()
        selected_item = item.text()
        cur_item_idx = items.index(selected_item)
        if cur_item_idx == len(items):
            return None
        else:
            items.pop(cur_item_idx)
            items.insert(cur_item_idx + 1, selected_item)
        self.treeWidget.clear()
        text = selected_item.split(': ')[-1]
        for idx, item in enumerate(items):
            item = item.split(': ')[-1]
            if text in item:
                found_idx = idx
            q_item = QtWidgets.QListWidgetItem(
                OrganizerUI.key_index.format(idx, item))
            self.treeWidget.addItem(q_item)
        items = self._get_item_list()
        cur_item_idx = items.index(OrganizerUI.key_index.format(
            found_idx, selected_item.split(': ')[-1]))
        self.treeWidget.setCurrentRow(cur_item_idx)
        self.set_targets_from_list()

    def remove_item(self):
        item = self.treeWidget.currentItem()
        items = self._get_item_list()
        cur_item_idx = items.index(item.text())
        items.pop(cur_item_idx)
        self.treeWidget.clear()
        for idx, item in enumerate(items):
            item = item.split(': ')[-1]
            q_item = QtWidgets.QListWidgetItem(
                OrganizerUI.key_index.format(idx, item))
            self.treeWidget.addItem(q_item)
        self.set_targets_from_list()

    def _get_item_list(self):
        items = []
        for idx in range(self.treeWidget.count()):
            item = self.treeWidget.item(idx).text()
            items.append(item)
        return items

    def set_targets_from_list(self):
        items = []
        for idx in range(self.treeWidget.count()):
            item = self.treeWidget.item(idx).text()
            items.append(item)
        items = ';'.join(items)
        os.environ["__TEMP_TARGETS_LIST"] = items

    def get_targets_from_list(self):
        return os.environ["__TEMP_TARGETS_LIST"].split(';')


# __name__
if __name__ == '__main__':
    openUI()
# ______________________________________________________________________________
# organizer tool
