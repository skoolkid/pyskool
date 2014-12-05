# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2013, 2014 Richard Dymond (rjdymond@gmail.com)
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
Play sound effects.
"""

import pygame
import os
import random

from . import debug

#: ID of the sound effect to play when Albert tells Mr Wacker that Eric is
#: escaping.
ALARM = 'ALARM'
#: ID of the sound effect to play when all the shields have been flashed.
ALL_SHIELDS = 'ALL_SHIELDS'
#: ID of the sound effect for the bell.
BELL = 'BELL'
#: ID of the sound effect to play when the bike is unchained.
BIKE = 'BIKE'
#: ID of the sound effect to play when Eric's catapult is fired.
CATAPULT = 'CATAPULT'
#: ID of the sound effect to play when Albert is knocked unconscious by the
#: conker.
CONKER = 'CONKER'
#: ID of the sound effect to play when Eric finds something in a desk.
DESK = 'DESK'
#: ID of the sound effect to play when Eric catches the frog or places it in a
#: cup.
FROG = 'FROG'
#: Hitting sound effect IDs.
HIT_SOUNDS = ('HIT0', 'HIT1')
#: ID of the sound effect to play when Eric kisses someone.
KISS = 'KISS'
#: ID of the sound effect to play when Eric jumps.
JUMP = 'JUMP'
#: ID of the sound effect to play when Eric is knocked over.
KNOCKED_OUT = 'KNOCKED_OUT'
#: ID of lines sound effect 1.
LINES1 = 'LINES1'
#: ID of lines sound effect 2.
LINES2 = 'LINES2'
#: ID of the sound effect to play when a mouse is caught.
MOUSE = 'MOUSE'
#: ID of the sound effect to play when the safe is opened (with the
#: combination).
OPEN_SAFE = 'OPEN_SAFE'
#: ID of the sound effect to play when Eric gets the safe key.
SAFE_KEY = 'SAFE_KEY'
#: ID of the sound effect to play when Eric fills the water pistol with sherry.
SHERRY = 'SHERRY'
#: ID of the sound effect to play when a shield is hit.
SHIELD = 'SHIELD'
#: ID of the sound effect to play when Eric gets the storeroom key.
STOREROOM_KEY = 'STOREROOM_KEY'
#: ID of the opening tune.
TUNE = 'TUNE'
#: ID of the sound effect to play when Eric goes up a year.
UP_A_YEAR = 'UP_A_YEAR'
#: Walking sound effect IDs.
WALK_SOUNDS = ('WALK0', 'WALK1', 'WALK2', 'WALK3')
#: ID of the sound effect to play when Eric's water pistol is fired.
WATER_PISTOL = 'WATER_PISTOL'

#: Sound effect play mode: suspend character movement and screen updates.
SUSPEND = 1
#: Sound effect play mode: asynchronous.
ASYNC = 2

class Beeper:
    """The maker of sound effects.

    :param sounds_dir: The path to the `sounds` directory.
    :type config: dict
    :param config: Configuration parameters from the ini file.
    """
    def __init__(self, sounds_dir, config):
        self.sounds_dir = sounds_dir
        self.sound_files = {}
        self.sounds = {}
        self.channel = None
        self.paused = False
        self.volume = min(max(0.0, config.get('Volume', 1.0)), 1.0)

    def __getstate__(self):
        d = self.__dict__.copy()
        d['sounds_dir'] = None
        d['sounds'] = None
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.sounds_dir = None
        self.sounds = {}

    def restore(self, sounds_dir):
        """Perform tasks required immediately after loading a saved game.

        :param sounds_dir: The path to the `sounds` directory.
        """
        self.sounds_dir = sounds_dir
        for sound_id, sound_file in self.sound_files.items():
            self._load_sound(sound_id, sound_file)

    def _load_sound(self, sound_id, sound_file):
        """Load a sound effect from a file.

        :param sound_id: The ID of the sound effect.
        :param sound_file: The file name of the sound effect (relative to the
                           `sounds` directory).
        """
        if pygame.mixer.get_init() is None:
            return
        fname = os.path.join(*sound_file.split('/'))
        base_path = os.path.join(self.sounds_dir, fname)
        for suffix in ('', '.wav', '.ogg'):
            path = base_path + suffix
            if os.path.isfile(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_id] = sound
                except pygame.error as e:
                    debug.log("Unable to load sound effect '%s' from %s: %s" % (sound_id, path, e.args[0]))
                return
        debug.log("Unable to load sound effect '%s' from %s{,.wav,.ogg}: file not found" % (sound_id, base_path))

    def add_sound(self, sound_id, sound_file):
        """Add a sound effect to the beeper's collection.

        :param sound_id: The ID of the sound effect.
        :param sound_file: The file name of the sound effect (relative to the
                           `sounds` directory).
        """
        self.sound_files[sound_id] = sound_file
        self._load_sound(sound_id, sound_file)

    def play(self, sound_id, mode=SUSPEND):
        """Play a sound effect.

        :param sound_id: The ID of the sound effect.
        :param mode: If :data:`SUSPEND`, movement of characters and screen
                     updates are suspended until the sound effect has finished
                     playing, but the quit and pause keys will be checked in
                     the meantime; if :data:`ASYNC` (or anything else), the
                     sound effect will play asynchronously.
        """
        if sound_id not in self.sounds:
            return
        channel = self.sounds[sound_id].play()
        if mode == SUSPEND:
            self.channel = channel

    def is_busy(self):
        """Return whether a sound effect is being played at the moment in
        :data:`SUSPEND` mode.
        """
        if self.channel:
            if self.channel.get_busy():
                return True
            self.channel = None
        return False

    def pause(self):
        """Pause the playing of any sound effect."""
        if not self.paused and self.is_busy():
            self.channel.pause()
            self.paused = True

    def unpause(self):
        """Resume the playing of any sound effect."""
        if self.paused and self.is_busy():
            self.channel.unpause()
            self.paused = False

    def make_walking_sound(self, index, mode):
        """Play a walking sound effect.

        :param index: The index of the walking sound effect.
        :param mode: The mode in which to play the sound effect (see
                     :meth:`play`).
        """
        self.play(WALK_SOUNDS[index % len(WALK_SOUNDS)], mode)

    def make_sitting_sound(self, mode):
        """Play a sitting sound effect. This will be a walking sound effect,
        chosen at random from those available.

        :param mode: The mode in which to play the sound effect (see
                     :meth:`play`).
        """
        self.play(random.choice(WALK_SOUNDS), mode)
