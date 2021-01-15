"""
    Controller node utility class for managing the nurbsCurve nodes
"""

# local imports
import object_utils
import node_utils
import name_utils
import nurbs_color_utils

# local variables
naming_conventions = name_utils.get_naming_conventions()

reload(node_utils)


class Control(node_utils.Node):
    def __init__(self, color_name="", color_level=0, color_value=None, **kwargs):
        super(Control, self).__init__(**kwargs)
        self.color_name = color_name
        self.color_level = color_level
        self.color_value = color_value

    def set_color_by_name(self, color_name=None):
        """
        sets the color of the controller
        :param color_name: <str> the color name to change to
        """
        if color_name:
            self.color_name = color_name
        nurbs_color_utils.set_color_by_name(self.shape_name, color_name=self.color_name, color_level=self.color_level)

    def set_color_by_value(self, color_value=None):
        """
        sets the color of the controller by value
        :param color_value: <tuple> the value to change the controller to
        """
        if color_value:
            self.color_value = color_value
        nurbs_color_utils.set_rgb_color_by_color_value(self.shape_name, color_value=self.color_value)

    def is_exists(self):
        """
        check if the node exists
        :return: <bool>
        """
        object_utils.is_exists(self.node)

    def get_shape_name(self):
        """
        get the nurbs curve shape node
        :return: <str>
        """
        shape_name = object_utils.get_shape_name(self.node)[0]
        return shape_name

    @property
    def shape_name(self):
        """
        returns the shape name of the controller object
        :return: <str> shape name
        """
        return self.get_shape_name()

    @property
    def is_control(self):
        """
        verify if the current node is of type nurbs curve
        :return: <bool>
        """
        is_control = object_utils.is_shape_nurbs_curve(self.node)
        return is_control

# ______________________________________________________________________________________________________________________
# control_shape_utils.py
