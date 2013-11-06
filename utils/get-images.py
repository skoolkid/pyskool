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

from pyskool.image import get_images, SKOOL_DAZE, BACK_TO_SKOOL

def parse_args(args):
    p_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('-'):
            print_usage()
        else:
            p_args.append(arg)
        i += 1
    if len(p_args) != 1:
        print_usage()
    return p_args[0]

def print_usage():
    sys.stderr.write("""Usage: {0} DIRECTORY

  Creates the stock Pyskool image files in a subdirectory named 'images' in
  DIRECTORY.
""".format(os.path.basename(sys.argv[0])))
    sys.exit(1)

###############################################################################
# Begin
###############################################################################
odir = parse_args(sys.argv[1:])
images_ini = os.path.join(PYSKOOL_HOME, 'images.ini')
get_images(images_ini, SKOOL_DAZE, 0, odir)
get_images(images_ini, SKOOL_DAZE, 1, odir)
get_images(images_ini, SKOOL_DAZE, 2, odir)
get_images(images_ini, BACK_TO_SKOOL, 0, odir)
get_images(images_ini, BACK_TO_SKOOL, 1, odir)
