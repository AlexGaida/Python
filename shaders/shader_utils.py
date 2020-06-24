# import maya modules
from maya import cmds


def check_components(components=()):
    """
    check if components exist.
    :param components: <tuple> check if these components exist.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not cmds.ls(components):
        return False
    return True


def create_shader(shader_type='lambert', shader_name='lambert_type'):
    """
    creates the shader type with name.
    :param shader_type:
    :param shader_name:
    :return:
    """
    if not cmds.objExists(shader_name):
        shader_name = cmds.shadingNode(shader_type, name=shader_name, asShader=True)
    return shader_name


def create_shader_set(shader_name=''):
    """
    creates the shader set and connects it.
    :param shader_name: <str> the shader name to create and connect.
    :return: <str> shader SG set name.
    """
    if not cmds.objExists(shader_name):
        return False

    # creates the shader sg
    shader_sg_name = '{}SG'.format(shader_name)
    if not cmds.objExists(shader_sg_name):
        shader_set = cmds.sets(name=shader_sg_name, empty=True, renderable=True, noSurfaceShader=True)
    return shader_set


def connect_shader_set(shader_name, shader_sg):
    """
    connects the shader name outColor to the shader set name.
    :param shader_name: shader name to connect from.
    :param shader_sg: shader SG set to connect to.
    :return: <bool> True for success.
    """
    out_attr = '{}.outColor'.format(shader_name)
    in_attr = '{}.surfaceShader'.format(shader_sg)
    if not cmds.isConnected(out_attr, in_attr):
        cmds.connectAttr(out_attr, in_attr)
    return True


def set_shader_color(shader_name='', color=(0, 0, 0)):
    """
    sets the shader color.
    :param shader_name: <str> the name of the shader to set the color attributes to.
    :param color: <tuple> array of 3 numbers.
    :return: <bool> True for success.
    """
    cmds.setAttr("{}.color".format(shader_name), *color, type='double3')
    return True


def add_lambert_shader(face_components=(), name="lambert"):
    """
    Adds a lambert shader to the face component
    :param face_components: <tuple> array of faces to add the lambert shader to.
    :param name: <str> the name of the shader to create.
    :return: <bool> True for success. <bool> False for failure.
    """
    if not check_components(face_components):
        return False
    shader_name = create_shader(shader_type='lambert', shader_name=name)
    shd_sg = create_shader_set(shader_name)
    set_shader_color(shader_name, color=(0, 0, 0))
    # connect the shader to the shader SG
    connect_shader_set(shader_name, shd_sg)
    for face in face_components:
        cmds.sets(face, e=True, forceElement=shd_sg)
    return True
