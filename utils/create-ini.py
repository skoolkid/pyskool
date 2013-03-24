#!/usr/bin/env python
import sys
import os

# Use the current development version of Pyskool
PYSKOOL_HOME = os.environ.get('PYSKOOL_HOME')
if not PYSKOOL_HOME:
    sys.stderr.write('PYSKOOL_HOME is not set; aborting\n')
    sys.exit(1)
if not os.path.isdir(PYSKOOL_HOME):
    sys.stderr.write('PYSKOOL_HOME=%s: directory not found\n' % PYSKOOL_HOME)
    sys.exit(1)
sys.path.insert(0, PYSKOOL_HOME)

from pyskool.sdini import SDIniMaker
from pyskool.btsini import BTSIniMaker

def parse_args(args):
    odir = os.path.expanduser(os.path.join('~', '.pyskool'))
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

  Creates the stock Pyskool game ini files in a subdirectory named 'ini' in
  DIRECTORY.

Options:
  -q  Be quiet
""".format(os.path.basename(sys.argv[0])))
    sys.exit(1)

###############################################################################
# Begin
###############################################################################
odir, verbose = parse_args(sys.argv[1:])
ini_dir = os.path.join(odir, 'ini')

SDIniMaker(0).write_ini_files(os.path.join(ini_dir, 'skool_daze'), verbose)
SDIniMaker(1).write_ini_files(os.path.join(ini_dir, 'skool_daze_take_too'), verbose)
SDIniMaker(2).write_ini_files(os.path.join(ini_dir, 'ezad_looks'), verbose)
BTSIniMaker(0).write_ini_files(os.path.join(ini_dir, 'back_to_skool'), verbose)
BTSIniMaker(1).write_ini_files(os.path.join(ini_dir, 'back_to_skool_daze'), verbose)
