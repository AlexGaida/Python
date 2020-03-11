"""
module for getting data from NurbsCurve.
"""
# import maya modules
from maya import OpenMaya
from maya import cmds

# import local modules
import object_utils
import math_utils

# define local variables
__shape_name__ = 'nurbsCurve'
connect_attr = object_utils.connect_attr
create_node = object_utils.create_node
attr_name = object_utils.attr_name
attr_set = object_utils.attr_set


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
    for i in xrange(number_of_knots):
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
    knotArray = OpenMaya.MDoubleArray()
    curve_fn.getKnots(knotArray)
    return list(knotArray)


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

    :param curve_obj:
    :return:
    """
    curve_fn = object_utils.get_fn(curve_obj)
    knots = get_nurb_obj_knot_data(curve_obj)

    edit_pts_data = ()
    edit_pnt = OpenMaya.MPoint()
    for u in knots:
        curve_fn.getPointAtParam(u, edit_pnt, OpenMaya.MFn.kWorld)
        edit_pts_data += (edit_pnt.x, edit_pnt.y, edit_pnt.z),
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

    # connect the output

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
