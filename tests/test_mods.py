import os
import shutil

from pyskooltest import demo, run
from pyskool import ai, animal, character, eric, user_dir
from pyskool.animatorystates import ARM_UP, BENDING_OVER, CATAPULT0, CATAPULT1, HITTING0, HITTING1, RIDING_BIKE0, RIDING_BIKE1, WALK0
from pyskool.location import Location

def _mod_ini(tmp_path, game_dir, *mods):
    """Copy a game's ini files to a temporary directory, apply some mods to
    them, and return the directory. Each mod is a (filename, old, new) tuple,
    where 'old' is the text to replace (or None to append 'new')."""
    ini_dir = tmp_path / 'ini'
    shutil.copytree(os.path.join(user_dir, 'ini', game_dir), ini_dir)
    for filename, old, new in mods:
        path = ini_dir / filename
        text = path.read_text()
        if old is None:
            text += new
        else:
            assert old in text
            text = text.replace(old, new, 1)
        path.write_text(text)
    return ini_dir

def test_command_execute():
    # A subclass of Command that doesn't override execute() does nothing and
    # returns itself when executed
    class DoNothing(ai.Command):
        pass

    command = DoNothing()
    assert command.execute() is command

def test_hop_is_not_interruptible():
    # Hop is used only by frogs, and is always on top of MoveFrog (which is
    # also uninterruptible) on the command stack, so a command list never asks
    # whether it is interruptible; its phases can't be given in an ini file
    # either, so it can't be placed in a non-frog character's command list
    assert ai.Hop(()).is_interruptible() is False

def test_animal_is_not_frog():
    # Eric.catch_animal() asks whether an animal is a frog only after finding
    # that it's not a mouse, and every animal is either a mouse or a frog, so
    # Animal.is_frog() is never called; an animal that is neither a mouse nor
    # a frog is not a frog
    class Hedgehog(animal.Animal):
        pass

    hedgehog = Hedgehog('HEDGEHOG', 'Hedgehog', WALK0, (0, 0))
    assert hedgehog.is_mouse() is False
    assert hedgehog.is_frog() is False

def test_unused_animatory_state_checks():
    # Character.is_firing_catapult(), is_punching() and is_riding_bike() are
    # not used by the game, but are part of the API
    c = character.Character('BOY01', 'PERKINS')
    for state, firing_catapult, punching, riding_bike in (
            (WALK0, False, False, False),
            (CATAPULT0, False, False, False),
            (CATAPULT1, True, False, False),
            (HITTING0, False, False, False),
            (HITTING1, False, True, False),
            (RIDING_BIKE0, False, False, True),
            (RIDING_BIKE1, False, False, True)
    ):
        c.animatory_state = state
        assert c.is_firing_catapult() is firing_catapult
        assert c.is_punching() is punching
        assert c.is_riding_bike() is riding_bike

def test_location_str():
    # Location.__str__() is not used by the game, but is part of the API
    loc = Location((43, 17))
    assert str(loc) == '(43, 17)'

def test_find_seat_outside_rooms(monkeypatch, capsys, tmp_path):
    # In Playtime-4, give BOY01 a command list that sends him out of the
    # dinner hall to a spot on the bottom floor that is in no room, and then
    # makes him look for a seat; FindSeat can find no chair there, and so
    # terminates
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini', None, '\n[CommandList FindSeatOutside]\nGoToXY, 60, 17\nFindSeat\nGoToRandomLocation\nWalkAround, 10\nRestart\n'),
        ('lessons.ini', '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, BigWindow\n',
         '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, FindSeatOutside\n')
    )
    executions = []
    def setup(d):
        execute = ai.FindSeat.execute
        def recorded(command):
            val = execute(command)
            c = command.character
            executions.append((d.tick, c.character_id, (c.x, c.y), c.room, val is command))
            return val
        monkeypatch.setattr(ai.FindSeat, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 200, setup=setup, options=['--ini-dir', str(ini_dir)])

    # FindSeat was executed once, by BOY01 at (60,17), which is in no room,
    # and terminated immediately
    assert executions == [(142, 'BOY01', (60, 17), None, True)]

def test_find_seat_in_room_without_chairs(monkeypatch, capsys, tmp_path):
    # In Playtime-4, give BOY01 a command list that sends him to a spot in the
    # dinner hall (which has no chairs), and then makes him look for a seat;
    # FindSeat can find no chair there, and so terminates
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini', None, '\n[CommandList FindSeatInDinnerHall]\nGoToXY, 42, 17\nFindSeat\nGoToRandomLocation\nWalkAround, 10\nRestart\n'),
        ('lessons.ini', '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, BigWindow\n',
         '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, FindSeatInDinnerHall\n')
    )
    executions = []
    def setup(d):
        execute = ai.FindSeat.execute
        def recorded(command):
            val = execute(command)
            c = command.character
            room = c.room
            executions.append((d.tick, c.character_id, (c.x, c.y), room.room_id if room else None, room.chairs if room else None, val is command))
            return val
        monkeypatch.setattr(ai.FindSeat, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 200, setup=setup, options=['--ini-dir', str(ini_dir)])

    # FindSeat was executed once, by BOY01 at (42,17), which is in the dinner
    # hall, and terminated immediately
    assert executions == [(9, 'BOY01', (42, 17), 'DinnerHall', [], True)]

def test_walk_around_on_stairs(monkeypatch, capsys, tmp_path):
    # In Playtime-4 (repeated, and shortened to 340 ticks), give BOY01 a
    # command list that begins with WalkAround and then sends him up to the
    # top floor; the bell rings while he's on the stairs, so WalkAround (at
    # the start of his restarted command list) makes him finish going up them
    # first
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini', None, '\n[CommandList WalkAroundFirst]\nWalkAround, 1\nGoToXY, 60, 3\nGoToRandomLocation\nWalkAround, 10\nRestart\n'),
        ('lessons.ini', '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, BigWindow\n',
         '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, WalkAroundFirst\n')
    )
    executions = []
    def setup(d):
        execute = ai.WalkAround.execute
        def recorded(command):
            c = command.character
            on_stairs, location = c.on_stairs(), (c.x, c.y)
            val = execute(command)
            if on_stairs:
                executions.append((d.tick, c.character_id, location, val))
            return val
        monkeypatch.setattr(ai.WalkAround, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 400, setup=setup, options=['--ini-dir', str(ini_dir), '--config', 'LessonLength,340'])

    # The bell rang at tick 342, with BOY01 at (73,13), on the stairs; then
    # WalkAround made him take three more steps up them
    assert executions == [
        (346, 'BOY01', (74, 13), None),
        (352, 'BOY01', (75, 12), None),
        (358, 'BOY01', (76, 11), None)
    ]

def test_grass_and_answer_questions_when_not_seated(monkeypatch, capsys, tmp_path):
    # In Withit-MapRoom-1, remove FindSeat from Einstein's command list;
    # GrassAndAnswerQuestions then finds that he's not sitting on a chair, and
    # makes him find a seat
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini',
         '[CommandList MapRoom-Swot]\nGoTo, MapRoom:1\nMoveAboutUntil, MapRoomReady\nFindSeat\nSignal, SwotReadyForLesson\nGrassAndAnswerQuestions\n',
         '[CommandList MapRoom-Swot]\nGoTo, MapRoom:1\nMoveAboutUntil, MapRoomReady\nSignal, SwotReadyForLesson\nGrassAndAnswerQuestions\n')
    )
    executions = []
    def setup(d):
        execute = ai.GrassAndAnswerQuestions.execute
        def recorded(command):
            c = command.character
            val = execute(command)
            if isinstance(val, ai.FindSeat):
                executions.append((d.tick, c.character_id, (c.x, c.y), val.go_to_back, val.move_along))
            return val
        monkeypatch.setattr(ai.GrassAndAnswerQuestions, 'execute', recorded)
    d, _ = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-MapRoom-1', '', 1500, setup=setup, options=['--ini-dir', str(ini_dir)])

    # GrassAndAnswerQuestions made Einstein find a seat (without going to the
    # back seat or moving along) just once, and he's now sitting on a chair
    assert executions == [(1157, 'SWOT', (67, 3), False, False)]
    swot = d.skool.cast.get('SWOT')
    assert swot.is_sitting_on_chair()

def test_write_on_board_without_blackboard(monkeypatch, capsys, tmp_path):
    # In Playtime-4, insert a WriteOnBoard command at the start of Boy
    # Wander's command list, before the GoTo command that sends him to a
    # blackboard; there is no blackboard where he is, so WriteOnBoard
    # terminates without writing anything
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini',
         '[CommandList WriteOnBoards-Tearaway]\nGoTo, ExamRoomBlackboard\n',
         '[CommandList WriteOnBoards-Tearaway]\nWriteOnBoard, HELLO\nGoTo, ExamRoomBlackboard\n')
    )
    executions = []
    def setup(d):
        execute = ai.WriteOnBoard.execute
        def recorded(command):
            c = command.character
            val = execute(command)
            executions.append((d.tick, c.character_id, (c.x, c.y), c.room and c.room.room_id, command.index, val is command))
            return val
        monkeypatch.setattr(ai.WriteOnBoard, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 10, setup=setup, options=['--ini-dir', str(ini_dir)])

    # WriteOnBoard was executed once, by Boy Wander at (25,17), which is in no
    # room, and terminated before writing the first letter
    assert executions == [(2, 'TEARAWAY', (25, 17), None, 1, True)]

def test_say_nothing(monkeypatch, capsys, tmp_path):
    # In Playtime-4, give BOY01 a command list that begins with a Say command
    # with an empty argument; Say terminates without making him say anything
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini', None, "\n[CommandList SayNothing]\nSay, ''\nGoToRandomLocation\nWalkAround, 10\nRestart\n"),
        ('lessons.ini', '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, BigWindow\n',
         '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, SayNothing\n')
    )
    executions = []
    def setup(d):
        execute = ai.Say.execute
        def recorded(command):
            c = command.character
            val = execute(command)
            executions.append((d.tick, c.character_id, command.words, c.bubble, val is command))
            return val
        monkeypatch.setattr(ai.Say, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 10, setup=setup, options=['--ini-dir', str(ini_dir)])

    # Say was executed once, by BOY01, and terminated without giving him a
    # speech bubble
    assert executions == [(3, 'BOY01', '', None, True)]

def test_fire_water_pistol_is_not_interruptible(monkeypatch, capsys, tmp_path):
    # In Playtime-1, give Boy Wander a water pistol (borrowing Eric's sprite
    # for aiming it) and a command list that begins with FireWaterPistol;
    # while that command is on his command stack, the command list checks
    # whether it is interruptible
    ini_dir = _mod_ini(tmp_path, 'back_to_skool',
        ('sprites.ini', 'CATAPULT1, 27\n\n[SpriteGroup WACKER]', 'CATAPULT1, 27\nWATERPISTOL, 14\n\n[SpriteGroup WACKER]'),
        ('sprites.ini', 'HERO, HeroWater, WATER, Water, Water\n', 'HERO, HeroWater, WATER, Water, Water\nTEARAWAY, TearawayWater, WATER, Water, Water\n'),
        ('command_lists.ini', None, '\n[CommandList FireWaterPistol-Tearaway]\nFireWaterPistol\nGoToRandomLocation\nWalkAround, 10\nRestart\n'),
        # The first occurrence of this line is in Playtime-1
        ('lessons.ini', 'TEARAWAY, WriteOnBoardsInBoysSkool-Tearaway\n', 'TEARAWAY, FireWaterPistol-Tearaway\n')
    )
    checks = []
    def setup(d):
        is_interruptible = ai.FireWaterPistol.is_interruptible
        def recorded(command):
            val = is_interruptible(command)
            c = command.character
            checks.append((d.tick, c.character_id, command.commands[command.index], c.water.is_visible(), val))
            return val
        monkeypatch.setattr(ai.FireWaterPistol, 'is_interruptible', recorded)
    run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', '', 30, setup=setup, options=['--ini-dir', str(ini_dir)])

    # FireWaterPistol was found to be uninterruptible before each of its
    # remaining steps after aiming, and Boy Wander fired the water pistol
    assert checks == [
        (5, 'TEARAWAY', 'fire', False, False),
        (8, 'TEARAWAY', 'lower', True, False),
        (11, 'TEARAWAY', 'done', True, False)
    ]

def test_drop_stinkbomb_is_not_interruptible(monkeypatch, capsys, tmp_path):
    # In Playtime-1, give Boy Wander some stinkbombs and a command list that
    # begins with DropStinkbomb; while that command is on his command stack,
    # the command list checks whether it is interruptible
    ini_dir = _mod_ini(tmp_path, 'back_to_skool',
        ('sprites.ini', 'HERO, HeroStinkbomb, STINKBOMB, Stinkbomb, Stinkbomb, 3\n', 'HERO, HeroStinkbomb, STINKBOMB, Stinkbomb, Stinkbomb, 3\nTEARAWAY, TearawayStinkbomb, STINKBOMB, Stinkbomb, Stinkbomb, 3\n'),
        ('command_lists.ini', None, '\n[CommandList DropStinkbomb-Tearaway]\nDropStinkbomb\nGoToRandomLocation\nWalkAround, 10\nRestart\n'),
        # The first occurrence of this line is in Playtime-1
        ('lessons.ini', 'TEARAWAY, WriteOnBoardsInBoysSkool-Tearaway\n', 'TEARAWAY, DropStinkbomb-Tearaway\n')
    )
    checks = []
    def setup(d):
        is_interruptible = ai.DropStinkbomb.is_interruptible
        def recorded(command):
            val = is_interruptible(command)
            c = command.character
            checks.append((d.tick, c.character_id, command.commands[command.index], c.stinkbomb.is_visible(), val))
            return val
        monkeypatch.setattr(ai.DropStinkbomb, 'is_interruptible', recorded)
    run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', '', 30, setup=setup, options=['--ini-dir', str(ini_dir)])

    # DropStinkbomb was found to be uninterruptible before each of its
    # remaining steps after raising his arm, and Boy Wander dropped a
    # stinkbomb
    assert checks == [
        (5, 'TEARAWAY', 'drop', False, False),
        (8, 'TEARAWAY', 'lower', True, False),
        (11, 'TEARAWAY', 'done', True, False)
    ]

def test_write_on_board_unless_outside_rooms(monkeypatch, capsys, tmp_path):
    # In Playtime-4, insert a WriteOnBoardUnless command at the start of Boy
    # Wander's command list, before the GoTo command that sends him to a
    # blackboard; he's not in a room, so WriteOnBoardUnless terminates
    # without making him write on a blackboard
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini',
         '[CommandList WriteOnBoards-Tearaway]\nGoTo, ExamRoomBlackboard\n',
         '[CommandList WriteOnBoards-Tearaway]\nWriteOnBoardUnless, EndOfLesson\nGoTo, ExamRoomBlackboard\n')
    )
    executions = []
    def setup(d):
        execute = ai.WriteOnBoardUnless.execute
        def recorded(command):
            c = command.character
            val = execute(command)
            executions.append((d.tick, c.character_id, (c.x, c.y), c.room, command.wrote_on_board, val is command))
            return val
        monkeypatch.setattr(ai.WriteOnBoardUnless, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 10, setup=setup, options=['--ini-dir', str(ini_dir)])

    # WriteOnBoardUnless was executed once, by Boy Wander at (25,17), which is
    # in no room, and terminated without making him write on a blackboard
    assert executions == [(2, 'TEARAWAY', (25, 17), None, False, True)]

def test_write_on_board_unless_no_blackboard(monkeypatch, capsys, tmp_path):
    # In Playtime-4, insert commands at the start of Boy Wander's command list
    # that send him to the dinner hall (which has no blackboard) and then make
    # him write on the blackboard there; WriteOnBoard terminates without
    # writing anything, so the blackboard is not dirty when WriteOnBoardUnless
    # is executed again, and it then terminates because he has already
    # (supposedly) written on the board
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini',
         '[CommandList WriteOnBoards-Tearaway]\nGoTo, ExamRoomBlackboard\n',
         '[CommandList WriteOnBoards-Tearaway]\nGoToXY, 40, 17\nWriteOnBoardUnless, EndOfLesson\nGoTo, ExamRoomBlackboard\n')
    )
    executions = []
    def setup(d):
        execute = ai.WriteOnBoardUnless.execute
        def recorded(command):
            c = command.character
            val = execute(command)
            executions.append((d.tick, c.character_id, (c.x, c.y), c.room.room_id, type(val).__name__, val is command))
            return val
        monkeypatch.setattr(ai.WriteOnBoardUnless, 'execute', recorded)
    run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 200, setup=setup, options=['--ini-dir', str(ini_dir)])

    # WriteOnBoardUnless was executed twice, by Boy Wander at (40,17) in the
    # dinner hall: first it returned a WriteOnBoard command, and then it
    # terminated
    assert executions == [
        (95, 'TEARAWAY', (40, 17), 'DinnerHall', 'WriteOnBoard', False),
        (95, 'TEARAWAY', (40, 17), 'DinnerHall', 'WriteOnBoardUnless', True)
    ]

def test_release_mice_without_mice(monkeypatch, capsys, tmp_path):
    # In Playtime-1, remove the mouse from the game, give Eric some mice
    # anyway (with the GIVE_ALL cheat key), and make him release them; no mice
    # are released, because there is no mouse to clone
    ini_dir = _mod_ini(tmp_path, 'back_to_skool',
        ('sprites.ini', 'MOUSE, MOUSE, RUN, (17, 3), Mouse, (1, 3)\n', '')
    )
    inputs = """
        1 GIVE_ALL
        10 RELEASE_MICE
    """
    releases = []
    def setup(d):
        cast = d.skool.cast
        release_mice = type(cast).release_mice
        def recorded(c, num_mice, x, y):
            val = release_mice(c, num_mice, x, y)
            releases.append((d.tick, num_mice, c.first_mouse, len(c.animals)))
            return val
        monkeypatch.setattr(type(cast), 'release_mice', recorded)
    d, _ = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 30, setup=setup, options=['--ini-dir', str(ini_dir), '--config', 'Cheat,1'])

    # Eric released five of his eight mice at tick 12, but none appeared (the
    # frog is still the only animal in the game)
    assert releases == [(12, 5, None, 1)]
    assert d.eric.mice == 3
    assert [a.character_id for a in d.skool.cast.animals] == ['FROG']

def _run_without_bend_over_hand_xy(monkeypatch, capsys, tmp_path, inputs):
    """Run Back to Skool's Playtime-1 for 30 ticks in cheat mode with the
    bendOverHandXY value removed from the [Eric] section, and with the given
    inputs. Return the Demo object and a list of the ticks at which Eric looked
    for an animal at his hand or released mice."""
    ini_dir = _mod_ini(tmp_path, 'back_to_skool',
        ('sprites.ini', 'BFPR, (0, 3)\n', 'BFPR\n')
    )
    calls = []
    def setup(d):
        cast = d.skool.cast
        assert d.eric.bend_over_hand_xy is None
        def recorded(c, *args):
            calls.append(d.tick)
        monkeypatch.setattr(type(cast), 'get_animal', recorded)
        monkeypatch.setattr(type(cast), 'release_mice', recorded)
    d, _ = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 30, setup=setup, options=['--ini-dir', str(ini_dir), '--config', 'Cheat,1'])
    return d, calls

def test_catch_without_bend_over_hand_xy(monkeypatch, capsys, tmp_path):
    # Without the bendOverHandXY value, Eric can still bend over to catch an
    # animal, but he doesn't look for one, and he catches nothing
    inputs = """
        10 CATCH
    """
    bends = []
    catch_animal = eric.Eric.catch_animal
    def recorded(e):
        bends.append((e.animatory_state, e.mice, set(e.inventory)))
        return catch_animal(e)
    monkeypatch.setattr(eric.Eric, 'catch_animal', recorded)
    d, calls = _run_without_bend_over_hand_xy(monkeypatch, capsys, tmp_path, inputs)
    assert bends == [(BENDING_OVER, 0, set())]
    assert calls == []
    assert d.eric.mice == 0
    assert d.eric.inventory == set()
    assert d.eric.animatory_state != BENDING_OVER

def test_release_mice_without_bend_over_hand_xy(monkeypatch, capsys, tmp_path):
    # Without the bendOverHandXY value, Eric can still bend over to release
    # mice (given some with the GIVE_ALL cheat key), but he releases none
    inputs = """
        1 GIVE_ALL
        10 RELEASE_MICE
    """
    bends = []
    release_mice = eric.Eric.release_mice
    def recorded(e):
        bends.append((e.animatory_state, e.mice))
        return release_mice(e)
    monkeypatch.setattr(eric.Eric, 'release_mice', recorded)
    d, calls = _run_without_bend_over_hand_xy(monkeypatch, capsys, tmp_path, inputs)
    assert bends == [(BENDING_OVER, 8)]
    assert calls == []
    assert d.eric.mice == 8
    assert d.eric.animatory_state != BENDING_OVER

def test_walk_from_non_walking_state(monkeypatch, capsys, tmp_path):
    # In Playtime-4, make Eric start with his arm raised (ARM_UP, which is not
    # one of his walking states), and make him walk left; he steps straight
    # into WALK0
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('sprites.ini', 'HERO, ERIC, ERIC, WALK0,', 'HERO, ERIC, ERIC, ARM_UP,')
    )
    inputs = """
        0 LEFT 3
    """
    indexes = []
    states = []
    def setup(d):
        get_walk_state_index = character.Character.get_walk_state_index
        def recorded(c):
            index = get_walk_state_index(c)
            if index < 0:
                indexes.append((d.tick, c.name, c.animatory_state))
            return index
        monkeypatch.setattr(character.Character, 'get_walk_state_index', recorded)
        states.append((d.eric.x, d.eric.animatory_state))
    d, _ = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 10, setup=setup, options=['--ini-dir', str(ini_dir)])

    # At tick 3, Eric.move() and then Character.walk() found Eric in ARM_UP
    # (and so got -1 as his walk state index), and he stepped from (48,17) to
    # (47,17) and into WALK0, where he stayed after LEFT was released
    assert states == [(48, ARM_UP)]
    assert indexes == [(3, 'ERIC', ARM_UP), (3, 'ERIC', ARM_UP)]
    assert (d.eric.x, d.eric.y, d.eric.animatory_state) == (47, 17, WALK0)

def test_go_to_random_location_without_random_locations(monkeypatch, capsys, tmp_path):
    # In Playtime-5, remove BOY01's random locations; GoToRandomLocation (at
    # the start of his command list) then chooses his current location as the
    # destination
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('config.ini', 'BOY01, (36, 3), (93, 3), (93, 17), (8, 17)\n', '')
    )
    destinations = []
    def setup(d):
        boy = d.skool.cast.get('BOY01')
        get_random_destination = boy.get_random_destination
        def recorded():
            dest = get_random_destination()
            destinations.append((d.tick, (boy.x, boy.y), dest))
            return dest
        boy.get_random_destination = recorded
    d, _ = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-5', '', 200, setup=setup, options=['--ini-dir', str(ini_dir)])

    # GoToRandomLocation chose BOY01's location, (43,17), as his destination
    assert d.skool.cast.get('BOY01').random_locations == ()
    assert destinations == [(3, (43, 17), (43, 17))]

def test_go_to_random_location_with_one_random_location(monkeypatch, capsys, tmp_path):
    # In Playtime-5, give BOY01 only one random location; GoToRandomLocation
    # (at the start of his command list) then chooses that location as the
    # destination
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('config.ini', 'BOY01, (36, 3), (93, 3), (93, 17), (8, 17)\n', 'BOY01, (8, 17)\n')
    )
    destinations = []
    def setup(d):
        boy = d.skool.cast.get('BOY01')
        get_random_destination = boy.get_random_destination
        def recorded():
            dest = get_random_destination()
            destinations.append((d.tick, (boy.x, boy.y), dest))
            return dest
        boy.get_random_destination = recorded
    d, _ = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-5', '', 200, setup=setup, options=['--ini-dir', str(ini_dir)])

    # GoToRandomLocation chose BOY01's only random location, (8,17), as his
    # destination
    assert d.skool.cast.get('BOY01').random_locations == [(8, 17)]
    assert destinations == [(3, (43, 17), (8, 17))]

def test_sit_on_stairs(monkeypatch, capsys, tmp_path):
    # In Playtime-4, give BOY01 a command list that sends him to the bottom
    # of the staircase up to the exam room, takes him one step up it, and
    # then makes him sit for assembly where he stands (facing down the
    # stairs)
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini', None, '\n[CommandList SitOnStairs]\nGoToXY, 70, 17\nGoTowardsXY, 77, 10\nSitForAssembly, AssemblyFinished, -1, (0, 0)\n'),
        ('lessons.ini', '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, BigWindow\n',
         '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, SitOnStairs\n')
    )
    checks = []
    def setup(d):
        can_sit_on_stairs = character.Character.can_sit_on_stairs
        def recorded(c):
            val = can_sit_on_stairs(c)
            checks.append((d.tick, c.character_id, (c.x, c.y), val))
            return val
        monkeypatch.setattr(character.Character, 'can_sit_on_stairs', recorded)
    d, _ = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 300, setup=setup, options=['--ini-dir', str(ini_dir)])

    # BOY01 was found to be able to sit on the stairs at (71,16), and is now
    # sitting there, facing down the stairs
    assert checks == [(257, 'BOY01', (71, 16), True)]
    boy = d.skool.cast.get('BOY01')
    assert ((boy.x, boy.y), boy.direction) == ((71, 16), -1)
    assert boy.is_sitting_on_stairs()

def test_fall_to_floor(monkeypatch, capsys, tmp_path):
    # In Playtime-4, give BOY01 a command list that begins with FallToFloor;
    # he's already on the floor, so he sits down there straight away (and
    # then stays there, because Character.get_up() can't restore his previous
    # animatory state, which was never saved)
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini', None, '\n[CommandList FallToFloor]\nFallToFloor\nSitStill\n'),
        ('lessons.ini', '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, BigWindow\n',
         '[Lesson Playtime-4 PLAYTIME]\n; characterId, commandListID\nBOY01, FallToFloor\n')
    )
    falls = []
    def setup(d):
        fall_to_floor = character.Character.fall_to_floor
        def recorded(c):
            fall_to_floor(c)
            falls.append((d.tick, c.character_id, (c.x, c.y), c.walk_delay))
        monkeypatch.setattr(character.Character, 'fall_to_floor', recorded)
    d, _ = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', '', 10, setup=setup, options=['--ini-dir', str(ini_dir)])

    # BOY01 fell to the floor at (43,17) at tick 3, and is still sitting there
    assert falls == [(3, 'BOY01', (43, 17), 10)]
    boy = d.skool.cast.get('BOY01')
    assert (boy.x, boy.y) == (43, 17)
    assert boy.is_sitting_on_floor()

def test_fall_off_plant(monkeypatch, capsys, tmp_path):
    # In Playtime-1, add a plant whose head starts at (40,10) on the left
    # middle floor, and give BOY01 a command list that makes him stand still
    # there; when he arrives, make the plant grow (as if Eric had watered it),
    # which lifts him two places up, and then die, which makes him fall back
    # down to the floor
    ini_dir = _mod_ini(tmp_path, 'back_to_skool',
        ('sprites.ini', 'RightGatePlant, PLANT, 135, 17, Plant\n', 'RightGatePlant, PLANT, 135, 17, Plant\nTestPlant, PLANT, 40, 11, Plant\n'),
        ('command_lists.ini', None, '\n[CommandList StandOnPlant]\nGoToXY, 40, 10\nSitStill\n'),
        ('lessons.ini', 'GIRL07, PlaytimeWalkabout-Boy/Girl\nBOY01, RevisionLibrary-Boy\n',
         'GIRL07, PlaytimeWalkabout-Boy/Girl\nBOY01, StandOnPlant\n')
    )
    events = []
    def setup(d):
        cast = d.skool.cast
        boy = cast.get('BOY01')
        plant = [p for p in cast.plants if p.character_id == 'TestPlant'][0]
        grow_execute = ai.Grow.execute
        def grow(command):
            if command.character is plant and not plant.growing and events == [] and (boy.x, boy.y) == (40, 10):
                plant.grow()
                events.append((d.tick, 'grow', (boy.x, boy.y)))
            return grow_execute(command)
        monkeypatch.setattr(ai.Grow, 'execute', grow)
        for name in ('appear', 'finish_growing', 'die'):
            method = getattr(type(plant), name)
            def recorded(p, name=name, method=method):
                method(p)
                if p is plant:
                    events.append((d.tick, name, (boy.x, boy.y)))
            monkeypatch.setattr(type(plant), name, recorded)
        fall_off_plant = character.Character.fall_off_plant
        def recorded_fall_off_plant(c):
            fall_off_plant(c)
            events.append((d.tick, 'fall_off_plant', c.character_id, (c.x, c.y), type(c.command_list.stack[-1]).__name__))
        monkeypatch.setattr(character.Character, 'fall_off_plant', recorded_fall_off_plant)
        fall_to_floor = character.Character.fall_to_floor
        def recorded_fall_to_floor(c):
            fall_to_floor(c)
            events.append((d.tick, 'fall_to_floor', c.character_id, (c.x, c.y)))
        monkeypatch.setattr(character.Character, 'fall_to_floor', recorded_fall_to_floor)
        # Standing on the plant or falling from it is not being lost
        is_lost = demo.Demo.is_lost
        def is_lost_off_plant(demo_obj, c):
            stack = c.command_list.stack
            if c is boy and (cast.plant(c) or (stack and isinstance(stack[-1], ai.FallToFloor))):
                return False
            return is_lost(demo_obj, c)
        monkeypatch.setattr(demo.Demo, 'is_lost', is_lost_off_plant)
    d, _ = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', '', 400, setup=setup, options=['--ini-dir', str(ini_dir)])

    # BOY01 reached (40,10) at tick 307, and the plant started growing; it
    # lifted him to (40,9) and then (40,8), and when it died, he fell off it
    # (with FallToFloor at the top of his command stack), landed at (40,10)
    # and sat on the floor
    assert events == [
        (307, 'grow', (40, 10)),
        (340, 'appear', (40, 9)),
        (361, 'finish_growing', (40, 8)),
        (382, 'fall_off_plant', 'BOY01', (40, 8), 'FallToFloor'),
        (382, 'die', (40, 8)),
        (393, 'fall_to_floor', 'BOY01', (40, 10))
    ]
    boy = d.skool.cast.get('BOY01')
    assert (boy.x, boy.y) == (40, 10)
    assert boy.is_sitting_on_floor()
    assert [type(c).__name__ for c in boy.command_list.stack] == ['SitStill']

def test_sit_when_sitting(monkeypatch, capsys, tmp_path):
    # In Withit-MapRoom-1, add a second FindSeat command to BOY01's command
    # list; after the first FindSeat has sat him in the back seat of the
    # reading room, the second one finds him beside that seat and makes him sit
    # again, which makes him stand up
    ini_dir = _mod_ini(tmp_path, 'skool_daze',
        ('command_lists.ini',
         '[CommandList ReadingRoom-Boy]\nGoTo, ReadingRoom:1\nMoveAboutUntil, ReadingRoomReady\nFindSeat\nSitStill\n',
         '[CommandList ReadingRoom-Boy]\nGoTo, ReadingRoom:1\nMoveAboutUntil, ReadingRoomReady\nFindSeat\nFindSeat\nSitStill\n')
    )
    sits = []
    def setup(d):
        boy = d.skool.cast.get('BOY01')
        sit = boy.sit
        def recorded():
            was_sitting = boy.is_sitting()
            val = sit()
            sits.append((d.tick, (boy.x, boy.y), was_sitting, boy.animatory_state, val))
            return val
        boy.sit = recorded
    run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-MapRoom-1', '', 1000, setup=setup, options=['--ini-dir', str(ini_dir)])

    # BOY01 sat down in the back seat at (56,3), and then (on the same tick)
    # stood up again, resuming the animatory state he was in before he sat
    # down
    assert sits == [
        (801, (56, 3), False, 'SITTING_ON_CHAIR', True),
        (801, (56, 3), True, 'WALK2', True)
    ]

def test_assembly_message_with_undefined_word_group(monkeypatch, capsys, tmp_path):
    # In Assembly, make the assembly message template refer to a word group
    # that isn't defined ($OBJECT); the group's name is used in its place
    ini_dir = _mod_ini(tmp_path, 'back_to_skool',
        ('messages.ini', 'MESSAGE, YOU\'RE ALL IN DETENTION UNTIL I FIND OUT WHO $VERB THE $NOUN\n',
         'MESSAGE, YOU\'RE ALL IN DETENTION UNTIL I FIND OUT WHO $VERB THE $OBJECT\n')
    )
    messages = []
    def setup(d):
        generator = d.skool.assembly_message_generator
        generate_message = generator.generate_message
        def recorded():
            message = generate_message()
            messages.append((d.tick, message))
            return message
        generator.generate_message = recorded
    run(monkeypatch, capsys, tmp_path, 'bts', 'Assembly', '', 1000, setup=setup, options=['--ini-dir', str(ini_dir)])

    # Mr Wacker's assembly message contained 'OBJECT' in place of a noun
    assert messages == [(788, "YOU'RE ALL IN DETENTION UNTIL I FIND OUT WHO KIDNAPPED THE OBJECT")]
