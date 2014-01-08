# -*- coding: utf-8 -*-

# Copyright 2008-2014 Richard Dymond (rjdymond@gmail.com)
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
import os.path
from optparse import OptionParser

from .game import Game
from . import version, package_dir, user_dir, images_subdir, sounds_subdir, skoolsound
from .image import get_images, SKOOL_DAZE, BACK_TO_SKOOL
from .sdini import SDIniMaker
from .btsini import BTSIniMaker

SEARCH_DIRS_MSG = """
Pyskool will search the following directories for 'pyskool.ini' and the
'{images}', '{sounds}' and '{ini}' subdirectories:
""".lstrip()

def info(text):
    sys.stdout.write('%s\n' % text)

def error(text):
    sys.stderr.write('%s\n' % text)
    sys.exit(1)

def find(name, search_dirs, directory=False):
    for f in [os.path.join(d, name) for d in search_dirs]:
        if (directory and os.path.isdir(f)) or (not directory and os.path.isfile(f)):
            return f
    msg = ["Cannot find %s '%s' in any of these locations:" % ('directory' if directory else 'file', name)]
    msg += ["  %s" % d for d in search_dirs]
    error('\n'.join(msg))

def find_dir(dname, search_dirs):
    return find(dname, search_dirs, True)

def main():
    names = {}
    names['skool_daze.py'] = 'Skool Daze'
    names['back_to_skool.py'] = 'Back to Skool'
    names['skool_daze_take_too.py'] = 'Skool Daze Take Too'
    names['ezad_looks.py'] = 'Ezad Looks'
    names['back_to_skool_daze.py'] = 'Back to Skool Daze'
    prog = os.path.basename(sys.argv[0].lower())
    name = names.get(prog, 'Unknown')
    default_ini_dir = os.path.join('ini', prog[:-3])
    synopsis = "Start Pyskool in %s mode." % name
    parser = OptionParser(version=version, description=synopsis)
    parser.add_option("-c", "--cheat", dest="cheat", action="store_true",
        help="enable cheat keys")
    parser.add_option("--create-images", "--get-images", dest="create_images", action="store_true",
        help="create the images required by the game and exit")
    parser.add_option("--create-ini", dest="create_ini", action="store_true",
        help="create the ini files required by the game and exit")
    parser.add_option("--create-sounds", dest="create_sounds", action="store_true",
        help="create the sound files required by the game and exit")
    parser.add_option("--force", dest="force", action="store_true",
        help="overwrite existing images, ini files and sound files")
    parser.add_option("-i", "--inidir", dest="inidir",
        help="read ini files from this directory instead of %s" % default_ini_dir)
    parser.add_option("-l", "--load", dest="savefile",
        help="load a saved game from the specified file")
    parser.add_option("--package-dir", dest="package_dir", action="store_true",
        help="show path to pyskool package directory and exit")
    parser.add_option("-q", "--quick-start", dest="quick_start", action="store_true",
        help="start the game quickly")
    parser.add_option("-r", "--load-last", dest="savedir",
        help="load the most recently saved game in the specified directory")
    parser.add_option("--sample-rate", dest="sample_rate", metavar="RATE", type="int", default=44100,
        help="set the sample rate of the sound files created by --create-sounds (default: 44100)")
    parser.add_option("-s", "--scale", dest="scale", type="int",
        help="scale graphics by this factor (1=original Speccy size)")
    parser.add_option("--search-dirs", dest="search_dirs", action="store_true",
        help="show the locations that Pyskool searches for data files and exit")
    parser.add_option("--setup", dest="setup", action="store_true",
        help="create the images, ini files and sound files required by the game and exit")
    options, args = parser.parse_args()

    # Set the search path for 'pyskool.ini', the 'images' directory, the 'sounds'
    # directory, and the 'ini' directory
    cwd = os.getcwd()
    search_dirs = [
        cwd,
        os.path.join(os.sep, 'usr', 'share', 'pyskool'),
        os.path.join(package_dir, 'data')
    ]
    scripts_dir = os.path.abspath(os.path.dirname(__file__))
    if scripts_dir not in search_dirs:
        search_dirs.insert(1, scripts_dir)

    # Attempt to create ~/.pyskool if it doesn't exist
    pyskool_dir = user_dir
    if not os.path.isdir(user_dir):
        try:
            os.makedirs(user_dir)
            info("Created directory '%s'" % user_dir)
        except OSError as e:
            info("Could not create directory '%s': %s" % (user_dir, e.strerror))
            pyskool_dir = cwd
    if pyskool_dir not in search_dirs:
        search_dirs.insert(1, pyskool_dir)

    # Show package directory if requested
    if options.package_dir:
        info(package_dir)
        sys.exit(0)

    # Show search directories if requested
    if options.search_dirs:
        info(SEARCH_DIRS_MSG.format(images=images_subdir, sounds=sounds_subdir, ini=default_ini_dir))
        for search_dir in search_dirs:
            info('- {0}'.format(search_dir))
        sys.exit(0)

    # Get images if requested
    if options.setup or options.create_images:
        images_ini = find('images.ini', search_dirs)
        info("Using ini file at %s" % images_ini)
        if prog == 'skool_daze.py':
            get_images(images_ini, SKOOL_DAZE, 0, user_dir, True, options.force)
        elif prog == 'skool_daze_take_too.py':
            get_images(images_ini, SKOOL_DAZE, 1, user_dir, True, options.force)
        elif prog == 'ezad_looks.py':
            get_images(images_ini, SKOOL_DAZE, 2, user_dir, True, options.force)
        elif prog == 'back_to_skool.py':
            get_images(images_ini, BACK_TO_SKOOL, 0, user_dir, True, options.force)
        elif prog == 'back_to_skool_daze.py':
            get_images(images_ini, BACK_TO_SKOOL, 1, user_dir, True, options.force)

    # Create ini files if requested
    if options.setup or options.create_ini:
        ini_maker = None
        if prog == 'skool_daze.py':
            ini_maker = SDIniMaker(0)
        elif prog == 'skool_daze_take_too.py':
            ini_maker = SDIniMaker(1)
        elif prog == 'ezad_looks.py':
            ini_maker = SDIniMaker(2)
        elif prog == 'back_to_skool.py':
            ini_maker = BTSIniMaker(0)
        elif prog == 'back_to_skool_daze.py':
            ini_maker = BTSIniMaker(1)
        if ini_maker:
            odir = os.path.join(user_dir, 'ini', prog[:-3])
            if not os.path.isdir(odir):
                os.makedirs(odir)
            ini_maker.write_ini_files(odir, True, options.force)

    # Create sound files if requested
    if options.setup or options.create_sounds:
        odir = os.path.join(user_dir, 'sounds')
        if prog in ('skool_daze.py', 'skool_daze_take_too.py', 'ezad_looks.py'):
            skoolsound.create_sounds(skoolsound.SKOOL_DAZE, odir, True, options.force, options.sample_rate)
        elif prog in ('back_to_skool.py', 'back_to_skool_daze.py'):
            skoolsound.create_sounds(skoolsound.BACK_TO_SKOOL, odir, True, options.force, options.sample_rate)

    if options.setup or options.create_images or options.create_ini or options.create_sounds:
        sys.exit(0)

    # Look for 'pyskool.ini'
    pyskool_ini = find('pyskool.ini', search_dirs)
    info("Using ini file at %s" % pyskool_ini)

    # Look for the directory that contains the game ini files
    if options.inidir:
        ini_dir = os.path.abspath(options.inidir)
        if not os.path.isdir(ini_dir):
            error('%s: directory does not exist' % ini_dir)
    else:
        ini_dir = find_dir(default_ini_dir, search_dirs)
        info("Using game ini files in %s" % ini_dir)

    # Look for the 'images' subdirectory
    images_dir = find_dir(images_subdir, search_dirs)
    info("Using images in %s" % images_dir)

    # Look for the 'sounds' subdirectory
    sounds_dir = find_dir(sounds_subdir, search_dirs)
    info("Using sounds in %s" % sounds_dir)

    # Look for a saved game (if specified on the command line)
    sav_file = None
    if options.savefile:
        if not os.path.isfile(options.savefile):
            error('%s: file not found' % options.savefile)
        sav_file = os.path.abspath(options.savefile)
    elif options.savedir:
        if not os.path.isdir(options.savedir):
            error('%s: directory does not exist' % options.savedir)
        sav_files = [f for f in os.listdir(options.savedir) if f.endswith('.sav') and os.path.isfile(os.path.join(options.savedir, f))]
        if sav_files:
            sav_files.sort()
            sav_file = os.path.abspath(os.path.join(options.savedir, sav_files[-1]))
        else:
            info("No saved games found in %s" % options.savedir)

    # Change to the directory where games will be saved/loaded and screenshots will
    # be dumped
    os.chdir(user_dir)
    info("Using %s to save/load games" % os.getcwd())

    game = Game(pyskool_ini, images_dir, sounds_dir, options.scale, ini_dir, options.quick_start, options.cheat, version, sav_file)
    game.play()
