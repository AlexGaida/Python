"""
This is a sample module for adding a singleton joint.
"""
# import maya modules
from maya import cmds

# import standard modules
import json

# import local modules
from maya_utils import object_utils


class TemplateModule(object):
    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",}

    def __init__(self, name="", prefix_name=""):
        self.name = name
        self.prefix_name = prefix_name

    def create(self):
        """
        the utility method for creating a thing.
        :return:
        """
        pass

    def parent_to(self, destination):
        """
        utility method to parenting to.
        :param destination:
        :return:
        """
        pass

    def constrain_to(self, destination):
        """
        utility method to constrain the module to.
        :param destination:
        :return:
        """
        pass

    def constrain_from(self, source):
        """
        utility method to constrain the module from.
        :param source:
        :return:
        """
        pass

    def write_attributes_json(self):
        """
        writes the json information.
        :return:
        """
        pass

    def add_attribute(self):
        """
        we need to add attribute to this node so it stands out when saving the node settings.
        :return:
        """
        pass

    def finish(self):
        """
        finish the module setup.
        :return:
        """
        pass

    def do_it(self):
        self.create()
        self.finish()
        return True
