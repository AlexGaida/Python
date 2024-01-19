"""
Creating and reading file objects, as well as manipulating the maya files.
"""
# import standard modules
import posixpath
import re
import os
import xml.etree.cElementTree as ET
import json
import glob
import ast
import shutil
import pickle

# import maya modules
from maya import cmds

# define local variables
# re_slash = re.compile(r'[^\\/]+|[\\/]')
re_slash = re.compile('(\\\\|/)')


def read_json_file(json_file_name):
    """
    reads the json file name.
    :param json_file_name: <str> reads the json file name
    :return: <dict> json file contents
    """
    with open(json_file_name, 'r') as f:
      json_file_contents = json.load(f)
    return json_file_contents


def remove_file(file_name):
    """
    removes this file from disk.
    :param file_name: <str> file path name.
    :return: <bool> True for success.
    :raises: <OSError> invalid file path.
    """
    os.unlink(file_name)
    return True


def make_py_file(dir_name, file_name):
    """
    create python file.
    :param dir_name:
    :param file_name:
    :return:
    """
    if ".py" not in file_name:
        file_name += ".py"
    file_path = concatenate_path(dir_name, file_name)
    if not is_file(file_path):
        f_ptr = open(file_path, 'w')
        f_ptr.close()
    return file_path


def copy_file(src_file, dst_file):
    return shutil.copyfile(src_file, dst_file)


def remove_directory(dir_name):
    """
    removes directory from path.
    :param dir_name: <str> directory name.
    :return: <bool> True for success.
    :raises: <OSError> invalid directory path.
    """
    os.rmdir(dir_name)
    return True


def get_files(path_name, file_ext='json'):
    """
    get the list of files in the path name
    :param path_name: <str> file path name to search.
    :param file_ext: <str> file extension to save.
    :return: <list> array of files found.
    """
    return glob.glob(path_name + '/*{}'.format(file_ext))


def get_directories(path_name, full_path=False):
    """
    get directories found in this path name.
    :param path_name: <str> use this path to get the files from.
    :param full_path: <bool> returns the full path of the directory path.
    :return: <tuple> files found.
    """
    files = tuple(glob.glob(path_name + '/*'))
    if full_path:
        directories = [f for f in files if os.path.isdir(f)]
        return directories
    else:
        directories = tuple(map(lambda x: os.path.split(x)[-1] if os.path.isdir(x) else None, files))
        directories = filter(None, directories)
        return directories


def build_dir(dir_name):
    """
    creates the directory path.
    :param dir_name: <str> directory name to create.
    :return: <str> directory name is successful. <bool> False if invalid directory path is given.
    """
    if is_file(dir_name):
        return False
    if not is_dir(dir_name):
        os.mkdir(dir_name)
    return dir_name


def build_directory(dir_name):
    """
    build an entire directory.
    :param dir_name:
    :return:
    """
    if is_file(dir_name):
        return False
    if not is_dir(dir_name):
        os.makedirs(dir_name)
    return dir_name


def get_path(*args):
    """
    construct a path from arguments provided.
    :param args: <tuple> array of arguments to concatenate.
    :return: <str> path
    """
    return posixpath.join(*args)


def get_maya_workspace_dir():
    """
    get the current working directory path for the maya project
    :return: <str> path
    """
    maya_workspace_dir = cmds.workspace(dir=True, q=1)
    return maya_workspace_dir


def get_maya_workspace_data_dir():
    """
    returns the data directory in the workspace directory.
    :return: <str> data workspace directory.
    """
    data_dir = get_maya_workspace_dir()
    if 'data' not in data_dir:
        data_dir = concatenate_path(get_maya_workspace_dir(), 'data')
    build_dir(data_dir)
    return data_dir


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


def current_file():
    """
    get the current file.
    :return:
    """
    return cmds.file(q=1, loc=1)


def current_file_parent(level=1):
    """
    get the directory parent path from level.
    :return: <str> get the file path string.
    :param level: <int> the path level to return.
    """
    if level == 0:
        raise IOError("[GetThisDirectoryParent] :: This cannot equal to zero.")
    return '/'.join(get_file_splits(current_file())[:_parent_level(level)])


def open_current_file():
    """
    Opens the current maya scene file.
    :return: <bool> True for success.
    """
    cmds.file(current_file(), o=1, f=1)
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
    return os.path.split(file_name)[1]


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
    return -1 * range(level+1)[-1]


def get_this_directory_parent(level=1):
    """
    get the directory parent path from level.
    :return: <str> get the file path string.
    """
    if level == 0:
        raise IOError("[GetThisDirectoryParent] :: This cannot equal to zero.")
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
    gets the relative path for the controller data folder directory
    :return: <str> directory path name
    """
    dir_name = get_this_directory_parent(level=2)
    return posixpath.join(dir_name, 'rig_utils', 'controller_data')


def list_files(file_name, filter_ext=None):
    """
    lists files in a file path given
    :param file_name: <str> the file directory name to list files from
    :param filter_ext: <list> filters these extension names
    :return: <tuple> array of available files.
    """
    if is_file(file_name):
        files = tuple(os.listdir(directory_name(file_name)))
        return files
    files = tuple(os.listdir(file_name))
    if filter_ext:
        for filt_ext in filter_ext:
            files = [f for f in files if not f.endswith(filt_ext)]
    return files


def list_controller_files():
    """
    lists all the files in the controller directory
    :return: <tuple> array of available controller files
    """
    return list_files(controller_data_dir())


def concatenate_path(*args):
    """
    concatenate the strings into one path
    :param args:
    :return: <str> directory file path name
    """
    return posixpath.join(*args)


class Serializer:
    """Abstract class for use as a base for context-specific data serialization"""
    def __init__(self):
        pass
    def save_file():
        pass
    def load_file():
        pass
    def insert_data():
        pass
    def append_data():
        pass
    def delete_file():
        pass

class DataSerializer(Serializer):
    """Data Serializer class for the basis of serializing python objects"""
    READ_DATA = None
    UPDATE_DATA = None
    FILE_NAME = ""
    EXT_NAME = ""
    SOURCE_DIR_PATH = ""
    DESTINATION_DIR_PATH = ""
    def __init__(self, destination_dir_path=None, source_dir_path=None, source_file=None):
        DataSerializer.SOURCE_DIR_PATH = source_dir_path
        DataSerializer.DESTINATION_DIR_PATH = destination_dir_path
        DataSerializer.FILE_NAME = source_file
        Serializer.__init__(self)
    def save_file():
        """save the updated data to a file if changes are made to the original data"""
        pass
    def load_file():
        """load the file and read the contents of the file"""
        pass
    def insert_data():
        """update the contents of the data file"""
        pass
    def append_data():
        """add new contents of data to the file"""
        pass
    def delete_data():
        """deletes the contents of data inside the file"""
        pass


class PickleSerializer(DataSerializer):
    """Pickle serializer for manipulation of data files."""
    READ_DATA = {}
    FILE_NAME = ""
    UPDATE_DATA = {}
    EXT_NAME = "json"

class CSVSerializer(DataSerializer):
    """CSV serializer for manipulation of data files."""
    READ_DATA = {}
    FILE_NAME = ""
    UPDATE_DATA = {}
    EXT_NAME = "json"

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
            # now write the file from the start
            write_file.seek(0)
            # then write the file
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

    def delete(self):
        if self.is_file_valid:
            remove_file(self.FILE_NAME)

    def file(self):
        return self._get_file_name()

    def __repr__(self):
        return self.FILE_NAME


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


def get_file_variables():
    """
    return full set of file variables associated with this Maya file.
    :return: <list> array of variables set.
    """
    file_list = cmds.fileInfo(query=True)
    file_data = {}
    for idx in range(0, len(file_list), 2):
        key_name = file_list[idx]
        key_value = file_list[idx + 1]
        file_data[key_name] = key_value
    return file_data


def update_internal_file_variables(variable_name, value_name):
    """
    updates the internalVar with variables.
    :return: <bool> True for success.
    """
    if isinstance(value_name, (dict, list, tuple)):
        value_name = "{}".format(value_name)
    cmds.fileInfo(variable_name, value_name)
    return True


def get_internal_var_file_variable(variable_name):
    """
    gets the internal variable.
    :param variable_name:
    :return:
    """
    file_data = get_file_variables()
    if variable_name not in file_data:
        return False
    var_value = file_data[variable_name]
    # if the variable is a dictionary
    if var_value.find("{") or var_value.find("}"):
        return ast.literal_eval(var_value)
    # else return as is
    return var_value


def interpret_text_data(text=""):
    """
    interprets text data.
    :param text: <str> incoming text string data.
    :return: <TypeName> of data.
    """
    # if the variable is a dictionary
    if text.find("{") > -1 and text.find("}") > -1:
        return ast.literal_eval(text)
    elif text.find("[") > -1 and text.find("]") > -1:
        return ast.literal_eval(text)
    elif text.isdigit():
        return ast.literal_eval(text)
    else:
        return text

# ______________________________________________________________________________________________________________________
# file_utils.py
