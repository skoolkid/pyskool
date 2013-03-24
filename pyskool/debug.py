# -*- coding: utf-8 -*-
# Copyright 2010 Richard Dymond (rjdymond@gmail.com)
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
Used for debugging Pyskool.
"""

import sys

def _write(text):
    sys.stderr.write("%s\n" % text)

def log(text):
    """Print `text` (a debug message) on stderr."""
    _write('DEBUG: %s' % text)

def error(text):
    """Print `text` (an error message) on stderr."""
    _write('ERROR: %s' % text)
