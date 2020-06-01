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
# define module variables
class_name = "Hand"


class Hand(template.TemplateModule):
    class_name = class_name
    class_name = class_name

    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",
                          "name": "",
                          "moduleType": "",
                          "positions": ()
                          }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo", "constrainTo", "positions", "numberOfJoints"],
                            'label': ["moduleType"]
                            }

    def __init__(self, name="", control_shape="cube", prefix_name="", information={}):
        super(Hand, self).__init__(name=name, prefix_name=prefix_name, information=information)

        # for whatever reason this doesn't work
        self.information = information
        self.update_information(information)
        self.number_of_joints = 4

        self.names = (self.name,
                      self.name + '_middle',
                      self.name + '_index',
                      self.name + '_thumb',
                      self.name + '_ring',
                      self.name + '_pinky')

        self.joints_num = (1,
                           self.number_of_joints,
                           self.number_of_joints,
                           self.number_of_joints - 1,
                           self.number_of_joints,
                           self.number_of_joints)

        self.add_new_information('numberOfJoints', value=self.number_of_joints)

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

    def create_guides(self):
        """
        creates a guide joint object.
        :return: <str> joint object name.
        """
        self.guide_joints = ()

        # get the positions for the middle joint
        hand_position = joint_utils.get_joint_positions(self.number_of_joints)
        mid_positions = joint_utils.get_joint_positions(self.number_of_joints, z=1.0)
        indx_positions = joint_utils.get_joint_positions(self.number_of_joints, x=1.0, z=1.0)
        thumb_positions = joint_utils.get_joint_positions(self.number_of_joints, x=2.0, z=1.0)
        ring_positions = joint_utils.get_joint_positions(self.number_of_joints, x=-1.0, z=1.0)
        pinky_positions = joint_utils.get_joint_positions(self.number_of_joints, x=-2.0, z=1.0)

        positions = (hand_position, mid_positions, indx_positions, thumb_positions, ring_positions, pinky_positions)

        # create the hand joint
        for name, jnt_num, pos in zip(self.names, self.joints_num, positions):
            self.guide_joints += joint_utils.create_joint(
                num_joints=jnt_num, name=name, guide_joint=True,
                prefix_name=self.prefix_name, as_strings=True, use_position=pos),

        for idx in xrange(1, len(self.guide_joints)):
            object_utils.do_parent(self.guide_joints[idx][0], self.guide_joints[0][0])

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

        self.created = True
        return True

    def create_controllers(self):
        """
        creates a controller object over the joint object.
        :return: <str> group name.
        """
        ctrl_data = ()
        for name, obj_array in zip(self.names, self.finished_joints):
            data = control_utils.create_controllers_with_standard_constraints(
                name, objects_array=obj_array, shape_name=self.control_shape)

            if "_" not in name:
                self.controller_data = data

            # parent everything else to the hand controller
            if name == self.name:
                par_obj = data[0]["controller"]
            else:
                object_utils.do_parent(data[0]["group_names"][0], par_obj)

            # perform the FK parenting
            self.perform_parenting(data)

            # return data
            ctrl_data += data,
        return ctrl_data

    def replace_guides(self):
        """
        replaces the guide joints with the actual bound joints.
        :return: <tuple> bound joint array.
        """
        if self.if_guides_exist():
            positions = self.get_guide_positions()
            self.finished_joints = ()

            # remove the existing guides
            for name, jnt_array, pos_array in zip(self.names, self.guide_joints, positions):
                object_utils.remove_node(jnt_array)
                # set the positions gathered from the guide joints
                self.finished_joints += joint_utils.create_joint(
                    name, num_joints=len(pos_array), prefix_name=self.prefix_name,
                    use_position=pos_array, bound_joint=True, as_strings=True),

            # set the guide joints to zero
            self.guide_joints = []

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

    def perform_parenting(self, controller_data):
        """
        now parent the groups to their controllers.
        :return: <bool> True for success. <bool> False for failure.
        """
        max_len = len(controller_data) - 1
        for idx in xrange(max_len):
            if idx + 1 <= max_len:
                c_data = controller_data[max_len - idx]
                next_data = controller_data[(max_len - idx) - 1]
                object_utils.do_parent(c_data["group_names"][0], next_data["controller"])
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

        # creates the controller object on the bound joint and do necessary parenting.
        controllers = self.create_controllers()

        # create connections to other nodes in the scene
        self.perform_connections()

        # store this information
        for ctrl_data in controllers:
            self.built_groups.extend(ctrl_data[0]['group_names'])
        print("[{}] :: finished.".format(self.name))
        self.finished = True
        return True
