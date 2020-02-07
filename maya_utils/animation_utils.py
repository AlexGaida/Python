"""
Animation data tools, manipulating animation settings.
"""
# import standard modules
from math import acos

# import maya modules
from maya import cmds
from maya import mel
from maya import OpenMaya as om
from maya import OpenMayaAnim as oma

# import custom modules
import object_utils
from object_utils import ScriptUtil


# define local variables
__version__ = '1.0.0'
__verbosity__ = 0
__m_util = om.MScriptUtil()
_float_ptr = ScriptUtil()


def set_key():
    pass


def set_driven_key(driver_node='',
                   driver_attr='',
                   driven_node='',
                   driven_attr='',
                   driven_value=None,
                   driver_value=None,
                   in_tangent='linear',
                   out_tangent='linear',
                   insert_blend=True
                   ):
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
        print("[Set Driven Key] :: {}: {} >> {}: {}".format(driver_str, driver_value, driven_str, driven_value))
    return True


def change_anim_nodes(node_object="", in_tangent='linear', out_tangent='linear'):
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


def get_anim_data(object_node=""):
    """
    get animation data from MFnAnimCurve nodes.
    :param object_node: <str> maya object node to check for keys from.
    :return: <dict> animCurve data. <bool> False for failure.
    """
    anim_nodes = object_utils.get_m_anim_from_sel(object_node=object_node)
    if not anim_nodes:
        return False

    anim_data = {}
    for a_name, a_node in anim_nodes.items():
        k_len = a_node.numKeys()

        if not k_len:
            continue

        anim_data[a_name] = {}
        anim_data[a_name]["num_keys"] = k_len
        anim_data[a_name]["anim_values"] = []

        # iterate through the key values
        for i in xrange(k_len):
            # cmds.keyframe('animCurveUL4', valueChange=1, q=1)
            # for whatever reason, this gives a more accurate time result than MTime.value()
            a_time = cmds.keyframe('animCurveUL4', floatChange=1, q=1)[i]
            m_time = a_node.time(i).value()
            a_val = a_node.value(i)

            i_x = om.MAngle()
            o_x = om.MAngle()
            i_y = __m_util.asDoublePtr()
            o_y = __m_util.asDoublePtr()
            a_node.getTangent(i, i_x, i_y, True)
            a_node.getTangent(i, o_x, o_y, False)
            i_y = __m_util.getDouble(i_y)
            o_y = __m_util.getDouble(o_y)
            anim_data[a_name]["anim_values"].append((a_time, a_val))

            if __verbosity__:
                print("time: {}".format(m_time))
                print("value: {}".format(a_val))
                print("tangent_ix: {}".format(i_x.asDegrees()))
                print("tangent_ox: {}".format(o_x.asDegrees()))
                print("InTangent: {}".format(i_y))
                print("OutTangent: {}".format(o_y))
    return anim_data


def __round(x):
    """
    rounds to the nearest 0.25
    :param x: <float> number.
    :return: <float> rounded number.
    """
    print(round(x*4)/4)


def set_anim_data(anim_data={}, rounded=False):
    """
    sets the existing animation data. This does not create new data.
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
        mfn_anim = oma.MFnAnimCurve(node_name)
        for i in xrange(num_keys):
            a_val, a_time = anim_data[i]
            if rounded:
                mfn_anim.setTime(i, __round(a_time))
            else:
                mfn_anim.setTime(i, a_time)
            mfn_anim.setValue(i, a_val)
    return True


def connections_gen(object_name="", direction='kDownstream', level='kPlugLevel', ftype=''):
    """
    get plug connections
    :param object_name: <str> object to check connections from.
    :param direction: <str> specify which direction to traverse.
    :param ftype: <str> specify which type to filter.
    :param level: <str> specify which level to traverse.
    """
    # define function variables
    node = object_utils.get_m_obj(object_name)
    direction = eval('om.MItDependencyGraph.{}'.format(direction))
    level = eval('om.MItDependencyGraph.{}'.format(level))
    if ftype:
        ftype = eval('om.MFn.{}'.format(ftype))

        # initiate the iterator object
        dag_iter = om.MItDependencyGraph(
            node,
            ftype,
            direction
        )
    else:
        # initiate the iterator object
        dag_iter = om.MItDependencyGraph(
            node,
            direction,
            level
        )
    dag_iter.reset()

    # iterate the dependency graph to find what we want.
    while not dag_iter.isDone():
        yield object_utils.Item(dag_iter.currentItem())
        dag_iter.next()


def get_anim_connections(object_name=""):
    """
    get plug connections
    :param object_name:
    :return: <dict> found animation connection plugs.
    """
    found_nodes = {}
    node = object_utils.get_m_obj(object_name)
    n_gen = connections_gen(node)

    for cur_node in n_gen:
        if cur_node.hasFn(om.MFn.kBlendWeighted):
            plugs = object_utils.get_plugs(cur_node, source=False)

            if "targets" not in found_nodes:
                found_nodes["targets"] = []

            u_conversion_nodes = filter(lambda x: x.startswith('unitConversion'), plugs)

            # get plug nodes
            n_plugs = set(plugs) - set(u_conversion_nodes)
            found_nodes["targets"].extend(n_plugs)

        # find what the curve nodes are attached to.
        if cur_node.hasFn(om.MFn.kAnimCurve):
            if "source" not in found_nodes:
                found_nodes["source"] = []
            plugs = object_utils.get_plugs(cur_node, source=True)
            for p_node in plugs:
                if p_node not in found_nodes["source"]:
                    found_nodes["source"].append(p_node)

            # collect anim nodes.
            if "animNodes" not in found_nodes:
                found_nodes["animNodes"] = {}
            anim_fn = oma.MFnAnimCurve(cur_node)
            if anim_fn.numKeys():
                anim_node = om.MFnDependencyNode(cur_node).name()
                found_nodes["animNodes"].update(get_animation_data_from_node(anim_node))
    return found_nodes


def get_animation_data_from_node(object_node=""):
    """
    get the animation data from the node specified.
    :param object_node: <str> the object to check the data from.
    :return: <dict> key data.
    """
    if not object_node:
        return False

    o_anim = None
    if isinstance(object_node, (str, unicode)):
        m_object = object_utils.get_m_obj(object_node)
        o_anim = oma.MFnAnimCurve(m_object)

    if isinstance(object_node, oma.MFnAnimCurve):
        o_anim = object_node
        object_node = object_node.name()

    # get connections
    source_attr = object_utils.get_plugs(object_node, source=True)
    destination_attr = object_utils.get_plugs(object_node, source=False, ignore_unit_nodes=True)

    if destination_attr:
        if destination_attr[0].startswith('blendWeighted'):
            node_gen = connections_gen(destination_attr[0], ftype='kUnitConversion')
            for g_node in node_gen:
                destination_attr = g_node.destination_plugs()

    # get the time from the keys supplied
    number_of_keys = o_anim.numKeys()
    anim_data = {}
    if number_of_keys > 1:
        anim_data[object_node] = {'data': {},
                                  'tangents': {},
                                  'sourceAttr': source_attr,
                                  'targetAttr': destination_attr
                                  }
        for i_key in xrange(number_of_keys):
            # this is a lie
            # i_x = _float_ptr.get_float_ptr()
            # i_y = _float_ptr.get_float_ptr()
            #
            # o_x = _float_ptr.get_float_ptr()
            # o_y = _float_ptr.get_float_ptr()
            #
            # o_anim.getTangent(i_key, i_x, i_y, True)
            # o_anim.getTangent(i_key, o_x, o_y, True)
            # this is a lie
            # v_float = o_anim.value(i_key)

            # this will get me the values that I want.
            # anim_data[object_node]['tangents'][i_key] = (ScriptUtil(i_x).asFloat(), ScriptUtil(i_y).asFloat(),
            #                                              ScriptUtil(o_x).asFloat(), ScriptUtil(o_y).asFloat())
            # anim_data[object_node]['tangents'][i_key] = (ScriptUtil(o_x).asFloat(), ScriptUtil(o_y).asFloat())

            # get the information the standard way
            v_float = cmds.keyframe(object_node, q=1, vc=1)[i_key]
            o_x = cmds.getAttr('{}.keyTanOutX[{}]'.format(object_node, i_key))
            o_y = cmds.getAttr('{}.keyTanOutY[{}]'.format(object_node, i_key))
            i_x = cmds.getAttr('{}.keyTanInX[{}]'.format(object_node, i_key))
            i_y = cmds.getAttr('{}.keyTanInY[{}]'.format(object_node, i_key))

            # save the information
            anim_data[object_node]['tangents'][i_key] = {'out': (o_x, o_y),
                                                         'in': (i_x, i_y)}
            anim_data[object_node]['data'][i_key] = v_float
    return anim_data
