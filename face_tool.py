"""
Face tool for loading and connecting the set driven key face utilities.
There must be face_[attribute] attributes on the controlling node!
Goal:
    Select controller, select object and set the driven keyframes.
Versions:
    1.0.0: Initial working release.
"""
# import standard modules
from pprint import pprint
import re

# import maya modules
from maya import cmds

# import local modules
import read_sides
from maya_utils import attribute_utils
from maya_utils import animation_utils
from maya_utils import transform_utils
from maya_utils import object_utils
from maya_utils import math_utils
from maya_utils import ui_utils

# reload modules
reload(attribute_utils)
reload(transform_utils)
reload(animation_utils)
reload(object_utils)
reload(math_utils)

# define global variables
__version__ = "1.0.0"
__verbosity__ = 0
_cls_mirror = read_sides.MirrorSides()
__default_attribute_values = attribute_utils.Attributes.DEFAULT_ATTR_VALUES
_k_transform = object_utils.om.MFn.kTransform
_k_locator = object_utils.om.MFn.kLocator
__interface_ctrls = []
__on_face_ctrls = []

if not cmds.objExists('on_face_control_grp'):
    cmds.warning("[ObjectDoesNotExist] :: on_face_control_grp")


def verbose(message=""):
    if __verbosity__:
        print(message)


def delete_keys_on_selected():
    s_ctrls = object_utils.get_selected_node(single=False)
    selected_ctrls = s_ctrls[:-1]
    interface_ctrl = s_ctrls[-1]
    print(selected_ctrls, interface_ctrl)
    for c_ctrl in selected_ctrls:
        delete_keys_on_controller(c_ctrl, interface_ctrl)
    return True


def inspect_interface_attributes():
    """
    prints the selected controller attributes.
    :return: <bool> True for success.
    """
    s_ctrls = object_utils.get_selected_node(single=False)
    for f_ctrl in s_ctrls:
        face_loc = find_face_system_controller(f_ctrl)
        attr = attribute_utils.Attributes(face_loc[0], custom=1, keyable=True)
        print(f_ctrl, ">>", attr.__dict__())
    return True


def get_face_attributes(object_node="", non_zero=False):
    """
    gets the face attributes from the controller specified.
    if there are no face attributes, list all keyable attributes.
    :param object_node: <str> maya object node.
    :param non_zero: <bool> get non zero face attributes.
    :return: <list> face attributes.
    """
    if not object_node:
        object_node = object_utils.get_selected_node()
    if isinstance(object_node, (list, tuple)):
        object_node = object_node[0]
    attrs = attribute_utils.Attributes(object_node, custom=True)
    a_data = {}
    if attrs:
        if non_zero:
            a_data = attrs.non_zero_attributes().items()
        else:
            a_data = attrs.items()
    return dict(filter(lambda a: a[0].startswith('face_'), a_data))


def get_offset_scale_attr(scale_attr=""):
    """
    utility node for getting the offset scale attribute name.
    :param scale_attr: <str> scale name attribute.
    :return: <str> offset scale attribute. <bool> False for failure.
    """
    if 'scaleX' in scale_attr:
        return 'offset_scaleX'
    if 'scaleY' in scale_attr:
        return 'offset_scaleY'
    if 'scaleZ' in scale_attr:
        return 'offset_scaleZ'
    return False


def setup_scale(controller_node="", scale_attr=""):
    """
    sets up the scale system for blend weighted node.
    :param controller_node: <str> driver node.
    :param scale_attr: the scale attribute to connect to.
    :return: <str> Plus minus average node. <bool> False for failure.
    """
    if not scale_attr:
        scale_attr = ['scaleX', 'scaleY', 'scaleZ']

    avg_node_name = controller_node + '_scale_offset'
    offset_x = 'offset_scaleX'
    offset_y = 'offset_scaleY'
    offset_z = 'offset_scaleZ'

    control_offset_x = '{}.{}'.format(controller_node, offset_x)
    control_offset_y = '{}.{}'.format(controller_node, offset_y)
    control_offset_z = '{}.{}'.format(controller_node, offset_z)

    if not cmds.ls(control_offset_x):
        cmds.addAttr(controller_node, ln=offset_x, at='float', k=1)

    if not cmds.ls(control_offset_y):
        cmds.addAttr(controller_node, ln=offset_y, at='float', k=1)

    if not cmds.ls(control_offset_z):
        cmds.addAttr(controller_node, ln=offset_z, at='float', k=1)

    if not cmds.objExists(avg_node_name):
        cmds.createNode('plusMinusAverage', name=avg_node_name)
        cmds.setAttr(avg_node_name + '.input3D[0].input3Dx', 1)
        cmds.setAttr(avg_node_name + '.input3D[0].input3Dy', 1)
        cmds.setAttr(avg_node_name + '.input3D[0].input3Dz', 1)

        cmds.setAttr(avg_node_name + '.input3D[1].input3Dx', 0)
        cmds.setAttr(avg_node_name + '.input3D[1].input3Dy', 0)
        cmds.setAttr(avg_node_name + '.input3D[1].input3Dz', 0)

    if 'scaleX' in scale_attr:
        avg_input_x_attr = avg_node_name + '.input3D[1].input3Dx'
        if not cmds.isConnected(control_offset_x, avg_input_x_attr):
            cmds.setAttr(avg_node_name + '.input3D[1].input3Dx', 0)
            cmds.connectAttr(control_offset_x, avg_input_x_attr)

    if 'scaleY' in scale_attr:
        avg_input_y_attr = avg_node_name + '.input3D[1].input3Dy'
        if not cmds.isConnected(control_offset_y, avg_input_y_attr):
            cmds.setAttr(avg_node_name + '.input3D[1].input3Dy', 0)
            cmds.connectAttr(control_offset_y, avg_input_y_attr)

    if 'scaleZ' in scale_attr:
        avg_input_z_attr = avg_node_name + '.input3D[1].input3Dz'
        if not cmds.isConnected(control_offset_z, avg_input_z_attr):
            cmds.setAttr(avg_node_name + '.input3D[1].input3Dz', 0)
            cmds.connectAttr(control_offset_z, avg_input_z_attr)

    if 'scaleX' in scale_attr:
        o_attr = avg_node_name + '.output3D.output3Dx'
        i_attr = controller_node + '.scaleX'
        if not cmds.isConnected(o_attr, i_attr):
            cmds.connectAttr(o_attr, i_attr)

    if 'scaleY' in scale_attr:
        o_attr = avg_node_name + '.output3D.output3Dy'
        i_attr = controller_node + '.scaleY'
        if not cmds.isConnected(o_attr, i_attr):
            cmds.connectAttr(o_attr, i_attr)

    if 'scaleZ' in scale_attr:
        o_attr = avg_node_name + '.output3D.output3Dz'
        i_attr = controller_node + '.scaleZ'
        if not cmds.isConnected(o_attr, i_attr):
            cmds.connectAttr(o_attr, i_attr)


def __set_key(controller_node, driven_node, driven_attr, face_attr, driven_value, driver_value):
    """
    private utility function for setting keys.
    :param controller_node:
    :param driven_node:
    :param driven_attr:
    :param face_attr:
    :return: <bool> True for success. <bool> False for failure.
    """
    # else use the standard attribute given
    return animation_utils.set_driven_key(
        driver_node=controller_node, driver_attr=face_attr,
        driven_node=driven_node, driven_attr=driven_attr,
        driven_value=driven_value, driver_value=driver_value
    )


def delete_keys(object_node=""):
    """
    Removes all keys from selected.
    :return: <bool> True for success.
    """
    anim_nodes = object_utils.get_m_anim_from_sel(object_node=object_node)
    cmds.delete(anim_nodes.keys())
    return True


def flatten_keys(object_node=None):
    """
    flatten the key frame values.
    :param object_node: <str> maya object node.
    :return: <bool> True for success.
    """
    anim_data = animation_utils.get_anim_data(object_node=object_node)
    animation_utils.set_anim_data(anim_data=anim_data, rounded=True)
    return True


def find_face_system_controller(object_node=""):
    """
    finds the interface locator controller from the control gui
    :return: <str> face system controller name.
    """
    if not object_node:
        object_node = object_utils.get_selected_node()
    if not object_node:
        raise ValueError("[FindFaceSystemController] :: no valid object parameter given.")

    return object_utils.get_connected_nodes(object_node,
                                            find_node_type=_k_transform,
                                            find_attr="face_",
                                            as_strings=True,
                                            with_shape=_k_locator)


def find_face_controls(interface=False, on_face=False):
    """
    find the facial interface controller objects in the scene.
    :return: <list> face controllers. <bool> False for failure.
    """
    if not interface and not on_face:
        raise ValueError("[FindFaceControls] :: Please specify boolean parameters for interface or on_face.")

    face_controls = cmds.ls('face_*', type='transform') + cmds.ls('*:face_*', type='transform')
    if __verbosity__:
        print("interface controllers have been identified.")
    if not face_controls:
        return ValueError("[FindFaceControls] :: No face controllers have been found.")

    if interface:
        return filter(lambda face_ctrl: find_face_system_controller(face_ctrl), face_controls)

    if on_face:
        return object_utils.get_transform_relatives(object_name='on_face_control_grp',
                                                    find_child='_ctrl',
                                                    with_shape='nurbsCurve')
    return False


def _get_interface_grp_name(interface_name=None):
    """
    get the interface group name.
    :param interface_name: <str>, <list> interface name from the gui.
    :return: <str> group name.
    """
    if isinstance(interface_name, (str, unicode)):
        nice_name = object_utils.get_nice_name(interface_name)
    if isinstance(interface_name, (list, tuple)):
        nice_name = object_utils.get_nice_name('_'.join(interface_name))
    return '{}_driver_grp'.format(nice_name)


def _make_driver_grp_from_interface(selected_on_face_ctrl='', interface_name=''):
    """
    makes the driver groups on the selected face controller if they do not exist.
    :param selected_on_face_ctrl: <str>
    :param interface_name: <str>
    :return: <str> grp name.
    """
    grp_name = _get_interface_grp_name([selected_on_face_ctrl, interface_name])
    return object_utils.insert_transform(selected_on_face_ctrl, name=grp_name)


def create_face_driver_grps():
    """
    create face driver groups for the on-face controllers.
    :return: <bool> True for success.
    """
    global __interface_ctrls
    global __on_face_ctrls

    # get the controllers on the interface
    if not __interface_ctrls:
        __interface_ctrls = find_face_controls(interface=True)

    # find the controllers on the face
    __on_face_ctrls = find_face_controls(on_face=True)

    # create interface control group
    for on_face_ctrl in __on_face_ctrls:
        # zero out the attributes on the face controllers first.
        attrs = attribute_utils.Attributes(on_face_ctrl, keyable=True)
        if attrs.non_zero_attributes():
            attrs.zero_attributes()

        # then build the parent transforms
        for interface_name in __interface_ctrls:
            driver_grp = _make_driver_grp_from_interface(on_face_ctrl, interface_name)
            # create the offset scale attribute for easier setting set driven keys on scale attributes
            setup_scale(driver_grp)
    return True


def check_non_zero(control_name=''):
    """
    check if the controller has non zero values.
    :param control_name: <str> controller name.
    :return: <bool> True for success. <bool> False for failure.
    """
    interface_attrs = attribute_utils.Attributes(control_name, keyable=True)
    interface_non_zero = interface_attrs.non_zero_attributes()
    if interface_non_zero:
        return True
    return False


def apply_key_on_face_control(selected_on_face_ctrl='', interface_ctrl=""):
    """
    apply a set driven key frame belonging to this face controller.
    will look for any transformation values for each interface controller.
    :return: <bool> True for success.
    """
    global __interface_ctrls

    if not selected_on_face_ctrl:
        return ValueError("[ApplyKeyOnFaceControl] :: selected_on_face_ctrl parameter is empty.")

    on_face_attrs = attribute_utils.Attributes(selected_on_face_ctrl, keyable=True)

    if not __interface_ctrls:
        if __verbosity__:
            print("interface controllers have been identified.")
        __interface_ctrls = find_face_controls(interface=True)

    # iterate through the interface controllers and apply key on any non-zero keys.
    # filter the list for any controller with non zero keys
    if not interface_ctrl:
        interface_controllers = filter(check_non_zero, __interface_ctrls)
    else:
        interface_controllers = [interface_ctrl]

    for interface_ctrl in interface_controllers:
        # grab the driven object name
        driven_object = _get_interface_grp_name([selected_on_face_ctrl, interface_ctrl])

        # get the attributes on the driven object
        drn_attr = attribute_utils.Attributes(driven_object, keyable=True)
        drn_custom_attr = attribute_utils.Attributes(driven_object, custom=True)

        # check for non-zero attributes on the interface controllers
        interface_attrs = attribute_utils.Attributes(interface_ctrl, keyable=True)
        interface_non_zero = interface_attrs.non_zero_attributes()
        if __verbosity__:
            print("[ApplyKeyOnFace] :: Driver: {}, {};\nDriven: {};".format(
                interface_ctrl, interface_non_zero, driven_object))

        # copy the attributes from the on-face control to the driver group node
        drn_attr.copy_attr(on_face_attrs, match_world_space=True)

        # copy the scale attributes to the custom scale attribute
        for s_attr, s_val in on_face_attrs.scale_attr().items():
            for c_attr in drn_custom_attr:
                if s_attr in c_attr:
                    scale_value = round(s_val + -1.0, 4)
                    cmds.setAttr('{}.{}'.format(driven_object, c_attr), scale_value)

        # zero out the driver attribute
        on_face_attrs.zero_attributes()

        # set the key on that driven group object
        set_keys_on_face_controller(selected_node=selected_on_face_ctrl,
                                    interface_ctrl=interface_ctrl,
                                    driven_node=driven_object)
    return True


def set_default_key_values(selected_on_face_ctrl="", interface_ctrl="", attr_name="", driver_value=0.0):
    """
    Set the default value keys.
    :param selected_on_face_ctrl: <str>
    :param interface_ctrl: <str>
    :param driver_value: <float>
    :param attr_name: <str>
    :return: <bool> for success.
    """
    if not selected_on_face_ctrl:
        raise ValueError("[SetDefaultKeyValues] :: selected_on_face_ctrl <str>, parameter not filled.")

    if not interface_ctrl:
        raise ValueError("[SetDefaultKeyValues] :: interface_ctrl <str>, parameter not filled.")

    # get the driver locator
    face_locator_node = find_face_system_controller(interface_ctrl)[0]

    # grab the driven object name
    driven_object = _get_interface_grp_name([selected_on_face_ctrl, interface_ctrl])

    # get the attributes on the driven object
    on_face_attr = attribute_utils.Attributes(selected_on_face_ctrl, keyable=True)

    # get the attributes on the driven object
    drn_attr = attribute_utils.Attributes(driven_object, keyable=True)

    # get the attributes on the driven object
    interface_attrs = attribute_utils.Attributes(face_locator_node, custom=True, keyable=True)

    # zero out the driven, controller and the on-face object
    drn_attr.zero_attributes()
    interface_attrs.zero_attributes()
    on_face_attr.zero_attributes()

    # set the key on default values on that driven group object
    for face_attr, face_val in interface_attrs.items():
        for driven_attr, driven_val in drn_attr.items():
            if attr_name:
                if attr_name not in driven_attr:
                    continue
            if 'scale' in driven_attr:
                driven_attr = get_offset_scale_attr(driven_attr)
            else:
                default_val = __default_attribute_values[driven_attr]

            animation_utils.set_driven_key(
                driver_node=face_locator_node, driver_attr=face_attr,
                driven_node=driven_object, driven_attr=driven_attr,
                driven_value=default_val, driver_value=driver_value
            )

    # reset the values on the driven, controller and the on-face object
    drn_attr.set_current_value()
    interface_attrs.set_current_value()
    on_face_attr.set_current_value()
    return True


def set_keys_on_face_controller(selected_node='', interface_ctrl="", driven_node=""):
    """
    Identify the selected face controller and set the driven key.
    :param selected_node: <str> selected node to get attributes from.
    :param interface_ctrl: <str> the controller maya object node which has the custom face_attributes.
    :param driven_node: <str> the driven maya object node.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not driven_node:
        driven_node = object_utils.get_selected_node()
    if not interface_ctrl:
        raise ValueError("[SetFaceKey :: parameter controller_node is empty.]")

    # grab the driven object name
    driven_object = _get_interface_grp_name([selected_node, interface_ctrl])
    interface_node = find_face_system_controller(interface_ctrl)[0]

    # get the attributes
    driven_attr_cls = attribute_utils.Attributes(driven_object, keyable=1)
    face_attrs = get_face_attributes(interface_node, non_zero=True)
    driven_attrs = driven_attr_cls.non_zero_attributes()

    if not face_attrs:
        raise RuntimeError("[SetKeysOnFaceControllerError] :: Cannot set key to this controller.")

    # set the key on the controller and the driven
    for face_attr, face_value in face_attrs.items():
        for driven_attr, driven_val in driven_attrs.items():
            # change the scale attribute
            if 'scale' in driven_attr:
                driven_attr = get_offset_scale_attr(driven_attr)
                driven_val += -1

            # set the key at the current space location
            face_value = math_utils.round_to_step(face_value)
            __set_key(interface_node, driven_node, driven_attr, face_attr, driven_val, face_value)
    return True


def set_key_on_selected():
    """
    set the driven keys on selected controller.
    :return: <bool> True for success.
    """
    get_selection = object_utils.get_selected_node(single=0)
    if not get_selection:
        return False
    for f_ctrl in get_selection:
        print(f_ctrl)
        apply_key_on_face_control(f_ctrl)
    return True


def set_key_default_on_selected(create_driver_groups=False):
    """
    set the default keys on selected.
    !!Important: Select the driver interface controller last!
    :return: <bool> True for success, <bool> False for failure.
    """
    # setup the driver nodes
    if create_driver_groups:
        create_face_driver_grps()

    # add default keys
    get_selection = object_utils.get_selected_node(single=0)
    if not get_selection:
        ui_utils.MessageBox("Please select the driven controllers first, then the interface controller!")
        return False
    on_face_ctrl = get_selection[:-1]
    interface_ctrl = get_selection[-1]
    for f_ctrl in on_face_ctrl:
        print("[SetDefaultKeyOnSelected] :: Setting defaults on, {}.".format(f_ctrl))
        set_default_key_values(f_ctrl, interface_ctrl)
    return True


def create_mouth_constraint(head_ctrl="c_head_ctrl", jaw_ctrl="on_face_c_jaw_ctrl"):
    """
    builds the mouth constraint system with percentages.
    :param head_ctrl: <str> the head control to source constraints.
    :param jaw_ctrl: <str> the jaw control to source constraints.
    :return: <bool> True for success.
    """
    selected_objects = object_utils.get_selected_node(single=False)
    if not selected_objects:
        raise RuntimeError("[CreateMouthConstraintError] :: Please select mouth control objects to constrain.")
    for ctrl in selected_objects:
        control_grp_name = object_utils.get_transform_relatives(ctrl, find_parent=True, as_strings=True)[0]
        cmds.parentConstraint(head_ctrl, jaw_ctrl, control_grp_name, mo=True)
    return True


def mirror_face_controllers(control_name=""):
    """
    mirrors the selected face controller.
    :param control_name: <str> controller name.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not control_name:
        control_names = object_utils.get_selected_node(single=False)

    for control_name in control_names:
        opposite_control_name = ''
        if '_l_' in control_name:
            opposite_control_name = control_name.replace('_l_', '_r_')
        if '_r_' in control_name:
            opposite_control_name = control_name.replace('_r_', '_l_')

        if opposite_control_name:
            # mirror the world matrix
            print(control_name, '-->', opposite_control_name)
            object_utils.mirror_object(control_name, opposite_control_name)
        else:
            # mirror the world matrix
            print(control_name, '-->', control_name)
            object_utils.mirror_object(control_name)
    return True


def zero_interface_controls():
    """
    zero out the interface controllers.
    :return: <bool> True for success. <bool> False for failure.
    """
    face_ctrls = find_face_controls(interface=True)
    if not face_ctrls:
        return False
    for face_ctrl in face_ctrls:
        f_attr = attribute_utils.Attributes(face_ctrl, keyable=True)
        if f_attr.non_zero_attributes():
            f_attr.zero_attributes()
    return True


def get_anim_nodes():
    """
    grabs the animation keys from the selected nodes.
    :return: <dict>
    """
    selected_nodes = object_utils.get_selected_node(single=False)
    if not selected_nodes:
        return False

    return_dict = {}
    for s_node in selected_nodes:
        parents = object_utils.get_parents(s_node, s_node + '_grp')
        for p_node in parents:
            anim_nodes = object_utils.get_m_anim_from_sel(p_node)
            if anim_nodes:
                for a_node, o_anim in anim_nodes.items():
                    a_data = animation_utils.get_animation_data_from_node(o_anim)
                    if a_data:
                        if s_node not in return_dict:
                            return_dict[s_node] = []
                        return_dict[s_node].append(a_data)
    return return_dict


def get_anim_data(nodes=[]):
    """
    grabs the animation keys from nodes provided.
    :param nodes: <list> animation data.
    :return: <dict> dictionary of animation node data.
    """
    if nodes and not isinstance(nodes, (list, tuple)):
        nodes = [nodes]

    # define function variables
    return_dict = {}

    # get animation data from object selected
    for s_node in nodes:
        if not s_node.endswith('_ctrl'):
            continue
        parents = object_utils.get_parents(s_node, s_node + '_grp')
        for p_node in parents:
            a_data = animation_utils.get_anim_connections(p_node)
            if a_data:
                return_dict[p_node] = a_data
    return return_dict


class MirrorList(object):
    def __init__(self, anim_data=None):
        self.temp_mirror_list = []
        self.temp_anim_data = {}

        if isinstance(anim_data, dict):
            self.temp_anim_data = anim_data
            self.get_mirror_list()
        if isinstance(anim_data, (list, tuple)):
            self.temp_mirror_list = anim_data

    def get_mirror_list(self):
        # we need the data in list form for easier access.
        for driven_node, data in self.temp_anim_data.items():
            for anim_curve_node, curve_data in data['animNodes'].items():
                driven_attr_name = curve_data['targetAttr'][0]
                driver_attr_name = curve_data['sourceAttr'][0]
                time_curves = curve_data['data']
                self.temp_mirror_list.append(tuple([driver_attr_name, driven_attr_name, time_curves]))

    def find(self, search_str="", attribute=False):
        # find the driver in the list
        __temp = []
        for current_values in self.temp_mirror_list:
            if not attribute:
                data = [c for c in current_values if search_str in c]
            else:
                data = [c for c in current_values[:-1] if search_str == c.split('.')[-1]]
            if data:
                __temp.append(current_values)
        return __temp

    def find_multiple(self, search_list=[]):
        # find the attribute from list
        __temp = []
        for current_values in self.temp_mirror_list:
            for cur_val in current_values:
                for s in search_list:
                    if s in cur_val:
                        if current_values not in __temp:
                            __temp.append(current_values)
        return __temp


def delete_keys_on_controller(controller_name="", interface_ctrl=""):
    """
    delete keys on the selected controller.
    :param controller_name: <str> controller name to delete keys from.
    :param interface_ctrl: <str> interface controller name.
    :return: <bool> True for success.
    """
    copy_to_node = _get_interface_grp_name([controller_name, interface_ctrl])
    print('deleting keys on: {}'.format(copy_to_node))
    delete_keys(object_node=copy_to_node)
    return True


def copy_keys_on_selected(selected_object="", copy_to_object="", copy_to_interface_ctrl="", mirror=False):
    """
    mirrors the keys on selected objects. The connections must be there to begin with.
    :param selected_object: <str> the original controller with animation data.
    :param copy_to_object: <str> copy the animation to this object.
    :param copy_to_interface_ctrl: <str> interface controller to use as the driver for the copied control.
    :param mirror: <bool> mirror the animation data from left to right. will follow certain rules.
    :return: <bool> True for success. <bool> False for failure.
    """
    __tmp_data = None
    __mirror_performed = []
    __tmp_driver_data = []

    if not selected_object:
        selected_object = object_utils.get_selected_node(single=False)
        if not selected_object:
            return False

    if not copy_to_object:
        raise ValueError("[CopyKeysOnSelected] :: Parameter mirror_to_object is not provided.")

    if not copy_to_interface_ctrl:
        raise ValueError("[CopyKeysOnSelected] :: Parameter copy_to_interface_ctrl is not provided.")

    # get animation dictionary data from object selected
    anim_data = get_anim_data(selected_object)

    # zero all controllers
    zero_interface_controls()
    object_utils.zero_all_controllers()

    # get the copy to interface control system controller
    copy_to_system_control = find_face_system_controller(copy_to_interface_ctrl)[0]

    if mirror:
        # we need the data in list form for easier access.
        __tmp_data = MirrorList(anim_data)

    # set the keys
    print('\n\n')
    print(selected_object)
    for driven_node, data in anim_data.items():
        copy_to_node = _get_interface_grp_name([copy_to_object, copy_to_interface_ctrl])

        for anim_curve_node, curve_data in data['animNodes'].items():
            driven_attr_name = curve_data['targetAttr'][0]
            driver_attr_name = curve_data['sourceAttr'][0]
            time_curves = curve_data['data']
            driven_object, driven_attr = driven_attr_name.split(".")
            driver_object, driver_attr = driver_attr_name.split(".")

            if mirror:
                # mirror_driver_attr = _cls_mirror.replace_side_string(driver_attr)
                if (driver_attr, driven_attr) in __mirror_performed:
                    continue

                # # get the data from the mirror
                if driven_attr in ["translateX", "rotateZ", "rotateY"]:
                    driver_data = __tmp_data.find(driven_attr)
                    __tmp_driver_data = MirrorList(driver_data)
                    __temp_attributes = __tmp_driver_data.find(driver_attr, attribute=True)
                    temp_time_curves = __temp_attributes[0][-1]

                    # invert the translation
                    for k, v in __temp_attributes[0][-1].items():
                        if "translateX" in driven_attr:
                            temp_time_curves[k] = v * -1
                        if "rotateY" in driven_attr:
                            temp_time_curves[k] = v * -1
                        if "rotateZ" in driven_attr:
                            temp_time_curves[k] = v * -1

                    # set the driven keyframes
                    animation_utils.__verbosity__ = 0
                    for driver_value, driven_value in temp_time_curves.items():
                        verbose('[{}]'.format(copy_to_node), driver_attr, driven_attr, driven_value)
                        animation_utils.set_driven_key(
                            driver_node=copy_to_system_control, driver_attr=driver_attr,
                            driven_node=copy_to_node, driven_attr=driven_attr,
                            driven_value=driven_value, driver_value=driver_value
                        )
                    __mirror_performed.append((driver_attr, driven_attr))

            # else continue with regular values for the driven key setup
            animation_utils.__verbosity__ = 0
            for driver_value, driven_value in time_curves.items():
                verbose('[{}]'.format(copy_to_node), driver_attr, driven_attr, driven_value)
                animation_utils.set_driven_key(
                    driver_node=copy_to_system_control, driver_attr=driver_attr,
                    driven_node=copy_to_node, driven_attr=driven_attr,
                    driven_value=driven_value, driver_value=driver_value
                )
    verbose("\n---------------")
    return True
