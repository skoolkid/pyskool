# -*- coding: utf-8 -*-

# Copyright 2010, 2013 Richard Dymond (rjdymond@gmail.com)
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

import skoolini
from sdtaps import SDTapMaker
from skoolids import *
import animatorystates as states
import graphics
import lines
import skoolbuilder
import sound

SKOOL_DAZE = 0
SKOOL_DAZE_TAKE_TOO = 1
EZAD_LOOKS = 2

# Floor IDs
FLR_BOTTOM = 'Bottom'
FLR_LEFT_MIDDLE = 'LeftMiddle'
FLR_RIGHT_MIDDLE = 'RightMiddle'
FLR_LEFT_TOP = 'LeftTop'
FLR_RIGHT_TOP = 'RightTop'

# Staircase IDs
SC_UP_TO_STAFF_ROOM = ('UpToStaffRoom', 'DownFromStaffRoom')
SC_UP_TO_STUDY = ('UpToStudy', 'DownFromStudy')
SC_UP_TO_EXAM_ROOM = ('UpToExamRoom', 'DownFromExamRoom')
SC_UP_TO_MAP_ROOM = ('UpToMapRoom', 'DownFromMapRoom')

class SDIniMaker(skoolini.SkoolIniMaker):
    def __init__(self, custom):
        skoolini.SkoolIniMaker.__init__(self, custom)
        self.tap_maker = SDTapMaker(custom)
        self.hit_zone = 7

    def get_random_locations(self, character_id):
        if self.custom == EZAD_LOOKS:
            return [(64, 3), (7, 3), (7, 17), (92, 17)]
        return [(36, 3), (93, 3), (93, 17), (8, 17)]

    def create_game_config(self):
        skoolini.SkoolIniMaker.create_game_config(self)
        save_game_dirs = {}
        save_game_dirs[SKOOL_DAZE] = 'skool_daze'
        save_game_dirs[SKOOL_DAZE_TAKE_TOO] = 'skool_daze_take_too'
        save_game_dirs[EZAD_LOOKS] = 'ezad_looks'
        self.game_config.append(('SaveGameDir', 'save/%s' % save_game_dirs[self.custom]))
        names = {}
        names[SKOOL_DAZE] = 'Skool Daze'
        names[SKOOL_DAZE_TAKE_TOO] = 'Skool Daze Take Too'
        names[EZAD_LOOKS] = 'Ezad Looks'
        self.game_config.append(('Name', names[self.custom]))
        self.game_config.append(('AllShieldsScore', 2000))
        self.game_config.append(('SafeSecrets', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.game_config.append(('SafeOpenScore', 1000))
        self.game_config.append(('UpAYearScore', 5000))
        self.game_config.append(('RestartOnYearEnd', 0))

    def create_timetable_config(self):
        skoolini.SkoolIniMaker.create_timetable_config(self)
        self.timetable_config.append(('SpecialPlaytimeProbability', 0.375))

    def create_lesson_config(self):
        skoolini.SkoolIniMaker.create_lesson_config(self)
        self.lesson_config.append(('EricsTeacherWriteOnBoardProbability', 0.296875))
        self.lesson_config.append(('QASessionProbability', 0.9375))
        self.lesson_config.append(('GrassForHittingProbability', 0.1171875))
        self.lesson_config.append(('LinesForTalesProbability', 0.09375))

    def create_screen_config(self):
        skoolini.SkoolIniMaker.create_screen_config(self)
        initial_column = 0 if self.custom == SKOOL_DAZE_TAKE_TOO else 32
        self.screen_config.append(('InitialColumn', initial_column))
        self.screen_config.append(('Background', (197, 0, 0)))
        logo_x = 24 if self.custom == EZAD_LOOKS else 0
        self.screen_config.append(('LogoPos', (logo_x, 21)))
        self.screen_config.append(('LessonBoxInk', (0, 198, 197)))
        self.screen_config.append(('LessonBoxPos', (12, 21)))
        score_box_x = 0 if self.custom == EZAD_LOOKS else 24
        self.screen_config.append(('ScoreBoxInk', (197, 198, 0)))
        self.screen_config.append(('ScoreBoxPos', (score_box_x, 21)))

    def create_images(self):
        skoolini.SkoolIniMaker.create_images(self)
        base_dir = 'skool_daze'
        img_dir = 'ezad_looks' if self.custom == EZAD_LOOKS else base_dir
        logo_dir = 'skool_daze_take_too' if self.custom == SKOOL_DAZE_TAKE_TOO else img_dir
        self.images.append((graphics.LOGO, '%s/logo.png' % logo_dir))
        self.images.append((graphics.MUTABLES, '%s/mutables.png' % img_dir))
        self.images.append((graphics.MUTABLES_INK, '%s/mutables_ink.png' % img_dir))
        self.images.append((graphics.MUTABLES_PAPER, '%s/mutables_paper.png' % img_dir))
        self.images.append((graphics.SKOOL, '%s/skool.png' % img_dir))
        self.images.append((graphics.SKOOL_INK, '%s/skool_ink.png' % img_dir))
        self.images.append((graphics.SKOOL_PAPER, '%s/skool_paper.png' % img_dir))
        self.images.append((graphics.SPEECH_BUBBLE, '%s/bubble.png' % base_dir))
        self.images.append((graphics.LESSON_BOX, '%s/lesson_box.png' % base_dir))
        self.images.append((graphics.SCOREBOX, '%s/scorebox.png' % base_dir))
        self.images.append((graphics.MESSAGE_BOX, '%s/message_box.png' % base_dir))

    def create_sounds(self):
        skoolini.SkoolIniMaker.create_sounds(self)
        sounds_dir = 'skool_daze'
        self.sounds.append((sound.BELL, '%s/bell' % sounds_dir))
        self.sounds.append((sound.HIT_SOUNDS[0], '%s/hit0' % sounds_dir))
        self.sounds.append((sound.HIT_SOUNDS[1], '%s/hit1' % sounds_dir))
        self.sounds.append((sound.LINES1, '%s/lines1' % sounds_dir))
        self.sounds.append((sound.LINES2, '%s/lines2' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[0], '%s/walk0' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[1], '%s/walk0' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[2], '%s/walk1' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[3], '%s/walk0' % sounds_dir))
        self.sounds.append((sound.JUMP, '%s/jump' % sounds_dir))
        self.sounds.append((sound.ALL_SHIELDS, '%s/all-shields' % sounds_dir))
        self.sounds.append((sound.OPEN_SAFE, '%s/all-shields' % sounds_dir))
        self.sounds.append((sound.SHIELD, '%s/shield' % sounds_dir))
        self.sounds.append((sound.TUNE, '%s/tune' % sounds_dir))
        self.sounds.append((sound.UP_A_YEAR, '%s/tune' % sounds_dir))

    def create_sprite_groups(self):
        skoolini.SkoolIniMaker.create_sprite_groups(self)
        self.sprite_groups.append((SG_ERIC, (states.WALK0, 0), (states.WALK1, 1), (states.WALK2, 2), (states.WALK3, 3), (states.SITTING_ON_CHAIR, 4), (states.SITTING_ON_FLOOR, 5), (states.KNOCKED_OUT, 6), (states.ARM_UP, 7), (states.HITTING0, 8), (states.HITTING1, 9), (states.CATAPULT0, 10), (states.CATAPULT1, 11)))
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.sprite_groups.append((SG_TAKE, (states.WALK0, 112), (states.WALK1, 113), (states.WALK2, 114), (states.WALK3, 115), (states.KNOCKED_OVER, 118), (states.ARM_UP, 119)))

    def get_initial_locations(self):
        locations = {}

        if self.custom == SKOOL_DAZE_TAKE_TOO:
            locations[BOY01] = (18, 3)
            locations[BOY02] = (93, 3)
            locations[BOY03] = (89, 3)
            locations[BOY04] = (24, 3)
            locations[BOY05] = (47, 17)
            locations[BOY06] = (48, 17)
            locations[BOY07] = (21, 3)
            locations[BOY08] = (10, 17)
            locations[BOY09] = (86, 3)
            locations[BOY10] = (90, 17)
            locations[BOY11] = (1, 17)
            locations[WACKER] = (1, 3)
            locations[ROCKITT] = (6, 10)
            locations[WITHIT] = (5, 17)
            locations[CREAK] = (3, 10)
            locations[TAKE] = (4, 3)
            locations[TEARAWAY] = (24, 17)
            locations[BULLY] = (27, 17)
            locations[SWOT] = (28, 3)
        else:
            # Standard initial locations
            locations[BOY01] = (43, 17)
            locations[BOY02] = (44, 17)
            locations[BOY03] = (45, 17)
            locations[BOY04] = (46, 17)
            locations[BOY05] = (47, 17)
            locations[BOY06] = (48, 17)
            locations[BOY07] = (49, 17)
            locations[BOY08] = (50, 17)
            locations[BOY09] = (51, 17)
            locations[BOY10] = (52, 17)
            locations[BOY11] = (53, 17)
            locations[WACKER] = (10, 17)
            locations[ROCKITT] = (10, 17)
            locations[WITHIT] = (10, 17)
            locations[CREAK] = (10, 17)
            locations[TEARAWAY] = (25, 17)
            locations[BULLY] = (70, 17)
            locations[SWOT] = (70, 17)
        if self.custom == EZAD_LOOKS:
            for character_id, (x, y) in locations.items():
                locations[character_id] = (93 - x, y)

        return locations

    def create_characters(self):
        locations = self.get_initial_locations()
        self.characters = []
        adult_head_xy = (1, 0)
        kid_head_xy = (1, 1)
        self.characters.append((BOY01, "PERKINS", SG_BOY, states.WALK0, -1, locations[BOY01], kid_head_xy, "F"))
        self.characters.append((BOY02, "GIBSON", SG_BOY, states.WALK0, 1, locations[BOY02], kid_head_xy, "F"))
        self.characters.append((BOY03, "FANSHAW", SG_BOY, states.WALK0, -1, locations[BOY03], kid_head_xy, "F"))
        self.characters.append((BOY04, "SMITH", SG_BOY, states.WALK0, 1, locations[BOY04], kid_head_xy, "F"))
        self.characters.append((BOY05, "HARRIS", SG_BOY, states.WALK0, -1, locations[BOY05], kid_head_xy, "F"))
        self.characters.append((BOY06, "MILLER", SG_BOY, states.WALK0, 1, locations[BOY06], kid_head_xy, "F"))
        self.characters.append((BOY07, "JONES", SG_BOY, states.WALK0, -1, locations[BOY07], kid_head_xy, "F"))
        self.characters.append((BOY08, "VICKERS", SG_BOY, states.WALK0, 1, locations[BOY08], kid_head_xy, "F"))
        self.characters.append((BOY09, "BUTLER", SG_BOY, states.WALK0, -1, locations[BOY09], kid_head_xy, "F"))
        self.characters.append((BOY10, "COOK", SG_BOY, states.WALK0, 1, locations[BOY10], kid_head_xy, "F"))
        self.characters.append((BOY11, "SNODGRASS", SG_BOY, states.WALK0, -1, locations[BOY11], kid_head_xy, "F"))
        self.characters.append((WACKER, "MR WACKER%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_WACKER, states.WALK0, -1, locations[WACKER], adult_head_xy, "ALPSTW"))
        self.characters.append((ROCKITT, "MR ROCKITT%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_ROCKITT, states.WALK0, -1, locations[ROCKITT], adult_head_xy, "ALPSTW"))
        self.characters.append((WITHIT, "MR WITHIT%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_WITHIT, states.WALK0, -1, locations[WITHIT], adult_head_xy, "ALPSTW"))
        self.characters.append((CREAK, "MR CREAK%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_CREAK, states.WALK0, -1, locations[CREAK], adult_head_xy, "ALPSTW"))
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.characters.append((TAKE, "MISS TAKE%sMiss" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_TAKE, states.WALK0, 1, locations[TAKE], adult_head_xy, "ALPTW"))
        self.characters.append((TEARAWAY, "BOY WANDER", SG_TEARAWAY, states.WALK0, -1, locations[TEARAWAY], kid_head_xy, "FPRT"))
        self.characters.append((BULLY, "ANGELFACE", SG_BULLY, states.WALK0, -1, locations[BULLY], kid_head_xy, "FPRTV"))
        self.characters.append((SWOT, "EINSTEIN", SG_SWOT, states.WALK0, -1, locations[SWOT], kid_head_xy, "FPRTV"))

    def create_eric(self):
        location = (15, 17) if self.custom == SKOOL_DAZE_TAKE_TOO else (48, 17)
        if self.custom == EZAD_LOOKS:
            location = (93 - location[0], location[1])
        self.eric = (HERO, 'ERIC', SG_ERIC, states.WALK0, -1, location, (1, 1), 'FPRT')

    def create_timetable(self):
        self.timetable = []
        self.timetable.append(LSN_PLAYTIME_4)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_READING_ROOM)
        else:
            self.timetable.append(LSN_WITHIT_MAP_ROOM_2)
        self.timetable.append(LSN_REVISION_LIBRARY_3)
        self.timetable.append(LSN_CREAK_WHITE_ROOM)
        self.timetable.append(LSN_PLAYTIME_6)
        self.timetable.append(LSN_CREAK_READING_ROOM_1)
        self.timetable.append(LSN_ROCKITT_WHITE_ROOM_2)
        self.timetable.append(LSN_PLAYTIME_2)
        self.timetable.append(LSN_DINNER_WITHIT)
        self.timetable.append(LSN_PLAYTIME_1)
        self.timetable.append(LSN_PLAYTIME_8)
        self.timetable.append(LSN_ROCKITT_WHITE_ROOM_1)
        self.timetable.append(LSN_WACKER_EXAM_ROOM)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_WITHIT_MAP_ROOM_1)
        self.timetable.append(LSN_PLAYTIME_3)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_MAP_ROOM)
        else:
            self.timetable.append(LSN_WITHIT_MAP_ROOM_1)
        self.timetable.append(LSN_WACKER_READING_ROOM)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_PLAYTIME_7)
        self.timetable.append(LSN_ROCKITT_WHITE_ROOM_2)
        self.timetable.append(LSN_CREAK_READING_ROOM_2)
        self.timetable.append(LSN_PLAYTIME_2)
        self.timetable.append(LSN_DINNER_WACKER)
        self.timetable.append(LSN_PLAYTIME_STAMPEDE_1)
        self.timetable.append(LSN_PLAYTIME_7)
        self.timetable.append(LSN_WACKER_EXAM_ROOM)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_EXAM_ROOM)
        else:
            self.timetable.append(LSN_REVISION_LIBRARY_3)
        self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_WITHIT_WHITE_ROOM)
        self.timetable.append(LSN_WACKER_MAP_ROOM)
        self.timetable.append(LSN_PLAYTIME_1)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_WHITE_ROOM)
        else:
            self.timetable.append(LSN_WACKER_EXAM_ROOM)
        self.timetable.append(LSN_WITHIT_MAP_ROOM_1)
        self.timetable.append(LSN_PLAYTIME_2)
        self.timetable.append(LSN_ROCKITT_WHITE_ROOM_1)
        self.timetable.append(LSN_CREAK_READING_ROOM_1)
        self.timetable.append(LSN_PLAYTIME_3)
        self.timetable.append(LSN_DINNER_WITHIT)
        self.timetable.append(LSN_PLAYTIME_STAMPEDE_1)
        self.timetable.append(LSN_PLAYTIME_7)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_READING_ROOM)
        else:
            self.timetable.append(LSN_WITHIT_WHITE_ROOM)
        self.timetable.append(LSN_REVISION_LIBRARY_1)
        self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_ROCKITT_WHITE_ROOM_2)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_WACKER_WHITE_ROOM)
        self.timetable.append(LSN_PLAYTIME_6)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_EXAM_ROOM)
        else:
            self.timetable.append(LSN_WACKER_READING_ROOM)
        self.timetable.append(LSN_CREAK_WHITE_ROOM)
        self.timetable.append(LSN_PLAYTIME_3)
        self.timetable.append(LSN_PLAYTIME_8)
        self.timetable.append(LSN_ROCKITT_READING_ROOM)
        self.timetable.append(LSN_WACKER_MAP_ROOM)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_DINNER_WACKER)
        self.timetable.append(LSN_PLAYTIME_STAMPEDE_2)
        self.timetable.append(LSN_CREAK_READING_ROOM_2)
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.timetable.append(LSN_TAKE_MAP_ROOM)
        else:
            self.timetable.append(LSN_ROCKITT_EXAM_ROOM)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_PLAYTIME_1)
        self.timetable.append(LSN_WITHIT_WHITE_ROOM)
        self.timetable.append(LSN_ROCKITT_READING_ROOM)

    def create_special_playtimes(self):
        self.special_playtimes = []
        self.special_playtimes.append(LSN_PLAYTIME_MUMPS)
        self.special_playtimes.append(LSN_PLAYTIME_SWOT_GRASS)
        self.special_playtimes.append(LSN_PLAYTIME_PEA_SHOOTER)

    def create_skool_locations(self):
        walkabout_locations = []
        other_locations = []

        walkabout_locations.append(( 8,  3, LOC_HEADS_STUDY_0))
        walkabout_locations.append((24,  3, LOC_PEA_SHOOTER_RACE_1))
        walkabout_locations.append((35,  3, LOC_REVISION_LIBRARY_0))
        walkabout_locations.append((36,  3, LOC_REVISION_LIBRARY_1))
        walkabout_locations.append((42,  3, LOC_PEA_SHOOTER_RACE_0))
        walkabout_locations.append((53,  3, LOC_READING_ROOM_0))
        walkabout_locations.append((54,  3, LOC_READING_ROOM_1))
        walkabout_locations.append((55,  3, LOC_READING_ROOM_2))
        walkabout_locations.append((65,  3, LOC_MAP_ROOM_0))
        walkabout_locations.append((67,  3, LOC_MAP_ROOM_1))
        walkabout_locations.append((68,  3, LOC_MAP_ROOM_2))
        walkabout_locations.append((93,  3, LOC_FIRE_ESCAPE_0))
        walkabout_locations.append(( 9, 10, LOC_STAFF_ROOM_0))
        walkabout_locations.append((36, 10, LOC_WHITE_ROOM_0))
        walkabout_locations.append((35, 10, LOC_WHITE_ROOM_1))
        walkabout_locations.append((34, 10, LOC_WHITE_ROOM_2))
        walkabout_locations.append((58, 10, LOC_EXAM_ROOM_0))
        walkabout_locations.append((59, 10, LOC_EXAM_ROOM_1))
        walkabout_locations.append((60, 10, LOC_EXAM_ROOM_2))
        walkabout_locations.append((61, 10, LOC_EXAM_ROOM_3))
        walkabout_locations.append(( 8, 17, LOC_BIG_WINDOW))
        walkabout_locations.append((45, 17, LOC_DINNER_HALL_0))
        walkabout_locations.append((46, 17, LOC_DINNER_HALL_1))
        walkabout_locations.append((93, 17, LOC_GYM))

        other_locations.append(( 3,  3, LOC_HEADS_STUDY_WINDOW))
        other_locations.append(( 6,  3, LOC_HEADS_STUDY_DESK))
        other_locations.append((30,  3, LOC_REVISION_LIBRARY))
        other_locations.append((40,  3, LOC_READING_ROOM_DOORWAY))
        other_locations.append((45,  3, LOC_READING_ROOM_BOARD))
        other_locations.append((50,  3, LOC_READING_ROOM_BOARD_EDGE))
        other_locations.append((52,  3, LOC_READING_ROOM))
        other_locations.append((60,  3, LOC_MAP_ROOM_MAP))
        other_locations.append((62,  3, LOC_MAP_ROOM_MAP_EDGE))
        other_locations.append((74,  3, LOC_MAP_ROOM_DOORWAY))
        other_locations.append((90,  3, LOC_FIRE_ESCAPE))
        other_locations.append(( 8, 10, LOC_STAFF_ROOM))
        other_locations.append((22, 10, LOC_WHITE_ROOM_DOORWAY))
        other_locations.append((30, 10, LOC_WHITE_ROOM_BOARD))
        other_locations.append((34, 10, LOC_WHITE_ROOM_BOARD_EDGE))
        other_locations.append((35, 10, LOC_WHITE_ROOM))
        other_locations.append((45, 10, LOC_EXAM_ROOM_BOARD))
        other_locations.append((49, 10, LOC_EXAM_ROOM_BOARD_EDGE))
        other_locations.append((70, 10, LOC_EXAM_ROOM_DOORWAY))
        other_locations.append((33, 17, LOC_DINNER_HALL_NEAR_END))
        other_locations.append((62, 17, LOC_DINNER_HALL_FAR_END))

        if self.custom == EZAD_LOOKS:
            for i, (x, y, loc_id) in enumerate(walkabout_locations):
                walkabout_locations[i] = (100 - x, y, loc_id)
            for i, (x, y, loc_id) in enumerate(other_locations):
                other_locations[i] = (93 - x, y, loc_id)

        self.skool_locations = walkabout_locations + other_locations

    def create_rooms(self):
        self.rooms = []
        self.rooms.append((READING_ROOM, 'READING ROOM', (40, 0), (56, 6), 'Y'))
        self.rooms.append((MAP_ROOM, 'MAP ROOM', (58, 0), (73, 6), 'Y'))
        self.rooms.append((WHITE_ROOM, 'WHITE ROOM', (22, 7), (37, 13), 'Y'))
        self.rooms.append((EXAM_ROOM, 'EXAM ROOM', (39, 7), (69, 13), 'Y'))
        self.rooms.append((DINNER_HALL, 'DINNER', (34, 14), (50, 20), 'N'))
        if self.custom == EZAD_LOOKS:
            for i, (room_id, name, top_left, bottom_right, get_along) in enumerate(self.rooms):
                new_top_left = (93 - bottom_right[0], top_left[1])
                new_bottom_right = (93 - top_left[0], bottom_right[1])
                self.rooms[i] = (room_id, name, new_top_left, new_bottom_right, get_along)

    def create_chairs(self):
        self.chairs = []
        self.chairs.append((READING_ROOM, 48, 50, 52, 54, 56))
        self.chairs.append((MAP_ROOM, 64, 66, 68, 70, 72))
        self.chairs.append((WHITE_ROOM, 29, 31, 33, 35, 37))
        self.chairs.append((EXAM_ROOM, 43, 45, 47, 49, 51, 53, 60, 62, 64, 66, 68))
        if self.custom == EZAD_LOOKS:
            for i, chair in enumerate(self.chairs):
                self.chairs[i] = [chair[0]] + [93 - x for x in chair[1:]]

    def create_walls(self):
        self.walls = []
        self.walls.append(('FarLeftWall', 0, 20, 0))   # Far left wall
        self.walls.append(('FarRightWall', 96, 20, 0)) # Far right wall
        if self.custom == EZAD_LOOKS:
            self.walls.append(('MiddleWall', 15, 13, 7))
            self.walls.append(('MapRoomWall', 37, 6, 0))
            self.walls.append(('ExamRoomWall', 56, 13, 7))
        else:
            self.walls.append(('MiddleWall', 80, 13, 7))   # Wall outside Exam Room
            self.walls.append(('MapRoomWall', 58, 6, 0))   # Wall between Map and Reading Rooms
            self.walls.append(('ExamRoomWall', 39, 13, 7)) # Wall between White and Exam Rooms

    def create_staircases(self):
        self.staircases = []
        self.staircases.append(('%s:%s' % SC_UP_TO_STAFF_ROOM, (19, 17), (12, 10)))
        self.staircases.append(('%s:%s' % SC_UP_TO_STUDY, (19, 10), (12, 3)))
        self.staircases.append(('%s:%s' % SC_UP_TO_EXAM_ROOM, (70, 17), (77, 10)))
        self.staircases.append(('%s:%s' % SC_UP_TO_MAP_ROOM, (70, 10), (77, 3)))
        if self.custom == EZAD_LOOKS:
            for i, (staircase_id, bottom, top) in enumerate(self.staircases):
                self.staircases[i] = (staircase_id, (93 - bottom[0], bottom[1]), (93 - top[0], top[1]))

    def create_floors(self):
        self.floors = []
        self.floors.append((FLR_BOTTOM, 0, 95, 17))
        if self.custom == EZAD_LOOKS:
            self.floors.append((FLR_LEFT_MIDDLE, 15, 55, 10))
            self.floors.append((FLR_RIGHT_MIDDLE, 56, 95, 10))
            self.floors.append((FLR_LEFT_TOP, 0, 36, 3))
            self.floors.append((FLR_RIGHT_TOP, 37, 95, 3))
        else:
            self.floors.append((FLR_LEFT_MIDDLE, 0, 38, 10))
            self.floors.append((FLR_RIGHT_MIDDLE, 39, 79, 10))
            self.floors.append((FLR_LEFT_TOP, 0, 56, 3))
            self.floors.append((FLR_RIGHT_TOP, 58, 95, 3))

    def create_routes(self):
        self.routes = {}

        bottom_routes = self.routes.setdefault(FLR_BOTTOM, [])
        if self.custom == EZAD_LOOKS:
            bottom_routes.append((FLR_RIGHT_MIDDLE, FLR_RIGHT_TOP, SC_UP_TO_STAFF_ROOM[0]))
        else:
            bottom_routes.append((FLR_LEFT_MIDDLE, FLR_LEFT_TOP, SC_UP_TO_STAFF_ROOM[0]))
        bottom_routes.append(('*', SC_UP_TO_EXAM_ROOM[0]))

        left_middle_routes = self.routes.setdefault(FLR_LEFT_MIDDLE, [])
        if self.custom == EZAD_LOOKS:
            left_middle_routes.append((FLR_LEFT_TOP, SC_UP_TO_MAP_ROOM[0]))
            left_middle_routes.append(('*', SC_UP_TO_EXAM_ROOM[1]))
        else:
            left_middle_routes.append((FLR_LEFT_TOP, SC_UP_TO_STUDY[0]))
            left_middle_routes.append(('*', SC_UP_TO_STAFF_ROOM[1]))

        right_middle_routes = self.routes.setdefault(FLR_RIGHT_MIDDLE, [])
        if self.custom == EZAD_LOOKS:
            right_middle_routes.append((FLR_RIGHT_TOP, SC_UP_TO_STUDY[0]))
            right_middle_routes.append(('*', SC_UP_TO_STAFF_ROOM[1]))
        else:
            right_middle_routes.append((FLR_RIGHT_TOP, SC_UP_TO_MAP_ROOM[0]))
            right_middle_routes.append(('*', SC_UP_TO_EXAM_ROOM[1]))

        if self.custom == EZAD_LOOKS:
            self.routes[FLR_LEFT_TOP] = [('*', SC_UP_TO_MAP_ROOM[1])]
            self.routes[FLR_RIGHT_TOP] = [('*', SC_UP_TO_STUDY[1])]
        else:
            self.routes[FLR_LEFT_TOP] = [('*', SC_UP_TO_STUDY[1])]
            self.routes[FLR_RIGHT_TOP] = [('*', SC_UP_TO_MAP_ROOM[1])]

    def create_no_go_zones(self):
        self.no_go_zones = []
        if self.custom == EZAD_LOOKS:
            self.no_go_zones.append(('HeadsStudy', 86, 95, 3, 0))
            self.no_go_zones.append(('StaffRoom', 83, 95, 10, 4))
        else:
            self.no_go_zones.append(('HeadsStudy', 0, 7, 3, 0))
            self.no_go_zones.append(('StaffRoom', 0, 10, 10, 4))

    def create_message_config(self):
        skoolini.SkoolIniMaker.create_message_config(self)
        self.message_config.append(('LinesMessageTemplate', '%s lines^%s' % (NUMBER_OF_LINES_MACRO, LINES_RECIPIENT_MACRO)))
        self.message_config.append(('BoardDirtyConditionId', BOARD_DIRTY))
        self.message_config.append(('UpAYearMessage', 'WELL DONE! GO^UP A YEAR'))

    def create_sit_down_messages(self):
        self.sit_down_messages = []
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.sit_down_messages.append((WACKER, "SILENCE! OR I'LL EXPEL THE LOT OF YOU"))
            self.sit_down_messages.append((ROCKITT, "OK! SIT DOWN MY FINE YOUNG FELLOWS"))
            self.sit_down_messages.append((WITHIT, "COME ON LADS - SIT YE DOWN"))
            self.sit_down_messages.append((CREAK, "BE QUIET AND SEATED YOU LITTLE SCUMBAGS"))
            self.sit_down_messages.append((TAKE, "OK BOYS - BUMS ON SEATS PLEASE"))
        elif self.custom == EZAD_LOOKS:
            self.sit_down_messages.append((WACKER, "FIVE MONTHS' DETENTION FOR ANYONE WHO DOESN'T SHUT UP AND SIT DOWN"))
            self.sit_down_messages.append((ROCKITT, "AHEM! SIT DOWN MY LITTLE ANGELS"))
            self.sit_down_messages.append((WITHIT, "OK CHAPS - TAKE YOUR SEATS"))
            self.sit_down_messages.append((CREAK, "SIT DOWN AND BE QUIET - NOW!"))
        else:
            self.sit_down_messages.append((WACKER, "SILENCE! OR I'LL CANE THE LOT OF YOU"))
            self.sit_down_messages.append((ROCKITT, 'RIGHT! SIT DOWN MY LITTLE CHERUBS'))
            self.sit_down_messages.append((WITHIT, 'COME ON CHAPS - SETTLE DOWN'))
            self.sit_down_messages.append((CREAK, 'BE QUIET AND SEATED YOU NASTY LITTLE BOYS'))

    def create_blackboards(self):
        self.blackboards = []
        chalk = (255, 255, 255)
        size = (8, 2)
        self.blackboards.append((READING_ROOM, (42, 3), size, chalk))
        self.blackboards.append((WHITE_ROOM, (26, 9), size, chalk))
        self.blackboards.append((EXAM_ROOM, (41, 9), size, chalk))
        if self.custom == EZAD_LOOKS:
            for i, (board_id, coords, width, chalk) in enumerate(self.blackboards):
                self.blackboards[i] = (board_id, (88 - coords[0], coords[1]), size, chalk)

    def create_blackboard_messages(self):
        self.blackboard_messages = {}

        tearaway_messages = self.blackboard_messages.setdefault(TEARAWAY, [])
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            tearaway_messages.append("i hate^kemistri")
            tearaway_messages.append("who's^$%s?" % TAKE)
            tearaway_messages.append("catapults^r fun")
            tearaway_messages.append("i love^Pyskool")
            tearaway_messages.append("$%s^smells orfle" % CREAK)
            tearaway_messages.append("liar liar^pants on fire")
            tearaway_messages.append("$%s^is a nob" % SWOT)
            tearaway_messages.append("i love lines")
        elif self.custom == EZAD_LOOKS:
            tearaway_messages.append("i love ritin^on bordz")
            tearaway_messages.append("$%s^is ugly" % BULLY)
            tearaway_messages.append("looks etah i")
            tearaway_messages.append("Pellets for^Fun & Profit")
            tearaway_messages.append("$%s^eats babies" % WACKER)
            tearaway_messages.append("bring bak^caning")
            tearaway_messages.append("i love^biskits")
            tearaway_messages.append("i'll get my^coat")
        else:
            tearaway_messages.append('i hate^fizziks')
            tearaway_messages.append('i hate sums')
            tearaway_messages.append('skool rools^o k')
            tearaway_messages.append('i hate skool')
            tearaway_messages.append('speling iz^boaring')
            tearaway_messages.append('i love^WHEELIE')
            tearaway_messages.append('SKYRANGER^is grate')
            tearaway_messages.append('skool dinners^are orrible')

        wacker_messages = self.blackboard_messages.setdefault(WACKER, [])
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            wacker_messages.append("CUBIC^EQUATIONS")
            wacker_messages.append("THE RIEMANN^HYPOTHESIS")
            wacker_messages.append("EQUILATERAL^TRIANGLES")
            wacker_messages.append("EULER'S^IDENTITY")
            wacker_messages.append("THE VOLUME^OF A SPHERE")
            wacker_messages.append("COMPLEX^ANALYSIS")
            wacker_messages.append("IMAGINARY^NUMBERS")
            wacker_messages.append("PRIME^NUMBERS")
        elif self.custom == EZAD_LOOKS:
            wacker_messages.append("DIFFERENTIAL^CALCULUS")
            wacker_messages.append("INTEGRAL^CALCULUS")
            wacker_messages.append("THE LIFE OF e")
            wacker_messages.append("LOGARITHMS")
            wacker_messages.append("EUCLIDEAN^GEOMETRY")
            wacker_messages.append("TWIN PRIME^CONJECTURE")
            wacker_messages.append("NON-EUCLIDEAN^GEOMETRY")
            wacker_messages.append("FACTORIALS")
        else:
            wacker_messages.append('THE 47 TIMES^TABLE')
            wacker_messages.append('QUADRATIC^EQUATIONS')
            wacker_messages.append('WHY SUMS ARE^FUN')
            wacker_messages.append('VECTORS AND^MATRICES')
            wacker_messages.append('ISOSCELES^TRIANGLES')
            wacker_messages.append('PYTHAGORAS^THEOREM')
            wacker_messages.append('FACTORS')
            wacker_messages.append('THE AREA OF^A CIRCLE')

        rockitt_messages = self.blackboard_messages.setdefault(ROCKITT, [])
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            rockitt_messages.append("Recreating^the Big Bang")
            rockitt_messages.append("Megatons^and gigatons")
            rockitt_messages.append("Black holes")
            rockitt_messages.append("Red dwarfs")
            rockitt_messages.append("TNT for^breakfast")
            rockitt_messages.append("Surviving a^supernova")
            rockitt_messages.append("Preparing for^the big crunch")
            rockitt_messages.append("A history of^nitroglycerine")
        elif self.custom == EZAD_LOOKS:
            rockitt_messages.append("DIY WMDs")
            rockitt_messages.append("Dynamite^for dinner")
            rockitt_messages.append("Living with^gelignite")
            rockitt_messages.append("The truth^about TNT")
            rockitt_messages.append("Quickstart^guide to C4")
            rockitt_messages.append("Detonation^velocity")
            rockitt_messages.append("How to catch^a quark")
            rockitt_messages.append("Particle^accelerators")
        else:
            rockitt_messages.append('The Periodic^Table')
            rockitt_messages.append('Splitting^The Atom')
            rockitt_messages.append('Explosions I^have known')
            rockitt_messages.append('How to blow^yourself up')
            rockitt_messages.append('Things to do^with TNT')
            rockitt_messages.append('Chemistry^of dynamite')
            rockitt_messages.append('First aid^for chemists')
            rockitt_messages.append('Fast ways to^open doors')

        withit_messages = self.blackboard_messages.setdefault(WITHIT, [])
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            withit_messages.append("TOTTENHAM^TORNADOES")
            withit_messages.append("HURRICANES^IN HACKNEY")
            withit_messages.append("THE EXPORTS^OF EGHAM")
            withit_messages.append("THE PEAKS OF^PADDINGTON")
            withit_messages.append("TV IN TUVALU")
            withit_messages.append("RADIO IN^ROTUMA")
            withit_messages.append("INTERNET IN^INDONESIA")
            withit_messages.append("IS MIDDLESEX^MIA?")
        elif self.custom == EZAD_LOOKS:
            withit_messages.append("MOUNTAINS^IN MARGATE")
            withit_messages.append("DUNTISBOURNE^ABBOTS")
            withit_messages.append("TRINIDAD^AND TOBAGO")
            withit_messages.append("SAINT KITTS^AND NEVIS")
            withit_messages.append("CRISPS IN^CUBA")
            withit_messages.append("FISH PUNS^IN FINLAND")
            withit_messages.append("ROLOS IN^ROMANIA")
            withit_messages.append("KNOWN LIARS^IN KNEBWORTH")
        else:
            withit_messages.append('MANCHESTER^MONSOONS')
            withit_messages.append('THE CLIMATE^OF CLAPHAM')
            withit_messages.append('THE PEAKS^OF PERU')
            withit_messages.append('THE GLASGOW^RAIN-FOREST')
            withit_messages.append('THE EXPORTS^OF FIJI')
            withit_messages.append('ACTIVE^VOLCANOES')
            withit_messages.append('POP MUSIC IN^ANTARCTICA')
            withit_messages.append('THE UPLANDS^OF RUTLAND')

        creak_messages = self.blackboard_messages.setdefault(CREAK, [])
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            creak_messages.append("Pyskool 0.0.1")
            creak_messages.append("Dinosaurs I^have known")
            creak_messages.append("The Roman^Empire")
            creak_messages.append("The French^Revolution")
            creak_messages.append("Christopher^Columbus")
            creak_messages.append("The Treaty^of Westphalia")
            creak_messages.append("Julius^Caesar")
            creak_messages.append("Sir Francis^Drake")
        elif self.custom == EZAD_LOOKS:
            creak_messages.append("Dinner with^Dickens")
            creak_messages.append("Breakfast^with Brecht")
            creak_messages.append("Lunch with^Le Corbusier")
            creak_messages.append("Tea with^Mark Twain")
            creak_messages.append("Supper with^Shakespeare")
            creak_messages.append("Elevenses^with Euclid")
            creak_messages.append("Midnight snack^with Mozart")
            creak_messages.append("Brunch with^Beckett")
        else:
            creak_messages.append('Industrial^Revolution')
            creak_messages.append('The Norman^Conquest')
            creak_messages.append('The Wars of^the Roses')
            creak_messages.append('The Spanish^Armada')
            creak_messages.append('The First^Crusade')
            creak_messages.append('Magna Carta')
            creak_messages.append('The Boston^Tea Party')
            creak_messages.append('The Black^Death')

        if self.custom == SKOOL_DAZE_TAKE_TOO:
            take_messages = self.blackboard_messages.setdefault(TAKE, [])
            take_messages.append('THE MEANING^OF LIFE')
            take_messages.append('ARISTOTELIAN^LOGIC')
            take_messages.append('ARTIFICIAL^INTELLIGENCE')
            take_messages.append('TO BE OR^NOT TO BE')
            take_messages.append("ZENO'S^PARADOXES")
            take_messages.append('METAPHYSICS^FOR DUMMIES')
            take_messages.append('BLUE PILL^OR RED PILL?')
            take_messages.append('HOW TO SPELL^SCHOPENHAUER')

    def create_questions_and_answers(self):
        self.questions_and_answers = {}

        creak_specials = []
        creak_qa_group = 'Battles'
        creak_specials.append((creak_qa_group, 0))
        creak_specials.append('WHAT HAPPENED IN THE YEAR THAT I WAS BORN?')
        creak_specials.append('Please %s I cannot tell a lie . . it was the battle of $2' % TITLE_MACRO)
        creak_questions = []
        creak_questions.append(('Q1', creak_qa_group, 'WHEN WAS THE BATTLE OF $2?'))
        creak_questions.append(('Q2', creak_qa_group, 'WHICH BATTLE OCCURRED IN $1?'))
        creak_answers = []
        creak_answers.append(('Q1', 'Please %s I cannot tell a lie . . it was in $1' % TITLE_MACRO))
        creak_answers.append(('Q2', 'Please %s I cannot tell a lie . . it was the battle of $2' % TITLE_MACRO))
        creak_qa_pairs = []
        creak_qa_pairs.append((creak_qa_group, '1066', 'Hastings'))
        creak_qa_pairs.append((creak_qa_group, '1265', 'Evesham'))
        creak_qa_pairs.append((creak_qa_group, '1314', 'Bannockburn'))
        creak_qa_pairs.append((creak_qa_group, '1346', 'Crecy'))
        creak_qa_pairs.append((creak_qa_group, '1356', 'Poitiers'))
        creak_qa_pairs.append((creak_qa_group, '1403', 'Shrewsbury'))
        creak_qa_pairs.append((creak_qa_group, '1415', 'Agincourt'))
        creak_qa_pairs.append((creak_qa_group, '1485', 'Bosworth'))
        creak_qa_pairs.append((creak_qa_group, '1513', 'Flodden'))
        creak_qa_pairs.append((creak_qa_group, '1571', 'Lepanto'))
        creak_qa_pairs.append((creak_qa_group, '1014', 'Clontarf'))
        creak_qa_pairs.append((creak_qa_group, '1685', 'Sedgemoor'))
        creak_qa_pairs.append((creak_qa_group, '1746', 'Culloden'))
        creak_qa_pairs.append((creak_qa_group, '1775', 'Lexington'))
        creak_qa_pairs.append((creak_qa_group, '1781', 'Yorktown'))
        creak_qa_pairs.append((creak_qa_group, '1805', 'Trafalgar'))
        creak_qa_pairs.append((creak_qa_group, '1815', 'Waterloo'))
        creak_qa_pairs.append((creak_qa_group, '1812', 'Borodino'))
        creak_qa_pairs.append((creak_qa_group, '1836', 'San Jacinto'))
        creak_qa_pairs.append((creak_qa_group, '1863', 'Gettysburg'))
        creak_qa_pairs.append((creak_qa_group, '1854', 'Balaclava'))

        withit_questions = []
        withit_qa_group = 'CapitalCities'
        withit_questions.append(('Q1', withit_qa_group, "WHAT'S THE CAPITAL OF $2?"))
        withit_questions.append(('Q2', withit_qa_group, "WHICH COUNTRY'S CAPITAL IS $1?"))
        withit_answers = []
        withit_answers.append(('Q1', 'Please %s I cannot tell a lie . . it is $1' % TITLE_MACRO))
        withit_answers.append(('Q2', 'Please %s I cannot tell a lie . . it is $2' % TITLE_MACRO))
        withit_qa_pairs = []
        withit_qa_pairs.append((withit_qa_group, 'Berne', 'Switzerland'))
        withit_qa_pairs.append((withit_qa_group, 'Helsinki', 'Finland'))
        withit_qa_pairs.append((withit_qa_group, 'Reykjavik', 'Iceland'))
        withit_qa_pairs.append((withit_qa_group, 'Budapest', 'Hungary'))
        withit_qa_pairs.append((withit_qa_group, 'Bucharest', 'Romania'))
        withit_qa_pairs.append((withit_qa_group, 'Tirana', 'Albania'))
        withit_qa_pairs.append((withit_qa_group, 'Jakarta', 'Indonesia'))
        withit_qa_pairs.append((withit_qa_group, 'Pyongyang', 'North Korea'))
        withit_qa_pairs.append((withit_qa_group, 'Vientiane', 'Laos'))
        withit_qa_pairs.append((withit_qa_group, 'Islamabad', 'Pakistan'))
        withit_qa_pairs.append((withit_qa_group, 'Rangoon', 'Burma'))
        withit_qa_pairs.append((withit_qa_group, 'Ankara', 'Turkey'))
        withit_qa_pairs.append((withit_qa_group, 'Amman', 'Jordan'))
        withit_qa_pairs.append((withit_qa_group, 'Gabarone', 'Botswana'))
        withit_qa_pairs.append((withit_qa_group, 'Lusaka', 'Zambia'))
        withit_qa_pairs.append((withit_qa_group, 'Monrovia', 'Liberia'))
        withit_qa_pairs.append((withit_qa_group, 'La Paz', 'Bolivia'))
        withit_qa_pairs.append((withit_qa_group, 'Caracas', 'Venezuela'))
        withit_qa_pairs.append((withit_qa_group, 'Quito', 'Ecuador'))
        withit_qa_pairs.append((withit_qa_group, 'Paramaribo', 'Surinam'))
        withit_qa_pairs.append((withit_qa_group, 'Santiago', 'Chile'))

        rockitt_questions = []
        rockitt_qa_group = 'Elements'
        rockitt_questions.append(('Q1', rockitt_qa_group, 'WHAT ELEMENT HAS THE SYMBOL $1?'))
        rockitt_questions.append(('Q2', rockitt_qa_group, 'WHAT IS THE CHEMICAL SYMBOL FOR $2?'))
        rockitt_answers = []
        rockitt_answers.append(('Q1', 'Please %s I cannot tell a lie . . it is $2' % TITLE_MACRO))
        rockitt_answers.append(('Q2', 'Please %s I cannot tell a lie . . it is $1' % TITLE_MACRO))
        rockitt_qa_pairs = []
        rockitt_qa_pairs.append((rockitt_qa_group, 'Sn', 'Tin'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Hg', 'Mercury'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Au', 'Gold'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Ag', 'Silver'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Pt', 'Platinum'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Cu', 'Copper'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Mg', 'Magnesium'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Pb', 'Lead'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Mn', 'Manganese'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Sb', 'Antimony'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'As', 'Arsenic'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'K', 'Potassium'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Na', 'Sodium'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Cl', 'Chlorine'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Zn', 'Zinc'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'W', 'Tungsten'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Cs', 'Caesium'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Si', 'Silicon'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'P', 'Phosphorus'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'Br', 'Bromine'))
        rockitt_qa_pairs.append((rockitt_qa_group, 'H', 'Hydrogen'))

        wacker_questions = []
        wacker_qa_group = 'Sums'
        wacker_questions.append(('Q1', wacker_qa_group, 'WHAT IS $1?'))
        wacker_answers = []
        wacker_answers.append(('Q1', 'Please %s I cannot tell a lie . . it is $2' % TITLE_MACRO))
        wacker_qa_pairs = []
        wacker_qa_pairs.append((wacker_qa_group, '12x34', '408'))
        wacker_qa_pairs.append((wacker_qa_group, '89x49', '4361'))
        wacker_qa_pairs.append((wacker_qa_group, '30x46', '1380'))
        wacker_qa_pairs.append((wacker_qa_group, '87x89', '7743'))
        wacker_qa_pairs.append((wacker_qa_group, '51x38', '1938'))
        wacker_qa_pairs.append((wacker_qa_group, '38x28', '1064'))
        wacker_qa_pairs.append((wacker_qa_group, '35x48', '1680'))
        wacker_qa_pairs.append((wacker_qa_group, '23x81', '1863'))
        wacker_qa_pairs.append((wacker_qa_group, '62x40', '2480'))
        wacker_qa_pairs.append((wacker_qa_group, '39x58', '2262'))
        wacker_qa_pairs.append((wacker_qa_group, '49x48', '2352'))
        wacker_qa_pairs.append((wacker_qa_group, '86x59', '5074'))
        wacker_qa_pairs.append((wacker_qa_group, '94x93', '8742'))
        wacker_qa_pairs.append((wacker_qa_group, '64x58', '3712'))
        wacker_qa_pairs.append((wacker_qa_group, '52x74', '3848'))
        wacker_qa_pairs.append((wacker_qa_group, '33x68', '2244'))
        wacker_qa_pairs.append((wacker_qa_group, '49x11', '539'))
        wacker_qa_pairs.append((wacker_qa_group, '64x10', '640'))
        wacker_qa_pairs.append((wacker_qa_group, '43x82', '3526'))
        wacker_qa_pairs.append((wacker_qa_group, '40x95', '3800'))
        wacker_qa_pairs.append((wacker_qa_group, '72x83', '5976'))
        wacker_qa_pairs.append((wacker_qa_group, '23x54', '1242'))

        if self.custom == SKOOL_DAZE_TAKE_TOO:
            take_questions = []
            take_qa_group = 'Misc'
            take_questions.append(('Q1', take_qa_group, '$1'))
            take_answers = []
            take_answers.append(('Q1', 'Please %s I cannot tell a lie . . $2' % TITLE_MACRO))
            take_qa_pairs = []
            take_qa_pairs.append((take_qa_group, '"What is the answer to the ultimate question of life, the universe and everything?"', 'it is 42'))
            take_qa_pairs.append((take_qa_group, '"If a tree falls in the woods, and no one is around to hear it, does it make a sound?"', 'yes it does'))
            take_qa_pairs.append((take_qa_group, 'This statement is false. Is that true?', "I'm not sure"))
            take_qa_pairs.append((take_qa_group, 'What is 5 + 7?', 'I thought this was a philosophy lesson'))
            take_qa_pairs.append((take_qa_group, 'Describe the nature of free will', 'I cannot do that in one sentence'))
            take_qa_pairs.append((take_qa_group, "Is Schrodinger's cat dead or alive?", 'yes it is'))
            take_qa_pairs.append((take_qa_group, '"If the barber shaves every man who does not shave himself, who shaves the barber?"', '"no one does, because the barber is a woman"'))
            take_qa_pairs.append((take_qa_group, '"If the forecast says there is a 40% chance of rain and it does rain, was the forecast correct?"', 'the laws of probability do not apply to single events'))
            take_qa_pairs.append((take_qa_group, 'What would the world be like without any hypothetical situations?', 'I cannot begin to imagine'))

        self.questions_and_answers[CREAK] = [creak_specials, creak_questions, creak_answers, creak_qa_pairs]
        self.questions_and_answers[WITHIT] = [[], withit_questions, withit_answers, withit_qa_pairs]
        self.questions_and_answers[ROCKITT] = [[], rockitt_questions, rockitt_answers, rockitt_qa_pairs]
        self.questions_and_answers[WACKER] = [[], wacker_questions, wacker_answers, wacker_qa_pairs]
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.questions_and_answers[TAKE] = [[], take_questions, take_answers, take_qa_pairs]

    def create_lines_messages(self):
        self.lines_messages = []
        self.lines_messages.append(('*', lines.NO_SITTING_ON_STAIRS, "DON'T SIT ON^THE STAIRS"))
        self.lines_messages.append(('*', lines.GET_OUT, 'THE ROOM IS^PRIVATE'))
        self.lines_messages.append(('*', lines.GET_ALONG, 'GET TO WHERE^YOU SHOULD BE'))
        self.lines_messages.append(('*', lines.SIT_DOWN, 'NOW FIND^A SEAT'))
        self.lines_messages.append(('*', lines.GET_UP, 'GET OFF^THE FLOOR'))
        self.lines_messages.append(('*', '%s_1' % lines.COME_ALONG_PREFIX, 'COME ALONG^WITH ME BOY'))
        self.lines_messages.append(('*', '%s_2' % lines.COME_ALONG_PREFIX, 'HURRY UP YOU^HORROR'))
        self.lines_messages.append(('*', '%s_3' % lines.COME_ALONG_PREFIX, "DON'T TRY MY^PATIENCE BOY"))
        self.lines_messages.append(('*', lines.NEVER_AGAIN, "NOW DON'T^DO IT AGAIN"))
        self.lines_messages.append(('*', lines.NO_TALES, "DON'T TELL^TALES"))
        self.lines_messages.append(('*', lines.BE_PUNCTUAL, 'NEVER BE^LATE AGAIN'))
        self.lines_messages.append(('*', lines.STAY_IN_CLASS, 'AND STAY^THIS TIME'))
        self.lines_messages.append(('*', lines.NO_WRITING, "DON'T TOUCH^BLACKBOARDS"))
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.lines_messages.append((TAKE, lines.NO_CATAPULTS, 'PUT THAT^AWAY NOW'))
        self.lines_messages.append(('*', lines.NO_CATAPULTS, 'CATAPULTS^ARE FORBIDDEN'))
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.lines_messages.append((TAKE, lines.NO_HITTING, 'BE GENTLE^PLEASE'))
        self.lines_messages.append(('*', lines.NO_HITTING, "DON'T HIT^YOUR MATES"))
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.lines_messages.append((TAKE, lines.NO_JUMPING, 'NO JUMPING^PLEASE'))
        self.lines_messages.append(('*', lines.NO_JUMPING, 'YOU ARE NOT^A KANGAROO'))

    def create_lesson_messages(self):
        self.lesson_messages = []
        if self.custom == SKOOL_DAZE_TAKE_TOO:
            self.lesson_messages.append(('*', '"READ PAGES $(25, 40) TO $(45, 60) OF YOUR LOVELY TEXTBOOK"'))
            self.lesson_messages.append(('*', '"WRITE A $(30, 79)-PAGE ESSAY WITH THIS TITLE"', BOARD_DIRTY))
            self.lesson_messages.append(('*', '"WRITE DOWN THESE WISE WORDS $(50, 99) TIMES IN YOUR EXERCISE BOOKS, AND PONDER THEM UNTIL THE BELL RINGS"', BOARD_DIRTY))
        elif self.custom == EZAD_LOOKS:
            self.lesson_messages.append((CREAK, "WRITE AN ESSAY TITLED 'WHY I HATE THE FUTURE'"))
            self.lesson_messages.append((WITHIT, "WRITE AN ESSAY TITLED 'WHY I LOVE THE RAINSHADOW EFFECT'"))
            self.lesson_messages.append((ROCKITT, "WRITE AN ESSAY TITLED 'WHY I LOVE GUNPOWDER'"))
            self.lesson_messages.append((WACKER, "WRITE AN ESSAY TITLED 'WHY I WANT TO BE A NUMBER'"))
            self.lesson_messages.append(('*', '"START READING AT PAGE $(50, 499) OF YOUR BOOKS"'))
        else:
            self.lesson_messages.append(('*', '"TURN TO PAGE $(100, 999) OF YOUR BOOKS, BE SILENT AND START READING"'))
            self.lesson_messages.append(('*', '"ANSWER THE QUESTIONS ON PAGE $(100, 999) OF YOUR LOVELY TEXTBOOK"'))
            self.lesson_messages.append(('*', 'WRITE AN ESSAY WITH THIS TITLE', BOARD_DIRTY))

    def create_shields(self):
        size = (1, 1)
        self.shields = []
        self.shields.append((100, ( 0, 0), size, ( 6,  2)))
        self.shields.append((100, ( 2, 0), size, ( 8,  2)))
        self.shields.append((100, ( 4, 0), size, (47,  2)))
        self.shields.append((100, ( 6, 0), size, (50,  2)))
        self.shields.append((100, ( 8, 0), size, (78,  2)))
        self.shields.append((200, (10, 0), size, (45,  8)))
        self.shields.append((200, (12, 0), size, (50,  8)))
        self.shields.append((200, (10, 0), size, (55,  8)))
        self.shields.append((200, ( 8, 0), size, (60,  8)))
        self.shields.append((200, (10, 0), size, (65,  8)))
        self.shields.append((400, ( 6, 0), size, (26, 14)))
        self.shields.append((400, (10, 0), size, (28, 14)))
        self.shields.append((400, ( 4, 0), size, (30, 14)))
        self.shields.append((400, (14, 0), size, (65, 14)))
        self.shields.append((400, (16, 0), size, (67, 14)))
        if self.custom == EZAD_LOOKS:
            for i, (score, top_left, image_size, coords) in enumerate(self.shields):
                self.shields[i] = (score, (18 - top_left[0], top_left[1]), image_size, (95 - coords[0], coords[1]))

    def create_safe(self):
        if self.custom == EZAD_LOOKS:
            self.safe = ((0, 0), (1, 1), (85, 9))
        else:
            self.safe = ((18, 0), (1, 1), (10, 9))
