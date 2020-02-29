"""
control_utils.py utility module for manipulating controllers
"""
# import standard modules
import re
from functools import partial

# import local modules
import read_sides
from maya_utils import object_utils
from maya_utils import attribute_utils
from maya_utils import transform_utils
from maya_utils import curve_utils

# import maya modules
from maya import cmds

# define private variables
__ctrl_suffix__ = 'ctrl'
__locator_suffix__ = 'loc'

# define local variables
re_brackets = re.compile(r'\[|]')
transform_attrs = attribute_utils.Attributes.DEFAULT_ATTR_VALUES
side_cls = read_sides.Sides()


def get_selected_ctrl():
    """
    the joints from current selection.
    :return: <tuple> array of joints from selection.
    """
    selected_obj = object_utils.get_selected_node()
    if selected_obj and object_utils.is_shape_curve(selected_obj):
        return selected_obj


def zero_all_controllers():
    """
    zeroes out all the scene controllers.
    :return: <bool> True for success.
    """
    for ctrl_name in iter(cmds.ls('*_{}'.format(__ctrl_suffix__))):
        c_attr = attribute_utils.Attributes(ctrl_name, keyable=True)
        if c_attr.non_zero_attributes():
            c_attr.zero_attributes()
    return True


def mirror_transforms(object_name=""):
    """
    mirror the transform controllers. **Must have corresponding left/ right naming.
    :param object_name: <str> the object to get transform values and find the mirror object from.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not object_name:
        object_name = object_utils.get_selected_node(single=True)
    mirror_obj_name = ''
    if '_l_' in object_name:
        mirror_obj_name = object_name.replace('_l_', '_r_')
    if '_r_' in object_name:
        mirror_obj_name = object_name.replace('_r_', '_l_')
    if mirror_obj_name == mirror_obj_name:
        return False
    p_object = object_utils.get_transform_relatives(
        object_name, find_parent=True, as_strings=True)[0]
    p_mirror_object = object_utils.get_transform_relatives(
        mirror_obj_name, find_parent=True, as_strings=True)[0]
    p_trm = transform_utils.Transform(p_object)
    matrix = p_trm.world_matrix()
    mirror_matrix = p_trm.mirror_matrix(matrix)
    cmds.xform(p_mirror_object, m=mirror_matrix, ws=1)
    return True


def create_locators():
    """
    create locators on position
    """
    for sl in cmds.ls(sl=1):
        if '.' in sl:
            name, dot, num = sl.partition('.')
            matrix = False
            translate = True
            name += '_{}'.format(re_brackets.sub('', num))
        else:
            matrix = True
            translate = False
            name = sl
        locator_name = name + '_{}'.format(__locator_suffix__)
        cmds.createNode('locator', name=locator_name + 'Shape')
        object_utils.snap_to_transform(locator_name, sl, matrix=matrix, translate=translate)
    return True


def copy_xform(object_1, object_2):
    """
    copy the worldSpace matrix from object_2 to object_1.
    :param object_1: <str> the first object to snap the second object to.
    :param object_2: <str> the second object.
    :return: <bool> True for success.
    """
    x_mat = cmds.xform(object_1, m=1, q=1, ws=1)
    cmds.xform(object_2, m=x_mat, ws=1)
    return True


def check_locator_suffix_name(object_name):
    """
    checks if the incoming object has the locator suffix name.
    :param object_name:
    :return:
    """
    suffix_name = '_{}'.format(__locator_suffix__)
    if suffix_name in object_name:
        return True
    return False


def remove_locator_suffix_name(object_name):
    """
    splits the object name from its locator suffix name.
    :param object_name:
    :return:
    """
    suffix_name = '_{}'.format(__locator_suffix__)
    return object_name.rpartition(suffix_name)[0]


def check_control_suffix_name(object_name):
    """
    checks if the incoming object has the locator suffix name.
    :param object_name: <str> the object name to split.
    :return: <str> formatted name.
    """
    suffix_name = '_{}'.format(__ctrl_suffix__)
    if suffix_name in object_name:
        return True
    return False


def remove_control_suffix_name(object_name):
    """
    splits the object name from its control suffix name.
    :param object_name: <str> the object name to split.
    :return: <str> formatted name.
    """
    return object_name.rpartition('_{}'.format(__ctrl_suffix__))[0]


def snap_control_to_selected_locator():
    """
    snap the controller to the selected locator with the same leading name.
    :return: <bool> True for success.
    """
    for sl in cmds.ls(sl=1, type='transform'):
        if not check_locator_suffix_name(sl):
            continue
        ctrl_name = remove_locator_suffix_name(sl)
        copy_xform(ctrl_name, sl)
    return True


def get_shape_names(transforms_array=()):
    """
    from an array of transform objects given, return an array of associated shape names.
    :param transforms_array: <tuple> array of transform objects
    :return: <tuple> shape names.
    """
    shapes_array = ()
    for transform_name in transforms_array:
        shapes_array += object_utils.get_shape_name(transform_name, "nurbsCurve")
    return shapes_array


def color_code_controllers():
    """
    color code all controller shape names.
    :return: <bool> True for success.
    """
    ctrl_curves = cmds.ls('*_{}'.format(__ctrl_suffix__))
    shape_names_array = get_shape_names(ctrl_curves)
    for shape_name in shape_names_array:
        # get a uniform side name
        side_name = side_cls.side_name_from_string(shape_name)
        if side_name == 'Center':
            curve_utils.set_nurb_shape_color(shape_name, color='yellow')
        if side_name == 'Left':
            curve_utils.set_nurb_shape_color(shape_name, color='blue')
        if side_name == 'Right':
            curve_utils.set_nurb_shape_color(shape_name, color='red')
    return True


def zero_controllers():
    """
    zero out all controllers in the scene.
    :return: <bool> True for success.
    """
