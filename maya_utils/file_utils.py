"""
Creating and reading file objects, as well as manipulating the maya files.
"""
#import standard modules
import sys
import os
import xml

# import local modules
from deformers import deform_utils

# import maya modules
from maya import cmds


def open_current_file():
    """
    Opens the current maya scene file.
    :return: <bool> True for success.
    """
    cmds.file(cmds.file(q=1, loc=1), o=1, f=1)
    return True


class XMLWeightsParser(xml.etree.ElementTree):
    DIRECTORY_FILE_NAME = ""
    DICTIONARY_DATA = {}

    def __init__(self, directory_file_name="", dictionary_data={}):
        self.DIRECTORY_FILE_NAME = directory_file_name
        self.DICTIONARY_DATA = dictionary_data
        self.xml_data = None

    def interpret_dictionary_data(self):
        """
        re-interpret the dictionary data as XML element trees.
        :return: <xml.Element> data.
        """
        self.xml_data = self.Element("skinCluster")
        items = self.subElement(self.xml_data, 'Data')

        for k_item, k_value in self.DICTIONARY_DATA.items():
            item = self.SubElement(items, k_item)
            item.set('name', k_item)
            item.text(str(k_value))

    def write(self):
        """
        write the XML data as string data.
        :return: <bool> True for success.
        """
        # collect the data
        self.interpret_dictionary_data()

        # write that data to a file
        xml_data = self.tostring(self.xml_data)
        with open(self.DIRECTORY_FILE_NAME, "w") as xml_file:
            xml_file.write(xml_data)
        return True

    def parse(self):
        """
        "Reads" the xml file.
        :return: <dict> weight data.
        """
        root = xml.etree.ElementTree.parse(self.DIRECTORY_FILE_NAME).getroot()
        dict_data = {}
        for a_type in root.findall('weights'):
            joints = a_type.get('joints')
            mesh_shape = a_type.get('mesh')
            deformer_name = a_type.get('deformer')

            print('[Joints] :: {}'.format(joints))
            print('[MeshShape] :: {}'.format(mesh_shape))
            print('[DeformerName] :: {}'.format(deformer_name))

