"""Helpers for running Pyskool games headless (via utils/demo.py) in tests."""

import os
import re
import sys
import warnings

import pytest

PYSKOOL_HOME = os.environ.get('PYSKOOL_HOME')
if not PYSKOOL_HOME:
    pytest.exit('PYSKOOL_HOME is not set; aborting', 1)
if not os.path.isdir(PYSKOOL_HOME):
    pytest.exit(f'PYSKOOL_HOME={PYSKOOL_HOME}: directory not found', 1)
sys.path.insert(0, os.path.join(PYSKOOL_HOME, 'utils'))

# Import pygame now (before demo does) to swallow the warnings it emits
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import pygame

import demo
from pyskool import user_dir

# A line printed by 'demo.py --lines', e.g.
#   LINES 284: +700 = 700 by MR WITHIT (38,17) [GET_UP] Eric (48,17)
#   LINES 306: +500 by MR WITHIT (36,17) [NEVER_AGAIN] to EINSTEIN Eric (30,17)
LINES_RE = re.compile(r'LINES (\d+): \+(\d+)(?: = \d+)? by (.+) \(\d+,\d+\) \[(\w+)\](?: to (.+))? Eric \(\d+,\d+\)$')

# Lines printed by 'demo.py --endings', e.g.
#   UP_A_YEAR 39167: Eric (81,2)
#   GAME_OVER 39168: up a year Eric (81,3)
#   GAME_OVER 468: by MR ROCKITT (10,10) Eric (15,13)
UP_A_YEAR_RE = re.compile(r'UP_A_YEAR (\d+): ')
GAME_OVER_RE = re.compile(r'GAME_OVER (\d+): (?:(up a year)|by (.+) \(\d+,\d+\)( expelled)?) Eric \(\d+,\d+\)$')

def check_assets(game):
    ini_dir = os.path.join(user_dir, 'ini', demo.GAMES[game])
    for path in (ini_dir, os.path.join(user_dir, 'images'), os.path.join(user_dir, 'sounds')):
        if not os.path.isdir(path):
            pytest.skip(f'{path} not found (run "make images ini sounds")')

def run(monkeypatch, capsys, tmp_path, game, lesson, inputs, ticks, seed=0, setup=None, options=()):
    """Run a game headless with 'demo.py --lines --endings' for one lesson (or, if
    'lesson' is None, the normal timetable starting at the lesson that the
    random seed selects), using the given random seed and inputs (the contents
    of an inputs file), and return the Demo object and the lines given, as
    (tick, lines, giver, message ID, recipient) tuples, where recipient is None
    if Eric got the lines. The Demo object's 'up_a_year_ticks' attribute is set
    to a list of the ticks at which Eric went up a year, and its 'endings'
    attribute to a list of the game endings, as (tick, reason) pairs, where
    reason is 'up a year', or the name of whoever ended the game (followed by
    ' (expelled)' if Eric was expelled).

    If given, 'setup' is called with the Demo object (whose 'skool' attribute
    is then set) before the first tick.

    'options' is a sequence of any extra options to pass to demo.py.
    """
    check_assets(game)
    # demo.py wraps these methods to log lines; make sure they are restored
    # afterwards, so that the logging doesn't pile up over several tests
    for cls, name in (
            (demo.character.Character, 'print_lines_message'),
            (demo.character.Character, 'add_lines'),
            (demo.eric_mod.Eric, 'kiss'),
            (demo.skool_mod.Skool, 'add_lines'),
            (demo.skool_mod.Skool, 'get_lines_message'),
            (demo.character.Character, 'end_game'),
            (demo.skool_mod.Skool, 'end_game'),
            (demo.skool_mod.Skool, '_up_a_year')
    ):
        monkeypatch.setattr(cls, name, getattr(cls, name))
    inputs_file = tmp_path / 'inputs.txt'
    inputs_file.write_text(inputs)
    args = ['-g', game, '-s', str(seed), '-i', str(inputs_file), '-t', str(ticks), '--lines', '--endings']
    if lesson:
        args.extend(('-l', lesson))
    args.extend(options)
    d = demo.Demo(demo.parse_args(args))

    if setup:
        main_loop = demo.game.Game._main_loop
        def set_up_main_loop(g):
            if d.tick == 0 and not hasattr(g, 'set_up'):
                g.set_up = True
                setup(d)
            return main_loop(g)
        monkeypatch.setattr(demo.game.Game, '_main_loop', set_up_main_loop)

    assert d.run(), 'demo crashed or a character got lost'
    lines = []
    d.up_a_year_ticks = []
    d.endings = []
    for line in capsys.readouterr().out.splitlines():
        match = LINES_RE.match(line)
        if match:
            tick, num, giver, message_id, recipient = match.groups()
            lines.append((int(tick), int(num), giver, message_id, recipient))
        match = UP_A_YEAR_RE.match(line)
        if match:
            d.up_a_year_ticks.append(int(match.group(1)))
        match = GAME_OVER_RE.match(line)
        if match:
            tick, up_a_year, ender, expelled = match.groups()
            d.endings.append((int(tick), up_a_year or ender + (' (expelled)' if expelled else '')))
    return d, lines
