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
from pyskool import ai, character, game, graphics, keys, lesson, sound, user_dir
from pyskool import eric as eric_mod
from pyskool import skool as skool_mod
from pyskool import timetable as timetable_mod
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

class FastClock:
    """A clock that runs the game (including scrolling) at a multiple of its
    normal speed."""
    def __init__(self, speed):
        self.clock = pygame.time.Clock()
        self.speed = speed

    def tick(self, framerate=0):
        return self.clock.tick(framerate * self.speed)

def read_inputs(fname):
    """Read an inputs file and return a list of (tick, action, duration)
    tuples sorted by tick. Each line has the form 'TICK ACTION [DURATION]' or
    'TICK TYPE TEXT'; blank lines and anything after '#' are ignored. An action
    with a duration is held down for that many ticks; an action without one is
    a single press. For TYPE, the 'duration' is the text to type on a
    blackboard.
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
                        raise ValueError('expected TICK ACTION [DURATION] or TICK TYPE TEXT')
                    if not fields[0].isdigit():
                        raise ValueError('invalid tick: {0}'.format(fields[0]))
                    tick = int(fields[0])
                    action = fields[1].upper()
                    if action == 'TYPE':
                        if len(fields) != 3:
                            raise ValueError('expected TICK TYPE TEXT')
                        inputs.append((tick, action, fields[2]))
                        continue
                    if len(fields) == 3 and not fields[2].isdigit():
                        raise ValueError('invalid duration: {0}'.format(fields[2]))
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
        self.typing = []
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

        The characters of a TYPE input, and any key press that arrives while
        Eric is writing on a blackboard (e.g. ENTER), are queued instead, and
        delivered one at a time by pump().
        """
        downs = []
        # Eric.write() doesn't remove the key-down events it reads, so don't
        # treat them as unread while he's writing
        writing = self.eric.keyboard.writing
        if (self.busy or self.eric.controller is not None) and not writing:
            downs = [e.key for e in self.pending if any(e is f for f in unread_events)]
        while self.next_input < len(self.inputs) and self.inputs[self.next_input][0] <= self.tick:
            tick, action, duration = self.inputs[self.next_input]
            self.next_input += 1
            if action == 'TYPE':
                self.typing.extend((ord(c.lower()), c) for c in duration)
                continue
            # Look up the key now, after the game has applied any custom key
            # bindings from pyskool.ini
            key = getattr(keys, action)[0]
            if writing:
                self.typing.append((key, ''))
            else:
                downs.append(key)
            if duration != 0:
                self.held_inputs.append(self.next_input - 1)
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
        if self.eric.keyboard.writing:
            # Record the characters typed on a blackboard (TYPE can't record a
            # space or '#'), and ENTER
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key in keys.ENTER:
                        self.inputs.append((self.tick, 'ENTER', 0))
                    elif e.unicode.isprintable() and e.unicode not in ' #':
                        self.inputs.append((self.tick, 'TYPE', e.unicode))
            return
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
        if self.typing and keyboard.writing and not self.eric.has_arm_raised():
            # Eric reads only the first key-down event when his arm is down
            # (and ignores the keyboard when it's raised), so deliver the
            # queued characters one at a time
            key, char = self.typing.pop(0)
            keyboard.key_down_events.insert(0, pygame.event.Event(pygame.KEYDOWN, key=key, unicode=char))
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
        # Fast-forward (with no sound or display updates) until tick --ffwd
        self.ffwd = bool(options.ffwd)
        if options.sounds:
            # Note when the game is suspended while a sound effect plays
            is_busy = sound.Beeper.is_busy
            play = sound.Beeper.play
            def watched_is_busy(beeper):
                self.sound_busy = not self.ffwd and is_busy(beeper)
                return self.sound_busy
            def watched_play(beeper, *args, **kwargs):
                if not self.ffwd:
                    return play(beeper, *args, **kwargs)
            sound.Beeper.is_busy = watched_is_busy
            sound.Beeper.play = watched_play
        else:
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            sound.Beeper.play = lambda *args, **kwargs: None
            sound.Beeper.is_busy = lambda beeper: False
        Keyboard.pump = lambda keyboard: self.pump(keyboard)
        self._guard_against_hangs()
        if options.lines:
            self._log_lines()
        if options.doors:
            self._log_doors()
        if options.bells:
            self._log_bells()
        if options.signals:
            self._log_signals()
        if options.lessons:
            self._log_lessons()
        if options.endings:
            self._log_endings()

        # With a screen, use the game's default scale and run at normal speed
        scale = None if options.screen else 1
        game_options = argparse.Namespace(config=['MaxLines, 100000000'], scale=scale, cheat=False, quick_start=True)
        g = game.Game(os.path.join(PYSKOOL_HOME, 'pyskool', 'data', 'pyskool.ini'), options.images_dir,
                      options.sounds_dir, options.ini_dir or os.path.join(user_dir, 'ini', GAMES[options.game]),
                      game_options, 'demo', None)
        if options.screen and not self.ffwd:
            g.clock = FastClock(options.speed)
        else:
            g.clock = NoClock()
        if self.ffwd:
            update = graphics.Screen._update
            graphics.Screen._update = lambda screen, *args: None
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
                if self.ffwd and tick >= options.ffwd:
                    # Show the current frame and continue at normal speed
                    self.ffwd = False
                    graphics.Screen._update = update
                    pygame.display.update()
                    g.clock = FastClock(options.speed)
                lessons_seen.add(timetable.lesson_id)
                history.append((tick, timetable.lesson_id, timetable.counter,
                                [(c.name, c.x, c.y, c.animatory_state) for c in skool.cast.character_list]))
                for c in others:
                    if c.name not in lost and self.is_lost(c):
                        lost.add(c.name)
                        self._report_lost(c, tick, history)
                if options.trace is not None and tick >= options.trace:
                    self._trace(tick)
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

    def _trace(self, tick):
        """Print Eric's state, and that of any watched characters or objects,
        after a tick.
        """
        eric, skool = self.eric, self.skool
        line = '{0}: ({1},{2}) dir={3} as={4} controller={5} score={6} lines={7}'.format(
            tick, eric.x, eric.y, eric.direction, eric.animatory_state,
            type(eric.controller).__name__ if eric.controller else None,
            skool.scoreboard.score, skool.scoreboard.lines)
        for name in self.options.watch:
            for c in skool.cast.everything:
                if name in (c.name, c.character_id):
                    line += ' | {0} ({1},{2}) dir={3} as={4}'.format(name, c.x, c.y, c.direction, c.animatory_state)
                    break
        print(line)

    def _report_lost(self, character, tick, history):
        print('LOST seed={0} tick={1} {2} at ({3},{4}) as={5} dir={6} stack={7}'.format(
            self.options.seed, tick, character.name, character.x, character.y,
            character.animatory_state, character.direction,
            '>'.join(type(c).__name__ for c in character.command_list.stack)))
        for t, lesson_id, counter, snapshot in history:
            me = [e for e in snapshot if e[0] == character.name][0]
            near = [e for e in snapshot if e[0] != character.name and abs(e[1] - me[1]) <= 3 and abs(e[2] - me[2]) <= 3]
            print('  t={0} {1} ctr={2} me={3} near={4}'.format(t, lesson_id, counter, me[1:], near))

    def _log_lines(self):
        """Print a line whenever Eric's lines total changes, saying who changed
        it and why, and whenever lines are given to another character whose
        lines don't count towards Eric's total.
        """
        source = [None]
        def with_source(method, get_source):
            def wrapped(*args):
                source[0] = get_source(*args)
                try:
                    return method(*args)
                finally:
                    source[0] = None
            return wrapped
        character.Character.print_lines_message = with_source(
            character.Character.print_lines_message,
            lambda c, recipient_id, message_id: (c, message_id, recipient_id))
        character.Character.add_lines = with_source(
            character.Character.add_lines, lambda c, lines: (c, 'AddLines', None))
        eric_mod.Eric.kiss = with_source(eric_mod.Eric.kiss, lambda e: (e, 'KISS', None))
        add_lines = skool_mod.Skool.add_lines
        def logged_add_lines(skool, addend):
            before = skool.scoreboard.lines
            add_lines(skool, addend)
            if skool.scoreboard.lines != before:
                line = 'LINES {0}: {1:+} = {2}'.format(self.tick + 1, skool.scoreboard.lines - before,
                                                       skool.scoreboard.lines)
                if source[0]:
                    c, reason, recipient_id = source[0]
                    line += ' by {0} ({1},{2}) [{3}]'.format(c.name, c.x, c.y, reason)
                    if recipient_id not in (None, self.eric.character_id):
                        line += ' to {0}'.format(skool.cast.get(recipient_id).name)
                line += ' Eric ({0},{1})'.format(self.eric.x, self.eric.y)
                print(line)
        skool_mod.Skool.add_lines = logged_add_lines
        # Skool.get_lines_message() is called by print_lines_message() whenever
        # lines are actually given (e.g. by a teacher who is on screen)
        get_lines_message = skool_mod.Skool.get_lines_message
        def logged_get_lines_message(skool, num_lines, name):
            if source[0]:
                c, reason, recipient_id = source[0]
                recipient = skool.cast.get(recipient_id)
                if recipient and not recipient.is_eric() and not recipient.adds_to_lines_total():
                    print('LINES {0}: +{1} by {2} ({3},{4}) [{5}] to {6} Eric ({7},{8})'.format(
                        self.tick + 1, num_lines, c.name, c.x, c.y, reason, recipient.name, self.eric.x, self.eric.y))
            return get_lines_message(skool, num_lines, name)
        skool_mod.Skool.get_lines_message = logged_get_lines_message

    def _log_bells(self):
        """Print a line whenever a lesson starts."""
        next_lesson = timetable_mod.Timetable.next_lesson
        def logged_next_lesson(timetable):
            next_lesson(timetable)
            print('BELL {0}: {1}'.format(self.tick + 1, timetable.lesson_id))
        timetable_mod.Timetable.next_lesson = logged_next_lesson

    def _log_doors(self):
        """Print a line whenever a door or window opens or shuts, saying who
        moved it.
        """
        source = [None]
        def with_source(method, get_source):
            def wrapped(*args):
                source[0] = get_source(*args)
                try:
                    return method(*args)
                finally:
                    source[0] = None
            return wrapped
        character.Character.move_door = with_source(character.Character.move_door, lambda c, barrier_id, shut: c)
        eric_mod.Eric.open_door = with_source(eric_mod.Eric.open_door, lambda e: e)
        skool_mod.Skool.auto_shut_doors = with_source(skool_mod.Skool.auto_shut_doors, lambda s: 'auto')
        move_door = skool_mod.Skool.move_door
        def logged_move_door(skool, barrier_id, shut):
            before = skool.barriers[barrier_id].shut
            move_door(skool, barrier_id, shut)
            if skool.barriers[barrier_id].shut != before:
                line = 'DOOR {0}: {1} {2}'.format(self.tick + 1, barrier_id, 'shut' if shut else 'opened')
                if source[0] == 'auto':
                    line += ' automatically'
                elif source[0]:
                    c = source[0]
                    line += ' by {0} ({1},{2})'.format(c.name, c.x, c.y)
                line += ' Eric ({0},{1})'.format(self.eric.x, self.eric.y)
                print(line)
        skool_mod.Skool.move_door = logged_move_door

    def _log_signals(self):
        """Print a line whenever a signal is raised or lowered, saying who
        raised or lowered it.
        """
        source = [None]
        def with_source(method):
            def wrapped(c, signal):
                source[0] = c
                try:
                    return method(c, signal)
                finally:
                    source[0] = None
            return wrapped
        character.Character.signal = with_source(character.Character.signal)
        character.Character.unsignal = with_source(character.Character.unsignal)
        def logged(method, raised):
            def wrapped(skool, signal):
                before = skool.got_signal(signal)
                method(skool, signal)
                if skool.got_signal(signal) != before:
                    line = 'SIGNAL {0}: {1} {2}'.format(self.tick + 1, signal, 'raised' if raised else 'lowered')
                    if source[0]:
                        c = source[0]
                        line += ' by {0} ({1},{2})'.format(c.name, c.x, c.y)
                    line += ' Eric ({0},{1})'.format(self.eric.x, self.eric.y)
                    print(line)
            return wrapped
        skool_mod.Skool.signal = logged(skool_mod.Skool.signal, True)
        skool_mod.Skool.unsignal = logged(skool_mod.Skool.unsignal, False)

    def _log_lessons(self):
        """Print a line whenever a teacher starts a lesson (by setting Eric's
        home room) or finishes assembly (by unsetting it), whenever the swot
        starts telling a tale, and whenever a character sets off to fetch Eric.
        """
        def location(c):
            return '{0} ({1},{2})'.format(c.name, c.x, c.y)
        def eric():
            return 'Eric ({0},{1})'.format(self.eric.x, self.eric.y)

        def logged_home_room(method, event):
            def wrapped(c):
                method(c)
                room = c.skool.get_home_room()
                print('LESSON {0}: {1} {2} by {3} {4}'.format(
                    self.tick + 1, event, room.room_id if room else c.skool.timetable.get_room_id(), location(c), eric()))
            return wrapped
        character.Character.set_home_room = logged_home_room(character.Character.set_home_room, 'started')
        character.Character.unset_home_room = logged_home_room(character.Character.unset_home_room, 'finished')

        def logged_tale(method, kind, get_subject):
            def wrapped(lsn):
                command = method(lsn)
                if command:
                    print('TALE {0}: {1} {2} by {3} to {4} {5}'.format(
                        self.tick + 1, kind, lsn.cast.get(get_subject(lsn)).name, location(lsn.swot),
                        location(lsn.teacher), eric()))
                return command
            return wrapped
        eric_id = lambda lsn: lsn.cast.eric.character_id
        lesson.Lesson.check_eric_initial = logged_tale(lesson.Lesson.check_eric_initial, 'ABSENT', eric_id)
        lesson.Lesson.check_eric = logged_tale(lesson.Lesson.check_eric, 'ABSENT', eric_id)
        lesson.Lesson.grass_for_hitting = logged_tale(lesson.Lesson.grass_for_hitting, 'HIT', lambda lsn: lsn.hitter_id)
        lesson.Lesson.grass_for_writing = logged_tale(lesson.Lesson.grass_for_writing, 'WRITE', lambda lsn: lsn.writer_id)

        execute = ai.FetchEric.execute
        def logged_execute(command):
            if not hasattr(command, 'logged'):
                command.logged = True
                print('FETCH {0}: by {1} {2}'.format(self.tick + 1, location(command.character), eric()))
            return execute(command)
        ai.FetchEric.execute = logged_execute

    def _log_endings(self):
        """Print a line whenever Eric goes up a year, and whenever the game
        ends, saying why.
        """
        up_a_year = skool_mod.Skool._up_a_year
        def logged_up_a_year(skool):
            print('UP_A_YEAR {0}: Eric ({1},{2})'.format(self.tick + 1, self.eric.x, self.eric.y))
            return up_a_year(skool)
        skool_mod.Skool._up_a_year = logged_up_a_year
        source = [None]
        end_game = character.Character.end_game
        def character_end_game(c):
            source[0] = c
            try:
                return end_game(c)
            finally:
                source[0] = None
        character.Character.end_game = character_end_game
        skool_end_game = skool_mod.Skool.end_game
        def logged_end_game(skool, up_a_year=False):
            line = 'GAME_OVER {0}:'.format(self.tick + 1)
            if up_a_year:
                line += ' up a year'
            elif source[0]:
                c = source[0]
                line += ' by {0} ({1},{2})'.format(c.name, c.x, c.y)
                if self.eric.expelled:
                    line += ' expelled'
            print(line + ' Eric ({0},{1})'.format(self.eric.x, self.eric.y))
            return skool_end_game(skool, up_a_year)
        skool_mod.Skool.end_game = logged_end_game

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
    parser.add_argument('--bells', action='store_true',
                        help='Print a line whenever a lesson starts, showing the tick and the lesson ID.')
    parser.add_argument('--doors', action='store_true',
                        help="Print a line whenever a door or window opens or shuts, showing the tick, the door or "
                             "window ID, who moved it (and where), and Eric's location.")
    parser.add_argument('-e', '--eric', metavar='MODE', choices=('follow', 'random', 'idle'),
                        help="How Eric behaves: follow little boy no. 10 or 11 (MODE=follow, the default), "
                             "press keys at random (MODE=random), or do nothing (MODE=idle).")
    parser.add_argument('--ffwd', metavar='TICKS', type=int,
                        help='With --screen, run the first TICKS ticks unthrottled, silently and without updating the '
                             'window, then continue at normal speed (or the speed set by --speed).')
    parser.add_argument('--endings', action='store_true',
                        help="Print an UP_A_YEAR line whenever Eric goes up a year, and a GAME_OVER line whenever the "
                             "game ends, showing the tick, why it ended (up a year, or who ended it and where, and "
                             "whether Eric was expelled), and Eric's location. The demo restarts the game after it "
                             "ends.")
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
                             "(default: a single press). A line of the form 'TICK TYPE TEXT' types TEXT (no spaces) on a "
                             "blackboard once Eric starts writing (after WRITE); follow it with ENTER to finish. "
                             "Anything after '#' is ignored.")
    parser.add_argument('-l', '--lesson', metavar='ID',
                        help='Use a timetable consisting of only this lesson.')
    parser.add_argument('--lessons', action='store_true',
                        help="Print a LESSON line whenever a teacher starts a lesson (by setting Eric's home room) or "
                             "finishes assembly, a TALE line whenever the swot starts telling a teacher that someone is "
                             "absent (ABSENT), hit him (HIT) or wrote on the blackboard (WRITE), and a FETCH line "
                             "whenever a character sets off to fetch Eric; each line shows the tick, who was involved "
                             "(and where), and Eric's location.")
    parser.add_argument('--lines', action='store_true',
                        help="Print a line whenever Eric's lines total changes, showing the tick, the change, the new "
                             "total, who changed it (and where), the reason (a lines message ID, AddLines or KISS), "
                             "any other recipient of the lines, and Eric's location. Also print a line (without the new "
                             "total) whenever lines are given to another character whose lines don't count towards "
                             "Eric's total.")
    parser.add_argument('-r', '--record', metavar='FILE',
                        help="Control Eric with the keyboard (requires --screen), and record the keypresses in this "
                             "file for replaying with --inputs (and the same --game, --seed and --lesson).")
    parser.add_argument('--screen', action='store_true',
                        help='Show the game in a window at normal speed instead of running headless. '
                             'Close the window or press Escape to stop.')
    parser.add_argument('-s', '--seed', type=int, default=0,
                        help='Random number seed (default: 0).')
    parser.add_argument('--speed', metavar='N', type=float, default=1,
                        help='With --screen, run the game at N times normal speed (default: 1).')
    parser.add_argument('--signals', action='store_true',
                        help="Print a line whenever a signal (as used by command lists, e.g. SwotGrassed) is raised or "
                             "lowered, showing the tick, the signal, who raised or lowered it (and where), and Eric's "
                             "location.")
    parser.add_argument('--sounds', action='store_true',
                        help='Play sound effects (requires --screen).')
    parser.add_argument('--sounds-dir', metavar='DIR', default=os.path.join(user_dir, 'sounds'),
                        help='Sounds directory (default: ~/.pyskool/sounds).')
    parser.add_argument('-t', '--ticks', type=int, default=160000,
                        help='Number of ticks to run for (default: 160000, about one cycle of the timetable).')
    parser.add_argument('--trace', metavar='TICK', type=int,
                        help="Print Eric's location, animatory state, controlling command, score and lines total "
                             "after every tick from this one on.")
    parser.add_argument('--watch', metavar='NAMES', type=lambda s: s.split(','), default=[],
                        help="With --trace, also print the location of these characters or objects (a comma-separated "
                             "list of names or IDs, e.g. 'MR WACKER,MOUSE').")
    options = parser.parse_args(args)
    if sum(1 for o in (options.eric, options.inputs, options.record) if o) > 1:
        parser.error('only one of --eric, --inputs and --record may be used')
    if options.record and not options.screen:
        parser.error('--record requires --screen')
    if options.speed <= 0:
        parser.error('--speed must be greater than 0')
    if options.speed != 1 and not options.screen:
        parser.error('--speed requires --screen')
    if options.ffwd is not None and not options.screen:
        parser.error('--ffwd requires --screen')
    if options.sounds and not options.screen:
        parser.error('--sounds requires --screen')
    options.eric = options.eric or 'follow'
    return options

###############################################################################
# Begin
###############################################################################
if __name__ == '__main__':
    sys.exit(0 if Demo(parse_args(sys.argv[1:])).run() else 1)
