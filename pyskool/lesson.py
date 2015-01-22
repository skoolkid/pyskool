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
Classes concerned with controlling what goes on during a lesson.
"""

import random
import re

from . import lines
from . import ai

class Lesson:
    """Controls the interaction between the teacher, the swot and Eric during a
    lesson. The various actions required by the teacher and the swot during a
    lesson - such as grassing on Eric for being absent, writing on the board,
    and asking and answering questions - are defined by individual methods on
    this class.

    A new lesson is created by the swot when he sits down after being told to
    by the teacher at the classroom doorway.

    :type cast: :class:`~pyskool.cast.Cast`
    :param cast: The cast.
    :type swot: :class:`~pyskool.character.Character`
    :param swot: The swot.
    :type room: :class:`~pyskool.room.Room`
    :param room: The classroom in which the lesson is taking place.
    :type config: dict
    :param config: Configuration parameters from the ini file.
    """
    def __init__(self, cast, swot, room, config):
        self.cast = cast
        self.swot = swot
        self.room = room
        self.hitter_id = None
        self.writer_id = None
        self.teacher = None
        self.qa_generator = None
        self.qa_group = None
        self.answer = None
        self.asked_special = False
        self.actor = None
        self.swot_action = 'check_eric_initial'
        self.teacher_action = None
        self.base_action = 'tell_class_what_to_do'
        self.base_location = None
        self.base_direction = None
        self.grassed = False
        self.absence_message_ids = (lines.BE_PUNCTUAL, lines.STAY_IN_CLASS)
        self.absence_index = 0
        self.p_grass_for_hitting = config.get('GrassForHittingProbability', 0.140625)
        self.p_lines_for_tales = config.get('LinesForTalesProbability', 0.328125)
        self.p_write_on_board = config.get('EricsTeacherWriteOnBoardProbability', 0.28125)
        self.p_qa_session = config.get('QASessionProbability', 0.90625)

    def join(self, teacher, qa_generator, qa_group):
        """Make a teacher join the lesson. This method is called by the teacher
        when he notices that the swot has sat down.

        :type teacher: :class:`~pyskool.character.Character`
        :param teacher: The teacher.
        :type qa_generator: :class:`~pyskool.lesson.QAGenerator`
        :param qa_generator: The question-and-answer generator to use.
        :param qa_group: The Q&A group from which to choose questions and
                         answers for the teacher and the swot; if `None`, the
                         Q&A group will be chosen at random from those
                         available each time a question and answer is
                         generated.
        """
        self.teacher = teacher
        self.qa_generator = None
        if random.random() < self.p_qa_session:
            self.qa_generator = qa_generator
            self.qa_group = qa_group
            self.base_action = 'ask_question'
        self.actor = self.swot
        self.base_location = (teacher.x, teacher.y)
        self.base_direction = teacher.direction

    def next_swot_action(self):
        """Complete any actions required of the swot, and return the next
        command to be executed by him, or `None` if it's not his turn to act.
        """
        while self.actor is self.swot:
            method = getattr(self, self.swot_action)
            next_action = method()
            if next_action:
                return next_action

    def check_eric_initial(self):
        """Make the swot tell the teacher that Eric is absent (if he is). This
        method defines the swot's first action during a lesson. If Eric is
        absent, the teacher's next action will be :meth:`fetch_eric`. The
        swot's next action is set to :meth:`grass_for_hitting`.

        :return: A :class:`~pyskool.ai.Say` command if Eric is absent,
                 otherwise `None`.
        """
        self.teacher.set_home_room()
        self.swot_action = 'grass_for_hitting'
        if self.is_eric_absent():
            self.teacher_action = 'fetch_eric'
            return ai.Say(self.cast.get_absent_tale(self.teacher), True)

    def grass_for_hitting(self):
        """Make the swot tell a tale about someone hitting him (possibly). This
        method defines the swot's second action during a lesson. The teacher's
        next action is set to :meth:`give_lines_for_hitting`. The swot's next
        action is set to :meth:`grass_for_writing`.

        :return: A :class:`~pyskool.ai.Say` command, or `None` if the swot
                 decides not to tell a tale.
        """
        self.swot_action = 'grass_for_writing'
        self.teacher_action = 'give_lines_for_hitting'
        if random.random() < self.p_grass_for_hitting:
            self.hitter_id, tale = self.cast.get_hit_tale(self.teacher)
            return ai.Say(tale, True)
        self.switch()

    def grass_for_writing(self):
        """Make the swot tell a tale about someone writing on the blackboard
        (if it was written on by Eric or the tearaway). This method defines the
        swot's third action during a lesson. The teacher's next action is set
        to :meth:`give_lines_for_writing`.

        :return: A :class:`~pyskool.ai.Say` command, or `None` if the swot
                 decides not to tell a tale.
        """
        self.grassed = True
        self.teacher_action = 'give_lines_for_writing'
        writer = self.room.get_blackboard_writer()
        if writer:
            self.writer_id, tale = self.cast.get_write_tale(writer.character_id, self.teacher)
            if tale:
                return ai.Say(tale, True)
        self.switch()

    def check_eric(self):
        """Make the swot tell the teacher that Eric is absent (if he is). If
        Eric is absent, the teacher's next action will be :meth:`fetch_eric`.

        :return: A :class:`~pyskool.ai.Say` command if Eric is absent,
                 otherwise `None`.
        """
        if self.is_eric_absent():
            self.teacher_action = 'fetch_eric'
            return ai.Say(self.cast.get_absent_tale(self.teacher), True)
        self.switch(self.base_action)

    def answer_question(self):
        """Make the swot answer the teacher's question. The swot's next action
        will be :meth:`check_eric`.
        """
        self.swot_action = 'check_eric'
        return ai.Say(self.cast.expand_title(self.answer, self.teacher))

    def next_teacher_action(self):
        """Complete any actions required of the teacher, and return the next
        command to be executed by him, or `None` if it's not his turn to act.
        """
        while self.actor is self.teacher:
            method = getattr(self, self.teacher_action)
            next_action = method()
            if next_action:
                return next_action

    def fetch_eric(self):
        """Make the teacher track down Eric if he is absent. The teacher may
        first give lines to the swot for telling tales. If Eric is present by
        the time this method is called (after the swot has finished telling the
        teacher that Eric is not in class), the teacher will give lines to Eric
        for being late (or for leaving early).

        :return: A :class:`~pyskool.ai.FetchEric` command if Eric is still
                 absent after the swot has finished speaking, otherwise `None`.
        """
        if random.random() < self.p_lines_for_tales:
            self.teacher.give_lines(self.swot.character_id, lines.NO_TALES, True)
        if self.is_eric_absent():
            self.teacher_action = 'return_to_base'
            self.teacher.reset_come_along_index()
            self.absence_index = 1
            return ai.FetchEric()
        lines_message_id = self.absence_message_ids[self.absence_index]
        self.absence_index = 1
        self.teacher.give_lines(self.cast.eric.character_id, lines_message_id, True)
        self.switch()

    def return_to_base(self):
        """Make the teacher return to the classroom after fetching Eric. The
        teacher's next action will be :meth:`ask_question` (if a
        question-and-answer session was interrupted) or
        :meth:`walk_up_or_down`.

        :return: A :class:`~pyskool.ai.GoToXY` command.
        """
        if (self.teacher.x, self.teacher.y) != self.base_location:
            return ai.GoToXY(*self.base_location)
        if self.room.has_blackboard() and not self.grassed:
            if self.teacher.direction != self.base_direction:
                # Turn teacher round before continuing
                return ai.GoTowardsXY(self.teacher.x - self.teacher.direction, self.teacher.y)
            else:
                self.switch()
                return
        if self.qa_generator:
            if self.teacher.direction != self.base_direction:
                # Turn teacher round before continuing
                return ai.GoTowardsXY(self.teacher.x - self.teacher.direction, self.teacher.y)
            else:
                self.teacher_action = 'ask_question'
        else:
            self.teacher_action = 'walk_up_or_down'
            if self.teacher.direction != self.base_direction:
                # Instead of turning round to face in the base direction only
                # to turn around again immediately, start walking up and down
                # now
                return ai.GoToXY(self.teacher.x + self.teacher.get_blackboard_pace_distance() * self.teacher.direction, self.teacher.y)

    def give_lines(self, victim_id, message_id):
        """Make the teacher give lines to the swot for telling a tale, or give
        lines to the subject of the swot's tale.

        :param victim_id: The ID of the subject (may be `None`, in which case
                          no lines will be given).
        :param message_id: The ID of the lines message.
        """
        if victim_id:
            victim_present = self.room.contains(self.cast.get(victim_id))
            punish_swot = random.random() < self.p_lines_for_tales
            if punish_swot or not victim_present:
                victim_id, message_id = self.swot.character_id, lines.NO_TALES
            self.teacher.give_lines(victim_id, message_id, True)

    def give_lines_for_hitting(self):
        """Make the teacher give lines to the swot for telling a tale about
        being hit, or give lines to the subject of the tale. If the swot has
        not told such a tale, nothing happens.
        """
        self.give_lines(self.hitter_id, lines.NO_HITTING)
        self.switch()

    def give_lines_for_writing(self):
        """Make the teacher give lines to the swot for telling a tale about the
        blackboard being written on, or give lines to the subject of the tale.
        If the swot has not told such a tale, nothing happens. The teacher's
        next action is set to :meth:`wipe_board`.
        """
        self.give_lines(self.writer_id, lines.NO_WRITING)
        self.teacher_action = 'wipe_board'

    def wipe_board(self):
        """Make the teacher wipe the board (if there is one). The teacher's
        next action will be :meth:`walk_to_board`.

        :return: A :class:`~pyskool.ai.WipeBoard` command if there is a
                 blackboard, `None` otherwise.
        """
        self.absence_index = 1
        if self.room.has_blackboard():
            self.teacher_action = 'walk_to_board'
            return ai.WipeBoard()
        self.teacher_action = self.base_action

    def walk_to_board(self):
        """Make the teacher walk to the middle of the blackboard (after having
        wiped it). The teacher's next action will be :meth:`write_on_board`.

        :return: A :class:`~pyskool.ai.GoToXY` command.
        """
        self.teacher_action = 'write_on_board'
        return ai.GoToXY(self.teacher.x - self.teacher.get_blackboard_backtrack() * self.teacher.direction, self.teacher.y)

    def write_on_board(self):
        """Make the teacher write on the blackboard (possibly). The teacher's
        next action will be the base action for this lesson (either
        :meth:`tell_class_what_to_do` or :meth:`ask_question`).

        :return: A :class:`~pyskool.ai.WriteOnBoard` command if the teacher
                 chooses to write, otherwise `None`.
        """
        self.base_location = (self.teacher.x, self.teacher.y)
        self.base_direction = self.teacher.direction
        self.teacher_action = self.base_action
        if random.random() < self.p_write_on_board:
            return ai.WriteOnBoard(self.teacher.get_blackboard_message())

    def ask_question(self):
        """Make the teacher ask a question. The swot's next action is set to
        :meth:`answer_question`.

        :return: A :class:`~pyskool.ai.Say` command.
        """
        self.swot_action = 'answer_question'
        return ai.Say(self.get_question(), True)

    def tell_class_what_to_do(self):
        """Make the teacher tell the class what to do (as opposed to starting a
        question-and-answer session with the swot). The teacher's next action
        (and base action for the remainder of the lesson) will be
        :meth:`walk_up_or_down`.

        :return: A :class:`~pyskool.ai.TellClassWhatToDo` command.
        """
        self.base_action = 'walk_up_or_down'
        self.teacher_action = 'walk_up_or_down'
        return ai.TellClassWhatToDo()

    def walk_up_or_down(self):
        """Make the teacher walk up or down in front of the blackboard. This
        action is used during a lesson with no question-and-answer session.
        The swot's next action is set to :meth:`check_eric`.

        :return: A :class:`~pyskool.ai.WalkUpOrDown` command.
        """
        self.switch('check_eric')
        return ai.WalkUpOrDown()

    def get_question(self):
        """Return the next question for the teacher to ask in a
        question-and-answer session with the swot.
        """
        if not self.asked_special and self.qa_generator.has_special_question():
            self.asked_special = True
            question, self.answer = self.qa_generator.prepare_special_qa()
        else:
            question, self.answer = self.qa_generator.prepare_qa(self.qa_group)
        return question

    def switch(self, action=None):
        """Switch turns between the actors in this lesson (the teacher and the
        swot).

        :param action: The next action (method to execute) for the next actor;
                       if `None`, the next action (which may have already been
                       set) is unchanged.
        """
        if self.actor is self.swot:
            self.actor = self.teacher
            self.teacher_action = action or self.teacher_action
        else:
            self.actor = self.swot
            self.swot_action = action or self.swot_action

    def finished_speaking(self):
        """Indicate that the current actor (teacher or swot) has finished
        speaking.
        """
        self.switch()

    def is_eric_absent(self):
        """Return whether Eric is absent from the classroom in which this
        lesson is taking place.
        """
        return not self.room.contains(self.cast.eric)

class QAGenerator:
    """Generates questions and answers for the teacher and swot to use during a
    lesson. Every teacher gets his own generator to keep; it is built before
    the game starts.
    """
    def __init__(self):
        self.questions = {}
        self.answers = {}
        self.qa_pairs = {}
        self.special_qa_group = None
        self.remaining = {}

    def set_special_group(self, qa_group, index):
        """Set the Q&A group to use for the teacher's special question (if
        there is one).

        :param qa_group: The name of the Q&A group.
        :param index: The index (0 or 1) of the special answer in the Q&A pair.
        """
        self.special_qa_group = qa_group
        self.special_qa_pair_index = index

    def initialise_special_answer(self):
        """Initialise the answer to the teacher's special question (if there is
        one). The special answer is chosen at random from the Q&A pairs in the
        Q&A group of the special question.
        """
        if self.special_qa_group:
            self.special_answer_index = random.randrange(len(self.qa_pairs[self.special_qa_group]))
            return self.qa_pairs[self.special_qa_group][self.special_answer_index][self.special_qa_pair_index]

    def has_special_question(self):
        """Return whether the teacher has a special question. A special
        question is one to which the answer must be seen written on a
        blackboard by the teacher to make him reveal his safe combination
        letter.
        """
        return self.special_qa_group is not None

    def add_question(self, question_id, qa_group, text):
        """Add a question to a Q&A group.

        :param question_id: The ID of the question.
        :param qa_group: The name of the Q&A group to add the question to.
        :param text: The text of the question.
        """
        q = self.questions.setdefault(qa_group, [])
        q.append((question_id, text))

    def add_answer(self, question_id, text):
        """Add an answer to a question.

        :param question_id: The ID of the question.
        :param text: The text of the answer.
        """
        self.answers[question_id] = text

    def add_qa_pair(self, qa_group, word1, word2):
        """Add a Q&A pair to a Q&A group.

        :param qa_group: The name of the Q&A group.
        :param word1: The first word of the pair.
        :param word2: The second word of the pair.
        """
        if qa_group not in self.qa_pairs:
            self.qa_pairs[qa_group] = []
            self.remaining[qa_group] = []
        self.qa_pairs[qa_group].append((word1, word2))

    def _expand(self, template, word1, word2):
        """Return a message template with any Q&A pair macro expanded to the
        appropriate word from the pair.

        :param template: The message template.
        :param word1: The first word of the pair.
        :param word2: The second word of the pair.
        """
        if template:
            return template.replace('$1', word1).replace('$2', word2)

    def prepare_special_qa(self):
        """Prepare the teacher's special question and answer (if any).

        :return: A 2-tuple containing the question and the answer.
        """
        word1, word2 = self.qa_pairs[self.special_qa_group][self.special_answer_index]
        return self.special_question, self._expand(self.special_answer, word1, word2)

    def prepare_qa(self, qa_group=None):
        """Prepare a randomly chosen question and answer.

        :param qa_group: The Q&A group from which to choose the question and
                         answer; if `None`, the Q&A group will be chosen at
                         random from those available.
        :return: A 2-tuple containing the question and the answer.
        """
        if not qa_group:
            qa_group = random.choice(list(self.questions.keys()))
        question_id, question = random.choice(self.questions.get(qa_group, [(None, None)]))
        answer = self.answers.get(question_id)
        if not self.remaining[qa_group]:
            self.remaining[qa_group] = list(range(len(self.qa_pairs[qa_group])))
        random_index = self.remaining[qa_group].pop(random.randrange(len(self.remaining[qa_group])))
        word1, word2 = self.qa_pairs[qa_group][random_index]
        return self._expand(question, word1, word2), self._expand(answer, word1, word2)

class AssemblyMessageGenerator:
    """Generates messages to be delivered by whoever is conducting assembly.
    There is only one assembly message generator, shared by the whole skool.
    """
    def __init__(self):
        self.templates = []
        self.groups = {}

    def add_message_template(self, template):
        """Add `template` to the generator's collection of message templates.
        """
        self.templates.append(template)

    def add_word(self, group_id, word):
        """Add a word to the generator's collection.

        :param group_id: The name of the group to add the word to.
        :param word: The word.
        """
        group = self.groups.setdefault(group_id, [])
        group.append(word)

    def generate_message(self):
        """Return a message based on a randomly chosen template and containing
        randomly chosen phrases.
        """
        message = random.choice(self.templates)
        while True:
            search = re.search('\$[A-Z0-9]+', message)
            if not search:
                break
            marker = search.group()
            group_id = marker[1:]
            if group_id in self.groups:
                rep = random.choice(self.groups[group_id])
                message = message.replace(marker, rep)
            else:
                message = message.replace(marker, group_id)
        return message
