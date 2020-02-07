"""
read_sides extracts the sides from strings provided.
proper nomenclature of using sides in Maya is _l_ or l_, _L_, L_, left_ or _left, Left_, and _Left.
Each class supports iteration and __getitem__ extraction.
"""
# import standard modules
import json
import os
import re

# define global variables
sides_file = os.path.join(os.path.dirname(__file__), "sides.json")


def read_file():
    """
    reads the sides json file.
    """
    with open(sides_file, 'r') as s_file:
        return json.load(s_file)


def extract_side_from_string(s_dict={}, in_string="", index=False):
    """
    extract the side from the string provided.
    :param s_dict: <dict> input dictionary.
    :param in_string: <str> input string.
    :param index: <bool> gets the index of the side found.
    :return: <str> side.
    """
    s_string = ""
    s_index = -1
    for k in s_dict:
        side_name = '{}_'.format(k)
        if in_string.startswith(side_name):
            s_string = side_name
            s_index = extract_side_index_from_string(in_string, s_string, start=True)

        side_name = '_{}'.format(k)
        if in_string.endswith(side_name):
            s_string = side_name
            s_index = extract_side_index_from_string(in_string, s_string, end=True)

        side_name = '_{}_'.format(k)
        if side_name in in_string:
            s_string = side_name
            s_index = extract_side_index_from_string(in_string, s_string)

    if index:
        return s_string, s_index
    else:
        return s_string


def extract_side_index_from_string(in_string="", side="", start=False, end=False):
    """
    extract the side from the string provided.
    :param in_string: <dict> input the string to check.
    :param side: <str> input string.
    :param start: <bool> find at the start of the string.
    :param end: <bool> find at the end of the string.
    :return: <str> side.
    """
    if start:
        return re.search('^{}'.format(side), in_string).start()
    if end:
        return re.search('{}$'.format(side), in_string).end()
    return in_string.find(side)


class Sides(object):
    SIDES = read_file()["sides"]

    def __init__(self):
        self.update_class()

    def update_class(self):
        """
        updates the current class with keys and values
        """
        for k, v in self.SIDES.items():
            self.__dict__[k] = v

    def side_from_string(self, in_string=""):
        return extract_side_from_string(self.SIDES, in_string)

    def sides(self):
        return self.SIDES

    def items(self):
        return self.SIDES.items()

    def __getitem__(self, item):
        return self.__dict__[item]

    def __repr__(self):
        return str(self.SIDES)

    def __iter__(self):
        return iter(self.SIDES)


class MirrorSides(object):
    MIRROR_SIDES = read_file()["mirror"]
    SIDES = Sides()

    def __init__(self):
        self.update_class()

    def update_class(self):
        """
        updates the current class with keys and values
        """
        for k, v in self.MIRROR_SIDES.items():
            self.__dict__[k] = v

    def side_from_string(self, in_string="", index=False):
        """
        get the sides from a string value provided.
        :param in_string: <str> input string to extract sides from.
        :param index: <bool> if true, extract the position where the side string came from.
        :return: <str> the side string value.
        """
        return extract_side_from_string(self.SIDES.__dict__, in_string, index=index)

    def replace_side_string(self, in_string=""):
        """
        replaces the side with the mirror side strings.
        :param in_string: <str> input string.
        :return: <str> output string with the replaced side string.
        """
        side, index = self.side_from_string(in_string=in_string, index=True)
        stripped_side_name = side.strip('_')

        # see if there is a side to check first.
        if stripped_side_name in self.__dict__:
            mirror_side_name = side.replace(stripped_side_name, self[stripped_side_name])
            split_str = list(in_string.partition(side))
            if split_str.count(side):
                split_index = split_str.index(side)
                split_str[split_index] = split_str[split_index].replace(side, mirror_side_name)
                return ''.join(split_str)
        return in_string

    def sides(self):
        return self.MIRROR_SIDES

    def items(self):
        return self.MIRROR_SIDES.items()

    def __getitem__(self, item):
        return self.__dict__[item]

    def __repr__(self):
        return str(self.MIRROR_SIDES)

    def __iter__(self):
        return iter(self.MIRROR_SIDES)