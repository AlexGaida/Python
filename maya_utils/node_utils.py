"""
    node_utils.py
        module
"""
# standard imports
import ast

# standard imports
import ast

# import maya modules
from maya import cmds

# local imports
from . import name_utils
from . import attribute_utils
from . import object_utils
from . import outliner_utils
import math_utils
from . import math_utils

# local variables
naming_conventions = name_utils.get_naming_conventions()

# reloads
# reload(attribute_utils)


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

    def __init__(self, node="", base_name="", suffix_name="", prefix_name="", index=None,
                 outliner_color_value=None, outliner_color_name=None,
                 letter=None, side_name="", naming_convention="standard", direction_name="", **kwargs):
        self.letter = letter
        self.index = index
        self.prefix_name = prefix_name
        self.suffix_name = suffix_name
        self.base_name = base_name
        self.outliner_color_value = outliner_color_value
        self.side_name = side_name
        self.direction_name = direction_name
        self.outliner_color_name = outliner_color_name
        self.naming_convention = self.get_naming_convention(naming_convention)
        # extra attributes
        self.naming_attr = 'node_name_data'
        if not node:
            self.name = self.get_name()
            self.node = self.name
        else:
            self.node = node
            self.name = node

    @staticmethod
    def get_naming_convention(convention):
        """
        gets naming convention dictionary data
        :param convention: <str> the naming convention key string
        :return: <dict> naming convention data
        """
        naming_convention = naming_conventions[convention]
        return naming_convention

    def create(self):
        """
        create the node in question
        :return:
        """
        # self.set_name_dict_attr()

    def get_name(self, suffix_name=None, index=None, letter=None,
                 side_name=None, prefix_name=None, direction_name=None):
        """
        Get the name from parameters given
        :param suffix_name: <str>
        :param index: <int>
        :param letter: <str>
        :param side_name: <str>
        :param prefix_name: <str>
        :param direction_name: <str>
        """
        if not suffix_name:
            suffix_name = self.suffix_name
        if not index:
            index = self.index
        if not letter:
            letter = self.letter
        if not side_name:
            side_name = self.side_name
        if not prefix_name:
            prefix_name = self.prefix_name
        if not direction_name:
            direction_name = self.direction_name
        if not self.prefix_name:
            prefix_name = self.prefix_name
        name = name_utils.get_name(self.base_name, suffix_name=suffix_name, prefix_name=prefix_name,
                                   direction_name=direction_name, index=index, letter=letter, side_name=side_name)
        self.name = name
        return name

    def set_name_dict_attr(self, base_name=None, suffix_name=None, index=None, letter=None,
                           side_name=None, prefix_name=None, direction_name=None):
        """
        sets the naming dictionary attributes to the node
        :param base_name: <str>
        :param suffix_name: <str>
        :param index: <int>
        :param letter: <str>
        :param side_name: <str>
        :param prefix_name: <str>
        :param direction_name: <str>
        :returns:
        """
        if not self.exists:
            return None
        if not self.is_transform:
            return None
        name_dict = {}
        if not base_name:
            base_name = self.base_name
            name_dict['base_name'] = base_name
        if not suffix_name:
            suffix_name = self.suffix_name
            name_dict['suffix_name'] = suffix_name
        if not index:
            index = self.index
            name_dict['index'] = index
        if not letter:
            letter = self.letter
            name_dict['letter'] = letter
        if not side_name:
            side_name = self.side_name
            name_dict['side_name'] = side_name
        if not prefix_name:
            prefix_name = self.prefix_name
            name_dict['prefix_name'] = prefix_name
        if not direction_name:
            direction_name = self.direction_name
            name_dict['direction_name'] = direction_name
        if not self.prefix_name:
            prefix_name = self.prefix_name
            name_dict['prefix_name'] = prefix_name
        # set attribute to the node
        attribute_utils.attr_add_str(self.node, self.naming_attr, name_dict)
        return name_dict

    def get_name_dict_attr(self):
        """
        gets the naming dictionary attribute to the node
        :return: <dict> naming dictionary data
        """
        naming_dict_str = attribute_utils.attr_get_value(
            self.node, self.naming_attr)
        naming_dict = ast.literal_eval(naming_dict_str)
        return naming_dict

    def set_outliner_color_value(self, color_value=None):
        """
        sets the color value in the out-liner color values
        :para, color_value: <tuple> color value to set on the outliner color
        """
        if color_value:
            self.outliner_color_value = color_value
        if self.outliner_color_value:
            outliner_utils.set_outliner_color_value(
                self.node, self.outliner_color_value)

    def set_outliner_color_name(self, color_name=None):
        """
        set the outliner color by name
        :param color_name: color name to set
        """
        if not color_name:
            self.outliner_color_name = color_name
        if self.outliner_color_name:
            outliner_utils.set_outliner_color_by_name(
                self.node, self.outliner_color_name)

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

    def point_constrain_to(self, target_node, skip_axes=('x', 'y', 'z'), maintain_offset=False):
        """
        point constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param maintain_offset: <bool> constrain with offset
        :param skip_axes: <tuple> skip these axes from being constrained
        :return: <str> point constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(skip_axes)
        point_cnst = cmds.pointConstraint(
            self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return point_cnst

    def orient_constrain_to(self, target_node, skip_axes=('x', 'y', 'z'), maintain_offset=False):
        """
        orient constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param maintain_offset: <bool> constrain with offset
        :param skip_axes: <tuple> skip these axes from being constrained
        :return: <str> orient constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(skip_axes)
        orient_cnst = cmds.orientConstraint(
            self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return orient_cnst

    def parent_constrain_to(self, target_node, maintain_offset=False):
        """
        parent constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param maintain_offset: <bool> constrain with offset
        :return: <str> parent constraint node
        """
        parent_cnst = cmds.parentConstraint(
            self.node, target_node, mo=maintain_offset)
        return parent_cnst

    def scale_constrain_to(self, target_node, skip_axes=('x', 'y', 'z'), maintain_offset=False):
        """
        scale constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param maintain_offset: <bool> constrain with offset
        :param skip_axes: <tuple> skip these axes from being constrained
        :return: <str> orient constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(skip_axes)
        scale_cnst = cmds.scaleConstraint(
            self.node, target_node, mo=maintain_offset, skip=skip_axes)
        return scale_cnst

    def aim_constrain_to(self, target_node, skip_axes=('x', 'y', 'z'), world_up_type="scene",
                         world_up_object=None, world_up_vector="y", maintain_offset=False):
        """
        scale constrain to a target node
        :param target_node: <str> the target node to constrain to
        :param maintain_offset: <bool> constrain with offset
        :param world_up_vector: <str> the up vector axis
        :param world_up_type: <str> object, vector, scene
        :param world_up_object: <str> object name to point the up axis towards
        :param skip_axes: <tuple> skip these axes from being constrained
        :return: <str> orient constraint node
        """
        accepted_axes = set(('x', 'y', 'z'))
        skip_axes = set(accepted_axes).difference(skip_axes)
        aim_cnst = cmds.aimConstraint(self.node, target_node, worldUpType=world_up_type, worldUpObject=world_up_object,
                                      worldUpVector=world_up_vector, mo=maintain_offset, skip=skip_axes)
        return aim_cnst

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
        if self.side_name and self.side_name not in sides:
            raise ValueError(
                "[SideNameInvalid] :: Incorrect side name provided.")
        side_name = self.naming_convention[self.side_name]
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

    def rename(self):
        """
        rename the node
        :return: <str> the new name
        """
        new_name = self.get_name()
        self.set_name_dict_attr(suffix_name=self.suffix_name, index=self.index, letter=self.letter,
                                side_name=self.side_name, prefix_name=self.prefix_name,
                                direction_name=self.direction_name)
        cmds.rename(self.node, new_name)
        return new_name

    def find_types_list(self, node_type, deep=False, exact=False, forward=False):
        """
        Search the node's dependency sub graph to find all nodes of the given type
        A search is either upstream (input connections), downstream (output connections)
        The plug/ attribute dependencies are not taken into account when searching from matching nodes
        only the connections
        :param deep: <bool> find all nodes of the given type instead of just the first
        :param exact: <bool> match node types exactly instead of any in the node hierarchy
        :param forward: <bool> look forwards (downstream) through the graph rather than backwards (upstream)
            for matching nodes
        :param node_type: <str> mandatory, type of node to look for
        :return: <list> found connections
        """
        find_types = cmds.findType(
            self.node, type=node_type, deep=deep, exact=exact, forward=forward)
        return find_types

    def get_world_matrix(self):
        """
        gets the world matrix
        :return: <list> node world matrix
        """
        world_matrix = []
        if self.is_transform:
            world_matrix = object_utils.get_world_matrix(self.node)
        return world_matrix

    def get_object_matrix(self):
        """
        gets the position from other node
        :return: <list> object matrix
        """
        relative_matrix = []
        if self.is_transform:
            relative_matrix = object_utils.get_relative_matrix(self.node)
        return relative_matrix

    def get_world_position(self):
        """
        get world position
        :return: <list> world position
        """
        world_position = []
        if self.is_transform:
            world_position = object_utils.get_world_position(self.node)
        return world_position

    def get_relative_position(self):
        """
        get relative position
        :return: <list> relative position
        """
        relative_position = []
        if self.is_transform:
            relative_position = object_utils.get_relative_position(self.node)
        return relative_position

    def lock_attribute(self, attribute_name):
        """
        lock the attribute
        """
        if not self.is_transform:
            return None
        if not attribute_name.startswith('.'):
            attribute_name = '.' + attribute_name
        cmds.setAttr(self.node + attribute_name, lock=True)

    def hide_attribute(self, attribute_name):
        """
        lock the attribute
        """
        if not self.is_transform:
            return None
        if not attribute_name.startswith('.'):
            attribute_name = '.' + attribute_name
        cmds.setAttr(self.node + attribute_name, k=False)

    def lock_hide_translate(self):
        """
        locks and hides translate attributes
        """
        if not self.is_transform:
            return None
        translate_attrs = ['.tx', '.ty', '.tz']
        for t_attr in translate_attrs:
            cmds.setAttr(self.node + t_attr, lock=True)
            cmds.setAttr(self.node + t_attr, k=False)

    def lock_hide_scale(self):
        """
        locks and hides scale attributes
        """
        if not self.is_transform:
            return None
        scale_attrs = ['.sx', '.sy', '.sz']
        for s_attr in scale_attrs:
            cmds.setAttr(self.node + s_attr, lock=True)
            cmds.setAttr(self.node + s_attr, k=False)

    def lock_hide_rotate(self):
        """
        locks and hides rotate attributes
        """
        if not self.is_transform:
            return None
        rotate_attrs = ['.rx', '.ry', '.rz']
        for r_attr in rotate_attrs:
            cmds.setAttr(self.node + r_attr, lock=True)
            cmds.setAttr(self.node + r_attr, k=False)

    def set_world_position(self, world_position):
        """
        sets the world position of this node
        :param world_position: <list> world position
        """
        cmds.xform(self.node, ws=1, t=world_position)

    def set_relative_position(self, world_position):
        """
        sets the world position of this node
        :param world_position: <list> world position
        """
        cmds.xform(self.node, ws=0, t=world_position)

    def set_position_to_node(self, node):
        """
        sets the position to the node
        :param node: <str> the node to set the current node to
        """
        print('node: ', node)
        if not hasattr(node, 'is_node'):
            world_position = cmds.xform(node, ws=1, t=1, q=1)
        else:
            world_position = node.get_world_position()
        cmds.xform(self.node, t=world_position)

    def parent_to(self, other_node):
        """
        parent this node to the other node
        :param other_node: <str> parent node to parent under
        """
        if not isinstance(other_node, basestring):
            other_node = other_node.node
        object_utils.do_parent(self.node, other_node)

    def aim_at(self, other_node):
        """
        aim this node at another transform object
        :param other_node: <str> aim at this other node object
        """
        aim_vector = math_utils.look_at(self.node, other_node)
        cmds.setAttr(self.node + '.rotation', *aim_vector)

    def remove(self):
        """
        remove this node from the Maya scene
        """
        object_utils.remove_node(self.node)

    def is_exists(self):
        """
        check if the node exists
        :return: <bool> True if exists, False if not
        """
        is_exists = object_utils.is_exists(self.node)
        return is_exists

    def get_parent_node(self):
        """
        return the parent node above this transform node
        :return: <str> parent node
        """
        parent_node = None
        if self.is_transform:
            parent_node = cmds.listRelatives(self.node, parent=True)
            if parent_node:
                parent_node = parent_node[0]
                parent_node = Node(parent_node)
        return parent_node

    @property
    def world_position(self):
        """
        return world position list
        :return: <list> world position list
        """
        world_position = self.get_world_position()
        return world_position

    @property
    def list_custom_attrs(self):
        """
        list custom attributes by node
        :return: <list> custom attributes
        """
        custom_attrs = cmds.listAttr(ud=True)
        return custom_attrs

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

    @property
    def exists(self):
        """
        returns true if the node exists
        :return: <bool> node exists
        """
        exists = cmds.objExists(self.name)
        return exists

    @property
    def is_node(self):
        """
        returns a boolean attribute for when object is queried this property
        :return: <bool> True
        """
        return True

    def __repr__(self):
        return self.name


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
# group node


class Group(Node):
    def __init__(self, suffix_name=None, **kwargs):
        if not suffix_name:
            suffix_name = 'Grp'
        self.suffix_name = suffix_name
        super(Group, self).__init__(suffix_name=suffix_name, **kwargs)
        # suffix name to use on this group node
        self.create()

    def create(self):
        """
        creates the group node
        :return:
        """
        if self.exists:
            return None
        cmds.group(name=self.name, em=True)

# ______________________________________________________________________________________________________________________
# node_utils.py
