"""
A tool that connects with the available blendshapes.
|-----------------------------------|
|  control_name:       [          ] |
|  connection_name:    [translateX] |
|  -------------------------------- |
|  blend_shape_node    [          ] |
|  blend_shape_attrib  [          ] |
| --------------------------------- |
|   [     button: connect       ]   |
|---------------------------------- |
"""

# import standard modules
from PySide2 import QtCore, QtGui, QtWidgets

# import local modules
from deformers import blendshape_utils
from maya_utils import ui_utils
from maya_utils import object_utils
from maya_utils import animation_utils

# reloads
reload(ui_utils)
reload(object_utils)

# define global variables
window_title = 'agBlendShapeConnector'
open_windows = {}


class Form(QtWidgets.QDialog):
    WIDGETS = {}

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle(window_title)

        # main layour
        layout = QtWidgets.QVBoxLayout()

        # controller object
        h_layout = QtWidgets.QHBoxLayout()
        self.WIDGETS['controllerLineEdit'] = QtWidgets.QLineEdit("Please enter the controller name.")
        self.WIDGETS['controllerLineEdit'].setReadOnly(True)
        self.WIDGETS['lineEditCtrlAddButton'] = QtWidgets.QPushButton(" <<< Control")
        h_layout.addWidget(self.WIDGETS['controllerLineEdit'], 0)
        h_layout.addWidget(self.WIDGETS['lineEditCtrlAddButton'], 1)

        layout.addLayout(h_layout) # 0
        layout.addWidget(QtWidgets.QLabel("--------------------------------------------------------------------------------")) # 2
        layout.insertSpacerItem(2, QtWidgets.QSpacerItem(5, 10)) # 2

        # attributes object
        h_layout2 = QtWidgets.QHBoxLayout()
        self.WIDGETS["blendShapeLabel"] = QtWidgets.QLabel("Please choose the available blend-shapes.")
        self.WIDGETS['blendShapeComboBox'] = QtWidgets.QComboBox()
        self.WIDGETS['blendShapeComboBox'].setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.add_menu_actions(self.WIDGETS['blendShapeComboBox'])
        self.populate_blendshapes()
        h_layout2.addWidget(self.WIDGETS["blendShapeLabel"], 0)
        h_layout2.addWidget(self.WIDGETS['blendShapeComboBox'], 1)

        # attributes object
        h_layout3 = QtWidgets.QHBoxLayout()
        self.WIDGETS["blendShaoeAttributesLabel"] = QtWidgets.QLabel("Please select available blend-shape attributes")
        self.WIDGETS['blendShaoeAttributesComboBox'] = QtWidgets.QComboBox()
        h_layout3.addWidget(self.WIDGETS["blendShaoeAttributesLabel"], 0)
        h_layout3.addWidget(self.WIDGETS['blendShaoeAttributesComboBox'], 1)
        
        layout.addLayout(h_layout2) # 3
        layout.addLayout(h_layout3) # 4
        layout.addWidget(QtWidgets.QLabel("Connect the blendShape with one of these attributes: "))  # 6
        layout.insertSpacerItem(5, QtWidgets.QSpacerItem(4, 10)) # 5

        self.WIDGETS['performConnectionButton'] = QtWidgets.QPushButton("Connect the attributes.")
        h_layout4 = QtWidgets.QHBoxLayout()
        self.WIbutton_group = QtWidgets.QButtonGroup()
        self.WIDGETS["attributesButtonGroup"] = QtWidgets.QButtonGroup()
        translateX = QtWidgets.QCheckBox("translateX")
        translateX.setChecked(True)
        translateY = QtWidgets.QCheckBox("translateY")
        translateZ = QtWidgets.QCheckBox("translateZ")

        rotateX = QtWidgets.QCheckBox("rotateX")
        rotateY = QtWidgets.QCheckBox("rotateY")
        rotateZ = QtWidgets.QCheckBox("rotateZ")
        self.WIDGETS["attributesButtonGroup"].addButton(translateX)
        self.WIDGETS["attributesButtonGroup"].addButton(translateY)
        self.WIDGETS["attributesButtonGroup"].addButton(translateZ)
        self.WIDGETS["attributesButtonGroup"].addButton(rotateX)
        self.WIDGETS["attributesButtonGroup"].addButton(rotateY)
        self.WIDGETS["attributesButtonGroup"].addButton(rotateZ)
        h_layout4.addWidget(translateX)
        h_layout4.addWidget(translateY)
        h_layout4.addWidget(translateZ)
        h_layout4.addWidget(rotateX)
        h_layout4.addWidget(rotateY)
        h_layout4.addWidget(rotateZ)
        layout.addLayout(h_layout4)
        layout.addWidget(self.WIDGETS['performConnectionButton'])

        self.setLayout(layout)
        self.connect_buttons()
        self.populate_shapes()
    
    def add_menu_actions(self, widget):
        """
        adds menu actions.
        """
        select = QtWidgets.QAction(self)
        select.setText("Select")
        select.triggered.connect(self.select_blendshape)
        widget.addAction(select)
        return True

    def select_blendshape(self):
        """
        selects the blendshape.
        """
        data = self.get_text_data()
        object_utils.select_object(data['blendShapeNode'])
        return True

    def populate_menu_bar(self):
        """
        populates the menu bar with options
        """
        file_menu = self.menuBar().addMenu('&BlendShape')
        file_menu.addAction("&Select BlendShape Node")
        return True

    def connect_buttons(self):
        """
        connects the abailable buttons
        """
        self.WIDGETS['lineEditCtrlAddButton'].clicked.connect(self.populate_controller)
        self.WIDGETS['performConnectionButton'].clicked.connect(self.connect_blendshape_attribute)

    def get_text_data(self):
        """
        get text data from the UI
        :return: <dict> return the line edit, comboBox text data as dictionary
        """
        text_data = {}
        text_data['controllerLineEdit'] = self.WIDGETS['controllerLineEdit'].text()
        item_idx = self.WIDGETS['blendShapeComboBox'].currentIndex()
        text_data['blendShapeNode'] = self.WIDGETS['blendShapeComboBox'].itemText(item_idx)
        item_idx = self.WIDGETS['blendShaoeAttributesComboBox'].currentIndex()
        text_data['blendShapeNodeAttributes'] = self.WIDGETS['blendShaoeAttributesComboBox'].itemText(item_idx)
        text_data['attributeName'] = self.WIDGETS['attributesButtonGroup'].checkedButton().text()
        return text_data

    def connect_blendshape_attribute(self):
        """
        make a dynamic fk chain through selection.
        :return: <bool> True for success.
        """
        data = self.get_text_data()
        controller_text = data['controllerLineEdit']
        driver_attrib_text = data['attributeName']
        blend_node_text = data['blendShapeNode']
        blend_shape_attribute = data['blendShapeNodeAttributes']
        print(controller_text, driver_attrib_text, ' >>> ', blend_node_text, blend_shape_attribute)
        animation_utils.connect_anim(controller_text, driver_attrib_text, blend_node_text, blend_shape_attribute)
        return True

    def populate_blendshapes(self):
        """
        populates the controller text edit box.
        :return:
        """
        blend_shape_nodes = blendshape_utils.get_scene_blendshapes(as_strings=True)
        self.WIDGETS['blendShapeComboBox'].addItems(blend_shape_nodes.values())

    def populate_shapes(self):
        """
        populates the controller text edit box.
        :return:
        """
        data = self.get_text_data()
        blend_node_text = data['blendShapeNode']
        shape_names = blendshape_utils.get_shapes(blend_node_text)
        self.WIDGETS['blendShaoeAttributesComboBox'].addItems(shape_names)

    def populate_controller(self):
        """
        populates the controller text edit box.
        :return:
        """
        selected_object = object_utils.get_selected_node(single=True)
        self.WIDGETS['controllerLineEdit'].setText(selected_object)
        self.setWindowTitle("{} :: {}".format(window_title, selected_object))

    def close(self):
        self.deleteLater()


def open_it():
    """
    opens the tool in whatever application we are using.
    :return: <bool> True for success.
    """
    global open_windows
    if window_title in open_windows:
        open_windows[window_title].close()
    open_windows[window_title] = Form(parent=ui_utils.get_maya_parent_window())
    open_windows[window_title].show()
    return open_windows
