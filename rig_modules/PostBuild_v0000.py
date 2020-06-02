"""
singleton method to creating a single joint in the scene.
"""
# import standard modules
import imp

# import maya modules
from maya import cmds

# import utility modules
from maya_utils import file_utils

# import rig modules
from rig_modules import template

class_name = "PreBuild"


class PreBuild(template.TemplateModule):
    class_name = class_name
    PUBLISH_ATTRIBUTES = {
        "name": "",
        "moduleType": ""
    }
    ATTRIBUTE_EDIT_TYPES = {
        'line-edit': ["name"],
        'label': ["moduleType"],
    }

    def __init__(self, name="", information={}):
        super(PreBuild, self).__init__(name=name, information=information)
        self.name = name
        self.information = information
        self.post_build_file = ""

    def get_creature(self):
        return self.information["creature"]

    def get_creature_dir(self):
        return self.information["creature_directory"]

    def create(self):
        """
        do nothing
        :return:
        """
        self.post_build_file = file_utils.make_py_file(self.get_creature_dir(), self.get_creature())
        self.created = True

    def finish(self):
        """
        perform an action of creating a new file.
        :return:
        """
        if self.finished:
            return False

        # open and execute the file to finish building the character
        imp.load_source("creature_file", self.post_build_file)

        # imports the geo file
        if 'geoFile' in self.information:
            cmds.file(self.information['geoFile'], i=1, f=1)

        print("[{}] :: finished.".format(class_name))
        self.finished = True

