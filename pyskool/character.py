# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2012-2014 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Character` class, which determines how characters are
animated and how they behave.
"""

import random
import re

from .location import Location
from . import ai
from .animatorystates import (
    ARM_UP, CATAPULT0, CATAPULT1, HITTING0, HITTING1, KISSING_ERIC,
    KNOCKED_OUT, KNOCKED_OVER, RIDING_BIKE0, RIDING_BIKE1, SITTING_ON_CHAIR,
    SITTING_ON_FLOOR, WALK0, WALK1, WALK2, WALK3, WATERPISTOL
)
from . import lines
from .lesson import QAGenerator
from . import sound
from . import debug

class Character:
    """Base class for anything in the game that moves.

    :param character_id: Unique ID.
    :param name: Display name.
    :param head_xy: The coordinates of the character's head within his sprite
                    when he's standing upright (used for collision detection).
    :param flags: Character flags.
    """
    def __init__(self, character_id, name, head_xy=None, flags=''):
        self.character_id = character_id
        self.name = name
        self.head_xy = head_xy
        self.flags = flags
        self.x, self.y = -3, 0
        self.random_locations = ()
        self.direction = 1 # 1 = facing right, -1 = facing left
        self.vertical_direction = 0 # 1 = down, 0 = neither up nor down
        self.action = 0 # 0 = walking, 1 = still, 2 = writing, 3 = other
        self.walk_states = [WALK0, WALK1, WALK2, WALK3]
        self.speed = 1 # 1 = walk, 2 = run
        self.fixed_speed = False
        self.speed_change_delay = 1
        self.always_runs = False
        self.walk_delay = None
        self.action_delay = 1
        self.staircase = None
        self.barrier = None
        self.room = None
        self.floor = None
        self.command_lists = {}
        self.sit_down_messages = []
        self.bubble = None
        self.blackboard_messages = []
        self.qa_generator = None
        self.wiping_board = False
        self.pellet = None
        self.water = None
        self.stinkbomb = None
        self.lines_message = None
        self.message_box_coords = None
        self.lines_messages = {}
        self.come_along_messages = []
        self.come_along_index = 0
        self.lesson_messages = []
        self.changes_seats = True
        self.special_answer = None
        self.safe_secret = None
        self.bike_secret = None
        self.storeroom_secret = None
        self.kisses = 0
        self.barrier_id = character_id
        self.fly_phases = None
        self.stop_eric = False
        self.width = None
        self.height = None
        self.command_list = ai.CommandList(self)

    def __getstate__(self):
        d = self.__dict__.copy()
        d['bubble'] = None
        return d

    def is_home(self, x):
        """Return whether the character is on the 'home' side of a given
        x-coordinate. For male characters, the home side is the left side; for
        female characters, it is the right side.

        :param x: The x-coordinate to check.
        """
        if 'G' in self.flags:
            return self.x > x
        elif 'B' in self.flags:
            return self.x < x - 1
        return True

    def is_punchable_now(self):
        """Return whether the character is amenable to being punched at this
        exact moment.
        """
        return self.is_punchable() and (self.is_standing() or self.is_sitting_on_chair())

    def get_location(self):
        """Return the on-floor location that is closest to the character."""
        staircase = self.skool.staircase(self)
        if staircase and staircase.supports(self):
            if staircase.bottom.y - self.y < self.y - staircase.top.y:
                return staircase.bottom.coords()
            return staircase.top.coords()
        return self.x, self.skool.floor_below(self).y

    def check_mouse(self, mouse):
        """Make the character respond appropriately to a mouse. The character
        will start jumping up and down if he:

        * is scared of mice, and
        * is on the same floor as the mouse, and
        * is facing it, and
        * is close enough to see it, and
        * is not doing anything else that precludes jumping up and down

        :param mouse: The mouse to check.
        """
        if not (self.is_scared_of_mice() and self.is_interruptible() and self.bubble is None):
            return
        if self.y == mouse.y and 0 <= (mouse.x - self.x) * self.direction <= self.cast.mouse_proximity:
            self.add_command(ai.EvadeMouse(self.cast.evade_mouse_delay))

    def get_random_destination(self):
        """Return a location randomly chosen from the character's collection.

        :return: An `(x, y)` tuple.
        """
        dest = (self.x, self.y)
        choice = len(self.random_locations)
        if choice == 0:
            return dest
        if choice == 1:
            return self.random_locations[0]
        while dest == (self.x, self.y):
            dest = random.choice(self.random_locations)
        return dest

    def impeded(self, bottom_y, top_y):
        """Return whether the character is blocked by an object (such as a
        wall).

        :param bottom_y: The y-coordinate of the bottom of the object.
        :param top_y: The y-coordinate of the top of the object.
        """
        return top_y - self.height < self.y <= bottom_y

    def can_open_door(self, door):
        """Return whether the character can open a door.

        :param door: The door.
        """
        return self.can_open_doors()

    def chair(self, check_dir=True):
        """Return the chair that is beside the character.

        :param check_dir: If `True`, return the chair only if the character is
                          facing the correct way to sit in it; otherwise,
                          return the chair whichever way the character is
                          facing.
        :return: The chair, or `None` if there is none.
        """
        return self.skool.chair(self, check_dir)

    def can_sit_on_stairs(self):
        """Return whether the character can sit on the stairs."""
        return True

    def dethrone(self):
        """Knock the character out of his seat."""
        self.sit_on_floor()
        self.add_command(ai.FindSeat(False))
        self.add_command(ai.Floored(self.cast.dethroned_delay))

    def keep_seat(self):
        """Indicate that the character should return to the same seat if he's
        knocked out of it. This is used by the swot during lessons. (The swot
        must return to the same seat so that he remains underneath his speech
        bubble.)
        """
        self.changes_seats = False

    def is_deckable(self):
        """Return whether the character is in an animatory state and location
        that are amenable to him being knocked over.
        """
        if not self.skool.on_floor(self):
            return False
        if self.is_adult():
            return self.is_standing() or self.has_arm_raised()
        return self.is_standing() or self.is_sitting_on_chair()

    def can_give_lines_now(self):
        """Return whether the character is in an animatory state and location
        that are amenable to him giving lines.
        """
        if self.skool.on_floor(self) or self.skool.on_staircase(self):
            return self.is_standing() or self.has_arm_raised()
        return False

    def is_door(self):
        """Return whether the character is a door.

        :return: `False`.
        """
        return False

    def get_floor(self, thing=None):
        """Return the floor that the character (or some other object) is on (or
        `None` if the character or object is not on a floor).

        :param thing: If not `None`, return the floor that `thing` is on;
                      otherwise return the floor that the character is on.
        """
        return self.skool.floor(thing or self)

    def on_stairs(self):
        """Return whether the character is on one of the steps of a
        staircase.
        """
        if self.staircase:
            return self.x not in (self.staircase.bottom.x, self.staircase.top.x)
        return False

    def get_next_staircase(self, destination):
        """Return the next staircase the character must ascend or descend in
        order to reach his destination.

        :type destination: :class:`~location.Location`
        :param destination: The character's destination.
        """
        if self.get_floor() is None:
            debug.log('%s at %i, %i has no home floor' % (self.name, self.x, self.y))
        if self.get_floor(destination) is None:
            debug.log('%s at %i, %i going to %i, %i has no destination floor' % (self.name, self.x, self.y, destination.x, destination.y))
        return self.skool.next_staircase(self.get_floor(), self.get_floor(destination))

    def open_door(self):
        """Return an :class:`~ai.OpenDoor` command for the door or window in front of the
        character.
        """
        return ai.OpenDoor(self.barrier.barrier_id)

    def move_door(self, barrier_id, shut):
        """Make the character open or close a door or window.

        :param barrier_id: The ID of the door or window.
        :param shut: `True` if the door or window should be closed, `False`
                     if it should be opened.
        """
        if shut:
            self.skool.move_bike_away(barrier_id)
        self.skool.move_door(barrier_id, shut)

    def get_next_chair(self, move_along, go_to_back):
        """Return the next chair that the character should find and sit on (at
        the start of a lesson, or after being dethroned).

        :param move_along: `True` if the character should proceed to the next
                           seat along (as after being dethroned), `False` if
                           he should re-take the seat he was pushed out of (as
                           the swot does).
        :param go_to_back: `True` if the character should proceed to the back
                           seat (as at the start of a lesson), `False`
                           otherwise.
        :return: A 2-tuple containing the target chair and the direction it
                 faces.
        """
        if self.room:
            return self.room.get_next_chair(self, move_along and self.changes_seats, go_to_back)
        debug.error("Character %s (%s) at (%s,%s) cannot find a chair because self.room == None" % (self.character_id, self.name, self.x, self.y))
        return None, 1

    def say(self, words, shift):
        """Make the character start or continue saying something.

        :type words: string
        :param words: The words to speak.
        :type shift: number
        :param shift: The amount by which the words should be shifted in the
                      text window of the speech bubble.
        :return: `True` if the character has finished speaking, `False`
                 otherwise.
        """
        if not self.bubble:
            bubble_x = 8 * ((self.x + 1) // 8)
            bubble_y = self.y - (3 if self.is_adult() or self.is_standing() else 2)
            self.bubble = [bubble_x, bubble_y, None]
        lip_pos = (self.x + 1) % 8
        self.bubble[2], done = self.screen.get_bubble(words, lip_pos, shift)
        return done

    def remove_bubble(self):
        """Remove the character's speech bubble."""
        self.bubble = None

    def get_blackboard(self):
        """Return the blackboard in the room in which the character is
        located, or `None` if there is none.
        """
        if self.room:
            return self.room.blackboard

    def wipe_board(self, column):
        """Wipe a bit of a blackboard clean.

        :param column: The column of the blackboard to wipe.
        """
        self.skool.wipe_board(self.get_blackboard(), column)

    def get_blackboard_backtrack(self):
        """Return the distance a teacher should walk back after wiping a
        blackboard.
        """
        return self.cast.blackboard_backtrack

    def write_on_board(self, message, index):
        """Make this character start or continue writing on a blackboard.

        :param message: The message being written.
        :param index: The index of the next character in the message to write.
        """
        self.action = 2
        return self.skool.write_on_board(self, self.get_blackboard(), message, index)

    def get_blackboard_pace_distance(self):
        """Return the distance a teacher should pace up and down in front of
        the blackboard during a lesson without a question-and-answer session.
        """
        return self.cast.bb_pace_distance

    def resolve_location_id(self, location_id):
        """Return the location with a given ID.

        :param location_id: The ID of the location.
        :return: The appropriate :class:`~location.Location`.
        """
        return self.skool.resolve_location_id(location_id)

    def get_qa_generator(self):
        """Return a :class:`~lesson.QAGenerator` for the character to use during this
        lesson.
        """
        if self.qa_generator is None:
            self.qa_generator = QAGenerator()
        return self.qa_generator

    def deck(self, paralyse=False):
        """Knock the character to the floor (as when struck by a fist or
        catapult pellet).

        :param paralyse: If `True`, the character will be rendered unconscious
                         until shortly before the bell is due to ring (as when
                         Albert is struck by a falling conker).
        """
        self.knock_over()
        self.kisses = max(0, self.kisses - self.cast.kiss_deckrement)
        if self.is_adult():
            self.add_command(ai.KnockedOver(self.cast.knocked_over_delay, self.cast.reprimand_delay, paralyse))
            if paralyse:
                self.skool.play_sound(sound.CONKER)
                self.skool.rewind_clock(self.cast.conker_clock_ticks)
        else:
            if self.previous_as == SITTING_ON_CHAIR:
                self.chair().vacate()
                self.add_command(ai.FindSeat(False, False))
            self.add_command(ai.Floored(self.cast.ko_delay))

    def is_time_to_wake(self):
        """Return whether it is time for the character to regain consciousness
        after being struck by a falling conker.
        """
        return self.skool.is_time_remaining(self.cast.conker_wake_time)

    def will_write_on_board(self):
        """Return whether the character will write on a blackboard. The answer
        is used by teachers who are conducting a class without Eric.
        """
        return random.random() < self.cast.write_on_board_probability

    def will_hit(self):
        """Return whether the character wants to throw a punch now."""
        return random.random() < self.cast.hit_probability

    def can_fire_catapult(self):
        """Return whether the character can fire a catapult. The answer will be
        `True` if and only if all of the following conditions are met:

        * the character has :data:`~pyskool.animatorystates.CATAPULT0` and
          :data:`~pyskool.animatorystates.CATAPULT1` sprites
        * the character has a catapult pellet
        * the catapult pellet is not currently airborne
        """
        if CATAPULT0 in self.as_dict_L and CATAPULT1 in self.as_dict_L:
            return self.pellet and not self.pellet.is_visible()

    def will_fire_catapult(self):
        """Return whether the character wants to fire a catapult now."""
        return random.random() < self.cast.fire_catapult_probability

    def fire_catapult(self):
        """Make the character launch his catapult pellet."""
        self.pellet.launch(self.x + self.direction, self.y, self.direction)

    def can_fire_water_pistol(self):
        """Return whether the character can fire a water pistol. The answer
        will be `True` if and only if all of the following conditions are met:

        * the character has a :data:`~pyskool.animatorystates.WATERPISTOL`
          sprite
        * the character has a water pistol
        * the character's water/sherry sprite is not currently visible
        """
        return WATERPISTOL in self.as_dict_L and self.water and not self.water.is_visible()

    def fire_water_pistol(self, liquid=None):
        """Make the character fire his water pistol. A stream of water or
        sherry will begin its trajectory as a result.

        :param liquid: The ID of the liquid.
        """
        self.water.launch(self.x + 2 * self.direction, self.y - 2, self.direction, liquid or self.cast.water_id)

    def can_drop_stinkbomb(self):
        """Return whether the character can drop a stinkbomb. The answer will
        be `True` if and only if all of the following conditions are met:

        * the character has an :data:`~pyskool.animatorystates.ARM_UP` sprite
        * the character can drop stinkbombs
        * the character's stinkbomb cloud sprite is not currently visible
        """
        return ARM_UP in self.as_dict_L and self.stinkbomb and not self.stinkbomb.is_visible()

    def drop_stinkbomb(self):
        """Make the character drop a stinkbomb. A stinkbomb cloud will appear
        as a result."""
        self.stinkbomb.drop(self.x + self.direction, self.y)

    def check_door_status(self, barrier_id, shut):
        """Return whether a door or window is in a given state (open or
        closed).

        :param barrier_id: The ID of the door or window.
        :param shut: `True` to check whether the door or window is closed,
                     `False` to check whether it's open.
        """
        return self.skool.is_door_shut(barrier_id) == shut

    def stalk(self, character_id):
        """Set the character's destination equal to that of another character's
        destination (if they are both under the control of a :class:`~ai.GoTo`
        command).
        """
        self.command_list.set_GoTo_destination(self.get_destination(character_id))

    def get_GoTo_destination(self):
        """Return the character's destination, or `None` if he is not under
        the control of a :class:`~ai.GoTo` command.
        """
        return self.command_list.get_GoTo_destination()

    def can_see_special_answer(self):
        """Return whether the character can see his special answer written on
        a blackboard.
        """
        if self.special_answer:
            blackboard = self.skool.visible_blackboard(self)
            if blackboard:
                return blackboard.shows(self.special_answer)

    def _print_secret(self, secret):
        """Print a message box containing a safe, bike or storeroom combination
        character.

        :param secret: The combination character.
        """
        self.print_message_box((secret,), self.cast.secret_ink, self.cast.secret_paper, sound.LINES2)

    def reveal_safe_secret(self, decked):
        """Make the character reveal his safe combination letter if certain
        conditions are met. The conditions are:

        * the character is on-screen
        * the character holds a safe combination letter
        * the safe has not been opened yet
        * the character can see his special answer on a blackboard, or the
          character has no special answer and all the shields are flashing

        :param decked: Whether the character has been knocked over.
        """
        if not self.screen.contains(self):
            return
        flashing = self.special_answer is None
        if not self.safe_secret or not self.skool.can_reveal_safe_secret(flashing):
            return
        reveal = flashing if decked else self.can_see_special_answer()
        if reveal:
            self._print_secret(self.safe_secret)

    def reveal_bike_secret(self):
        """Make the character reveal his bike combination digit (if he has
        one, and he is on-screen).
        """
        if self.bike_secret and self.screen.contains(self):
            self._print_secret(self.bike_secret)

    def reveal_storeroom_secret(self):
        """Make the character reveal his storeroom combination letter (if he
        has one, and he is on-screen).
        """
        if self.storeroom_secret and self.screen.contains(self):
            self._print_secret(self.storeroom_secret)

    def _get_head_coords(self):
        """Return the coordinates of the character's head."""
        head_x, head_y = self.x + self.head_xy[0], self.y + self.head_xy[1]
        if self.is_adult() and self.is_knocked_over():
            head_y += 1
        return head_x, head_y

    def head_at(self, x, y):
        """Return whether the character's head is at a given location.

        :param x: The x-coordinate of the location.
        :param y: The x-coordinate of the location.
        """
        return (x, y) == self._get_head_coords()

    def check_shields_at(self, x, y):
        """Return whether there is a shield at a given location.

        :param x: The x-coordinate to check.
        :param y: The y-coordinate to check.
        """
        return self.skool.hit_shield(x, y)

    def end_game(self):
        """End the game."""
        self.skool.end_game()

    def trip_people_up(self):
        """Make the character trip people up at his current location."""
        self.cast.trip_people_up_at(self, self.x, self.y)

    def hide(self):
        """Hide the character. This is used mostly by inanimate objects (such
        as the desk lid) or non-human characters (such as mice) that are not
        always in the play area.
        """
        self.x = -3

    def is_visible(self):
        """Return whether the character is somewhere in the play area. The
        answer is generally `True` for human characters, but may be `False`
        for inanimate objects (such as the desk lid) or non-human characters
        (such as mice, which occasionally hide).
        """
        return self.x >= 0

    def fall_off_plant(self):
        """Make the character fall off a plant that has just died. This method
        adds a :class:`~ai.FallToFloor` command to the character's command list. It is
        not currently used by any non-player characters, because they never
        climb onto plants.
        """
        self.add_command(ai.FallToFloor())

    def fall_to_floor(self):
        """Make the character sit on the floor for a bit (as after falling off
        a plant that has just died, or upon landing after jumping from the
        saddle of a bike). This method is not currently used by any non-player
        characters, because they never climb onto plants or ride bikes.
        """
        self.sit_on_floor()
        self.walk_delay = 10

    def can_smell_stinkbomb(self, stinkbomb):
        """Return whether the character can smell a given stinkbomb. The answer
        will be true if the character:

        * can smell stinkbombs generally, and
        * is standing up, and
        * is on the same floor as and within smelling range of the stinkbomb

        :param stinkbomb: The stinkbomb to check.
        """
        if self.can_smell_stinkbombs() and self.is_standing() and self.y == stinkbomb.y:
            return abs(stinkbomb.x - self.x) <= stinkbomb.stink_range
        return False

    def open_window(self, window):
        """Make the character take a detour to a window and open it.

        :type window: :class:`~barrier.Window`
        :param window: The window to open.
        """
        if not self.command_list.is_GoToing():
            # The character should return to the location from which he took
            # his window-opening detour so that he can resume his command list
            # correctly
            self.add_command(ai.GoToXY(self.x, self.y))
        self.add_command(ai.OpenDoor(window.barrier_id))
        self.add_command(ai.GoToXY(*window.opener_coords))

    #//////////////////////////////////////////////////////////////////////////
    # Character construction
    #//////////////////////////////////////////////////////////////////////////
    def set_components(self, cast, skool, screen, config):
        """Set the character up with access to essential objects.

        :type cast: :class:`~cast.Cast`
        :param cast: The cast.
        :type skool: :class:`~skool.Skool`
        :param skool: The skool.
        :type screen: :class:`~graphics.Screen`
        :param screen: The screen.
        :type config: dict
        :param config: Configuration parameters from the ini file.
        """
        self.cast = cast
        self.kisses = self.cast.initial_kiss_count
        self.slow_delay = config.get('GoSlow', 5)
        self.fast_delay = config.get('GoFast', 3)
        self.faster_delay = config.get('GoFaster', 2)
        self.walk_delay = random.randint(self.fast_delay, self.slow_delay)
        self.speed_change_delay_range = config.get('SpeedChangeDelayRange', (16, 31))
        self.width = self.cast.sprite_width
        self.height = self.cast.sprite_height
        self.skool = skool
        self.screen = screen

    def set_initial_location(self, x, y):
        """Set the character's initial location.

        :param x: Initial x-coordinate.
        :param y: Initial y-coordinate.
        """
        self.initial_location = Location((x, y))
        self.x = x
        self.y = y

    def add_sit_down_message(self, message):
        """Add a sit-down message to the character's repertoire.

        :param message: The message to add.
        """
        self.sit_down_messages.append(message)

    def add_blackboard_message(self, message):
        """Add a blackboard message to the character's repertoire.

        :param message: The message to add.
        """
        self.blackboard_messages.append(message)

    def set_animatory_states(self, as_dict_L, as_dict_R):
        """Set the character's animatory states (sprite collection). These are
        organised into a collection of left-facing sprites keyed by animatory
        state name (such as :data:`~pyskool.animatorystates.WALK0`), and a
        corresponding collection of right-facing sprites.

        :type as_dict_L: dict
        :param as_dict_L: The left-facing sprites.
        :type as_dict_R: dict
        :param as_dict_R: The right-facing sprites.
        """
        self.as_dict_L = as_dict_L
        self.as_dict_R = as_dict_R

    def set_random_locations(self, locations):
        """Set the character's collection of random locations.

        :param locations: Sequence of `(x, y)` tuples.
        """
        self.random_locations = locations

    def add_lines_message(self, message_id, message_lines):
        """Add a lines message to the character's collection of lines messages
        that he is authorised to utter.

        :param message_id: The lines message ID.
        :param message_lines: A 2-element tuple containing the lines of text of
                              the message.
        """
        if message_id not in self.lines_messages:
            self.lines_messages[message_id] = message_lines
        if message_id.startswith(lines.COME_ALONG_PREFIX):
            self.come_along_messages.append(message_id)

    def add_lesson_message(self, message, condition):
        """Add a lesson message to the character's collection. A lesson message
        is something like 'START READING AT THE NEXT CHAPTER IN YOUR BOOKS',
        which will be used by a teacher during class if he's not teaching Eric,
        or he has decided not to have a question-and-answer session with the
        swot.

        :param message: The lesson message.
        :param condition: The condition identifier; the lesson message will be
                          used only if this condition is true.
        """
        self.lesson_messages.append((message, condition))

    def add_command_list(self, lesson_id, command_list_id):
        """Add a command list ID to the character's personal timetable.

        :param lesson_id: The ID of the lesson in which the command list will
                          be used.
        :param command_list_id: The command list ID.
        """
        self.command_lists[lesson_id] = command_list_id

    #//////////////////////////////////////////////////////////////////////////
    # Initialisation
    #//////////////////////////////////////////////////////////////////////////
    def initialise_special_answer(self):
        """Initialise the character's special answer (if he has one). A special
        answer is something that the character must see written on a blackboard
        before he will reveal his safe combination letter.
        """
        if self.qa_generator:
            self.special_answer = self.qa_generator.initialise_special_answer()

    def initialise_animatory_state(self, initial_as, direction):
        """Set the character's initial animatory state and direction.

        :param initial_as: The animatory state.
        :param direction: The direction.
        """
        self.direction = self.initial_direction = direction
        self.animatory_state = self.initial_as = initial_as

    def reinitialise(self):
        """Reinitialise the character after a game has ended or restarted. In
        particular:

        * restore the initial animatory state and location
        * remove any speech bubble
        * create a new, empty command list
        """
        self.x, self.y = self.initial_location.x, self.initial_location.y
        self.direction = self.initial_direction
        self.vertical_direction = 0
        self.animatory_state = self.initial_as
        self.bubble = None
        self.wiping_board = False
        self.action = 0
        self.speed = 1
        self.fixed_speed = False
        self.speed_change_delay = 1
        self.kisses = self.cast.initial_kiss_count
        self.stop_eric = False
        self.command_list = ai.CommandList(self)

    def initialise_safe_secret(self):
        """Set and return a safe combination letter (chosen at random) for the
        character to hold.
        """
        if self.has_safe_secret():
            self.safe_secret = random.choice(self.cast.safe_secrets)
        return self.safe_secret

    def initialise_bike_secret(self):
        """Set and return a bike combination digit (chosen at random) for the
        character to hold.
        """
        if self.has_bike_secret():
            self.bike_secret = random.choice(self.cast.bike_secrets)
        return self.bike_secret

    def initialise_storeroom_secret(self):
        """Set and return a storeroom combination letter (chosen at random) for
        the character to hold.
        """
        if self.has_storeroom_secret():
            self.storeroom_secret = random.choice(self.cast.storeroom_secrets)
        return self.storeroom_secret

    #//////////////////////////////////////////////////////////////////////////
    # Animatory states
    #//////////////////////////////////////////////////////////////////////////
    def is_standing(self):
        """Return whether the character is upright (in a walking animatory
        state).
        """
        return self.animatory_state in (WALK0, WALK1, WALK2, WALK3)

    def is_sitting(self):
        """Return whether the character is sitting down (on the floor or on a
        chair).
        """
        return self.animatory_state in (SITTING_ON_FLOOR, SITTING_ON_CHAIR)

    def is_sitting_on_floor(self):
        """Return whether the character is sitting on the floor."""
        return self.animatory_state == SITTING_ON_FLOOR and self.get_floor()

    def is_sitting_on_chair(self):
        """Return whether the character is sitting on a chair."""
        return self.animatory_state == SITTING_ON_CHAIR and self.chair()

    def is_sitting_on_stairs(self):
        """Return whether the character is sitting on a staircase."""
        return self.animatory_state == SITTING_ON_CHAIR and not self.chair()

    def is_knocked_over(self):
        """Return whether the character has been knocked over."""
        return self.animatory_state == KNOCKED_OVER

    def has_arm_raised(self):
        """Return whether the character has his arm raised (as when writing on
        a blackboard or opening a door).
        """
        return self.animatory_state == ARM_UP

    def is_knocked_out(self):
        """Return whether the character has been knocked out."""
        return self.animatory_state == KNOCKED_OUT

    def is_raising_catapult(self):
        """Return whether the character is raising his catapult."""
        return self.animatory_state == CATAPULT0

    def is_firing_catapult(self):
        """Return whether the character is firing his catapult."""
        return self.animatory_state == CATAPULT1

    def is_lowering_catapult(self):
        """Return whether the character is lowering his catapult."""
        return self.animatory_state == CATAPULT0

    def is_raising_fist(self):
        """Return whether the character is raising his fist."""
        return self.animatory_state == HITTING0

    def is_punching(self):
        """Return whether the character is punching."""
        return self.animatory_state == HITTING1

    def is_lowering_fist(self):
        """Return whether the character is lowering his fist."""
        return self.animatory_state == HITTING0

    def is_riding_bike(self):
        """Return whether the character is riding a bike."""
        return self.animatory_state in (RIDING_BIKE0, RIDING_BIKE1)

    def midstride(self):
        """Return whether the character is midstride."""
        return self.animatory_state in (WALK1, WALK3)

    def turn(self):
        """Make the character turn round."""
        self.direction *= -1

    def get_up(self):
        """Make a character get up from a sitting position. If the character
        was sitting in a chair, the chair will be marked vacant.
        """
        if self.is_sitting_on_chair():
            self.chair().vacate()
        self.animatory_state = self.previous_as

    def stand_up(self):
        """Make the character stand up."""
        self.animatory_state = WALK0
        self.reset_walk_delay()

    def sit_on_floor(self):
        """Make the character sit on the floor."""
        self.animatory_state = SITTING_ON_FLOOR

    def raise_arm(self):
        """Make the character raise his arm."""
        self.animatory_state = ARM_UP

    def lower_arm(self):
        """Make the character lower his arm."""
        self.animatory_state = WALK0

    def knock_over(self):
        """Knock the character over (as when hit by a catapult pellet)."""
        self.previous_as = self.animatory_state
        if self.is_adult():
            self.animatory_state = KNOCKED_OVER
        else:
            self.animatory_state = KNOCKED_OUT
        self.action = 1

    def raise_fist(self):
        """Make the character start raising his fist."""
        self.animatory_state = HITTING0
        self.action = 3

    def punch(self):
        """Make the character finish raising his fist (to punching height)."""
        self.animatory_state = HITTING1

    def lower_fist(self):
        """Make the character start lowering his fist."""
        self.animatory_state = HITTING0

    def raise_catapult(self):
        """Make the character start raising his catapult."""
        self.animatory_state = CATAPULT0
        self.action = 3

    def aim_catapult(self):
        """Make the character finish raising his catapult (to firing height).
        """
        self.animatory_state = CATAPULT1

    def lower_catapult(self):
        """Make the character start lowering his catapult."""
        self.animatory_state = CATAPULT0

    def aim_water_pistol(self):
        """Make the character aim his water pistol."""
        self.animatory_state = WATERPISTOL

    def complete_action(self):
        """Restore the character's animatory state after completing an action
        (such as firing a catapult or water pistol).
        """
        self.animatory_state = WALK0
        self.action = 0

    #//////////////////////////////////////////////////////////////////////////
    # Cast queries
    #//////////////////////////////////////////////////////////////////////////
    def is_facing(self, thing):
        """Return whether the character is facing something or somebody else.

        :param thing: The thing (such as a blackboard or another character) to
                      check.
        """
        return self.direction * (thing.x - self.x) >= 0

    def get_punchee(self, offset):
        """Return the first punchable character in front of this one.

        :type offset: number
        :param offset: The distance in front of this character to check for
                       punchees.
        :return: A punchable character, or `None` if there is none at the
                 given distance.
        """
        return self.cast.get_punchee(self, offset)

    def get_nearby_adults(self):
        """Return a list of adults who are close enough to the character (and
        are facing the right way) to be able to see him.
        """
        return self.cast.get_nearby_adults(self)

    def get_destination(self, character_id):
        """Return the destination of another character.

        :param character_id: The ID of the character to get the destination of.
        """
        character = self.cast.get(character_id)
        if character:
            return character.get_GoTo_destination()

    def has_line_of_sight_to(self, character):
        """Return whether the character has a line of sight to another
        character (that is, there are no walls between them).

        :type character: :class:`~character.Character`
        :param character: The other character.
        """
        return self.skool.line_of_sight_between(self, character)

    def wait_at_door(self, door_id):
        """Return whether the characters are on the 'home' side of the given
        door.
        """
        return self.cast.is_home(self.skool.get_door(door_id).x)

    #//////////////////////////////////////////////////////////////////////////
    # Character flags
    #//////////////////////////////////////////////////////////////////////////
    def is_adult(self):
        """Return whether the character is an adult. The answer is used in
        various situations where the difference between an adult and a child is
        significant, as when placing a speech bubble, or being knocked over or
        knocked out by a catapult pellet.
        """
        return 'A' in self.flags

    def is_conkerable(self):
        """Return whether the character can be knocked over by a falling
        conker.
        """
        return 'C' in self.flags

    def can_open_doors(self):
        """Return whether the character can open doors and windows."""
        return 'D' in self.flags

    def is_punchable(self):
        """Return whether the character can be knocked over by a punch.
        """
        return 'F' in self.flags

    def has_safe_key(self):
        """Return whether the character holds the key to the safe."""
        return 'K' in self.flags

    def can_give_lines(self):
        """Return whether the character can give lines."""
        return 'L' in self.flags

    def is_scared_of_mice(self):
        """Return whether the character is scared of mice."""
        return 'M' in self.flags

    def can_smell_stinkbombs(self):
        """Return whether the character can smell stinkbombs (and will be
        compelled to open a nearby window if he smells one).
        """
        return 'N' in self.flags

    def is_pelletable(self):
        """Return whether the character can be knocked over by a catapult
        pellet.
        """
        return 'P' in self.flags

    def can_receive_lines(self):
        """Return whether the character can be given lines."""
        return 'R' in self.flags

    def has_safe_secret(self):
        """Return whether the character holds a safe combination letter."""
        return 'S' in self.flags

    def is_trippable(self):
        """Return whether the character can be tripped up by a stampeding kid.
        """
        return 'T' in self.flags

    def adds_to_lines_total(self):
        """Return whether any lines the character gets are added to Eric's
        total.
        """
        return 'U' in self.flags

    def adds_to_score(self):
        """Return whether any lines the character gets are added to Eric's
        score.
        """
        return 'V' in self.flags

    def sometimes_runs(self):
        """Return whether the character sometimes runs instead of walking (as
        the kids do).
        """
        return 'W' not in self.flags

    def has_bike_secret(self):
        """Return whether the character holds a bike combination digit."""
        return 'X' in self.flags

    def has_storeroom_secret(self):
        """Return whether the character holds a storeroom combination letter.
        """
        return 'Y' in self.flags

    def is_very_conkerable(self):
        """Return whether the character will be rendered unconscious for a
        while if struck by a falling conker.
        """
        return 'Z' in self.flags

    #//////////////////////////////////////////////////////////////////////////
    # Command list
    #//////////////////////////////////////////////////////////////////////////
    def set_subcommand(self, command_name, args):
        """Set a subcommand on the character's command list. See
        :meth:`pyskool.ai.CommandList.set_subcommand` for details.
        """
        self.command_list.set_subcommand(command_name, args)

    def set_controlling_command(self, command):
        """Set the controlling command on the character's command list. See
        :meth:`pyskool.ai.CommandList.set_controlling_command` for more
        details.

        :type command: :class:`~ai.Command`
        :param command: The controlling command.
        """
        self.command_list.set_controlling_command(command)

    def is_interruptible(self):
        """Return whether the character's current command can be
        interrupted.
        """
        return self.command_list.is_interruptible()

    def get_command_list_id(self, lesson_id):
        """Return a command list ID from the character's personal timetable.

        :param lesson_id: The ID of the lesson to retrieve the command list
                          for.
        """
        return self.command_lists[lesson_id]

    def set_command_list_template(self, template):
        """Set the character's command list template. This method is called to
        change a character's command list (for example, after the bell rings).
        """
        self.command_list.set_template(template)
        self.lesson = None
        self.trigger_speed_change()

    def change_command_list(self, command_list_id):
        """Make the character switch to a different command list immediately.

        :param command_list_id: The ID of the command list to switch to.
        """
        self.cast.change_command_list(self.character_id, command_list_id)

    def restart_command_list(self):
        """Restart the character's command list."""
        self.command_list.restart()

    def add_command(self, command):
        """Add a command to the character's command list. The command will
        become the character's current command (that is, it will be executed
        the next time the character is moved).

        :type command: :class:`~ai.Command`
        :param command: The command to add.
        """
        self.command_list.add_command(command)

    def set_restart_point(self):
        """Discard the current and all previous commands in the character's
        command list. Any command that restarts the command list from now on
        will see the next command as the first.
        """
        self.command_list.set_restart_point()

    def jump_if_shut(self, door_id, offset):
        """Jump forwards (or backwards) in the character's command list if a
        given door is shut.

        :param door_id: The ID of the door to check.
        :type offset: number
        :param offset: The offset by which to jump in the command list.
        """
        if self.skool.is_door_shut(door_id):
            self.command_list.jump(offset)

    def jump_if_open(self, door_id, offset):
        """Jump forwards (or backwards) in the character's command list if a
        given door is open.

        :param door_id: The ID of the door to check.
        :type offset: number
        :param offset: The offset by which to jump in the command list.
        """
        if not self.skool.is_door_shut(door_id):
            self.command_list.jump(offset)

    #//////////////////////////////////////////////////////////////////////////
    # Drawing
    #//////////////////////////////////////////////////////////////////////////
    def get_image(self):
        """Return the image (a `pygame.Surface`) corresponding to the
        character's current animatory state.
        """
        as_dict = self.as_dict_R if self.direction > 0 else self.as_dict_L
        return (self.x, self.y, as_dict[self.animatory_state])

    def build_images(self):
        """Build the animatory state images for the character. This method is
        called after rescaling the screen or loading a saved game.
        """
        for image in self.as_dict_L.values():
            image.build()
        for image in self.as_dict_R.values():
            image.build()

    #//////////////////////////////////////////////////////////////////////////
    # Eric
    #//////////////////////////////////////////////////////////////////////////
    def is_eric(self):
        """Return whether the character is Eric.

        :return: `False`.
        """
        return False

    def can_kiss_eric(self):
        """Return whether the character can kiss Eric. The answer is `True`
        if the character has a :data:`~pyskool.animatorystates.KISSING_ERIC`
        sprite defined.
        """
        return KISSING_ERIC in self.as_dict_L

    def will_kiss_eric(self):
        """Return whether the character will kiss Eric (if he tries)."""
        return self.kisses > 0

    def pause(self):
        """Add a :class:`~ai.Pause` command to the character's command list. This is used
        to temporarily suspend a character's command list while kissing Eric.
        """
        self.paused = True
        self.add_command(ai.Pause())

    def resume(self):
        """Resume the character's command list after being suspended by a
        :class:`~ai.Pause` command (see :meth:`pause`). This is used to
        indicate to the :class:`~ai.Pause` command that it should terminate.
        """
        self.paused = False

    def kiss_eric(self):
        """Make the character kiss Eric."""
        self.previous_as = self.animatory_state
        self.animatory_state = KISSING_ERIC
        self.x += self.direction
        self.direction *= -1
        self.kisses = max(self.kisses - self.cast.kiss_decrement, 0)

    def is_kissing_eric(self):
        """Return whether the character is kissing Eric."""
        return self.animatory_state == KISSING_ERIC

    def finish_kiss(self):
        """Restore the character's animatory state after kissing Eric."""
        self.animatory_state = self.previous_as
        self.direction *= -1

    def is_teaching_eric(self):
        """Return whether the character is teaching Eric this period."""
        return self.skool.is_teaching_eric(self)

    def is_eric_expelled(self):
        """Return whether Eric is due to be or is in the process of being
        expelled.
        """
        return self.cast.is_eric_expelled()

    def get_location_of_eric(self):
        """Return the on-floor location closest to Eric."""
        return self.cast.get_location_of_eric()

    def is_facing_eric(self):
        """Return whether the character is facing Eric."""
        return self.is_facing(self.cast.eric)

    def is_beside_eric(self):
        """Return whether the character is beside Eric."""
        return self.cast.is_beside_eric(self)

    def is_eric_absent(self):
        """Return whether Eric is absent from a classroom or other region he
        should be present in right now.
        """
        return self.cast.is_eric_absent()

    def freeze_eric(self):
        """Freeze Eric (as when he is being spoken to by a little boy, or by
        Mr Wacker for having exceeded the lines limit).
        """
        return self.cast.freeze_eric()

    def unfreeze_eric(self):
        """Unfreeze Eric (see :meth:`freeze_eric`)."""
        self.cast.unfreeze_eric()

    def get_tell_eric_delay(self):
        """Return the time to wait for Eric to respond before repeating a
        message.
        """
        return self.cast.tell_eric_delay

    def eric_understood(self):
        """Return whether Eric has acknowledged understanding of a message
        delivered to him.
        """
        return self.cast.eric_understood()

    def is_touching_eric(self):
        """Return whether the character is in the same location as Eric."""
        return self.cast.is_touching_eric(self)

    def add_lines(self, lines):
        """Add lines to Eric's total.

        :param lines: The number of lines to add.
        """
        self.skool.add_lines(lines)

    def should_stop_eric(self, escape_x, danger_zone):
        """Return whether this character should try to prevent Eric from
        escaping.

        :param escape_x: The x-coordinate beyond which Eric should be regarded
                         as trying to escape.
        :param danger_zone: The minimum and maximum distance to the left of the
                            watcher that Eric must be for him to raise the
                            alarm.
        """
        eric_x, eric_y = self.cast.get_location_of_eric()
        if eric_y != self.y or self.direction > 0:
            return False
        return eric_x >= escape_x and self.x - danger_zone[1] <= eric_x <= self.x - danger_zone[0]

    def raise_alarm(self, message, alertee_id, command_list_id):
        """Make this character raise the alarm that Eric is escaping.

        :param message: The alarm message.
        :param alertee_id: The ID of the character to alert.
        :param command_list_id: The ID of the command list that the alerted
                                character should switch to.
        """
        self.print_message_box(self.skool.expand_message(message), self.cast.escape_alarm_ink, self.cast.escape_alarm_paper, sound.ALARM)
        if not self.cast.is_eric_expelled():
            self.cast.change_command_list(alertee_id, command_list_id)

    def is_stopping_eric(self, eric):
        """Return whether this character is preventing Eric from escaping."""
        return self.stop_eric and eric.impeded(self.y + 3, self.y) and self.direction != eric.direction and abs(self.x - eric.x) == 2

    def should_chase_eric(self, chase_x):
        """Return whether the character should start chasing Eric away. The
        answer will be `True` if all of the following conditions are met:

        * it is not playtime
        * Eric's x-coordinate is greater than `chase_x`
        * Eric is on the same floor as the character

        :param chase_x: The x-coordinate beyond which Eric must be for the
                        monitor to start chasing Eric.
        """
        if not self.skool.is_playtime():
            eric_x, eric_y = self.cast.get_location_of_eric()
            return eric_x >= chase_x and eric_y == self.y
        return False

    #//////////////////////////////////////////////////////////////////////////
    # Lesson coordination
    #//////////////////////////////////////////////////////////////////////////
    def start_lesson(self):
        """Called by the swot to start a lesson."""
        self.lesson = self.cast.create_lesson(self, self.room)
        self.skool.lesson = self.lesson

    def join_lesson(self, qa_group):
        """Called by the teacher to join the lesson started by the swot.

        :param qa_group: The Q&A group from which to choose questions and
                         answers for the teacher and the swot; if `None`, the
                         Q&A group will be chosen at random from those
                         available each time a question and answer is
                         generated.
        """
        self.lesson = self.skool.lesson
        self.lesson.join(self, self.qa_generator, qa_group)

    def next_swot_action(self):
        """Return the next command to be executed by the swot (which may be
        `None`).
        """
        return self.lesson.next_swot_action()

    def next_teacher_action(self):
        """Return the next command to be executed by the teacher (which may be
        `None`).
        """
        return self.lesson.next_teacher_action()

    def finished_speaking(self):
        """Called by the swot or the teacher when he's finished speaking."""
        self.lesson.finished_speaking()

    def set_home_room(self):
        """Set Eric's home room for the current period. The home room is the
        place Eric should be in by now; if he's not, and he's spotted by a
        teacher, he will be given lines.
        """
        self.skool.set_home_room()

    def unset_home_room(self):
        """Unset Eric's home room for the current period. This is used when
        assembly is finished (so that Eric is not told off for being outside
        the assembly hall after Mr Wacker has finished speaking).
        """
        self.skool.unset_home_room()

    def reset_come_along_index(self):
        """Reset the index of the teacher's `COME_ALONG*` messages for this
        lesson.
        """
        self.come_along_index = 0

    #//////////////////////////////////////////////////////////////////////////
    # Lines
    #//////////////////////////////////////////////////////////////////////////
    def print_lines_message(self, recipient_id, message_id):
        """Make the character give lines to someone. First display the
        recipient's name and the number of lines being given, accompanied by a
        sound effect. Then display the reprimand message, accompanied by
        another sound effect.

        :param recipient_id: The ID of the character receiving the lines.
        :param message_id: The ID of the reprimand message.
        """
        if not self.screen.contains(self):
            return
        recipient = self.cast.get(recipient_id)
        admonition = self.lines_messages.get(message_id)
        if not (recipient and admonition):
            return
        if recipient.is_eric() and recipient.expelled:
            return
        num_lines = 100 * random.randint(*self.cast.lines_range)
        message = self.skool.get_lines_message(num_lines, recipient.name)
        if recipient.is_eric():
            paper = self.cast.lines_paper_eric
            self.skool.add_lines(num_lines)
        else:
            paper = self.cast.lines_paper_other
            if recipient.adds_to_score():
                self.skool.add_to_score(num_lines)
            elif recipient.adds_to_lines_total():
                self.skool.add_lines(num_lines)
        ink = self.cast.lines_ink
        pre_resume = self.print_message_box
        # It is possible for a character to change location between the
        # printing of the first lines bubble and the printing of the second;
        # thus we use prev_coords=True to ensure that the first and second
        # lines bubbles are printed in the same place
        pre_resume_args = (admonition, ink, paper, sound.LINES2, True)
        self.print_message_box(message, ink, paper, sound.LINES1, pre_resume=pre_resume, pre_resume_args=pre_resume_args)

    def print_message_box(self, message, ink, paper, sound_id, prev_coords=False, pre_resume=None, pre_resume_args=None):
        """Print a message box above the character's head.

        :param message: The text to display in the message box.
        :type ink: number
        :param ink: The ink colour of the message box.
        :type paper: number
        :param paper: The paper colour of the message box.
        :param sound_id: The ID of the sound effect to play.
        :param prev_coords: If `True`, print the message box at the same
                            coordinates as the last one; otherwise calculate
                            the coordinates afresh.
        :param pre_resume: A method to execute after the sound effect has
                           finished playing.
        :param pre_resume_args: The arguments for the `pre_resume` method.
        """
        if not (self.message_box_coords and prev_coords):
            self.message_box_coords = self._get_head_coords()
        x, y = self.message_box_coords
        self.screen.print_message_box(x, y, message, ink, paper)
        self.skool.locked = pre_resume is not None
        self.skool.play_sound(sound_id, pre_resume=pre_resume, pre_resume_args=pre_resume_args)

    def give_lines(self, recipient_id, message_id, now=False):
        """Add a lines message to the character's buffer.

        :param recipient_id: The ID of the character receiving the lines.
        :param message_id: The ID of the reprimand message.
        :param now: If `True`, the lines message box will be printed
                    immediately; if `False`, it will be printed on the next
                    pass through the main loop (after the screen has been
                    updated for the character's current animatory state and
                    location).
        """
        self.lines_message = (recipient_id, message_id)
        if now:
            self.give_lines_now()

    def give_lines_now(self):
        """Print the lines message that is in the character's buffer (if there
        is one) immediately.
        """
        if self.lines_message:
            self.print_lines_message(*self.lines_message)
            self.lines_message = None

    def can_give_lines_message(self, message_id):
        """Return whether the character is authorised to utter a given lines
        message.

        :param message_id: The ID of the lines message to check.
        """
        return message_id in self.lines_messages

    def reprimand(self):
        """Make the character give lines to the nearest lines recipient for
        knocking him over.
        """
        recipient = self.cast.get_nearest_lines_recipient(self)
        if recipient:
            self.give_lines(recipient.character_id, lines.NEVER_AGAIN)

    #//////////////////////////////////////////////////////////////////////////
    # Messages
    #//////////////////////////////////////////////////////////////////////////
    def get_title(self):
        """Return the name the swot should use when addressing this character.
        """
        return self.title or self.name

    def get_assembly_message(self):
        """Return a message to deliver during assembly (with verb and noun
        randomly chosen).
        """
        return self.skool.get_assembly_message()

    def get_sit_down_message(self):
        """Return a sit-down message randomly chosen from the character's
        collection.
        """
        if self.sit_down_messages:
            message = random.choice(self.sit_down_messages)
            return self.cast.expand_names(message)

    def get_blackboard_message(self):
        """Return a blackboard message randomly chosen from the character's
        collection.
        """
        if self.blackboard_messages:
            message = random.choice(self.blackboard_messages)
            return self.cast.expand_names(message)

    def get_come_along_message_id(self):
        """Return the ID of the message for Eric's teacher to use next as he
        encourages him to stop playing truant.

        :return: `COME_ALONG1`, `COME_ALONG2`, or `COME_ALONG3`.
        """
        message_id = self.come_along_messages[self.come_along_index]
        self.come_along_index = (self.come_along_index + 1) % len(self.come_along_messages)
        if self.come_along_index == 0 and len(self.come_along_messages) > 2:
            self.come_along_index = 1
        return message_id

    def _lesson_message_condition(self, condition):
        """Return whether a lesson message condition is true.

        :param condition: The condition identifier.
        :return: `True` if the condition is true or the condition identifier
                 is unrecognised; `False` otherwise.
        """
        if condition == self.cast.board_dirty:
            return self.room.blackboard_dirty()
        return True

    def get_lesson_message(self):
        """Return a lesson message randomly chosen from the character's
        collection.
        """
        message = None
        messages = self.lesson_messages[:]
        while messages:
            message, condition = messages.pop(random.randrange(len(messages)))
            if self._lesson_message_condition(condition):
                return self._expand_page_numbers(message)

    def _expand_page_numbers(self, message):
        """Expand any page number macros in a lesson message and return the
        result.
        """
        while True:
            search = re.search('\$\( *[0-9]+, *[0-9]+ *\)', message)
            if not search:
                break
            macro = search.group()
            page_range = eval(macro[1:])
            message = message.replace(macro, str(random.randint(*page_range)), 1)
        return message

    def expand_names(self, message):
        """Return a message with character name macros expanded. A character
        name macro takes the form `$WACKER` (for example), which expands to
        the name of the character whose ID is `WACKER`.

        :param message: The message that may contain unexpanded name macros.
        """
        return self.cast.expand_names(message)

    #//////////////////////////////////////////////////////////////////////////
    # Movement
    #//////////////////////////////////////////////////////////////////////////
    def go_fast(self):
        """Ensure that this character runs continuously."""
        self.speed = 2
        self.fixed_speed = True

    def go_slow(self):
        """Ensure that this character does not run."""
        self.speed = 1
        self.fixed_speed = True

    def trigger_speed_change(self):
        """Make it so that the character will consider a change of walking
        speed the next time he is moved.
        """
        self.fixed_speed = False
        self.speed_change_delay = 1

    def reset_walk_delay(self):
        """Reset the delay before the character is moved again (if he is
        walking).
        """
        self.walk_delay = self.fast_delay if self.speed == 2 else self.slow_delay

    def is_time_to_move(self):
        """Return whether the character should be moved on this pass."""
        if self.bubble:
            self.action_delay = (self.action_delay + 1) % self.fast_delay
            return self.action_delay == 0
        if self.action in (1, 2):
            # Writing or not moving
            self.action_delay = (self.action_delay + 1) % self.slow_delay
            return self.action_delay == 0
        if self.action == 3:
            # Perform hitting, firing etc. quickly
            self.action_delay = (self.action_delay + 1) % self.faster_delay
            return self.action_delay == 0
        self.walk_delay -= 1
        if self.walk_delay > 0:
            return False
        self.speed_change_delay -= 1
        if self.speed_change_delay == 0:
            self.speed_change_delay = random.randint(*self.speed_change_delay_range)
            if not self.fixed_speed:
                if self.always_runs:
                    self.speed = 2
                elif self.sometimes_runs():
                    self.speed = random.randint(1, 2)
                else:
                    self.speed = 1
        self.reset_walk_delay()
        return True

    def move(self):
        """Move the character. The steps taken are:

        1. make the character give lines (if he has a lines message buffered)
        2. check whether it's time to move the character, and abort if not
        3. move the character from the midstride position (if he is
           midstride), or
        4. hand control of the character over to the current command in his
           command list
        """
        self.give_lines_now()
        if not self.is_time_to_move():
            return
        if self.midstride():
            return self.walk()
        self.staircase = self.skool.staircase(self)
        self.barrier = self.skool.barrier(self)
        self.room = self.skool.room(self)
        self.floor = self.get_floor()
        self.command_list.command()

    def left(self):
        """Move the character leftwards."""
        if self.direction > 0:
            self.turn()
            return
        if self.barrier and self.barrier.x <= self.x:
            if self.barrier.is_door() and self.can_open_door(self.barrier):
                return self.open_door()
            return ai.GoToXY(self.x + 1, self.y)
        on_stairs = False
        if self.staircase:
            if self.staircase.direction < 0:
                on_stairs = self.x != self.staircase.bottom.x or self.staircase.force
            else:
                on_stairs = self.x != self.staircase.top.x or self.staircase.force
        self.walk(on_stairs)

    def right(self):
        """Move the character rightwards."""
        if self.direction < 0:
            self.turn()
            return
        if self.barrier and self.x < self.barrier.x:
            if self.barrier.is_door() and self.can_open_door(self.barrier):
                return self.open_door()
            return ai.GoToXY(self.x - 1, self.y)
        on_stairs = False
        if self.staircase:
            if self.staircase.direction > 0:
                on_stairs = self.x != self.staircase.bottom.x or self.staircase.force
            else:
                on_stairs = self.x != self.staircase.top.x or self.staircase.force
        self.walk(on_stairs)

    def up(self):
        """Move the character upwards."""
        if self.staircase:
            if self.direction == self.staircase.direction or (self.x == self.staircase.top.x and self.staircase.force):
                return self.walk(True)
            elif self.x != self.staircase.top.x:
                return self.turn()
        if self.direction > 0:
            self.right()
        else:
            self.left()

    def down(self):
        """Move the character downwards."""
        if self.staircase:
            if self.direction != self.staircase.direction or (self.x == self.staircase.bottom.x and self.staircase.force):
                return self.walk(True)
            elif self.x != self.staircase.bottom.x:
                return self.turn()
        if self.direction > 0:
            self.right()
        else:
            self.left()

    def get_walk_state_index(self):
        """Return the index of the character's current animatory state in his
        collection of walking sprites.

        :return: 0, 1, 2, or 3 (or -1 if the character is not standing or
                 walking).
        """
        if self.animatory_state in self.walk_states:
            return self.walk_states.index(self.animatory_state)
        return -1

    def walk(self, on_stairs=False):
        """Make a character take one step in the direction he's facing. The
        character's y-coordinate will be adjusted appropriately if he's going
        up or down a staircase.

        :param on_stairs: `True` if the character is on a staircase, `False`
                          otherwise.
        """
        if on_stairs:
            if self.direction == self.staircase.direction:
                if not self.midstride():
                    self.y -= 1
            else:
                self.vertical_direction = 1
        walk_state = (self.get_walk_state_index() + 1) % len(self.walk_states)
        if walk_state % 2 == 0:
            self.x += self.direction
            self.y += self.vertical_direction
            if self.wiping_board:
                # Animatory state sequence is 0, 1, 0, 1... when wiping board
                walk_state = 0
            self.vertical_direction = 0
        self.animatory_state = self.walk_states[walk_state]
        self.action = 0

    def sit(self):
        """Make the character sit in a chair or on the floor (if he is standing
        up), or stand up (if he is sitting or lying down).
        """
        if self.is_sitting():
            self.get_up()
            return True
        self.previous_as = self.animatory_state
        chair = self.chair()
        if chair:
            self.animatory_state = SITTING_ON_CHAIR
            occupant = chair.occupant
            chair.seat(self)
            if occupant:
                occupant.dethrone()
        else:
            staircase = self.skool.staircase(self)
            if staircase and staircase.supports(self):
                if self.can_sit_on_stairs() and self.direction * staircase.direction < 0:
                    self.animatory_state = SITTING_ON_CHAIR
            else:
                self.sit_on_floor()
        self.action = 1
        return self.animatory_state != self.previous_as

    #//////////////////////////////////////////////////////////////////////////
    # Skool clock
    #//////////////////////////////////////////////////////////////////////////
    def is_time_to_start_lesson(self):
        """Return whether enough time has passed to start the lesson. This is
        used, for example, to check whether a teacher should tell the kids to
        sit down, or continue pacing up and down outside the classroom doorway.
        """
        return self.skool.is_time_to_start_lesson()

    def stop_clock(self):
        """Stop the skool clock. This is used to prevent the bell from ringing
        before a certain event happens. (See :meth:`start_clock`.)
        """
        self.skool.stop_clock()

    def start_clock(self, ticks):
        """Restart the skool clock at a given time. (See :meth:`stop_clock`.)

        :param ticks: The number of ticks until the end of the period.
        """
        self.skool.start_clock(ticks)

    #//////////////////////////////////////////////////////////////////////////
    # Signals
    #//////////////////////////////////////////////////////////////////////////
    def signal(self, signal):
        """Raise a signal.

        :type signal: string
        :param signal: The signal to raise.
        """
        self.skool.signal(signal)

    def unsignal(self, signal):
        """Lower a signal.

        :type signal: string
        :param signal: The signal to lower.
        """
        self.skool.unsignal(signal)

    def got_signal(self, signal):
        """Return whether a signal has been raised.

        :param signal: The signal to check.
        """
        return self.skool.got_signal(signal)
