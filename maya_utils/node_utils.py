"""
    node_utils.py
        module
"""
# import maya modules
from maya import cmds

# local imports
import name_utils
import attribute_utils
import object_utils
import outliner_utils

# local variables
naming_conventions = name_utils.get_naming_conventions()

# reloads
reload(attribute_utils)


def print_node_types():
    """
    all available node types
    """
    node_types = cmds.allNodeTypes()
    return node_types


def print_node_types_by_name(query_name):
    """
    retrieve node types by name
    """
    node_types = print_node_types()
    find_nodes = ()
    for n_type in node_types:
        if query_name in n_type:
            find_nodes += n_type,


class Node(object):
    """
    The main node class for general maya node use
    """
    def __init__(self, node="", base_name="", suffix_type_name="", index=None, outliner_color_value=None,
                 letter=None, side="", naming_convention="standard", direction_name=""):
        self.node = node
        self.letter = letter
        self.index = index
        self.suffix_type_name = suffix_type_name
        self.base_name = base_name
        self.outliner_color_value = outliner_color_value
        self.side = side
        self.direction_name = direction_name
        self.naming_convention = self.get_naming_convention(naming_convention)

    @staticmethod
    def get_naming_convention(convention):
        """
        gets naming convention dictionary data
        :param convention: <str> the naming convention key string
        :return: <dict> naming convention data
        """
        naming_convention = naming_conventions[convention]
        return naming_convention

    def set_outliner_color_value(self):
        """
        sets the color value in the outliner
        """
        outliner_utils.set_outliner_color()

    def connect_to(self, source_attribute, target_node, target_attribute):
        """
        connects the node from the source attribute to the target attribute
        :param source_attribute: <str> source attribute to connect from
        :param target_node: <str> target node name
        :param target_attribute: <str> target attribute to connect to
        """
        src_attr = self.node + '.' + source_attribute
        tgt_attr = target_node + '.' + target_attribute
        if not cmds.isConnected(src_attr, tgt_attr):
            cmds.connectAttr(src_attr, tgt_attr)

    def point_constrain_to(self, target_node, axes=('x', 'y', 'z'), maintain_offset=False):
        """
        point constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param axes: <tuple> axes to constrain to
        :param maintain_offset: <bool> constrain with offset
        :return: <str> point constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(axes)
        point_cnst = cmds.pointConstraint(self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return point_cnst

    def orient_constrain_to(self, target_node, axes=('x', 'y', 'z'), maintain_offset=False):
        """
        orient constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param axes: <tuple> axes to constrain to
        :param maintain_offset: <bool> constrain with offset
        :return: <str> orient constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(axes)
        orient_cnst = cmds.orientConstraint(self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return orient_cnst

    def parent_constrain_to(self, target_node, axes=('x', 'y', 'z'), maintain_offset=False):
        """
        parent constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param axes: <tuple> axes to constrain to
        :param maintain_offset: <bool> constrain with offset
        :return: <str> parent constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(axes)
        parent_cnst = cmds.parentConstraint(self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return parent_cnst

    def scale_constrain_to(self, target_node, axes=('x', 'y', 'z'), maintain_offset=False):
        """
        scale constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param axes: <tuple> axes to constrain to
        :param maintain_offset: <bool> constrain with offset
        :return: <str> orient constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(axes)
        scale_cnst = cmds.scaleConstraint(self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return scale_cnst

    def aim_constrain_to(self, target_node, axes=('x', 'y', 'z'), world_up_type="scene",
                         world_up_object=None, world_up_vector="y", maintain_offset=False):
        """
        scale constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param axes: <tuple> axes to constrain to
        :param maintain_offset: <bool> constrain with offset
        :param world_up_vector: <str> the up vector axis
        :param world_up_type: <str> object, vector, scene
        :param world_up_object: <str> object name to point the up axis towards
        :return: <str> orient constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(axes)
        aim_cnst = cmds.aimConstraint(self.node, target_node, worldUpType=world_up_type, worldUpObject=world_up_object,
                                      worldUpVector=world_up_vector, mo=maintain_offset, skip=skip_axes)
        return aim_cnst

    def add_parent_group_node(self):
        """
        adds a parent group node on top of the current node in the same transform space
        :return: <str> parent group node
        """

    def add_float_attr(self, attr_name, default_value=None, max_value=None, min_value=None):
        """
        add a float attribute to the node
        :return: <str> float attribute
        """
        float_attr = attribute_utils.attr_add_float(
            self.node, attr_name, default_value=default_value, max_value=max_value, min_value=min_value)
        return float_attr

    def get_suffix_type_name(self):
        """
        suffix type name
        :return: <str> suffix type name
        """
        if self.suffix_type_name and self.suffix_type_name in self.naming_convention:
            suffix_type_name = self.naming_convention[self.suffix_type_name]
        else:
            suffix_type_name = cmds.nodeType(self.node)
        return suffix_type_name

    def get_side_name(self):
        """
        gets the side name
        :return: <str> side name
        """
        sides = ('right', 'left', 'center')
        if self.side and self.side not in sides:
            raise ValueError("[SideNameInvalid] :: Incorrect side name provided.")
        side_name = self.naming_convention[self.side]
        return side_name

    def get_control_suffix_name(self):
        """
        gets the control suffix name
        :return: <str> suffix name
        """
        ctrl_suffix_name = self.naming_convention['control']
        return ctrl_suffix_name

    def get_group_suffix_name(self):
        """
        gets the group suffix name
        :return: <str> group suffix name
        """
        group_suffix_name = self.naming_convention['group']
        return group_suffix_name

    def get_letter_name(self):
        """
        gets the letter name correctly
        :return: <str> letter name
        """
        letter_name = ""
        if self.letter:
            letter_name = self.letter.upper()
        return letter_name

    def get_name(self, suffix_name=None):
        """
        gets the provided name
        """
        side_name = self.get_side_name()
        name = name_utils.get_name(name=self.base_name, index=self.index, letter=self.letter,
                                   direction_name=self.direction_name, side_name=side_name, suffix_name=suffix_name)
        return name

    def rename(self):
        """
        rename the node
        :return: <str> the new name
        """
        new_name = self.get_name()
        cmds.rename(self.node, new_name)
        return new_name

    def find_types_list(self, node_type, deep=False, exact=False, forward=False):
        """
        Search the node's dependency sub graph to find all nodes of the given type.
        A search is either upstream (input connections), downstream (output connections)
        The plug/ attribute dependencies are not taken into account when searching from matching nodes,
        only the connections
        :param deep: <bool> find all nodes of the given type instead of just the first
        :param exact: <bool> match node types exactly instead of any in the node hierarchy
        :param forward: <bool> look forwards (downstream) through the graph rather than backwards (upstream)
            for matching nodes
        :param node_type: <str> mandatory, type of node to look for.
        :return: <list> found connections
        """
        find_types = cmds.findType(self.node, type=node_type, deep=deep, exact=exact, forward=forward)
        return find_types

    @property
    def is_transform(self):
        """
        check if the node is a transform node
        :return: <bool> is node a transform
        """
        is_transform = object_utils.is_transform(self.node)
        return is_transform

    @property
    def is_shape_nurbs_curve(self):
        """
        check if the node has a shape node
        :return: <bool> is node a shape
        """
        has_nurbs_curve = object_utils.is_shape_nurbs_curve(self.node)
        return has_nurbs_curve

    @property
    def is_shape_mesh(self):
        """
        check if node is a mesh object
        :return:
        """
        is_shape_mesh = object_utils.is_shape_mesh(self.node)
        return is_shape_mesh

    @property
    def is_dag(self):
        """
        check if node is a mesh object
        :return:
        """
        is_dag = object_utils.is_dag(self.node)
        return is_dag


# ______________________________________________________________________________________________________________________
# blend colors

class BlendColors(Node):
    def __init__(self, **kwargs):
        super(BlendColors, self).__init__(**kwargs)

    def create_binary_switch(self, name='', driver_attr="", driven_attr_0="", driven_attr_1=""):
        """
        creates a binary switch for the controller object.
        :return: <str> blendColors node.
        """
        blend_node = cmds.createNode('blendColors', name=name)
        # setting the value of the first condition switch
        cmds.setAttr(blend_node + '.color1R', 1.0)
        cmds.setAttr(blend_node + '.color1G', 0.0)
        cmds.setAttr(blend_node + '.color1B', 0.0)
        # setting the value of the second condition switch
        cmds.setAttr(blend_node + '.color1R', 0.0)
        cmds.setAttr(blend_node + '.color1G', 1.0)
        cmds.setAttr(blend_node + '.color1B', 0.0)
        # now connect the result
        cmds.connectAttr(driver_attr, blend_node + '.blender')
        cmds.connectAttr(blend_node + '.outputR', driven_attr_0)
        cmds.connectAttr(blend_node + '.outputG', driven_attr_1)
        return blend_node

# ______________________________________________________________________________________________________________________
# group


class Group(Node):
    def __init__(self, suffix_name="", **kwargs):
        # suffix name to use on this group node
        self.suffix_name = suffix_name
        super(Group, self).__init__(**kwargs)

    def create(self):
        """
        creates the group node
        :return:
        """
        cmds.group(em=True)

# ______________________________________________________________________________________________________________________
# node_utils.py
