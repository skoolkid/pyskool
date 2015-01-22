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
The main timetable and the skool clock.
"""

import random

class Timetable:
    """Represents the timetable of lessons, and the skool clock that ticks down
    until the bell rings.

    :type config: dict
    :param config: Configuration parameters from the ini file.
    """
    def __init__(self, config):
        self.index = -1
        self.lesson_id = None
        self.lessons = []
        self.lesson_details = {}
        self.counter = 0
        self.ticking = True
        self.lesson_length = config.get('LessonLength', 2400)
        self.lesson_start_time = config.get('LessonStartTime', 600)
        self.get_along_time = config.get('GetAlongTime', 200)
        self.assembly_prefix = config.get('AssemblyPrefix', 'Assembly')
        self.playtime_prefix = config.get('PlaytimePrefix', 'Playtime')
        self.special_playtimes = []
        self.p_special_playtime = config.get('SpecialPlaytimeProbability', 0)

    def reinitialise(self):
        """Reinitialise the timetable after a game has ended."""
        self.counter = 0
        self.ticking = True
        # Move to the next playtime in the timetable, or to the beginning of
        # the timetable if no playtime is found
        while not self.is_playtime() and self.index < len(self.lessons):
            self.index += 1
            self.lesson_id = self.lessons[self.index % len(self.lessons)]
        self.index -= 1

    def add_lesson(self, lesson_id):
        """Add a lesson to the timetable.

        :param lesson_id: The ID of the lesson.
        """
        self.lessons.append(lesson_id)

    def add_lesson_details(self, lesson_id, hide_teacher, teacher_id, room_id):
        """Add the details of a lesson to the timetable.

        :param lesson_id: The ID of the lesson.
        :param hide_teacher: If `True`, the teacher's name (if any) will not
                             be printed in the lesson box for this period.
        :param teacher_id: The ID of the teacher supervising Eric for this
                           period, or an empty string if it is unsupervised.
        :param room_id: The ID of the room in which the lesson takes place, or
                        the name of the period (such as PLAYTIME) if it is
                        unsupervised.
        """
        self.lesson_details[lesson_id] = (hide_teacher, teacher_id, room_id)

    def add_special_playtime(self, lesson_id):
        """Add a special playtime. Special playtimes do not appear in the main
        timetable (though they could be inserted); occasionally a normal
        playtime in the main timetable will be replaced by a special playtime.

        :param lesson_id: The ID of the special playtime.
        """
        self.special_playtimes.append(lesson_id)

    def is_assembly(self):
        """Return whether it's Assembly."""
        return self.assembly_prefix and self.lesson_id.startswith(self.assembly_prefix)

    def is_playtime(self):
        """Return whether it's Playtime."""
        return self.playtime_prefix and self.lesson_id.startswith(self.playtime_prefix)

    def next_lesson(self):
        """Proceed to the next lesson in the timetable. If the next lesson is
        playtime and there are any special playtimes defined, one of those may
        be chosen as the next lesson.
        """
        self.ticking = True
        self.counter = self.lesson_length
        self.index = (self.index + 1) % len(self.lessons)
        self.lesson_id = self.lessons[self.index]
        if self.is_playtime() and self.special_playtimes and random.random() < self.p_special_playtime:
            self.lesson_id = random.choice(self.special_playtimes)

    def hide_teacher(self):
        """Return whether the teacher's name (if any) should be displayed in
        the lesson box for the current period. This is generally `True` for
        classroom periods, and `False` for any other period (supervised or
        otherwise).
        """
        return self.lesson_details[self.lesson_id][0]

    def get_teacher_id(self):
        """Return the ID of the teacher supervising Eric for the current
        period, or an empty string if it is an unsupervised period.
        """
        return self.lesson_details[self.lesson_id][1]

    def get_room_id(self):
        """Return the ID of the room Eric's will be expected to show up in at
        some point during the current period, or else the name of the period
        (such as PLAYTIME).
        """
        return self.lesson_details[self.lesson_id][2]

    def tick(self):
        """Advance the skool clock by one tick (unless the clock has been
        stopped).

        :return: `True` if it's time for the bell to ring, `False` otherwise.
        """
        if self.ticking:
            self.counter -= 1
        return self.counter < 0

    def _is_time(self, ticks):
        """Return whether at least a certain number of skool clock ticks have
        happened since the bell rang.

        :param ticks: The number of ticks.
        """
        return self.counter + ticks < self.lesson_length

    def is_time_remaining(self, ticks):
        """Return whether there is no more than a certain number of skool clock
        ticks remaining before the bell rings.

        :param ticks: The number of ticks.
        """
        return self.counter <= ticks

    def is_time_to_get_along(self):
        """Return whether Eric should have left the classroom he was in last
        period by now.
        """
        return self._is_time(self.get_along_time)

    def is_time_to_start_lesson(self):
        """Return whether it's time to start a lesson. When the answer is
        `True`, teachers will stop pacing up and down outside classroom
        doorways.
        """
        return self._is_time(self.lesson_start_time)

    def is_teaching_eric(self, character):
        """Return whether a character is supervising Eric during the current
        period.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        """
        return self.get_teacher_id() == character.character_id

    def up_a_year(self):
        """Take appropriate action when Eric has gone up a year. This entails
        setting the skool clock so that half a normal lesson length remains
        before the bell will ring.
        """
        self.counter = self.lesson_length // 2

    def stop(self):
        """Stop the skool clock. Any further attempts to make it tick will be
        futile until :meth:`resume` is called."""
        self.ticking = False

    def resume(self, ticks):
        """Start the skool clock with a certain number of ticks remaining till
        the bell rings. If the clock was previously stopped (see :meth:`stop`),
        it will start ticking again.

        :param ticks: The number of ticks.
        """
        self.counter = ticks
        self.ticking = True

    def rewind(self, ticks):
        """Rewind the skool clock by a number of ticks.

        :param ticks: The number of ticks.
        """
        self.counter += ticks
