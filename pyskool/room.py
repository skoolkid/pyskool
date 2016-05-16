# -*- coding: utf-8 -*-
# Copyright 2008-2010, 2015, 2016 Richard Dymond (rjdymond@gmail.com)
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
Classes that represent the rooms in the skool and their furniture.
"""

class Room:
    """A classroom or some other region of the skool that Eric is expected to
    show up in when the timetable demands it.

    :param room_id: The unique ID of the room.
    :param name: The name of the room (as it should appear in the lesson box).
    :param top_left: The coordinates of the top-left corner of the room.
    :param bottom_right: The coordinates of the bottom-right corner of the
                         room.
    :param get_along: If `True`, Eric will be told to get along if he's found
                      in this room when the timetable doesn't say he should be
                      in it.
    """
    def __init__(self, room_id, name, top_left, bottom_right, get_along):
        self.room_id = room_id
        self.name = name
        self.min_x = top_left[0]
        self.max_x = bottom_right[0]
        self.min_y = top_left[1]
        self.max_y = bottom_right[1]
        self.get_along = get_along
        self.chairs = []
        self.desks = []
        self.blackboard = None

    def get_blackboard_writer(self):
        """Return the character who wrote on the blackboard in this room, or
        `None` if either the room has no blackboard, or the blackboard is
        clean.
        """
        if self.blackboard:
            return self.blackboard.writer

    def has_blackboard(self):
        """Return whether the room has a blackboard."""
        return self.blackboard is not None

    def add_blackboard(self, screen, top_left, size, chalk, skool_image):
        """Add a blackboard to the room.

        :type screen: :class:`~pyskool.graphics.Screen`
        :param screen: The screen.
        :param top_left: The coordinates of the top-left of the blackboard.
        :param size: The size (width, height) of the blackboard.
        :param chalk: The chalk colour to use when writing on the blackboard.
        :type skool_image: :class:`~pyskool.graphics.Image`
        :param skool_image: An image of the skool.
        """
        self.blackboard = Blackboard(screen, top_left, size, chalk, skool_image)

    def restore_blackboard(self):
        """Restore the image of the blackboard in this room. This method is
        used to draw the contents of a blackboard afresh after restoring a
        saved game.
        """
        if self.blackboard:
            self.blackboard.restore()

    def build_blackboard_images(self):
        """Build the images for the blackboard in this room (if any). This
        method is called after rescaling the screen or loading a saved game.
        """
        if self.blackboard:
            self.blackboard.build_images()

    def blackboard_dirty(self):
        """Return `True` if the room has a blackboard and it is dirty,
        `False` otherwise.
        """
        if self.blackboard:
            return self.blackboard.is_dirty()

    def wipe_blackboard(self):
        """Wipe the blackboard in the room (if any) and mark it as clean."""
        if self.blackboard:
            self.blackboard.clear(True)

    def add_chair(self, x):
        """Add a chair to the room.

        :param x: The x-coordinate of the chair.
        """
        self.chairs.append(Chair(self, x))

    def add_desk(self, x):
        """Add a desk (that can be opened) to the room.

        :param x: The x-coordinate of the desk.
        """
        self.desks.append(Desk(self, x))

    def beside_blackboard(self, character):
        """Return whether a character is standing beside the blackboard in this
        room.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        if self.blackboard:
            on_floor_y = self.max_y - character.height + 1
            return on_floor_y == character.y and self.blackboard.beside(character)

    def contains(self, character):
        """Return whether a character is in this room.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        if self.min_y <= character.y <= self.max_y - character.height + 1:
            return self.min_x <= character.x <= self.max_x
        return False

    def get_chair_direction(self):
        """Return the direction in which the chairs in this room are facing.

        :return: -1 if the chairs are facing left, 1 if they are facing right,
                 or `None` if there are no chairs in the room.
        """
        if self.chairs:
            return -1 if self.chairs[0].x < self.chairs[-1].x else 1

    def chair(self, character, check_dir=True):
        """Return the chair in this room that a character is next to, or
        `None` if the character is not next to a chair.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        :param check_dir: If `True`, return a chair only if the character is
                          beside one and facing the right way to sit in it;
                          otherwise disregard the direction in which the
                          character is facing.
        """
        direction = self.get_chair_direction()
        for chair in self.chairs:
            on_floor_y = self.max_y - character.height + 1
            if (not check_dir or character.direction == direction) and (character.x, character.y) == (chair.x, on_floor_y):
                return chair

    def desk(self, character):
        """Return the desk in this room that a character is sitting at, or
        `None` if the character is not sitting at a desk.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        if character.is_sitting_on_chair():
            for desk in self.desks:
                on_floor_y = self.max_y - character.height + 1
                if (character.x, character.y) == (desk.x, on_floor_y):
                    return desk

    def get_next_chair(self, character, move_along, go_to_back):
        """Return the chair that a character should find and sit in.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character looking for a chair.
        :param move_along: If `True` (and `go_to_back` is False), return the
                           next seat along if the character is currently beside
                           one; otherwise return the seat closest to the
                           character.
        :param go_to_back: If `True`, return the back seat in the room.
        :return: A 2-tuple containing the target chair and the direction it
                 faces (-1 or 1).
        """
        front_seat, back_seat = self.chairs[0], self.chairs[-1]
        direction = self.get_chair_direction()
        if go_to_back:
            return back_seat, direction
        if character.direction != direction or (move_along and front_seat.x == character.x):
            return back_seat, direction
        min_distance = 1000
        next_chair = back_seat
        for chair in self.chairs:
            distance = (chair.x - character.x) * direction
            if distance == 0 and move_along:
                continue
            if 0 <= distance < min_distance:
                min_distance = distance
                next_chair = chair
        return next_chair, direction

class Chair:
    """A seat in a classroom.

    :type room: :class:`Room`
    :param room: The room the chair is in.
    :param x: The x-coordinate of the chair.
    """
    def __init__(self, room, x):
        self.x = x
        self.room = room
        self.occupant = None

    def seat(self, character):
        """Mark the chair as being occupied by a character.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character sitting in the chair.
        """
        self.occupant = character

    def vacate(self):
        """Mark this chair as vacant."""
        self.occupant = None

class Desk:
    """A desk (that can be opened) in a classroom.

    :type room: :class:`Room`
    :param room: The room the desk is in.
    :param x: The x-coordinate of the desk.
    """
    def __init__(self, room, x):
        self.x = x
        self.room = room
        self.empty()

    def insert(self, item):
        """Insert an inventory item (water pistol or stinkbombs) into the desk.

        :param item: The ID of the item to insert.
        """
        self.contents = item

    def empty(self):
        """Mark the desk as empty."""
        self.contents = None

class Blackboard:
    """A blackboard in a classroom.

    :type screen: :class:`~pyskool.graphics.Screen`
    :param screen: The screen.
    :param top_left: The coordinates of the top-left of the blackboard.
    :param size: The size (width, height) of the blackboard.
    :param chalk: The chalk colour to use when writing on the blackboard.
    :type skool_image: :class:`~pyskool.graphics.Image`
    :param skool_image: An image of the skool.
    """
    def __init__(self, screen, top_left, size, chalk, skool_image):
        self.screen = screen
        self.x = top_left[0]
        self.y = top_left[1]
        self.width = size[0]
        self.height = size[1]
        self.right_x = self.x + self.width - 1
        self.chalk = chalk
        # Create a colorkey for the blackboard text images that is different
        # from the chalk colour
        self.key = ((chalk[0] + 1) % 256, 0, 0)
        self.clear()
        self.image = skool_image.subsurface(top_left, size)
        self.clean_image = self.image.copy()
        self.wiped_columns = []

    def __getstate__(self):
        d = self.__dict__.copy()
        d['clean_image'] = None
        return d

    def restore(self):
        """Restore the image of this blackboard. This method is used after
        restoring a saved game.
        """
        self.write('')
        for column in self.wiped_columns:
            self._wipe_column(column)

    def build_images(self):
        """Build the images for the blackboard. This method is called after
        rescaling the screen or loading a saved game."""
        self.image.build()
        self.clean_image = self.image.copy()

    def write(self, char):
        """Write a character on the blackboard.

        :param char: The character to write.
        """
        if self.lines:
            if len(self.lines) == 1:
                line_width = self.screen.get_text_width(self.lines[0] + char)
                if line_width > self.width * 8:
                    self.newline()
            self.lines[-1] += char
        else:
            self.lines.append(char)
        for line_no, line in enumerate(self.lines):
            if line:
                text_image = self.screen.get_text(line, self.chalk, self.key)
                self.image.scale_blit(text_image, (0, line_no))

    def newline(self):
        """Start a new line on the blackboard."""
        if len(self.lines) < self.height:
            self.lines.append('')

    def _wipe_column(self, column):
        """Wipe a column of the blackboard image.

        :param column: The column to wipe.
        """
        self.image.scale_blit(self.clean_image.surface, (column, 0), (column, 0, 1, self.height))

    def wipe(self, column):
        """Wipe a column of the blackboard clean.

        :param column: The column to wipe clean.
        """
        self._wipe_column(column)
        self.wiped_columns.append(column)
        if len(self.wiped_columns) == self.width:
            self.clear()

    def is_dirty(self):
        """Return whether anything is written on the blackboard."""
        return self.lines and len(self.lines[0]) > 0

    def clear(self, blit=False):
        """Mark this blackboard as clean.

        :param blit: If `True`, the blackboard surface will be blitted clean
                     too; otherwise it will be left alone.
        """
        self.lines = []
        self.writer = None
        if blit:
            self.image.blit(self.clean_image.surface, (0, 0))
        self.wiped_columns = []

    def beside(self, character):
        """Return whether a character is standing beside the blackboard.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        arm_x = character.x + character.direction + 1
        return self.x + 1 <= arm_x <= self.x + self.width - 2

    def shows(self, text, in_order=True):
        """Return whether the blackboard displays all the characters in a given
        piece of text.

        :param text: The text to look for.
        :param in_order: If `True`, return `True` only if the order of the
                         characters written on the board matches too.
        """
        if not self.lines:
            return False
        if in_order:
            return self.lines[0].lower().startswith(text.lower())
        source = self.lines[0][:len(text)].lower()
        target = text.lower()
        if len(source) != len(target):
            return False
        while source:
            if source[0] in target:
                target = target.replace(source[0], '', 1)
                source = source[1:]
            else:
                return False
        return True

class NoGoZone:
    """A region of the skool in which Eric is never allowed to be.

    :param zone_id: The zone's unique ID.
    :param min_x: The x-coordinate of the left edge of the zone.
    :param max_x: The x-coordinate of the right edge of the zone.
    :param bottom_y: The y-coordinate of the bottom edge of the zone.
    :param top_y: The y-coordinate of the top edge of the zone.
    """
    def __init__(self, zone_id, min_x, max_x, bottom_y, top_y):
        self.zone_id = zone_id
        self.min_x = min_x
        self.max_x = max_x
        self.bottom_y = bottom_y
        self.top_y = top_y

    def contains(self, x, y):
        """Return whether a given location is inside the zone.

        :param x: The x-coordinate of the location.
        :param y: The y-coordinate of the location.
        """
        return self.min_x <= x <= self.max_x and self.top_y <= y <= self.bottom_y
