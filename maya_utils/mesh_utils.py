"""
mesh_utils.py utility node relating to mesh functions
"""
# import standatd modules
from pprint import pprint

# import maya modules
from maya import OpenMaya

# import local modules
import object_utils

# define local variables
DATA_DICT = {}

# define private variables
__verbosity__ = 1


def pprint_verbosity(*args):
    """
    if the module's verbosity is set to True, pprint the incoming data.
    :param args:
    :return:
    """
    if __verbosity__:
        return pprint(args)


def check_and_convert_obj_into_array(object_name=""):
    """
    converts the object into an array tuple.
    :param object_name:
    :return:
    """
    if not isinstance(object_name, (list, tuple)):
        return object_name,
    return object_name


def init_data_dict(key_name, data_dict={}):
    """
    initialize a data dictionary.
    :param key_name:
    :return:
    """
    if key_name not in data_dict:
        data_dict[key_name] = {}
    return data_dict


def updata_data_dict(key_name, data_key, data_value, data_dict={}):
    """
    updates the data dictionary
    :param key_name:
    :param data_key:
    :param data_value:
    :return:
    """
    if data_key not in data_dict[key_name]:
        data_dict[key_name][data_key] = ()
    data_dict[key_name][data_key] = data_value,
    return data_dict


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


def get_space(world_space=False, object_space=False):
    if world_space:
        return object_utils.get_k_space(space='world')
    if object_space:
        return object_utils.get_k_space(space='object')


def get_data(m_dag, m_component, world_space=True, index=False, uv=False,
             position=False, as_m_vector=False, object_space=False, uv_map_name="map1"):
    """
    grabs the data from the m_dag and the m_component parameters given.
    :param m_dag: <OpenMaya.MDagPath>
    :param m_component: <OpenMaya.MObject>
    :param world_space: <bool> if True, get the vectors in world space coordinates.
    :param index: <bool> if True, get the vertex/ CV indices.
    :param uv: <bool> if True, get the UV indices.
    :param position: <bool> if True, get the position x y z.
    :param as_m_vector: <bool> if True, return position in world space.
    :param object_space: <bool> if True, return position in object space.
    :return: <tuple> array of requested items.
    """
    data = ()

    # if nurbsSurface shape
    if object_utils.is_shape_nurbs_surface(m_dag):
        s_iter = OpenMaya.MItSurfaceCV(m_dag, m_component)
        while not s_iter.isDone():
            if index:
                data += s_iter.index(),

            elif uv:
                int_u = object_utils.ScriptUtil(as_int_ptr=True)
                int_v = object_utils.ScriptUtil(as_int_ptr=True)
                s_iter.getIndex(int_u.ptr, int_v.ptr)
                data += int_u.get_int(), int_v.get_int(),

            elif position:
                m_point = s_iter.position(get_space(world_space, object_space))
                if as_m_vector:
                    vector = OpenMaya.MVector(m_point)
                elif not as_m_vector:
                    vector = m_point.x, m_point.y, m_point.z,
                data += vector,
            s_iter.next()
        # end loop

    # if mesh shape
    if object_utils.is_shape_mesh(m_dag):
        msh_iter = OpenMaya.MItMeshVertex(m_dag, m_component)
        while not msh_iter.isDone():
            if index:
                data += msh_iter.index(),

            if uv:
                float2 = object_utils.ScriptUtil((0.0, 0.0), as_float2_ptr=True)
                msh_iter.getUV(float2.ptr, uv_map_name)

            elif position:
                m_point = msh_iter.position(get_space(world_space, object_space))
                if as_m_vector:
                    vector = OpenMaya.MVector(m_point)
                elif not as_m_vector:
                    vector = m_point.x, m_point.y, m_point.z,
                data += vector,
            msh_iter.next()
        # end loop
    return data


def get_component_data(objects_array=(), uv=False, position=True, as_m_vector=False, world_space=True, object_space=False):
    """
    get the component indices data
    :param objects_array: <tuple> (optional) array of objects. to iterate over. Else iterates over selected items.
    :param position: <bool> get X, Y, Z position values from component index selected.
    :param uv: <bool> get UV data, not implemented correctly.
    :param as_m_vector: <bool> return as an OpenMaya.MVector object.
    :param world_space: <bool> return the position in world space co-ordinates.
    :param object_space: <bool> return the position in object space co-ordinates.
    :return: <dict> tuples of indices.
    """
    objects_array = check_and_convert_obj_into_array(objects_array)
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

        # key_name = m_dag.partialPathName()

        # if nurbsSurface shape
        if object_utils.is_shape_nurbs_surface(m_dag):
            s_iter = OpenMaya.MItSurfaceCV(m_dag, m_component)
            while not s_iter.isDone():
                key_name = s_iter.index()
                items = init_data_dict(key_name, data_dict=items)
                # items.update(updata_data_dict(key_name, 'index', s_iter.index()))

                if uv:
                    int_u = object_utils.ScriptUtil(as_int_ptr=True)
                    int_v = object_utils.ScriptUtil(as_int_ptr=True)
                    s_iter.getIndex(int_u.ptr, int_v.ptr)

                    items.update(updata_data_dict(key_name, 'uv', (int_u.get_int(), int_v.get_int()), data_dict=items))

                if position:
                    m_point = s_iter.position(get_space(world_space, object_space))
                    if as_m_vector:
                        vector = OpenMaya.MVector(m_point)
                    elif not as_m_vector:
                        vector = m_point.x, m_point.y, m_point.z,
                    items.update(updata_data_dict(key_name, 'position', vector, data_dict=items))
                s_iter.next()

        # if mesh shape
        if object_utils.is_shape_mesh(m_dag):
            msh_iter = OpenMaya.MItMeshVertex(m_dag, m_component)
            while not msh_iter.isDone():
                key_name = msh_iter.index()
                items = init_data_dict(key_name, data_dict=items)
                # items.update(updata_data_dict(key_name, 'index', msh_iter.index()))

                if uv:
                    float2 = object_utils.ScriptUtil((0.0, 0.0), as_float2_ptr=True)
                    msh_iter.getUV(float2.ptr, 'map1')

                    items.update(updata_data_dict(key_name, 'uv', float2.get_float2_item(), data_dict=items))

                if position:
                    m_point = msh_iter.position(get_space(world_space, object_space))
                    if as_m_vector:
                        vector = OpenMaya.MVector(m_point)
                    elif not as_m_vector:
                        vector = m_point.x, m_point.y, m_point.z,
                    items.update(updata_data_dict(key_name, 'position', vector, data_dict=items))
                msh_iter.next()
        m_iter.next()
    return items


def get_component_position(object_name="", as_m_vector=False, world_space=True, object_space=False):
    """
    get the component position vector
    :param object_name:
    :param as_m_vector: <bool> return OpenMaya.MVector object
    :param world_space: <bool> return position vector in world space.
    :param object_space: <bool> return position vector in object space.
    :return: <tuple> position X, Y, Z values
    """
    data = get_component_data(
        object_name, position=True, world_space=world_space, object_space=object_space)
    pprint_verbosity(data)
    for index, component_data in data.items():
        if as_m_vector:
            return OpenMaya.MVector(*component_data['position'][0])
        elif not as_m_vector:
            return component_data['position'][0]


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