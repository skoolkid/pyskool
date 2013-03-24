# -*- coding: utf-8 -*-

# Copyright 2010 Richard Dymond (rjdymond@gmail.com)
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

ADD_LINES = 'AddLines'
CHASE_ERIC_OUT = 'ChaseEricOut'
CHECK_IF_TOUCHING_ERIC = 'CheckIfTouchingEric'
CONDUCT_ASSEMBLY = 'ConductAssembly'
CONDUCT_CLASS = 'ConductClass'
DO_ASSEMBLY_DUTY = 'DoAssemblyDuty'
END_GAME = 'EndGame'
FALL = 'Fall'
FIND_ERIC = 'FindEric'
FIND_ERIC_IF_MISSING = 'FindEricIfMissing'
FIND_SEAT = 'FindSeat'
FIRE_NOW_AND_THEN = 'FireNowAndThen'
FOLLOW = 'Follow'
GO_TO = 'GoTo'
GO_TO_RANDOM_LOCATION = 'GoToRandomLocation'
GRASS_AND_ANSWER_QUESTIONS = 'GrassAndAnswerQuestions'
GROW = 'Grow'
HIT_NOW_AND_THEN = 'HitNowAndThen'
JUMP_IF_OPEN = 'JumpIfOpen'
JUMP_IF_SHUT = 'JumpIfShut'
MONITOR_ERIC = 'MonitorEric'
MOVE_ABOUT_UNTIL = 'MoveAboutUntil'
MOVE_BIKE = 'MoveBike'
MOVE_DESK_LID = 'MoveDeskLid'
MOVE_FROG = 'MoveFrog'
MOVE_MOUSE = 'MoveMouse'
MOVE_PELLET = 'MovePellet'
MOVE_WATER = 'MoveWater'
OPEN_DOOR = 'OpenDoor'
RESTART = 'Restart'
SET_CLOCK = 'SetClock'
SET_CONTROLLING_COMMAND = 'SetControllingCommand'
SET_RESTART_POINT = 'SetRestartPoint'
SET_SUBCOMMAND = 'SetSubcommand'
SHADOW_ERIC = 'ShadowEric'
SHUT_DOOR = 'ShutDoor'
SIGNAL = 'Signal'
SIT_FOR_ASSEMBLY = 'SitForAssembly'
SIT_STILL = 'SitStill'
STALK_AND_HIT = 'StalkAndHit'
START_ASSEMBLY_IF_READY = 'StartAssemblyIfReady'
START_DINNER_IF_READY = 'StartDinnerIfReady'
START_LESSON_IF_READY = 'StartLessonIfReady'
STINK = 'Stink'
TELL_ERIC_AND_WAIT = 'TellEricAndWait'
TELL_ERIC = 'TellEric'
TRIP_PEOPLE_UP = 'TripPeopleUp'
UNSIGNAL = 'Unsignal'
WAIT_AT_DOOR = 'WaitAtDoor'
WAIT_UNTIL = 'WaitUntil'
WALK_AROUND = 'WalkAround'
WALK_FAST = 'WalkFast'
WATCH_FOR_ERIC = 'WatchForEric'
WRITE_ON_BOARD_UNLESS = 'WriteOnBoardUnless'

SIG_SWOT_READY_FOR_LESSON = 'SwotReadyForLesson'
SIG_END_OF_LESSON = 'EndOfLesson'

class CommandList:
    def __init__(self, name):
        self.name = name
        self.commands = []

    def add_command(self, *args):
        self.commands.append(args)

class Lesson:
    def __init__(self, lesson_id, *details):
        self.lesson_id = lesson_id
        self.details = details
        self.entries = []

    def add_entry(self, character_id, tap_id):
        self.entries.append((character_id, tap_id))
