# -*- coding: utf-8 -*-

# Copyright 2012, 2014 Richard Dymond (rjdymond@gmail.com)
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

from .snapshot import get_snapshot

class Udg:
    def __init__(self, attr, data, mask=None):
        self.attr = attr
        self.data = data
        self.mask = mask
        # If paper is set, it will override attr (see _get_all_colours() and
        # _build_image_data_bd_any() on PngWriter)
        self.paper = None

_BLANK_UDG = Udg(0, [0] * 8)

class SkoolMemory:
    def __init__(self, snafile, custom):
        self.snapshot = get_snapshot(snafile)
        self.custom = custom

    def get_skool_udgs(self, x, y, w, h):
        skool_udgs = []
        for row in range(y, y + h):
            skool_udgs.append([])
            for col in range(x, x + w):
                skool_udgs[-1].append(self.get_skool_udg(row, col))
        return skool_udgs

    def get_logo(self):
        return self.get_box_graphic(self.logo_address)

    def get_score_box_udgs(self):
        udg = Udg(self.snapshot[self.score_box_address], [0] * 8)
        return [[udg] * 8] * 3

    def get_lesson_box_udgs(self):
        udg = Udg(self.lesson_box_attr, [0] * 8)
        return [[udg] * 8] * 3

    def _get_box_udg(self, address, row, col, attr=None):
        if attr is None:
            attr = self.snapshot[address + 8 * row + col]
        start = address + 24 + 64 * row + col
        return Udg(attr, self.snapshot[start:start + 64:8])

    def get_box_graphic(self, address, attr=None):
        udg_array = []
        for row in range(3):
            udg_array.append([self._get_box_udg(address, row, col, attr) for col in range(8)])
        return udg_array

    def add_transparency(self, udg_array, pixel_coords):
        for y, x in pixel_coords:
            udg = udg_array[y // 8][x // 8]
            if udg.mask is None:
                udg.mask = udg.data[:]
            udg.mask[y % 8] |= (2 ** (7 - (x % 8)))

class SDMemory(SkoolMemory):
    def __init__(self, snafile, custom):
        SkoolMemory.__init__(self, snafile, custom)
        self.logo_address = 61184
        self.lesson_box_attr = 5
        self.score_box_address = 60928

    def get_skool_udg(self, y, x):
        ref_page = y + 152
        attr_addr = x + 128 + 256 * ref_page
        ref_addr = x + 256 * ref_page
        ref = self.snapshot[ref_addr]
        attr = self.snapshot[attr_addr]
        udg_page = 128 + 8 * (x // 32)
        udg_addr = ref + 256 * udg_page
        udg_bytes = self.snapshot[udg_addr:udg_addr + 2048:256]
        return Udg(attr, udg_bytes)

    def get_speech_bubble(self, attr=56):
        bubble_udgs = [[], []]
        for n in range(8):
            bubble_udgs[0].append(Udg(attr, self.snapshot[33008 + n:35056 + n:256]))
            bubble_udgs[1].append(Udg(attr, self.snapshot[33016 + n:35064 + n:256]))
        return bubble_udgs

    def get_bubble_udgs(self):
        attr = 56
        udgs = self.get_speech_bubble(attr)
        udgs[0].append(Udg(attr, self.snapshot[33007:35055:256]))
        udgs[1].append(_BLANK_UDG)
        self._fix_bubble(udgs)
        return udgs

    def _fix_bubble(self, udgs):
        """Add transparency to the speech bubble and close the 'open' lip."""
        pixel_coords = (
            (0,  0), (0,  1), (0, 62), (0, 63),
            (1,  0), (1, 63),
            (4, 64), (4, 71),
            (5, 64), (5, 71),
            (6, 64), (6, 65), (6, 71),
            (7, 64), (7, 65), (7, 66), (7, 70), (7, 71)
        )
        self.add_transparency(udgs, pixel_coords)
        for udg in udgs[1][:8]:
            udg.data[7] = 126

    def get_mutable_udgs(self):
        udgs = []
        for x, y in ((6, 2), (8, 2), (47, 2), (50, 2), (78, 2), (45, 8), (50, 8), (65, 14), (67, 14)):
            shield_udg = self.get_skool_udg(y, x)
            udgs.append(shield_udg)
            udgs.append(self.invert(shield_udg))
        safe_udg = self.get_skool_udg(9, 10)
        udgs.append(safe_udg)
        udgs.append(self.invert(safe_udg))
        return [udgs]

    def invert(self, udg):
        bright = udg.attr & 64
        ink = udg.attr & 7
        paper = (udg.attr & 56) // 8
        attr = bright + ink * 8 + paper
        return Udg(attr, udg.data)

    def _wipe_blackboards(self):
        for i in range(32768, 34816, 256):
            self.snapshot[i + 225:i + 231] = [255] * 6
            self.snapshot[i + 233:i + 239] = [255] * 6
        for i in range(34816, 36864, 256):
            self.snapshot[i + 191:i + 225] = [255] * 34
            self.snapshot[i + 231:i + 233] = [255] * 2

    def _remove_speech_bubble(self):
        lip_ref_addr = self.snapshot[32612] + 256 * self.snapshot[32613]
        if lip_ref_addr == 0:
            return
        self.snapshot[lip_ref_addr] = self.snapshot[32614]
        lip_attr_addr = lip_ref_addr + 128
        self.snapshot[lip_attr_addr] = self.snapshot[32615]
        top_left_ref_addr = (lip_ref_addr & 65400) - 512
        self.snapshot[top_left_ref_addr:top_left_ref_addr + 8] = self.snapshot[32616:32624]
        bottom_left_ref_addr = top_left_ref_addr + 256
        self.snapshot[bottom_left_ref_addr:bottom_left_ref_addr + 8] = self.snapshot[32624:32632]
        top_left_attr_addr = top_left_ref_addr + 128
        self.snapshot[top_left_attr_addr:top_left_attr_addr + 8] = self.snapshot[32632:32640]
        bottom_left_attr_addr = top_left_attr_addr + 256
        self.snapshot[bottom_left_attr_addr:bottom_left_attr_addr + 8] = self.snapshot[32640:32648]

    def get_play_area_udgs(self):
        self._wipe_blackboards()
        self._remove_speech_bubble()
        return self.get_skool_udgs(0, 0, 96, 21)

    def get_logo_udgs(self):
        logo_udgs = self.get_logo()
        if self.custom == 1:
            self._adjust_logo(logo_udgs)
        return logo_udgs

    def _adjust_logo(self, logo_udgs):
        take = (
            ('01111100', '11001001', '01111000'),
            ('00010001', '00101010', '01000000'),
            ('00010001', '00101100', '01111000'),
            ('00010001', '11101010', '01000000'),
            ('00010001', '00101001', '01111000')
        )
        for i, p_row in enumerate(take):
            for j, p in enumerate(p_row):
                logo_udgs[0][j].data[i + 1] = int(p, 2)
        too = (
            ('11111001', '10001100'),
            ('00100010', '01010010'),
            ('00100010', '01010010'),
            ('00100010', '01010010'),
            ('00100001', '10001100')
        )
        for i, p_row in enumerate(too):
            for j, p in enumerate(p_row):
                logo_udgs[0][j + 5].data[i + 1] = int(p, 2)

    def get_message_box_udgs(self):
        udgs = self.get_box_graphic(60160)

        # Set the attributes
        for row in udgs:
            for udg in row:
                udg.attr = 23

        # Remove the '0 lines' graphic
        blank = [0] * 4
        for x in (3, 4, 5, 6):
            udgs[0][x].data[4:] = blank
            udgs[1][x].data[:4] = blank

        return udgs

    def _get_font_bitmap(self, character):
        base_address = ord(character) + 55808
        width = self.snapshot[base_address - 256]
        return self.snapshot[base_address:base_address + 256 * width:256]

    def get_font_udgs(self):
        columns = []
        for c in range(32, 128):
            columns.append(0)
            columns.extend(self._get_font_bitmap(chr(c)))
        udg_array = []
        for col in range(len(columns)):
            col_byte = columns[col]
            udg_index = col // 8
            bit = 2 ** (7 - (col - 8 * udg_index))
            if udg_index == len(udg_array):
                udg_array.append([0] * 8)
            udg = udg_array[udg_index]
            for b in range(8):
                udg[7 - b] |= bit * (col_byte & 1)
                col_byte //= 2
        return [[Udg(56, udg) for udg in udg_array]]

class BTSMemory(SkoolMemory):
    def __init__(self, snafile, custom):
        SkoolMemory.__init__(self, snafile, custom)
        self.logo_address = 59176
        self.lesson_box_attr = 87
        self.score_box_address = 58920

    def build_sprite(self, state, attr=None):
        udg_array = []
        for row in range(4):
            udg_array.append([self.get_sprite_udg(state, attr, row, col) for col in range(3)])
        return udg_array

    def _get_sprite_udg(self, state, attr, ref_page, udg_page):
        ref_addr = state + 256 * ref_page
        ref = self.snapshot[ref_addr]
        if ref == 0:
            udg = [0] * 8
            mask = [255] * 8
        else:
            udg_addr = ref + 256 * udg_page
            udg = self.snapshot[udg_addr:udg_addr + 4096:512]
            mask = self.snapshot[udg_addr + 256:udg_addr + 4352:512]
        return Udg(attr, udg, mask)

    def get_skool_udg(self, y, x):
        q_addr = x + 46336
        q = self.snapshot[q_addr]
        h = y + 160
        hl = 180 + q // 2 + 256 * h
        i = 0
        if q & 1:
            p = self.snapshot[hl] & 15
        else:
            p = (self.snapshot[hl] & 240) // 16
        if p == 0:
            i = q & 3 or 2
            if q & 1:
                p = self.snapshot[hl + 256] & 15
            else:
                p = (self.snapshot[hl + 256] & 240) // 16
        attr = i | (8 * p)
        ref_addr = q + 256 * h
        ref = self.snapshot[ref_addr]
        a = 136 // (2 ** (q & 3)) & self.snapshot[144 + q // 4 + 256 * h]
        udg_page = (8 if a & 15 else 0) + (144 if a & 240 else 128)
        udg_addr = ref + 256 * udg_page
        udg_bytes = self.snapshot[udg_addr:udg_addr + 2048:256]
        return Udg(attr, udg_bytes)

    def get_sprite_udg(self, state, attr, row, col):
        as_norm = state | 128
        udg_page = 183 if as_norm < 208 else 199
        col = 2 - col if state & 128 else col
        ref_page = 215 + col * 4 + row
        udg = self._get_sprite_udg(as_norm, attr, ref_page, udg_page)
        if state == 81 and (row, col) == (3, 2):
            # Fix MR WACKER's shoe
            udg.mask[0:2] = [127] * 2
            udg.data[4:7] = [192] * 3
            udg.mask[4:7] = [223] * 3
        return udg

    def get_udg(self, address, attr):
        return Udg(attr, self.snapshot[address:address + 8])

    def get_speech_bubble(self, attr=56):
        top_row = [39392]
        top_row.extend([39648] * 6)
        top_row.append(39904)
        bottom_row = [40160]
        bottom_row.extend([40416] * 6)
        bottom_row.append(40672)
        bubble_udgs = [[self.get_udg(address, attr) for address in top_row]]
        bubble_udgs.append([self.get_udg(address, attr) for address in bottom_row])
        return bubble_udgs

    def get_bubble_udgs(self):
        attr = 56
        udgs = self.get_speech_bubble(attr)
        udgs[0].append(Udg(attr, self.snapshot[39136:39144]))
        udgs[1].append(_BLANK_UDG)
        self._fix_bubble(udgs)
        return udgs

    def _fix_bubble(self, udgs):
        """Add transparency to the speech bubble."""
        pixel_coords = (
            ( 0,  0), ( 0, 63),
            ( 2, 64),
            ( 3, 64), ( 3, 71),
            ( 4, 64), ( 4, 71),
            ( 5, 64), ( 5, 65), (5, 71),
            ( 6, 64), ( 6, 65), (6, 71),
            ( 7, 64), ( 7, 65), (7, 66), (7, 70), (7, 71),
            (15,  0), (15, 63)
        )
        self.add_transparency(udgs, pixel_coords)

    def _alter_skool_udgs(self, address):
        coords = []
        while True:
            y = self.snapshot[address]
            if y == 255:
                break
            x = self.snapshot[address + 1]
            coords.append((x, y))
            udg_lsb = self.snapshot[address + 2]
            attr = self.snapshot[address + 3]
            d = y + 160
            col_ref = self.snapshot[x + 46336]
            self.snapshot[col_ref + 256 * d] = udg_lsb
            z = 2 ** (col_ref & 3)
            e = 128 + (col_ref + 104) // 2
            a = self.snapshot[e + 256 * d]
            if col_ref & 1:
                a = (a & 240) | (attr & 15)
            else:
                a = (16 * (attr & 15)) | (a & 15)
            self.snapshot[e + 256 * d] = a
            a = attr & 192
            if a & 64:
                a = a - 56
            e = 144 + col_ref // 4
            self.snapshot[e + 256 * d] = self.snapshot[e + 256 * d] & 255 - 136 // z | a // z
            address += 4
        return coords

    def _get_dimensions(self, coords):
        x_range = [c[0] for c in coords]
        y_range = [c[1] for c in coords]
        left_x = min(x_range)
        top_y = min(y_range)
        width = max(x_range) - left_x + 1
        height = max(y_range) - top_y + 1
        return left_x, top_y, width, height

    def get_mutable_udg_array(self, address):
        coords = self._alter_skool_udgs(address)
        return self.get_skool_udgs(*self._get_dimensions(coords))

    def get_mutables(self):
        doors = []
        doors.append(56637)    # Left study door
        doors.append(57088)    # Right study door
        doors.append(56576)    # Science Lab storeroom door
        doors.append(57149)    # Boys' skool door
        doors.append(63744)    # Skool gate
        doors.append(56064)    # Drinks cabinet door

        windows = []
        windows.append(55040)  # Top-floor window
        windows.append(55552)  # Middle-floor window

        bike = 57600

        return doors, windows, bike

    def get_cups(self):
        cups = []
        # All cups on the shelf in the boys' skool (empty)
        cups.append((56081, []))
        # Leftmost cup on the shelf in the boys' skool (water/sherry)
        cups.append((56694, [5]))
        # Middle cup on the shelf in the boys' skool (water/sherry)
        cups.append((56950, [5]))
        # Rightmost cup on the shelf in the boys' skool (water/sherry)
        cups.append((57206, [5]))
        # Cup on the shelf in the girls' skool (empty/water/sherry)
        cups.append((56337, [1125, 5]))
        return cups

    def get_inventory_items(self):
        items = []
        items.append(((39144,), 6))        # Safe key
        items.append(((39400,), 7))        # Science Lab storeroom key
        items.append(((39656,), 4))        # Frog
        items.append(((39912, 40168), 5))  # Water pistol (water)
        items.append(((39912, 40168), 3))  # Water pistol (sherry)
        items.append(((40424,), 7))        # Three stinkbombs
        items.append(((40680,), 7))        # Two stinkbombs
        items.append(((40936,), 7))        # One stinkbomb
        items.append(((40928,), 7))        # Mouse
        return items

    def get_mutable_udgs(self):
        udgs = [[None] * 18 for y in range(14)]
        doors, windows, bike = self.get_mutables()

        left_study_door = doors[0]
        left_study_door_closed = self.get_mutable_udg_array(left_study_door)
        self.blit_udgs(udgs, left_study_door_closed, 0, 0)
        left_study_door_open = self.get_mutable_udg_array(left_study_door + 256)
        self.blit_udgs(udgs, left_study_door_open, 3, 0)

        right_study_door = doors[1]
        right_study_door_closed = self.get_mutable_udg_array(right_study_door)
        self.blit_udgs(udgs, right_study_door_closed, 6, 0)
        right_study_door_open = self.get_mutable_udg_array(right_study_door + 256)
        self.blit_udgs(udgs, right_study_door_open, 9, 0)

        science_lab_door = doors[2]
        science_lab_door_closed = self.get_mutable_udg_array(science_lab_door)
        self.blit_udgs(udgs, science_lab_door_closed, 12, 0)
        science_lab_door_open = self.get_mutable_udg_array(science_lab_door + 256)
        self.blit_udgs(udgs, science_lab_door_open, 15, 0)

        skool_door = doors[3]
        skool_door_closed = self.get_mutable_udg_array(skool_door)
        self.blit_udgs(udgs, skool_door_closed, 0, 5)
        skool_door_open = self.get_mutable_udg_array(skool_door + 256)
        self.blit_udgs(udgs, skool_door_open, 3, 5)

        gate = doors[4]
        gate_closed = self.get_mutable_udg_array(gate)
        self.blit_udgs(udgs, gate_closed, 6, 5)
        gate_open = self.get_mutable_udg_array(gate + 256)
        self.blit_udgs(udgs, gate_open, 10, 5)

        cabinet_door = doors[5]
        cabinet_door_closed = self.get_mutable_udg_array(cabinet_door)
        self.blit_udgs(udgs, cabinet_door_closed, 14, 5)
        cabinet_door_open = self.get_mutable_udg_array(cabinet_door + 256)
        self.blit_udgs(udgs, cabinet_door_open, 16, 5)

        top_window = windows[0]
        top_window_closed = self.get_mutable_udg_array(top_window)
        self.blit_udgs(udgs, top_window_closed, 0, 10)
        top_window_open = self.get_mutable_udg_array(top_window + 256)
        self.blit_udgs(udgs, top_window_open, 3, 10)

        middle_window = windows[1]
        middle_window_closed = self.get_mutable_udg_array(middle_window)
        self.blit_udgs(udgs, middle_window_closed, 6, 10)
        middle_window_open = self.get_mutable_udg_array(middle_window + 256)
        self.blit_udgs(udgs, middle_window_open, 8, 10)

        tree_without_bike = self.get_mutable_udg_array(bike)
        self.blit_udgs(udgs, tree_without_bike, 10, 10)
        tree_with_bike = self.get_mutable_udg_array(bike + 256)
        self.blit_udgs(udgs, tree_with_bike, 13, 10)

        cups = self.get_cups()

        boy_cups_empty_udgs = self.get_mutable_udg_array(cups[0][0])
        left_cup_empty_udg = boy_cups_empty_udgs[0][0]
        self.blit_udgs(udgs, [[left_cup_empty_udg]], 14, 7)
        middle_cup_empty_udg = boy_cups_empty_udgs[0][2]
        self.blit_udgs(udgs, [[middle_cup_empty_udg]], 14, 8)
        girl_cup_empty = self.get_mutable_udg_array(cups[4][0])
        self.blit_udgs(udgs, girl_cup_empty, 14, 9)

        left_cup_water = self.get_mutable_udg_array(cups[1][0])
        self.blit_udgs(udgs, left_cup_water, 15, 7)
        middle_cup_water = self.get_mutable_udg_array(cups[2][0])
        self.blit_udgs(udgs, middle_cup_water, 15, 8)
        girl_cup_water = self.get_mutable_udg_array(cups[4][0] + cups[4][1][0])
        self.blit_udgs(udgs, girl_cup_water, 15, 9)

        left_cup_sherry = self.get_mutable_udg_array(cups[1][0] + cups[1][1][0])
        self.blit_udgs(udgs, left_cup_sherry, 16, 7)
        middle_cup_sherry = self.get_mutable_udg_array(cups[2][0] + cups[2][1][0])
        self.blit_udgs(udgs, middle_cup_sherry, 16, 8)
        girl_cup_sherry = self.get_mutable_udg_array(cups[4][0] + sum(cups[4][1]))
        self.blit_udgs(udgs, girl_cup_sherry, 16, 9)

        for y in range(len(udgs)):
            for x in range(len(udgs[y])):
                if udgs[y][x] is None:
                    udgs[y][x] = _BLANK_UDG

        if self.custom == 1:
            self._draw_shields_and_safe(udgs)
        return udgs

    def get_inventory_udgs(self):
        udgs = []
        for addresses, attr in self.get_inventory_items():
            for address in addresses:
                udgs.append(self.get_udg(address, attr))
        return [udgs]

    def blit_udgs(self, montage, udgs, x, y):
        for i, row in enumerate(udgs):
            montage[y + i][x:x + len(row)] = row

    def _fix_graphic_glitches(self):
        self.snapshot[59001] = 204 # Score box
        self.snapshot[47249] = 252 # EINSTEIN's head
        self.snapshot[47254] = 255 # EINSTEIN's head (lying down)
        self.snapshot[47265] = 255 # BOY WANDER's head
        self.snapshot[53356] = 171 # MR CREAK's ear
        self.snapshot[53896] = 228 # MR WACKER's trousers
        self.snapshot[53461] = 95  # MR WITHIT's and ALBERT's shoes (1)
        self.snapshot[53973] = 95  # MR WITHIT's and ALBERT's shoes (2)
        self.snapshot[54485] = 223 # MR WITHIT's and ALBERT's shoes (3)
        self.snapshot[54487] = 250 # MR WITHIT's and ALBERT's shoes (4)
        self.snapshot[51417] = 235 # MR WITHIT's and MISS TAKE's hand
        self.snapshot[50281] = 222 # Kids' shoes
        self.snapshot[49864] = 239 # HAYLEY's and little girl's back foot
        self.snapshot[50877] = 238 # HAYLEY's and little girl's foot
        self.snapshot[47209] = 231 # Boys' hands
        self.snapshot[53853] = 223 # ALBERT's waist
        self.snapshot[54865] = 127 # Under Albert's arm
        self.snapshot[52316] = 191 # Back of Albert's head (1)
        self.snapshot[54876] = 191 # Back of Albert's head (2)
        self.snapshot[52089] = 30  # Mr Creak's hand (1)
        self.snapshot[52345] = 222 # Mr Creak's hand (2)

        # MR ROCKITT's lab coat (arm up)
        self.snapshot[51644] = 232
        self.snapshot[51900] = 232
        self.snapshot[52668] = 36
        self.snapshot[52924] = 164
        self.snapshot[53180] = 44
        self.snapshot[53436] = 172
        self.snapshot[53692] = 46
        self.snapshot[53948] = 174
        self.snapshot[54204] = 54
        self.snapshot[54460] = 182
        self.snapshot[54716] = 53
        self.snapshot[54972] = 181

    def _fix_sprites(self, udgs):
        """Apply fixes to graphic glitches that cannot be fixed by adjusting
        tiles (because the tiles are used in multiple places, and the fix
        applies to a subset of those places).
        """
        pixel_coords = (
            # Eric's face
            ( 10,   7), ( 10,  55), ( 10, 103), ( 10, 175), ( 10, 199), ( 10, 223), ( 10, 247),
            ( 11,   7), ( 11,  55), ( 11, 103), ( 11, 175), ( 11, 199), ( 11, 223), ( 11, 247),
            ( 12,   7), ( 12,  55), ( 12, 103), ( 12, 175), ( 12, 199), ( 12, 223), ( 12, 247),
            ( 13,   7), ( 13,  55), ( 13, 103), ( 13, 175), ( 13, 199),             ( 13, 247),
            ( 14,   7), ( 14,  55), ( 14, 103),             ( 14, 199),             ( 14, 247),

            # BOY WANDER's face
            ( 41,   7), ( 41,  55), ( 41, 103), ( 41, 175), ( 41, 247), ( 41, 271),
            ( 43,   7), ( 43,  55), ( 43, 103), ( 43, 175), ( 43, 247),
            ( 44,   7), ( 44,  55), ( 44, 103), ( 44, 175), ( 44, 247),
            ( 45,   7), ( 45,  55), ( 45, 103), ( 45, 175), ( 45, 247),
            ( 46,   7), ( 46,  55), ( 46, 103),             ( 46, 247),

            # ANGELFACE's head
            ( 73,   7), ( 73,  55), ( 73, 103), ( 73, 199), ( 73, 223),

            (152,  27), # Little boy's hand
            (191,  55), # MR WACKER's foot
            (239, 233), (239, 281), # Albert's elbow
            (253,  88), (254,  88)  # MISS TAKE's gown
        )
        self.add_transparency(udgs, pixel_coords)

        # End of the frog's leg: (46,352)
        udgs[5][44].mask[6] &= 127

    def get_shield_udgs(self):
        return (self.get_skool_udg(2, 74), self.get_skool_udg(2, 79), self.get_skool_udg(2, 82))

    def get_safe_udg(self):
        return self.get_skool_udg(2, 81)

    def _initialise_mutables(self):
        self._alter_skool_udgs(64000) # Open the skool gate
        self._alter_skool_udgs(57405) # Open the skool door
        self._alter_skool_udgs(57856) # Chain the bike up
        self._alter_skool_udgs(55040) # Close the top-floor window
        self._alter_skool_udgs(55552) # Close the middle-floor window
        self._alter_skool_udgs(56064) # Close the drinks cabinet door
        self._alter_skool_udgs(56637) # Close the left study door
        self._alter_skool_udgs(57088) # Close the right study door
        self._alter_skool_udgs(56576) # Close the science lab storeroom door
        self._alter_skool_udgs(56081) # Empty the cups in the boys' skool
        self._alter_skool_udgs(56337) # Empty the cup in the girls' skool

    def _wipe_blackboards(self):
        for i in range(32768, 34816, 256):
            self.snapshot[i:i + 80] = [255] * 80

    def get_play_area_udgs(self):
        self._initialise_mutables()
        self._wipe_blackboards()
        skool_udgs = self.get_skool_udgs(0, 0, 192, 21)
        if self.custom == 1:
            self._place_shields(skool_udgs)
        return skool_udgs

    def _place_shields(self, skool_udgs):
        self.s_udgs = []

        # Add shield UDGs with green, cyan, yellow and white paper (ink
        # unchanged)
        shield_udgs = self.get_shield_udgs()
        for paper in (4, 5, 6, 7):
            udgs = []
            for shield_udg in shield_udgs:
                ink = shield_udg.attr & 7
                udg = Udg(8 * paper + ink, shield_udg.data)
                udgs.append(udg)
            self.s_udgs.append(udgs)
        self.s_udgs.append([self.get_safe_udg()])

        # Remove the picture from the wall in the Science Lab storeroom
        for x in (55, 56, 57):
            for y in (9, 10):
                skool_udgs[y][x].data = [0] * 8
        skool_udgs[9][58].data = [3] * 8
        skool_udgs[10][58].data = (3, 3, 3, 3, 3, 0, 0, 0)

        # Place the extra shields (x, y, paper [4567], index [012])
        shields = (
            (4, 2, 5, 0), (9, 2, 5, 1), (162, 2, 5, 1), (167, 2, 5, 2),
            (33, 8, 6, 1), (38, 8, 6, 2), (57, 9, 5, 2), (173, 8, 6, 0),
            (4, 15, 4, 1), (8, 15, 4, 2), (12, 15, 4, 0), (30, 14, 7, 2),
            (186, 14, 7, 1)
        )
        for x, y, udg_i, udg_j in shields:
            s_udg = self.s_udgs[udg_i - 4][udg_j]
            skool_udgs[y][x] = Udg(s_udg.attr, s_udg.data[:])

    def _draw_shields_and_safe(self, mutable_udgs):
        # Remove the picture on the wall from the storeroom door images
        for x in (13, 14):
            for y in (0, 1):
                mutable_udgs[y][x].data = [0] * 8
        mutable_udgs[0][17].data[6:] = [3, 3]
        mutable_udgs[1][17].data[:4] = [3, 3, 3, 3]

        # Draw the shields and the safe
        udg_locations = (
            ( 6,  9), ( 8,  9), (10,  9),  # Shields with green paper
            (16, 10), (16, 11), (16, 12),  # Shields with cyan paper
            ( 0, 13), ( 2, 13), ( 4, 13),  # Shields with yellow paper
            (10, 13), (12, 13), (14, 13),  # Shields with white paper
            (12,  9)                       # Safe
        )
        i = 0
        for udg_set in self.s_udgs:
            for udg in udg_set:
                ink = udg.attr & 7
                paper = (udg.attr & 56) // 8
                bright = udg.attr & 64
                inverse_udg = Udg(bright + 8 * ink + paper, udg.data)
                x, y = udg_locations[i]
                mutable_udgs[y][x] = udg
                mutable_udgs[y][x + 1] = inverse_udg
                i += 1

    def get_logo_udgs(self):
        logo_udgs = self.get_logo()
        if self.custom == 1:
            self._adjust_logo(logo_udgs)
        return logo_udgs

    def _adjust_logo(self, logo_udgs):
        # Shift logo 8 pixels to the left to make room for 'daze'
        for row in logo_udgs:
            row.append(row.pop(0))

        # Write the word 'daze' on the logo
        bit_patterns = (
            ('',         '00000000', '00000000'),
            ('',         '00000000', '00000000'),
            ('',         '00000000', '00000000'),
            ('',         '00000000', '00011100'),
            ('',         '00000000', '00100010'),
            ('',         '00000000', '00100100'),
            ('',         '00000000', '00101001'),
            ('',         '00000000', '10010010'),
            ('10000100', '00000001', '10001100'),
            ('10001000', '00000010', '10000000'),
            ('01110000', '00000100', '10010000'),
            ('00000000', '00000000', '10100000'),
            ('10000000', '01110000', '11000000'),
            ('10000000', '10001000', '10000000'),
            ('00100000', '10000100', '00000000'),
            ('00010000', '10000110', '00000000'),
            ('00001000', '10000100', '00000000'),
            ('00000100', '01001000', '00000000'),
            ('00011110', '00110000', '00000000'),
            ('00010001', '00000000', '00000000'),
            ('00010000', '10000000', '00000000'),
            ('00010001', '00000000', '00000000'),
            ('00010001', '00000000', '00000000'),
            ('00001110', '00000000', '00000000')
        )

        # Convert the bit patterns into UDG data
        new_udgs = []
        for i, patterns in enumerate(bit_patterns):
            row = i // 8
            if len(new_udgs) == row:
                new_udgs.append([])
                for j in range(len(patterns)):
                    new_udgs[row].append([])
            for k, p in enumerate(patterns):
                if p:
                    new_udgs[row][k].append(int(p, 2))

        # Insert the UDGs
        for y in range(3):
            for x in range(1, len(new_udgs[y]) + 1):
                data = new_udgs[y][-x]
                if data:
                    logo_udgs[y][-x].data = data

    def get_message_box_udgs(self):
        udg = Udg(16, [0] * 8)
        return [[udg] * 8] * 3

    def get_animatory_states(self):
        self._fix_graphic_glitches()
        montage = []
        for y in range(8):
            montage.extend([[], [], [], []])
            for x in range(16):
                state = x + 16 * y
                sprite = self.build_sprite(state, 120)
                for i, row in enumerate(sprite):
                    montage[4 * y + i].extend(row)
        self._fix_sprites(montage)
        return montage

    def get_icon_udgs(self):
        eric = self.build_sprite(1, 112)
        udgs = [eric[1][:2]]
        udgs.append(eric[2][:2])
        return udgs
