# -*- coding: utf-8 -*-
# Copyright 2008-2010 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Location` class.
"""

class Location:
    """A location in the skool specified by a pair of coordinates.

    :param coords: The coordinates of this location.
    """
    def __init__(self, coords):
        self.x = coords[0]
        self.y = coords[1]

    def coords(self):
        """Return the coordinates of this location as a 2-tuple."""
        return self.x, self.y

    def __str__(self):
        """Return a display string for this location: '`(x, y)`'."""
        return '(%s, %s)' % (self.x, self.y)
