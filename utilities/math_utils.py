"""
Math utilities
"""
from maya.api import OpenMaya


def lerp_matrix(matrix_a, matrix_b, lerp_value, translation=True, rotation=True, scale=True, *args, **kwargs):
    """
    Lerp between 2 matrices. matrices are decoupled, lerped, then recoupled
    :param OpenMaya MMatrix matrix_a: first matrix
    :param OpenMaya MMatrix matrix_b: second matrix
    :param float lerp_value: lerp weight
    :param bool translation: option to return translation lerp
    :param bool rotation:  option to return rotation lerp
    :param bool scale: option to return scale lerp
    :return OpenMaya MMatrix: lerped matrix
    """

    a = OpenMaya.MMatrix(matrix_a)
    b = OpenMaya.MMatrix(matrix_b)

    a_translation, a_rotation, a_scale, a_shear = decompose_position_matrix(a)

    b_translation, b_rotation, b_scale, b_shear = decompose_position_matrix(b)

    lerp_translation = a_translation
    if translation:
        lerp_translation = lerp_vector(a_translation, b_translation, lerp_value)

    lerp_rotation = a_rotation
    if rotation:
        lerp_rotation = OpenMaya.MQuaternion.slerp(a_rotation, b_rotation, lerp_value)  # NOTE: rotation is SLERPed

    lerp_scale = a_scale
    if scale:
        lerp_scale = lerp_vector(a_scale, b_scale, lerp_value)

    # I am using a_shear as is because lerping the shear could cause issues. you want shear to be 0,0,0
    lerped_matrix = recompose_position_matrix(lerp_translation, lerp_rotation, lerp_scale, a_shear)

    return lerped_matrix


def lerp_vector(a, b, t):
    """
    lerp between 2 tuples
    :param tuple a: first vector
    :param tuple b: second vector
    :param float t: float value to lerp_vector to
    """
    av = OpenMaya.MVector(*a)
    bv = OpenMaya.MVector(*b)
    return (1 - t) * av + (t * bv)


def lerp(a, b, t):
    """
    lerp between 2 floats
    :param float a: first float
    :param float b: second float
    :param float t: lerp weight. value between 0.0 and 1.0. can be higher or lower to overshoot value
    :return:
    """
    return (1 - t) * a + (t * b)


def inverse_lerp(a, b, v):
    """
    Resolve the lerp weight
    :param a: first float
    :param b: second float
    :param v: value
    :return: lerp weight
    """
    return (v-a)/(b-a)


def decompose_position_matrix(om_matrix):
    """
    decompose a position matrix into translation, rotation, scale and shear
    :param om_matrix: OpenMaya MMatrix object
    :return: list[tuple,tuple,tuple,tuple]
    """
    om_transform = OpenMaya.MTransformationMatrix(om_matrix)
    translation = om_transform.translation(OpenMaya.MSpace.kWorld)
    rotation = om_transform.rotation(asQuaternion=True)
    scale = om_transform.scale(OpenMaya.MSpace.kWorld)
    shear = om_transform.shear(OpenMaya.MSpace.kTransform)

    return translation, rotation, scale, shear


def recompose_position_matrix(translation, rotation, scale, shear):
    """
    recompose a position matrix
    :param translation:
    :param rotation:
    :param scale:
    :param shear:
    :return: OpenMaya.MMatrix object
    """
    recomposed_position_transform = OpenMaya.MTransformationMatrix()
    recomposed_position_transform.setTranslation(translation, OpenMaya.MSpace.kWorld)
    recomposed_position_transform.setRotation(rotation)
    recomposed_position_transform.setScale(scale, OpenMaya.MSpace.kWorld)
    recomposed_position_transform.setShear(shear, OpenMaya.MSpace.kTransform)

    recomposed_position_matrix = recomposed_position_transform.asMatrix()
    return recomposed_position_matrix


def calculate_matrix_difference(matrix_a, matrix_b):
    """
    calculate the offset matrix
    :param matrix_a:
    :param matrix_b:
    :return: offset_matrix
    """
    offset_mmatrix = matrix_b * matrix_a.inverse()
    return offset_mmatrix