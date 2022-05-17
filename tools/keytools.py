#!/usr/bin/env python
"""

::

    Name :          keytools.py
    Maintained by : Alex Gaidachev
    Description :   functions pertaining the manipulation of anim curves in maya.

                    [ ] A note about how Maya counts time:

                        Maya converts each frame into ticks: tick is the smallest incrementation of time.
                        1 tick: 1/6000th of a second.
                        6000 ticks per second [tps].
                        rate of 24 frames per second [fps].
                        250 ticks per frame [tpf].

                    How to use this information:
                        the ticks per frame varies depending on the playback speed [fps]
                        6000 / 15[fps] --> 400 [tpf]

                    Maya Documentation Link:
                    https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2015/ENU/Maya/files/How-Maya-counts-time-htm.html

                    [ ] Animation curve types - needed to be specified during creation to avoid implicit conversion nodes.

                        timeToAngular (animCurveTA)
                        timeToLinear (animCurveTL)
                        timeToTime (animCurveTT)
                        timeToUnitless (animCurveTU)
                        unitlessToAngular (animCurveUA)
                        unitlessToLinear (animCurveUL)
                        unitlessToTime (animCurveUT)
                        unitlessToUnitless (animCurveUU)



from tmalibmaya.utils import keytools
reload(keytools)
"""
# ______________________________________________________________________________________________________________________

# STANDARD IMPORTS
import time

# STUDIO IMPORTS
from tmalibmaya.utils import animUtils
from tmalibmaya.utils import pointerUtils

# THIRD PARTY IMPORTS
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import cmds
from maya import mel

# LOCAL VARIABLES
# we get the conversion of 1 radian = 180 / pi
RADIANS_2_DEGREES = 57.29577951308232
TANGENT_TYPES_STR_DICT = {
    'global': OpenMayaAnim.MItKeyframe.kTangentGlobal,
    # 'spline': OpenMayaAnim.MItKeyframe.kTangentSpline,
    'fixed': OpenMayaAnim.MItKeyframe.kTangentFixed,
    'linear': OpenMayaAnim.MItKeyframe.kTangentLinear,
    'flat': OpenMayaAnim.MItKeyframe.kTangentFlat,
    'smooth': OpenMayaAnim.MItKeyframe.kTangentSmooth,
    'slow': OpenMayaAnim.MItKeyframe.kTangentSlow,
    'fast': OpenMayaAnim.MItKeyframe.kTangentFast,
    # 'auto': OpenMayaAnim.MItKeyframe.kTangentAuto, 11
    'clamped': OpenMayaAnim.MItKeyframe.kTangentClamped,
    'plateau': OpenMayaAnim.MItKeyframe.kTangentPlateau,
    'step': OpenMayaAnim.MItKeyframe.kTangentStep,
    'stepnext': OpenMayaAnim.MItKeyframe.kTangentStepNext,
    'auto': 18,
}


INFINITY_TYPES_STR_DICT = {
    'constant': OpenMayaAnim.MFnAnimCurve.kConstant,
    'linear': OpenMayaAnim.MFnAnimCurve.kLinear,
    'cycle': OpenMayaAnim.MFnAnimCurve.kCycle,
    'cyclerelative': OpenMayaAnim.MFnAnimCurve.kCycleRelative,
    'oscillate': OpenMayaAnim.MFnAnimCurve.kOscillate,
}

ANIMATION_CURVE_TYPES = {
    'time': {'distance': 'animCurveTL',
             'angle': 'animCurveTA',
             'time': 'animCurveTT',
             'double': 'animCurveTU',
             'unknown': 'kAnimCurveUnknown',
             },
    'double': {'distance': 'animCurveUL',
               'angle': 'animCurveUA',
               'time': 'animCurveUT',
               'double': 'animCurveUU',
               'unknown': 'kAnimCurveUnknown',
              }
}

ANIMATION_CURVE_STR_DICT = {
    'animCurveTL': 'distance',
    'animCurveTT': 'time',
    'kAnimCurveUnknown': 'unknown',
    'animCurveTU': 'double',
    'animCurveTA': 'angle',
    'animCurveUA': 'angle',
    'animCurveUL': 'distance',
    'animCurveUT': 'time',
    'animCurveUU': 'double'
}

FPS_STR_DICT = {
    'film': 24.0,
    'games': 15.0,
    'PALFrame': 25.0,
    'NTSCFrame': 30.0,
    'ShowScan': 48.0,
    'PALField': 50.0,
    'NTSCField': 60.0,
    'default': 24.0
}


# reverse the dictionary to get the tangnet type strings from integers
TANGENT_TYPES_INT_DICT = {}
for k_str, k_int in TANGENT_TYPES_STR_DICT.items():
    TANGENT_TYPES_INT_DICT[k_int] = k_str


INFINITY_TYPES_INT_DICT = {}
for k_str, k_int in INFINITY_TYPES_STR_DICT.items():
    INFINITY_TYPES_STR_DICT[k_int] = k_str

# ______________________________________________________________________________________________________________________


def multiplicative_rounding(float_number, precision=4):
    """Multiplicative rounding is faster than the python rounding function.
    However, there are rounding errors when concerning negative numbers so we multiply -1 at the end

    Args:
        float_number (float): floating digit to round off at the precision level of significant digits.
        precision (int): precision level for rounding out the floating digits.

    Returns:

    """
    reverse_int = 1.0
    if float_number < 0.0:
        reverse_int = -1.0
        float_number *= -1
    p = float(10 ** precision)
    rounded_number = int(float_number * p + 0.5) / p
    return reverse_int * rounded_number


def prune_keyframes_from_nodes_array(nodes, angle_tolerance=0.001, value_tolerance=0.001, with_undo=True):
    """Prunes all keyframe objects from the selected objects.

    Args:
        nodes (tuple, list): array of nodes to remove redundant keys from..
        angle_tolerance (float): Tangents with angles below this value will be considered flat.
        value_tolerance (float): Neighboring values that fall within this tolerance will be considered matching.
        with_undo (bool): performs the operation with undo capability, otherwise proceed with OpenMaya cutting of keys.

    Returns:

    """
    for node in nodes:
        prune_keyframes_from_object_str(node, angle_tolerance=angle_tolerance,
                                        value_tolerance=value_tolerance, with_undo=with_undo)


def prune_keyframes_from_object_str(node, angle_tolerance=0.001, value_tolerance=0.001, with_undo=True):
    """Prunes all keyframe objects from the selected objects.

    Args:
        node (str): object to prune keyframes from.
        angle_tolerance (float): Tangents with angles below this value will be considered flat.
        value_tolerance (float): Neighboring values that fall within this tolerance will be considered matching.
        with_undo (bool): performs the operation with undo capability, otherwise proceed with OpenMaya cutting of keys.

    Returns:

    """
    m_obj = get_m_object(node)
    prune_keyframes_from_obj(m_obj,
                             angle_tolerance=angle_tolerance,
                             value_tolerance=value_tolerance,
                             with_undo=with_undo)


def prune_keyframes_from_obj(node, angle_tolerance=0.001, value_tolerance=0.001, with_undo=True):
    """Prunes all keyframe objects from the selected objects.

    Args:
        node (OpenMaya.MObject): object to prune keyframes from.
        angle_tolerance (float): Tangents with angles below this value will be considered flat.
        value_tolerance (float): Neighboring values that fall within this tolerance will be considered matching.
        with_undo (bool): performs the operation with undo capability, otherwise proceed with OpenMaya cutting of keys.

    Returns:

    """
    total_keys_deleted = 0
    transform_name = OpenMaya.MFnDependencyNode(node).name()
    anim_node_iter = get_connected_upstream_node_type_iter(node, OpenMaya.MFn.kAnimCurve, full_name=False)
    obj_key_length = 0
    data_collection_time = 0.0
    deletion_time = 0.0
    start_time = time.time()
    deletion = {}
    for anim_curve_obj in anim_node_iter:
        anim_curve_node = OpenMaya.MFnDependencyNode(anim_curve_obj).name()
        anim_fn = OpenMayaAnim.MFnAnimCurve(anim_curve_obj)
        number_of_keys = anim_fn.numKeys()

        # get the data of this curve node
        # key_values = cmds.keyframe(anim_curve_node, query=True, valueChange=True)
        # in_angles = cmds.keyTangent(anim_curve_node, query=True, inAngle=True)
        # out_angles = cmds.keyTangent(anim_curve_node, query=True, outAngle=True)
        # out_tangent_names = cmds.keyTangent(anim_curve_node, query=True, outTangentType=True)

        in_angles = get_anim_curve_in_angles_from_obj(anim_curve_obj)
        out_angles = get_anim_curve_out_angles_from_obj(anim_curve_obj)
        out_tangent_names = get_anim_curve_out_tangent_names_from_obj(anim_curve_obj)
        key_values = get_anim_curve_values_from_obj(anim_curve_obj)
        key_times = get_anim_curve_times_from_obj(anim_curve_obj)
        deletion[anim_curve_node] = {}

        # make absolute values of in angle and out angle
        in_angles = tuple(map(abs, in_angles))
        out_angles = tuple(map(abs, out_angles))

        if number_of_keys == 1:
            continue

        delete_indices = ()
        for idx in range(number_of_keys):
            # as long as the current keyframe is between 0, and less than the total number of keyframes, continue
            if idx == 0 or idx == (number_of_keys - 1):
                continue

            # if the index exceeds the length of keys, the next keyframe will be the current key.
            next_index = idx + 1
            prev_index = idx - 1

            # get the outTangentType of the previous frame, the current frame, and the next frame.
            # check the out tangents for type OpenMayaAnim.MItKeyframe.kTangentStep
            prev_out_tangent = out_tangent_names[prev_index]
            curr_out_tangent = out_tangent_names[idx]
            next_out_tangent = out_tangent_names[next_index]

            prev_out_angle = out_angles[prev_index]
            curr_in_angle = in_angles[idx]
            curr_out_angle = out_angles[idx]
            next_in_angle = in_angles[next_index]

            stepped = (prev_out_tangent == "step" and
                       curr_out_tangent == "step" and
                       next_out_tangent == "step")

            # check for one of the following conditions (1 or 2) is true:
            # 1)  $stepped is true (1)
            # 2)  outAngle of the previous frame is less than angleTol
            # &   inAngle of the current frame is less than angleTol
            # &   outAngle of the current frame is less than angleTol
            # &   inAngle of the next frame is less than angleTol
            if (stepped or
                    prev_out_angle < angle_tolerance and
                    curr_in_angle < angle_tolerance and
                    curr_out_angle < angle_tolerance and
                    next_in_angle < angle_tolerance):
                # get the difference of the current value against the previous value
                prev_value_diff = abs(key_values[prev_index] - key_values[idx])
                # get the difference of the next value against the previous value
                next_value_diff = abs(key_values[next_index] - key_values[idx])

                # If one of the following (1 or 2) conditions is true, set $deleteIndex:
                # 1)  $stepped is true (1)
                # &   $prevValDif is less than valueTol
                # 2)  $stepped is false (0)
                # &   $prevValDif is larger than valueTol
                # &   $nextValDif is larger than $valueTol
                if (stepped and
                        prev_value_diff < value_tolerance or
                    not stepped and
                        prev_value_diff < value_tolerance and
                        next_value_diff < value_tolerance):
                    delete_indices += idx,
                    deletion[anim_curve_node][key_times] = idx

        end_time = time.time()
        data_collection_time += end_time - start_time

        # remove the keyframes
        start_time = time.time()
        delete_key_length = len(delete_indices)
        obj_key_length += delete_key_length
        total_keys_deleted += delete_key_length
        if delete_key_length:
            # keys are automatically sorted at removal so we need to reverse our sorted delete_indices for deletion
            if with_undo:
                anim_curve_name = OpenMaya.MFnDependencyNode(anim_curve_obj).name()
                # it's faster to remove keys on a massive scale using MEL
                mel_str = """cutKey -clear"""
                for idx in reversed(delete_indices):
                    # cmds.cutKey(anim_curve_name, index=(idx, idx), clear=True)
                    mel_str += " -index {} ".format(idx)
                mel_str += anim_curve_name
                mel.eval(mel_str)
            else:
                for idx in reversed(delete_indices):
                    anim_fn.remove(idx)
        end_time = time.time()
        deletion_time += end_time - start_time
    print(deletion)
    print("[PruneDataCollection] :: Took {} seconds.".format(data_collection_time))
    print("[KeyDeletion] :: Took {} seconds.".format(deletion_time))
    print("[PruneKeyframes] :: Total time elapsed: {}.".format(data_collection_time + deletion_time))
    print("[PruneKeyframes] :: {} Keyframes deleted from: {}.".format(obj_key_length, transform_name))


def get_anim_curve_out_angles_from_obj(anim_curve_obj, as_degrees=True):
    """

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    out_angles = OpenMaya.MFloatArray()
    index = 0
    while not anim_keys_iter.isDone():
        angle_out, weight_out = get_tangent_out_angle_and_weight_from_curve_obj(anim_curve_obj, index, as_degrees=as_degrees)
        out_angles.append(angle_out)
        index += 1
        anim_keys_iter.next()
    return out_angles


def get_anim_curve_in_angles_from_obj(anim_curve_obj, as_degrees=True):
    """

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    out_angles = OpenMaya.MFloatArray()
    index = 0
    while not anim_keys_iter.isDone():
        angle_out, weight_out = get_tangent_out_angle_and_weight_from_curve_obj(anim_curve_obj, index, as_degrees=as_degrees)
        out_angles.append(angle_out)
        index += 1
        anim_keys_iter.next()
    return out_angles


def get_anim_curve_out_tangent_names_from_obj(anim_curve_obj):
    """

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    out_tangent_names = []
    while not anim_keys_iter.isDone():
        tangent_name = TANGENT_TYPES_INT_DICT[anim_keys_iter.outTangentType()]
        out_tangent_names.append(tangent_name)
        anim_keys_iter.next()
    return out_tangent_names


def get_anim_curve_values_from_obj(anim_curve_obj):
    """

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    is_angle = is_curve_type_angle(anim_curve_obj)
    key_values = ()
    while not anim_keys_iter.isDone():
        anim_value = anim_keys_iter.value()
        # apply radians to degrees conversion
        if is_angle:
            anim_value = RADIANS_2_DEGREES * anim_value
        key_values += anim_value,
        anim_keys_iter.next()
    return key_values


def is_curve_type_angle(anim_curve_obj):
    """Checks if the curve type is an angle

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_fn = OpenMayaAnim.MFnAnimCurve(anim_curve_obj)
    return ANIMATION_CURVE_STR_DICT[anim_fn.typeName()] == 'angle'


def get_anim_curve_times_from_obj(anim_curve_obj):
    """

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    key_times = ()
    while not anim_keys_iter.isDone():
        key_times += anim_keys_iter.time().value(),
        anim_keys_iter.next()
    return key_times


def get_anim_curve_data_arrays(anim_curve_obj):
    """get anim curve data from array of curve nodes provided.
        returns the following items:
            time: X- Axis values.
            value: Y-Axis values at time.
            tangents: out: x, y, locked, type, in: x, y, locked, type,

    Args:
        anim_curve_obj (OpenMaya.MObject): anim curve node.

    Returns:
        (MFloatArray, MFloatArray, MFloatArray): inAngle array, outAnge array, tangentType array.

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    out_angles = ()
    in_angles = ()
    out_tangent_names = ()
    key_values = ()
    key_times = ()
    index = 0
    while not anim_keys_iter.isDone():
        angle_out, weight_out = get_tangent_out_angle_and_weight_from_curve_obj(anim_curve_obj, index)
        angle_in, weight_in = get_tangent_in_angle_and_weight_from_curve_obj(anim_curve_obj, index)
        out_angles += angle_out,
        in_angles += angle_in,
        out_tangent_names += TANGENT_TYPES_INT_DICT[anim_keys_iter.outTangentType()],
        key_values += anim_keys_iter.value(),
        key_times += anim_keys_iter.time().value(),
        anim_keys_iter.next()
    return in_angles, out_angles, out_tangent_names, key_values, key_times


def get_anim_node_keyframe_data_from_object(object_name):
    """returns all animation time and data. We find the rotations

    Args:
        object_name:

    Returns:

    """
    m_object = get_m_object(object_name)
    anim_curve_objects_iter = get_connected_upstream_node_type_iter(m_object, OpenMaya.MFn.kAnimCurve, full_name=False)
    keyframe_data = {}
    for anim_curve in anim_curve_objects_iter:
        keyframe_data.update(get_anim_curve_data_dict_from_obj(anim_curve))
    return keyframe_data


def get_anim_node_scene_data_dict():
    """Traverse the entire scene in search of animation curves and finding the data.

    Returns:

    """
    keyframe_data = {}
    for anim_curve_obj in get_scene_anim_node_iter():
        cur_fn = OpenMaya.MFnDependencyNode(anim_curve_obj)
        node_name = cur_fn.name()
        keyframe_data[node_name] = get_anim_curve_data_dict_from_obj(anim_curve_obj)
    return keyframe_data


def get_scene_anim_node_iter():
    """returns the animation curve scene iter.

    Returns:

    """
    dag_iter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kAnimCurve)
    while not dag_iter.isDone():
        anim_curve = dag_iter.item()
        yield anim_curve
        dag_iter.next()


def get_anim_curve_data_dict_from_object_str(object_name):
    """

    Args:
        object_name:

    Returns:

    """
    node_obj = get_m_object(object_name)
    anim_data = get_anim_curve_data_dict_from_obj(node_obj)
    return anim_data


def get_anim_curve_data_dict_from_obj(anim_curve_obj):
    """get anim curve data from array of curve nodes provided.
        returns the following items:
            time: X- Axis values.
            value: Y-Axis values at time.
            tangents: out: x, y, locked, type, in: x, y, locked, type,

    Args:
        anim_curve_obj (OpenMaya.MObject): anim curve node.

    Returns:
        (dict): animation curve data.

    """
    anim_curve_data = {}
    key_values = get_anim_keyframe_values(anim_curve_obj)
    key_times = get_anim_keyframe_time_values(anim_curve_obj)
    if not key_values or not key_times:
        print("[AnimCurveData] :: No keyframe data found for: {}".format(
            OpenMaya.MFnDependencyNode(anim_curve_obj).name()
        ))
        return anim_curve_data
    # we need to know if these anim curves are connected to rotations so we can convert it to degrees
    is_angle = is_curve_type_angle(anim_curve_obj)
    if is_angle:
        # apply radians to degrees conversion
        rotational_values = ()
        for rad_value in key_values:
            rotational_values += RADIANS_2_DEGREES * rad_value,
        key_values = rotational_values
    num_of_keys = len(key_times)
    anim_curve_data = {'num_keys': num_of_keys, 'time': key_times, 'values': key_values}
    anim_curve_data.update(get_object_tangents_dict(anim_curve_obj))
    return anim_curve_data


def get_connections_from_node(from_node):
    """return all the connected nodes from this node.

    Args:
        from_node (OpenMaya.MObject): find connections from this node.

    Returns:
        (tuple): array of plug names connected to the specified node.

    """
    connected_plug_names = ()
    from_node_fn = OpenMaya.MFnDependencyNode(from_node)
    from_node_connections_array = OpenMaya.MPlugArray()
    from_node_fn.getConnections(from_node_connections_array)
    for fr_i in range(from_node_connections_array.length()):
        from_plug = from_node_connections_array[fr_i]
        connected_plug_names += from_plug.name(),
    return connected_plug_names


def get_connections_to_node(from_node):
    """Get outgoing connections from node.

    Args:
        from_node:

    Returns:

    """
    connected_plug_names = ()
    from_node_fn = OpenMaya.MFnDependencyNode(from_node)
    from_node_connections_array = OpenMaya.MPlugArray()
    from_node_fn.getConnections(from_node_connections_array)
    for fr_i in range(from_node_connections_array.length()):
        from_plug = from_node_connections_array[fr_i]
        to_connections = OpenMaya.MPlugArray()
        # MPlug::connectedTo(MPLugArray, asDestination, asSource)
        from_plug.connectedTo(to_connections, False, True)
        if to_connections.length() == 0:
            continue
        connected_plug_names += to_connections[0].name(),
    return connected_plug_names


def get_connected_node_plug_names_dict(from_node, to_node):
    """Returns the connections from one node to the other.

    Args:
        from_node (OpenMaya.MObject): from node maya object.
        to_node (OpenMaya.MObject): to_node maya object.

    Returns:
        (dict) from_node.plug : (connected_plugs)

    """
    connected_plugs = {}
    from_node_fn = OpenMaya.MFnDependencyNode(from_node)
    from_node_connections_array = OpenMaya.MPlugArray()
    from_node_fn.getConnections(from_node_connections_array)

    to_node_fn = OpenMaya.MFnDependencyNode(to_node)
    to_node_connections_array = OpenMaya.MPlugArray()
    to_node_fn.getConnections(to_node_connections_array)

    for fr_i in range(from_node_connections_array.length()):
        from_plug = from_node_connections_array[fr_i]
        to_connections = OpenMaya.MPlugArray()
        # bool MPLug::connectedT(MPlugArray& array, bool asDestination, bool asSource)
        from_plug.connectedTo(to_connections, True, False)
        connected_plugs[from_plug.name()] = ()
        for idx in range(to_connections.length()):
            connected_plugs[from_plug.name()] += to_connections[idx].name(),
    return connected_plugs


def get_connected_anim_curve_objects(object_node, full_name=False):
    """return any connected anim nodes to the transform object.

    Args:
        object_node (OpenMaya.MObject): find the anim curves attached to this object.
        full_name (bool): return the nodes in full names instead of MObjects.

    Returns:
        (tuple): animation curve nodes.

    """
    anim_curve_objects_iter = get_connected_upstream_node_type_iter(
        object_node, OpenMaya.MFn.kAnimCurve, full_name=full_name)
    anim_curve_objects = ()
    for pair_blend in anim_curve_objects_iter:
        anim_curve_objects += pair_blend,
    return anim_curve_objects


def get_connected_downstream_node_type_iter(object_node, node_type, full_name=False):
    """return any connected anim nodes upstream from the transform object.

    Args:
        object_node (OpenMaya.MObject): find the anim curves attached to this object.
        node_type (OpenMaya.MFn.Type): the object type to find connected to the specified node.
        full_name (bool): return the nodes in full names instead of MObjects.

    Returns:
        (tuple): animation curve nodes.

    """
    dag_iter = OpenMaya.MItDependencyGraph(object_node,
                                           node_type,
                                           OpenMaya.MItDependencyGraph.kDownstream,
                                           OpenMaya.MItDependencyGraph.kBreadthFirst,
                                           OpenMaya.MItDependencyGraph.kNodeLevel)

    while not dag_iter.isDone():
        cur_item = dag_iter.currentItem()
        if full_name:
            cur_fn = OpenMaya.MFnDependencyNode(cur_item)
            node_name = cur_fn.name()
            yield node_name
        else:
            yield cur_item
        dag_iter.next()


def get_connected_transform_from_anim_curve_obj(anim_curve_obj):
    """

    Returns:

    """
    transform_iter = get_connected_downstream_node_type_iter(anim_curve_obj, OpenMaya.MFn.kTransform, full_name=True)
    for transform in transform_iter:
        return transform


def get_connected_pair_blend_objects(object_node, full_name=False):
    """return any connected anim nodes to the transform object.

    Args:
        object_node (OpenMaya.MObject): find the anim curves attached to this object.
        full_name (bool): return the nodes in full names instead of MObjects.

    Returns:
        (tuple): animation curve nodes.

    """
    pair_blend_objects_iter = get_connected_upstream_node_type_iter(
        object_node, OpenMaya.MFn.kPairBlend, full_name=full_name)
    pair_blend_objects = ()
    for pair_blend in pair_blend_objects_iter:
        pair_blend_objects += pair_blend,
    return pair_blend_objects


def get_connected_upstream_node_type_iter(object_node, node_type, full_name=False):
    """return any connected anim nodes upstream from the transform object.

    Args:
        object_node (OpenMaya.MObject): find the anim curves attached to this object.
        node_type (OpenMaya.MFn.Type): the object type to find connected to the specified node.
        full_name (bool): return the nodes in full names instead of MObjects.

    Returns:
        (tuple): animation curve nodes.

    """
    dag_iter = OpenMaya.MItDependencyGraph(object_node,
                                           node_type,
                                           OpenMaya.MItDependencyGraph.kUpstream,
                                           OpenMaya.MItDependencyGraph.kBreadthFirst,
                                           OpenMaya.MItDependencyGraph.kNodeLevel)

    while not dag_iter.isDone():
        cur_item = dag_iter.currentItem()
        if full_name:
            cur_fn = OpenMaya.MFnDependencyNode(cur_item)
            node_name = cur_fn.name()
            yield node_name
        else:
            yield cur_item
        dag_iter.next()


def get_m_object(object_name):
    """returns the m object of the string object.

    Args:
        object_name (str) object name to turn into maya object.

    Returns:

    """
    om_sel = OpenMaya.MSelectionList()
    om_sel.add(object_name)
    node = OpenMaya.MObject()
    om_sel.getDependNode(0, node)
    return node


def object_keyframe_value_iter(anim_curve_obj):
    """iterator object returning the keyframe values (Y-Axis)

    Args:
        anim_curve_obj (OpenMaya.MObject):

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    while not anim_keys_iter.isDone():
        key_value = anim_keys_iter.value()
        anim_keys_iter.next()
        yield key_value


def get_object_tangents_dict(anim_curve_obj):
    """iterator object returning the tangents values (in: X, Y axes, out: X, Y axes)

    Args:
        anim_curve_obj (OpenMaya.MAnimKeyframe):

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    tangents_dict = {}
    index = 0
    while not anim_keys_iter.isDone():
        angle_out, weight_out = get_tangent_out_angle_and_weight_from_curve_obj(anim_curve_obj, index)
        angle_in, weight_in = get_tangent_in_angle_and_weight_from_curve_obj(anim_curve_obj, index)

        value = anim_keys_iter.time().value()
        out_tangent_type = anim_keys_iter.outTangentType()
        in_tangent_type = anim_keys_iter.inTangentType()
        in_tangent_values = get_tangent_in_values(anim_keys_iter)
        out_tangent_values = get_tangent_out_values(anim_keys_iter)
        tangents_dict[value] = {'out': {'type': out_tangent_type, 'type_str': TANGENT_TYPES_INT_DICT[out_tangent_type],
                                        'x': out_tangent_values[0], 'y': out_tangent_values[1],
                                        'angle': angle_out, 'weight': weight_out
                                        },
                                'in': {'type': in_tangent_type, 'type_str': TANGENT_TYPES_INT_DICT[in_tangent_type],
                                       'x': in_tangent_values[0], 'y': in_tangent_values[1],
                                       'angle': angle_in, 'weight': weight_in
                                       },
                                'locked': anim_keys_iter.tangentsLocked()
                                }
        index += 1
        anim_keys_iter.next()
    return tangents_dict


def get_selected_objs_iter():
    """returns the selected objects iter

    Returns:

    """

    m_list = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(m_list)
    m_iter = OpenMaya.MItSelectionList(m_list, OpenMaya.MFn.kTransform)

    while not m_iter.isDone():
        m_dag = OpenMaya.MDagPath()
        m_iter.getDagPath(m_dag)
        yield m_dag.node()
        m_iter.next()


def get_tangent_out_angle_and_weight_from_curve_obj(anim_curve_obj, key_index, as_degrees=True):
    """

    Args:
        anim_curve_obj (OpenMaya.OpenMayaAnim):
        key_index: (int): the keyframe count index.
        as_degrees (bool): default: True, returns the angle value as degrees.

    Returns:
        (float, float): angle, weight.

    """
    anim_curve_fn = OpenMayaAnim.MFnAnimCurve(anim_curve_obj)
    weight_ptr = pointerUtils.create_double_ptr()
    m_angle = OpenMaya.MAngle()
    # True: InTangent, False: OutTangent
    anim_curve_fn.getTangent(key_index, m_angle, weight_ptr, False)
    weight = pointerUtils.get_double_from_double_ptr(weight_ptr)
    if as_degrees:
        angle = m_angle.asDegrees()
    else:
        angle = m_angle.asRadians()
    return angle, weight


def get_tangent_in_angle_and_weight_from_curve_obj(anim_curve_obj, key_index, as_degrees=True):
    """

    Args:
        anim_curve_obj (OpenMaya.OpenMayaAnim):
        key_index: (int): the keyframe count index.
        as_degrees (bool): default: True, returns the angle value as degrees.

    Returns:
        (float, float): angle, weight.

    """
    anim_curve_fn = OpenMayaAnim.MFnAnimCurve(anim_curve_obj)
    weight_ptr = pointerUtils.create_double_ptr()
    m_angle = OpenMaya.MAngle()
    # True: InTangent, False: OutTangent
    anim_curve_fn.getTangent(key_index, m_angle, weight_ptr, True)
    weight = pointerUtils.get_double_from_double_ptr(weight_ptr)
    if as_degrees:
        angle = m_angle.asDegrees()
    else:
        angle = m_angle.asRadians()
    return angle, weight


def get_tangent_out_values(anim_key_iter):
    """Return the out tangent values

    Args:
        anim_key_iter:

    Returns:

    """
    x_ptr = pointerUtils.create_double_ptr()
    y_ptr = pointerUtils.create_double_ptr()
    anim_key_iter.getTangentOut(x_ptr, y_ptr)
    x = pointerUtils.get_double_from_double_ptr(x_ptr)
    y = pointerUtils.get_double_from_double_ptr(y_ptr)
    return x, y,


def get_tangent_in_values(anim_key_iter):
    """Return the out tangent values

    Args:
        anim_key_iter:

    Returns:

    """
    x_ptr = pointerUtils.create_double_ptr()
    y_ptr = pointerUtils.create_double_ptr()
    anim_key_iter.getTangentIn(x_ptr, y_ptr)
    x = pointerUtils.get_double_from_double_ptr(x_ptr)
    y = pointerUtils.get_double_from_double_ptr(y_ptr)
    return x, y,


def get_anim_keyframe_values(anim_curve_obj):
    """get all keyframe values (Y-Axis)

    Args:
        anim_curve_obj (OpenMaya.MObject): maya animation curve node.

    Returns:
        (tuple) : key frame values.

    """
    values = ()
    for value in object_keyframe_value_iter(anim_curve_obj):
        values += value,
    return values


def get_anim_keyframe_time_values(anim_curve_obj):
    """

    Args:
        anim_curve_obj:

    Returns:

    """
    key_times = ()
    for key_time in object_keyframe_time_iter(anim_curve_obj):
        key_times += key_time,
    return key_times


def object_keyframe_time_iter(anim_curve_obj):
    """iterator object returning the keyframe times (X-Axis) in seconds.

    Args:
        anim_curve_obj:

    Returns:

    """
    anim_keys_iter = OpenMayaAnim.MItKeyframe(anim_curve_obj)
    while not anim_keys_iter.isDone():
        key_time = anim_keys_iter.time().value()
        anim_keys_iter.next()
        yield key_time


def convert_seconds_to_frame_time(maya_time_float):
    """Each tick represents 1/6000 of a second. So we need to do the conversion from ticks to maya frames.

    Returns:

    """
    maya_framerate = animUtils.get_frame_rate()
    ticks_per_frame = (6000 / maya_framerate)
    frame_time = maya_time_float * ticks_per_frame
    return frame_time


def get_node_from_name(object_name):
    """

    Args:
        object_name:

    Returns:

    """
    m_sel = OpenMaya.MSelectionList()
    obj = OpenMaya.MObject()
    m_sel.add(object_name)
    m_sel.getDependNode(0, obj)
    return obj


def get_start_and_end_scene_time():
    """return scene frame range data. Checks if render globals is on, otherwise get the time slider.

    Returns:
        (int, int, int) start_frame, end_frame, by_frame_step.

    """
    # get render globals
    render_globals_obj = get_node_from_name("defaultRenderGlobals")
    render_globals_fn = OpenMaya.MFnDependencyNode(render_globals_obj)

    animation_plug = render_globals_fn.findPlug("animation")
    # mdg = OpenMaya.MDGContext()  # dependency graph context class
    using_render_globals = animation_plug.asShort()
    # check if render globals used for frame range
    if using_render_globals:
        print("[GetStartAndEndSceneTime] :: Using Render Global Animation Start/ End Frames.")
        start_frame = render_globals_fn.findPlug('startFrame').asFloat()
        end_frame = render_globals_fn.findPlug('endFrame').asFloat()
        by_frame_step = render_globals_fn.findPlug('byFrameStep').asFloat()
    else:
        start_frame_time = OpenMayaAnim.MAnimControl.minTime()
        start_frame = int(start_frame_time.asUnits(start_frame_time.uiUnit()))
        end_frame_time = OpenMayaAnim.MAnimControl.maxTime()
        end_frame = int(end_frame_time.asUnits(end_frame_time.uiUnit()))
        by_frame_step = 1
    return start_frame, end_frame, by_frame_step


def get_playback_speed(frames_per_second):
    """returns the playback speed of the scene

    Args:
        frames_per_second (float): frames per second to determine the actual playback speed.

    Returns:

    """
    playback_speed = OpenMayaAnim.MAnimControl.playbackSpeed() * frames_per_second
    return playback_speed
