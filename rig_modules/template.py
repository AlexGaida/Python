"""
This is a sample module for adding a singleton joint.
"""
# import maya modules
from maya import cmds

# import standard modules
import json

# import local modules
from maya_utils import object_utils

# define module variables
class_name = "Template"


class TemplateModule(object):
    class_name = class_name
    """
    publish_attributes:
        attributes to be saved to a build dictionary.
    attribute_q_types:
        create line edit fields.
    """
    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",
                          "name": "",
                          "moduleType": "",
    }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo", "constrainTo"],
                            'label': ["moduleType"],
    }

    def __init__(self, name="", prefix_name=""):
        self.name = name
        self.prefix_name = prefix_name

        # publish attributes
        self.PUBLISH_ATTRIBUTES["moduleType"] = self.class_name

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

    def create(self):
        """
        the utility method for creating a thing.
        :return:
        """
        pass

    def finish(self):
        """
        finalize the module setup.
        :return:
        """
        pass

    def remove(self):
        """
        removes the module setup.
        :return:
        """
        pass

    def update(self, *args):
        """
        updates the module
        :return:
        """
        pass
