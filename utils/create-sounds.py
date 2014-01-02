#!/usr/bin/env python
import sys
import os

# Use the current development version of Pyskool
PYSKOOL_HOME = os.environ.get('PYSKOOL_HOME')
if not PYSKOOL_HOME:
    sys.stderr.write('PYSKOOL_HOME is not set; aborting\n')
    sys.exit(1)
if not os.path.isdir(PYSKOOL_HOME):
    sys.stderr.write('PYSKOOL_HOME={0}: directory not found\n'.format(PYSKOOL_HOME))
    sys.exit(1)
sys.path.insert(0, PYSKOOL_HOME)

from pyskool.skoolsound import create_sounds, SKOOL_DAZE, BACK_TO_SKOOL

def parse_args(args):
    p_args = []
    verbose = True
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-q':
            verbose = False
        elif arg.startswith('-'):
            print_usage()
        else:
            p_args.append(arg)
        i += 1
    if len(p_args) != 1:
        print_usage()
    return p_args[0], verbose

def print_usage():
    sys.stderr.write("""Usage: {0} [options] DIRECTORY

  Creates the stock Pyskool sound files in a subdirectory named 'sounds' in
  DIRECTORY.

Options:
  -q  Be quiet
""".format(os.path.basename(sys.argv[0])))
    sys.exit(1)

###############################################################################
# Begin
###############################################################################
odir, verbose = parse_args(sys.argv[1:])
sounds_dir = os.path.join(odir, 'sounds')
create_sounds(SKOOL_DAZE, sounds_dir, verbose)
create_sounds(BACK_TO_SKOOL, sounds_dir, verbose)
