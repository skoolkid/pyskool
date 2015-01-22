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
Defines the :class:`Plant` and :class:`PlantPot` classes.
"""

from .character import Character
from . import animatorystates
from .location import Location

class Plant(Character):
    """A plant that grows when watered.

    :param plant_id: The ID of the plant.
    :param command_list_id: The ID of the command list the plant will use.
    :param x: The x-coordinate of the plant.
    :param y: The y-coordinate of the plant.
    """
    def __init__(self, plant_id, command_list_id, x, y):
        Character.__init__(self, plant_id, plant_id)
        self.command_list_id = command_list_id
        self.grow_x = x
        self.y = y
        self.animatory_state = self.initial_as = animatorystates.PLANT_GROWING
        self.direction = self.initial_direction = -1
        self.initial_location = Location((-3, y))
        self.head_height = 0
        self.growing = False
        self.always_runs = True

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the plant.

        :param lesson_id: The ID of the current lesson (ignored - plants do
                          not follow a timetable).
        """
        return self.command_list_id

    def grow(self):
        """Make this plant start growing."""
        self.growing = True

    def head_coords(self):
        """Return the coordinates of the head of the plant."""
        return (self.x, self.y - self.head_height - 1)

    def supports(self, character):
        """Return whether a character is standing on the head of the plant.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return (character.x, character.y) == self.head_coords()

    def appear(self):
        """Make the plant appear half-grown. Anyone standing on the plant pot
        will be lifted.
        """
        self.x = self.grow_x
        self.animatory_state = self.initial_as
        self.cast.lift_anyone_at(*self.head_coords())
        self.head_height = 1

    def finish_growing(self):
        """Make the plant appear fully grown. Anyone standing on the head of
        the plant will be lifted.
        """
        self.animatory_state = animatorystates.PLANT_GROWN
        self.cast.lift_anyone_at(*self.head_coords())
        self.head_height = 2

    def is_fully_grown(self):
        """Return whether the plant is fully grown."""
        return self.head_height == 2

    def die(self):
        """Make the plant die. Anyone standing on the head of the plant will
        be dropped to the ground.
        """
        self.cast.drop_anyone_at(*self.head_coords())
        self.head_height = 0
        self.growing = False
        self.hide()

class PlantPot:
    """A plant pot.

    :param plant_pot_id: The ID of the plant pot.
    :type plant: :class:`Plant`
    :param plant: The plant in the plant pot.
    :param x: The x-coordinate of the plant pot.
    :param y: The y-coordinate of the plant pot.
    """
    def __init__(self, plant_pot_id, plant, x, y):
        self.plant_pot_id = plant_pot_id
        self.plant = plant
        self.x = x
        self.y = y
