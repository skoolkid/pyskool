import os

from pyskooltest import PYSKOOL_HOME, check_assets, demo

REPLAYS_DIR = os.path.join(PYSKOOL_HOME, 'replays')

def _run_replay(monkeypatch, game, replay, ticks):
    """Run a replay headless and return the Demo object, the shield mode
    changes as (tick, mode) pairs, the ticks at which Eric went up a year, and
    the game endings as (tick, up_a_year) pairs."""
    check_assets(game)
    d = demo.Demo(demo.parse_args(['-g', game, '-i', os.path.join(REPLAYS_DIR, replay), '-t', str(ticks)]))

    up_a_year_ticks = []
    up_a_year = demo.skool_mod.Skool._up_a_year
    def recorded_up_a_year(skool):
        up_a_year_ticks.append(d.tick + 1)
        return up_a_year(skool)
    monkeypatch.setattr(demo.skool_mod.Skool, '_up_a_year', recorded_up_a_year)

    endings = []
    end_game = demo.skool_mod.Skool.end_game
    def recorded_end_game(skool, up_a_year=False):
        endings.append((d.tick + 1, up_a_year))
        return end_game(skool, up_a_year)
    monkeypatch.setattr(demo.skool_mod.Skool, 'end_game', recorded_end_game)

    shield_modes = []
    main_loop = demo.game.Game._main_loop
    def recorded_main_loop(g):
        rv = main_loop(g)
        mode = g.skool.shield_mode
        if not shield_modes or shield_modes[-1][1] != mode:
            shield_modes.append((d.tick + 1, mode))
        return rv
    monkeypatch.setattr(demo.game.Game, '_main_loop', recorded_main_loop)

    assert d.run(), 'demo crashed or a character got lost'
    return d, shield_modes, up_a_year_ticks, endings

def test_skool_daze(monkeypatch):
    d, shield_modes, up_a_year_ticks, endings = _run_replay(monkeypatch, 'sd', 'skool_daze.txt', 16600)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert up_a_year_ticks == [16478]

    # The game never ended (Skool Daze carries on into the next year after Eric
    # goes up a year, and Eric was never expelled)
    assert endings == []
    assert not skool.game_over

    # Eric is now in the next year: no shields are flashing and the safe is
    # closed
    assert skool.shield_mode == 1
    assert not any(shield.flashing for shield in skool.shields)
    assert not skool.safe.flashing

    # Eric's score and lines
    assert skool.scoreboard.score == 16000
    assert skool.scoreboard.lines == 6700
    # demo.py lifts the lines limit, so check against the game's real limit
    assert skool.scoreboard.lines < 10000

    # Eric is in the Exam Room
    assert skool.room(d.eric).name == 'EXAM ROOM'

def test_back_to_skool(monkeypatch):
    d, shield_modes, up_a_year_ticks, endings = _run_replay(monkeypatch, 'bts', 'back_to_skool.txt', 39300)
    skool = d.skool

    # There are no shields; Eric opened the safe with the key and went up a
    # year exactly once
    assert skool.shields == []
    assert [m for t, m in shield_modes] == [1]
    assert up_a_year_ticks == [39167]

    # The game ended exactly once, because Eric went up a year (Back to Skool
    # restarts then, keeping the score and lines), and was then restarted
    assert endings == [(39168, True)]
    assert not skool.game_over
    assert not skool.clear_score

    # Eric is now in the next year: the safe is closed
    assert not skool.safe.flashing

    # Eric's score and lines
    assert skool.scoreboard.score == 8500
    assert skool.scoreboard.lines == 7400
    # demo.py lifts the lines limit, so check against the game's real limit
    assert skool.scoreboard.lines < 10000

    # Eric is outside, in the playground
    assert skool.room(d.eric) is None
    assert (d.eric.x, d.eric.y) == (133, 17)

def test_skool_daze_take_too(monkeypatch):
    d, shield_modes, up_a_year_ticks, endings = _run_replay(monkeypatch, 'sdtt', 'skool_daze_take_too.txt', 25300)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert up_a_year_ticks == [25205]

    # The game never ended (Skool Daze Take Too carries on into the next year
    # after Eric goes up a year, and Eric was never expelled)
    assert endings == []
    assert not skool.game_over

    # Eric is now in the next year: no shields are flashing and the safe is
    # closed
    assert skool.shield_mode == 1
    assert not any(shield.flashing for shield in skool.shields)
    assert not skool.safe.flashing

    # Eric's score and lines
    assert skool.scoreboard.score == 16100
    assert skool.scoreboard.lines == 5200
    # demo.py lifts the lines limit, so check against the game's real limit
    assert skool.scoreboard.lines < 10000

    # Eric is in the Exam Room
    assert skool.room(d.eric).name == 'EXAM ROOM'

def test_ezad_looks(monkeypatch):
    d, shield_modes, up_a_year_ticks, endings = _run_replay(monkeypatch, 'el', 'ezad_looks.txt', 23900)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert up_a_year_ticks == [23813]

    # The game never ended (Ezad Looks carries on into the next year after Eric
    # goes up a year, and Eric was never expelled)
    assert endings == []
    assert not skool.game_over

    # Eric is now in the next year: no shields are flashing and the safe is
    # closed
    assert skool.shield_mode == 1
    assert not any(shield.flashing for shield in skool.shields)
    assert not skool.safe.flashing

    # Eric's score and lines
    assert skool.scoreboard.score == 18300
    assert skool.scoreboard.lines == 2500
    # demo.py lifts the lines limit, so check against the game's real limit
    assert skool.scoreboard.lines < 10000

    # Eric is in the Exam Room
    assert skool.room(d.eric).name == 'EXAM ROOM'

def test_back_to_skool_daze(monkeypatch):
    d, shield_modes, up_a_year_ticks, endings = _run_replay(monkeypatch, 'btsd', 'back_to_skool_daze.txt', 86800)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert up_a_year_ticks == [86686]

    # The game ended exactly once, because Eric went up a year (Back to Skool
    # Daze restarts then, keeping the score and lines), and was then restarted
    assert endings == [(86687, True)]
    assert not skool.game_over
    assert not skool.clear_score

    # Eric is now in the next year: no shields are flashing and the safe is
    # closed
    assert skool.shield_mode == 1
    assert not any(shield.flashing for shield in skool.shields)
    assert not skool.safe.flashing

    # Eric's score and lines
    assert skool.scoreboard.score == 18500
    assert skool.scoreboard.lines == 9000
    # demo.py lifts the lines limit, so check against the game's real limit
    assert skool.scoreboard.lines < 10000

    # Eric is outside, in the playground
    assert skool.room(d.eric) is None
    assert (d.eric.x, d.eric.y) == (133, 17)
