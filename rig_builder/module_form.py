"""
    module_form
"""
# import local modules
import build_utils

# import qt modules
from maya_utils.ui_utils import QtWidgets, QtCore
import blueprint_utils

# icons
buttons = {"empty": build_utils.empty_icon,
           "red": build_utils.red_icon,
           "green": build_utils.green_icon,
           "yellow": build_utils.yellow_icon
           }


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
        self.vertical_layout.addLayout(slider_layout)
        self.vertical_layout.addWidget(self.list)
        self.setLayout(self.vertical_layout)
        self.setMinimumWidth(self.parent.WIDTH / 2)
        # connect the widget
        # connect the combo changer
        self.creature_combo.currentIndexChanged.connect(self.creature_selected_call)

    #  Module Form utilities
    # __________________________________________________________________________________________________________________
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
        """
        self.build = 0
        if self.get_selected_blueprint():
            if args == 1:
                self.build = 1
                # self.finish_all_call()
            elif args == 0:
                self.build = 0
                # self.create_all_call()
        else:
            QtWidgets.QMessageBox().warning(self, "Creature Blueprint Not Saved.", "Please save creature blueprint.")
            self.reset_slider(args)

    def reset_slider(self, index):
        """
        sets the slider position at the opposite to that of the given index.
        :param index: <int> index position of the build slider.
        """
        self.build_slider.blockSignals(True)
        self.build_slider.setValue(int(not index))
        self.build_slider.blockSignals(False)

    def connect_slider(self, slider):
        """
        connects the slider.
        """
        slider.valueChanged.connect(self.toggle_build_call)

    def add_module_list(self):
        """
        adds a module list to the widget
        :return: <QtWidgets.QListWidget> The main list widget
        """
        list = QtWidgets.QListWidget(self)
        list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        list.setMinimumHeight(self.parent.HEIGHT - 50)
        list.setMinimumWidth(self.parent.WIDTH - 50)
        return list

    def add_build_slider(self):
        """
        adds the new button
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
        h_layout.addWidget(label)
        h_layout.addWidget(self.build_slider)
        self.connect_slider(self.build_slider)
        return h_layout

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
        # clear the current instructions
        self.parent.remove_modules()
        # fill the modules with the selected blueprint
        self.parent.initializer(selected_file=True)
        # if the creature has been changed, reset the slider back at default position
        self.reset_slider(True)
        return True


class ModuleWidget(QtWidgets.QWidget):
    """
    the module widget form layout
    can be anything from a single script to a transform object
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
        # self.module_index = get_module_count(module_name)
        # set the information data dictionary of the module to pass data down to modules
        if information:
            if "name" in information:
                self.name = information["name"]
            if "creature" not in information:
                information["creature"] = parent.module_form.get_selected_blueprint()
            if "creature_directory" not in information:
                information["creature_directory"] = blueprint_utils.build_dir(information["creature"])
        else:
            self.name = '{}_{}'.format(module_name, self.module_index)
        # build the module widgets
        self.build()
        self.initialize_versions()
        # create the connections
        self.connect_buttons()
        # activate this module
        self.create_module(information=information)
        # initialize the attributes
        # Python never implicitly copies the objects, when set, it is referred to the exact same module.
        self.module_attributes = dict(self.module.PUBLISH_ATTRIBUTES)
        # update the class published attribute with the name given
        self.update_attribute('name', self.name)

    #  Create widget connections
    # __________________________________________________________________________________________________________________
    def get_data(self):
        """
        returns the module data information
        :return:
        """
        return self.module_data[self.module_name]

# ______________________________________________________________________________________________________________________
# module_form.py
