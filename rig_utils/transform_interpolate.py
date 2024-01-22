# import maya modules
from maya import cmds
try:
    import pymel.core as pm
except ImportError:
    raise ImportError("Please install PyMel.")
from maya import OpenMaya
# import custom modules
from ui_tools import organizer_tool
from maya_utils import math_utils
# import standard modules
import copy
import re
import random
# global variables
dt = pm.datatypes
SHAPE_ATTR = 'shapes'
find_digit = re.compile('[\d+]')


class KeywordError(BaseException):
    def __init__(self, message):
        self.message = message


class IntentionalNoBlendMatrixNodeError(BaseException):
    def __init__(self, message):
        self.message = message


def create_source_locator(control_name, shape_scale=1.0):
    """
    """
    source_loc_name = create_name(control_name, suffix_name='source')
    if not cmds.objExists(source_loc_name):
        shape_loc = cmds.createNode('locator', name=source_loc_name + 'Shape')
        cmds.setAttr('{}.localScaleX'.format(shape_loc), shape_scale)
        cmds.setAttr('{}.localScaleY'.format(shape_loc), shape_scale)
        cmds.setAttr('{}.localScaleZ'.format(shape_loc), shape_scale)
    return source_loc_name


def create_targets(control_name, name='', num=4, shape_scale=0.2):
    """create targets with name
    """
    source_locator = create_source_locator(control_name, shape_scale)
    targets = (source_locator, )
    for i in range(num):
        loc_target_name = create_name(name, suffix_name='{}_target'.format(i))
        shape_loc = cmds.createNode('locator', name=loc_target_name + 'Shape')
        cmds.setAttr('{}.localScaleX'.format(shape_loc), shape_scale)
        cmds.setAttr('{}.localScaleY'.format(shape_loc), shape_scale)
        cmds.setAttr('{}.localScaleZ'.format(shape_loc), shape_scale)
        targets += loc_target_name,
        cmds.xform(loc_target_name, t=(i, 0, 0), ws=True)
    face_shape_grp_node = add_grp_node(name=name, suffix_name="TARGETFACE_GRP",
                                       children=targets)
    return face_shape_grp_node


def interpolate_matrices(matrix_a, matrix_b, envelope):
    """Interpolates between two MMatrix objects based on the given envelope
    (1 - t) * A + t * B
    :param matrix_a: (OpenMaya.MMatrix,) the first matrix
    :param matrix_b: (OpenMaya.MMatrix,) the second matrix
    :param envelope: (float,) the interpolation envelope (0.0 to 1.0)
    :return: (OpenMaya.MMatrix,) the interpolated matrix
    """
    if not (0.0 <= envelope <= 1.0):
        raise ValueError("Envelope must be between 0.0 and 1.0")
    result_matrix = OpenMaya.MMatrix()
    for i in range(4):
        for j in range(4):
            result_matrix[i][j] = (1 - envelope) * \
                matrix_a[i][j] + envelope * matrix_b[i][j]
    return result_matrix


def zero_transform_values(node_name, translate=True, scale=True, rotate=True, skip_tx=False):
    """zero the transform node's XYZ channels
    :param translate: (bool) zeroes the translate values
    :param scale: (bool) zeroes the scale values
    :param rotate: (bool) zeroes the rotate values
    :param skip_tx: (bool) 
    """
    if translate:
        if not skip_tx:
            cmds.setAttr(node_name + '.translateX', 0)
        cmds.setAttr(node_name + '.translateY', 0)
        cmds.setAttr(node_name + '.translateZ', 0)
    if rotate:
        cmds.setAttr(node_name + '.rotateX', 0)
        cmds.setAttr(node_name + '.rotateY', 0)
        cmds.setAttr(node_name + '.rotateZ', 0)
    if scale:
        cmds.setAttr(node_name + '.scaleX', 1)
        cmds.setAttr(node_name + '.scaleY', 1)
        cmds.setAttr(node_name + '.scaleZ', 1)


def lock_transforms(node_name, translate=True, scale=True, rotate=True, visibility=True):
    """lock and hide the channels
    :param translate: (bool) locks and hide the translate channel
    :param scale: (bool) locks and hide the scale channel
    :param rotate: (bool) locks and hide the rotate channel
    :param skip_tx: (bool) 
    """
    if translate:
        cmds.setAttr(node_name + '.translateX', k=False, l=True)
        cmds.setAttr(node_name + '.translateY', k=False, l=True)
        cmds.setAttr(node_name + '.translateZ', k=False, l=True)
    if rotate:
        cmds.setAttr(node_name + '.rotateX', k=False, l=True)
        cmds.setAttr(node_name + '.rotateY', k=False, l=True)
        cmds.setAttr(node_name + '.rotateZ', k=False, l=True)
    if scale:
        cmds.setAttr(node_name + '.scaleX', k=False, l=True)
        cmds.setAttr(node_name + '.scaleY', k=False, l=True)
        cmds.setAttr(node_name + '.scaleZ', k=False, l=True)
    if visibility:
        cmds.setAttr(node_name + '.visibility', k=False, l=True)


def add_face_attr_to_node(node_name):
    """adds a custom attribute for a later, clean, deletion
    """
    attr_name = "FaceMatrixInterpolateNode"
    if not cmds.ls(node_name + '.' + attr_name):
        cmds.addAttr(node_name, ln=attr_name, at='float', min=0.0, max=0.0)
    return attr_name


def delete_nodes():
    """deletes the created face nodes
    """
    attr_name = "FaceMatrixInterpolateNode"
    nodes = cmds.ls('*.{}'.format(attr_name))
    for node in nodes:
        node = node.split('.')[0]
        if node.endswith("_DRV"):
            parent_node = cmds.listRelatives(node, p=True, type='transform')
            child_node = cmds.listRelatives(node, c=True, type='transform')
            cmds.parent(child_node, parent_node)
        cmds.delete(node)


def add_curve_attr_to_node(node_name):
    """adds a custom attribute for a later, clean, deletion
    """
    attr_name = "FaceMatrixCurveNode"
    if not cmds.ls(node_name + '.' + attr_name):
        cmds.addAttr(node_name, ln=attr_name, at='float', min=0.0, max=0.0)
    return attr_name


def delete_nodes():
    """deletes the created face nodes
    """
    attr_name = "FaceMatrixCurveNode"
    nodes = cmds.ls('*.{}'.format(attr_name))
    cmds.delete(nodes)


def create_name(name, suffix_name=""):
    """create a name
    :param name: <str>
    :param suffix_name: <str>
    """
    full_name = name
    if suffix_name:
        full_name += '_' + suffix_name
    return full_name


def add_plua_minus_average(name, suffix_name=""):
    """create a plus minus average node
    :param name: (str)
    :param suffix_name: (str)
    """
    pma_node_name = create_name(name, suffix_name=suffix_name + 'PMA')
    if not cmds.ls(pma_node_name, type='plusMinusAverage'):
        cmds.createNode('plusMinusAverage', name=pma_node_name)
    return pma_node_name


def add_vector_product(name, suffix_name="", operation="pointMatrixProduct"):
    """create a vector product node
    :param name: (str)
    :param suffix_name: (str)
    :param operation: (str) Default "pointMatrixProduct"
    """
    operation_dict = {"noOperation": 0,
                      "dotProduct": 1,
                      "crossProduct": 2,
                      "vectorMatrixProduct": 3,
                      "pointMatrixProduct": 4}
    operation_int = operation_dict[operation]
    vector_product_name = create_name(name, suffix_name=suffix_name + '_VEC')
    vector_product_node = cmds.ls(vector_product_name, type="vectorProduct")
    if not vector_product_node:
        vector_product_node = cmds.createNode(
            "vectorProduct", name=vector_product_name)
    else:
        vector_product_node = vector_product_node[0]
    cmds.setAttr(vector_product_name + '.operation', operation_int)
    return vector_product_name


def connect_to_cv_point(transform_node, curve_node, name="", index=0):
    """connects a transform to a curve point
    :returns: <str> vectorProduct node
    """
    vec_node = add_vector_product(name, suffix_name=transform_node)
    src_attr = transform_node + '.worldMatrix[0]'
    dst_attr = vec_node + '.matrix'
    if not cmds.isConnected(src_attr, dst_attr):
        cmds.connectAttr(src_attr, dst_attr)
    src_attr = '{}.output'.format(vec_node)
    dst_attr = '{}.controlPoints[{}]'.format(curve_node, index)
    if not cmds.isConnected(src_attr, dst_attr):
        cmds.connectAttr(src_attr, dst_attr)
    return vec_node


def add_blend_colors_node(name, suffix_name="", percent=0.5):
    """percentage baseed vector output between two vectors
    """
    blend_colors_node_name = create_name(name, suffix_name)
    blend_colors_node = cmds.ls(blend_colors_node_name, type='blendColors')
    if not blend_colors_node:
        blend_colors_node = cmds.createNode(
            "blendColors", name=blend_colors_node_name)
    else:
        blend_colors_node = blend_colors_node[0]
    cmds.setAttr(blend_colors_node + '.blender', percent)
    add_face_attr_to_node(blend_colors_node)
    return blend_colors_node


def add_driver_transform(use_transform, name="", suffix_name="", insert=True):
    """adds a driver transform to be connected by this interpolation system 
    :param name: 
    """
    driver_m = cmds.xform(use_transform, ws=1, q=1, m=1)
    if not name:
        name = use_transform
    drv_trasform_node_name = use_transform + \
        '_' + create_name(name, suffix_name)
    drv_trasform_node = cmds.ls(drv_trasform_node_name, type="transform")
    if not drv_trasform_node:
        drv_trasform_node = cmds.createNode(
            "transform", name=drv_trasform_node_name)
        cmds.xform(drv_trasform_node, ws=1, m=driver_m)
        if insert:
            parent_node = cmds.listRelatives(use_transform, p=True)
            if parent_node:
                cmds.parent(drv_trasform_node, parent_node[0])
            cmds.parent(use_transform, drv_trasform_node)
    else:
        drv_trasform_node = drv_trasform_node[0]
    add_face_attr_to_node(drv_trasform_node)
    return drv_trasform_node


def add_set_range_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    set_range_node_name = create_name(name, suffix_name)
    set_range_node = cmds.ls(set_range_node_name, type='setRange')
    if not set_range_node:
        set_range_node = cmds.createNode("setRange", name=set_range_node_name)
    else:
        set_range_node = set_range_node[0]
    add_face_attr_to_node(set_range_node)
    return set_range_node


def add_inverse_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    inv_matrix_node_name = create_name(name, suffix_name)
    inv_matrix_node = cmds.ls(inv_matrix_node_name, type='inverseMatrix')
    if not inv_matrix_node:
        inv_matrix_node = cmds.createNode(
            "inverseMatrix", name=inv_matrix_node_name)
    else:
        inv_matrix_node = inv_matrix_node[0]
    add_face_attr_to_node(inv_matrix_node)
    return inv_matrix_node


def add_mult_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    mult_matrix_node_name = create_name(name, suffix_name)
    mult_matrix_node = cmds.ls(mult_matrix_node_name, type='multMatrix')
    if not mult_matrix_node:
        mult_matrix_node = cmds.createNode(
            "multMatrix", name=mult_matrix_node_name)
    else:
        mult_matrix_node = mult_matrix_node[0]
    add_face_attr_to_node(mult_matrix_node)
    return mult_matrix_node


def add_mult_divide_node(name, suffix_name=""):
    """multiply divide node
    :param name:
    """
    mult_divide_node_name = create_name(name, suffix_name)
    # i have to get the existing multiply divide nodes that currently exist
    mult_divide_node = cmds.ls(mult_divide_node_name, type='multiplyDivide')
    if not mult_divide_node:
        mult_divide_node = cmds.createNode(
            "multiplyDivide", name=mult_divide_node_name)
    else:
        mult_divide_node = mult_divide_node[0]
    add_face_attr_to_node(mult_divide_node)
    return mult_divide_node


def add_blend_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    blend_matrix_node_name = create_name(name, suffix_name)
    blend_matrix_node = cmds.ls(blend_matrix_node_name, type='blendMatrix')
    if not blend_matrix_node:
        blend_matrix_node = cmds.createNode(
            "blendMatrix", name=blend_matrix_node_name)
    else:
        blend_matrix_node = blend_matrix_node[0]
    add_face_attr_to_node(blend_matrix_node)
    return blend_matrix_node


def add_aim_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    aim_matrix_node_name = create_name(name, suffix_name)
    aim_matrix_node = cmds.ls(aim_matrix_node_name, type='aimMatrix')
    if not aim_matrix_node:
        aim_matrix_node = cmds.createNode(
            "aimMatrix", name=aim_matrix_node_name)
    else:
        aim_matrix_node = aim_matrix_node[0]
    add_face_attr_to_node(aim_matrix_node)
    return aim_matrix_node


def add_compose_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    compose_matrix_node_name = create_name(name, suffix_name)
    compose_matrix_node = cmds.ls(
        compose_matrix_node_name, type='composeMatrix')
    if not compose_matrix_node:
        compose_matrix_node = cmds.createNode(
            "composeMatrix", name=compose_matrix_node_name)
    else:
        compose_matrix_node = compose_matrix_node[0]
    add_face_attr_to_node(compose_matrix_node)
    return compose_matrix_node


def set_matrix_attr(node_name, xform_matrix, matrix_attr="secondaryTargetMatrix"):
    """function for setting matrix attribute types
    """
    cmds.setAttr("{}.{}".format(node_name, matrix_attr),
                 xform_matrix, type='matrix')


def add_remap_value_node(name, suffix_name=""):
    """remap value node
    :param name:
    :param suffix_name:
    """
    remap_value_node_name = create_name(name, suffix_name)
    remap_value_node = cmds.ls(remap_value_node_name, type='remapValue')
    if not remap_value_node:
        remap_value_node = cmds.createNode(
            "remapValue", name=remap_value_node_name)
    else:
        remap_value_node = remap_value_node[0]
    add_face_attr_to_node(remap_value_node)
    return remap_value_node


def add_condition_node(name, suffix_name="", second_term=1, operation="equal", color_if_true=1.0, color_if_false=0.0):
    """creates a condition node
    :param name:
    :param suffix_name:
    """
    # ...operation dictionary
    operation_dict = {"equal": 0,
                      "NotEqual": 1,
                      "Greater Than": 2,
                      "Greater or Equal": 3,
                      "Less Than": 4,
                      "Less or Equal": 5}
    condition_node_name = create_name(name, suffix_name)
    condition_node = cmds.ls(condition_node_name, type='condition')
    if not condition_node:
        condition_node = cmds.createNode("condition", name=condition_node_name)
    else:
        condition_node = condition_node[0]
    # ...set attributes
    cmds.setAttr(condition_node + '.secondTerm', second_term)
    cmds.setAttr(condition_node + '.operation', operation_dict[operation])
    cmds.setAttr(condition_node + '.colorIfTrueR', color_if_true)
    cmds.setAttr(condition_node + '.colorIfFalseR', color_if_false)
    add_face_attr_to_node(condition_node)
    return condition_node


def get_node_attributes(name, print_attrs=False):
    """return information about node attributes
    :param name:
    :param print_attrs:
    """
    attrs_data = {}
    for ea in cmds.listAttr(name):
        try:
            data = cmds.getAttr(name + '.' + ea)
        except RuntimeError:
            continue  # no data values, skip
        except ValueError:
            continue  # no object matches name
        if data:
            attrs_data[ea] = data
    if print_attrs:
        for k, v in attrs_data.items():
            print(k + ':\t' + str(v))
    return attrs_data


def add_source_locator(name, suffix_name="", xform=False):
    """adds a source locator if it does not yet exist for the face controller
    :param name: ()
    :param suffix_name:
    """
    locator_name = 'source' + '_' + create_name(name, suffix_name=suffix_name)
    source = cmds.ls(locator_name)
    if not source:
        source = cmds.spaceLocator(name=locator_name)[0]
    else:
        source = source[0]
    if xform:
        ws_m = cmds.xform(xform, ws=1, m=1, q=1)
        cmds.xform(locator_name, ws=1, m=ws_m)
    add_face_attr_to_node(source)
    return source


def add_grp_node(name, suffix_name="", children=[], parent=""):
    """adds a group node
    :param name: (str) the name to use when creating the new group node
    :param suffix_name: (str) the suffix name to concatenate to the new name
    :param children: (list) the chilcren to parent to the parent arg
    :param parent: (str) the parent to parent the group node into
    """
    grp_node_name = create_name(name, suffix_name)
    grp_node = cmds.ls(grp_node_name, type='transform')
    if not grp_node:
        grp_node = cmds.createNode("transform", name=grp_node_name)
    else:
        grp_node = grp_node[0]
    if parent:
        check_and_parent_node(grp_node, parent)
    if children:
        for ch_node in children:
            check_and_parent_node(ch_node, grp_node)
    return grp_node


def check_face_control_bool(face_ctrl_name):
    """checks for the face controller for connections into the interpolation setup
    :param face_ctrl_name: (str) the controller name to add the custom attribute
    :return: (bool) True if the controller is a face control
    """
    custom_attrs = cmds.listAttr(face_ctrl_name, ud=True)
    for custom_attr in custom_attrs:
        face_attr_name = "{}.{}".format(face_ctrl_name, custom_attr)
        matrix_node = cmds.listConnections(
            face_attr_name, d=True, s=False, type='inverseMatrix')
        if matrix_node:
            return True


def mirror_x(loc_name, skip_name_check=True, flip_rot_x=False, flip_rot_y=False, flip_rot_z=False,
             flip_axis_x=False, flip_axis_y=False, flip_axis_z=False, replace_rot_xz=False):
    """mirror a transform node
    :return: (list, ) mirror matrix
    """
    if not cmds.objExists(loc_name):
        return False
    if skip_name_check:
        right_loc = loc_name.replace('l_', 'r_')
    else:
        right_loc = loc_name
    if not cmds.objExists(right_loc):
        return False
    # mirror transformation x-axis
    mirror_matrix = mirror(right_loc, flip_rot_x=flip_rot_x, flip_axis_x=flip_axis_x, flip_axis_y=flip_axis_y, flip_axis_z=flip_axis_z,
                           flip_rot_y=flip_rot_y, flip_rot_z=flip_rot_z, replace_rot_xz=replace_rot_xz, normal=(1.0, 0.0, 0.0))
    cmds.xform(loc_name, matrix=mirror_matrix)
    return mirror_matrix


def mirror(transfrom_node, normal=(0.0, 1.0, 0.0), flip_rot_x=False, flip_rot_y=False, flip_rot_z=False, replace_rot_xz=False, flip_axis_x=False, flip_axis_y=False, flip_axis_z=False):
    """Mirror a transform node ober the YZ plane axis
    Information:
        matrix = [
        norm-vector(1, 0, 0), 0,  # x-axis direction, and scale
        norm-vector(0, 1, 0), 0,  # y-axis direction, and scale
        norm-vector(0, 0, 1), 0,  # z-axis direction, and scale
        coordinates(0, 0, 0), 1,  # position, relative to parent
        ]    
    :param transfrom_node: (str, ) the node to mirror
    :returns: (list, ) mirrored matrix
    """
    if isinstance(transfrom_node, str):
        transfrom_node = pm.ls(transfrom_node)[0]
    transform_matrix = transfrom_node.__apimfn__().transformation().asMatrix()
    transform_matrix = math_utils.list_from_MMatrix(transform_matrix)
    base_x = transform_matrix[12]  # tx
    base_y = transform_matrix[13]  # ty
    base_z = transform_matrix[14]  # tz
    m = OpenMaya.MMatrix()
    m_flip = OpenMaya.MMatrix()
    m_flip.setToIdentity()
    # ...mirror rotations
    data = math_utils.list_from_MMatrix(m_flip)
    rotation_x = data[0:3]  # x-axis vector
    rotation_y = data[4:7]  # y-axis vector
    rotation_z = data[8:11] # z-axis vector
    # ...mirror against the origin at the grid
    mirror_base = math_utils.mirror_vector_math(
        (base_x, base_y, base_z), (0.0, 0.0, 0.0), normal=normal)
    mirror_x = mirror_base[0]
    mirror_y = mirror_base[1]
    mirror_z = mirror_base[2]
    # ...define flip matrix
    OpenMaya.MScriptUtil.createMatrixFromList([*transform_matrix[0:12],
                                               mirror_x, mirror_y, mirror_z, 1.0],
                                              m_flip)
    # ...flip single rotation axes
    if flip_axis_x:
        rotation_x = math_utils.mirror_vector_math(
            rotation_x, (base_x, base_y, base_z), normal=normal)
    if flip_axis_y:
        rotation_y = math_utils.mirror_vector_math(
            rotation_y, (mirror_x, mirror_y, mirror_z), normal=normal)
        if rotation_y[0] < 0:
            rotation_x = [rotation_y[1], rotation_y[0] * -1, rotation_y[2]]
            rotation_x[0] *= -1
        else:
            rotation_x = [rotation_y[1] * -1,
                          rotation_y[0] * -1, rotation_y[2]]
    if flip_axis_z:
        rotation_z = math_utils.mirror_vector_math(
            rotation_z, (base_x, base_y, base_z), normal=normal)
    if (flip_axis_y or flip_axis_x or flip_axis_z):
        # ...x
        data[0] = rotation_x[0]
        data[1] = rotation_x[1]
        data[2] = rotation_x[2]
        # ...y
        data[4] = rotation_y[0]
        data[5] = rotation_y[1]
        data[6] = rotation_y[2]
        # ...z
        data[8] = rotation_z[0]
        data[9] = rotation_z[1]
        data[10] = rotation_z[2]
    # ...replace rotation axes
    if replace_rot_xz:
        # ...x
        data[0] = rotation_z[0]
        data[1] = rotation_z[1]
        data[2] = rotation_z[2]
        # ...y
        data[4] = rotation_y[0]
        data[5] = rotation_y[1]
        data[6] = rotation_y[2]
        # ...z
        data[8] = rotation_x[0]
        data[9] = rotation_x[1]
        data[10] = rotation_x[2]
    # ...invert rotation axes
    if flip_rot_x:
        data[0] *= -1.0
        data[1] *= -1.0
        data[2] *= -1.0
    if flip_rot_y:
        data[4] *= -1.0
        data[5] *= -1.0
        data[6] *= -1.0
    if flip_rot_z:
        data[8] *= -1.0
        data[9] *= -1.0
        data[10] *= -1.0
    # ...apply transform
    data[12] = mirror_x
    data[13] = mirror_y
    data[14] = mirror_z
    # ...return list from MMatrix
    OpenMaya.MScriptUtil.createMatrixFromList(data, m)
    return math_utils.list_from_MMatrix(m)


def select_locators_for_export():
    """get the locators for export
    """
    locs = cmds.ls(type='locator')
    validated_locs = ()
    for loc in locs:
        loc = cmds.listRelatives(loc, p=True)
        if cmds.listAttr(loc, ud=True):
            validated_locs += loc[0],
    return validated_locs,


def disconnect_incoming_connections(node_name, translate=True, rotate=True, scale=False):
    """disconnect incoming connections into the transform node
    """
    if translate:
        try:
            source_plug = cmds.listConnections(
                node_name + '.translate', s=True, d=False, plugs=True) or []
            check_and_disconnect_attr(source_plug[0], node_name + '.translate')
        except IndexError:
            try:
                # ...translateX
                source_plug = cmds.listConnections(
                    node_name + '.translateX', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.translateX')
            except IndexError:
                pass
            try:
                # ...translateY
                source_plug = cmds.listConnections(
                    node_name + '.translateY', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.translateY')
            except IndexError:
                pass
            try:
                source_plug = cmds.listConnections(
                    node_name + '.translateZ', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.translateZ')
            except IndexError:
                pass
    if rotate:
        try:
            source_plug = cmds.listConnections(
                node_name + '.rotate', s=True, d=False, plugs=True) or []
            check_and_disconnect_attr(source_plug[0], node_name + '.rotate')
        except IndexError:
            try:
                # ...rotateX
                source_plug = cmds.listConnections(
                    node_name + '.rotateX', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.rotateX')
            except IndexError:
                pass
            try:
                # ...rotateY
                source_plug = cmds.listConnections(
                    node_name + '.rotateY', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.rotateY')
            except IndexError:
                pass
            try:
                # ...rotateZ
                source_plug = cmds.listConnections(
                    node_name + '.rotateZ', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.rotateZ')
            except IndexError:
                pass
    if scale:
        try:
            source_plug = cmds.listConnections(
                node_name + '.scale', s=True, d=False, plugs=True) or []
            check_and_disconnect_attr(source_plug[0], node_name + '.scale')
        except IndexError:
            try:
                # ...scaleX
                source_plug = cmds.listConnections(
                    node_name + '.scaleX', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.scaleX')
            except IndexError:
                pass
            try:
                # ...scaleY
                source_plug = cmds.listConnections(
                    node_name + '.scaleY', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.scaleY')
            except IndexError:
                pass
            try:
                # ...scaleZ
                source_plug = cmds.listConnections(
                    node_name + '.scaleZ', s=True, d=False, plugs=True) or []
                check_and_disconnect_attr(
                    source_plug[0], node_name + '.scaleZ')
            except IndexError:
                pass
    return True


def get_attr_selected_shape(face_ctrl_name, shape_attr=SHAPE_ATTR):
    """check shape attribute, this attribute is for quality of life for the face rig to show how many shapes it is supposed to drive
    :param face_ctrl_name: <str> the controller name to check the interpolation
    :param shape_attr: <str> default: "shapes" attribute to show what linked interpolations are connected to this controller
    :return: (list) enumeration attribute string names
    """
    if cmds.ls(face_ctrl_name + '.' + shape_attr):
        enum_strings = cmds.attributeQuery(
            shape_attr, node=face_ctrl_name, listEnum=True)[0].split(':')
        return enum_strings
    else:
        # Attribute name not recognized
        return []


def add_shape_enum(transform_node, shape_name, shape_attr=SHAPE_ATTR):
    """add shape enumeration attribute names to a controller transform node
    :param transform_node: <str> the controller name to add the enum attribute
    :param shape_name: <str> add this enumeration name to the attribute
    :param shape_attr: <str> the enumeration attribute name to create to the transform_node
    """
    face_enum = get_attr_selected_shape(transform_node, shape_attr)
    if face_enum and not shape_name in face_enum:
        face_enum.append(shape_name)
        cmds.addAttr('{}.{}'.format(transform_node, shape_attr),
                     at='enum', en=':'.join(face_enum), edit=True)
    elif face_enum and shape_name in face_enum:
        length_of_attrs = len(
            get_attr_selected_shape(transform_node, shape_attr))
        return length_of_attrs
    else:
        cmds.addAttr(transform_node, ln=shape_attr, at="enum",
                     en="off:{}:".format(shape_name))
        cmds.setAttr("{}.{}".format(transform_node, shape_attr), keyable=True)
    length_of_attrs = len(get_attr_selected_shape(transform_node, shape_attr))
    return length_of_attrs


def check_and_connect_attrs(source_attr, dest_attr, force=False, silence=True):
    """Warning free connections of the attributes
    :param source_attr: (str) source full attribute name
    :param dest_attr: (str) destomaton full attribute name
    :param force: (bool) force the connection when there is an already pre-existing connection
    """
    if not cmds.isConnected(source_attr, dest_attr):
        try:
            return cmds.connectAttr(source_attr, dest_attr, force=force)
        except RuntimeError:
            # attribute already connected
            existing_connection = cmds.listConnections(
                dest_attr, s=True, d=False, plugs=True)
            if not silence:
                print("Attribute is already connected, Debug: {} >> {}".format(
                    source_attr, existing_connection))
    else:
        return True


def check_and_parent_node(transform_node, parent_node):
    """checks the transform node for the parent name and parents it,
    so we can avoid the RuntimeError: Maya command error
    :param transform_node: (str) transform node to parent
    :param parent_node: (str) parent_node to parent into
    :return: (list) parent_nodes
    """
    if not parent_node:
        return False
    parent_nodes = cmds.listRelatives(transform_node, p=True)
    if not parent_nodes:
        cmds.parent(transform_node, parent_node)
    elif parent_node not in parent_nodes:
        cmds.parent(transform_node, parent_node)
    return parent_nodes


def check_and_disconnect_attr(source_attr, dest_attr):
    """Warning free disconnection of attributes
    :param source_attr: source full attribute name
    :param dest_attr: target full attribute name
    :return: (bool) True for success
    """
    if "." not in dest_attr:
        connections = cmds.listConnections(source_attr, d=True, plugs=True)
        if not connections:
            return False
        for con in connections:
            if dest_attr in con:
                cmds.disconnectAttr(source_attr, con)
    else:
        cmds.disconnectAttr(source_attr, dest_attr)
    return True


def get_transform_vector(transform_name):
    """returns the world space vector position from transform object provided
    :param transform_name:(str)
    :return: datatype.Vector
    """
    return dt.Vector(cmds.xform(transform_name, ws=1, t=1, q=1))


def get_vector_between_points(transform_a, transform_b, transform_c):
    """calculate the percentage distance of transform C vector against AB vector
    :param transform_a: source transform object
    :param transform_b: end transform object
    :param transform_c: target transform object
    :return: (tuple, ) final_vec, percent
    """
    ta_vec = get_transform_vector(transform_a)
    tb_vec = get_transform_vector(transform_b)
    tc_vec = get_transform_vector(transform_c)
    # ...calculate the percent the target_c is in relation to the total distance
    orig_vec = tb_vec - ta_vec
    orig_mag = orig_vec.length()
    target_vec = tc_vec - ta_vec
    target_mag = target_vec.length()
    percent = target_mag / orig_mag
    if percent > 1:
        percent = 1.0
    calc_vec = orig_vec * percent
    final_vec = ta_vec + calc_vec
    # ...return the results
    return final_vec, percent


def get_vector_info_between_two_points(transform_a, transform_b):
    """get the vector information between the two transform objects
    :param transform_a: (str,) transform object origin
    :param transform_b: (str,) transform object target
    :returns: (tuple) orig_vec, normalized_vec, orig_length, step_length
    """
    vec_1 = dt.Vector(cmds.xform(transform_a, ws=1, t=1, q=1))
    vec_2 = dt.Vector(cmds.xform(transform_b, ws=1, t=1, q=1))
    orig_vec = vec_2 - vec_1
    normalized_vec = copy.copy(orig_vec)
    normalized_vec.normalize()
    orig_length = orig_vec.length()
    step_length = orig_length / 10
    return orig_vec, normalized_vec, orig_length, step_length


def create_measurement_curve_from_transform(name, suffix_name="", source_transform="", target_transform=""):
    """
    :param name: (str) name of the matrix-interpolation curve
    :parm suffix_name: (str) the suffix name to concatenate the naming string
    :param source_transform: (str) the source transform to start the curve CV
    :param target_transform: (str) the target transform to end the curve CV
    :return: (str) curve_node
    """
    curve_name = create_name(name, suffix_name=suffix_name + '_VISUAL_CRV')
    # ...check curve node
    curve_node = cmds.ls(curve_name)
    if curve_node:
        curve_node = curve_node[0]
    if not cmds.filterExpand(curve_node, sm=9):
        position_a = cmds.xform(source_transform, ws=1, t=1, q=1)
        position_b = cmds.xform(target_transform, ws=1, t=1, q=1)
        curve_node = cmds.curve(name=curve_name, degree=1, point=(
            position_a, position_b), knot=(0, 1))
        add_curve_attr_to_node(curve_node)
    return curve_node


def hide_channels(transform_node, t=True, r=True, s=True, v=True):
    """Hide the attribute channels on the given transform_node
    :param t: (bool) hides the translation channel
    :param r: (bool) hides the rotation channel
    :param s: (bool) hides the scale channel
    :param v: (bool) hides the visibility channel
    """
    if t:
        cmds.setAttr(transform_node + '.tx', k=False, lock=True)
        cmds.setAttr(transform_node + '.ty', k=False, lock=True)
        cmds.setAttr(transform_node + '.tz', k=False, lock=True)
    if r:
        cmds.setAttr(transform_node + '.rx', k=False, lock=True)
        cmds.setAttr(transform_node + '.ry', k=False, lock=True)
        cmds.setAttr(transform_node + '.rz', k=False, lock=True)
    if s:
        cmds.setAttr(transform_node + '.sx', k=False, lock=True)
        cmds.setAttr(transform_node + '.sy', k=False, lock=True)
        cmds.setAttr(transform_node + '.sz', k=False, lock=True)
    if v:
        cmds.setAttr(transform_node + '.v', k=False, lock=True)
    return True


def add_and_connect_curve_attributes_to_transform(control_node, curve_node):
    """connect the color attributes to attach to the curve's override transform
    :param control_node: (str,) the control node to hold the attributes to
    :parm curve_node: (str,) the curve node to affect the override attribute into
    """
    print('Adding Curve Attributes: {}, {}'.format(control_node, curve_node))
    color_attr_name = "curveColor"
    line_width_attr_name = "lineWidth"
    color_dict = {"gray": 0,
                  "black": 1,
                  "midnightGray": 2,
                  "lightGray": 3,
                  "cherryRed": 4,
                  "navyBlue": 5,
                  "ceruleanBlue": 6,
                  "jungleGreen": 7,
                  "plumPurple": 9,
                  "magneta": 10,
                  "bronze": 11,
                  "chocolateBrown": 12,
                  "siennaBrown": 13,
                  "red": 14,
                  "green": 15,
                  "cobaltBlue": 16,
                  "white": 17,
                  "yellow": 18,
                  "cyan": 19,
                  "green": 20,
                  "pink": 21,
                  "paleYellow": 22,
                  "jadeGreen": 23,
                  "mustardYelow": 25,
                  "ochreBrown": 24,
                  "verdantGreen": 26,
                  "emeraldGreen": 27,
                  "aquaBlue": 28,
                  "azureBlue": 29,
                  "purple": 30,
                  "magneta": 31}
    # ..color attr name
    if not cmds.ls(control_node + '.' + color_attr_name):
        cmds.addAttr(control_node, ln=color_attr_name,
                     at="enum", en=":".join(color_dict.keys()))
        cmds.setAttr(control_node + '.' + color_attr_name, k=True)
    cmds.setAttr(curve_node + '.overrideEnabled', True)
    check_and_connect_attrs(control_node + '.' +
                            color_attr_name, curve_node + '.overrideColor')
    # ..lineWidth attr
    if not cmds.ls(control_node + '.' + line_width_attr_name):
        cmds.addAttr(control_node, ln=line_width_attr_name,
                     at='float', min=-1.0, max=10.0)
        cmds.setAttr(control_node + '.' + line_width_attr_name, k=True)
    check_and_connect_attrs(control_node + '.' +
                            line_width_attr_name, curve_node + '.lineWidth')
    return (color_attr_name, list(color_dict.keys())), (line_width_attr_name, -1.0, 10.0),


def create_measurement_curve_from_vectors(name, suffix_name="", vector_a=[], vector_b=[]):
    """
    :param name: (str,) name of the measurement curve system
    :param suffix_name: (str) the suffix name to concatenate to the name
    :param vector_a: (list) xyz translateA 3D coord
    :param vector_b: (list) xyz translateB 3D coord
    :return: (str) curve name
    """
    # create a new curve from vector_a to vector_b
    curve_name = create_name(name, suffix_name=suffix_name + '_VISUAL_CRV')
    cmds.curve(name=curve_name, degree=1, point=(
        vector_a, vector_b), knot=(0, 1))
    return curve_name


def create_interpolation(driver_transform, source_transform, name="", target_transforms=[], add_groups=True):
    """creates an interpolation math at a single source transform and a multiple-transform objects
    :param name: name of the single matrix-interpolation 
    :param driver_transform: <str> the transform that will hold the driver attributes connection
    :param source_transform: <str> the transform that will have the ParentOffsetMatrix connection
    :param attribute_control: <str> the transform that will hold the interpolation attributes
    :param target_transforms: <list> the target transforms to interpolate into, ordered by index
    :returns: (dict) dictionary of nodes
    """
    # ...store attrs
    node_dict = {}
    node_dict[driver_transform] = ()
    # ...add the shape enumerator attribute
    attr_index = add_shape_enum(driver_transform, name)
    condition_node = add_condition_node(driver_transform, name + '_VIS', second_term=attr_index-1,
                                        operation="equal", color_if_true=1.0, color_if_false=0.0)
    add_face_attr_to_node(condition_node)
    # ...check the parent node on the source transform, else the parent offset shapes will not work correctly!
    if not check_parent(source_transform):
        add_driver_transform(source_transform, name='ParentXform')
    # ...add a mult matrix node to zero out the matrix transforms of the source location of the face control
    mult_node = add_mult_matrix_node(
        source_transform, suffix_name='Interpolate_matrixMult')
    # ...get connected indices
    try:
        attrs = cmds.listAttr('{}.matrixIn[*]'.format(mult_node))
        input_index = int(find_digit.findall(attrs[-1])[0])
        input_index += 1
    except ValueError:
        input_index = 0
    initial_transform = target_transforms[0]
    # ...rename initial
    # initial_transform = cmds.rename(initial_transform, source_transform + '_' + name)
    target_transforms.pop(0)
    interpolate_math = (10 / len(target_transforms))
    last_value = 0
    blend_matrix_node = add_blend_matrix_node('{}_{}'.format(
        driver_transform, name), suffix_name="Interpolate")
    # ... connect the driver transform shapes into the first term condition node
    check_and_connect_attrs(driver_transform + '.shapes',
                            condition_node + '.firstTerm')
    # ...create driver face attribute
    if not cmds.ls(driver_transform + '.' + name):
        cmds.addAttr(driver_transform, ln=name, min=0.0, max=10.0, at='float')
        cmds.setAttr(driver_transform + '.' + name, keyable=True)
    # ...special consideration for the first blendMatrix: have the source be connected as a target
    check_and_connect_attrs('{}.matrixSum'.format(
        mult_node), '{}.offsetParentMatrix'.format(source_transform))
    check_and_connect_attrs('{}.outputMatrix'.format(
        blend_matrix_node), '{}.matrixIn[{}]'.format(mult_node, input_index))
    renamed_targets = ()
    for idx, target_tfm in enumerate(target_transforms):
        # ...check and rename the targets
        # target_tfm = cmds.rename(target_tfm, driver_transform + '_' + target_tfm)
        renamed_targets += target_tfm,
        # ...connect attribute
        check_and_connect_attrs(
            condition_node + '.outColorR', target_tfm + '.visibility')
        # ...connect the target matrices
        check_and_connect_attrs('{}.xformMatrix'.format(
            target_tfm), '{}.target[{}].targetMatrix'.format(blend_matrix_node, idx))
        # ...create RemapValue node to connect the driver attributes into
        weight_remap_node = add_remap_value_node(
            target_tfm, suffix_name='REMAP')
        # ...calculate remap values on min/ max based on the number of target transforms
        if idx == 0:
            set_float_attr(weight_remap_node, 'inputMin', 0.0)
        else:
            set_float_attr(weight_remap_node, 'inputMin', last_value)
        last_value += interpolate_math
        set_float_attr(weight_remap_node, 'inputMax', last_value)
        check_and_connect_attrs('{}.{}'.format(
            driver_transform, name), '{}.inputValue'.format(weight_remap_node))
        check_and_connect_attrs('{}.outValue'.format(
            weight_remap_node), '{}.target[{}].weight'.format(blend_matrix_node, idx))
        # store this attribute for later use
        node_dict[driver_transform] += weight_remap_node,
    # ...group the target locators
    if add_groups:
        control_grp_node = add_grp_node(
            name=driver_transform + "_FACE_CONTROLS", suffix_name="TARGETS_GRP")
        face_shape_grp_node = add_grp_node(
            name=driver_transform + '_' + name, suffix_name="TARGETFACE_GRP", parent=control_grp_node)
        set_position(face_shape_grp_node, initial_transform)
        check_and_parent_node(renamed_targets, face_shape_grp_node)
        check_and_parent_node(initial_transform, face_shape_grp_node)
        # ... parent the children into the face shape_grp node
        for ch_node in renamed_targets:
            check_and_parent_node(ch_node, face_shape_grp_node)
        add_and_connect_message_attr(
            face_shape_grp_node, initial_transform, attr_name='start_transform')
        add_and_connect_message_attr(
            face_shape_grp_node, renamed_targets[-1], attr_name='end_transform')
    # ...create visualization curves
    create_curves(source_transform + '_' + name, initial_transform,
                  renamed_targets, connect_to_vis_attr=(condition_node + '.outColorR'))
    # ...connect to the message attributes on the targets
    return node_dict, control_grp_node


def check_parent(node):
    """checks if there is a parent node, located in the same space as the argument node
    """
    par_node = cmds.listRelatives(node, p=True, c=False)
    if not par_node:
        return False
    return True


def set_position(node, target_transform):
    """
    """
    m = cmds.xform(target_transform, m=1, ws=1, q=1)
    cmds.xform(node, m=m, ws=1)
    return m


def edit_interpolation(controller_transform, name="", shape_attr=SHAPE_ATTR, transforms=[], add=False, remove=False):
    """Rearrange the transform targets for a given shape name. This will delete the old system and create a new system with reorganized targets affecting the controller transform
    :param shape_attr:
    :param transforms:
    :param add:
    :param remove:
    """
    if not add and not remove:
        answer = cmds.confirmDialog(b=("Ok"), title="Please select a command type",
                                    message="Please identify if you'd like to add or remove targets")
        raise ValueError("Command not chosen.")
    if not name:
        shape_enum = get_attr_selected_shape(controller_transform, shape_attr)
        name = shape_enum[get_float_attr_value(
            controller_transform, shape_attr)]
        answer = cmds.confirmDialog(b=("Ok", "Cancel"), title="Create Interpolation For Selected Shape?",
                                    message="Would you like to Continue editing this interpolation shape?")
        if answer == 'Cancel':
            return None
    # get the target objects:
    # ..grab the existing grp node by checking connections
    existing_targets = get_existing_targets(
        controller_transform, shape_name=shape_attr)
    blend_matrix_node_name = create_name('{}_{}'.format(
        controller_transform, name), suffix_name="Interpolate")
    condition_node_name = create_name(controller_transform, name + '_VIS')
    if not blend_matrix_node_name:
        raise IntentionalNoBlendMatrixNodeError(
            "No Blendmatrix node found for name: {}".format(name))
    if add:
        targets = existing_targets + transforms
        re_organized_targets = confirm_selected_targets(targets)
        if not re_organized_targets:
            raise ValueError('You need to have targets to continue!')
        # ...clear the current connections coming into the blend matrix node:
        _disconnect_blend_matrix_targets(blend_matrix_node_name)
        # ...reconnect to the blend matrix node
        _connect_blend_matrix_targets(
            blend_matrix_node_name, re_organized_targets, connect_to_vis=condition_node_name + '.outColorR')
    if remove:
        for r_target in transforms:
            existing_targets.pop(existing_targets.index(r_target))
        re_organized_targets = confirm_selected_targets(transforms)
        # ...clear the current connections coming into the blend matrix node:
        _disconnect_blend_matrix_targets(blend_matrix_node_name)
        # ...reconnect to the blend matrix node
        _connect_blend_matrix_targets(
            blend_matrix_node_name, re_organized_targets, connect_to_vis=condition_node_name + '.outColorR')
    return True


def _connect_blend_matrix_targets(blend_matrix_node, targets, connect_to_vis=None):
    for idx, target_tfm in enumerate(targets):
        # ...connect attribute
        check_and_connect_attrs(connect_to_vis + '.outColorR', target_tfm)
        # ...connect the target matrices
        check_and_connect_attrs('{}.xformMatrix'.format(
            target_tfm), '{}.target[{}].targetMatrix'.format(blend_matrix_node, idx))


def _disconnect_blend_matrix_targets(blend_matrix_node):
    sources = cmds.listConnections(
        blend_matrix_node, source=True, destination=False, plugs=True)
    for s_plug in sources:
        t_plug = cmds.listConnections(
            s_plug, d=True, s=False, type='blendMatrix', plugs=True)
        if '.target' in t_plug:
            cmds.disconnectAttr(s_plug, t_plug)
    return True


def get_float_attr_value(node, attr_name):
    """returns the float attribute from a node
    """
    float_attr_value = cmds.getAttr('{}.{}'.format(node, attr_name))
    return float_attr_value


def set_float_attr(node, attr_name, attr_value):
    if not check_attr(node, attr_name):
        raise NameError('Attribute does not exist!')
    if '.' not in attr_name:
        attr_name = '{}.{}'.format(node, attr_name)
    cmds.setAttr(attr_name, attr_value)


def get_existing_targets(ctrl_node, shape_name=SHAPE_ATTR):
    """get existing targets from the controller name given
    :param ctrl_node: (str,)
    :param shape_name: (str,)
    """
    get_targets = cmds.listConnections(
        ctrl_node + '.' + shape_name, d=True, s=False)
    interpolation_node = cmds.listConnections(
        get_targets[0], d=True, s=False)[0]
    all_src_plugs = cmds.listConnections(
        interpolation_node, s=True, d=False, plugs=True)
    targets_list = [a.split('.')[0]
                    for a in all_src_plugs if '.worldMatrix' in a]
    if not targets_list:
        grp_node = '{}_TARGETFACE_GRP'.format(shape_name)
        targets_list = get_children_nodes(grp_node)
    return targets_list


def get_children_nodes(grp_node):
    return list(set(cmds.filterExpand(grp_node, selectionMask=22, fullPath=False, expand=True)))


def check_driver_transform(driver_transform, shape_attr=SHAPE_ATTR):
    """checks the driver transform for 'shapes' attribute
    """
    check_transform = False
    try:
        check_transform = cmds.listAttr(
            driver_transform, ud=True).index(shape_attr)
    except ValueError:
        # 'shapes' is not in list
        pass
    return check_transform


def add_and_connect_message_attr(system_node, message_to, attr_name=''):
    if not check_attr(system_node, attr_name):
        add_message_attr(system_node, attr_name)
    if not check_attr(message_to, attr_name):
        add_message_attr(message_to, attr_name)
    check_and_connect_attrs(system_node + '.' + attr_name,
                            message_to + '.' + attr_name)


def get_start_transform(system_node):
    return cmds.listConnections(system_node + '.start_transform', d=True, s=False)


def get_end_transform(system_node):
    return cmds.listConnections(system_node + '.end_transform', d=True, s=False)


def add_message_attr(node, attr_name):
    cmds.addAttr(node, ln=attr_name, at='message')


def check_attr(node, attr_name):
    return bool(cmds.ls('{}.{}'.format(node, attr_name)))


def create_curves(name, source_transform, target_transforms=[], parent="", connect_to_vis_attr=""):
    """Creates the curves necessary for the visualization of target transforms
    :param name: (str,) the name of the curve system to create
    :param source_transform: (str,) the source transform to start the curve from
    :param target_transforms: (tuple, list,) the transform targets to attach curves to
    :param parent: (str,) parent the system group to this node
    :param connect_to_vis_attr: (str,) connect the visibility of the system to this attribute
    """
    # ...check target array the reason why it cannot do this
    if source_transform in target_transforms:
        t_index = target_transforms.index(source_transform)
        target_transforms.pop(t_index)
    # ...create visualization curves
    orig_curve_node = create_measurement_curve_from_transform(
        name, suffix_name=source_transform, source_transform=source_transform, target_transform=target_transforms[-1])
    if connect_to_vis_attr:
        check_and_connect_attrs(connect_to_vis_attr,
                                orig_curve_node + '.visibility')
    add_curve_attr_to_node(orig_curve_node)
    hide_channels(orig_curve_node, v=False)
    vec_node_1 = connect_to_cv_point(
        target_transforms[-1], orig_curve_node, name=name, index=0)
    add_curve_attr_to_node(vec_node_1)
    vec_node_2 = connect_to_cv_point(
        source_transform, orig_curve_node, name=name, index=1)
    add_curve_attr_to_node(vec_node_2)
    # ..create an organizational group_node
    face_crv_grp_node = add_grp_node(name, suffix_name="FACECRV_GRP")
    check_and_parent_node(orig_curve_node, face_crv_grp_node)
    color_attr, line_width_attr = add_and_connect_curve_attributes_to_transform(
        face_crv_grp_node, orig_curve_node)
    check_and_parent_node(face_crv_grp_node, parent)
    for target_tfm in target_transforms[:-1]:
        mid_vector, mid_percent = get_vector_between_points(
            source_transform, target_transforms[-1], target_tfm)
        target_vec = get_transform_vector(target_tfm)
        measure_curve = create_measurement_curve_from_vectors(
            name, suffix_name=target_tfm, vector_a=mid_vector, vector_b=target_vec)
        hide_channels(measure_curve, v=False)
        check_and_parent_node(measure_curve, face_crv_grp_node)
        if connect_to_vis_attr:
            check_and_connect_attrs(
                connect_to_vis_attr, measure_curve + '.visibility')
        add_curve_attr_to_node(measure_curve)
        bc_node = add_blend_colors_node(
            name, suffix_name=target_tfm + 'A', percent=mid_percent)
        add_curve_attr_to_node(bc_node)
        cmds.connectAttr(vec_node_1 + '.output', bc_node + '.color1')
        cmds.connectAttr(vec_node_2 + '.output', bc_node + '.color2')
        cmds.connectAttr(bc_node + '.output',
                         measure_curve + '.controlPoints[0]')
        connect_to_cv_point(target_tfm, measure_curve, name=name, index=1)
        add_and_connect_curve_attributes_to_transform(
            face_crv_grp_node, measure_curve)
    choice_color = random.choice(color_attr[1])
    choice_color = color_attr[1].index(choice_color)
    choice_thickness = random.randint(line_width_attr[1], line_width_attr[2])
    cmds.setAttr('{}.{}'.format(
        face_crv_grp_node, color_attr[0]), choice_color)
    cmds.setAttr('{}.{}'.format(face_crv_grp_node,
                 line_width_attr[0]), choice_thickness)
    return True


def set_compound_matrix_node(compose_matrix_node, xform_t=None, xform_ro=None, xform_s=None, invert_t=False):
    """set xform values for the compound matrix node for mathematical operations
    """
    if xform_t:
        cmds.setAttr(compose_matrix_node + '.inputTranslateX', xform_t[0])
        cmds.setAttr(compose_matrix_node + '.inputTranslateY', xform_t[1])
        cmds.setAttr(compose_matrix_node + '.inputTranslateZ', xform_t[2])
    if invert_t:
        cmds.setAttr(compose_matrix_node + '.inputTranslateX', -1 * xform_t[0])
        cmds.setAttr(compose_matrix_node + '.inputTranslateY', -1 * xform_t[1])
        cmds.setAttr(compose_matrix_node + '.inputTranslateZ', -1 * xform_t[2])
    if xform_ro:
        # rotates
        cmds.setAttr(compose_matrix_node + '.inputRotateX', xform_ro[0])
        cmds.setAttr(compose_matrix_node + '.inputRotateY', xform_ro[1])
        cmds.setAttr(compose_matrix_node + '.inputRotateZ', xform_ro[2])
    if xform_s:
        # scale
        cmds.setAttr(compose_matrix_node + '.inputScaleX', xform_s[0])
        cmds.setAttr(compose_matrix_node + '.inputScaleY', xform_s[1])
        cmds.setAttr(compose_matrix_node + '.inputScaleZ', xform_s[2])
    return True


def create_linear_interpolate(start_transform, end_transform, driven_transforms=[], name="", aim_at_end=True):
    """creates a linear interpolation of transforms between the two points
    :param name: (str,) the name to use for this system
    :param start_transform: (str,)
    :param end_transform: (str,)
    :param driven_transforms: (tuple, list,) 
    """
    outbound_matrix_attr = '.xformMatrix'
    if not name:
        cmds.warning('Please name your interpolation')
        return False
    system_node_name = "{}_interpolate".format(name)
    # ...add a system node
    system_node = add_grp_node(system_node_name)
    # get interpolation math
    interpolate_math = 1.0/len(driven_transforms)
    last_value = 0
    # start xform
    # ..create the start offset matrix node
    start_compose_matrix_node = add_compose_matrix_node(
        start_transform, suffix_name="StartMatrixOffset")
    start_mult_matrix_node = add_mult_matrix_node(
        start_transform, suffix_name="StartOffsetMultMatrix")
    check_and_connect_attrs(
        start_transform + outbound_matrix_attr, start_mult_matrix_node + '.matrixIn[0]')
    check_and_connect_attrs(start_compose_matrix_node +
                            '.outputMatrix', start_mult_matrix_node + '.matrixIn[1]')
    # ..create the end offset matrix node
    end_mult_matrix_node = add_mult_matrix_node(
        end_transform, suffix_name="EndOffsetMultMatrix")
    check_and_connect_attrs(
        end_transform + outbound_matrix_attr, end_mult_matrix_node + '.matrixIn[0]')
    check_and_connect_attrs(start_compose_matrix_node +
                            '.outputMatrix', end_mult_matrix_node + '.matrixIn[1]')
    # ...attr names
    attr_names = ()
    # connect the starting and end transform matrices
    for ea_transform in driven_transforms:
        cmds.parent(ea_transform, system_node)
        par_node = add_driver_transform(ea_transform, suffix_name="DRV")
        # ...
        vector, percent = get_vector_between_points(
            start_transform, end_transform, ea_transform)
        if percent > 1.0:
            percent = 1.0
        blend_matrix_node = add_blend_matrix_node(
            ea_transform, suffix_name="interpolate")
        # ...connect the composed matrix offsets into the blend matrix start and end targets
        check_and_connect_attrs(
            start_mult_matrix_node + '.matrixSum', blend_matrix_node + '.inputMatrix')
        check_and_connect_attrs(
            end_mult_matrix_node + '.matrixSum', blend_matrix_node + '.target[0].targetMatrix')
        # add an offset to the original joint values
        compose_matrix_node = add_compose_matrix_node(
            ea_transform, suffix_name="MatrixOffset")
        # set_compound_matrix_node(compose_matrix_node, get_orig_xform_t, get_xform_ro, invert_t=True)
        mult_matrix_node = add_mult_matrix_node(
            ea_transform, suffix_name="TargetOffsetMatrix")
        check_and_connect_attrs(
            compose_matrix_node + '.outputMatrix', mult_matrix_node + '.matrixIn[0]')
        check_and_connect_attrs(
            blend_matrix_node + '.outputMatrix', mult_matrix_node + '.matrixIn[1]')
        if aim_at_end:
            aim_matrix_node = add_aim_matrix_node(
                ea_transform, suffix_name="interpolateAim")
            set_matrix_attr(aim_matrix_node, [
                            1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 10.0, 0.0, 1.0])
            check_and_connect_attrs(
                end_mult_matrix_node + '.matrixSum', aim_matrix_node + '.primaryTargetMatrix')
            check_and_connect_attrs(
                aim_matrix_node + '.outputMatrix', par_node + '.offsetParentMatrix')
            check_and_connect_attrs(
                mult_matrix_node + '.matrixSum', aim_matrix_node + '.inputMatrix')
            cmds.setAttr(aim_matrix_node + '.envelope', percent)
        else:
            check_and_connect_attrs(
                mult_matrix_node + '.matrixSum', ea_transform + '.offsetParentMatrix')
        cmds.setAttr(blend_matrix_node + '.envelope', percent)
        # ...zero joint transforms
        zero_transform_values(par_node, translate=True,
                              scale=True, rotate=True)
        last_value += interpolate_math
        # ...add attributes
        cmds.addAttr(start_transform, ln=ea_transform,
                     min=0, max=1, dv=percent)
        cmds.setAttr(start_transform + '.' + ea_transform, k=True)
        cmds.connectAttr(start_transform + '.' + ea_transform,
                         blend_matrix_node + '.envelope')
        attr_names += start_transform + '.' + ea_transform,
    # finish the function and return the system node
    return system_node, attr_names


def confirm_selected_targets(targets):
    """open the ui to shuffle the targets in their right places"""
    organizer_tool.openUI(targets)
    organized_target_list = organizer_tool.get_organized_list()
    return organized_target_list


def check_and_delete_system(controller_transform, shape_name):
    """Checks and deletes the currect system, minus the multiply matrix connected to the parentOffsetMatrix to the driven transform
    :param controller_transform: (str,) the driving transform that holds the attributes
    :param shape_name: (str,) the shape name to check and delete
    :returns: (bool,) 
    """
    get_targets = get_destination_connection(controller_transform, shape_name)
    interpolation_node = get_destination_connection(get_targets[0], 'outValue')
    all_src_plugs = get_source_connection_plugs(interpolation_node[0], '')
    remap_nodes = [a.split('.')[0]
                   for a in all_src_plugs if '.worldMatrix' not in a]
    print(remap_nodes)
    cmds.delete(remap_nodes + interpolation_node)
    # ...delete target curves
    grp_node = "{}_FACECRV_GRP".format(shape_name)
    check_and_delete_node(grp_node)
    return True


def check_and_delete_node(grp_node):
    """
    """
    if cmds.objExists(grp_node):
        cmds.delete(grp_node)


def get_source_connection(node, attr_name, plugs=False):
    """returns a list of source connections into the node
    :param attr_name:
    :parm node:
    :param plugs:
    """
    return cmds.listConnections('{}.{}'.format(node, attr_name), s=True, d=False, plugs=plugs)


def get_source_connection_plugs(node, attr_name, plugs=True):
    """returns source connection plugs into the node
    :param attr_name:
    :parm node:
    :param plugs:
    """
    return get_source_connection(node, attr_name, plugs=plugs)


def get_destination_connection(node, attr_name, plugs=False):
    """returns destination connections into the node
    :param attr_name:
    :parm node:
    :param plugs:
    """
    return cmds.listConnections('{}.{}'.format(node, attr_name), s=False, d=True, plugs=plugs)


def get_destination_connection_plugs(node, attr_name, plugs=True):
    """returns destination connection plugs into the node
    :param attr_name:
    :parm node:
    :param plugs:
    """
    return get_destination_connection(node, attr_name, plugs=plugs)


def _check_target_node(node):
    """checks the target node for vector connections
    """
    vector_node = cmds.listConnections(
        node + 'worldMatrix[0]', destination=True, source=False, type='vectorProduct')
    return vector_node


def create_spline_interpolate(start_transform, end_transform, driven_transforms=[], name="", aim_at_end=True, attach=True, control_node=None, maintain_offset=True):
    """
    :param attach: <bool> attach the driven transforms to the resultant spline locators
    :param start_transform:
    :param end_transform:
    :param driven_transforms:
    :param name:
    :param aim_at_end:
    :param attach:
    :param control_node:
    :param maintain_offset:
    """
    if not name:
        raise ValueError(
            "Please enter a name for this linear interpolation system")
    if not control_node:
        control_node = start_transform
    # ...t float add attributes
    upper_attr_name = name + 'upper_interpolate'
    lower_attr_name = name + 'lower_interpolate'
    middle_attr_name = name + 'middle_interpolate'
    cmds.addAttr(control_node, ln=upper_attr_name,
                 at='float', min=-1.0, max=1.0, keyable=True)
    cmds.setAttr(control_node + '.' + upper_attr_name, k=True)
    cmds.addAttr(control_node, ln=middle_attr_name,
                 at='float', min=-1.0, max=1.0, keyable=True)
    cmds.setAttr(control_node + '.' + middle_attr_name, k=True)
    cmds.addAttr(control_node, ln=lower_attr_name,
                 at='float', min=-1.0, max=1.0, keyable=True)
    cmds.setAttr(control_node + '.' + lower_attr_name, k=True)
    percentages = get_percent_values_from_transforms(
        start_transform, end_transform, driven_transforms=driven_transforms)
    upper_start_loc = add_source_locator(
        start_transform + '_{}Upper'.format(name), xform=start_transform)
    upper_end_loc = add_source_locator(
        end_transform + '_{}Upper'.format(name), xform=end_transform)
    upr_sys_node, upper_locators, upr_attr_names = create_locator_linear_interpolate(
        upper_start_loc, upper_end_loc, driven_transforms=driven_transforms, name=name + 'Upper', aim_at_end=aim_at_end)
    # ...create different drivers for the "lower locators"
    lower_start_loc = add_source_locator(
        start_transform + '_{}Lower'.format(name), xform=start_transform)
    lower_end_loc = add_source_locator(
        end_transform + '_{}Lower'.format(name), xform=end_transform)
    # ...constrain the end to the start
    cmds.parentConstraint(lower_end_loc, lower_start_loc, mo=True)
    lwr_sys_node, lower_locators, lwr_attr_names = create_locator_linear_interpolate(
        lower_start_loc, lower_end_loc, driven_transforms=driven_transforms, name=name + 'Lower', aim_at_end=aim_at_end)
    # ...lower interpolation attribute
    for idx, attr_name in enumerate(lwr_attr_names):
        add_float_smooth_interpolation_at_value(
            control_node + '.' + lower_attr_name, attr_name, value=0.0, driver_value=-1.0)
        add_float_smooth_interpolation_at_value(
            control_node + '.' + lower_attr_name, attr_name, value=percentages[idx], driver_value=0.0)
        add_float_smooth_interpolation_at_value(
            control_node + '.' + lower_attr_name, attr_name, value=1.0, driver_value=1.0)
    # ...upper interpolation attribute
    for idx, attr_name in enumerate(upr_attr_names):
        add_float_smooth_interpolation_at_value(
            control_node + '.' + upper_attr_name, attr_name, value=0.0, driver_value=-1.0)
        add_float_smooth_interpolation_at_value(
            control_node + '.' + upper_attr_name, attr_name, value=percentages[idx], driver_value=0.0)
        add_float_smooth_interpolation_at_value(
            control_node + '.' + upper_attr_name, attr_name, value=1.0, driver_value=1.0)
    # ...create the spline group
    grp_node = add_grp_node(name='lerpSys_' + name, suffix_name="GRP")
    # ...create middle locators
    locator_trs = ()
    for idx, driven_trs in enumerate(driven_transforms):
        mid_locator = add_source_locator(
            driven_trs + '_' + name, suffix_name="Driven")
        locator_trs += mid_locator,
        driver_m = cmds.xform(driven_trs, ws=1, q=1, m=1)
        cmds.xform(mid_locator, ws=True, m=driver_m)
        start_loc = upper_locators[idx]
        end_loc = lower_locators[idx]
        create_parent_constraint_linear_interpolate(
            start_loc, end_loc, mid_locator, attribute_name="interpolate", driver_value=percentages[idx], maintain_offset=maintain_offset)
        # ...maybe trying to be clever isn't worth it
        add_float_smooth_interpolation_at_value(
            control_node + '.' + middle_attr_name, mid_locator + '.interpolate', value=0.0, driver_value=-1.0)
        add_float_smooth_interpolation_at_value(
            control_node + '.' + middle_attr_name, mid_locator + '.interpolate', value=percentages[idx], driver_value=0.0)
        add_float_smooth_interpolation_at_value(
            control_node + '.' + middle_attr_name, mid_locator + '.interpolate', value=1.0, driver_value=1.0)
        if attach:
            cmds.parentConstraint(mid_locator, driven_trs, mo=maintain_offset)
    # ..constrain the locators
    cmds.parentConstraint(upper_start_loc, upper_end_loc, mo=True)
    cmds.parentConstraint(lower_end_loc, lower_start_loc, mo=True)
    cmds.parentConstraint(start_transform, upper_start_loc, mo=True)
    cmds.parentConstraint(end_transform, lower_end_loc, mo=True)
    # return the locators that will be driving the skinCluster joints
    cmds.parent(locator_trs, grp_node)
    cmds.parent(upr_sys_node, grp_node)
    cmds.parent(lwr_sys_node, grp_node)
    cmds.parent([upper_start_loc, upper_end_loc,
                lower_start_loc, lower_end_loc], grp_node)
    return locator_trs


def add_float_smooth_interpolation_at_value(driver_attr_name, driven_attr_name, driver_value=0.0, value=1.0):
    """
    """
    # create an automatic spline animation interpolation
    cmds.setDrivenKeyframe(
        driven_attr_name, currentDriver=driver_attr_name, driverValue=driver_value, value=value)
    return True


def create_locator_linear_interpolate(start_transform, end_transform, driven_transforms=[], name="", aim_at_end=True):
    """creates locators at the specified driven transforms and creates the blend matrix nodes
    :param start_transform: (str)
    :param end_transform: (str)
    :param driven_transforms: (tuple, list)
    :param name: (str)
    :param am_at_end: (bool)
    :return: (tuple,) sys_node, locator_trs, attr_names
    """
    locator_trs = []
    for driven_trs in driven_transforms:
        begin_locator = add_source_locator(
            driven_trs + '_' + name, suffix_name="Begin")
        driver_m = cmds.xform(driven_trs, ws=1, q=1, m=1)
        cmds.xform(begin_locator, ws=True, m=driver_m)
        locator_trs.append(begin_locator)
    sys_node, attr_names = create_linear_interpolate(
        start_transform, end_transform, driven_transforms=locator_trs, name=name, aim_at_end=aim_at_end)
    return sys_node, locator_trs, attr_names


def get_percent_values_from_transforms(start_transform, end_transform, driven_transforms=[]):
    """derive the percentage values based on distance from start_transform to the end_transform
    :param start_transform: (str) the starting transform object
    :param end_transform: (str) the final transform object
    :param driven_transforms: (tuple, list) the driven transforms to calculate the percentage values
    """
    percentage_values = ()
    for ea_transform in driven_transforms:
        vector, percent = get_vector_between_points(
            start_transform, end_transform, ea_transform)
        if percent > 1.0:
            percent = 1.0
        percentage_values += percent,
    return percentage_values


def create_parent_constraint_linear_interpolate(start_position, end_position, mid_position,
                                                start_value=0.5, end_value=0.5, attribute_name="interpolate",
                                                driver_value=0.0, maintain_offset=True):
    """given three transforms, create a parent constraint linear interpolation rig
    :param start_position: (str) the starting tranform object
    :param end_position: (str) the end transform object
    :param mid_position: (str) the middle transform object
    :param start_value: (float) the float start value of the constraint coming from the start_position node
    :param end_value: (float) the float end value of the constraint coming from the end_position node
    :param attribute_name: (str) the driver attribute name 
    :param maintain_offset: (bool) True/ False, create a constraint that may or may not have matrix offset values
    """
    par_node = cmds.parentConstraint(
        start_position, end_position, mid_position, mo=maintain_offset)[0]
    if driver_value == 0.0:
        driver_value = (start_value + end_value) / 2.0
    cmds.addAttr(mid_position, ln=attribute_name,
                 at='float', min=0, max=1, dv=driver_value)
    cmds.setAttr(mid_position + ".{}".format(attribute_name), k=True)
    par_node_attrs = cmds.listAttr(par_node, ud=True)
    # ...setDrivenKeyframe between the two points
    cmds.setDrivenKeyframe(
        par_node + '.' + par_node_attrs[0], currentDriver=mid_position + ".interpolate", driverValue=0.0, value=1.0)
    cmds.setDrivenKeyframe(
        par_node + '.' + par_node_attrs[0], currentDriver=mid_position + ".interpolate", driverValue=1.0, value=0.0)
    cmds.setDrivenKeyframe(
        par_node + '.' + par_node_attrs[1], currentDriver=mid_position + ".interpolate", driverValue=0.0, value=0.0)
    cmds.setDrivenKeyframe(
        par_node + '.' + par_node_attrs[1], currentDriver=mid_position + ".interpolate", driverValue=1.0, value=1.0)
    return mid_position + '.' + attribute_name


def print_xform_matrix(object_name=None):
    if not object_name:
        object_name = cmds.ls(sl=1)[0]
    matrix = cmds.xform(object_name, q=True, matrix=True)
    for i in range(4):
        base = i * 4
        print('{}, '.format([str(m) for m in matrix[base:base+4]]))
    return True
# ______________________________________________________________________________________________________________
# agtransform_interpolate.py
