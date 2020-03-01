"""
follicle_utils module for dealing with anything relating with follicle rigging.
"""
# import maya modules
from maya import cmds
from maya import OpenMaya

# import local modules
import object_utils
import transform_utils

# define local variables
FOLLICLE_SUFFIX = 'foll'
CLOSEST_POINT_ON_MESH_SUFFIX = 'cpom'
CLOSEST_POINT_ON_SURFACE_SUFFIX = 'cpos'
CLOSEST_POINT_ON_CURVE_SUFFIX = 'cpoc'


def find_all_follicles():
    """
    finds all follicles by the follicle suffix name.
    :return: <tuple> array of follicles found.
    """
    return find_objects_by_suffix(FOLLICLE_SUFFIX)


def find_all_point_on_mesh_nodes():
    """
    finds all point on mesh nodes by the suffix name.
    :return: <tuple> array of follicles found.
    """
    return find_objects_by_suffix(CLOSEST_POINT_ON_MESH_SUFFIX)


def find_all_point_on_surface_nodes():
    """
    finds all point on surface nodes by the suffix name.
    :return: <tuple> array of follicles found.
    """
    return find_objects_by_suffix(CLOSEST_POINT_ON_SURFACE_SUFFIX)


def find_all_point_on_curve_nodes():
    """
    finds all point on curve nodes by the suffix name.
    :return: <tuple> array of follicles found.
    """
    return find_objects_by_suffix(CLOSEST_POINT_ON_CURVE_SUFFIX)


def find_objects_by_suffix(suffix_str):
    """
    find these objects by the suffix name.
    :param suffix_str: <str> the suffix name to look for.
    :return: <tuple> found objects by the suffix name.
    """
    return tuple(cmds.ls('*_{}'.format(suffix_str)))


def follicle_node_name(object_name):
    """
    concatenates the follicle object against the object name.
    :param object_name: <str> object name.
    :return: <str> the follicle object name.
    """
    length_of_nodes = len(find_objects_by_suffix(FOLLICLE_SUFFIX))
    return '{}_{}_{}'.format(object_name, length_of_nodes, FOLLICLE_SUFFIX)


def closest_point_surface_node_name(object_name):
    """
    concatenates the follicle object against the object name.
    :param object_name: <str> object name.
    :return: <str> the closest point on surface node name
    """
    length_of_nodes = len(find_objects_by_suffix(CLOSEST_POINT_ON_SURFACE_SUFFIX))
    return '{}_{}_{}'.format(object_name, length_of_nodes, CLOSEST_POINT_ON_SURFACE_SUFFIX)


def closest_point_mesh_node_name(object_name):
    """
    concatenates the follicle object against the object name.
    :param object_name: <str> object name.
    :return: <str> the closest point on surface node name
    """
    length_of_nodes = len(find_objects_by_suffix(CLOSEST_POINT_ON_MESH_SUFFIX))
    return '{}_{}_{}'.format(object_name, length_of_nodes, CLOSEST_POINT_ON_MESH_SUFFIX)


def closest_point_curve_node_name(object_name):
    """
    concatenates the follicle object against the object name.
    :param object_name: <str> object name.
    :return: <str> the closest point on surface node name
    """
    length_of_nodes = len(find_objects_by_suffix(CLOSEST_POINT_ON_CURVE_SUFFIX))
    return '{}_{}_{}'.format(object_name, length_of_nodes, CLOSEST_POINT_ON_CURVE_SUFFIX)


def create_follicle(name=""):
    """
    creates the follicle object and snap it against a surface object.
    :param name: <str> the name of the follicle node.
    :return: <str> follicle object name.
    """
    return cmds.createNode('follicle', name=follicle_node_name(name))


def attr_connect(attr_src, attr_trg):
    """
    connect the attributes from the source attribute to the target attribute.
    :param attr_src: <str> source attribute.
    :param attr_trg: <str> target attribute.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not cmds.isConnected(attr_src, attr_trg):
        cmds.connectAttr(attr_src, attr_trg)
    return True


def attr_name(object_name, attr):
    """
    concatenate strings to make an attribute name.
    checks to see if the attribute is valid.
    :return: <str> attribute name.
    """
    attr_str = '{}.{}'.format(object_name, attr)
    if not cmds.objExists(attr_str):
        raise ValueError('[AttrName :: attribute name does not exit.]')
    return attr_str


def create_node(node_type, node_name=""):
    """
    creates this node name.
    :param node_type: <str> create this type of node.
    :param node_name: <str> create a node with this name.
    :return: <str> node name.
    """
    if not cmds.objExists(node_name):
        cmds.createNode(node_type, name=node_name)
    return node_name


def create_follicle_node(name=""):
    """
    creates a follicle node.
    :param name: <str> use this base name to create the follicle with.
    :return: <str> follicle node.
    """
    return create_node('follicle', follicle_node_name(name) + 'Shape')


def attach_follicle(mesh_name, follicle_name=""):
    """
    attaches a follicle to the specified mesh object.
    :param follicle_name: <str> the follicle object name.
    :param mesh_name: <str> the shape object name. Could be a nurbsSurface to a mesh object.
    :return: <bool> True for success. <bool> False for failure.
    """
    shape_m_obj_array = object_utils.get_shape_obj(mesh_name)
    shape_name_array = object_utils.get_shape_name(mesh_name)

    follicles = ()

    for shape_m_obj, shape_name in zip(shape_m_obj_array, shape_name_array):
        if not follicle_name:
            follicle_shape_name = create_follicle_node(mesh_name)
            follicle_name = object_utils.get_parent_name(follicle_shape_name)[0]
        else:
            follicle_shape_name = object_utils.get_shape_name(follicle_name)[0]

        follicles += follicle_name,

        if object_utils.check_shape_type_name(shape_m_obj, 'nurbsSurface'):
            attr_connect(attr_name(shape_name, 'matrix'), attr_name(follicle_shape_name, 'inputWorldMatrix'))
            attr_connect(attr_name(shape_name, 'worldSpace[0]'), attr_name(follicle_shape_name, 'inputSurface'))

        elif object_utils.check_shape_type_name(shape_m_obj, 'mesh'):
            attr_connect(attr_name(shape_name, 'worldMatrix[0]'), attr_name(follicle_shape_name, 'inputWorldMatrix'))
            attr_connect(attr_name(shape_name, 'outMesh'), attr_name(follicle_shape_name, 'inputMesh'))

        elif object_utils.check_shape_type_name(shape_m_obj, 'nurbsCurve'):
            attr_connect(attr_name(shape_name, 'worldMatrix[0]'), attr_name(follicle_shape_name, 'inputWorldMatrix'))
            attr_connect(attr_name(shape_name, 'outCurve'), attr_name(follicle_shape_name, 'inputCurve'))

        attr_connect(attr_name(follicle_shape_name, 'outRotate'), attr_name(follicle_name, 'rotate'))
        attr_connect(attr_name(follicle_shape_name, 'outTranslate'), attr_name(follicle_name, 'translate'))
    return follicles


def set_closest_uv_follicles(driver_objs, mesh_name, follicles_array=()):
    """
    set the closest uv coordinates onto the follicle nodes.
    :param driver_objs: <tuple> array of driver objects.
    :param follicles_array: <tuple> array of follicle objects.
    :return: <bool> True for success.
    """
    if not follicles_array:
        follicles_array = get_attached_follicles(mesh_name)

    if not isinstance(driver_objs, (tuple, list)):
        driver_objs = driver_objs,

    for driver_node, follicle_node in zip(driver_objs, follicles_array):
        u, v = get_closest_uv(driver_node, mesh_name)
        cmds.setAttr(attr_name(follicle_node, 'parameterU'), u)
        cmds.setAttr(attr_name(follicle_node, 'parameterV'), v)
    return True


def get_attached_follicles(mesh_name=""):
    """
    gets the attached follicles from the mesh name provided.
    :param mesh_name: <str> mesh name to check for connected follicles.
    :return: <tuple> array of follicles found.
    """
    shape_obj_array = object_utils.get_shape_obj(mesh_name)
    follicles = ()
    for shape_obj in shape_obj_array:
        follicles += object_utils.get_connected_nodes(shape_obj, find_node_type='follicle')
    return follicles


def attach_closest_point_node(driver_name, mesh_name, follicle_name):
    """
    attaches the closest point node.
    :param driver_name: <str> the driving object.
    :param mesh_name:  <str> the mesh object.
    :param follicle_name: <str> the follicle transform object.
    :return: <str> closestPoint nodes.
    """
    shape_m_obj_array = object_utils.get_shape_obj(mesh_name)
    shape_name_array = object_utils.get_shape_name(mesh_name)
    nodes = ()
    for shape_m_obj, shape_name in zip(shape_m_obj_array, shape_name_array):
        foll_shape_name = object_utils.get_shape_name(follicle_name)
        if object_utils.check_shape_type_name(shape_m_obj, 'nurbsSurface'):
            node_name = closest_point_surface_node_name(driver_name)
            nodes += cmds.createNode('closestPointOnSurface', name=node_name),
            attr_connect(attr_name(shape_name, 'worldSpace[0]'), attr_name(node_name, 'inputSurface'))

        elif object_utils.check_shape_type_name(shape_m_obj, 'mesh'):
            node_name = closest_point_mesh_node_name(driver_name)
            nodes += cmds.createNode('closestPointOnMesh', name=follicle_name(driver_name)),
            attr_connect(attr_name(shape_name, 'worldMesh[0]'), attr_name(node_name, 'inMesh'))

        elif object_utils.check_shape_type_name(shape_m_obj, 'nurbsCurve'):
            node_name = closest_point_curve_node_name(driver_name)
            nodes += cmds.createNode('closestPointOnCurve', name=follicle_name(driver_name)),
            attr_connect(attr_name(shape_name, 'worldSpace[0]'), attr_name(node_name, 'inCurve'))

        attr_connect(attr_name(driver_name, 'translate'), attr_name(node_name, 'inPosition'))
        attr_connect(attr_name(node_name, 'parameterU'), attr_name(foll_shape_name, 'parameterU'))
        attr_connect(attr_name(node_name, 'parameterV'), attr_name(foll_shape_name, 'parameterV'))
    return nodes


def get_closest_normal(driver_name, mesh_name):
    """
    get the closest normal vector on nurbsSurface.
    :param driver_name: <str> the driving object.
    :param mesh_name:  <str> the mesh object.
    :return: <tuple> U, V,
    """
    shape_fn = object_utils.get_shape_fn(mesh_name)
    if object_utils.is_shape_nurbs_surface(mesh_name):
        u, v = get_closest_uv(driver_name, mesh_name)
        return shape_fn.normal(u, v)


def get_closest_uv(driver_name, mesh_name):
    """
    get the closest point on surface UV values.
    :param driver_name: <str> the driving object.
    :param mesh_name:  <str> the mesh object.
    :return: <tuple> U, V,
    """
    shape_fn = object_utils.get_shape_fn(mesh_name)
    if object_utils.is_shape_nurbs_surface(mesh_name):
        param_u = object_utils.ScriptUtil(0.0, as_double_ptr=True)
        param_v = object_utils.ScriptUtil(0.0, as_double_ptr=True)
        cpos = get_closest_point(driver_name, mesh_name, as_point=True)
        shape_fn.getParamAtPoint(cpos, param_u.ptr, param_v.ptr, OpenMaya.MSpace.kObject)
        return param_u.get_double(), param_v.get_double(),


def get_closest_parameter(driver_name, curve_name, normalize=False):
    """
    for nurbs curves only. get the closest parameter value.
    :param driver_name: <str> the driving object.
    :param curve_name:  <str> the mesh object.
    :param normalize: <bool> if set True, returns a normalized parameter value.
    :return: <tuple> parameter value.
    """
    shape_fn = object_utils.get_shape_fn(curve_name)
    cpoc = get_closest_point(driver_name, curve_name, as_point=True)
    param_u = object_utils.ScriptUtil(0.0, as_double_ptr=True)
    shape_fn.getParamAtPoint(cpoc, param_u.ptr)
    if normalize:
        return param_u.get_double() / get_param_length(curve_name)
    else:
        return param_u.get_double(),


def get_parameter_normal(driver_name, curve_name):
    """
    for nurbs curves only. get the normal from parameter value.
    :param driver_name: <str> the driving object.
    :param curve_name:  <str> the mesh object.
    :return: <tuple> normal value.
    """
    shape_fn = object_utils.get_shape_fn(curve_name)
    c_param = get_closest_parameter(driver_name, curve_name)
    normal = object_utils.ScriptUtil(0.0, as_double_ptr=True)
    shape_fn.normal(c_param, normal.ptr)
    return normal.get_double(),


def get_parameter_tangent(driver_name, curve_name):
    """
    for nurbs curves only. get the normal from parameter value.
    :param driver_name: <str> the driving object.
    :param curve_name:  <str> the mesh object.
    :return: <tuple> normal value.
    """
    shape_fn = object_utils.get_shape_fn(curve_name)
    c_param = get_closest_parameter(driver_name, curve_name)
    tangent = object_utils.ScriptUtil(0.0, as_double_ptr=True)
    shape_fn.tangent(c_param, tangent.ptr)
    return tangent.get_double(),


def get_closest_curve_distance(driver_name, curve_name):
    """
    for nurbs curves only. get the closest curve distance from the point given.
    :param driver_name: <str> the driving object.
    :param curve_name:  <str> the mesh object.
    :return: <tuple> normal value.
    """
    shape_fn = object_utils.get_shape_fn(curve_name)
    c_point = get_closest_point(driver_name, curve_name, as_point=True)
    distance = shape_fn.distanceToPoint(c_point)
    return distance,


def get_curve_length(curve_name):
    """
    for nurbs curves only. get the curve length.
    :return: <float> curve length.
    """
    shape_fn = object_utils.get_shape_fn(curve_name)
    return shape_fn.length()


def get_param_length(curve_name):
    """
    for nurbs curves only. get the parameter length.
    :return: <float> curve length.
    """
    shape_fn = object_utils.get_shape_fn(curve_name)
    return shape_fn.findParamFromLength(shape_fn.length())


def get_closest_point(driver_name, mesh_name, as_point=False, tree_based=False):
    """
    uses the Function set Shape to get the closestPoint positions.
    :param driver_name: <str> the driving object.
    :param mesh_name:  <str> the mesh object.
    :param as_point: <bool> if True, return as a <OpenMaya.MPoint> object. Else return as a tuple(x, y, z).
    :param tree_based: <bool> get the closest point on nurbsSurface using treeBased algorithm.
    :return: <tuple> x, y, z. <OpenMaya.MPoint>.
    """
    shape_fn = object_utils.get_shape_fn(mesh_name)
    # the get_shape_obj function returns a tuple of children items, so we only need one.
    shape_obj = object_utils.convert_list_to_str(object_utils.get_shape_obj(mesh_name))

    mesh_dag = object_utils.get_dag(mesh_name)
    driver_vector = transform_utils.Transform(driver_name).translate_values(as_m_vector=True)

    m_matrix = mesh_dag.inclusiveMatrixInverse()

    if object_utils.is_shape_nurbs_surface(mesh_name):
        m_point = OpenMaya.MPoint(driver_vector)
        if tree_based:
            m_nurb_intersect = OpenMaya.MNurbsIntersector()
            m_nurb_intersect.create(shape_obj, m_matrix)
            point_nurb = OpenMaya.MPointOnNurbs()
            m_nurb_intersect.getClosestPoint(m_point, point_nurb)
            result_point = point_nurb.getPoint()
        else:
            m_point *= m_matrix
            result_point = shape_fn.closestPoint(m_point)
        if as_point:
            return result_point
        return unpack_vector(result_point * mesh_dag.inclusiveMatrix())

    elif object_utils.is_shape_mesh(mesh_name):
        m_point = OpenMaya.MPoint(driver_vector)
        result_m_point = OpenMaya.MPoint()
        shape_fn.getClosestPoint(m_point, result_m_point)
        if as_point:
            return result_m_point
        return unpack_vector(result_m_point)

    elif object_utils.is_shape_nurbs_curve(mesh_name):
        m_point = OpenMaya.MPoint(driver_vector)
        m_point *= m_matrix
        result_point = shape_fn.closestPoint(m_point)
        if as_point:
            return result_point
        return unpack_vector(result_point * mesh_dag.inclusiveMatrix())

    else:
        OpenMaya.MGlobal.displayError("[ClosestPoint] :: Invalid object.")
        return False


def unpack_vector(m_vector=None):
    """
    unpacks the vector into a tuple x, y, z
    :param m_vector: <OpenMaya.MVector>, <OpenMaya.MPoint>
    :return: <tuple> x, y, z values.
    """
    if isinstance(m_vector, (OpenMaya.MVector, OpenMaya.MPoint)):
        return m_vector.x, m_vector.y, m_vector.z,
    else:
        return None, None, None,
