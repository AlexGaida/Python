"""
    Controller node utility class for managing the nurbsCurve nodes
"""
# local imports
import object_utils
import node_utils
import name_utils
import nurbs_color_utils
from rig_utils import control_shape_utils

# local variables
naming_conventions = name_utils.get_naming_conventions()

# reloads
reload(node_utils)
reload(object_utils)


class Locator(node_utils.Node):
    def __init__(self, color_name=None, color_level=0, color_value=None, shape=None, position=None, **kwargs):
        super(Locator, self).__init__(**kwargs)
        if not shape:
            shape = 'cube'
        self.shape = shape
        self.position = position
        self.color_name = color_name
        self.color_level = color_level
        self.color_value = color_value
        self.suffix_name = self.naming_convention['control']
        # get the name with the updated suffix name parameter
        self.name = self.get_name(suffix_name=self.suffix_name)
        if not self.exists:
            self.node = self.name
            self.create()

    def create(self):
        """
        create the node in question
        :return: <str> new node created
        """
        ctrl = control_shape_utils.create_controller(shape_name=self.shape, name=self.name)
        self.set_color_by_name()
        self.set_color_by_value()
        self.set_outliner_color_name()
        self.set_outliner_color_value()
        self.node = ctrl

    def set_color_by_name(self, color_name=None, color_level=None):
        """
        sets the color of the controller
        :param color_name: <str> the color name to change to
        :param color_level: <int> sets the color level
        """
        if color_name:
            self.color_name = color_name
        if color_level:
            self.color_level = color_level
        if self.color_name:
            nurbs_color_utils.set_color_by_name(
                self.shape_name, color_name=self.color_name, color_level=self.color_level)

    def set_color_by_value(self, color_value=None):
        """
        sets the color of the controller by value
        :param color_value: <tuple> the value to change the controller to
        """
        if color_value:
            self.color_value = color_value
        if self.color_value:
            nurbs_color_utils.set_rgb_color_by_color_value(self.shape_name, color_value=self.color_value)

    def get_shape_name(self):
        """
        get the nurbs curve shape node
        :return: <str>
        """
        shape_name = object_utils.get_shape_name(self.node)[0]
        return shape_name

    def insert_parent_group(self, suffix_name=None):
        """
        inserts a new group transform about the controller transform
        :return: <str> group name
        """
        if not suffix_name:
            suffix_name = 'Grp'
        grp_name = name_utils.get_name(self.base_name, suffix_name=suffix_name, prefix_name=self.prefix_name,
                                       direction_name=self.direction_name, index=self.index,
                                       letter=self.letter, side_name=self.side_name)
        world_position = self.get_world_position()
        # create group sharing the same name as this controller
        if not object_utils.is_exists(grp_name):
            grp_node = object_utils.create_group(grp_name, position=world_position)
        else:
            raise ValueError("[ParentGroup] :: Already exists")
        object_utils.do_parent(self.node, grp_node)
        return grp_node

    def insert_child_group(self, suffix_name):
        """
        inserts a new group transform about the controller transform
        :return: <str> group name
        """
        grp_name = name_utils.get_name(self.base_name, suffix_name=suffix_name, prefix_name=self.prefix_name,
                                       direction_name=self.direction_name, index=self.index,
                                       letter=self.letter, side_name=self.side_name)
        world_position = self.get_world_position()
        # create group sharing the same name as this controller
        if not object_utils.is_exists(grp_name):
            grp_node = object_utils.create_group(grp_name, position=world_position)
        else:
            raise ValueError("[ChildGroup] :: Already exists")
        object_utils.do_parent(grp_node, self.node)
        return grp_node

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
        is_control = object_utils.is_shape_locator(self.node)
        return is_control

# ______________________________________________________________________________________________________________________
# locator_utils.py
