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
Defines the :class:`DeskLid` class.
"""

from . import animatorystates
from .character import Character
from .location import Location
from . import items

class DeskLid(Character):
    """A desk lid.

    :param desk_lid_id: The ID of the desk lid.
    :param command_list_id: The ID of the command list the desk lid will use.
    :param x_offset: The offset (relative to the desk being opened) at which
                     the desk lid should be displayed.
    """
    def __init__(self, desk_lid_id, command_list_id, x_offset):
        Character.__init__(self, desk_lid_id, desk_lid_id)
        self.command_list_id = command_list_id
        self.x_offset = x_offset
        self.animatory_state = self.initial_as = animatorystates.DESK_EMPTY
        self.direction = self.initial_direction = -1
        self.initial_location = Location((-3, 0))
        self.desk = None
        self.opener = None
        self.always_runs = True

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the desk lid.

        :param lesson_id: The ID of the current lesson (ignored - desk lids do
                          not follow a timetable).
        """
        return self.command_list_id

    def raise_lid(self, desk, character):
        """Raise the lid of a desk.

        :type desk: :class:`~pyskool.room.Desk`
        :param desk: The desk.
        :type character: :class:`~pyskool.character.Character`
        :param character: The character raising the lid.
        """
        if self.is_visible():
            return
        self.desk = desk
        self.direction = character.direction
        self.x, self.y = desk.x + (self.x_offset * self.direction), character.y
        if desk.contents == items.WATER_PISTOL:
            self.animatory_state = animatorystates.DESK_WATER_PISTOL
        elif desk.contents == items.STINKBOMBS3:
            self.animatory_state = animatorystates.DESK_STINKBOMBS
        else:
            self.animatory_state = animatorystates.DESK_EMPTY
        self.opener = character

    def deliver_contents(self):
        """Deliver the contents of the desk to whoever raised the lid."""
        self.opener.collect_desk_contents(self.desk)
