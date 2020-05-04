"""
Singleton method to creating a single joint in the scene.
"""
# import local modules
from rig_utils import control_utils
from rig_utils import name_utils
from rig_utils import joint_utils
from rig_modules import template
from maya_utils import object_utils

# define module variables
class_name = "Singleton"


class Singleton(template.TemplateModule):
    class_name = class_name

    def __init__(self, name="", control_shape="cube", prefix_name="", information=""):
        super(Singleton, self).__init__(name=name, prefix_name=prefix_name, information=information)
        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape
        self.controller_data = {}
        self.guide_joints = []
        self.built_groups = []

    def create_guides(self):
        """
        creates a guide joint object.
        :return: <str> joint object name.
        """
        jnt_name = joint_utils.create_joint(
            name=self.name, guide_joint=True, prefix_name=self.prefix_name, as_strings=True)
        self.guide_joints.append(jnt_name[0])

    def create_controller(self, constraint_object):
        """
        creates a controller object.
        :return: <str> group name.
        """
        name = self.prefix_name + self.name
        return control_utils.create_controllers_with_standard_constraints(
            name, objects_array=constraint_object, shape_name=self.control_shape)

    def rename(self, name):
        """
        updates the guide joint with the information
        :return:
        """
        self.name = name
        for idx, guide_jnt in enumerate(self.guide_joints):
            new_name = name_utils.get_guide_name("", name, self.suffix_name)
            object_utils.rename_node(guide_jnt, new_name)
            self.guide_joints[idx] = new_name

        if self.built_controllers:
            for grp_name in self.built_controllers:
                control_utils.rename_controls(grp_name, new_name=name)
        return True

    def update(self, *args):
        """
        update the module.
        :param args: <list> updates the guide joints. the first argument is the name.
        :return:
        """
        if args:
            name = args[0]
            self.rename(name)
        self.information["positions"] = self.get_guide_positions()

    def remove(self):
        """
        removes the guide joints from the scene.
        :return: <bool> True for success.
        """
        if self.guide_joints:
            object_utils.remove_node(self.guide_joints)
        if self.built_groups:
            object_utils.remove_node(self.built_groups[0])
        if self.finished_joints:
            object_utils.remove_node(self.finished_joints)
        self.finished = False
        self.created = False

    def create(self):
        """
        creates a joint controlled by one joint.
        :return: <bool> True for success.
        """
        if self.created:
            return False

        # create the guide joints, collect the self.guide_joints class array.
        self.create_guides()

        # set the guide joint positions
        self.set_guide_positions()

        self.created = True
        return True

    def finish(self):
        """
        finish the construction of this module.
        :return: <bool> True for success.
        """
        if self.finished:
            return False

        # populate the finished joints using the positions of the guide joints
        self.replace_guides()

        # creates the controller object on the bound joint.
        self.controller_data = self.create_controller(self.finished_joints)[0]

        # create connections to other nodes in the scene
        parent_to = self.PUBLISH_ATTRIBUTES['parentTo']
        constrain_to = self.PUBLISH_ATTRIBUTES['constrainTo']
        if constrain_to and object_utils.is_exists(constrain_to):
            object_utils.do_parent_constraint(self.controller_data['controller'], constrain_to)
        if parent_to and object_utils.is_exists(parent_to):
            object_utils.do_parent(self.controller_data['group_names'][-1], parent_to)

        # store this
        self.built_groups = self.controller_data['group_names']
        print("[{}] :: finished.".format(self.name))
        self.finished = True
        return True
