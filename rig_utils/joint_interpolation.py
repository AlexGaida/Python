from maya import cmds

class Interpolate(object):
    """Create an interpolating vector for a single joints, borken up with individual interpolating angles in between the 0-1 value
    """
    def __init__(joint_name, name="test0", interpolation_data={}):
        """
        :param joint_name: the name of the joint to apply interpolation to
        :param name: name to use on creating the interpolation
        :param interpolation_data: use this data to create a new interpolation point
        """
        self.joint_xform = cmds.xform(joint_name, ws=1, m=1, query=1)
        self.name = name

    def create_linear_target(self, shape_name, start_obj, end_obj):
        """creates a linear target rig 
        :param start_obj:
        :param end_obj:
        """
        start_xform = cmds.xform(start_obj, ws=1, m=1, query=1)
        end_xform = cmds.xform(end_obj, ws=1, m=1, query=1)
        mel.eval("curve -d 1 -p {} -p {} -k 0 -k 1".format(start_xform, end_xform))
        #...create pink locators
        cmds.spaceLocator(name=shape_name, )
        #...
        return True
# _______________________________________________________________________________
# joint_interpolation.py