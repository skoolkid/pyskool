# -*- coding: utf-8 -*-

# Copyright 2010, 2012-2015 Richard Dymond (rjdymond@gmail.com)
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

from .skoolini import SkoolIniMaker, BACK_TO_SKOOL, BACK_TO_SKOOL_DAZE
from .btstaps import BTSTapMaker
from .skoolids import *
from . import animatorystates as states
from . import graphics
from . import items
from . import lines
from . import skoolbuilder
from . import sound

# Animation phases
AP_FROG_TURN_ROUND = 'FrogTurnRound'
AP_FROG_SHORT_HOP = 'FrogShortHop'
AP_FROG_LONG_HOP = 'FrogLongHop'
AP_DESCENT_MIDDLE_WINDOW = 'DescentMiddleWindow'
AP_DESCENT_UPPER_WINDOW = 'DescentUpperWindow'
AP_CLIMB_SKOOL_GATE = 'ClimbSkoolGate'
AP_FLY_OVER_SKOOL_GATE = 'FlyOverSkoolGate'
AP_WATER = 'Water'
AP_STINKBOMB = 'Stinkbomb'

# Floor IDs
FLR_BOTTOM = 'Bottom'
FLR_STAGE = 'Stage'
FLR_LEFT_MIDDLE = 'LeftMiddle'
FLR_RIGHT_MIDDLE = 'RightMiddle'
FLR_GIRLS_MIDDLE = 'GirlsMiddle'
FLR_LEFT_TOP = 'LeftTop'
FLR_RIGHT_TOP = 'RightTop'
FLR_GIRLS_TOP = 'GirlsTop'

# Staircase IDs
SC_GIRLS_SKOOL_LOWER = 'GirlsSkoolLower'
SC_GIRLS_SKOOL_UPPER = 'GirlsSkoolUpper'
SC_UP_TO_TOILETS = ('UpToToilets', 'DownFromToilets')
SC_UP_TO_STAGE = ('UpToStage', 'DownFromStage')
SC_UP_FROM_STAGE = ('UpFromStage', 'DownToStage')
SC_UP_TO_LIBRARY = ('UpToLibrary', 'DownFromLibrary')
SC_UP_TO_STUDY = ('UpToStudy', 'DownFromStudy')

# Questions and answers (MR CREAK)
CREAK_QA = {
    BACK_TO_SKOOL: (
        (),
        (
            (
                'Kings',
                (
                    ('Q1', 'WHEN DID $1 BECOME KING?'),
                    ('Q2', 'WHO BECAME KING IN $2?')
                ),
                (
                    ('Q1', 'Please {0} I cannot tell a lie . . it was in $2'.format(TITLE_MACRO)),
                    ('Q2', 'Please {0} I cannot tell a lie . . it was KING $1'.format(TITLE_MACRO))
                ),
                (
                    ('JOHN', '1199'),
                    ('STEPHEN', '1135'),
                    ('JAMES I', '1603'),
                    ('GEORGE V', '1910'),
                    ('HENRY V', '1413'),
                    ('HENRY VII', '1485'),
                    ('GEORGE I', '1714'),
                    ('CHARLES I', '1625')
                ),
            ),
        )
    ),
    BACK_TO_SKOOL_DAZE: (
        (
            ('PrimeMinisters', 1),
            'WHO BECAME PRIME MINISTER IN THE YEAR THAT I WAS BORN?',
            'Please {0} I cannot tell a lie . . it was $1'.format(TITLE_MACRO)
        ),
        (
            (
                'PrimeMinisters',
                (
                    ('Q1', 'WHEN DID $1 BECOME PRIME MINISTER?'),
                    ('Q2', 'WHO BECAME PRIME MINISTER IN $2?')
                ),
                (
                    ('Q1', 'Please {0} I cannot tell a lie . . it was in $2'.format(TITLE_MACRO)),
                    ('Q2', 'Please {0} I cannot tell a lie . . it was $1'.format(TITLE_MACRO))
                ),
                (
                    ('SPENCER COMPTON', 1742),
                    ('WILLIAM CAVENDISH', 1756),
                    ('JOHN STUART', 1762),
                    ('WILLIAM PITT THE ELDER', 1766),
                    ('FREDERICK NORTH', 1770),
                    ('HENRY ADDINGTON', 1801),
                    ('CHARLES GREY', 1830),
                    ('ARCHIBALD PRIMROSE', 1894),
                    ('ARTHUR BALFOUR', 1902),
                    ('HERBERT HENRY ASQUITH', 1908)
                ),
            ),
        )
    )
}

# Questions and answers (MR ROCKITT)
ROCKITT_QA = {
    BACK_TO_SKOOL: (
        (),
        (
            (
                'AnimalHomes',
                (
                    ('Q1', 'WHERE DOES A$1 LIVE?'),
                    ('Q2', 'WHAT LIVES IN A$2?')
                ),
                (
                    ('Q1', 'Please {0} I cannot tell a lie . . it is A$2'.format(TITLE_MACRO)),
                    ('Q2', 'Please {0} I cannot tell a lie . . it is A$1'.format(TITLE_MACRO))
                ),
                (
                    ('" BADGER"', '" SET"'),
                    ('" SQUIRREL"', '" DREY"'),
                    ('" BEAVER"', '" LODGE"'),
                    ('" HARE"', '" FORM"'),
                    ('N EAGLE', 'N EYRIE'),
                    ('N OTTER', '" HOLT"'),
                    ('" BEE"', '" HIVE"'),
                    ('" BUG"', '" BAD PROGRAM"')
                ),
            ),
        )
    ),
    BACK_TO_SKOOL_DAZE: (
        (),
        (
            (
                'Bones',
                (
                    ('Q1', 'WHERE IN THE HUMAN BODY WOULD YOU FIND THE $1?'),
                ),
                (
                    ('Q1', 'Please {0} I cannot tell a lie . . it is $2'.format(TITLE_MACRO)),
                ),
                (
                    ('OCCIPITAL BONE', 'at the back of the head'),
                    ('MALLEUS', 'in the ear'),
                    ('ULNA', 'in the forearm'),
                    ('PATELLA', 'in the knee'),
                    ('NAVICULAR BONE', 'in the foot')
                ),
            ),
            (
                'Muscles',
                (
                    ('Q2', 'WHERE IN THE HUMAN BODY WOULD YOU FIND THE $1?'),
                ),
                (
                    ('Q2', 'Please {0} I cannot tell a lie . . it is in the $2'.format(TITLE_MACRO)),
                ),
                (
                    ('BICEPS', 'upper arm'),
                    ('GLUTEUS MAXIMUS', 'buttocks'),
                    ('QUADRICEPS', 'thigh'),
                    ('PECTORALIS MAJOR', 'chest'),
                    ('TIBIALIS ANTERIOR', 'lower leg')
                ),
            )
        )
    )
}

# Questions and answers (MR WITHIT)
WITHIT_QA = {
    BACK_TO_SKOOL: (
        (),
        (
            (
                'Mountains',
                (
                    ('Q1', 'WHERE IS MT. $1?'),
                    ('Q2', 'WHAT IS THE HIGHEST MOUNTAIN IN $2?')
                ),
                (
                    ('Q1', 'Please {0} I cannot tell a lie . . it is in $2'.format(TITLE_MACRO)),
                    ('Q2', 'Please {0} I cannot tell a lie . . it is MT. $1'.format(TITLE_MACRO))
                ),
                (
                    ('KILIMANJARO', 'TANZANIA'),
                    ('KOSCIUSKO', 'AUSTRALIA'),
                    ('McKINLEY', 'ALASKA'),
                    ('KOMMUNISMA', 'THE USSR'),
                    ('HUASCARAN', 'PERU'),
                    ('SAJAMA', 'BOLIVIA'),
                    ('COOK', 'NEW ZEALAND'),
                    ('SNOWDON', 'WALES')
                ),
            ),
        )
    ),
    BACK_TO_SKOOL_DAZE: (
        (),
        (
            (
                'Languages',
                (
                    ('Q1', 'WHAT IS THE OFFICIAL LANGUAGE OF $1?'),
                ),
                (
                    ('Q1', 'Please {0} I cannot tell a lie . . it is $2'.format(TITLE_MACRO)),
                ),
                (
                    ('BRAZIL', 'Portuguese'),
                    ('GUYANA', 'English'),
                    ('ISRAEL', 'Hebrew'),
                    ('QATAR', 'Arabic'),
                    ('MONACO', 'French'),
                    ('COSTA RICA', 'Spanish'),
                    ('SAN MARINO', 'Italian'),
                    ('BRUNEI', 'Malay'),
                    ('IRAN', 'Persian'),
                    ('SURINAME', 'Dutch')
                ),
            ),
        )
    )
}

class BTSIniMaker(SkoolIniMaker):
    def __init__(self, custom):
        SkoolIniMaker.__init__(self, custom)
        self.tap_maker = BTSTapMaker(custom)
        self.create_random_locations()
        self.hit_zone = 5
        self.teachers = ((CREAK, CREAK_QA), (WITHIT, WITHIT_QA), (ROCKITT, ROCKITT_QA))

    def get_random_locations(self, character_id):
        return self.random_locations[character_id]

    def create_random_locations(self):
        self.random_locations = {}
        self.random_locations[GIRL01] = ((129, 17), (144, 17), (136, 17), (189, 17))
        self.random_locations[GIRL02] = ((129, 17), (144, 17), (136, 17), (189, 17))
        self.random_locations[GIRL03] = ((129, 17), (144, 17), (136, 17), (189, 17))
        self.random_locations[GIRL04] = ((189, 17), (189, 10), (170, 17), (182, 3))
        self.random_locations[GIRL05] = ((189, 17), (189, 10), (170, 17), (182, 3))
        self.random_locations[GIRL06] = ((189, 17), (189, 10), (170, 17), (182, 3))
        self.random_locations[GIRL07] = ((189, 17), (189, 10), (170, 17), (182, 3))
        self.random_locations[BOY01] = ((38, 3), (10, 10), (10, 17), (66, 17))
        self.random_locations[BOY02] = ((38, 3), (10, 10), (10, 17), (66, 17))
        self.random_locations[BOY03] = ((38, 3), (10, 10), (10, 17), (66, 17))
        self.random_locations[BOY04] = ((38, 3), (10, 17), (109, 17), (75, 17))
        self.random_locations[BOY05] = ((38, 3), (10, 17), (109, 17), (75, 17))
        self.random_locations[BOY06] = ((38, 3), (10, 17), (109, 17), (75, 17))
        self.random_locations[BOY07] = ((38, 3), (10, 17), (109, 17), (75, 17))
        self.random_locations[BOY08] = ((38, 3), (10, 17), (109, 17), (75, 17))
        self.random_locations[BOY09] = ((112, 17), (145, 17), (158, 17), (37, 3))
        self.random_locations[BOY10] = ((112, 17), (145, 17), (158, 17), (37, 3))
        self.random_locations[WACKER] = ((157, 17), (38, 3), (10, 17), (92, 17))
        self.random_locations[WITHIT] = ((157, 17), (38, 3), (10, 17), (92, 17))
        self.random_locations[ROCKITT] = ((38, 3), (90, 3), (10, 17), (90, 17))
        self.random_locations[CREAK] = ((38, 3), (90, 3), (10, 17), (90, 17))
        self.random_locations[TAKE] = ((189, 17), (189, 10), (170, 17), (182, 3))
        self.random_locations[ALBERT] = ((112, 17), (145, 17), (158, 17), (37, 3))
        self.random_locations[TEARAWAY] = ((189, 10), (183, 17), (137, 17), (72, 17))
        self.random_locations[BULLY] = ((189, 10), (183, 17), (137, 17), (72, 17))
        self.random_locations[SWOT] = ((112, 17), (145, 17), (158, 17), (37, 3))
        self.random_locations[HEROINE] = ((129, 17), (144, 17), (136, 17), (189, 17))

    def create_game_config(self):
        SkoolIniMaker.create_game_config(self)
        save_game_dirs = {}
        save_game_dirs[BACK_TO_SKOOL] = 'back_to_skool'
        save_game_dirs[BACK_TO_SKOOL_DAZE] = 'back_to_skool_daze'
        self.game_config.append(('SaveGameDir', 'save/%s' % save_game_dirs[self.custom]))
        names = {}
        names[BACK_TO_SKOOL] = 'Back to Skool'
        names[BACK_TO_SKOOL_DAZE] = 'Back to Skool Daze'
        self.game_config.append(('Name', names[self.custom]))
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.game_config.append(('AllShieldsScore', 2000))
            self.game_config.append(('SafeOpenScore', 1000))
            self.game_config.append(('SafeSecrets', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.game_config.append(('BikeSecrets', '"0123456789"'))
        self.game_config.append(('StoreroomSecrets', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.game_config.append(('BikeCombinationScore', 1000))
        self.game_config.append(('StoreroomDoorId', STOREROOM_DOOR))
        self.game_config.append(('StoreroomCombinationScore', 1000))
        self.game_config.append(('SafeKeyScore', 2000))
        self.game_config.append(('UpAYearScore', 2000))
        self.game_config.append(('RestartOnYearEnd', 1))
        self.game_config.append(('PlayTuneOnRestart', 0 if self.custom == BACK_TO_SKOOL_DAZE else 1))
        self.game_config.append(('WindowProximity', 16))
        self.game_config.append(('DrinksCabinetDoorId', DRINKS_CABINET))
        self.game_config.append(('Playground', (96, 158)))
        self.game_config.append(('AssemblyHallId', ASSEMBLY_HALL))
        self.game_config.append(('AssemblySitDirection', 1))
        self.game_config.append(('KissCounter', 40))
        self.game_config.append(('KissCounterDecrement', 7))
        self.game_config.append(('KissCounterDeckrement', 1))
        self.game_config.append(('KissDistance', 2))
        self.game_config.append(('KissLines', 1000))
        self.game_config.append(('MouseCatchScore', 100))
        self.game_config.append(('MaxMiceRelease', 5))
        self.game_config.append(('MouseProximity', 5))
        self.game_config.append(('EvadeMouseDelay', 21))
        self.game_config.append(('ConkerClockTicks', 1200))
        self.game_config.append(('ConkerWakeTime', 200))
        self.game_config.append(('WaterId', 'WATER'))
        self.game_config.append(('SherryId', 'SHERRY'))

    def create_timetable_config(self):
        SkoolIniMaker.create_timetable_config(self)
        self.timetable_config.append(('AssemblyPrefix', ASSEMBLY_PREFIX))

    def create_lesson_config(self):
        SkoolIniMaker.create_lesson_config(self)
        self.lesson_config.append(('EricsTeacherWriteOnBoardProbability', 0.28125))
        self.lesson_config.append(('QASessionProbability', 0.90625))
        self.lesson_config.append(('GrassForHittingProbability', 0.140625))
        self.lesson_config.append(('LinesForTalesProbability', 0.328125))

    def create_timing_config(self):
        SkoolIniMaker.create_timing_config(self)
        self.timing_config.append(('BendOverDelay', 4))

    def create_screen_config(self):
        SkoolIniMaker.create_screen_config(self)
        self.screen_config.append(('InitialColumn', 120))
        self.screen_config.append(('EscapeAlarmInk', (197, 0, 0)))
        self.screen_config.append(('EscapeAlarmPaper', (197, 198, 0)))
        self.screen_config.append(('Background', (0, 0, 0)))
        self.screen_config.append(('LogoPos', (24, 21)))
        self.screen_config.append(('LessonBoxInk', (255, 255, 255)))
        self.screen_config.append(('LessonBoxPos', (16, 21)))
        self.screen_config.append(('ScoreBoxInk', (205, 198, 205)))
        self.screen_config.append(('ScoreBoxPos', (0, 21)))
        self.screen_config.append(('MouseInventoryInk', (205, 199, 205)))
        self.screen_config.append(('MouseInventoryPos', (8, 21)))
        self.screen_config.append(('MouseInventorySize', (8, 1)))
        self.screen_config.append(('InventoryKey', (0, 0, 0)))
        self.screen_config.append(('InventoryPos', (10, 23)))
        self.screen_config.append(('InventorySize', (6, 1)))

    def create_images(self):
        SkoolIniMaker.create_images(self)
        base_dir = 'back_to_skool'
        img_dir = 'back_to_skool_daze' if self.custom == BACK_TO_SKOOL_DAZE else base_dir
        self.images.append((graphics.LOGO, '%s/logo.png' % img_dir))
        self.images.append((graphics.MUTABLES, '%s/mutables.png' % img_dir))
        self.images.append((graphics.MUTABLES_INK, '%s/mutables_ink.png' % img_dir))
        self.images.append((graphics.MUTABLES_PAPER, '%s/mutables_paper.png' % img_dir))
        self.images.append((graphics.SKOOL, '%s/skool.png' % img_dir))
        self.images.append((graphics.SKOOL_INK, '%s/skool_ink.png' % img_dir))
        self.images.append((graphics.SKOOL_PAPER, '%s/skool_paper.png' % img_dir))
        self.images.append((graphics.INVENTORY, '%s/inventory.png' % base_dir))
        self.images.append((graphics.SPEECH_BUBBLE, '%s/bubble.png' % base_dir))
        self.images.append((graphics.LESSON_BOX, '%s/lesson_box.png' % base_dir))
        self.images.append((graphics.SCOREBOX, '%s/scorebox.png' % base_dir))
        message_box_dir = 'skool_daze' if self.custom == BACK_TO_SKOOL_DAZE else base_dir
        self.images.append((graphics.MESSAGE_BOX, '%s/message_box.png' % message_box_dir))

    def create_sounds(self):
        SkoolIniMaker.create_sounds(self)
        sounds_dir = 'back_to_skool'
        tunes_dir = 'back_to_skool_daze' if self.custom == BACK_TO_SKOOL_DAZE else sounds_dir
        self.sounds.append((sound.ALARM, '%s/lines2' % sounds_dir))
        self.sounds.append((sound.BELL, '%s/bell' % sounds_dir))
        self.sounds.append((sound.LINES1, '%s/lines1' % sounds_dir))
        self.sounds.append((sound.LINES2, '%s/lines2' % sounds_dir))
        self.sounds.append((sound.MOUSE, '%s/mouse' % sounds_dir))
        self.sounds.append((sound.CONKER, '%s/conker' % sounds_dir))
        self.sounds.append((sound.SHERRY, '%s/sherry' % sounds_dir))
        self.sounds.append((sound.WATER_PISTOL, 'common/catapult'))
        self.sounds.append((sound.DESK, '%s/bingo' % sounds_dir))
        self.sounds.append((sound.FROG, '%s/bingo' % sounds_dir))
        self.sounds.append((sound.BIKE, '%s/bingo' % sounds_dir))
        self.sounds.append((sound.STOREROOM_KEY, '%s/bingo' % sounds_dir))
        self.sounds.append((sound.KISS, '%s/bingo' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[0], '%s/walk0' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[1], '%s/walk1' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[2], '%s/walk2' % sounds_dir))
        self.sounds.append((sound.WALK_SOUNDS[3], '%s/walk3' % sounds_dir))
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.sounds.append((sound.SHIELD, '%s/bingo' % sounds_dir))
        else:
            self.sounds.append((sound.SAFE_KEY, '%s/safe-key' % sounds_dir))
        self.sounds.append((sound.TUNE, '%s/tune' % tunes_dir))
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.sounds.append((sound.ALL_SHIELDS, '%s/all-shields' % tunes_dir))
            self.sounds.append((sound.OPEN_SAFE, '%s/open-safe' % tunes_dir))
        self.sounds.append((sound.UP_A_YEAR, '%s/up-a-year' % tunes_dir))

    def create_sprite_groups(self):
        SkoolIniMaker.create_sprite_groups(self)
        self.sprite_groups.append((SG_ERIC, (states.WALK0, 0), (states.WALK1, 1), (states.WALK2, 2), (states.WALK3, 3), (states.SITTING_ON_CHAIR, 4), (states.SITTING_ON_FLOOR, 5), (states.KNOCKED_OUT, 6), (states.ARM_UP, 7), (states.HITTING0, 8), (states.HITTING1, 9), (states.CATAPULT0, 10), (states.CATAPULT1, 11), (states.RIDING_BIKE0, 12), (states.RIDING_BIKE1, 13), (states.WATERPISTOL, 14), (states.BENDING_OVER, 39)))
        self.sprite_groups.append((SG_GIRL, (states.WALK0, 72), (states.WALK1, 73), (states.WALK2, 74), (states.WALK3, 75), (states.SITTING_ON_CHAIR, 76), (states.SITTING_ON_FLOOR, 77), (states.KNOCKED_OUT, 78)))
        self.sprite_groups.append((SG_ALBERT, (states.WALK0, 120), (states.WALK1, 121), (states.WALK2, 122), (states.WALK3, 123), (states.KNOCKED_OVER, 126), (states.ARM_UP, 127)))
        self.sprite_groups.append((SG_TAKE, (states.WALK0, 112), (states.WALK1, 113), (states.WALK2, 114), (states.WALK3, 115), (states.KNOCKED_OVER, 118), (states.ARM_UP, 119)))
        self.sprite_groups.append((SG_HEROINE, (states.WALK0, 56), (states.WALK1, 57), (states.WALK2, 58), (states.WALK3, 59), (states.SITTING_ON_CHAIR, 60), (states.SITTING_ON_FLOOR, 61), (states.KNOCKED_OUT, 62), (states.ARM_UP, 63), (states.KISSING_ERIC, 15)))
        self.sprite_groups.append((SG_MOUSE, (states.RUN, 47)))
        self.sprite_groups.append((SG_FROG, (states.SIT, 28), (states.HOP1, 29), (states.HOP2, 30)))
        self.sprite_groups.append((SG_WATER, (states.WATER0, 84), (states.WATER1, 92), (states.WATER2, 108), (states.WATER3, 116), (states.WATER4, 124)))
        self.sprite_groups.append((SG_STINKBOMB, (states.STINKBOMB, 71)))
        self.sprite_groups.append((SG_DESK, (states.DESK_EMPTY, 44), (states.DESK_STINKBOMBS, 45), (states.DESK_WATER_PISTOL, 46)))
        self.sprite_groups.append((SG_BIKE, (states.BIKE_ON_FLOOR, 24), (states.BIKE_UPRIGHT, 25)))
        self.sprite_groups.append((SG_PLANT, (states.PLANT_GROWING, 42), (states.PLANT_GROWN, 43)))
        self.sprite_groups.append((SG_WATER_DROP, (states.WATER_DROP, 31)))
        self.sprite_groups.append((SG_SHERRY_DROP, (states.SHERRY_DROP, 31)))
        self.sprite_groups.append((SG_CONKER, (states.CONKER, 55)))

    def create_characters(self):
        self.characters = []
        adult_head_xy = (1, 0)
        kid_head_xy = (1, 1)
        self.characters.append((GIRL01, "JESSICA", SG_GIRL, states.WALK0, -1, (117, 17), kid_head_xy, "FGM"))
        self.characters.append((GIRL02, "HYACINTH", SG_GIRL, states.WALK0, 1, (114, 17), kid_head_xy, "FGM"))
        self.characters.append((GIRL03, "PENELOPE", SG_GIRL, states.WALK0, -1, (120, 17), kid_head_xy, "FGM"))
        self.characters.append((GIRL04, "VIOLET", SG_GIRL, states.WALK0, 1, (160, 17), kid_head_xy, "FGM"))
        self.characters.append((GIRL05, "AMELIA", SG_GIRL, states.WALK0, -1, (163, 17), kid_head_xy, "FGM"))
        self.characters.append((GIRL06, "SARAH-JANE", SG_GIRL, states.WALK0, 1, (166, 17), kid_head_xy, "FGM"))
        self.characters.append((GIRL07, "PHILIPPA", SG_GIRL, states.WALK0, -1, (165, 17), kid_head_xy, "FGM"))
        self.characters.append((BOY01, "PERKINS", SG_BOY, states.WALK0, -1, (5, 10), kid_head_xy, "BF"))
        self.characters.append((BOY02, "GIBSON", SG_BOY, states.WALK0, 1, (7, 10), kid_head_xy, "BF"))
        self.characters.append((BOY03, "FANSHAW", SG_BOY, states.WALK0, -1, (10, 10), kid_head_xy, "BF"))
        self.characters.append((BOY04, "SMITH", SG_BOY, states.WALK0, 1, (72, 17), kid_head_xy, "BF"))
        self.characters.append((BOY05, "HARRIS", SG_BOY, states.WALK0, -1, (74, 17), kid_head_xy, "BF"))
        self.characters.append((BOY06, "MILLER", SG_BOY, states.WALK0, 1, (104, 17), kid_head_xy, "BF"))
        self.characters.append((BOY07, "JONES", SG_BOY, states.WALK0, -1, (107, 17), kid_head_xy, "BF"))
        self.characters.append((BOY08, "VICKERS", SG_BOY, states.WALK0, 1, (110, 17), kid_head_xy, "BF"))
        self.characters.append((BOY09, "BUTLER", SG_BOY, states.WALK0, -1, (123, 17), kid_head_xy, "BF"))
        self.characters.append((BOY10, "COOK", SG_BOY, states.WALK0, 1, (126, 17), kid_head_xy, "BF"))
        extra_flags = 'ST' if self.custom == BACK_TO_SKOOL_DAZE else ''
        self.characters.append((WACKER, "MR WACKER%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_WACKER, states.WALK0, -1, (76, 3), adult_head_xy, "ABCDLNP%sWXY" % extra_flags))
        self.characters.append((WITHIT, "MR WITHIT%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_WITHIT, states.WALK0, 1, (15, 17), adult_head_xy, "ABCDLP%sWXY" % extra_flags))
        self.characters.append((ROCKITT, "MR ROCKITT%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_ROCKITT, states.WALK0, -1, (37, 10), adult_head_xy, "ABCDLP%sWXY" % extra_flags))
        self.characters.append((CREAK, "MR CREAK%sSir" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_CREAK, states.WALK0, 1, (43, 17), adult_head_xy, "ABCDLP%sWXY" % extra_flags))
        extra_flags = 'T' if self.custom == BACK_TO_SKOOL_DAZE else ''
        self.characters.append((TAKE, "MISS TAKE%sMiss" % skoolbuilder.NAME_TITLE_SEPARATOR, SG_TAKE, states.WALK0, -1, (188, 3), adult_head_xy, "ACDGKLMP%sW" % extra_flags))
        self.characters.append((ALBERT, "ALBERT", SG_ALBERT, states.WALK0, -1, (136, 17), adult_head_xy, "ADWZ"))
        self.characters.append((TEARAWAY, "BOY WANDER", SG_TEARAWAY, states.WALK0, 1, (122, 17), kid_head_xy, "BCFPR%s" % extra_flags))
        self.characters.append((BULLY, "ANGELFACE", SG_BULLY, states.WALK0, -1, (116, 17), kid_head_xy, "BCFPR%sV" % extra_flags))
        self.characters.append((SWOT, "EINSTEIN", SG_SWOT, states.WALK0, -1, (24, 3), kid_head_xy, "BCFPR%sV" % extra_flags))
        self.characters.append((HEROINE, "HAYLEY", SG_HEROINE, states.WALK0, -1, (136, 17), kid_head_xy, "CGFMPR%sU" % extra_flags))

    def create_eric(self):
        extra_flags = 'T' if self.custom == BACK_TO_SKOOL_DAZE else ''
        self.eric = (HERO, 'ERIC', SG_ERIC, states.WALK0, -1, (133, 17), (1, 1), 'BFPR%s' % extra_flags, (0, 3))

    def create_water_drop(self):
        self.water_drop = ('water', SG_WATER_DROP, CL_WATER_DROP, (1, 3))

    def create_sherry_drop(self):
        self.sherry_drop = ('sherry', SG_SHERRY_DROP, CL_SHERRY_DROP, (1, 3))

    def create_conker(self):
        self.conker = ('conker', SG_CONKER, CL_CONKER, 98, 102, 2, 3, (1, 3))

    def create_water(self):
        self.water = [(HERO, 'HeroWater', SG_WATER, CL_WATER, AP_WATER)]

    def create_stinkbombs(self):
        self.stinkbombs = [(HERO, 'HeroStinkbomb', SG_STINKBOMB, CL_STINKBOMB, AP_STINKBOMB, 3)]

    def create_mice(self):
        self.mice = []
        self.mice.append(('MOUSE', SG_MOUSE, states.RUN, (17, 3), CL_MOUSE, (1, 3)))

    def create_mouse_locations(self):
        self.mouse_locations = (
            (10,  3), (88,  3), (170,  3),
            (10, 10), (88, 10), (170, 10),
            (10, 17), (88, 17), (170, 17)
        )

    def create_frogs(self):
        self.frogs = []
        if self.custom != 1:
            self.frogs.append(('FROG', SG_FROG, states.SIT, (59, 10), CL_FROG, AP_FROG_TURN_ROUND, AP_FROG_SHORT_HOP, AP_FROG_LONG_HOP, (1, 3), 4))

    def create_bike(self):
        self.bike = ('BIKE', SG_BIKE, states.BIKE_ON_FLOOR, (100, 17), CL_BIKE, (10, 10), (3, 3), (100, 18), 3, 2, 50)

    def create_timetable(self):
        self.timetable = []
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.timetable.append(LSN_PLAYTIME_BOYS_SKOOL_STAMPEDE)
        else:
            self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_CREAK_YELLOW_ROOM_2)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_2)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_PLAYTIME_3)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_3)
        self.timetable.append(LSN_CREAK_BLUE_ROOM_1)
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.timetable.append(LSN_PLAYTIME_GIRLS_SKOOL_STAMPEDE)
        else:
            self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_2)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_DINNER_WITHIT)
        self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_1)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_CREAK_YELLOW_ROOM_1)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_REVISION_LIBRARY_1)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_3)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_WITHIT_BLUE_ROOM_1)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_1)
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.timetable.append(LSN_PLAYTIME_BOYS_SKOOL_STAMPEDE)
        else:
            self.timetable.append(LSN_PLAYTIME_1)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_2)
        self.timetable.append(LSN_CREAK_YELLOW_ROOM_2)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_PLAYTIME_2)
        self.timetable.append(LSN_WITHIT_SCIENCE_LAB_1)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_WITHIT_YELLOW_ROOM_2)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_3)
        self.timetable.append(LSN_CREAK_BLUE_ROOM_1)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_WITHIT_BLUE_ROOM_2)
        self.timetable.append(LSN_REVISION_LIBRARY_1)
        self.timetable.append(LSN_CREAK_YELLOW_ROOM_2)
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.timetable.append(LSN_PLAYTIME_GIRLS_SKOOL_STAMPEDE)
        else:
            self.timetable.append(LSN_PLAYTIME_3)
        self.timetable.append(LSN_WITHIT_SCIENCE_LAB_2)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_2)
        self.timetable.append(LSN_REVISION_LIBRARY_1)
        self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_CREAK_YELLOW_ROOM_1)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_3)
        self.timetable.append(LSN_PLAYTIME_5)
        self.timetable.append(LSN_CREAK_BLUE_ROOM_1)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_WITHIT_BLUE_ROOM_1)
        self.timetable.append(LSN_ROCKITT_SCIENCE_LAB_1)
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.timetable.append(LSN_PLAYTIME_BOYS_SKOOL_STAMPEDE)
        else:
            self.timetable.append(LSN_PLAYTIME_4)
        self.timetable.append(LSN_WITHIT_SCIENCE_LAB_1)
        self.timetable.append(LSN_REVISION_LIBRARY_1)
        self.timetable.append(LSN_PLAYTIME_2)
        self.timetable.append(LSN_CREAK_BLUE_ROOM_2)
        self.timetable.append(LSN_REVISION_LIBRARY_2)
        self.timetable.append(LSN_DINNER_WACKER)
        self.timetable.append(LSN_PLAYTIME_1)
        self.timetable.append(LSN_CREAK_YELLOW_ROOM_1)
        self.timetable.append(LSN_ASSEMBLY)
        self.timetable.append(LSN_WITHIT_SCIENCE_LAB_2)

    def create_skool_locations(self):
        walkabout_locations = []
        other_locations = []

        walkabout_locations.append(( 21,  3, LOC_BLUE_ROOM_0))
        walkabout_locations.append(( 22,  3, LOC_BLUE_ROOM_1))
        walkabout_locations.append(( 36,  3, LOC_REVISION_LIBRARY_0))
        walkabout_locations.append(( 37,  3, LOC_REVISION_LIBRARY_1))
        walkabout_locations.append(( 55,  3, LOC_YELLOW_ROOM_0))
        walkabout_locations.append(( 56,  3, LOC_YELLOW_ROOM_1))
        walkabout_locations.append(( 81,  3, LOC_HEADS_STUDY_0))
        walkabout_locations.append((177,  3, LOC_UPPER_ROOM))
        walkabout_locations.append(( 48, 10, LOC_SCIENCE_LAB_0))
        walkabout_locations.append(( 50, 10, LOC_SCIENCE_LAB_1))
        walkabout_locations.append(( 51, 10, LOC_SCIENCE_LAB_2))
        walkabout_locations.append((174, 10, LOC_MIDDLE_ROOM))
        walkabout_locations.append(( 53, 17, LOC_BOYS_DINNER_HALL_0))
        walkabout_locations.append(( 54, 17, LOC_BOYS_DINNER_HALL_1))
        walkabout_locations.append(( 71, 17, LOC_ASSEMBLY_HALL_0))
        walkabout_locations.append(( 73, 17, LOC_ASSEMBLY_HALL_1))
        walkabout_locations.append(( 75, 17, LOC_ASSEMBLY_HALL_2))
        walkabout_locations.append((104, 17, LOC_JUST_RIGHT_OF_TREE))
        if self.custom == BACK_TO_SKOOL_DAZE:
            walkabout_locations.append((108, 17, LOC_BOYS_PLAYGROUND_0))
            walkabout_locations.append((152, 17, LOC_GIRLS_PLAYGROUND_0))
        walkabout_locations.append((174, 17, LOC_GIRLS_DINNER_HALL))
        walkabout_locations.append((189, 17, LOC_KITCHEN))

        other_locations.append((  6,  3, LOC_BLUE_ROOM_BOARD_MIDDLE))
        other_locations.append(( 11,  3, LOC_BLUE_ROOM_BOARD_EDGE))
        other_locations.append(( 23,  3, LOC_BLUE_ROOM_DOORWAY))
        other_locations.append(( 31,  3, LOC_REVISION_LIBRARY))
        other_locations.append(( 38,  3, LOC_YELLOW_ROOM_DOORWAY))
        other_locations.append(( 44,  3, LOC_YELLOW_ROOM_BOARD_MIDDLE))
        other_locations.append(( 49,  3, LOC_YELLOW_ROOM_BOARD_EDGE))
        other_locations.append(( 76,  3, LOC_HEADS_STUDY_WINDOW))
        other_locations.append((164,  3, LOC_UPPER_ROOM_BOARD_MIDDLE))
        other_locations.append((169,  3, LOC_UPPER_ROOM_BOARD_EDGE))
        other_locations.append((180,  3, LOC_UPPER_ROOM_DOORWAY))
        other_locations.append((183,  3, LOC_TAKES_STUDY_DOORWAY))
        other_locations.append((188,  3, LOC_DRINKS_CABINET))
        other_locations.append(( 18, 10, LOC_JUST_OUTSIDE_TOILETS))
        other_locations.append(( 28, 10, LOC_SCIENCE_LAB_DOORWAY))
        other_locations.append(( 35, 10, LOC_SCIENCE_LAB_BOARD_MIDDLE))
        other_locations.append(( 40, 10, LOC_SCIENCE_LAB_BOARD_EDGE))
        other_locations.append(( 85, 10, LOC_TOP_OF_STAIRS_DOWN_TO_STAGE))
        other_locations.append((164, 10, LOC_MIDDLE_ROOM_BOARD_MIDDLE))
        other_locations.append((169, 10, LOC_MIDDLE_ROOM_BOARD_EDGE))
        other_locations.append((179, 10, LOC_MIDDLE_ROOM_DOORWAY))
        other_locations.append((188, 10, LOC_GIRLS_MIDDLE_FLOOR_WINDOW))
        other_locations.append(( 77, 14, LOC_ASSEMBLY_HALL_STAGE_EDGE))
        other_locations.append(( 79, 14, LOC_ASSEMBLY_HALL_STAGE_MIDDLE))
        other_locations.append((  3, 17, LOC_CLOAK_ROOM))
        other_locations.append(( 40, 17, LOC_BOYS_DINNER_HALL_END_1))
        other_locations.append(( 61, 17, LOC_BOYS_DINNER_HALL_END_2))
        other_locations.append(( 62, 17, LOC_ASSEMBLY_HALL_WAY_BACK))
        other_locations.append(( 65, 17, LOC_ASSEMBLY_HALL_BACK))
        other_locations.append(( 95, 17, LOC_BOYS_SKOOL_DOOR))
        other_locations.append((112, 17, LOC_BOYS_PLAYGROUND_MIDDLE))
        other_locations.append((130, 17, LOC_SKOOL_GATE_TO_SHUT))
        other_locations.append((132, 17, LOC_SKOOL_GATE_TO_OPEN))

        self.skool_locations = walkabout_locations + other_locations

    def create_inventory(self):
        self.inventory = []
        if self.custom != 1:
            self.inventory.append((items.SAFE_KEY, (0, 0), (1, 1)))
        self.inventory.append((items.STOREROOM_KEY, (1, 0), (1, 1)))
        if self.custom != 1:
            self.inventory.append((items.FROG, (2, 0), (1, 1)))
        self.inventory.append((items.WATER_PISTOL, (3, 0), (2, 1)))
        self.inventory.append((items.SHERRY_PISTOL, (5, 0), (2, 1)))
        self.inventory.append((items.STINKBOMBS3, (7, 0), (1, 1)))
        self.inventory.append((items.STINKBOMBS2, (8, 0), (1, 1)))
        self.inventory.append((items.STINKBOMBS1, (9, 0), (1, 1)))
        self.inventory.append((items.MOUSE, (10, 0), (1, 1)))

    def create_rooms(self):
        self.rooms = []
        self.rooms.append((BLUE_ROOM, 'BLUE ROOM', (0, 0), (23, 6), 'Y'))
        self.rooms.append((YELLOW_ROOM, 'YELLOW ROOM', (40, 0), (63, 6), 'Y'))
        self.rooms.append((SCIENCE_LAB, 'SCIENCE LAB', (30, 7), (54, 13), 'Y'))
        self.rooms.append((MIDDLE_ROOM, 'MIDDLE ROOM', (159, 7), (179, 13), 'Y'))
        self.rooms.append((UPPER_ROOM, 'UPPER ROOM', (159, 0), (180, 6), 'Y'))
        self.rooms.append((DINNER_HALL, 'DINNER', (42, 14), (62, 20), 'N'))
        self.rooms.append((ASSEMBLY_HALL, 'ASSEMBLY', (63, 14), (76, 20), 'N'))

    def create_chairs(self):
        self.chairs = []
        self.chairs.append((BLUE_ROOM, 11, 13, 15, 17, 19, 21))
        self.chairs.append((YELLOW_ROOM, 50, 52, 54, 56, 58, 60))
        self.chairs.append((SCIENCE_LAB, 40, 42, 44, 46, 48, 50, 52))
        self.chairs.append((MIDDLE_ROOM, 167, 169, 171, 173, 175, 177))
        self.chairs.append((UPPER_ROOM, 168, 170, 172, 174, 176, 178))

    def create_desks(self):
        self.desks = self.chairs

    def create_desk_lid(self):
        self.desk_lid = ('DeskLid', SG_DESK, CL_DESK_LID, 1)

    def create_doors(self):
        self.doors = []
        self.doors.append(('StudyBackDoor', 73, 6, 0, 'Y', 40, (0, 0), (3, 5), (71, 2)))
        self.doors.append(('StudyDoor', 84, 6, 0, 'Y', 40, (6, 0), (3, 5), (84, 2)))
        self.doors.append((STOREROOM_DOOR, 54, 13, 7, 'Y', 40, (12, 0), (3, 5), (54, 9)))
        self.doors.append((SKOOL_DOOR, 95, 20, 14, 'N', 0, (0, 5), (3, 5), (93, 16)))
        self.doors.append((SKOOL_GATE, 134, 20, 14, 'N', 0, (6, 5), (4, 4), (132, 17), AP_CLIMB_SKOOL_GATE, AP_FLY_OVER_SKOOL_GATE))
        self.doors.append((DRINKS_CABINET, 0, 0, 0, 'Y', 0, (14, 5), (2, 2), (190, 2))) # Not a barrier

    def create_windows(self):
        self.windows = []
        self.windows.append(('UpperWindow', 93, 4, 2, 'Y', (90, 3), (0, 10), (3, 3), (92, 2), AP_DESCENT_UPPER_WINDOW, CL_EXPEL_ERIC_NOT_A_BIRD))
        self.windows.append(('MiddleWindow', 95, 11, 8, 'Y', (92, 10), (6, 10), (2, 4), (94, 8), AP_DESCENT_MIDDLE_WINDOW))

    def create_walls(self):
        self.walls = []
        self.walls.append(('FarLeftWall', 0, 20, 0))       # Far left wall (boys' skool)
        self.walls.append(('FarRightWall', 191, 20, 0))    # Far right wall (girls' skool)
        self.walls.append(('ScienceLabWall', 64, 13, 7))   # Science Lab storeroom wall
        self.walls.append(('TopRightWall', 93, 6, 5))      # Right wall in boys' skool (top floor)
        self.walls.append(('MiddleRightWall', 95, 13, 12)) # Right wall in boys' skool (middle floor)
        self.walls.append(('TopLeftWall', 160, 6, 0))      # Left wall in girls' skool (top floor)
        self.walls.append(('MiddleLeftWall', 160, 13, 7))  # Left wall in girls' skool (middle floor)

    def create_staircases(self):
        self.staircases = []
        self.staircases.append(('%s:%s' % SC_UP_TO_TOILETS, (22, 17), (15, 10)))
        self.staircases.append(('%s:%s' % SC_UP_TO_STAGE, (83, 17), (80, 14)))
        self.staircases.append((SC_GIRLS_SKOOL_LOWER, (176, 17), (183, 10)))
        self.staircases.append(('%s:%s' % SC_UP_FROM_STAGE, (81, 14), (85, 10), True))
        self.staircases.append(('%s:%s' % SC_UP_TO_LIBRARY, (19, 10), (26, 3)))
        self.staircases.append(('%s:%s' % SC_UP_TO_STUDY, (91, 10), (84, 3)))
        self.staircases.append((SC_GIRLS_SKOOL_UPPER, (186, 10), (179, 3)))

    def create_floors(self):
        self.floors = []
        self.floors.append((FLR_BOTTOM, 0, 191, 17))         # Bottom floor
        self.floors.append((FLR_STAGE, 77, 81, 14))          # Assembly hall stage
        self.floors.append((FLR_LEFT_MIDDLE, 0, 64, 10))     # Left-middle floor in boys' skool
        self.floors.append((FLR_RIGHT_MIDDLE, 85, 94, 10))   # Right-middle floor in boys' skool
        self.floors.append((FLR_GIRLS_MIDDLE, 159, 191, 10)) # Middle floor in girls' skool
        self.floors.append((FLR_LEFT_TOP, 0, 73, 3))         # Top floor in boys' skool (left of study)
        self.floors.append((FLR_RIGHT_TOP, 74, 94, 3))       # Top floor in boys' skool (right of left study door)
        self.floors.append((FLR_GIRLS_TOP, 159, 191, 3))     # Top floor in girls' skool

    def create_routes(self):
        self.routes = {}

        bottom_routes = self.routes.setdefault(FLR_BOTTOM, [])
        bottom_routes.append((FLR_LEFT_MIDDLE, FLR_LEFT_TOP, SC_UP_TO_TOILETS[0]))
        bottom_routes.append((FLR_GIRLS_MIDDLE, FLR_GIRLS_TOP, SC_GIRLS_SKOOL_LOWER))
        bottom_routes.append(('*', SC_UP_TO_STAGE[0]))

        stage_routes = self.routes.setdefault(FLR_STAGE, [])
        stage_routes.append((FLR_RIGHT_MIDDLE, FLR_RIGHT_TOP, SC_UP_FROM_STAGE[0]))
        stage_routes.append(('*', SC_UP_TO_STAGE[1]))

        left_middle_routes = self.routes.setdefault(FLR_LEFT_MIDDLE, [])
        left_middle_routes.append((FLR_LEFT_TOP, SC_UP_TO_LIBRARY[0]))
        left_middle_routes.append(('*', SC_UP_TO_TOILETS[1]))

        right_middle_routes = self.routes.setdefault(FLR_RIGHT_MIDDLE, [])
        right_middle_routes.append((FLR_RIGHT_TOP, SC_UP_TO_STUDY[0]))
        right_middle_routes.append(('*', SC_UP_FROM_STAGE[1]))

        girls_middle_routes = self.routes.setdefault(FLR_GIRLS_MIDDLE, [])
        girls_middle_routes.append((FLR_GIRLS_TOP, SC_GIRLS_SKOOL_UPPER))
        girls_middle_routes.append(('*', SC_GIRLS_SKOOL_LOWER))

        self.routes[FLR_LEFT_TOP] = [('*', SC_UP_TO_LIBRARY[1])]
        self.routes[FLR_RIGHT_TOP] = [('*', SC_UP_TO_STUDY[1])]
        self.routes[FLR_GIRLS_TOP] = [('*', SC_GIRLS_SKOOL_UPPER)]

    def create_no_go_zones(self):
        self.no_go_zones = []
        self.no_go_zones.append(('GirlsSkool', 159, 195, 17, 0))
        self.no_go_zones.append(('AroundStage', 77, 94, 16, 4))
        self.no_go_zones.append(('HeadsArea', 63, 93, 3, 0))
        self.no_go_zones.append(('ScienceLabStoreroom', 54, 63, 10, 4))

    def create_message_config(self):
        SkoolIniMaker.create_message_config(self)
        self.message_config.append(('LinesMessageTemplate', '%s LINES^%s' % (NUMBER_OF_LINES_MACRO, LINES_RECIPIENT_MACRO)))
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.message_config.append(('BoardDirtyConditionId', BOARD_DIRTY))
        self.message_config.append(('UpAYearMessage', 'ONTO THE^NEXT YEAR'))

    def create_sit_down_messages(self):
        self.sit_down_messages = []
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.sit_down_messages.append((WITHIT, "SETTLE DOWN NOW LADS"))
            self.sit_down_messages.append((ROCKITT, "RIGHT! SIT DOWN MY LITTLE SERAPHS"))
            self.sit_down_messages.append((CREAK, "BE QUIET AND SEATED YOU ROTTEN LITTLE SCOUNDRELS"))
            self.sit_down_messages.append((TAKE, "COME ON GIRLS - TAKE YOUR SEATS PLEASE"))
        else:
            self.sit_down_messages.append((WITHIT, 'SIT DOWN CHAPS'))
            self.sit_down_messages.append((ROCKITT, 'SIT DOWN MY CHERUBS'))
            self.sit_down_messages.append((CREAK, 'SIT DOWN YOU LITTLE ANARCHISTS'))
            self.sit_down_messages.append((TAKE, 'SIT DOWN'))

    def create_assembly_messages(self):
        self.assembly_messages = []
        verb = 'VERB'
        noun = 'NOUN'
        self.assembly_messages.append((skoolbuilder.AM_MESSAGE, "YOU'RE ALL IN DETENTION UNTIL I FIND OUT WHO $%s THE $%s" % (verb, noun)))
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.assembly_messages.append((verb, "DISEMBOWELLED"))
            self.assembly_messages.append((verb, "DECAPITATED"))
            self.assembly_messages.append((verb, "DEFENESTRATED"))
            self.assembly_messages.append((verb, "IS GNAWING BITS OFF"))
            self.assembly_messages.append((verb, "SENT A LETTER BOMB TO"))
            self.assembly_messages.append((verb, "THREW ROTTEN EGGS AT"))
            self.assembly_messages.append((noun, "SCHOOL LEOPARD"))
            self.assembly_messages.append((noun, "HEADMISTRESS"))
            self.assembly_messages.append((noun, "TEACHING ASSISTANT"))
            self.assembly_messages.append((noun, "DINNER LADY"))
            self.assembly_messages.append((noun, "PRESIDENT OF THE CHESS CLUB"))
            self.assembly_messages.append((noun, "CARETAKER'S WHIPPET"))
            self.assembly_messages.append((noun, "LATIN MASTER'S AUNT"))
            self.assembly_messages.append((noun, "MUSIC TEACHER'S PIANO"))
        else:
            self.assembly_messages.append((verb, "KIDNAPPED"))
            self.assembly_messages.append((verb, "ATE"))
            self.assembly_messages.append((verb, "SET FIRE TO"))
            self.assembly_messages.append((verb, "BLEW UP"))
            self.assembly_messages.append((verb, "IS MAKING RUDE PHONE CALLS TO"))
            self.assembly_messages.append((verb, "IS BLACKMAILING"))
            self.assembly_messages.append((verb, "SQUASHED"))
            self.assembly_messages.append((verb, "POISONED"))
            self.assembly_messages.append((noun, "GOLDFISH"))
            self.assembly_messages.append((noun, "SCHOOL CAT"))
            self.assembly_messages.append((noun, "LATIN MASTER"))
            self.assembly_messages.append((noun, "LOLLIPOP LADY"))
            self.assembly_messages.append((noun, "PTA"))
            self.assembly_messages.append((noun, "CARETAKER'S BUDGIE"))
            self.assembly_messages.append((noun, "MILK MONITOR"))
            self.assembly_messages.append((noun, "HEAD BOY"))

    def create_blackboards(self):
        self.blackboards = []
        chalk = (255, 255, 255)
        size = (8, 2)
        self.blackboards.append((BLUE_ROOM, (3, 3), size, chalk))
        self.blackboards.append((YELLOW_ROOM, (41, 3), size, chalk))
        self.blackboards.append((SCIENCE_LAB, (32, 9), size, chalk))
        self.blackboards.append((UPPER_ROOM, (161, 3), size, chalk))
        self.blackboards.append((MIDDLE_ROOM, (161, 9), size, chalk))

    def create_blackboard_messages(self):
        self.blackboard_messages = {}

        withit_messages = self.blackboard_messages.setdefault(WITHIT, [])
        if self.custom == BACK_TO_SKOOL_DAZE:
            withit_messages.append("THE ARCTIC^SQUARE")
            withit_messages.append("TOPIC DRIFT")
            withit_messages.append("FROST^WEDGING")
            withit_messages.append("ICE JAMS I^HAVE TASTED")
            withit_messages.append("RELIEVING^ANABATIC WIND")
            withit_messages.append("THE TROPIC^OF GEMINI")
        else:
            withit_messages.append('ARTESIAN^WELLS')
            withit_messages.append('THE DOLDRUMS')
            withit_messages.append('TASTY^GEYSERS')
            withit_messages.append('THE GREEN^REVOLUTION')
            withit_messages.append('TREACLE^MINING')
            withit_messages.append('FROG FARMING')

        rockitt_messages = self.blackboard_messages.setdefault(ROCKITT, [])
        if self.custom == BACK_TO_SKOOL_DAZE:
            rockitt_messages.append("GENETIC^ENGINEERING")
            rockitt_messages.append("COLD FUSION")
            rockitt_messages.append("DEPLETED^URANIUM")
            rockitt_messages.append("CHIROPRACTIC^SUBLUXATION")
            rockitt_messages.append("WATER^FLUORIDATION")
            rockitt_messages.append("STEM CELL^RESEARCH")
        else:
            rockitt_messages.append('HEAVY WATER')
            rockitt_messages.append('HOLOGRAMS &^LASERS')
            rockitt_messages.append('DNA')
            rockitt_messages.append('VAMPIRE^BATS')
            rockitt_messages.append('NUCLEAR^FUSION')
            rockitt_messages.append('BACTERIA^AS PETS')

        creak_messages = self.blackboard_messages.setdefault(CREAK, [])
        if self.custom == BACK_TO_SKOOL_DAZE:
            creak_messages.append("THE TOMORROW^PEOPLE")
            creak_messages.append("MUFFIN THE^MULE")
            creak_messages.append("THE MAGIC^ROUNDABOUT")
            creak_messages.append("REMEMBERING^ROOBARB")
            creak_messages.append("THE TAO OF^BOD")
            creak_messages.append("MR BENN")
        else:
            creak_messages.append('ATTILA THE^HUN')
            creak_messages.append('ERIC THE RED')
            creak_messages.append('NOGGIN THE^NOG')
            creak_messages.append('IVAN THE^TERRIBLE')
            creak_messages.append('ETHELRED THE^UNREADY')
            creak_messages.append('THE LUDDITES')

        take_messages = self.blackboard_messages.setdefault(TAKE, [])
        if self.custom == BACK_TO_SKOOL_DAZE:
            take_messages.append("ALL THINGS^NICE")
            take_messages.append("ATONAL^COMPOSITION")
            take_messages.append("DECEPTIVE^CADENCE")
            take_messages.append("THE RAIN^IN SPAIN")
            take_messages.append("GOURMET^GRUEL")
            take_messages.append("WHY I HATE^MICE")
        else:
            take_messages.append('IAMBIC^PENTAMETERS')
            take_messages.append('ELOCUTION^AINT ARF FUN')
            take_messages.append('SUGAR AND^SPICE')
            take_messages.append('TONE POEMS')
            take_messages.append('ELEMENTARY^ASTROPHYSICS')
            take_messages.append('THE BARD OF^AVON')

        tearaway_messages = self.blackboard_messages.setdefault(TEARAWAY, [])
        if self.custom == BACK_TO_SKOOL_DAZE:
            tearaway_messages.append("$%s^is a bast" % SWOT)
            tearaway_messages.append("*wibble*")
            tearaway_messages.append("i love #!@&@^NO CARRIER")
            tearaway_messages.append("/join #speccy")
            tearaway_messages.append("i woz ere")
            tearaway_messages.append("i hate^DEF FN")
        else:
            tearaway_messages.append('i hate^girls')
            tearaway_messages.append('i hate^skool')
            tearaway_messages.append('i hate^mafs')
            tearaway_messages.append('i hate^$%s' % WACKER)
            tearaway_messages.append('i hate^groan-ups')
            tearaway_messages.append("who's Sam^Cruise?")

    def create_lines_messages(self):
        self.lines_messages = []
        self.lines_messages.append(('*', lines.GET_OUT, 'YOU ARE NOT^ALLOWED HERE'))
        self.lines_messages.append(('*', lines.GET_ALONG, 'GET ALONG^NOW'))
        self.lines_messages.append(('*', lines.SIT_DOWN, 'NOW^SIT DOWN'))
        self.lines_messages.append(('*', lines.GET_UP, 'GET OFF^THE FLOOR'))
        self.lines_messages.append(('*', '%s_1' % lines.COME_ALONG_PREFIX, 'COME ALONG^YOU MONSTER'))
        self.lines_messages.append(('*', '%s_2' % lines.COME_ALONG_PREFIX, "DON'T KEEP^ME WAITING"))
        self.lines_messages.append(('*', lines.NEVER_AGAIN, "NOW DON'T^DO IT AGAIN"))
        self.lines_messages.append(('*', lines.NO_TALES, "DON'T TELL^TALES"))
        self.lines_messages.append(('*', lines.BE_PUNCTUAL, "DON'T BE^LATE AGAIN"))
        self.lines_messages.append(('*', lines.STAY_IN_CLASS, 'STAY TILL I^DISMISS YOU'))
        self.lines_messages.append(('*', lines.NO_WRITING, "DON'T TOUCH^BLACKBOARDS"))
        self.lines_messages.append(('*', lines.NO_CATAPULTS, 'NO^CATAPULTS'))
        self.lines_messages.append(('*', lines.NO_HITTING, "DON'T HIT^YOUR MATES"))
        self.lines_messages.append(('*', lines.GET_OFF_PLANT, "GET OFF^THE PLANTS"))
        self.lines_messages.append(('*', lines.NO_BIKES, "DON'T RIDE^BIKES IN HERE"))
        self.lines_messages.append(('*', lines.BACK_TO_SKOOL, "GET BACK^TO SCHOOL"))
        self.lines_messages.append(('*', lines.SIT_FACING_STAGE, "SIT FACING^THE STAGE"))
        self.lines_messages.append(('*', lines.NO_STINKBOMBS, "NO^STINKBOMBS"))
        self.lines_messages.append(('*', lines.NO_WATERPISTOLS, "NO^WATERPISTOLS"))
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.lines_messages.append(('*', lines.NO_JUMPING, 'YOU ARE NOT^A KANGAROO'))

    def create_lesson_messages(self):
        self.lesson_messages = []
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.lesson_messages.append(('*', '"START READING AT CHAPTER $(3, 9) IN YOUR BOOKS"'))
            self.lesson_messages.append(('*', '"DO THE EXERCISES ON PAGES $(15, 25) TO $(30, 40) OF YOUR LOVELY TEXTBOOK"'))
            self.lesson_messages.append(('*', "WRITE AN ESSAY TITLED 'WHY MY TEACHER IS GREAT'"))
        else:
            self.lesson_messages.append(('*', 'START REVISING FOR YOUR EXAMS'))
            self.lesson_messages.append(('*', 'START READING AT THE NEXT CHAPTER IN YOUR BOOKS'))
            self.lesson_messages.append(('*', "WRITE AN ESSAY TITLED 'WHY I LOVE SCHOOL'"))

    def create_shields(self):
        self.shields = []
        if self.custom == BACK_TO_SKOOL_DAZE:
            size = (1, 1)
            self.shields.append((100, (16, 10), size, (  4,  2)))
            self.shields.append((100, (16, 11), size, (  9,  2)))
            self.shields.append((100, ( 6,  9), size, ( 74,  2)))
            self.shields.append((100, ( 8,  9), size, ( 79,  2)))
            self.shields.append((100, (10,  9), size, ( 82,  2)))
            self.shields.append((100, (16, 11), size, (162,  2)))
            self.shields.append((100, (16, 12), size, (167,  2)))
            self.shields.append((200, ( 2, 13), size, ( 33,  8)))
            self.shields.append((200, ( 4, 13), size, ( 38,  8)))
            self.shields.append((800, (16, 12), size, ( 57,  9)))
            self.shields.append((200, (0 , 13), size, (173,  8)))
            self.shields.append((400, ( 8,  9), size, (  4, 15)))
            self.shields.append((400, (10,  9), size, (  8, 15)))
            self.shields.append((400, ( 6,  9), size, ( 12, 15)))
            self.shields.append((400, (14, 13), size, ( 30, 14)))
            self.shields.append((800, (12, 13), size, (186, 14)))

    def create_safe(self):
        if self.custom == BACK_TO_SKOOL_DAZE:
            self.safe = ((12, 9), (1, 1), (81, 2))
        else:
            self.safe = ((0, 0), (0, 0), (81, 2))

    def create_cups(self):
        self.cups = []
        self.cups.append(('LeftCup', (14, 7), (1, 1), (25, 14)))
        self.cups.append(('MiddleCup', (14, 8), (1, 1), (27, 14)))
        if self.custom != BACK_TO_SKOOL_DAZE:
            self.cups.append(('RightCup', (14, 7), (1, 1), (30, 14)))
        self.cups.append(('GirlsCup', (14, 9), (1, 1), (186, 14)))

    def create_plants(self):
        self.plants = []
        self.plants.append(('TopFloorPlant', SG_PLANT, 91, 3, CL_PLANT))
        self.plants.append(('MiddleFloorPlant', SG_PLANT, 93, 10, CL_PLANT))
        self.plants.append(('LeftGatePlant', SG_PLANT, 132, 17, CL_PLANT))
        self.plants.append(('RightGatePlant', SG_PLANT, 135, 17, CL_PLANT))

    def create_animation_phases(self):
        self.animation_phases = []

        frog_desc = 'animatoryState, xInc, directionChange'
        self.animation_phases.append((AP_FROG_TURN_ROUND, frog_desc,
            (states.HOP1, 0, 1),
            (states.SIT, 0, -1)
        ))
        self.animation_phases.append((AP_FROG_SHORT_HOP, frog_desc,
            (states.HOP1, 1, 1),
            (states.SIT, 0, 1)
        ))
        self.animation_phases.append((AP_FROG_LONG_HOP, frog_desc,
            (states.HOP1, 1, 1),
            (states.HOP2, 1, 1),
            (states.HOP1, 1, 1),
            (states.SIT, 0, 1)
        ))

        window_desc = 'xInc, yInc, animatoryState'
        self.animation_phases.append((AP_DESCENT_MIDDLE_WINDOW, window_desc,
            (0, 0, states.WALK1),
            (1, 0, states.WALK2),
            (0, 0, states.WALK3),
            (1, 0, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0)
        ))
        self.animation_phases.append((AP_DESCENT_UPPER_WINDOW, window_desc,
            (0, 0, states.WALK1),
            (1, 0, states.WALK2),
            (0, 0, states.WALK3),
            (1, 0, states.WALK0),
            (1, 1, states.WALK0),
            (1, 1, states.WALK0),
            (1, 1, states.WALK0),
            (1, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.WALK0),
            (0, 1, states.SITTING_ON_CHAIR),
            (0, 1, states.SITTING_ON_CHAIR),
            (0, 1, states.SITTING_ON_CHAIR),
            (0, 1, states.SITTING_ON_FLOOR),
            (0, 1, states.SITTING_ON_FLOOR),
            (0, 1, states.SITTING_ON_FLOOR),
            (0, 1, states.KNOCKED_OUT)
        ))

        flight_desc = 'xInc, yInc, animatoryState'
        self.animation_phases.append((AP_CLIMB_SKOOL_GATE, flight_desc,
            (0, 0, states.WALK1),
            (1, 0, states.WALK2),
            (0, 0, states.WALK3),
            (1, 0, states.WALK0),
            (0, 0, states.WALK1),
            (1, 0, states.WALK2),
            (0, 1, states.WALK2),
            (0, 1, states.WALK2),
            (0, 1, states.WALK2)
        ))
        self.animation_phases.append((AP_FLY_OVER_SKOOL_GATE, flight_desc,
            (1, -1, states.WALK0),
            (1, -1, states.WALK0),
            (1, -1, states.WALK0),
            (1,  1, states.WALK0),
            (1,  1, states.SITTING_ON_CHAIR),
            (1,  0, states.SITTING_ON_FLOOR),
            (1,  1, states.SITTING_ON_FLOOR),
            (1,  1, states.SITTING_ON_FLOOR)
        ))

        self.animation_phases.append((AP_WATER, 'animatoryState, xInc, yInc, hit',
            (states.WATER1, 2, -1, 0),
            (states.WATER2, 2,  0, 1),
            (states.WATER3, 1,  0, 0),
            (states.WATER4, 0,  1, 0),
            (states.WATER4, 0,  1, 2)
        ))

        self.animation_phases.append((AP_STINKBOMB, 'animatoryState, direction',
            (states.STINKBOMB, -1),
            (states.STINKBOMB, 1)
        ))
