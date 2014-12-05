# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2014 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Pellet` class.
"""

from .character import Character
from . import animatorystates
from .location import Location

class Pellet(Character):
    """A catapult pellet.

    :param pellet_id: The ID of the pellet.
    :param command_list_id: The ID of the command list the pellet will use.
    :param pellet_range: The maximum distance the pellet will travel after
                         launch.
    :param hit_zone: The size of the portion at the end of the pellet's
                     journey in which it can hit things.
    :param hit_xy: The coordinates of the pellet within its sprite (used for
                   collision detection).
    """
    def __init__(self, pellet_id, command_list_id, pellet_range, hit_zone, hit_xy):
        Character.__init__(self, pellet_id, pellet_id)
        self.command_list_id = command_list_id
        self.pellet_range = pellet_range
        self.hit_zone = hit_zone
        self.hit_xy = hit_xy
        self.animatory_state = self.initial_as = animatorystates.FLY
        self.initial_direction = -1
        self.initial_location = Location((-3, 0))
        self.always_runs = True

    def get_hit_coords(self):
        """Return the coordinates of the pellet adjusted for comparison with
        the coordinates of a cup, shield or conker.
        """
        return self.x + self.hit_xy[0], self.y + self.hit_xy[1]

    def impeded(self, bottom_y, top_y):
        """Return whether the pellet is blocked by an object (such as a wall).

        :param bottom_y: The y-coordinate of the bottom of the object.
        :param top_y: The y-coordinate of the top of the object.
        """
        return bottom_y >= self.y + 1 >= top_y

    def get_victim(self):
        """Return whoever has been hit by this pellet, or `None` if no one was
        hit.
        """
        return self.cast.get_pelletable(self.x, self.y)

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the pellet.

        :param lesson_id: The ID of the current lesson (ignored - pellets do
                          not follow a timetable).
        """
        return self.command_list_id

    def hit_shield(self):
        """Check whether the pellet hit a shield, and make the shield flash or
        unflash as appropriate if so.

        :return: `True` if the pellet hit a shield, `False` otherwise.
        """
        return self.check_shields_at(*self.get_hit_coords())

    def hit_cup(self):
        """Check whether the pellet hit a cup, and spill its contents if so.

        :return: `True` if the pellet hit a cup containing water, sherry or a
                 frog, `False` otherwise.
        """
        cup = self.skool.cup(*self.get_hit_coords())
        if cup and not cup.is_empty():
            self.cast.knock_cup(cup)
            return True
        return False

    def hit_conker(self):
        """Check whether the pellet hit a conker in the tree, and make the
        conker fall if so.

        :return: `True` if the pellet hit a conker, `False` otherwise.
        """
        return self.cast.hit_conker(self)

    def launch(self, x, y, direction):
        """Launch the pellet from a starting point.

        :param x: The x-coordinate of the starting point.
        :param y: The y-coordinate of the starting point.
        :param direction: The direction the pellet will travel.
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.action_delay = 1
