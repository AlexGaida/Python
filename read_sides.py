"""
read_sides extracts the sides from strings provided.
proper nomenclature of using sides in Maya is _l_ or l_, _L_, L_, left_ or _left, Left_, and _Left.
Each class supports iteration and __getitem__ extraction.
"""
# import standard modules
import json
import os
import re

# define local variables
sides_file = os.path.join(os.path.dirname(__file__), "sides.json")
re_any_upper = re.compile('[A-Z]+')


def read_file():
    """
    reads the sides json file.
    """
    with open(sides_file, 'r') as s_file:
        return json.load(s_file)


def strip_underscore(in_string="", strip=False):
    """
    if true, strips any underscores from the incoming parameter.
    :param in_string: <str> check this string for any underscores.
    :param strip: <bool> if true, strip '_' from the string.
    :return: <str> resultant string name.
    """
    if strip:
        return in_string.strip("_")
    return in_string


def extract_side_from_string(s_dict={}, in_string="", index=False, with_underscore=True):
    """
    extract the side from the string provided.
    :param s_dict: <dict> input dictionary.
    :param in_string: <str> input string.
    :param index: <bool> gets the index of the side found.
    :param with_underscore: <bool> return with underscore.
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
        return strip_underscore(s_string, not with_underscore), s_index
    else:
        return strip_underscore(s_string, not with_underscore)


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
    KEY = "sides"
    SIDES = {}
    START = 0
    LENGTH = 0

    def __init__(self):
        self.SIDES = read_file()[self.KEY]
        self.LENGTH = len(self.SIDES)
        self.update_class()

    def update_class(self):
        """
        updates the current class with keys and values
        """
        for k, v in self.SIDES.items():
            self.__dict__[k] = v

    def side_from_string(self, in_string=""):
        """
        get the side from string collected.
        :param in_string: <str> search for a side string name from this parameter.
        :return: <str> the side string name.
        """
        return extract_side_from_string(self.SIDES, in_string)

    def side_name_from_string(self, in_string=""):
        """
        get a uniform, title-cased side name from an incoming string object.
        :param in_string: <str> check this string for a side name.
        :return: <str> side name from string.
        """
        side_name = extract_side_from_string(self.SIDES, in_string, with_underscore=False)
        if len(side_name) == 1:
            return self.SIDES[side_name].title()
        return side_name.title()

    def split(self):
        """
        finds if there is an _ in the sides dictionary.
        :return: <tuple> array of names with '_'.
        """
        return tuple(filter(lambda x: '_' in x, self.SIDES))

    def sides(self):
        """
        get all the side keys in sides.json dictionary.
        :return: <tuple> array of side names.
        """
        return tuple(self.SIDES)

    def items(self):
        """
        array of side names.
        :return: <list> array of side names with their corresponding letter/ letters.
        """
        return self.SIDES.items()

    def upper(self):
        """
        return any name with upper case letters.
        :return: <tuple> upper case letter names.
        """
        return tuple(filter(lambda x: re_any_upper.search(x), self.SIDES))

    def lower(self):
        """
        return any name with lower case letters.
        :return: <tuple> lower case letter names.
        """
        return tuple(filter(lambda x: x.islower(), self.SIDES))

    def upper_singles(self):
        """
        return any name with upper case single letters.
        :return: <tuple> upper case single letter names.
        """
        return tuple(filter(lambda x: len(x) == 1, self.upper()))

    def lower_singles(self):
        """
        return any name with lower case single letters.
        :return: <tuple> lower case single letter names.
        """
        return tuple(filter(lambda x: len(x) == 1, self.lower()))

    def lower_names(self):
        """
        return any lower case names.
        :return: <tuple> lower case names.
        """
        return tuple(filter(lambda x: len(x) != 1, self.lower()))

    def upper_names(self):
        """
        return any upper case names.
        :return: <tuple> upper case names.
        """
        return tuple(filter(lambda x: len(x) != 1, self.upper()))

    def __getitem__(self, item):
        return self.__dict__[item]

    def __repr__(self):
        return str(self.SIDES)

    def __iter__(self):
        return self

    def next(self):
        num = self.START
        self.START += 1
        if num < self.LENGTH:
            return self.SIDES[self.SIDES.keys()[num]]
        else:
            raise StopIteration("[Sides] :: Max length reached.")


class Axes(Sides):
    KEY = "axes"
    SIDES = []

    def __init__(self):
        super(Axes, self).__init__()

    def update_class(self):
        for k in self.SIDES:
            self.__dict__[k] = None

    def next(self):
        num = self.START
        self.START += 1
        if num < self.LENGTH:
            return self.SIDES[num]
        else:
            raise StopIteration("[Axes] :: Max length reached.")


class MirrorSides(Sides):
    KEY = "mirror"

    def __init__(self):
        super(MirrorSides, self).__init__()

    def side_from_string(self, in_string="", index=False):
        """
        get the sides from a string value provided.
        :param in_string: <str> input string to extract sides frOpenMaya.
        :param index: <bool> if true, extract the position where the side string came frOpenMaya.
        :return: <str> the side string value.
        """
        return extract_side_from_string(self.SIDES, in_string, index=index)

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
