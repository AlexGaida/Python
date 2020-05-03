"""
singleton method to creating a single joint in the scene.
"""
# import maya modules
from maya import cmds
from rig_modules import template

class_name = "PreBuild"


class PreBuild(template.TemplateModule):
    class_name = class_name
    PUBLISH_ATTRIBUTES = {
        "name": "",
        "moduleType": ""
        "geoFile"
    }
    ATTRIBUTE_EDIT_TYPES = {
        'line-edit': ["name", "geoFile"],
        'label': ["moduleType"],
    }

    def __init__(self, name="", information={}):
        super(PreBuild, self).__init__(name=name, information=information)
        self.name = name
        self.information = information

    def create(self):
        """
        do nothing
        :return:
        """
        cmds.file(new=True, f=1)
        self.created = True

    def finish(self):
        """
        perform an action of creating a new file.
        :return:
        """
        if self.finished:
            return False

        # imports the geo file
        if 'geoFile' in self.information:
            cmds.file(self.information['geoFile'], i=1, f=1)

        print("[{}] :: finished.".format(class_name))
        self.finished = True

