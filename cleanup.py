from maya import cmds


from maya_utils import object_utils


functions = ['normalize_skin_weights',
             'zero_controls']


def normalize_skin_weights():
    for skin_node in cmds.ls(type='skinCluster'):
        cmds.skinCluster(skin_node, e=1, fnw=1)
    return True


def zero_controls():
    object_utils.zero_all_controllers()
    return True


def run_cleanup_functions():
    for clean_func in functions:
        eval(clean_func)()
        return True
