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
try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen, URLError
import zipfile
from io import BytesIO

from . import user_dir
from .skoolimage import SDMemory, BTSMemory, Udg
from .pngwriter import PngWriter, WHITE, BLACK
from .iniparser import IniParser

show_info = True

SKOOL_DAZE = 'skool_daze'
BACK_TO_SKOOL = 'back_to_skool'

def info(text):
    if show_info:
        sys.stdout.write('{0}\n'.format(text))

def error(text):
    sys.stderr.write('Error: {0}\n'.format(text))

def get_tzx(name, sources):
    for source in sources:
        url, sep, member = source.partition('|')
        if member and not url.lower().endswith('.zip'):
            error('Unsupported archive type: {0}'.format(os.path.basename(url)))
            continue

        try:
            info('Downloading {0}'.format(url))
            u = urlopen(url, timeout=30)
            data = u.read()
        except URLError as e:
            error(e.args[0])
            continue

        if member:
            try:
                z = zipfile.ZipFile(BytesIO(data))
                tzx = z.open(member)
            except (KeyError, zipfile.BadZipfile) as e:
                error(e.args[0])
                continue
            data = tzx.read()

        fname = os.path.join(user_dir, '{0}.tzx'.format(name))
        with open(fname, 'wb') as f:
            f.write(data)

        info('Saved {0}'.format(fname))
        return fname

    error('Unable to retrieve a TZX file')
    sys.exit(1)

def find_tzx_or_snapshot(name, sources):
    for suffix in ('tzx', 'sna', 'z80', 'szx'):
        fname = os.path.join(user_dir, '{0}.{1}'.format(name, suffix))
        if os.path.isfile(fname):
            info('Found {0}'.format(fname))
            return fname
    return get_tzx(name, sources)

def flip_udgs(udgs):
    flipped = []
    for row in udgs:
        flipped_row = []
        for udg in row:
            flipped_data = []
            flipped_mask = []
            for i in range(8):
                flipped_data.append(flip_byte(udg.data[i]))
                if udg.mask:
                    flipped_mask.append(flip_byte(udg.mask[i]))
            flipped_udg = Udg(udg.attr, flipped_data, flipped_mask)
            flipped_udg.paper = udg.paper
            flipped_row.insert(0, flipped_udg)
        flipped.append(flipped_row)
    return flipped

def flip_byte(byte):
    f = 0
    for b in range(8):
        f = 2 * f + (byte & 1)
        byte //= 2
    return f

def switch_udgs(udgs):
    # Swap pairs of UDGs in each row
    switched = []
    for row in udgs:
        switched_row = [None] * len(row)
        for i, udg in enumerate(row):
            if i % 2:
                switched_row[i - 1] = udg
            else:
                switched_row[i + 1] = udg
        switched.append(switched_row)
    return switched

def write_images(writer, udgs, image_fnames, prefix, flip=False, switch=False, force=False):
    # ink and paper
    fname = image_fnames[prefix]
    if force or not os.path.isfile(fname):
        write_image(writer, udgs, fname, flip=flip, switch=switch)

    # ink
    fname = image_fnames['{0}_ink'.format(prefix)]
    if force or not os.path.isfile(fname):
        for row in udgs:
            for udg in row:
                udg.paper = 15
        write_image(writer, udgs, fname, flip=flip, switch=switch)

    # paper
    fname = image_fnames['{0}_paper'.format(prefix)]
    if force or not os.path.isfile(fname):
        blank = [0] * 8
        for row in udgs:
            for udg in row:
                udg.paper = None
                udg.data = blank
        write_image(writer, udgs, fname, flip=flip, switch=switch)

def write_image(writer, udgs, fname, scale=1, mask=False, width=None, flip=False, switch=False):
    if flip:
        udgs = flip_udgs(udgs)
    if switch:
        udgs = switch_udgs(udgs)
    info('Writing {0}'.format(fname))
    with open(fname, 'wb') as f:
        writer.write_image(udgs, f, scale, mask, width)

def get_images(images_ini, game, custom, odir, verbose=True, force=False):
    global show_info
    show_info = verbose
    images_dir = os.path.join(odir, 'images', 'originalx1')
    flip = False
    switch = False
    images = {}
    if game == SKOOL_DAZE:
        flip = custom == 2
        switch = flip
        game_subdir = os.path.join(images_dir, {
            0: 'skool_daze',
            1: 'skool_daze_take_too',
            2: 'ezad_looks',
        }[custom])
        parent_game_subdir = os.path.join(images_dir, 'skool_daze')
        skool_subdir = parent_game_subdir if custom == 1 else game_subdir
        message_box_subdir = parent_game_subdir
    elif game == BACK_TO_SKOOL:
        skool_subdir = game_subdir = os.path.join(images_dir, {
            0: 'back_to_skool',
            1: 'back_to_skool_daze'
        }[custom])
        parent_game_subdir = os.path.join(images_dir, 'back_to_skool')
        images['inventory'] = os.path.join(parent_game_subdir, 'inventory.png')
        message_box_subdir = os.path.join(images_dir, 'skool_daze') if custom == 1 else parent_game_subdir
    common_subdir = os.path.join(images_dir, 'common')

    images.update({
        'icon': os.path.join(odir, 'icon.png'),
        'font': os.path.join(common_subdir, 'font.png'),
        'sprites': os.path.join(common_subdir, 'sprites.png'),
        'bubble': os.path.join(parent_game_subdir, 'bubble.png'),
        'lesson_box': os.path.join(parent_game_subdir, 'lesson_box.png'),
        'score_box': os.path.join(parent_game_subdir, 'scorebox.png'),
        'message_box': os.path.join(message_box_subdir, 'message_box.png'),
        'logo': os.path.join(game_subdir, 'logo.png'),
        'mutables': os.path.join(skool_subdir, 'mutables.png'),
        'mutables_ink': os.path.join(skool_subdir, 'mutables_ink.png'),
        'mutables_paper': os.path.join(skool_subdir, 'mutables_paper.png'),
        'skool': os.path.join(skool_subdir, 'skool.png'),
        'skool_ink': os.path.join(skool_subdir, 'skool_ink.png'),
        'skool_paper': os.path.join(skool_subdir, 'skool_paper.png')
    })
    missing_images = set()
    for img_id, img_fname in images.items():
        if force or not os.path.isfile(img_fname):
            missing_images.add(img_id)
    if not missing_images:
        info('All images present')
        return

    ini_parser = IniParser(images_ini, show_info)
    if game == SKOOL_DAZE or custom == 1 or 'font' in missing_images:
        sd_sources = ini_parser.parse_section('SkoolDaze', split=False)
        if not sd_sources:
            error('No SkoolDaze section in {0}'.format(images_ini))
            sys.exit(1)
        skool_daze = SDMemory(find_tzx_or_snapshot(SKOOL_DAZE, sd_sources), custom)
    if game == BACK_TO_SKOOL or missing_images & set(('icon', 'sprites')):
        bts_sources = ini_parser.parse_section('BackToSkool', split=False)
        if not bts_sources:
            error('No BackToSkool section in {0}'.format(images_ini))
            sys.exit(1)
        back_to_skool = BTSMemory(find_tzx_or_snapshot(BACK_TO_SKOOL, bts_sources), custom)
    if game == SKOOL_DAZE:
        skool = skool_daze
    elif game == BACK_TO_SKOOL:
        skool = back_to_skool

    if not os.path.isdir(common_subdir):
        os.makedirs(common_subdir)
    if not os.path.isdir(parent_game_subdir):
        os.makedirs(parent_game_subdir)
    if not os.path.isdir(game_subdir):
        os.makedirs(game_subdir)
    if not os.path.isdir(message_box_subdir):
        os.makedirs(message_box_subdir)

    writer = PngWriter()

    # Icon
    if 'icon' in missing_images:
        write_image(writer, back_to_skool.get_icon_udgs(), images['icon'], scale=2, flip=True)

    # Sprites (common)
    if 'sprites' in missing_images:
        write_image(writer, back_to_skool.get_animatory_states(), images['sprites'], mask=True)

    # Font (common)
    if 'font' in missing_images:
        font_writer = PngWriter({WHITE: (255, 254, 253), BLACK: (0, 1, 2)})
        write_image(font_writer, skool_daze.get_font_udgs(), images['font'], width=459)

    # Message box
    if 'message_box' in missing_images:
        message_box_skool = skool_daze if game == SKOOL_DAZE or custom == 1 else skool
        write_image(writer, message_box_skool.get_message_box_udgs(), images['message_box'])

    # Lesson box
    if 'lesson_box' in missing_images:
        write_image(writer, skool.get_lesson_box_udgs(), images['lesson_box'])

    # Score box
    if 'score_box' in missing_images:
        write_image(writer, skool.get_score_box_udgs(), images['score_box'])

    # Speech bubble
    if 'bubble' in missing_images:
        write_image(writer, skool.get_bubble_udgs(), images['bubble'], mask=True)

    # BTS inventory
    if 'inventory' in missing_images:
        write_image(writer, skool.get_inventory_udgs(), images['inventory'])

    # Logo
    if 'logo' in missing_images:
        write_image(writer, skool.get_logo_udgs(), images['logo'], flip=flip)

    # Skool
    if missing_images & set(('skool', 'skool_ink', 'skool_paper')):
        write_images(writer, skool.get_play_area_udgs(), images, 'skool', flip=flip, force=force)

    # Mutables
    if missing_images & set(('mutables', 'mutables_ink', 'mutables_paper')):
        write_images(writer, skool.get_mutable_udgs(), images, 'mutables', flip=flip, switch=switch, force=force)
