"""
    constraint_utils.py managing constraint nodes
"""

# import maya modules
from maya import cmds

# import local modules
import node_utils
import name_utils


class Point(node_utils.Node):
    def __init__(self, **kwargs):
        super(Point, self).__init__(**kwargs)


class Aim(node_utils.Node):
    """
        Create an aim constraint between the specified source and target transforms.
    """
    def __init__(self, aim_axis='x', up_axis='y', world_up_type=None,
                 world_up_vector='y', offset=(0.0, 0.0, 0.0), maintain_offset=False, **kwargs):
        super(Aim, self).__init__(**kwargs)


class Parent(node_utils.Node):
    def __init__(self, **kwargs):
        super(Parent, self).__init__(**kwargs)


class Scale(node_utils.Node):
    def __init__(self, **kwargs):
        super(Scale, self).__init__(**kwargs)


# ______________________________________________________________________________________________________________________
# constraint_utils.py
