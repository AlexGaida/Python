from maya import cmds


# local variables
_suffix_name = "_rbf"
_left_name = "_lf_"
_right_name = "_rt_"


# load the necessary plugins
def load_plugins():
    cmds.loadPlugin("weightDriver", qt=1)
    if not cmds.pluginInfo('weightDriver', query=True, loaded=True):
        raise ValueError('[weightDriver] :: Plugin is not loaded.')


def get_weight_drivers():
    return cmds.ls(type='weightDriver')


def get_weight_driver_data():
    driver_data = {}
    drivers = get_weight_drivers()
    for driver in drivers:
        num_poses = cmds.getAttr(driver + '.poses', mi=1)
        if not len(num_poses) > 1:
            continue

        num_inputs = cmds.getAttr(driver + '.input', mi=1)
        num_outputs = cmds.getAttr(driver + '.output', mi=1)
        driver_data[driver] = {}
        # 0 = vectorAngle; 1 = RBF;
        driver_data[driver]["type"] = cmds.getAttr(driver + '.type')
        driver_data[driver]["num_poses"] = num_poses
        driver_data[driver]["num_inputs"] = num_inputs
        driver_data[driver]["pose_inputs"] = {}
        driver_data[driver]["pose_values"] = {}
        driver_data[driver]["driver_node"] = cmds.listConnections(driver + '.input[0]', s=1, d=0,
                                                                  skipConversionNodes=True)[0]
        driver_data[driver]["driven_node"] = cmds.listConnections(driver + '.output[0]', s=0, d=1)[0]
        driver_data[driver]["driver_attrs"] = ()
        driver_data[driver]["driven_attrs"] = ()

        # get drivers
        for input_idx in num_inputs:
            driver_data[driver]["driver_attrs"] += cmds.listConnections(driver + '.input[{}]'.format(input_idx),
                                                                        s=1, d=0, skipConversionNodes=True, plugs=True)[0],

        # get drivens
        for output_idx in num_outputs:
            driver_data[driver]["driven_attrs"] += cmds.listConnections(driver + '.output[{}]'.format(output_idx),
                                                                        s=0, d=1, plugs=True)[0],

        # get poses data
        for num_pose in num_poses:
            pose_inputs = cmds.getAttr(driver + '.poses[{}].poseInput'.format(num_pose), mi=1)
            pose_values = cmds.getAttr(driver + '.poses[{}].poseValue'.format(num_pose), mi=1)

            if not pose_inputs or not pose_values:
                continue

            driver_data[driver]["pose_inputs"][num_pose] = ()
            driver_data[driver]["pose_values"][num_pose] = ()

            pose_input_attr = driver + '.poses[{}].poseInput'.format(num_pose)
            pose_value_attr = driver + '.poses[{}].poseValue'.format(num_pose)
            for input_idx in pose_inputs:
                input_idx = int(input_idx)
                driver_data[driver]["pose_inputs"][num_pose] += cmds.getAttr(pose_input_attr + '[{}]'.format(
                    int(input_idx))),

            for input_idx in pose_values:
                input_idx = int(input_idx)
                driver_data[driver]["pose_values"][num_pose] += cmds.getAttr(pose_value_attr + '[{}]'.format(
                    int(input_idx))),
    return driver_data


def mirror_data(driver_data={}, mirror_rotations=True):
    """
    Adds additional data for mirroring the information.
    :param driver_data: <dict> driver data from the left side.
    :param mirror_rotations: <bool> adds mirroring information.
    :return: <dict> driver data with right side information.
    :note:
        Currently supports mirroring the rotational data from left to right.
    """
    if mirror_rotations:
        mirror_axes = -1.0, -1.0, 1.0,
    right_driver_data = {}
    for driver in driver_data:
        driven_name = driver_data[driver]["driver_attrs"][0].split('.')[0]
        if _suffix_name not in driven_name:
            rbf_node_name = driven_name + _suffix_name
        else:
            rbf_node_name = driven_name
        if _left_name in driver:
            rbf_node_name = rbf_node_name.replace(_left_name, _right_name)
        if cmds.ls(rbf_node_name):
            continue

        right_driver_data[rbf_node_name] = {}
        right_driver_data[rbf_node_name]["type"] = driver_data[driver]["type"]
        driver_attrs = driver_data[driver]["driver_attrs"]
        right_driver_data[rbf_node_name]["driver_attrs"] = map(lambda x: x.replace(
            _left_name, _right_name), driver_attrs)

        driven_attrs = driver_data[driver]["driven_attrs"]
        right_driver_data[rbf_node_name]["driven_attrs"] = map(lambda x: x.replace(
            _left_name, _right_name), driven_attrs)

        right_driver_data[rbf_node_name]["num_poses"] = driver_data[driver]["num_poses"]
        right_driver_data[rbf_node_name]["pose_inputs"] = {}
        for idx in driver_data[driver]["num_poses"]:
            # mirror the pose inputs
            inputs = driver_data[driver]["pose_inputs"][idx]
            right_driver_data[rbf_node_name]["pose_inputs"][idx] = map(lambda x, a: x*a, inputs, mirror_axes)

        # edit the pose values
        right_driver_data[rbf_node_name]["pose_values"] = driver_data[driver]["pose_values"]
    return right_driver_data


def setup_weight_drivers(driver_data={}):
    """
    Installs the drivers based on the data input
    :param driver_data:
    :return:
    """
    # load the necessary plugins
    load_plugins()

    driver_nodes = ()
    for driver in driver_data:
        driven_name = driver_data[driver]["driver_attrs"][0].split('.')[0]
        if _suffix_name not in driven_name:
            rbf_node_name = driven_name + _suffix_name
        else:
            rbf_node_name = driven_name
        print(rbf_node_name)
        if cmds.ls(rbf_node_name):
            continue
        weight_driver_node = cmds.createNode('weightDriver')

        cmds.setAttr(weight_driver_node + '.type', driver_data[driver]["type"])

        for idx, driver_attr in enumerate(driver_data[driver]["driver_attrs"]):
            cmds.connectAttr(driver_attr, weight_driver_node + '.input[{}]'.format(idx))

        for idx, driven_attr in enumerate(driver_data[driver]["driven_attrs"]):
            cmds.connectAttr(weight_driver_node + '.output[{}]'.format(idx), driven_attr)

        for idx in driver_data[driver]["num_poses"]:
            # edit the pose inputs
            inputs = driver_data[driver]["pose_inputs"][idx]
            for input_idx, input_value in enumerate(inputs):
                cmds.setAttr(weight_driver_node + '.poses[{}].poseInput[{}]'.format(idx, input_idx), input_value)

            # edit the pose values
            pose_values = driver_data[driver]["pose_values"][idx]
            for pose_value_idx, pose_value in enumerate(pose_values):
                cmds.setAttr(weight_driver_node + '.poses[{}].poseValue[{}]'.format(idx, pose_value_idx), pose_value)
        driver_nodes += cmds.rename(cmds.listRelatives(weight_driver_node, p=1)[0], rbf_node_name),
    return driver_nodes
