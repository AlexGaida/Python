"""
module for getting data from NurbsCurve.
"""
# import maya modules
from maya import OpenMaya
from maya import cmds

# import local modules
from maya_utils import object_utils

# define local variables
__shape_name__ = 'nurbsCurve'


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


def get_nurb_obj_knot_data(curve_obj=None):
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

        curve_data[crv_name]['degree'] = get_nurb_obj_curve_degree(nurb_obj)
        curve_data[crv_name]['order'] = get_nurb_obj_curve_order(nurb_obj)
        curve_data[crv_name]['form'] = get_nurb_obj_curve_form(nurb_obj)
    return curve_data


def set_curve_color(color='yellow'):
    """
    sets the color on the MFn.kNurbsCurve
    :param color: <str>, <list>, <list> color property.
    :return: <bool> True for success. <bool> False for failure.
    """
    for ctrl in object_utils.get_selected_node(single=False):
        cmds.setAttr(ctrl + 'Shape.overrideEnabled', 1)
        cmds.setAttr(ctrl + 'Shape.overrideRGBColors', 1)
        if isinstance(color, (str, unicode)):
            if color == 'yellow':
                cmds.setAttr(ctrl + 'Shape.overrideColorRGB', 1.0, 1.0, 0.0, type='double3')
            if color == 'blue':
                cmds.setAttr(ctrl + 'Shape.overrideColorRGB', 0.0, 0.0, 1.0, type='double3')
            if color == 'red':
                cmds.setAttr(ctrl + 'Shape.overrideColorRGB', 1.0, 0.0, 0.0, type='double3')
        elif isinstance(color, (list, tuple)):
            r, g, b = color
            cmds.setAttr(ctrl + 'Shape.overrideColorRGB', r, g, b, type='double3')
    return True
