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
Classes representing the parts of the skool that cause obstructions, namely
walls, windows and doors.
"""

class Barrier:
    """Abstract superclass of all obstructions.

    :param barrier_id: The ID of the barrier.
    :param x: The x-coordinate of the barrier.
    :param bottom_y: The y-coordinate of the bottom of the barrier.
    :param top_y: The y-coordinate of the top of the barrier.
    """
    def __init__(self, barrier_id, x, bottom_y, top_y, climb_phases=(), fly_phases=()):
        self.barrier_id = barrier_id
        self.x = x
        self.bottom_y = bottom_y
        self.top_y = top_y
        self.climb_phases = climb_phases
        self.fly_phases = fly_phases

    def impedes(self, character, distance=0, force_shut=False):
        """Return whether a character is impeded by this barrier.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        :param distance: The maximum distance in front of the character at
                         which the barrier should be considered an obstruction.
        :param force_shut: If `True`, the barrier will be considered an
                           obstruction even if it's open; otherwise it will be
                           considered an obstruction only when closed.
        """
        if not (force_shut or self.is_shut()):
            return False
        if character.impeded(self.bottom_y, self.top_y):
            if character.x < self.x and character.direction > 0:
                return character.x + distance >= self.x - character.width + 1
            elif character.x >= self.x and character.direction < 0:
                return character.x - distance <= self.x
        return False

    def is_shut(self):
        """Return whether the barrier is shut. Subclasses override this method
        as appropriate.

        :return: `True`.
        """
        return True

    def is_door(self):
        """Return whether the barrier is a door (or window). Subclasses
        override this method as appropriate.

        :return: `False`.
        """
        return False

class Wall(Barrier):
    """A wall in the skool."""
    def separates(self, a, b):
        """Return whether this wall blocks the view from one location to
        another.

        :type a: :class:`~pyskool.location.Location`
        :param a: The first location.
        :type b: :class:`~pyskool.location.Location`
        :param b: The other location.
        """
        min_x = min(a.x, b.x)
        max_x = max(a.x, b.x)
        if min_x < self.x <= max_x:
            return self.top_y <= max(a.y, b.y) and self.bottom_y >= min(a.y, b.y)
        return False

class Door(Barrier):
    """A door that may be opened and closed.

    :param door_id: The ID of the door.
    :param x: The x-coordinate of the door.
    :param bottom_y: The y-coordinate of the bottom of the door.
    :param top_y: The y-coordinate of the top of the door.
    :param shut: Whether the door is shut at the start of the game.
    :param auto_shut_delay: The delay before the door shuts automatically; if
                            zero or negative, the door will not shut
                            automatically.
    :param climb_phases: The sequence of animation phases to use for Eric if he
                         climbs over the door when it's shut.
    :param fly_phases: The sequence of animation phases to use for Eric if he
                        he flies over the door after hitting it while standing
                        on the saddle of the bike.
    """
    def __init__(self, door_id, x, bottom_y, top_y, shut, auto_shut_delay, climb_phases, fly_phases=()):
        Barrier.__init__(self, door_id, x, bottom_y, top_y, climb_phases, fly_phases)
        self.shut = self.initially_shut = shut
        self.open_images = None
        self.shut_images = None
        self.top_left = None
        self.auto_shut_timer = 0
        self.auto_shut_delay = auto_shut_delay

    def is_shut(self):
        """Return whether the door is shut."""
        return self.shut

    def move(self, shut):
        """Open or close the door.

        :param shut: If `True`, close the door; otherwise open it.
        :return: A 2-tuple containing a list of images of the current state of
                 the door, and the coordinates at which to draw the door.
        """
        self.shut = shut
        if not shut:
            self.auto_shut_timer = self.auto_shut_delay
        return self.get_images()

    def set_images(self, open_images, shut_images, top_left):
        """Define the images to use for the door when open or closed.

        :param open_images: A list of the images to use when the door is open.
        :param shut_images: A list of the images to use when the door is
                            closed.
        :param top_left: The coordinates at which to draw the image of the
                         door.
        """
        self.open_images = open_images
        self.shut_images = shut_images
        self.top_left = top_left

    def get_images(self):
        """Return a 2-tuple containing a list of images of the current state of
        the door, and the coordinates at which to draw the door.
        """
        images = self.shut_images if self.shut else self.open_images
        return images, self.top_left

    def build_images(self):
        """Build the images for the barrier. This method is called after
        rescaling the screen or loading a saved game.
        """
        for image in self.open_images:
            image.build()
        for image in self.shut_images:
            image.build()

    def auto_shut(self):
        """Return whether this door should automatically shut now."""
        if self.shut or self.auto_shut_delay < 1:
            return False
        self.auto_shut_timer = max(self.auto_shut_timer - 1, 0)
        return self.auto_shut_timer == 0

    def is_door(self):
        """Return whether this is a door.

        :return: `True`.
        """
        return True

class Window(Door):
    """A window that may be opened and closed.

    :param window_id: The ID of the window.
    :param x: The x-coordinate of the window.
    :param bottom_y: The y-coordinate of the bottom of the window.
    :param top_y: The y-coordinate of the top of the window.
    :param shut: Whether the window is shut at the start of the game.
    :param opener_coords: Where a character should stand to open or close the
                          window.
    :param phases: The animation phases to use for Eric if he jumps out of the
                   window.
    :param not_a_bird: The ID of the command list Mr Wacker should switch to
                       when Eric hits the ground after jumping out of the
                       window; if not blank, Eric will be paralysed when he
                       hits the ground.
    """
    def __init__(self, window_id, x, bottom_y, top_y, shut, opener_coords, phases, not_a_bird):
        Door.__init__(self, window_id, x, bottom_y, top_y, shut, False, phases)
        self.opener_coords = opener_coords
        self.not_a_bird = not_a_bird
