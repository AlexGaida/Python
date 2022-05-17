"""
module for managing constraint functions within Maya
"""
# import maya modules
from maya import cmds


def parent_constraint(source_obj, target_obj, maintain_offset=True):
    """
    create parent constraint.
    :param source_obj:
    :param target_obj:
    :param maintain_offset:
    :return:
    """
    return cmds.parentConstraint(source_obj, target_obj, mo=maintain_offset)[0]


def scale_constraint(source_obj, target_obj, maintain_offset=True):
    """
    create scale constraint.
    :param source_obj:
    :param target_obj:
    :param maintain_offset:
    :return:
    """
    return cmds.scaleConstraint(source_obj, target_obj, mo=maintain_offset)[0]


def point_constraint(source_obj, target_obj, maintain_offset=True):
    """
    create point constraint.
    :param source_obj:
    :param target_obj:
    :param maintain_offset:
    :return:
    """
    return cmds.pointConstraint(source_obj, target_obj, mo=maintain_offset)[0]


def orient_constraint(source_obj, target_obj, maintain_offset=True):
    """
    create orient constraint
    :param source_obj:
    :param target_obj:
    :param maintain_offset:
    :return:
    """
    return cmds.orientConstraint(source_obj, target_obj, mo=maintain_offset)[0]


def symmetry_constraint(source_obj, target_obj):
    """
    symmetry constraint
    :param source_obj:
    :param target_obj:
    :return:
    """
    symmetry_node = cmds.createNode('symmetryConstraint')

    # source attributes
    source_translate_attr = '{}.translate'.format(source_obj)
    source_rotate_attr = '{}.rotate'.format(source_obj)
    source_scale_attr = '{}.scale'.format(source_obj)
    source_parent_matrix_attr = '{}.parentMatrix[0]'.format(source_obj)
    source_world_matrix_attr = '{}.worldMatrix[0]'.format(source_obj)
    source_rotate_order_attr = '{}.rotateOrder'.format(source_obj)

    # target attributes
    target_translate_attr = '{}.translate'.format(target_obj)
    target_rotate_attr = '{}.rotate'.format(target_obj)
    target_scale_attr = '{}.scale'.format(target_obj)
    target_rotate_order_attr = '{}.rotateOrder'.format(target_obj)
    target_parent_inv_matrix_attr = '{}.parentInverseMatrix[0]'.format(target_obj)

    # symmetry node attributes
    sym_node_translate_attr = '{}.targetTranslate'.format(symmetry_node)
    sym_node_rotate_attr = '{}.targetRotate'.format(symmetry_node)
    sym_node_scale_attr = '{}.targetScale'.format(symmetry_node)
    sym_node_parent_matrix_attr = '{}.targetParentMatrix'.format(symmetry_node)
    sym_node_world_matrix_attr = '{}.targetWorldMatrix'.format(symmetry_node)
    sym_node_rotate_order_attr = '{}.targetRotateOrder'.format(symmetry_node)

    sym_node_cnst_translate_attr = '{}.constraintTranslate'.format(symmetry_node)
    sym_node_cnst_rotate_attr = '{}.constraintRotate'.format(symmetry_node)
    sym_node_cnst_scale_attr = '{}.constraintScale'.format(symmetry_node)
    sym_node_cnst_rotate_order_attr = '{}.constraintRotateOrder'.format(symmetry_node)
    sym_node_cnst_inverse_matrix_attr = '{}.constraintInverseParentWorldMatrix'.format(symmetry_node)

    # make connections from source
    cmds.connectAttr(source_translate_attr, sym_node_translate_attr)
    cmds.connectAttr(source_rotate_attr, sym_node_rotate_attr)
    cmds.connectAttr(source_scale_attr, sym_node_scale_attr)

    cmds.connectAttr(source_parent_matrix_attr, sym_node_parent_matrix_attr)
    cmds.connectAttr(source_world_matrix_attr, sym_node_world_matrix_attr)
    cmds.connectAttr(source_rotate_order_attr, sym_node_rotate_order_attr)

    # make connections to target
    cmds.connectAttr(target_parent_inv_matrix_attr, sym_node_cnst_inverse_matrix_attr)
    cmds.connectAttr(sym_node_cnst_translate_attr, target_translate_attr)
    cmds.connectAttr(sym_node_cnst_rotate_attr, target_rotate_attr)
    cmds.connectAttr(sym_node_cnst_scale_attr, target_scale_attr)
    cmds.connectAttr(sym_node_cnst_rotate_order_attr, target_rotate_order_attr)
    cmds.parent(symmetry_node, source_obj)

# ______________________________________________________________________________________________________________________
# constraint_utils.py
