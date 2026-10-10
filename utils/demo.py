#!/usr/bin/env python3
import sys
import os
import argparse
import collections
import contextlib
import io
import random
import traceback

# Use the current development version of Pyskool
PYSKOOL_HOME = os.environ.get('PYSKOOL_HOME')
if not PYSKOOL_HOME:
    sys.stderr.write('PYSKOOL_HOME is not set; aborting\n')
    sys.exit(1)
if not os.path.isdir(PYSKOOL_HOME):
    sys.stderr.write(f'PYSKOOL_HOME={PYSKOOL_HOME}: directory not found\n')
    sys.exit(1)
sys.path.insert(0, PYSKOOL_HOME)

with contextlib.redirect_stderr(io.StringIO()):
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
from pyskool import ai, game, keys, sound, user_dir
from pyskool.input import Keyboard
from pyskool.animatorystates import WALK1, WALK3

# Maximum number of commands that may be added to a command list during a
# single call to CommandList.command() before it is regarded as a hang
MAX_COMMANDS_PER_TICK = 500

# Game codes and the names of their ini subdirectories
GAMES = {
    'sd': 'skool_daze',
    'bts': 'back_to_skool',
    'el': 'ezad_looks',
    'sdtt': 'skool_daze_take_too',
    'btsd': 'back_to_skool_daze'
}

# Actions that may be used in an inputs file (the names of key lists in the
# pyskool.keys module, plus WAIT)
ACTIONS = ('LEFT', 'RIGHT', 'UP', 'DOWN', 'SIT_STAND', 'OPEN_DESK', 'FIRE_CATAPULT', 'FIRE_WATER_PISTOL',
           'DUMP_WATER_PISTOL', 'DROP_STINKBOMB', 'HIT', 'JUMP', 'WRITE', 'ENTER', 'CATCH', 'UNDERSTOOD',
           'MOUNT_BIKE', 'RELEASE_MICE', 'KISS', 'WAIT')

class Location:
    def __init__(self, x, y):
        self.x, self.y = x, y

class PressedKeys(dict):
    def __getitem__(self, key):
        return self.get(key, False)

class NoClock:
    def tick(self, *args):
        return 0

def read_inputs(fname):
    """Read an inputs file and return a list of (tick, action, duration)
    tuples sorted by tick. Each line has the form 'TICK ACTION [DURATION]';
    blank lines and anything after '#' are ignored. An action with a duration
    is held down for that many ticks; an action without one is a single press.
    """
    inputs = []
    try:
        with open(fname) as f:
            for num, line in enumerate(f, 1):
                fields = line.partition('#')[0].split()
                if not fields:
                    continue
                try:
                    if len(fields) not in (2, 3):
                        raise ValueError('expected TICK ACTION [DURATION]')
                    if not fields[0].isdigit():
                        raise ValueError('invalid tick: {0}'.format(fields[0]))
                    if len(fields) == 3 and not fields[2].isdigit():
                        raise ValueError('invalid duration: {0}'.format(fields[2]))
                    tick = int(fields[0])
                    action = fields[1].upper()
                    duration = int(fields[2]) if len(fields) == 3 else 0
                    if action not in ACTIONS:
                        raise ValueError('unknown action: {0}'.format(fields[1]))
                except ValueError as e:
                    sys.stderr.write('{0}, line {1}: {2}\n'.format(fname, num, e))
                    sys.exit(1)
                if action != 'WAIT':
                    inputs.append((tick, action, duration))
    except OSError as e:
        sys.stderr.write('{0}\n'.format(e))
        sys.exit(1)
    return sorted(inputs, key=lambda i: i[0])

class Demo:
    def __init__(self, options):
        self.options = options
        self.rng = random.Random(options.seed * 7919 + 1)
        self.held = []
        self.eric = None
        self.target = None
        self.tick = 0
        self.inputs = read_inputs(options.inputs) if options.inputs else None
        self.next_input = 0
        self.held_inputs = []
        self.pending = []
        self.busy = False
        self.sound_busy = False
        if options.record:
            self.inputs = []
            self.open_holds = {}

    def follow_keys(self):
        """Return the held key and key-down keys that make Eric follow the
        highest-numbered little boy (no. 11, or no. 10 in Back to Skool).
        """
        eric, skool, target = self.eric, self.skool, self.target
        if eric.controller or eric.is_knocked_out():
            return None, []
        # Sit when the boy sits, stand when he stands
        if target.is_sitting_on_chair():
            if eric.is_sitting():
                return None, []
            room = skool.room(eric)
            if room and room.chairs and room is skool.room(target):
                if eric.chair():
                    return None, [keys.SIT_STAND[0]]
                chair, direction = room.get_next_chair(eric, False, False)
                if eric.x == chair.x:
                    return (keys.LEFT if direction < 0 else keys.RIGHT)[0], []
                return (keys.RIGHT if eric.x < chair.x else keys.LEFT)[0], []
        elif eric.is_sitting():
            return None, [keys.SIT_STAND[0]]
        if eric.on_stairs():
            return (keys.LEFT if eric.direction < 0 else keys.RIGHT)[0], []
        tx, ty = target.get_location() if target.x >= 0 else (target.x, target.y)
        home, dest = skool.floor(eric), skool.floor(Location(tx, ty))
        if home is None or dest is None:
            return None, []
        staircase = skool.next_staircase(home, dest)
        if staircase:
            at_bottom = eric.y == staircase.bottom.y
            next_x = staircase.bottom.x if at_bottom else staircase.top.x
        else:
            next_x = tx
        if eric.x < next_x:
            return keys.RIGHT[0], []
        if eric.x > next_x:
            return keys.LEFT[0], []
        if staircase:
            return (keys.UP if at_bottom else keys.DOWN)[0], []
        return None, []

    def random_keys(self):
        """Return the held key and key-down keys that make Eric wander about
        at random, hitting, firing, jumping and sitting now and then.
        """
        downs = []
        if self.rng.random() < 0.05:
            self.held = self.rng.choice([keys.LEFT, keys.RIGHT, keys.UP, keys.DOWN, []])
        if self.rng.random() < 0.08:
            downs.append(self.rng.choice([keys.HIT, keys.FIRE_CATAPULT, keys.JUMP, keys.SIT_STAND])[0])
        held = self.held[0] if self.held else None
        if held:
            downs.append(held)
        return held, downs

    def input_keys(self, unread_events):
        """Return the held keys and key-down keys specified in the inputs
        file for the current tick. A key press scheduled for a tick on which
        Eric doesn't check the keyboard is delivered at his next check, and a
        key press that Eric didn't get round to (because he was midstride or
        busy, or acted on another key press first, e.g. HIT before JUMP) is
        delivered again.
        """
        downs = []
        if self.busy or self.eric.controller is not None:
            downs = [e.key for e in self.pending if any(e is f for f in unread_events)]
        while self.next_input < len(self.inputs) and self.inputs[self.next_input][0] <= self.tick:
            tick, action, duration = self.inputs[self.next_input]
            # Look up the key now, after the game has applied any custom key
            # bindings from pyskool.ini
            downs.append(getattr(keys, action)[0])
            if duration != 0:
                self.held_inputs.append(self.next_input)
            self.next_input += 1
        # A duration of None means the key is still held down (when recording)
        self.held_inputs = [i for i in self.held_inputs
                            if self.inputs[i][2] is None or self.inputs[i][0] + self.inputs[i][2] > self.tick]
        return [getattr(keys, self.inputs[i][1])[0] for i in self.held_inputs], downs

    def record_keys(self, events):
        """Add the keys pressed and held down on the real keyboard since the
        last check to the inputs being recorded.
        """
        # Map each key to the action whose replayed key it is, if there is one
        # (e.g. 'o' to OPEN_DESK rather than LEFT); otherwise to the first
        # action that uses it (e.g. 'p' to RIGHT)
        key_actions = {}
        for action in ACTIONS[:-1]:
            for key in getattr(keys, action):
                if key not in key_actions or key == getattr(keys, action)[0]:
                    key_actions[key] = action
        pressed = pygame.key.get_pressed()
        held = {a for k, a in key_actions.items() if pressed[k]}
        downs = []
        for e in events:
            if e.type == pygame.KEYDOWN and key_actions.get(e.key) not in (None, *downs):
                downs.append(key_actions[e.key])
        # End any hold whose key has been released (or released and pressed
        # again)
        for action, i in list(self.open_holds.items()):
            if action not in held or action in downs:
                tick = self.inputs[i][0]
                self.inputs[i] = (tick, action, self.tick - tick)
                del self.open_holds[action]
        for action in downs + sorted(held.difference(downs, self.open_holds)):
            if action in held:
                self.open_holds[action] = len(self.inputs)
                self.inputs.append((self.tick, action, None))
            else:
                self.inputs.append((self.tick, action, 0))

    def write_inputs(self):
        """Write the recorded inputs to a file."""
        options = self.options
        args = ['-g', options.game, '-s', str(options.seed)]
        if options.lesson:
            args.extend(('-l', options.lesson))
        if options.ini_dir:
            args.extend(('--ini-dir', options.ini_dir))
        with open(options.record, 'w') as f:
            f.write('# Recorded by demo.py; replay with: {0} -i FILE\n'.format(' '.join(args)))
            for tick, action, duration in self.inputs:
                if duration is None:
                    duration = self.tick - tick
                if duration:
                    f.write('{0} {1} {2}\n'.format(tick, action, duration))
                else:
                    f.write('{0} {1}\n'.format(tick, action))
        print('Recorded {0} inputs in {1}'.format(len(self.inputs), options.record))

    def pump(self, keyboard):
        """Replacement for Keyboard.pump() that supplies Eric's keypresses.
        Closing the window or pressing Escape ends the demo.
        """
        options = self.options
        events = pygame.event.get()
        keyboard.quit = any(e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)
                            for e in events)
        if self.sound_busy:
            # The game is suspended while a sound effect plays, and doesn't
            # read Eric's keys; leave them alone, so that what Eric receives
            # (and what is recorded) doesn't depend on how long the sound takes
            return
        unread_events, keyboard.key_down_events = getattr(keyboard, 'key_down_events', []), []
        held, downs = [], []
        if self.eric:
            if options.record:
                self.record_keys(events)
            if self.inputs is not None:
                held, downs = self.input_keys(unread_events)
                self.busy = self.eric.midstride() or self.eric.controller is not None
            else:
                if options.eric == 'follow':
                    key, downs = self.follow_keys()
                elif options.eric == 'random':
                    key, downs = self.random_keys()
                else:
                    key = None
                held = [key] if key else []
        # Eric.write() reads the 'unicode' attribute of key-down events
        self.pending = [pygame.event.Event(pygame.KEYDOWN, key=k, unicode='') for k in downs]
        keyboard.key_down_events = self.pending[:]
        if self.eric and self.eric.frozen:
            # Acknowledge any message, or the skool clock stays stopped
            keyboard.key_down_events.append(pygame.event.Event(pygame.KEYDOWN, key=keys.UNDERSTOOD[0], unicode=''))
        keyboard.pressed_keys = PressedKeys({k: True for k in held})

    def is_lost(self, character):
        """Return whether a character is somewhere he should never be: not on
        a floor, not on a staircase, and not midstride.
        """
        if character.x < 0 or character.animatory_state in (WALK1, WALK3):
            return False
        stack = character.command_list.stack
        if stack and isinstance(stack[-1], ai.EvadeMouse):
            # Jumping or standing on a chair to get away from a mouse
            return False
        skool = self.skool
        if skool.on_floor(character) or skool.on_staircase(character):
            return False
        staircase = skool.staircase(character)
        return not (staircase and staircase.contains_location(character.x, character.y))

    def run(self):
        options = self.options
        # SDL reads SDL_VIDEODRIVER and SDL_AUDIODRIVER when pygame.init() is
        # called (in game.Game())
        if not options.screen:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
        random.seed(options.seed)
        if options.sounds:
            # Note when the game is suspended while a sound effect plays
            is_busy = sound.Beeper.is_busy
            def watched_is_busy(beeper):
                self.sound_busy = is_busy(beeper)
                return self.sound_busy
            sound.Beeper.is_busy = watched_is_busy
        else:
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            sound.Beeper.play = lambda *args, **kwargs: None
            sound.Beeper.is_busy = lambda beeper: False
        Keyboard.pump = lambda keyboard: self.pump(keyboard)
        self._guard_against_hangs()

        # With a screen, use the game's default scale and run at normal speed
        scale = None if options.screen else 1
        game_options = argparse.Namespace(config=['MaxLines, 100000000'], scale=scale, cheat=False, quick_start=True)
        g = game.Game(os.path.join(PYSKOOL_HOME, 'pyskool', 'data', 'pyskool.ini'), options.images_dir,
                      options.sounds_dir, options.ini_dir or os.path.join(user_dir, 'ini', GAMES[options.game]),
                      game_options, 'demo', None)
        g.clock = pygame.time.Clock() if options.screen else NoClock()
        g.confirm_close = 0
        g.paused = False
        g.scroll = 0
        self.skool = skool = g.skool
        self.eric = eric = skool.cast.eric
        others = [c for c in skool.cast.character_list if c is not eric]
        self.target = skool.cast.get(max(c.character_id for c in others if c.character_id.startswith('BOY')))

        timetable = skool.timetable
        if options.lesson:
            if options.lesson not in timetable.lesson_details:
                sys.stderr.write('Unknown lesson: {0}\n'.format(options.lesson))
                sys.exit(1)
            timetable.lessons = [options.lesson]
            timetable.index = -1
        else:
            # Start each seed at a different point in the timetable
            timetable.index = (options.seed * 13) % len(timetable.lessons) - 1

        history = collections.deque(maxlen=12)
        lessons_seen = set()
        lost = set()
        restarts = tick = 0
        status = 'DONE'
        try:
            while tick < options.ticks:
                if skool.game_over:
                    skool.reinitialise()
                    restarts += 1
                self.tick = tick
                self.sound_busy = False
                if g._main_loop():
                    status = 'QUIT'
                    break
                if self.sound_busy:
                    # Count only the ticks on which the game advances, so that
                    # tick numbers don't depend on how long sound effects take
                    continue
                tick += 1
                lessons_seen.add(timetable.lesson_id)
                history.append((tick, timetable.lesson_id, timetable.counter,
                                [(c.name, c.x, c.y, c.animatory_state) for c in skool.cast.character_list]))
                for c in others:
                    if c.name not in lost and self.is_lost(c):
                        lost.add(c.name)
                        self._report_lost(c, tick, history)
        except Exception:
            status = 'CRASH'
            traceback.print_exc(file=sys.stdout)
        if options.record:
            self.tick = tick
            self.write_inputs()
        print('{0} seed={1} ticks={2} restarts={3} lesson={4} lost={5}'.format(
            status, options.seed, tick, restarts, timetable.lesson_id, sorted(lost)))
        print('Lessons seen ({0}): {1}'.format(len(lessons_seen), ' '.join(sorted(lessons_seen))))
        return status != 'CRASH' and not lost

    def _report_lost(self, character, tick, history):
        print('LOST seed={0} tick={1} {2} at ({3},{4}) as={5} dir={6} stack={7}'.format(
            self.options.seed, tick, character.name, character.x, character.y,
            character.animatory_state, character.direction,
            '>'.join(type(c).__name__ for c in character.command_list.stack)))
        for t, lesson_id, counter, snapshot in history:
            me = [e for e in snapshot if e[0] == character.name][0]
            near = [e for e in snapshot if e[0] != character.name and abs(e[1] - me[1]) <= 3 and abs(e[2] - me[2]) <= 3]
            print('  t={0} {1} ctr={2} me={3} near={4}'.format(t, lesson_id, counter, me[1:], near))

    def _guard_against_hangs(self):
        """Make an infinite loop inside CommandList.command() raise an
        exception instead of freezing the demo.
        """
        count = [0]
        command = ai.CommandList.command
        add_command = ai.CommandList.add_command
        def guarded_command(command_list):
            count[0] = 0
            return command(command_list)
        def guarded_add_command(command_list, cmd):
            count[0] += 1
            if count[0] > MAX_COMMANDS_PER_TICK:
                raise RuntimeError('HANG: {0} stack={1}'.format(
                    command_list.character.name, [type(c).__name__ for c in command_list.stack][-6:]))
            return add_command(command_list, cmd)
        ai.CommandList.command = guarded_command
        ai.CommandList.add_command = guarded_add_command

def parse_args(args):
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options]',
        description="Run Pyskool headless and unthrottled (or on screen at normal speed), with Eric under "
                    "automatic control, following a file of keypresses, or under keyboard control, and report any crash, hang, or character found off every floor and staircase.")
    parser.add_argument('-e', '--eric', metavar='MODE', choices=('follow', 'random', 'idle'),
                        help="How Eric behaves: follow little boy no. 10 or 11 (MODE=follow, the default), "
                             "press keys at random (MODE=random), or do nothing (MODE=idle).")
    parser.add_argument('-g', '--game', metavar='GAME', choices=tuple(GAMES), default='sd',
                        help='The game to run: sd (Skool Daze, the default), bts (Back to Skool), el (Ezad Looks), '
                             'sdtt (Skool Daze Take Too) or btsd (Back to Skool Daze).')
    parser.add_argument('--images-dir', metavar='DIR', default=os.path.join(user_dir, 'images'),
                        help='Images directory (default: ~/.pyskool/images).')
    parser.add_argument('--ini-dir', metavar='DIR',
                        help="Game ini directory (default: the game's subdirectory of ~/.pyskool/ini).")
    parser.add_argument('-i', '--inputs', metavar='FILE',
                        help="Move Eric according to the keypresses in this file instead of under automatic control. "
                             "Each line has the form 'TICK ACTION [DURATION]', where ACTION is LEFT, RIGHT, UP, DOWN etc. "
                             "(as in pyskool/keys.py) or WAIT, and DURATION is the number of ticks to hold the key down for "
                             "(default: a single press). Anything after '#' is ignored.")
    parser.add_argument('-l', '--lesson', metavar='ID',
                        help='Use a timetable consisting of only this lesson.')
    parser.add_argument('-r', '--record', metavar='FILE',
                        help="Control Eric with the keyboard (requires --screen), and record the keypresses in this "
                             "file for replaying with --inputs (and the same --game, --seed and --lesson).")
    parser.add_argument('--screen', action='store_true',
                        help='Show the game in a window at normal speed instead of running headless. '
                             'Close the window or press Escape to stop.')
    parser.add_argument('-s', '--seed', type=int, default=0,
                        help='Random number seed (default: 0).')
    parser.add_argument('--sounds', action='store_true',
                        help='Play sound effects (requires --screen).')
    parser.add_argument('--sounds-dir', metavar='DIR', default=os.path.join(user_dir, 'sounds'),
                        help='Sounds directory (default: ~/.pyskool/sounds).')
    parser.add_argument('-t', '--ticks', type=int, default=160000,
                        help='Number of ticks to run for (default: 160000, about one cycle of the timetable).')
    options = parser.parse_args(args)
    if sum(1 for o in (options.eric, options.inputs, options.record) if o) > 1:
        parser.error('only one of --eric, --inputs and --record may be used')
    if options.record and not options.screen:
        parser.error('--record requires --screen')
    if options.sounds and not options.screen:
        parser.error('--sounds requires --screen')
    options.eric = options.eric or 'follow'
    return options

###############################################################################
# Begin
###############################################################################
sys.exit(0 if Demo(parse_args(sys.argv[1:])).run() else 1)
