# -*- coding: utf-8 -*-
# Copyright 2008-2010, 2015 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Floor` class.
"""

class Floor:
    """A region of the skool regarded as a starting point from which to reach a
    destination (which will be on the same or another floor).

    :param floor_id: The floor's unique ID.
    :param left_x: The x-coordinate of the left edge of the floor.
    :param right_x: The x-coordinate of the right edge of the floor.
    :param y: The y-coordinate of the floor.
    """
    def __init__(self, floor_id, left_x, right_x, y):
        self.floor_id = floor_id
        self.left_x = left_x
        self.right_x = right_x
        self.y = y

    def supports(self, character):
        """Return whether a character is on this floor.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return self.y == character.y and self.left_x <= character.x <= self.right_x

    def below(self, character):
        """Return whether this floor is below a character's current location.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return self.y >= character.y and self.left_x <= character.x <= self.right_x

    def contains_location(self, x, y):
        """Return whether the location `(x, y)` is on this floor."""
        return self.y == y and self.left_x <= x <= self.right_x
