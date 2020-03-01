"""
Creating and reading file objects, as well as manipulating the maya files.
"""
# import standard modules
import sys
import os
import xml.etree.cElementTree as ET
import json

# import local modules
from deformers import deform_utils

# import maya modules
from maya import cmds


def is_file(file_name):
    """
    checks if the file name is valid.
    :param file_name: <str> check this file name for validity.
    :return: <bool> True for success. <bool> False for failure.
    """
    return os.path.isfile(file_name)


def is_dir(file_name):
    """
    checks if the directory name is valid.
    :param file_name: <str> check this directory name for validity.
    :return: <bool> True for success. <bool> False for failure.
    """
    return os.path.isdir(file_name)


def open_current_file():
    """
    Opens the current maya scene file.
    :return: <bool> True for success.
    """
    cmds.file(cmds.file(q=1, loc=1), o=1, f=1)
    return True


class JSONSerializer(json):
    READ_DATA = {}
    FILE_NAME = ""
    INCOMING_DATA = {}

    def __init__(self, file_name="", data={}):
        super(JSONSerializer, self).__init__()
        self._get_data(data)
        self._get_file_name(file_name)

    def _get_file_name(self, file_name):
        """
        checks which incoming file name to use.
        :param file_name: <str> the incoming file name to check.
        :return: <str> file name.
        """
        if not file_name:
            return self.FILE_NAME
        else:
            self._update_file_name_variable(file_name)
            return file_name

    def _get_data(self, data):
        """
        checks which incoming data to use.
        :param data: <dict> the incoming data.
        :return: <dict> data.
        """
        if not data:
            return self.INCOMING_DATA
        else:
            self._update_data_variable(data)
            return data

    def _update_file_name_variable(self, file_name):
        """
        updates the file name class variable.
        :return: <bool> True for success.
        """
        self.FILE_NAME = file_name
        return self.FILE_NAME == file_name

    def _update_data_variable(self, data):
        """
        updates the data class variable.
        :param data: <dict> the data object to store.
        :return: <bool> True for success.
        """
        self.INCOMING_DATA = data
        return self.INCOMING_DATA == data

    def write(self, file_name="", data={}):
        """
        write the JSON data.
        :param file_name: <str> the file name string to write files to.
        :param data: <dict> the data dictionary to write.
        :return: <bool> True for success. <bool> False for failure.
        """
        with open(self._get_file_name(file_name), "w") as write_file:
            self.dump(self._get_data(data), write_file, indent=4, sort_keys=True)

    def read(self, file_name=""):
        """
        write the JSON data.
        :param file_name: <str> the file name string to write files to.
        :return: <bool> True for success. <bool> False for failure.
        """
        with open(self._get_file_name(file_name), "r") as read_file:
            return self.loads(read_file)

    @property
    def read_data(self):
        return self.read()

    @property
    def file_name(self):
        return self.FILE_NAME

    @property
    def is_file_valid(self):
        return is_file(self.FILE_NAME)

    @property
    def is_data_valid(self):
        return isinstance(self.DATA, dict)

    @property
    def has_data(self):
        return bool(self.DATA)


class XMLSerializer:
    def __init__(self):
        self.READ_DATA = {}
        self.xml_data = None

    def interpret_dictionary_data(self, dictionary_data=None):
        """
        re-interpret the dictionary data as XML element trees.
        :return: <xml.Element> data.
        """
        if not isinstance(dictionary_data, dict):
            raise ValueError("[InterpretDictionaryData] :: Must have a dictionary type as input parameter.")

        self.xml_data = ET.Element("DataInformation")
        items = ET.SubElement(self.xml_data, 'Data')

        for k_item, k_value in dictionary_data.items():
            item = ET.SubElement(items, k_item)
            if not isinstance(k_value, dict):
                ET.SubElement(item, k_value)
            else:
                for k_name, v_items in k_value.items():
                    array_key = ET.SubElement(item, k_name)
                    if isinstance(v_items, str):
                        ET.SubElement(array_key, v_items)
                    elif isinstance(v_items, (tuple, list)):
                        for it_name in v_items:
                            ET.SubElement(array_key, str(it_name))
                    elif isinstance(v_items, dict):
                        for it_name, it_val in v_items.items():
                            it_elem = ET.SubElement(array_key, str(it_name))
                            ET.SubElement(it_elem, str(it_val))
        return ET.dump(self.xml_data)

    def write(self, file_name, dictionary_data):
        """
        write the XML data as string data.
        :return: <bool> True for success.
        """
        # collect the data
        self.interpret_dictionary_data(dictionary_data)
        tree = ET.ElementTree(self.xml_data)
        tree.write(file_name)
        return True

    def read(self, file_name):
        """
        read the XML data file
        :return: <data> information.
        """
        tree = ET.parse(file_name)
        root = tree.getroot()

        for elem in root:
            for sub_elem in elem:
                self.update_read_data(sub_elem.attrib, sub_elem.text)

    def update_read_data(self, key_name, value):
        """
        updates the read dictionary data.
        :param key_name:
        :param value:
        :return:
        """
        if key_name not in self.READ_DATA:
            self.READ_DATA[key_name] = value
