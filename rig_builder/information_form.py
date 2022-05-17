"""
    Information form: module for handling information items about the selected modules.
"""
# import local modules
from imp import reload
import build_utils
import blueprint_utils
import ui_tools
import ui_stylesheets
from maya_utils import name_utils
from rig_utils import joint_utils
from rig_utils import control_shape_utils
from maya_utils import ui_utils
from maya_utils import file_utils
from maya_utils import object_utils

# import qt modules
from maya_utils.ui_utils import QtWidgets

# module reloads
reload(ui_stylesheets)
reload(build_utils)
reload(object_utils)
reload(joint_utils)
reload(ui_tools)
reload(control_shape_utils)
reload(file_utils)
reload(name_utils)
reload(blueprint_utils)

# define local variables
parent_win = ui_utils.get_maya_parent_window()
title = "Rig Builder"
object_name = title.replace(" ", "")
modules = build_utils.get_available_modules()


class InformationForm(QtWidgets.QFrame):
    information = {}
    info_widgets = {}

    def __init__(self, parent=None):
        super(InformationForm, self).__init__(parent)
        self.parent = parent
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.widgets = {}
        self.build()
        self.resize(40, 100)
        self.setLayout(self.main_layout)
        self.connect_buttons()

    #  Build the module information
    # __________________________________________________________________________________________________________________
    def build(self):
        """
        builds the widget with stuff
        """
        self.widgets['label'] = QtWidgets.QLabel("Intentionally Empty")
        self.widgets['instructions'] = QtWidgets.QVBoxLayout()
        self.widgets['updateButton'] = QtWidgets.QPushButton("Update")
        self.main_layout.addLayout(self.widgets['instructions'])
        self.widgets['instructions'].insertStretch(0)
        self.widgets['instructions'].addWidget(self.widgets['label'])
        self.main_layout.addWidget(self.widgets['updateButton'])

    def construct_items(self, data):
        """
        constructs the items based on the selection of the modules from the main window.
        """
        self.clear_instructions()
        self.build_instructions(data)
        self.update_field_information()

    def connect_buttons(self):
        """
        connects the buttons for use.
        """
        # self.widgets['updateButton'].clicked.connect(self.update_call)

    def build_instructions(self, data):
        """
        build instructions
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

    #  Information module utilities
    # __________________________________________________________________________________________________________________
    def clear_instructions(self):
        """
        updates the information based from the module clicked
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

    #  Information module update dictionary
    # __________________________________________________________________________________________________________________
    # def update_call(self):
    #     """
    #     information update when the update button is clicked
    #     :return: <bool> True for success. <bool> False for failure
    #     """
    #     if self.parent.module_form.is_build_toggled:
    #         QtWidgets.QMessageBox().warning(self, "Could not update.", "Please revert back to guides (Turn off build).")
    #         return False
    #     # get information
    #     self.get_information()
    #     # update the selected widget information data
    #     if self.information:
    #         self.parent.set_selected_module_name(self.information["name"])
    #         # update the widgets' published attributes
    #         self.parent.update_selected_item_attributes(self.information)
    #         debug_print("Updating module: %s with data: %s " % (self.information["name"], self.information))
    #     # update each module's guide positions (if any)
    #     self.parent.update_guide_position_data()
    #     # trigger the update function for each of the modules loaded in the UI
    #     # update_data_modules()
    #     # save the dictionary data into the chosen creature file
    #     creature_name = self.parent.get_selected_creature_name()
    #     # if creature_name:
    #     #     save_blueprint(creature_name, get_module_data())
    #     return True
    #
    # def update_information(self, key_name, value):
    #     """
    #     updates the specific fields with information.
    #     :return: <bool> True for success. <bool> False for failure.
    #     """
    #     if key_name in self.info_widgets:
    #         self.info_widgets[key_name].set_text(value)
    #         return True
    #     return False
    #
    # def update_field_information(self):
    #     """
    #     updates the fields with information from the selected item.
    #     :return: <bool> True for success.
    #     """
    #     attributes = self.parent.get_selected_item_attributes()
    #     debug_print('attributes: >> {}'.format(attributes))
    #     for attr_name, attr_val in attributes.items():
    #         self.update_information(attr_name, attr_val)
    #     return True
    #
    # def delete_all_widgets(self):
    #     """
    #     wipes the widgets away to rebuild them all anew.
    #     :return: <bool> True for success.
    #     """
    #     items_i = self.main_layout.count()
    #     for i in reversed(range(items_i.count())):
    #         items_i.itemAt(i).widget().deleteLater()
    #     return True
    #
    # def get_information(self):
    #     """
    #     extracts the information from the widgets.
    #     :return: <bool> True for success.
    #     """
    #     # get the information from informationWidget
    #     for item, widget in self.info_widgets.items():
    #         # let's get the positions data
    #         if item == "positions":
    #             self.information[item] = self.parent.get_selected_module_guide_positions()
    #         else:
    #             self.information[item] = self.get_text_data(widget.get_text())
    #     return True
    #
    # def get_text_data(self, text=""):
    #     """
    #     interprets the text data from the QLineEdits.
    #     :param text: <str> interpret this text data.
    #     :return: <bool> True for success. <bool> False for failure.
    #     """
    #     return file_utils.interpret_text_data(text)

# ______________________________________________________________________________________________________________________
# information_form.py
