"""
    Measuring utility for determining values of the float objects
"""
# standard maya modules
import math

# maya modules
from maya import cmds, mel

# local modules
import math_utils
import curve_utils


def get_average_vector(vector_values):
    """
    returns the average value from the array of values given
    :param vector_values: <list> array of float values to get the average from
    :return:  <float> average from the values provided
    """
    x = ()
    y = ()
    z = ()
    for val in vector_values:
        x += val[0],
        y += val[1],
        z += val[2],
    average_x = sum(x) / len(vector_values)
    average_y = sum(y) / len(vector_values)
    average_z = sum(z) / len(vector_values)
    return average_x, average_y, average_z

# ______________________________________________________________________________________________________________________
# measuring_utils.py
