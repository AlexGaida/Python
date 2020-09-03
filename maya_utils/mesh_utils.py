"""
mesh_utils.py utility node relating to mesh functions
"""
# import standatd modules
from pprint import pprint

# import maya modules
from maya import OpenMaya
from maya import cmds

# import local modules
import object_utils
from maya_utils import transform_utils
from maya_utils import math_utils

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


def get_selected_components():
    """
    get the string version of the selected components.
    :return:
    """
    m_dag, m_component = object_utils.iterate_items()
    return m_dag.partialPathName(), get_data(m_dag, m_component, index=True)


def get_boundingbox_center(object_name):
    """
    returns the bounding box center.
    :param object_name:
    :return:
    """
    return transform_utils.Transform(object_name).bbox_center()


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
    :param uv_map_name: <str> the UV map name to get coordinates from.
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


def get_mirror_index(mesh_obj, vertex_index=0, world_space=False, object_space=False, deviation_delta=0.00):
    """
    gets the mirror mesh vertex index.
    :param mesh_obj: <str> the mesh object to get mesh data from.
    :param vertex_index: <int> get the position data from this vertex point.
    :param world_space: <bool> if True, get the data from worldSpace position coordinates.
    :param object_space: <bool> if True, get the data from objectSpace position coordinates.
    :param deviation_delta: <float> the deviation delta to get vertex position comparison from.
    :return: <bool>, <bool> False, False for failure. <int>, <tuple> for success.
    """
    mesh_obj = object_utils.get_m_obj(mesh_obj)

    # if nurbsSurface shape
    if object_utils.is_shape_nurbs_surface(mesh_obj):
        msh_iter = OpenMaya.MItSurfaceCV(mesh_obj)

    # if mesh shape
    if object_utils.is_shape_mesh(mesh_obj):
        msh_iter = OpenMaya.MItMeshVertex(mesh_obj)

    # grab the position the index is at
    while not msh_iter.isDone():
        index_num = msh_iter.index()
        if vertex_index == index_num:
            m_point = msh_iter.position(get_space(world_space, object_space))
            break
        msh_iter.next()

    # now find the mirror vertex index by comparing the mirror position
    while not msh_iter.isDone():
        find_point = msh_iter.position(get_space(world_space, object_space))
        index_num = msh_iter.index()
        vector1 = find_point.x, find_point.y, find_point.z
        vector2 = m_point.x * -1, m_point.y, m_point.z
        # compare the second vector with a deviation relative to the first vector
        if compare_positions(vector1, vector2, deviation_delta=deviation_delta, interval_comparison=True):
            return index_num, vector1
        msh_iter.next()
    return False, False


def set_index_position(mesh_obj, vertex_index=0, position=()):
    """
    sets the position of the vertex index.
    :param mesh_obj:
    :param vertex_index: <int> set the position for this vertex index.
    :param position: <tuple> the position vector to set the index at.
    :return: <bool> True for success.
    """
    mesh_obj = object_utils.get_m_obj(mesh_obj)

    # if nurbsSurface shape
    if object_utils.is_shape_nurbs_surface(mesh_obj):
        s_iter = OpenMaya.MItSurfaceCV(mesh_obj)
        while not s_iter.isDone():
            index_num = s_iter.index()
            if vertex_index == index_num:
                s_iter.setPosition(OpenMaya.MPoint(OpenMaya.MVector(*position)))
                break
            s_iter.next()

    # if mesh shape
    if object_utils.is_shape_mesh(mesh_obj):
        msh_iter = OpenMaya.MItMeshVertex(mesh_obj)
        while not msh_iter.isDone():
            index_num = msh_iter.index()
            if vertex_index == index_num:
                msh_iter.setPosition(OpenMaya.MPoint(OpenMaya.MVector(*position)))
                break
            msh_iter.next()
    return True


def get_component_data(objects_array=(), uv=False, position=True,
                       as_m_vector=False, world_space=True, object_space=False,
                       rounded=True):
    """
    get the component indices data
    :param objects_array: <tuple> (optional) array of objects. to iterate over. Else iterates over selected items.
    :param position: <bool> get X, Y, Z position values from component index selected.
    :param uv: <bool> get UV data, not implemented correctly.
    :param as_m_vector: <bool> return as an OpenMaya.MVector object.
    :param world_space: <bool> return the position in world space co-ordinates.
    :param object_space: <bool> return the position in object space co-ordinates.
    :param rounded: <bool> the positional data will be rounded to 4 significant digits.
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

        # if nurbsSurface shape
        if object_utils.is_shape_nurbs_surface(m_dag):
            s_iter = OpenMaya.MItSurfaceCV(m_dag, m_component)
            while not s_iter.isDone():
                key_name = s_iter.index()

                items = init_data_dict(key_name, data_dict=items)

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
                        vector = round(m_point.x, 4), round(m_point.y, 4), round(m_point.z, 4),
                    items.update(updata_data_dict(key_name, 'position', vector, data_dict=items))
                s_iter.next()

        # if mesh shape
        if object_utils.is_shape_mesh(m_dag):
            msh_iter = OpenMaya.MItMeshVertex(m_dag, m_component)
            while not msh_iter.isDone():
                key_name = msh_iter.index()

                items = init_data_dict(key_name, data_dict=items)

                if uv:
                    float2 = object_utils.ScriptUtil((0.0, 0.0), as_float2_ptr=True)
                    msh_iter.getUV(float2.ptr, 'map1')

                    items.update(updata_data_dict(key_name, 'uv', float2.get_float2_item(), data_dict=items))

                if position:
                    m_point = msh_iter.position(get_space(world_space, object_space))
                    if as_m_vector:
                        vector = OpenMaya.MVector(m_point)
                    elif not as_m_vector:
                        vector = round(m_point.x, 4), round(m_point.y, 4), round(m_point.z, 4),
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


def compare_positions(vector_1, vector_2, deviation_delta=0.001, interval_comparison=False):
    """
    compare the two array positions through interval comparison.
    :param vector_1: <tuple>
    :param vector_2: <tuple>
    :param deviation_delta: <float> the deviation delta to match the length against.
    :return: <bool> True if match.
    """
    vector_1 = round(vector_1[0], 4), round(vector_1[1], 4), round(vector_1[2], 4)
    vector_2 = round(vector_2[0], 4), round(vector_2[1], 4), round(vector_2[2], 4)
    if interval_comparison:
        vector_bool = ()
        vector_bool += vector_2[0] - deviation_delta <= vector_1[0] <= vector_2[0] + deviation_delta,
        vector_bool += vector_2[1] - deviation_delta <= vector_1[1] <= vector_2[1] + deviation_delta,
        vector_bool += vector_2[2] - deviation_delta <= vector_1[2] <= vector_2[2] + deviation_delta,
        return all(vector_bool)
    else:
        vector = OpenMaya.MVector(*vector_2) - OpenMaya.MVector(*vector_1)
        return vector.length() <= 0.0


def get_mesh_point_mean(mesh_1="", round_to=4):
    """
    gets the mesh mean float value.
    :param mesh_1:
    :param round_to: <int> round the squared difference by this many significant digits.
    :return:
    """
    mesh_data = get_component_data(mesh_1, position=True, world_space=False, object_space=True)
    x_positions = ()
    y_positions = ()
    z_positions = ()
    for idx, data in mesh_data.items():
        mesh_1_position = data['position'][0]
        x_positions += mesh_1_position[0],
        y_positions += mesh_1_position[1],
        z_positions += mesh_1_position[2],
    return round(math_utils.squared_difference(
        (math_utils.squared_difference(x_positions),
         math_utils.squared_difference(y_positions),
         math_utils.squared_difference(z_positions))), round_to)


def get_point_mean(mesh_1="", mesh_2="", mesh_1_data={}, mesh_2_data={}, round_to=4):
    """
    get the positional data from both mesh and then calculate the average mean from XYZ values.
    :param mesh_1:
    :param mesh_2:
    :return: <tuple> XYZ mean.
    """
    if not mesh_1_data:
        mesh_1_data = get_component_data(mesh_1, position=True, world_space=False, object_space=True)
    if not mesh_2_data:
        mesh_2_data = get_component_data(mesh_2, position=True, world_space=False, object_space=True)
    x_positions = ()
    y_positions = ()
    z_positions = ()
    for idx, data in mesh_1_data.items():
        mesh_1_position = data['position'][0]
        mesh_2_position = mesh_2_data[idx]['position'][0]
        x_positions += mesh_1_position[0] - mesh_2_position[0],
        y_positions += mesh_1_position[1] - mesh_2_position[1],
        z_positions += mesh_1_position[2] - mesh_2_position[2],
    return round(math_utils.squared_difference(
        (math_utils.squared_difference(x_positions),
         math_utils.squared_difference(y_positions),
         math_utils.squared_difference(z_positions))), round_to)


def get_changed_vertices(mesh_1, mesh_2, mirror_x=False, deviation=0.0, round_deviation=4):
    """
    returns a dictionary of delta vertices from the base mesh to the posed shape mesh.
    :param mesh_1: <str> mesh delta
    :param mesh_2: <str> target mesh
    :param mirror_x: <bool>
    :param deviation: <float> (optional) use this deviation to get changed indices.
    :param round_deviation: <int> find the vertex index within this positions' deviation delta.
    :return:
    """
    mesh_1_data = get_component_data(mesh_1, position=True, world_space=False, object_space=True)
    mesh_2_data = get_component_data(mesh_2, position=True, world_space=False, object_space=True)
    if not deviation:
        deviation = get_point_mean(mesh_1_data=mesh_1_data, mesh_2_data=mesh_2_data, round_to=round_deviation)
    print("deviation delta: {}".format(deviation))
    changed_vertices = {}
    for idx, data in mesh_1_data.items():
        mesh_1_position = data['position'][0]
        mesh_2_position = mesh_2_data[idx]['position'][0]

        # first we compare the vertices that have been changed
        if not compare_positions(mesh_1_position, mesh_2_position, deviation):
            if mirror_x:
                # then we start comparing the vertex indices' positions of x * -1
                mir_index, mir_position = get_mirror_index(mesh_2, idx, object_space=True, deviation_delta=deviation)
                if mir_index and mir_position:
                    changed_vertices[mir_index] = mesh_1_position[0] * -1, mesh_1_position[1], mesh_1_position[2]
            else:
                changed_vertices[idx] = mesh_1_position
    return changed_vertices


def get_selected_vertices_mirror():
    """

    :return:
    """
    mesh_name, index_array = get_selected_components()
    vertice_names = map(lambda x: '{}.vtx[{}]'.format(mesh_name, x), index_array)
    deviation_mean = get_mesh_point_mean(mesh_name)
    data = get_component_data(vertice_names)
    mirror = ()
    for idx in data:
        mir_index, mir_position = get_mirror_index(mesh_name, idx, object_space=True, deviation_delta=deviation_mean)
        mirror += mir_index,
    return mirror


def select_vertices_mirror():
    """

    :return:
    """
    vertices = get_selected_vertices_mirror()
    select_indices(vertices)


def select_changed_vertices(mesh1, mesh2, round_deviation=6, mirror_x=False):
    """
    select the difference vertices.
    :param mesh1:
    :param mesh2:
    :param mirror_x:
    :return:
    """
    indices = get_changed_vertices(mesh1, mesh2, mirror_x=mirror_x, round_deviation=round_deviation)
    select_indices(mesh2, indices)


def get_index_name(mesh_name, mesh_index):
    """
    gets the mesh vertex name from the parameters given.
    :param mesh_name:
    :param mesh_index:
    :return:
    """
    return mesh_name + '.vtx[%d]' % mesh_index


def select_indices(mesh_obj, index_array):
    """
    selects index array on the mesh object.
    :param mesh_obj:
    :param index_array:
    :return:
    """
    cmds.select(d=True)
    vertices = ()
    for idx in index_array:
        vertices += get_index_name(mesh_obj, idx),
    cmds.select(vertices)


def copy_mesh_positions(mesh_1, mesh_2, mirror_x=False):
    """
    given two similar mesh objects, copy and set the positional data.
    mesh_1 has the pose, mesh_2 does not have the pose.
    :return:
    """
    indices = get_changed_vertices(mesh_1, mesh_2, mirror_x=mirror_x)
    for idx, vertex in indices.items():
        set_index_position(mesh_2, idx, vertex)
    return True


def get_closest_point(mesh_name="", transform_point=""):
    """
    gets the closest point on mesh from the mesh and transform provided.
    :param mesh_name:
    :param transform_point:
    :return:
    """
    mesh_fn = object_utils.get_shape_fn(mesh_name)[0]
    t = cmds.xform(transform_point, ws=1, t=1, q=1)
    to_this_point = OpenMaya.MPoint(*t)
    result_point = OpenMaya.MPoint()

    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    id_pointer = util.asIntPtr()
    mesh_fn.getClosestPoint(to_this_point, result_point, OpenMaya.MSpace.kTransform, id_pointer)
    return (result_point.x, result_point.y, result_point.z), OpenMaya.MScriptUtil(id_pointer).asInt()


def get_edge_loop_points_at_axis(mesh_name='', axis='z', rounded_to=4, half_loops=True):
    """
    function to get the edge loops of the sphere.
    :param mesh_name: <str> mesh name to get data from.
    :param axis: <str> the axis to get the vertices from.
    :param rounded_to: <int> the rounding digit.
    :return: <dict> axis integers with points.
    """
    data = get_component_data([mesh_name], position=False, world_space=True, object_space=False)
    axes = ('x', 'y', 'z')
    axis_index = axes.index(axis)
    axis_data = {}
    for vtx_id in data:
        position = cmds.xform(mesh_name + '.vtx[{}]'.format(vtx_id), q=1, t=1)
        position_value = round(position[axis_index], rounded_to)
        if position[axis_index] >= 0.0:
            if position_value not in axis_data:
                axis_data[position_value] = ()
            axis_data[position_value] += vtx_id,
    return axis_data
