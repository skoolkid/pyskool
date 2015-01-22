# -*- coding: utf-8 -*-
# Copyright 2008-2010, 2013-2015 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Skool` class.
"""

import random

from .barrier import Door, Wall, Window
from .floor import Floor
from .plant import PlantPot
from .lesson import AssemblyMessageGenerator
from .mutable import Shield, Safe, Cup, Bike
from .room import Room, NoGoZone
from .staircase import Staircase
from .scoreboard import Scoreboard
from .location import Location
from .timetable import Timetable
from . import items
from . import sound
from . import graphics
from . import debug

class Skool:
    """Represents the play area and its features and fixtures.

    :type config: dict
    :param config: Configuration parameters from the ini file.
    :type screen: :class:`~pyskool.graphics.Screen`
    :param screen: The screen to draw on.
    :type beeper: :class:`~pyskool.sound.Beeper`
    :param beeper: The beeper to use.
    :type cast: :class:`~pyskool.cast.Cast`
    :param cast: The cast of characters.
    :type gallery: :class:`~pyskool.graphics.Gallery`
    :param gallery: The gallery to obtain skool images from.
    """
    def __init__(self, config, screen, beeper, cast, gallery):
        self.screen = screen
        self.mode = screen.mode
        self.beeper = beeper
        self.cast = cast
        self.gallery = gallery
        self.skool = None if self.mode == 1 else gallery.get_image(graphics.SKOOL)
        self.ink = gallery.get_image(graphics.SKOOL_INK) if self.mode == 1 else None
        self.paper = gallery.get_image(graphics.SKOOL_PAPER) if self.mode == 1 else None
        self.mutables = gallery.get_image(graphics.MUTABLES)
        self.mutables_ink = gallery.get_image(graphics.MUTABLES_INK)
        self.mutables_paper = gallery.get_image(graphics.MUTABLES_PAPER)
        self.inventory = gallery.get_image(graphics.INVENTORY)
        self.inventory_images = {}
        self.inventory_item_ids = []
        self.timetable = Timetable(config)
        self.scoreboard = Scoreboard(screen)
        self.locations = {}
        self.rooms = {}
        self.doors = {}
        self.windows = {}
        self.walls = {}
        self.barriers = {} # Doors, windows and walls
        self.staircases = {}
        self.floors = {}
        self.routes = {}
        self.no_go_zones = []
        self.assembly_message_generator = AssemblyMessageGenerator()
        self.shields = []
        self.shield_mode = 1
        self.safe_combination = None
        self.bike_combination = None
        self.storeroom_combination = None
        self.draw_index = 0
        self.signals = {}
        self.messages = {}
        self.cups = {}
        self.plant_pots = {}
        self.bike = None
        self.clear_score = True

        self.screenshot_dir = config.get('ScreenshotDir', 'screenshots')
        self.save_game_dir = config.get('SaveGameDir', 'save')
        self.save_game_compression = config.get('SaveGameCompression', 9)
        self.flash_cycle = config.get('FlashCycle', 10)
        self.lines_message_template = config.get('LinesMessageTemplate', '$n LINES^$r')
        self.num_lines_macro = config.get('NumberOfLinesMacro', '$n')
        self.lines_recipient_macro = config.get('LinesRecipientMacro', '$r')
        self.max_lines = config.get('MaxLines', 10000)
        self.all_shields_score = config.get('AllShieldsScore', 0)
        self.safe_open_score = config.get('SafeOpenScore', 0)
        self.up_a_year_score = config.get('UpAYearScore', 2000)
        self.up_a_year_message = config.get('UpAYearMessage', 'WELL DONE! GO^UP A YEAR')
        self.restart_on_year_end = config.get('RestartOnYearEnd', 0)
        self.play_tune_on_restart = config.get('PlayTuneOnRestart', 0)
        self.too_many_lines = config.get('TooManyLinesCommandList', 'ExpelEric:TooManyLines')
        self.expeller_id = config.get('ExpellerId', 'WACKER')
        self.window_proximity = config.get('WindowProximity', 16)
        self.newline = config.get('Newline', '^')[0]
        self.drinks_cabinet_door_id = config.get('DrinksCabinetDoorId', 'DrinksCabinet')
        self.playground = config.get('Playground')
        self.location_marker = config.get('LocationMarker', 'Location:')

        self.inverse = 0
        self.game_over = False
        self.play_tune = True
        self.suspended = False
        self.pre_resume = None

        # `locked` is set to True to prevent screen updates between two sound
        # effects played one after the other (such as the shield sound effect
        # when the final shield is hit, and the celebratory tune that follows;
        # see Game._main_loop())
        self.locked = False

    def _up_a_year(self):
        """Make Eric go up a year (after opening the safe, or unflashing all
        the shields). The up-a-year tune is played and points are awarded. When
        the tune has finished, :meth:`_begin_year` is called.
        """
        self.screen.print_lesson(*self.expand_message(self.up_a_year_message))
        self.add_to_score(self.up_a_year_score)
        self.play_sound(sound.UP_A_YEAR, pre_resume=self._begin_year)

    def _begin_year(self):
        """Begin a new year at skool. This means either starting a new game, or
        resetting the shields, safe and safe combination.
        """
        self.locked = False
        if self.restart_on_year_end:
            self.end_game(True)
        else:
            self.shield_mode = 1
            if self.safe:
                self.unflash(self.safe)
                self.initialise_safe_combo()
            self.timetable.up_a_year()

    def _get_character(self, character_id):
        """Return a character.

        :param character_id: The ID of the character.
        """
        return self.cast.get(character_id)

    def got_safe_combination(self):
        """Return whether the safe combination is written on any of the
        blackboards in the skool.
        """
        for room in self.rooms.values():
            board = room.blackboard
            if board and board.shows(self.safe_combination):
                return True
        return False

    def got_bike_combination(self, blackboard):
        """Return whether the bike combination is written on a blackboard.

        :type blackboard: :class:`~pyskool.room.Blackboard`
        :param blackboard: The blackboard to check.
        """
        return self.bike_combination and blackboard.shows(self.bike_combination, False)

    def got_storeroom_combination(self, blackboard):
        """Return whether the storeroom combination is written on a blackboard.

        :type blackboard: :class:`~pyskool.room.Blackboard`
        :param blackboard: The blackboard to check.
        """
        return self.storeroom_combination and blackboard.shows(self.storeroom_combination, False)

    def can_reveal_safe_secret(self, flashing):
        """Return whether safe combination letters can be revealed now. This
        will be `True` only if the following conditions are met:

          * the safe has not been opened yet
          * all the shields are flashing, or `flashing` is `False`
        """
        if flashing:
            return self.shield_mode == 2
        return self.shield_mode <= 2

    def get_room(self, room_id):
        """Return the room with a given ID.

        :param room_id: The ID of the room.
        """
        return self.rooms.get(room_id, None)

    def get_door(self, door_id):
        """Return the door or window with a given ID.

        :param door_id: The ID of the door or window.
        """
        return self.doors.get(door_id, None)

    def next_staircase(self, home_floor, dest_floor):
        """Return the next staircase that any character on one floor (the home
        floor) should ascend or descend next to reach another floor (the
        destination floor).

        :param home_floor: The home floor.
        :param dest_floor: The destination floor.
        """
        if home_floor is None:
            debug.log('Cannot determine next staircase when home floor is None')
            return None
        if dest_floor is None:
            debug.log('Cannot determine next staircase when destination floor is None')
            return None
        if home_floor is dest_floor:
            return None
        routes = self.routes[home_floor.floor_id]
        staircase_id = routes.get(dest_floor.floor_id, routes['*'])
        return self.staircases[staircase_id]

    def hide_in_desk(self, item):
        """Hide an item (stinkbombs or a water pistol) in a desk.

        :param item: The item to hide.
        """
        desks = self._get_desks()
        while desks:
            desk = desks.pop(random.randrange(len(desks)))
            if not desk.contents:
                desk.insert(item)
                break

    def is_door_shut(self, barrier_id):
        """Return whether a door or window is shut.

        :param barrier_id: The ID of the door or window.
        """
        return self.barriers[barrier_id].is_shut()

    def move_bike_away(self, barrier_id):
        """Move the bike away from a door if necessary (so that it may be
        closed).

        :param barrier_id: The ID of the door.
        """
        door = self.doors.get(barrier_id)
        if door:
            self.cast.move_bike_away(door)

    def line_of_sight_between(self, a, b):
        """Return whether there is a clear line of sight between two points
        (that is, there are no walls between them).
        """
        return not any(wall.separates(a, b) for wall in self.walls.values())

    def move_characters(self):
        """Move the characters.

        :return: -1 if the screen should scroll right, 1 if it should scroll
                 left, or 0 if it should not scroll (after moving Eric).
        """
        if self.suspended:
            return 0
        return self.cast.move()

    def expel_eric(self, command_list_id):
        """Set whoever is responsible for expelling Eric on his way.

        :param command_list_id: The ID of the command list the expeller should
                                switch to.
        """
        self.cast.change_command_list(self.expeller_id, command_list_id)

    def end_game(self, up_a_year=False):
        """Indicate that the game should restart. The score will be cleared if
        Eric was expelled, or retained if he went up a year.

        :param up_a_year: Whether Eric has gone up a year.
        """
        self.clear_score = not up_a_year
        self.play_tune = not up_a_year or self.play_tune_on_restart
        self.game_over = True

    #//////////////////////////////////////////////////////////////////////////
    # Initialisation
    #//////////////////////////////////////////////////////////////////////////
    def initialise_safe_combo(self):
        """Initialise the safe combination."""
        letters = self.cast.initialise_safe_combo()
        if letters:
            self.safe_combination = letters[0]
            indexes = [n for n in range(1, len(letters))]
            while indexes:
                self.safe_combination += letters[indexes.pop(random.randrange(len(indexes)))]

    def initialise_bike_combo(self):
        """Initialise the bike combination."""
        self.bike_combination = self.cast.initialise_bike_combo()

    def initialise_storeroom_combo(self):
        """Initialise the storeroom combination."""
        self.storeroom_combination = self.cast.initialise_storeroom_combo()

    def initialise_cast(self, keyboard):
        """Initialise the cast and the safe, bike and storeroom
        combinations.

        :type keyboard: :class:`~pyskool.input.Keyboard`
        :param keyboard: The keyboard for Eric to use.
        """
        self.cast.initialise(self, keyboard)
        self.initialise_safe_combo()
        self.initialise_bike_combo()
        self.initialise_storeroom_combo()

    def reinitialise(self):
        """Reinitialise the skool in preparation for a new game."""
        self.screen.reinitialise()
        self._clear_signals()
        self.cast.reinitialise()
        self.initialise_safe_combo()
        self.initialise_bike_combo()
        self.initialise_storeroom_combo()
        self.timetable.reinitialise()
        if self.clear_score:
            self.scoreboard.reinitialise()
        for room in self.rooms.values():
            room.wipe_blackboard()
        self.shield_mode = 1
        for shield in self.shields:
            self.unflash(shield)
        if self.safe:
            self.unflash(self.safe)
        self.fill_desks()
        for cup_id in self.cups:
            self.fill_cup(cup_id, None)
        for door in self.doors.values():
            self.move_door(door.barrier_id, door.initially_shut)
        for window in self.windows.values():
            self.move_door(window.barrier_id, door.initially_shut)
        self.chain_bike()
        self.game_over = False

    def _get_desks(self):
        """Return a list of all the desks in the skool."""
        desks = []
        for room in self.rooms.values():
            desks.extend(room.desks)
        return desks

    def fill_desks(self):
        """Hide the water pistol and stinkbombs in randomly chosen desks."""
        desks = self._get_desks()
        if not desks:
            return
        for desk in desks:
            desk.empty()
        desks.pop(random.randrange(len(desks))).insert(items.WATER_PISTOL)
        if desks:
            random.choice(desks).insert(items.STINKBOMBS3)

    #//////////////////////////////////////////////////////////////////////////
    # Skool construction
    #//////////////////////////////////////////////////////////////////////////
    def add_location(self, location_id, coords):
        """Add a named location. Named locations can be used by the
        :class:`~pyskool.ai.GoTo` command.

        :param location_id: The name of the location.
        :param coords: The coordinates of the location (as a 2-tuple).
        """
        self.locations[location_id] = coords

    def add_room(self, room_id, name, top_left, bottom_right, get_along):
        """Add a room to the skool.

        :param room_id: The room's unique ID.
        :param name: The room's name (as it will appear in the lesson box).
        :param top_left: The coordinates of the top-left corner of the room.
        :param bottom_right: The coordinates of the bottom-right corner of the
                             room.
        :param get_along: Whether Eric should be told to get a move on if he's
                          spotted in this room when the timetable says he
                          should be somewhere else.
        """
        self.rooms[room_id] = Room(room_id, name, top_left, bottom_right, get_along)

    def add_chair(self, room_id, x):
        """Add a chair to a classroom in the skool.

        :param room_id: The ID of the classroom.
        :param x: The x-coordinate of the chair.
        """
        self.rooms[room_id].add_chair(x)

    def add_desk(self, room_id, x):
        """Add a desk to a classroom in the skool.

        :param room_id: The ID of the classroom.
        :param x: The x-coordinate of the desk.
        """
        self.rooms[room_id].add_desk(x)

    def add_door(self, door_id, x, bottom_y, top_y, initially_shut, auto_shut_delay, shut_top_left, size, coords, climb_phases, fly_phases):
        """Add a door to the skool.

        :param door_id: The door's unique ID.
        :param x: The door's x-coordinate.
        :param bottom_y: The y-coordinate of the bottom of the door.
        :param top_y: The y-coordinate of the top of the door.
        :param initially_shut: Whether the door is shut at the start of a game.
        :param auto_shut_delay: The delay before the door shuts automatically;
                                if zero or negative, the door will not shut
                                automatically.
        :param shut_top_left: The coordinates of the top left of the image of
                              the door when shut.
        :param size: The size of the image.
        :param coords: The coordinates of the door in the skool.
        :param climb_phases: The sequence of animation phases to use for Eric
                             if he climbs over the door when it's shut; if
                             empty, Eric will not be able to climb over the
                             door.
        :param fly_phases: The sequence of animation phases to use for Eric if
                           he flies over the door after hitting it while
                           standing on the saddle of the bike; if empty, Eric
                           will not be able to fly over the door.
        """
        door = Door(door_id, x, bottom_y, top_y, initially_shut, auto_shut_delay, climb_phases, fly_phases)
        self.doors[door_id] = door
        self.barriers[door_id] = door
        open_top_left = (shut_top_left[0] + size[0], shut_top_left[1])
        if self.mode == 0:
            shut_images = (self.mutables.subsurface(shut_top_left, size),)
            open_images = (self.mutables.subsurface(open_top_left, size),)
        else:
            shut_image_ink = self.mutables_ink.subsurface(shut_top_left, size)
            shut_image_paper = self.mutables_paper.subsurface(shut_top_left, size)
            shut_images = (shut_image_ink, shut_image_paper)
            open_image_ink = self.mutables_ink.subsurface(open_top_left, size)
            open_image_paper = self.mutables_paper.subsurface(open_top_left, size)
            open_images = (open_image_ink, open_image_paper)
        door.set_images(open_images, shut_images, coords)

    def add_window(self, window_id, x, bottom_y, top_y, initially_shut, opener_coords, shut_top_left, size, coords, descent_phases, not_a_bird):
        """Add a window to the skool.

        :param window_id: The window's unique ID.
        :param x: The window's x-coordinate.
        :param bottom_y: The y-coordinate of the bottom of the window.
        :param top_y: The y-coordinate of the top of the window.
        :param initially_shut: Whether the window is shut at the start of a
                               game.
        :param opener_coords: The coordinates at which a character should stand
                              to open or close the window.
        :param shut_top_left: The coordinates of the top left of the image of
                              the window when shut.
        :param size: The size of the image.
        :param coords: The coordinates of the window in the skool.
        :param descent_phases: The animation phases to use for Eric if he jumps
                               out of the window.
        :param not_a_bird: The ID of the command list Mr Wacker should switch
                           to when Eric hits the ground after jumping out of
                           the window; if not blank, Eric will be paralysed
                           when he hits the ground.
        """
        window = Window(window_id, x, bottom_y, top_y, initially_shut, opener_coords, descent_phases, not_a_bird)
        self.windows[window_id] = window
        self.barriers[window_id] = window
        open_top_left = (shut_top_left[0] + size[0], shut_top_left[1])
        if self.mode == 0:
            shut_images = (self.mutables.subsurface(shut_top_left, size),)
            open_images = (self.mutables.subsurface(open_top_left, size),)
        else:
            shut_image_ink = self.mutables_ink.subsurface(shut_top_left, size)
            shut_image_paper = self.mutables_paper.subsurface(shut_top_left, size)
            shut_images = (shut_image_ink, shut_image_paper)
            open_image_ink = self.mutables_ink.subsurface(open_top_left, size)
            open_image_paper = self.mutables_paper.subsurface(open_top_left, size)
            open_images = (open_image_ink, open_image_paper)
        window.set_images(open_images, shut_images, coords)

    def add_inventory_item(self, item_id, top_left, size):
        """Add an inventory item.

        :param item_id: The item's unique ID.
        :param top_left: The coordinates of the top left of the image of the
                         inventory item.
        :param size: The size of the image.
        """
        self.inventory_images[item_id] = self.inventory.subsurface(top_left, size)
        self.inventory_item_ids.append(item_id)

    def add_wall(self, wall_id, x, bottom_y, top_y):
        """Add a wall to the skool.

        :param wall_id: The wall's unique ID.
        :param x: The wall's x-coordinate.
        :param bottom_y: The y-coordinate of the bottom of the wall.
        :param top_y: The y-coordinate of the top of the wall.
        """
        wall = Wall(wall_id, x, bottom_y, top_y)
        self.walls[wall_id] = wall
        self.barriers[wall_id] = wall

    def add_staircase(self, staircase_id, bottom, top, force, alias):
        """Add a staircase to the skool.

        :param staircase_id: The unique ID of the staircase.
        :param bottom: The coordinates of the bottom of the staircase.
        :param top: The coordinates of the top of the staircase.
        :param force: If `True`, the staircase must be ascended or descended
                      when approached.
        :param alias: An alias for the staircase (may be blank).
        """
        staircase = Staircase(bottom, top, force)
        self.staircases[staircase_id] = staircase
        if alias:
            self.staircases[alias] = staircase

    def add_floor(self, floor_id, min_x, max_x, y):
        """Add a floor to the skool.

        :param floor_id: The floor's unique ID.
        :param min_x: The x-coordinate of the left edge of the floor.
        :param max_x: The x-coordinate of the right edge of the floor.
        :param y: The y-coordinate of the floor.
        """
        self.floors[floor_id] = Floor(floor_id, min_x, max_x, y)

    def add_routes(self, home_floor_id, dest_floor_ids, staircase_id):
        """Add routes from one floor (the home floor) to other floors.

        :param home_floor_id: The ID of the home floor.
        :param dest_floor_ids: The IDs of the destination floors.
        :param staircase_id: The ID of the first staircase to use when moving
                             from the home floor to any of the destination
                             floors.
        """
        if home_floor_id not in self.routes:
            self.routes[home_floor_id] = {}
        for dest_floor_id in dest_floor_ids:
            self.routes[home_floor_id][dest_floor_id] = staircase_id

    def add_blackboard(self, room_id, top_left, size, chalk):
        """Add a blackboard to a room in the skool.

        :param room_id: The ID of the room.
        :param top_left: The coordinates of the top-left of the blackboard.
        :param size: The size (width, height) of the blackboard.
        :param chalk: The chalk colour to use when writing on the blackboard.
        """
        skool_image = self.skool if self.mode == 0 else self.ink
        self.rooms[room_id].add_blackboard(self.screen, top_left, size, chalk, skool_image)

    def add_no_go_zone(self, zone_id, min_x, max_x, bottom_y, top_y):
        """Add a no-go zone to the skool.

        :param zone_id: The zone's unique ID.
        :param min_x: The x-coordinate of the left edge of the zone.
        :param max_x: The x-coordinate of the right edge of the zone.
        :param bottom_y: The y-coordinate of the bottom edge of the zone.
        :param top_y: The y-coordinate of the top edge of the zone.
        """
        self.no_go_zones.append(NoGoZone(zone_id, min_x, max_x, bottom_y, top_y))

    def _get_flashable(self, subclass, top_left, size, coords, score=0):
        """Return an instance of a flashable object (safe or shield).

        :param subclass: The class of the object
                         (:class:`~pyskool.mutable.Safe` or
                         :class:`~pyskool.mutable.Shield`).
        :param top_left: The coordinates of the top left of the image of the
                         object.
        :param size: The size of the image.
        :param coords: The coordinates of the object in the skool.
        :param score: The score for hitting the object (used only for shields).
        """
        if self.mode == 0:
            images = (self.mutables.subsurface(top_left, size),)
            inverse_images = (self.mutables.subsurface((top_left[0] + size[0], top_left[1]), size),)
        else:
            image_ink = self.mutables_ink.subsurface(top_left, size)
            image_paper = self.mutables_paper.subsurface(top_left, size)
            images = (image_ink, image_paper)
            inverse_image_ink = self.mutables_ink.subsurface((top_left[0] + size[0], top_left[1]), size)
            inverse_image_paper = self.mutables_paper.subsurface((top_left[0] + size[0], top_left[1]), size)
            inverse_images = (inverse_image_ink, inverse_image_paper)
        return subclass(coords[0], coords[1], images, inverse_images, score)

    def add_shield(self, score, top_left, size, coords):
        """Add a shield to the skool.

        :param top_left: The coordinates of the top left of the image of the
                         shield.
        :param size: The size of the image.
        :param coords: The coordinates of the shield in the skool.
        :param score: The score for hitting the shield.
        """
        shield = self._get_flashable(Shield, top_left, size, coords, score)
        self.shields.append(shield)

    def add_safe(self, top_left, size, coords):
        """Add a safe to the skool.

        :param top_left: The coordinates of the top left of the image of the
                         safe.
        :param size: The size of the image.
        :param coords: The coordinates of the safe in the skool.
        """
        self.safe = self._get_flashable(Safe, top_left, size, coords)

    def add_cup(self, cup_id, empty_top_left, size, coords):
        """Add a cup to the skool.

        :param cup_id: The cup's unique ID.
        :param empty_top_left: The coordinates of the top left of the image of
                               the cup when empty.
        :param size: The size of the image.
        :param coords: The coordinates of the cup in the skool.
        """
        cup = Cup(cup_id, coords, self.cast.water_id, self.cast.sherry_id)
        self.cups[cup_id] = cup
        water_top_left = (empty_top_left[0] + size[0], empty_top_left[1])
        sherry_top_left = (water_top_left[0] + size[0], empty_top_left[1])
        if self.mode == 0:
            empty_images = (self.mutables.subsurface(empty_top_left, size),)
            water_images = (self.mutables.subsurface(water_top_left, size),)
            sherry_images = (self.mutables.subsurface(sherry_top_left, size),)
        else:
            empty_image_ink = self.mutables_ink.subsurface(empty_top_left, size)
            empty_image_paper = self.mutables_paper.subsurface(empty_top_left, size)
            empty_images = (empty_image_ink, empty_image_paper)
            water_image_ink = self.mutables_ink.subsurface(water_top_left, size)
            water_image_paper = self.mutables_paper.subsurface(water_top_left, size)
            water_images = (water_image_ink, water_image_paper)
            sherry_image_ink = self.mutables_ink.subsurface(sherry_top_left, size)
            sherry_image_paper = self.mutables_paper.subsurface(sherry_top_left, size)
            sherry_images = (sherry_image_ink, sherry_image_paper)
        cup.set_images(empty_images, water_images, sherry_images)

    def add_plant(self, plant_id, sprite_group_id, x, y, command_list_id):
        """Add a plant pot to the skool, and a plant to the cast.

        :param plant_id: The plant's unique ID.
        :param sprite_group_id: The ID of the plant's sprite group.
        :param x: The x-coordinate of the plant.
        :param y: The y-coordinate of the plant.
        :param command_list_id: The ID of the command list the plant will use.
        """
        plant = self.cast.add_plant(plant_id, sprite_group_id, x, y, command_list_id)
        self.plant_pots[plant_id] = PlantPot(plant_id, plant, x, y - 1)

    def add_bike(self, bike_id, sprite_group_id, initial_as, location, command_list_id, top_left, size, coords, move_delay, pedal_momentum, max_momentum):
        """Add a bike to the skool and the cast.

        :param bike_id: The bike's unique ID.
        :param sprite_group_id: The ID of the bike's sprite group.
        :param initial_as: The bike's initial animatory state.
        :param location: The bike's initial location.
        :param command_list_id: The ID of the command list the bike will use.
        :param top_left: The coordinates of the top left of the image of the
                         base of the tree without the bike.
        :param size: The size of the image.
        :param coords: The coordinates of the image in the skool.
        :param move_delay: The delay between consecutive movements of the bike
                           when wheeling along or being pedalled.
        :param pedal_momentum: The momentum increment when the bike is
                               pedalled.
        :param max_momentum: The maximum momentum the bike can have.
        """
        self.cast.add_bike(bike_id, sprite_group_id, initial_as, location, command_list_id, move_delay, pedal_momentum, max_momentum)
        self.bike = Bike(*coords)
        chained_top_left = (top_left[0] + size[0], top_left[1])
        if self.mode == 0:
            unchained_images = (self.mutables.subsurface(top_left, size),)
            chained_images = (self.mutables.subsurface(chained_top_left, size),)
        else:
            unchained_image_ink = self.mutables_ink.subsurface(top_left, size)
            unchained_image_paper = self.mutables_paper.subsurface(top_left, size)
            unchained_images = (unchained_image_ink, unchained_image_paper)
            chained_image_ink = self.mutables_ink.subsurface(chained_top_left, size)
            chained_image_paper = self.mutables_paper.subsurface(chained_top_left, size)
            chained_images = (chained_image_ink, chained_image_paper)
        self.bike.set_images(unchained_images, chained_images)

    def add_font_character(self, char, offset, width):
        """Define the location and width of a font character bitmap in the font
        image.

        :param char: The font character.
        :param offset: The offset (in pixels) of the font character bitmap from
                       the left edge of the font image.
        :param width: The width of the font character bitmap.
        """
        self.screen.add_font_character(char, offset, width)

    #//////////////////////////////////////////////////////////////////////////
    # Drawing
    #//////////////////////////////////////////////////////////////////////////
    def get_inventory_images(self, item_ids):
        """Return a list of images of inventory items.

        :param item_ids: The IDs of the inventory items.
        """
        images = []
        for item_id in self.inventory_item_ids:
            if item_id in item_ids:
                images.append(self.inventory_images.get(item_id))
        return images

    def get_mouse_image(self):
        """Return an image of a captured mouse (as it appears in the mouse
        inventory).
        """
        return self.inventory_images.get(items.MOUSE)

    def move_door(self, barrier_id, shut):
        """Open or close a door or window.

        :param barrier_id: The ID of the door or window.
        :param shut: `True` if the door or window should be closed, `False`
                     if it should be opened.
        """
        self.draw_mutable(*self.barriers[barrier_id].move(shut))

    def auto_shut_doors(self):
        """Shut any automatically shutting doors that are due to be and can be
        shut.
        """
        for barrier_id, door in self.doors.items():
            if door.auto_shut() and not self.cast.somebody_near_door(door):
                self.move_door(barrier_id, True)

    def unchain_bike(self):
        """Unchain the bike from the tree."""
        if self.bike:
            self.draw_mutable(*self.bike.unchain())
            self.cast.unchain_bike()

    def chain_bike(self):
        """Chain the bike to the tree."""
        if self.bike:
            self.draw_mutable(*self.bike.chain())

    def draw_mutable(self, images, coords):
        """Draw a mutable object (a door, window, cup, or bike-on-a-tree).

        :param images: The images of the mutable object.
        :param coords: The coordinates at which to draw the object.
        """
        if self.mode == 0:
            self.skool.scale_blit(images[0].surface, coords)
        else:
            self.ink.scale_blit(images[0].surface, coords)
            self.paper.scale_blit(images[1].surface, coords)

    def get_width(self):
        """Return the width of the play area (in pixels)."""
        surface = self.skool or self.ink
        return surface.get_width()

    def get_height(self):
        """Return the height of the play area (in pixels)."""
        surface = self.skool or self.ink
        return surface.get_height()

    def draw(self, update=True):
        """Draw the skool.

        :param update: Whether to update the screen after drawing.
        """
        skool_images = (self.skool, self.ink, self.paper)
        cast_images = self.cast.get_images()
        inverse = self.draw_index >= self.flash_cycle // 2
        flash = inverse ^ self.inverse
        self.inverse = inverse
        if flash:
            for shield in self.shields:
                if shield.flashing:
                    self.draw_mutable(*shield.get_images(inverse))
            if self.safe and self.safe.flashing:
                self.draw_mutable(*self.safe.get_images(inverse))
        self.screen.draw(skool_images, cast_images, self.cast.get_speech_bubbles(), update)
        self.draw_index = (self.draw_index + 1) % self.flash_cycle

    def scroll_on(self, clock):
        """Scroll the skool into view across the screen.

        :param clock: The clock to use to time the scrolling.
        """
        self.screen.scroll_skool(self, clock)
        if self.play_tune:
            self.play_sound(sound.TUNE)
        self.play_tune = True

    def scroll(self, inc, clock):
        """Scroll the skool left or right across the screen.

        :param inc: The scroll increment; should be -1 (scroll right), 0 (don't
                    scroll), or 1 (scroll left).
        :param clock: The clock to use to time the scrolling.
        """
        if inc != 0:
            self.screen.scroll(inc, self, clock)

    def wipe_board(self, blackboard, column):
        """Wipe a bit of a blackboard clean.

        :param blackboard: The blackboard.
        :param column: The column of the blackboard to wipe.
        """
        if blackboard:
            blackboard.wipe(column)

    def write_on_board(self, character, blackboard, message, index=1):
        """Write the next character of a message on a blackboard.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character writing on the blackboard.
        :param blackboard: The blackboard.
        :param message: The message being written.
        :param index: The index of the next character in the message to write.
        :return: `True` if the entire message has been written, `False`
                 otherwise.
        """
        if blackboard:
            char = message[index - 1]
            if char == self.newline:
                blackboard.newline()
            else:
                blackboard.write(char)
            blackboard.writer = character
        return index == len(message)

    def fill_cup(self, cup_id, contents):
        """Fill a cup with water, sherry, or nothing.

        :param cup_id: The ID of the cup.
        :param contents: The stuff to fill the cup with.
        """
        self.draw_mutable(*self.cups[cup_id].fill(contents))

    def unflash(self, flashable):
        """Make a flashing object stop flashing.

        :param flashable: The flashing object.
        """
        flashable.unflash()
        self.draw_mutable(*flashable.get_images(False))

    def restore(self):
        """Perform tasks required immediately after rescaling or loading a
        saved game. The tasks are:

          * set the screen size and background colour
          * set the window icon and title
          * print the logo, score box, lesson box and inventories
          * restore the blackboard images
          * redraw the bike, cups, doors, and windows
        """
        self.screen.setup(True)
        self._build_images()
        self.update_score_box()
        self.print_lesson()
        for room in self.rooms.values():
            room.restore_blackboard()
        for cup in self.cups.values():
            self.draw_mutable(*cup.get_images())
        if self.bike:
            self.draw_mutable(*self.bike.get_images())
        for window in self.windows.values():
            self.draw_mutable(*window.get_images())
        for door in self.doors.values():
            self.draw_mutable(*door.get_images())
        self.cast.restore()

    def update_score_box(self):
        """Print the score, lines total and hi-score."""
        self.scoreboard.print_score_box()

    def _build_images(self):
        """Build the skool images. This method is called after rescaling the
        screen or loading a saved game.
        """
        if self.mode == 1:
            self.ink.build()
            self.paper.build()
        else:
            self.skool.build()
        self.mutables.build()
        self.mutables_ink.build()
        self.mutables_paper.build()
        self.inventory.build()
        for image in self.inventory_images.values():
            image.build()
        for room in self.rooms.values():
            room.build_blackboard_images()
        for cup in self.cups.values():
            cup.build_images()
        if self.bike:
            self.bike.build_images()
        for window in self.windows.values():
            window.build_images()
        for door in self.doors.values():
            door.build_images()
        for shield in self.shields:
            shield.build_images()
        if self.safe:
            self.safe.build_images()

    #//////////////////////////////////////////////////////////////////////////
    # Location queries
    #//////////////////////////////////////////////////////////////////////////
    def resolve_location_id(self, location_id):
        """Resolve a location ID into a pair of coordinates.

        :param location_id: The ID of the location.
        :return: The coordinates of the location.
        """
        if location_id.startswith(self.location_marker):
            character = self._get_character(location_id[len(self.location_marker):])
            return Location(character.get_location())
        if location_id in self.locations:
            return Location(self.locations[location_id])

    def hit_shield(self, x, y):
        """Check whether there is a shield that can be hit at a given location,
        and make it flash or unflash if required. If the last shield was made
        to flash or unflash, appropriate sound effects are played, points are
        awarded, and other required actions are taken.

        :param x: The x-coordinate of the location to check.
        :param y: The y-coordinate of the location to check.
        :return: `True` if a shield was hit, `False` otherwise.
        """
        for shield in self.shields:
            if (shield.x, shield.y) == (x, y):
                hit = False
                if self.shield_mode == 3 and shield.flashing:
                    self.unflash(shield)
                    hit = True
                elif self.shield_mode == 1 and not shield.flashing:
                    shield.flash()
                    hit = True
                if hit:
                    self.add_to_score(shield.score)
                    self.locked = True
                    self.play_sound(sound.SHIELD, pre_resume=self._change_shield_mode)
                return True
        return False

    def _change_shield_mode(self):
        """Advance to the next shield mode if the last shield was hit."""
        if self.shield_mode == 1 and all(shield.flashing for shield in self.shields):
            self.shield_mode = 2
            self.add_to_score(self.all_shields_score)
            self.play_sound(sound.ALL_SHIELDS)
        elif self.shield_mode == 3 and not any(shield.flashing for shield in self.shields):
            self._up_a_year()

    def check_safe(self, x, y, got_key):
        """Check whether there is a safe that can be opened at a given
        location. The safe will be opened if Eric either has the safe key, or
        has written the safe combination on a blackboard while all the shields
        are flashing.

        :param x: The x-coordinate of the location to check.
        :param y: The y-coordinate of the location to check.
        :param got_key: Whether Eric has the safe key.
        """
        if (self.safe.x, self.safe.y) == (x, y):
            if got_key:
                self._up_a_year()
            elif self.shield_mode == 2 and self.got_safe_combination():
                self.shield_mode += 1
                self.safe.flash()
                self.add_to_score(self.safe_open_score)
                self.play_sound(sound.OPEN_SAFE)

    def check_drinks_cabinet(self, x, y):
        """Return whether the drinks cabinet is at a given location and is
        open.

        :param x: The x-coordinate of the location to check.
        :param y: The y-coordinate of the location to check.
        """
        door = self.doors.get(self.drinks_cabinet_door_id)
        if door:
            return (x, y) == door.top_left and not door.shut
        return False

    def visible_blackboard(self, character):
        """Return the blackboard that is in a character's line of sight, or
        `None` if there is none.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        for room in self.rooms.values():
            board = room.blackboard
            if board and board.y <= character.y <= board.y + 2 and character.is_facing(board) and self.line_of_sight_between(character, board):
                return board

    def beside_blackboard(self, character):
        """Return whether a character is beside a blackboard.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        for room in self.rooms.values():
            if room.beside_blackboard(character):
                return True

    def room(self, character):
        """Return the room a character is in (or `None` if he is not in a
        room).

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        for room in self.rooms.values():
            if room.contains(character):
                return room

    def staircase(self, character, distance=0):
        """Return the staircase that a character is on or close to.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        :param distance: The maximum distance in front of the character to
                         check for a staircase.
        :return: The staircase, or `None` if there is none.
        """
        for staircase in self.staircases.values():
            if staircase.contains(character, distance):
                return staircase

    def on_staircase(self, character):
        """Return whether a character is on a step of any of the staircases in
        the skool.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        """
        return any(staircase.supports(character) for staircase in self.staircases.values())

    def floor(self, thing):
        """Return the floor that a character or thing is in direct contact
        with.

        :param thing: The character or thing.
        :return: The floor, or `None` is the character is not on a floor.
        """
        for floor in self.floors.values():
            if floor.supports(thing):
                return floor

    def floor_below(self, character):
        """Return the highest floor that is below a character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        """
        floor = None
        for f in self.floors.values():
            if f.below(character):
                if floor is None or f.y < floor.y:
                    floor = f
        return floor

    def on_floor(self, character):
        """Return whether a character is in direct contact with a floor.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        """
        return any(floor.supports(character) for floor in self.floors.values())

    def floor_at(self, x, y):
        """Return the floor at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        for floor in self.floors.values():
            if floor.contains_location(x, y):
                return floor

    def in_no_go_zone(self, x, y):
        """Return whether a given location is in a no-go zone.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        return any(zone.contains(x, y) for zone in self.no_go_zones)

    def in_playground(self, character):
        """Return whether a character is in the playground.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        if self.playground:
            return self.playground[0] <= character.x <= self.playground[1]
        return False

    def barrier(self, character, distance=0):
        """Return the barrier (wall, window or door) that is in front of a
        character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        :param distance: The maximum distance to check in front of the
                         character.
        :return: The wall, window or door in front of the character, or `None`
                 if there is none.
        """
        for barrier in self.barriers.values():
            if barrier.impedes(character, distance):
                return barrier

    def chair(self, character, check_dir=True):
        """Return the chair that is beside a character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        :param check_dir: If `True`, return the chair only if the character is
                          facing the correct way to sit in it; otherwise,
                          return the chair whichever way the character is
                          facing.
        :return: The chair, or `None` if there is none.
        """
        room = self.room(character)
        if room:
            return room.chair(character, check_dir)

    def desk(self, character):
        """Return the desk that a character is sitting at.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        :return: The desk, or `None` if the character is not sitting at a
                 desk.
        """
        room = self.room(character)
        if room:
            return room.desk(character)

    def cup(self, x, y):
        """Return the cup at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        :return: The cup, or `None` if there is no cup at the given location.
        """
        for cup in self.cups.values():
            if (cup.x, cup.y) == (x, y):
                return cup

    def plant_pot(self, x, y):
        """Return the plant pot at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        :return: The plant pot, or `None` if there is no plant pot at the
                 given location.
        """
        for plant_pot in self.plant_pots.values():
            if (plant_pot.x, plant_pot.y) == (x, y):
                return plant_pot

    def window(self, character):
        """Return the window that is in front of a character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        :return: The window, or `None` if there is no window.
        """
        for window in self.windows.values():
            if window.impedes(character, force_shut=True):
                return window

    def nearby_window(self, character):
        """Return a window that is close to a character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        :return: The window, or `None` if there is no window nearby.
        """
        for window in self.windows.values():
            x, y = window.opener_coords
            if character.y == y and abs(character.x - x) <= self.window_proximity:
                return window

    #//////////////////////////////////////////////////////////////////////////
    # Messages
    #//////////////////////////////////////////////////////////////////////////
    def get_assembly_message(self):
        """Return a message to deliver during assembly (with verb and noun
        randomly chosen).
        """
        return self.assembly_message_generator.generate_message()

    def expand_message(self, message):
        """Return a message with character name and newline macros expanded. A
        character name macro takes the form `$WACKER` (for example), which
        expands to the name of the character whose ID is `WACKER`.

        :param message: The message that may contain unexpanded name macros.
        :return: A list of the lines in the expanded message.
        """
        return self.cast.expand_names(message).split(self.newline)

    def get_lines_message(self, num_lines, name):
        """Return a lines message containing the number of lines being given
        and the recipient's name.

        :param num_lines: The number of lines being given.
        :param name: The recipient's name.
        """
        message = self.lines_message_template
        if self.num_lines_macro:
            message = message.replace(self.num_lines_macro, str(num_lines))
        if self.lines_recipient_macro:
            message = message.replace(self.lines_recipient_macro, name)
        return message.split(self.newline)

    #//////////////////////////////////////////////////////////////////////////
    # Sound effects
    #//////////////////////////////////////////////////////////////////////////
    def play_sound(self, sound_id, mode=sound.SUSPEND, pre_resume=None, pre_resume_args=()):
        """Play a sound effect.

        :param sound_id: The ID of the sound effect.
        :param mode: See :meth:`pyskool.sound.Beeper.play`.
        :param pre_resume: A method to execute after a sound effect played in
                           :data:`~pyskool.sound.SUSPEND` mode has finished.
        :param pre_resume_args: The arguments for the `pre_resume` method.
        """
        if mode == sound.SUSPEND:
            self.suspended = True
            self.pre_resume = pre_resume
            self.pre_resume_args = pre_resume_args
        self.beeper.play(sound_id, mode)

    def make_sitting_sound(self):
        """Play a sitting sound effect. This will be a walking sound effect,
        chosen at random from those available.
        """
        self.beeper.make_sitting_sound(sound.ASYNC)

    def make_walking_sound(self, index):
        """Play a walking sound effect.

        :param index: The index of the walking sound effect.
        """
        self.beeper.make_walking_sound(index, sound.ASYNC)

    def resume(self):
        """Run any method that was queued up before playing a sound effect in
        :data:`~pyskool.sound.SUSPEND` mode.
        """
        self.suspended = False
        if self.pre_resume:
            self.pre_resume(*self.pre_resume_args)
        else:
            self.locked = False
        if not self.suspended:
            self.pre_resume = None
            self.pre_resume_args = None

    #//////////////////////////////////////////////////////////////////////////
    # Scoreboard
    #//////////////////////////////////////////////////////////////////////////
    def add_to_score(self, addend):
        """Award some points.

        :param addend: The number of points to add to the score.
        """
        self.scoreboard.add_to_score(addend)

    def add_lines(self, addend):
        """Add some lines to Eric's total. If, as a result, Eric has exceeded
        the lines limit, appropriate action is taken.

        :param addend: The number of lines to add.
        """
        if not self.cast.is_eric_expelled():
            self.scoreboard.add_lines(addend)
            if self.scoreboard.lines > self.max_lines:
                self.stop_clock()
                self.cast.expel_eric(self.expeller_id, self.too_many_lines)

    #//////////////////////////////////////////////////////////////////////////
    # Skool clock
    #//////////////////////////////////////////////////////////////////////////
    def stop_clock(self):
        """Stop the skool clock."""
        self.timetable.stop()

    def start_clock(self, ticks):
        """Start the skool clock with a certain number of ticks remaining till
        the bell rings.

        :param ticks: The number of ticks.
        """
        self.timetable.resume(ticks)

    def rewind_clock(self, ticks):
        """Rewind the skool clock by a number of ticks.

        :param ticks: The number of ticks.
        """
        self.timetable.rewind(ticks)

    def tick(self):
        """Advance the skool clock by one tick."""
        return self.timetable.tick()

    def is_time_to_start_lesson(self):
        """Return whether enough time has passed to start the lesson. This is
        used, for example, to check whether a teacher should tell the kids to
        sit down, or continue pacing up and down outside the classroom doorway.
        """
        return self.timetable.is_time_to_start_lesson()

    def is_time_remaining(self, ticks):
        """Return whether there is no more than a certain number of skool clock
        ticks remaining before the bell rings.

        :param ticks: The number of ticks.
        """
        return self.timetable.is_time_remaining(ticks)

    #//////////////////////////////////////////////////////////////////////////
    # Signals
    #//////////////////////////////////////////////////////////////////////////
    def _clear_signals(self):
        self.signals = {}

    def signal(self, signal):
        """Raise a signal.

        :param signal: The signal to raise.
        """
        self.signals[signal] = True

    def unsignal(self, signal):
        """Lower a signal.

        :param signal: The signal to lower.
        """
        self.signals[signal] = False

    def got_signal(self, signal):
        """Return whether a signal has been raised.

        :param signal: The signal to check.
        """
        return self.signals.get(signal, False)

    #//////////////////////////////////////////////////////////////////////////
    # Timetable
    #//////////////////////////////////////////////////////////////////////////
    def is_teaching_eric(self, character):
        """Return whether a character is teaching Eric's class this period.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return self.timetable.is_teaching_eric(character)

    def get_teacher(self):
        """Return Eric's teacher for this period.

        :return: Eric's teacher, or `None` if it's an unsupervised period.
        """
        return self.cast.get(self.timetable.get_teacher_id())

    def set_home_room(self):
        """Set Eric's home room for the current period. The home room is the
        place Eric should be in by now; if he's not, and he's spotted by a
        teacher, he will be given lines.
        """
        self.home_room = self.get_room(self.timetable.get_room_id())

    def unset_home_room(self):
        """Unset Eric's home room for the current period. This is used when
        assembly is finished (so that Eric is not told off for being outside
        the assembly hall after Mr Wacker has finished speaking).
        """
        self.home_room = None

    def get_home_room(self):
        """Return the room Eric's supposed to be in at the moment.

        :return: The room, or `None` if it's an unsupervised period or Eric
                 still has time to reach the room in which the class will be
                 taking place.
        """
        return self.home_room

    def should_get_along(self, eric):
        """Return whether Eric is somewhere other than he should be."""
        if self.home_room:
            return not self.home_room.contains(eric)
        if self.timetable.is_time_to_get_along():
            # Give Eric time to leave a classroom
            room = self.room(eric)
            if room:
                destination = self.get_room(self.timetable.get_room_id())
                return room != destination and room.get_along
            elif self.in_playground(eric) and not self.is_playtime():
                return True
        return False

    def is_playtime(self):
        """Return whether it's Playtime."""
        return self.timetable.is_playtime()

    def is_assembly(self):
        """Return whether it's Assembly."""
        return self.timetable.is_assembly()

    def get_lesson_desc(self):
        """Return the name of the teacher and the room for this period (for
        display in the lesson box). The name of the teacher will be blank if
        it's Playtime or Revision Library.
        """
        teacher_id = self.timetable.get_teacher_id()
        if self.timetable.hide_teacher():
            teacher_id = ''
        room_id = self.timetable.get_room_id()
        room = self.get_room(room_id)
        teacher = self._get_character(teacher_id)
        return teacher.name if teacher else teacher_id, room.name if room else room_id

    def print_lesson(self):
        """Print the lesson description in the lesson box."""
        line1, line2 = self.get_lesson_desc()
        if not line1:
            elements = line2.split(' ')
            if len(elements) > 1:
                line1 = elements[0]
                line2 = elements[1]
        self.screen.print_lesson(line1, line2)

    def next_lesson(self, ring_bell):
        """Proceed to the next lesson in the timetable.

        :param ring_bell: Whether to ring the bell.
        """
        self.timetable.next_lesson()
        self.cast.set_lesson(self.timetable.lesson_id)
        self.print_lesson()
        self._clear_signals()
        self.home_room = None
        if ring_bell:
            self.play_sound(sound.BELL)
