"""Tests for the debug.log/error calls made by the pyskool modules."""

import gzip
import os
import pickle
import re
import sys
import warnings
from types import SimpleNamespace

import pytest

# Import pygame now (before pyskool does) to swallow the warnings it emits
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import pygame

PYSKOOL_HOME = os.environ.get('PYSKOOL_HOME')
if not PYSKOOL_HOME:
    pytest.exit('PYSKOOL_HOME is not set; aborting', 1)
if not os.path.isdir(PYSKOOL_HOME):
    pytest.exit(f'PYSKOOL_HOME={PYSKOOL_HOME}: directory not found', 1)
sys.path.insert(0, PYSKOOL_HOME)

from pyskool.ai import GoTo, GoToXY
from pyskool.animatorystates import WALK0
from pyskool.character import Character
from pyskool.graphics import Gallery
from pyskool.game import Game
from pyskool.location import Location
from pyskool.skool import Skool
from pyskool.sound import Beeper
from pyskool import game
from pyskool import keys

def _make_skool(config=None):
    # A Skool needs only the screen's graphics mode and a gallery that can
    # supply images; images aren't needed by these tests
    screen = SimpleNamespace(mode=1)
    gallery = SimpleNamespace(get_image=lambda image_id: None)
    return Skool(config or {}, screen, None, None, gallery)

def _make_character(skool, x, y, character_id='WACKER', name='MR WACKER'):
    # A Character's ordinary setup needs a Cast; GoTo needs only the skool,
    # the character's location and its animatory state
    character = Character(character_id, name)
    character.skool = skool
    character.x, character.y = x, y
    character.initialise_animatory_state(WALK0, 1)
    return character

def _run_command(command, character):
    command.character = character
    return command.execute()

def _make_game(**attrs):
    # Bypass Game.__init__ (which needs the ini files and images) and give
    # the game only the attributes that the method under test uses
    g = Game.__new__(Game)
    g.__dict__.update(attrs)
    return g

class _SavedSkool:
    # A stand-in for a Skool that can be pickled and then restored by
    # Game._load()
    def __init__(self, save_game_dir='save'):
        self.save_game_dir = save_game_dir
        self.save_game_compression = 9
        self.screen = SimpleNamespace(scale=1)
        self.beeper = Beeper(None, {})
        self.gallery = Gallery(None, 'original', 1, {})
        self.cast = SimpleNamespace(eric=SimpleNamespace(keyboard=None))

    def restore(self):
        pass

class _Keyboard:
    # A keyboard on which the given keys (e.g. keys.REVEAL) are pressed
    def __init__(self, *pressed):
        self.pressed = pressed

    def is_pressed(self, keys):
        return any(k is keys for k in self.pressed)

    def was_pressed(self, keys):
        return self.is_pressed(keys)

class _Flashable:
    # A stand-in for a shield or a safe
    def __init__(self):
        self.flashed = False

    def flash(self):
        self.flashed = True

def _cheat_skool(**attrs):
    # A stand-in for a Skool with no shields, inventory items, doors or
    # secrets, unless given in `attrs`
    skool = SimpleNamespace(
        shields=[],
        inventory_item_ids=[],
        doors={},
        windows={},
        rooms={},
        safe_combination=None,
        bike_combination=None,
        storeroom_combination=None,
        unflash=lambda thing: setattr(thing, 'flashed', False)
    )
    skool.__dict__.update(attrs)
    return skool

def _press_cheat_keys(g, *pressed):
    g.keyboard = _Keyboard(*pressed)
    g._check_cheat_keys()

@pytest.fixture
def mixer(monkeypatch):
    # A Beeper loads sound effects only if pygame.mixer is initialised; the
    # dummy audio driver lets it be initialised without a sound device
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')
    initialised = pygame.mixer.get_init() is not None
    if not initialised:
        pygame.mixer.init()
    yield
    if not initialised:
        pygame.mixer.quit()

def test_skool_next_staircase_when_home_floor_is_none(capsys):
    skool = _make_skool()
    skool.add_floor('Bottom', 0, 50, 17)

    assert skool.next_staircase(None, skool.floors['Bottom']) is None
    assert capsys.readouterr().err == 'DEBUG: Cannot determine next staircase when home floor is None\n'

def test_skool_next_staircase_when_dest_floor_is_none(capsys):
    skool = _make_skool()
    skool.add_floor('Bottom', 0, 50, 17)

    assert skool.next_staircase(skool.floors['Bottom'], None) is None
    assert capsys.readouterr().err == 'DEBUG: Cannot determine next staircase when destination floor is None\n'

def test_ai_goto_cannot_resolve_location_id(capsys):
    skool = _make_skool()
    skool.add_floor('Bottom', 0, 50, 17)
    wacker = _make_character(skool, 10, 17)

    assert _run_command(GoTo('Nowhere'), wacker) is None
    assert capsys.readouterr().err == "DEBUG: Cannot resolve location ID 'Nowhere' for MR WACKER\n"

def test_ai_goto_cannot_determine_next_staircase(capsys):
    # Mr Wacker is on a floor, directly below a destination that is not on a
    # floor, so there is no staircase that will take him there
    skool = _make_skool()
    skool.add_floor('Bottom', 0, 50, 17)
    wacker = _make_character(skool, 10, 17)

    assert _run_command(GoToXY(10, 10), wacker) is None
    assert capsys.readouterr().err.splitlines() == [
        'DEBUG: MR WACKER at 10, 17 going to 10, 10 has no destination floor',
        'DEBUG: Cannot determine next staircase when destination floor is None',
        'ERROR: Cannot determine next staircase for MR WACKER at (10,17) going to (10,10)'
    ]

def test_character_get_next_staircase_when_no_home_floor(capsys):
    skool = _make_skool()
    skool.add_floor('Bottom', 0, 50, 17)
    wacker = _make_character(skool, 10, 10)

    assert wacker.get_next_staircase(Location((20, 17))) is None
    assert capsys.readouterr().err.splitlines() == [
        'DEBUG: MR WACKER at 10, 10 has no home floor',
        'DEBUG: Cannot determine next staircase when home floor is None'
    ]

def test_character_get_next_staircase_when_no_destination_floor(capsys):
    skool = _make_skool()
    skool.add_floor('Bottom', 0, 50, 17)
    wacker = _make_character(skool, 10, 17)

    assert wacker.get_next_staircase(Location((20, 10))) is None
    assert capsys.readouterr().err.splitlines() == [
        'DEBUG: MR WACKER at 10, 17 going to 20, 10 has no destination floor',
        'DEBUG: Cannot determine next staircase when destination floor is None'
    ]

def test_character_get_next_chair_when_not_in_a_room(capsys):
    skool = _make_skool()
    wacker = _make_character(skool, 10, 17)

    assert wacker.get_next_chair(True, True) == (None, 1)
    assert capsys.readouterr().err == 'ERROR: Character WACKER (MR WACKER) at (10,17) cannot find a chair because self.room == None\n'

def test_graphics_gallery_image_file_not_found(capsys, tmp_path):
    images_dir = str(tmp_path)
    gallery = Gallery(images_dir, 'original', 1, {'SKOOL': 'skool/skool.png'})

    assert gallery.get_surface('SKOOL') is None
    image_file = os.path.join(images_dir, 'originalx1', 'skool', 'skool.png')
    assert capsys.readouterr().err == f"DEBUG: Unable to load image 'SKOOL' from {image_file}: file not found\n"

def test_sound_beeper_sound_file_not_found(capsys, tmp_path, mixer):
    sounds_dir = str(tmp_path)
    beeper = Beeper(sounds_dir, {})

    beeper.add_sound('BELL', 'common/bell')
    assert 'BELL' not in beeper.sounds
    base_path = os.path.join(sounds_dir, 'common', 'bell')
    assert capsys.readouterr().err == f"DEBUG: Unable to load sound effect 'BELL' from {base_path}{{,.wav,.ogg}}: file not found\n"

def test_sound_beeper_cannot_load_sound_file(capsys, tmp_path, mixer):
    sounds_dir = str(tmp_path)
    (tmp_path / 'common').mkdir()
    (tmp_path / 'common' / 'bell.wav').write_bytes(b'junk')
    beeper = Beeper(sounds_dir, {})

    beeper.add_sound('BELL', 'common/bell')
    assert 'BELL' not in beeper.sounds
    # The reason given after the path comes from SDL_mixer, and may vary
    # between versions
    path = os.path.join(sounds_dir, 'common', 'bell.wav')
    prefix = f"DEBUG: Unable to load sound effect 'BELL' from {path}: "
    err = capsys.readouterr().err
    assert err.startswith(prefix)
    assert err.endswith('\n')
    assert len(err) > len(prefix) + 1

def test_game_unable_to_restore_saved_game(capsys, monkeypatch, tmp_path):
    # Game.__init__ reads the main ini file and the game ini files before it
    # checks the saved game file; stop it when it goes on to build the
    # gallery for a new game
    class Stop(Exception):
        pass
    def gallery(*args):
        raise Stop
    monkeypatch.setattr(game, 'Gallery', gallery)
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')
    monkeypatch.chdir(tmp_path)
    ini_file = tmp_path / 'pyskool.ini'
    ini_file.write_text('')
    ini_dir = tmp_path / 'ini'
    ini_dir.mkdir()
    options = SimpleNamespace(config=None, scale=None, cheat=None, quick_start=None)
    sav_file = str(tmp_path / 'missing.sav')

    with pytest.raises(Stop):
        Game(str(ini_file), None, None, str(ini_dir), options, '0.0', sav_file)
    assert capsys.readouterr().err == f'DEBUG: Unable to restore from {sav_file}: file not found\n'

def test_game_key_id_not_recognised(capsys):
    g = _make_game()

    g._create_key_bindings([('LEFT', 'NOSUCHKEY')])
    assert keys.LEFT == [pygame.K_LEFT, pygame.K_o]
    assert capsys.readouterr().err == 'DEBUG: NOSUCHKEY: key ID not recognised\n'

def test_game_skool_saved(capsys, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    g = _make_game(skool=_SavedSkool())

    g._save('test.sav')
    sav_file = tmp_path / 'save' / 'test.sav'
    assert sav_file.is_file()
    assert capsys.readouterr().err == f'DEBUG: Skool saved to {sav_file}\n'

def test_game_skool_loaded(capsys, tmp_path):
    sav_file = str(tmp_path / 'test.sav')
    with gzip.open(sav_file, 'wb') as f:
        pickle.dump(_SavedSkool(), f)
    g = _make_game(screen=None, scale=1, images_dir=None, sounds_dir=None, menu_config={}, menus={})

    g._load(sav_file)
    assert isinstance(g.skool, _SavedSkool)
    # The time taken to load the game varies
    err = capsys.readouterr().err
    assert re.fullmatch(fr'DEBUG: Skool loaded from {re.escape(sav_file)} in \d+\.\d\ds\n', err), err

def test_game_cannot_load_games_when_no_save_game_dir(capsys, tmp_path):
    save_game_dir = str(tmp_path / 'save')
    g = _make_game(skool=_SavedSkool(save_game_dir))

    assert g._load_last() is None
    assert capsys.readouterr().err == f"DEBUG: Cannot load games from '{save_game_dir}': directory not found\n"

def test_game_no_saved_games_found(capsys, tmp_path):
    save_game_dir = tmp_path / 'save'
    save_game_dir.mkdir()
    (save_game_dir / 'notes.txt').write_text('')
    g = _make_game(skool=_SavedSkool(str(save_game_dir)))

    assert g._load_last() is None
    assert capsys.readouterr().err == f"DEBUG: No saved games found in '{save_game_dir}'\n"

def test_game_cheat_flash_most_shields(capsys):
    shields = [_Flashable() for i in range(3)]
    safe = _Flashable()
    safe.flashed = True
    g = _make_game(skool=_cheat_skool(shields=shields, safe=safe, shield_mode=3))

    _press_cheat_keys(g, keys.FLASH_MOST)
    assert [s.flashed for s in shields] == [False, True, True]
    assert not safe.flashed
    assert g.skool.shield_mode == 1
    assert capsys.readouterr().err == 'DEBUG: Flashed all but one shield; hit it and then open the safe\n'

def test_game_cheat_unflash_most_shields(capsys):
    shields = [_Flashable() for i in range(3)]
    for shield in shields:
        shield.flashed = True
    safe = _Flashable()
    g = _make_game(skool=_cheat_skool(shields=shields, safe=safe, shield_mode=2))

    _press_cheat_keys(g, keys.UNFLASH_MOST)
    assert [s.flashed for s in shields] == [True, False, False]
    assert safe.flashed
    assert g.skool.shield_mode == 3
    assert capsys.readouterr().err == 'DEBUG: Unflashed all but one shield; hit it to go up a year\n'

def test_game_cheat_disable_and_enable_lines_giving(capsys, monkeypatch):
    # Restore Character.give_lines after the test
    monkeypatch.setattr(Character, 'give_lines', Character.give_lines)
    g = _make_game(skool=_cheat_skool())

    give_lines = Character.give_lines
    _press_cheat_keys(g, keys.NO_LINES)
    assert Character.give_lines is Game._no_lines
    _press_cheat_keys(g, keys.NO_LINES)
    assert Character.give_lines is give_lines
    assert capsys.readouterr().err.splitlines() == [
        'DEBUG: Disabled lines-giving',
        'DEBUG: Enabled lines-giving'
    ]

def test_game_cheat_add_lines(capsys):
    added = []
    g = _make_game(skool=_cheat_skool(add_lines=added.append), cast=SimpleNamespace(lines_range=(7, 8)))

    _press_cheat_keys(g, keys.ADD_LINES)
    assert added == [700]
    assert capsys.readouterr().err == 'DEBUG: Added 700 lines\n'

def test_game_cheat_zero_lines(capsys):
    added = []
    skool = _cheat_skool(add_lines=added.append, scoreboard=SimpleNamespace(lines=1200))
    g = _make_game(skool=skool)

    _press_cheat_keys(g, keys.ZERO_LINES)
    assert added == [-1200]
    assert capsys.readouterr().err == 'DEBUG: Set lines total to zero\n'

def test_game_cheat_reveal_secrets(capsys):
    desks = [SimpleNamespace(x=x, contents=c) for x, c in ((60, None), (62, 'WATERPISTOL'))]
    rooms = {'Map': SimpleNamespace(name='MAP ROOM', desks=desks)}
    skool = _cheat_skool(rooms=rooms, safe_combination='WACK', bike_combination='1234', storeroom_combination='S7N2')
    characters = [
        SimpleNamespace(name='MR WACKER', special_answer=None),
        SimpleNamespace(name='MR ROCKITT', special_answer='1066')
    ]
    g = _make_game(skool=skool, cast=SimpleNamespace(character_list=characters))

    _press_cheat_keys(g, keys.REVEAL)
    assert capsys.readouterr().err.splitlines() == [
        'DEBUG: MAP ROOM x=62: WATERPISTOL',
        'DEBUG: MR ROCKITT: 1066',
        'DEBUG: Safe: WACK',
        'DEBUG: Bike: 1234',
        'DEBUG: Storeroom: S7N2'
    ]

def test_game_cheat_open_and_close_doors(capsys):
    moved = []
    skool = _cheat_skool(
        doors={'LeftStudyDoor': None},
        windows={'TopWindow': None},
        move_door=lambda door_id, shut: moved.append((door_id, shut))
    )
    g = _make_game(skool=skool)

    _press_cheat_keys(g, keys.OPEN_DOORS)
    _press_cheat_keys(g, keys.CLOSE_DOORS)
    assert moved == [('LeftStudyDoor', False), ('TopWindow', False), ('LeftStudyDoor', True), ('TopWindow', True)]
    assert capsys.readouterr().err.splitlines() == [
        'DEBUG: Opened all doors and windows',
        'DEBUG: Closed all doors and windows'
    ]

def test_game_took_screenshot(capsys, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    screenshots = []
    screen = SimpleNamespace(take_screenshot=screenshots.append)
    g = _make_game(skool=SimpleNamespace(screenshot_dir='screenshots'), screen=screen, screenshot=0)

    g._take_screenshot()
    assert len(screenshots) == 1
    img_path = screenshots[0]
    # The image file name is a timestamp followed by the screenshot number
    assert re.fullmatch(r'screenshots[/\\]\d{8}-\d{6}-000\.png', img_path), img_path
    assert capsys.readouterr().err == f'DEBUG: Took screenshot: {img_path}\n'
