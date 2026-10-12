import os

from pyskooltest import PYSKOOL_HOME, demo, run

REPLAYS_DIR = os.path.join(PYSKOOL_HOME, 'replays')

def _run_replay(monkeypatch, capsys, tmp_path, game, replay, ticks):
    """Run a replay headless and return the Demo object (see run()) and the
    shield mode changes as (tick, mode) pairs."""
    with open(os.path.join(REPLAYS_DIR, replay)) as f:
        inputs = f.read()

    shield_modes = []
    demos = []
    main_loop = demo.game.Game._main_loop
    def recorded_main_loop(g):
        rv = main_loop(g)
        mode = g.skool.shield_mode
        if not shield_modes or shield_modes[-1][1] != mode:
            shield_modes.append((demos[0].tick + 1, mode))
        return rv
    monkeypatch.setattr(demo.game.Game, '_main_loop', recorded_main_loop)

    d, lines = run(monkeypatch, capsys, tmp_path, game, None, inputs, ticks, setup=demos.append)
    return d, shield_modes

def test_skool_daze(monkeypatch, capsys, tmp_path):
    d, shield_modes = _run_replay(monkeypatch, capsys, tmp_path, 'sd', 'skool_daze.txt', 16600)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert d.up_a_year_ticks == [16478]

    # The game never ended (Skool Daze carries on into the next year after Eric
    # goes up a year, and Eric was never expelled)
    assert d.endings == []
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

def test_back_to_skool(monkeypatch, capsys, tmp_path):
    d, shield_modes = _run_replay(monkeypatch, capsys, tmp_path, 'bts', 'back_to_skool.txt', 39300)
    skool = d.skool

    # There are no shields; Eric opened the safe with the key and went up a
    # year exactly once
    assert skool.shields == []
    assert [m for t, m in shield_modes] == [1]
    assert d.up_a_year_ticks == [39167]

    # The game ended exactly once, because Eric went up a year (Back to Skool
    # restarts then, keeping the score and lines), and was then restarted
    assert d.endings == [(39168, 'up a year')]
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

def test_skool_daze_take_too(monkeypatch, capsys, tmp_path):
    d, shield_modes = _run_replay(monkeypatch, capsys, tmp_path, 'sdtt', 'skool_daze_take_too.txt', 25300)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert d.up_a_year_ticks == [25205]

    # The game never ended (Skool Daze Take Too carries on into the next year
    # after Eric goes up a year, and Eric was never expelled)
    assert d.endings == []
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

def test_ezad_looks(monkeypatch, capsys, tmp_path):
    d, shield_modes = _run_replay(monkeypatch, capsys, tmp_path, 'el', 'ezad_looks.txt', 23900)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert d.up_a_year_ticks == [23813]

    # The game never ended (Ezad Looks carries on into the next year after Eric
    # goes up a year, and Eric was never expelled)
    assert d.endings == []
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

def test_back_to_skool_daze(monkeypatch, capsys, tmp_path):
    d, shield_modes = _run_replay(monkeypatch, capsys, tmp_path, 'btsd', 'back_to_skool_daze.txt', 86800)
    skool = d.skool

    # Eric flashed all the shields, opened the safe, unflashed all the shields,
    # and went up a year exactly once
    assert [m for t, m in shield_modes] == [1, 2, 3, 1]
    assert d.up_a_year_ticks == [86686]

    # The game ended exactly once, because Eric went up a year (Back to Skool
    # Daze restarts then, keeping the score and lines), and was then restarted
    assert d.endings == [(86687, 'up a year')]
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
