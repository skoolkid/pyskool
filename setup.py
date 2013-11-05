#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
import shutil

from pyskool import version

PACKAGE_DIR = 'build/pyskool-pkg'
DATA_DIR = '{0}/data'.format(PACKAGE_DIR)

shutil.rmtree(PACKAGE_DIR, True)
shutil.copytree('pyskool', PACKAGE_DIR, ignore=shutil.ignore_patterns('*.pyc'))
shutil.copytree('ini', '{0}/ini'.format(DATA_DIR))
shutil.copytree('sounds', '{0}/sounds'.format(DATA_DIR))
shutil.copy('images.ini', DATA_DIR)
shutil.copy('pyskool.ini', DATA_DIR)

setup(
    name='pyskool',
    version=version,
    author='Richard Dymond',
    author_email='rjdymond@gmail.com',
    license='GPLv3',
    url='http://pyskool.ca/',
    description="A remake of 'Skool Daze' and 'Back to Skool' using Pygame",
    packages=['pyskool'],
    package_dir={'pyskool': PACKAGE_DIR},
    package_data={'pyskool': [
        'data/images.ini',
        'data/pyskool.ini',
        'data/ini/back_to_skool/*.ini',
        'data/ini/back_to_skool_daze/*.ini',
        'data/ini/ezad_looks/*.ini',
        'data/ini/skool_daze/*.ini',
        'data/ini/skool_daze_take_too/*.ini',
        'data/sounds/back_to_skool/*',
        'data/sounds/common/*',
        'data/sounds/skool_daze/*'
    ]},
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games'
    ]
)
