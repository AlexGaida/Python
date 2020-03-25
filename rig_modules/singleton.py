"""
singleton method to creating a single joint in the scene.
"""

# import local modules
from rig_utils import control_utils
from rig_utils import joint_utils

import template


class_name = "Singleton"


class Singleton(template):

    def __init__(self, name="", control_shape="cube", prefix_name=""):
        Singleton.__init__(self)
        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape

    def create_joint(self):
        """
        creates a joint object.
        :return: <str> joint object name.
        """
        return joint_utils.create_joint(name=self.name,
                                        prefix_name=self.prefix_name,
                                        suffix_name='_bnd_jnt',
                                        as_strings=True)[0]

    def create_controller(self, constraint_object):
        """
        creates a controller object.
        :return: <str> group name.
        """
        name = self.prefix_name + self.name
        return control_utils.create_controllers_with_standard_constraints(name,
                                                                          objects_array=constraint_object,
                                                                          shape_name=self.control_shape)

    def create(self):
        """
        creates a joint controlled by one joint.
        :return:
        """
        joint_name = self.create_joint()
        self.create_controller(joint_name)
        return True

