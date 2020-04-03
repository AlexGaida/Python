"""
Animation data tools, manipulating animation settings.
"""
# import standard modules
from math import acos

# import maya modules
from maya import cmds
from maya import mel
from maya import OpenMaya as OpenMaya
from maya import OpenMayaAnim as OpenMayaAnim

# import custom modules
import object_utils
from maya_utils import math_utils


# define private variables
__version__ = '1.0.0'
__verbosity__ = 0
__m_util = OpenMaya.MScriptUtil()


def connect_anim(source_object_name, source_attribute_name, dest_object_name, dest_attribute_name):
    """
    connects an attribute using set driven keys.
    benefit: set driven keyframes can be blended into a single driven attribute.
        driver_node='',
        driver_attr='',
        driven_node='',
        driven_attr='',
        driven_value=None,
        driver_value=None,
    """
    set_driven_key(source_object_name, source_attribute_name,
                                   dest_object_name, dest_attribute_name,
                                   driven_value=0.0,
                                   driver_value=0.0)
    set_driven_key(source_object_name, source_attribute_name,
                                   dest_object_name, dest_attribute_name,
                                   driven_value=1.0,
                                   driver_value=1.0)
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
    # print('cmds.setDrivenKeyframe("{}", cd="{}", driverValue={}, '
    #       'value={}, inTangentType="{}", outTangentType="{}", insertBlend={})'.format(
    #     driven_str, driver_str, driver_value, driven_value, in_tangent, out_tangent, insert_blend))
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


def get_value_from_time(a_node="", idx=0):
    """
    gets the value from the time supplied.
    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    :return: <tuple> data.
    """
    return OpenMaya.MTime(a_node.time(idx).value(), OpenMaya.MTime.kSeconds).value(), a_node.value(idx),


def get_tangents_from_time(a_node="", idx=0):
    """
    gets the value from the time supplied.
    :param a_node: MFn.kAnimCurve node.
    :param idx: <int> the time index.
    :return: <tuple> data.
    """
    i_x = __m_util.asDoublePtr()
    o_x = __m_util.asDoublePtr()
    i_y = __m_util.asDoublePtr()
    o_y = __m_util.asDoublePtr()
    a_node.getTangent(idx, i_x, i_y, True)
    a_node.getTangent(idx, o_x, o_y, False)
    return __m_util.getFloat(i_x), __m_util.getFloat(i_y), __m_util.getFloat(o_x), __m_util.getFloat(o_y),


def get_anim_fn_data(a_node=""):
    """
    get animation data from MFnAnimCurve nodes.
    :return: <dict> animCurve data. <bool> False for failure.
    """
    k_len = a_node.numKeys()
    collection = []
    for i in xrange(k_len):
        collection.append(get_value_from_time(a_node, i))
    return collection


def get_anim_curve_data(object_name=""):
    return get_anim_fn_data(get_mfn_anim_node(object_name))


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
        mfn_anim = OpenMayaAnim.MFnAnimCurve(node_name)
        for i in xrange(num_keys):
            a_val, a_time = anim_data[i]
            if rounded:
                mfn_anim.setTime(i, __round(a_time))
            else:
                mfn_anim.setTime(i, a_time)
            mfn_anim.setValue(i, a_val)
    return True


def connections_gen(object_name="", attribute="", direction='kDownstream', level='kPlugLevel', ftype=''):
    """
    get plug connections
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
    """
    get plug connections
    :param object_name:
    :return: <dict> found animation connection plugs.
    """
    found_nodes = {}

    for cur_node in connections_gen(object_utils.get_m_obj(object_name)):
        if cur_node.hasFn(OpenMaya.MFn.kBlendWeighted):
            plugs = object_utils.get_plugs(
                cur_node, source=False, ignore_nodes=['kBlendWeighted', 'kUnitConversion', 'kNodeGraphEditorInfo'])

            if "targets" not in found_nodes:
                found_nodes["targets"] = []

            # get plug nodes
            found_nodes["targets"].extend(plugs)

        # find what the curve nodes are attached to.
        if cur_node.hasFn(OpenMaya.MFn.kAnimCurve):
            if "source" not in found_nodes:
                found_nodes["source"] = []
            plugs = object_utils.get_plugs(cur_node, source=True)
            for p_node in plugs:
                if p_node not in found_nodes["source"]:
                    found_nodes["source"].append(p_node)

            # collect anim nodes.
            if "animNodes" not in found_nodes:
                found_nodes["animNodes"] = {}
            anim_fn = OpenMayaAnim.MFnAnimCurve(cur_node)
            if anim_fn.numKeys():
                anim_node = OpenMaya.MFnDependencyNode(cur_node).name()
                found_nodes["animNodes"].update(get_animation_data_from_node(anim_node))
    # change the lists into tuples
    if "source" in found_nodes:
        if found_nodes["source"]:
            found_nodes["source"] = tuple(found_nodes["source"])
    if "targets" in found_nodes:
        if found_nodes["targets"]:
            found_nodes["targets"] = tuple(found_nodes["targets"])
    return found_nodes


def get_animation_data_from_node(object_node=""):
    """
    get the animation data from the node specified.
    :param object_node: <str> the object to check the data frOpenMaya.
    :return: <dict> key data.
    """
    if not object_node:
        return False

    o_anim = None
    if isinstance(object_node, (str, unicode)):
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
            v_float = cmds.keyframe(object_node, q=1, valueChange=1)[i_key]
            try:
                t_float = cmds.keyframe(object_node, floatChange=1, q=1)[i_key]
            except TypeError:
                t_float = i_key
            o_x = cmds.getAttr('{}.keyTanOutX[{}]'.format(object_node, i_key))
            o_y = cmds.getAttr('{}.keyTanOutY[{}]'.format(object_node, i_key))
            i_x = cmds.getAttr('{}.keyTanInX[{}]'.format(object_node, i_key))
            i_y = cmds.getAttr('{}.keyTanInY[{}]'.format(object_node, i_key))

            # save the information
            anim_data[object_node]['tangents'][t_float] = {'out': (o_x, o_y),
                                                           'in': (i_x, i_y),
                                                           'keyNum': i_key}
            anim_data[object_node]['data'][t_float] = v_float
    return anim_data


def attribute_name(node_name, target_attr):
    return node_name + '.' + target_attr


def get_connected_blend_weighted_node(node_name="", target_attr=""):
    """
    get connected blend weighted node from the node name and the attribute provided.
    :param node_name: <str> the node name to check.
    :param target_attr: <str> the connected target attribute to get the blendWeighted node from.
    :return: <>
    """
    node_attr = attribute_name(node_name, target_attr)
    return object_utils.get_plugs(node_name, attr_name=node_attr, ignore_nodes=['kUnitConversion'])


def get_blend_weighted_values(node_name="", target_attr=""):
    """
    get the values of the blendWeighted node and calculate the new difference value.
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
    """
    gets the difference in values.
    :param value_data: <list> the values to get the
    :return: <float> sum of numbers.
    """
    return math_utils.get_sum(value_data)


def get_blend_weighted_sum(node_name="", target_attr=""):
    """
    get the sum of all values given by the blend weighted node found from the parameters given.
    :param node_name: <str> the node name to get the blend weighted node frOpenMaya.
    :param target_attr: <str> the attribute to get blendWeighted values frOpenMaya.
    :return: <float> the sum of all values.
    """
    return get_sum(get_blend_weighted_values(node_name, target_attr))
