"""
Warning: The mirror functionnality of OMTK is in alpha stage. Use it at your own risk!
Usage example:
# Step 1: Add attributes
for obj in pymel.selected():
    add_mirror_attr(obj)
# Step 2: Manually configure attributes
# Step 3: Mirror
mirror_objs(pymel.selected())
"""

import pymel.core as pymel
from maya import cmds
from maya import OpenMaya

class Axis:
    """
    Fake enum as class with constant variable to represent the axis value that could change
    """
    x = 'X'
    y = 'Y'
    z = 'Z'

def list_from_MMatrix(m):
    return [
        m(0, 0),
        m(0, 1),
        m(0, 2),
        m(0, 3),
        m(1, 0),
        m(1, 1),
        m(1, 2),
        m(1, 3),
        m(2, 0),
        m(2, 1),
        m(2, 2),
        m(2, 3),
        m(3, 0),
        m(3, 1),
        m(3, 2),
        m(3, 3)
    ]

def mirror_matrix_axis(m, axis):
    m_flip = OpenMaya.MMatrix()
    if axis == Axis.x:
        OpenMaya.MScriptUtil.createMatrixFromList([-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], m_flip)
    elif axis == Axis.y:
        OpenMaya.MScriptUtil.createMatrixFromList([1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], m_flip)
    elif axis == Axis.z:
        OpenMaya.MScriptUtil.createMatrixFromList([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1], m_flip)
    else:
        raise Exception("Unsupported axis. Got {0}".format(axis))
    m = m * m_flip
    return m

def flip_matrix_axis_pos(m, axis):
    data = list_from_MMatrix(m)
    if axis == Axis.x:
        data[12] *= -1.0
    elif axis == Axis.y:
        data[13] *= -1.0
    elif axis == Axis.z:
        data[14] *= -1.0
    else:
        raise Exception("Unsupported axis. Got {0}".format(axis))
    OpenMaya.MScriptUtil.createMatrixFromList(data, m)
    return m

def flip_matrix_axis_rot(m, axis):
    """
    Utility function to mirror the x, y or z axis of an provided matrix.
    :param m: The pymel.datatypes.Matrix to flip.
    :param axis: The axis to flip.
    :return: The resulting pymel.datatypes.Matrix.
    """
    data = list_from_MMatrix(m)

    if axis == Axis.x:
        data[0] *= -1.0
        data[1] *= -1.0
        data[2] *= -1.0
    elif axis == Axis.y:
        data[4] *= -1.0
        data[5] *= -1.0
        data[6] *= -1.0
    elif axis == Axis.z:
        data[8] *= -1.0
        data[9] *= -1.0
        data[10] *= -1.0
    else:
        raise Exception("Unsupported axis. Got {0}".format(axis))
    OpenMaya.MScriptUtil.createMatrixFromList(data, m)
    return m

def get_name_friend(obj_src_name, separator='_'):
    tokens_side_l = ['l', 'L', 'lf', 'LF', 'left', 'Left']
    tokens_side_r = ['r', 'R', 'rt', 'RT', 'right', 'Right']
    # Resolve obj_dst_name
    tokens_src = obj_src_name.split(separator)
    tokens_dst = []
    for i, token in enumerate(tokens_src):
        for token_side_l, token_side_r in zip(tokens_side_l, tokens_side_r):
            if token == token_side_l:
                token = token_side_r
            elif token == token_side_r:
                token = token_side_l
        tokens_dst.append(token)
    obj_dst_name = separator.join(tokens_dst)
    return obj_dst_name

def get_ctrl_friend(obj_src):
    obj_src_name = obj_src.name()
    obj_dst_name = get_name_friend(obj_src_name)

    if obj_dst_name is None:
        print("Can't find ctrl friend of {0}".format(obj_src_name))
        return None

    if not cmds.objExists(obj_dst_name):
        print ("Can't find ctrl named {0}".format(obj_dst_name))
        return None
    return pymel.PyNode(obj_dst_name)


def mirror_matrix(m,
                  mirror_x=False, mirror_y=False, mirror_z=False,
                  flip_pos_x=False, flip_pos_y=False, flip_pos_z=False,
                  flip_rot_x=False, flip_rot_y=False, flip_rot_z=False,
                  parent_ref=None):
    """
    Mirror a pose using the local matrix and a flip vector.
    Note that you can store the flip vector in the BaseCtrl instance of each ctrls.
    """
    # Mirror axis if necessary
    # Note that in 99.9% of case we only want to mirror one axis.
    if (mirror_x or mirror_y or mirror_z) and not (flip_rot_x or flip_rot_y or flip_rot_z):
        raise Exception(
            "When mirroring, please at least flip one axis, otherwise you might end of with a right handed matrix!")
    if mirror_x:
        m = mirror_matrix_axis(m, Axis.x)
    if mirror_y:
        m = mirror_matrix_axis(m, Axis.y)
    if mirror_z:
        m = mirror_matrix_axis(m, Axis.z)

    # Flip rotation axises if necessary
    if flip_rot_x:
        flip_matrix_axis_rot(m, Axis.x)
    if flip_rot_y:
        flip_matrix_axis_rot(m, Axis.y)
    if flip_rot_z:
        flip_matrix_axis_rot(m, Axis.z)

    # Flip position if necessary
    if flip_pos_x:
        m = flip_matrix_axis_pos(m, Axis.x)
    if flip_pos_y:
        m = flip_matrix_axis_pos(m, Axis.y)
    if flip_pos_z:
        m = flip_matrix_axis_pos(m, Axis.z)
    return m

def get_obj_mirror_def(obj):
    try:
        return(
            obj.attr('mirror_x').get(),
            obj.attr('mirror_y').get(),
            obj.attr('mirror_z').get(),
            obj.attr('mirror_flip_pos_x').get(),
            obj.attr('mirror_flip_pos_y').get(),
            obj.attr('mirror_flip_pos_z').get(),
            obj.attr('mirror_flip_rot_x').get(),
            obj.attr('mirror_flip_rot_y').get(),
            obj.attr('mirror_flip_rot_z').get()
        )
    except Exception as e:
        print("Error getting mirror attributes on {0}: {1}".format(obj, str(e)))

def add_mirror_attr(obj):
    def handle_attr(obj, attr_name):
        if not obj.hasAttr(attr_name):
            pymel.addAttr(obj, longName=attr_name, at='bool')
    attr_names = (
        'mirror_x',
        'mirror_y',
        'mirror_z',
        'mirror_flip_pos_x',
        'mirror_flip_pos_y',
        'mirror_flip_pos_z',
        'mirror_flip_rot_x',
        'mirror_flip_rot_y',
        'mirror_flip_rot_z',
    )
    for attr_name in attr_names:
        handle_attr(obj, attr_name)

def mirror_objs(objs):
    # Only work on transforms
    objs = filter(
        lambda obj: isinstance(obj, pymel.nodetypes.Transform) and not isinstance(obj, pymel.nodetypes.Constraint),
        objs)

    # Resolve desired poses without affecting anything
    tms_by_objs = {}
    for obj_dst in objs:
        # Resolve source object
        obj_src = get_ctrl_friend(obj_dst)
        if obj_src is None:
            obj_src = obj_dst

        # Resolve mirror definition
        # If we didn't find any friend, we'll use a default mirror definition.
        data = get_obj_mirror_def(obj_dst)
        if data is None:
            continue

        m = obj_dst.__apimfn__().transformation().asMatrix()
        m = mirror_matrix(m, *data)

        tms_by_objs[obj_src] = OpenMaya.MTransformationMatrix(m)

    # Apply desired poses
    cmds.undoInfo(openChunk=True)
    for mfn_transform_src in tms_by_objs.keys():
        tm = tms_by_objs[mfn_transform_src]
        # HACK: Use cmds so undoes are working
        # mfn_transform_src.set(tm)
        cmds.xform(mfn_transform_src.__melobject__(), matrix=list_from_MMatrix(tm.asMatrix()))
    cmds.undoInfo(closeChunk=True)
# __________________________________________________________________________________________________________
# xform_mirror.py