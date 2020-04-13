"""
rig-building module for modular construction of rigs uses to load and save blueprints for data management.
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
import ui_tools
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
MODULES_LIST = []

# icons
buttons = {"empty": build_utils.empty_icon,
           "red": build_utils.red_icon,
           "green": build_utils.green_icon,
           "yellow": build_utils.yellow_icon
           }


def remove_module_decorator(func):
    def wrapper(*args, **kwargs):
        # run function
        index = func(*args, **kwargs)
        MODULES_LIST.pop(index)
        print MODULES_LIST
    return wrapper


class MainWindow(QtWidgets.QMainWindow):
    HEIGHT = 400
    WIDTH = 400
    # the main build blue-print to construct
    # every time the module is added to module form, this updates the blueprint dictionary
    # the blueprint should be saved automatically.
    BUILD_BLUEPRINT = {}

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
        self.menu_bar_data["clearModules"].triggered.connect(self.remove_modules)

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
        menu_data["clearModules"] = QtWidgets.QAction("Clear Modules")

        menu_data["toggleVis"] = QtWidgets.QAction("Toggle Verbosity")
        menu_data["loadBlueprint"] = QtWidgets.QAction("Load Blueprint")
        menu_data["options"].addAction(menu_data["addModule"])
        menu_data["options"].addAction(menu_data["toggleVis"])
        menu_data["options"].addAction(menu_data["clearModules"])
        self.setMenuBar(menu_bar)
        return menu_data

    def add_module(self, *args):
        """
        adds the module
        :param args:
        :return:
        """
        module_name = args[0]
        item = QtWidgets.QListWidgetItem()
        widget = ModuleWidget(module_name=module_name, list_widget=self.module_form.list, item=item)
        item.setSizeHint(widget.sizeHint())

        # update the class variable
        MODULES_LIST.append(widget)

        # add a widget to the list
        self.module_form.list.addItem(item)
        self.module_form.list.setItemWidget(item, widget)

        # connect the widget
        self.module_form.list.itemClicked.connect(partial(self.clicked_item, widget, self.information_form))

    def remove_modules(self):
        """
        removes the modules from the list widget.
        :return:
        """
        return self.module_form.list.clear()

    def construct_information_items(self, attributes_data):
        """
        construct items to the information_form based on the data given.
        :param attributes_data:
        :return:
        """
        line_edit_name = 'line-edit'
        if line_edit_name in attributes_data:
            for line_name in attributes_data[line_edit_name]:
                line_edit = ui_tools.LineEdit(label=line_name)
                self.information_form.information["instructions"].addWidget(line_edit)
        return True

    def clicked_item(self, *args):
        """
        click on the item call
        :param args:
        :return:
        """
        module_widget, info_form, list_item = args

        # module_data: {'singleton': {'0000': <class 'singleton_v0000.Singleton'>}}
        data = module_widget.module_data[module_widget.module_name]

        module_version = module_widget.get_current_version()
        attributes_data = data[module_version].ATTRIBUTE_EDIT_TYPES
        # construct the information item data inputs
        self.information_form.construct_items(attributes_data)

        # adjust the window size
        self.setMinimumSize(self.HEIGHT + 100, self.WIDTH)


class ModuleForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModuleForm, self).__init__(parent)
        self.resize(200, 400)

        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.list = QtWidgets.QListWidget(self)

        self.button = self.add_button()

        # connect buttons
        self.button.clicked.connect(self.build_all_call)

        self.vertical_layout.addWidget(self.list)
        self.vertical_layout.addWidget(self.button)
        self.setLayout(self.vertical_layout)

    def add_button(self):
        return QtWidgets.QPushButton("Build All")

    def build_all_call(self):
        """
        builds all the items in the list.
        :return:
        """
        for mod in MODULES_LIST:
            mod.perform_module_build_call()


class InformationForm(QtWidgets.QWidget):
    label = None

    def __init__(self, parent=None):
        super(InformationForm, self).__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.widgets = {}

        self.build()

        self.resize(40, 100)
        self.setLayout(self.main_layout)

    def build(self):
        """
        builds the widget with stuff.
        :return: <bool> True for success.
        """
        self.widgets['label'] = QtWidgets.QLabel("I am here")
        self.widgets['instructions'] = QtWidgets.QVBoxLayout()
        self.widgets['updateButton'] = QtWidgets.QPushButton("Update")
        self.main_layout.addLayout(self.widgets['instructions'])
        self.widgets['instructions'].insertStretch(0)
        self.widgets['instructions'].addWidget(self.widgets['label'])
        self.main_layout.addWidget(self.widgets['updateButton'])
        return True

    def clear_instructions(self):
        """
        updates the information based from the module clicked.
        :return: <bool> True for success.
        """
        widget_count = self.widgets['instructions'].count()
        for idx in reversed(range(1, widget_count)):
            item = self.widgets['instructions'].takeAt(idx)
            if item is not None:
                item.widget().deleteLater()
        return True

    def delete_all_widgets(self):
        """
        wipes the widgets away to rebuild them all anew.
        :return: <bool> True for success.
        """
        items_i = self.main_layout.count()
        for i in reversed(range(items_i.count())):
            items_i.itemAt(i).widget().deleteLater()
        return True

    def build_instructions(self, data):
        """
        build instructions
        :return:
        """
        for widget, items in data.items():
            if "line-edit" in widget:
                for item in items:
                    line_edit = ui_tools.LineEdit(label=item)
                    self.widgets['instructions'].addWidget(line_edit)

    def construct_items(self, data):
        """
        constructs the items based on the selection of the modules from the main window.
        :return:
        """
        self.clear_instructions()
        self.build_instructions(data)
        print("Whoaa I got clicked~", data)


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
        self.name_label = None
        self.dialog = None
        self.module = None
        self.module_name = module_name
        self.list_widget = list_widget
        self.item = item
        self.name = "Singleton"

        self.main_layout = QtWidgets.QHBoxLayout()
        self.module_data = self.find_module_data(module_name)

        # initialize the widgets
        self.build()
        self.initialize_versions()

        self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(self.main_layout)

        self.connect_buttons()

        # finalize
        self.create_module()

    def get_module_version(self):
        """
        builds the module version string
        :return: <str> the correct module name
        """
        version = self.get_current_version()
        return build_utils.module_file_name(self.module_name, version)

    def get_current_version(self):
        """
        gets the current version from the QComboBox
        :return: <str> version.
        """
        return self.version_combo.currentText()

    def initialize_versions(self):
        """
        updates the QComboBox with versions.
        :return: <bool> True for success.
        """
        versions = self.module_data[self.module_name].keys()
        self.version_combo.addItems(sorted(versions))

    def add_version(self):
        """
        adds a QComboBox.
        :return: <QtGui.QComboBox>
        """
        return QtWidgets.QComboBox()

    def add_text(self, name):
        """
        adds a QLabel text widget.
        :return: <QtGui.QPushButton>
        """
        return QtWidgets.QLabel(name)

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
        pix = QtGui.QPixmap(buttons["empty"])
        label.setPixmap(pix)
        return label, pix

    def build(self):
        self.icon, self.q_pix = self.add_icon()
        self.q_text = self.add_text(self.module_name)
        self.name_label = self.add_text(self.name)

        self.add_rename_action(self.name_label)

        self.version_combo = self.add_version()
        self.build_button = self.add_build_button()
        self.delete_button = self.add_delete_button()
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.q_text)
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.version_combo)
        self.main_layout.addWidget(self.build_button)
        self.main_layout.addWidget(self.delete_button)
        return True

    def add_rename_action(self, label):
        """
        executes a rename call.
        :param label:
        :return:
        """
        rename = QtWidgets.QAction(label)
        rename.setText("Rename")
        label.setContextMenuPolicy(QtGui.Qt.ActionsContextMenu)
        rename.triggered.connect(self.rename_call)
        label.addAction(rename)

    def rename_call(self):
        """
        rename this widget
        :return:
        """
        self.dialog = ui_tools.RenameWidget(label=self.name_label.text())
        self.dialog.exec_()
        self.name_label.setText(self.dialog.result)

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
        self.build_button.clicked.connect(self.perform_module_create_call)
        self.delete_button.clicked.connect(self.remove_item_call)

    def perform_module_create_call(self):
        """
        module build call perform
        :return:
        """
        self.create_module()
        # change the pixmap icon

    @remove_module_decorator
    def remove_item_call(self):
        """
        removes the item in question.
        """
        # removes the module from the list widget
        index = self.list_widget.row(self.item)
        self.list_widget.takeItem(index)

        # removes the module items
        self.remove_module()

        return index

    def change_status(self, color="green"):
        """
        Change the status of the widget to "built"
        """
        self.q_pix = QtGui.QPixmap(buttons[color])
        self.icon.setPixmap(self.q_pix)

    def get_module_name(self):
        return self.q_text.text()

    def get_module_version(self):
        return self.version_combo.itemText(0)

    def get_module(self, activate=False):
        module_name = self.q_text.text()
        module_version = self.get_module_version()
        module_class = build_utils.get_rig_module(module_name, module_version)

        if activate:
            return module_class(name=self.name)
        else:
            return module_class

    def create_module(self):
        self.module = self.get_module(activate=True)
        self.module.create()
        self.change_status(color="yellow")

    def finish_module(self):
        """
        finalize the module setup.
        :return:
        """
        self.module.finish()
        self.change_status(color="green")
        return True

    def remove_module(self):
        return self.module.remove()


def open_ui():
    global builder_win
    if builder_win:
        builder_win.close()
    builder_win = MainWindow(parent=parent_win)
    builder_win.show()
    return builder_win
