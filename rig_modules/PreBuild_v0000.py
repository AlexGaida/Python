"""
singleton method to creating a single joint in the scene.
"""
# import maya modules
from maya import cmds

# import local modules
from rig_utils import control_utils
from rig_utils import joint_utils

import template
reload(template)

class_name = "Singleton"


class Singleton(template.TemplateModule):

    def __init__(self, name=""):
        super(Singleton, self).__init__(name=name, prefix_name=prefix_name)
        self.name = name

    def create(self):
        """
        creates a joint controlled by one joint.
        :return:
        """
        cmds.file(o=1, f=1)
        return True

    def finish(self):
        """
        finish the construction of this module.
        :return:
        """
        print('New file opened.')

    def do_it(self):
        pass
