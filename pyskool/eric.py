# -*- coding: utf-8 -*-
# Copyright 2008-2015 Richard Dymond (rjdymond@gmail.com)
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
Defines the :class:`Eric` class.
"""

import random

from . import character
from .animatorystates import ARM_UP, BENDING_OVER, RIDING_BIKE0, RIDING_BIKE1, WALK0
from . import ai
from . import lines
from . import items
from . import keys
from . import sound

class Eric(character.Character):
    """This class represents our hero.

    :param character_id: Unique ID.
    :type config: dict
    :param config: Configuration parameters from the ini file.
    :param name: Display name.
    :param head_xy: The coordinates of Eric's head within his sprite when he's
                    standing upright (used for collision detection).
    :param flags: Character flags.
    :param bend_over_hand_xy: The coordinates of Eric's hand within his
                              left-facing `BENDING_OVER` sprite (used to
                              determine where a mouse or frog should be when
                              caught or released).
    """
    def __init__(self, character_id, config, name, head_xy, flags, bend_over_hand_xy):
        character.Character.__init__(self, character_id, name, head_xy, flags)
        self.keyboard = None
        self.bike_combo_score = config.get('BikeCombinationScore', 1000)
        self.storeroom_combo_score = config.get('StoreroomCombinationScore', 1000)
        self.safe_key_score = config.get('SafeKeyScore', 2000)
        self.storeroom_door = config.get('StoreroomDoorId', 'ScienceLabDoor')
        self.min_lines_delay = config.get('MinimumLinesDelay', 60)
        self.assembly_hall = config.get('AssemblyHallId', 'AssemblyHall')
        self.assembly_sit_direction = config.get('AssemblySitDirection', 1)
        self.kiss_lines = config.get('KissLines', 1000)
        self.mouse_catch_score = config.get('MouseCatchScore', 100)
        self.max_mice_release = config.get('MaxMiceRelease', 5)
        self.default_walk_delay = config.get('EricWalkDelay', 2)
        self.jump_delay = config.get('JumpDelay', 4)
        self.bend_over_delay = config.get('BendOverDelay', 4)
        self.bend_over_hand_xy = bend_over_hand_xy
        self._reinitialise()

    def move(self):
        """Move Eric. This entails checking the keyboard for relevant
        keypresses and moving Eric accordingly, and dealing with Eric if he's
        currently engaged in an action such as firing the catapult or water
        pistol (during which keypresses are ignored).

        :return: -1 if the screen should scroll right, 1 if it should scroll
                 left, or 0 if it should not scroll (after moving Eric).
        """
        self.get_lines()
        self.walk_delay -= 1
        if self.walk_delay > 0:
            return 0
        self.walk_delay = self.default_walk_delay
        self.barrier = self.skool.barrier(self) or self.cast.get_eric_stopper()
        self.floor = self.get_floor()
        self.keyboard.pump()
        if self.controller:
            next_controller = self.controller.execute()
            if next_controller is self.controller:
                self._set_controller(None)
            elif next_controller is not None:
                self._set_controller(next_controller)
            return self.screen.get_scroll_increment(self.x)
        if self.midstride():
            self.make_walking_sound(self.get_walk_state_index())
            return self.walk()
        if self.is_knocked_out() or self.is_sitting():
            if self.keyboard.was_pressed(keys.SIT_STAND):
                if self.is_sitting_on_chair():
                    self.chair().vacate()
                self.animatory_state = WALK0
                self.make_sitting_sound()
            elif self.is_sitting_on_chair() and self.keyboard.was_pressed(keys.OPEN_DESK):
                self.open_desk(self.skool.desk(self))
            return 0
        if self.keyboard.was_pressed(keys.SIT_STAND) and self.sit():
            self.make_sitting_sound()
            return 0
        if self.keyboard.was_pressed(keys.FIRE_CATAPULT) and self.can_fire_catapult():
            self._set_controller(ai.FireCatapult())
            return 0
        if self.keyboard.was_pressed(keys.FIRE_WATER_PISTOL) and self.can_fire_water_pistol():
            self._set_controller(ai.FireWaterPistol())
            return 0
        if self.keyboard.was_pressed(keys.DUMP_WATER_PISTOL) and self.can_dump_water_pistol():
            self.bend_over()
            self._set_controller(ai.DumpWaterPistol())
            return 0
        if self.keyboard.was_pressed(keys.DROP_STINKBOMB) and self.can_drop_stinkbomb():
            self._set_controller(ai.DropStinkbomb())
            return 0
        if self.keyboard.was_pressed(keys.HIT):
            self._set_controller(ai.Hit())
            return 0
        if self.keyboard.was_pressed(keys.JUMP):
            self._set_controller(ai.Jump())
            return 0
        if self.keyboard.was_pressed(keys.WRITE) and self.skool.beside_blackboard(self):
            self.raise_arm()
            self._set_controller(ai.Write())
            self.keyboard.start_writing()
            self.writing = True
            return 0
        if self.keyboard.was_pressed(keys.CATCH) and self.can_bend_over():
            self.bend_over()
            self._set_controller(ai.Catch())
            return 0
        if self.keyboard.was_pressed(keys.MOUNT_BIKE) and self.can_mount_bike():
            self.bike = self.cast.bike
            self.mount_bike()
            self._set_controller(ai.RideBike(self.bike))
            return 0
        if self.keyboard.was_pressed(keys.KISS) and self.can_kiss():
            self.previous_as = self.animatory_state
            self._set_controller(ai.Kiss())
            return 0
        if self.keyboard.was_pressed(keys.RELEASE_MICE) and self.can_release_mice():
            self.bend_over()
            self._set_controller(ai.ReleaseMice())
            return 0
        self.staircase = self.skool.staircase(self)
        if not self.is_supported():
            self.y += 1
            return 0
        self.base_location = None
        old_ws, old_as, old_direction = self.get_walk_state_index(), self.animatory_state, self.direction
        plant = self.cast.plant(self)
        if self.keyboard.pressed(keys.LEFT):
            if plant and plant.is_fully_grown():
                barrier = self.skool.barrier(self, 1)
                if barrier and barrier.is_shut() and barrier.climb_phases:
                    self._set_controller(ai.Flight(barrier.climb_phases))
                    return 0
            self.left()
        elif self.keyboard.pressed(keys.RIGHT):
            if plant and plant.is_fully_grown():
                window = self.skool.window(self)
                if window:
                    if not window.is_shut():
                        self._set_controller(ai.Flight(window.climb_phases, window.not_a_bird))
                    return 0
                elif self.barrier and self.barrier.is_shut() and self.barrier.climb_phases:
                    self._set_controller(ai.Flight(self.barrier.climb_phases))
                    return 0
            self.right()
        elif self.keyboard.pressed(keys.UP):
            self.up()
        elif self.keyboard.pressed(keys.DOWN):
            self.down()
        if (self.animatory_state, self.direction) != (old_as, old_direction):
            self.make_walking_sound(old_ws)
        return 0

    def _set_controller(self, command):
        """Set Eric's controlling command.

        :param command: The command.
        """
        if command:
            command.character = self
        self.controller = command

    def can_fire_catapult(self):
        """Return whether Eric can fire a catapult. This will be `True` if and
        only if :meth:`~pyskool.character.Character.can_fire_catapult` (on
        :class:`~pyskool.character.Character`) returns `True` and the conker is
        not falling from the tree.
        """
        return character.Character.can_fire_catapult(self) and not self.cast.conker_falling()

    def can_sit_on_stairs(self):
        """Return whether Eric can sit on the stairs. This will be `True` if
        and only if the relevant lines message is defined.
        """
        return self.cast.can_get_lines(lines.NO_SITTING_ON_STAIRS)

    def is_supported(self):
        """Return whether Eric is standing on something that prevents him from
        falling. The things that can prevent Eric from falling are:

        * a floor
        * a staircase
        * a knocked out kid
        * a plant pot
        * a plant
        """
        return (self.staircase
            or self.cast.is_standing_on_kid(self)
            or self.skool.on_floor(self)
            or self.skool.plant_pot(self.x, self.y)
            or self.cast.plant(self))

    def can_open_door(self, door):
        """Return whether Eric can open a specific door. This will be `False`
        unless the door in question is the storeroom door and Eric has the key
        to it.

        :param door: The door to check.
        """
        if door.barrier_id == self.storeroom_door and items.STOREROOM_KEY in self.inventory:
            return True
        return character.Character.can_open_door(self, door)

    def open_door(self):
        """Open the door that Eric is facing.

        :return: 0 (to indicate that the screen should not scroll).
        """
        self.skool.move_door(self.barrier.barrier_id, False)
        return 0

    def get_lines(self):
        """Check whether Eric is up to anything that merits being given lines,
        and make any nearby teacher who can see him give the lines.
        """
        self.lines_delay = max(0, self.lines_delay - 1)
        if self.lines_delay > self.min_lines_delay / 2:
            return
        if self.lines_delay == 0:
            self.last_lines_giver = None
        room = self.skool.room(self)
        home_room = self.skool.get_home_room()
        if self.base_location:
            # Use Eric's pre-jump coordinates for comparison if he's jumping
            x, y = self.base_location
        elif self.bike and not self.sitting_on_saddle:
            # Use the bike's y-coordinate if Eric's standing on the saddle
            x, y = self.x, self.bike.y
        else:
            # Otherwise use Eric's actual location
            x, y, = self.x, self.y
        if self.skool.in_no_go_zone(x, y):
            self.alert_lines_givers(lines.GET_OUT, True)
        elif self.should_get_along():
            self.alert_lines_givers(lines.GET_ALONG, True)
        elif self.is_sitting_on_stairs():
            self.alert_lines_givers(lines.NO_SITTING_ON_STAIRS, True)
        elif self.is_knocked_out():
            self.alert_lines_givers(lines.GET_UP, True)
        elif self.bike and not self.skool.in_playground(self):
            self.alert_lines_givers(lines.NO_BIKES, True)
        elif self.skool.plant_pot(self.x, self.y) or self.cast.plant(self):
            self.alert_lines_givers(lines.GET_OFF_PLANT, True)
        else:
            is_assembly = self.skool.is_assembly()
            if self.is_sitting_on_floor():
                # Eric is sitting on the floor...
                if room and room.room_id == self.assembly_hall:
                    if self.direction != self.assembly_sit_direction:
                        # ...facing left in the assembly hall...
                        if is_assembly:
                            # ...and it's assembly - tell him to sit facing the
                            # stage
                            self.alert_lines_givers(lines.SIT_FACING_STAGE, True)
                        else:
                            # ...and it's not assembly - tell him to get off
                            # the floor
                            self.alert_lines_givers(lines.GET_UP, True)
                else:
                    # ...somewhere other than the assembly hall - tell him to
                    # get off the floor
                    self.alert_lines_givers(lines.GET_UP, True)
            elif self.is_standing() and home_room and home_room.contains(self) and (home_room.chairs or home_room.room_id == self.assembly_hall):
                # Eric is standing up either in a classroom after the lesson
                # has started, or in the assembly hall after assembly has
                # started - tell him to sit down
                self.alert_lines_givers(lines.SIT_DOWN, True)

    def is_absent(self):
        """Return whether Eric is playing truant."""
        return self.skool.get_home_room() not in (None, self.skool.room(self))

    def should_get_along(self):
        """Return whether Eric is somewhere other than he should be."""
        return self.skool.should_get_along(self)

    def walk(self, on_stairs=False):
        """Move Eric one step in the direction he is facing. If Eric moves
        close enough to the left or right edge of the screen, it will scroll.
        """
        character.Character.walk(self, on_stairs)
        if not self.midstride():
            return self.screen.get_scroll_increment(self.x)
        return 0

    def dethrone(self):
        """Push Eric out of his seat and play a suitable sound effect."""
        self.sit_on_floor()
        self.play_sound(sound.KNOCKED_OUT, sound.ASYNC)

    def deck(self):
        """Knock Eric out and play a suitable sound effect."""
        if self.is_sitting_on_chair():
            self.chair().vacate()
        self.knock_over()
        if self.writing:
            self.writing = False
            self.keyboard.finish_writing()
            self._set_controller(None)
        self.play_sound(sound.KNOCKED_OUT, sound.ASYNC)

    def alert_lines_givers(self, message_id, reset_delay=False):
        """Look for a lines-giver in the vicinity of Eric; if one is found,
        make him give lines to Eric.

        :param message_id: The ID of the lines message to scream.
        :param reset_delay: Whether to reset the lines-giving delay.
        """
        nearby_lines_givers = self.cast.get_nearby_lines_givers(self)
        if reset_delay and self.last_lines_giver in nearby_lines_givers:
            nearby_lines_givers.remove(self.last_lines_giver)
        if nearby_lines_givers:
            lines_giver = nearby_lines_givers[0]
            if message_id == lines.GET_ALONG:
                teacher = self.skool.get_teacher()
                if teacher in nearby_lines_givers:
                    lines_giver = teacher
                    message_id = teacher.get_come_along_message_id()
                elif self.skool.in_playground(self):
                    message_id = lines.BACK_TO_SKOOL
            if reset_delay:
                self.lines_delay = self.min_lines_delay
            lines_giver.give_lines(self.character_id, message_id)
            self.last_lines_giver = lines_giver

    def aim_catapult(self):
        """Make Eric aim his catapult (raise it to eye level). Also alert any
        lines-givers in the vicinity, and play a sound effect.
        """
        character.Character.aim_catapult(self)
        self.alert_lines_givers(lines.NO_CATAPULTS)
        self.play_sound(sound.CATAPULT, sound.ASYNC)

    def has_water_pistol(self):
        """Return whether Eric has a water pistol (containing either water or
        sherry).
        """
        return items.WATER_PISTOL in self.inventory or items.SHERRY_PISTOL in self.inventory

    def can_fire_water_pistol(self):
        """Return whether Eric can fire a water pistol. This will be `True` if
        Character.can_fire_water_pistol returns `True` and Eric actually has
        the water pistol.
        """
        if self.has_water_pistol():
            return character.Character.can_fire_water_pistol(self)

    def can_dump_water_pistol(self):
        """Return whether Eric can throw away the water pistol. This will be
        `True` if Eric has the water pistol and has a
        :data:`~pyskool.animatorystates.BENDING_OVER` sprite defined.
        """
        return self.has_water_pistol() and self.can_bend_over()

    def dump_water_pistol(self):
        """Make Eric throw away the water pistol. The water pistol will be
        filled with water and placed in a desk chosen at random.
        """
        pistol = None
        if items.WATER_PISTOL in self.inventory:
            pistol = items.WATER_PISTOL
        elif items.SHERRY_PISTOL in self.inventory:
            pistol = items.SHERRY_PISTOL
        if pistol:
            self.inventory.remove(pistol)
            self.print_inventory()
            self.skool.hide_in_desk(items.WATER_PISTOL)
        self.walk_delay = self.bend_over_delay

    def fire_water_pistol(self):
        """Make Eric fire the water pistol. Also alert any lines-givers in the
        vicinity, and play a sound effect.
        """
        liquid = self.cast.sherry_id if items.SHERRY_PISTOL in self.inventory else self.cast.water_id
        character.Character.fire_water_pistol(self, liquid)
        self.alert_lines_givers(lines.NO_WATERPISTOLS)
        self.play_sound(sound.WATER_PISTOL, sound.ASYNC)

    def can_drop_stinkbomb(self):
        """Return whether Eric can drop a stinkbomb. This will be `True` if
        :meth:`~pyskool.character.Character.can_drop_stinkbomb` (on
        :class:`~pyskool.character.Character`) returns `True` and Eric has a
        stinkbomb and is standing on a floor (as opposed to a staircase).
        """
        return self.floor and self.has_stinkbomb() and character.Character.can_drop_stinkbomb(self)

    def has_stinkbomb(self):
        """Return whether Eric has at least one stinkbomb."""
        return any([i in self.inventory for i in (items.STINKBOMBS1, items.STINKBOMBS2, items.STINKBOMBS3)])

    def drop_stinkbomb(self):
        """Make Eric drop a stinkbomb. Also alert any lines-givers in the
        vicinity.
        """
        character.Character.drop_stinkbomb(self)
        if items.STINKBOMBS3 in self.inventory:
            self.inventory.remove(items.STINKBOMBS3)
            self.inventory.add(items.STINKBOMBS2)
        elif items.STINKBOMBS2 in self.inventory:
            self.inventory.remove(items.STINKBOMBS2)
            self.inventory.add(items.STINKBOMBS1)
        elif items.STINKBOMBS1 in self.inventory:
            self.inventory.remove(items.STINKBOMBS1)
        self.print_inventory()
        self.alert_lines_givers(lines.NO_STINKBOMBS)

    def open_desk(self, desk):
        """Make Eric raise a desk lid.

        :param desk: The desk to open.
        """
        if desk:
            self.cast.open_desk(self, desk)

    def collect_desk_contents(self, desk):
        """Place the contents (if any) of a desk in Eric's inventory. Also play
        a sound effect if the desk is not empty."""
        if desk.contents:
            if desk.contents == items.STINKBOMBS3:
                for item in (items.STINKBOMBS2, items.STINKBOMBS1):
                    if item in self.inventory:
                        self.inventory.remove(item)
            self.inventory.add(desk.contents)
            if desk.contents == items.WATER_PISTOL:
                desk.empty()
            self.play_sound(sound.DESK)
            self.print_inventory()

    def punch(self):
        """Make Eric throw a punch. Also alert any lines-givers in the
        vicinity.
        """
        character.Character.punch(self)
        self.alert_lines_givers(lines.NO_HITTING)
        self.play_sound(random.choice(sound.HIT_SOUNDS))

    def jump(self):
        """Make Eric jump. Also alert any lines-givers in the vicinity."""
        if not self.base_location:
            self.base_location = (self.x, self.y)
        self.previous_as = self.animatory_state
        self.y -= 1
        self.walk_delay = self.jump_delay
        self.animatory_state = ARM_UP
        self.alert_lines_givers(lines.NO_JUMPING)

    def descend(self):
        """Make Eric finish a jump. If Eric jumped up to the safe, or a shield,
        or an open drinks cabinet while carrying a water pistol, appropriate
        action is taken. Eric will descend to the floor unless the jump placed
        him on a knocked out kid or a plant pot.
        """
        self.play_sound(sound.JUMP)
        x, y = self.get_location_above_hand()
        self.skool.check_safe(x, y, items.SAFE_KEY in self.inventory)
        self.check_shields_at(x, y)
        if self.skool.check_drinks_cabinet(x, y) and items.WATER_PISTOL in self.inventory:
            self.inventory.remove(items.WATER_PISTOL)
            self.inventory.add(items.SHERRY_PISTOL)
            self.print_inventory()
            self.play_sound(sound.SHERRY)
        if not self.cast.is_standing_on_kid(self) and not self.skool.plant_pot(self.x, self.y):
            self.y += 1
            self.base_location = None
        self.animatory_state = self.previous_as

    def can_bend_over(self):
        """Return whether Eric can bend over. This will be `True` if and only
        if he has a :data:`~pyskool.animatorystates.BENDING_OVER` sprite
        defined.
        """
        return BENDING_OVER in self.as_dict_L

    def bend_over(self):
        """Make Eric bend over (as when catching or releasing mice)."""
        self.previous_as = self.animatory_state
        self.walk_delay = 1
        self.animatory_state = BENDING_OVER

    def _get_bend_over_hand_coords(self):
        """Return the coordinates of Eric's hand when he's bending over."""
        if not self.bend_over_hand_xy:
            return
        hand_x = self.x + (self.bend_over_hand_xy[0] if self.direction < 0 else self.width - self.bend_over_hand_xy[0] - 1)
        hand_y = self.y + self.bend_over_hand_xy[1]
        return hand_x, hand_y

    def catch_animal(self):
        """Make Eric catch any animal that is close at hand. If Eric catches
        something, a sound effect is played.
        """
        animal = self.cast.get_animal(*self._get_bend_over_hand_coords())
        if animal:
            if animal.is_mouse():
                self.skool.add_to_score(self.mouse_catch_score)
                self.play_sound(sound.MOUSE)
                self.mice += 1
                self.print_mouse_inventory()
                self.cast.caught_mouse(animal)
            elif animal.is_frog():
                animal.hide()
                self.play_sound(sound.FROG)
                self.inventory.add(items.FROG)
                self.print_inventory()
        self.walk_delay = self.bend_over_delay

    def print_mouse_inventory(self):
        """Print Eric's mouse inventory."""
        self.screen.print_mice(self.mice, self.skool.get_mouse_image())

    def can_release_mice(self):
        """Return whether Eric can release mice at the moment. This will be
        `True` if Eric is standing on a floor (as opposed to a staircase), has
        at least one mouse, and can bend over.
        """
        return self.floor and self.mice > 0 and self.can_bend_over()

    def release_mice(self):
        """Make Eric release some mice."""
        if self.mice > 0:
            num_mice = min(self.mice, self.max_mice_release)
            self.mice -= num_mice
            self.print_mouse_inventory()
            self.cast.release_mice(num_mice, *self._get_bend_over_hand_coords())
        self.walk_delay = self.bend_over_delay

    def print_inventory(self):
        """Print Eric's inventory."""
        self.screen.print_inventory(self.skool.get_inventory_images(self.inventory))

    def stand_up(self):
        """Make Eric stand up (after sitting down or bending over)."""
        self.animatory_state = self.previous_as
        self.walk_delay = 1

    def get_location(self):
        """Return the on-floor location that is closest to Eric."""
        x, y = self.x, self.y
        if self.hide_coords:
            # If Eric is hiding (e.g. while kissing), temporarily restore his
            # pre-hide coordinates for the location check
            self.x, self.y = self.hide_coords
        elif self.base_location:
            # If Eric is jumping, temporarily restore his pre-jump coordinates
            # for the location check
            self.x, self.y = self.base_location
        location = character.Character.get_location(self)
        self.x, self.y = x, y
        return location

    def get_location_above_hand(self):
        """Return the location above Eric's hand. This location will be used to
        check for the presence of a shield, the safe, or a cup.
        """
        return (self.x + self.direction + 1, self.y)

    def write(self):
        """Control Eric when he's writing on a blackboard.

        :return: `True` if Eric has finished writing, `False` otherwise.
        """
        blackboard = self.skool.room(self).blackboard
        if self.has_arm_raised():
            self.lower_arm()
            self.writing = self.keyboard.writing
            if self.writing:
                self.alert_lines_givers(lines.NO_WRITING)
            else:
                self.check_combinations(blackboard)
            return not self.writing
        key_down_events = self.keyboard.key_down_events
        if key_down_events:
            first_event = key_down_events[0]
            if first_event.key in keys.ENTER:
                self.raise_arm()
                self.keyboard.finish_writing()
                return
            char = first_event.unicode
            if self.screen.has_font_char(char):
                self.raise_arm()
                self.skool.write_on_board(self, blackboard, char)
        else:
             # Maximise responsiveness
            self.walk_delay = 1

    def check_combinations(self, blackboard):
        """Check whether the bike or storeroom combination has been written on
        any of the blackboards. If the bike combination has been written on a
        blackboard, unchain the bike and play a sound effect. If the storeroom
        combination has been written on a blackboard, give Eric the key to that
        room and play a sound effect.
        """
        if not self.cast.is_bike_visible() and self.skool.got_bike_combination(blackboard):
            self.skool.add_to_score(self.bike_combo_score)
            self.skool.unchain_bike()
            self.play_sound(sound.BIKE)
        elif items.STOREROOM_KEY not in self.inventory and self.skool.got_storeroom_combination(blackboard):
            self.skool.add_to_score(self.storeroom_combo_score)
            self.inventory.add(items.STOREROOM_KEY)
            self.print_inventory()
            self.play_sound(sound.STOREROOM_KEY)

    def is_eric(self):
        """Return whether this character is Eric.

        :return: `True`.
        """
        return True

    def freeze(self):
        """Attempt to freeze Eric. The attempt will fail if Eric is writing on
        a blackboard, or is already frozen.

        :return: `True` if Eric was frozen, `False` otherwise.
        """
        if self.writing or self.frozen:
            return False
        self._set_controller(ai.Freeze())
        self.frozen = True
        return True

    def unfreeze(self):
        """Unfreeze Eric."""
        if self.frozen:
            self._set_controller(None)
            self.frozen = False
            self.understood = False

    def check_understanding(self):
        """Check whether Eric indicated understanding of the message just
        delivered to him.
        """
        if self.keyboard.was_pressed(keys.UNDERSTOOD):
            self.understood = True

    def understood_message(self):
        """Return whether Eric understood the message just delivered to him."""
        return self.understood

    def paralyse(self, command_list_id):
        """Signal that Eric is paralysed (as after falling from the top-floor
        window). Mr Wacker will be alerted.

        :param command_list_id: The ID of the command list Mr Wacker should
                                switch to.
        """
        self.expelled = True
        self.skool.expel_eric(command_list_id)

    def take_safe_key(self):
        """Make Eric collect the safe key. A celebratory sound effect will be
        played.
        """
        if items.SAFE_KEY not in self.inventory:
            self.skool.add_to_score(self.safe_key_score)
            self.play_sound(sound.SAFE_KEY, sound.SUSPEND)
            self.inventory.add(items.SAFE_KEY)
            self.print_inventory()

    def can_kiss(self):
        """Return whether anyone in the cast can kiss Eric."""
        return self.cast.has_kissees()

    def kissee(self):
        """Return the first kissable candidate in front of Eric, or `None` if
        there is none.
        """
        return self.cast.kissee()

    def kiss(self):
        """Decrease Eric's lines total and play the kissing sound effect."""
        self.skool.add_lines(-self.kiss_lines)
        self.play_sound(sound.KISS)

    def hide(self):
        """Hide Eric. This is used when Eric is kissing someone, and two
        sprites become one.
        """
        self.hide_coords = (self.x, self.y)
        character.Character.hide(self)

    def unhide(self):
        """Unhide Eric. Eric's pre-kiss coordinates are restored."""
        if self.hide_coords:
            self.x, self.y = self.hide_coords
            self.hide_coords = None

    def fall_to_floor(self):
        """Make Eric land on the floor in the sitting position, and play a
        sound effect.
        """
        self.sit_on_floor()
        self.play_sound(sound.KNOCKED_OUT, sound.ASYNC)

    def fall_off_plant(self):
        """Make Eric fall off a plant that has just died."""
        self._set_controller(ai.FallToFloor())

    def fly(self, x_inc, y_inc):
        """Move Eric to the next spot in his flight out of a window or over the
        skool gate.

        :param x_inc: The x-coordinate increment.
        :param y_inc: The y-coordinate increment.
        """
        self.x += x_inc * self.direction
        self.y += y_inc
        self.make_walking_sound(self.x % 4)

    def end_flight(self):
        """Play a sound effect if Eric did not land on his feet after flying
        out of a window or over the skool gate.
        """
        if not self.is_standing():
            self.play_sound(sound.KNOCKED_OUT, sound.ASYNC)

    #//////////////////////////////////////////////////////////////////////////
    # Initialisation
    #//////////////////////////////////////////////////////////////////////////
    def reinitialise(self):
        """Perform generic reinitialisation of Eric."""
        character.Character.reinitialise(self)
        self._reinitialise()

    def _reinitialise(self):
        """Perform specific reinitialisation of Eric."""
        self.writing = False
        self.frozen = False
        self.understood = False
        self._set_controller(None)
        self.lines_delay = self.min_lines_delay
        self.last_lines_giver = None
        self.inventory = set()
        self.mice = 0
        self.last_bike_key = None
        self.bike_key = None
        self.bike = None
        self.started_pedalling = False
        self.sitting_on_saddle = False
        self.expelled = False
        self.hide_coords = None
        self.base_location = None

    #//////////////////////////////////////////////////////////////////////////
    # Bike
    #//////////////////////////////////////////////////////////////////////////
    def can_mount_bike(self):
        """Return whether Eric can mount the bike at the moment. This will be
        `True` if Eric has the :data:`~pyskool.animatorystates.RIDING_BIKE0`
        sprite defined and is standing next to the bike.
        """
        return RIDING_BIKE0 in self.as_dict_L and self.cast.is_beside_bike(self)

    def mount_bike(self):
        """Make Eric mount the bike."""
        self.last_bike_key = None
        self.started_pedalling = False
        self.sitting_on_saddle = True
        self.previous_as = self.animatory_state
        self.animatory_state = RIDING_BIKE0

    def check_bike_keys(self):
        """Check whether any key related to bike movement has been pressed. Any
        bike key pressed is stored and acted upon later by another bike-related
        method.
        """
        self.bike_key = None
        for key in keys.LEFT + keys.RIGHT + keys.UP + keys.DOWN + keys.JUMP:
            if self.keyboard.was_pressed([key]):
                self.bike_key = key
                break

    def hit_barrier(self, bike):
        """Return the wall, door or Eric-stopping character that Eric rode the
        bike into (if any).

        :param bike: The bike Eric is riding.
        :return: The barrier that was hit, or `None` if none was hit.
        """
        if bike.is_visible():
            return bike.hit_barrier() or self.cast.get_eric_stopper()
        # Check from a distance of 1 if travelling leftwards so that the bike
        # does not appear too close to the barrier if it hits it
        distance = 0 if self.direction > 0 else 1
        return self.skool.barrier(self, distance) or self.cast.get_eric_stopper()

    def pedalled(self):
        """Return whether Eric pedalled the bike since the last time he was
        moved. This will be `True` if and only if:

        * he is sitting on the saddle, and
        * 'left' or 'right' was pressed, and
        * the bike key pressed on the last call is different from the one
          pressed on this call
        """
        if self.sitting_on_saddle:
            pedalled = self.bike_key in keys.LEFT + keys.RIGHT and self.bike_key != self.last_bike_key
            if pedalled:
                self.started_pedalling = True
                self.pedal()
                self.last_bike_key = self.bike_key
            if self.started_pedalling:
                self.move_bike()
            return pedalled
        return False

    def pedal(self):
        """Make Eric pedal the bike. The Eric-on-a-bike sprite is moved to the
        next phase of animation.
        """
        if self.animatory_state == RIDING_BIKE0:
            self.animatory_state = RIDING_BIKE1
        else:
            self.animatory_state = RIDING_BIKE0

    def move_bike(self):
        """Move the bike (while Eric's on it)."""
        self.x += self.direction

    def dismounted(self):
        """Return whether Eric dismounted from the bike. This will be `True`
        if Eric was sitting on the saddle and 'down' was pressed.
        """
        return self.sitting_on_saddle and self.bike_key in keys.DOWN

    def dismount(self):
        """Make Eric dismount from the bike."""
        self.bike = None

    def stood_on_saddle(self):
        """Return whether Eric stood on the saddle of the bike. This will be
        `True` if Eric was sitting on the saddle and 'up' was pressed.
        """
        if self.sitting_on_saddle and self.bike_key in keys.UP:
            self.last_bike_key = self.bike_key
            self.sitting_on_saddle = False
        return not self.sitting_on_saddle

    def stand_on_saddle(self):
        """Make Eric stand on the saddle of the bike."""
        self.animatory_state = WALK0
        self.x -= self.direction
        self.y -= 1

    def got_back_on_saddle(self):
        """Return whether Eric got back on the saddle of the bike. This will be
        `True` if Eric was standing on the saddle and 'down' was pressed.
        """
        if not self.sitting_on_saddle and self.bike_key in keys.DOWN:
            self.last_bike_key = self.bike_key
            self.sitting_on_saddle = True
        return self.sitting_on_saddle

    def get_back_on_saddle(self):
        """Make Eric get back on the saddle of the bike."""
        self.animatory_state = RIDING_BIKE0
        self.x += self.direction
        self.y += 1

    def jumped_off_saddle(self):
        """Return whether Eric jumped off the saddle of the bike. This will be
        `True` if Eric was standing on the saddle and 'up' or 'jump' was
        pressed.
        """
        if not self.sitting_on_saddle and self.bike_key in keys.JUMP + keys.UP:
            self.base_location = (self.x, self.bike.y)
            return True
        return False

    def check_cup(self):
        """Check whether Eric managed to reach a cup while in possession of the
        frog. If so, the frog is placed in the cup and a sound effect is
        played.
        """
        if items.FROG in self.inventory:
            cup = self.skool.cup(*self.get_location_above_hand())
            if cup:
                self.cast.insert_frog(cup)
                self.inventory.remove(items.FROG)
                self.print_inventory()
                self.play_sound(sound.FROG)

    def landed(self):
        """Return whether Eric has landed after jumping from the saddle of the
        bike.
        """
        if self.y >= self.base_location[1] and self.get_floor():
            self.base_location = None
            return True
        return False

    #//////////////////////////////////////////////////////////////////////////
    # Sound effects
    #//////////////////////////////////////////////////////////////////////////
    def play_sound(self, sound_id, mode=sound.SUSPEND):
        """Play a sound effect.

        :param sound_id: The ID of the sound effect.
        :param mode: See :meth:`pyskool.sound.Beeper.play`.
        """
        self.skool.play_sound(sound_id, mode)

    def make_sitting_sound(self):
        """Play a sitting sound effect. This will be a walking sound effect,
        chosen at random from those available.
        """
        self.skool.make_sitting_sound()

    def make_walking_sound(self, index):
        """Make a walking sound effect.

        :param index: The index of the walking sound effect.
        """
        self.skool.make_walking_sound(index)

