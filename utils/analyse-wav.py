#!/usr/bin/env python
import sys
import argparse

def _to_chars(data):
    return ''.join(chr(b) for b in data)

def _to_int(data, signed=False):
    if len(data) == 4:
        return 16777216 * data[3] + 65536 * data[2] + 256 * data[1] + data[0]
    value = 256 * data[1] + data[0]
    if value < 32768 or not signed:
        return value
    return value - 65536

def _print_chunk_id(data, i):
    chunk_id = _to_chars(data[i:i + 4])
    print('{:6d} "{}"'.format(i, chunk_id))
    return i + 4, chunk_id

def _print_length(data, i, suffix=''):
    length = _to_int(data[i:i + 4])
    if suffix:
        suffix = ': {}'.format(suffix)
    print('{:6d} {} (length{})'.format(i, length, suffix))
    return i + 4, length

def analyse_wav(data, options):
    i, chunk_id = _print_chunk_id(data, 0) # RIFF
    i, length = _print_length(data, i)
    i, chunk_id = _print_chunk_id(data, i) # WAVE
    while i < len(data):
        i, chunk_id = _print_chunk_id(data, i)
        suffix = ''
        if chunk_id == 'data':
            num_samples = _to_int(data[i:i + 4]) // 2
            suffix = '{} samples, {:.02f}s'.format(num_samples, num_samples / (num_channels * float(sample_rate)))
        i, length = _print_length(data, i, suffix)
        if chunk_id == 'fmt ':
            j = i
            audio_format = _to_int(data[j:j + 2])
            print('{:6d} {} (audio format)'.format(j, audio_format))
            j += 2
            num_channels = _to_int(data[j:j + 2])
            print('{:6d} {} (num channels)'.format(j, num_channels))
            j += 2
            sample_rate = _to_int(data[j:j + 4])
            print('{:6d} {} (sample rate)'.format(j, sample_rate))
            j += 4
            byte_rate = _to_int(data[j:j + 4])
            print('{:6d} {} (byte rate)'.format(j, byte_rate))
            j += 4
            bytes_per_sample = _to_int(data[j:j + 2])
            print('{:6d} {} (bytes per sample)'.format(j, bytes_per_sample))
            j += 2
            bits_per_sample = _to_int(data[j:j + 2])
            print('{:6d} {} (bits per sample)'.format(j, bits_per_sample))
        elif chunk_id == 'data' and options.show_samples:
            j = i
            while j < i + length:
                num_samples = 8
                end = min(i + length, j + num_samples * 2)
                samples = [_to_int(data[k:k + 2], True) for k in range(j, end, 2)]
                print('{:6d} {}'.format(j, ', '.join(['{:6d}'.format(s) for s in samples])))
                j += len(samples) * 2
        else:
            print('{:6d} ...'.format(i))
        i += length

parser = argparse.ArgumentParser(
    usage='analyse-wav.py [options] FILE',
    description="Analyse a WAV file.",
    add_help=False
)
parser.add_argument('wavfile', help=argparse.SUPPRESS, nargs='?')
group = parser.add_argument_group('Options')
group.add_argument('-s', '--show-samples', action='store_true', dest='show_samples',
                   help='Show samples')
namespace, unknown_args = parser.parse_known_args()
if unknown_args or namespace.wavfile is None:
    parser.exit(2, parser.format_help())

with open(namespace.wavfile, 'rb') as f:
    file_data = list(bytearray(f.read())) # PY: 'list(f.read())' in Python 3
analyse_wav(file_data, namespace)
