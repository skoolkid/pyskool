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
Build the skool and its cast of characters.
"""

from .iniparser import IniParser

# Section names
ANIMATION_PHASES = 'AnimationPhases'
ASSEMBLY_MESSAGES = 'AssemblyMessages'
BIKE = 'Bike'
BLACKBOARD_MESSAGES = 'BlackboardMessages'
BLACKBOARDS = 'Blackboards'
CATAPULT_PELLETS = 'CatapultPellets'
CHAIRS = 'Chairs'
CHARACTERS = 'Characters'
COMMAND_LIST = 'CommandList'
CONKER = 'Conker'
CUPS = 'Cups'
DESK_LID = 'DeskLid'
DESKS = 'Desks'
DOORS = 'Doors'
ERIC = 'Eric'
FONT = 'Font'
FLOORS = 'Floors'
FROGS = 'Frogs'
GRASS_MESSAGES = 'GrassMessages'
IMAGES = 'Images'
INVENTORY = 'Inventory'
LESSON = 'Lesson'
LESSON_MESSAGES = 'LessonMessages'
LINES_MESSAGES = 'LinesMessages'
MICE = 'Mice'
MOUSE_LOCATIONS = 'MouseLocations'
NO_GO_ZONES = 'NoGoZones'
PLANTS = 'Plants'
QUESTIONS_AND_ANSWERS = 'QuestionsAndAnswers'
RANDOM_LOCATIONS = 'RandomLocations'
ROOMS = 'Rooms'
ROUTES = 'Routes'
SAFE = 'Safe'
SHERRY_DROP = 'SherryDrop'
SHIELDS = 'Shields'
SIT_DOWN_MESSAGES = 'SitDownMessages'
SKOOL_LOCATIONS = 'SkoolLocations'
SOUNDS = 'Sounds'
SPECIAL_PLAYTIMES = 'SpecialPlaytimes'
SPRITE_GROUP = 'SpriteGroup'
STAIRCASES = 'Staircases'
STINKBOMBS = 'Stinkbombs'
TIMETABLE = 'Timetable'
WALLS = 'Walls'
WATER = 'Water'
WATER_DROP = 'WaterDrop'
WINDOWS = 'Windows'

# Keywords in the QuestionsAndAnswers sections
QA_SPECIAL_GROUP = 'SpecialGroup'
QA_SPECIAL_QUESTION = 'SpecialQuestion'
QA_SPECIAL_ANSWER = 'SpecialAnswer'
QA_QUESTION = 'Question'
QA_ANSWER = 'Answer'

# Keywords in the GrassMessages section
GM_HITTERS = 'Hitters'
GM_WRITERS = 'Writers'
GM_HIT_TALE = 'HitTale'
GM_WRITE_TALE = 'WriteTale'
GM_ABSENT_TALE = 'AbsentTale'

# Keywords used in the AssemblyMessages section
AM_MESSAGE = 'MESSAGE'

# The marker used to indicate that a teacher's name be hidden when printing the
# lesson
HIDE_TEACHER_MARKER = '*'

# The separator used between a character's name and title
NAME_TITLE_SEPARATOR = '/'

class SkoolBuilder(IniParser):
    """Builds a skool and its cast from the contents of ini files."""

    def build_skool(self, skool):
        """Build a skool from the contents of the ini files.

        :type skool: :class:`~pyskool.skool.Skool`
        :param skool: The skool to build.
        """
        self.skool = skool
        self.cast = skool.cast
        self.beeper = skool.beeper
        self.timetable = skool.timetable
        self.assembly_message_generator = skool.assembly_message_generator

        self._parse_sounds()
        self._parse_sprite_groups()
        self._parse_characters()
        self._parse_eric()
        self._parse_catapult_pellets()
        self._parse_water_drop()
        self._parse_sherry_drop()
        self._parse_conker()
        self._parse_water()
        self._parse_stinkbombs()
        self._parse_mice()
        self._parse_mouse_locations()
        self._parse_frogs()
        self._parse_bike()
        self._parse_timetable()
        self._parse_special_playtimes()
        self._parse_lessons()
        self._parse_random_locations()
        self._parse_skool_locations()
        self._parse_inventory()
        self._parse_command_lists()
        self._parse_rooms()
        self._parse_chairs()
        self._parse_desks()
        self._parse_desk_lid()
        self._parse_doors()
        self._parse_windows()
        self._parse_walls()
        self._parse_staircases()
        self._parse_floors()
        self._parse_routes()
        self._parse_no_go_zones()
        self._parse_sit_down_messages()
        self._parse_font()
        self._parse_assembly_messages()
        self._parse_blackboards()
        self._parse_blackboard_messages()
        self._parse_questions_and_answers()
        self._parse_lines_messages()
        self._parse_lesson_messages()
        self._parse_shields()
        self._parse_safe()
        self._parse_cups()
        self._parse_plants()
        self._parse_grass_messages()

    def _get_animation_phases(self, phase_set_id):
        """Return a list of animation phase elements from a section of the ini
        file.

        :param phase_set_id: The name of the animation phase set.
        """
        return self.parse_section('%s %s' % (ANIMATION_PHASES, phase_set_id))

    def _parse_sounds(self):
        """Parse the 'Sounds' section of the ini file."""
        for sound_id, sound_file in self.parse_section(SOUNDS):
            self.beeper.add_sound(sound_id, sound_file)

    def _parse_sprite_groups(self):
        """Parse the 'SpriteGroup' sections of the ini file."""
        for group_id, section in self._get_sections('%s ' % SPRITE_GROUP).items():
            for sprite_id, sprite_index in section:
                self.cast.add_sprite(group_id, sprite_id, sprite_index)

    def _parse_eric(self):
        """Parse the 'Eric' section of the ini file."""
        for character_id, name, sprite_group, initial_as, direction, location, head_xy, flags, bend_over_hand_xy in self.parse_section(ERIC, num_elements=9):
            direction = -1 if direction < 0 else 1
            self.cast.add_eric(character_id, name, sprite_group, initial_as, direction, head_xy, flags.upper(), bend_over_hand_xy)
            self.cast.set_location(character_id, *location)

    def _parse_characters(self):
        """Parse the 'Characters' section of the ini file."""
        for character_id, name_and_title, sprite_group, initial_as, direction, location, head_xy, flags in self.parse_section(CHARACTERS):
            names = name_and_title.partition(NAME_TITLE_SEPARATOR)
            name, title = names[0], names[2]
            self.cast.add_character(character_id, name, title, sprite_group, initial_as, direction, head_xy, flags.upper())
            self.cast.set_location(character_id, *location)

    def _parse_catapult_pellets(self):
        """Parse the 'CatapultPellets' section of the ini file."""
        for character_id, pellet_id, sprite_group, command_list_id, pellet_range, hit_zone, hit_xy in self.parse_section(CATAPULT_PELLETS):
            self.cast.add_pellet(character_id, pellet_id, sprite_group, command_list_id, pellet_range, hit_zone, hit_xy)

    def _parse_water_drop(self):
        """Parse the 'WaterDrop' section of the ini file."""
        for object_id, sprite_group_id, command_list_id, hit_xy in self.parse_section(WATER_DROP):
            self.cast.add_water_drop(object_id, sprite_group_id, command_list_id, hit_xy)

    def _parse_sherry_drop(self):
        """Parse the 'SherryDrop' section of the ini file."""
        for object_id, sprite_group_id, command_list_id, hit_xy in self.parse_section(SHERRY_DROP):
            self.cast.add_sherry_drop(object_id, sprite_group_id, command_list_id, hit_xy)

    def _parse_conker(self):
        """Parse the 'Conker' section of the ini file."""
        for object_id, sprite_group_id, command_list_id, min_x, max_x, min_y, max_y, hit_xy in self.parse_section(CONKER):
            self.cast.add_conker(object_id, sprite_group_id, command_list_id, min_x, max_x, min_y, max_y, hit_xy)

    def _parse_water(self):
        """Parse the 'Water' section of the ini file."""
        for character_id, water_id, sprite_group, command_list_id, phase_set_id in self.parse_section(WATER):
            phases = self._get_animation_phases(phase_set_id)
            self.cast.add_water(character_id, water_id, sprite_group, command_list_id, phases)

    def _parse_stinkbombs(self):
        """Parse the 'Stinkbombs' section of the ini file."""
        for character_id, stinkbomb_id, sprite_group, command_list_id, phase_set_id, stink_range in self.parse_section(STINKBOMBS):
            phases = self._get_animation_phases(phase_set_id)
            self.cast.add_stinkbomb(character_id, stinkbomb_id, sprite_group, command_list_id, phases, stink_range)

    def _parse_mice(self):
        """Parse the 'Mice' section of the ini file."""
        for mouse_id, sprite_group_id, initial_as, location, command_list_id, sprite_xy in self.parse_section(MICE):
            self.cast.add_mouse(mouse_id, sprite_group_id, initial_as, location, command_list_id, sprite_xy)

    def _parse_mouse_locations(self):
        """Parse the 'MouseLocations' section of the ini file."""
        for x, y in self.parse_section(MOUSE_LOCATIONS):
            self.cast.add_mouse_location(x, y)

    def _parse_frogs(self):
        """Parse the 'Frogs' section of the ini file."""
        for frog_id, sprite_group_id, initial_as, location, command_list_id, turn_round_id, short_hop_id, long_hop_id, sit_xy, eric_proximity in self.parse_section(FROGS):
            turn_round = self._get_animation_phases(turn_round_id)
            short_hop = self._get_animation_phases(short_hop_id)
            long_hop = self._get_animation_phases(long_hop_id)
            self.cast.add_frog(frog_id, sprite_group_id, initial_as, location, command_list_id, turn_round, short_hop, long_hop, sit_xy, eric_proximity)

    def _parse_bike(self):
        """Parse the 'Bike' section of the ini file."""
        for bike_id, sprite_group_id, initial_as, location, command_list_id, top_left, size, coords, move_delay, pedal_momentum, max_momentum in self.parse_section(BIKE):
            self.skool.add_bike(bike_id, sprite_group_id, initial_as, location, command_list_id, top_left, size, coords, move_delay, pedal_momentum, max_momentum)

    def _parse_timetable(self):
        """Parse the 'Timetable' section of the ini file."""
        for lesson_type in self.parse_section(TIMETABLE):
            self.timetable.add_lesson(*lesson_type)

    def _parse_special_playtimes(self):
        """Parse the 'SpecialPlaytimes' section of the ini file."""
        for lesson_type in self.parse_section(SPECIAL_PLAYTIMES):
            self.timetable.add_special_playtime(*lesson_type)

    def _parse_lessons(self):
        """Parse the 'Lesson' sections of the ini file."""
        for details, section in self._get_sections('%s ' % LESSON).items():
            index = details.index(' ')
            lesson_id = details[:index]
            lesson_details = [e.strip() for e in details[index + 1:].split(',')]
            room_id = lesson_details[-1]
            teacher_id = lesson_details[0] if len(lesson_details) > 1 else ''
            hide_teacher = teacher_id.startswith(HIDE_TEACHER_MARKER)
            if hide_teacher:
                teacher_id = teacher_id[1:]
            self.timetable.add_lesson_details(lesson_id, hide_teacher, teacher_id, room_id)
            for character_id, command_list_id in section:
                self.cast.add_command_list(character_id, lesson_id, command_list_id)

    def _parse_random_locations(self):
        """Parse the 'RandomLocations' section of the ini file."""
        for elements in self.parse_section(RANDOM_LOCATIONS):
            character_id = elements[0]
            locations = elements[1:]
            self.cast.set_random_locations(character_id, locations)

    def _parse_skool_locations(self):
        """Parse the 'SkoolLocations' section of the ini file."""
        for location_id, x, y in self.parse_section(SKOOL_LOCATIONS):
            self.skool.add_location(location_id, (x, y))

    def _parse_inventory(self):
        """Parse the 'Inventory' section of the ini file."""
        for item_id, top_left, size in self.parse_section(INVENTORY):
            self.skool.add_inventory_item(item_id, top_left, size)

    def _parse_command_lists(self):
        """Parse the 'CommandList' sections of the ini file."""
        for command_list_id, section in self._get_sections('%s ' % COMMAND_LIST).items():
            for elements in section:
                command_name = elements[0]
                params = elements[1:]
                self.cast.add_command(command_list_id, command_name, *params)

    def _parse_rooms(self):
        """Parse the 'Rooms' section of the ini file."""
        for room_id, name, top_left, bottom_right, get_along in self.parse_section(ROOMS):
            self.skool.add_room(room_id, name, top_left, bottom_right, get_along.upper() == 'Y')

    def _parse_chairs(self):
        """Parse the 'Chairs' section of the ini file."""
        for elements in self.parse_section(CHAIRS):
            room_id = elements[0]
            for x in elements[1:]:
                self.skool.add_chair(room_id, x)

    def _parse_desks(self):
        """Parse the 'Desks' section of the ini file."""
        for elements in self.parse_section(DESKS):
            room_id = elements[0]
            for x in elements[1:]:
                self.skool.add_desk(room_id, x)
        self.skool.fill_desks()

    def _parse_desk_lid(self):
        """Parse the 'DeskLid' section of the ini file."""
        for desk_lid_id, sprite_group_id, command_list_id, x_offset in self.parse_section(DESK_LID):
            self.cast.add_desk_lid(desk_lid_id, sprite_group_id, command_list_id, x_offset)

    def _parse_doors(self):
        """Parse the 'Doors' section of the ini file."""
        for door_id, x, bottom_y, top_y, initially_shut, auto_shut_delay, shut_top_left, size, coords, climb_phase_set_id, fly_phase_set_id in self.parse_section(DOORS, num_elements=11):
            initially_shut = initially_shut.upper() == 'Y'
            climb_phases = self._get_animation_phases(climb_phase_set_id)
            fly_phases = self._get_animation_phases(fly_phase_set_id)
            self.skool.add_door(door_id, x, bottom_y, top_y, initially_shut, auto_shut_delay, shut_top_left, size, coords, climb_phases, fly_phases)

    def _parse_windows(self):
        """Parse the 'Windows' section of the ini file."""
        for window_id, x, bottom_y, top_y, initially_shut, opener_coords, shut_top_left, size, coords, descent_phase_set_id, not_a_bird in self.parse_section(WINDOWS, num_elements=11):
            initially_shut = initially_shut.upper() == 'Y'
            descent_phases = self._get_animation_phases(descent_phase_set_id)
            self.skool.add_window(window_id, x, bottom_y, top_y, initially_shut, opener_coords, shut_top_left, size, coords, descent_phases, not_a_bird)

    def _parse_walls(self):
        """Parse the 'Walls' section of the ini file."""
        for wall_id, x, bottom_y, top_y in self.parse_section(WALLS):
            self.skool.add_wall(wall_id, x, bottom_y, top_y)

    def _parse_staircases(self):
        """Parse the 'Staircases' section of the ini file."""
        for elements in self.parse_section(STAIRCASES):
            staircase_ids = elements[0].partition(':')
            bottom = elements[1]
            top = elements[2]
            force = len(elements) == 4
            self.skool.add_staircase(staircase_ids[0], bottom, top, force, staircase_ids[2])

    def _parse_floors(self):
        """Parse the 'Floors' section of the ini file."""
        for floor_id, min_x, max_x, y in self.parse_section(FLOORS):
            self.skool.add_floor(floor_id, min_x, max_x, y)

    def _parse_routes(self):
        """Parse the 'Routes' section of the ini file."""
        for elements in self.parse_section(ROUTES):
            home_floor_id = elements[0]
            staircase_id = elements[-1]
            dest_floor_ids = elements[1:-1]
            self.skool.add_routes(home_floor_id, dest_floor_ids, staircase_id)

    def _parse_no_go_zones(self):
        """Parse the 'NoGoZones' section of the ini file."""
        for zone_id, min_x, max_x, bottom_y, top_y in self.parse_section(NO_GO_ZONES):
            self.skool.add_no_go_zone(zone_id, min_x, max_x, bottom_y, top_y)

    def _parse_sit_down_messages(self):
        """Parse the 'SitDownMessages' section of the ini file."""
        for character_id, message in self.parse_section(SIT_DOWN_MESSAGES, parse_numbers=False):
            self.cast.add_sit_down_message(character_id, message)

    def _parse_font(self):
        """Parse the 'Font' section of the ini file."""
        for char, offset, width in self.parse_section(FONT):
            self.skool.add_font_character(char, offset, width)

    def _parse_assembly_messages(self):
        """Parse the 'AssemblyMessages' section of the ini file."""
        for elements in self.parse_section(ASSEMBLY_MESSAGES, parse_numbers=False):
            if elements[0] == AM_MESSAGE:
                self.assembly_message_generator.add_message_template(elements[1])
            else:
                self.assembly_message_generator.add_word(elements[0], elements[1])

    def _parse_blackboards(self):
        """Parse the 'Blackboards' section of the ini file."""
        for room_id, top_left, size, chalk in self.parse_section(BLACKBOARDS):
            self.skool.add_blackboard(room_id, top_left, size, chalk)

    def _parse_blackboard_messages(self):
        """Parse the 'BlackboardMessages' sections of the ini file."""
        for character_id, section in self._get_sections(BLACKBOARD_MESSAGES, parse_numbers=False, split=False).items():
            for message in section:
                self.cast.add_blackboard_message(character_id, message)

    def _parse_questions_and_answers(self):
        """Parse the 'QuestionsAndAnswers' sections of the ini file."""
        for teacher_id, section in self._get_sections('%s ' % QUESTIONS_AND_ANSWERS, parse_numbers=False).items():
            qa_generator = self.cast.get(teacher_id).get_qa_generator()
            for elements in section:
                entry_type = elements[0]
                if entry_type == QA_SPECIAL_GROUP:
                    qa_generator.set_special_group(elements[1], int(elements[2]))
                elif entry_type == QA_SPECIAL_QUESTION:
                    qa_generator.special_question = elements[1]
                elif entry_type == QA_SPECIAL_ANSWER:
                    qa_generator.special_answer = elements[1]
                elif entry_type == QA_QUESTION:
                    question_id, qa_group, text = elements[1:4]
                    qa_generator.add_question(question_id, qa_group, text)
                elif entry_type == QA_ANSWER:
                    question_id, text = elements[1:3]
                    qa_generator.add_answer(question_id, text)
                else:
                    qa_group, word1, word2 = elements[:3]
                    qa_generator.add_qa_pair(qa_group, word1, word2)

    def _parse_lines_messages(self):
        """Parse the 'LinesMessages' section of the ini file."""
        for character_id, message_id, message in self.parse_section(LINES_MESSAGES, parse_numbers=False):
            self.cast.add_lines_message(character_id, message_id, message)

    def _parse_lesson_messages(self):
        """Parse the 'LessonMessages' section of the ini file."""
        for elements in self.parse_section(LESSON_MESSAGES, parse_numbers=False):
            character_id = elements[0]
            message = elements[1]
            condition = '' if len(elements) < 3 else elements[2]
            self.cast.add_lesson_message(character_id, message, condition)

    def _parse_shields(self):
        """Parse the 'Shields' section of the ini file."""
        for score, top_left, size, coords in self.parse_section(SHIELDS):
            self.skool.add_shield(score, top_left, size, coords)

    def _parse_safe(self):
        """Parse the 'Safe' section of the ini file."""
        for top_left, size, coords in self.parse_section(SAFE):
            self.skool.add_safe(top_left, size, coords)

    def _parse_cups(self):
        """Parse the 'Cups' section of the ini file."""
        for cup_id, empty_top_left, size, coords in self.parse_section(CUPS):
            self.skool.add_cup(cup_id, empty_top_left, size, coords)

    def _parse_plants(self):
        """Parse the 'Plants' section of the ini file."""
        for plant_id, sprite_group_id, x, y, command_list_id in self.parse_section(PLANTS):
            self.skool.add_plant(plant_id, sprite_group_id, x, y, command_list_id)

    def _parse_grass_messages(self):
        """Parse the 'GrassMessages' section of the ini file."""
        for elements in self.parse_section(GRASS_MESSAGES, parse_numbers=False):
            param = elements[0]
            values = elements[1:]
            if param == GM_HITTERS:
                self.cast.hitters = values
            elif param == GM_WRITERS:
                self.cast.writers = values
            elif param == GM_HIT_TALE:
                self.cast.hit_tale = values[0]
            elif param == GM_WRITE_TALE:
                self.cast.write_tale = values[0]
            elif param == GM_ABSENT_TALE:
                self.cast.absent_tale = values[0]
