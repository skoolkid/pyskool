# -*- coding: utf-8 -*-

# Copyright 2013, 2014 Richard Dymond (rjdymond@gmail.com)
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
import math

FRAME_T_STATES = 69888
INTERRUPT_DELAY = 942
CONTENTION_FACTOR = 0.34

SKOOL_DAZE = 'skool_daze'
BACK_TO_SKOOL = 'back_to_skool'

def delays_to_samples(delays, sample_rate, max_amplitude):
    sample_delay = 3500000.0 / sample_rate
    samples = []
    direction = 1
    i = 0
    d0 = 0
    d1 = delays[i]
    t = 0
    while 1:
        while t >= d1:
            i += 1
            if i >= len(delays):
                break
            d0 = d1
            d1 += delays[i]
            direction *= -1
        if i >= len(delays):
            break
        sample = direction * int(max_amplitude * math.sin(math.pi * (t - d0) / (d1 - d0)))
        if sample > 32767:
            sample = 32767
        elif sample < -32768:
            sample = 32768
        elif sample < 0:
            sample += 65536
        samples.append(sample)
        t += sample_delay
    return samples

def add_contention(delays, contention=True, interrupts=False, cycle=0):
    c_start = 14334
    c_end = 57248
    for i, delay in enumerate(delays):
        d = 0
        while d < delay:
            if interrupts and cycle == 0:
               cycle = INTERRUPT_DELAY
               if i:
                   delay += INTERRUPT_DELAY
            end = min(FRAME_T_STATES, cycle + delay - d)
            if contention and c_start <= end and cycle < c_end:
                contended_cycles = min(c_end, end) - max(cycle, c_start)
                delay += int(contended_cycles * CONTENTION_FACTOR)
            d += end - cycle
            cycle = end % FRAME_T_STATES
        delays[i] = delay

def sd65122(d, e, h):
    delays = []
    for n in range(d or 256):
        delays.append(13 * (e or 256) + 50)
        e = (e + h) & 255
    return delays

def bts62155(d, e, h):
    delays = []
    for n in range(d or 256):
        delays.append(13 * (e or 256) + 50)
        e = (e + h) & 255
    if d & 1:
        delays.append(13 * (e or 256) + 52)
    return delays

def bts29836(b, de):
    e, d = de % 256, de // 256
    inner_delay = 13 * (b or 256) + 30
    delays = [inner_delay] * ((e or 256) - 1)
    if d > 1:
        outer_delay = inner_delay + 11
        inner_delays = [inner_delay] * 255
        for n in range(d - 1):
            delays.append(outer_delay)
            delays.extend(inner_delays)
    if de & 1 == 0:
        delays.append(inner_delay + 13)
    return delays

def jump():
    # SD 60139
    delays = sd65122(50, 96, 3)
    delays.append(3282)
    delays += [2532] * 7 # Walking sound (SD 65088)
    add_contention(delays, contention=False, interrupts=True)
    return delays

def catapult():
    # SD 65141, BTS 63861
    delays = sd65122(128, 0, 248)
    add_contention(delays, contention=False, interrupts=True)
    return delays

def shield():
    # SD 58604
    return sd65122(64, 0, 254) * 16

def hit(cycle):
    # SD 60128
    delays = [2532] * 15
    delays[7] = 2589
    add_contention(delays, contention=False, interrupts=True, cycle=cycle)
    return delays

def hit0():
    return hit(17472)

def hit1():
    return hit(17472 * 3)

def bingo():
    # BTS 62178#62404
    delays = bts62155(255, 255, 255)
    delays += ([83] + delays) * 4
    add_contention(delays, contention=False, interrupts=True)
    return delays

def sherry():
    # BTS 23907#23988
    delays = bts62155(0, 0, 2)
    add_contention(delays, contention=False, interrupts=True)
    return delays

def knocked_out():
    # SD 65111, BTS 62094#62147
    delays = sd65122(0, 0, 1)
    add_contention(delays, contention=False, interrupts=True)
    return delays

def mouse():
    # BTS 28952#28964
    squeak = bts29836(26, 1632)
    pause_delay = 399464 + squeak[0]
    delays = squeak + ([pause_delay] + squeak[1:]) * 2
    add_contention(delays, interrupts=True)
    return delays

def conker():
    # BTS 29896#29978
    delays = bts29836(40, 10240)
    add_contention(delays, interrupts=True)
    return delays

def safe_key():
    # BTS 30804#30853
    delays = bts29836(1, 256)
    for n in range(255, 0, -1):
        subdelays = bts29836((n & 63) + 1, 256)
        delays.append(119 + subdelays[0])
        delays.extend(subdelays[1:])
    add_contention(delays, interrupts=True)
    return delays

def bts_bell():
    # BTS 32433#32492
    delays = bts29836(128, 4096)
    add_contention(delays, interrupts=True)
    return delays

def sd_bell():
    # SD 26450
    delays = [1718] * 4600
    add_contention(delays)
    return delays

def sd_lines1():
    # SD 30464#30544
    delays = []
    inner_delays = [296] * 255
    for d in range(39):
        delays.extend(inner_delays)
        delays.append(307)
    delays.extend(inner_delays)
    add_contention(delays, interrupts=True)
    return delays

def sd_lines2():
    # SD 30464#30575
    delays = []
    inner_delays = [686] * 255
    for d in range(19):
        delays.extend(inner_delays)
        delays.append(697)
    delays.extend(inner_delays)
    add_contention(delays, interrupts=True)
    return delays

def bts_lines1():
    # BTS 29716#29790
    delays = bts29836(20, 10240)
    add_contention(delays, interrupts=True)
    return delays

def bts_lines2():
    # BTS 29716#29818
    delays = bts29836(50, 5120)
    add_contention(delays, interrupts=True)
    return delays

def tune(notes):
    # SD 32279
    pitch_data = (
        (47,196),
        (53,174),
        (60,154),
        (63,145),
        (71,129),
        (80,114),
        (90,101),
        (95,96)
    )
    delays = []
    for i, note in enumerate(notes):
        if note > 255:
            # This is a delay
            delays.append(note)
        else:
            duration, pitch = pitch_data[(note // 2)  & 7]
            duration *= note // 16
            duration //= 2
            if i:
                gap = 207 + 13 * prev_pitch + 24 * (note // 16)
                if note & 1:
                    gap += 61617
                delays.append(gap)
            delays.extend([13 * pitch + 51] * (duration - 1))
            prev_pitch = pitch
    add_contention(delays)
    return delays

def sd_tune():
    # SD 32353
    return tune((
        121,53,119,51,121,53,113,
        49,115,53,70,53,51,121,53,177,
        121,53,55,55,51,121,53,177,
        51,51,53,55,53,51,121,53,177
    ))

def all_shields():
    # SD 32406
    part1 = (55,55,55,57,123,121,55,59,57,57,183) # 32434
    part2 = (
        57,57,57,57,115,115,57,55,53,51,241,
        55,55,55,57,123,121,55,59,57,57,247
    ) # 32446
    delay = (242174,)
    return tune(part1 + delay + part1 + delay + part2)

def bts_tune():
    # BTS 56385 etc.
    return tune((
        59,113,51,183,57,27,91,123,
        251,49,113,51,119,119,115,241,128,
        59,113,51,183,57,27,91,123,
        251,191,59,121,123,119,247,134
    ))

def up_a_year():
    # BTS 56364 etc.
    return tune((
        55,55,55,119,59,127,59,119,55,121,57,121,55,117,51,177,
        55,55,55,119,59,127,59,119,55,121,57,49,66,53,183,183
    ))

def bts_walk(cycle):
    # BTS 29012
    delays = [2532] * 6
    add_contention(delays, interrupts=True, cycle=cycle)
    return delays

def bts_walk0():
    return bts_walk(8736)

def bts_walk1():
    return bts_walk(8736 * 3)

def bts_walk2():
    return bts_walk(8736 * 5)

def bts_walk3():
    return bts_walk(8736 * 7)

def sd_walk(cycle):
    # SD 65088
    delays = [2532] * 7
    add_contention(delays, contention=False, interrupts=True, cycle=cycle)
    return delays

def sd_walk0():
    return sd_walk(8736)

def sd_walk1():
    return sd_walk(8736 * 7)

def _to_bytes4(num):
    return (num & 255, (num >> 8) & 255, (num >> 16) & 255, num >> 24)

def write_text(f, text):
    f.write(bytearray([ord(c) for c in text]))

def write_bytes(f, data):
    f.write(bytearray(data))

def write_wav(samples, fname, sample_rate):
    data_length = 2 * len(samples)
    with open(fname, 'wb') as f:
        write_text(f, 'RIFF')
        write_bytes(f, _to_bytes4(36 + data_length))
        write_text(f, 'WAVE')
        write_text(f, 'fmt ')
        write_bytes(f, (16, 0, 0, 0)) # length of fmt chunk (16)
        write_bytes(f, (1, 0)) # format (1=PCM)
        write_bytes(f, (1, 0)) # channels
        write_bytes(f, _to_bytes4(sample_rate)) # sample rate
        write_bytes(f, _to_bytes4(sample_rate * 2)) # byte rate
        write_bytes(f, (2, 0)) # bytes per sample
        write_bytes(f, (16, 0)) # bits per sample
        write_text(f, 'data')
        write_bytes(f, _to_bytes4(data_length)) # length of data chunk
        for sample in samples:
            write_bytes(f, (sample & 255, sample // 256))

FILES = {
    'catapult': (catapult, 'common', 'catapult'),
    'knocked-out': (knocked_out, 'common', 'knocked-out'),
    'all-shields': (all_shields, 'skool_daze', 'all-shields'),
    'sd-bell': (sd_bell, 'skool_daze', 'bell'),
    'hit0': (hit0, 'skool_daze', 'hit0'),
    'hit1': (hit1, 'skool_daze', 'hit1'),
    'jump': (jump, 'skool_daze', 'jump'),
    'sd-lines1': (sd_lines1, 'skool_daze', 'lines1'),
    'sd-lines2': (sd_lines2, 'skool_daze', 'lines2'),
    'shield': (shield, 'skool_daze', 'shield'),
    'sd-tune': (sd_tune, 'skool_daze', 'tune'),
    'sd-walk0': (sd_walk0, 'skool_daze', 'walk0'),
    'sd-walk1': (sd_walk1, 'skool_daze', 'walk1'),
    'bts-bell': (bts_bell, 'back_to_skool', 'bell'),
    'bingo': (bingo, 'back_to_skool', 'bingo'),
    'conker': (conker, 'back_to_skool', 'conker'),
    'bts-lines1': (bts_lines1, 'back_to_skool', 'lines1'),
    'bts-lines2': (bts_lines2, 'back_to_skool', 'lines2'),
    'mouse': (mouse, 'back_to_skool', 'mouse'),
    'safe-key': (safe_key, 'back_to_skool', 'safe-key'),
    'sherry': (sherry, 'back_to_skool', 'sherry'),
    'bts-tune': (bts_tune, 'back_to_skool', 'tune'),
    'up-a-year': (up_a_year, 'back_to_skool', 'up-a-year'),
    'bts-walk0': (bts_walk0, 'back_to_skool', 'walk0'),
    'bts-walk1': (bts_walk1, 'back_to_skool', 'walk1'),
    'bts-walk2': (bts_walk2, 'back_to_skool', 'walk2'),
    'bts-walk3': (bts_walk3, 'back_to_skool', 'walk3')
}

SOUNDS = {
    SKOOL_DAZE: (
        'catapult', 'knocked-out', 'all-shields', 'sd-bell', 'hit0', 'hit1',
        'jump', 'sd-lines1', 'sd-lines2', 'shield', 'sd-tune', 'sd-walk0',
        'sd-walk1'
    ),
    BACK_TO_SKOOL: (
        'catapult', 'knocked-out', 'bts-bell', 'bingo', 'conker', 'bts-lines1',
        'bts-lines2', 'mouse', 'safe-key', 'sherry', 'bts-tune', 'up-a-year',
        'bts-walk0', 'bts-walk1', 'bts-walk2', 'bts-walk3'
    )
}

def create_sounds(game, odir, verbose=True, force=False, sample_rate=44100, max_amplitude=65536):
    wrote_wavs = False
    for sound in SOUNDS[game]:
        delays_f, subdir, fname = FILES[sound]
        sounds_dir = os.path.join(odir, subdir)
        if not os.path.isdir(sounds_dir):
            os.makedirs(sounds_dir)
        wav = os.path.join(sounds_dir, fname + '.wav')
        if force or not os.path.isfile(wav):
            if verbose:
                print('Writing {0}'.format(wav))
            samples = delays_to_samples(delays_f(), sample_rate, max_amplitude)
            write_wav(samples, wav, sample_rate)
            wrote_wavs = True
    if verbose and not wrote_wavs:
        print("All sound files present")
