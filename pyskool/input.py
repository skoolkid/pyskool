# -*- coding: utf-8 -*-
# Copyright 2008, 2010 Richard Dymond (rjdymond@gmail.com)
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
Collect input from the keyboard.
"""

import pygame

class Keyboard:
    """Collects input from the keyboard."""
    def __init__(self):
        self.pump()
        self.writing = False

    def pump(self):
        """Process the input event queue."""
        self.key_down_events = []
        self.quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                self.key_down_events.append(event)
        # It's important to collect pressed_keys AFTER clearing the event queue,
        # otherwise keys may appear to "stick"
        self.pressed_keys = list(pygame.key.get_pressed())

    def got_quit(self):
        """Return whether the window close button was clicked."""
        return self.quit

    def start_writing(self):
        """Prepare the keyboard for Eric writing on a blackboard, during which
        time keypresses are echoed on the blackboard instead of making Eric
        move.
        """
        self.writing = True

    def finish_writing(self):
        """Return the keyboard to normal operation after Eric has finished
        writing on a blackboard.
        """
        self.writing = False

    def is_pressed(self, keys):
        """Return whether any one of a set of keys is being pressed, or
        `False` if Eric is writing on a blackboard at the moment.

        :param keys: A list of keys to check.
        """
        pressed = False
        if not self.writing:
            for key in keys:
                if self.pressed_keys[key]:
                    self.pressed_keys[key] = 0
                    pressed = True
        return pressed

    def was_pressed(self, keys, force_check=False):
        """Return whether any one of a set of keys was pressed since the last
        keyboard check.

        :param keys: A list of keys to check.
        :param force_check: If `True`, check keys even if Eric is writing on a
                            blackboard.
        """
        pressed = False
        if not self.writing or force_check:
            for event in self.key_down_events:
                if event.key in keys:
                    self.key_down_events.remove(event)
                    pressed = True
        return pressed

    def pressed(self, keys):
        """Return whether any one of a set of keys either is being pressed or
        was pressed since the last keyboard check.

        :param keys: A list of keys to check.
        """
        return self.was_pressed(keys) or self.is_pressed(keys)
