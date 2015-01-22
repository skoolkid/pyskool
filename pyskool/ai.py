# -*- coding: utf-8 -*-

# Copyright 2008-2012, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
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
Classes that implement the commands found in command lists, such as
:class:`GoTo` and :class:`ConductClass`.
"""

import sys
import random

from .location import Location
from . import debug

def get_command_class(command_name):
    """Return the class object for a given command.

    :param command_name: The name of the command.
    """
    return getattr(sys.modules[__name__], command_name)

class CommandListTemplate:
    """Template from which a specific command list may be created (one or more
    times). `command_list_id` is an identifier for the command list, used only
    for debugging purposes.
    """
    def __init__(self, command_list_id):
        self.command_list_id = command_list_id
        self.commands = []

    def add_command(self, command_class, *params):
        """Add a command to this template.

        :param command_class: The class object that implements the command.
        :param params: The command's parameters.
        """
        self.commands.append((command_class, params))

    def get_commands(self, start):
        """Return a list of commands (initialised command class instances)
        constructed from this template.

        :param start: The index of the first command. If `start` is 0, the
                      entire list of commands is returned. If `start` is N>0,
                      the first N commands are omitted.
        """
        return [cmd_class(*params) for cmd_class, params in self.commands[start:]]

class CommandList:
    """A list of commands built from a :class:`CommandListTemplate`. Maintains
    a command stack from which commands are popped after they have finished
    executing.

    :type character: :class:`~pyskool.character.Character`
    :param character: The character to be controlled (the command list owner).
    """
    def __init__(self, character):
        self.character = character
        self.stack = []
        self.index = None
        self.restart_index = None
        self.template = None
        self.controlling_command = None
        self.controlling_command_timer = None
        self.subcommand = None

    def command(self):
        """Hand control of the command list owner over to the current command.
        The steps taken are:

        1. Add the controlling command (if there is one, and the current
           command is interruptible) to the stack.
        2. Add the subcommand (if there is one, and the current command is
           interruptible) to the stack.
        3. If the command stack is empty, pull the next command from the
           command list and add it to the stack.
        4. Execute the current command (the last command on the stack).
        5. Act on the return value from the current command; if it is:

          * `None`, then return from this method;
          * `self` (the command itself), then pop the current command from the
            stack and go to step 3;
          * another command, then add that command to the stack and go to step
            4.
        """
        if self.stack and self.is_interruptible() and self.controlling_command and self.controlling_command not in self.stack:
            self.add_command(self.controlling_command)
        if self.subcommand and self.subcommand not in self.stack and self.is_interruptible():
            self.add_command(self.subcommand)
        while True:
            if self.stack:
                command = self.stack[-1]
                subcommand = command.execute()
                if subcommand is None:
                    break
                elif subcommand is not command:
                    self.add_command(subcommand)
                elif self.stack:
                    self.stack.pop()
            else:
                # Remove any controlling command before moving to the next
                # command
                if self.controlling_command:
                    self.controlling_command_timer -= 1
                    if self.controlling_command_timer < 0:
                        if self.controlling_command in self.stack:
                            # Finish the controlling command only if it got a
                            # chance to be placed on the stack
                            self.controlling_command.finish()
                        self.controlling_command = None
                self.add_command(self.commands[self.index])
                self.index += 1

    def restart(self, index=None):
        """Restart this command list. When the current command finishes, the
        next command will be the first command in the command list, or the
        command denoted by `index`.

        :param index: The index of the command at which to restart (defaults to
                      0).
        """
        self.index = index or 0
        self.commands = self.template.get_commands(self.restart_index)

    def add_command(self, command):
        """Add a command to the stack.

        :param command: The :class:`Command` to add.
        """
        command.character = self.character
        self.stack.append(command)

    def set_template(self, template):
        """Set the template for this command list. This method is used to
        replace a character's current command list (e.g. when the bell rings).
        Any interruptible commands remaining on the stack are removed (after
        calling their :meth:`~Command.finish` methods); uninterruptible
        commands are left in place so that they have a chance to finish before
        the new command list kicks in.

        :param template: The :class:`CommandListTemplate` to use.
        """
        self.template = template
        self.subcommand = None
        while self.stack and self.stack[0].is_interruptible():
            self.stack[0].finish()
            self.stack.pop(0)
        self.restart_index = 0
        self.restart()

    def set_controlling_command(self, command):
        """Set the controlling command for this command list. The controlling
        command, if set, is executed before and in addition to the current
        command on the stack (see :meth:`command`). :class:`WalkFast` and
        :class:`HitNowAndThen` are examples of commands that are used as
        controlling commands.

        :type command: :class:`Command`
        :param command: The command to set as the controlling command.
        """
        self.controlling_command = command
        self.controlling_command_timer = 1

    def set_restart_point(self):
        """Remove the current and all previous commands from the command list.
        When the current command finishes, the next command will be regarded as
        the first for the purposes of a command list restart.
        """
        self.restart_index = self.index
        self.restart()

    def jump(self, offset):
        """Jump forwards (or backwards) in the list of commands.

        :param offset: The offset by which to jump. -2 means the previous
                       command, -1 means the current command, 0 means the next
                       command, and 1 means the next command but one.
        """
        self.restart(self.index + offset)

    def is_GoToing(self):
        """Return whether the character is under the control of one of the
        :class:`GoTo` commands.
        """
        return self.stack and self.stack[0].is_GoTo()

    def get_GoTo_destination(self):
        """Return the destination of the character, or `None` if he is not
        under the control of a :class:`GoTo` command.
        """
        if self.is_GoToing():
            return self.stack[0].destination

    def set_GoTo_destination(self, destination):
        """Set the destination of the character if he is under the control of a
        :class:`GoTo` command.

        :type destination: :class:`~pyskool.location.Location`
        :param destination: The destination to set.
        """
        if destination and self.is_GoToing():
            self.stack[0].destination = destination

    def is_interruptible(self):
        """Return `False` if the command stack contains an uninterruptible
        command, `True` otherwise.
        """
        for command in self.stack:
            if not command.is_interruptible():
                return False
        return True

    def set_subcommand(self, command_name, args):
        """Set the subcommand for this command list. The subcommand, if set, is
        executed before and in addition to the current command on the stack
        (see :meth:`command`). :class:`MonitorEric` is an example of a command
        that is used as a subcommand.

        :param command_name: The name of the command to set as the subcommand.
        :param args: The subcommand's arguments.
        """
        command_class = get_command_class(command_name)
        self.subcommand = command_class(*args)

class Command:
    """Abstract class from which all other command classes inherit. Subclasses
    should implement a method named `execute`.
    """
    def is_interruptible(self):
        """Return whether this command is interruptible. An interruptible
        command can be terminated immediately by a command list restart. This
        method returns `True`, but subclasses may override it and return
        `False` instead.
        """
        return True

    def is_GoTo(self):
        """Return whether this command is one of the :class:`GoTo` commands.
        This method returns `False`, but the :class:`GoTo` commands override it
        and return `True`.
        """
        return False

    def execute(self):
        """Execute the command. The default implementation provided here does
        nothing; subclasses should override this method to supply the desired
        behaviour.

        :return: `self`
        """
        return self

    def finish(self):
        """Perform any required cleanup before the command is removed from the
        command stack. This method is called on a controlling command just
        before it is terminated, and on an interruptible command when it is
        interrupted. The default implementation provided here does nothing;
        subclasses override this method as necessary.
        """
        return

class ComplexCommand(Command):
    """Abstract class used by many commands that require a fixed sequence of
    steps to be executed with little or no conditional logic. Each step is
    implemented as a separate method. Subclasses must implement a method named
    `get_commands` that returns a list of the names of the methods to execute.
    """
    def __init__(self):
        self.index = 0
        self.commands = self.get_commands()

    def execute(self):
        """Execute the next step (method) in this command's sequence. What
        happens after that depends on the return value from the method called;
        if it is:

        * `False`, then the step is taken to be still in progress, and will
          be executed again the next time this method is called
        * `None`, then the step is taken to be finished
        * `self` (this command), then the entire command is taken to be
          finished, and no more steps will be executed
        * another command, then that command is added to the stack (so that
          it will be executed before proceeding to the next step)
        """
        method = getattr(self, self.commands[self.index])
        val = method()
        if val is not False:
            self.index = (self.index + 1) % len(self.commands)
        return val or None

    def restart(self):
        """Return to the first step in the sequence."""
        self.index = -1

    def done(self):
        """Terminate this complex command. This method is typically used as the
        last step in the sequence, and is provided for convenience to
        subclasses.

        :return: `self` (to terminate this command)
        """
        return self

class SitForAssembly(ComplexCommand):
    """Command that makes a character find a spot to sit down during assembly,
    and keeps him seated until assembly has finished.

    :param assembly_finished: The signal that indicates assembly is finished.
    :param sit_direction: The direction to face when sitting down.
    :param sit_range: The minimum and maximum distances the character should
                      walk back to find a spot to sit.
    """
    def __init__(self, assembly_finished, sit_direction, sit_range=(1, 4)):
        ComplexCommand.__init__(self)
        self.assembly_finished = assembly_finished
        self.sit_direction = sit_direction
        self.sit_range = sit_range

    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`find_spot_to_sit`
        * :meth:`sit_down`
        * :meth:`get_up`
        * :meth:`~ComplexCommand.done`
        """
        return ('find_spot_to_sit', 'sit_down', 'get_up', 'done')

    def find_spot_to_sit(self):
        """Make a character find a spot to sit during assembly. If assembly has
        already finished, the command is terminated.

        :return: `self` if assembly has finished, or a :class:`GoToXY` command
                 to send the character to a place to sit down.
        """
        if self.character.got_signal(self.assembly_finished):
            return self
        return GoToXY(self.character.x - random.randint(*self.sit_range), self.character.y)

    def sit_down(self):
        """Make a character sit down for assembly, or turn round to face the
        right way for assembly. If assembly has already finished, the command
        is terminated.

        :return: `self` if assembly has finished, `False` if the character
                 was turned round, or `None` if the character sat down.
        """
        if self.character.got_signal(self.assembly_finished):
            return self
        if self.character.direction != self.sit_direction:
            self.character.turn()
            return False
        self.character.sit()

    def get_up(self):
        """Make a character get up if assembly has finished. If assembly has
        not finished yet, return here next time.

        :return: `False` if assembly is still in progress, or `None` if the
                 character got up off the floor.
        """
        if not self.character.got_signal(self.assembly_finished):
            return False
        self.character.get_up()

class MoveDoor(ComplexCommand):
    """Abstract command that makes a character open or close a door or
    window.

    :param barrier_id: The ID of the door or window.
    :param shut: `True` if the door or window should be shut, `False`
                 otherwise.
    """
    def __init__(self, barrier_id, shut):
        ComplexCommand.__init__(self)
        self.barrier_id = barrier_id
        self.shut = shut

    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`raise_arm`
        * :meth:`move_door`
        * :meth:`lower_arm`
        * :meth:`~ComplexCommand.done`
        """
        return ('raise_arm', 'move_door', 'lower_arm', 'done')

    def raise_arm(self):
        """Make a character raise his arm in preparation for opening or closing
        a door or window, or do nothing if the door/window is already in the
        desired state.

        :return: `self` if the door/window is already in the desired state, or
                 `None` if the character raised his arm.
        """
        if self.character.check_door_status(self.barrier_id, self.shut):
            # Move on now if the door is already in the desired state
            return self
        self.character.raise_arm()

    def move_door(self):
        """Open or close a door or window.

        :return: `None`.
        """
        self.character.move_door(self.barrier_id, self.shut)

    def lower_arm(self):
        """Make a character lower his arm after opening or closing a door or
        window.

        :return: `None`.
        """
        self.character.lower_arm()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False`.
        """
        return False

class OpenDoor(MoveDoor):
    """Command that makes a character open a door or window.

    :param barrier_id: The ID of the door or window.
    """
    def __init__(self, barrier_id):
        MoveDoor.__init__(self, barrier_id, False)

class ShutDoor(MoveDoor):
    """Command that makes a character close a door or window.

    :param barrier_id: The ID of the door or window.
    """
    def __init__(self, barrier_id):
        MoveDoor.__init__(self, barrier_id, True)

class WipeBoard(ComplexCommand):
    """Command that makes a character wipe a blackboard."""
    def __init__(self):
        ComplexCommand.__init__(self)
        self.column = 0
        self.blackboard = None

    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`walk`
        * :meth:`wipe`
        * :meth:`lower_arm`
        * :meth:`~ComplexCommand.done`
        """
        return ('walk', 'wipe', 'lower_arm', 'done')

    def walk(self):
        """Make a character walk to the next part of the blackboard that needs
        wiping. If the character hasn't started wiping yet, he is sent to the
        nearest edge of the blackboard.

        :return: A :class:`GoToXY` command to send the character to the
                 appropriate location.
        """
        self.character.wiping_board = True
        if self.column == 0:
            self.blackboard = self.character.get_blackboard()
            if self.character.x < self.blackboard.x - 2:
                x = self.blackboard.x - 2
            else:
                x = self.blackboard.right_x
        else:
            x = self.character.x + self.character.direction
        return GoToXY(x, self.character.y)

    def wipe(self):
        """Make a character raise his arm and wipe a bit of a blackboard.

        :return: `None`.
        """
        self.character.raise_arm()
        wipe_col = self.column if self.character.direction > 0 else self.blackboard.width - 1 - self.column
        self.character.wipe_board(wipe_col)

    def lower_arm(self):
        """Make a character lower his arm after wiping a bit of a blackboard.
        If there are any bits of the blackboard left to wipe, the command is
        restarted.

        :return: `None`.
        """
        self.column += 1
        self.character.lower_arm()
        if self.column < self.blackboard.width:
            # Repeat until the board is clean
            self.restart()
        else:
            self.character.wiping_board = False

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (blackboards should never be left partially wiped).
        """
        return False

class GoTo(Command):
    """Command that makes a character go to a location.

    :param location_id: The ID of the location to go to (may be `None`).
    :type destination: :class:`~pyskool.location.Location`
    :param destination: The location to go to (required if `location_id`
                        is `None`).
    :param go_one_step: `True` if this command should terminate after
                        sending the character one step towards the
                        destination.
    """
    def __init__(self, location_id, destination=None, go_one_step=False):
        self.location_id = location_id
        self.destination = destination
        self.go_one_step = go_one_step
        self.done = False

    def execute(self):
        """Make a character take the next step towards his destination.

        :return: `self` if the character has already reached his destination,
                 `None` otherwise.
        """
        if self.destination is None:
            self.destination = self.character.resolve_location_id(self.location_id)
            if self.destination is None:
                debug.log("Cannot resolve location ID '%s' for %s" % (self.location_id, self.character.name))
                return
        if (self.character.x, self.character.y) == (self.destination.x, self.destination.y) or self.done:
            return self
        if self.character.on_stairs():
            self.character.walk(True)
            return
        if self.character.is_sitting():
            self.character.get_up()
            return
        next_staircase = self.character.get_next_staircase(self.destination)
        if next_staircase:
            if self.character.y == next_staircase.bottom.y:
                next_x = next_staircase.bottom.x
            else:
                next_x = next_staircase.top.x
        else:
            next_x = self.destination.x
        if self.character.x < next_x:
            self.done = self.go_one_step
            return self.character.right()
        elif self.character.x > next_x:
            self.done = self.go_one_step
            return self.character.left()
        else:
            if next_staircase.contains(self.character):
                self.character.walk(True)
            else:
                self.character.turn()
        self.done = self.go_one_step

    def is_GoTo(self):
        """Return whether this command is one of the :class:`GoTo` commands.

        :return: `True`.
        """
        return True

class GoToRandomLocation(GoTo):
    """Command that makes a character go to a location chosen at random."""
    def __init__(self):
        GoTo.__init__(self, None)

    def execute(self):
        """Make a character start the journey towards a randomly chosen
        location.

        :return: A :class:`GoTo` command.
        """
        if self.destination is None:
            self.destination = Location(self.character.get_random_destination())
        return GoTo.execute(self)

class GoToXY(GoTo):
    """Command that makes a character go to a location specified by x- and
    y-coordinates.

    :param x: The x-coordinate of the location to go to.
    :param y: The y-coordinate of the location to go to.
    """
    def __init__(self, x, y):
        GoTo.__init__(self, None, Location((x, y)))

class GoTowardsXY(GoTo):
    """Command that makes a character take one step towards a location.

    :param x: The x-coordinate of the location to go towards.
    :param y: The y-coordinate of the location to go towards.
    """
    def __init__(self, x, y):
        GoTo.__init__(self, None, Location((x, y)), True)

class Restart(Command):
    """Command that restarts a character's command list."""
    def execute(self):
        """Restart a character's command list.

        :return: `self`
        """
        self.character.restart_command_list()
        return self

class FindSeat(Command):
    """Command that makes a character find a seat and sit down.

    :param go_to_back: `True` if the character should seek out the back seat,
                        `False` if he should find the nearest seat.
    :param move_along: `True` if the character should move along to the next
                        seat even if he's already standing beside one, `False`
                        otherwise.
    """
    def __init__(self, go_to_back=True, move_along=True):
        self.go_to_back = go_to_back
        self.move_along = move_along

    def execute(self):
        """Make a character find a seat, turn round if he's already beside one
        but facing the wrong way, or sit down.

        :return: `self` if the character sat down, `None` if he's beside a
                 seat but had to turn round, or a :class:`GoToXY` command to
                 send him to a seat.
        """
        next_chair, direction = self.character.get_next_chair(self.move_along, self.go_to_back)
        if next_chair:
            self.move_along = False
            if self.character.x == next_chair.x:
                if self.character.direction == direction:
                    self.character.sit()
                    return self
                self.character.turn()
            else:
                return GoToXY(next_chair.x, self.character.y)
        else:
            # We couldn't find a chair, so terminate this command; this is not
            # supposed to happen!
            return self

class MoveAboutUntil(Command):
    """Command that makes a character walk up and down until a signal is
    raised.

    :param signal: The signal to wait for.
    :param walkabout_range: The minimum and maximum distances to walk away from
                            the walkabout origin.
    """
    def __init__(self, signal, walkabout_range=(1, 7)):
        self.signal = signal
        self.walkabout_range = walkabout_range

    def execute(self):
        """Make a character walk up and down unless the signal has been raised.

        :return: `self` if the signal has been raised, or a :class:`WalkAround`
                 command.
        """
        if self.character.got_signal(self.signal):
            return self
        return WalkAround(1, self.walkabout_range)

class WalkAround(Command):
    """Command that makes a character walk up and down a given number of times.

    :param walkabouts: The number of times to walk up and down.
    :param walkabout_range: The minimum and maximum distances to walk away from
                            the walkabout origin.
    """
    def __init__(self, walkabouts, walkabout_range=(1, 7)):
        self.count = walkabouts
        self.walkabout_range = walkabout_range
        self.origin = None

    def execute(self):
        """Make a character walk up (away from the walkabout origin) or down
        (back to the walkabout origin). If the character is on a staircase,
        make him finish going up or down it first.

        :return: `self` if the designated number of walkabouts has been
                 performed, `None` if the character is on a staircase, or
                 a :class:`GoToXY` command.
        """
        if self.count == 0:
            return self
        # Cannot move about an x-coordinate on a staircase, so get off the
        # stairs first
        if self.character.on_stairs():
            self.character.walk(True)
            return
        if self.origin is None:
            self.origin = self.character.x
        if self.character.x == self.origin:
            return GoToXY(self.character.x - random.randint(*self.walkabout_range), self.character.y)
        self.count -= 1
        return GoToXY(self.origin, self.character.y)

class SitStill(Command):
    """Command that makes a character do nothing. It is used to make a
    character sit still during a lesson.
    """
    def execute(self):
        """Make a character do nothing.

        :return: `None`.
        """
        return

class GrassAndAnswerQuestions(Command):
    """Command that makes a character tell tales and answer the teacher's
    questions during a lesson. It is used by the swot.
    """
    def __init__(self):
        self.ready = False

    def execute(self):
        """Make a character tell a tale, wait for a teacher to ask a question,
        or answer a teacher's question.

        :return: `None` if the character should do nothing at the moment, or
                 an appropriate :class:`Command`.
        """
        if not self.character.is_sitting_on_chair():
            return FindSeat(False, False)
        self.character.keep_seat()
        if not self.ready:
            self.ready = True
            self.character.start_lesson()
        return self.character.next_swot_action()

class WaitUntil(Command):
    """Command that makes a character wait until a signal is raised.

    :param signal: The signal to wait for.
    """
    def __init__(self, signal):
        self.signal = signal

    def execute(self):
        """Make a character wait for a signal.

        :return: `self` if the signal has been raised, `None` otherwise.
        """
        if self.character.got_signal(self.signal):
            return self

class DoAssemblyDuty(Command):
    """Command that makes a character perform assembly duty. This involves
    checking whether Eric is present in the assembly hall, and chasing him down
    if he's absent.

    :param assembly_started: The signal that indicates assembly has started.
    :param assembly_finished: The signal that indicates assembly is finished.
    """
    def __init__(self, assembly_started, assembly_finished):
        self.assembly_started = assembly_started
        self.assembly_finished = assembly_finished
        self.fetched_eric = False

    def execute(self):
        """Make a character perform assembly duty. If the character has just
        successfully herded the absent Eric to the assembly hall, the
        character's command list is restarted (so that he returns to the back
        of the assembly hall and starts the Eric-watching process over again).

        :return: `self` if the character has just herded Eric back to the
                 assembly hall, or assembly has finished; `None` if it's not
                 time to start keeping an eye out for Eric yet, or Eric is
                 present; or a :class:`FetchEric` command.
        """
        if self.fetched_eric:
            self.character.restart_command_list()
            return self
        if self.character.got_signal(self.assembly_finished):
            return self
        if not self.character.got_signal(self.assembly_started):
            return
        if self.character.is_eric_absent():
            self.fetched_eric = True
            return FetchEric()

class StartAssemblyIfReady(Command):
    """Command that restarts a character's command list unless it's time to
    start assembly.

    :param signal: The signal to raise to indicate that assembly has started.
    """
    def __init__(self, signal):
        self.signal = signal

    def execute(self):
        """Restart a character's command list unless it's time to start
        assembly.

        :return: `self` if it's time to start assembly, `None` otherwise.
        """
        if self.character.is_time_to_start_lesson():
            self.character.set_home_room()
            self.character.signal(self.signal)
        else:
            self.character.restart_command_list()
        return self

class ConductAssembly(Command):
    """Command that makes a character conduct assembly. This involves
    delivering a detention message.
    """
    def __init__(self):
        self.spoken = False

    def execute(self):
        """Make a character deliver a detention message. After the message has
        been delivered, a signal is raised to indicate that assembly is
        finished.

        :return: `self` if the detention message has been delivered, or a
                 :class:`Say` command.
        """
        if self.spoken:
            self.character.unset_home_room()
            return self
        self.spoken = True
        return Say(self.character.get_assembly_message())

class StartLessonIfReady(Command):
    """Command that makes a character start a lesson if the time has come, or
    restarts the character's command list if it's still too early.

    :param signal: The signal to raise when starting the lesson.
    """
    def __init__(self, signal):
        self.signal = signal
        self.ready = False

    def execute(self):
        """Make a character start a lesson, or restart his command list if it's
        too early to start the lesson. If it's time to start the lesson, the
        character has a special safe secret question, and he can see the answer
        on a nearby blackboard, he will reveal his safe secret.

        :return: A :class:`TellKidsToSitDown` command if it's time to start the
                 lesson, `self` otherwise.
        """
        if not self.ready:
            if self.character.is_time_to_start_lesson():
                self.ready = True
                self.character.signal(self.signal)
                self.character.reveal_safe_secret(False)
                return TellKidsToSitDown()
            else:
                self.character.restart_command_list()
        return self

class StartDinnerIfReady(Command):
    """Command that makes a character start dinner if the time has come, or
    restarts the character's command list if it's still too early. It is used
    by teachers on dinner duty.
    """
    def execute(self):
        """Make a character start dinner, or restart his command list if it's
        too early to start dinner.

        :return: `self`
        """
        if self.character.is_time_to_start_lesson():
            self.character.set_home_room()
        else:
            self.character.restart_command_list()
        return self

class TellKidsToSitDown(Command):
    """Command that makes a character tell the kids to sit down."""
    def __init__(self):
        self.spoken = False

    def execute(self):
        """Make a character tell the kids to sit down.

        :return: A :class:`Say` command, or `self` if the character has
                 finished telling the kids to sit down.
        """
        if self.spoken:
            return self
        self.spoken = True
        return Say(self.character.get_sit_down_message())

class ConductClass(Command):
    """Command that makes a character conduct a class. It determines whether
    the character is teaching Eric, and passes control to a
    :class:`ConductClassWithEric` or :class:`ConductClassWithoutEric` command
    as appropriate.

    :param signal: The signal raised by the swot to indicate that he's ready to
                   start the lesson.
    :param qa_group: The Q&A group from which to choose questions and answers
                     for the teacher and the swot; if `None`, the Q&A group
                     will be chosen at random from those available each time a
                     question and answer is generated.
    """
    def __init__(self, signal=None, qa_group=None):
        self.signal = signal
        self.qa_group = qa_group

    def execute(self):
        """Make a character conduct a class.

        :return: A :class:`ConductClassWithoutEric` command if the character is
                 not teaching Eric; `None` if the character is teaching Eric
                 but the swot hasn't shown up yet; a
                 :class:`ConductClassWithEric` command otherwise.
        """
        if self.character.is_teaching_eric():
            if self.character.got_signal(self.signal):
                return ConductClassWithEric(self.qa_group)
        else:
            return ConductClassWithoutEric()

class ConductClassWithoutEric(Command):
    """Command that makes a character conduct a class without Eric. This
    involves wiping the board (if there is one in the room), optionally writing
    on the board, telling the kids what to do, and then pacing up and down
    until the bell rings.
    """
    def __init__(self):
        self.wiped_board = False
        self.walked_to_board = False
        self.wrote_on_board = False
        self.told_class = False

    def execute(self):
        """Make a character perform the next step in conducting this class.

        :return: A :class:`WipeBoard` command; a :class:`GoToXY` command to
                 make the character return to the middle of the board after
                 wiping it; a :class:`WriteOnBoard` command (possibly); a
                 :class:`TellClassWhatToDo` command; or a :class:`WalkUpOrDown`
                 command.
        """
        if self.character.get_blackboard():
            if not self.wiped_board:
                self.wiped_board = True
                return WipeBoard()
            if not self.walked_to_board:
                self.walked_to_board = True
                return GoToXY(self.character.x - self.character.get_blackboard_backtrack() * self.character.direction, self.character.y)
            if not self.wrote_on_board:
                self.wrote_on_board = True
                if self.character.will_write_on_board():
                    return WriteOnBoard(self.character.get_blackboard_message())
        if not self.told_class:
            self.told_class = True
            return TellClassWhatToDo()
        return WalkUpOrDown()

class TellClassWhatToDo(Command):
    """Command that makes a character tell a class what to do. It is used by
    teachers.
    """
    def __init__(self):
        self.done = False

    def execute(self):
        """Make a character tell the class what to do.

        :return: A :class:`Say` command, or `self` if the character has
                 finished telling the class what to do.
        """
        if self.done:
            return self
        self.done = True
        return Say(self.character.get_lesson_message())

class WalkUpOrDown(Command):
    """Command that makes a character walk up (away from an origin) or down
    (back to the origin).
    """
    def __init__(self):
        self.done = False

    def execute(self):
        """Make a character walk up or down.

        :return: A :class:`GoToXY` command, or `self` if the character is ready
                 to turn round.
        """
        if self.done:
            return self
        self.done = True
        return GoToXY(self.character.x - self.character.get_blackboard_pace_distance() * self.character.direction, self.character.y)

class WriteOnBoard(Command):
    """Command that makes a character write on a blackboard.

    :param message: The message to write on the blackboard.
    """
    def __init__(self, message):
        self.message = message
        self.index = 1
        self.arm_down = True

    def execute(self):
        """Make a character write the next letter of the message on a
        blackboard. The character's arm will be alternately raised or lowered
        while writing.

        :return: `self` if the character has finished writing, `None`
                 otherwise.
        """
        if not (self.message and self.character.get_blackboard()):
            return self
        if self.character.write_on_board(self.message, self.index):
            self.character.lower_arm()
            return self
        if self.arm_down:
            self.character.raise_arm()
        else:
            self.character.lower_arm()
        self.arm_down = not self.arm_down
        self.index += 1

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (a blackboard should not be left half-written on)
        """
        return False

class ConductClassWithEric(Command):
    """Command that makes a character conduct a class with Eric. This involves
    waiting until the swot shows up, listening to him while he tells tales and
    responding appropriately, wiping the board (if there is one in the room),
    optionally writing on the board, and finally either telling the kids what
    to do and pacing up and down until the bell rings, or starting a
    question-and-answer session with the swot. At various points in this
    process, the character will also respond to the swot's tales about Eric
    being missing.

    :param qa_group: The Q&A group from which to choose questions and answers
                     for the teacher and the swot; if `None`, the Q&A group
                     will be chosen at random from those available each time a
                     question and answer is generated.
    """
    def __init__(self, qa_group=None):
        self.joined = False
        self.qa_group = qa_group

    def execute(self):
        """Make a character perform the next required action while conducting
        the class.

        :return: `None` if the character should do nothing at the moment, or
                 an appropriate :class:`Command`.
        """
        if not self.joined:
            self.joined = True
            self.character.join_lesson(self.qa_group)
        return self.character.next_teacher_action()

class Say(Command):
    """Command that makes a character say something.

    :param words: The words to say.
    :param notify: `True` if the character who is listening should be notified
                    (as during a question-and-answer session between a teacher
                    and the swot), `False` otherwise.
    """
    def __init__(self, words, notify=False):
        self.words = words
        self.notify = notify
        self.shift = -4

    def execute(self):
        """Make a character utter the next bit of whatever he's saying. If the
        character has finished speaking, his speech bubble is removed, and any
        listeners are notified.

        :return: `self` if the character has finished speaking, `None`
                 otherwise.
        """
        if not self.words:
            return self
        if self.character.say(self.words, self.shift):
            self.character.remove_bubble()
            if self.notify:
                self.character.finished_speaking()
            return self
        self.shift += 1

    def finish(self):
        """Remove the character's speech bubble. This method is called if the
        command is removed from the command stack before exiting normally.
        """
        self.character.remove_bubble()

class Signal(Command):
    """Command that makes a character raise a signal.

    :param signal: The signal to raise.
    """
    def __init__(self, signal):
        self.signal = signal

    def execute(self):
        """Make a character raise a signal.

        :return: `self`.
        """
        self.character.signal(self.signal)
        return self

class Unsignal(Command):
    """Command that makes a character lower a signal.

    :param signal: The signal to lower.
    """
    def __init__(self, signal):
        self.signal = signal

    def execute(self):
        """Make a character lower a signal.

        :return: `self`.
        """
        self.character.unsignal(self.signal)
        return self

class SetControllingCommand(Command):
    """Command that sets a controlling command on a character's command list.
    See :meth:`CommandList.set_controlling_command` for more details.

    :param command_name: The name of the controlling command.
    :param params: The controlling command's initialisation parameters.
    """
    def __init__(self, command_name, *params):
        self.command_name = command_name
        self.params = params

    def execute(self):
        """Set the controlling command on a character's command list.

        :return: `self`.
        """
        command_class = get_command_class(self.command_name)
        self.character.set_controlling_command(command_class(*self.params))
        return self

class HitOrFireNowAndThen(Command):
    """Abstract command that makes a character check whether it's a good time
    to throw a punch or launch a catapult pellet, and act accordingly.
    """
    def ready(self):
        """Return whether now is a good time for this character to throw a
        punch or fire a catapult pellet. The answer will be `True` if all the
        following conditions are met:

        * The character is not on a staircase.
        * There are no adults nearby facing the character.
        * The character is standing upright.
        """
        if self.character.on_stairs() or self.character.get_nearby_adults():
            return False
        return self.character.is_standing()

    def execute(self):
        """Make a character start throwing a punch or launching a catapult
        pellet if conditions are favourable.

        :return: `self` if conditions are not favourable, or a :class:`Hit` or
                 :class:`FireCatapult` command.
        """
        if not self.ready():
            return self
        return self.get_command()

class FireNowAndThen(HitOrFireNowAndThen):
    """Command that makes a character check whether it's a good time to launch
    a catapult pellet, and act accordingly. This command is used as a
    controlling command (see :meth:`CommandList.set_controlling_command`).
    """
    def ready(self):
        """Return whether this character will fire a catapult pellet. The
        answer will be `True` if all the conditions described in
        :class:`HitOrFireNowAndThen.ready` are met, and also:

        * The character's x-coordinate is divisible by 4.
        * The character's catapult pellet is not currently airborne.
        * The character chooses to.
        """
        if not HitOrFireNowAndThen.ready(self):
            return False
        if self.character.x % 4 != 0:
            return False
        if self.character.pellet.is_visible():
            return False
        return self.character.will_fire_catapult()

    def get_command(self):
        """Returns the command that should be used to make a character fire his
        catapult.

        :return: A :class:`FireCatapult` command.
        """
        return FireCatapult()

class FireCatapult(ComplexCommand):
    """Command that makes a character fire a catapult."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`aim`
        * :meth:`fire`
        * :meth:`lower`
        * :meth:`~ComplexCommand.done`
        """
        return ('aim', 'fire', 'lower', 'done')

    def aim(self):
        """Make a character start or finish raising his catapult to eye level.

        :return: `False` if the character has yet to raise the catapult to eye
                 level, or `None` if he has raised it to eye level.
        """
        if self.character.is_raising_catapult():
            self.character.aim_catapult()
        else:
            self.character.raise_catapult()
            return False

    def fire(self):
        """Make a character launch a catapult pellet.

        :return: `None`.
        """
        self.character.fire_catapult()

    def lower(self):
        """Make a character start or finish lowering his catapult.

        :return: `False` if the character has not finished lowering his
                 catapult, or `None` if he has.
        """
        if self.character.is_lowering_catapult():
            self.character.complete_action()
        else:
            self.character.lower_catapult()
            return False

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (a catapult-firing character should finish what he's
                 started).
        """
        return False

class MovePellet(Command):
    """Command that controls a catapult pellet."""
    def __init__(self):
        self.count = 0
        self.x_inc = None
        self.y_inc = 0

    def execute(self):
        """Move a catapult pellet if it's currently airborne, remove it from
        sight if it's reached the end of its flight, or else do nothing. If the
        pellet is airborne and hits a wall, door, window, shield, cup, conker
        or head, appropriate action is taken.

        :return: `None`.
        """
        pellet = self.character
        if not pellet.is_visible():
            return
        if self.count <= 0:
            self.count = pellet.pellet_range
            self.x_inc = pellet.direction
            self.y_inc = 0
        self.count -= 1
        if self.count == 0 or pellet.barrier:
            self._end_flight()
            return
        if self.y_inc < 0 or self.count <= pellet.hit_zone:
            if pellet.hit_shield() or pellet.hit_cup() or pellet.hit_conker():
                self._end_flight()
                return
        if self.y_inc == 0 and self.count <= pellet.hit_zone:
            victim = pellet.get_victim()
            if victim:
                if victim.is_deckable():
                    victim.deck()
                    self._end_flight()
                    return
                if victim.is_adult() and victim.is_knocked_over():
                    self.x_inc = 0
                    self.y_inc = -1
                    self.count = 5
        pellet.x += self.x_inc
        pellet.y += self.y_inc

    def _end_flight(self):
        """End the flight of a pellet (that is, hide it from view)."""
        self.count = 0
        self.character.hide()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (a catapult pellet should not be stopped by the
                 bell).
        """
        return False

class FireWaterPistol(ComplexCommand):
    """Command that makes a character fire a water pistol."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`aim`
        * :meth:`fire`
        * :meth:`lower`
        * :meth:`~ComplexCommand.done`
        """
        return ('aim', 'fire', 'lower', 'done')

    def aim(self):
        """Make a character take out his water pistol and aim it.

        :return: `None`.
        """
        self.character.aim_water_pistol()

    def fire(self):
        """Make a character pull the trigger of his water pistol (thus
        releasing a jet of water or sherry).

        :return: `None`.
        """
        self.character.fire_water_pistol()

    def lower(self):
        """Make a character put his water pistol back in his pocket.

        :return: `None`.
        """
        self.character.complete_action()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False`.
        """
        return False

class DumpWaterPistol(ComplexCommand):
    """Command that makes Eric throw away his water pistol."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`dump_water_pistol`
        * :meth:`stand_up`
        """
        return ('dump_water_pistol', 'stand_up')

    def dump_water_pistol(self):
        """Make Eric drop his water pistol.

        :return: `None`.
        """
        self.character.dump_water_pistol()

    def stand_up(self):
        """Make Eric stand up straight again after dropping his water pistol.

        :return: `None`.
        """
        self.character.stand_up()
        return self

class MoveWater(Command):
    """Command that controls a stream of liquid (water or sherry) fired from a
    water pistol.
    """
    def __init__(self):
        self.phase = 0

    def execute(self):
        """Move a stream of water or sherry one phase further in its
        trajectory. If the liquid hits a cup, a plant or the floor on its
        journey, appropriate action is taken.

        :return: `None`.
        """
        water = self.character
        if not water.is_visible():
            return
        state, x_inc, y_inc, hit = water.phases[self.phase]
        if hit == 1 and water.hit_cup():
            return self._end_flight()
        if hit == 2 and water.hit_plant():
            return self._end_flight()
        if water.hit_floor():
            return self._end_flight()
        water.x += water.direction * x_inc
        water.y += y_inc
        water.animatory_state = state
        self.phase = min(self.phase + 1, len(water.phases) - 1)

    def _end_flight(self):
        """End the flight of the water or sherry (that is, hide it from view).
        """
        self.phase = 0
        self.character.hide()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (flying liquids are unstoppable).
        """
        return False

class DropStinkbomb(ComplexCommand):
    """Command that makes a character drop a stinkbomb."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`raise_arm`
        * :meth:`drop`
        * :meth:`lower`
        * :meth:`~ComplexCommand.done`
        """
        return ('raise_arm', 'drop', 'lower', 'done')

    def raise_arm(self):
        """Make a character raise his arm in preparation for dropping a
        stinkbomb.

        :return: `None`.
        """
        self.character.raise_arm()

    def drop(self):
        """Make a character drop a stinkbomb (thus creating a stinkbomb cloud).

        :return: `None`.
        """
        self.character.drop_stinkbomb()

    def lower(self):
        """Make a character lower his arm after dropping a stinkbomb.

        :return: `None`.
        """
        self.character.complete_action()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False`.
        """
        return False

class Stink(Command):
    """Command that controls a stinkbomb cloud.

    :param delay: The delay before the stinkbomb disappears.
    """
    def __init__(self, delay):
        self.delay = delay
        self._reset()

    def _reset(self):
        """Reset the command. This method is called after a stinkbomb cloud has
        dissipated, to prepare it for its next appearance.
        """
        self.count = self.delay

    def execute(self):
        """Animate a stinkbomb cloud (if it's visible).

        :return: `None`.
        """
        bomb = self.character
        if not bomb.is_visible():
            return
        self.count -= 1
        if self.count <= 0:
            self._reset()
            bomb.hide()
            return
        bomb.move_cloud()

class MoveDeskLid(Command):
    """Command that controls a desk lid.

    :param delay: The delay before an opened desk lid closes.
    """
    def __init__(self, delay):
        self.delay = delay
        self._reinitialise()

    def _reinitialise(self):
        """Reinitialise this command. This method is called after a desk lid
        has closed, to prepare it for its next appearance."""
        self.count = self.delay

    def execute(self):
        """Control a desk lid. If the desk lid is not raised, nothing happens.
        If the desk lid has just been raised, the contents of the desk (if any)
        are delivered to the lid-raiser.

        :return: `None`.
        """
        desk_lid = self.character
        if not desk_lid.is_visible():
            return
        if self.count >= self.delay:
            desk_lid.deliver_contents()
        self.count -= 1
        if self.count <= 0:
            self._reinitialise()
            desk_lid.hide()

class HitNowAndThen(HitOrFireNowAndThen):
    """Command that makes a character check whether it's a good time to throw a
    punch, and act accordingly. This command is used as a controlling command
    (see :meth:`CommandList.set_controlling_command`).
    """
    def ready(self):
        """Return whether this character will throw a punch. The answer will be
        `True` if all the conditions described in
        :meth:`HitOrFireNowAndThen.ready` are met, and also:

        * There is someone punchable in front of the character.
        * The character chooses to.
        """
        if HitOrFireNowAndThen.ready(self) and self.character.get_punchee(3):
            return self.character.will_hit()
        return False

    def get_command(self):
        """Returns the command that should be used to make a character throw a
        punch.

        :return: A :class:`Hit` command.
        """
        return Hit()

class Hit(ComplexCommand):
    """Command that makes a character throw a punch."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`aim`
        * :meth:`hit`
        * :meth:`lower`
        * :meth:`~ComplexCommand.done`
        """
        return ('aim', 'hit', 'lower', 'done')

    def aim(self):
        """Make a character start or finish raising his fist.

        :return: `None` if the character's fist is fully raised, `False`
                 otherwise.
        """
        if self.character.is_raising_fist():
            self.character.punch()
        else:
            self.character.raise_fist()
            return False

    def hit(self):
        """Make a character deck anyone unfortunate enough to come into contact
        with his raised fist.

        :return: `None`.
        """
        facing_character = self.character.get_punchee(2)
        if facing_character:
            facing_character.deck()

    def lower(self):
        """Make a character start or finish lowering his fist.

        :return: `None` if the character's fist is fully lowered, `False`
                 otherwise.
        """
        if self.character.is_lowering_fist():
            self.character.complete_action()
        else:
            self.character.lower_fist()
            return False

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False`.
        """
        return False

class Floored(Command):
    """Command that controls a character who has been knocked to the floor.

    :param count: The delay before the character should get up.
    """
    def __init__(self, count):
        self.count = count

    def execute(self):
        """Make a character remain on the floor, or get up if enough time has
        passed.

        :return: `self` if the character has got up and is ready to resume
                 normal service, `None` otherwise.
        """
        if self.character.is_standing():
            return self
        self.count -= 1
        if self.count < 0:
            self.character.stand_up()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (the bell cannot raise characters from the floor).
        """
        return False

class KnockedOver(Floored):
    """Command that controls an adult character who has been knocked over by a
    catapult pellet or conker.

    :param delay: The delay before the character rises.
    :param reprimand_delay: The delay before the character gives lines to
                            someone for knocking him over.
    :param sleep: Whether the character should remain unconscious for a while
                  (as when Albert is struck by a conker).
    """
    def __init__(self, delay, reprimand_delay, sleep):
        Floored.__init__(self, delay)
        self.delay = delay
        self.reprimand_delay = reprimand_delay
        self.sleep = sleep

    def execute(self):
        """Control an adult character who has been knocked over. If conditions
        are right and the character holds a safe combination letter, he will
        reveal it. If enough time has passed since being knocked over, the
        character will give lines if any suitable recipient is nearby.

        :return: `self` if the character has got up and is ready to resume
                 normal service, `None` otherwise.
        """
        if self.sleep:
            if self.character.is_time_to_wake():
                self.sleep = False
                self.count = 0
            else:
                # Make sure we check this character on every tick of the skool
                # clock so that he doesn't miss the wake-up time
                self.character.action_delay = -1
                return
        if Floored.execute(self) is self:
            return self
        if self.count == self.delay - 1:
            self.character.reveal_safe_secret(True)
        if self.count == self.delay - self.reprimand_delay:
            self.character.reprimand()

class WriteOnBoardUnless(Command):
    """Command that makes a character write on a blackboard unless a specified
    signal has been raised.

    :param signal: The signal to check before writing on the blackboard.
    """
    def __init__(self, signal):
        self.signal = signal
        self.wrote_on_board = False

    def execute(self):
        """Make a character write on a blackboard unless a signal has been
        raised.

        :return: `self` if the signal has been raised, or the blackboard is
                 dirty, or the character has finished writing on the
                 blackboard; a :class:`WriteOnBoard` command otherwise.
        """
        if not self.character.room:
            return self
        if self.character.got_signal(self.signal) or self.character.room.blackboard_dirty():
            return self
        if self.wrote_on_board:
            return self
        self.wrote_on_board = True
        return WriteOnBoard(self.character.get_blackboard_message())

class SetRestartPoint(Command):
    """Command that makes the next command in a character's command list be
    regarded as the first (for the purposes of a restart).
    """
    def execute(self):
        """Make the next command in a character's command list be regarded as
        the first (for the purposes of a restart).

        :return: `self`.
        """
        self.character.set_restart_point()
        return self

class JumpIfShut(Command):
    """Command that jumps forwards or backwards in a character's command list
    if a specified door or window is shut.

    :param door_id: The ID of the door or window to check.
    :type offset: number
    :param offset: The offset by which to jump in the command list.
    """
    def __init__(self, door_id, offset):
        self.door_id = door_id
        self.offset = offset

    def execute(self):
        """Jump forwards or backwards in a character's command list if a
        specified door or window is shut.

        :return: `self`.
        """
        self.character.jump_if_shut(self.door_id, self.offset)
        return self

class JumpIfOpen(Command):
    """Command that jumps forwards or backwards in a character's command list
    if a specified door or window is open.

    :param door_id: The ID of the door or window to check.
    :type offset: number
    :param offset: The offset by which to jump in the command list.
    """
    def __init__(self, door_id, offset):
        self.door_id = door_id
        self.offset = offset

    def execute(self):
        """Jump forwards or backwards in a character's command list if a
        specified door or window is open.

        :return: `self`.
        """
        self.character.jump_if_open(self.door_id, self.offset)
        return self

class WalkFast(Command):
    """Command that makes a character walk fast (as kids do half the time, and
    teachers do when chasing Eric). This command is used as a controlling
    command (see :meth:`CommandList.set_controlling_command`).
    """
    def execute(self):
        """Ensure that a character starts or continues to walk fast.

        :return: `self`.
        """
        self.character.go_fast()
        return self

    def finish(self):
        """Trigger a speed change for the character so that he no longer runs
        continuously.
        """
        self.character.trigger_speed_change()

class StalkAndHit(HitNowAndThen):
    """Command that makes a character seek out another character while throwing
    occasional punches. This command is used as a controlling command (see
    :meth:`CommandList.set_controlling_command`).

    :param character_id: The ID of the character to stalk.
    """
    def __init__(self, character_id):
        self.character_id = character_id

    def execute(self):
        """Make a character proceed one step further towards whoever he's
        stalking, and consider throwing a punch while he's at it.

        :return: A :class:`HitNowAndThen` command.
        """
        self.character.stalk(self.character_id)
        return HitNowAndThen.execute(self)

class WaitAtDoor(Command):
    """Command that makes a character wait at a door until everyone is on the
    correct side of it (that is, boys on the boys' side, girls on the girls'
    side).

    :param door_id: The ID of the door to wait at.
    """
    def __init__(self, door_id):
        self.door_id = door_id

    def execute(self):
        """Make a character wait at a door until everyone is on the correct
        side of it.

        :return: `self` if everyone is on the correct side of the door,
                 `None` otherwise.
        """
        if self.character.wait_at_door(self.door_id):
            return self

class Jump(ComplexCommand):
    """Command that makes a character jump."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`up`
        * :meth:`down`
        * :meth:`~ComplexCommand.done`
        """
        return ('up', 'down', 'done')

    def up(self):
        """Make a character jump into the air.

        :return: `None`.
        """
        self.character.jump()

    def down(self):
        """Make a character return to the floor after jumping.

        :return: `None`.
        """
        self.character.descend()

class Write(Command):
    """Command that controls Eric while he's writing on a blackboard."""
    def __init__(self):
        self.finished = False

    def execute(self):
        """Control Eric while he's writing on a blackboard.

        :return: `self` if Eric has finished writing on the blackboard,
                 `None` otherwise.
        """
        if self.finished:
            self.character.lower_arm()
            return self
        self.finished = self.character.write()

class FindEric(Command):
    """Command that makes a character go and find Eric."""
    def execute(self):
        """Make a character take the next step in the search for Eric. The
        skool clock is stopped to ensure that the character has enough time to
        find him. When Eric is found, he is frozen until the character decides
        to unfreeze him.

        :return: `self` if Eric has been found and frozen, `None` if Eric has
                 been found but cannot be frozen at the moment, or a
                 :class:`GoTowardsXY` command.
        """
        self.character.stop_clock()
        self.character.go_fast()
        if self.character.is_beside_eric():
            if self.character.freeze_eric():
                self.character.trigger_speed_change()
                return self
            return
        return GoTowardsXY(*self.character.get_location_of_eric())

class Freeze(Command):
    """Command that controls Eric while he's frozen (as by the
    :class:`FindEric` command).
    """
    def execute(self):
        """Control Eric while he's frozen. Each time this method is called, a
        check is made whether Eric has acknowledged understanding of the
        message being delivered to him (see :class:`TellEricAndWait`).

        :return: `None`.
        """
        self.character.check_understanding()

class TellEric(Command):
    """Command that makes a character say something to Eric.

    :param message: The message to give to Eric.
    """
    def __init__(self, message):
        self.told_eric = False
        self.message = message

    def execute(self):
        """Make a character say something to Eric. When the character has
        finished speaking, Eric will be unfrozen.

        :return: `self` if the character has finished speaking, or a
                 :class:`Say` command.
        """
        if self.told_eric:
            self.character.unfreeze_eric()
            return self
        self.told_eric = True
        return Say(self.character.expand_names(self.message))

class TellEricAndWait(Command):
    """Command that makes a character say something to Eric, and wait for a
    response.

    :param message: The message to give to Eric.
    """
    def __init__(self, message):
        self.told_eric = 0
        self.delay = None
        self.message = message

    def execute(self):
        """Make a character say something to Eric, and then wait for a
        response. When Eric has responded, he will be unfrozen. If Eric does
        not respond within a certain period, the character will repeat the
        message and wait again.

        :return: `self` if Eric has responded, `None` if the character is
                 waiting for Eric to respond, or a :class:`Say` command.
        """
        if self.told_eric == 0:
            self.told_eric = 1
            self.delay = self.character.get_tell_eric_delay()
            return Say(self.character.expand_names(self.message))
        if self.character.eric_understood():
            self.character.unfreeze_eric()
            return self
        self.delay -= 1
        if self.delay < 0:
            self.delay = self.character.get_tell_eric_delay()
            self.told_eric = 0

class SetClock(Command):
    """Command that makes a character set the skool clock to a specified time.

    :type ticks: number
    :param ticks: The time to set the clock to (remaining ticks till the bell
                  rings).
    """
    def __init__(self, ticks):
        self.ticks = ticks

    def execute(self):
        """Make a character set the skool clock.

        :return: `self`.
        """
        self.character.start_clock(self.ticks)
        return self

class CheckIfTouchingEric(Command):
    """Command that checks whether a character is touching Eric. This command
    is used by Angelface when he has mumps.

    :param eric_knows_signal: The signal used to indicate that Eric has been
                              told to avoid the character who has mumps.
    :param eric_has_mumps_signal: The signal to use to indicate that Eric has
                                  mumps.
    """
    def __init__(self, eric_knows_signal, eric_has_mumps_signal):
        self.eric_knows_signal = eric_knows_signal
        self.eric_has_mumps_signal = eric_has_mumps_signal

    def execute(self):
        """Make a character check whether he's touching Eric (and has therefore
        transmitted his disease). If Eric has been informed of the character's
        condition, and the character is touching Eric, the appropriate signal
        is raised to indicate that Eric has mumps.

        :return: `self`.
        """
        if self.character.got_signal(self.eric_knows_signal) and self.character.is_touching_eric():
            self.character.signal(self.eric_has_mumps_signal)
        return self

class EndGame(Command):
    """Command that ends the game. May be used by any character."""
    def execute(self):
        """Make a character end the game.

        :return: `None`.
        """
        self.character.end_game()

class AddLines(Command):
    """Command that adds lines to Eric's total. May be used by any character.

    :type lines: number
    :param lines: The lines to add to Eric's total.
    """
    def __init__(self, lines):
        self.lines = lines

    def execute(self):
        """Make a character add lines to Eric's total.

        :return: `self`.
        """
        self.character.add_lines(self.lines)
        return self

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False`.
        """
        return False

class FetchEric(Command):
    """Command that makes a character find and hover around Eric until he goes
    to wherever he should be.
    """
    def execute(self):
        """Make a character take the next step in the search for Eric.

        :return: `self` if Eric is where he should be, or is due to be
                 expelled; `None` if the character is already beside Eric; or
                 a :class:`GoTowardsXY` command.
        """
        self.character.go_fast()
        if not self.character.is_eric_absent() or self.character.is_eric_expelled():
            self.character.trigger_speed_change()
            return self
        if not self.character.is_beside_eric():
            return GoTowardsXY(*self.character.get_location_of_eric())
        if not self.character.is_facing_eric():
            self.character.turn()

class FindEricIfMissing(Command):
    """Command that makes a character start looking for Eric if he's not where
    he should be.
    """
    def execute(self):
        """Make a character check whether Eric is where he should be, and go
        looking for him if not.

        :return: `self` if Eric is where he should be, or a :class:`FetchEric`
                 command.
        """
        if not self.character.is_eric_expelled() and self.character.is_eric_absent():
            return FetchEric()
        return self

class TripPeopleUp(Command):
    """Command that makes a character trip people up while running towards his
    destination. This command is used as a controlling command (see
    :meth:`CommandList.set_controlling_command`).
    """
    def execute(self):
        """Make a character start or continue running, and trip up anyone in
        his path.

        :return: `self`.
        """
        self.character.go_fast()
        self.character.trip_people_up()
        return self

class Follow(Command):
    """Command that makes a character follow another character.

    :param character_id: The ID of the character to follow.
    """
    def __init__(self, character_id):
        self.target_id = character_id
        self.done = False

    def execute(self):
        """Make a character go to the same destination as another character.

        :return: `self` if the destination has been reached, or a :class:`GoTo`
                 command.
        """
        if self.done:
            return self
        self.done = True
        return GoTo(None, self.character.get_destination(self.target_id))

class MoveMouse(Command):
    """Command that controls a mouse.

    :type hide_range: 2-tuple
    :param hide_range: Minimum and maximum delays before the mouse comes out of
                       hiding.
    :type sprints: 2-tuple
    :param sprints: Minimum and maximum number of sprints the mouse will make
                    before hiding.
    :type sprint_range: 2-tuple
    :param sprint_range: Minimum and maximum distances of a sprint.
    :type life_range: 2-tuple
    :param life_range: Minimum and maximum number of sprint sessions the mouse
                       will engage in before dying (if released by Eric).
    """
    def __init__(self, hide_range, sprints, sprint_range, life_range):
        self.hide_range = hide_range
        self.sprints = sprints
        self.sprint_range = sprint_range
        self.life_range = life_range
        self._reset_sprints()
        self.hide_x = -1
        self.hide_delay = None
        self.life = random.randint(*self.life_range)

    def _reset_sprints(self):
        """Reset the number of sprints the mouse will perform before hiding."""
        self.sprint_count = random.randint(*self.sprints)
        self._reset_sprint_distance()

    def _reset_sprint_distance(self):
        """Reset the distance the mouse will travel on the next sprint."""
        self.sprint_distance = random.randint(*self.sprint_range)

    def execute(self):
        """Control a mouse. The pattern of movements of a mouse is as follows:

          1. Sprint up and down a few times.
          2. Hide for a bit.
          3. Go to 1, or die.

        :return: `None`.
        """
        mouse = self.character
        if self.hide_x >= 0:
            if self.hide_delay > 0:
                self.hide_delay -= 1
                return
            if not mouse.immortal:
                self.life -= 1
                if self.life <= 0:
                    mouse.die()
                    return
            mouse.x = self.hide_x
            self.hide_x = -1
            self._reset_sprints()
        elif self.sprint_distance > 0:
            self.sprint_distance -= 1
            self._move()
        elif self.sprint_count > 0:
            self.sprint_count -= 1
            self._reset_sprint_distance()
            mouse.direction = random.choice((-1, 1))
            self._move()
        else:
            self.hide_x = mouse.x
            self.hide_delay = random.randint(*self.hide_range)
            mouse.hide()

    def _move(self):
        """Make a mouse move forwards (or backwards if faced by a wall, a
        closed door, or a staircase) and scare any musophobes in the vicinity.
        """
        mouse = self.character
        if mouse.is_blocked():
            mouse.turn()
        mouse.x += mouse.direction
        mouse.scare_people()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (mice do not care about the bell).
        """
        return False

class EvadeMouse(Command):
    """Command that makes a character stand on a chair or start jumping.

    :param delay: The delay before the character will get off a chair or stop
                  jumping.
    """
    def __init__(self, delay):
        self.count = delay
        self.in_the_air = False
        self.on_a_chair = False
        self.old_as = None

    def execute(self):
        """Make a character:

        1. stand or remain standing on a chair, or
        2. start or continue jumping, or
        3. finish either one of these activities (after a certain time).

        :return: `self` if the character has finished standing on a chair or
                 jumping, `None` otherwise.
        """
        if self.old_as is None:
            self.old_as = self.character.animatory_state
            if self.character.is_sitting():
                self.character.get_up()
                return
        self.count -= 1
        if self.count <= 0:
            if self.in_the_air or self.on_a_chair:
                self.character.y += 1
                self.in_the_air = self.on_a_chair = False
                return
            self.character.animatory_state = self.old_as
            self.character.trigger_speed_change()
            return self
        self.character.go_slow()
        if self.in_the_air:
            self.character.y += 1
            self.in_the_air = False
        elif not self.on_a_chair:
            if self.character.chair(False):
                self.on_a_chair = True
            self.character.y -= 1
            self.in_the_air = not self.on_a_chair

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (a musophobe must not be distracted while evading a
                 mouse).
        """
        return False

class MoveFrog(Command):
    """Command that controls a frog.

    :param p_hop: Probability that the frog will keep still if Eric is not
                  nearby.
    :param p_turn_round: Probability that the frog will turn round.
    :param p_short_hop: Probability that the frog will attempt a short hop
                        (instead of a long hop) if not turning round.
    """
    def __init__(self, p_hop, p_turn_round, p_short_hop):
        self.p_hop = p_hop
        self.p_turn_round = p_turn_round
        self.p_short_hop = p_short_hop

    def execute(self):
        """Control a frog.

        :return: A :class:`Hop` command, or `None` if the frog decides not to
                 move.
        """
        frog = self.character
        if frog.trapped or not frog.is_visible():
            return
        if frog.falling:
            if frog.check_heads():
                frog.bounce_off_head()
            else:
                frog.y += 1
                if frog.get_floor():
                    frog.falling = False
                    frog.sit()
            return
        if not frog.is_eric_nearby() and random.random() < self.p_hop:
            return
        if random.random() < self.p_turn_round:
            phases = frog.turn_round
        elif random.random() < self.p_short_hop:
            phases = frog.turn_round if frog.is_blocked(1) else frog.short_hop
        else:
            phases = frog.turn_round if frog.is_blocked(3) else frog.long_hop
        return Hop(phases)

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (frogs do not care about the bell).
        """
        return False

class Hop(Command):
    """Command that controls a frog while it's hopping.

    :param phases: The phases of animation to use for the hop.
    """
    def __init__(self, phases):
        self.phases = phases
        self.index = 0

    def execute(self):
        """Move a frog to the next phase of animation in the hop.

        :return: `self` if the hop is finished, or `None`.
        """
        frog = self.character
        if self.index >= len(self.phases):
            return self
        state, x_inc, dir_change = self.phases[self.index]
        frog.animatory_state = state
        frog.x += x_inc * frog.direction
        frog.direction *= dir_change
        self.index += 1

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False`.
        """
        return False

class Catch(ComplexCommand):
    """Command that makes Eric catch a mouse or frog (if one is at hand)."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`catch_animal`
        * :meth:`stand_up`
        """
        return ('catch_animal', 'stand_up')

    def catch_animal(self):
        """Make Eric catch a mouse or frog if one is at the location of his
        hand.

        :return: `None`.
        """
        self.character.catch_animal()

    def stand_up(self):
        """Make Eric stand up straight after bending over to catch a mouse or
        frog.

        :return: `self`.
        """
        self.character.stand_up()
        return self

class ReleaseMice(ComplexCommand):
    """Command that makes Eric release some mice."""
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`release_mice`
        * :meth:`stand_up`
        """
        return ('release_mice', 'stand_up')

    def release_mice(self):
        """Make Eric release some mice.

        :return: `None`.
        """
        self.character.release_mice()

    def stand_up(self):
        """Make Eric stand up straight after bending over to release some mice.

        :return: `self`.
        """
        self.character.stand_up()
        return self

class Grow(Command):
    """Command that controls a plant.

    :param half: The delay between being watered and appearing at half-height.
    :param full: The delay between being watered and growing to full height.
    :param die: The delay between being watered and dying.
    """
    def __init__(self, half, full, die):
        self.half = half
        self.full = full
        self.die = die
        self.count = 0

    def execute(self):
        """Control a plant. If the plant has recently been watered, it will
        grow to full height and then die (disappear).

        :return: `None`.
        """
        plant = self.character
        if not plant.growing:
            return
        self.count += 1
        if self.count == self.half:
            plant.appear()
        elif self.count == self.full:
            plant.finish_growing()
        elif self.count >= self.die:
            plant.die()
            self.count = 0

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (plants do not care about the bell).
        """
        return False

class Fall(Command):
    """Command that controls a falling object (a conker or a drop of water or
    sherry).
    """
    def execute(self):
        """Control an object that may be falling. If the object is not falling,
        do nothing; otherwise make it fall a bit, taking appropriate action if
        it hits the floor or a person's head.

        :return: `None`.
        """
        thing = self.character
        if not thing.is_visible():
            return
        if thing.floor or thing.hit_victim():
            thing.hide()
        thing.y += 1

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (falling objects do not care about the bell).
        """
        return False

class MoveBike(Command):
    """Command that controls a bike when Eric's not sitting on the saddle."""
    def execute(self):
        """Control a bike when Eric's not sitting on the saddle. If the bike is
        resting on the floor or is not yet visible, do nothing; otherwise move
        the bike forwards.

        :return: `None`.
        """
        bike = self.character
        if bike.momentum <= 0 or not bike.is_visible():
            return
        bike.wheel()
        if bike.momentum <= 0:
            bike.fall()

    def is_interruptible(self):
        """Return whether this command is interruptible.

        :return: `False` (the bike does not care about the bell).
        """
        return False

class RideBike(Command):
    """Command that controls Eric while he's on a bike.

    :param bike: The bike Eric's riding.
    """
    def __init__(self, bike):
        self.bike = bike
        bike.prepare()

    def execute(self):
        """Control Eric while he's on a bike. Keep the bike moving if Eric
        pedals, or carry Eric along with the bike if he's standing on the
        saddle.

        :return: `self` if Eric has dismounted; a :class:`JumpOffSaddle`
                 command if Eric jumped while standing on the saddle; a
                 :class:`Flight` command if Eric hit the skool gate while
                 standing on the saddle; a :class:`FallToFloor` command if the
                 bike ran out of momentum; or `None` otherwise.
        """
        self.character.walk_delay = self.bike.move_delay
        self.character.check_bike_keys()
        barrier = self.character.hit_barrier(self.bike)
        if barrier:
            self.bike.momentum = 0
        elif self.character.pedalled():
            self.bike.pedal()
            return
        elif self.character.dismounted():
            self.character.stand_up()
            self.bike.start_wheeling(self.character)
            self.character.dismount()
            return self
        elif self.character.sitting_on_saddle:
            if self.character.stood_on_saddle():
                self.bike.start_wheeling(self.character)
                self.character.stand_on_saddle()
        elif self.character.got_back_on_saddle():
            self.character.get_back_on_saddle()
            self.bike.hide()
        elif self.character.jumped_off_saddle():
            self.character.dismount()
            return JumpOffSaddle()
        else:
            # Eric is standing on the saddle of the bike; move him with it
            self.character.x += self.character.direction
        self.bike.momentum -= 1
        if self.bike.momentum <= 0:
            self.character.dismount()
            if self.character.sitting_on_saddle:
                self.bike.fall(self.character)
            else:
                self.bike.fall()
                if barrier and barrier.fly_phases:
                    return Flight(barrier.fly_phases)
            return FallToFloor()

class FallToFloor(Command):
    """Command that controls Eric's descent to the floor (as from a bike that
    has run out of momentum, or a plant that has died).
    """
    def execute(self):
        """Make Eric fall. If he has reached the floor, he will assume a
        sitting position.

        :return: `self` if Eric has hit the floor, or `None` if he's still
                 falling.
        """
        if self.character.floor:
            self.character.fall_to_floor()
            return self
        self.character.y += 1

class Flight(Command):
    """Command that controls Eric's flight through a designated sequence of
    locations (relative to the starting point) and animatory states.

    :param phases: The phases of animation to proceed through.
    :param command_list_id: The ID of the command list Mr Wacker should switch
                            to when Eric hits the ground; if not blank, Eric
                            will be paralysed when he hits the ground.
    """
    def __init__(self, phases, command_list_id=None):
        self.index = 0
        self.phases = phases
        self.command_list_id = command_list_id

    def execute(self):
        """Move Eric to the next location and phase of animation in the
        flight sequence.

        :return: `self` if Eric has landed safely; a :class:`Freeze` command if
                 Eric has landed but is now immobilised (as when falling from a
                 great height); or `None` otherwise.
        """
        if self.index < len(self.phases):
            x_inc, y_inc, state = self.phases[self.index]
            self.index += 1
            self.character.fly(x_inc, y_inc)
            self.character.animatory_state = state
            if self.index == len(self.phases):
                self.character.end_flight()
            return
        if self.command_list_id:
            self.character.paralyse(self.command_list_id)
            return Freeze()
        return self

class JumpOffSaddle(ComplexCommand):
    """Command that controls Eric after he's jumped off the saddle of the bike.
    """
    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`rise`
        * :meth:`reach`
        * :meth:`check_cup`
        * :meth:`fall`
        * :meth:`~ComplexCommand.done`
        """
        return ('rise', 'reach', 'check_cup', 'fall', 'done')

    def rise(self):
        """Make Eric rise off the bike saddle.

        :return: `None`.
        """
        self.character.y -= 1

    def reach(self):
        """Make Eric rise again and raise his arm (to reach for a cup).

        :return: `None`.
        """
        self.character.y -= 1
        self.character.raise_arm()

    def check_cup(self):
        """Place the frog in a cup (if Eric has it and has reached a cup).

        :return: `None`
        """
        self.character.check_cup()
        self.character.sit_on_floor()

    def fall(self):
        """Guide Eric back to the floor after jumping off the saddle of the
        bike.

        :return: `False` if Eric has not reached the floor yet, or `None`
                 otherwise.
        """
        self.character.y += 1
        if self.character.landed():
            self.character.fall_to_floor()
            return
        return False

class Kiss(ComplexCommand):
    """Command that controls Eric while he kisses (or attempts to kiss) another
    character.
    """
    def __init__(self):
        ComplexCommand.__init__(self)
        self.kissee = None

    def get_commands(self):
        """Return the list of steps (methods) to execute for this complex
        command. The steps are:

        * :meth:`start_kiss`
        * :meth:`finish_kiss`
        * :meth:`~ComplexCommand.done`
        """
        return ('start_kiss', 'finish_kiss', 'done')

    def start_kiss(self):
        """Control Eric as he begins an attempt to kiss someone. If there is no
        one within kissing range in front of Eric, he will move midstride. If
        there is someone kissable within kissing range, they will either accept
        the kiss or slap him.

        :return: `None`.
        """
        self.kissee = self.character.kissee()
        if self.kissee:
            self.kissee.pause()
            if self.kissee.will_kiss_eric():
                self.character.x += self.character.direction
                self.character.hide()
                self.kissee.kiss_eric()
            else:
                self.kissee.raise_arm()
        else:
            self.character.walk()
            self.character.walk_delay = 4

    def finish_kiss(self):
        """Control Eric as he finishes a kiss or attempted kiss. If there was
        no one within kissing range in front of Eric, he will return from the
        midstride position. If there was someone kissable within kissing range,
        they will either finish the kiss with Eric (if they accepted it) or
        deck him (if they decided to slap him instead).

        :return: `None`.
        """
        if self.kissee:
            if self.kissee.is_kissing_eric():
                self.character.kiss()
                self.character.unhide()
                self.kissee.finish_kiss()
            else:
                self.kissee.lower_arm()
                self.character.deck()
            self.kissee.resume()
        else:
            self.character.stand_up()

class Pause(Command):
    """Command used to occupy a character while they are responding to an
    attempted kiss from Eric.
    """
    def execute(self):
        """Occupy a character while they are responding to an attempted kiss
        from Eric. The character's animation is controlled by the :class:`Kiss`
        command while this command is in effect.

        :return: `self` if the character has finished responding to the kiss,
                 or `None` if they are still occupied.
        """
        if not self.character.paused:
            return self

class WatchForEric(Command):
    """Command that makes a character keep an eye out for Eric, and alert
    someone if they spot him trying to escape from skool. This command is used
    as a controlling command (see :meth:`CommandList.set_controlling_command`).

    :param alertee_id: The ID of the character to alert.
    :param command_list_id: The ID of the command list the alerted character
                            should use.
    :param alert_message: The message to scream if Eric is spotted trying to
                          escape.
    :param escape_x: The x-coordinate beyond which Eric should be regarded as
                     trying to escape.
    :param danger_zone: The minimum and maximum distance to the left of the
                        watcher that Eric must be for him to raise the alarm.
    """
    def __init__(self, alertee_id, command_list_id, alert_message, escape_x, danger_zone):
        self.alertee_id = alertee_id
        self.command_list_id = command_list_id
        self.alert_message = alert_message
        self.escape_x = escape_x
        self.danger_zone = danger_zone

    def execute(self):
        """Make a character check whether Eric is trying to escape from skool,
        and take appropriate action if he is.

        :return: A :class:`StopEric` command if Eric is spotted trying to
                 escape, or `self` otherwise.
        """
        if self.character.should_stop_eric(self.escape_x, self.danger_zone):
            self.character.raise_arm()
            self.character.stop_eric = True
            return StopEric(self.alertee_id, self.command_list_id, self.alert_message, self.escape_x, self.danger_zone)
        return self

class StopEric(Command):
    """Command that makes a character try to stop Eric escaping from skool, and
    alert whoever should be alerted.

    :param alertee_id: The ID of the character to alert.
    :param command_list_id: The ID of the command list the alerted character
                            should use.
    :param alert_message: The alert message to scream.
    :param escape_x: The x-coordinate beyond which Eric should be regarded as
                     trying to escape.
    :param danger_zone: The minimum and maximum distance to the left of the
                        watcher that Eric must be for him to raise the alarm.
    """
    def __init__(self, alertee_id, command_list_id, alert_message, escape_x, danger_zone):
        self.raised_alarm = False
        self.alertee_id = alertee_id
        self.command_list_id = command_list_id
        self.alert_message = alert_message
        self.escape_x = escape_x
        self.danger_zone = danger_zone

    def execute(self):
        """Make a character raise the alarm (if he hasn't already) that Eric is
        trying to escape, and continue trying to stop Eric if need be.

        :return: `self` if the character has deemed it no longer necessary to
                 try and stop Eric escaping, or `None` otherwise.
        """
        if not self.raised_alarm:
            self.raised_alarm = True
            self.character.raise_alarm(self.alert_message, self.alertee_id, self.command_list_id)
        if not self.character.should_stop_eric(self.escape_x, self.danger_zone):
            self.character.lower_arm()
            self.character.stop_eric = False
            return self

class ShadowEric(Command):
    """Command that makes a character run after Eric and then hover around him
    until the bell rings."""
    def execute(self):
        """Make a character take the next step in the search for Eric, or
        remain by his side.

        :return: A :class:`GoTowardsXY` command if the character hasn't found
                 Eric yet, or `None` if the character is already by Eric's
                 side.
        """
        self.character.go_fast()
        if not self.character.is_beside_eric():
            return GoTowardsXY(*self.character.get_location_of_eric())
        if not self.character.is_facing_eric():
            self.character.turn()

class SetSubcommand(Command):
    """Command that sets a subcommand on a character's command list. See
    :meth:`CommandList.set_controlling_command` for more details.

    :param command_name: The name of the subcommand.
    :param args: The subcommand's parameters.
    """
    def __init__(self, command_name, *args):
        self.command_name = command_name
        self.args = args

    def execute(self):
        """Set a subcommand on a character's command list.

        :return: `self`.
        """
        self.character.set_subcommand(self.command_name, self.args)
        return self

class MonitorEric(Command):
    """Command that makes a character keep an eye out for Eric, and act
    appropriately if he's spotted. It is used by Miss Take to make her chase
    Eric out of the girls' skool if she spots him there when it's not
    playtime. This command is used as a subcommand (see
    :meth:`CommandList.set_subcommand`).

    :param command_list_id: The ID of the command list to execute if Eric is
                            spotted.
    :param chase_x: The x-coordinate beyond which Eric must be for the monitor
                    to start chasing Eric.
    """
    def __init__(self, command_list_id, chase_x):
        self.command_list_id = command_list_id
        self.chase_x = chase_x

    def execute(self):
        """Make a character check whether they can see Eric in the girls' skool
        during a non-playtime period, and switch to an appropriate command list
        if so.

        :return: `self`.
        """
        if self.character.should_chase_eric(self.chase_x):
            self.character.change_command_list(self.command_list_id)
        return self

class ChaseEricOut(Command):
    """Command that makes a character chase Eric up to the girls' side of the
    skool gate. It is used by Miss Take if she spots him in the girls' skool
    when it's not playtime.

    :param min_x: The x-coordinate at which the character should stop chasing
                  Eric, and stand on guard.
    """
    def __init__(self, min_x):
        self.min_x = min_x

    def execute(self):
        """Make a character take the next step while chasing Eric, or remain by
        his side if already there.

        :return: A :class:`GoTowardsXY` command if the character hasn't caught
                 up with Eric yet, or `None` if the character is already by
                 Eric's side.
        """
        self.character.go_fast()
        if self.character.x >= self.min_x:
            if not self.character.is_beside_eric():
                return GoTowardsXY(*self.character.get_location_of_eric())
            if not self.character.is_facing_eric():
                self.character.turn()
