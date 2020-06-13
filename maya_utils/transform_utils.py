"""
Transform module for finding, creating and setting attributes
"""
# import standard modules
import math

# import maya modules
from maya import OpenMaya
from maya import cmds

# import local modules
import object_utils


def set_to_object_center(object_name, target_name):
    """
    set the object to the center of the other object.
    :param object_name: <str> the object name to position to the target.
    :param target_name: <str> the target name to get the center of the transform from.
    :return: <bool> True for success.
    """
    center_t = Transform(target_name).get_bounding_box_center()
    match_position_transform(object_name, center_t)
    return True


def get_world_position(object_name):
    """
    returns the translate position in world space.
    :param object_name:
    :return: <tuple> position transform array
    """
    return Transform(object_name).get_world_translation_list()


def get_world_matrix(object_name):
    """
    returns the world matrix
    :param object_name: <str> the object to get world matrix from.
    :return: <tuple> world matris array.
    """
    return Transform(object_name).wmatrix


def match_position_transform(source, target):
    """
    match the transform from the target to the source.
    :param source: <str> source object to snap to target.
    :param target: <str>, <tuple> target object, or position array.
    :return: <bool> True for success. <bool> False for failure.
    """
    if isinstance(target, (tuple, list)):
        if len(target) == 3:
            cmds.xform(source, t=target)
        else:
            cmds.xform(source, m=target)
    else:
        cmds.xform(source, t=get_world_position(target))
    return True


def match_matrix_transform(source, target):
    """
    match the transform
    :param source: <str> source object to snap to target.
    :param target: <str>, <tuple> target object, or matrix array.
    :return: <bool> True for success. <bool> False for failure.
    """
    if isinstance(target, (tuple, list)) and len(target) == 16:
        cmds.xform(source, m=target)
    else:
        cmds.xform(source, m=get_world_matrix(target))
    return True


def get_plug_value(in_plug):
    """
    Gets the value of the given plug.
    """
    pAttribute = in_plug.attribute()
    apiType = pAttribute.apiType()

    # Float Groups - rotate, translate, scale; Compounds
    if apiType in [OpenMaya.MFn.kAttribute3Double, OpenMaya.MFn.kAttribute3Float, OpenMaya.MFn.kCompoundAttribute]:
        result = ()

        if in_plug.isCompound():
            for c in xrange(in_plug.numChildren()):
                result += get_plug_value(in_plug.child(c)),
            return result

    # Distance
    elif apiType in [OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute]:
        return in_plug.asMDistance().asCentimeters()

    # Angle
    elif apiType in [OpenMaya.MFn.kDoubleAngleAttribute, OpenMaya.MFn.kFloatAngleAttribute]:
        return in_plug.asMAngle().asDegrees()

    # TYPED
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        pType = OpenMaya.MFnTypedAttribute(pAttribute).attrType()

        # Matrix
        if pType == OpenMaya.MFnData.kMatrix:
            return OpenMaya.MFnMatrixData(in_plug.asMObject()).matrix()

        # String
        elif pType == OpenMaya.MFnData.kString:
            return in_plug.asString()

    # MATRIX
    elif apiType == OpenMaya.MFn.kMatrixAttribute:
        return OpenMaya.MFnMatrixData(in_plug.asMObject()).matrix()

    # NUMBERS
    elif apiType == OpenMaya.MFn.kNumericAttribute:
        pType = OpenMaya.MFnNumericAttribute(pAttribute).unitType()

        if pType == OpenMaya.MFnNumericData.kBoolean:
            return in_plug.asBool()

        elif pType in [OpenMaya.MFnNumericData.kShort, OpenMaya.MFnNumericData.kInt, OpenMaya.MFnNumericData.kLong,
                       OpenMaya.MFnNumericData.kByte]:
            return in_plug.asInt()

        elif pType in [OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble, OpenMaya.MFnNumericData.kAddr]:
            return in_plug.asDouble()

    # Enum
    elif apiType == OpenMaya.MFn.kEnumAttribute:
        return in_plug.asInt()


class Transform(OpenMaya.MFnTransform):
    MAYA_STR_OBJECT = None
    M_SCRIPT_UTIL = OpenMaya.MScriptUtil()

    WORLD_SPACE = OpenMaya.MSpace.kWorld
    OBJECT_SPACE = OpenMaya.MSpace.kObject

    ROTATION_ORDER_NAMES = {1: 'kXYZ',
                            2: 'kYZX',
                            3: 'kZXY',
                            4: 'kXZY',
                            5: 'kYXZ',
                            6: 'kZYX'}

    ROTATE_ORDER_XYZ = OpenMaya.MTransformationMatrix.kXYZ
    ROTATE_ORDER_YZX = OpenMaya.MTransformationMatrix.kYZX
    ROTATE_ORDER_ZXY = OpenMaya.MTransformationMatrix.kZXY
    ROTATE_ORDER_XZY = OpenMaya.MTransformationMatrix.kXZY
    ROTATE_ORDER_YXZ = OpenMaya.MTransformationMatrix.kYXZ
    ROTATE_ORDER_ZYX = OpenMaya.MTransformationMatrix.kZYX
    ROTATE_ORDER_INVALID = OpenMaya.MTransformationMatrix.kInvalid

    X = OpenMaya.MVector(1, 0, 0)
    Y = OpenMaya.MVector(0, 1, 0)
    Z = OpenMaya.MVector(0, 0, 1)

    def __init__(self, maya_node=""):
        self.MAYA_STR_OBJECT = maya_node
        self.MAYA_M_OBJECT = object_utils.get_m_obj(maya_node)
        self.MAYA_MFN_OBJECT = object_utils.get_mfn_obj(maya_node)
        self.MAYA_M_DAG_PATH = object_utils.get_m_dag_path(maya_node)
        self.OBJECT_NODE_TYPE = self.MAYA_MFN_OBJECT.typeName()
        super(Transform, self).__init__(self.MAYA_M_OBJECT)

    @property
    def m_object(self):
        return self.MAYA_M_OBJECT

    @property
    def mfn_object(self):
        return self.MAYA_MFN_OBJECT

    @property
    def mdag_object(self):
        return self.MAYA_M_DAG_PATH

    @property
    def node_type(self):
        return self.OBJECT_NODE_TYPE

    def scale_values(self, as_m_vector=False):
        """
        return the scale attribute values
        :return: <tuple> scale attribute values
        """
        double_ptr = object_utils.get_double_ptr()
        self.getScale(double_ptr)
        x = self.M_SCRIPT_UTIL.getDoubleArrayItem(double_ptr, 0)
        y = self.M_SCRIPT_UTIL.getDoubleArrayItem(double_ptr, 1)
        z = self.M_SCRIPT_UTIL.getDoubleArrayItem(double_ptr, 2)
        if not as_m_vector:
            return x, y, z,
        else:
            return OpenMaya.MVector([x, y, z])

    @staticmethod
    def get_translation_from_matrix(matrix):
        """
        gets the translation from the matrix.
        :return:
        """
        return matrix[12:15]

    def invert_translation(self):
        return self.getTranslation(self.OBJECT_SPACE) * self.inclusive_matrix()

    def translate_values(self, as_m_vector=False, world=False):
        """
        return the translate attribute values
        :return: <tuple> scale attribute values
        """
        m_vector = self.getTranslation(self.OBJECT_SPACE)
        if world:
            m_vector = OpenMaya.MVector(*self.get_world_translation_list())

        if not as_m_vector:
            x = round(m_vector.x, 4)
            y = round(m_vector.y, 4)
            z = round(m_vector.z, 4)
            return x, y, z,
        else:
            return m_vector

    def get_translation(self):
        return self.transformation().translation(self.OBJECT_SPACE)

    def get_translation_list(self):
        return [self.get_translation()[t] for t in range(3)]

    def get_world_translation_list(self):
        world_space = self.get_world_matrix()
        return world_space[12:15]

    def get_world_matrix(self):
        return self.matrix_values(world=True, flatten=True)

    def get_local_matrix(self):
        return self.matrix_values(world=False, flatten=True)

    def get_rotation_order_name(self, idx=0):
        return self.ROTATION_ORDER_NAMES[idx]

    def get_bounding_box(self):
        """
        gets the transformation BoundingBox values
        :return:
        """
        return self.MAYA_MFN_OBJECT.boundingBox()

    def bbox_center(self):
        """
        returns bounding box center.
        :return:
        """
        bbox = self.get_bounding_box()
        return bbox.center()

    def intersects(self, other_bbox):
        """
        check if the bounding box intersects with another.
        :return:
        """
        bbox = self.get_bounding_box()
        bbox.intersects(bbox)

    def rotate_values(self, world=False, as_m_vector=False):
        """
        return the rotate attribute values
        :return: <tuple> rotate attribute values
        """
        if not world:
            m_rotate = OpenMaya.MEulerRotation(self.OBJECT_SPACE)
        else:
            m_rotate = OpenMaya.MEulerRotation(self.WORLD_SPACE)
        self.getRotation(m_rotate)

        if not as_m_vector:
            x = round(m_rotate.x, 4)
            y = round(m_rotate.y, 4)
            z = round(m_rotate.z, 4)
            return x, y, z,
        else:
            return m_rotate

    def crash_maya(self):
        """
        deliberately crash Maya like this.
        :return: <None>
        """
        m_matrix_transform = self.transformation()
        m_matrix = m_matrix_transform.asMatrix()
        m_double = object_utils.get_double4_ptr()
        m_matrix.get(m_double)
        return None

    def crash_maya_1(self):
        """
        deliberately crash Maya by returning a list object of the euler rotation.
        :return: <None>
        """
        return list(self.euler_rotation())

    def matrix_values(self, world=False, flatten=False):
        """
        returns row column float items.
        :param world: <bool> return the matrix in world space.
        :param flatten: <bool> flatten the matrix and return row, column of tuple items.
        :return: <list> matrix.
        """
        if world:
            return self.matrix_list(self.inclusive_matrix(), flatten=flatten)
        else:
            # return row, column tuple items
            return self.matrix_list(self.matrix(), flatten=flatten)

    def world_transform_matrix(self):
        return OpenMaya.MTransformationMatrix(self.world_matrix())

    def world_matrix_list(self):
        """
        returns the world matrix
        :return: <list> world matrix values.
        """
        return self.matrix_list(self.inclusive_matrix(), flatten=True)

    def inclusive_matrix_list(self):
        return self.matrix_list(self.inclusive_matrix(), flatten=True)

    def inclusive_matrix(self):
        return self.MAYA_M_DAG_PATH.inclusiveMatrix()

    def world_matrix(self):
        return self.inclusive_matrix_list()

    def matrix(self):
        return self.transformation().asMatrix()

    def inverse_matrix(self):
        return self.transformation().asMatrixInverse()

    def world_to_local_matrix(self):
        return self.world_matrix_from_plug() * self.inverse_matrix()

    def world_matrix_from_plug(self):
        """
        grabs the world matrix from plug.
        :return: <OpenMaya.MMatrix> world matrix object.
        """
        return self.world_matrix_attr_plug()

    def world_matrix_attr_index(self):
        """
        returns an worldMatrix attribute MObject
        :return: <OpenMaya.MObject> attribute object. <bool> False for nothing found.
        """
        for a_idx in xrange(self.attr_count()):
            attr_obj = self.MAYA_MFN_OBJECT.attribute(a_idx)
            if not attr_obj.isNull():
                a_plug = OpenMaya.MPlug(self.MAYA_M_OBJECT, attr_obj)
                if 'worldMatrix' in a_plug.name():
                    return a_idx
        return False

    def get_plug(self, attr_name=""):
        """
        get this plug
        :return:
        """
        return self.MAYA_MFN_OBJECT.findPlug(attr_name)

    def world_matrix_attr_plug(self):
        """
        returns an worldMatrix attribute MObject
        :return: <OpenMaya.MObject> attribute object. <bool> False for nothing found.
        """
        for a_idx in xrange(self.attr_count()):
            attr_obj = self.MAYA_MFN_OBJECT.attribute(a_idx)
            if not attr_obj.isNull():
                a_plug = OpenMaya.MPlug(self.MAYA_M_OBJECT, attr_obj)
                if 'worldMatrix' in a_plug.name():
                    return a_plug
        return False

    def world_matrix_attr_obj(self):
        """
        returns an worldMatrix attribute MObject
        :return: <OpenMaya.MObject> attribute object. <bool> False for nothing found.
        """
        for a_idx in xrange(self.attr_count()):
            attr_obj = self.MAYA_MFN_OBJECT.attribute(a_idx)
            if not attr_obj.isNull():
                a_plug = OpenMaya.MPlug(self.MAYA_M_OBJECT, attr_obj)
                if 'worldMatrix' in a_plug.name():
                    return attr_obj
        return False

    def attr_count(self):
        return self.MAYA_MFN_OBJECT.attributeCount()

    def m_attr_plug(self, attr):
        return OpenMaya.MPlug(self.MAYA_M_OBJECT, attr)

    def print_4x4_local_matrix(self):
        for m in [self.local_matrix[i:i + 4] for i in range(0, len(self.local_matrix), 4)]:
            print m

    def print_4x4_world_matrix(self):
        for m in [self.world_matrix[i:i + 4] for i in range(0, len(self.world_matrix), 4)]:
            print m

    @property
    def wmatrix(self):
        return self.get_world_matrix()

    @property
    def local_matrix(self):
        return self.get_local_matrix()

    @property
    def world_translation(self):
        return self.get_world_translation_list()

    @staticmethod
    def m_attr_index(m_plug, idx):
        return m_plug.elementByLogicalIndex(idx)

    @staticmethod
    def matrix_data_fn(m_plug):
        return OpenMaya.MFnMatrixData(m_plug.asMObject())

    def get_transformatrion_matrix(self, matrix=None):
        if matrix:
            return OpenMaya.MTransformationMatrix(matrix)
        else:
            return self.transformation()

    def rotation_order_name(self):
        """
        returns kInvalid
                kXYZ
                kYZX
                kZXY
                kXZY
                kYXZ
                kZYX
                kLast
        :param matrix: <OpenMaya.MMatrix>
        :return: <OpenMaya.MTransformationMatrix.RotationOrder>
        """
        return self.get_rotation_order_name(self.rotationOrder())

    def matrix_list(self, m_matrix=OpenMaya.MMatrix, flatten=False):
        """
        returns the OpenMaya.MMatrix as a tuple
        :param m_matrix: <OpenMaya.MMatrix>
        :param flatten: <bool> flatten the tuples.
        :return: <tuple> matrix vector transforms.
        """
        m_tuples = tuple(
                tuple(
                    self.M_SCRIPT_UTIL.getDoubleArrayItem(
                        m_matrix[r], c
                    ) for c in xrange(4)
                ) for r in xrange(4)
            )
        if flatten:
            return tuple([e for tupl in m_tuples for e in tupl])
        else:
            return m_tuples

    def set_matrix_row(self, matrix, vector, row):
        """
        builds a matrix from vector and row provided.
        :param matrix:
        :param vector:
        :param row:
        :return:
        """
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[row], 0, vector.x)
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[row], 1, vector.y)
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[row], 2, vector.z)

    def set_matrix_cell(self, matrix, row, column, value):
        """
        sets a matrix cell value
        :param matrix:
        :param row:
        :param column:
        :param value:
        :return:
        """
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[row], column, value)

    def build_matrix(self, matrix_list=[]):
        """
        builds a matrix from list.
        :param matrix_list:
        :return: <OpenMaya.MMatrix> built matrix with values from list provided.
        """
        matrix = OpenMaya.MMatrix()
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[0], 0, matrix_list[0][0])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[0], 1, matrix_list[0][1])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[0], 2, matrix_list[0][2])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[1], 0, matrix_list[1][0])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[1], 1, matrix_list[1][1])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[1], 2, matrix_list[1][2])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[2], 0, matrix_list[2][0])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[2], 1, matrix_list[2][1])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[2], 2, matrix_list[2][2])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[3], 0, matrix_list[3][0])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[3], 1, matrix_list[3][1])
        self.M_SCRIPT_UTIL.setDoubleArray(matrix[3], 2, matrix_list[3][2])
        return matrix

    def matrix_from_list(self, mat_list=[]):
        return object_utils.ScriptUtil(mat_list, matrix_from_list=True).matrix_from_list()

    def set_relative_rotation_x(self, degree=0):
        self.rotateBy(self.quaternion_rotation(degree, axis='X'))

    def set_relative_rotation_y(self, degree=0):
        self.rotateBy(self.quaternion_rotation(degree, axis='Y'))

    def set_relative_rotation_z(self, degree=0):
        self.rotateBy(self.quaternion_rotation(degree, axis='Z'))

    def slerp(self, q_rotation=None, identity=True):
        """
        interpolating between the two rotations by using Spherical Linear Interpolation
        """
        if identity:
            return OpenMaya.MQuaternion.slerp(OpenMaya.MQuaternion.kIdentity, q_rotation, 0.1)

    def get_quaternion_rotation(self, normalize=True):
        if not normalize:
            return self.transformation().rotation()
        else:
            return self.transformation().rotation().normalizeIt()

    def quaternion_list(self):
        return [self.get_quaternion_rotation()[x] for x in range(4)]

    def reset_rotation(self):
        self.setRotation(self.get_quaternion_rotation(), self.OBJECT_SPACE)

    def set_rotation(self, q_list=[]):
        self.setRotationComponents(q_list, self.OBJECT_SPACE, asQuaternion=True)

    def set_rotation_identity(self):
        self.setRotation(OpenMaya.MQuaternion.kIdentity, self.OBJECT_SPACE)

    def set_euler_rotation_order(self, rotation_order="kXYZ"):
        return self.euler_rotation().reorderIt(eval('OpenMaya.MTransformationMatrix.{}'.format(rotation_order)))

    def get_euler_rotation(self):
        return self.transformation().rotation().asEulerRotation()

    def euler_rotation_as_list(self):
        return [self.get_euler_rotation()[r] for r in range(3)]

    def euler_rotation(self, as_list=False):
        if not as_list:
            return self.get_euler_rotation()
        else:
            return self.euler_rotation_as_list()

    @staticmethod
    def convert_euler_to_angle(m_euler):
        return [m_euler[r] for r in range(3)]

    def get_euler_angles(self):
        return [math.degrees(angle) for angle in self.euler_rotation(as_list=True)]

    def get_euler_radians(self):
        return [math.radians(angle) for angle in self.euler_rotation(as_list=True)]

    def get_world_scale(self):
        return map(self.world_scale_double_ptr.double_array_item, range(3))

    def get_object_scale(self):
        return map(self.object_scale_double_ptr.double_array_item, range(3))

    @property
    def object_scale_double_ptr(self):
        """
        get the double pointer script util class instance.
        :return: <MScriptUtil> scale attribute double pointer
        """
        return object_utils.ScriptUtil(as_double_ptr=True,
                                       function=(self.transformation().getScale, self.OBJECT_SPACE))

    @property
    def world_scale_double_ptr(self):
        """
        get the double pointer script util class instance.
        :return: <MScriptUtil> scale attribute double pointer
        """
        return object_utils.ScriptUtil(as_double_ptr=True,
                                       function=(self.transformation().getScale, self.WORLD_SPACE))

    @staticmethod
    def mirror_matrix(matrix_list, across='YZ', behaviour=False,
                      invert_rotate_x=False, invert_rotate_y=False, invert_rotate_z=False):
        """
        builds the mirror matrix
        :param matrix_list: <list> matrix transform list.
        :param across: <str> the planar axis to mirror across.
        :param behaviour: <bool> mirrors the behaviour of the transform object.
        :param invert_rotate_x: <bool> invert rotateX
        :param invert_rotate_y: <bool> invert rotateY
        :param invert_rotate_z: <bool> invert rotateZ
        :return: <bool> True for success. <bool> False for failure.
        """
        if isinstance(matrix_list, tuple):
            matrix_list = list(matrix_list)

        # invert rotation columns,
        rx = [n * -1 for n in matrix_list[0:9:4]]
        ry = [n * -1 for n in matrix_list[1:10:4]]
        rz = [n * -1 for n in matrix_list[2:11:4]]

        # invert translation row,
        t = [n * -1 for n in matrix_list[12:15]]

        # set matrix based on given plane, and whether to include behaviour or not.
        if across is 'XY':
            matrix_list[14] = t[2]  # set inverse of the Z translation

            # set inverse of all rotation columns but for the one we've set translate to.
            if behaviour:
                matrix_list[0:9:4] = rx
                matrix_list[1:10:4] = ry

        elif across is 'YZ':
            matrix_list[12] = t[0]  # set inverse of the X translation

            if behaviour:
                matrix_list[1:10:4] = ry
                matrix_list[2:11:4] = rz
        else:
            matrix_list[13] = t[1]  # set inverse of the Y translation

            if behaviour:
                matrix_list[0:9:4] = rx
                matrix_list[2:11:4] = rz

        if invert_rotate_x:
            matrix_list[0:9:4] = rx

        if invert_rotate_y:
            matrix_list[1:10:4] = ry

        if invert_rotate_z:
            matrix_list[2:11:4] = rz
        return matrix_list

    def mirror_euler_rotation(self, m_euler=None, mirror_x=False, mirror_y=False, mirror_z=False):
        """
        mirror euler rotations
        :param m_euler: <OpenMaya.MEuler>
        :param mirror_x: <bool> mirrors rotation x axis
        :param mirror_y: <bool> mirrors rotation y axis
        :param mirror_z: <bool> mirrors rotation z axis
        """
        angles = self.get_euler_angles(m_euler=m_euler)
        if mirror_x:
            angles[0] *= -1
        if mirror_y:
            angles[1] *= -1
        if mirror_z:
            angles[2] *= -1
        return angles

    def mirror_world_matrix(self):
        """
        mirrors world matrix.
        :return: <list> mirrored world matrix list matrix values.
        """
        return self.mirror_matrix(self.matrix_values(world=True, flatten=True))

    def mirror_rotation_matrix(self):
        # world_matrix = self.world_matrix_list()
        # mirror_matrix = self.mirror_matrix(world_matrix)
        m_xform = OpenMaya.MTransformationMatrix(object_utils.ScriptUtil().matrix_from_list(self.inclusive_matrix_list()))
        xform_euler = m_xform.rotation().asEulerRotation()
        euler_angles = self.convert_euler_to_angle(xform_euler)

        # mirror axis Y
        euler_angles[1] *= -1
        # mirror axis Z
        euler_angles[2] *= -1

        quat = OpenMaya.MQuaternion()
        quat += self.quaternion_rotation(euler_angles[0], 'X')
        quat += self.quaternion_rotation(euler_angles[0], 'Y')
        quat += self.quaternion_rotation(euler_angles[0], 'Z')
        return quat.asEulerRotation().asMatrix()

        # convert the angles back to eulers
    def print_decomposed_matrix(self):
        print('[Translation] :: {}'.format(self.get_translation_list()))
        print('[Rotation] :: {}'.format(self.get_euler_angles()))
        print('[Scale] :: {}'.format(self.get_world_scale()))

    @staticmethod
    def get_matrix_rotations(matrix_list=None):
        """
        returns the rotational values in the matrix list provided.
        :return:
        """
        rx = matrix_list[0:9:4]
        ry = matrix_list[1:10:4]
        rz = matrix_list[2:11:4]
        return rx, ry, rz

    def quaternion_rotation(self, degree=0, axis='Y'):
        if axis == 'X':
            return OpenMaya.MQuaternion(math.radians(degree), self.X)
        if axis == 'Y':
            return OpenMaya.MQuaternion(math.radians(degree), self.Y)
        if axis == 'Z':
            return OpenMaya.MQuaternion(math.radians(degree), self.Z)

    def rotate_by_quaternion(self, quat):
        """
        rotate by quaternion.
        :param quat: <OpenMaya,MQuaternion>
        :return: <OpenMaya.MStatus>
        """
        return self.rotateByQuaternion(quat.x, quat.y, quat.z, quat.w, OpenMaya.MSpace.kPreTransform)

    def get_bounding_box_center(self):
        """
        returns the center of the boundingBox from the object given.
        :return: <tuple> center transform object information.
        """
        bb_min = cmds.getAttr('{}.boundingBoxMin'.format(self.MAYA_STR_OBJECT))[0]
        bb_max = cmds.getAttr('{}.boundingBoxMax'.format(self.MAYA_STR_OBJECT))[0]
        return bb_max[0] / 2 + bb_min[0] / 2, bb_max[1] / 2 + bb_min[1] / 2, bb_max[2] / 2 + bb_min[2] / 2,


def mirror_object(control_name="", mirror_obj_name="", invert_rotate=False, keep_rotation=False):
    """
    mirrors the selected object. If mirror object is not supplied, then mirror the supplied object directly.
    :param control_name: <str> controller object to get transformational values frOpenMaya.
    :param mirror_obj_name: <str> the object to receive mirror information.
    :param invert_rotate: <bool> invert the rotation values.
    :param keep_rotation: <bool> does not change the orientation of the transform object being mirrored.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not control_name:
        control_name = object_utils.get_selected_node(single=True)
    if not control_name:
        return False

    # mirror the world matrix
    c_transform = Transform(control_name)
    w_matrix = c_transform.get_world_matrix()
    mir_matrix = c_transform.mirror_matrix(w_matrix)
    rotation_values = cmds.xform(control_name, ro=1, q=1)
    if invert_rotate:
        # mirror rotate y
        rotation_values[1] *= -1

        # mirror rotate z
        rotation_values[2] *= -1

    elif keep_rotation:
        # mirror rotate x
        rotation_values[2] *= -1

    if not mirror_obj_name:
        cmds.xform(control_name, m=mir_matrix, ws=1)
        cmds.xform(control_name, ro=rotation_values)
    else:
        cmds.xform(mirror_obj_name, m=mir_matrix, ws=1)
        cmds.xform(mirror_obj_name, ro=rotation_values)
    return True
