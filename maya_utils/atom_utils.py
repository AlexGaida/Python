# import maya modules
from maya import cmds
from maya import mel


def import_atom(atom_file_name="", atom_file_path_name=""):
    mel.eval("file -import -type \"atomImport\" -ra true -namespace \"{}\" -options \";;targetTime=1;srcTime=1:55;dstTime=1:55;option=scaleInsert;match=hierarchy;;selected=selectedOnly;search=;replace=;prefix=;suffix=;mapFile=D:/Work/Maya/RnD/data/;\" \"{}\"".format(atom_file_name, atom_file_path_name))


def export_atom():
    mel.eval("file -force -options"
    "\"precision=8;statics=1;baked=1;sdk=0;constraint=0;animLayers=0;selected=selectedOnly;whichRange=1;range=1:10;hierarchy=none;controlPoints=0;useChannelBox=1;options=keys;copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 0\" "
    "-ch 1 -typ "\"atomExport\" -es "
    "D:/Work/Maya/RnD/testexport.atom")
    return True
