"""
mesh_utils.py utility node relating to mesh functions
"""
# import maya modules
from maya import OpenMaya

# import local modules
import object_utils

# define local variables
DATA_DICT = {}


def init_data_dict(key_name):
    if key_name not in DATA_DICT:
        DATA_DICT[key_name] = {}
    return DATA_DICT


def updata_data_dict(key_name, data_key, data_value):
    if data_key not in DATA_DICT[key_name]:
        DATA_DICT[key_name][data_key] = ()
    DATA_DICT[key_name][data_key] += data_value,
    return DATA_DICT


def is_component(m_component):
    """
    return the valid status of the component.
    :param m_component:
    :return:
    """
    if m_component.isNull() or not m_component.hasFn(OpenMaya.MFn.kComponent):
        return False
    return True


def is_array_component(objects_array=()):
    """
    check if any array objects are of type component and have valid components.
    :param objects_array:
    :return: <bool> True for success. <bool> False for failure.
    """
    m_iter = object_utils.get_m_selection_iter(objects_array)

    while not m_iter.isDone():
        m_dag = OpenMaya.MDagPath()
        m_component = OpenMaya.MObject()
        m_iter.getDagPath(m_dag, m_component)
        if not is_component(m_component):
            return False
        m_iter.next()
    return True


def get_component_data(objects_array=(), index=False, uv=True, position=True):
    """
    get the component indices
    :param objects_array: <tuple> (optional) array of objects. to iterate over. Else iterates over selected items.
    :param index: <bool> get component index.
    :param position: <bool> get X, Y, Z position values from component index selected.
    :param uv: <bool> get UV data, not implemented correctly.
    :return: <dict> tuples of indices.
    """
    m_iter = object_utils.get_m_selection_iter(objects_array)

    items = {}
    while not m_iter.isDone():
        m_dag = OpenMaya.MDagPath()
        m_component = OpenMaya.MObject()
        m_iter.getDagPath(m_dag, m_component)
        if object_utils.get_shapes_len(m_dag):
            m_shape_dag = object_utils.get_shape_dag(m_dag)
            sel = OpenMaya.MSelectionList()
            sel.add(m_shape_dag)

            m_dag = OpenMaya.MDagPath()
            m_component = OpenMaya.MObject()
            sel.getDagPath(0, m_dag, m_component)

        key_name = m_dag.partialPathName()
        items.update(init_data_dict(key_name))

        if object_utils.is_shape_nurbs_surface(m_dag):
            s_iter = OpenMaya.MItSurfaceCV(m_dag, m_component)
            while not s_iter.isDone():
                if index:
                    items.update(updata_data_dict(key_name, 'index', s_iter.index()))

                if uv:
                    int_u = object_utils.ScriptUtil(as_int_ptr=True)
                    int_v = object_utils.ScriptUtil(as_int_ptr=True)
                    s_iter.getIndex(int_u.ptr, int_v.ptr)

                    items.update(updata_data_dict(key_name, 'uv', (int_u.get_int(), int_v.get_int())))

                if position:
                    m_point = s_iter.position(OpenMaya.MSpace.kWorld)
                    items.update(updata_data_dict(key_name, 'position', (m_point.x, m_point.y, m_point.z)))
                s_iter.next()

        if object_utils.is_shape_mesh(m_dag):
            msh_iter = OpenMaya.MItMeshVertex(m_dag, m_component)
            while not msh_iter.isDone():
                if index:
                    items.update(updata_data_dict(key_name, 'index', msh_iter.index()))
                if uv:
                    float2 = object_utils.ScriptUtil((0.0, 0.0), as_float2_ptr=True)
                    msh_iter.getUV(float2.ptr, 'map1')

                    items.update(updata_data_dict(key_name, 'uv', float2.get_float2_item()))

                if position:
                    m_point = msh_iter.position(OpenMaya.MSpace.kWorld)
                    items.update(updata_data_dict(key_name, 'position', (m_point.x, m_point.y, m_point.z)))
                msh_iter.next()
        m_iter.next()
    return items


def is_points_on_same_edge(point_a, point_b):
    """
    check if the points all share the same edge loop.
    :param point_a: <str> point a.
    :param point_b: <str> point b check relating to point_b.
    :return: <bool> True for yes. <bool> False for no.
    """
    return NotImplementedError("[WIP]")
    m_point_1 = object_utils.get_m_obj(point_a)
    m_point_2 = object_utils.get_m_obj(point_b)

    OpenMaya.MItMeshEdge()
    return False