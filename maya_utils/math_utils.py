# import maya modules
from maya.OpenMaya import MVector, MMatrix, MPoint
from maya import cmds

# import local modules
import math
import decimal


def power(x, n):
    return x ** n


def exponential(x):
    return 2.718281**x


def gaussian(x, x0, sigma):
    return exponential(-power((x - x0)/sigma, 2.)/2.)


def float_range(start, stop, step):
    while start <= stop:
        yield float(start)
        start += step


def round_to_step(x, parts=4):
    """
    rounds to the step given, 4 is a quarter step, because 1.0 / 4 = 0.25.
    :param x: input value.
    :param parts: divisible by this many parts.
    :return: <float> to the rounded part.
    """
    return round(x*parts)/parts


def get_object_transform(item):
    return map(float, cmds.xform(item, q=True, t=True, ws=True))


def get_object_matrix(item):
    return cmds.xform(item, q=True, matrix=True, ws=True)


def get_halfway_point(point1="", point2=""):
    """
    returns a halfway point translate list
    :return: <list> halfway point.
    """
    omv_1 = MVector(*get_object_transform(point1))
    omv_2 = MVector(*get_object_transform(point2))
    vector_result = (omv_1 + omv_2) / 2
    return vector_result.x, vector_result.y, vector_result.z


def world_matrix(obj):
    """'
    convenience method to get the world matrix of <obj> as a matrix object
    """
    return MMatrix(get_object_matrix(obj))


def world_pos(obj):
    """'
    convenience method to get the world position of <obj> as an MPoint
    """
    return MPoint(get_object_transform(obj))


def relative_position(world_object="", position_object=""):
    """
    Get an object's relative position to another.
    :return: <str> position.
    """
    return str(world_pos(position_object) * world_matrix(world_object).inverse())


def pythag(x, y, find=0):
    """
    Pythogream Theorem.
    cos**2 + adj**2 = hyp**2
    x= Adjacent y= Opposite , find hypotneuse.
    :param x:
    :param y:
    :param find:
    :return: <float>
    """

    if not isinstance(x, float) and not isinstance(x, int):
        raise ValueError("Please input only float/ interger values for x: such as 1.0")

    if not isinstance(y, float) and not isinstance(y, int):
        raise ValueError("Please input only float/ interger values for y: such as 1.0")

    if find == 0:
        ''' input is opposite and adjacent '''
        return ((x**2)+(y**2))*0.5

        # Or you can use math.hypot(x, y)

    if find == 1:
        ''' input is hypotenuse and opposite or adjacent '''
        return abs((x**2)-(y**2))**0.5


def bary_2d(start, end, percent, barycentric=False):
    """
    2D Barycentric Co-ordinates
    Co-ordinates between start and end point: (start + end)* 0.5
    Accepts a vector start and a vector end and a float/interger percentage.
    Coordinates at percentage between start and end point
    :param start: <list>
    :param end: <list>
    :param barycentric: <bool> return barycentric coordinates instead.
    :param percent: <float> percent value.
    """

    if type(percent) not in [float, int]:
        if percent > 1 or percent < 0:
            raise ValueError("Percent must fall in between 1 and 0.")
        raise ValueError("Please input only float/ interger values for incrementing such as 1.0")

    # clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
    # perc = clamp( percent, -1, 0)

    vc = lambda x, y, z, i, percent: ((x * (i + percent)), (y*(i + percent)), (z*(i + percent)))

    if start and end:
        vector1 = vc(*(start+(0, percent)))
        vector2 = vc(*(end+(-1, percent)))

    mvec_1 = MVector(*vector1)
    mvec_2 = MVector(*vector2)

    mvec_3 = mvec_1 + mvec_2

    if barycentric:
        return (start * percent) + (end * (1-percent))
    return mvec_3.x, mvec_3.y, mvec_3.z


def mag(vector1, vector2):
    """
    Adds two vectors and finds the length of the third vector
    :param vector1: <list> translation data.
    :param vector2: <list> translation data.
    :return: <int> value.
    Uses Maya MVector class
    """
    omv_1 = MVector(*vector1)
    omv_2 = MVector(*vector2)
    omv_3 = omv_2 - omv_1
    segment_mag = lambda x, y, z: ((x**2)+(y**2)+(z**2))**0.5
    return segment_mag(omv_3.x, omv_3.y, omv_3.z)


def magnitude(*args):
    """
    INPUTS:
        args: magnitude( list(), list() ) or magnitude(list())


    INFO:
        suebtracts the second list vector from the first.
        squares each item in list then

        Inputs must be a vector of 3 values in a list!

    """
    data = list()

    # if a list of tail vector values are fed.
    if len(args) == 2:
        tail = args[0]
        if not type(tail) is list:
            raise ValueError("Please use a list of 3 floats or intergers")

        head = args[1]
        if not type(head) is list:
            raise ValueError("Please use a list of 3 floats or intergers")

        # vectors assume only three values in the list!
        # Using this, we find the vector!
        for j in range(3):
            data.append((tail[j] - head[j])**2)

        data= sum(data)

        return abs(data**0.5)

    # if a list of head vector values are fed.
    elif len(args)== 1:
        head = args[0]
        if not type(head) is list:
            raise ValueError("Please use a list of 3 floats or intergers")

        # Calculating magnitude of WorldSpace: sqrt((ax * ax) + (ay * ay) + (az * az))
        for j in range(len(head)):
            data.append(head[j]**2)
        data = sum(data)**0.5

        return abs(data)
    else:
        print("Wrong number of arguments used!\r\n\
                You must have either one or two lists of vectors: head, tail or head")


def angle(vector1, vector2):
    """
    Using formula cos? = a.b / |a||b|
    Computes the angle from two vectors.
    :param vector1: <list> translate point
    :param vector2: <list> translate point
    """
    data = list()
    # Add all magnitude of vector components!
    for j in range(3):
        data.append(vector1[j] * vector2[j])

    data = sum(data)
    return math.degrees(math.acos(data / (magnitude(vector1) * magnitude(vector2))))


class Vector:
    """
    INPUT:
        args: list() of three values, int(), int(), int() or float(), float(), float() types.
                two lists of three values: vector tail, vector head.

    INFO:
        Inputs a vector list, returns a class function of the vector.
        Accepts tail, head vector lists.
        Vector.magnitude returns a vector magnitude from origin.

    USAGE:
        # Define vectors
        a= Vector([1.5, 0.4, 6])
        b= Vector([6, 2, 1])

        # Add or subtract vectors
        c = a + b
        print "ADD: %s"%c
        c = a - b
        print "SUB: %s"%c
    """
    def __init__(self, *args):
        data = list()
        mag = list()

        # if a list of tail vector values are fed.
        if len(args) == 2:
            tail = args[0]
            if not type(tail) is list:
                raise ValueError("Please use a list of 3 floats or intergers")

            head = args[1]
            if not type(head) is list:
                raise ValueError("Please use a list of 3 floats or intergers")

            self.magnitude = magnitude(tail, head)

        # if a list of head vector values are fed.
        elif len(args) == 1:
            head = args[0]
            if not type(head) is list:
                raise ValueError("Please use a list of 3 floats or intergers")

            self.data = head

            self.magnitude = magnitude(head)

            # Calculating magnitude of WorldSpace: sqrt((ax * ax) + (ay * ay) + (az * az))
            for j in range(len(self.data)):
                mag.append(self.data[j]*self.data[j])
            mag = sum(mag)**0.5
            self.magnitude = abs(mag)

        else:
            print("Wrong number of arguments used!\r\n\
                    You must have either one or two lists of vectors: head, tail or head")

        # get the vector data by subtracting from the head by the tail.
        if "tail" in dir():
            for v in range(len(tail)):
                data.append(head[v] - tail[v])

            self.data = data

    def __str__(self):

        return repr(self.data)

    def __repr__(self):
        """
        When using __repr__, it is important to note that what returns is an instance
        You can get the name of the instance by loc1.__class__.__name__
        But you still need to get the object.data
        """
        return "%s" % self.data

    def __add__(self, other):
        data = list()

        for j in range(len(self.data)):
            data.append(self.data[j] + other.data[j])

        return Vector(data)

    def __sub__(self, other):
        data = list()

        for j in range(len(self.data)):
            data.append(self.data[j] - other.data[j])

        return Vector(data)

    def __mul__(self, other):
        data = list()

        if type(other) is float or type(other) is int:
            for j in range(len(self.data)):
                data.append(self.data[j] * other)

        if type(other) is list or type(other) is tuple:
            for j in range(len(self.data)):
                data.append(self.data[j] * other[j])

        else:
            try:
                for j in range(len(self.data)):
                    data.append(self.data[j] * other.data[j])
            except IndexError:
                pass

        return Vector(data)

    def __pow__(self, other):
        data = list()

        if type(other) is float or type(other) is int:
            for j in range(len(self.data)):
                data.append(self.data[j] ** other)

        if type(other) is list or type(other) is tuple:
            for j in range(len(self.data)):
                data.append(self.data[j] ** other[j])

        else:
            try:
                for j in range(len(self.data)):
                    data.append(self.data[j] ** other.data[j])
            except IndexError:
                pass

        return Vector(data)
