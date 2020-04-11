"""
singleton method to creating a single joint in the scene.
"""
# import maya modules
from maya import cmds

# import local modules
from rig_utils import control_utils
from rig_utils import joint_utils
from rig_modules import template

class_name = "Singleton"


class Singleton(template.TemplateModule):
    def __init__(self, name="", control_shape="cube", prefix_name=""):
        super(Singleton, self).__init__(name=name, prefix_name=prefix_name)
        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape
        self.controller_data = {}

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
        self.controller_data = self.create_controller(joint_name)
        return True

    def finish(self):
        """
        finish the construction of this module.
        :return:
        """
        parent_to = self.PUBLISH_ATTRIBUTES['parentTo']
        constrain_to = self.PUBLISH_ATTRIBUTES['constrainTo']
        if constrain_to:
            cmds.parentConstraint(self.controller_data['controller'], constrain_to, mo=True)
        if parent_to:
            cmds.parent(self.controller_data['group_names'][-1], parent_to)
        return True

    def do_it(self):
        pass
