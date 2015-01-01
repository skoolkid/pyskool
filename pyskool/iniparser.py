# -*- coding: utf-8 -*-
# Copyright 2010, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of Pyskool.
#
# Pyskool is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Pyskool is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pyskool. If not, see <http://www.gnu.org/licenses/>.

"""
Parse a single ini file, or a directory of ini files.
"""

import sys
import os
import re
from collections import OrderedDict

# Separators
CONFIG_SEPARATOR = ','
SEPARATOR = ','

class IniParser:
    """Parses one or more ini files.

    :param path: An ini file, or a directory to scan for ini files.
    :param verbose: Whether to print status information while reading files.
    """
    def __init__(self, path, verbose=True):
        cwd = os.getcwd()
        if os.path.isdir(path):
            ini_dir = path
            os.chdir(ini_dir)
            ini_files = [f for f in os.listdir(path) if f.endswith('.ini') and os.path.isfile(f)]
            ini_files.sort()
        elif os.path.isfile(path):
            ini_dir = os.path.abspath(os.path.dirname(path))
            os.chdir(ini_dir)
            ini_files = [path]
        else:
            sys.stderr.write('%s: file or directory not found\n' % path)
            sys.exit(1)
        self.sections = OrderedDict()
        for ini_file in ini_files:
            f = open(ini_file, 'r')
            if verbose:
                sys.stdout.write('Reading %s\n' % os.path.join(ini_dir, ini_file))
            section = None
            for line in f:
                if line.startswith('[') and ']' in line:
                    section_name = line[1:line.index(']')].strip()
                    if section_name.endswith('+'):
                        section = self.sections.setdefault(section_name[:-1], [])
                    else:
                        section = self.sections[section_name] = []
                elif line.isspace():
                    continue
                elif line.startswith(';'):
                    continue
                elif section is not None:
                    section.append(line.strip())
            f.close()
        os.chdir(cwd)

    def _find_separator(self, line, start, separator):
        """Return the index of the next separator in a line, or the length of
        the line if no separator is found.

        :param line: The line.
        :param start: The index of the character from which to start searching.
        :param separator: The character sequence that separates the elements in
                          the line.
        """
        index = line.find(separator, start)
        if index < 0:
            return len(line)
        return index

    def _get_quoted_string(self, elements, details, index, separator):
        """Extract a quoted string from a line.

        :param elements: The list of elements to add the string to.
        :param details: The line.
        :param index: The index of the opening quote in the line.
        :param separator: The character sequence that separates the elements in
                          the line.
        :return: The index of the first character of the next element in the
                 line.
        """
        quote = details[index]
        end = details.index(quote, index + 1)
        elements.append(details[index + 1:end])
        return 1 + self._find_separator(details, end + 1, separator)

    def _get_tuple(self, elements, details, index, separator):
        """Extract a tuple of integers from a line.

        :param elements: The list of elements to add the tuple to.
        :param details: The line.
        :param index: The index of the opening bracket of the tuple in the
                      line.
        :param separator: The character sequence that separates the elements in
                          the line.
        :return: The index of the first character of the next element in the
                 line.
        """
        end = details.index(')', index)
        values = [int(v) for v in details[index + 1:end].split(',')]
        elements.append(tuple(values))
        return 1 + self._find_separator(details, end + 1, separator)

    def _get_element(self, elements, details, index, parse_numbers, separator):
        """Extract an element from a line.

        :param elements: The list of elements to add the tuple to.
        :param details: The line.
        :param index: The index of the opening bracket of the tuple in the
                      line.
        :param parse_numbers: If `True`, convert the element to a number if
                              possible; otherwise leave it as a string.
        :param separator: The character sequence that separates the elements in
                          the line.
        :return: The index of the first character of the next element in the
                 line.
        """
        end = self._find_separator(details, index, separator)
        element = details[index:end].strip()
        if parse_numbers:
            try:
                elements.append(int(element))
            except ValueError:
                try:
                    elements.append(float(element))
                except ValueError:
                    elements.append(element)
        else:
            elements.append(element)
        return end + 1

    def _get_elements(self, details, parse_numbers=True, num_elements=None, separator=SEPARATOR):
        """Return the elements extracted from a line in a section.

        :param details: The line.
        :param parse_numbers: If `True`, any numeric element is converted to a
                              number; otherwise it is left as a string.
        :param num_elements: The minimum number of elements to return. If there
                             are fewer elements than this in the line, the list
                             of elements is padded out with `None` instances.
        :param separator: The character sequence that separates the elements in
                          the line.
        """
        elements = []
        index = 0
        while index < len(details):
            if details[index].isspace():
                index += 1
            elif details[index] in '"\'':
                index = self._get_quoted_string(elements, details, index, separator)
            elif details[index] == '(':
                index = self._get_tuple(elements, details, index, separator)
            else:
                index = self._get_element(elements, details, index, parse_numbers, separator)
        if num_elements is not None:
            elements.extend([None] * (num_elements - len(elements)))
        return elements

    def parse_section(self, name, parse_numbers=True, num_elements=None, split=True, separator=SEPARATOR):
        """Extract the elements from every line in a section. The return value
        is a list of lists of elements from each line (if `split` is `True`),
        or a list of the lines. If the named section does not exist, an empty
        list is returned.

        :param name: The name of the section.
        :param parse_numbers: If `True`, any numeric element is converted to a
                              number; otherwise it is left as a string.
        :param num_elements: The minimum number of elements to return for each
                             line in the section. If any line has fewer
                             elements than this, the list of elements is padded
                             out with `None` instances.
        :param split: If `True`, each line is split on commas; otherwise, the
                      line is returned whole.
        :param separator: The character sequence that separates the elements in
                          a line.
        """
        contents = []
        if name in self.sections:
            for line in self.sections[name]:
                if split:
                    contents.append(self._get_elements(line, parse_numbers, num_elements, separator))
                else:
                    contents.append(line)
        return contents

    def _get_sections(self, prefix, parse_numbers=True, num_elements=None, split=True, separator=SEPARATOR):
        """Extract the elements from every line in the sections whose names
        begin with a certain prefix. Return a dictionary whose keys are the
        section name suffixes, and where each value is a list of lists of
        elements from each line (if `split` is `True`), or a list of the lines.

        :param prefix: The section name prefix.
        :param parse_numbers: If `True`, any numeric element is converted to a
                              number; otherwise it is left as a string.
        :param num_elements: The minimum number of elements to return for each
                             line in each section. If any line has fewer
                             elements than this, the list of elements is padded
                             out with `None` instances.
        :param split: If `True`, each line is split on commas; otherwise, the
                      line is returned whole.
        :param separator: The character sequence that separates the elements in
                          a line.
        """
        sections = {}
        for name in self.sections:
            if name.startswith(prefix):
                sections[name[len(prefix):].strip()] = self.parse_section(name, parse_numbers, num_elements, split, separator)
        return sections

    def get_config(self, pattern):
        """Return a dictionary of keys and values from every section whose name
        matches `pattern`.
        """
        config = {}
        for section_name in self.sections:
            match = re.match(pattern, section_name)
            if match and match.group() == section_name:
                for key, value in self.parse_section(section_name, separator=CONFIG_SEPARATOR):
                    config[key] = value
        return config
