import argparse
import hashlib
import os
import random
import shutil

import pytest

import pyskooltest
from pyskooltest import PYSKOOL_HOME, demo, pygame, run
from pyskool import items, keys, room, user_dir

REPLAYS_DIR = os.path.join(PYSKOOL_HOME, 'replays')

def _state(g):
    """Return a snapshot of the state of a game: the lesson, the skool clock,
    the score, lines total and hi-score, the location, animatory state,
    direction and command stack of every character, and a hash of the
    screen contents."""
    skool = g.skool
    timetable = skool.timetable
    scoreboard = skool.scoreboard
    return (
        timetable.lesson_id,
        timetable.counter,
        (scoreboard.score, scoreboard.lines, scoreboard.hiscore),
        [(c.name, c.x, c.y, c.animatory_state, c.direction, [type(cmd).__name__ for cmd in c.command_list.stack])
         for c in skool.cast.character_list],
        hashlib.md5(pygame.image.tostring(pygame.display.get_surface(), 'RGB')).hexdigest()
    )

def _install_pump(monkeypatch, g, presses=(), held=()):
    """Replace Keyboard.pump() with a method that supplies no input from Eric
    other than acknowledging messages, delivers the keys in 'presses' (a
    list, which is emptied as it goes) one per call, and holds down the keys
    in 'held'."""
    def pump(keyboard):
        keyboard.quit = False
        keyboard.pressed_keys = demo.PressedKeys({k: True for k in held})
        keyboard.key_down_events = []
        if presses:
            keyboard.key_down_events.append(pygame.event.Event(pygame.KEYDOWN, key=presses.pop(0), unicode=''))
        if g.skool.cast.eric.frozen:
            keyboard.key_down_events.append(pygame.event.Event(pygame.KEYDOWN, key=keys.UNDERSTOOD[0], unicode=''))
    monkeypatch.setattr(demo.Keyboard, 'pump', pump)

def _continue(monkeypatch, g, ticks):
    """Run a game for a number of ticks with no input from Eric (other than
    acknowledging messages), and return the state of the game (see _state())
    after each tick."""
    _install_pump(monkeypatch, g)
    states = []
    for i in range(ticks):
        assert not g._main_loop()
        states.append(_state(g))
    return states

def _skool_images(skool):
    """Return the contents (as RGB bytes) of the images of the whole play
    area: the full-colour image in graphics mode 0, or the ink and paper
    images in graphics mode 1."""
    return [pygame.image.tostring(image.surface, 'RGB') for image in (skool.skool, skool.ink, skool.paper) if image]

def _start(monkeypatch, capsys, tmp_path, game, inputs, ticks, setup=None, lesson=None, options=()):
    """Run a game headless for a number of ticks with the given inputs (see
    run(), which also explains 'setup', 'lesson' and 'options'), and return
    the Game object that demo.py created."""
    games = []
    main_loop = demo.game.Game._main_loop
    def captured_main_loop(g):
        if not games:
            games.append(g)
        return main_loop(g)
    monkeypatch.setattr(demo.game.Game, '_main_loop', captured_main_loop)
    run(monkeypatch, capsys, tmp_path, game, lesson, inputs, ticks, setup=setup, options=options)
    return games[0]

def _new_game(game, sav_file=None):
    """Create a new Game object (restoring a saved game if 'sav_file' is
    given), set up as demo.py sets up its Game object, and return it."""
    game_options = argparse.Namespace(config=['MaxLines, 100000000'], scale=1, cheat=False, quick_start=True)
    g = demo.game.Game(os.path.join(PYSKOOL_HOME, 'pyskool', 'data', 'pyskool.ini'),
                       os.path.join(user_dir, 'images'), os.path.join(user_dir, 'sounds'),
                       os.path.join(user_dir, 'ini', demo.GAMES[game]), game_options, 'demo', sav_file)
    g.clock = demo.NoClock()
    g.confirm_close = 0
    g.paused = False
    g.scroll = 0
    return g

def _save_and_restore(monkeypatch, capsys, tmp_path, game, replay, ticks, more_ticks, setup=None, check_images=True,
                      lesson=None, options=()):
    """Run a replay headless (or, if 'replay' is None, run the game with Eric
    idle) for a number of ticks, save the game, and then restore it into a
    new Game object. Check that the restored game's state and play area
    images are the same as the saved game's, and that both games then run in
    exactly the same way for a further number of ticks. Return the saved game
    and the restored game.

    If given, 'setup' is called with the Demo object before the first tick
    (see run()). If 'check_images' is False, the play area images are not
    checked. If 'lesson' is given, the timetable is restricted to that lesson
    (see run()). 'options' is a sequence of any extra options to pass to
    demo.py when running the game that is saved (see run()); the restored game
    is created as demo.py creates its Game object, without them.
    """
    inputs = ''
    if replay:
        with open(os.path.join(REPLAYS_DIR, replay)) as f:
            inputs = f.read()

    saved = _start(monkeypatch, capsys, tmp_path, game, inputs, ticks, setup, lesson, options)

    # Save the game (Game._save() writes to a directory relative to the cwd)
    monkeypatch.chdir(tmp_path)
    saved._save('test.sav')
    sav_file = os.path.join(tmp_path, *saved.skool.save_game_dir.split('/'), 'test.sav')
    assert os.path.isfile(sav_file)
    saved_state = _state(saved)
    saved_images = _skool_images(saved.skool)

    # Run the saved game on for a while, and then restore the random state
    # (which the saved game file doesn't include)
    rng_state = random.getstate()
    saved_states = _continue(monkeypatch, saved, more_ticks)
    random.setstate(rng_state)

    # Restore the game into a new Game object
    restored = _new_game(game, sav_file)
    assert restored.skool is not saved.skool

    # The restored game's state (except for the screen contents, which are
    # not redrawn until the next tick) is the same as the saved game's
    assert _state(restored)[:-1] == saved_state[:-1]

    # The restored game's play area images (including the parts that are off
    # screen) are the same as the saved game's, so every door, window, cup,
    # bike, shield and safe has been redrawn as it was
    if check_images:
        assert _skool_images(restored.skool) == saved_images

    # The restored game then runs in exactly the same way as the saved game
    restored_states = _continue(monkeypatch, restored, more_ticks)
    for tick, (saved_s, restored_s) in enumerate(zip(saved_states, restored_states), ticks + 1):
        assert restored_s == saved_s, f'Game states differ at tick {tick}'

    return saved, restored

def _set_up_eric(score=0, lines=0, flashing=(), shield_mode=1, safe=False, inventory=(), mice=0):
    """Return a setup function (see run()) that gives Eric a score and lines
    total, flashes the shields whose indexes are in 'flashing' (and the safe
    if 'safe' is True), sets the shield mode, and gives Eric some inventory
    items and mice."""
    def setup(d):
        skool = d.skool
        skool.add_to_score(score)
        skool.add_lines(lines)
        for i in flashing:
            skool.shields[i].flash()
        skool.shield_mode = shield_mode
        if safe:
            skool.safe.flash()
        eric = d.eric
        eric.inventory.update(inventory)
        eric.mice = mice
        eric.print_inventory()
        eric.print_mouse_inventory()
    return setup

def test_save_and_restore_skool_daze(monkeypatch, capsys, tmp_path):
    # Save the game after Eric has flashed all but two of the shields and got
    # some lines
    setup = _set_up_eric(2700, 1900, flashing=range(2, 15))
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'sd', None, 100, 500, setup)
    skool = restored.skool
    assert skool.scoreboard.score >= 2700
    assert skool.scoreboard.lines >= 1900
    assert skool.shield_mode == 1
    assert [shield.flashing for shield in skool.shields] == [False] * 2 + [True] * 13

def test_save_and_restore_back_to_skool(monkeypatch, capsys, tmp_path):
    # Save the game after Eric has collected the water pistol, some
    # stinkbombs and a mouse
    setup = _set_up_eric(2000, 400, inventory=(items.WATER_PISTOL, items.STINKBOMBS3), mice=1)
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'bts', None, 100, 500, setup)
    skool = restored.skool
    assert skool.scoreboard.score >= 2000
    assert skool.scoreboard.lines >= 400
    assert skool.cast.eric.inventory == {items.WATER_PISTOL, items.STINKBOMBS3}
    assert skool.cast.eric.mice == 1

def test_save_and_restore_skool_daze_take_too(monkeypatch, capsys, tmp_path):
    # Save the game after Eric has flashed all the shields and opened the safe
    setup = _set_up_eric(6500, 3200, flashing=range(15), shield_mode=3, safe=True)
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'sdtt', None, 100, 500, setup)
    skool = restored.skool
    assert skool.scoreboard.score >= 6500
    assert skool.scoreboard.lines >= 3200
    assert skool.shield_mode == 3
    assert all(shield.flashing for shield in skool.shields)
    assert skool.safe.flashing

def test_save_and_restore_ezad_looks(monkeypatch, capsys, tmp_path):
    # Save the game after Eric has opened the safe and started unflashing the
    # shields
    setup = _set_up_eric(8000, 300, flashing=range(1, 15), shield_mode=3, safe=True)
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'el', None, 100, 500, setup)
    skool = restored.skool
    assert skool.scoreboard.score >= 8000
    assert skool.scoreboard.lines >= 300
    assert skool.shield_mode == 3
    assert [shield.flashing for shield in skool.shields] == [False] + [True] * 14
    assert skool.safe.flashing

def test_save_and_restore_back_to_skool_daze(monkeypatch, capsys, tmp_path):
    # Save the game after Eric has flashed all the shields and collected the
    # sherry-filled water pistol, some stinkbombs and the storeroom key.
    inventory = (items.SHERRY_PISTOL, items.STINKBOMBS1, items.STOREROOM_KEY)
    setup = _set_up_eric(10000, 6900, flashing=range(16), shield_mode=2, inventory=inventory)
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'btsd', None, 100, 500, setup)
    skool = restored.skool
    assert skool.scoreboard.score >= 10000
    assert skool.scoreboard.lines >= 6900
    assert skool.shield_mode == 2
    assert all(shield.flashing for shield in skool.shields)
    assert not skool.safe.flashing
    assert skool.cast.eric.inventory == set(inventory)

def _start_test(monkeypatch, capsys, tmp_path, game='sd'):
    """Run a game headless for a few ticks with Eric walking left, and return
    the Game object. The cwd is changed to 'tmp_path' (where any saved games
    go) and the random state is fixed."""
    g = _start(monkeypatch, capsys, tmp_path, game, '0 LEFT 100', 100)
    monkeypatch.chdir(tmp_path)
    random.seed(1)
    return g

def _press(monkeypatch, g, *keys_pressed):
    """Press keys one at a time, running the main loop until each has been
    delivered by Keyboard.pump() and then once more (so that the key is acted
    on even if it was delivered at the end of the loop, as it is while a menu
    is displayed). Return whether the main loop said the game is quitting."""
    presses = []
    _install_pump(monkeypatch, g, presses)
    for key in keys_pressed:
        presses.append(key[0])
        for i in range(100):
            if g._main_loop():
                return True
            if not presses:
                break
        else:
            raise AssertionError(f'Key {key} was not delivered')
        if g._main_loop():
            return True
    return False

def _sav_files(g):
    save_game_dir = g.skool.save_game_dir
    if os.path.isdir(save_game_dir):
        return sorted(f for f in os.listdir(save_game_dir) if f.endswith('.sav'))
    return []

def test_menu_open_and_exit(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert not _press(monkeypatch, g, keys.MENU)
    assert g.menu is g.menus['Main']
    assert g.menu.selected_index == 0
    counter = g.skool.timetable.counter

    # MENU_PREV and MENU_NEXT move the selection, wrapping round at either
    # end, and the game doesn't advance while the menu is displayed
    assert not _press(monkeypatch, g, keys.MENU_PREV)
    assert g.menu.selected_index == len(g.menu.items) - 1
    assert not _press(monkeypatch, g, keys.MENU_NEXT, keys.MENU_NEXT)
    assert g.menu.selected_index == 1
    assert g.skool.timetable.counter == counter

    # MENU_EXIT closes the menu and the game carries on
    assert not _press(monkeypatch, g, keys.MENU_EXIT)
    assert g.menu is None
    assert not g._main_loop()
    assert g.skool.timetable.counter != counter

    # The menu is reset when it's opened again
    assert not _press(monkeypatch, g, keys.MENU)
    assert g.menu.selected_index == 0

def test_menu_resume(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    before = _state(g)
    assert not _press(monkeypatch, g, keys.MENU)
    assert g.menu.items[0][0] == demo.game.RESUME
    assert _state(g)[-1] != before[-1]
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.menu is None
    # The skool has been redrawn without the menu
    after = _state(g)
    g.skool.draw()
    assert _state(g)[-1] == after[-1]

def test_menu_save_game(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert _sav_files(g) == []
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_NEXT)
    assert g.menu.items[1][0] == demo.game.SAVE
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    sav_files = _sav_files(g)
    assert len(sav_files) == 1
    assert g.menu.status == f'Saved {sav_files[0]}'
    # The menu stays open
    assert g.menu is g.menus['Main']

def test_menu_load_game(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_NEXT, keys.MENU_EXEC, keys.MENU_EXIT)
    sav_file = _sav_files(g)[0]
    saved_state = _state(g)[:-1]
    skool = g.skool

    # Run the game on, and then load the saved game
    _continue(monkeypatch, g, 50)
    assert _state(g)[:-1] != saved_state
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_NEXT, keys.MENU_NEXT)
    assert g.menu.items[2][0] == demo.game.LOAD
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.menu.status == f'Loaded {sav_file}'
    assert g.skool is not skool
    assert _state(g)[:-1] == saved_state

    # The game carries on from the saved game
    assert not _press(monkeypatch, g, keys.MENU_EXIT)
    assert g.menu is None
    _continue(monkeypatch, g, 50)

@pytest.mark.parametrize('saved_fullscreen', [True, False])
def test_load_game_keeps_display_mode(monkeypatch, capsys, tmp_path, saved_fullscreen):
    g = _start_test(monkeypatch, capsys, tmp_path)
    modes = _record_modes(monkeypatch)
    g.screen.fullscreen = saved_fullscreen
    g._save('test.sav')
    sav_file = os.path.join(tmp_path, *g.skool.save_game_dir.split('/'), 'test.sav')

    # A game saved in one display mode is loaded in the current mode
    g.screen.toggle_fullscreen(g.skool)
    assert g.screen.fullscreen is not saved_fullscreen
    skool = g.skool
    modes.clear()
    g._load(sav_file)
    assert g.skool is not skool
    assert g.screen.fullscreen is not saved_fullscreen
    assert modes == [0 if saved_fullscreen else FULLSCREEN]
    _continue(monkeypatch, g, 20)

def test_load_game_saved_in_full_screen_mode_at_startup(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    modes = _record_modes(monkeypatch)
    g.screen.toggle_fullscreen(g.skool)
    g._save('test.sav')
    sav_file = os.path.join(tmp_path, *g.skool.save_game_dir.split('/'), 'test.sav')

    # A game saved in full-screen mode is loaded at startup in windowed mode
    modes.clear()
    restored = _new_game('sd', sav_file)
    assert not restored.screen.fullscreen
    assert modes and not any(modes)
    _continue(monkeypatch, restored, 20)

def test_menu_load_game_with_no_saved_games(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    skool = g.skool
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_NEXT, keys.MENU_NEXT, keys.MENU_EXEC)
    assert g.menu.status == 'No saved games found'
    assert g.skool is skool

def test_menu_scale_up_and_down(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    width, height = pygame.display.get_surface().get_size()
    assert g.screen.scale == 1
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_NEXT, keys.MENU_NEXT, keys.MENU_NEXT)
    assert g.menu.items[3][0] == demo.game.SCALE_UP
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.screen.scale == 2
    assert g.menu.status == 'Scale set to 2'
    assert pygame.display.get_surface().get_size() == (2 * width, 2 * height)

    assert not _press(monkeypatch, g, keys.MENU_NEXT)
    assert g.menu.items[4][0] == demo.game.SCALE_DOWN
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.screen.scale == 1
    assert g.menu.status == 'Scale set to 1'
    assert pygame.display.get_surface().get_size() == (width, height)

    # The scale can't go below 1, and the status bar is left alone if it
    # doesn't change
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.screen.scale == 1
    assert g.menu.status == 'Scale set to 1'
    assert pygame.display.get_surface().get_size() == (width, height)

    # The game carries on at the new scale
    assert not _press(monkeypatch, g, keys.MENU_PREV, keys.MENU_EXEC, keys.MENU_EXIT)
    assert g.screen.scale == 2
    _continue(monkeypatch, g, 20)
    assert pygame.display.get_surface().get_size() == (2 * width, 2 * height)

def _start_speech_bubble_test(monkeypatch, capsys, tmp_path):
    """Run Skool Daze headless until Mr Withit is speaking, and return the
    Game object and his speech bubble. The cwd is changed to 'tmp_path'
    (where any saved games go)."""
    g = _start(monkeypatch, capsys, tmp_path, 'sd', '', 620, lesson='Wacker-ExamRoom')
    monkeypatch.chdir(tmp_path)
    bubbles = g.skool.cast.get_speech_bubbles()
    assert len(bubbles) == 1
    bubble = bubbles[0]
    assert bubble.words == 'COME ON CHAPS - SETTLE DOWN'
    assert bubble.image is not None
    return g, bubble

def test_load_game_with_speech_bubble(monkeypatch, capsys, tmp_path):
    g, bubble = _start_speech_bubble_test(monkeypatch, capsys, tmp_path)
    g._save('test.sav')
    sav_file = os.path.join(tmp_path, *g.skool.save_game_dir.split('/'), 'test.sav')

    # The speech bubble's image isn't saved, but it's rebuilt when the game
    # is loaded
    restored = _new_game('sd', sav_file)
    bubbles = restored.skool.cast.get_speech_bubbles()
    assert len(bubbles) == 1
    assert bubbles[0] is not bubble
    assert bubbles[0].words == bubble.words
    assert bubbles[0].image is not None
    assert _image_data(bubbles[0].image.surface) == _image_data(bubble.image.surface)
    _continue(monkeypatch, restored, 20)

def test_menu_scale_up_with_speech_bubble(monkeypatch, capsys, tmp_path):
    g, bubble = _start_speech_bubble_test(monkeypatch, capsys, tmp_path)
    width, height = bubble.image.surface.get_size()

    # The game doesn't advance while the menu is displayed, so the speech
    # bubble's image is rebuilt at the new scale only by rescaling
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_NEXT, keys.MENU_NEXT, keys.MENU_NEXT)
    assert g.menu.items[3][0] == demo.game.SCALE_UP
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.screen.scale == 2
    assert g.skool.cast.get_speech_bubbles() == [bubble]
    assert bubble.image.surface.get_size() == (2 * width, 2 * height)

def _record_modes(monkeypatch):
    """Replace pygame.display.set_mode() with a function that records the
    flags it's given and then sets the mode without them (because full-screen
    mode isn't available with the dummy video driver), and return the list of
    flags."""
    modes = []
    set_mode = pygame.display.set_mode
    def record_mode(size, flags=0):
        modes.append(flags)
        return set_mode(size)
    monkeypatch.setattr(pygame.display, 'set_mode', record_mode)
    return modes

FULLSCREEN = pygame.FULLSCREEN | pygame.SCALED

def test_menu_toggle_fullscreen(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    modes = _record_modes(monkeypatch)
    assert not _press(monkeypatch, g, keys.MENU, *[keys.MENU_NEXT] * 5)
    assert g.menu.items[5][0] == demo.game.TOGGLE_FULLSCREEN
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.screen.fullscreen
    assert modes == [FULLSCREEN]
    assert g.menu is g.menus['Main']

    # The menu is redrawn over the redrawn skool
    menu_screen = _state(g)[-1]
    g.screen.draw_menu(g.menu)
    assert _state(g)[-1] == menu_screen

    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert not g.screen.fullscreen
    assert modes == [FULLSCREEN, 0]

def test_menu_quit(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert not _press(monkeypatch, g, keys.MENU, keys.MENU_PREV)
    assert g.menu.items[6][0] == demo.game.QUIT
    assert _press(monkeypatch, g, keys.MENU_EXEC)

def test_quit_menu_yes(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert g.confirm_quit
    assert not _press(monkeypatch, g, keys.QUIT)
    assert g.menu is g.menus['Quit']
    assert g.menu.items[0] == [demo.game.QUIT, 'Yes']
    assert _press(monkeypatch, g, keys.MENU_EXEC)

def test_quit_menu_no(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert not _press(monkeypatch, g, keys.QUIT)
    assert g.menu is g.menus['Quit']
    assert not _press(monkeypatch, g, keys.MENU_NEXT)
    assert g.menu.items[1] == [demo.game.RESUME, 'No']
    assert not _press(monkeypatch, g, keys.MENU_EXEC)
    assert g.menu is None
    _continue(monkeypatch, g, 20)

def _start_cheat_test(monkeypatch, capsys, tmp_path, game='sd'):
    """Start a game (see _start_test()) with the cheat keys enabled, and
    return the Game object."""
    g = _start_test(monkeypatch, capsys, tmp_path, game)
    g.cheat = True
    # Make sure the NO_LINES cheat key doesn't leave lines-giving disabled
    monkeypatch.setattr(demo.character.Character, 'give_lines', demo.character.Character.give_lines)
    capsys.readouterr()
    return g

def test_cheat_keys_disabled(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert not g.cheat
    skool = g.skool
    lesson_id = skool.timetable.lesson_id
    _press(monkeypatch, g, keys.NEXT_LESSON, keys.FLASH_MOST, keys.ADD_LINES)
    assert skool.timetable.lesson_id == lesson_id
    assert not any(shield.flashing for shield in skool.shields)
    assert skool.scoreboard.lines == 0

def test_cheat_keys_slow_and_fast(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path)
    assert g.speed == 1
    for held, speed in ((keys.SLOW, 0.5), (keys.FAST, 2), ((), 1)):
        _install_pump(monkeypatch, g, held=held[:1])
        for i in range(10):
            g._main_loop()
        assert g.speed == speed

def test_cheat_key_next_lesson(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path)
    timetable = g.skool.timetable
    index = timetable.index
    _press(monkeypatch, g, keys.NEXT_LESSON)
    assert timetable.index == (index + 1) % len(timetable.lessons)
    assert timetable.lesson_id == timetable.lessons[timetable.index]

def test_cheat_keys_flash_and_unflash_most(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path)
    skool = g.skool
    _press(monkeypatch, g, keys.FLASH_MOST)
    assert skool.shield_mode == 1
    assert [shield.flashing for shield in skool.shields] == [False] + [True] * (len(skool.shields) - 1)
    assert not skool.safe.flashing
    assert 'DEBUG: Flashed all but one shield; hit it and then open the safe' in capsys.readouterr().err

    _press(monkeypatch, g, keys.UNFLASH_MOST)
    assert skool.shield_mode == 3
    assert [shield.flashing for shield in skool.shields] == [True] + [False] * (len(skool.shields) - 1)
    assert skool.safe.flashing
    assert 'DEBUG: Unflashed all but one shield; hit it to go up a year' in capsys.readouterr().err

def test_up_a_year_message_with_one_line(monkeypatch, capsys, tmp_path):
    # Eric stands on the top floor below the first shield; he unflashes all
    # the other shields (with the UNFLASH_MOST cheat key), and then jumps to
    # hit the first one, which sends him up a year; the up-a-year message
    # (configured here to have no newline character) is printed in the lesson
    # box on a single line
    inputs = """
        1 UNFLASH_MOST
        10 JUMP
    """
    prints = []
    def setup(d):
        d.eric.x, d.eric.y, d.eric.direction = 6, 3, -1
        screen = d.skool.screen
        print_lesson = type(screen).print_lesson
        def lesson_box():
            coords = screen.scale_coords(screen.lesson_box_pos)
            size = screen.lesson_box.surface.get_size()
            return pygame.image.tostring(screen.screen.subsurface(coords, size), 'RGB')
        def recorded(s, *text_lines):
            print_lesson(s, *text_lines)
            if len(text_lines) > 1:
                return
            printed = lesson_box()
            # The lesson box should look the same as when the text is printed
            # with an empty second line, and different from when it's blank
            print_lesson(s, *text_lines, '')
            two_lines = lesson_box()
            print_lesson(s, '', '')
            blank = lesson_box()
            print_lesson(s, *text_lines)
            prints.append((d.tick, text_lines, printed == two_lines, printed != blank))
        monkeypatch.setattr(type(screen), 'print_lesson', recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 30, setup=setup,
                   options=['--config', 'Cheat,1', '--config', 'UpAYearMessage,UP A YEAR!'])

    # Eric went up a year (the tick here is one more than d.tick, following
    # demo.py's '--endings' output), and the up-a-year message was printed
    # (with nothing on the second line); no other text was printed in the
    # lesson box without a second line
    assert d.up_a_year_ticks == [19]
    assert prints == [(18, ('UP A YEAR!',), True, True)]

def test_cheat_key_no_lines(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path)
    teacher = g.cast.get('WACKER')
    teacher.give_lines('ERIC', 'NEVER_AGAIN')
    assert teacher.lines_message is not None
    teacher.lines_message = None

    # Disable lines-giving
    _press(monkeypatch, g, keys.NO_LINES)
    assert 'DEBUG: Disabled lines-giving' in capsys.readouterr().err
    teacher.give_lines('ERIC', 'NEVER_AGAIN')
    assert teacher.lines_message is None

    # Enable lines-giving again
    _press(monkeypatch, g, keys.NO_LINES)
    assert 'DEBUG: Enabled lines-giving' in capsys.readouterr().err

def test_cheat_key_no_lines_twice(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path)
    _press(monkeypatch, g, keys.NO_LINES, keys.NO_LINES)
    teacher = g.cast.get('WACKER')
    teacher.give_lines('ERIC', 'NEVER_AGAIN')
    assert teacher.lines_message == ('ERIC', 'NEVER_AGAIN')

def test_cheat_keys_add_and_zero_lines(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path)
    scoreboard = g.skool.scoreboard
    assert scoreboard.lines == 0
    min_lines, max_lines = (100 * n for n in g.cast.lines_range)
    total = 0
    for i in range(3):
        _press(monkeypatch, g, keys.ADD_LINES)
        added = scoreboard.lines - total
        assert min_lines <= added < max_lines
        assert added % 100 == 0
        assert f'DEBUG: Added {added} lines' in capsys.readouterr().err
        total = scoreboard.lines

    _press(monkeypatch, g, keys.ZERO_LINES)
    assert scoreboard.lines == 0
    assert 'DEBUG: Set lines total to zero' in capsys.readouterr().err

@pytest.mark.parametrize('game', ['sd', 'bts'])
def test_cheat_key_reveal(monkeypatch, capsys, tmp_path, game):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path, game)
    skool = g.skool
    _press(monkeypatch, g, keys.REVEAL)
    expected = []
    for room in skool.rooms.values():
        for desk in room.desks:
            if desk.contents:
                expected.append(f'DEBUG: {room.name} x={desk.x}: {desk.contents}')
    for c in g.cast.character_list:
        if c.special_answer:
            expected.append(f'DEBUG: {c.name}: {c.special_answer}')
    for name, combination in (
            ('Safe', skool.safe_combination),
            ('Bike', skool.bike_combination),
            ('Storeroom', skool.storeroom_combination)
    ):
        if combination:
            expected.append(f'DEBUG: {name}: {combination}')
    assert capsys.readouterr().err.splitlines() == expected
    if game == 'sd':
        # Skool Daze has Mr Creak's birth year and a safe combination, but no
        # desk contents, bike or storeroom
        assert expected == [f'DEBUG: MR CREAK: {g.cast.get("CREAK").special_answer}',
                            f'DEBUG: Safe: {skool.safe_combination}']
    else:
        # Back to Skool has desk contents, and bike and storeroom combinations,
        # but no safe combination
        assert skool.safe_combination is None
        assert any(line.endswith(': WATER_PISTOL') for line in expected)
        assert expected[-2:] == [f'DEBUG: Bike: {skool.bike_combination}',
                                 f'DEBUG: Storeroom: {skool.storeroom_combination}']

def test_cheat_key_switch_pistol(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path, 'bts')
    inventory = g.cast.eric.inventory
    # Nothing happens if Eric has no water pistol
    _press(monkeypatch, g, keys.SWITCH_PISTOL)
    assert not inventory & {items.WATER_PISTOL, items.SHERRY_PISTOL}

    _press(monkeypatch, g, keys.GIVE_WATER_PISTOL)
    assert items.WATER_PISTOL in inventory
    _press(monkeypatch, g, keys.SWITCH_PISTOL)
    assert items.SHERRY_PISTOL in inventory
    assert items.WATER_PISTOL not in inventory
    _press(monkeypatch, g, keys.SWITCH_PISTOL)
    assert items.WATER_PISTOL in inventory
    assert items.SHERRY_PISTOL not in inventory

def test_cheat_key_give_all(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path, 'bts')
    skool = g.skool
    eric = g.cast.eric
    frog = g.cast.frogs[0]
    assert skool.bike.chained
    _press(monkeypatch, g, keys.GIVE_ALL)
    assert {items.SAFE_KEY, items.STOREROOM_KEY, items.FROG, items.WATER_PISTOL, items.STINKBOMBS3} <= eric.inventory
    assert eric.mice == 8
    assert not frog.is_visible()
    assert not skool.bike.chained

def test_cheat_keys_open_and_close_doors(monkeypatch, capsys, tmp_path):
    g = _start_cheat_test(monkeypatch, capsys, tmp_path, 'bts')
    skool = g.skool
    barriers = list(skool.doors.values()) + list(skool.windows.values())
    assert barriers
    _press(monkeypatch, g, keys.OPEN_DOORS)
    assert not any(b.shut for b in barriers)
    assert 'DEBUG: Opened all doors and windows' in capsys.readouterr().err
    _press(monkeypatch, g, keys.CLOSE_DOORS)
    assert all(b.shut for b in barriers)
    assert 'DEBUG: Closed all doors and windows' in capsys.readouterr().err

def _play(monkeypatch, g, ticks, end_game_at=()):
    """Call Game.play() with an unthrottled clock, end the game (as if Eric
    had been expelled) after each main loop pass whose number (counting from
    1) is in 'end_game_at', and make the window's close button appear to be
    clicked after 'ticks' passes. Return a list of the events that occurred:
    ('scroll_on', pass number), ('reinitialise', pass number) and ('quit',
    pass number)."""
    monkeypatch.setattr(pygame.time, 'Clock', demo.NoClock)
    events = []
    passes = [0]
    main_loop = demo.game.Game._main_loop
    def counted_main_loop(game):
        passes[0] += 1
        if passes[0] == ticks:
            # The pump resets Keyboard.quit, so make got_quit() say yes
            # regardless
            monkeypatch.setattr(game.keyboard, 'got_quit', lambda: True)
        rv = main_loop(game)
        if rv:
            events.append(('quit', passes[0]))
        elif passes[0] in end_game_at:
            game.skool.end_game()
        return rv
    monkeypatch.setattr(demo.game.Game, '_main_loop', counted_main_loop)
    for cls, name in ((demo.skool_mod.Skool, 'scroll_on'), (demo.skool_mod.Skool, 'reinitialise')):
        method = getattr(cls, name)
        def recorded(skool, *args, method=method, name=name):
            events.append((name, passes[0]))
            return method(skool, *args)
        monkeypatch.setattr(cls, name, recorded)
    _install_pump(monkeypatch, g)
    assert g.play() is None
    return events

def test_play_quit(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert g.quick_start
    counter = g.skool.timetable.counter
    events = _play(monkeypatch, g, 50)
    # The skool isn't scrolled on in quick start mode; play() returns as soon
    # as the main loop says the game is quitting
    assert events == [('quit', 50)]
    assert not g.quick_start
    assert not g.paused
    assert g.skool.timetable.counter != counter

def test_play_scroll_on(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    g.quick_start = False
    columns = []
    scroll_skool = demo.graphics.Screen.scroll_skool
    def recorded_scroll_skool(screen, skool, clock):
        columns.append(screen.column)
        scroll_skool(screen, skool, clock)
        columns.append(screen.column)
    monkeypatch.setattr(demo.graphics.Screen, 'scroll_skool', recorded_scroll_skool)
    events = _play(monkeypatch, g, 20)
    assert events == [('scroll_on', 0), ('quit', 20)]
    # The skool was scrolled on across the whole screen, ending up where it
    # started
    assert len(columns) == 2
    assert columns[0] == columns[1]

def test_play_restart(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    skool = g.skool
    skool.add_lines(500)
    events = _play(monkeypatch, g, 60, end_game_at=(10, 30))
    # After each game ends, the skool is reinitialised and (since quick start
    # mode applies only to the first game) scrolled on
    assert events == [('reinitialise', 10), ('scroll_on', 10), ('reinitialise', 30), ('scroll_on', 30), ('quit', 60)]
    assert g.skool is skool
    assert not skool.game_over
    # Eric was expelled, so the score and lines have been cleared
    assert skool.scoreboard.lines == 0
    # Each new game starts at a playtime
    assert skool.timetable.is_playtime()

def test_mixer_failure(monkeypatch, capsys, tmp_path):
    pyskooltest.check_assets('sd')
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')
    monkeypatch.setattr(pygame.mixer, 'get_init', lambda: None)
    g = _new_game('sd')
    out = capsys.readouterr().out.splitlines()
    assert out[0] == 'WARNING: pygame.mixer failed to initialise; there will be no sound'
    assert not any(line.startswith('WARNING') for line in out[1:])
    assert g.skool is not None

def test_full_screen_key(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    modes = _record_modes(monkeypatch)
    tick = []
    tick_method = demo.skool_mod.Skool.tick
    monkeypatch.setattr(demo.skool_mod.Skool, 'tick', lambda skool: tick.append(1) or tick_method(skool))
    presses = [keys.FULL_SCREEN[0]]
    _install_pump(monkeypatch, g, presses)
    while presses:
        g._main_loop()
    ticks = len(tick)
    # The main loop pass on which the key is acted on does nothing else
    assert not g._main_loop()
    assert g.screen.fullscreen
    assert modes == [FULLSCREEN]
    assert len(tick) == ticks
    assert g.menu is None
    assert not g._main_loop()
    assert len(tick) == ticks + 1

def test_full_screen_key_while_paused(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    assert not _press(monkeypatch, g, keys.PAUSE)
    assert g.paused
    state = _state(g)
    modes = _record_modes(monkeypatch)
    updates = []
    update = pygame.display.update
    monkeypatch.setattr(pygame.display, 'update', lambda *args: updates.append(args) or update(*args))

    # The display is updated with the redrawn skool straight away, and the
    # game stays paused
    assert not _press(monkeypatch, g, keys.FULL_SCREEN)
    assert g.screen.fullscreen
    assert modes == [FULLSCREEN]
    assert () in updates
    assert g.paused
    assert _state(g) == state

    updates.clear()
    assert not _press(monkeypatch, g, keys.FULL_SCREEN)
    assert not g.screen.fullscreen
    assert modes == [FULLSCREEN, 0]
    assert () in updates
    assert g.paused
    assert _state(g) == state

def test_screenshot_key(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    monkeypatch.setattr(demo.game.time, 'strftime', lambda fmt: '20261015-120000')
    capsys.readouterr()
    assert not _press(monkeypatch, g, keys.SCREENSHOT, keys.SCREENSHOT)
    screenshot_dir = tmp_path / g.skool.screenshot_dir
    assert sorted(os.listdir(screenshot_dir)) == ['20261015-120000-000.png', '20261015-120000-001.png']
    assert g.screenshot == 2
    err = capsys.readouterr().err
    for n in range(2):
        assert f'DEBUG: Took screenshot: {os.path.join(g.skool.screenshot_dir, f"20261015-120000-00{n}.png")}' in err
    image = pygame.image.load(str(screenshot_dir / '20261015-120000-000.png'))
    assert image.get_size() == pygame.display.get_surface().get_size()

def test_close_window_with_confirm_close(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    g.confirm_close = 1
    monkeypatch.setattr(g.keyboard, 'got_quit', lambda: True)
    assert not g._main_loop()
    assert g.menu is g.menus['Quit']

def test_quit_key_without_confirm_quit(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    g.confirm_quit = 0
    assert _press(monkeypatch, g, keys.QUIT)
    assert g.menu is None

def test_pause_key(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    pauses = []
    monkeypatch.setattr(g.beeper, 'pause', lambda: pauses.append(1))
    assert not _press(monkeypatch, g, keys.PAUSE)
    assert g.paused
    state = _state(g)
    for i in range(20):
        assert not g._main_loop()
    # Nothing moves while the game is paused
    assert _state(g) == state
    assert len(pauses) >= 20

    assert not _press(monkeypatch, g, keys.PAUSE)
    assert not g.paused
    _continue(monkeypatch, g, 20)
    assert _state(g)[:-1] != state[:-1]

def test_sound_effect_busy(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    _install_pump(monkeypatch, g)
    monkeypatch.setattr(g.beeper, 'is_busy', lambda: True)
    state = _state(g)
    for i in range(20):
        assert not g._main_loop()
    # Nothing moves while a sound effect is playing
    assert _state(g) == state

    monkeypatch.setattr(g.beeper, 'is_busy', lambda: False)
    _continue(monkeypatch, g, 20)
    assert _state(g)[:-1] != state[:-1]

def test_save_and_load_keys(monkeypatch, capsys, tmp_path):
    g = _start_test(monkeypatch, capsys, tmp_path)
    skool = g.skool
    # Record the state of the game just after it's saved and just after it's
    # loaded (_press() runs the main loop once more after each key press)
    states = []
    for name in ('_save', '_load'):
        method = getattr(demo.game.Game, name)
        def recorded(game, fname, method=method):
            method(game, fname)
            states.append(_state(game)[:-1])
        monkeypatch.setattr(demo.game.Game, name, recorded)

    assert _sav_files(g) == []
    assert not _press(monkeypatch, g, keys.SAVE)
    assert len(_sav_files(g)) == 1
    assert len(states) == 1

    _continue(monkeypatch, g, 50)
    assert _state(g)[:-1] != states[0]
    assert not _press(monkeypatch, g, keys.LOAD)
    assert g.skool is not skool
    assert len(states) == 2
    assert states[1] == states[0]
    _continue(monkeypatch, g, 20)

def _set_up_mutables(d):
    """Set up Back to Skool Daze with every kind of mutable object in a
    non-default state: flip every door and window, fill every cup, unchain
    the bike, and flash every other shield and the safe."""
    skool = d.skool
    for barrier_id, barrier in list(skool.doors.items()) + list(skool.windows.items()):
        skool.move_door(barrier_id, not barrier.shut)
    for cup_id in skool.cups:
        skool.fill_cup(cup_id, 'WATER')
    skool.unchain_bike()
    for shield in skool.shields[::2]:
        shield.flash()
    skool.safe.flash()

@pytest.mark.parametrize('mode', [0, 1])
def test_save_and_restore_mutables(monkeypatch, capsys, tmp_path, mode):
    # Restoring a game rebuilds the play area images (the full-colour image in
    # graphics mode 0, or the ink and paper images in mode 1) and redraws the
    # mutable objects on them. The restored game is created without the
    # GraphicsMode setting, so it gets the graphics mode from the saved game.
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'btsd', None, 50, 50, _set_up_mutables,
                                        options=['--config', f'GraphicsMode,{mode}'])
    assert saved.screen.mode == restored.screen.mode == mode
    skool = restored.skool
    if mode == 0:
        assert skool.skool is not None and skool.ink is None and skool.paper is None
    else:
        assert skool.skool is None and skool.ink is not None and skool.paper is not None

    # The mutable objects are still in non-default states
    barriers = list(skool.doors.values()) + list(skool.windows.values())
    assert any(b.shut and not b.initially_shut for b in barriers)
    assert any(not b.shut and b.initially_shut for b in barriers)
    assert [cup.contents for cup in skool.cups.values()] == ['WATER'] * 2
    assert not skool.bike.chained
    assert [shield.flashing for shield in skool.shields] == [True, False] * 8
    assert skool.safe.flashing

def _play_area_image(g):
    """Return a hash of the image of the whole play area as it appears on
    screen (without the characters): the full-colour image in graphics mode
    0, or the ink image laid over the paper image in mode 1."""
    skool = g.skool
    if skool.skool:
        surface = skool.skool.surface
    else:
        surface = skool.paper.surface.copy()
        ink = skool.ink.surface.copy()
        ink.set_colorkey(g.screen.skool_colorkey)
        surface.blit(ink, (0, 0))
    return hashlib.md5(pygame.image.tostring(surface, 'RGB')).hexdigest()

def _run_in_graphics_mode(capsys, tmp_path, mode, ticks):
    """Run Back to Skool Daze headless in a graphics mode for a number of
    ticks, with Eric idle and the mutable objects set up by
    _set_up_mutables(). Return a list of tuples, one for each tick, each
    containing the state of the game (see _state(), but without the screen
    hash), whether the flashing shields and safe are in the inverse half of
    their flash cycle, a hash of the play area image (see
    _play_area_image()), and the screen contents (as RGB bytes)."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        ticks_seen = []
        main_loop = demo.game.Game._main_loop
        def recorded_main_loop(g):
            assert g.screen.mode == mode
            rv = main_loop(g)
            ticks_seen.append((_state(g)[:-1], g.skool.inverse, _play_area_image(g),
                               pygame.image.tostring(pygame.display.get_surface(), 'RGB')))
            return rv
        monkeypatch.setattr(demo.game.Game, '_main_loop', recorded_main_loop)
        run(monkeypatch, capsys, tmp_path, 'btsd', None, '', ticks, setup=_set_up_mutables,
            options=['--config', f'GraphicsMode,{mode}'])
    return ticks_seen

def test_graphics_mode_0(capsys, tmp_path):
    # Graphics mode 0 uses the full-colour skool and mutables images instead
    # of the separate ink and paper images that mode 1 uses to emulate the
    # Spectrum's colour attributes. Back to Skool Daze has every kind of
    # mutable object (shields, the safe, doors, windows, cups and the bike),
    # and _set_up_mutables() puts them all in non-default states.
    ticks = 100
    ticks0 = _run_in_graphics_mode(capsys, tmp_path, 0, ticks)
    ticks1 = _run_in_graphics_mode(capsys, tmp_path, 1, ticks)
    assert len(ticks0) == len(ticks1) == ticks

    size = pygame.display.get_surface().get_size()
    white = (255, 255, 255)
    num_diffs = 0
    for tick, ((state0, inverse0, image0, screen0), (state1, inverse1, image1, screen1)) in enumerate(zip(ticks0, ticks1), 1):
        # The game plays out in exactly the same way in both modes
        assert state0 == state1, f'Game states differ at tick {tick}'
        assert inverse0 == inverse1

        # The whole play area (including the parts that are off screen) looks
        # exactly the same in both modes
        assert image0 == image1, f'Play area images differ at tick {tick}'

        # The screens differ only where mode 0 shows white: in mode 1, white
        # areas of the sprites take on the paper colour of the skool behind
        # them
        if screen0 != screen1:
            num_diffs += 1
            # Paste the mode 0 screen (minus its white pixels) over the mode 1
            # screen; the result should be the mode 1 screen
            surface0 = pygame.image.fromstring(screen0, size, 'RGB')
            surface0.set_colorkey(white)
            surface1 = pygame.image.fromstring(screen1, size, 'RGB')
            surface1.blit(surface0, (0, 0))
            assert pygame.image.tostring(surface1, 'RGB') == screen1, f'Screens differ at tick {tick}'

    # Sanity checks: both halves of the flash cycle were seen, and the
    # graphics mode did make a difference to the screen
    assert {inverse for state, inverse, image, screen in ticks0} == {False, True}
    assert num_diffs > ticks // 2

def _record_icons(monkeypatch):
    """Replace pygame.display.set_icon() with a function that records the
    icons it's given (as (size, RGB bytes) pairs), and return the list of
    them."""
    icons = []
    monkeypatch.setattr(pygame.display, 'set_icon', lambda icon: icons.append(_image_data(icon)))
    return icons

def _image_data(surface):
    return surface.get_size(), pygame.image.tostring(surface, 'RGB')

def _load_icon(path):
    """Load an icon file as Screen.setup() does (which needs the display to
    have been set up), and return its size and RGB bytes."""
    return _image_data(pygame.image.load(path).convert())

def test_icon(monkeypatch, capsys, tmp_path):
    # The default icon file is 'icon.png' in the cwd, which is ~/.pyskool
    # when the game is played normally (see run.main())
    shutil.copy(os.path.join(user_dir, 'icon.png'), tmp_path)
    monkeypatch.chdir(tmp_path)
    icons = _record_icons(monkeypatch)
    g = _start(monkeypatch, capsys, tmp_path, 'sd', '', 1)
    assert g.screen.icon_fname == 'icon.png'
    assert icons == [_load_icon('icon.png')]
    assert icons[0][0] == (32, 32)

def test_no_icon(monkeypatch, capsys, tmp_path):
    # No icon is set if the icon file doesn't exist
    monkeypatch.chdir(tmp_path)
    icons = _record_icons(monkeypatch)
    g = _start(monkeypatch, capsys, tmp_path, 'sd', '', 1)
    assert not os.path.exists(g.screen.icon_fname)
    assert icons == []

def test_custom_icon(monkeypatch, capsys, tmp_path):
    # Make a 16x16 icon in a subdirectory, and put the default icon file in
    # the cwd too, to show that it's not used
    os.mkdir(tmp_path / 'icons')
    custom_icon = pygame.Surface((16, 16))
    custom_icon.fill((255, 0, 0))
    custom_icon.fill((0, 0, 255), pygame.Rect(4, 4, 8, 8))
    pygame.image.save(custom_icon, str(tmp_path / 'icons' / 'custom.png'))
    shutil.copy(os.path.join(user_dir, 'icon.png'), tmp_path)
    monkeypatch.chdir(tmp_path)
    icons = _record_icons(monkeypatch)
    g = _start(monkeypatch, capsys, tmp_path, 'sd', '', 1, options=['--config', 'Icon,icons/custom.png'])
    assert g.screen.icon_fname == 'icons/custom.png'
    assert icons == [_load_icon('icons/custom.png')]
    assert icons[0][0] == (16, 16)

def test_icon_after_rescale_and_load(monkeypatch, capsys, tmp_path):
    # The icon is set again whenever the screen is set up again: after a
    # change of scale and after a saved game is loaded
    shutil.copy(os.path.join(user_dir, 'icon.png'), tmp_path)
    monkeypatch.chdir(tmp_path)
    icons = _record_icons(monkeypatch)
    g = _start(monkeypatch, capsys, tmp_path, 'sd', '', 1)
    icon = _load_icon('icon.png')
    assert icons == [icon]
    assert not _press(monkeypatch, g, keys.MENU, *[keys.MENU_NEXT] * 3)
    assert g.menu.items[3][0] == demo.game.SCALE_UP
    assert not _press(monkeypatch, g, keys.MENU_EXEC, keys.MENU_EXIT)
    assert g.screen.scale == 2
    assert icons == [icon] * 2
    assert not _press(monkeypatch, g, keys.SAVE, keys.LOAD)
    assert icons == [icon] * 3

def test_mouse_inventory_overflow(monkeypatch, capsys, tmp_path):
    # In Back to Skool, the mouse inventory box has room for 8 mice. With more
    # than that, one mouse is drawn, followed by a counter (e.g. 'x9').
    g = _start_test(monkeypatch, capsys, tmp_path, 'bts')
    screen = g.screen
    eric = g.cast.eric
    mouse_width = g.skool.get_mouse_image().get_width()
    box_width, box_height = screen.scale_coords(screen.mouse_box_size)
    assert box_width == 8 * mouse_width
    box = pygame.Rect(screen.scale_coords(screen.mouse_box_coords), (box_width, box_height))

    def mouse_inventory(mice):
        eric.mice = mice
        eric.print_mouse_inventory()
        return pygame.display.get_surface().subsurface(box).copy()

    def slot(surface, index):
        return pygame.image.tostring(surface.subsurface((index * mouse_width, 0, mouse_width, box_height)), 'RGB')

    empty = mouse_inventory(0)
    one_mouse = mouse_inventory(1)
    assert slot(one_mouse, 0) != slot(empty, 0)

    # 8 mice fill the box, side by side
    eight_mice = mouse_inventory(8)
    assert all(slot(eight_mice, i) == slot(one_mouse, 0) for i in range(8))

    # 9 or more mice: one mouse and a counter
    for mice in (9, 12, 100):
        expected = one_mouse.copy()
        counter = screen.get_text(f'x{mice}', screen.mouse_box_ink, screen.inventory_key)
        expected.blit(counter, (mouse_width, (box_height - g.skool.get_mouse_image().get_height()) // 2))
        assert _image_data(mouse_inventory(mice)) == _image_data(expected), f'{mice} mice'
        assert _image_data(expected) != _image_data(one_mouse)

def _write_on_blackboards(d):
    """Write on every blackboard in the skool."""
    for room in d.skool.rooms.values():
        if room.blackboard:
            for char in 'HELLO WORLD':
                room.blackboard.write(char)

# In Skool Daze, during Rockitt-WhiteRoom-1, the teacher taking the class in
# the Reading Room wipes its blackboard (8 columns), from right to left, one
# column every 20 ticks from tick 853; at tick 968, 6 columns have been
# wiped. Nobody is speaking at that point (Einstein speaks from tick 872 to
# tick 964): speech bubbles aren't saved, so saving while someone is
# speaking makes the restored game differ.
MID_WIPE_LESSON = 'Rockitt-WhiteRoom-1'
MID_WIPE_TICK = 968
MID_WIPE_COLUMNS = [7, 6, 5, 4, 3, 2]

def _record_blackboard_restores(monkeypatch):
    """Make Blackboard.restore() record the columns wiped so far on each
    blackboard it restores, and return the list of them."""
    wiped = []
    restore = room.Blackboard.restore
    def recorded_restore(blackboard):
        wiped.append(list(blackboard.wiped_columns))
        restore(blackboard)
    monkeypatch.setattr(room.Blackboard, 'restore', recorded_restore)
    return wiped

def test_save_and_restore_mid_wipe(monkeypatch, capsys, tmp_path):
    # Save the game while a teacher is wiping a blackboard; restoring it must
    # leave the blackboard partly wiped, as it was
    wiped = _record_blackboard_restores(monkeypatch)
    saved, restored = _save_and_restore(monkeypatch, capsys, tmp_path, 'sd', None, MID_WIPE_TICK, 100,
                                        _write_on_blackboards, lesson=MID_WIPE_LESSON)
    # Only the Reading Room blackboard was partly wiped when the game was saved
    assert sorted(wiped) == [[], [], MID_WIPE_COLUMNS]
    # By now the teacher has finished wiping it
    assert not restored.skool.rooms['ReadingRoom'].blackboard.is_dirty()
    assert restored.skool.rooms['WhiteRoom'].blackboard.is_dirty()

def test_rescale_mid_wipe(monkeypatch, capsys, tmp_path):
    # Change the scale up and back down while a teacher is wiping a
    # blackboard; the play area should look exactly as it did before
    g = _start(monkeypatch, capsys, tmp_path, 'sd', '', MID_WIPE_TICK, _write_on_blackboards, MID_WIPE_LESSON)
    images = _skool_images(g.skool)
    wiped = _record_blackboard_restores(monkeypatch)
    assert not _press(monkeypatch, g, keys.MENU, *[keys.MENU_NEXT] * 3)
    assert g.menu.items[3][0] == demo.game.SCALE_UP
    assert not _press(monkeypatch, g, keys.MENU_EXEC, keys.MENU_NEXT, keys.MENU_EXEC)
    assert g.menu.items[4][0] == demo.game.SCALE_DOWN
    assert g.screen.scale == 1
    assert sorted(wiped) == [[], [], [], [], MID_WIPE_COLUMNS, MID_WIPE_COLUMNS]
    assert _skool_images(g.skool) == images
