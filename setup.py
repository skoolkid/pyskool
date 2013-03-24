#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from pyskool import version

setup(
    name='pyskool',
    version=version,
    author='Richard Dymond',
    author_email='rjdymond@gmail.com',
    license='GPLv3',
    url='http://pyskool.ca/',
    description="A remake of 'Skool Daze' and 'Back to Skool' using Pygame",
    packages=['pyskool'],
    scripts=['back_to_skool_daze.py', 'back_to_skool.py', 'ezad_looks.py', 'skool_daze.py', 'skool_daze_take_too.py']
)
