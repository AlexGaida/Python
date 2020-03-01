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


def attach_follicle(follicle_name, mesh_name):
    """
    attaches a follicle to the specified mesh object.
    :param follicle_name: <str> the follicle object name.
    :param mesh_name: <str> the shape object name. Could be a nurbsSurface to a mesh object.
    :return: <bool> True for success. <bool> False for failure.
    """
    shape_m_obj = object_utils.get_m_shape(mesh_name)
    shape_name = object_utils.get_shape_name(mesh_name)
    shape_fn = object_utils.get_shape_fn(mesh_name)
    foll_shape_name = object_utils.get_shape_name(follicle_name)
    foll_parent_name = object_utils.get_parent_name(follicle_name)

    if object_utils.check_shape_type_name(shape_m_obj, 'nurbsSurface'):
        attr_connect(attr_name(shape_name, 'matrix'), attr_name(follicle_name, 'inputWorldMatrix'))
        attr_connect(attr_name(shape_name, 'worldSpace[0]'), attr_name(follicle_name, 'inputSurface'))

    elif object_utils.check_shape_type_name(shape_m_obj, 'mesh'):
        attr_connect(attr_name(shape_name, 'worldMatrix[0]'), attr_name(follicle_name, 'inputWorldMatrix'))
        attr_connect(attr_name(shape_name, 'outMesh'), attr_name(follicle_name, 'inputMesh'))

    attr_connect(attr_name(foll_shape_name, 'outRotate'), attr_name(foll_parent_name, 'rotate'))
    attr_connect(attr_name(foll_shape_name, 'outTranslate'), attr_name(foll_parent_name, 'translate'))
    return True


def attach_closest_point_node(driver_name, mesh_name, follicle_name):
    """
    attaches the closest point node.
    :param driver_name: <str> the driving object.
    :param mesh_name:  <str> the mesh object.
    :param follicle_name: <str> the follicle transform object.
    :return: <str> closestPoint node.
    """
    shape_m_obj = object_utils.get_m_shape(mesh_name)
    shape_name = object_utils.get_shape_name(mesh_name)
    foll_shape_name = object_utils.get_shape_name(follicle_name)

    if object_utils.check_shape_type_name(shape_m_obj, 'nurbsSurface'):
        node_name = closest_point_surface_node_name(driver_name)
        cmds.createNode('closestPointOnSurface', name=node_name)
        attr_connect(attr_name(shape_name, 'worldSpace[0]'), attr_name(node_name, 'inputSurface'))

    elif object_utils.check_shape_type_name(shape_m_obj, 'mesh'):
        node_name = closest_point_mesh_node_name(driver_name)
        cmds.createNode('closestPointOnMesh', name=follicle_name(driver_name))
        attr_connect(attr_name(shape_name, 'worldMesh[0]'), attr_name(node_name, 'inMesh'))

    attr_connect(attr_name(driver_name, 'translate'), attr_name(node_name, 'inPosition'))
    attr_connect(attr_name(node_name, 'parameterU'), attr_name(foll_shape_name, 'parameterU'))
    attr_connect(attr_name(node_name, 'parameterV'), attr_name(foll_shape_name, 'parameterV'))
    return follicle_name(driver_name)


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

    if object_utils.is_shape_nurbs_surface(mesh_name):
        m_matrix = mesh_dag.inclusiveMatrixInverse()
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

    if object_utils.is_shape_mesh(mesh_name):
        m_point = OpenMaya.MPoint(driver_vector)
        result_m_point = OpenMaya.MPoint()
        shape_fn.getClosestPoint(m_point, result_m_point)
        if as_point:
            return result_m_point
        return unpack_vector(result_m_point)


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
