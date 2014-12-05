# -*- coding: utf-8 -*-

# Copyright 2010, 2012-2014 Richard Dymond (rjdymond@gmail.com)
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

import sys
import os

from .skoolids import *
from . import animatorystates as states
from . import graphics
from . import skoolbuilder
from . import sound

SKOOL_DAZE = 0
SKOOL_DAZE_TAKE_TOO = 1
EZAD_LOOKS = 2

BACK_TO_SKOOL = 0
BACK_TO_SKOOL_DAZE = 1

CONFIG_SEPARATOR = ', '
SEPARATOR = ', '

class SkoolIniMaker:
    def __init__(self, custom):
        self.custom = custom
        self.ofile = None

    def build_ini(self):
        self.create_game_config()
        self.create_timetable_config()
        self.create_lesson_config()
        self.create_timing_config()
        self.create_screen_config()
        self.create_images()
        self.create_sounds()
        self.create_sprite_groups()
        self.create_eric()
        self.create_timetable()
        self.create_special_playtimes()
        self.create_characters()
        self.create_pellets()
        self.create_water_drop()
        self.create_sherry_drop()
        self.create_conker()
        self.create_water()
        self.create_stinkbombs()
        self.create_mice()
        self.create_mouse_locations()
        self.create_frogs()
        self.create_bike()
        self.create_lessons()
        self.create_skool_locations()
        self.create_inventory()
        self.create_taps()
        self.create_rooms()
        self.create_chairs()
        self.create_desks()
        self.create_desk_lid()
        self.create_doors()
        self.create_windows()
        self.create_walls()
        self.create_staircases()
        self.create_floors()
        self.create_routes()
        self.create_no_go_zones()
        self.create_font()
        self.create_message_config()
        self.create_sit_down_messages()
        self.create_assembly_messages()
        self.create_blackboards()
        self.create_blackboard_messages()
        self.create_questions_and_answers()
        self.create_lines_messages()
        self.create_lesson_messages()
        self.create_grass_messages()
        self.create_shields()
        self.create_safe()
        self.create_cups()
        self.create_plants()
        self.create_animation_phases()

    def write_ini_files(self, odir, verbose, force=False):
        self.build_ini()
        self.odir = odir
        self.verbose = verbose
        if not os.path.isdir(odir):
            os.makedirs(odir)
        cwd = os.getcwd()
        os.chdir(odir)

        wrote_inis = False
        for write_ini, fname in (
            (self.write_command_lists_ini, 'command_lists.ini'),
            (self.write_config_ini, 'config.ini'),
            (self.write_font_ini, 'font.ini'),
            (self.write_lessons_ini, 'lessons.ini'),
            (self.write_messages_ini, 'messages.ini'),
            (self.write_skool_ini, 'skool.ini'),
            (self.write_sprites_ini, 'sprites.ini')
        ):
            if self.open_file(fname, force):
                write_ini()
                wrote_inis = True
        if verbose and not wrote_inis:
            sys.stdout.write("All ini files present\n")

        if self.ofile:
            self.ofile.close()
        os.chdir(cwd)

    def write_command_lists_ini(self):
        self.write_command_lists()

    def write_config_ini(self):
        self.write_config('GameConfig', self.game_config)
        self.write_config('TimetableConfig', self.timetable_config)
        self.write_config('LessonConfig', self.lesson_config)
        self.write_config('TimingConfig', self.timing_config)
        self.write_config('ScreenConfig', self.screen_config)
        self.write_images()
        self.write_sounds()
        self.write_mouse_locations()
        self.write_random_locations()
        self.write_skool_locations()
        self.write_inventory()
        self.write_animation_phases()

    def write_font_ini(self):
        self.write_font()

    def write_lessons_ini(self):
        self.write_timetable()
        self.write_special_playtimes()
        self.write_lessons()

    def write_messages_ini(self):
        self.write_config('MessageConfig', self.message_config)
        self.write_sit_down_messages()
        self.write_assembly_messages()
        self.write_blackboard_messages()
        self.write_questions_and_answers()
        self.write_lines_messages()
        self.write_lesson_messages()
        self.write_grass_messages()

    def write_skool_ini(self):
        self.write_walls()
        self.write_rooms()
        self.write_blackboards()
        self.write_chairs()
        self.write_desks()
        self.write_doors()
        self.write_windows()
        self.write_floors()
        self.write_staircases()
        self.write_routes()
        self.write_no_go_zones()
        self.write_safe()
        self.write_shields()
        self.write_cups()

    def write_sprites_ini(self):
        self.write_sprite_groups()
        self.write_characters()
        self.write_eric()
        self.write_pellets()
        self.write_water_drop()
        self.write_sherry_drop()
        self.write_conker()
        self.write_water()
        self.write_stinkbombs()
        self.write_mice()
        self.write_frogs()
        self.write_bike()
        self.write_desk_lid()
        self.write_plants()

    def open_file(self, fname, force):
        if self.ofile:
            self.ofile.close()
        if not force and os.path.isfile(fname):
            return False
        self.ofile = open(fname, 'w')
        if self.verbose:
            sys.stdout.write('Writing {0}\n'.format(os.path.join(self.odir, fname)))
        return True

    def create_game_config(self):
        self.game_config = []
        self.game_config.append(('ImageSet', 'original'))
        self.game_config.append(('Icon', 'icon.png'))
        self.game_config.append(('ScreenshotDir', 'screenshots'))
        self.game_config.append(('MaxLines', 10000))
        self.game_config.append(('TooManyLinesCommandList', CL_EXPEL_ERIC_TOO_MANY_LINES))
        self.game_config.append(('ExpellerId', WACKER))
        self.game_config.append(('QuickStart', 0))
        self.game_config.append(('Cheat', 0))
        self.game_config.append(('GameFps', 20))
        self.game_config.append(('MinimumLinesDelay', 60))
        self.game_config.append(('LocationMarker', LOCATION_MARKER))
        self.game_config.append(('BesideEricXRange', 4))
        self.game_config.append(('LinesGivingRange', (10, 3)))
        self.game_config.append(('HitProbability', 0.5))
        self.game_config.append(('FireCatapultProbability', 0.5))
        self.game_config.append(('LinesRange', (1, 8)))
        self.game_config.append(('SpriteSize', (3, 4)))
        self.game_config.append(('SaveGameCompression', 9))
        self.game_config.append(('ConfirmClose', 0))
        self.game_config.append(('ConfirmQuit', 1))
        self.game_config.append(('Volume', 1.0))

    def create_timetable_config(self):
        self.timetable_config = []
        self.timetable_config.append(('LessonLength', 2400))
        self.timetable_config.append(('LessonStartTime', 600))
        self.timetable_config.append(('GetAlongTime', 200))
        self.timetable_config.append(('PlaytimePrefix', PLAYTIME_PREFIX))

    def create_lesson_config(self):
        self.lesson_config = []
        self.lesson_config.append(('WriteOnBoardProbability', 0.375))
        self.lesson_config.append(('BlackboardBacktrack', 3))
        self.lesson_config.append(('BlackboardPaceDistance', 3))

    def create_timing_config(self):
        self.timing_config = []
        self.timing_config.append(('EricWalkDelay', 2))
        self.timing_config.append(('JumpDelay', 4))
        self.timing_config.append(('DethronedDelay', 3))
        self.timing_config.append(('KnockoutDelay', 10))
        self.timing_config.append(('KnockedOverDelay', 15))
        self.timing_config.append(('ReprimandDelay', 8))
        self.timing_config.append(('TellEricDelay', 20))
        self.timing_config.append(('GoSlow', 5))
        self.timing_config.append(('GoFast', 3))
        self.timing_config.append(('GoFaster', 2))
        self.timing_config.append(('SpeedChangeDelayRange', (16, 31)))

    def create_screen_config(self):
        self.screen_config = []
        self.screen_config.append(('Scale', 2))
        self.screen_config.append(('Width', 32))
        self.screen_config.append(('Height', 24))
        self.screen_config.append(('GraphicsMode', 1))
        self.screen_config.append(('ScrollFps', 20))
        self.screen_config.append(('ScrollRightOffset', 9))
        self.screen_config.append(('ScrollLeftOffset', 10))
        self.screen_config.append(('ScrollColumns', 8))
        self.screen_config.append(('SpeechBubbleSize', (8, 3)))
        self.screen_config.append(('SpeechBubbleLipCoords', (8, 0)))
        self.screen_config.append(('SpeechBubbleLipSize', (1, 1)))
        self.screen_config.append(('SpeechBubbleInset', (4, 4)))
        self.screen_config.append(('SpeechBubbleInk', (0, 0, 0)))
        self.screen_config.append(('SpeechBubbleKey', (0, 254, 0)))
        self.screen_config.append(('SpriteKey', (0, 254, 0)))
        self.screen_config.append(('SpriteMatrixWidth', 16))
        self.screen_config.append(('SkoolInkKey', (255, 255, 255)))
        self.screen_config.append(('ScoreOffset', 1))
        self.screen_config.append(('LinesOffset', 9))
        self.screen_config.append(('HiScoreOffset', 17))
        self.screen_config.append(('FontInk', (0, 1, 2)))
        self.screen_config.append(('FontPaper', (255, 254, 253)))
        self.screen_config.append(('FlashCycle', 10))
        self.screen_config.append(('MessageBoxColour', (197, 0, 0)))
        self.screen_config.append(('MessageBoxKey', (1, 1, 1)))
        self.screen_config.append(('LinesInk', (205, 198, 205)))
        self.screen_config.append(('LinesPaperEric', (197, 0, 0)))
        self.screen_config.append(('LinesPaperOther', (0, 198, 0)))
        self.screen_config.append(('SecretInk', (205, 198, 205)))
        self.screen_config.append(('SecretPaper', (0, 0, 0)))

    def create_images(self):
        self.images = []
        common_dir = 'common'
        self.images.append((graphics.FONT, '%s/font.png' % common_dir))
        self.images.append((graphics.SPRITES, '%s/sprites.png' % common_dir))

    def create_sounds(self):
        self.sounds = []
        common_dir = 'common'
        self.sounds.append((sound.CATAPULT, '%s/catapult' % common_dir))
        self.sounds.append((sound.KNOCKED_OUT, '%s/knocked-out' % common_dir))

    def create_sprite_groups(self):
        self.sprite_groups = []
        self.sprite_groups.append((SG_BOY, (states.WALK0, 64), (states.WALK1, 65), (states.WALK2, 66), (states.WALK3, 67), (states.SITTING_ON_CHAIR, 68), (states.SITTING_ON_FLOOR, 69), (states.KNOCKED_OUT, 70)))
        self.sprite_groups.append((SG_SWOT, (states.WALK0, 48), (states.WALK1, 49), (states.WALK2, 50), (states.WALK3, 51), (states.SITTING_ON_CHAIR, 52), (states.SITTING_ON_FLOOR, 53), (states.KNOCKED_OUT, 54)))
        self.sprite_groups.append((SG_BULLY, (states.WALK0, 32), (states.WALK1, 33), (states.WALK2, 34), (states.WALK3, 35), (states.SITTING_ON_CHAIR, 36), (states.SITTING_ON_FLOOR, 37), (states.KNOCKED_OUT, 38), (states.HITTING0, 40), (states.HITTING1, 41)))
        self.sprite_groups.append((SG_TEARAWAY, (states.WALK0, 16), (states.WALK1, 17), (states.WALK2, 18), (states.WALK3, 19), (states.SITTING_ON_CHAIR, 20), (states.SITTING_ON_FLOOR, 21), (states.KNOCKED_OUT, 22), (states.ARM_UP, 23), (states.CATAPULT0, 26), (states.CATAPULT1, 27)))
        self.sprite_groups.append((SG_WACKER, (states.WALK0, 80), (states.WALK1, 81), (states.WALK2, 82), (states.WALK3, 83), (states.KNOCKED_OVER, 86), (states.ARM_UP, 87)))
        self.sprite_groups.append((SG_ROCKITT, (states.WALK0, 96), (states.WALK1, 97), (states.WALK2, 98), (states.WALK3, 99), (states.KNOCKED_OVER, 102), (states.ARM_UP, 103)))
        self.sprite_groups.append((SG_WITHIT, (states.WALK0, 88), (states.WALK1, 89), (states.WALK2, 90), (states.WALK3, 91), (states.KNOCKED_OVER, 94), (states.ARM_UP, 95)))
        self.sprite_groups.append((SG_CREAK, (states.WALK0, 104), (states.WALK1, 105), (states.WALK2, 106), (states.WALK3, 107), (states.KNOCKED_OVER, 110), (states.ARM_UP, 111)))
        self.sprite_groups.append((SG_PELLET, (states.FLY, 79)))

    def create_pellets(self):
        self.pellets = []
        self.pellets.append((TEARAWAY, 'TearawayPellet', SG_PELLET, CL_PELLET, 13, self.hit_zone, (1, 1)))
        self.pellets.append((HERO, 'HeroPellet', SG_PELLET, CL_PELLET, 13, self.hit_zone, (1, 1)))

    def create_water_drop(self):
        self.water_drop = None

    def create_sherry_drop(self):
        self.sherry_drop = None

    def create_conker(self):
        self.conker = None

    def create_mice(self):
        self.mice = []

    def create_mouse_locations(self):
        self.mouse_locations = []

    def create_frogs(self):
        self.frogs = []

    def create_bike(self):
        self.bike = None

    def create_inventory(self):
        self.inventory = []

    def create_water(self):
        self.water = []

    def create_stinkbombs(self):
        self.stinkbombs = []

    def create_desks(self):
        self.desks = []

    def create_desk_lid(self):
        self.desk_lid = None

    def create_doors(self):
        self.doors = []

    def create_windows(self):
        self.windows = []

    def create_special_playtimes(self):
        self.special_playtimes = []

    def create_lessons(self):
        self.lessons = self.tap_maker.get_lessons()

    def create_taps(self):
        self.taps = self.tap_maker.get_taps()

    def create_font(self):
        self.font = []
        self.font.append((' ', 4))
        self.font.append(('!', 2))
        self.font.append(('"', 4))
        self.font.append(('#', 6))
        self.font.append(('$', 6))
        self.font.append(('%', 4))
        self.font.append(('&', 6))
        self.font.append(("'", 3))
        self.font.append(('(', 3))
        self.font.append((')', 3))
        self.font.append(('*', 6))
        self.font.append(('+', 6))
        self.font.append((',', 3))
        self.font.append(('-', 5))
        self.font.append(('.', 3))
        self.font.append(('/', 4))
        self.font.append(('0', 5))
        self.font.append(('1', 4))
        self.font.append(('2', 5))
        self.font.append(('3', 5))
        self.font.append(('4', 5))
        self.font.append(('5', 5))
        self.font.append(('6', 5))
        self.font.append(('7', 5))
        self.font.append(('8', 5))
        self.font.append(('9', 5))
        self.font.append((':', 3))
        self.font.append((';', 3))
        self.font.append(('<', 5))
        self.font.append(('=', 5))
        self.font.append(('>', 5))
        self.font.append(('?', 5))
        self.font.append(('@', 6))
        self.font.append(('A', 5))
        self.font.append(('B', 5))
        self.font.append(('C', 5))
        self.font.append(('D', 5))
        self.font.append(('E', 5))
        self.font.append(('F', 5))
        self.font.append(('G', 5))
        self.font.append(('H', 5))
        self.font.append(('I', 4))
        self.font.append(('J', 5))
        self.font.append(('K', 5))
        self.font.append(('L', 5))
        self.font.append(('M', 6))
        self.font.append(('N', 5))
        self.font.append(('O', 5))
        self.font.append(('P', 5))
        self.font.append(('Q', 6))
        self.font.append(('R', 5))
        self.font.append(('S', 5))
        self.font.append(('T', 6))
        self.font.append(('U', 5))
        self.font.append(('V', 6))
        self.font.append(('W', 6))
        self.font.append(('X', 6))
        self.font.append(('Y', 6))
        self.font.append(('Z', 6))
        self.font.append(('[', 3))
        self.font.append(('\\', 4))
        self.font.append((']', 3))
        self.font.append(('^', 6))
        self.font.append(('_', 6))
        self.font.append(('`', 5))
        self.font.append(('a', 5))
        self.font.append(('b', 5))
        self.font.append(('c', 5))
        self.font.append(('d', 5))
        self.font.append(('e', 5))
        self.font.append(('f', 5))
        self.font.append(('g', 5))
        self.font.append(('h', 5))
        self.font.append(('i', 2))
        self.font.append(('j', 4))
        self.font.append(('k', 5))
        self.font.append(('l', 2))
        self.font.append(('m', 6))
        self.font.append(('n', 5))
        self.font.append(('o', 5))
        self.font.append(('p', 5))
        self.font.append(('q', 5))
        self.font.append(('r', 5))
        self.font.append(('s', 5))
        self.font.append(('t', 4))
        self.font.append(('u', 5))
        self.font.append(('v', 4))
        self.font.append(('w', 6))
        self.font.append(('x', 6))
        self.font.append(('y', 5))
        self.font.append(('z', 5))
        self.font.append(('{', 4))
        self.font.append(('|', 2))
        self.font.append(('}', 4))
        self.font.append(('~', 5))

    def create_message_config(self):
        self.message_config = []
        self.message_config.append(('Newline', '^'))
        self.message_config.append(('TitleMacro', TITLE_MACRO))
        self.message_config.append(('GrasseeMacro', GRASSEE_MACRO))
        self.message_config.append(('ScoreLabel', 'Score'))
        self.message_config.append(('LinesTotalLabel', 'Lines'))
        self.message_config.append(('HiScoreLabel', 'Hi-Sc'))
        self.message_config.append(('NumberOfLinesMacro', NUMBER_OF_LINES_MACRO))
        self.message_config.append(('LinesRecipientMacro', LINES_RECIPIENT_MACRO))

    def create_cups(self):
        self.cups = []

    def create_plants(self):
        self.plants = []

    def create_assembly_messages(self):
        self.assembly_messages = []

    def create_questions_and_answers(self):
        self.questions_and_answers = {}
        for teacher, teacher_qa in self.teachers:
            teacher_questions = []
            teacher_answers = []
            teacher_qa_pairs = []
            specials, groups = teacher_qa[self.custom]
            for group, questions, answers, qa_pairs in groups:
                teacher_questions += [(q_id, group, q_template) for q_id, q_template in questions]
                teacher_answers += [(q_id, a_template) for q_id, a_template in answers]
                teacher_qa_pairs += [(group, word1, word2) for word1, word2 in qa_pairs]
            self.questions_and_answers[teacher] = [specials, teacher_questions, teacher_answers, teacher_qa_pairs]

    def create_grass_messages(self):
        self.grass_messages = []
        self.grass_messages.append((skoolbuilder.GM_WRITERS, HERO, TEARAWAY))
        self.grass_messages.append((skoolbuilder.GM_WRITE_TALE, 'Please %s I cannot tell a lie . . %s wrote on the blackboard' % (TITLE_MACRO, GRASSEE_MACRO)))
        self.grass_messages.append((skoolbuilder.GM_HITTERS, HERO, BULLY))
        self.grass_messages.append((skoolbuilder.GM_HIT_TALE, 'Please %s I cannot tell a lie . . %s hit me' % (TITLE_MACRO, GRASSEE_MACRO)))
        self.grass_messages.append((skoolbuilder.GM_ABSENT_TALE, 'Please %s I cannot tell a lie . . $%s is not here' % (TITLE_MACRO, HERO)))

    def create_animation_phases(self):
        self.animation_phases = []

    def write(self, line):
        self.ofile.write('%s\n' % line)

    def write_section_header(self, name):
        self.write('[%s]' % name)

    def end_section(self):
        self.write('')

    def write_tuples(self, tuples, separator=SEPARATOR, sort=False):
        if sort:
            tuples = sorted(tuples)
        for t in tuples:
            self.write(separator.join([str(e) for e in t]))

    def write_config(self, name, config):
        self.write_section_header(name)
        self.write_tuples(config, CONFIG_SEPARATOR, True)
        self.end_section()

    def write_images(self):
        self.write_section_header(skoolbuilder.IMAGES)
        self.write('; imageId, path')
        self.write_tuples(self.images)
        self.end_section()

    def write_sounds(self):
        self.write_section_header(skoolbuilder.SOUNDS)
        self.write('; soundId, path')
        self.write_tuples(self.sounds)
        self.end_section()

    def write_sprite_groups(self):
        for group in self.sprite_groups:
            self.write_section_header('%s %s' % (skoolbuilder.SPRITE_GROUP, group[0]))
            self.write_tuples(group[1:])
            self.end_section()

    def write_eric(self):
        self.write_section_header(skoolbuilder.ERIC)
        self.write('; characterId, name, spriteGroupId, animatoryState, direction, (x, y), headXY, flags[, bendOverHandXY]')
        self.write_tuples([self.eric])
        self.end_section()

    def write_characters(self):
        self.write_section_header(skoolbuilder.CHARACTERS)
        self.write('; characterId, name[/title], spriteGroupId, animatoryState, direction, (x, y), headXY, flags')
        self.write_tuples(self.characters)
        self.end_section()

    def write_pellets(self):
        self.write_section_header(skoolbuilder.CATAPULT_PELLETS)
        self.write('; characterId, pelletId, spriteGroupId, commandListId, range, hitZone, hitXY')
        self.write_tuples(self.pellets)
        self.end_section()

    def write_water_drop(self):
        if self.water_drop:
            self.write_section_header(skoolbuilder.WATER_DROP)
            self.write('; objectId, spriteGroupId, commandListId, hitXY')
            self.write_tuples([self.water_drop])
            self.end_section()

    def write_sherry_drop(self):
        if self.sherry_drop:
            self.write_section_header(skoolbuilder.SHERRY_DROP)
            self.write('; objectId, spriteGroupId, commandListId, hitXY')
            self.write_tuples([self.sherry_drop])
            self.end_section()

    def write_conker(self):
        if self.conker:
            self.write_section_header(skoolbuilder.CONKER)
            self.write('; objectId, spriteGroupId, commandListId, minX, maxX, minY, maxY, hitXY')
            self.write_tuples([self.conker])
            self.end_section()

    def write_water(self):
        if self.water:
            self.write_section_header(skoolbuilder.WATER)
            self.write('; characterId, waterId, spriteGroupId, commandListId, animationPhases')
            self.write_tuples(self.water)
            self.end_section()

    def write_stinkbombs(self):
        if self.stinkbombs:
            self.write_section_header(skoolbuilder.STINKBOMBS)
            self.write('; characterId, stinkbombId, spriteGroupId, commandListId, animationPhases, stinkRange')
            self.write_tuples(self.stinkbombs)
            self.end_section()

    def write_mice(self):
        if self.mice:
            self.write_section_header(skoolbuilder.MICE)
            self.write('; mouseId, spriteGroupId, animatoryState, (x, y), commandListId, spriteXY')
            self.write_tuples(self.mice)
            self.end_section()

    def write_mouse_locations(self):
        if self.mouse_locations:
            self.write_section_header(skoolbuilder.MOUSE_LOCATIONS)
            self.write('; x, y')
            self.write_tuples(self.mouse_locations)
            self.end_section()

    def write_frogs(self):
        if self.frogs:
            self.write_section_header(skoolbuilder.FROGS)
            self.write('; frogId, spriteGroupId, animatoryState, (x, y), commandListId, turnRound, shortHop, longHop, sitXY, ericProximity')
            self.write_tuples(self.frogs)
            self.end_section()

    def write_bike(self):
        if self.bike:
            self.write_section_header(skoolbuilder.BIKE)
            self.write('; bikeId, spriteGroupId, animatoryState, unchainXY, commandListId, topLeft, size, coords, moveDelay, pedalMomentum, maxMomentum')
            self.write_tuples([self.bike])
            self.end_section()

    def write_timetable(self):
        self.write_section_header(skoolbuilder.TIMETABLE)
        self.write('; lessonID')
        for lesson_id in self.timetable:
            self.write(lesson_id)
        self.end_section()

    def write_special_playtimes(self):
        if self.special_playtimes:
            self.write_section_header(skoolbuilder.SPECIAL_PLAYTIMES)
            self.write('; lessonID')
            for lesson_id in self.special_playtimes:
                self.write(lesson_id)
            self.end_section()

    def write_lessons(self):
        for lesson in self.lessons:
            self.write_section_header('%s %s %s' % (skoolbuilder.LESSON, lesson.lesson_id, ', '.join(lesson.details)))
            self.write('; characterId, commandListID')
            self.write_tuples(lesson.entries)
            self.end_section()

    def write_random_locations(self):
        self.write_section_header(skoolbuilder.RANDOM_LOCATIONS)
        self.write('; characterID, (x, y), (x, y)...')
        for c in self.characters:
            character_id = c[0]
            self.write_tuples([[character_id] + list(self.get_random_locations(character_id))])
        self.end_section()

    def write_skool_locations(self):
        self.write_section_header(skoolbuilder.SKOOL_LOCATIONS)
        self.write('; locationId, x, y')
        self.skool_locations.sort(key=lambda loc: loc[2])
        for x, y, location_id in self.skool_locations:
            self.write('%s, %i, %i' % (location_id, x, y))
        self.end_section()

    def write_inventory(self):
        if self.inventory:
            self.write_section_header(skoolbuilder.INVENTORY)
            self.write('; itemId, topLeft, size')
            self.write_tuples(self.inventory)
            self.end_section()

    def write_command_lists(self):
        for tap in self.taps:
            self.write_section_header('%s %s' % (skoolbuilder.COMMAND_LIST, tap.name))
            for elements in tap.commands:
                self.write_tuples([elements])
            self.end_section()

    def write_rooms(self):
        self.write_section_header(skoolbuilder.ROOMS)
        self.write('; roomId, name, topLeft, bottomRight, getAlong')
        self.write_tuples(self.rooms)
        self.end_section()

    def write_chairs(self):
        self.write_section_header(skoolbuilder.CHAIRS)
        self.write('; roomId, x1, x2,...')
        self.write_tuples(self.chairs)
        self.end_section()

    def write_desks(self):
        if self.desks:
            self.write_section_header(skoolbuilder.DESKS)
            self.write('; roomId, x1, x2,...')
            self.write_tuples(self.desks)
            self.end_section()

    def write_desk_lid(self):
        if self.desk_lid:
            self.write_section_header(skoolbuilder.DESK_LID)
            self.write('; deskLidId, spriteGroupId, commandListId, xOffset')
            self.write_tuples([self.desk_lid])
            self.end_section()

    def write_doors(self):
        if self.doors:
            self.write_section_header(skoolbuilder.DOORS)
            self.write('; doorId, x, bottomY, topY, initiallyShut, autoShutDelay, shutTopLeft, size, coords[, climb[, fly]]')
            self.write_tuples(self.doors)
            self.end_section()

    def write_windows(self):
        if self.windows:
            self.write_section_header(skoolbuilder.WINDOWS)
            self.write('; windowId, x, bottomY, topY, initiallyShut, openerCoords, shutTopLeft, size, coords, descentPhases[, notABird]')
            self.write_tuples(self.windows)
            self.end_section()

    def write_walls(self):
        self.write_section_header(skoolbuilder.WALLS)
        self.write('; wallId, x, bottomY, topY')
        self.write_tuples(self.walls)
        self.end_section()

    def write_staircases(self):
        self.write_section_header(skoolbuilder.STAIRCASES)
        self.write('; staircaseId[:alias], bottom, top[, force]')
        self.write_tuples(self.staircases)
        self.end_section()

    def write_floors(self):
        self.write_section_header(skoolbuilder.FLOORS)
        self.write('; floorId, minX, maxX, y')
        self.write_tuples(self.floors)
        self.end_section()

    def write_routes(self):
        self.write_section_header(skoolbuilder.ROUTES)
        self.write('; homeFloorId, destFloorId|*[, destFloorId[, ...]], nextStaircaseId')
        for home_floor_id in self.routes:
            for route in self.routes[home_floor_id]:
                dest_floor_ids = route[:-1]
                staircase_id = route[-1]
                self.write('%s, %s, %s' % (home_floor_id, ', '.join(dest_floor_ids), staircase_id))
        self.end_section()

    def write_no_go_zones(self):
        self.write_section_header(skoolbuilder.NO_GO_ZONES)
        self.write('; zoneId, minX, maxX, bottomY, topY')
        self.write_tuples(self.no_go_zones)
        self.end_section()

    def write_sit_down_messages(self):
        self.write_section_header(skoolbuilder.SIT_DOWN_MESSAGES)
        self.write('; characterId, sitDownMessage')
        self.write_tuples(self.sit_down_messages)
        self.end_section()

    def write_font(self):
        self.write_section_header(skoolbuilder.FONT)
        self.write('; char, offset, width')
        offset = 0
        for char, width in self.font:
            quote = "'" if char == '"' else '"'
            self.write('%s%s%s, %i, %i' % (quote, char, quote, offset, width))
            offset += width
        self.end_section()

    def write_assembly_messages(self):
        if not self.assembly_messages:
            return
        self.write_section_header(skoolbuilder.ASSEMBLY_MESSAGES)
        self.write_tuples(self.assembly_messages)
        self.end_section()

    def write_blackboards(self):
        self.write_section_header(skoolbuilder.BLACKBOARDS)
        self.write('; roomId, topLeft, size, chalk')
        self.write_tuples(self.blackboards)
        self.end_section()

    def write_blackboard_messages(self):
        for character_id in self.blackboard_messages:
            self.write_section_header('%s %s' % (skoolbuilder.BLACKBOARD_MESSAGES, character_id))
            for message in self.blackboard_messages[character_id]:
                self.write(message)
            self.end_section()

    def write_questions_and_answers(self):
        for teacher_id in self.questions_and_answers:
            specials, questions, answers, qa_pairs = self.questions_and_answers[teacher_id]
            self.write_section_header('%s %s' % (skoolbuilder.QUESTIONS_AND_ANSWERS, teacher_id))
            if specials:
                self.write('%s, %s, %i' % (skoolbuilder.QA_SPECIAL_GROUP, specials[0][0], specials[0][1]))
                self.write('%s, %s' % (skoolbuilder.QA_SPECIAL_QUESTION, specials[1]))
                self.write('%s, %s' % (skoolbuilder.QA_SPECIAL_ANSWER, specials[2]))
            self.write('; Question, questionId, groupId, questionTemplate')
            self.write_tuples([[skoolbuilder.QA_QUESTION] + list(q) for q in questions])
            self.write('; Answer, questionId, answerTemplate')
            self.write_tuples([[skoolbuilder.QA_ANSWER] + list(a) for a in answers])
            self.write('; groupId, word1, word2')
            self.write_tuples(qa_pairs)
            self.end_section()

    def write_lines_messages(self):
        self.write_section_header(skoolbuilder.LINES_MESSAGES)
        self.write('; characterId|*, linesMessageId, linesMessage')
        self.write_tuples(self.lines_messages)
        self.end_section()

    def write_lesson_messages(self):
        self.write_section_header(skoolbuilder.LESSON_MESSAGES)
        self.write('; characterId|*, lessonMessage[, condition]')
        self.write_tuples(self.lesson_messages)
        self.end_section()

    def write_shields(self):
        if self.shields:
            self.write_section_header(skoolbuilder.SHIELDS)
            self.write('; score, topLeft, size, coords')
            self.write_tuples(self.shields)
            self.end_section()

    def write_safe(self):
        self.write_section_header(skoolbuilder.SAFE)
        self.write('; topLeft, size, coords')
        self.write_tuples([self.safe])
        self.end_section()

    def write_cups(self):
        if self.cups:
            self.write_section_header(skoolbuilder.CUPS)
            self.write('; cupId, emptyTopLeft, size, coords')
            self.write_tuples(self.cups)
            self.end_section()

    def write_plants(self):
        if self.plants:
            self.write_section_header(skoolbuilder.PLANTS)
            self.write('; plantId, spriteGroupId, x, y, commandListId')
            self.write_tuples(self.plants)
            self.end_section()

    def write_grass_messages(self):
        self.write_section_header(skoolbuilder.GRASS_MESSAGES)
        self.write_tuples(self.grass_messages)
        self.end_section()

    def write_animation_phases(self):
        for phase_set in self.animation_phases:
            self.write_section_header('%s %s' % (skoolbuilder.ANIMATION_PHASES, phase_set[0]))
            self.write('; %s' % phase_set[1])
            self.write_tuples(phase_set[2:])
            self.end_section()
