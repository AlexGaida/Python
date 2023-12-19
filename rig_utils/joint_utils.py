"""
joint_utils.py manipulating and retrieving information from joints.
"""
# import standard modules

# import maya modules
from maya import cmds, OpenMaya

# import local modules
from maya_utils import name_utils
from maya_utils import node_utils
from maya_utils import object_utils
from maya_utils import transform_utils
from maya_utils import curve_utils

# define local variables
BND_JNT_SUFFIX = name_utils.get_classification_name('bound_joint')
JNT_SUFFIX = name_utils.get_classification_name('joint')


def reload_selection(func):
    """
    a decorator that deselects and then selects again after the function is complete.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        objects = cmds.ls(sl=1)
        cmds.select(d=1)
        func(*args, **kwargs)
        cmds.select(objects)
    return wrapper


def joint_name(name="", idx=-1):
    """
    concatenate the strings to form a joint name.
    :param name: <str> the base name string to use.
    :param idx: <int> the number to concatenate into.
    :return: <str> the joint name.
    """
    if not name.endswith(JNT_SUFFIX):
        return '{}_{}'.format(name, JNT_SUFFIX)
    elif name and idx != -1:
        return '{}_{}_{}'.format(name, idx, JNT_SUFFIX)
    else:
        return name


def get_joints_from_selection():
    """
    the joints from current selection.
    :return: <tuple> array of joints from selection.
    """
    return tuple(cmds.ls(sl=1, type='joint'))


def get_joints():
    """
    get all joints in the scene.
    :return: <tuple> array of joints.
    """
    return tuple(cmds.ls(type='joint'))


def get_bnd_joints():
    """
    return only bound joints.
    :return: <tuple> filtered array of joints.
    """
    return filter(lambda x: x.endswith(BND_JNT_SUFFIX), get_joints())


def mirror_joints(joints=(), axis='YZ', behaviour=False, search_replace=('l_', 'r_')):
    """
    mirrors an array of joints
    :param joints: <list>, <tuple> array of joints.
    :param axis: <str> mirrors by this axis.
    :param behaviour: <bool> mirrors behaviour.
    :param search_replace: <tuple> (0,) find this string and replace it (1,)
    :return: <tuple> array of mirrored joints.
    """
    if not joints:
        joints = get_joints_from_selection()
    # get only the joint objects in our selection
    jnt_array = filter(object_utils.is_joint, joints)
    mirror_array = ()
    for jnt in jnt_array:
        if axis == 'XY':
            mirror_array += tuple(cmds.mirrorJoint(
                jnt, mirrorXY=True, mirrorBehavior=behaviour, searchReplace=search_replace))
        if axis == 'YZ':
            mirror_array += tuple(cmds.mirrorJoint(
                jnt, mirrorYZ=True, mirrorBehavior=behaviour, searchReplace=search_replace))
        if axis == 'XZ':
            mirror_array += tuple(cmds.mirrorJoint(
                jnt, mirrorXZ=True, mirrorBehavior=behaviour, searchReplace=search_replace))
    return mirror_array


def set_joint_labels():
    """
    names the bind joints through the labels for skinCluster weights.
    :return: <bool> True for success.
    """
    for j_name in get_bnd_joints():
        cmds.setAttr(j_name + ".type", 18)
        if j_name.startswith('l_'):
            side = 'l'
            cmds.setAttr(j_name+".side", 1)
        if j_name.startswith('c_'):
            side = 'c'
            cmds.setAttr(j_name + ".side", 0)
        if j_name.startswith('r_'):
            side = 'r'
            cmds.setAttr(j_name + ".side", 2)
        if side:
            cmds.setAttr(j_name+'.otherType', j_name.replace(side, ''), type='string')
    return True


@reload_selection
def create_joint_at_transform(transform_name="", name=""):
    """
    creates joints at the same position as the transform object.
    :param transform_name: <str> the transform name to get values from.
    :param name: <str> the name to use when creating joints.
    :return: <str> joint name.
    """
    if not name:
        jnt_name = joint_name(transform_name)
    else:
        jnt_name = name
    tfm = transform_utils.Transform(transform_name)
    cmds.joint(name=jnt_name)
    cmds.xform(jnt_name, m=tfm.world_matrix(), ws=True)
    return jnt_name


def create_joint_at_transforms(transform_objects=(), name=""):
    """
    creates joint at transforms.
    :return:
    """
    joints = ()
    for t_obj in transform_objects:
        joints += create_joint_at_transform(t_obj, name),
    return joints


@reload_selection
def create_joints(objects_array, name, bind_name=False):
    """
    create joints at transform objects.
    :param objects_array: <tuple> array of transform objects.
    :param name: <str> the name to use when creating the joints.
    :param bind_name: <bool> create bind joint name.
    :return: <tuple> array of joints.
    """
    names = name_utils.get_joint_name_array(name, length=len(objects_array), bind_name=bind_name)
    joints = ()
    for trfm_name, obj_name in zip(objects_array, names):
        joints += create_joint_at_transform(trfm_name, obj_name),
    return joints


def create_joints_at_positions(position_array, name, prefix_name="", guide_joint=False, bound_joint=False):
    """
    create joints at transform objects.
    :param position_array: <tuple> array of transform objects.
    :param name: <str> the name to use when creating the joints.
    :param prefix_name: <str> use this prefix name.
    :param guide_joint: <bool> create a joint using the guide joint suffix name.
    :param bound_joint: <bool> create a joint using the bound joint suffix name.
    :param bind_name: <bool> create bind joint name.
    :return: <tuple> array of joints.
    """
    joint_names = create_joint(name=name, num_joints=len(position_array),
                               prefix_name=prefix_name,
                               guide_joint=guide_joint,
                               bound_joint=bound_joint,
                               as_strings=True)
    for jnt_name, position in zip(joint_names, position_array):
        cmds.xform(jnt_name, t=position, ws=1)
    return joint_names


def create_joint_at_position(position, name):
    """
    creates joint at position.
    :param position: <tuple> array of transform position.
    :param name: <str> joint name to use.
    :return: <str> joint name.
    """
    joint = cmds.joint(name=name)
    cmds.xform(joint, t=position, ws=1)
    return joint


def create_joints_at_selection(name):
    """
    creates the joints at selected transform objects.
    :param name: <str> the name to use when creating the joints.
    :return: <tuple> array of joints created.
    """
    objects = object_utils.get_selected_node(single=False)
    return create_joints(objects, name)


def create_bind_joints_at_selection(name):
    """
    creates the joints at selected transform objects.
    :param name: <str> the name to use when creating the joints.
    :return: <tuple> array of joints created.
    """
    objects = object_utils.get_selected_node(single=False)
    return create_joints(objects, name, bind=True)


def get_joint_hierarchy(base_joint_name=""):
    """
    get the joint hierarchy.
    :param base_joint_name:
    :return: <tuple> array of joint hierarchy.
    """
    return object_utils.get_children_names(base_joint_name, type_name='joint')


def get_joint_hierarchy_positions(base_joint_name=""):
    """
    get hierarchial positions array.
    :return: <tuple> positions array.
    """
    joint_hierarchy = get_joint_hierarchy(base_joint_name)
    positions_array = ()
    for jnt_name in joint_hierarchy:
        positions_array += transform_utils.Transform(jnt_name).get_world_translation_list(),
    return positions_array


@reload_selection
def create_dynamic_chain(base_joint_name="", name="", curve_degree=2):
    """
    creates a dynamic chain from the joint chain provided.
    :return: <str> curve_name
    """
    joint_hierarchy = get_joint_hierarchy(base_joint_name)
    points_array = get_joint_hierarchy_positions(base_joint_name)
    print(points_array)
    curve_name = curve_utils.create_curve_from_points(points_array, degree=curve_degree, curve_name=name)
    # cmds.select(curve_name)
    # make the curve name dynamic
    # mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
    # now make the spline Ik Handle
    # return curve_name


def get_joint_name(prefix_name, name, i, suffix_name):
    """
    get the guide joint name.
    :param prefix_name: <str> prefix name.
    :param name: <str> actual name.
    :param i: <int> integer name
    :param suffix_name: <str> name after the name.
    :return: <str> guide joint name.
    """
    return '{prefix}{name}_{idx}{suffix}'.format(prefix=prefix_name, name=name, idx=i, suffix=suffix_name)


def get_joint_names(name,
                    prefix_name="",
                    num_joints=1,
                    use_name=False,
                    guide_joint=False,
                    bound_joint=False,
                    suffix_name=""):
    """
    returns an array of joint names.
    :param name: <str> (mandatory) base name of the joint to use at creation.
    :param num_joints: the number of joints created.
    :param prefix_name: <str> the prefix name to use.
    :param guide_joint: <str> create joint with '_bnd_jnt' name.
    :param use_name: <str> use the name that is coming in as-is.
    :param guide_joint: <bool> returns guide joint names.
    :param bound_joint: <bool> returns bound joint names.
    :param suffix_name: <str> custom suffix joint name.
    :return:
    """
    if use_name:
        joint_names = [name]

    else:
        if suffix_name:
            joint_names = name_utils.get_suffix_name_array(prefix_name=prefix_name,
                                                           name=name,
                                                           length=num_joints,
                                                           suffix_name=suffix_name)
        elif guide_joint:
            joint_names = name_utils.get_guide_name_array(prefix_name=prefix_name,
                                                          name=name,
                                                          length=num_joints)
        elif bound_joint:
            joint_names = name_utils.get_bound_name_array(prefix_name=prefix_name,
                                                          name=name,
                                                          length=num_joints)
        else:
            joint_names = name_utils.get_name_array(prefix_name=prefix_name,
                                                    name=name,
                                                    length=num_joints)
    return joint_names


def get_joint_positions(num=3, y=0.0, x=0.0, z=0.0, direction='z'):
    """
    returns the joint positions by the number of joints required to build.
    :param num: <int> creates this number of joints in the scene.
    :param y: <float> sets the initial y value.
    :param x: <float> sets the initial x value.
    :param z: <float> sets the initial z value.
    :param direction: <str> the direction of the axis to create joint towards.
    :return: <tuple> positions
    """
    positions = ()
    for i in range(num):
        if direction == 'z':
            positions += [x, y, z + float(i)],
        if direction == 'x':
            positions += [x + float(i), y, z],
        if direction == 'y':
            positions += [x, y + float(i), z],
    return positions


def create_joint(name, prefix_name="",
                 num_joints=1,
                 as_strings=False,
                 guide_joint=False,
                 bound_joint=False,
                 suffix_name="",
                 use_name=False,
                 use_transform="",
                 use_position=()):
    """
    creates a joint and names it using OpenMaya.
    :param name: <str> the name of the joint to create !important.
    :param num_joints: the number of joints created.
    :param prefix_name: <str> the prefix name to use.
    :param guide_joint: <str> create joint with '_bnd_jnt' name.
    :param bound_joint: <str> create joint with '__guide_jnt' name.
    :param as_strings: <bool> returns <str> objects instead of <OpenMaya.MObject> objects.
    :param use_name: <str> use the name that is coming in.
    :param use_transform: <str> use this object's transform co-ordinates.
    :param use_position: <tuple, list> array of floats to use as transform or matrix.
    :param suffix_name: <str> uses a custom suffix name string.
    :return: <tuple> array of created joint objects.
    """
    if not name:
        name = 'joint'
    dag_mod = OpenMaya.MDagModifier()
    # create the joint MObjects we will be manipulating.
    jnt_objects = ()
    jnt_names = ()
    # grabs the joint names
    joint_names = get_joint_names(prefix_name=prefix_name,
                                  name=name,
                                  num_joints=num_joints,
                                  use_name=use_name,
                                  guide_joint=guide_joint,
                                  bound_joint=bound_joint,
                                  suffix_name=suffix_name)
    for i in range(0, num_joints):
        # only create new if the objects's names do not exist
        new_name = joint_names[i]
        # create only when the name does not exist
        if name and not object_utils.is_exists(new_name):
            jnt_names += new_name,
            if i == 0:
                # The first joint has no parent.
                jnt_obj = dag_mod.createNode('joint')
            else:
                # Assign the new joint as a child to the previous joint.
                jnt_obj = dag_mod.createNode('joint', jnt_objects[i - 1])
            # rename the joint using OpenMaya
            dag_mod.renameNode(jnt_obj, new_name)
            dag_mod.doIt()
            # keep track of all the joints created.
            jnt_objects += jnt_obj,
        elif name and object_utils.is_exists(new_name):
            jnt_names += new_name,
            jnt_objects += object_utils.get_m_obj(new_name),
        # snap the joint to the transform
        if use_transform and object_utils.is_exists(new_name):
            object_utils.snap_to_transform(new_name, use_transform, matrix=True)
        # set the position of the newly created joint
        if use_position:
            if isinstance(use_position[0], (int, float)):
                set_position(new_name, use_position)
            else:
                set_position(new_name, use_position[i])
    if not as_strings:
        return jnt_objects
    elif as_strings:
        return jnt_names


def set_position(obj, positional_array):
    """
    sets position of the joint
    :param obj:
    :param positional_array:
    :return:
    """
    if positional_array and len(positional_array) == 3:
        object_utils.set_object_transform(obj, t=positional_array)
    elif positional_array and len(positional_array) > 3:
        object_utils.set_object_transform(obj, m=positional_array)


def get_joint_orientation(joint_name):
    """
    joint orientation
    :param joint_name: <str> joint name to get orientation from.
    :return: <OpenMaya.MMatrix> orientation matrix.
    """
    # Factor in Joint Orientation
    j_obj = object_utils.get_m_obj(joint_name)
    j_fn = object_utils.get_fn(j_obj)
    j_quat = OpenMaya.MQuaternion()
    j_fn.getOrientation(j_quat)
    return j_quat.asMatrix()


def create_joints_from_arrays(positions, names, parented=False):
    """
    creates the joints from array of names and joints given.
    :return:
    """
    idx = 0
    joints = ()
    for position, name in zip(positions, names):
        joints += create_joint(name, use_position=position, use_name=True, as_strings=True)[0],
        if parented and idx > 0:
            # parent the last joint created to the newly created joint
            cmds.parent(joints[idx], joints[idx - 1])
        idx += 1
    return joints


def create_ik_handle(joint_array, name='', sticky="off", solver="ikRPsolver", priority=2):
    """
    creates the ik handle from the joints array provided.
    :param joint_array: <tuple>, <list> the joint array to use.
    :param name: <str> create an IkHandle with this name.
    :param sticky: <str> 'on' or 'off' if we want sticky on the ik end points.
    :param priority: <int> the processing priority number for this ikHandle.
    :param solver: <str> ikRPsolver, ikSCsolver and ikSplineSolver.
    :return: <tuple> ikHandle, ikEffector created.
    """
    ik_name = name_utils.get_ik_handle_name(name)
    return tuple(cmds.ikHandle(startJoint=joint_array[0], endEffector=joint_array[-1],
                               name=ik_name, sticky=sticky, solver=solver, priority=priority))


def freeze_transformations(object_name, translate=True, rotate=True, scale=True):
    """
    freezes the transformations.
    :param object_name: <str> the object to freeze transforms to.
    :param translate: <bool> freeze the translations on this transform.
    :param rotate: <bool> freeze the rotations on this transform.
    :param scale: <bool> freeze the scale on this transform.
    :return: <bool> True for success.
    """
    cmds.makeIdentity(object_name, apply=1, t=translate, r=rotate, s=scale, n=0, pn=1)
    return True


def zero_joint_orient(object_name, x=True, y=True, z=True):
    """
    zeroes the joint orient attribute.
    :return: <bool>
    """
    if x:
        cmds.setAttr(object_name + '.jointOrientX', 0.0)
    if y:
        cmds.setAttr(object_name + '.jointOrientY', 0.0)
    if z:
        cmds.setAttr(object_name + '.jointOrientZ', 0.0)
    return True


def orient_joints(joint_array, primary_axis='x'):
    """
    orients the joints.
    :param joint_array: <tuple> array of joints.
    :param primary_axis: <str> the axis to orient joints towards.
    :return:
    """
    for jnt_name in joint_array:
        # freezes all transform values on this joint
        freeze_transformations(jnt_name)
        # reorient joint
        if primary_axis == 'x':
            return cmds.joint(jnt_name, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        if primary_axis == 'y':
            return cmds.joint(jnt_name, e=True, oj='yzx', secondaryAxisOrient='yup', ch=True, zso=True)
        if primary_axis == 'z':
            return cmds.joint(jnt_name, e=True, oj='zxy', secondaryAxisOrient='yup', ch=True, zso=True)
    raise ValueError("[OrientJoints] :: You must specify the axis of orientation: x, y or z.")


def unlock_joints(jnt_suffix=''):
    """
    unlocks the joints bound to the skin clusters in scene.
    :return: <bool> True for success.
    """
    if jnt_suffix:
        joints = cmds.ls('*_{}'.format(jnt_suffix))
    if not jnt_suffix:
        joints = get_bnd_joints()
    for jnt in joints:
        cmds.setAttr('%s.liw' % jnt, 0)
    return True


class Joint(node_utils.Node):
    def __init__(self, **kwargs):
        super(Joint, self).__init__(**kwargs)
        self.dag_mod = OpenMaya.MDagModifier()
        if not self.suffix_name:
            self.suffix_name = self.naming_convention['joint']
        # get the name with the updated suffix name parameter
        self.name = self.get_name(suffix_name=self.suffix_name)
        if not self.exists:
            self.node = self.name
            self.create()

    def create(self, mfn_dag=False):
        if not self.exists:
            if mfn_dag:
                # The first joint has no parent.
                jnt_obj = self.dag_mod.createNode('joint')
                # rename the joint using OpenMaya
                self.dag_mod.renameNode(jnt_obj, self.name)
                self.dag_mod.doIt()
            else:
                cmds.select(d=True)  # deselect first before creating any joints
                cmds.joint(name=self.name)

    def unlock(self):
        """
        lock the joint from weight paint
        """
        self.setAttr(self.node + '.liw', 0)

    def lock(self):
        """
        un-lock the joint from weight paint
        """
        self.setAttr(self.node + '.liw', 1)

    def orient_axis(self, axis='x'):
        """
        :param axis: <str> joint orient axis
        """
        if axis == 'x':
            cmds.joint(self.node, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        if axis == 'y':
            cmds.joint(self.node, e=True, oj='yzx', secondaryAxisOrient='yup', ch=True, zso=True)
        if axis == 'z':
            cmds.joint(self.node, e=True, oj='zxy', secondaryAxisOrient='yup', ch=True, zso=True)

    def zero_joint_orients(self):
        """
        zeroes joint orientations
        """
        cmds.setAttr(self.node + ".jointOrientX", 0)
        cmds.setAttr(self.node + ".jointOrientY", 0)
        cmds.setAttr(self.node + ".jointOrientZ", 0)

# ______________________________________________________________________________________________________________________
# joint_utils.py
