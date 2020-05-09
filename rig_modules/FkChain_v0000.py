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
class_name = "FkChain"


class FkChain(template.TemplateModule):
    class_name = class_name

    def __init__(self, name="", control_shape="cube", prefix_name="", information=""):
        super(FkChain, self).__init__(name=name, prefix_name=prefix_name, information=information)

        self.add_new_information('positions')
        self.add_new_information('numberOfBones', value=3)

        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape

        # redefine template variables
        self.guide_joints = []
        self.controller_data = {}
        self.built_groups = []

    def create_guides(self):
        """
        creates a guide joint object.
        :return: <str> joint object name.
        """
        jnt_name = joint_utils.create_joint(
            name=self.name, guide_joint=True, prefix_name=self.prefix_name, as_strings=True)
        self.guide_joints.append(jnt_name[0])

    def rename(self, name):
        """
        updates the guide joint with the information
        :return: <bool> True for success.
        """
        self.name = name
        for idx, guide_jnt in enumerate(self.guide_joints):
            new_name = name_utils.get_guide_name("", name, self.suffix_name)
            object_utils.rename_node(guide_jnt, new_name)
            self.guide_joints[idx] = new_name

        if self.built_groups:
            control_utils.rename_controls(self.built_groups[0], new_name=name)
        return True

    def set_guide_positions(self):
        """
        sets the positions
        :return: <bool> True for success.
        """
        if self.guide_joints and "positions" in self.information:
            for jnt, pos in zip(self.guide_joints, self.information["positions"]):
                object_utils.set_object_transform(jnt, m=pos, ws=True)
            return True
        return False

    def get_guide_positions(self):
        """
        gets the current positions of guide joints.
        :return: <tuple> array of translation values.
        """
        if self.guide_joints:
            transforms = ()
            for jnt in self.guide_joints:
                transforms += object_utils.get_object_transform(jnt, m=True),
            return transforms
        return ()

    def update(self, *args):
        """
        update the module.
        :param args: <list> updates the guide joints. the first argument is the name.
        :return:
        """
        if args:
            name = args[0]
            self.rename(name)
        print('update called.')
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

    def create_controller(self, constraint_object):
        """
        creates a controller object.
        :return: <str> group name.
        """
        name = self.prefix_name + self.name
        return control_utils.create_controllers_with_standard_constraints(
            name, objects_array=constraint_object, shape_name=self.control_shape)

    def replace_guides(self):
        """
        replaces the guide joints with the actual bound joints.
        :return: <tuple> bound joint array.
        """
        self.finished_joints = ()
        if self.if_guides_exist():
            positions = self.get_guide_positions()
            object_utils.remove_node(self.guide_joints)
            for position in positions:
                self.finished_joints += joint_utils.create_joint(self.name, prefix_name=self.prefix_name,
                                                                 use_position=position, bound_joint=True,
                                                                 as_strings=True)[0],
            self.guide_joints = []

    def if_guides_exist(self):
        """
        checking function to search the validity of guides in the scene.
        :return:
        """
        return all(map(object_utils.is_exists, self.guide_joints))

    def select_guides(self):
        """
        select the guide joints
        :return:
        """
        if self.guide_joints:
            object_utils.select_object(self.guide_joints)

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
