"""
Animation data tools, manipulating animation settings.
Written in both cmds and OpenMaya way.
"""
from importlib import reload
# import standard modules
from math import atan, cos

# import maya modules
from maya import cmds
from maya import mel
from maya import OpenMaya as OpenMaya
from maya import OpenMayaAnim as OpenMayaAnim

# import custom modules
from . import object_utils
from maya_utils import math_utils
from maya_utils import file_utils
from ui_tools import list_tool
reload(list_tool)


# define private variables
__version__ = '1.2.0'
__verbosity__ = 0
__m_util = OpenMaya.MScriptUtil()

__anim_tangentType = {
    OpenMayaAnim.MFnAnimCurve.kTangentGlobal: "kTangentGlobal",
    OpenMayaAnim.MFnAnimCurve.kTangentFixed: "kTangentFixed",
    OpenMayaAnim.MFnAnimCurve.kTangentLinear: "kTangentLinear",
    OpenMayaAnim.MFnAnimCurve.kTangentFlat: "kTangentFlat",
    OpenMayaAnim.MFnAnimCurve.kTangentSmooth: "TangentSmooth",
    OpenMayaAnim.MFnAnimCurve.kTangentStep: "kTangentStep",
    OpenMayaAnim.MFnAnimCurve.kTangentSlow: "kTangentSlow",
    OpenMayaAnim.MFnAnimCurve.kTangentFast: "kTangentFast",
    OpenMayaAnim.MFnAnimCurve.kTangentClamped: "kTangentClamped",
    OpenMayaAnim.MFnAnimCurve.kTangentPlateau: "kTangentPlateau",
    OpenMayaAnim.MFnAnimCurve.kTangentStepNext: "kTangentStepNext",
    OpenMayaAnim.MFnAnimCurve.kTangentAuto: "kTangentAuto",
    OpenMayaAnim.MFnAnimCurve.kTangentAutoMix: "kTangentAutoMix",
    OpenMayaAnim.MFnAnimCurve.kTangentAutoEase: "kTangentAutoEase",
    OpenMayaAnim.MFnAnimCurve.kTangentAutoCustom: "kTangentAutoCustom"
}

__anim_curveType = {
    OpenMayaAnim.MFnAnimCurve.kAnimCurveTA: "kAnimCurveTA",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveTL: "kAnimCurveTL",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveTT: "kAnimCurveTT",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveTU: "kAnimCurveTU",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveUA: "kAnimCurveUA",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveUL: "kAnimCurveUL",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveUT: "kAnimCurveUT",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveUU: "kAnimCurveUU",
    OpenMayaAnim.MFnAnimCurve.kAnimCurveUnknown: "kAnimCurveUnknown"
}

__anim_infinityType = {
    OpenMayaAnim.MFnAnimCurve.kConstant: "kConstant",
    OpenMayaAnim.MFnAnimCurve.kLinear: "kLinear",
    OpenMayaAnim.MFnAnimCurve.kCycle: "kCycle",
    OpenMayaAnim.MFnAnimCurve.kCycleRelative: "kCycleRelative",
    OpenMayaAnim.MFnAnimCurve.kOscillate: "kOscillate"
}


def write_anim_data():
    """writes keyframe data, from selected objects onto a JSON file into a local temp directory
    !for demonstration purposes only
    """
    objects = object_utils.get_selected_objects_gen()
    directory_name = file_utils.temp_dir
    for anim_obj_name in objects:
        data = get_anim_curve_data(anim_obj_name)
        file_name = file_utils.posixpath.join(directory_name, anim_obj_name)
        file_handler = file_utils.JSONSerializer(file_name, data)
        file_handler.write()


def read_anim_data(file_path="", apply_angles=True, apply_xy=False):
    """reads the keyframe data, from a specified file_path
    !for demonstration purposes only
    :param file_path: <str> the file path name
    """
    if not file_path:
        file_name = _get_file_from_dir()
        if not file_name:
            return False
    else:
        if file_utils.is_dir(file_path):
            file_name = _get_file_from_dir(file_path)
        elif file_utils.is_file(file_path):
            if file_utils.has_ext(file_path, 'json'):
                pass
            else:
                raise IOError("File Invalid")
    print("file chosen: {}".format(file_name))
    # ...choose the animation file name
    file_handler = file_utils.JSONSerializer(file_name)
    data = file_handler.read()
    data = check_obj_names_from_data(data)
    if not data:
        raise KeyError("Empty Dictionary, Aborting procedure!")
    add_keys_from_data(data, apply_angles=apply_angles, apply_xy=apply_xy)


def write_anim_data_cmd():
    """writes keyframe data, from selected objects onto a JSON file into a local temp directory
    !for demonstration purposes only
    """
    objects = object_utils.get_selected_objects_gen()
    directory_name = file_utils.temp_dir
    for anim_obj_name in objects:
        data = get_anim_connections(anim_obj_name)
        file_name = file_utils.posixpath.join(directory_name, anim_obj_name)
        file_handler = file_utils.JSONSerializer(file_name, data)
        file_handler.write()


def read_anim_data_cmd(file_path=""):
    """writes keyframe data, from selected objects onto a JSON file into a local temp directory
    !for demonstration purposes only
    """
    if not file_path:
        file_name = _get_file_from_dir()
        if not file_name:
            return False
    else:
        if file_utils.is_dir(file_path):
            file_name = _get_file_from_dir(file_path)
        elif file_utils.is_file(file_path):
            if file_utils.has_ext(file_path, 'json'):
                pass
            else:
                raise IOError("File Invalid")
    print("file chosen: {}".format(file_name))
    # ...choose the animation file name
    file_handler = file_utils.JSONSerializer(file_name)
    data = file_handler.read()
    data = check_obj_names_from_data(data)
    if not data:
        raise KeyError("Empty Dictionary, Aborting procedure!")
    add_keyframes(data)


def _get_file_from_dir(dir_name=""):
    """return file name from directory
    """
    if not dir_name:
        dir_name = file_utils.temp_dir
    files_list = file_utils.get_files(dir_name, strip_dir=True)
    ui = list_tool.openUI(objects_list=files_list, modal=True)
    anim_obj_file_name = ui.selected
    if not anim_obj_file_name:
        return False
    file_path = file_utils.posixpath.join(
        dir_name, anim_obj_file_name)
    return file_path


def check_obj_names_from_data(data):
    """check keyframe node against existing items in the current scene and strip them
    :param data: <dict> parse the given dictionary
    :return: <dict> pruned dictionary
    """
    strip_data = ()
    if 'animNodes' in data:
        data = data['animNodes']
    else:
        data = data
    for keyframe_name in data:
        object_name = keyframe_name.rsplit('_', 1)[0]
        if not cmds.objExists(object_name):
            strip_data += keyframe_name,
    for key_name in strip_data:
        data.pop(key_name)
    return data


def connect_anim(source_object_name, source_attribute_name, dest_object_name, dest_attribute_name, driver_value=1.0):
    """
    connects an attribute using set driven keys.
    benefit: set driven keyframes can be blended into a single driven attribute.
        driver_node='',
        driver_attr='',
        driven_node='',
        driven_attr='',
        driver_value=1.0,
    """
    set_driven_key(source_object_name, source_attribute_name, dest_object_name, dest_attribute_name,
                   driven_value=0.0, driver_value=0.0)
    set_driven_key(source_object_name, source_attribute_name, dest_object_name, dest_attribute_name,
                   driven_value=1.0, driver_value=driver_value)
    # ...
    return True


def get_mfn_anim_node(object_node):
    """
    returns an OpenMaya.MFnAnimCurve object from the object specified.
    :param object_node: <str> object node.
    :return: <OpenMaya.MFnAnimCurve> maya object.
    """
    return OpenMayaAnim.MFnAnimCurve(object_utils.get_m_obj(object_node))


def get_name_from_mfn_anim_node(object_node):
    """
    returns a name of the MFnAnimCurve node.
    :param object_node: <OpenMaya.MFnAnimCurve> maya object.
    :return: <str> curve node name.
    """
    if isinstance(object_node, OpenMayaAnim.MFnAnimCurve):
        return object_node.name()
    return object_node


def set_driven_key(driver_node='',
                   driver_attr='',
                   driven_node='',
                   driven_attr='',
                   driven_value=None,
                   driver_value=None,
                   in_tangent='linear',
                   out_tangent='linear',
                   insert_blend=True):
    """
    perform set driven keyframe command.
    :param driver_node: <str>
    :param driven_node: <str>
    :param driver_attr: <str>
    :param driven_attr: <str>
    :param insert_blend: <bool>
    :param in_tangent: <str> get the tangent type: "auto", clamped",
                        "fast", "flat", "linear", "plateau", "slow", "spline", and "stepnext"
    :param out_tangent: <str>
    :param driven_value: <float>
    :param driver_value: <float>
    :return: <bool> True for success. <bool> False for failure.
    """
    driver_str = '.'.join([driver_node, driver_attr])
    driven_str = '.'.join([driven_node, driven_attr])
    if not driven_value:
        driven_value = round(cmds.getAttr(driven_str), 3)
    if not driver_value:
        driver_value = round(cmds.getAttr(driver_str), 3)
    # understanding limitations: set driven keyframe does not set the keys well when both the controller
    # and the driven object has values.
    cmds.setDrivenKeyframe(driven_str, cd=driver_str,
                           driverValue=driver_value, value=driven_value,
                           inTangentType=in_tangent, outTangentType=out_tangent,
                           insertBlend=insert_blend)
    if __verbosity__:
        print("[Set Driven Key] :: {}: {} >> {}: {}".format(
            driver_str, driver_value, driven_str, driven_value))
    return True


def change_anim_tangents(node_object="", in_tangent='linear', out_tangent='linear'):
    """
    Changes the setting on all anim nodes.
    :param node_object:
    :param in_tangent:
    :param out_tangent:
    :return: <bool> True for success. <bool> False for failure.
    """
    anim_nodes = object_utils.get_connected_anim(node_object)
    cmds.keyTangent(anim_nodes, itt=in_tangent, ott=out_tangent)
    return True


def get_selected_timeslider_anim():
    """
    returns the selected keys in time slider.
    :return: <data>
    """
    a_time_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    return cmds.timeControl(a_time_slider, q=True, rangeArray=True)


def get_time_range():
    """return a range of time from min to max
    """
    min_time = cmds.playbackOptions(min=1, query=True)
    max_time = cmds.playbackOptions(max=1, query=True)
    return min_time, max_time


def get_time_from_idx(a_node="", idx=0):
    """gets time from node and index supplied.
    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    """
    m_time = a_node.time(idx)
    time = m_time.asUnits(OpenMaya.MTime.kFilm)
    return time


def get_value_from_time(a_node="", idx=0):
    """
    gets the value from the time supplied.
    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    :return: <tuple> data.
    """
    data = {}
    time = get_time_from_idx(a_node, idx)
    data.update({'time': time})
    data.update({'value': a_node.value(idx)})
    return data


def get_type_from_node(a_node):
    """returns type from animation node
    :param a_node: MFn.kAnimCurve node.
    :return: <dict> type
    """
    data = {}
    data.update({'type': a_node.animCurveType()})
    return data


def get_properties_from_time(a_node="", idx=0):
    """
    gets keyframe attributes: weightsLocked, tangentsLocked
    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    :return: <dict> data.
    """
    data = {
        "weightsLocked": a_node.weightsLocked(idx),
        # "tangentsLocked": a_node.tangentsLocked(idx),
        "tangentsLocked": False,
        "preInfinityType": a_node.preInfinityType(),
        "postInfinityType": a_node.postInfinityType(),
        "isWeighted": a_node.isWeighted(),
        "isBreakdown": a_node.isBreakdown(idx)
    }
    return data


def get_tangents_angle_from_time(a_node, idx=0):
    """gets the angle value from the time supplied

    the tangents are vector representations of the in/ out values
    angle = atan(y/x)
    weight = x/(3*cos(angle))

    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    :return: <dict> in, out tangents.
    """
    data = {}
    # tangent types
    in_type = a_node.inTangentType(idx)
    out_type = a_node.outTangentType(idx)
    in_type = 3
    out_type = 3
    weight = object_utils.ScriptUtil(as_double_ptr=True)
    angle = OpenMaya.MAngle()
    out_angle = OpenMaya.MAngle()
    angle.setUnit(OpenMaya.MAngle.kRadians)
    # isInTangent = True
    a_node.getTangent(idx, angle, weight.ptr, True)
    # print(idx, angle.asRadians(), True)
    data.update({'in': (in_type, angle.asRadians(), weight.get_double())})
    # isInTangent = False
    a_node.getTangent(idx, out_angle, weight.ptr, False)
    # print(idx, out_angle.asRadians(), False)
    data.update({'out': (out_type, out_angle.asRadians(), weight.get_double())})
    return data


def add_keys_from_data(anim_data={}, offset_value=0, add_key=True, apply_angles=True, apply_xy=True):
    """sets the animation data onto the object name
    :param object_name: <str> the name of the object to add keyframes to
    """
    anim_indices = {}
    for node_name, a_list in anim_data.items():
        # use this node for the undo/ redo behavior
        m_curve_change = OpenMayaAnim.MAnimCurveChange()
        anim_fn = None
        anim_indices[node_name] = {
            'indices': (), 'anim_nodes': (), 'angle_tangents': (), 'property_data': (), 'xy_tangent_data': ()}
        for a_data_dict in a_list:
            for anim_index, a_data_list in a_data_dict.items():
                node_data, xy_tangent_data, angle_tangent_data, property_data, key_type = a_data_list
                m_time = OpenMaya.MTime(
                    node_data["time"] + offset_value, OpenMaya.MTime.kFilm)
                if not anim_fn:
                    # get anim_fn instead of finding a key at time
                    object_name = node_name[:node_name.rfind('_')]
                    anim_fn = find_keyframe(object_name, m_time, anim_index)
                    if not anim_fn:
                        anim_fn, m_dag_mod = add_keyframe_node(
                            node_name, key_type["type"])
                if add_key:
                    anim_fn.addKeyframe(
                        m_time, node_data["value"], angle_tangent_data["in"][0], angle_tangent_data["out"][0], m_curve_change)
                anim_indices[node_name]['indices'] += int(anim_index),
                anim_indices[node_name]['anim_nodes'] += anim_fn,
                anim_indices[node_name]['property_data'] += property_data,
                anim_indices[node_name]['angle_tangents'] += angle_tangent_data,
                anim_indices[node_name]['xy_tangent_data'] += xy_tangent_data,
                anim_fn.evaluate(m_time)
    # the argument is that the tangents aren't created until all the keys have been made
    for anim_node, anim_data in anim_indices.items():
        anim_idxs = anim_data['indices']
        anim_nodes = anim_data['anim_nodes']
        property_data = anim_data['property_data']
        angle_tangent_data = anim_data['angle_tangents']
        xy_tangent_data = anim_data['xy_tangent_data']
        for node_fn in anim_nodes:
            # anim indices start at 1, we want the system to start counting from 0
            for idx, anim_idx in enumerate(anim_idxs):
                # unlock the tangents first, if there are any
                set_properties_at_time(
                    node_fn, property_data[idx], anim_idx)
                # set the XY coordinate to tangents
                if apply_xy:
                    set_tangent_XY_at_time(
                        node_fn, xy_tangent_data[idx], anim_idx)
                # set the angles to tangents
                if apply_angles:
                    set_tangents_angle_at_time(
                        node_fn, angle_tangent_data[idx], anim_idx)
    # MS::kSuccess
    return True


def find_keyframe(keyframe_name, m_time=None, anim_idx=1):
    """finds a keyframe at time
    :param m_time: <OpenMaya.MTime>
    """
    object_name = keyframe_name[:keyframe_name.rfind('_')]
    attribute_name = keyframe_name[keyframe_name.rfind('_') + 1:]
    anim_data = get_anim_connections(keyframe_name)
    if "animNodes" not in anim_data:
        return False
    nodes = anim_data["animNodes"]
    anim_fn = None
    for anim_node, anim_data in nodes.items():
        if keyframe_name in anim_node:
            value_data = anim_data['values']
            if anim_idx in value_data:
                plug_node = object_utils.get_plug(object_name, attribute_name)
                anim_fn = OpenMayaAnim.MFnAnimCurve(plug_node)
                # try:
                #     # find out if there is a key set at a specified time
                #     key_bool = anim_fn.find(m_time, anim_idx)
                # except BaseException:
                #     pass
            break
    return anim_fn


def add_keyframe_node(keyframe_name="", key_type=None):
    """adds a keyframe node to a plug
    :param keyframe_name: str, nodeName_attributeName
    :return: <tuple> MFnAnimCurve, MDagModifier
    """
    if not key_type:
        key_type = OpenMayaAnim.MFnAnimCurve.kTangentGlobal
    anim_fn = OpenMayaAnim.MFnAnimCurve()
    m_dag_mod = OpenMaya.MDagModifier()
    object_name = keyframe_name[:keyframe_name.rfind('_')]
    attribute_name = keyframe_name[keyframe_name.rfind('_') + 1:]
    node = object_utils.get_m_obj(object_name)
    attr_plug_node = object_utils.get_plug(node, attribute_name)
    anim_fn.create(attr_plug_node, key_type, m_dag_mod)
    return anim_fn, m_dag_mod,


def set_properties_at_time(a_node, property_data, idx=0):
    """sets the property infomation onto a keyframe node
    :param a_node: <OpenMaya.MFnAnimCurve> Animation curve node
    :param idx: <int> key index
    """
    a_node.setIsBreakdown(idx, property_data["isBreakdown"])
    a_node.setIsWeighted(property_data["isWeighted"])
    a_node.setWeightsLocked(idx, property_data["weightsLocked"])
    a_node.setTangentsLocked(idx, property_data["tangentsLocked"])
    a_node.setPreInfinityType(property_data["preInfinityType"])
    a_node.setPostInfinityType(property_data["postInfinityType"])


def set_tangents_angle_at_time(a_node, data, idx=0):
    """set the tangent information onto a keyframe node
    :param a_node: <OpenMaya.MFnAnimCurve> Animation curve node
    :param data: <dict> tangent data dictionary
    :param idx: <int> key index
    """
    in_angle = data["in"][1]
    in_weight = data["in"][2]
    out_angle = data["out"][1]
    out_weight = data["out"][2]
    angle = OpenMaya.MAngle()
    angle.setUnit(OpenMaya.MAngle.kRadians)
    # inTangent
    angle.setValue(in_angle)
    # print("in_angle", idx, in_angle, angle.value())
    a_node.setTangent(idx, angle, in_weight, True)
    a_node.setAngle(idx, angle, True)
    a_node.setWeight(idx, in_weight, True)
    # outTangent
    angle.setValue(out_angle)
    # print("out_angle", idx, out_angle, angle.value())
    a_node.setTangent(idx, angle, out_weight, False)
    a_node.setAngle(idx, angle, False)
    a_node.setWeight(idx, out_weight, False)


def set_tangent_XY_at_time(a_node, data, idx=0):
    """set the tangent information onto a keyframe node
    :param a_node: <OpenMaya.MFnAnimCurve> Animation curve node
    :param data: <dict> tangent data dictionary
    :param idx: <int> key index
    """
    in_x = data["xy_in"][1]
    in_y = data["xy_in"][2]
    out_x = data["xy_out"][1]
    out_y = data["xy_out"][2]
    # inTangent
    a_node.setTangent(idx, in_x, in_y, True)
    # outTangent
    a_node.setTangent(idx, out_x, out_y, False)


def get_tangents_from_time(a_node="", idx=0, time=1.0):
    """
    gets the value from the time supplied.
    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    :return: <dict> in, out tangents.
    """
    data = {}
    # get tangent types
    in_type = a_node.inTangentType(idx)
    out_type = a_node.outTangentType(idx)
    x = __m_util.asFloatPtr()
    y = __m_util.asFloatPtr()
    # isInTangent = True
    a_node.getTangent(idx, x, y, True)
    x_value = __m_util.getFloat(x)
    y_value = __m_util.getFloat(y)
    data.update({'xy_in': (in_type, x_value, y_value)})
    # isInTangent = False
    a_node.getTangent(idx, x, y, False)
    x_value = __m_util.getFloat(x)
    y_value = __m_util.getFloat(y)
    data.update({'xy_out': (out_type, x_value, y_value)})
    return data


def get_anim_fn_data(a_node="", as_xy=False):
    """
    get animation data from MFnAnimCurve nodes.
    :return: <dict> animCurve data. <bool> False for failure.
    """
    k_len = a_node.numKeys()
    collection = []
    for i in range(k_len):
        collection.append({i: (get_value_from_time(a_node, i),
                               get_tangents_from_time(a_node, i),
                               get_tangents_angle_from_time(a_node, i),
                               get_properties_from_time(a_node, i),
                               get_type_from_node(a_node)
                               )
                           }
                          ),
    return collection


def get_anim_curve_data(object_name=""):
    """
    """
    # get the anim curve object nodes
    data = {}
    anim_nodes = get_anim_connections(object_name)
    if "animNodes" not in anim_nodes:
        raise ValueError("No Keys Found on Object!")
    for a_node in anim_nodes["animNodes"]:
        entry = {a_node: get_anim_fn_data(get_mfn_anim_node(a_node))}
        data.update(entry)
    return data


def __round(x):
    """rounds to the nearest 0.25
    :param x: <float> number.
    :return: <float> rounded number.
    """
    print(round(x*4)/4)


def set_anim_data(anim_data={}, set_tangents_angle=False, set_tangents_xy=False):
    """sets the existing animation data. This does not create a new key.
    :param anim_data: <dict> animation data from get_anim_data function.
    :param rounded: <bool> flattens the animation data.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not anim_data or not isinstance(anim_data, dict):
        raise ValueError("[SetAnimData :: parameter anim_data is invalid.]")

    for node_name, a_data in anim_data.items():
        if node_name not in a_data:
            continue
        num_keys = a_data[node_name]["num_keys"]
        anim_data = a_data[node_name]["anim_values"]
        mfn_anim = OpenMayaAnim.MFnAnimCurve(node_name)
        for i in range(num_keys):
            a_val, a_time = anim_data[i]
            mfn_anim.setTime(i, a_time)
            mfn_anim.setValue(i, a_val)
            if set_tangents_angle:
                set_tangent_XY_at_time(mfn_anim, a_time)
    return True


def connections_gen(object_name="", attribute="", direction='kDownstream', level='kPlugLevel', ftype=''):
    """get plug connections
    :param object_name: <str> object to check connections frOpenMaya.
    :param direction: <str> specify which direction to traverse.
    :param attribute: <str> find nodes connected to this attribute.
    :param ftype: <str> specify which type to filter.
    :param level: <str> specify which level to traverse.
    """
    # define function variables
    node = object_utils.get_m_obj(object_name)
    direction = eval('OpenMaya.MItDependencyGraph.{}'.format(direction))
    level = eval('OpenMaya.MItDependencyGraph.{}'.format(level))
    if ftype:
        ftype = eval('OpenMaya.MFn.{}'.format(ftype))
        # initiate the iterator object
        dag_iter = OpenMaya.MItDependencyGraph(
            node,
            ftype,
            direction
        )
    else:
        # initiate the iterator object
        dag_iter = OpenMaya.MItDependencyGraph(
            node,
            direction,
            level
        )
    dag_iter.reset()
    # iterate the dependency graph to find what we want.
    while not dag_iter.isDone():
        if not attribute:
            yield object_utils.Item(dag_iter.currentItem())
        elif attribute:
            attribute_name = '{}.{}'.format(object_name, attribute)
            item = object_utils.Item(dag_iter.currentItem())
            plugs = item.source_plugs()
            if filter(lambda x: attribute_name in x, plugs):
                yield item
        dag_iter.next()


def get_anim_connections(object_name=""):
    """get plug connections
    :param object_name: <str> object name to get animation data from.
    :return: <dict> found animation connection plugs.
    """
    found_nodes = {}
    for cur_node in connections_gen(object_name):
        if cur_node.hasFn(OpenMaya.MFn.kBlendWeighted):
            plugs = object_utils.get_plugs(
                cur_node, source=True, ignore_nodes=['kBlendWeighted', 'kUnitConversion', 'kNodeGraphEditorInfo'])
            if "targets" not in found_nodes:
                found_nodes["targets"] = []
            # get plug nodes
            found_nodes["targets"].extend(plugs)
        # find what the curve nodes are attached to.
        if cur_node.hasFn(OpenMaya.MFn.kAnimCurve):
            if "source" not in found_nodes:
                found_nodes["source"] = []
            plugs = object_utils.get_plugs(cur_node, source=False)
            for p_node in plugs:
                if p_node not in found_nodes["source"]:
                    found_nodes["source"].append(p_node)
            # collect anim nodes.
            if "animNodes" not in found_nodes:
                found_nodes["animNodes"] = {}
            anim_fn = OpenMayaAnim.MFnAnimCurve(cur_node)
            if anim_fn.numKeys():
                anim_node = OpenMaya.MFnDependencyNode(cur_node).name()
                found_nodes["animNodes"].update(
                    get_animation_data_from_node(anim_node))
    # change the lists into tuples
    if "source" in found_nodes:
        if found_nodes["source"]:
            found_nodes["source"] = tuple(found_nodes["source"])
    if "targets" in found_nodes:
        if found_nodes["targets"]:
            found_nodes["targets"] = tuple(found_nodes["targets"])
    return found_nodes


def get_animation_data_from_node(object_node=""):
    """get the animation data from the node specified.
    :param object_node: <str> the object to check the data.
    :return: <dict> key data.
    """
    if not object_node:
        return False
    o_anim = None
    # if isinstance(object_node, (str, unicode)):
    if isinstance(object_node, str):
        m_object = object_utils.get_m_obj(object_node)
        o_anim = OpenMayaAnim.MFnAnimCurve(m_object)
    if isinstance(object_node, OpenMayaAnim.MFnAnimCurve):
        o_anim = object_node
        object_node = o_anim.name()
    if isinstance(object_node, OpenMaya.MObject):
        o_anim = OpenMayaAnim.MFnAnimCurve(object_node)
        object_node = o_anim.name()
    # get connections
    source_attr = object_utils.get_plugs(
        object_node, source=True)
    destination_attr = object_utils.get_plugs(
        object_node, source=False,
        ignore_nodes=['kUnitConversion', 'kBlendWeighted', 'kNodeGraphEditorInfo'])
    # get the time from the keys supplied
    number_of_keys = o_anim.numKeys()
    anim_data = {}
    if number_of_keys > 1:
        anim_data[object_node] = {'values': {},
                                  'tangents': {},
                                  'sourceAttr': source_attr,
                                  'targetAttr': destination_attr
                                  }
        for i_key in range(number_of_keys):
            # get the information the old way
            v_float = cmds.keyframe(object_node, q=1, valueChange=1)[i_key]
            try:
                t_float = cmds.keyframe(object_node, floatChange=1, q=1)[i_key]
            except TypeError:
                t_float = i_key
            time = cmds.keyframe(object_node,
                                 q=True, index=(i_key, i_key))[0]
            time = int(time)
            o_x = cmds.getAttr('{}.keyTanOutX[{}]'.format(object_node, i_key))
            o_y = cmds.getAttr('{}.keyTanOutY[{}]'.format(object_node, i_key))
            i_x = cmds.getAttr('{}.keyTanInX[{}]'.format(object_node, i_key))
            i_y = cmds.getAttr('{}.keyTanInY[{}]'.format(object_node, i_key))
            in_angle = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, inAngle=True)
            in_weight = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, inWeight=True)
            out_angle = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, outAngle=True)
            out_weight = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, outWeight=True)
            # ...tangent properties
            lock_tangents = cmds.keyTangent("{}".format(object_node),
                                            time=(time, time), query=True, lock=True)
            out_tangent = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, outTangentType=True)
            in_tangent = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, inTangentType=True)
            weight_lock = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, weightLock=True)
            weight_tangent = cmds.keyTangent("{}".format(object_node), time=(
                time, time), query=True, weightedTangents=True)
            # save the information
            anim_data[object_node]['tangents'][t_float] = {'time': time,
                                                           'xy_out': (o_x, o_y),
                                                           'xy_in': (i_x, i_y),
                                                           'in_angle': (in_angle),
                                                           'in_weight': (in_weight),
                                                           'out_angle': (out_angle),
                                                           'out_weight': (out_weight),
                                                           'keyNum': i_key,
                                                           'lock': lock_tangents,
                                                           'out_tangent': out_tangent,
                                                           'in_tangent': in_tangent,
                                                           'weight_lock': weight_lock,
                                                           'weight_tangent': weight_tangent}
            anim_data[object_node]['values'][t_float] = v_float
    return anim_data


def add_keyframes(data):
    """add keyframe from data provided
    :param data: <dict> 
    """
    anim_dict = data["animNodes"]
    for anim_node, anim_data in anim_dict.items():
        node_name = anim_node.rsplit('_', 1)[0]
        node_attr = anim_node.rsplit('_', 1)[1]
        # set keyframes
        values = anim_data["values"]
        for anim_idx, val in values.items():
            tangent_data = anim_data["tangents"][anim_idx]
            out_tangent = tangent_data['out_tangent']
            if out_tangent:
                out_tangent = out_tangent[0]
                if "fixed" in out_tangent:
                    out_tangent = "auto"
            in_tangent = tangent_data['in_tangent']
            if in_tangent:
                in_tangent = in_tangent[0]
                if "fixed" in in_tangent:
                    in_tangent = "auto"
            time = tangent_data['time']
            # add keyframe
            if not in_tangent and not out_tangent:
                cmds.setKeyframe(node_name, attribute=node_attr, time=[
                    time, time], value=val)
            else:
                cmds.setKeyframe(node_name, attribute=node_attr, time=[
                    time, time], ott=out_tangent, itt=in_tangent, value=val)
        # set key tangents
        for anim_idx, val in values.items():
            tangent_data = anim_data["tangents"][anim_idx]
            time = tangent_data['time']
            lock = tangent_data['lock']
            if lock:
                lock = lock[0]
            if not lock:
                lock = False
            in_angle = tangent_data['in_angle'][0]
            in_weight = tangent_data['in_weight'][0]
            out_angle = tangent_data['out_angle'][0]
            out_weight = tangent_data['out_weight'][0]
            weight_tangent = tangent_data['weight_tangent'][0]
            # set tangents
            cmds.keyTangent(node_name, attribute=node_attr,
                            time=(time, time), edit=True, lock=False)
            cmds.keyTangent(node_name, attribute=node_attr,
                            time=(time, time), edit=True, weightedTangents=weight_tangent)
            # edit key tangents
            cmds.keyTangent(node_name, absolute=True, edit=True, inAngle=in_angle, inWeight=in_weight,
                            time=(time, time), attribute=node_attr, outAngle=out_angle, outWeight=out_weight)


def attribute_name(node_name, target_attr):
    """return an attribute name from node_name and target_attr
    :param node_name: str, name of the node
    :param target_attr: str, name of the attribute
    """
    return node_name + '.' + target_attr


def get_connected_blend_weighted_node(node_name="", target_attr=""):
    """get connected blend weighted node from the node name and the attribute provided.
    :param node_name: <str> the node name to check.
    :param target_attr: <str> the connected target attribute to get the blendWeighted node from.
    :return: <>
    """
    node_attr = attribute_name(node_name, target_attr)
    return object_utils.get_plugs(node_name, attr_name=node_attr, ignore_nodes=['kUnitConversion'])


def get_blend_weighted_values(node_name="", target_attr=""):
    """get the values of the blendWeighted node and calculate the new difference value.
    :param node_name: <str> the name of the node to get the plug connections from
    :param target_attr: find the blendWeighted node from the target attribute.
    :return: <float> difference value.
    """
    # get the blendWeighted node.
    node = get_connected_blend_weighted_node(node_name, target_attr)
    if not node:
        return []
    if object_utils.check_object_type(node, 'blendWeighted'):
        node_name, node_attr = node[0].split('.')
        return cmds.getAttr(node_name + '.input')
    return []


def get_sum(value_data=[]):
    """gets the difference in values.
    :param value_data: <list> the values to get the
    :return: <float> sum of numbers.
    """
    return math_utils.get_sum(value_data)


def get_blend_weighted_sum(node_name="", target_attr=""):
    """get the sum of all values given by the blend weighted node found from the parameters given.
    :param node_name: <str> the node name to get the blend weighted node frOpenMaya.
    :param target_attr: <str> the attribute to get blendWeighted values frOpenMaya.
    :return: <float> the sum of all values.
    """
    return get_sum(get_blend_weighted_values(node_name, target_attr))


def break_tangent(object_name, time_int, attribute_name=None):
    """break the key-tangent
    :param object_name: <str>
    :param time: <int>
    :param attribute_name: <str>
    """
    if not attribute_name:
        attribute_name = 'translateX'
    cmds.keyTangent(object_name, lock=False, edit=True,
                    time=(time_int, time_int), attribute=attribute_name)


def change_tangent_in_angle(anim_node, time_int, in_angle, in_weight, attribute_name=None):
    """change the tangent angle
    :param anim_node: <str>
    :param time: <int>
    :param attribute_name: <str>
    """
    if not attribute_name:
        attribute_name = 'translateX'
    cmds.keyTangent(anim_node, absolute=True, lock=False, edit=True, inAngle=in_angle, inWeight=in_weight,
                    time=(time_int, time_int), attribute=attribute_name)


def change_tangent_xy_in():
    """
    """
# ______________________________________________________________________________________________________________________
# animation_utils.py
