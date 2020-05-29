"""
Singleton method to creating a single joint in the scene.
"""
# import standard modules
from pprint import pprint

# import local modules
from rig_utils import control_utils
from rig_utils import name_utils
from rig_utils import joint_utils
from rig_modules import template
from maya_utils import object_utils

# reloads
# reload(template)

# define module variables
class_name = "FkChain"


class FkChain(template.TemplateModule):
    class_name = class_name

    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",
                          "name": "",
                          "moduleType": "",
                          "positions": ()
                          }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo", "constrainTo", "positions", "numberOfBones"],
                            'label': ["moduleType"]
                            }

    def __init__(self, name="", control_shape="cube", prefix_name="", information=""):
        super(FkChain, self).__init__(name=name, prefix_name=prefix_name, information=information)

        self.add_new_information('positions')
        self.number_of_bones = 3
        self.information = information
        self.update_information(information)
        self.add_new_information('numberOfBones', value=self.number_of_bones)

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
        positions = joint_utils.get_joint_positions(self.number_of_bones)
        self.guide_joints = joint_utils.create_joint(
            num_joints=self.number_of_bones, name=self.name, guide_joint=True,
            prefix_name=self.prefix_name, as_strings=True, use_position=positions)

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
        if self.if_guides_exist():
            positions = self.get_guide_positions()
            object_utils.remove_node(self.guide_joints)
            self.guide_joints = []
            return joint_utils.create_joint(self.name,
                                            prefix_name=self.prefix_name,
                                            num_joints=len(positions),
                                            use_position=positions,
                                            bound_joint=True,
                                            as_strings=True),

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

    def perform_parenting(self):
        """
        now parent the groups to their controllers.
        :return: <bool> True for success. <bool> False for failure.
        """
        max_len = len(self.controller_data) - 1
        for idx in xrange(max_len):
            # data = {'controller': u'FkChain_0_0_ctrl', 'group_names': ('FkChain_0_0_ctrl_grp', 'FkChain_0_0_ctrl_cnst')
            if idx + 1 <= max_len:
                c_data = self.controller_data[max_len - idx]
                next_data = self.controller_data[(max_len - idx) - 1]
                object_utils.do_parent(c_data["group_names"][0], next_data["controller"])
        return True

    def finish(self):
        """
        finish the construction of this module.
        :return: <bool> True for success.
        """
        if self.finished:
            return False

        # creates the controller object on the bound joint.
        self.controller_data = self.create_controller(self.replace_guides()[0])

        # create connections to other nodes in the scene
        self.perform_connections()

        # now parent each group to their respective parent controller
        self.perform_parenting()

        # store this for deletion
        self.built_groups = self.controller_data[0]['group_names']

        print("[{}] :: finished.".format(self.name))
        self.finished = True
        return True
