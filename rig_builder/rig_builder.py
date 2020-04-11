"""
rig-building module for modular building of rigs.
This is the main UI module for the rig builder.
Contains two most important widgets:
0. Menu bar to add items to the entire main window.
1. The information widget.
2. The Module collection widget.
"""
# import standard modules
import sys
import os

from functools import partial

# import local modules
import build_utils
from maya_utils import ui_utils

# import qt modules
from PySide2 import QtWidgets, QtGui, QtCore

# reloads
reload(build_utils)

# define local variables
parent_win = ui_utils.get_maya_parent_window()
builder_win = None
title = "Rig Builder"
modules = build_utils.get_available_modules()

# icons
empty_icon = build_utils.empty_icon
red_icon = build_utils.red_icon
green_icon = build_utils.green_icon
yellow_icon = build_utils.yellow_icon


class ModuleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ModuleDialog, self).__init__(parent)

        # class variables
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addStretch(1)


class MainWindow(QtWidgets.QMainWindow):
    HEIGHT = 400
    WIDTH = 400

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # add the widgets to the layouts.
        self.main_widget = QtWidgets.QWidget(self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout(self)

        # add the two widgets to the main layout
        self.module_form = ModuleForm()
        self.information_form = InformationForm()
        self.main_layout.addWidget(self.module_form)
        self.main_layout.addWidget(self.information_form)

        # set up the right click menu box
        self.module_form.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.add_menu_actions(self.module_form)

        # add a menu bar
        self.menu_bar_data = self.setup_menu_bar()

        # resize the main window
        self.setMinimumSize(self.HEIGHT, self.WIDTH)

        # connect triggers
        self.menu_bar_data["addModule"].triggered.connect(self.add_module)

        # add main layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle(title)

    def add_menu_actions(self, widget):
        """
        adds menu actions.
        """
        actions = {}
        for mod in modules:
            if "_v" in mod:
                mod = mod.split('_v')[0]
            actions[mod] = QtWidgets.QAction(self)
            actions[mod].setText(mod)
            actions[mod].triggered.connect(partial(self.add_module, mod))
            widget.addAction(actions[mod])
        return actions

    def setup_menu_bar(self):
        """
        creates a menu bar for this main window
        :return: <bool> True for success.
        """
        menu_data = {}
        menu_bar = QtWidgets.QMenuBar()
        menu_data["options"] = menu_bar.addMenu("&Options")
        menu_data["addModule"] = QtWidgets.QAction("Add Module")
        menu_data["toggleVis"] = QtWidgets.QAction("Toggle Verbosity")
        menu_data["menuBar"] = menu_data["options"].addAction(menu_data["addModule"])
        menu_data["menuBar"] = menu_data["options"].addAction(menu_data["toggleVis"])
        self.setMenuBar(menu_bar)
        return menu_data

    def add_module(self, *args):
        print("[Module] :: Added, {}".format(args))
        module_name = args[0]
        item = QtWidgets.QListWidgetItem()
        widget = ModuleWidget(module_name=module_name, list_widget=self.module_form.list, item=item)
        item.setSizeHint(widget.sizeHint())

        # add a widget to the list
        self.module_form.list.addItem(item)
        self.module_form.list.setItemWidget(item, widget)

        # connect the widget
        self.module_form.list.itemClicked.connect(partial(self.clicked_item, widget, self.information_form))

    def clicked_item(self, *args):
        print(args)


class ModuleForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModuleForm, self).__init__(parent)
        self.resize(200, 400)

        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.list = QtWidgets.QListWidget(self)

        button = self.add_button()
        self.vertical_layout.addWidget(self.list)
        self.vertical_layout.addWidget(button)
        self.setLayout(self.vertical_layout)

    def add_button(self):
        return QtWidgets.QPushButton("Build All")


class InformationForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InformationForm, self).__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(QtWidgets.QLabel("I am here."))
        self.resize(40, 100)
        self.setLayout(self.main_layout)

    def build(self):
        """
        builds the widget with stuff.
        :return: <bool> True for success.
        """

    def delete_all_widgets(self):
        """
        wipes the widgets away to rebuild them all anew.
        :return: <bool> True for success.
        """
        items_i = self.main_layout.count()
        for i in reversed(range(items_i.count())):
            items_i.itemAt(i).widget().deleteLater()
        return True


class ModuleWidget(QtWidgets.QWidget):
    """
    the module widget form layout.
    can be anything from a single script to a transform object.
    """
    def __init__(self, parent=None, module_name="", list_widget=None, item=None):
        super(ModuleWidget, self).__init__(parent)

        # initialize variables
        self.icon = None
        self.q_text = None
        self.q_pix = None
        self.build_button = None
        self.delete_button = None
        self.version = 0000
        self.version_combo = None
        self.module_name = module_name
        self.list_widget = list_widget
        self.item = item

        self.main_layout = QtWidgets.QHBoxLayout()
        self.module_data = self.find_module_data(module_name)
        #
        # initialize the widgets
        self.build()

        self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(self.main_layout)

        self.connect_buttons()
        # self.populate_versions()

    def add_version(self):
        """
        adds a QComboBox.
        :return: <QtGui.QComboBox>
        """
        return QtWidgets.QComboBox()

    def add_text(self):
        """
        adds a QLabel text widget.
        :return: <QtGui.QPushButton>
        """
        return QtWidgets.QLabel(self.module_name)

    def add_build_button(self):
        """
        adds a push button.
        :return: <QtGui.QPushButton>
        """
        return QtWidgets.QPushButton("Build")

    def add_delete_button(self):
        """
        adds a push button.
        :return: <QtGui.QPushButton>
        """
        return QtWidgets.QPushButton("Remove")

    def add_icon(self):
        """
        adds an empty 64x6x icon.
        :return: <QtGui.QIcon>
        """
        label = QtWidgets.QLabel()
        pix = QtGui.QPixmap(empty_icon)
        label.setPixmap(pix)
        return label, pix

    def build(self):
        self.icon, self.q_pix = self.add_icon()
        self.q_text = self.add_text()
        self.version_combo = self.add_version()
        self.build_button = self.add_build_button()
        self.delete_button = self.add_delete_button()
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.q_text)
        self.main_layout.addWidget(self.version_combo)
        self.main_layout.addWidget(self.build_button)
        self.main_layout.addWidget(self.delete_button)
        return True

    def find_module_data(self, module_name):
        return build_utils.find_module_data(module_name)

    def populate_versions(self):
        for mod, data in self.module_data:
            self.version_combo.addItems(data.keys())
        return True

    def populate_label(self):
        label_name = self.module_data.keys()[0]
        self.q_text.setText(label_name)
        return True

    def connect_buttons(self):
        self.build_button.clicked.connect(self.change_status_call)
        self.delete_button.clicked.connect(self.remove_item_call)

    def remove_item_call(self):
        """
        removes the item in question.
        """
        self.list_widget.takeItem(self.list_widget.row(self.item))

    def change_status_call(self):
        """
        Change the status of the widget to "built"
        """
        self.q_pix = QtGui.QPixmap(green_icon)
        self.icon.setPixmap(self.q_pix)

    def get_module_name(self):
        return self.q_text.text()

    def get_module_version(self):
        return self.version_combo.itemText(0)

    def get_module(self):
        module_name = self.q_text.text()
        module_version = self.get_module_version()
        build_utils.get_rig_module(module_name, module_version)


def open_ui():
    global builder_win
    if builder_win:
        builder_win.close()
    builder_win = MainWindow(parent=parent_win)
    builder_win.show()
    return builder_win
