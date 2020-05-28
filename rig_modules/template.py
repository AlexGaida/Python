"""
This is a sample module for adding a singleton joint.
"""
# import standard modules
import gc

# import custom modules
from maya_utils import object_utils
from rig_utils import joint_utils
from rig_utils import control_utils

# define module variables
class_name = "Template"


class TemplateModule(object):
    class_name = class_name
    positions = ()
    guide_joints = []
    finished_joints = ()
    information = {}
    created = False
    finished = False
    controller_data = {}
    built_groups = []

    """
    publish_attributes:
        attributes to be saved to another, build dictionary.
    attribute_q_types:
        create line edit fields.
    """
    PUBLISH_ATTRIBUTES = {"constrainTo": "",
                          "parentTo": "",
                          "name": "",
                          "moduleType": "",
                          "positions": ()
                          }

    ATTRIBUTE_EDIT_TYPES = {'line-edit': ["name", "parentTo", "constrainTo", "positions"],
                            'label': ["moduleType"]
                            }

    def __init__(self, name="", prefix_name="", information={}):
        self.name = name
        self.prefix_name = prefix_name
        self.information = information
        self.suffix_name = 'guide_jnt'

        # publish attributes
        self.PUBLISH_ATTRIBUTES["moduleType"] = self.class_name

    def created_decorator(self, func):
        print('created decorator called.')

        def wrapper(*args, **kwargs):
            called = False
            try:
                called = func(*args, **kwargs)
            except RuntimeError:
                self.created = False
            if called:
                self.created = True
        return wrapper

    def finished_decorator(self, func):
        print('finished decorator called.')

        def wrapper(*args, **kwargs):
            called = False
            if self.created and not self.finished:
                try:
                    called = func(*args, **kwargs)
                except AttributeError:
                    self.finished = False
                if called:
                    self.finished = True
        return wrapper

    def add_new_information(self, key_name, widget_type='line-edit', value=""):
        """
        Adds a new line edit to the dictionary attributes
        :return:
        """
        if key_name not in self.ATTRIBUTE_EDIT_TYPES[widget_type]:
            self.ATTRIBUTE_EDIT_TYPES[widget_type].append(key_name)
        if key_name not in self.PUBLISH_ATTRIBUTES:
            self.PUBLISH_ATTRIBUTES[key_name] = value

    def perform_connections(self):
        """
        performs the connections between the modules
        :return: <bool> True for success. <bool> False for failure.
        """
        if not self.information:
            return False

        # create connections to other nodes in the scene
        parent_to = self.information['parentTo']
        constrain_to = self.information['constrainTo']

        # we want to deliberately raise an error when the object is not found
        if constrain_to:
            if not object_utils.is_exists(constrain_to):
                ctrl_obj = control_utils.get_control_name(constrain_to)
                object_utils.do_parent_constraint(ctrl_obj, self.controller_data['controller'])
            else:
                object_utils.do_parent_constraint(constrain_to, self.controller_data['controller'])

        if parent_to:
            if not object_utils.is_exists(parent_to):
                ctrl_obj = control_utils.get_control_name(parent_to)
                object_utils.do_parent(self.controller_data['group_names'][-1], ctrl_obj)
            else:
                object_utils.do_parent(self.controller_data['group_names'][-1], parent_to)
        return True

    def update_information(self, dictionary):
        """
        updates the publush attributes dictionary
        :param dictionary: <dict> input dictionary
        :return:
        """
        self.PUBLISH_ATTRIBUTES.update(dictionary)

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
        pass

    def get_guide_positions(self):
        """
        gets the current positions of guide joints.
        :return: <tuple> array of translation values.
        """
        pass

    def replace_guides(self):
        """
        replaces the guide joints with the actual bound joints.
        :return: <tuple> bound joint array.
        """
        pass

    def if_guides_exist(self):
        """
        checking function to search the validity of guides in the scene.
        :return:
        """
        pass

    def select_guides(self):
        """
        select the guide joints
        :return:
        """
        pass

    def select_built_objects(self):
        """
        select the built objects
        :return:
        """
        pass

    def __del__(self):
        del self
        gc.collect()

