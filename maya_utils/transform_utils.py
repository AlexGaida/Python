"""
Transform module for finding, creating and setting attributes
"""

# import maya modules
from maya import OpenMaya as om

# import local modules
import object_utils

# define global variables
__version__ = "1.0.0"


class Transform(om.MFnTransform):
    MAYA_STR_OBJECT = None
    M_SCRIPT_UTIL = om.MScriptUtil()

    WORLD_SPACE = om.MSpace.kWorld
    OBJECT_SPACE = om.MSpace.kObject

    ROTATE_ORDER_XYZ = om.MTransformationMatrix.kXYZ
    ROTATE_ORDER_YZX = om.MTransformationMatrix.kYZX
    ROTATE_ORDER_ZXY = om.MTransformationMatrix.kZXY
    ROTATE_ORDER_YXZ = om.MTransformationMatrix.kYXZ
    ROTATE_ORDER_ZYX = om.MTransformationMatrix.kZYX
    ROTATE_ORDER_INVALID = om.MTransformationMatrix.kInvalid

    def __init__(self, maya_node=""):
        self.MAYA_STR_OBJECT = maya_node
        self.MAYA_M_OBJECT = object_utils.get_m_obj(maya_node)
        self.MAYA_MFN_OBJECT = object_utils.get_mfn_obj(maya_node)
        self.MAYA_M_DAG_PATH = object_utils.get_m_dag_path(maya_node)
        self.OBJECT_NODE_TYPE = self.MAYA_MFN_OBJECT.typeName()
        super(Transform, self).__init__(self.MAYA_M_OBJECT)

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
            return om.MVector([x, y, z])

    def translate_values(self, world=False, as_m_vector=False):
        """
        return the translate attribute values
        :return: <tuple> scale attribute values
        """
        if not world:
            m_vector = self.getTranslation(self.OBJECT_SPACE)
        else:
            m_vector = self.getTranslation(self.WORLD_SPACE)
        if not as_m_vector:
            x = round(m_vector.x, 4)
            y = round(m_vector.y, 4)
            z = round(m_vector.z, 4)
            return x, y, z,
        else:
            return m_vector

    def rotate_values(self, world=False, as_m_vector=False):
        """
        return the rotate attribute values
        :return: <tuple> rotate attribute values
        """
        if not world:
            m_rotate = om.MEulerRotation(self.OBJECT_SPACE)
        else:
            m_rotate = om.MEulerRotation(self.WORLD_SPACE)
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

    def matrix_values(self, world=False, flatten=False):
        """
        returns row column float items.
        :param world: <bool> return the matrix in world space.
        :param flatten: <bool> flatten the returning list of tuple matrices.
        :return: <list> matrix.
        """
        m_matrix_transform = self.transformation()
        m_matrix = m_matrix_transform.asMatrix()

        print(self.matrix_list(m_matrix, flatten=flatten))

        if world:
            return self.matrix_list(m_matrix_transform.asMatrixInverse(), flatten=flatten)
        else:
            # return row, column tuple items
            return self.matrix_list(m_matrix, flatten=flatten)

    def world_matrix(self):
        """
        returns the world matrix
        :return: <list> world matrix values.
        """
        matrix = self.MAYA_M_DAG_PATH.inclusiveMatrix()
        return self.matrix_list(matrix, flatten=True)

    def matrix_list(self, m_matrix=om.MMatrix, flatten=False):
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
        :return: <om.MMatrix> built matrix with values from list provided.
        """
        matrix = om.MMatrix()
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

    def mirror_world_matrix(self):
        """
        mirrors world matrix.
        :return: <list> mirrored world matrix list matrix values.
        """
        w_matrix = self.world_matrix()
        return self.mirror_matrix(w_matrix)

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
