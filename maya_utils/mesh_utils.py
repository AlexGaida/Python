"""
mesh_utils.py utility node relating to mesh functions
"""
# import maya modules
from maya import OpenMaya

# import local modules
import object_utils

# define local variables


def compare_points_on_edge(point_a, point_b):
    """
    check if the points all share the same edge loop.
    :param point_a: <str> point a.
    :param point_b: <str> point b check relating to point_b.
    :return: <bool> True for yes. <bool> False for no.
    """
    m_point_1 = object_utils.get_m_obj(point_a)
    m_point_2 = object_utils.get_m_obj(point_b)

    return False