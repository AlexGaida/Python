"""
rig-building module for modular construction of rigs uses to load and save blueprints for data management.
The data is created and stored by the creation of guide joints themselves. The guide joints have the module information.
This is the main UI module for the rig builder.
Contains two most important widgets:
0. Menu bar to add items to the entire main window.
1. The information widget.
2. The Module collection widget.

Information:
    This is still in its infancy. Please do not use.
"""
# import standard modules
from functools import partial
from pprint import pprint

# import local modules
import build_utils
import blueprint_utils
import ui_tools
import ui_stylesheets
from rig_utils import name_utils
from rig_utils import joint_utils
from rig_utils import control_utils
from maya_utils import ui_utils
from maya_utils import file_utils
from maya_utils import object_utils

# import qt modules
from maya_utils.ui_utils import QtWidgets
from maya_utils.ui_utils import Qt
from maya_utils.ui_utils import QtCore
from maya_utils.ui_utils import QPixmap
from maya_utils.ui_utils import MayaQWidgetBaseMixin

# module reloads
reload(ui_stylesheets)
reload(build_utils)
reload(object_utils)
reload(joint_utils)
reload(ui_tools)
reload(control_utils)
reload(file_utils)
reload(name_utils)
reload(blueprint_utils)

# define local variables
parent_win = ui_utils.get_maya_parent_window()
title = "Rig Builder"
object_name = title.replace(" ", "")
modules = build_utils.get_available_modules()
proper_modules = build_utils.get_proper_modules()

MODULES_LIST = []
MODULE_NAMES_LIST = []
BUILD_BLUEPRINT = ()
MODULE_DATA = {}

# define private variables
__version__ = "0.0.1"

# icons
buttons = {"empty": build_utils.empty_icon,
           "red": build_utils.red_icon,
           "green": build_utils.green_icon,
           "yellow": build_utils.yellow_icon
           }

debug = True


def debug_print(*args, **kwargs):
    if not debug:
        return 1
    if 'pp' in kwargs:
        pprint(args)
        return 0
    print(args)
    return 0


def add_module_decorator(func):
    """
    adds the module to the global list variable.
    :param func: <PythonFunc>
    :return: <PythonFunc>
    """
    def wrapper(*args, **kwargs):
        widget = func(*args, **kwargs)
        add_item(widget)
    return wrapper


def remove_module_decorator(func):
    """
    removes the module from the global list variable.
    :param func: <PythonFunc>
    :return: <PythonFunc>
    """
    def wrapper(*args, **kwargs):
        index = func(*args, **kwargs)
        remove_item(index)
    return wrapper


class MainWindow(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    HEIGHT = 400
    WIDTH = 400
    INFORMATION = {}

    module_form = None
    information_form = None

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # add the widgets to the layouts.
        self.main_widget = QtWidgets.QWidget(self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout(self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # add the two widgets to the main layout
        horizontal_split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.main_layout.addWidget(horizontal_split)

        self.module_form = ModuleForm(parent=self)
        self.information_form = InformationForm(parent=self)
        horizontal_split.addWidget(self.module_form)
        horizontal_split.addWidget(self.information_form)

        # set up the right click menu box
        self.module_form.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.add_menu_actions(self.module_form)

        # add a menu bar
        self.menu_bar_data = self.setup_menu_bar()

        # resize the main window
        self.setMinimumSize(self.HEIGHT, self.WIDTH)

        # connect triggers
        self.connect_menu_options()
        self.connect_blueprint_options()
        self.connect_utilities_options()

        # add main layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle(title)

        self.setStyleSheet(ui_stylesheets.dark_orange_stylesheet)
        self.setObjectName(object_name)

        # we do not need the extra functionality right now..
        # initialize the builder with options
        # initialized = self.initializer(this_file=True)
        # print("[Builder] :: Modules intitialized {}.".format(initialized))

    # -----------------------------------------------
    #  Creature UI Initialize
    # -----------------------------------------------
    def __add_module_to_ui(self, blueprint_array):
        """
        blueprint array add
        """
        print "-->\n", blueprint_array
        for module_data in blueprint_array:
            module_data = module_data.values()[0]
            module_type = module_data["moduleType"]
            self.add_module(module_type, module_data)
        return True

    def initializer(self, this_file=False, selected_file=False):
        """
        fill the module form with blueprint information.
        :param this_file:
        :param selected_file:
        :return: <bool> Modules initialized.
        """
        if this_file:
            blueprint_array = get_file_blueprint()
        elif selected_file:
            # get the information
            current_selection = self.module_form.get_selected_blueprint()
            if not current_selection:
                return False
            blueprint_array = blueprint_utils.read_blueprint(current_selection)

        if blueprint_array:
            # clear the built modules history
            clear_module_list_data()

            # adds modules to the builder
            self.__add_module_to_ui(blueprint_array)
            return True
        return False

    # -----------------------------------------------
    #  Events
    # -----------------------------------------------
    def closeEvent(self, *args):
        """
        MainWindow close event call.
        :return: <bool> True for success.
        """
        # clear history cache
        clear_module_list_data()
        return True

    # -----------------------------------------------
    #  Main Window utility items
    # -----------------------------------------------
    def add_module_menu(self):
        """
        module menu item
        :return: <bool> True if the module has been selected. <bool> False module is not selected.
        """
        mod_widget = ui_tools.ModulesList(list_items=proper_modules)
        mod_widget.exec_()
        selected_module = mod_widget.result
        if selected_module:
            self.add_module(selected_module)
            return True
        return False

    @add_module_decorator
    def add_module(self, *args):
        """
        adds the module to the list widget.
        :param args: <list> incoming arguments
        :return: <QtWidgets.QWidget>
        """
        module_name = args[0]
        information = {}

        if len(args) > 1:
            information = args[1]

        item = QtWidgets.QListWidgetItem()
        widget = ModuleWidget(module_name=module_name,
                              list_widget=self.module_form.list,
                              item=item,
                              parent=self,
                              information=information)

        # makes sure the modules are shown correctly in the list widget
        item.setSizeHint(widget.sizeHint())

        # add a widget to the list
        self.module_form.list.addItem(item)
        self.module_form.list.setItemWidget(item, widget)
        return widget

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

    def remove_modules(self):
        """
        removes the modules from the list widget.
        :return: <bool> True for success.
        """
        self.module_form.list.clear()
        self.information_form.clear_instructions()
        clear_module_list_data()
        return True

    # -----------------------------------------------
    #  Performs connections
    # -----------------------------------------------
    def connect_menu_options(self):
        """
        connects the MainWindow module menu options.
        :return: <bool> True for success.
        """
        self.menu_bar_data["addModule"].triggered.connect(self.add_module_menu)
        self.menu_bar_data["clearModules"].triggered.connect(self.remove_modules)
        return True

    def connect_blueprint_options(self):
        """
        connects the MainWindow blueprint menu options.
        :return: <bool> True for success.
        """
        self.menu_bar_data["setBlueprintPath"].triggered.connect(self.set_blueprint_path_call)
        self.menu_bar_data["saveNewBlueprint"].triggered.connect(self.save_new_blueprint_call)
        self.menu_bar_data["saveBlueprint"].triggered.connect(self.save_blueprint_call)
        self.menu_bar_data["removeBlueprint"].triggered.connect(self.remove_blueprint_call)
        self.menu_bar_data["openBlueprintDir"].triggered.connect(self.open_blueprint_dir_call)
        self.menu_bar_data["openBlueprintFile"].triggered.connect(self.open_blueprint_file_call)
        return True

    def connect_utilities_options(self):
        """
        connects the utility options
        :return: <bool> True for success.
        """
        self.menu_bar_data["printData"].triggered.connect(self.print_module_data)
        self.menu_bar_data["reloadModules"].triggered.connect(self.reload_module_data)
        return True

    def clear_information(self):
        """
        clears the information form.
        :return: <bool> True for success.
        """
        self.information_form.clear_instructions()
        return True

    # -----------------------------------------------
    #  Selected module widget utility
    # -----------------------------------------------
    def select_item(self, *args):
        """
        click on the item call
        :param args: <list> widget items.
        :return: <bool> True for success.
        """
        global MODULES_LIST
        global MODULE_NAMES_LIST

        # get the selected widget
        row_int = self.get_item_row(args)
        module_widget = MODULES_LIST[row_int]

        # get the information about the module
        attributes_data = self.get_attribute_data(module_widget)
        # attributes_data = self.get_selected_item_attributes()
        print("data: {}".format(attributes_data))

        # construct the information item data inputs
        self.information_form.construct_items(attributes_data)

        # updates the information
        self.information_form.update_information('name', module_widget.name)
        return True

    @staticmethod
    def get_item_row(args):
        """
        returns the currently selected items' row
        :return: <int>
        """
        return args[0].listWidget().currentRow()

    @staticmethod
    def get_attribute_data(module_widget):
        """
        gets the module information.
        :return: <dict> attribute data
        """
        data = module_widget.get_data()
        module_version = module_widget.get_current_version()

        # get build instructions about the module
        return data[module_version].ATTRIBUTE_EDIT_TYPES
        # return data[module_version].information

    def get_selected_row(self):
        return self.module_form.list.currentRow()

    def get_selected_list_item(self):
        return MODULES_LIST[self.get_selected_row()]

    def get_selected_module_name(self):
        return self.get_selected_list_item().get_name()

    def set_selected_module_name(self, new_name):
        return self.get_selected_list_item().set_name(new_name)

    def get_selected_item_attributes(self):
        return self.get_selected_list_item().attributes

    def update_selected_item_attribute(self, key_name, value):
        return self.get_selected_list_item().update_attribute(key_name, value)

    def update_selected_item_attributes(self, dictionary_value):
        return self.get_selected_list_item().update_attributes(dictionary_value)

    def get_selected_module_guide_positions(self):
        return self.get_selected_list_item().get_module_positions()

    @staticmethod
    def update_guide_position_data():
        for mod in MODULES_LIST:
            mod.update_attribute('positions', mod.get_module_positions())
        return True

    # -----------------------------------------------
    #  Setup menu items
    # -----------------------------------------------
    def add_menu_actions(self, widget):
        """
        adds menu actions.
        """
        actions = {}
        for mod in proper_modules:
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
        menu_data["options"] = menu_bar.addMenu("&Module Options")
        menu_data["blueprintOptions"] = menu_bar.addMenu("&Blueprint Options")
        menu_data["utilities"] = menu_bar.addMenu("&Utilities")

        # create utility
        menu_data["printData"] = QtWidgets.QAction("&Print Module Data")
        menu_data["reloadModules"] = QtWidgets.QAction("&Reload Rig Modules")

        # create regular option actions
        menu_data["updateModules"] = QtWidgets.QAction("Update Modules")
        menu_data["addModule"] = QtWidgets.QAction("Add Module")
        menu_data["clearModules"] = QtWidgets.QAction("Clear Modules")

        # create blueprint option actions
        menu_data["setBlueprintPath"] = QtWidgets.QAction("S&et Blueprint Path")
        menu_data["saveBlueprint"] = QtWidgets.QAction("Save &Blueprint")
        menu_data["saveNewBlueprint"] = QtWidgets.QAction("Save &New Blueprint")
        menu_data["removeBlueprint"] = QtWidgets.QAction("&Remove Blueprint")
        menu_data["openBlueprintDir"] = QtWidgets.QAction("&Open Blueprint Dir")
        menu_data["openBlueprintFile"] = QtWidgets.QAction("Open Blueprint &File")

        # utility actions
        menu_data["utilities"].addAction(menu_data["printData"])
        menu_data["utilities"].addAction(menu_data["reloadModules"])

        # blueprint options
        menu_data["blueprintOptions"].addAction(menu_data["setBlueprintPath"])
        menu_data["blueprintOptions"].addAction(menu_data["saveBlueprint"])
        menu_data["blueprintOptions"].addAction(menu_data["saveNewBlueprint"])
        menu_data["blueprintOptions"].addAction(menu_data["removeBlueprint"])
        menu_data["blueprintOptions"].addAction(menu_data["openBlueprintDir"])
        menu_data["blueprintOptions"].addAction(menu_data["openBlueprintFile"])

        # set actions
        menu_data["options"].addAction(menu_data["updateModules"])
        menu_data["options"].addAction(menu_data["addModule"])
        menu_data["options"].addAction(menu_data["clearModules"])
        self.setMenuBar(menu_bar)
        return menu_data

    # -----------------------------------------------
    #  Blueprint file utility functions
    # -----------------------------------------------
    def set_blueprint_path_call(self):
        """
        blueprint path call.
        :return:
        """
        print("setting blueprint path.")

    def load_blueprint_call(self):
        """
        loads the available blueprints.
        :return:
        """
        print("blueprint loaded.")

    def save_blueprint_call(self):
        """
        blueprint save.
        :return:
        """
        creature_name = self.get_selected_creature_name()
        if creature_name:
            save_blueprint(creature_name, get_module_data())

    def save_new_blueprint_call(self):
        """
        saves the blueprint.
        :return: <bool> saves the blueprint.
        """
        dialog = ui_tools.GetNameWidget(label="Please choose a name.", text="CreatureA")
        dialog.exec_()
        creature_name = dialog.result
        if creature_name:
            save_blueprint(creature_name, get_module_data())

            # refresh the creature combo box
            self.module_form.fill_blueprints(set_to_name=creature_name)
        return True

    def get_selected_creature_data(self):
        """
        grabs the selected creature file name.
        :return:
        """
        selected_creature = self.module_form.get_selected_blueprint()
        return blueprint_utils.read_blueprint(selected_creature)

    def remove_blueprint_call(self):
        """
        removes the blueprint.
        :return:
        """
        selected_creature = self.module_form.get_selected_blueprint()
        if selected_creature:
            blueprint_utils.delete_blueprint(selected_creature)
            self.module_form.fill_blueprints()

            # removes all files stored.
            clear_module_list_data()
        return True

    def open_blueprint_dir_call(self):
        """
        opens the selected blueprint directory
        :return: <bool> True for success.
        """
        selected_creature = self.module_form.get_selected_blueprint()
        if selected_creature:
            blueprint_utils.open_blueprint_dir(selected_creature)
        return True

    def open_blueprint_file_call(self):
        """
        opens the selected blueprint directory
        :return: <bool> True for success.
        """
        selected_creature = self.module_form.get_selected_blueprint()
        if selected_creature:
            blueprint_utils.open_blueprint_file(selected_creature)
        return True

    def get_selected_creature_name(self):
        """
        get creature name.
        :return: <str> creature name.
        """
        return self.module_form.get_selected_blueprint()

    # -----------------------------------------------
    #  Additional utilities
    # -----------------------------------------------
    @staticmethod
    def print_module_data():
        """
        prints the module data to the console.
        :return: <bool> True for success.
        """
        pprint(get_module_data())
        return True

    @staticmethod
    def reload_module_data():
        """
        reloads all the modules in the rig_modules directory folder.
        :return: <bool> True for success.
        """
        build_utils.reload_modules()


class ModuleForm(QtWidgets.QFrame):
    build_slider = None

    def __init__(self, parent=None):
        super(ModuleForm, self).__init__(parent)
        self.resize(200, 400)
        self.parent = parent

        # set the toggle back at default
        self.build = 0

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.combo_layout = QtWidgets.QHBoxLayout()

        self.creature_combo = QtWidgets.QComboBox(self)
        self.fill_blueprints()

        self.creature_label = QtWidgets.QLabel("Select Blueprint: ")
        self.combo_layout.addWidget(self.creature_label)
        self.combo_layout.addWidget(self.creature_combo)
        self.vertical_layout.addLayout(self.combo_layout)

        self.list = self.add_module_list()
        slider_layout = self.add_build_slider()

        # connect buttons
        # self.button.clicked.connect(self.finish_all_call)

        self.vertical_layout.addLayout(slider_layout)
        self.vertical_layout.addWidget(self.list)
        self.setLayout(self.vertical_layout)

        self.setMinimumWidth(self.parent.WIDTH / 2)

        # connect the widget
        self.list.itemClicked.connect(parent.select_item)

        # connect the combo changer
        self.creature_combo.currentIndexChanged.connect(self.creature_selected_call)

    # -----------------------------------------------
    #  Module Form utilities
    # -----------------------------------------------
    def get_selected_blueprint(self):
        """
        returns the name of the selected blueprint.
        :return: <str> selected blueprint.
        """
        text = self.creature_combo.currentText()
        if "New" in text:
            return False
        return text

    def fill_blueprints(self, set_to_name=""):
        """
        fills the creature combobox with blueprints.
        :param set_to_name: (optional) <str> set the combo box to this creature name.
        :return: <bool> True for success.
        """
        self.creature_combo.blockSignals(True)

        blueprints = ['New']
        blueprints += build_utils.get_blueprints()
        self.creature_combo.clear()
        self.creature_combo.addItems(blueprints)
        self.set_creature_combo(set_to_name)

        self.creature_combo.blockSignals(False)
        return True

    def set_creature_combo(self, text="", block_signal=False):
        """
        sets the combo-box with the provided creature name.
        :return: <bool> True for success.
        """
        if text:
            text_int = self.creature_combo.findText(text)
            if block_signal:
                self.creature_combo.blockSignals(True)

            self.creature_combo.setCurrentIndex(text_int)

            if block_signal:
                self.creature_combo.blockSignals(False)
        return True

    @property
    def is_build_toggled(self):
        return self.build

    def toggle_build_call(self, args):
        """
        toggles the build call.
        :param args: <int> incoming set integer.
        :return:
        """
        self.build = 0
        if self.get_selected_blueprint():
            if args == 1:
                self.build = 1
                self.finish_all_call()
            elif args == 0:
                self.build = 0
                self.create_all_call()
        else:
            QtWidgets.QMessageBox().warning(self, "Creature Blueprint Not Saved.", "Please save creature blueprint.")
            self.reset_slider(args)

    def reset_slider(self, index):
        """
        sets the slider position at the opposite to that of the given index.
        :param index: <int> index position of the build slider.
        :return: <bool> True for success.
        """
        self.build_slider.blockSignals(True)
        self.build_slider.setValue(int(not index))
        self.build_slider.blockSignals(False)
        return True

    def connect_slider(self, slider):
        """
        connects the slider.
        :return: <bool> True for success.
        """
        slider.valueChanged.connect(self.toggle_build_call)
        return True

    def add_module_list(self):
        """
        adds a module list to the widget.
        :return: <QtWidgets.QListWidget>
        """
        list = QtWidgets.QListWidget(self)
        list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        list.setMinimumHeight(self.parent.HEIGHT - 50)
        list.setMinimumWidth(self.parent.WIDTH - 50)
        return list

    def add_build_slider(self):
        """
        adds the new button.
        :return: <QTWidgets.QPushButton>
        """
        h_layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Build: ")
        label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # set slider options
        self.build_slider = QtWidgets.QSlider()
        self.build_slider.setTickInterval(1)
        self.build_slider.setMinimum(0)
        self.build_slider.setMaximum(1)
        self.build_slider.setSliderPosition(0)
        self.build_slider.setOrientation(QtCore.Qt.Horizontal)
        self.build_slider.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        # slider.setStyleSheet(ui_stylesheets.slider_stylesheet)

        h_layout.addWidget(label)
        h_layout.addWidget(self.build_slider)

        self.connect_slider(self.build_slider)
        return h_layout
        # return QtWidgets.QPushButton("Build All")

    def finish_all_call(self):
        """
        builds all the items in the list.
        :return: <bool> True for success.
        """
        for mod in MODULES_LIST:
            mod.perform_module_finish_call()
        return True

    def create_all_call(self):
        """
        returns the modules back to default setting.
        :return: <bool> True for success.
        """
        self.creature_selected_call()
        return True

    def creature_selected_call(self, *args):
        """
        calls the creature selection comboBox.
        :return: <bool> True for success.
        """
        # clear history cache
        clear_module_list_data()

        # clear the current instructions
        self.parent.remove_modules()

        # fill the modules with the selected blueprint
        self.parent.initializer(selected_file=True)

        # if the creature has been changed, reset the slider back at default position
        self.reset_slider(True)
        return True


class InformationForm(QtWidgets.QFrame):
    information = {}
    info_widgets = {}

    def __init__(self, parent=None):
        super(InformationForm, self).__init__(parent)

        # define variables
        self.parent = parent
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.widgets = {}

        self.build()

        self.resize(40, 100)
        self.setLayout(self.main_layout)
        self.connect_buttons()

    # -----------------------------------------------
    #  Build the module information
    # -----------------------------------------------
    def build(self):
        """
        builds the widget with stuff.
        :return: <bool> True for success.
        """
        self.widgets['label'] = QtWidgets.QLabel("Intentionally Empty")
        self.widgets['instructions'] = QtWidgets.QVBoxLayout()
        self.widgets['updateButton'] = QtWidgets.QPushButton("Update")
        self.main_layout.addLayout(self.widgets['instructions'])
        self.widgets['instructions'].insertStretch(0)
        self.widgets['instructions'].addWidget(self.widgets['label'])
        self.main_layout.addWidget(self.widgets['updateButton'])
        return True

    def construct_items(self, data):
        """
        constructs the items based on the selection of the modules from the main window.
        :return:
        """
        self.clear_instructions()
        self.build_instructions(data)
        self.update_field_information()
        return True

    def connect_buttons(self):
        """
        connects the buttons for use.
        :return:
        """
        self.widgets['updateButton'].clicked.connect(self.update_call)

    def build_instructions(self, data):
        """
        build instructions.
        :return: <bool> True for success.
        """

        # labels first
        if 'label' in data:
            labels = data['label']
            for item in labels:
                label = ui_tools.AttributeLabel(label=item)
                self.widgets['instructions'].addWidget(label)
                self.info_widgets[item] = label

        # build divider
        divider = QtWidgets.QLabel("Information: ")
        self.widgets['instructions'].addWidget(divider)
        self.widgets['instructions'].insertStretch(len(self.info_widgets) + 1)

        # then comes the editable content
        if 'line-edit' in data:
            line_edits = data['line-edit']
            for item in line_edits:
                line_edit = ui_tools.LineEdit(label=item)
                self.widgets['instructions'].addWidget(line_edit)
                self.info_widgets[item] = line_edit
        return True

    # -----------------------------------------------
    #  Information module utilities
    # -----------------------------------------------
    def clear_instructions(self):
        """
        updates the information based from the module clicked.
        :return: <bool> True for success.
        """
        widget_count = self.widgets['instructions'].count()
        for idx in reversed(range(1, widget_count)):
            item = self.widgets['instructions'].takeAt(idx)
            if item is not None:
                widget_item = item.widget()
                if widget_item:
                    item.widget().deleteLater()
        # revert the widgets back to default
        self.info_widgets = {}
        return True

    # -----------------------------------------------
    #  Information module update dictionary
    # -----------------------------------------------
    def update_call(self):
        """
        information update when the update button is clicked.
        :return: <bool> True for success. <bool> False for failure.
        """
        if self.parent.module_form.is_build_toggled:
            QtWidgets.QMessageBox().warning(self, "Could not update.", "Please revert back to guides (Turn off build).")
            return False

        # get information
        self.get_information()

        # update the selected widget information data
        if self.information:
            self.parent.set_selected_module_name(self.information["name"])

            # update the widgets' published attributes
            self.parent.update_selected_item_attributes(self.information)
            debug_print("Updating module: %s with data: %s " % (self.information["name"], self.information))

        # update each module's guide positions (if any)
        self.parent.update_guide_position_data()

        # trigger the update function for each of the modules loaded in the UI
        update_data_modules()

        # save the dictionary data into the chosen creature file
        creature_name = self.parent.get_selected_creature_name()
        if creature_name:
            save_blueprint(creature_name, get_module_data())
        return True

    def update_information(self, key_name, value):
        """
        updates the specific fields with information.
        :return: <bool> True for success. <bool> False for failure.
        """
        if key_name in self.info_widgets:
            self.info_widgets[key_name].set_text(value)
            return True
        return False

    def update_field_information(self):
        """
        updates the fields with information from the selected item.
        :return: <bool> True for success.
        """
        attributes = self.parent.get_selected_item_attributes()
        debug_print('attributes: >> {}'.format(attributes))
        for attr_name, attr_val in attributes.items():
            self.update_information(attr_name, attr_val)
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

    def get_information(self):
        """
        extracts the information from the widgets.
        :return: <bool> True for success.
        """
        # get the information from informationWidget
        for item, widget in self.info_widgets.items():
            # self.information[item] = widget.get_text()
            # let's get the positions data
            if item == "positions":
                self.information[item] = self.parent.get_selected_module_guide_positions()
            else:
                self.information[item] = self.get_text_data(widget.get_text())
        return True

    def get_text_data(self, text=""):
        """
        interprets the text data from the QLineEdits.
        :param text: <str> interpret this text data.
        :return: <bool> True for success. <bool> False for failure.
        """
        return file_utils.interpret_text_data(text)


class ModuleWidget(QtWidgets.QWidget):
    """
    the module widget form layout.
    can be anything from a single script to a transform object.
    """
    # store the information inside this attributes variable
    module_attributes = {}

    def __init__(self, parent=None, module_name="", list_widget=None, item=None, information=None):
        super(ModuleWidget, self).__init__(parent)
        # initialize the module main layout
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(self.main_layout)

        # initialize widget variables
        self.icon = None
        self.q_text = None
        self.q_pix = None
        self.build_button = None
        self.delete_button = None
        self.version_combo = None
        self.name_label = None
        self.dialog = None
        self.module = None

        # initialize important variables
        self.list_widget = list_widget
        self.item = item
        self.parent = parent
        self.version = 0000

        self.module_name = module_name
        self.module_data = self.find_module_data(module_name)
        self.module_index = get_module_count(module_name)

        # set name of the module
        if information:
            if "name" in information:
                self.name = information["name"]
        else:
            self.name = '{}_{}'.format(module_name, self.module_index)

        # debug print
        debug_print("{}\n".format(self.name))
        debug_print(information)

        # build the module widgets
        self.build()
        self.initialize_versions()

        # create the connections
        self.connect_buttons()

        # activate this module
        self.create_module(information=information)

        debug_print(self.module.PUBLISH_ATTRIBUTES)

        # initialize the attributes
        # Python never implicitly copies the objects, when set, it is referred to the exact same module.
        self.module_attributes = dict(self.module.PUBLISH_ATTRIBUTES)

        # update the class published attribute with the name given
        self.update_attribute('name', self.name)

    # -----------------------------------------------
    #  Create widget connections
    # -----------------------------------------------

    def get_data(self):
        """
        returns the module data information
        :return:
        """
        return self.module_data[self.module_name]

    def update_information(self, key_name, value):
        """
        when the QLabel name gets updated, it also updates the information form.
        :param key_name: <str> new module name.
        :param value: <str>
        :return: <bool> True for success.
        """
        self.parent.information_form.update_information(key_name=key_name, value=value)
        return True

    def connect_buttons(self):
        """
        button clicked connections.
        :return: <bool> True for success.
        """
        self.build_button.clicked.connect(self.finish_module)
        self.delete_button.clicked.connect(self.remove_item_call)
        return True

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
        self.clear_information()
        return index

    def rename_guide_items_call(self):
        """
        renames the guide items if available
        :return:
        """
        name = self.get_name_label_text()
        # updates the scene with the new information.
        self.module.update(name)

        # updates the information widget
        self.update_information('name', name)

        # update the class attributes
        self.update_attribute('name', name)

    def select_call(self):
        """
        selects the objects.
        :return:
        """
        self.module.select_guides()
        self.module.select_built_objects()

    def rename_call(self):
        """
        Opens up a new dialog window to help with renaming a module widget.
        :return: <str> chosen module name.
        """
        self.dialog = ui_tools.GetNameWidget(label=self.name_label.text(), text=self.name)
        self.dialog.exec_()
        # get proper name
        if self.dialog.result:
            new_name = name_utils.get_start_name_with_num(self.dialog.result)
            # new_name = name_utils.get_start_name(self.dialog.result)

            self.set_name(new_name)
            return self.dialog.result

    # -----------------------------------------------
    #  Module widget utilities
    # -----------------------------------------------
    def get_name_label_text(self):
        """
        get the name label text.
        :return:
        """
        name = self.name_label.text()
        if len(name) > 1:
            name = ''.join(name)
        return name

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

    def install_module_text_changed_call(self):
        """
        installs module connections
        :return:
        """
        self.name_label.named.connect(self.rename_guide_items_call)

    def set_name(self, name):
        """
        sets the name of the rig module.
        :param name: <str> set the name in question.
        :return: <bool> True for success.
        """
        # change the name of the text label
        self.name_label.change_text(name)
        # change the name in the module itself
        self.module.name = name
        # change the name of this class
        self.name = name
        return True

    def clear_information(self):
        """
        clears information from the Module Form.
        :return: <bool> True for success.
        """
        return self.parent.clear_information()

    def change_status(self, color="green"):
        """
        Change the status of the widget to "built"
        """
        self.q_pix = QPixmap(buttons[color])
        self.icon.setPixmap(self.q_pix)

    def get_module_name(self):
        return self.q_text.text()

    def get_name(self):
        return self.name_label.text()

    def get_module_version(self):
        return self.version_combo.itemText(0)

    # -----------------------------------------------
    #  Class module utilities
    # -----------------------------------------------
    def get_module(self, activate=False, information={}):
        """
        instantiates the selected module class
        :param activate: <bool> create the instance of the specified class.
        :param information: <dict> create the module with incoming saved information.
        :return: <Class> module class.
        """
        module_name = self.q_text.text()
        module_version = self.get_module_version()

        # get the right rig module type with the associated version
        module_class = build_utils.get_rig_module(module_name, module_version)

        if activate:
            return module_class(name=self.name, information=information)
        else:
            return module_class

    def create_module(self, information):
        """
        creates a new module.
        :return:
        """
        self.module = self.get_module(activate=True, information=information)
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
        """
        removes a module.
        :return:
        """
        self.module.remove()
        del self.module
        return True

    def build_module(self):
        """
        removes a module.
        :return:
        """
        return self.module.build()

    def update_attribute(self, key_name, value):
        """
        updates the attributes with the latest
        :return: <bool> True for success.
        """
        # updates the class information
        self.module_attributes[key_name] = value
        return True

    def update_attributes(self, dictionary):
        """
        updates the modules' publish dictionary with new parameters.
        :param dictionary:
        :return: <bool> True for success.
        """
        # debug_print(" ------- Updating Publish Dictionary ------- ")
        self.module_attributes.update(dictionary)
        # debug_print(self.module_attributes, pp=1)

        # debug_print(" ------- Updating Module Dictionary ------- ")
        self.module.information.update(dictionary)
        # debug_print(self.module.informationm pp=1)
        return True

    def perform_module_finish_call(self):
        """
        module build call perform
        :return:
        """
        self.finish_module()

    def update_module(self):
        """
        updates the current module with current information.
        :return:
        """
        self.module.update()
        # self.update_attributes(self.module.information)

    def get_module_positions(self):
        """
        returns the positions of this module's guide joints
        :return: <tuple> positions.
        """
        return self.module.get_guide_positions()

    # -----------------------------------------------
    #  Builds the module widget
    # -----------------------------------------------
    @staticmethod
    def find_module_data(module_name):
        """
        grabs the module class data.
        :param module_name: <str> module name.
        :return: <dict> module data.
        """
        return build_utils.find_module_data(module_name)

    def populate_label(self):
        """
        populates the correct module name.
        :return:
        """
        label_name = self.module_data.keys()[0]
        self.q_text.setText(label_name)
        return True

    def initialize_versions(self):
        """
        updates the QComboBox with versions.
        :return: <bool> True for success.
        """
        versions = self.module_data[self.module_name].keys()
        self.version_combo.addItems(sorted(versions))

    def add_custom_text(self, name):
        """
        adds a custom text
        :return: <ui_tools.QLabel>
        """
        return ui_tools.Label(label=name)

    def add_text(self, name):
        """
        adds a QLabel text widget.
        :return: <QtWidgets.QLabel>
        """
        return QtWidgets.QLabel(name)

    @staticmethod
    def add_build_button():
        """
        adds a push button.
        :return: <QtWidgets.QPushButton>
        """
        return QtWidgets.QPushButton("Build")

    @staticmethod
    def add_delete_button():
        """
        adds a push button.
        :return: <QtWidgets.QPushButton>
        """
        return QtWidgets.QPushButton("Remove")

    @staticmethod
    def add_icon():
        """
        adds an empty 6`x6x icon.
        :return: <QtGui.QPixmap>
        """
        label = QtWidgets.QLabel()
        pix = QPixmap(buttons["empty"])
        label.setPixmap(pix)
        return label, pix

    def build(self):
        """
        build the items for this module.
        :return: <bool> True for success.
        """
        # build the module widget items
        self.icon, self.q_pix = self.add_icon()
        self.q_text = self.add_text(self.module_name)
        self.name_label = self.add_custom_text(self.name)
        self.version_combo = self.add_version()
        self.build_button = self.add_build_button()
        self.delete_button = self.add_delete_button()

        # creates a rename action for this module
        self.install_module_text_changed_call()
        self.add_actions(self.name_label)

        # appends a widget to the widget's main layout
        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.q_text)
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.version_combo)
        self.main_layout.addWidget(self.build_button)
        self.main_layout.addWidget(self.delete_button)
        return True

    def add_actions(self, label):
        """
        executes a rename call.
        :param label:
        :return:
        """
        select = QtWidgets.QAction(label)
        select.setText("Select")

        rename = QtWidgets.QAction(label)
        rename.setText("Rename")

        remove = QtWidgets.QAction(label)
        remove.setText("Remove")

        label.setContextMenuPolicy(Qt.ActionsContextMenu)
        rename.triggered.connect(self.rename_call)
        remove.triggered.connect(self.remove_item_call)
        select.triggered.connect(self.select_call)
        label.addAction(rename)
        label.addAction(remove)
        label.addAction(select)

    def add_version(self):
        """
        adds a QComboBox.
        :return: <QtGui.QComboBox>
        """
        return QtWidgets.QComboBox()

    @property
    def attributes(self):
        """
        returns the module published attributes.
        :return: <dict> module attributes
        """
        return self.module_attributes

    @property
    def current_version(self):
        """
        returns the version number from QComboBox.
        :return: <str> version number.
        """
        return self.get_current_version()


def clear_module_list_data():
    """
    clears the module list data.
    :return: <bool> True for success.
    """
    global MODULES_LIST
    global MODULE_NAMES_LIST
    global BUILD_BLUEPRINT

    MODULES_LIST = []
    MODULE_NAMES_LIST = []
    BUILD_BLUEPRINT = ()
    return True


def get_file_blueprint():
    """
    gets the blueprint saves into this Maya File.
    :return: <dict> creature data.
    """
    return build_utils.get_file_creature_data()


def save_blueprint(creature_name, data):
    """
    saves the blueprint file into the creature name specified.
    :param creature_name:
    :param data:
    :return:
    """
    blueprint_utils.write_blueprint(creature_name, data)
    # save the blueprint information
    file_utils.update_internal_file_variables("creatureData", data)
    return True


def get_module_count(module_name):
    """
    get the module count.
    :param module_name:
    :return: <int> modules count
    """
    return MODULE_NAMES_LIST.count(module_name)


def update_data_modules():
    """
    updates the current modules in the scene.
    :return: <bool> True for success.
    """
    global MODULES_LIST

    print("updating module list information.")

    for mod in MODULES_LIST:
        mod.update_module()
    return True


def get_module_data():
    """
    extracts the currently created module data.
    :return: <tuple> blueprint module data.
    """
    global MODULES_LIST
    global MODULE_NAMES_LIST
    global BUILD_BLUEPRINT

    BUILD_BLUEPRINT = ()

    if not MODULES_LIST or not MODULE_NAMES_LIST:
        raise ValueError("Modules list is empty, could not load data.")

    for idx, name in enumerate(MODULE_NAMES_LIST):
        module_info = MODULES_LIST[idx].module_attributes
        module_name = MODULES_LIST[idx].name

        MODULE_DATA = {}
        if module_name not in MODULE_DATA:
            MODULE_DATA[module_name] = module_info
        BUILD_BLUEPRINT += MODULE_DATA,
    return BUILD_BLUEPRINT


def add_item(widget):
    """
    adds item.
    :param widget: <PySide.QtWidget>
    :return: <bool> True for success.
    """
    global MODULES_LIST
    global MODULE_NAMES_LIST
    MODULES_LIST.append(widget)
    MODULE_NAMES_LIST.append(widget.module_name)
    return True


def remove_item(index):
    """
    remove item.
    :param index: <int> item at index.
    :return: <bool> True for success.
    """
    global MODULES_LIST
    global MODULE_NAMES_LIST
    del(MODULES_LIST[index])
    del(MODULE_NAMES_LIST[index])
    # MODULES_LIST.pop(index)
    # MODULE_NAMES_LIST.pop(index)
    return True


def close_ui():
    """
    closes the builder User Interface.
    :return: <bool> True for success.
    """
    ui_utils.close_window(object_name)

    # clear history cache
    clear_module_list_data()
    return True


def open_ui():
    """
    Opens the builder User Interface.
    :return: <PySide.QtMainWindow>
    """
    close_ui()

    builder_win = MainWindow(parent=parent_win)
    builder_win.show()
    return builder_win
