#!/usr/bin/env python3
import sys
import os
import argparse
import contextlib
import io
import random
import re
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import demo
from pyskool import character

# SDL starts a thread, but the forked children don't depend on it
warnings.filterwarnings('ignore', 'This process .* is multi-threaded', DeprecationWarning)

def expand(template, v):
    """Return the input lines in a template, with each '{expr}' replaced by
    the value of expr for the value v. An expression's value may itself
    contain several input lines separated by ';'.
    """
    text = re.sub(r'\{([^}]*)\}', lambda m: str(eval(m.group(1), {'v': v})), template)
    return [line.strip() for line in text.split(';') if line.strip()]

def parse_input(line):
    """Parse an input line in the same way as demo.read_inputs(), and return a
    (tick, action, duration) tuple, or None for WAIT.
    """
    fields = line.split()
    if len(fields) not in (2, 3) or not fields[0].isdigit():
        raise ValueError('invalid input: {0}'.format(line))
    tick, action = int(fields[0]), fields[1].upper()
    if action == 'TYPE':
        return (tick, action, fields[2])
    if action not in demo.ACTIONS:
        raise ValueError('unknown action: {0}'.format(fields[1]))
    if action != 'WAIT':
        return (tick, action, int(fields[2]) if len(fields) == 3 else 0)

class Scan:
    def __init__(self, options, demo_args):
        self.options = options
        self.demo = demo.Demo(demo.parse_args(demo_args + ['-t', str(options.to)]))
        self.value = None
        self.game = None
        self.secrets = []

    def env(self):
        d = self.demo
        return {'demo': d, 'game': self.game, 'skool': d.skool, 'eric': d.eric, 'cast': d.skool.cast,
                'tick': d.tick + 1, 'secrets': self.secrets, 'char': self.char}

    def char(self, name):
        """Return the character (or object) with a given name or ID."""
        for c in self.demo.skool.cast.everything:
            if name in (c.name, c.character_id):
                return c

    def report(self):
        if self.options.report:
            return eval(self.options.report, self.env())
        d = self.demo
        eric, scoreboard = d.eric, d.skool.scoreboard
        return '({0},{1}) dir={2} as={3} score={4} lines={5} secrets={6}'.format(
            eric.x, eric.y, eric.direction, eric.animatory_state, scoreboard.score, scoreboard.lines,
            ' '.join(self.secrets))

    def fork(self):
        """Fork a child for each value, and return in the child (with its
        inputs added). The parent exits when all the children have finished.
        """
        d = self.demo
        # Expand the template for every value before forking, so that any
        # error is reported once
        try:
            alternatives = []
            for v in eval(self.options.values):
                new = [i for i in (parse_input(line) for line in expand(self.options.template, v)) if i]
                if any(i[0] < d.tick for i in new):
                    raise ValueError('input before tick {0} for value {1}'.format(d.tick, v))
                alternatives.append((v, new))
        except Exception as e:
            print('Error: {0}'.format(e), file=sys.__stderr__)
            os._exit(1)
        for v, new in alternatives:
            sys.__stdout__.flush()
            # Python reseeds the random module in a forked child, so restore
            # the parent's state there to keep the run deterministic
            rng_state = random.getstate()
            pid = os.fork()
            if pid == 0:
                random.setstate(rng_state)
                self.value = v
                pending = d.inputs[d.next_input:] + new
                d.inputs = d.inputs[:d.next_input] + sorted(pending, key=lambda i: i[0])
                return
            os.waitpid(pid, 0)
        os._exit(0)

    def run(self):
        d, options = self.demo, self.options
        main_loop = demo.game.Game._main_loop
        def wrapped_main_loop(g):
            self.game = g
            if d.tick == options.at and self.value is None and not d.sound_busy:
                self.fork()
            rv = main_loop(g)
            if self.value is not None and options.until and not d.sound_busy and eval(options.until, self.env()):
                print('{0}: STOP at {1}: {2}'.format(self.value, d.tick + 1, self.report()), file=sys.__stdout__)
                sys.__stdout__.flush()
                os._exit(0)
            return rv
        demo.game.Game._main_loop = wrapped_main_loop

        # Record each combination letter or digit revealed (and when)
        print_secret = character.Character._print_secret
        def logged_print_secret(c, secret):
            self.secrets.append('{0}={1}@{2}'.format(c.name, secret, d.tick + 1))
            return print_secret(c, secret)
        character.Character._print_secret = logged_print_secret

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            d.run()
        if self.value is None:
            print('Tick {0} not reached'.format(options.at))
            sys.exit(1)
        if any(line.startswith(('CRASH', 'LOST', 'Traceback')) for line in out.getvalue().split('\n')):
            print(out.getvalue(), end='')
        print('{0}: {1}'.format(self.value, self.report()))
        sys.stdout.flush()
        os._exit(0)

###############################################################################
# Begin
###############################################################################
parser = argparse.ArgumentParser(
    usage='%(prog)s --at TICK --to TICK -c TEMPLATE -v VALUES [options] [DEMO_OPTIONS]',
    description="Run utils/demo.py up to tick TICK (--at), then try a series of alternative inputs from there, each "
                "in a forked copy of the game running up to tick TICK (--to), and report on each one. Each "
                "alternative is TEMPLATE with every '{expr}' replaced by the value of expr for one of VALUES (as v). "
                "Any other options (e.g. -g, -i, -s) are passed to demo.py; the inputs in TEMPLATE are added to those "
                "from -i (if given). EXPR and COND may refer to demo, game, skool, eric, cast, tick (the number of "
                "the tick just finished), secrets (a list of combination letters and digits revealed) and "
                "char(name) (a character or object). Requires os.fork(), so doesn't work on Windows.",
    epilog="Example: %(prog)s -g bts -i inputs.txt --at 1287 --to 1600 -c '1287 RIGHT 32;{v} CATCH' "
           "-v 'range(1300,1600,2)' --until 'eric.mice>0'")
parser.add_argument('--at', metavar='TICK', type=int, required=True,
                    help='The tick at which to start trying the alternatives.')
parser.add_argument('--to', metavar='TICK', type=int, required=True,
                    help='The tick at which to stop each alternative.')
parser.add_argument('-c', dest='template', metavar='TEMPLATE', required=True,
                    help="Input lines (as in an inputs file) to add, separated by ';' (e.g. '{v} FIRE_CATAPULT;{v+20} JUMP').")
parser.add_argument('-v', dest='values', metavar='VALUES', required=True,
                    help="A Python expression for the values to try (e.g. 'range(100,200,2)' or "
                         "'[(d,t) for d in (8,16) for t in range(500,600,2)]').")
parser.add_argument('--until', metavar='COND', help='Stop an alternative as soon as this Python expression is true.')
parser.add_argument('--report', metavar='EXPR',
                    help="A Python expression to print at the end of each alternative (default: Eric's location, "
                         "animatory state, score and lines total, and any secrets revealed).")
options, demo_args = parser.parse_known_args()
if '-i' not in demo_args and '--inputs' not in demo_args and not any(a.startswith('--inputs=') for a in demo_args):
    # Replay inputs only from the template
    demo_args = demo_args + ['-i', os.devnull]
Scan(options, demo_args).run()
