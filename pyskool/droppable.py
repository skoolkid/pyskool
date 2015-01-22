# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
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
Classes for things in the skool that fall from a height onto the floor or
someone's head.
"""

from . import character
from . import animatorystates
from .location import Location

class Droppable(character.Character):
    """Abstract superclass for objects that fall from a height.

    :param object_id: The ID of the object.
    :param command_list_id: The ID of the command list the object will use.
    :param hit_xy: The coordinates of the object within its sprite (used for
                   collision detection).
    :param animatory_state: The object's animatory state.
    :param direction: The direction the object faces (this is used to orient
                      the object's animatory state).
    """
    def __init__(self, object_id, command_list_id, hit_xy, animatory_state, direction):
        character.Character.__init__(self, object_id, object_id)
        self.command_list_id = command_list_id
        self.hit_xy = hit_xy
        self.animatory_state = self.initial_as = animatory_state
        self.direction = self.initial_direction = direction
        self.x = -3
        self.y = 0
        self.initial_location = Location((self.x, self.y))
        self.always_runs = True

    def _get_hit_coords(self):
        """Return the coordinates of the location immediately below the falling
        object.
        """
        hit_x = self.x + self.hit_xy[0]
        hit_y = self.y + self.hit_xy[1] + 1
        return hit_x, hit_y

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by this object.

        :param lesson_id: The ID of the current lesson (ignored - this object
                          does not follow a timetable).
        """
        return self.command_list_id

    def fall(self, x, y):
        """Make the object begin its descent from a specified location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        self.x = x - self.hit_xy[0]
        self.y = y - self.hit_xy[1]

class Drop(Droppable):
    """Abstract superclass for a drop of liquid (water or sherry)."""
    def hit_victim(self):
        """Knock anyone over who was unfortunate enough to be struck by the
        drop of liquid, and make them reveal a secret.

        :return: `True` if someone was struck, `False` otherwise.
        """
        hit_x, hit_y = self._get_hit_coords()
        victim = self._get_victim(hit_x, hit_y)
        if victim:
            self._reveal_secret(victim)
            if victim.is_standing():
                victim.deck()
            return True
        return False

class WaterDrop(Drop):
    """A drop of water (as knocked from a cup by a catapult pellet).

    :param object_id: The ID of the water drop.
    :param command_list_id: The ID of the command list the drop will use.
    :param hit_xy: The coordinates of the water drop within its sprite (used
                   for collision detection).
    """
    def __init__(self, object_id, command_list_id, hit_xy):
        Drop.__init__(self, object_id, command_list_id, hit_xy, animatorystates.WATER_DROP, -1)

    def _get_victim(self, x, y):
        """Check whether there is anyone vulnerable to a falling drop of water
        at a given location, and return them if there is (or `None` if there
        is no one).

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        return self.cast.get_waterable(x, y)

    def _reveal_secret(self, victim):
        """Make a character reveal a bike combination digit (after being struck
        by a falling drop of water).

        :param victim: The character who was struck.
        """
        victim.reveal_bike_secret()

class SherryDrop(Drop):
    """A drop of sherry (as knocked from a cup by a catapult pellet).

    :param object_id: The ID of the sherry drop.
    :param command_list_id: The ID of the command list the drop will use.
    :param hit_xy: The coordinates of the sherry drop within its sprite (used
                   for collision detection).
    """
    def __init__(self, object_id, command_list_id, hit_xy):
        Drop.__init__(self, object_id, command_list_id, hit_xy, animatorystates.SHERRY_DROP, 1)

    def _get_victim(self, x, y):
        """Check whether there is anyone vulnerable to a falling drop of sherry
        at a given location, and return them if there is (or `None` if there
        is no one).

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        return self.cast.get_sherryable(x, y)

    def _reveal_secret(self, victim):
        """Make a character reveal a storeroom combination letter (after being
        struck by a falling drop of sherry).

        :param victim: The character who was struck.
        """
        victim.reveal_storeroom_secret()

class Conker(Droppable):
    """A conker (as knocked out of a tree by a catapult pellet).

    :param object_id: The ID of the conker.
    :param command_list_id: The ID of the command list the conker will use.
    :param min_x: The minimum x-coordinate a pellet must reach to knock the
                  conker out of the tree.
    :param max_x: The maximum x-coordinate a pellet must reach to knock the
                  conker out of the tree.
    :param min_y: The minimum y-coordinate a pellet must fly at to knock the
                  conker out of the tree.
    :param max_y: The maximum y-coordinate a pellet must fly at to knock the
                  conker out of the tree.
    :param hit_xy: The coordinates of the conker within its sprite (used for
                   collision detection).
    """
    def __init__(self, object_id, command_list_id, min_x, max_x, min_y, max_y, hit_xy):
        Droppable.__init__(self, object_id, command_list_id, hit_xy, animatorystates.CONKER, -1)
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def hit_by(self, pellet):
        """Return whether the conker was hit by a catapult pellet.

        :type pellet: :class:`~pyskool.pellet.Pellet`
        :param pellet: The catapult pellet to check.
        """
        return self.min_x <= pellet.x <= self.max_x and self.min_y <= pellet.y <= self.max_y

    def hit_victim(self):
        """Knock anyone over or out who was unfortunate enough to be struck by
        the conker.

        :return: `True` if someone was struck, `False` otherwise.
        """
        victim = self.cast.get_conkerable(*self._get_hit_coords())
        if victim and victim.is_standing():
            victim.deck(victim.is_very_conkerable())
            return True
        return False
