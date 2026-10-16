import pytest

from pyskooltest import give_water_pistol, run
from pyskool import ai, items

def test_back_to_skool_climb_over_skool_gate_from_plant(monkeypatch, capsys, tmp_path):
    # The skool gate is shut, and Eric has the water pistol and is standing 7
    # paces to the right of the plant pot just right of the gate, facing it;
    # he fires the water pistol at the plant pot, walks to it, jumps onto it,
    # waits for the plant to grow to full height, and then walks left off it
    inputs = """
        1 FIRE_WATER_PISTOL
        12 LEFT 26
        40 JUMP
        90 LEFT
    """
    events = []
    def setup(d):
        give_water_pistol(d)
        eric = d.eric
        eric.x, eric.y, eric.direction = 142, 17, -1
        d.skool.move_door('SkoolGate', True)
        # Put Albert where he's going (just inside the skool gate), so that he
        # doesn't open the gate on his way there
        albert = d.skool.cast.get('ALBERT')
        albert.x, albert.y = 112, 17
        plant = d.skool.plant_pots['RightGatePlant'].plant
        def finish_growing(method=plant.finish_growing):
            method()
            events.append((d.tick, 'finish_growing', (eric.x, eric.y)))
        plant.finish_growing = finish_growing
        def set_controller(command, method=eric._set_controller):
            method(command)
            if isinstance(command, ai.Flight):
                events.append((d.tick, 'Flight', (eric.x, eric.y), command.phases))
        eric._set_controller = set_controller
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 120, seed=5, setup=setup)

    # Eric was lifted to (135,14) as the plant grew to full height, and when
    # he walked left off the plant, he climbed over the skool gate
    gate = d.skool.barriers['SkoolGate']
    assert events == [
        (79, 'finish_growing', (135, 14)),
        (90, 'Flight', (135, 14), gate.climb_phases)
    ]

    # Eric landed on the other side of the gate, which is still shut
    assert (d.eric.x, d.eric.y) == (132, 17)
    assert d.eric.controller is None
    assert gate.is_shut()

    # Nobody gave Eric lines
    assert lines == []

def test_skool_daze_knocked_out_of_chair(monkeypatch, capsys, tmp_path):
    # Eric sits down in a chair in the Exam Room; Boy Wander, starting 12
    # paces to his left and facing him, walks towards him and fires his
    # catapult (from 8 paces away), knocking Eric out of the chair
    inputs = """
        1 SIT_STAND
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 64, 10, -1
        tearaway = d.skool.cast.get('TEARAWAY')
        tearaway.x, tearaway.y, tearaway.direction = 52, 10, 1
        def fire_catapult(method=tearaway.fire_catapult):
            events.append((d.tick, 'fire_catapult', (tearaway.x, tearaway.y)))
            method()
        tearaway.fire_catapult = fire_catapult
        def deck(method=eric.deck):
            chair = eric.chair()
            events.append((d.tick, 'deck', bool(eric.is_sitting_on_chair()), chair.x, chair.occupant is eric))
            method()
            events.append((d.tick, 'decked', eric.animatory_state, chair.occupant))
        eric.deck = deck
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-8', inputs, 60, setup=setup)

    # Boy Wander fired his catapult, and the pellet hit Eric while he was
    # sitting in the chair at x=64; Eric was knocked out, and the chair was
    # vacated
    assert events == [
        (29, 'fire_catapult', (56, 10)),
        (52, 'deck', True, 64, True),
        (52, 'decked', 'KNOCKED_OUT', None)
    ]
    assert d.eric.is_knocked_out()
    assert (d.eric.x, d.eric.y) == (64, 10)

    # Nobody gave Eric lines
    assert lines == []

def test_skool_daze_knocked_out_while_writing_on_blackboard(monkeypatch, capsys, tmp_path):
    # Eric starts writing on the blackboard in the Exam Room; Boy Wander,
    # starting 8 paces to his left and facing him, takes a step towards him
    # and fires his catapult, knocking Eric over while he's still writing
    inputs = """
        1 WRITE
        2 TYPE AB
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 47, 10, -1
        tearaway = d.skool.cast.get('TEARAWAY')
        tearaway.x, tearaway.y, tearaway.direction = 39, 10, 1
        def fire_catapult(method=tearaway.fire_catapult):
            events.append((d.tick, 'fire_catapult', (tearaway.x, tearaway.y)))
            method()
        tearaway.fire_catapult = fire_catapult
        def deck(method=eric.deck):
            events.append((d.tick, 'deck', eric.writing, type(eric.controller).__name__, eric.keyboard.writing))
            method()
            events.append((d.tick, 'decked', eric.writing, eric.controller, eric.keyboard.writing))
        eric.deck = deck
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-8', inputs, 40, setup=setup)

    # Boy Wander fired his catapult, and the pellet hit Eric while he was
    # writing on the blackboard; Eric was knocked out, and stopped writing
    assert events == [
        (11, 'fire_catapult', (40, 10)),
        (31, 'deck', True, 'Write', True),
        (31, 'decked', False, None, False)
    ]
    assert d.eric.is_knocked_out()
    assert (d.eric.x, d.eric.y) == (47, 10)

    # What Eric wrote before he was knocked out is on the blackboard
    blackboard = d.skool.get_room('ExamRoom').blackboard
    assert blackboard.lines == ['AB']
    assert blackboard.writer is d.eric

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_drop_three_stinkbombs(monkeypatch, capsys, tmp_path):
    # Eric has three stinkbombs; he drops them one at a time, waiting for each
    # stinkbomb cloud to disappear before dropping the next
    inputs = """
        1 DROP_STINKBOMB
        100 DROP_STINKBOMB
        200 DROP_STINKBOMB
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.inventory.add(items.STINKBOMBS3)
        def drop_stinkbomb(method=eric.drop_stinkbomb):
            before = sorted(eric.inventory)
            method()
            events.append((d.tick, before, sorted(eric.inventory), eric.has_stinkbomb()))
        eric.drop_stinkbomb = drop_stinkbomb
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 210, seed=5, setup=setup)

    # Each drop used up one stinkbomb, and after the last one Eric had none
    # left
    assert events == [
        (7, [items.STINKBOMBS3], [items.STINKBOMBS2], True),
        (105, [items.STINKBOMBS2], [items.STINKBOMBS1], True),
        (205, [items.STINKBOMBS1], [], False)
    ]
    assert d.eric.inventory == set()

    # Nobody gave Eric lines
    assert lines == []

@pytest.mark.parametrize('stinkbombs', ['STINKBOMBS1', 'STINKBOMBS2'])
def test_back_to_skool_collect_stinkbombs_when_already_having_some(monkeypatch, capsys, tmp_path, stinkbombs):
    # Eric has one or two stinkbombs, and starts beside a desk in the Blue Room
    # that contains three stinkbombs; he sits down and opens the desk
    inputs = """
        1 SIT_STAND
        10 OPEN_DESK
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 15, 3, -1
        eric.inventory.add(stinkbombs)
        desk = [desk for desk in d.skool.rooms['BlueRoom'].desks if desk.x == 15][0]
        assert desk.contents is None
        desk.insert(items.STINKBOMBS3)
        def collect_desk_contents(desk, method=eric.collect_desk_contents):
            before = sorted(eric.inventory)
            method(desk)
            events.append((d.tick, before, sorted(eric.inventory), desk.contents))
        eric.collect_desk_contents = collect_desk_contents
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 20, setup=setup)

    # Eric's stinkbombs were replaced by the three in the desk (which still
    # contains them)
    assert events == [
        (12, [stinkbombs], [items.STINKBOMBS3], items.STINKBOMBS3)
    ]
    assert d.eric.inventory == {items.STINKBOMBS3}

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_location_while_kissing(monkeypatch, capsys, tmp_path):
    # Eric walks right to the girls' dinner hall, where Hayley spends Mr
    # Withit's lesson, and kisses her while Mr Withit is on his way to fetch
    # him
    inputs = """
        1 RIGHT 156
        1304 KISS
    """
    events = []
    def setup(d):
        eric = d.eric
        def get_location(method=eric.get_location):
            location = method()
            if eric.hide_coords:
                events.append((d.tick, 'get_location', (eric.x, eric.y), eric.hide_coords, location))
            return location
        eric.get_location = get_location
        for name in ('hide', 'unhide'):
            def recorded(name=name, method=getattr(eric, name)):
                method()
                events.append((d.tick, name, (eric.x, eric.y)))
            setattr(eric, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Withit-BlueRoom-1', inputs, 1320, setup=setup)

    # While Eric was hidden (off-screen) during the kiss, Mr Withit checked
    # where he was, and got his real (pre-kiss) location
    assert events == [
        (1307, 'hide', (-3, 17)),
        (1308, 'get_location', (-3, 17), (172, 17), (172, 17)),
        (1308, 'get_location', (-3, 17), (172, 17), (172, 17)),
        (1309, 'unhide', (172, 17))
    ]

    # Eric is back where he was before the kiss
    assert (d.eric.x, d.eric.y) == (172, 17)
    assert d.eric.hide_coords is None

    # Nobody gave Eric lines
    assert lines == []
