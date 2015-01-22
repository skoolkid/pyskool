# -*- coding: utf-8 -*-
# Copyright 2008-2010, 2012, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Staircase` class.
"""

from .location import Location

class Staircase:
    """A staircase.

    :param bottom: The coordinates of the bottom of the staircase.
    :param top: The coordinates of the top of the staircase.
    :param force: If `True`, the staircase must be ascended or descended when
                  approached (like the staircase in Back to Skool that leads up
                  from or down to the stage).
    """
    def __init__(self, bottom, top, force=False):
        self.bottom = Location(bottom)
        self.top = Location(top)
        self.force = force
        self.direction = 1 if self.bottom.x < self.top.x else -1

    def contains(self, character, distance=0):
        """Return whether a character is (a) on a step of this staircase, or
        (b) at the bottom of this staircase facing the top, or (c) at the top
        of this staircase facing the bottom.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        :param distance: The maximum distance to check in front of the
                         character.
        """
        for x, y in [(character.x + d * character.direction, character.y) for d in range(distance + 1)]:
            if self.contains_location(x, y):
                if x == self.bottom.x:
                    return character.direction == self.direction
                if x == self.top.x:
                    return character.direction != self.direction
                return True
        return False

    def contains_location(self, x, y):
        """Return whether the location `(x, y)` is at the bottom, or at the
        top, or on a step of this staircase.
        """
        if self.direction * self.bottom.x <= self.direction * x <= self.direction * self.top.x:
            if (x, y) in (self.bottom.coords(), self.top.coords()):
                return True
            if self.top.y < y < self.bottom.y:
                return x == self.bottom.x + self.direction * (self.bottom.y - y)
        return False

    def supports(self, character):
        """Return whether a character is on a step of this staircase.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        if not self.contains_location(character.x, character.y):
            return False
        return (character.x, character.y) not in (self.bottom.coords(), self.top.coords())
