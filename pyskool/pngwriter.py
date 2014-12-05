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

import zlib

TRANSPARENT = 'TRANSPARENT'
BLACK = 'BLACK'
BLUE = 'BLUE'
RED = 'RED'
MAGENTA = 'MAGENTA'
GREEN = 'GREEN'
CYAN = 'CYAN'
YELLOW = 'YELLOW'
WHITE = 'WHITE'
BRIGHT_BLUE = 'BRIGHT_BLUE'
BRIGHT_RED = 'BRIGHT_RED'
BRIGHT_MAGENTA = 'BRIGHT_MAGENTA'
BRIGHT_GREEN = 'BRIGHT_GREEN'
BRIGHT_CYAN = 'BRIGHT_CYAN'
BRIGHT_YELLOW = 'BRIGHT_YELLOW'
BRIGHT_WHITE = 'BRIGHT_WHITE'

# http://www.libpng.org/pub/png/spec/iso/index-object.html
PNG_SIGNATURE = (137, 80, 78, 71, 13, 10, 26, 10)
IHDR = (73, 72, 68, 82)
PLTE = (80, 76, 84, 69)
IDAT = (73, 68, 65, 84)
IEND_CHUNK = (0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130)
CRC_MASK = 4294967295

class PngWriter:
    def __init__(self, palette=None):
        full_palette = self._get_default_palette()
        if palette:
            full_palette.update(palette)
        self._create_colours(full_palette)
        self._create_attr_index()
        self._create_crc_table()
        self.png_signature = bytearray(PNG_SIGNATURE)
        self.idat = bytearray(IDAT)
        self.iend_chunk = bytearray(IEND_CHUNK)

    def write_image(self, udg_array, img_file, scale=1, mask=False, width=None):
        width = width or 8 * len(udg_array[0]) * scale
        height = 8 * len(udg_array) * scale
        palette, attr_map, trans = self._get_palette(udg_array, scale, mask)
        bit_depth, plte_chunk, img_data = self._build_image_data(udg_array, scale, palette, attr_map, trans, width)

        # PNG signature
        img_file.write(self.png_signature)

        # IHDR
        self._write_ihdr_chunk(img_file, width, height, bit_depth)

        # PLTE
        self._write_chunk(img_file, plte_chunk)

        # IDAT
        self._write_img_data_chunk(img_file, self.idat + img_data)

        # IEND
        img_file.write(self.iend_chunk)

    def _get_default_palette(self):
        return  {
            TRANSPARENT: (0, 254, 0),
            BLACK: (0, 0, 0),
            BLUE: (0, 0, 197),
            RED: (197, 0, 0),
            MAGENTA: (197, 0, 197),
            GREEN: (0, 198, 0),
            CYAN: (0, 198, 197),
            YELLOW: (197, 198, 0),
            WHITE: (205, 198, 205),
            BRIGHT_BLUE: (0, 0, 255),
            BRIGHT_RED: (255, 0, 0),
            BRIGHT_MAGENTA: (255, 0, 255),
            BRIGHT_GREEN: (0, 255, 0),
            BRIGHT_CYAN: (0, 255, 255),
            BRIGHT_YELLOW: (255, 255, 0),
            BRIGHT_WHITE: (255, 255, 255)
        }

    def _create_colours(self, palette):
        colours = []
        colours.append(palette[TRANSPARENT])
        colours.append(palette[BLACK])
        colours.append(palette[BLUE])
        colours.append(palette[RED])
        colours.append(palette[MAGENTA])
        colours.append(palette[GREEN])
        colours.append(palette[CYAN])
        colours.append(palette[YELLOW])
        colours.append(palette[WHITE])
        colours.append(palette[BRIGHT_BLUE])
        colours.append(palette[BRIGHT_RED])
        colours.append(palette[BRIGHT_MAGENTA])
        colours.append(palette[BRIGHT_GREEN])
        colours.append(palette[BRIGHT_CYAN])
        colours.append(palette[BRIGHT_YELLOW])
        colours.append(palette[BRIGHT_WHITE])
        self.colours = colours

    def _create_attr_index(self):
        self.attr_index = {}
        for attr in range(128):
            if attr & 64:
                ink = 8 + (attr & 7)
                paper = 8 + (attr & 56) // 8
                if ink == 8:
                    ink = 1
                if paper == 8:
                    paper = 1
            else:
                ink = 1 + (attr & 7)
                paper = 1 + (attr & 56) // 8
            self.attr_index[attr] = (paper, ink)

    def _get_all_colours(self, udg_array, mask):
        # Find all the colours in an image
        attrs = set()
        colours = set()
        has_trans = 0
        all_masked = 1

        for row in udg_array:
            for udg in row:
                attr = udg.attr
                attrs.add(attr & 127)
                paper, ink = self.attr_index[attr & 127]
                if udg.paper is not None:
                    attr = udg.paper * 8
                    paper = self.attr_index[attr][0]
                    attrs.add(attr)
                if mask and udg.mask:
                    data = [udg.data[i] & udg.mask[i] for i in range(8)]
                    has_non_trans = False
                    if any(data):
                        colours.add(ink)
                        has_non_trans = True
                    if any([b < 255 for b in udg.mask]):
                        colours.add(paper)
                        has_non_trans = True
                    if any([data[i] | udg.mask[i] > data[i] for i in range(8)]):
                        has_trans = 1
                else:
                    if any(udg.data):
                        colours.add(ink)
                    if any([b < 255 for b in udg.data]):
                        colours.add(paper)
                    all_masked = 0

        trans = 1 + all_masked if has_trans else 0
        return colours, attrs, trans

    def _get_palette(self, udg_array, scale, mask):
        colours, attrs, trans = self._get_all_colours(udg_array, mask)

        colour_map = {}
        palette = []
        i = 0
        if trans:
            palette.extend(self.colours[0])
            i += 1
        for colour in colours:
            palette.extend(self.colours[colour])
            colour_map[colour] = i
            i += 1

        attr_map = {}
        for attr in attrs:
            paper, ink = self.attr_index[attr]
            attr_map[attr] = (colour_map.get(paper, 0), colour_map.get(ink, 0))

        return palette, attr_map, trans

    def _create_crc_table(self):
        self.crc_table = []
        for i in range(256):
            c = i
            for k in range(8):
                if c & 1:
                    c = 3988292384 ^ (c >> 1)
                else:
                    c = c >> 1
            self.crc_table.append(c)

    def _to_bytes(self, num):
        return (num >> 24, (num >> 16) & 255, (num >> 8) & 255, num & 255)

    def _write_ihdr_chunk(self, img_file, width, height, bit_depth):
        data = list(IHDR) # chunk type
        data.extend(self._to_bytes(width)) # width
        data.extend(self._to_bytes(height)) # height
        data.extend((bit_depth, 3)) # bit depth and colour type
        data.extend((0, 0, 0)) # compression, filter and interlace methods
        self._write_chunk(img_file, data)

    def _build_image_data(self, udg_array, scale, palette, attr_map, trans, width):
        palette_size = len(palette) // 3
        if palette_size > 4:
            bit_depth = 4
        elif palette_size > 2:
            bit_depth = 2
        else:
            bit_depth = 1
        plte_chunk = list(PLTE)
        plte_chunk.extend(palette)

        img_data = self._build_image_data_bd_any(udg_array, scale, attr_map, trans, bit_depth, width)
        return bit_depth, plte_chunk, img_data

    def _get_crc(self, byte_list):
        crc = CRC_MASK
        for b in byte_list:
            crc = self.crc_table[(crc ^ b) & 255] ^ (crc >> 8)
        return self._to_bytes(crc ^ CRC_MASK)

    def _write_chunk(self, img_file, chunk_data):
        img_file.write(bytearray(self._to_bytes(len(chunk_data) - 4))) # length
        img_file.write(bytearray(chunk_data))
        img_file.write(bytearray(self._get_crc(chunk_data))) # CRC

    def _write_img_data_chunk(self, img_file, img_data):
        img_file.write(bytearray(self._to_bytes(len(img_data) - 4))) # length
        img_file.write(img_data)
        img_file.write(bytearray(self._get_crc(img_data))) # CRC

    def _build_image_data_bd_any(self, udg_array, scale, attr_map, trans, bit_depth, width):
        compressor = zlib.compressobj(9)
        img_data = bytearray()
        for row in udg_array:
            for i in range(8):
                p = []
                for udg in row:
                    byte = udg.data[i]
                    attr = udg.attr
                    paper, ink = attr_map[attr & 127]
                    if udg.paper is not None:
                        paper = attr_map[udg.paper * 8][0]
                    if trans and udg.mask:
                        mask_byte = udg.mask[i]
                        byte &= mask_byte
                    else:
                        mask_byte = 0
                    for b in range(8):
                        if byte & 128:
                            p.extend((ink,) * scale)
                        elif mask_byte & 128 == 0:
                            p.extend((paper,) * scale)
                        else:
                            p.extend((0,) * scale)
                        byte *= 2
                        mask_byte *= 2
                scanline = bytearray((0,))
                if bit_depth == 1:
                    p.extend((0,) * (8 - len(p) & 7))
                    scanline.extend([p[j] * 128 + p[j + 1] * 64 + p[j + 2] * 32 + p[j + 3] * 16 + p[j + 4] * 8 + p[j + 5] * 4 + p[j + 6] * 2 + p[j + 7] for j in range(0, len(p), 8)])
                elif bit_depth == 2:
                    p.extend((0,) * (4 - len(p) & 3))
                    scanline.extend([p[j] * 64 + p[j + 1] * 16 + p[j + 2] * 4 + p[j + 3] for j in range(0, len(p), 4)])
                elif bit_depth == 4:
                    p.extend((0,) * (2 - len(p) & 1))
                    scanline.extend([p[j] * 16 + p[j + 1] for j in range(0, len(p), 2)])
                # PY: No need to convert to bytes in Python 3
                img_data.extend(compressor.compress(bytes(scanline[:width] * scale)))
        img_data.extend(compressor.flush())
        return img_data
