"""
Creating and reading file objects, as well as manipulating the maya files.
"""
# import standard modules
import posixpath
import re
import os
import xml.etree.cElementTree as ET
import json

# import maya modules
from maya import cmds

# define local variables
# re_slash = re.compile(r'[^\\/]+|[\\/]')
re_slash = re.compile('(\\\\|/)')


def has_ext(file_name, ext_name=""):
    """
    check if the file name string has the extension name.
    :param file_name: <str> file name to check.
    :param ext_name: <str> check this extension string name.
    :return: <bool> True for yes. <bool> False for no.
    """
    name, ext = os.path.splitext(file_name)
    if ext_name and ext_name != ext:
        return False
    elif not ext:
        return False
    return True


def add_extension(file_name, ext_name=""):
    """
    add this extension name to the file name variable.
    :param file_name: <str> the file name to add the extension to.
    :param ext_name: <str> the extension string name to add to the file name.
    :return: <str> file name with extension string.
    """
    name, ext = os.path.splitext(file_name)
    return name + '.{}'.format(ext_name.strip('.'))


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


def split_file_ext(file_name):
    """
    splits the extension from the file name.
    :param file_name:
    :return:
    """
    return os.path.splitext(file_name)[1]


def split_file_name(file_name):
    """
    splits the name from the file name.
    :param file_name:
    :return:
    """
    return os.path.splitext(file_name)[0]


def get_file_splits(file_name):
    """
    split the current file string.
    :return: <tuple> array of file directory file names.
    """
    return tuple(filter(lambda x: x not in ('', '/', '\\'), re_slash.split(file_name)))


def get_this_directory():
    """
    return this directory path.
    :return:
    """
    return '/'.join(get_file_splits(__file__)[:-1])


def _parent_level(level):
    """
    inverts the integer.
    :param level:
    :return:
    """
    return -1 * xrange(level+1)[-1]


def get_this_directory_parent(level=0):
    """
    get the directory parent path from level.
    :return: <str> get the file path string.
    """
    return '/'.join(get_file_splits(__file__)[:_parent_level(level)])


def directory_name(file_name):
    """
    return the directory name from the file name.
    :param file_name:
    :return:
    """
    return os.path.dirname(file_name)


def controller_data_dir():
    """
    gets the relative path for the controller data folder directory.
    :return: <str> directory path name.
    """
    dir_name = get_this_directory_parent(level=2)
    return posixpath.join(dir_name, 'rig_utils', 'controller_data')


def list_files(file_name):
    """
    lists files in a file path given.
    :param file_name:
    :return: <tuple> array of available files.
    """
    if is_file(file_name):
        return tuple(os.listdir(directory_name(file_name)))
    return tuple(os.listdir(file_name))


def list_controller_files():
    """
    lists all the files in the controller directory
    :return: <tuple> array of available controller files.
    """
    return list_files(controller_data_dir())


def concatenate_path(*args):
    """
    concatenate the strings into one path.
    :param args:
    :return: <str> directory file path name.
    """
    return posixpath.join(*args)


class JSONSerializer:
    """
    json serializer data class in case we want to manipulate json data.
    """
    READ_DATA = {}
    FILE_NAME = ""
    INCOMING_DATA = {}
    EXT_NAME = "json"

    def __init__(self, file_name="", data={}):
        self._get_data(data)
        self._get_file_name(file_name)
        if not self.is_directory_valid:
            raise IOError('Invalid directory: {}'.format(self.FILE_NAME))

    def _get_file_name(self, file_name):
        """
        checks which incoming file name to use.
        :param file_name: <str> the incoming file name to check.
        :return: <str> file name.
        """
        if not file_name:
            return self.FILE_NAME
        else:
            if not has_ext(file_name, 'json'):
                file_name = add_extension(file_name, self.EXT_NAME)
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
            json.dump(self._get_data(data), write_file, indent=4, sort_keys=True)

    def read(self, file_name=""):
        """
        write the JSON data.
        :param file_name: <str> the file name string to write files to.
        :return: <bool> True for success. <bool> False for failure.
        """
        with open(self._get_file_name(file_name), "r") as read_file:
            return json.load(read_file)

    @property
    def read_data(self):
        return self.read()

    @property
    def file_name(self):
        return self.FILE_NAME

    @property
    def is_directory_valid(self):
        if has_ext(self.FILE_NAME):
            return is_dir(directory_name(self.FILE_NAME))
        return is_dir(self.FILE_NAME)

    @property
    def is_file_valid(self):
        return is_file(self.FILE_NAME)

    @property
    def is_data_valid(self):
        return isinstance(self.READ_DATA, dict)

    @property
    def has_data(self):
        return bool(self.READ_DATA)


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


def scanf(file_name, token):
    """
    returns scanf functionality using regex.
    :return: <regex>
    """
    if token == '%c':
        re_compiled = re.compile('.', re.DOTALL)
    elif token == '%5c':
        re_compiled = re.compile('.{5}')
    elif token == '%d':
        re_compiled = re.compile('[-+]?\d+')
    elif token in ('%e', '%E', '%f', '%g'):
        re_compiled = re.compile('[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')
    elif token == '%i':
        re_compiled = re.compile('[-+]?(0[xX][\dA-Fa-f]+|0[0-7]*|\d+)')
    elif token == '%o':
        re_compiled = re.compile('[-+]?[0-7]+')
    elif token == '%s':
        re_compiled = re.compile('\S+')
    elif token == '%u':
        re_compiled = re.compile('\d+')
    elif token in ('%x', '%X'):
        re_compiled = re.compile('[-+]?(0[xX])?[\dA-Fa-f]+')
    else:
        raise ValueError('[ScanF] :: No token found.')
    return re_compiled.findall(file_name)
