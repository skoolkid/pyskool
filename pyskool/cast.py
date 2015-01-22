# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Cast` class.
"""

import random

from .character import Character
from .desklid import DeskLid
from . import animal
from .bike import Bike
from . import droppable
from .plant import Plant
from .eric import Eric
from .pellet import Pellet
from .water import Water
from .stinkbomb import Stinkbomb
from . import ai
from .lesson import Lesson
from . import graphics

class Cast:
    """The control centre from which the entire cast of characters is
    monitored.

    :type config: dict
    :param config: Configuration parameters from the ini file.
    :type screen: :class:`~pyskool.graphics.Screen`
    :param screen: The screen to draw on.
    :type gallery: :class:`~pyskool.graphics.Gallery`
    :param gallery: The gallery of images to use for drawing.
    """
    def __init__(self, config, screen, gallery):
        self.config = config
        self.screen = screen
        self.sprites = gallery.get_image(graphics.SPRITES)
        self._extract_config(config)
        self.skool = None
        self.sprite_groups = {}
        self.eric = None
        self.everything = []     # Everything that must be drawn
        self.characters = {}     # Humans
        self.character_list = [] # Ordered list of humans
        self.lines_givers = []   # Characters who can give lines
        self.movables = []       # All computer-controlled things
        self.command_lists = {}
        # Grass configuration
        self.hitters = None
        self.writers = None
        self.hit_tale = None
        self.write_tale = None
        self.absent_tale = None
        # We store animals (mice and frogs) separately so that we can check
        # whether Eric is next to one
        self.animals = []
        # We store plants separately so that we can check whether Eric is
        # standing on one
        self.plants = []
        # We store the bike separately so that we can release it and check
        # whether Eric is beside it
        self.bike = None
        # We store the first mouse separately so that it can be cloned
        self.first_mouse = None
        self.mouse_locations = []
        # We store frogs separately so that they can be placed in a cup
        self.frogs = []
        # We store the desk lid separately so that it can be opened and closed
        self.desk_lid = None
        # We store the conker separately so that we can check whether it is hit
        # by a catapult pellet
        self.conker = None

    def _extract_config(self, config):
        """Extract configuration parameters for later use.

        :type config: dict
        :param config: Configuration parameters from the ini file.
        """
        self.sprite_matrix_width = config.get('SpriteMatrixWidth', 16)
        self.sprite_width, self.sprite_height = config.get('SpriteSize', (3, 4))
        self.sprite_colorkey = config.get('SpriteKey', (0, 254, 0))
        self.lines_range = config.get('LinesRange', (1, 8))
        self.lines_ink = config.get('LinesInk', 7)
        self.lines_paper_eric = config.get('LinesPaperEric', 2)
        self.lines_paper_other = config.get('LinesPaperOther', 4)
        self.escape_alarm_ink = config.get('EscapeAlarmInk', 2)
        self.escape_alarm_paper = config.get('EscapeAlarmPaper', 6)
        self.conker_clock_ticks = config.get('ConkerClockTicks', 1200)
        self.conker_wake_time = config.get('ConkerWakeTime', 200)
        self.safe_secrets = config.get('SafeSecrets', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.bike_secrets = config.get('BikeSecrets', '0123456789')
        self.storeroom_secrets = config.get('StoreroomSecrets', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.secret_ink = config.get('SecretInk', 7)
        self.secret_paper = config.get('SecretPaper', 0)
        self.lines_message_newline = config.get('Newline', '^')
        self.initial_kiss_count = config.get('KissCounter', 40)
        self.kiss_decrement = config.get('KissCounterDecrement', 7)
        self.kiss_deckrement = config.get('KissCounterDeckrement', 1)
        self.kiss_distance = config.get('KissDistance', 2)
        self.beside_eric_x_range = config.get('BesideEricXRange', 4)
        self.lines_giving_range = config.get('LinesGivingRange', (10, 3))
        self.hit_probability = config.get('HitProbability', 0.5)
        self.fire_catapult_probability = config.get('FireCatapultProbability', 0.5)
        self.write_on_board_probability = config.get('WriteOnBoardProbability', 0.375)
        self.blackboard_backtrack = config.get('BlackboardBacktrack', 3)
        self.bb_pace_distance = config.get('BlackboardPaceDistance', 3)
        self.mouse_proximity = config.get('MouseProximity', 5)
        self.evade_mouse_delay = config.get('EvadeMouseDelay', 21)
        self.water_id = config.get('WaterId', 'WATER')
        self.sherry_id = config.get('SherryId', 'SHERRY')
        self.board_dirty = config.get('BoardDirtyConditionId', 'BoardDirty')
        self.ko_delay = config.get('KnockoutDelay', 10)
        self.dethroned_delay = config.get('DethronedDelay', 3)
        self.knocked_over_delay = config.get('KnockedOverDelay', 15)
        self.reprimand_delay = config.get('ReprimandDelay', 8)
        self.tell_eric_delay = config.get('TellEricDelay', 20)
        self.title_macro = config.get('TitleMacro', '$TITLE')
        self.grassee_macro = config.get('GrasseeMacro', '$1')

    def get(self, character_id):
        """Return a member of the cast.

        :param character_id: The ID of the cast member.
        """
        return self.characters.get(character_id, None)

    def move(self):
        """Move the members of the cast.

        :return: -1 if the screen should scroll right, 1 if it should scroll
                 left, or 0 if it should not scroll (after moving Eric).
        """
        for movable in self.movables:
            movable.move()
        return self.eric.move()

    def set_lesson(self, lesson_id):
        """Set the lesson (as after the bell rings). Everybody except Eric
        collects a new command list from their personal timetable.

        :param lesson_id: The ID of the lesson.
        """
        for movable in self.movables:
            command_list_id = movable.get_command_list_id(lesson_id)
            movable.set_command_list_template(self.command_lists[command_list_id])
            movable.remove_bubble()
        self.eric.unfreeze()

    def create_lesson(self, swot, room):
        """Return a new :class:`~pyskool.lesson.Lesson` instance for the swot.

        :type swot: :class:`~pyskool.character.Character`
        :param swot: The swot.
        :type room: :class:`~pyskool.room.Room`
        :param room: The room in which the lesson will take place.
        """
        return Lesson(self, swot, room, self.config)

    def _get_facing_characters(self, character, offset):
        """Return a list of characters who are facing a target character at a
        given distance.

        :type character: :class:`~pyskool.character.Character`
        :param character: The target character.
        :param offset: The distance in front of the target character to look
                       for facing characters.
        """
        target_x = character.x + offset * character.direction
        target_y = character.y
        target_direction = -1 * character.direction
        facing_characters = []
        for c in self.character_list:
            if (c.x, c.y, c.direction) == (target_x, target_y, target_direction):
                facing_characters.append(c)
        return facing_characters

    def get_punchee(self, character, offset):
        """Return the first punchable character who is facing a target
        character at a given distance.

        :type character: :class:`~pyskool.character.Character`
        :param character: The target character.
        :param offset: The distance in front of the target character to look
                       for facing characters.
        :return: A punchable character, or `None` if there is none at the
                 given distance.
        """
        for c in self._get_facing_characters(character, offset):
            if c.is_punchable_now():
                return c

    def get_pelletable(self, x, y):
        """Return the most suitable character to hit with a catapult pellet at
        a given location, or `None` if there is none.

        :param x: The x-coordinate of the location.
        :param y: The x-coordinate of the location.
        """
        pelletables = [c for c in self.character_list if c.is_pelletable()]
        for adult in [c for c in pelletables if c.is_adult()]:
            if (adult.x, adult.y) == (x, y):
                return adult
        for child in [c for c in pelletables if not c.is_adult()]:
            if (child.x, child.y) == (x, y):
                return child

    def get_waterable(self, x, y):
        """Return a suitable character to hit with a drop of water at a given
        location, or `None` if there is none. A character is considered
        suitable if he holds a bike combination digit.

        :param x: The x-coordinate of the location.
        :param y: The x-coordinate of the location.
        """
        for c in self.character_list:
            if c.has_bike_secret() and c.head_at(x, y):
                return c

    def get_sherryable(self, x, y):
        """Return a suitable character to hit with a drop of sherry at a given
        location, or `None` if there is none. A character is considered
        suitable if he holds a storeroom combination letter.

        :param x: The x-coordinate of the location.
        :param y: The x-coordinate of the location.
        """
        for c in self.character_list:
            if c.has_storeroom_secret() and c.head_at(x, y):
                return c

    def is_home(self, x):
        """Return whether every character is on the 'home' side of a given
        x-coordinate.

        :param x: The x-coordinate.
        """
        return all(c.is_home(x) for c in self.character_list)

    def is_standing_on_kid(self, character):
        """Return whether a character is standing on a kid who's been knocked
        out.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        for c in self.character_list:
            if c.is_knocked_out() and c.x - 1 <= character.x <= c.x + 1 and character.y == c.y - 1:
                return True

    def somebody_near_door(self, door):
        """Return whether somebody is standing near a door.

        :param door: The door to check.
        """
        for c in self.character_list:
            if door.x - 2 <= c.x <= door.x + 1 and door.top_y <= c.y <= door.bottom_y:
                return True

    def open_desk(self, character, desk):
        """Make a character open a desk. The desk lid will be raised.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character.
        :param desk: The desk.
        """
        self.desk_lid.raise_lid(desk, character)

    def trip_people_up_at(self, character, x, y):
        """Make a character trip people up at a given location.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character trying to trip people up.
        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        # Assume trippability == pelletability
        trippables = [c for c in self.character_list if c.is_trippable()]
        for trippable in trippables:
            if trippable is not character and (trippable.x, trippable.y) == (x, y) and trippable.is_deckable():
                trippable.deck()

    def knock_cup(self, cup):
        """Make a cup spill its contents (as when hit by a catapult pellet). A
        cup may contain water, sherry, a frog, or nothing.

        :param cup: The cup.
        """
        if cup.frogs:
            for frog in cup.frogs:
                frog.fall_from_cup(cup)
            return
        if cup.contents == self.water_id and not self.water_drop.is_visible():
            self.water_drop.fall(cup.x, cup.y)
        elif cup.contents == self.sherry_id and not self.sherry_drop.is_visible():
            self.sherry_drop.fall(cup.x, cup.y)

    def smeller(self, stinkbomb):
        """Return a character who can smell a stinkbomb, or `None` if there is
        none.

        :param stinkbomb: The stinkbomb.
        """
        for c in self.character_list:
            if c.can_smell_stinkbomb(stinkbomb):
                return c

    def change_command_list(self, character_id, command_list_id):
        """Switch a character to a new command list.

        :param character_id: The ID of the character.
        :param command_list_id: The ID of the command list.
        """
        if character_id in self.characters:
            self.characters[character_id].set_command_list_template(self.command_lists[command_list_id])

    #//////////////////////////////////////////////////////////////////////////
    # Cast construction
    #//////////////////////////////////////////////////////////////////////////
    def _get_animatory_state(self, state):
        """Return an animatory state image from the matrix of images.

        :param state: The index of the image in the matrix.
        """
        sprite_x = self.sprite_width * (state % self.sprite_matrix_width)
        sprite_y = self.sprite_height * (state // self.sprite_matrix_width)
        image = self.sprites.subsurface((sprite_x, sprite_y), (self.sprite_width, self.sprite_height))
        image.set_colorkey(self.sprite_colorkey)
        return image

    def add_sprite(self, group_id, sprite_id, sprite_index):
        """Add a sprite (an animatory state image) to the cast.

        :param group_id: The sprite group ID.
        :param sprite_id: The sprite ID.
        :param sprite_index: The index of the sprite in the sprite matrix.
        """
        if group_id not in self.sprite_groups:
            self.sprite_groups[group_id] = [{}, {}]
        sprite = self._get_animatory_state(sprite_index)
        self.sprite_groups[group_id][0][sprite_id] = sprite
        self.sprite_groups[group_id][1][sprite_id] = sprite.flip()

    def add_eric(self, character_id, name, sprite_group_id, initial_as, direction, head_xy, flags, bend_over_hand_xy):
        """Add Eric to the cast.

        :param character_id: Eric's unique ID.
        :param name: Eric's name.
        :param sprite_group_id: The ID of Eric's sprite group.
        :param initial_as: Eric's initial animatory state.
        :param direction: Eric's initial direction.
        :param head_xy: The coordinates of Eric's head within his sprite when
                        he's standing upright (used for collision detection).
        :param flags: Eric's character flags.
        :param bend_over_hand_xy: The coordinates of Eric's hand within his
                                  left-facing `BENDING_OVER` sprite (used to
                                  determine where a mouse or frog should be
                                  when caught or released).
        """
        self.eric = Eric(character_id, self.config, name, head_xy, flags, bend_over_hand_xy)
        self.eric.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.eric.initialise_animatory_state(initial_as, direction)
        self.everything.append(self.eric)
        self.characters[character_id] = self.eric
        self.character_list.append(self.eric)

    def add_character(self, character_id, name, title, sprite_group_id, initial_as, direction, head_xy, flags):
        """Add a character (other than Eric) to the cast.

        :param character_id: The character's unique ID.
        :param name: The character's name.
        :param title: The character's title (how he is addressed by the swot).
        :param sprite_group_id: The ID of the character's sprite group.
        :param initial_as: The character's initial animatory state.
        :param direction: The character's initial direction.
        :param head_xy: The coordinates of the character's head within his
                        sprite when he's standing upright (used for collision
                        detection).
        :param flags: The character's flags.
        """
        c = Character(character_id, name, head_xy, flags)
        c.title = title
        c.set_animatory_states(*self.sprite_groups[sprite_group_id])
        c.initialise_animatory_state(initial_as, direction)
        self.everything.append(c)
        self.characters[character_id] = c
        self.character_list.append(c)
        if c.can_give_lines():
            self.lines_givers.append(c)
        self.movables.append(c)

    def add_pellet(self, character_id, pellet_id, sprite_group_id, command_list_id, pellet_range, hit_zone, hit_xy):
        """Add a pellet to the cast.

        :param character_id: The ID of the pellet's owner.
        :param pellet_id: The ID of the pellet.
        :param sprite_group_id: The ID of the pellet's sprite group.
        :param command_list_id: The ID of the command list the pellet will use.
        :param pellet_range: The maximum distance the pellet will travel after
                             launch.
        :param hit_zone: The size of the portion at the end of the pellet's
                         journey in which it can hit things.
        :param hit_xy: The coordinates of the pellet within its sprite (used
                       for collision detection).
        """
        pellet = Pellet(pellet_id, command_list_id, pellet_range, hit_zone, hit_xy)
        pellet.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(pellet)
        self.movables.append(pellet)
        self.get(character_id).pellet = pellet

    def add_water_drop(self, object_id, sprite_group_id, command_list_id, hit_xy):
        """Add the water drop to the cast.

        :param object_id: The ID of the water drop.
        :param sprite_group_id: The ID of the water drop's sprite group.
        :param command_list_id: The ID of the command list the water drop will
                                use.
        :param hit_xy: The coordinates of the water drop within its sprite
                       (used for collision detection).
        """
        self.water_drop = droppable.WaterDrop(object_id, command_list_id, hit_xy)
        self.water_drop.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(self.water_drop)
        self.movables.append(self.water_drop)

    def add_sherry_drop(self, object_id, sprite_group_id, command_list_id, hit_xy):
        """Add the sherry drop to the cast.

        :param object_id: The ID of the sherry drop.
        :param sprite_group_id: The ID of the sherry drop's sprite group.
        :param command_list_id: The ID of the command list the sherry drop will
                                use.
        :param hit_xy: The coordinates of the sherry drop within its sprite
                       (used for collision detection).
        """
        self.sherry_drop = droppable.SherryDrop(object_id, command_list_id, hit_xy)
        self.sherry_drop.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(self.sherry_drop)
        self.movables.append(self.sherry_drop)

    def add_conker(self, object_id, sprite_group_id, command_list_id, min_x, max_x, min_y, max_y, hit_xy):
        """Add the conker to the cast.

        :param object_id: The ID of the conker.
        :param sprite_group_id: The ID of the conker's sprite group.
        :param command_list_id: The ID of the command list the conker will use.
        :param min_x: The minimum x-coordinate a pellet must reach to knock the
                      conker out of the tree.
        :param max_x: The maximum x-coordinate a pellet must reach to knock the
                      conker out of the tree.
        :param min_y: The minimum y-coordinate a pellet must fly at to knock
                      the conker out of the tree.
        :param max_y: The maximum y-coordinate a pellet must fly at to knock
                      the conker out of the tree.
        :param hit_xy: The coordinates of the conker within its sprite (used
                       for collision detection).
        """
        self.conker = droppable.Conker(object_id, command_list_id, min_x, max_x, min_y, max_y, hit_xy)
        self.conker.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(self.conker)
        self.movables.append(self.conker)

    def add_water(self, character_id, water_id, sprite_group_id, command_list_id, phases):
        """Add a jet of water or sherry to the cast.

        :param character_id: The ID of the water/sherry's owner.
        :param water_id: The ID of the water/sherry.
        :param sprite_group_id: The ID of the water/sherry's sprite group.
        :param command_list_id: The ID of the command list the water/sherry
                                will use.
        :param phases: The phases of animation the water will use after being
                       fired from a water pistol.
        """
        water = Water(water_id, command_list_id, phases)
        water.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(water)
        self.movables.append(water)
        self.get(character_id).water = water

    def add_stinkbomb(self, character_id, stinkbomb_id, sprite_group_id, command_list_id, phases, stink_range):
        """Add a stinkbomb to the cast.

        :param character_id: The ID of the stinkbomb's owner.
        :param stinkbomb_id: The ID of the stinkbomb.
        :param sprite_group_id: The ID of the stinkbomb's sprite group.
        :param command_list_id: The ID of the command list the stinkbomb will
                                use.
        :param phases: The phases of animation the stinkbomb cloud will use.
        :param stink_range: The maximum distance from which the stinkbomb can
                            be smelt.
        """
        stinkbomb = Stinkbomb(stinkbomb_id, command_list_id, phases, stink_range)
        stinkbomb.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(stinkbomb)
        self.movables.append(stinkbomb)
        self.get(character_id).stinkbomb = stinkbomb

    def add_desk_lid(self, desk_lid_id, sprite_group_id, command_list_id, x_offset):
        """Add the desk lid to the cast.

        :param desk_lid_id: The ID of the desk lid.
        :param sprite_group_id: The ID of the desk lid's sprite group.
        :param command_list_id: The ID of the command list the desk lid will
                                use.
        :param x_offset: The offset (relative to the desk being opened) at
                         which the desk lid should be displayed.
        """
        self.desk_lid = DeskLid(desk_lid_id, command_list_id, x_offset)
        self.desk_lid.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(self.desk_lid)
        self.movables.append(self.desk_lid)

    def add_mouse(self, mouse_id, sprite_group_id, initial_as, location, command_list_id, sprite_xy, immortal=True):
        """Add a mouse to the cast.

        :param mouse_id: The ID of the mouse.
        :param sprite_group_id: The ID of the mouse's sprite group.
        :param initial_as: The mouse's initial animatory state.
        :param location: The mouse's initial location.
        :param command_list_id: The ID of the command list the mouse will use.
        :param sprite_xy: The coordinates of the mouse within its sprite (used
                          for detecting whether Eric has caught it).
        :param immortal: Whether the mouse is immortal (will not disappear
                        until Eric catches it).
        """
        mouse = animal.Mouse(mouse_id, command_list_id, initial_as, location, sprite_xy, immortal)
        mouse.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(mouse)
        self.animals.append(mouse)
        self.movables.append(mouse)
        if self.first_mouse is None:
            self.first_mouse = mouse
            self.mouse_sprite_group_id = sprite_group_id
        return mouse

    def add_mouse_location(self, x, y):
        """Add a location at which a new immortal mouse may appear after Eric
        catches one.

        :param x: The x-coordinate of the location.
        :param y: The x-coordinate of the location.
        """
        self.mouse_locations.append((x, y))

    def add_frog(self, frog_id, sprite_group_id, initial_as, location, command_list_id, turn_round, short_hop, long_hop, sit_xy, eric_proximity):
        """Add a frog to the cast.

        :param frog_id: The ID of the frog.
        :param sprite_group_id: The ID of the frog's sprite group.
        :param initial_as: The frog's initial animatory state.
        :param location: The frog's initial location.
        :param command_list_id: The ID of the command list the frog will use.
        :param turn_round: The animation phases to use when the frog turns
                           round.
        :param short_hop: The animation phases to use when the frog makes a
                          short hop.
        :param long_hop: The animation phases to use when the frog makes a long
                         hop.
        :param sit_xy: The coordinates of the frog within its sprite when it's
                       sitting (used for collision detection and placement in
                       cups).
        :param eric_proximity: The minimum distance from the frog that Eric can
                               be before it will try to hop away.
        """
        frog = animal.Frog(frog_id, command_list_id, initial_as, location, sit_xy, eric_proximity)
        frog.set_animatory_states(*self.sprite_groups[sprite_group_id])
        frog.turn_round = turn_round
        frog.short_hop = short_hop
        frog.long_hop = long_hop
        self.everything.append(frog)
        self.animals.append(frog)
        self.movables.append(frog)
        self.frogs.append(frog)

    def add_bike(self, bike_id, sprite_group_id, initial_as, location, command_list_id, move_delay, pedal_momentum, max_momentum):
        """Add the bike to the cast.

        :param bike_id: The ID of the bike.
        :param sprite_group_id: The ID of the bike's sprite group.
        :param initial_as: The bike's initial animatory state.
        :param location: The bike's initial location (after being unchained).
        :param command_list_id: The ID of the command list the bike will use.
        :param move_delay: The delay between consecutive movements of the bike
                           when wheeling along or being pedalled.
        :param pedal_momentum: The momentum increment when the bike is
                               pedalled.
        :param max_momentum: The maximum momentum the bike can have.
        """
        self.bike = Bike(bike_id, command_list_id, initial_as, location, move_delay, pedal_momentum, max_momentum)
        self.bike.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(self.bike)
        self.movables.append(self.bike)

    def add_plant(self, plant_id, sprite_group_id, x, y, command_list_id):
        """Add a plant to the cast.

        :param plant_id: The ID of the plant.
        :param sprite_group_id: The ID of the plant's sprite group.
        :param x: The plant's x-coordinate.
        :param y: The plant's y-coordinate.
        :param command_list_id: The ID of the command list the bike will use.
        :return: The plant.
        """
        plant = Plant(plant_id, command_list_id, x, y)
        plant.set_animatory_states(*self.sprite_groups[sprite_group_id])
        self.everything.append(plant)
        self.plants.append(plant)
        self.movables.append(plant)
        return plant

    def add_command(self, command_list_id, command_name, *params):
        """Add a command to a command list.

        :param command_list_id: The ID of the command list.
        :param command_name: The name of the command.
        :param params: The command's parameters.
        """
        if command_list_id not in self.command_lists:
            self.command_lists[command_list_id] = ai.CommandListTemplate(command_list_id)
        command_class = getattr(ai, command_name)
        self.command_lists[command_list_id].add_command(command_class, *params)

    def set_random_locations(self, character_id, locations):
        """Set the collection of random locations for a character.

        :param character_id: The ID of the character.
        :param locations: The locations.
        """
        if character_id in self.characters:
            self.characters[character_id].set_random_locations(locations)

    def add_command_list(self, character_id, lesson_id, command_list_id):
        """Add a command list to a character's personal timetable.

        :param character_id: The ID of the character.
        :param lesson_id: The ID of the lesson to place the command list
                          against.
        :param command_list_id: The ID of the command list.
        """
        if character_id in self.characters:
            self.characters[character_id].add_command_list(lesson_id, command_list_id)

    def add_sit_down_message(self, character_id, message):
        """Add a sit-down message for a character.

        :param character_id: The ID of the character
        :param message: The sit-down message.
        """
        if character_id in self.characters:
            self.characters[character_id].add_sit_down_message(message)

    def add_blackboard_message(self, character_id, message):
        """Add a blackboard message to a character's collection.

        :param character_id: The ID of the character.
        :param message: The blackboard message.
        """
        if character_id in self.characters:
            self.characters[character_id].add_blackboard_message(message)

    def add_lines_message(self, character_id, message_id, message):
        """Add a lines message to a character's collection.

        :param character_id: The ID of the character.
        :param message_id: The ID of the lines message.
        :param message: The lines message.
        """
        message_lines = message.split(self.lines_message_newline)
        if character_id == '*':
            for c in self.lines_givers:
                c.add_lines_message(message_id, message_lines)
        elif character_id in self.characters:
            self.characters[character_id].add_lines_message(message_id, message_lines)

    def add_lesson_message(self, character_id, message, condition):
        """Add a lesson message to a character's collection. A lesson message
        is something like 'START READING AT THE NEXT CHAPTER IN YOUR BOOKS',
        which will be used by a teacher during class if he's not teaching Eric,
        or he has decided not to have a question-and-answer session with the
        swot.

        :param character_id: The ID of the character.
        :param message: The lesson message.
        :type condition: string
        :param condition: The name of the condition that must be met before the
                          lesson message is used.
        """
        if character_id == '*':
            for c in self.character_list:
                c.add_lesson_message(message, condition)
        elif character_id in self.characters:
            self.characters[character_id].add_lesson_message(message, condition)

    def set_location(self, character_id, x, y):
        """Set the location of a character.

        :param character_id: The ID of the character.
        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        if character_id in self.characters:
            self.characters[character_id].set_initial_location(x, y)

    #//////////////////////////////////////////////////////////////////////////
    # Initialisation
    #//////////////////////////////////////////////////////////////////////////
    def _initialise_character(self, character):
        """Set up a member of the cast with access to the
        :class:`~pyskool.skool.Skool` and :class:`~pyskool.graphics.Screen`
        objects.

        :type character: :class:`~pyskool.character.Character`
        :param character: The member to initialise.
        """
        character.set_components(self, self.skool, self.screen, self.config)

    def initialise(self, skool, keyboard):
        """Initialise every member of the cast.

        :type skool: :class:`~pyskool.skool.Skool`
        :param skool: The skool.
        :type keyboard: :class:`~pyskool.input.Keyboard`
        :param keyboard: The keyboard for Eric to use.
        """
        self.skool = skool
        for character in self.everything:
            self._initialise_character(character)
        self.eric.keyboard = keyboard

    def reinitialise(self):
        """Reinitialise every member of the cast."""
        for c in self.everything:
            c.reinitialise()

    def initialise_safe_combo(self):
        """Initialise the safe combination.

        :return: The combination.
        """
        letters = ''
        for character in self.character_list:
            character.initialise_special_answer()
            if character.has_safe_secret():
                letters += character.initialise_safe_secret()
        return letters

    def initialise_bike_combo(self):
        """Initialise the bike combination.

        :return: The combination.
        """
        digits = ''
        for character in self.character_list:
            if character.has_bike_secret():
                digits += character.initialise_bike_secret()
        return digits

    def initialise_storeroom_combo(self):
        """Initialise the storeroom combination.

        :return: The combination.
        """
        letters = ''
        for character in self.character_list:
            if character.has_storeroom_secret():
                letters += character.initialise_storeroom_secret()
        return letters

    #//////////////////////////////////////////////////////////////////////////
    # Animals
    #//////////////////////////////////////////////////////////////////////////
    def get_animal(self, x, y):
        """Return any animal that is on the floor at a given location.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        :return: The animal, or `None` if there is none.
        """
        for animal in self.animals:
            if animal.is_catchable_at(x, y):
                return animal

    def caught_mouse(self, mouse):
        """Take appropriate action when a mouse is caught. If the mouse is
        immortal (defined in the [Mice] section of the ini file), it will be
        relocated (so that Eric can catch it again). If it is not immortal
        (Eric previously released it), it is removed from the game.

        :param mouse: The captured mouse.
        """
        if mouse.immortal:
            self.relocate_mouse(mouse)
        else:
            self.kill_mouse(mouse)

    def relocate_mouse(self, mouse):
        """Relocate a mouse at a randomly chosen location."""
        locations = self.mouse_locations[:]
        while locations and self.screen.contains(mouse):
            mouse.x, mouse.y = locations.pop(random.randrange(len(locations)))
        mouse.restart_command_list()

    def release_mice(self, num_mice, x, y):
        """Release some mice at a given location.

        :param num_mice: The number of mice to release.
        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        if self.first_mouse is None:
            return
        while num_mice > 0:
            mouse_id = 'MortalMouse%i' % num_mice
            initial_as = self.first_mouse.initial_as
            command_list_id = self.first_mouse.get_command_list_id(None)
            sprite_xy = self.first_mouse.sprite_xy
            release_coords = (x - sprite_xy[0], y - sprite_xy[1])
            mouse = self.add_mouse(mouse_id, self.mouse_sprite_group_id, initial_as, release_coords, command_list_id, sprite_xy, False)
            self._initialise_character(mouse)
            mouse.set_command_list_template(self.command_lists[command_list_id])
            num_mice -= 1

    def kill_mouse(self, mouse):
        """Remove a mouse from the game.

        :param mouse: The mouse to remove.
        """
        self.everything.remove(mouse)
        self.movables.remove(mouse)
        self.animals.remove(mouse)

    def scare_musophobes(self, mouse):
        """Make any characters near a mouse respond appropriately.

        :param mouse: The mouse.
        """
        for c in self.character_list:
            c.check_mouse(mouse)

    def insert_frog(self, cup):
        """Insert any frogs that have been caught by Eric into a cup.

        :param cup: The cup.
        """
        for frog in self.frogs:
            if not frog.is_visible():
                cup.insert_frog(frog)
                break

    def check_heads_at(self, x, y):
        """Check whether a frog has hit the head of anyone who holds a safe
        key, and hand the safe key to Eric if so.

        :param x: The x-coordinate to check for heads.
        :param y: The y-coordinate to check for heads.
        :return: `True` if the frog hit someone's head, `False` otherwise.
        """
        for c in self.character_list:
            if c.has_safe_key() and c.head_at(x, y):
                self.eric.take_safe_key()
                return True
        return False

    #//////////////////////////////////////////////////////////////////////////
    # Bike
    #//////////////////////////////////////////////////////////////////////////
    def is_bike_visible(self):
        """Return whether the bike is in the play area at the moment."""
        return self.bike and self.bike.is_visible()

    def is_beside_bike(self, character):
        """Return whether a character is next to the bike.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return self.bike and (self.bike.x, self.bike.y) == (character.x, character.y)

    def move_bike_away(self, door):
        """Move the bike away from a door if necessary (so that it may be
        closed).

        :param door: The door.
        """
        if self.bike and door.top_y <= self.bike.y <= door.bottom_y and door.x - 2 <= self.bike.x <= door.x:
            self.bike.x = door.x + 1

    def unchain_bike(self):
        """Bring the bike into the play area (as after being unchained)."""
        self.bike.unchain()

    #//////////////////////////////////////////////////////////////////////////
    # Conker
    #//////////////////////////////////////////////////////////////////////////
    def get_conkerable(self, x, y):
        """Return a suitable character to hit with a conker at a given
        location, or `None` if there is none. A character is considered
        suitable if he can be knocked over by a conker.

        :param x: The x-coordinate of the location.
        :param y: The x-coordinate of the location.
        """
        for c in self.character_list:
            if (c.is_conkerable() or c.is_very_conkerable()) and c.head_at(x, y):
                return c

    def hit_conker(self, pellet):
        """Check whether a catapult pellet has hit a conker. If it has, the
        conker will start falling.

        :param pellet: The catapult pellet.
        :return: `True` if a conker was hit, `False` otherwise.
        """
        if self.conker and self.conker.hit_by(pellet):
            self.conker.fall(*pellet.get_hit_coords())
            return True
        return False

    def conker_falling(self):
        """Return whether a conker is currently falling."""
        return self.conker and self.conker.is_visible()

    #//////////////////////////////////////////////////////////////////////////
    # Drawing
    #//////////////////////////////////////////////////////////////////////////
    def get_images(self):
        """Return a list of images for every member of the cast."""
        return [thing.get_image() for thing in self.everything]

    def get_speech_bubbles(self):
        """Return a list of speech bubbles currently in use by the cast."""
        speech_bubbles = []
        for character in self.character_list:
            if character.bubble:
                speech_bubbles.append(character.bubble)
        return speech_bubbles

    def restore(self):
        """Perform tasks required immediately after restoring a saved game. The
        tasks are:

        * build the sprite images
        * print the inventory
        * print the mouse inventory
        """
        self.sprites.build()
        for m in self.movables:
            m.build_images()
        self.eric.build_images()
        self.eric.print_inventory()
        self.eric.print_mouse_inventory()

    #//////////////////////////////////////////////////////////////////////////
    # Eric
    #//////////////////////////////////////////////////////////////////////////
    def is_beside_eric(self, character):
        """Return whether a character is beside Eric (and so need go no further
        to find him).

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        eric_x, eric_y = self.get_location_of_eric()
        return abs(character.x - eric_x) <= self.beside_eric_x_range and character.y == eric_y

    def get_location_of_eric(self):
        """Return the non-staircase location closest to Eric."""
        return self.eric.get_location()

    def expel_eric(self, character_id, command_list_id):
        """Mark Eric as expelled and set somebody on their way to expel him.

        :param character_id: The ID of the character who will expel Eric.
        :param command_list_id: The ID of the command list the character should
                                switch to.
        """
        self.eric.expelled = True
        self.change_command_list(character_id, command_list_id)

    def is_eric_expelled(self):
        """Return whether Eric is due to be or is in the process of being
        expelled.
        """
        return self.eric.expelled

    def get_eric_stopper(self):
        """Return any character who is currently standing in Eric's way (as
        Albert does when trying to prevent him from escaping), or `None` if
        there is none.
        """
        for c in self.character_list:
            if c.is_stopping_eric(self.eric):
                return c

    def freeze_eric(self):
        """Attempt to freeze Eric. The attempt will fail if Eric is writing on
        a blackboard.

        :return: `True` if Eric was frozen, `False` otherwise.
        """
        return self.eric.freeze()

    def unfreeze_eric(self):
        """Unfreeze Eric."""
        self.eric.unfreeze()

    def eric_understood(self):
        """Return whether Eric understood the message just delivered to him."""
        return self.eric.understood_message()

    def is_touching_eric(self, character):
        """Return whether a character is in the same location as Eric.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return (character.x, character.y) == (self.eric.x, self.eric.y)

    def is_eric_absent(self):
        """Return whether Eric is playing truant."""
        return self.eric.is_absent()

    def has_kissees(self):
        """Return whether anyone in the cast can kiss Eric."""
        return any(c.can_kiss_eric() for c in self.character_list)

    def kissee(self):
        """Return the first kissable candidate in front of Eric, or `None` if
        there is none.
        """
        for c in self._get_facing_characters(self.eric, self.kiss_distance):
            if c.can_kiss_eric() and c.is_interruptible() and c.is_standing():
                return c

    #//////////////////////////////////////////////////////////////////////////
    # Lines
    #//////////////////////////////////////////////////////////////////////////
    def _get_nearby_characters(self, character, candidates, witness):
        """Return a list of characters chosen from a list of candidates who are
        close enough to a target character to be visible to him.

        :type character: :class:`~pyskool.character.Character`
        :param character: The target character.
        :param candidates: The list of candidates.
        :param witness: If `True`, only choose characters that are facing the
                        target character.
        """
        x0 = character.x - self.lines_giving_range[0]
        x1 = character.x + self.lines_giving_range[0]
        y0 = character.y - self.lines_giving_range[1]
        y1 = character.y + self.lines_giving_range[1]
        nearby_characters = []
        for c in candidates:
            if c is not character and x0 <= c.x <= x1 and y0 <= c.y <= y1 and c.has_line_of_sight_to(character):
                if not witness or c.direction * (character.x - c.x) >= 0:
                    nearby_characters.append(c)
        return nearby_characters

    def get_nearby_adults(self, character):
        """Return a list of adults who are close to and facing a target
        character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The target character.
        """
        adults = [c for c in self.character_list if c.is_adult()]
        return self._get_nearby_characters(character, adults, True)

    def get_nearby_lines_givers(self, character):
        """Return a list of lines-givers who are close to and facing a target
        character, and are able to give lines now.

        :type character: :class:`~pyskool.character.Character`
        :param character: The target character.
        """
        nearby_lines_givers = []
        for c in self._get_nearby_characters(character, self.lines_givers, True):
            if c.can_give_lines_now():
                nearby_lines_givers.append(c)
        return nearby_lines_givers

    def get_nearest_lines_recipient(self, character):
        """Return the potential lines recipient who is nearest to a target
        character, or `None` if there is none.

        :type character: :class:`~pyskool.character.Character`
        :param character: The target character.
        """
        lines_recipients = [c for c in self.character_list if c.can_receive_lines()]
        candidates = self._get_nearby_characters(character, lines_recipients, False)
        if len(candidates) > 0:
            nearest = candidates[0]
            for c in candidates[1:]:
                if abs(c.x - character.x) < abs(nearest.x - character.x):
                    nearest = c
            return nearest

    def can_get_lines(self, message_id):
        """Return whether any member of the cast can give a specific lines
        message.

        :param message_id: The ID of the lines message.
        """
        return any(c.can_give_lines_message(message_id) for c in self.lines_givers)

    #//////////////////////////////////////////////////////////////////////////
    # Messages
    #//////////////////////////////////////////////////////////////////////////
    def expand_title(self, message, character):
        """Replace any title macros in a message with the title of a character.

        :param message: The message that may contain title macros.
        :type character: :class:`~pyskool.character.Character`
        :param character: The character whose title should be substituted.
        """
        if self.title_macro:
            message = message.replace(self.title_macro, character.get_title())
        return message

    def get_hit_tale(self, teacher):
        """Return a tale about hitting for the swot to tell a teacher.

        :param teacher: The teacher.
        :return: A 2-tuple containing the ID of the character blamed by the
                 swot, and the tale.
        """
        hitter_id = random.choice(self.hitters)
        message = self.expand_names(self.hit_tale.replace(self.grassee_macro, '$%s' % hitter_id))
        return hitter_id, self.expand_title(message, teacher)

    def get_write_tale(self, writer_id, teacher):
        """Return a tale about writing on the blackboard for the swot to tell a
        teacher.

        :param writer_id: The ID of the character to who wrote on the
                          blackboard.
        :param teacher: The teacher.
        :return: A 2-tuple containing `writer_id` and the tale, or
                 `(None, None)` if the character who wrote on the board is not
                 in the list of scapegoats favoured by the swot.
        """
        if writer_id in self.writers:
            message = self.expand_names(self.write_tale.replace(self.grassee_macro, '$%s' % writer_id))
            return writer_id, self.expand_title(message, teacher)
        return None, None

    def get_absent_tale(self, teacher):
        """Return a tale about Eric being absent for the swot to tell a
        teacher.

        :param teacher: The teacher.
        """
        return self.expand_title(self.expand_names(self.absent_tale), teacher)

    def expand_names(self, message):
        """Replace occurrences of $BLAH in a message with the name of the
        character whose unique ID is 'BLAH'.

        :param message: The message.
        """
        index = 0
        marker = '$'
        while message.find(marker, index) >=0:
            start = message.index(marker, index)
            end = start + 1
            while end < len(message) and message[end].isalnum():
                end += 1
            character = self.get(message[start + 1:end])
            if character:
                message = message.replace(message[start:end], character.name, 1)
            index = end
        return message

    #//////////////////////////////////////////////////////////////////////////
    # Plants
    #//////////////////////////////////////////////////////////////////////////
    def water_plant(self, plant_pot, liquid):
        """Water (or sherry) a plant. If the liquid is water, the plant will
        start growing.

        :param plant_pot: The plant pot hit by the water or sherry.
        :param liquid: The type of liquid.
        """
        if liquid == self.water_id:
            plant_pot.plant.grow()

    def lift_anyone_at(self, x, y):
        """Lift any character at a given location. This is used by plants when
        growing.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        for c in self.character_list:
            if (c.x, c.y) == (x, y):
                c.y -= 1

    def plant(self, character):
        """Return the plant that a character is standing on, or `None` if he's
        not standing on one.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        for plant in self.plants:
            if plant.supports(character):
                return plant

    def drop_anyone_at(self, x, y):
        """Drop any character at a given location. This is used by plants when
        they die.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        for c in self.character_list:
            if (c.x, c.y) == (x, y):
                c.fall_off_plant()
