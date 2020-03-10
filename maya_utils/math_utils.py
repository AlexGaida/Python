"""
Standard math functions and manipulating vector operations.
"""
# import standard modules
from collections import Iterable

# import maya modules
from maya.OpenMaya import MVector, MMatrix, MPoint, MTransformationMatrix
from maya import cmds

# import local modules
import math
import transform_utils
import object_utils

# define local variables
M_PI = 3.14159265358979323846
CIRCLE = 360
HALF_CIRCLE = 180
EXP = 2.718281
RADIANS_2_DEGREES = 57.2958
DEGREES_2_RADIANS = 0.0174533

connect_attr = object_utils.connect_attr
attr_name = object_utils.attr_name
attr_set = object_utils.attr_set


def squared_difference(num_array=()):
    """
    calculate the squared difference (the mean) from the array of number values given.
    :param num_array:
    :return:
    """
    return (sum(map(lambda x: x**2, num_array)) / len(num_array))**0.5


def gaussian(in_value=0.0, magnitude=0.0, mean=0.0, variance=0.0):
    """
    calculate gaussian
    :param in_value:
    :param magnitude:
    :param mean:
    :param variance:
    :return:
    """
    if variance <= 0.0:
        variance = 0.001
    return magnitude * EXP ** (-1 * (in_value - mean**2) / (2.0 * variance))


def flatten_list(list_data=()):
    """
    flatten the nested lists into one list.
    :param list_data: <list> the list of lists to flatten.
    :return: <list> flattened list.
    """
    for x in list_data:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten_list(x):
                yield sub_x
        else:
            yield x


def get_sum(value_data=()):
    """
    gets the sum of all values inside a list object.
    :param value_data: <list> the values to get the
    :return: <float> the sum of all values.
    """
    return sum(flatten_list(value_data))


def power(x, n):
    return x ** n


def exponential(x):
    return EXP**x


def gaussian(x, x0, sigma):
    return exponential(-power((x - x0)/sigma, 2.0)/2.0)


def float_range(start, stop, step):
    while start <= stop:
        yield float(start)
        start += step


def degrees_to_radians(degrees):
    return degrees * (M_PI / 180.0)


def radians_to_degrees(radians):
    return radians * (180.0 / M_PI)


def round_to_step(x, parts=4):
    """
    rounds to the step given, 4 is a quarter step, because 1.0 / 4 = 0.25.
    :param x: input value.
    :param parts: divisible by this many parts.
    :return: <float> to the rounded part.
    """
    return round(x*parts)/parts


def get_object_transform(item):
    return tuple(map(float, cmds.xform(item, q=True, t=True, ws=True)))


def get_object_matrix(item):
    return tuple(cmds.xform(item, q=True, matrix=True, ws=True))


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
    elif len(args) == 1:
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


class Vector(MVector):
    RESULT = ()

    def __init__(self, *args):
        if isinstance(args[0], str):
            super(Vector, self).__init__(*get_object_transform(args[0]))
        else:
            super(Vector, self).__init__(*args)

    def do_division(self, amount=2.0):
        """
        divide the vector into sections.
        :param amount: <int> divide the vector into these sections.
        :return: <tuple> section vector.
        """
        self.RESULT = self.x / amount, self.y / amount, self.z / amount,
        return self.RESULT

    def do_multiply(self, amount=2.0):
        """
        multiply the vector by the amount.
        :param amount: <int> divide the vector into these sections.
        :return: <tuple> section vector.
        """
        self.RESULT = self.x * amount, self.y * amount, self.z * amount,
        return self.RESULT

    def get_position(self):
        self.RESULT = self.x, self.y, self.z,
        return self.RESULT

    @property
    def result(self):
        return self.RESULT

    @property
    def position(self):
        return self.get_position()


class OldVector:
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

    def __div__(self, division):
        data = list()

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


def look_at(source, target, up_vector=(0, -1, 0)):
    """
    allows the transform object to look at another target vector object.
    :return: <tuple> rotational vector.
    """
    source_world = transform_utils.Transform(source).world_matrix_list()
    target_world = transform_utils.Transform(target).world_matrix_list()
    source_parent_name = object_utils.get_parent_name(source_world)
    parent_world = transform_utils.Transform(source_parent_name).world_matrix_list()

    # build normalized vector
    z = MVector(target_world[12] - source_world[12],
                target_world[13] - source_world[13],
                target_world[14] - source_world[14])
    z.normalize()

    # get normalized cross the z with the up vector at origin
    x = z ^ MVector(-up_vector[0], -up_vector[1], -up_vector[2])
    x.normalize()

    # get the normalized y vector
    y = x ^ z
    y.normalize()

    # build the aim matrix
    local_matrix_list = (
        x.x, x.y, x.z, 0,
        y.x, y.y, y.z, 0,
        z.x, z.y, z.z, 0,
        0, 0, 0, 1)

    matrix = object_utils.ScriptUtil(local_matrix_list, matrix_from_list=True)

    if source_parent_name:
        # transform the matrix in the local space of the parent object
        parent_matrix = object_utils.ScriptUtil(parent_world, matrix_from_list=True)
        matrix *= parent_matrix.inverse()

    # retrieve the desired rotation for "source" to aim at "target", in degrees
    rotation = MTransformationMatrix(matrix).eulerRotation() * RADIANS_2_DEGREES
    vector = rotation.asVector()
    return vector.x, vector.y, vector.z,


def get_vector_position_2_points(position_1, position_2, divisions=2.0):
    """
    calculates the world space vector between the two positions.
    :param position_1: <tuple> list vector
    :param position_2: <tuple> list vector
    :param divisions: <int> calculate the vector positions of divisions.
    :return: <tuple> vector
    """
    positions = ()
    for i in xrange(1, divisions):
        vec_1 = Vector(*position_1)
        vec_2 = Vector(*position_2)
        new_vec = Vector(vec_1 - vec_2)
        div_vec = Vector(new_vec * (float(i) / float(divisions)))
        result_vec = Vector(*div_vec.position)
        positions += Vector(result_vec + vec_2).position,
    return positions


def get_vector_positon_2_objects(object_1, object_2, divisions=2):
    """
    calculates the world space vector between the two points.
    :return: <tuple> vector positions.
    """
    vector_1 = transform_utils.Transform(object_1).translate_values(world=True)
    vector_2 = transform_utils.Transform(object_2).translate_values(world=True)
    return get_vector_position_2_points(vector_1, vector_2, divisions)


def calculate_angle(vector1, vector2):
    """
    calculates the angle from x, y values given
    :return:
    """
    v1 = Vector(*vector1)
    v2 = Vector(*vector2)
    dot_product = v1 * v2
    return math.acos(dot_product) * 180 / M_PI


def calculate_circle_collision(object_1, object_2, object_1_radius=0.0, object_2_radius=0.0):
    """
    return True if the two objects' radiuses collide with eachother.
    :param object_1:
    :param object_2:
    :param object_1_radius:
    :param object_2_radius:
    :return: <bool> if the objects collide.
    """
    return mag(object_1, object_2) <= object_1_radius + object_2_radius


def calculate_circle_point_collision(object_1, object_2, object_1_radius=0.0):
    """
    return True if the two objects' radiuses collide with each other.
    :param object_1: the circle object.
    :param object_2:
    :param object_1_radius: the radius of the circle.
    :return: <bool> if the objects collide.
    """
    return mag(object_1, object_2) <= object_1_radius


def create_ratio_driver(driver_object="", driven_object="", add_clamp=True, radius=1.0, driver_type='sine',
                        driven_attribute='translateY', driver_attributes=('translateX', 'translateY')):
    """
    create a sine ratio from the driver vector co-ordinates to the driver object vector.
    :param driver_object: <str> driving object.
    :param driven_object: <str> driven object.
    :param driven_attribute: <str> driven attribute to drive.
    :param add_clamp: <bool> adds a clamp node to clamp the values to not get the -1.0 return value.
    :param radius: <float> the radius object from the origin of rotation.
    :param driver_type: <str> sine, cosine, the driver ratio type to create.
    :param driver_attributes: <tuple> the two driving attributes to use. (numerator/ denominator)
    :return: <str> ratio node.
    """
    ratio_node_name = "{}_{}_ratio".format(driver_object, driver_type)
    clamp_node_name = "{}_{}_clamp".format(driver_object, driver_type)
    ratio_node = object_utils.create_node('multiplyDivide', node_name=ratio_node_name)
    clamp_node = object_utils.create_node('clamp', node_name=clamp_node_name)
    attr_set(attr_name(ratio_node, 'operation'), 2)
    if driver_type == 'sine':
        attr_set(attr_name(ratio_node, 'input2X'), radius)
        connect_attr(attr_name(driver_object, driver_attributes[1]), attr_name(ratio_node, 'input1X'))
    elif driver_type == 'cosine':
        attr_set(attr_name(ratio_node, 'input2X'), radius)
        connect_attr(attr_name(driver_object, driver_attributes[0]), attr_name(ratio_node, 'input1X'))
    else:
        raise NotImplementedError("[InvalidDriverType] :: Available options: sine, cosine.")
    attr_set(attr_name(clamp_node, 'maxR'), 1.0)
    if add_clamp:
        connect_attr(attr_name(ratio_node, 'outputX'), attr_name(clamp_node, 'inputR'))
        connect_attr(attr_name(clamp_node, 'outputR'), attr_name(driven_object, driven_attribute))
    elif not add_clamp:
        connect_attr(attr_name(ratio_node, 'outputX'), attr_name(driven_object, driven_attribute))
    return ratio_node


def create_sine_ratio_driver(driver_object="", driven_object="", add_clamp=True, radius=1.0,
                             driven_attribute='translateY', driver_attributes=('translateX', 'translateY')):
    """
    Sine ratio: opposite/ radius
    :param driver_object:
    :param driven_object:
    :param add_clamp:
    :param radius:
    :param driven_attribute:
    :param driver_attributes:
    :return: <str> ratio node.
    """
    return create_ratio_driver(driver_object,
                               driven_object,
                               add_clamp,
                               radius,
                               'sine',
                               driven_attribute,
                               driver_attributes)


def create_cosine_ratio_driver(driver_object="", driven_object="", add_clamp=True, radius=1.0,
                               driven_attribute='translateY', driver_attributes=('translateX', 'translateY')):
    """
    Cosine ratio: adjacent/ radius.
    :param driver_object:
    :param driven_object:
    :param add_clamp:
    :param radius:
    :param driven_attribute:
    :param driver_attributes:
    :return: <str> ratio node.
    """
    return create_ratio_driver(driver_object,
                               driven_object,
                               add_clamp,
                               radius,
                               'cosine',
                               driven_attribute,
                               driver_attributes)


def quadratic(v0, v1, v2, t):
    """
    calculates the quadratic curve interpolation
    :param v0:
    :param v1:
    :param v2:
    :param t:
    :return:
    """
    point_final = {}
    point_final.update(x=((1 - t) ** 2) * v0.x + (1 - t) * 2 * t * v1.x + t * t * v2.x)
    point_final.update(y=((1 - t) ** 2) * v0.y + (1 - t) * 2 * t * v1.y + t * t * v2.y)
    point_final.update(z=((1 - t) ** 2) * v0.z + (1 - t) * 2 * t * v1.z + t * t * v2.z)
    return point_final


def bezier(v0, v1, v2, v3, t):
    """
    calculates the bezier curve interpolation
    :param v0:
    :param v1:
    :param v2:
    :param t:
    :return:
    """
    point_final = {}
    point_final.update(x=((1 - t) ** 3) * v0.x + (1 - t) ** 2 * 3 * t * v1.x +
                         (1 - t) * 3 * t * t * v2.x + t * t * t * v3.x)
    point_final.update(y=((1 - t) ** 3) * v0.y + (1 - t) ** 2 * 3 * t * v1.y +
                         (1 - t) * 3 * t * t * v2.y + t * t * t * v3.y)
    point_final.update(z=((1 - t) ** 3) * v0.z + (1 - t) ** 2 * 3 * t * v1.z +
                         (1 - t) * 3 * t * t * v2.z + t * t * t * v3.z)
    return point_final


def linear_cubic_interpolation(driver_array=(), divisions=20, interpolation='quadratic'):
    """
    interpolate the cubic line between points.
    :return:
    """

    point_final = ()
    if interpolation == 'quadratic':
        for t in xrange(divisions):
            v1 = Vector(driver_array[0])
            v2 = Vector(driver_array[1])
            v3 = Vector(driver_array[2])
            point_final += quadratic(v1, v2, v3, float(t) / float(divisions)),
        return point_final

    elif interpolation == 'bezier':
        for t in xrange(divisions):
            v1 = Vector(driver_array[0])
            v2 = Vector(driver_array[1])
            v3 = Vector(driver_array[2])
            v4 = Vector(driver_array[3])
            point_final += bezier(v1, v2, v3, v4, float(t) / float(divisions))
        return point_final
