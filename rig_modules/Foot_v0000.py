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

# define module variables
class_name = "Foot"


class Foot(template.TemplateModule):
    class_name = class_name
    class_name = class_name

    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",
                          "name": "",
                          "moduleType": "",
                          "positions": (),
                          "pivot_positions": ()
                          }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo",
                                          "constrainTo", "positions",
                                          "forwardAxis", "pivot_positions"],
                            'label': ["moduleType"]
                            }

    def __init__(self, name="", control_shape="cube", prefix_name="", information={}):
        super(Foot, self).__init__(name=name, prefix_name=prefix_name, information=information)

        # for whatever reason this doesn't work
        self.information = information
        self.update_information(information)

        # define module variables
        self.names = (name + '_ankle',
                      name + '_ball',
                      name + '_toe')

        self.pivot_names = (self.name + '_back_step',
                            self.name + '_ball',
                            self.name + '_right_step',
                            self.name + '_left_step',
                            self.name + '_front_step')

        # initial pivot positions
        self.pivot_positions = ([0.0, 0.0, 0.0],
                                [0.0, 0.0, 2.0],
                                [1.0, 0.0, 2.0],
                                [-1.0, 0.0, 2.0],
                                [0.0, 0.0, 3.0])

        self.locator_pivot_guide_names = map(name_utils.get_locator_name, self.pivot_names)
        self.pivot_names = map(name_utils.get_pivot_name, self.pivot_names)
        self.controller_names = map(name_utils.get_control_name, self.names)

        ankle_ik = name_utils.get_ik_handle_name(self.name + '_ankle')
        toe_ik = name_utils.get_ik_handle_name(self.name + '_toe')

        self.ik_handles = ankle_ik, toe_ik,

        ankle_grp = name_utils.get_ctrl_group_name(self.names[0])
        ball_grp = name_utils.get_ctrl_group_name(self.names[1])
        toe_grp = name_utils.get_ctrl_group_name(self.names[2])

        self.ik_handles_structure = {
            ankle_ik: (self.get_bound_joint_name(self.names[0]), self.get_bound_joint_name(self.names[1])),
            toe_ik: (self.get_bound_joint_name(self.names[1]), self.get_bound_joint_name(self.names[2]))
        }

        # set the parenting structure
        # parent_name, (children)
        self.parent_structure = (
            (self.pivot_names[3], self.pivot_names[4]),
            (self.pivot_names[4], self.pivot_names[0]),
            (self.pivot_names[0], ankle_grp),
            (self.pivot_names[2], self.controller_names[1]),
            (self.controller_names[0], (ball_grp,  self.pivot_names[1])),
            (self.pivot_names[1], self.pivot_names[2]),
            (self.controller_names[1], toe_grp),
        )

        self.add_new_information('forwardAxis', value='x')
        self.add_new_information('pivot_positions', value=self.pivot_positions)

        self.forward_axis = self.information['forwardAxis']
        if not self.forward_axis:
            self.forward_axis = 'x'

        # define template variables
        self.name = name
        self.prefix_name = prefix_name
        self.control_shape = control_shape
        self.parent_to = ""
        self.constrain_to = ""

        # redefine template variables
        self.guide_joints = []
        self.controller_data = {}
        self.built_groups = []
        self.ik_handles = ()
        self.pivot_locators = ()

    def create_locators_pivot_guides(self):
        """
        create locator positions for the foot pivoting system.
        :return: <bool> True for success.
        """
        # create the pivot locators
        self.pivot_locators = ()
        for name, pivot in zip(self.locator_pivot_guide_names, self.pivot_positions):
            self.pivot_locators += object_utils.create_locator(name, position=pivot),
        return True

    def create_guides(self):
        """
        creates a guide joint object.
        :return: <str> joint object name.
        """
        self.guide_joints = ()

        # get the positions for the middle joint
        positions = ([0.0, 1.0, 0.0], [0.0, 0.0, 2.0], [0.0, 0.0, 3.0])

        # create the hand joint
        for name, pos in zip(self.names, positions):
            self.guide_joints += joint_utils.create_joint(
                num_joints=1, name=name, guide_joint=True,
                prefix_name=self.prefix_name, as_strings=True, use_position=pos),

        for idx in xrange(1, len(self.guide_joints)):
            object_utils.do_parent(self.guide_joints[idx], self.guide_joints[idx - 1])

    def rename(self, name):
        """
        updates the guide joint with the information
        :return: <bool> True for success.
        """

        # rename the joints
        for idx, guide_jnt in enumerate(self.guide_joints):
            # new_name = name_utils.get_guide_name("", name, self.suffix_name)
            new_name = guide_jnt.replace(self.name, name)
            object_utils.rename_node(guide_jnt, new_name)
            self.guide_joints[idx] = new_name
        self.name = name

        # rename the controllers
        # if self.built_groups:
        #     control_utils.rename_controls(self.built_groups[0], new_name=name)
        return True

    def set_locator_pivot_positions(self):
        """
        sets the positions
        :return: <bool> True for success.
        """
        if self.pivot_locators and "pivot_positions" in self.information:
            if self.information["pivot_positions"]:
                for jnt, pos in zip(self.guide_joints, self.information["pivot_positions"]):
                    object_utils.set_object_transform(jnt, m=pos, ws=True)
                return True
        return False

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
            for tup_jnts in self.guide_joints:
                tup_positions = ()
                for jnt in tup_jnts:
                    tup_positions += object_utils.get_object_transform(jnt, m=True),
                transforms += tup_positions,
            return transforms
        return ()

    def get_pivot_positions(self):
        """
        gets the current pivot locator positions.
        :return:
        """
        if self.pivot_locators:
            transforms = ()
            for piv_loc in self.pivot_locators:
                transforms += object_utils.get_object_transform(piv_loc, t=True),
            return transforms
        return ()

    def update(self, *args):
        """
        updates the module.
        :param args: <list> updates the guide joints. the first argument is the name.
        :return:
        """
        if args:
            name = args[0]
            self.rename(name)

        # updates the module information
        self.information["positions"] = self.get_guide_positions()
        self.information["pivot_positions"] = self.get_pivot_positions()
        self.information["name"] = self.name

        # updates the relationship information
        self.information["parentTo"] = self.PUBLISH_ATTRIBUTES['parentTo']
        self.information["constrainTo"] = self.PUBLISH_ATTRIBUTES['constrainTo']

    def remove(self):
        """
        removes the guide joints from the scene.
        :return: <bool> True for success.
        """
        if self.guide_joints:
            for jnt_array in self.guide_joints:
                object_utils.remove_node(jnt_array)
        if self.finished_joints:
            for jnt_array in self.finished_joints:
                object_utils.remove_node(jnt_array)
        if self.built_groups:
            object_utils.remove_node(self.built_groups[0])
        if self.pivot_locators:
            for loc in self.pivot_locators:
                object_utils.remove_node(loc)
        self.finished = False
        self.created = False

        # garbage collection

    def create(self):
        """
        creates a joint controlled by one joint.
        :return: <bool> True for success.
        """
        if self.created:
            return False

        # create the guide joints, collect the self.guide_joints class array.
        self.create_guides()

        # set the guide joint positions as directed from the stored JSON dictionary file.
        self.set_guide_positions()

        # create the locators
        self.create_locators_pivot_guides()

        self.created = True
        return True

    def create_controllers(self):
        """
        creates a controller object over the joint object.
        :return: <str> group name.
        """
        ctrl_data = ()
        for joint_name, name in zip(self.finished_joints, self.names):
            data = control_utils.create_controls(joint_name, name, shape_name=self.control_shape)

            # return data
            ctrl_data += data,

        object_utils.do_point_constraint(self.controller_names[-1], self.ik_handles[-1])
        object_utils.do_point_constraint(self.controller_names[:-2], self.ik_handles[:-2])

        self.controller_data = ctrl_data
        return ctrl_data

    def replace_guides(self):
        """
        replaces the guide joints with the actual bound joints.
        :return: <tuple> bound joint array.
        """
        if self.if_guides_exist():
            positions = self.get_guide_positions()
            self.finished_joints = ()

            for name, jnt_array, pos_array in zip(self.names, self.guide_joints, positions):
                # remove the existing guides
                object_utils.remove_node(jnt_array)

                # set the positions gathered from the guide joints
                self.finished_joints += joint_utils.create_joint(
                    name, num_joints=len(pos_array), prefix_name=self.prefix_name,
                    use_position=pos_array, bound_joint=True, as_strings=True),

                # parent the replaced joints
                if len(self.finished_joints) > 1:
                    object_utils.do_parent(self.finished_joints[-1], self.finished_joints[-2])

            # set the guide joints to zero
            self.guide_joints = []

    def get_bound_joint_name(self, name, num=1):
        """
        gets the bound joint name.
        :param name: <str>
        :param num: <int>
        :return: <str> bound joint name.
        """
        return joint_utils.get_joint_names(name, prefix_name=self.prefix_name, num_joints=num, bound_joint=True)[0]

    def if_guides_exist(self):
        """
        checking function to search the validity of guides in the scene.
        :return:
        """
        for tup_guides in self.guide_joints:
            if not all(map(object_utils.is_exists, tup_guides)):
                return False
        return True

    def select_guides(self):
        """
        select the guide joints
        :return: <bool> True for success.
        """
        if self.if_guides_exist:
            object_utils.select_object(self.guide_joints)
        return True

    def select_built_objects(self):
        """
        select the built objects
        :return: <bool> True for success.
        """
        if self.controller_data:
            object_utils.select_object(self.controller_data['group_names'][-1])

    def perform_parenting(self):
        """
        now parent the groups to their controllers.
        :return: <bool> True for success. <bool> False for failure.
        """
        for structure in self.parent_structure:
            object_utils.do_parent(structure[1], structure[0])
        return True

    def create_pivots(self):
        """
        gets the pivot positions.
        :return: <bool> True for success.
        """
        positions = self.get_pivot_positions()
        for pivot_name, position in zip(self.pivot_names, positions):
            # sets the position array to this pivot node.
            object_utils.create_group(pivot_name, position=position)

        # remove the guide pivots
        if self.pivot_locators:
            for piv_loc in self.pivot_locators:
                object_utils.remove_node(piv_loc)
            self.pivot_locators = ()
        return True

    def create_ik(self):
        """
        creates the ik system for the foot pivots
        :return: <tuple> ik handles
        """
        ik_handles = ()
        for ik_name, bone_array in self.ik_handles_structure.items():
            ik_handles += joint_utils.create_ik_handle(
                bone_array, name=ik_name, sticky="sticky", solver="ikSCsolver")
        return ik_handles

    def finish(self):
        """
        finish the construction of this module.
        :return: <bool> True for success.
        """
        if self.finished:
            return False

        # populate the finished joints using the positions of the guide joints
        self.replace_guides()

        # reorient joints
        joint_utils.orient_joints(self.finished_joints, primary_axis=self.information["forwardAxis"])

        # create the ik handles
        self.create_ik()

        # creates the controller object on the bound joint and do necessary parenting.
        self.create_controllers()

        # create the pivot setup
        self.create_pivots()

        # create parenting structure
        self.perform_parenting()

        # create connections to other nodes in the scene
        self.perform_connections()

        # store this information
        # for ctrl_data in controllers:
        #     self.built_groups.extend(ctrl_data[0]['group_names'])
        print("[{}] :: finished.".format(self.name))
        self.finished = True
        return True
