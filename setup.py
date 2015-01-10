#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

from pyskool import version

LONG_DESCRIPTION = """
Pyskool
=======
In 1984, Microsphere published `Skool Daze`_, a game for the
`Sinclair ZX Spectrum`_. In 1985, the sequel `Back to Skool`_ was published.

Each game is based in a boys' school (though Back to Skool adds a playground
and a girls' school) and revolves around the antics of Eric, the hero. In Skool
Daze, Eric must steal his report card from the school safe - the combination of
which must be extracted from the teachers' brains using flashing shields or, in
the case of the history teacher, post-hypnotic suggestion. In Back to Skool,
Eric must get his report card back into the school safe, this time with the
extra help provided by a water pistol, stinkbombs, a bike, mice, a frog and a
girlfriend.

Pyskool is a re-implementation of these classic games in Pygame, with the aim
of making them easy to customise by editing configuration files or - for more
advanced customisation - writing some Python code.

.. _Skool Daze: http://en.wikipedia.org/wiki/Skool_Daze
.. _Back to Skool: http://en.wikipedia.org/wiki/Back_to_Skool
.. _Sinclair ZX Spectrum: http://en.wikipedia.org/wiki/ZX_Spectrum

Requirements
------------
Pyskool requires Python 2.7 and `Pygame`_ (version 1.8+).

On Linux/\*BSD, Pygame is available via the package management system: the
`python-pygame` package on Debian-based distros and openSUSE, the `pygame`
package on Fedora, the `devel/py-game` port on FreeBSD and NetBSD, and the
`devel/pygame` port on OpenBSD.

Windows and Mac OS X users should take care to select the Pygame installer that
matches the version of Python that is installed.

.. _Pygame: http://www.pygame.org/download.shtml

Running Pyskool
---------------
Pyskool is actually five separate games:

* Skool Daze (`skool_daze.py`)
* Back to Skool (`back_to_skool.py`)
* Skool Daze Take Too (`skool_daze_take_too.py`)
* Ezad Looks (`ezad_looks.py`)
* Back to Skool Daze (`back_to_skool_daze.py`)

Before playing any of these games for the first time, the required images, ini
files and sound files will need to be created. This can be done by using the
``--setup`` option; for example::

  $ skool_daze.py --setup

This will:

* download TZX files from the sources listed in `images.ini` and use them to
  create the required images in `~/.pyskool/images`
* write the required ini files in `~/.pyskool/ini`
* write the required sound files in `~/.pyskool/sounds`

After that, Pyskool can be run in Skool Daze mode::

  $ skool_daze.py

Playing Pyskool
---------------
The keys to move Eric around are:

* 'q' or up arrow - go up stairs, or continue walking in the same direction
* 'a' or down arrow - go down stairs, or continue walking in the same direction
* 'o' or left arrow - left
* 'p' or right arrow - right
* 'f' - fire catapult
* 'h' - hit
* 'j' - jump
* 's' - sit/stand
* 'w' - write on a blackboard (press Enter/Return to finish)

Other useful keys are:

* Escape - quit the game
* End - pause/resume
* Insert - take a screenshot
* F2 - save the game
* F6 - load the most recently saved game
* F11 - switch between full-screen and windowed mode
* F12 - show/hide the menu

For full instructions, see the `documentation`_.

.. _documentation: http://pyskool.ca/docs/pyskool/play.html
"""

setup(
    name='pyskool',
    version=version,
    author='Richard Dymond',
    author_email='rjdymond@gmail.com',
    license='GPLv3',
    url='http://pyskool.ca/',
    description="A remake of 'Skool Daze' and 'Back to Skool' using Pygame",
    long_description=LONG_DESCRIPTION,
    packages=['pyskool'],
    package_data={'pyskool': ['data/images.ini', 'data/pyskool.ini']},
    scripts=[
        'back_to_skool_daze.py',
        'back_to_skool.py',
        'ezad_looks.py',
        'skool_daze.py',
        'skool_daze_take_too.py'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games'
    ]
)
