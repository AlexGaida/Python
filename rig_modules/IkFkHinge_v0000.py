"""
Singleton method to creating a single joint in the scene.
"""
# import standard modules
from pprint import pprint

# import local modules
from rig_utils import control_utils
from maya_utils import transform_utils
from maya_utils import attribute_utils
from maya_utils import math_utils
from rig_utils import joint_utils
from rig_modules import template
from maya_utils import object_utils

# reloads
# reload(template)

# define module variables
# define module variables
class_name = "IkFkHinge"


class IkFkHinge(template.TemplateModule):
    class_name = class_name
    class_name = class_name

    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",
                          "name": "",
                          "moduleType": "",
                          "positions": ()
                          }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo", "constrainTo", "positions", "forwardAxis"],
                            'label': ["moduleType"]
                            }

    def __init__(self, name="", control_shape="cube", prefix_name="", information={}):
        super(IkFkHinge, self).__init__(name=name, prefix_name=prefix_name, information=information)

        # for whatever reason this doesn't work
        self.information = information
        self.update_information(information)
        self.guide_positions = ()

        self.names = (name + '_upper',
                      name + '_elbow',
                      name + '_wrist')

        self.add_new_information('forwardAxis', value='x')

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

    def create_guides(self):
        """
        creates a guide joint object.
        :return: <str> bool.
        """
        self.guide_joints = ()

        # get the positions for the middle joint
        positions = ([0.0, 0.0, 0.0], [2.0, 0.0, -1.0], [4.0, 0.0, 0.0])

        # create the hand joint
        idx = 0
        for name, pos in zip(self.names, positions):
            # create the guide joints
            self.guide_joints += joint_utils.create_joint(
                num_joints=1, name=name, guide_joint=True,
                prefix_name=self.prefix_name, as_strings=True, use_position=pos)[0],

            if len(self.guide_joints) > 1:
                # parent the guide joints
                object_utils.do_parent(self.guide_joints[idx], self.guide_joints[idx - 1])
            idx += 1
        joint_utils.orient_joints(self.guide_joints, primary_axis=self.forward_axis)
        joint_utils.zero_joint_orient(self.guide_joints[-1])

    def rename(self, name):
        """
        updates the guide joint with the information
        :return: <bool> True for success.
        """

        # rename the joints
        new_joints = ()
        for idx, guide_jnt in enumerate(self.guide_joints):
            # new_name = name_utils.get_guide_name("", name, self.suffix_name)
            new_name = guide_jnt.replace(self.name, name)
            object_utils.rename_node(guide_jnt, new_name)
            new_joints += new_name,
        self.guide_joints = new_joints
        self.name = name
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
            for jnt in self.finished_joints:
                object_utils.remove_node(jnt)
        if self.built_groups:
            for k in self.built_groups:
                print(k)
                if isinstance(k, dict):
                    object_utils.remove_node(k['group_names'][0])
                elif isinstance(k, (str, unicode)):
                    object_utils.remove_node(k)
                elif isinstance(k, (list, tuple)):
                    object_utils.remove_node(k)
                else:
                    object_utils.remove_node(k)

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

    def create_controllers(self, joints_array):
        """
        creates a controller object over the joint object.
        :return: <str> group name.
        """
        ctrl_data = ()
        # create the controller data
        for name, obj_array in zip(self.names, joints_array):
            ctrl_data += control_utils.create_controllers_with_standard_constraints(
                name, objects_array=obj_array, shape_name=self.control_shape),
        # perform the FK parenting
        self.perform_parenting(ctrl_data)
        return ctrl_data

    def create_joints(self, positions, suffix="bnd"):
        """
        create bind joints at positions.
        :param positions: <tuple> positions array.
        :param suffix: <str> suffix name.
        :return: <tuple> bind joints
        """
        bind_joints = ()
        # create the arm joint
        idx = 0
        for name, pos in zip(self.names, positions):
            bind_joints += joint_utils.create_joint(
                num_joints=1, name=name, suffix_name=suffix,
                prefix_name=self.prefix_name, as_strings=True, use_position=pos)[0],

            if len(bind_joints) > 1:
                # parent the guide joints
                object_utils.do_parent(bind_joints[idx], bind_joints[idx - 1])

            # we must freeze the rotational transformations for the ik handle to work properly.
            joint_utils.freeze_transformations(bind_joints[idx], rotate=True, translate=False, scale=False)
            # if len(positions) - 1 == idx:
            #     joint_utils.zero_joint_orient(bind_joints[-1])
            idx += 1
        return bind_joints

    def replace_guides(self):
        """
        replaces the guide joints with the actual bound joints.
        :return: <tuple> bound joint array.
        """
        if self.if_guides_exist():
            self.guide_positions = self.get_guide_positions()
            self.finished_joints = ()

            # create the joints for this module
            bind_joints = self.create_joints(self.guide_positions, suffix="bnd")
            fk_joints = self.create_joints(self.guide_positions, suffix="fk")
            ik_joints = self.create_joints(self.guide_positions, suffix="ik")

            # remove the existing guide joints
            object_utils.remove_node(self.guide_joints)

            self.finished_joints += bind_joints
            self.finished_joints += fk_joints
            self.finished_joints += ik_joints

            # set the guide joints to zero
            self.guide_joints = []
            return bind_joints, fk_joints, ik_joints

    def if_guides_exist(self):
        """
        checking function to search the validity of guides in the scene.
        :return:
        """
        if not all(map(object_utils.is_exists, self.guide_joints)):
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

    @staticmethod
    def perform_parenting(controller_data):
        """
        now parent the groups to their controllers.
        :return: <bool> True for success. <bool> False for failure.
        """
        max_len = len(controller_data) - 1
        for idx in xrange(max_len):
            # data = {'controller': u'FkChain_0_0_ctrl', 'group_names': ('FkChain_0_0_ctrl_grp', 'FkChain_0_0_ctrl_cnst')
            if idx + 1 <= max_len:
                c_data = controller_data[max_len - idx]
                next_data = controller_data[(max_len - idx) - 1]
                object_utils.do_parent(c_data[0]["group_names"], next_data[0]["controller"])
        return True

    @staticmethod
    def get_control_top_group(control_dict):
        """
        utility function to get the top group from controller dictionary variable.
        :param control_dict:
        :return: <str> top group name.
        """
        if isinstance(control_dict, (list, tuple)):
            try:
                return control_dict[0]['group_names'][0]
            except TypeError:
                return control_dict[0][0]['group_names'][0]
        return control_dict['group_names'][0]

    @staticmethod
    def get_controller_name(control_dict):
        """
        utility function to get the controller dictionary.
        :param control_dict: <dict>
        :return: <str> controller name.
        """
        if isinstance(control_dict, (list, tuple)):
            try:
                return control_dict[0]['controller']
            except TypeError:
                return control_dict['controller']
        return control_dict['controller']

    @staticmethod
    def get_ikfk_attrs(object_name):
        """
        get the custom attributes
        :param object_name:
        :return:
        """
        attrs_list = attribute_utils.get_custom_attributes(object_name, full_name=True)
        attributes = {'ik': '',
                      'fk': ''}
        for a in attrs_list:
            if "_ik_" in a.lower():
                attributes['ik'] = a
            if "_fk_" in a.lower():
                attributes['fk'] = a
        return attributes

    def make_arm_stretchy(self):
        """
        creates additional utility nodes to make a stretchy arm.
        :return: <bool> True for success.
        """
        return True

    def create_pole_vector_controller(self, ik_joints, ik_handle):
        """
        creates a pole vector for the Ik Handle
        :param ik_joints:
        :param ik_handle:
        :return:
        """
        ik_pole_vector = control_utils.create_control(shape_name='sphere', name=self.name + '_ik_pole_vector_ctrl')
        position = math_utils.get_pole_vector_position(*ik_joints)
        transform_utils.match_position_transform(self.get_control_top_group(ik_pole_vector), position)
        object_utils.do_pole_vector_constraint(self.get_controller_name(ik_pole_vector), ik_handle)
        return ik_pole_vector

    def create_arm_system(self, bind_joints, fk_joints, ik_joints):
        """
        creates the ik fk blending system.
        :param bind_joints: <tuple> bind joints array.
        :param fk_joints: <tuple> fk joints array.
        :param ik_joints: <tuple> ik joints array.
        :return: <dict> controller date information.
        """
        controller_data = {}

        # creates the ik system for the ik joints
        # print ik_joints
        ik_handle = joint_utils.create_ik_handle(ik_joints, name=self.name + '_ik')
        self.built_groups.append(ik_handle[0])

        controller_data['pole_vector_ctrl'] = self.create_pole_vector_controller(ik_joints, ik_handle[0])

        # create the controller to manage the ik_fk switching
        ik_fk_ctrl = control_utils.create_control(shape_name='locator', name=self.name + '_ikfk')
        ik_fk_ctrl_attr = object_utils.attr_add_float(ik_fk_ctrl['controller'], 'ikfk', min_value=0.0, max_value=1.0)
        transform_utils.match_position_transform(self.get_control_top_group(ik_fk_ctrl), ik_joints[-1])

        blend_node = object_utils.create_node(node_type='blendColors', node_name=self.name + "_blend")
        self.built_groups.append(blend_node)
        object_utils.do_connections(ik_fk_ctrl_attr, blend_node + '.blender')
        object_utils.do_set_attr(blend_node + '.color2R', 0.0)
        object_utils.do_set_attr(blend_node + '.color1R', 1.0)
        object_utils.do_set_attr(blend_node + '.color1G', 0.0)
        object_utils.do_set_attr(blend_node + '.color2G', 1.0)
        controller_data["ikfk_controller"] = ik_fk_ctrl

        # creates the parent constraints and setup the switching system
        for bnd_jnt, fk_jnt, ik_jnt in zip(bind_joints, fk_joints, ik_joints):
            # connect the blend color controller to the constraint group
            parent_cnst = object_utils.do_parent_constraint((ik_jnt, fk_jnt), bnd_jnt)
            attrs = self.get_ikfk_attrs(parent_cnst)
            status = object_utils.do_connections(blend_node + '.outputR', attrs["ik"])
            if not status:
                raise RuntimeError("[Arm] :: Connection failure: {}.".format(blend_node))
            status = object_utils.do_connections(blend_node + '.outputG', attrs["fk"])
            if not status:
                raise RuntimeError("[Arm] :: Connection failure: {}.".format(blend_node))

        # constrain the control node, the ik and fk joints are stored as the last ones in list
        control_cnst = object_utils.do_parent_constraint((ik_jnt, fk_jnt),
                                                         ik_fk_ctrl["group_names"][0],
                                                         maintain_offset=False)
        attrs = self.get_ikfk_attrs(control_cnst)
        status = object_utils.do_connections(blend_node + '.outputR', attrs["ik"])
        if not status:
            raise RuntimeError("[Arm] :: Connection failure: {}.".format(blend_node))
        status = object_utils.do_connections(blend_node + '.outputG', attrs["fk"])
        if not status:
            raise RuntimeError("[Arm] :: Connection failure: {}.".format(blend_node))

        # create the controllers for the Ik system
        wrist_ik_ctrl = control_utils.create_control(shape_name='sphere', name=self.name + '_wrist_ik')
        transform_utils.match_matrix_transform(self.get_control_top_group(wrist_ik_ctrl), ik_joints[-1])
        object_utils.do_point_constraint(wrist_ik_ctrl['controller'], ik_handle[0])
        controller_data["ik_wrist_controller"] = wrist_ik_ctrl

        upper_ik_ctrl = control_utils.create_control(shape_name='sphere', name=self.name + '_upper_ik')
        transform_utils.match_matrix_transform(self.get_control_top_group(upper_ik_ctrl), ik_joints[0])
        object_utils.do_point_constraint(upper_ik_ctrl['controller'], ik_joints[0])
        controller_data["ik_upper_controller"] = upper_ik_ctrl

        # create the controllers for the Fk system
        controller_data["fk_controller"] = self.create_controllers(fk_joints)

        # organize the control systems
        control_grp = object_utils.create_node('transform', node_name=self.name + '_controllers_grp')
        for k_name in controller_data:
            top_grp = self.get_control_top_group(controller_data[k_name])
            object_utils.do_parent(top_grp, control_grp)

        # organize the systems nodes
        systems_grp = object_utils.create_node('transform', node_name=self.name + '_systems_grp')
        object_utils.do_parent(ik_handle[0], systems_grp)
        object_utils.do_parent(bind_joints[0], systems_grp)
        object_utils.do_parent(fk_joints[0], systems_grp)
        object_utils.do_parent(ik_joints[0], systems_grp)

        # now create a master controller for this arm system
        master_ctrl = control_utils.create_control(shape_name='locator', name=self.name + '_plug')
        object_utils.do_parent_constraint(master_ctrl["controller"], systems_grp, maintain_offset=True)
        object_utils.do_scale_constraint(master_ctrl["controller"], systems_grp, maintain_offset=True)
        object_utils.do_parent_constraint(master_ctrl["controller"], control_grp, maintain_offset=True)
        object_utils.do_scale_constraint(master_ctrl["controller"], control_grp, maintain_offset=True)

        # now make the arm stretchy
        self.make_arm_stretchy()

        # store the master controller as part of the main controller data
        self.controller_data = master_ctrl
        self.built_groups.append(controller_data)
        return controller_data

    def finish(self):
        """
        finish the construction of this module.
        :return: <bool> True for success.
        """
        if self.finished:
            return False

        # populate the finished joints using the positions of the guide joints
        bind_joints, fk_joints, ik_joints = self.replace_guides()

        # create the arm system
        self.create_arm_system(bind_joints, fk_joints, ik_joints)

        # create connections to other nodes in the scene
        print('connections: ', self.controller_data)
        self.perform_connections()

        # store this information
        self.built_groups.extend(self.controller_data['group_names'])
        print("[{}] :: finished.".format(self.name))
        self.finished = True
        return True
