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
Defines the :class:`Stinkbomb` class.
"""

from .character import Character
from .location import Location

class Stinkbomb(Character):
    """A stinkbomb.

    :param stinkbomb_id: The ID of the stinkbomb.
    :param command_list_id: The ID of the command list the stinkbomb will use.
    :param phases: The phases of animation the stinkbomb cloud will use.
    :param stink_range: The maximum distance from which the stinkbomb can be
                        smelt.
    """
    def __init__(self, stinkbomb_id, command_list_id, phases, stink_range):
        Character.__init__(self, stinkbomb_id, stinkbomb_id)
        self.command_list_id = command_list_id
        self.phases = phases
        self.stink_range = stink_range
        self.animatory_state = self.initial_as = phases[0][0]
        self.initial_direction = phases[0][1]
        self.initial_location = Location((-3, 0))
        self.smelt = False
        self.phase_index = 0
        self.always_runs = True

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the stinkbomb.

        :param lesson_id: The ID of the current lesson (ignored - stinkbombs do
                          not follow a timetable).
        """
        return self.command_list_id

    def drop(self, x, y):
        """Drop the stinkbomb at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        self.smelt = False
        self.x = x
        self.y = y

    def move_cloud(self):
        """Animate the stinkbomb cloud. Any stinkbomb smeller in the vicinity
        of the stinkbomb will be alerted and open a nearby window if
        possible.
        """
        self.phase_index = (self.phase_index + 1) % len(self.phases)
        self.animatory_states, self.direction = self.phases[self.phase_index]
        if not self.smelt:
            smeller = self.cast.smeller(self)
            if smeller:
                window = self.skool.nearby_window(smeller)
                if window and window.shut:
                    self.smelt = True
                    smeller.open_window(window)
