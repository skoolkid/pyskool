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
Defines the :class:`Bike` class.
"""

from .character import Character
from . import animatorystates
from .location import Location

class Bike(Character):
    """The bike.

    :param bike_id: The ID of the bike.
    :param command_list_id: The ID of the command list the bike will use.
    :param initial_as: The bike's initial animatory state.
    :param unchain_location: The location at which the bike will be deposited
                             when it's unchained from the tree.
    :param move_delay: The delay between consecutive movements of the bike when
                       wheeling along or being pedalled.
    :param pedal_momentum: The momentum increment when the bike is pedalled.
    :param max_momentum: The maximum momentum the bike can have.
    """
    def __init__(self, bike_id, command_list_id, initial_as, unchain_location, move_delay, pedal_momentum, max_momentum):
        Character.__init__(self, bike_id, bike_id)
        self.command_list_id = command_list_id
        self.animatory_state = self.initial_as = initial_as
        self.direction = self.initial_direction = -1
        self.unchain_location = unchain_location
        self.x, self.y = -3, 0
        self.initial_location = Location((self.x, self.y))
        self.momentum = 0
        self.move_delay = move_delay
        self.pedal_momentum = pedal_momentum
        self.max_momentum = max_momentum

    def get_command_list_id(self, lesson_id):
        """Return the ID of the command list used by the bike.

        :param lesson_id: The ID of the current lesson (ignored - bikes do
                          not follow a timetable).
        """
        return self.command_list_id

    def unchain(self):
        """Deposit the bike at the base of the tree (or whatever the unchain
        location is set to).
        """
        self.x, self.y = self.unchain_location

    def prepare(self):
        """Prepare the bike for riding by Eric. This entails giving the bike
        some initial momentum, and hiding its sprite.
        """
        # Give ERIC some time to start pedalling before the bike falls over
        self.momentum = 3
        # The bike hides while ERIC is riding it
        self.hide()

    def pedal(self):
        """Pedal the bike (increase its momentum)."""
        self.momentum = min(self.momentum + self.pedal_momentum, self.max_momentum)

    def start_wheeling(self, rider):
        """Start wheeling the bike along after the rider has dismounted or
        stood on the saddle.

        :type rider: :class:`~pyskool.character.Character`
        :param rider: The rider.
        """
        self.walk_delay = self.move_delay
        self.x, self.y, self.direction = rider.x, rider.y, rider.direction
        self.animatory_state = animatorystates.BIKE_UPRIGHT

    def wheel(self):
        """Continue wheeling the bike along until it hits a barrier or runs out
        of momentum.
        """
        self.walk_delay = self.move_delay
        self.momentum = max(self.momentum - 1, 0)
        if self.hit_barrier():
            self.momentum = 0
        else:
            self.x += self.direction

    def hit_barrier(self):
        """Return the wall or door that the bike has hit (if any).

        :return: The barrier that was hit, or `None` if none was hit.
        """
        # Check from a distance of 1 if travelling leftwards so that the bike
        # does not appear too close to the barrier if it hits it
        distance = 1 if self.direction < 0 else 0
        return self.skool.barrier(self, distance)

    def fall(self, rider=None):
        """Make the bike fall over (as when it has lost momentum).

        :type rider: :class:`~pyskool.character.Character`
        :param rider: Whoever was riding the bike (if anybody).
        """
        if rider:
            self.x, self.y, self.direction = rider.x, rider.y, rider.direction
        self.animatory_state = animatorystates.BIKE_ON_FLOOR
