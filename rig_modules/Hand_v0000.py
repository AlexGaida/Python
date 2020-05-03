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
class_name = "Hand"

reload(joint_utils)


class Hand(template.TemplateModule):
    class_name = class_name
    positions = ([0.0, 0.0, 0.0],
                 [3.0, 0.0, -2.0],
                 [6.0, 0.0, 0.0])

    def __init__(self, name="", control_shape="cube", prefix_name="", information=""):
        super(Hand, self).__init__(name=name, prefix_name=prefix_name, information=information)
        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape
        self.controller_data = {}
        self.guide_joints = []
        self.built_controllers = []

    def create_guides(self):
        """
        creates a guide joint object.
        :return: <bool> True for success.
        """
        self.guide_joints = joint_utils.create_joints_at_positions(self.positions,
                                                                   self.name,
                                                                   prefix_name=self.prefix_name,
                                                                   suffix_name=self.suffix_name)
        return self.guide_joints

    def create_controller(self, constraint_object):
        """
        creates a controller object.
        :return: <str> group name.
        """
        name = self.prefix_name + self.name
        return control_utils.create_controllers_with_standard_constraints(
            name, objects_array=constraint_object, shape_name=self.control_shape)

    def get_positions(self):
        """
        returns the positions of each guide joint.
        :return:
        """
        guide_positions = ()
        for jnt in self.guide_joints:
            guide_positions += object_utils.get_object_transform(jnt, ws=1, m=1),
        return guide_positions

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
        self.information["positions"] = self.get_positions()

    def remove(self):
        """
        removes the guide joints from the scene.
        :return: <bool> True for success.
        """
        if self.guide_joints:
            object_utils.remove_node(self.guide_joints)
        if self.built_controllers:
            object_utils.remove_node(self.built_controllers)
        self.finished = False
        self.created = False

    def replace_guides(self):
        """
        replaces the guide joints with actual joints.
        :return: <bool> True for success.
        """
        for jnt in self.guide_joints:
            # get the correct name from guides.
            bnd_jnt_name = name_utils.replace_guide_name_with_bnd_name(jnt)
            joint_utils.create_joint_at_transform(jnt, bnd_jnt_name)
        return True

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

        self.controller_data = self.create_controller(self.guide_joints)[0]
        parent_to = self.PUBLISH_ATTRIBUTES['parentTo']
        constrain_to = self.PUBLISH_ATTRIBUTES['constrainTo']
        if constrain_to and object_utils.is_exists(constrain_to):
            object_utils.do_parent_constraint(self.controller_data['controller'], constrain_to)
        if parent_to and object_utils.is_exists(parent_to):
            object_utils.do_parent(self.controller_data['group_names'][-1], parent_to)

        # store this
        self.built_controllers.append(self.controller_data['group_names'])
        print("[{}] :: finished.".format(self.name))
        self.finished = True
        return True
