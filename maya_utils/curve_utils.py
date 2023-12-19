"""
module for getting data from NurbsCurve.
"""
# import maya modules
from maya import OpenMaya
from maya import cmds

# import local modules
from . import object_utils
from . import math_utils
from . import transform_utils
from . import attribute_utils

# define local variables
__shape_name__ = 'nurbsCurve'
connect_attr = object_utils.connect_attr
create_node = object_utils.create_node
attr_name = attribute_utils.attr_name
attr_set = attribute_utils.attr_set
world_transform = lambda x: transform_utils.Transform(x).get_world_translation_list()


def get_all_nurb_objs():
    """
    traverses the scene to get all nurbsCurve objects.
    :return: <tuple> array of nurbsCurve objects.
    """
    return object_utils.get_scene_objects(node_type=__shape_name__)


def get_all_nurb_fn():
    """
    traverses the scene to get all nurbsCurve function objects.
    :return: <tuple> array of nurbsCurve function objects.
    """
    return map(object_utils.get_fn, get_all_nurb_objs())


def get_all_nurb_names():
    """
    traverses the scene to get all nurbsCurve names.
    :return: <tuple> array of nurbsCurve names.
    """
    return object_utils.get_scene_objects(node_type=__shape_name__, as_strings=True)


def get_nurb_shapes(curve_name=""):
    """
    get the nurbsCurve shape from name.
    :param curve_name: <str> the transform node of the nurbsCurve.
    :return: <tuple> nurbsCurve shape names.
    """
    return object_utils.get_shape_name(curve_name, shape_type=__shape_name__)


def get_nurb_shape_objs(curve_name=""):
    """
    return all shapes from the curve name provided.
    :param curve_name: <str> the nurbsCurve name.
    :return: <tuple> OpenMaya.MObject nurbsCurves.
    """
    return object_utils.get_shape_obj(curve_name, shape_type=__shape_name__)


def get_nurb_obj_cv_data(curve_obj=None):
    """
    get all points associated with the nurbs curve.
    :param curve_obj: <OpenMaya.MObject> nurbsCurve object.
    :return: <tuple> array of curve CV's.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    cvs = OpenMaya.MPointArray()
    curve_fn.getCVs(cvs)
    return_data = ()
    for i in range(cvs.length()):
        return_data += (i, cvs[i].x, cvs[i].y, cvs[i].z),
    return return_data


def get_nurb_obj_knot_data_old(curve_obj=None):
    """
    get the knot information from nurbsCurves.
    Maya returns 2 knots less than it should.
    :param curve_obj: <OpenMaya.MObject> nurbsCurve object.
    :return: <tuple> array of curve knot data.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    number_of_knots = curve_fn.numKnots()
    knots = ()
    # invent the first knot value for a clamped or periodic curve
    if curve_fn.knot(1) - curve_fn.knot(0) < 0.01:
        knots += curve_fn.knot(0),
    else:
        knots += curve_fn.knot(0) - 1,
    # write the rest of the knots
    for i in range(number_of_knots):
        knots += curve_fn.knot(i),
    # invent the last knot value
    if curve_fn.knot(1) - curve_fn.knot(0) < 0.01:
        knots += curve_fn.knot(number_of_knots - 1),
    else:
        knots += curve_fn.knot(number_of_knots - 1) + 1,
    return knots


def get_nurb_obj_knot_data(curve_obj=None):
    """
    get the knot information from nurbsCurves.
    Maya returns 2 knots less than it should.
    :param curve_obj: <OpenMaya.MObject> nurbsCurve object.
    :return: <tuple> array of curve knot data.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    knot_array = OpenMaya.MDoubleArray()
    curve_fn.getKnots(knot_array)
    return list(knot_array)


def get_nurb_obj_curve_degree(curve_obj=None):
    """
    get the curve information: order.
    :param curve_obj: <OpenMaya.MObject> nurbsCurve object.
    :return: <int> order.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    return curve_fn.degree()


def get_nurb_obj_curve_order(curve_obj=None):
    """
    get the curve information: degree.
    :param curve_obj: <OpenMaya.MObject> nurbsCurve object.
    :return: <int> form.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    return curve_fn.degree() + 1


def get_nurb_obj_curve_form(curve_obj=None):
    """
    get the curve information: form.
    kOpen :: the curve end and start CVs do not meet.
    kClosed :: the curve end and start CVs meet but is not continuous.
    kPeriodic :: the end points of the CVs meet and continuity is maintained.
    :param curve_obj: <OpenMaya.MObject> nurbsCurve object.
    :return: <dict> {<int>: <str>}.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    form_int = curve_fn.form()
    if form_int == 1:
        return {form_int: 'kOpen'}
    if form_int == 2:
        return {form_int: 'kClosed'}
    if form_int == 3:
        return {form_int: 'kPeriodic'}


def get_nurb_obj_edit_points(curve_obj=None):
    """
    gets the data on nurbs objects' edit points.
    :param curve_obj: <OpenMaya.MObject>
    :return: <tuple> edit point data.
    """
    curve_fn = object_utils.get_fn(curve_obj)
    knots = get_nurb_obj_knot_data(curve_obj)

    edit_pts_data = ()
    edit_pnt = OpenMaya.MPoint()
    for u in knots:
        try:
            curve_fn.getPointAtParam(u, edit_pnt, OpenMaya.MFn.kWorld)
            edit_pts_data += (edit_pnt.x, edit_pnt.y, edit_pnt.z),
        except RuntimeError:
            continue
    return edit_pts_data


def create_curve_dict(nurb_objects=()):
    """
    create the nurbsCurve data dictionary.
    :param nurb_objects: <tuple> array of nurbsCurve objects to get information frOpenMaya.
    :return: <dict> nurbCurve dictionary.
    """
    nurb_data = {}
    for nurb_obj in nurb_objects:
        crv_name = object_utils.get_m_object_name(nurb_obj)
        if crv_name not in nurb_data:
            nurb_data[crv_name] = {'cvs': (),
                                   'knots': (),
                                   'editPts': (),
                                   'degree': (),
                                   'order': (),
                                   'form': ()}
    return nurb_data


def get_nurb_data(curve_name=""):
    """
    get nurbsCurve data.
    :param curve_name: <str> curve name data.
    :return: <tuple> nurbsCurve data.
    """
    nurb_objects = get_nurb_shape_objs(curve_name)
    curve_data = create_curve_dict(nurb_objects)
    for nurb_obj in nurb_objects:
        crv_name = object_utils.get_m_object_name(nurb_obj)
        curve_data[crv_name]['cvs'] = get_nurb_obj_cv_data(nurb_obj)
        curve_data[crv_name]['knots'] = get_nurb_obj_knot_data(nurb_obj)
        curve_data[crv_name]['editPts'] = get_nurb_obj_edit_points(nurb_obj)
        curve_data[crv_name]['degree'] = get_nurb_obj_curve_degree(nurb_obj)
        curve_data[crv_name]['order'] = get_nurb_obj_curve_order(nurb_obj)
        curve_data[crv_name]['form'] = get_nurb_obj_curve_form(nurb_obj)
    return curve_data


def set_nurb_shape_color(shape_name="", color='yellow'):
    """
    sets the color on the nurbsCurve shape.
    :param shape_name: <str> the shape name to change settings on.
    :param color: <str>, <list>, <list> color property.
    :return: <bool> True for success. <bool> False for failure.
    """
    cmds.setAttr(shape_name + '.overrideEnabled', 1)
    cmds.setAttr(shape_name + '.overrideRGBColors', 1)
    if isinstance(color, (str, unicode)):
        if color == 'yellow':
            cmds.setAttr(shape_name + '.overrideColorRGB', 1.0, 1.0, 0.0, type='double3')
        if color == 'blue':
            cmds.setAttr(shape_name + '.overrideColorRGB', 0.0, 0.0, 1.0, type='double3')
        if color == 'red':
            cmds.setAttr(shape_name + '.overrideColorRGB', 1.0, 0.0, 0.0, type='double3')
    elif isinstance(color, (list, tuple)):
        r, g, b = color
        cmds.setAttr(shape_name + '.overrideColorRGB', r, g, b, type='double3')
    return True


def curve_info_matrix(point_on_curve=""):
    """
    get the matrix from point on curve info node.
    :param point_on_curve:
    :return: <tuple> matrix
    """
    point_on_curve_result_name = '{}.result'.format(point_on_curve)
    normal_vector = math_utils.Vector(*cmds.getAttr('{}.normal'.format(point_on_curve_result_name))).normal()
    tangent_vector = math_utils.Vector(*cmds.getAttr('{}.tangent'.format(point_on_curve_result_name))).normal()
    cross_vector = normal_vector ^ tangent_vector
    position = math_utils.Vector(*cmds.getAttr('{}.position'.format(point_on_curve_result_name)))
    matrix = (
         tangent_vector[0], tangent_vector[1], tangent_vector[2], 0,
         normal_vector[0],  normal_vector[1],  normal_vector[2],  0,
         cross_vector[0],   cross_vector[1],   cross_vector[2],   0,
         position[0],       position[1],       position[2],       1
    )
    return matrix


def attach_transform_to_curve(object_name="", curve_name=""):
    """
    attach a transform object to the curve object.
    :return:
    """
    poc_node_name = "{}_poc".format(object_name)
    cross_vector_name = "{}_cross".format(object_name)
    cross_vector_name2 = "{}_cross2".format(object_name)
    four_by_four_name = "{}_4by4".format(object_name)
    decompose_name = "{}_decomp".format(object_name)
    poc_node = create_node('pointOnCurveInfo', node_name=poc_node_name)
    cross_vector_node = create_node('vectorProduct', node_name=cross_vector_name)
    cross_vector_node2 = create_node('vectorProduct', node_name=cross_vector_name2)
    four_by_four_node = create_node('fourByFourMatrix', node_name=four_by_four_name)
    decompose_node = create_node('decomposeMatrix', node_name=decompose_name)
    # set the vector product into cross product operation
    attr_set(attr_name(cross_vector_name, 'operation'), 2)
    # connect the curve shape into the point on curve node
    connect_attr(object_utils.get_shape_name(curve_name)[0], attr_name(poc_node, 'inputCurve'))
    # connect the position vector to the four by four matrix node
    for out_attr, in_attr in zip(('positionX', 'positionY', 'positionZ'),
                                 ('in30', 'in31', 'in32')):
        connect_attr(attr_name(poc_node, out_attr), attr_name(four_by_four_node, in_attr))
    # connect the normalized tangent vector to the cross product2 node
    for out_attr, in_attr in zip(('normalizedTangentX', 'normalizedTangentY', 'normalizedTangentZ'),
                                 ('input2X', 'input2Y', 'input2Z')):
        connect_attr(attr_name(poc_node, out_attr), attr_name(cross_vector_node2, in_attr))
    # connect the normalized tangent vector to the four by four matrix node
    for out_attr, in_attr in zip(('normalizedTangentX', 'normalizedTangentY', 'normalizedTangentZ'),
                                 ('in00', 'in01', 'in02')):
        connect_attr(attr_name(poc_node, out_attr), attr_name(four_by_four_node, in_attr))
    # connect the normalized normal and the normalized tangent into the vector product (crossProduct)
    for out_attr, in_attr in zip(('normalizedNormalX', 'normalizedNormalY', 'normalizedNormalZ'),
                                 ('input1X', 'input1Y', 'input1Z')):
        connect_attr(attr_name(poc_node, out_attr), attr_name(cross_vector_node, in_attr))

    for out_attr, in_attr in zip(('normalizedTangentX', 'normalizedTangentY', 'normalizedTangentZ'),
                                 ('input2X', 'input2Y', 'input2Z')):
        connect_attr(attr_name(poc_node, out_attr), attr_name(cross_vector_node, in_attr))
    # connect the cross product output into the four by four matrix node
    for out_attr, in_attr in zip(('outputX', 'outputY', 'outputZ'),
                                 ('in20', 'in21', 'in22')):
        connect_attr(attr_name(cross_vector_name, out_attr), attr_name(four_by_four_node, in_attr))
    # connect the four by four node into the decompose matrix node.
    connect_attr(attr_name(four_by_four_node, 'output'), attr_name(decompose_node, 'inputMatrix'))
    # connect the decompose matrix into the transform node.
    connect_attr(attr_name(decompose_node, 'outputRotate'), attr_name(object_name, 'rotate'))
    connect_attr(attr_name(decompose_node, 'outputTranslate'), attr_name(object_name, 'translate'))
    return True


def list_scanner(array_list, index=0):
    """
    scanner list.
    :param array_list: <tuple>
    :param index: <int> the index to search the array list from.
    :return: <tuple> array of 3 tuples of XYZ values.
    """
    if index == 0:
        return array_list[index], array_list[index], array_list[index + 1],
    if index == len(array_list) - 1:
        return array_list[index - 1], array_list[index], array_list[index],
    return array_list[index - 1], array_list[index], array_list[index + 1]


def get_spans(ncvs, degree):
    return ncvs - degree


def get_knots(ncvs, degree):
    return get_spans(ncvs, degree) + 2 * (degree - 1)


def get_knot_sequence(ncvs, degree):
    """
    knot sequence
    :param ncvs:
    :param degree:
    :return:
    """
    num_knots = get_knots(ncvs, degree)
    m_double_array = OpenMaya.MDoubleArray()
    m_double_array.append(0)
    for i in range(0, num_knots + degree - 1):
        m_double_array.append(i)
        if i == num_knots:
            m_double_array.append(i)
    return m_double_array


def get_point_array(points_array, equal_distance=False):
    """
    calculate the positional array object.

    :param points_array:
    :param equal_distance: <bool> calculate the equal distance of CV's
    :return:
    """
    m_array = OpenMaya.MPointArray()
    if equal_distance:
        array_length = len(points_array)
        for idx, point in enumerate(points_array):
            if idx == 0:
                m_array.append(OpenMaya.MPoint(*point))
                m_array.append(OpenMaya.MPoint(*point))
            elif idx >= 1 and idx != array_length - 1:
                prev_p, cur_p, next_p = list_scanner(points_array, idx)
                cur_v = math_utils.Vector(*cur_p)
                prev_v = math_utils.Vector(*prev_p)
                new_vec = math_utils.Vector(cur_v - prev_v)
                new_vec = math_utils.Vector(new_vec * 0.5)
                new_vec = math_utils.Vector(prev_v + new_vec)
                m_array.append(OpenMaya.MPoint(*new_vec.position))
            elif idx == array_length - 1:
                prev_p, cur_p, next_p = list_scanner(points_array, idx)
                prev_v = math_utils.Vector(*prev_p)
                next_v = math_utils.Vector(*next_p)
                new_vec = math_utils.Vector(next_v - prev_v)
                new_vec = math_utils.Vector(new_vec * 0.5)
                new_vec = math_utils.Vector(prev_v + new_vec)
                # add two points in the same spot
                m_array.append(OpenMaya.MPoint(*new_vec.position))
                m_array.append(OpenMaya.MPoint(*point))
    else:
        for idx, point in enumerate(points_array):
            if idx == 1:
                prev_p, cur_p, next_p = list_scanner(points_array, idx)
                cur_v = math_utils.Vector(*cur_p)
                prev_v = math_utils.Vector(*prev_p)
                new_vec = math_utils.Vector(cur_v - prev_v)
                new_vec = math_utils.Vector(new_vec * 0.5)
                new_vec = math_utils.Vector(prev_v + new_vec)
                m_array.append(OpenMaya.MPoint(*new_vec.position))
            elif idx == len(points_array) - 1:
                prev_p, cur_p, next_p = list_scanner(points_array, idx)
                prev_v = math_utils.Vector(*prev_p)
                next_v = math_utils.Vector(*next_p)
                new_vec = math_utils.Vector(next_v - prev_v)
                new_vec = math_utils.Vector(new_vec * 0.5)
                new_vec = math_utils.Vector(prev_v + new_vec)
                m_array.append(OpenMaya.MPoint(*new_vec.position))
            m_array.append(OpenMaya.MPoint(*point))
    return m_array


def create_curve_from_points(points_array, degree=2, curve_name="", equal_cv_positions=True):
    """
    create a nurbs curve from points.
    :param points_array: <tuple> positional points array.
    :param degree: <int> curve degree.
    :param curve_name: <str> the name of the curve to create.
    :param equal_cv_positions: <bool> if True create CV's at equal positions.
    :return: <str> maya curve name.
    """
    knot_length = len(points_array)
    knot_array = get_knot_sequence(knot_length, degree)
    m_point_array = get_point_array(points_array, equal_distance=equal_cv_positions)
    curve_fn = OpenMaya.MFnNurbsCurve()
    curve_fn.create(m_point_array, knot_array, degree,
                    OpenMaya.MFnNurbsCurve.kOpen,
                    False, False)
    m_path = OpenMaya.MDagPath()
    curve_fn.getPath(m_path)
    if curve_name:
        parent_obj = object_utils.get_parent_obj(m_path.partialPathName())[0]
        object_utils.rename_node(parent_obj, curve_name)
        return curve_name
    return curve_fn.name()


def create_curve_from_transforms(transform_array, degree=2, curve_name="", equal_cv_positions=False):
    """
    creates a curve object from an array of transforms.
    :param transform_array:
    :param degree: <int> curve degree.
    :param curve_name: <str> the name of the curve to create.
    :param equal_cv_positions: <bool> if True create CV's at equal positions.
    :return: <str> curve name.
    """
    points_array = ()
    for tfm_name in transform_array:
        points_array += world_transform(tfm_name),
    return create_curve_from_points(points_array, degree=degree,
                                    curve_name=curve_name, equal_cv_positions=equal_cv_positions)


def create_curve_from_selection(degree=2, curve_name="", equal_cv_positions=False):
    """
    creates a curve object from an array of selected transforms.
    :param degree: <int> curve degree.
    :param curve_name: <str> the name of the curve to create.
    :param equal_cv_positions: <bool> if True create CV's at equal positions.
    :return: <str> curve name.
    """
    m_list = object_utils.get_m_selection(as_strings=True)
    if len(m_list) == 0:
        raise ValueError('[CurveFromSelectionEmptySelectionError] :: Please select some transform objects.')
    print(m_list)
    return create_curve_from_transforms(m_list, degree=degree,
                                        curve_name=curve_name, equal_cv_positions=equal_cv_positions)


def get_curve_shapes_fn(object_name):
    """the shape fn object from the string object provided.

    Args:
        object_name: (str) the object to get curve shapes from.

    Returns:
        tuple: array of curve MFnNurbsCurve Object belonging to this shape.

    """
    m_shapes = object_utils.get_m_curve_shapes(object_utils.get_m_dag(object_name))
    shape_array = ()
    for shape_m_obj in m_shapes:
        if object_utils.is_shape_intermediate(shape_m_obj):
            continue
        shape_array += OpenMaya.MFnNurbsCurve(shape_m_obj),
    return shape_array


def get_param_u_from_point(curve_name, point):
    """Returns a parameterU value from a translation point provided.

    Args:
        point: (tuple, list) x, y, z position
        curve_name: (str) the curve name to get parameterU from

    Returns:
        float: parameterU float value.

    """
    return _get_param_u(point=point, curve_name=curve_name)


def get_param_u_from_transform(curve_name, transform):
    """Returns a parameterU value from a translation object provided.

    Args:
        transform: (str) transform object name.
        curve_name: (str) the curve name to get parameterU from

    Returns:
        float: parameterU float value.

    """
    return _get_param_u(transform_obj=transform, curve_name=curve_name)


def get_curve_length(curve_name):
    """Get the curve length

    Args:
        curve_name (str): curve name to get the arc length.

    Returns:
        float: 0.0 for failure, (float) > 0.0 for success.

    """
    curve_fn = get_curve_shapes_fn(curve_name)[0]
    return curve_fn.length(0.001)


def _get_param_u(curve_name, transform_obj=None, point=None):
    """retrieves the parameter (dimension) U value from the curve specified from a point in space.

    Args:
        transform_obj (str, unicode): the transform_object to get translation point location data from.
        point (tuple, list): array of X, Y, Z point coordinates.
        curve_name (str, unicode): the name of the curve to be used.

    Returns:
        float: parameter double attribute value.

    """
    if transform_obj:
        point = cmds.xform(transform_obj, t=1, q=1, ws=1)
    point = OpenMaya.MPoint(*point)
    curve_fn = get_curve_shapes_fn(curve_name)[0]
    double_ptr = object_utils.ScriptUtils(as_double_ptr=True)
    is_point_on_curve = curve_fn.isPointOnCurve(point)
    if is_point_on_curve:
        curve_fn.getParamAtPoint(point, double_ptr, 0.001, OpenMaya.MSpace.kObject)
    else:
        # MFnNurbsCurve::closestPoint(MPoint const &,double *,double,MSpace::Space,MStatus *) const
        point = curve_fn.closestPoint(point, double_ptr.ptr, 0.001, OpenMaya.MSpace.kObject)
        curve_fn.getParamAtPoint(point, double_ptr.ptr, 0.001, OpenMaya.MSpace.kObject)
    return double_ptr.get_double()

# ______________________________________________________________________________________________________________________
# curve_utils.py
