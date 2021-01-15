"""
    Main rig builder window.
"""
# import standard modules
from functools import partial
from pprint import pprint

# import local modules
import build_utils
import blueprint_utils
import ui_tools
import ui_stylesheets
from maya_utils import ui_utils
import module_form
import information_form

# import qt modules
from maya_utils.ui_utils import QtWidgets
from maya_utils.ui_utils import QtCore
from maya_utils.ui_utils import MayaQWidgetBaseMixin


# local variables
parent_win = ui_utils.get_maya_parent_window()
buttons = {"empty": build_utils.empty_icon,
           "red": build_utils.red_icon,
           "green": build_utils.green_icon,
           "yellow": build_utils.yellow_icon
           }
proper_modules = build_utils.get_proper_modules()
debug = False
title = 'RigBuilder'
object_name = 'RigBuilder'


def close_ui(object_name):
    """
    closes the builder User Interface.
    :return: <bool> True for success.
    """
    ui_utils.close_window(object_name)
    # clear history cache
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
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        # add the two widgets to the main layout
        horizontal_split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.main_layout.addWidget(horizontal_split)
        self.module_form = module_form.ModuleForm(parent=self)
        self.information_form = information_form.InformationForm(parent=self)
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

    #  Creature UI Initialize
    # __________________________________________________________________________________________________________________
    def __add_module_to_ui(self, blueprint_array):
        """
        blueprint array add
        """
        for module_data in blueprint_array:
            module_data = module_data.values()[0]
            module_type = module_data["moduleType"]
            self.add_module(module_type, module_data)

    def initializer(self, this_file=False, selected_file=False):
        """
        fill the module form with blueprint information
        :param this_file: <bool> get the file blueprint
        :param selected_file: <bool> get the selected blueprint file
        :return: <bool> Modules initialized
        """
        if this_file:
            blueprint_array = blueprint_utils.get_file_blueprint()
        elif selected_file:
            # get the information
            current_selection = self.module_form.get_selected_blueprint()
            if not current_selection:
                return False
            blueprint_array = blueprint_utils.read_blueprint(current_selection)
        if blueprint_array:
            # adds modules to the builder
            self.__add_module_to_ui(blueprint_array)
            return True

    #  Events
    # __________________________________________________________________________________________________________________
    def closeEvent(self, *args):
        """
        MainWindow close event call.
        :return: <bool> True for success.
        """
        # clear history cache
        return True

    #  Main Window utility items
    # __________________________________________________________________________________________________________________
    def add_module_menu(self):
        """
        module menu item
        :return: <bool> True if the module has been selected. <bool> False module is not selected.
        """
        mod_widget = ui_tools.ModulesList(list_items=[])
        mod_widget.exec_()
        selected_module = mod_widget.result
        if selected_module:
            self.add_module(selected_module)
            return True
        return False

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
        widget = module_form.ModuleWidget(module_name=module_name,
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
        return True

    #  Performs connections
    # __________________________________________________________________________________________________________________
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

    #  Selected module widget utility
    # __________________________________________________________________________________________________________________
    def select_item(self, *args):
        """
        click on the item call
        :param args: <list> widget items.
        """
        global MODULES_LIST
        global MODULE_NAMES_LIST
        # get the selected widget
        row_int = self.get_item_row(args)
        module_widget = MODULES_LIST[row_int]
        # get the information about the module
        attributes_data = self.get_attribute_data(module_widget)
        # construct the information item data inputs
        self.information_form.construct_items(attributes_data)
        # updates the information
        self.information_form.update_information('name', module_widget.name)

    @staticmethod
    def get_item_row(args):
        """
        returns the currently selected items' row
        :return: <int>
        """
        current_row = args[0].listWidget().currentRow()
        return current_row

    @staticmethod
    def get_attribute_data(module_widget):
        """
        gets the module information.
        :return: <dict> attribute data
        """
        data = module_widget.get_data()
        module_version = module_widget.get_current_version()
        # get build instructions about the module
        attribute_data = data[module_version].ATTRIBUTE_EDIT_TYPES
        return attribute_data

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
        """
        updates the guide positional data
        :return:
        """
        for mod in MODULES_LIST:
            mod.update_attribute('positions', mod.get_module_positions())

    #  Setup menu items
    # __________________________________________________________________________________________________________________
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
        :return: <dict> menu data.
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
        menu_data["saveNewBlueprint"] = QtWidgets.QAction("Save &New Blueprint")
        menu_data["removeBlueprint"] = QtWidgets.QAction("&Remove Blueprint")
        menu_data["openBlueprintDir"] = QtWidgets.QAction("&Open Blueprint Dir")
        menu_data["openBlueprintFile"] = QtWidgets.QAction("Open Blueprint &File")
        # utility actions
        menu_data["utilities"].addAction(menu_data["printData"])
        menu_data["utilities"].addAction(menu_data["reloadModules"])
        # blueprint options
        menu_data["blueprintOptions"].addAction(menu_data["setBlueprintPath"])
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

    #  Blueprint file utility functions
    # __________________________________________________________________________________________________________________
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
        # creature_name = self.get_selected_creature_name()
        # if creature_name:
        #     # save_blueprint(creature_name, get_module_data())

    def save_new_blueprint_call(self):
        """
        saves the blueprint.
        :return: <bool> saves the blueprint.
        """
        # dialog = ui_tools.GetNameWidget(label="Please choose a name.", text="CreatureA")
        # dialog.exec_()
        # creature_name = dialog.result
        # if creature_name:
        #     save_blueprint(creature_name, get_module_data())
        #     # refresh the creature combo box
        #     self.module_form.fill_blueprints(set_to_name=creature_name)
        # return True

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
            # clear_module_list_data()
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

    #  Additional utilities
    # __________________________________________________________________________________________________________________
    @staticmethod
    def print_module_data():
        """
        prints the module data to the console.
        :return: <bool> True for success.
        """
        # pprint(get_module_data())
        return True

    @staticmethod
    def reload_module_data():
        """
        reloads all the modules in the RigModules directory folder.
        :return: <bool> True for success.
        """
        build_utils.reload_modules()

# ______________________________________________________________________________________________________________________
