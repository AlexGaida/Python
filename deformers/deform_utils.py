from maya import cmds


def load_deformer_weights(file_name="", deformer_name=""):
    """
    loads the deformer weights
    :param file_name: <str>
    :param deformer_name: <str>
    :return: <bool> True for success.
    """
    cmds.deformerWeights(file_name, path=dir, deformer=deformer_name, im=1)
    return True


def save_deformer_skin_weights(skin_name="", directory_path_name=""):
    """
    saves the deformer skin weights.
    :param skin_name: <str>
    :param directory_path_name: <str> The directory path to save the skin weights to.
    :return: <bool> True for success.
    """
    cmds.deformerWeights(skin_name + '.skinWeights', path=directory_path_name, ex=1, deformer=skin_name)
    return True
