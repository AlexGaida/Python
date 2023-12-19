from maya import cmds
import pymel.core as pm
import copy
# global variables
dt = pm.datatypes

def zero_transform_values(node_name, translate=True, scale=True, rotate=True, skip_tx=False):
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

def add_vector_product(name, suffix_name="", operation="pointMatrixProduct"):
    """
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
        vector_product_node = cmds.createNode("vectorProduct", name=vector_product_name)
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
        blend_colors_node = cmds.createNode("blendColors", name=blend_colors_node_name)
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
    drv_trasform_node_name = use_transform + '_' + create_name(name, suffix_name)
    drv_trasform_node = cmds.ls(drv_trasform_node_name, type="transform")
    if not drv_trasform_node:
        drv_trasform_node = cmds.createNode("transform", name=drv_trasform_node_name)
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
        inv_matrix_node = cmds.createNode("inverseMatrix", name=inv_matrix_node_name)
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
        mult_matrix_node = cmds.createNode("multMatrix", name=mult_matrix_node_name)
    else:
        mult_matrix_node = mult_matrix_node[0]
    add_face_attr_to_node(mult_matrix_node)
    return mult_matrix_node

def add_blend_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    blend_matrix_node_name = create_name(name, suffix_name)
    blend_matrix_node = cmds.ls(blend_matrix_node_name, type='blendMatrix')
    if not blend_matrix_node:
        blend_matrix_node = cmds.createNode("blendMatrix", name=blend_matrix_node_name)
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
        aim_matrix_node = cmds.createNode("aimMatrix", name=aim_matrix_node_name)
    else:
        aim_matrix_node = aim_matrix_node[0]
    add_face_attr_to_node(aim_matrix_node)
    return aim_matrix_node

def add_compose_matrix_node(name, suffix_name=""):
    """inverse matrix node
    :param name:
    """
    compose_matrix_node_name = create_name(name, suffix_name)
    compose_matrix_node = cmds.ls(compose_matrix_node_name, type='composeMatrix')
    if not compose_matrix_node:
        compose_matrix_node = cmds.createNode("composeMatrix", name=compose_matrix_node_name)
    else:
        compose_matrix_node = compose_matrix_node[0]
    add_face_attr_to_node(compose_matrix_node)
    return compose_matrix_node


def set_matrix_attr(node_name, xform_matrix, matrix_attr="secondaryTargetMatrix"):
    """function for setting matrix attribute types
    """
    cmds.setAttr("{}.{}".format(node_name, matrix_attr), xform_matrix, type='matrix')

def add_remap_value_node(name, suffix_name=""):
    """remap value node
    :param name:
    :param suffix_name:
    """
    remap_value_node_name = create_name(name, suffix_name)
    remap_value_node = cmds.ls(remap_value_node_name, type='remapValue')
    if not remap_value_node:
        remap_value_node = cmds.createNode("remapValue", name=remap_value_node_name)
    else:
        remap_value_node = remap_value_node[0]
    add_face_attr_to_node(remap_value_node)
    return remap_value_node


def add_condition_node(name, suffix_name="", second_term=1, operation="equal", color_if_true=1.0, color_if_false=0.0):
    """creates a condition node
    :param name:
    :param suffix_name:
    """
    #...operation dictionary
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
    #...set attributes
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
            continue # no data values, skip
        except ValueError:
            continue # no object matches name    
        if data:
            attrs_data[ea] = data
    if print_attrs:
        for k, v in attrs_data.items():
            print(k + ':\t' + str(v))
    return attrs_data

def add_source_locator(name, suffix_name=""):
    """adds a source locator if it does not yet exist for the face controller
    :param name:
    :param suffix_name:
    """
    locator_name = 'source' + '_' + create_name(name, suffix_name=suffix_name)
    source = cmds.ls(locator_name)
    if not source:
        source = cmds.spaceLocator(name=locator_name)[0]
    else:
        source = source[0]
    add_face_attr_to_node(source)
    return source

def add_grp_node(name, suffix_name="", children=[], parent=""):
    """adds a group node
    :param name:
    :param suffix_name:
    :param children:
    :param parrent:
    """
    grp_node_name = create_name(name, suffix_name)
    grp_node = cmds.ls(grp_node_name, type='transform')
    if not grp_node:
        grp_node = cmds.createNode("transform", name=grp_node_name)
    else:
        grp_node = grp_node[0]
    # if parent == 'world':
    #     cmds.parent(grp_node, world=True)
    if parent:
        cmds.parent(grp_node, parent)
    if children:
        for ch_node in children:
            cmds.parent(ch_node, grp_node)
    return grp_node

def check_face_control_bool(face_ctrl_name):
    """checks for the face controller for connections into the interpolation setup
    returns True if the controller is a face control
    """
    custom_attrs = cmds.listAttr(face_ctrl_name, ud=True)
    for custom_attr in custom_attrs:
        face_attr_name = "{}.{}".format(face_ctrl_name, custom_attr)
        matrix_node = cmds.listConnections(face_attr_name, d=True, s=False, type='inverseMatrix')
        if matrix_node:
            return True

def create_mirror_matrix_transform(source_transform, target_transform=None, name="", suffix_name=""):
    """creates a mirror matrix with a negative 1 scale and connects to the transform and rotate of the target transform
    :param source_transform:
    :param target_transform:
    :param name:
    :param suffix_name:
    """
    compose_node = cmds.createNode('composeMatrix', name = name + '_' + suffix_name)
    cmds.setAttr(compose_node + '.inputScale', -1, 1, 1, type='double3')
    mult_matrix = cmds.createNode('multMatrix', name = name + '_' + suffix_name)
    cmds.connectAttr(source_transform + '.worldMatrix[0]', mult_matrix + '.matrixIn[0]')
    cmds.connectAttr(compose_node + '.outputMatrix', mult_matrix + '.matrixIn[1]')
    decompose_matrix = cmds.createNode('decomposeMatrix', name = name + '_' + suffix_name)
    cmds.connectAttr(mult_matrix + '.matrixSum', decompose_matrix + '.inputMatrix')
    #...verify target transform
    if not target_transform:
        target_transform = cmds.spaceLocator(name='target')[0]
    #...finally connect to the target
    cmds.connectAttr(decompose_matrix + '.outputTranslate', target_transform + '.transform')
    cmds.connectAttr(decompose_matrix + '.outputRotate', target_transform + '.rotate')
    return target_transform

def check_shape_attributes(face_ctrl_name, shape_attr='shapes'):
    """check shape attribute, this attribute is for quality of life for the face rig to show how many shapes it is supposed to drive
    :param face_ctrl_name: <str> the controller name to check the interpolation
    :param shape_attr: <str> default: "shapes" attribute to show what linked interpolations are connected to this controller
    """
    if cmds.ls(face_ctrl_name + '.' + shape_attr):
        enum_strings = cmds.attributeQuery(shape_attr, node=face_ctrl_name, listEnum=True)[0].split(':')
        return enum_strings
    else:
        # Attribute name not recognized
        return []

def add_shape_enum(face_ctrl_name, shape_name, shape_attr='shapes'):
    """add shape enumeration attribute names to a controller
    :param face_ctrl_name: <str> the controller name to check the interpolation
    :param shape_name: <str>
    :param shape_attr: <str>
    """
    face_enum = check_shape_attributes(face_ctrl_name, shape_attr)
    if face_enum and not shape_name in face_enum:
        face_enum.append(shape_name)
        cmds.addAttr('{}.{}'.format(face_ctrl_name, shape_attr), at='enum', en=':'.join(face_enum), edit=True)
    elif face_enum and shape_name in face_enum:
        return len(check_shape_attributes(face_ctrl_name, shape_attr))
    else:
        cmds.addAttr(face_ctrl_name, ln=shape_attr, at="enum", en="off:{}:".format(shape_name))
        cmds.setAttr("{}.{}".format(face_ctrl_name, shape_attr), keyable=True)
    return len(check_shape_attributes(face_ctrl_name, shape_attr))

def check_and_connect_attrs(source_attr, dest_attr, force=False):
    """Warning free connections of the attributes
    """
    if not cmds.isConnected(source_attr, dest_attr):
        try:
            return cmds.connectAttr(source_attr, dest_attr, force=force)
        except RuntimeError:
            # attribute already connected
            existing_connection = cmds.listConnections(dest_attr, s=True, d=False, plugs=True)
            print("Attribute is already connected, Debug: {} >> {}".format(source_attr, existing_connection))
    else:
        return True

def check_and_parent_node(transform_node, parent_node):
    parent_nodes = cmds.listRelatives(transform_node, p=True)
    if not parent_nodes:
        cmds.parent(transform_node, parent_node)
    elif parent_node not in parent_nodes:
        cmds.parent(transform_node, parent_node)
    return parent_nodes

def check_and_disconnect_attr(source_attr, dest_attr):
    """Warning free disconnection of attributes
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
    """
    return dt.Vector(cmds.xform(transform_name, ws=1, t=1, q=1))

def get_vector_between_points(transform_a, transform_b, transform_c):
    """calculate the percentage distance of transform C vector against AB vector

    """
    ta_vec = get_transform_vector(transform_a)
    tb_vec = get_transform_vector(transform_b)
    tc_vec = get_transform_vector(transform_c)
    #...calculate the percent the target_c is in relation to the total distance
    orig_vec = tb_vec - ta_vec
    orig_mag = orig_vec.length()
    target_vec = tc_vec - ta_vec
    target_mag = target_vec.length()
    percent = target_mag / orig_mag
    if percent > 1:
        percent = 1.0
    calc_vec = orig_vec * percent
    final_vec = ta_vec + calc_vec
    #...return the results
    return final_vec, percent

def get_vector_info_between_two_points(transform_a, transform_b):
    """
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
    :param name: name of the single matrix-interpolation 
    """
    curve_name = create_name(name, suffix_name=suffix_name + '_VISUAL_CRV')
    #...check curve node
    curve_node = cmds.ls(curve_name)
    if curve_node:
        curve_node = curve_node[0]
    if not cmds.filterExpand(curve_node, sm=9):
        position_a = cmds.xform(source_transform, ws=1, t=1, q=1)
        position_b = cmds.xform(target_transform, ws=1, t=1, q=1)
        curve_node = cmds.curve(name=curve_name, degree=1, point=(position_a, position_b), knot=(0, 1))
        add_curve_attr_to_node(curve_node)
    return curve_node

def hide_channels(transform_node, t=True, r=True, s=True, v=True):
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
    """
    """
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
    #..color attr name
    if not cmds.ls(control_node + '.' + color_attr_name):
        cmds.addAttr(control_node, ln=color_attr_name, at="enum", en=":".join(color_dict.keys()))
        cmds.setAttr(control_node + '.' + color_attr_name, k=True)
    cmds.setAttr(curve_node + '.overrideEnabled', True)
    check_and_connect_attrs(control_node + '.' + color_attr_name, curve_node + '.overrideColor')
    #..lineWidth attr
    if not cmds.ls(control_node + '.' + line_width_attr_name):
        cmds.addAttr(control_node, ln=line_width_attr_name, at='float', min=-1.0, max=10.0)
        cmds.setAttr(control_node + '.' + line_width_attr_name, k=True)
    check_and_connect_attrs(control_node + '.' + line_width_attr_name, curve_node + '.lineWidth')

def create_measurement_curve_from_vectors(name, suffix_name="", vector_a=[], vector_b=[]):
    """
    :param name: name of the single matrix-interpolation 
    """
    curve_name = create_name(name, suffix_name=suffix_name + '_VISUAL_CRV')
    cmds.curve(name=curve_name, degree=1, point=(vector_a, vector_b), knot=(0, 1))
    return curve_name

def create_curves(name, source_transform, target_transforms=[], parent="", connect_to_vis_attr=""):
    #...create visualization curves
    orig_curve_node = create_measurement_curve_from_transform(name, suffix_name=source_transform, source_transform=source_transform, target_transform=target_transforms[-1])
    if connect_to_vis_attr:
        check_and_connect_attrs(connect_to_vis_attr, orig_curve_node + '.visibility')
    add_curve_attr_to_node(orig_curve_node)
    hide_channels(orig_curve_node, v=False)
    vec_node_1 = connect_to_cv_point(target_transforms[-1], orig_curve_node, name=name, index=0)
    add_curve_attr_to_node(vec_node_1)
    vec_node_2 = connect_to_cv_point(source_transform, orig_curve_node, name=name, index=1)
    add_curve_attr_to_node(vec_node_2)
    #..create an organizational group_node
    face_crv_grp_node = add_grp_node(name, suffix_name="FACECRV_GRP")
    check_and_parent_node(orig_curve_node, face_crv_grp_node)
    add_and_connect_curve_attributes_to_transform(face_crv_grp_node, orig_curve_node)
    check_and_parent_node(face_crv_grp_node, parent)
    for target_tfm in target_transforms[:-1]:
        mid_vector, mid_percent = get_vector_between_points(source_transform, target_transforms[-1], target_tfm)
        target_vec = get_transform_vector(target_tfm)
        measure_curve = create_measurement_curve_from_vectors(name, suffix_name=target_tfm, vector_a=mid_vector, vector_b=target_vec)
        hide_channels(measure_curve, v=False)
        check_and_parent_node(measure_curve, face_crv_grp_node)
        if connect_to_vis_attr:
            check_and_connect_attrs(connect_to_vis_attr, measure_curve + '.visibility')
        add_curve_attr_to_node(measure_curve)
        bc_node = add_blend_colors_node(name, suffix_name=target_tfm + 'A', percent=mid_percent)
        add_curve_attr_to_node(bc_node)
        cmds.connectAttr(vec_node_1 + '.output', bc_node + '.color1')
        cmds.connectAttr(vec_node_2 + '.output', bc_node + '.color2')
        cmds.connectAttr(bc_node + '.output', measure_curve + '.controlPoints[0]')
        connect_to_cv_point(target_tfm, measure_curve, name=name, index=1)
        add_and_connect_curve_attributes_to_transform(face_crv_grp_node, measure_curve)
    #...
    return True 

def create_interpolation(driver_transform, name="", source_transform="", target_transforms=[], add_groups=True):
    """creates an interpolation math at a single source transform and a multiple-transform objects
    :param name: name of the single matrix-interpolation 
    :param driver_transform: <str> the transform that will hold the driver attributes connection
    :param source_transform: <str> the transform that will have the ParentOffsetMatrix connection
    :param attribute_control: <str> the transform that will hold the interpolation attributes
    :param target_transforms: <list> the target transforms to interpolate into, ordered by index
    """
    #...store attrs
    node_dict = {}
    node_dict[driver_transform] = ()
    #...add the shape enumerator attribute
    attr_index = add_shape_enum(driver_transform, name)
    condition_node = add_condition_node(driver_transform, name + '_VIS', second_term=attr_index-1, operation="equal", color_if_true=1.0, color_if_false=0.0)
    add_face_attr_to_node(condition_node)
    #...cancel the source transformation
    if not source_transform:
        driver_parent_transform = add_driver_transform(driver_transform, name='Driver')
        source_transform = add_source_locator(driver_transform)
        cmds.hide(source_transform)
        #...move the source locator to the driver transform
        m = cmds.xform(driver_transform, m=True, worldSpace=True, query=True)
        cmds.xform(source_transform, m=m, ws=True)
    #...check if the driver transform is a face controller
    inv_node = add_inverse_matrix_node(source_transform, suffix_name='mInverse')
    #...add a mult matrix node to zero out the matrix transforms of the source location of the face control 
    mult_node = add_mult_matrix_node(source_transform, suffix_name='mMatrix')
    try:
        cmds.connectAttr('{}.worldMatrix[0]'.format(source_transform), '{}.inputMatrix'.format(inv_node))
    except RuntimeError:
        # Maya command error: attribute already connected
        pass
    try:
        cmds.connectAttr('{}.worldMatrix[0]'.format(source_transform), '{}.matrixIn[0]'.format(mult_node))
    except RuntimeError:
        # Maya command error: attribute already connected
        pass
    try:
        cmds.connectAttr('{}.outputMatrix'.format(inv_node), '{}.matrixIn[1]'.format(mult_node))
    except RuntimeError:
        # Maya command error: attribute already connected
        pass
    interpolate_math = 10/len(target_transforms)
    last_value = 0
    blend_matrix_node = add_blend_matrix_node('{}_{}'.format(driver_transform, name), suffix_name="Interpolate")
    cmds.connectAttr(driver_transform + '.shapes', condition_node + '.firstTerm')
    #...create driver face attribute
    if not cmds.ls(driver_transform + '.' + name):
        cmds.addAttr(driver_transform, ln=name, min=0.0, max=10.0, at='float')
        cmds.setAttr(driver_transform + '.' + name, keyable=True)
    for idx, target_tfm in enumerate(target_transforms):
        #...connect attribute
        cmds.connectAttr(condition_node + '.outColorR', target_tfm + '.visibility')
        if idx == 0:
            #...special consideration for the first blendMatrix: have the source be connected as a target
            check_and_connect_attrs('{}.matrixSum'.format(mult_node), '{}.inputMatrix'.format(blend_matrix_node))
            check_and_connect_attrs('{}.outputMatrix'.format(inv_node), '{}.target[0].targetMatrix'.format(blend_matrix_node))
            check_and_connect_attrs('{}.worldMatrix[0]'.format(source_transform), '{}.target[1].targetMatrix'.format(blend_matrix_node))
        #...connect the target matrices
        try:
            cmds.connectAttr('{}.worldMatrix[0]'.format(target_tfm), '{}.target[{}].targetMatrix'.format(blend_matrix_node, 2+idx))
        except RuntimeError:
            # Maya command error: attribute already connected
            pass
        #...create RemapValue node to connect the driver attributes into
        weight_remap_node = add_remap_value_node(target_tfm, suffix_name='REMAP')
        #...calculate remap values on min/ max based on the number of target transforms
        if idx==0:
            cmds.setAttr(weight_remap_node + '.inputMin', 0.0)
        else:
            cmds.setAttr(weight_remap_node + '.inputMin', last_value)
        last_value += interpolate_math
        cmds.setAttr(weight_remap_node + '.inputMax', last_value)
        cmds.connectAttr(driver_transform + '.' + name, weight_remap_node + '.inputValue')
        cmds.connectAttr(weight_remap_node + '.outValue', blend_matrix_node + '.target[{}].weight'.format(2+idx))
        # store this attribute for later use
        node_dict[driver_transform] += weight_remap_node,
    blend_inv_matrix_node = add_blend_matrix_node(source_transform, suffix_name="_INVMATRIX")
    output_sum_mult_node = add_mult_matrix_node(driver_parent_transform, suffix_name='Interpolate_matrixMult')
    try:
        input_index = len(cmds.listAttr('{}.matrixIn[*]'.format(output_sum_mult_node)))
    except ValueError:
        input_index = 0
    #...connect attrs
    check_and_connect_attrs('{}.outputMatrix'.format(inv_node), '{}.inputMatrix'.format(blend_inv_matrix_node))
    if input_index == 0:
        check_and_connect_attrs('{}.worldMatrix[0]'.format(source_transform), '{}.matrixIn[0]'.format(output_sum_mult_node), force=True)
    check_and_connect_attrs('{}.outputMatrix'.format(blend_inv_matrix_node), '{}.matrixIn[{}]'.format(output_sum_mult_node, input_index + 1))
    check_and_disconnect_attr('{}.worldInverseMatrix[0]'.format(source_transform), output_sum_mult_node)
    #...get multMatrix connected index numbers
    cmds.connectAttr("{}.outputMatrix".format(blend_matrix_node), '{}.matrixIn[{}]'.format(output_sum_mult_node, input_index + 2))
    check_and_connect_attrs('{}.worldInverseMatrix[0]'.format(source_transform), '{}.matrixIn[{}]'.format(output_sum_mult_node, input_index + 3))
    # except RuntimeError:
    #     # Maya command error: attribute already connected
    #     pass
    #...connect to output
    # if not cmds.isConnected(mult_node + '.matrixSum', driver_parent_transform + '.offsetParentMatrix'):
    # if not cmds.isConnected('l_main_CTRL_Driver_Interpolate_matrixMult.matrixSum', 'l_main_CTRL_Driver.offsetParentMatrix'):
    check_and_connect_attrs('{}.matrixSum'.format(output_sum_mult_node), '{}.offsetParentMatrix'.format(driver_parent_transform))
    #...group the target locators
    if add_groups:
        control_grp_node = add_grp_node(name="FACE_CONTROLS", suffix_name="TARGETS_GRP")
        face_shape_grp_node = add_grp_node(name=name, suffix_name="TARGETFACE_GRP", children=target_transforms + [source_transform], parent=control_grp_node)
    #...create visualization curves
    create_curves(name, source_transform, target_transforms, parent=face_shape_grp_node, connect_to_vis_attr=(condition_node + '.outColorR'))
    return node_dict

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

def create_linear_interpolate(start_transform, end_transform, driven_transforms=[], name="", aim_at_end=True):
    """creates a linear interpolation of transforms between the two points
    :param start_transform:
    :param end_transform:
    :param driven_transforms:
    """
    outbound_matrix_attr = '.xformMatrix'
    if not name:
        cmds.warning('Please name your interpolation')
        return False
    system_node_name = "{}_interpolate".format(name)
    #...add a system node
    system_node = add_grp_node(system_node_name)
    # cmds.parent(start_transform, system_node)
    # cmds.parent(end_transform, system_node)
    # get interpolation math
    interpolate_math = 1.0/len(driven_transforms)
    last_value = 0
    # start xform
    get_start_xform_t = cmds.xform(start_transform, t=True, ws=1, query=True)
    get_start_xform_ro = cmds.xform(start_transform, ro=True, ws=1, query=True)
    get_start_xform_s = cmds.xform(start_transform, s=True, ws=1, query=True)
    # end xform
    get_end_xform_t = cmds.xform(start_transform, t=True, ws=1, query=True)
    get_end_xform_ro = cmds.xform(start_transform, ro=True, ws=1, query=True)
    get_end_xform_s = cmds.xform(start_transform, s=True, ws=1, query=True)
    #..create the start offset matrix node
    start_compose_matrix_node = add_compose_matrix_node(start_transform, suffix_name="StartMatrixOffset")
    start_mult_matrix_node = add_mult_matrix_node(start_transform, suffix_name="StartOffsetMultMatrix")
    check_and_connect_attrs(start_transform + outbound_matrix_attr, start_mult_matrix_node + '.matrixIn[0]')
    check_and_connect_attrs(start_compose_matrix_node + '.outputMatrix', start_mult_matrix_node + '.matrixIn[1]')
    #..create the end offset matrix node
    # end_compose_matrix_node = add_compose_matrix_node(end_transform, suffix_name="EndMatrixOffset")
    # set_compound_matrix_node(end_compose_matrix_node, get_end_xform_t, get_end_xform_ro, invert_t=True)
    end_mult_matrix_node = add_mult_matrix_node(end_transform, suffix_name="EndOffsetMultMatrix")
    check_and_connect_attrs(end_transform + outbound_matrix_attr, end_mult_matrix_node + '.matrixIn[0]')
    check_and_connect_attrs(start_compose_matrix_node + '.outputMatrix', end_mult_matrix_node + '.matrixIn[1]')
    # connect the starting and end transform matrices
    for ea_transform in driven_transforms:
        cmds.parent(ea_transform, system_node)
        par_node = add_driver_transform(ea_transform, suffix_name="DRV")
        get_orig_xform_t = cmds.xform(ea_transform, t=True, ws=True, query=True)
        get_xform_t = list(dt.Vector(get_start_xform_t) - dt.Vector(get_orig_xform_t))
        get_xform_ro = cmds.xform(ea_transform, ro=True, ws=True, query=True)
        # get_xform_s = cmds.xform(ea_transform, s=True, ws=False, query=True)
        #...
        vector, percent = get_vector_between_points(start_transform, end_transform, ea_transform)
        if percent > 1.0:
            percent = 1.0
        blend_matrix_node = add_blend_matrix_node(ea_transform, suffix_name="interpolate")
        #...connect the composed matrix offsets into the blend matrix start and end targets
        check_and_connect_attrs(start_mult_matrix_node + '.matrixSum', blend_matrix_node + '.inputMatrix')
        check_and_connect_attrs(end_mult_matrix_node + '.matrixSum', blend_matrix_node + '.target[0].targetMatrix')
        # add an offset to the original joint values
        compose_matrix_node = add_compose_matrix_node(ea_transform, suffix_name="MatrixOffset")
        # set_compound_matrix_node(compose_matrix_node, get_orig_xform_t, get_xform_ro, invert_t=True)
        print(ea_transform, get_xform_t, compose_matrix_node)
        mult_matrix_node = add_mult_matrix_node(ea_transform, suffix_name="TargetOffsetMatrix")
        check_and_connect_attrs(compose_matrix_node + '.outputMatrix', mult_matrix_node + '.matrixIn[0]')
        check_and_connect_attrs(blend_matrix_node + '.outputMatrix', mult_matrix_node + '.matrixIn[1]')
        if aim_at_end:
            aim_matrix_node = add_aim_matrix_node(ea_transform, suffix_name="interpolateAim")
            set_matrix_attr(aim_matrix_node, [1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,10.0,0.0,1.0])
            check_and_connect_attrs(end_mult_matrix_node + '.matrixSum', aim_matrix_node + '.primaryTargetMatrix')
            check_and_connect_attrs(aim_matrix_node + '.outputMatrix', par_node + '.offsetParentMatrix')
            check_and_connect_attrs(mult_matrix_node + '.matrixSum', aim_matrix_node + '.inputMatrix')
            cmds.setAttr(aim_matrix_node + '.envelope', percent)
        else:
            check_and_connect_attrs(mult_matrix_node + '.matrixSum', ea_transform + '.offsetParentMatrix')
        cmds.setAttr(blend_matrix_node + '.envelope', percent)
        #...zero joint transforms
        zero_transform_values(par_node, translate=True, scale=True, rotate=True)
        last_value += interpolate_math
        #...add attributes
        cmds.addAttr(start_transform, ln=ea_transform, min=0, max=1, dv=percent)
        cmds.setAttr(start_transform + '.' + ea_transform, k=True)
        cmds.connectAttr(start_transform + '.' + ea_transform, blend_matrix_node + '.envelope')
    # finish the function and return the system node
    return system_node

def create_parent_constraint_linear_interpolate(start_position, end_position, mid_position, start_value=0.5, end_value=0.5):
    """given three transforms, create a parent constraint linear interpolation rig
    """
    par_node = cmds.parentConstraint(start_position, end_position, mid_position, mo=False)[0]
    driver_value = (start_value + end_value) / 2.0
    cmds.addAttr(mid_position, ln="interpolate", at='float', min=0, max=1, dv=driver_value)
    cmds.setAttr(mid_position + ".interpolate", k=True)
    par_node_attrs = cmds.listAttr(par_node, ud=True)
    #...setDrivenKeyframe between the two points
    cmds.setDrivenKeyframe(par_node + '.' + par_node_attrs[0], currentDriver=mid_position + ".interpolate", driverValue=0.0, value=1.0)
    cmds.setDrivenKeyframe(par_node + '.' + par_node_attrs[0], currentDriver=mid_position + ".interpolate", driverValue=1.0, value=0.0)
    cmds.setDrivenKeyframe(par_node + '.' + par_node_attrs[1], currentDriver=mid_position + ".interpolate", driverValue=0.0, value=0.0)
    cmds.setDrivenKeyframe(par_node + '.' + par_node_attrs[1], currentDriver=mid_position + ".interpolate", driverValue=1.0, value=1.0)
# ______________________________________________________________________________________________________________
# agtransform_interpolate.py