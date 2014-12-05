# -*- coding: utf-8 -*-
# Copyright 2010, 2014 Richard Dymond (rjdymond@gmail.com)
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
Classes that represent the animals in the game.
"""

from .character import Character
from . import animatorystates
from .location import Location

class Animal(Character):
    """Abstract superclass for any animals in the game.

    :param animal_id: The ID of the animal.
    :param command_list_id: The ID of the command list the animal will use.
    :param initial_as: The animal's initial animatory state.
    :param location: The animal's initial location.
    """
    def __init__(self, animal_id, command_list_id, initial_as, location):
        Character.__init__(self, animal_id, animal_id)
        self.x, self.y = location
        self.initial_location = Location(location)
        self.command_list_id = command_list_id
        self.animatory_state = self.initial_as = initial_as
        self.direction = self.initial_direction = -1
        self.always_runs = True

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the animal.

        :param lesson_id: The ID of the current lesson (ignored - animals do
                          not follow a timetable).
        """
        return self.command_list_id

    def is_mouse(self):
        """Return whether this animal is a mouse.

        :return: `False`.
        """
        return False

    def is_frog(self):
        """Return whether this animal is a frog.

        :return: `False`.
        """
        return False

    def is_blocked(self, distance=0):
        """Return `True` if the animal can proceed no further in the current
        direction, `False` otherwise.

        :param distance: The maximum distance to check in front of the animal.
        """
        # Check walls and closed doors
        if self.skool.barrier(self, distance):
            return True
        # Check staircases that must be ascended or descended
        staircase = self.skool.staircase(self, distance)
        if staircase and staircase.force:
            return True
        # Check whether there is a floor in front of the animal
        floor = self.skool.floor_at(self.x + self.direction * max(1, distance), self.y)
        return floor is None

class Mouse(Animal):
    """A mouse.

    :param mouse_id: The ID of the mouse.
    :param command_list_id: The ID of the command list the mouse will use.
    :param initial_as: The mouse's initial animatory state.
    :param location: The mouse's initial location.
    :param sprite_xy: The coordinates of the mouse within its sprite (used for
                      detecting whether Eric has caught it).
    :param immortal: If `True`, the mouse will not disappear until Eric catches
                     it; otherwise it will die (disappear from the game) after
                     a certain time.
    """
    def __init__(self, mouse_id, command_list_id, initial_as, location, sprite_xy, immortal=True):
        Animal.__init__(self, mouse_id, command_list_id, initial_as, location)
        self.sprite_xy = sprite_xy
        self.immortal = immortal

    def is_mouse(self):
        """Return whether this animal is a mouse.

        :return: `True`.
        """
        return True

    def is_catchable_at(self, x, y):
        """Return whether the mouse is currently catchable at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        return (x, y) == (self.x + self.sprite_xy[0], self.y + self.sprite_xy[1])

    def scare_people(self):
        """Alert any nearby musophobes of this mouse's presence."""
        self.cast.scare_musophobes(self)

    def die(self):
        """Kill this mouse. The mouse is removed from the game, never to be
        seen again.
        """
        self.cast.kill_mouse(self)

class Frog(Animal):
    """A frog.

    :param frog_id: The ID of the frog.
    :param command_list_id: The ID of the command list the frog will use.
    :param initial_as: The frog's initial animatory state.
    :param location: The frog's initial location.
    :param sit_xy: The coordinates of the frog within its sprite when it's
                   sitting (used for collision detection and placement in
                   cups).
    :param eric_proximity: The minimum distance from the frog that Eric can be
                           before it will try to hop away.
    """
    def __init__(self, frog_id, command_list_id, initial_as, location, sit_xy, eric_proximity):
        Animal.__init__(self, frog_id, command_list_id, initial_as, location)
        self.sit_xy = sit_xy
        self.eric_proximity = eric_proximity
        self.falling = False
        self.trapped = False
        self.turn_round = ()
        self.short_hop = ()
        self.long_hop = ()

    def is_frog(self):
        """Return whether this animal is a frog.

        :return: `True`.
        """
        return True

    def is_catchable_at(self, x, y):
        """Return whether the frog is currently catchable at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        if self.animatory_state == animatorystates.SIT:
            return (x, y) == (self.x + self.sit_xy[0], self.y + self.sit_xy[1])
        return False

    def sit(self):
        """Make the frog assume a sitting position."""
        self.animatory_state = animatorystates.SIT

    def insert_into_cup(self, cup):
        """Insert this frog into a cup. The frog will be trapped until Eric
        knocks the frog out.

        :param cup: The cup.
        """
        self.trapped = True
        self.sit()
        self.x, self.y = cup.x - self.sit_xy[0], cup.y - self.sit_xy[1]

    def fall_from_cup(self, cup):
        """Make this frog fall out of a cup.

        :param cup: The cup.
        """
        cup.remove_frog(self)
        self.trapped = False
        self.falling = True

    def check_heads(self):
        """Check whether this frog has hit anybody's head, and take appropriate
        action (such as handing the safe key to Eric) if so.
        """
        return self.cast.check_heads_at(self.x + self.sit_xy[0], self.y + self.sit_xy[1] + 1)

    def bounce_off_head(self):
        """Make the frog bounce off a character's head."""
        self.animatory_state = animatorystates.HOP1
        self.direction = -1
        self.x -= 1

    def is_eric_nearby(self):
        """Return whether Eric is on the same floor as and close to the frog.
        The answer is used by the frog to decide whether to hop.
        """
        eric_x, eric_y = self.get_location_of_eric()
        return self.y == eric_y and abs(self.x - eric_x) < self.eric_proximity
