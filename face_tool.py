"""
Face tool for loading and connecting the set driven key face utilities.
There must be face_[attribute] attributes on the controlling node!
Goal:
    Select controller, select object and set the driven keyframes.
Versions:
    1.0.0: Initial working release.
    1.0.1: Bug fix: blending the values of two shapes.
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
from deformers import deform_utils
from maya_utils import math_utils
from maya_utils import ui_utils

# reload modules
reload(attribute_utils)
reload(deform_utils)
reload(transform_utils)
reload(animation_utils)
reload(object_utils)
reload(math_utils)
reload(read_sides)

# define private variables
__version__ = "1.0.1"
__verbosity__ = 0

_cls_mirror = read_sides.MirrorSides()
__default_attribute_values = attribute_utils.Attributes.DEFAULT_ATTR_VALUES
transform_type = object_utils.node_types['transform']
locator_type = object_utils.node_types['locator']
curve_type = object_utils.node_types['nurbsCurve']

# define global variables
SIDES = read_sides.Sides()
MIRROR_SIDES = read_sides.MirrorSides()
AXES = read_sides.Axes()


def flatten_list(list_obj):
    return tuple([item for sublist in list_obj for item in sublist])


def verbose(*args):
    if __verbosity__:
        if isinstance(args, (unicode, str)):
            print(''.join(args))
        else:
            print(' '.join(args))


def get_interface_shape_names():
    """
    gets the shape names from the interface controllers.
    :return: <tuple> shape names.
    """
    controllers = find_face_controls(interface=True)
    collection = []
    for control_name in controllers:
        collection.append(control_name.split('face_')[-1].rpartition('_ctrl')[0])
    return tuple(collection)


def get_active_face_controller():
    """
    returns the active controller with the attribute value and key times.
    :return: <str>, <str>, <dict>, <tuple> interface_system_controller, face_attrs, get_average_key_times
    """
    interface_controllers = find_non_zero_interface_controllers()
    face_attrs = filter_face_attributes(interface_controllers, non_zero=True)
    for interface_ctrl in interface_controllers:
        interface_system_controller = find_face_system_controller(interface_ctrl)[0]
        return interface_ctrl, interface_system_controller, face_attrs, get_specified_key_time(interface_ctrl),


def get_corrective_shape_name(mesh_name, shape_name, attribute_name):
    return '{}_{}_{}_sculpt'.format(mesh_name, shape_name, attribute_name)


def get_blend_shape_target_name():
    """
    get the target blend shape attribute name for creation and setting of the attributes.
    :return: <str> target name.
    """
    shape_names = get_interface_shape_names()
    active_data = get_active_face_controller()
    interface_name = active_data[0]
    attribute_name = active_data[2].keys()[0]
    shape_name = [x for x in shape_names if x in interface_name][0]
    return shape_name + '_' + attribute_name


def create_corrective_shape(mesh_name=""):
    """
    creates a corrective sculpting mesh.
    :param mesh_name: <str> the mesh name to add the sculpt to.
    :return: <str> mesh name.
    """
    active_data = get_active_face_controller()
    shape_names = get_interface_shape_names()
    if not active_data:
        return False
    interface_name = active_data[0]
    attribute_name = active_data[2].keys()[0]
    shape_name = [x for x in shape_names if x in interface_name][0]
    print(mesh_name, shape_name, attribute_name)
    corrective_mesh_name = get_corrective_shape_name(mesh_name, shape_name, attribute_name)
    if not cmds.objExists(corrective_mesh_name):
        cmds.rename(cmds.duplicate(mesh_name), corrective_mesh_name)
        cmds.parent(corrective_mesh_name, world=True)
    return corrective_mesh_name


def get_corrective_mesh_name(mesh_name=""):
    """
    programmatically construct a corrective mesh name.
    :param mesh_name: <str> use this to construct a name.
    :return: <str> corrective mesh name.
    """
    active_data = get_active_face_controller()
    shape_names = get_interface_shape_names()
    if not active_data:
        return False
    interface_name = active_data[0]
    attribute_name = active_data[2].keys()[0]
    shape_name = [x for x in shape_names if x in interface_name][0]
    corrective_mesh_name = get_corrective_shape_name(mesh_name, shape_name, attribute_name)
    return corrective_mesh_name


def extract_delta(mesh_name="", corrective_mesh_name=""):
    """
    extract the mesh deltas from the mesh name, and corrective mesh name provided
    :param mesh_name: <str> the base mesh to compare vertex deltas frOpenMaya.
    :param corrective_mesh_name: <str> the corrective mesh name to extract deltas frOpenMaya.
    :return: <str> delta mesh name.
    """
    delta_mesh = deform_utils.extract_mesh_deltas(mesh_name, corrective_mesh_name)
    cmds.parent(delta_mesh, world=True)
    return delta_mesh


def attach_corrective_to_mesh(mesh_name="", corrective_sculpt_mesh=""):
    """
    attached the corrective blend-shape to the mesh object and connects it.
    :param mesh_name: <str> mesh that has the blend shape and corrective sculpt.
    :return: <bool> True for success.
    """
    target_name = get_blend_shape_target_name()
    if not corrective_sculpt_mesh:
        corrective_sculpt_mesh = get_corrective_mesh_name(mesh_name)
    return deform_utils.add_target_shape(
        mesh_name=mesh_name, target_mesh=corrective_sculpt_mesh, target_name=target_name)


def create_corrective_shape_on_selected():
    mesh_object = object_utils.get_selected_node(single=True)
    if mesh_object:
        return create_corrective_shape(mesh_object)


def do_corrective_process_on_selected():
    mesh_object = object_utils.get_selected_node(single=True)
    if mesh_object:
        return do_corrective_process(mesh_object)


def do_corrective_process(mesh_name=""):
    """
    performs the attachment of a corrective to the driver.
    :param mesh_name:
    :return:
    """
    corrective_mesh_name = get_corrective_mesh_name(mesh_name)
    delta_mesh = extract_delta(mesh_name, corrective_mesh_name)
    attach_corrective_to_mesh(mesh_name, delta_mesh)
    connect_driver_to_active_target_blendshape(mesh_name)
    return True


def connect_driver_to_active_target_blendshape(mesh_name=""):
    """
    gets the blend shape name, the active target name and connects it.
    :param mesh_name:
    :return:
    """
    face_controller_data = get_active_face_controller()
    controller_loc = face_controller_data[1]
    attr = face_controller_data[2].keys()[0]
    driver_attr = '{}.{}'.format(controller_loc, attr)

    blend_node = deform_utils.get_connected_blendshape_nodes(mesh_name, as_strings=True)
    if not blend_node:
        return False
    blend_node = blend_node[0]
    target_name = get_blend_shape_target_name()
    target_attr = deform_utils.get_blend_target_attribute(blend_node=blend_node, target_name=target_name)
    print("[ConnectingDriverToBlendShape] :: {} >> {}".format(driver_attr, target_attr))
    target_attr = target_attr[0][0]
    target_attr = '{}.{}'.format(blend_node, target_attr)
    object_utils.connect_attr(driver_attr, target_attr)
    return True


def evaluate_blend_weighted_node(node_name, target_attr):
    """
    force the evaluation of the blend weighted node.
    :param node_name:
    :param target_attr:
    :return:
    """
    cmds.dgeval(animation_utils.get_connected_blend_weighted_node(node_name, target_attr))


def math_get_sign(number=0.0):
    """
    returns the sign for number direction.
    :param number:
    :return:
    """
    if number < 0:
        return -1
    else:
        return 1


def get_anim_node_key_times(face_system_controller=""):
    """
    from a non-zero interface controller, extract the affecting anim curves and get the time values.
    :return: <dict> animation curve items.
    """
    if not face_system_controller:
        interface_controllers = find_non_zero_interface_controllers()
    else:
        interface_controllers = [face_system_controller]
    objects = {}
    for interface_node in interface_controllers:
        # filters only one active driver attributes
        interface_system_controller = find_face_system_controller(interface_node)[0]
        face_attrs = filter_face_attributes(interface_system_controller, non_zero=True)
        # system_attribute = '{}.{}'.format(interface_system_controller, face_attrs.keys()[0])
        anim_curves_gen = animation_utils.connections_gen(
                interface_system_controller, attribute=face_attrs.keys()[0], ftype='kAnimCurve')
        for curve_node in anim_curves_gen:
            anim_curve_name = object_utils.get_m_object_name(curve_node)
            # get keys only
            data = animation_utils.get_animation_data_from_node(curve_node)
            if anim_curve_name and anim_curve_name in data:
                time_values = data[anim_curve_name]['data'].keys()
                objects[anim_curve_name] = tuple(time_values)
            else:
                continue
    return objects


def get_specified_key_time(interface_control, rounded=True):
    """
    get the average key times.
    :return:  <tuple> of all key times
    """
    items = flatten_list(set(get_anim_node_key_times(interface_control).values()))
    if rounded:
        return tuple(set(map(lambda x: round(x, 4), items)))
    else:
        return tuple(set(items))


def get_average_key_times(rounded=True):
    """
    get the average key times.
    :return:  <tuple> of all key times
    """
    items = flatten_list(set(get_anim_node_key_times().values()))
    if rounded:
        return tuple(set(map(lambda x: round(x, 4), items)))
    else:
        return tuple(set(items))


def get_empty_anim_curves():
    """
    return a tuple list of all empty anim curve nodes.
    :return: <tuple> nodes.
    """
    garbage_collection = []
    anim_curve_nodes = object_utils.get_scene_objects(node_type='kAnimCurve')
    print("kAnimCurves in Scene: {}".format(len(anim_curve_nodes)))
    for curve_node in anim_curve_nodes:
        anim_fn = object_utils.OpenMayaAnim.MFnAnimCurve(curve_node)
        if not anim_fn.numKeys() or anim_fn.numKeys() < 2:
            garbage_collection.append(anim_fn.name())
    print("Empty kAnimCurves: {}".format(len(garbage_collection)))
    return tuple(garbage_collection)


def remove_single_key_nodes():
    """
    removes any animCurve nodes that only have a single key.
    :return: <bool> True for success.
    """
    cmds.delete(get_empty_anim_curves())
    return True


def copy_keys_left_to_right(interface_ctrl="", mirror_interface=True):
    """
    copy the keys from left to right. Please specify which interface driver controller the copy neecs to go to.
    :param interface_ctrl: <bool> the driver interface.
    :param mirror_interface: <bool> mirror the interface controller as well.
    :return: <bool> True for success. <bool> False for failure.
    """
    if mirror_interface:
        mirror_interface_ctrl = MIRROR_SIDES.replace_side_string(interface_ctrl)
    else:
        mirror_interface_ctrl = interface_ctrl

    for sel_obj in get_selected_objects_gen():
        # get the opposing side string
        mirror_sel_obj = MIRROR_SIDES.replace_side_string(sel_obj)

        # trim anim data
        driven_object = _get_interface_grp_name([sel_obj, interface_ctrl])
        anim_data = get_anim_data(sel_obj)
        if driven_object not in anim_data:
            continue

        # copy the animation data
        copy_keys_on_selected(
            selected_object=sel_obj,
            copy_to_object=mirror_sel_obj,
            copy_to_interface_ctrl=mirror_interface_ctrl,
            anim_data=anim_data[driven_object],
            mirror=True)
    print('[MirrorKeys] :: Done.')
    return True


def find_non_zero_on_face_controllers():
    """
    return a tuple list of all available controllers.
    :return: <tuple> list of all available controllers
    """
    ctrl_names = []
    controllers = find_face_controls(on_face=True)
    for ctrl_name in controllers:
        attrs = attribute_utils.Attributes(ctrl_name, keyable=True)
        if attrs.non_zero_attributes():
            ctrl_names.append(ctrl_name)
    return tuple(ctrl_names)


def find_non_zero_interface_controllers():
    """
    return a tuple list of all available controllers.
    :return: <tuple> list of all available controllers
    """
    ctrl_names = []
    controllers = find_interface_controllers()
    for ctrl_name in controllers:
        attrs = attribute_utils.Attributes(ctrl_name, keyable=True)
        if attrs.non_zero_attributes():
            ctrl_names.append(ctrl_name)
    return tuple(ctrl_names)


def get_list_index(ls_object=[], find_str=""):
    """
    find a string index from list provided.
    :param ls_object: <list> the list to find the string frOpenMaya.
    :param find_str: <str> the string to find inside the list.
    :return: <int> the found index. -1 if not found.
    """
    try:
        return ls_object.index(find_str)
    except ValueError:
        return -1


def get_blend_weighted_items(driven_object, driven_attr):
    """
    get blend weighteed objects.
    :param driven_object:
    :param driven_attr:
    :return:
    """
    return map(lambda x: round(x, 4), animation_utils.get_blend_weighted_values(
        node_name=driven_object, target_attr=driven_attr)[0])


def get_weighted_values_length(driven_object, driven_attr):
    """
    Get the length of all non-zero weighted values.
    :param driven_object: <str> the driven object to get connections frOpenMaya.
    :param driven_attr: <str> the driven attribute to get the weighted values frOpenMaya.
    :return: <int> length.
    """
    rounder = lambda x: round(x, 4)
    weighted_values = animation_utils.get_blend_weighted_values(
        node_name=driven_object, target_attr=driven_attr)
    if weighted_values:
        # return len(tuple(filter(lambda x: round(x, 4) != 0.0, weighted_values)))
        return len(filter(None, map(rounder, weighted_values[0])))
    else:
        return 0


def get_original_weight_value(driven_object, driven_attr, interface_node, face_attr):
    """
    get the weight value from the blend weighted node. If no blendWeighted node is found, return default 0.0
    :param driven_object: <str> the driven object to get connections frOpenMaya.
    :param driven_attr: <str> the driven attribute to get the weighted values frOpenMaya.
    :param interface_node: <str> the driver interface controller.
    :param face_attr: <str> the face driver attribute.
    :return: <float> the weighted float value.
    """
    weighted_values = animation_utils.get_blend_weighted_values(
        node_name=driven_object, target_attr=driven_attr)
    if not weighted_values:
        return 0.0
    blend_node = object_utils.get_plugs(driven_object, attr_name=driven_attr)[0]
    anim_data = animation_utils.get_anim_connections(blend_node)
    index = get_list_index(anim_data['source'], '{}.{}'.format(interface_node, face_attr))
    return weighted_values[0][index]


def get_keyable_object_attributes(driven_object):
    """
    from the object provided, return the driven keyable attributes names and values in dictionary format.
    :param driven_object: <str> the driven object to get keyable attributes frOpenMaya.
    :return: <dict> all keyable attributes with values.
    """
    return attribute_utils.Attributes(driven_object, keyable=1).__dict__()


def get_keyable_non_zero_attributes(driven_object):
    """
    from the object provided, return the driven keyable attributes names and values in dictionary format.
    :param driven_object: <str> the driven object to get keyable attributes frOpenMaya.
    :return: <dict> all keyable attributes with values.
    """
    return attribute_utils.Attributes(driven_object, keyable=1).non_zero_attributes()


def check_if_object_is_control(object_name=""):
    """
    checks if the object name provided is a valid control transform.
    :param object_name: <str> the object name to check if it's a valid control item.
    :return: <bool> True if the object provided is a valid controller object.
            <bool> False else it's not a valid controller object.
    """
    return cmds.objectType(object_name) == 'transform' and object_name.endswith('_ctrl')


def delete_keys_on_selected():
    """
    deletes set driven keys from selected controllers.
    :return: <bool> True for success.
    """
    s_ctrls = object_utils.get_selected_node(single=False)
    if not s_ctrls:
        raise IndexError("[DeleteKeysOnSelectedError] :: No controllers are selected.")
    selected_ctrls = s_ctrls[:-1]
    interface_ctrl = s_ctrls[-1]
    for c_ctrl in selected_ctrls:
        if not check_if_object_is_control(c_ctrl):
            continue
        print('[DeleteKeysOnSelected] :: Deleting keys on {}.'.format(c_ctrl))
        delete_keys_on_controller(c_ctrl, interface_ctrl)
    return True


def on_face_controllers_gen():
    """
    on face controller generator.
    :return: <listiterator object> list iterator.
    """
    return iter(find_face_controls(on_face=True))


def interface_controllers_gen():
    """
    interface controller generator.
    :return: <listiterator object> list iterator.
    """
    return iter(find_face_controls(interface=True))


def inspect_interface_attributes():
    """
    prints the selected controller attributes.
    :return: <bool> True for success.
    """
    s_ctrls = object_utils.get_selected_node(single=False)
    for f_ctrl in s_ctrls:
        # face_loc = find_face_system_controller(f_ctrl)
        # if not face_loc:
        face_loc = find_system_locator(f_ctrl)
        attr = attribute_utils.Attributes(face_loc[0], custom=1, keyable=True)
        print(f_ctrl, face_loc, ">>", attr.__dict__())
        # print(get_specified_key_time(face_loc))
    return True


def get_object_node(object_node):
    """
    grabs the object node.
    :param object_node: <str> object node
    :return:
    """
    if not object_node:
        object_node = object_utils.get_selected_node()
    if isinstance(object_node, (list, tuple)):
        object_node = object_node[0]
    return object_node


def get_face_attributes(object_node="", non_zero=False):
    """
    gets the face attributes from the controller specified.
    if there are no face attributes, list all keyable attributes.
    :param object_node: <str> maya object node.
    :param non_zero: <bool> get non zero face attributes.
    :return: <list> face attributes.
    """
    object_node = get_object_node(object_node)
    attrs = attribute_utils.Attributes(object_node, custom=True, keyable=True)
    a_data = {}
    if attrs:
        if non_zero:
            a_data = attrs.non_zero_attributes().items()
        else:
            a_data = attrs.items()
    return dict(filter(lambda a: a[0].startswith('face_'), a_data))


def filter_face_attributes(object_node="", non_zero=True):
    """
    filters the attributes on the controller node.
    :param object_node: <str> maya object node.
    :param non_zero: <bool> get non zero face attributes.
    :return: <list> face attributes.
    """
    object_node = get_object_node(object_node)
    object_node = find_face_system_controller(object_node)
    attribute_dict = get_face_attributes(object_node, non_zero)
    collection = {}
    for attr, val in attribute_dict.items():
        if filter(lambda x: x == attr.partition('_')[-1], AXES.split()):
            collection[attr] = val
    if collection:
        return collection
    else:
        return attribute_dict


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
    anim_data = get_anim_data(object_node=object_node)
    animation_utils.set_anim_data(anim_data=anim_data, rounded=True)
    return True


def find_interface_controllers():
    """
    find the interface controller.
    :return:
    """
    controller_objects = object_utils.get_scene_objects(find_attr='face_', dag=True)
    controller_array = ()
    for control_obj in controller_objects:
        controller_array += object_utils.get_connected_nodes(
            control_obj,
            find_node_type=transform_type,
            with_shape=curve_type,
            as_strings=True,
            up_stream=True,
            down_stream=False)
    return controller_array


def find_face_system_controller(object_node=""):
    """
    finds the interface locator controller from the control gui
    :return: <str> face system controller name.
    """
    if not object_node:
        object_node = object_utils.get_selected_node()
    if not object_node:
        raise ValueError("[FindFaceSystemController] :: no valid object parameter given.")
    face_attrs = get_face_attributes(object_node)
    if face_attrs:
        return object_node
    return object_utils.get_connected_nodes(object_node,
                                            find_node_type=transform_type,
                                            with_shape=locator_type,
                                            find_attr="face_",
                                            as_strings=True,
                                            up_stream=False,
                                            down_stream=True)


def find_system_locator(object_node=""):
    """
    finds the locator node thats being driven by the controller object.
    :param object_node:
    :return:
    """
    if not object_node:
        object_node = object_utils.get_selected_node()
    if not object_node:
        raise ValueError("[FindFaceSystemController] :: no valid object parameter given.")
    face_attrs = get_face_attributes(object_node)
    if face_attrs:
        return object_node
    return object_utils.get_connected_nodes(object_node,
                                            find_node_type=transform_type,
                                            with_shape=locator_type,
                                            find_attr="",
                                            as_strings=True,
                                            up_stream=False,
                                            down_stream=True)


def find_face_controls(interface=False, on_face=False):
    """
    find the facial interface controller objects in the scene.
    :return: <list> face controllers. <bool> False for failure.
    """
    if not interface and not on_face:
        raise ValueError("[FindFaceControls] :: Please specify boolean parameters for interface or on_face.")

    face_controls = cmds.ls('face_*', type='transform') + cmds.ls('*:face_*', type='transform')
    verbose("interface controllers have been identified.")

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
    verbose(selected_on_face_ctrl, grp_name)
    return object_utils.insert_transform(selected_on_face_ctrl, name=grp_name)


def create_face_driver_grps():
    """
    create face driver groups for the on-face controllers.
    :return: <bool> True for success.
    """
    # create interface control group
    for on_face_ctrl in on_face_controllers_gen():
        # zero out the attributes on the face controllers first.
        attrs = attribute_utils.Attributes(on_face_ctrl, keyable=True)
        if attrs.non_zero_attributes():
            attrs.zero_attributes()

        # then build the parent transforms
        for interface_name in interface_controllers_gen():
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


def set_key_on_selected():
    """
    set the driven keys on selected controller.
    :return: <bool> True for success.
    """
    get_selection = object_utils.get_selected_node(single=0)
    if not get_selection:
        return False
    for f_ctrl in get_selection:
        if not check_if_object_is_control(f_ctrl):
            continue
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
        verbose("[SetDefaultKeyOnSelected] :: Setting defaults on, {}.".format(f_ctrl))
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
            verbose(control_name, '-->', opposite_control_name)
            object_utils.mirror_object(control_name, opposite_control_name)
        else:
            # mirror the world matrix
            verbose(control_name, '-->', control_name)
            object_utils.mirror_object(control_name)
    return True


def zero_interface_controls():
    """
    zero out the interface controllers.
    :return: <bool> True for success. <bool> False for failure.
    """
    for face_ctrl in iter(find_non_zero_interface_controllers()):
        f_attr = attribute_utils.Attributes(face_ctrl, keyable=True)
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


def get_anim_data(nodes=()):
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
    Mirror_Sides = read_sides.MirrorSides()
    """
    Class object for data mining the animation data attributes for mirror operations.
    """
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
        for anim_curve_node, curve_data in self.temp_anim_data['animNodes'].items():
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

    def find_multiple(self, search_list=()):
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
    :param controller_name: <str> controller name to delete keys frOpenMaya.
    :param interface_ctrl: <str> interface controller name.
    :return: <bool> True for success.
    """
    copy_to_node = _get_interface_grp_name([controller_name, interface_ctrl])
    verbose('deleting keys on: {}'.format(copy_to_node))
    delete_keys(object_node=copy_to_node)
    return True


def copy_keys_on_selected(selected_object="", copy_to_object="", copy_to_interface_ctrl="", anim_data={}, mirror=False):
    """
    mirrors the keys on selected objects. The connections must be there to begin with.
    :param selected_object: <str> the original controller with animation data.
    :param copy_to_object: <str> copy the animation to this object.
    :param copy_to_interface_ctrl: <str> interface controller to use as the driver for the copied control.
    :param anim_data: <dict> use this anim data instead. Otherwise the copy will loop through all the data.
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
    if not anim_data:
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
    verbose('\n\n')
    verbose(selected_object)
    copy_to_node = _get_interface_grp_name([copy_to_object, copy_to_interface_ctrl])
    for anim_curve_node, curve_data in anim_data['animNodes'].items():
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


def apply_key_on_face_control(selected_on_face_ctrl='', interface_ctrl=""):
    """
    prepare the controllers and their respective groups before setting the keys.
    will look for any transformation values for each interface controller.
    :return: <bool> True for success.
    """
    if not selected_on_face_ctrl:
        return ValueError("[ApplyKeyOnFaceControl] :: selected_on_face_ctrl parameter is empty.")

    on_face_attrs = attribute_utils.Attributes(selected_on_face_ctrl, keyable=True)

    # iterate through the interface controllers and apply key on any non-zero keys.
    # filter the list for any controller with non zero keys
    if not interface_ctrl:
        interface_controllers = find_non_zero_interface_controllers()
    else:
        interface_controllers = [interface_ctrl]

    for interface_ctrl in interface_controllers:
        # grab the driven object name
        driven_object = _get_interface_grp_name([selected_on_face_ctrl, interface_ctrl])

        # get the attributes on the driven object
        drn_attr = attribute_utils.Attributes(driven_object, keyable=True)
        # original_attributes = drn_attr.__dict__()
        drn_custom_attr = attribute_utils.Attributes(driven_object, custom=True)

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
                                    driven_node=driven_object,
                                    original_data=on_face_attrs.__dict__())
    return True


def find_blend_weighted_node(driven_object, driven_attr):
    """
    finds the blend weighted node from the driven object found.
    :param driven_object: <str> the driven object to find the blendWeighted connected node from.
    :param driven_attr: <str> the driven attribute the connecting blend weighted node to be found as source.
    :return: <tuple> connected blendWeighted node from attribute given.
    """
    return animation_utils.get_connected_blend_weighted_node(driven_object, driven_attr)


def set_keys_on_face_controller(selected_node='', interface_ctrl="", driven_node="", original_data={}):
    """
    Identify the selected face controller and set the driven key.
    :param selected_node: <str> selected node to get attributes frOpenMaya.
    :param interface_ctrl: <str> the controller maya object node which has the custom face_attributes.
    :param driven_node: <str> the driven maya object node.
    :param original_data: <dict> get the original attributes to get the difference of values frOpenMaya.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not driven_node:
        driven_node = object_utils.get_selected_node()
    if not interface_ctrl:
        raise ValueError("[SetFaceKey :: parameter controller_node is empty.]")

    # get the face system controller with the driver attributes
    interface_node = find_face_system_controller(interface_ctrl)[0]

    # grabs only one driving attribute.
    face_attrs = filter_face_attributes(interface_node, non_zero=True)

    if not face_attrs:
        raise RuntimeError("[NoFaceAttributeFoundError] :: Cannot use this face controller: {}.".format(
            interface_node
        ))

    # grab the driven object name
    driven_object = _get_interface_grp_name([selected_node, interface_ctrl])

    # get the keyable driven attributes
    # driven_attrs = get_keyable_object_attributes(driven_object)
    driven_attrs = get_keyable_object_attributes(driven_object)

    print('[SetKeys] :: {}, {}, {}'.format(selected_node, face_attrs, driven_attrs))

    # set the key on the controller and the driven
    for face_attr, face_value in face_attrs.items():
        for driven_attr, driven_val in driven_attrs.items():
            weighted_sum = animation_utils.get_blend_weighted_sum(node_name=driven_object, target_attr=driven_attr)
            # skip the attributes that already have original values on them
            # if original_data[driven_attr] != 0.0 and original_data[driven_attr] == weighted_sum:
            #     continue
            if 'visibility' in driven_attr:
                continue

            # skip the offset_ attributes
            if 'offset_' in driven_attr:
                continue

            # change the driven scale attribute name
            if 'scale' in driven_attr:
                driven_attr = get_offset_scale_attr(driven_attr)
                driven_val += -1

            # evaluate the blend weighted node
            # evaluate_blend_weighted_node(driven_object, driven_attr)

            # grab the original data
            if driven_attr in original_data:
                original_driven_value = original_data[driven_attr]
            else:
                original_driven_value = 0.0

            # find the weighted value corresponding to the driven attribute name
            driven_weighted_value = get_original_weight_value(driven_object, driven_attr, interface_node, face_attr)

            # driven_val = driven_weighted_value - driven_value_difference
            blend_node = find_blend_weighted_node(driven_object, driven_attr)

            if not blend_node:
                print("[SetKeyFailure] :: Attribute not initialized: {}".format(driven_attr))
                continue

            if get_weighted_values_length(driven_object, driven_attr) > 0:
                print(driven_attr, original_driven_value, driven_weighted_value, get_weighted_values_length(driven_object, driven_attr), driven_val)
                # driven_val = (original_driven_value + driven_weighted_value)
                # driven_val = original_driven_value + driven_weighted_value
                if original_driven_value:
                    print('The driven value will be blended.\n{}'.format(driven_attr))
                    if driven_weighted_value != original_driven_value + weighted_sum:
                        driven_val = original_driven_value + driven_weighted_value

            # set the key at the current space location
            face_value = math_utils.round_to_step(face_value)
            verbose('\n')
            verbose('[WeightedSum] :: {}'.format(weighted_sum))
            verbose('[OriginalDrivenValue] :: {}, {}'.format(driven_attr, original_driven_value))
            verbose('[OriginalDrivenWeightedValue] :: {}, {}'.format(driven_attr, driven_weighted_value))
            verbose('[DrivenValue] :: {}, {}'.format(driven_attr, driven_val))
            verbose('[FaceValue] :: {}, {}'.format(face_attr, face_value))
            verbose('\n')
            __set_key(interface_node, driven_node, driven_attr, face_attr, driven_val, face_value)
    return True


def setup_follicle_eyelids(driver_objects, mesh_name):
    """
    create a follicle setup of eyelids on a surface object.
    :return: <bool> True for success. <bool> False for failure.
    """
