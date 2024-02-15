# import maya modules
from maya import cmds
try:
    from importlib import reload
except ModuleNotFoundError:
    pass
from maya_utils import file_utils
from maya_utils import animation_utils
from maya_utils import object_utils
from ui_tools import list_tool
# reloads
reload(file_utils)
# load the atom importer/ exporter
cmds.loadPlugin('atomImportExport', quiet=True)


def import_atom(atom_file_name=""):
    """imports the atom file
    :param atom_file_name: <str>
    :return: None
    """
    if not atom_file_name:
        directory_name = file_utils.temp_dir
        objects = object_utils.get_selected_node(single=False)
        for anim_obj_name in objects:
            atom_file_name = file_utils.posixpath.join(
                directory_name, anim_obj_name)
            atom_file_name += '.atom'
            if not file_utils.is_file(atom_file_name):
                continue
            base_name = file_utils.get_file_name_from_file_path(atom_file_name)
            namespace = file_utils.remove_file_ext(base_name)
            min_time, max_time = animation_utils.get_time_range()
            proj_path = cmds.workspace(rd=True, q=True)
            atom_import_options = (
                ";;"
                "targetTime=1;"
                "srcTime={min_time}:{max_time};"
                "dstTime={min_time}:{max_time};"
                "option=scaleInsert;"
                "match=hierarchy;"
                ";"
                "selected=selectedOnly"
                "search=;"
                "replace=;"
                "prefix=;"
                "suffix=;"
                "mapFile={proj_path}/data/;"
                "".format(min_time=min_time, max_time=max_time, proj_path=proj_path))
            print("Importing file: ", atom_file_name)
            cmds.file(atom_file_name, i=True, type="atomImport", renameAll=True,
                      namespace=namespace, options=atom_import_options)


def export_atom(atom_file_name=""):
    """exporting animation on a per-object basis by the atom
    :param atom_file_name: <str>
    :return: None
    """
    min_time, max_time = animation_utils.get_time_range()
    if not atom_file_name:
        directory_name = file_utils.temp_dir
        objects = object_utils.get_selected_node(single=False)
        for anim_obj_name in objects:
            file_name = file_utils.posixpath.join(
                directory_name, anim_obj_name)
            atom_export_options = (
                "precision=8;"
                "statics=1;"
                "baked=1;"
                "sdk=0;"
                "constraint=0;"
                "animLayers=0;"
                "selected=selectedOnly;"
                "whichRange=1;"
                "range={min_time}:{max_time};"
                "hierarchy=none;"
                "controlPoints=0;"
                "useChannelBox=1;"
                "options=keys;"
                "copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 0 "
                "".format(min_time=min_time, max_time=max_time))
            print("exporting file: {}".format(file_name))
            cmds.file(file_name, force=True, options=atom_export_options,
                      constructionHistory=True, typ="atomExport", exportSelected=True)
    return True
# __________________________________________________________________________________________________________________
# atom_utils.py
