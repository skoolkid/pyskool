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
Defines the :class:`Water` class.
"""

from .character import Character
from . import animatorystates
from .location import Location

class Water(Character):
    """A jet of water or sherry (as fired from a water pistol).

    :param water_id: The ID of the jet of liquid.
    :param command_list_id: The ID of the command list the jet of liquid will
                            use.
    :param phases: The phases of animation the water will use after being fired
                   from a water pistol.
    """
    def __init__(self, water_id, command_list_id, phases):
        Character.__init__(self, water_id, water_id)
        self.command_list_id = command_list_id
        self.phases = phases
        self.animatory_state = self.initial_as = animatorystates.WATER0
        self.initial_direction = -1
        self.initial_location = Location((-3, 0))
        self.liquid = None
        self.always_runs = True

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the jet of liquid.

        :param lesson_id: The ID of the current lesson (ignored - water and
                          sherry do not follow a timetable).
        """
        return self.command_list_id

    def launch(self, x, y, direction, liquid):
        """Launch this jet of water or sherry from a starting point.

        :param x: The x-coordinate of the starting point.
        :param y: The y-coordinate of the starting point.
        :param direction: The direction the jet will travel.
        :param liquid: The type of liquid.
        """
        self.animatory_state = self.initial_as
        self.x = x
        self.y = y
        self.direction = direction
        self.liquid = liquid
        self.action_delay = 2
        self.action == 3

    def hit_cup(self):
        """Check whether the jet of liquid hit a cup, and fill the cup if so.

        :return: `True` if the liquid hit a cup, `False` otherwise.
        """
        x = self.x - (1 if self.direction < 0 else -3)
        cup = self.skool.cup(x, self.y)
        if cup:
            self.skool.fill_cup(cup.cup_id, self.liquid)
            return True
        return False

    def hit_plant(self):
        """Check whether the jet of liquid hit a plant, and if so, make the
        plant start growing if the liquid is water.

        :return: `True` if a plant was hit, `False` otherwise.
        """
        plant_pot = self.skool.plant_pot(self.x, self.y)
        if plant_pot:
            self.cast.water_plant(plant_pot, self.liquid)
            return True
        return False

    def hit_floor(self):
        """Return whether the jet of liquid hit the floor."""
        return self.floor is not None
