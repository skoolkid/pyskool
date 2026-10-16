from pyskooltest import run

def _recorder(signals):
    """Return a 'setup' function for run() that records the signals raised
    and lowered (as ('signal', ID) and ('unsignal', ID) pairs) in 'signals'."""
    def setup(d):
        skool = d.skool
        for name in ('signal', 'unsignal'):
            def recorded(signal_id, name=name, method=getattr(skool, name)):
                signals.append((name, signal_id))
                method(signal_id)
            setattr(skool, name, recorded)
    return setup

def test_skool_daze_swot_grasses(monkeypatch, capsys, tmp_path):
    # Eric walks right to the gym, where the little boy waiting there tells
    # him that Einstein is going to tell Mr Wacker what he's up to (Eric
    # presses 'U' as soon as the boy starts speaking); Eric then goes up to the
    # top of the stairs outside Mr Wacker's study (via the stairs up to the
    # staff room) and waits there, making no attempt to stop Einstein getting
    # to the study
    inputs = """
        1 RIGHT 184
        367 UNDERSTOOD
        617 LEFT 298
        915 UP 28
        943 RIGHT 30
        973 LEFT
        975 UP 28
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-SwotGrass', inputs, 1838)

    # Einstein reached Mr Wacker's study (at tick 1691), and then Mr Wacker
    # came out and gave Eric 2000 lines
    assert lines == [(1836, 2000, 'MR WACKER', 'AddLines', None)]
    assert d.skool.scoreboard.lines == 2000

    # Eric is still at the top of the stairs
    assert (d.eric.x, d.eric.y) == (12, 3)

def test_skool_daze_swot_stopped(monkeypatch, capsys, tmp_path):
    # Eric goes up to the top floor (via the stairs up to the Exam Room and
    # the Map Room) and waits near the fire escape, where the little boy finds
    # him and tells him that Einstein is going to tell Mr Wacker what he's up
    # to (Eric presses 'U' as soon as the boy starts speaking); then, as
    # Einstein sets off for Mr Wacker's study, Eric punches him eight times,
    # each time just as he gets up, which delays him long enough
    inputs = """
        1 RIGHT 92
        93 UP 28
        121 LEFT 30
        151 RIGHT
        153 UP 28
        181 RIGHT 36
        675 UNDERSTOOD
        942 HIT
        1005 HIT
        1069 HIT
        1132 HIT
        1195 HIT
        1258 HIT
        1321 HIT
        1384 HIT
    """
    signals = []
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-SwotGrass', inputs, 2435,
                   setup=_recorder(signals))

    # Eric was told about Einstein, but Einstein never got to Mr Wacker's
    # study before the bell rang (at tick 2433), and the skool clock was reset
    # for the next lesson (Playtime-SwotGrass again)
    assert ('signal', 'EricWasToldAboutSwot') in signals
    assert ('signal', 'SwotGrassed') not in signals
    assert d.skool.timetable.counter > 2000

    # So Eric didn't get 2000 lines from Mr Wacker (or any other lines)
    assert lines == []

def test_skool_daze_pea_shooter_found_by_wacker(monkeypatch, capsys, tmp_path):
    # Eric walks right to the gym, where the little boy waiting there tells
    # him that Boy Wander has hidden a pea-shooter on the fire escape, and that
    # Eric will get lines if Mr Wacker gets there first (Eric presses 'U' as
    # soon as the boy starts speaking); Eric then goes up to the top floor (via
    # the stairs up to the Exam Room and the Map Room) and waits near the fire
    # escape, making no attempt to stop Mr Wacker getting there
    inputs = """
        1 RIGHT 184
        639 UNDERSTOOD
        946 LEFT 95
        1041 RIGHT
        1043 UP 28
        1071 LEFT 30
        1101 RIGHT
        1103 UP 28
        1131 RIGHT 36
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-HiddenPeaShooter', inputs, 2015)

    # Mr Wacker reached the fire escape before Boy Wander, and then gave Eric
    # 2000 lines
    assert lines == [(2013, 2000, 'MR WACKER', 'AddLines', None)]
    assert d.skool.scoreboard.lines == 2000

    # Eric is still near the fire escape
    assert (d.eric.x, d.eric.y) == (86, 3)

def test_skool_daze_pea_shooter_found_by_boy_wander(monkeypatch, capsys, tmp_path):
    # Eric goes up to the library (via the stairs up to the staff room and Mr
    # Wacker's study), where the little boy finds him and tells him about the
    # pea-shooter (Eric presses 'U' as soon as the boy starts speaking); then,
    # as Mr Wacker sets off for the fire escape (walking away from Eric), Eric
    # knocks him over three times by firing at his back
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 30
        177 LEFT
        179 UP 28
        207 RIGHT 90
        1329 UNDERSTOOD
        1660 FIRE_CATAPULT
        1742 FIRE_CATAPULT
        1826 FIRE_CATAPULT
    """
    signals = []
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-HiddenPeaShooter', inputs, 3144,
                   setup=_recorder(signals))

    # Boy Wander reached the fire escape (and lowered his signal) before Mr
    # Wacker; then the bell rang (at tick 3142), and the skool clock was reset
    # for the next lesson (Playtime-HiddenPeaShooter again)
    assert ('signal', 'EricWasToldAboutTearaway') in signals
    assert ('unsignal', 'TearawayReady') in signals
    assert d.skool.timetable.counter > 2000

    # So Eric didn't get 2000 lines from Mr Wacker (only lines for knocking him
    # over, each time he got up)
    assert lines == [
        (1725, 800, 'MR WACKER', 'NEVER_AGAIN', None),
        (1807, 200, 'MR WACKER', 'NEVER_AGAIN', None),
        (1889, 100, 'MR WACKER', 'NEVER_AGAIN', None)
    ]

def test_skool_daze_mumps(monkeypatch, capsys, tmp_path):
    # Eric is told by a little boy not to let Angelface (who has mumps) touch
    # him (and presses 'U' as soon as the boy starts speaking), but stays put
    # while Angelface walks past (at tick 223); he then walks left and up the
    # stairs towards the staff room, where Mr Rockitt is waiting
    inputs = """
        3 UNDERSTOOD
        224 LEFT 117
        341 UP 16
    """
    signals = []
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-Mumps', inputs, 470,
                   setup=_recorder(signals))

    # Eric caught mumps from Angelface, and then Mr Rockitt found him and sent
    # him home (ending the game)
    assert signals.index(('signal', 'EricWasToldAboutBully')) < signals.index(('signal', 'EricHasMumps'))
    assert d.endings == [(468, 'MR ROCKITT')]

    # Eric got no lines
    assert lines == []

def test_skool_daze_mumps_avoided(monkeypatch, capsys, tmp_path):
    # Eric is told by a little boy not to let Angelface (who has mumps) touch
    # him (and presses 'U' as soon as the boy starts speaking); he then walks
    # left (ahead of Angelface) and goes up the stairs to the White Room, where
    # he stays (out of sight of the teachers, and where Angelface never goes)
    # until the bell rings
    inputs = """
        3 UNDERSTOOD
        178 LEFT 117
        295 UP 28
        323 RIGHT 74
    """
    signals = []
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-Mumps', inputs, 1680,
                   setup=_recorder(signals))

    # Eric was told about Angelface, but never caught mumps; the bell rang (at
    # tick 1678) and the skool clock was reset for the next lesson
    # (Playtime-Mumps again)
    assert ('signal', 'EricWasToldAboutBully') in signals
    assert ('signal', 'EricHasMumps') not in signals
    assert d.endings == []
    assert d.skool.timetable.counter > 2000

    # Eric got no lines, and is still in the White Room
    assert lines == []
    assert d.skool.room(d.eric).name == 'WHITE ROOM'
