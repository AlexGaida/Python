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
    suffix_name = '_guide_jnt'

    def __init__(self, name="", control_shape="cube", prefix_name=""):
        super(Singleton, self).__init__(name=name, prefix_name=prefix_name)
        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape
        self.controller_data = {}
        self.guide_joints = []
        self.built_controllers = []

    def create_joint(self):
        """
        creates a guide joint object.
        :return: <str> joint object name.
        """
        self.guide_joints.append(joint_utils.create_joint(name=self.name,
                                 prefix_name=self.prefix_name,
                                 suffix_name=self.suffix_name,
                                 as_strings=True,
                                 add_index=False)[0])

    def create_controller(self, constraint_object):
        """
        creates a controller object.
        :return: <str> group name.
        """
        name = self.prefix_name + self.name
        return control_utils.create_controllers_with_standard_constraints(
            name, objects_array=constraint_object, shape_name=self.control_shape)

    def create(self):
        """
        creates a joint controlled by one joint.
        :return: <bool> True for success.
        """
        self.create_joint()
        return True

    def rename(self, name):
        """
        updates the guide joint with the information
        :return:
        """
        self.name = name
        for idx, guide_jnt in enumerate(self.guide_joints):
            new_name = joint_utils.get_joint_name("", name, "", self.suffix_name)
            cmds.rename(guide_jnt, new_name)
            self.guide_joints[idx] = new_name

        if self.built_controllers:
            for grp_name in self.built_controllers:
                control_utils.rename_controls(grp_name, new_name=name)
        return True

    def update(self, *args):
        """
        update the module.
        :param args: <list> updates the guide joints
        :return:
        """
        name = args[0]
        return self.rename(name)

    def remove(self):
        """
        removes the guide joints from the scene.
        :return: <bool> True for success.
        """
        cmds.delete(self.guide_joints)
        cmds.delete(self.built_controllers[0])

    def finish(self):
        """
        finish the construction of this module.
        :return: <bool> True for success.
        """
        self.controller_data = self.create_controller(self.guide_joints)[0]
        parent_to = self.PUBLISH_ATTRIBUTES['parentTo']
        constrain_to = self.PUBLISH_ATTRIBUTES['constrainTo']
        if constrain_to:
            cmds.parentConstraint(self.controller_data['controller'], constrain_to, mo=True)
        if parent_to:
            cmds.parent(self.controller_data['group_names'][-1], parent_to)

        # store this
        self.built_controllers.append(self.controller_data['group_names'])
        return True
