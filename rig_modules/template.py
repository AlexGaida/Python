"""
This is a sample module for adding a singleton joint.
"""
# import maya modules
from maya import cmds

# define module variables
class_name = "Template"


class TemplateModule(object):
    class_name = class_name
    positions = ()
    guide_joints = []
    information = {}
    created = False
    finished = False

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
                          "positions": ()
                          }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo", "constrainTo"],
                            'label': ["moduleType"]
                            }

    def __init__(self, name="", prefix_name="", information={}):
        self.name = name
        self.prefix_name = prefix_name
        self.information = information

        # publish attributes
        self.PUBLISH_ATTRIBUTES["moduleType"] = self.class_name

        # update class attributes with incoming information
        if information:
            self.PUBLISH_ATTRIBUTES.update(information)

    def created_decorator(self, func):
        print('created decorator called.')

        def wrapper(*args, **kwargs):
            called = func(*args, **kwargs)
            if called:
                self.created = True
        return wrapper

    def finished_decorator(self, func):
        print('finished decorator called.')

        def wrapper(*args, **kwargs):
            if self.created and not self.finished:
                called = func(*args, **kwargs)
                if called:
                    self.finished = True
        return wrapper

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
        self.created = True
        pass

    def finish(self):
        """
        finalize the module setup.
        :return:
        """
        self.finished = True
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

    def get_positions(self):
        """
        retrieves the position of guide joints.
        :return:
        """
        pass

    def create_guides(self):
        """
        creates the guide joints of this module.
        :return: <bool> True for success.
        """
        pass

    def set_guide_positions(self):
        """
        sets the positions
        :return: <bool> True for success.
        """
        if self.guide_joints and "positions" in self.information:
            for jnt, pos in zip(self.guide_joints, self.information["positions"]):
                cmds.xform(jnt, m=pos, ws=True)
            return True
        return False

    def replace_guides(self):
        """
        replaces the guide joints with the actual bound joints.
        :return: <tuple> bound joint array.
        """
        pass
