# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2012-2015 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Game` class.
"""

import sys
import gzip
import os
import pickle
import pygame
import random
import time

from .cast import Cast
from .character import Character
from .skool import Skool
from .graphics import Screen, Gallery
from .sound import Beeper
from .input import Keyboard
from .iniparser import IniParser
from . import skoolbuilder
from . import keys
from . import items
from . import debug

#: Menu operation: Resume.
RESUME = 'RESUME'
#: Menu operation: Save.
SAVE = 'SAVE'
#: Menu operation: Load.
LOAD = 'LOAD'
#: Menu operation: Quit.
QUIT = 'QUIT'
#: Menu operation: Increase scale.
SCALE_UP = 'SCALE_UP'
#: Menu operation: Decrease scale.
SCALE_DOWN = 'SCALE_DOWN'
#: Menu operation: Toggle fullscreen mode.
TOGGLE_FULLSCREEN = 'TOGGLE_FULLSCREEN'
#: Menu operation: Update the screen.
UPDATE = 'UPDATE'

class Game:
    """Builds the skool and the cast, and executes the main loop of the
    game.

    :param ini_file: The main Pyskool ini file.
    :param images_dir: The path to the `images` directory.
    :param sounds_dir: The path to the `sounds` directory.
    :type scale: number
    :param ini_dir: The directory to scan for game ini files.
    :param options: Options passed from the command line.
    :type version: string
    :param version: The version number of Pyskool.
    :param sav_file: A file from which to restore a saved game.
    """
    def __init__(self, ini_file, images_dir, sounds_dir, ini_dir, options, version, sav_file):
        # Reduce latency in Pygame 1.8+
        pygame.mixer.pre_init(44100, -16, 1, 1024)
        pygame.init()
        if pygame.mixer.get_init() is None:
            sys.stdout.write("WARNING: pygame.mixer failed to initialise; there will be no sound\n")

        parser = IniParser(ini_file)
        self._create_key_bindings(parser.parse_section('Keys'))

        self.menus = {}
        self.menu_config = {}
        for menu_name in ('Main', 'Quit'):
            self.menu_config[menu_name] = (
                parser.get_config('Menu {0}'.format(menu_name)),
                parser.parse_section('MenuItems {0}'.format(menu_name))
            )

        self.images_dir = images_dir
        self.sounds_dir = sounds_dir
        self.speed = 1
        self.screenshot = 0
        self.version = version
        self.screen = None
        self.menu = None

        builder = skoolbuilder.SkoolBuilder(ini_dir)
        builder.sections['ExtraConfig'] = options.config or []
        config = builder.get_config('[A-Za-z]+Config')
        self.scale = options.scale or config.get('Scale', 2)
        self.cheat = options.cheat or config.get('Cheat', 0)
        self.quick_start = options.quick_start or config.get('QuickStart', 0)
        self.ring_bell = not self.quick_start
        self.confirm_close = config.get('ConfirmClose', 0)
        self.confirm_quit = config.get('ConfirmQuit', 1)

        if sav_file:
            if os.path.isfile(sav_file):
                self.quick_start = True
                self.ring_bell = True
                self._load(sav_file)
                return
            debug.log('Unable to restore from %s: file not found' % sav_file)

        image_set = config.get('ImageSet', 'original')
        gallery = Gallery(images_dir, image_set, self.scale, builder.get_config(skoolbuilder.IMAGES))
        title_prefix = 'Pyskool %s: ' % version
        self.screen = Screen(config, gallery, title_prefix)
        self.beeper = Beeper(sounds_dir, config)
        self.cast = Cast(config, self.screen, gallery)
        self.skool = Skool(config, self.screen, self.beeper, self.cast, gallery)
        builder.build_skool(self.skool)
        self.keyboard = Keyboard()
        self.skool.initialise_cast(self.keyboard)
        self.screen.initialise_column(self.skool.get_width(), self.cast.eric.x)
        self.screen.setup()
        self.skool.update_score_box()
        self._build_menus()

    def _build_menus(self):
        """Build the menus."""
        for menu_name, (menu_config, menu_items) in self.menu_config.items():
            self.menus[menu_name] = Menu(self.screen, menu_config, menu_items)

    def _build_menu_images(self):
        for menu in self.menus.values():
            menu.build_images(self.screen)

    def _handle_menu(self):
        """Handle keypresses while a menu is displayed."""
        draw = False
        refresh = False
        status = ''
        operation = self.menu.get_operation(self.keyboard)
        if operation == UPDATE:
            draw = True
        elif operation == RESUME:
            self.menu = None
            self.skool.draw()
        elif operation == SAVE:
            sav_file = self._save_game()
            status = 'Saved %s' % sav_file
        elif operation == LOAD:
            sav_file = self._load_last()
            status = 'Loaded %s' % sav_file if sav_file else 'No saved games found'
            self.skool.draw(False)
            refresh = True
        elif operation == SCALE_UP:
            self.screen.scale_up()
            self.skool.restore()
            self.skool.draw(False)
            refresh = True
            status = 'Scale set to %i' % self.screen.scale
            self._build_menu_images()
        elif operation == SCALE_DOWN:
            if self.screen.scale_down():
                self.skool.restore()
                self.skool.draw(False)
                refresh = True
                status = 'Scale set to %i' % self.screen.scale
                self._build_menu_images()
        elif operation == TOGGLE_FULLSCREEN:
            pygame.display.toggle_fullscreen()
        elif operation == QUIT:
            return True
        if draw or status:
            self.menu.status = status
            self.screen.draw_menu(self.menu, refresh)
        self.clock.tick(10)
        self.keyboard.pump()
        return False

    def _create_key_bindings(self, keydefs):
        """Create the key bindings.

        :param keydefs: Key definitions.
        """
        for keydef in keydefs:
            action = keydef[0]
            bindings = []
            for kdef in keydef[1:]:
                try:
                    bindings.append(getattr(pygame, 'K_%s' % kdef))
                except AttributeError:
                    debug.log('%s: key ID not recognised' % kdef)
            if bindings:
                setattr(keys, action, bindings)

    def _no_lines(self, *args):
        """Method used to replace
        :meth:`~pyskool.character.Character.give_lines` when the
        :data:`~pyskool.keys.NO_LINES` cheat key is pressed. The method does
        nothing.
        """
        return
    _give_lines = Character.give_lines

    def _save(self, fname):
        """Save the current game state.

        :param fname: The name of the file to save to.
        """
        save_game_dir = os.path.join(*self.skool.save_game_dir.split('/'))
        if not os.path.isdir(save_game_dir):
            os.makedirs(save_game_dir)
        ofile = os.path.join(save_game_dir, fname)
        f = gzip.open(ofile, 'wb', self.skool.save_game_compression)
        pickle.dump(self.skool, f)
        f.close()
        debug.log('Skool saved to %s' % os.path.abspath(ofile))

    def _load(self, fname):
        """Load a saved game.

        :param fname: The name of the file to load from.
        """
        scale = self.screen.scale if self.screen else self.scale
        start = time.time()
        f = gzip.open(fname, 'rb')
        self.skool = pickle.load(f)
        f.close()

        # Restore instance variables
        self.screen = self.skool.screen
        self.beeper = self.skool.beeper
        self.cast = self.skool.cast
        self.keyboard = self.cast.eric.keyboard

        # Perform necessary post-load tasks
        if scale:
            self.screen.scale = scale
        self.skool.beeper.restore(self.sounds_dir)
        self.skool.gallery.restore(self.images_dir)
        self.skool.restore()
        self._build_menus()

        debug.log('Skool loaded from %s in %0.2fs' % (os.path.abspath(fname), time.time() - start))

    def _save_game(self):
        """Save the game."""
        fname = '%s.sav' % time.strftime('%Y%m%d-%H%M%S')
        self._save(fname)
        return fname

    def _load_last(self):
        """Load the most recently saved game."""
        save_game_dir = os.path.abspath(self.skool.save_game_dir)
        if not os.path.isdir(save_game_dir):
            debug.log("Cannot load games from '%s': directory not found" % save_game_dir)
            return
        sav_files = [f for f in os.listdir(save_game_dir) if f.endswith('.sav') and os.path.isfile(os.path.join(save_game_dir, f))]
        if not sav_files:
            debug.log("No saved games found in '%s'" % save_game_dir)
            return
        sav_files.sort()
        sav_file = sav_files[-1]
        self._load(os.path.join(save_game_dir, sav_file))
        return sav_file

    def _check_cheat_keys(self):
        """Check whether any cheat keys were pressed, and take appropriate
        action. This method is called from the main loop.
        """
        if self.keyboard.is_pressed(keys.SLOW):
            self.speed = 0.5
        elif self.keyboard.is_pressed(keys.FAST):
            self.speed = 2
        else:
            self.speed = 1
        if self.keyboard.was_pressed(keys.NEXT_LESSON):
            self.skool.next_lesson(False)
        if self.skool.shields:
            if self.keyboard.was_pressed(keys.FLASH_MOST):
                for shield in self.skool.shields[1:]:
                    shield.flash()
                self.skool.unflash(self.skool.shields[0])
                self.skool.unflash(self.skool.safe)
                self.skool.shield_mode = 1
                debug.log('Flashed all but one shield; hit it and then open the safe')
            if self.keyboard.was_pressed(keys.UNFLASH_MOST):
                for shield in self.skool.shields[1:]:
                    self.skool.unflash(shield)
                self.skool.shields[0].flash()
                self.skool.safe.flash()
                self.skool.shield_mode = 3
                debug.log('Unflashed all but one shield; hit it to go up a year')
        if self.keyboard.was_pressed(keys.NO_LINES):
            if Character.give_lines == self._no_lines:
                Character.give_lines = self._give_lines
                debug.log('Enabled lines-giving')
            else:
                Character.give_lines = self._no_lines
                debug.log('Disabled lines-giving')
        if self.keyboard.was_pressed(keys.ADD_LINES):
            lines = 100 * random.randrange(*self.cast.lines_range)
            self.skool.add_lines(lines)
            debug.log('Added %i lines' % lines)
        if self.keyboard.was_pressed(keys.ZERO_LINES):
            self.skool.add_lines(-self.skool.scoreboard.lines)
            debug.log('Set lines total to zero')
        if self.keyboard.was_pressed(keys.REVEAL):
            for room in self.skool.rooms.values():
                for desk in room.desks:
                    if desk.contents:
                        debug.log('%s x=%i: %s' % (room.name, desk.x, desk.contents))
            for c in self.cast.character_list:
                if c.special_answer:
                    debug.log('%s: %s' % (c.name, c.special_answer))
            if self.skool.safe_combination:
                debug.log('Safe: %s' % self.skool.safe_combination)
            if self.skool.bike_combination:
                debug.log('Bike: %s' % self.skool.bike_combination)
            if self.skool.storeroom_combination:
                debug.log('Storeroom: %s' % self.skool.storeroom_combination)
        if self.skool.inventory_item_ids:
            eric = self.cast.eric
            inventory = eric.inventory
            if self.keyboard.was_pressed(keys.SWITCH_PISTOL):
                if items.WATER_PISTOL in inventory:
                    inventory.remove(items.WATER_PISTOL)
                    inventory.add(items.SHERRY_PISTOL)
                elif items.SHERRY_PISTOL in inventory:
                    inventory.remove(items.SHERRY_PISTOL)
                    inventory.add(items.WATER_PISTOL)
                eric.print_inventory()
            if self.keyboard.was_pressed(keys.GIVE_ALL):
                inventory.update((items.SAFE_KEY, items.STOREROOM_KEY, items.FROG, items.WATER_PISTOL, items.STINKBOMBS3))
                if self.cast.frogs:
                    self.cast.frogs[0].hide()
                eric.mice = 8
                eric.print_inventory()
                eric.print_mouse_inventory()
                self.skool.unchain_bike()
        if self.skool.doors:
            if self.keyboard.was_pressed(keys.OPEN_DOORS):
                for door_id in self.skool.doors:
                    self.skool.move_door(door_id, False)
                for window_id in self.skool.windows:
                    self.skool.move_door(window_id, False)
                debug.log('Opened all doors and windows')
            if self.keyboard.was_pressed(keys.CLOSE_DOORS):
                for door_id in self.skool.doors:
                    self.skool.move_door(door_id, True)
                for window_id in self.skool.windows:
                    self.skool.move_door(window_id, True)
                debug.log('Closed all doors and windows')

    def _take_screenshot(self):
        """Take a screenshot."""
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        img_fname = '{}-{:03d}.png'.format(timestamp, self.screenshot)
        scrshot_dir = self.skool.screenshot_dir
        if not os.path.isdir(scrshot_dir):
            os.makedirs(scrshot_dir)
        img_path = os.path.join(scrshot_dir, img_fname)
        self.screen.take_screenshot(img_path)
        self.screenshot += 1
        debug.log('Took screenshot: {}'.format(img_path))

    def play(self):
        """Start the game and enter the main loop."""
        self.clock = pygame.time.Clock()
        self.paused = False

        while True:
            self.scroll = 0

            if not self.quick_start:
                self.skool.scroll_on(self.clock)

            self.quick_start = False

            while not self.skool.game_over:
                if self._main_loop():
                    return

            self.skool.reinitialise()

    def _main_loop(self):
        """The main loop of the game. The following things are done in the main
        loop:

        * check the keyboard and act on keypresses
        * advance the skool clock
        * move the characters
        * shut any auto-shutting doors that need shutting
        * update the screen
        * scroll the screen if necessary

        :return: `True` if the game is quitting, `False` otherwise.
        """
        if self.keyboard.was_pressed(keys.FULL_SCREEN, force_check=True):
            pygame.display.toggle_fullscreen()
            return False

        if self.keyboard.was_pressed(keys.SCREENSHOT, force_check=True):
            self._take_screenshot()

        if self.menu:
            return self._handle_menu()

        show_quit_menu = False
        if self.keyboard.got_quit():
            if not self.confirm_close:
                return True
            show_quit_menu = True
        elif self.keyboard.was_pressed(keys.QUIT, force_check=True):
            if not self.confirm_quit:
                return True
            show_quit_menu = True
        if show_quit_menu:
            self.menu = self.menus['Quit']
            self.menu.reset()
            self.screen.draw_menu(self.menu)
            self.beeper.pause()
            return False

        self.paused ^= self.keyboard.was_pressed(keys.PAUSE, force_check=True)
        if self.paused:
            self.beeper.pause()
            self.clock.tick(10)
            self.keyboard.pump()
            return False

        self.beeper.unpause()
        if self.beeper.is_busy():
            self.keyboard.pump()
            return False

        if self.skool.suspended:
            # The skool was suspended while a sound effect played; now resume
            if not self.skool.locked:
                self.skool.draw()
                if self.scroll:
                    self.skool.scroll(self.scroll, self.clock)
                    self.scroll = 0
            self.skool.resume()
            return False

        if self.skool.tick():
            self.skool.next_lesson(self.ring_bell)
            self.ring_bell = True
            if self.skool.suspended:
                return False

        if self.cheat:
            self._check_cheat_keys()

        self.scroll = self.skool.move_characters()
        if self.skool.suspended:
            return False

        self.skool.auto_shut_doors()
        self.clock.tick(self.screen.fps * self.speed)
        self.skool.draw()
        self.skool.scroll(self.scroll, self.clock)

        if self.keyboard.was_pressed(keys.MENU, force_check=True):
            self.menu = self.menus['Main']
            self.menu.reset()
            self.screen.draw_menu(self.menu)
        elif self.keyboard.was_pressed(keys.SAVE, force_check=True):
            self._save_game()
        elif self.keyboard.was_pressed(keys.LOAD, force_check=True):
            self._load_last()

        return False

class Menu:
    """The in-game menu.

    :type screen: :class:`~pyskool.graphics.Screen`
    :param screen: The screen (to draw the menu on).
    :type config: dict
    :param config: Configuration parameters.
    :param items: The menu items (`(operation, label)` tuples).
    """
    def __init__(self, screen, config, items):
        self.ink = config.get('Ink', (255, 255, 255))
        self.paper = config.get('Paper', (255, 0, 0))
        self.highlight = config.get('Highlight', (200, 0, 0))
        self.status_bar = config.get('StatusBar', 1)
        self.status_paper = config.get('StatusPaper', (100, 100, 100))
        self.title_paper = config.get('TitlePaper', (100, 100, 100))
        self.width = config.get('Width', 0.9)
        self.title_text = config.get('Title', 'Menu')
        self.alpha = config.get('Alpha', 224)
        self.items = items
        self.build_images(screen)
        self.reset()

    def reset(self):
        """Reset the menu. Specifically:

        * set the selected index to 0
        * clear the status text
        * clear the backdrop on which the menu is drawn
        """
        self.selected_index = 0
        self.status = ''
        self.backdrop = None

    def build_images(self, screen):
        """Build the title image and menu item images."""
        self.title = screen.get_text(self.title_text, self.ink, self.title_paper)
        self.images = []
        for operation, label in self.items:
            self.images.append(screen.get_text(label, self.ink, self.paper))
        self.backdrop = None

    def get_operation(self, keyboard):
        """Return the operation to perform (which may be `None`)."""
        operation = None
        if keyboard.was_pressed(keys.MENU_EXIT, force_check=True):
            return RESUME
        if keyboard.was_pressed(keys.MENU_PREV, force_check=True):
            self.selected_index -= 1
            operation = UPDATE
        elif keyboard.was_pressed(keys.MENU_NEXT, force_check=True):
            self.selected_index += 1
            operation = UPDATE
        elif keyboard.was_pressed(keys.MENU_EXEC, force_check=True):
            operation = self.items[self.selected_index][0]
        self.selected_index = self.selected_index % len(self.items)
        return operation
