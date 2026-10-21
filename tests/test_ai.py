import pytest

from pyskooltest import demo, run
from pyskool import ai, barrier, items

def _desk_with(skool, item):
    """Return the (room ID, x-coordinate) of the desk containing an item, or
    None if no desk contains it."""
    for room_id, room in skool.rooms.items():
        for desk in room.desks:
            if desk.contents == item:
                return (room_id, desk.x)

def _desks_with(skool, item):
    """Return a list of the (room ID, x-coordinate) of every desk containing
    an item."""
    return [(room_id, desk.x) for room_id, room in skool.rooms.items() for desk in room.desks if desk.contents == item]

def test_back_to_skool_collect_and_drop_water_pistol(monkeypatch, capsys, tmp_path):
    # With seed 5, the water pistol is in the leftmost desk in the girls'
    # skool's Middle Room; Eric walks right to the girls' skool, goes up the
    # stairs to the middle floor, walks left to that desk, sits down, opens
    # it (collecting the water pistol), stands up, and then drops the water
    # pistol
    inputs = """
        1 RIGHT 172
        173 UP 40
        213 LEFT 73
        290 SIT_STAND
        300 OPEN_DESK
        320 SIT_STAND
        330 DUMP_WATER_PISTOL
    """
    events = []
    def setup(d):
        assert _desk_with(d.skool, items.WATER_PISTOL) == ('MiddleRoom', 167)
        eric = d.eric
        for name in ('collect_desk_contents', 'dump_water_pistol'):
            def recorded(*args, name=name, method=getattr(eric, name)):
                method(*args)
                events.append((d.tick, name, items.WATER_PISTOL in eric.inventory, _desk_with(d.skool, items.WATER_PISTOL)))
            setattr(eric, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 340, seed=5, setup=setup)

    # Eric collected the water pistol from the desk (leaving it empty) when
    # the desk lid went up, and then dropped the water pistol, which was then
    # hidden in a randomly chosen desk
    assert events == [
        (302, 'collect_desk_contents', True, None),
        (331, 'dump_water_pistol', False, ('BlueRoom', 17))
    ]

    # Nobody gave Eric lines
    assert lines == []

    # Eric is standing up again next to the desk
    assert (d.eric.x, d.eric.y) == (167, 10)
    assert not d.eric.is_sitting()

def test_back_to_skool_drop_sherry_filled_water_pistol(monkeypatch, capsys, tmp_path):
    # Eric is given the water pistol, fills it with sherry, and then drops it
    # (the cheat keys don't take the original water pistol out of its desk,
    # which with seed 5 is the leftmost desk in the girls' skool's Middle
    # Room)
    inputs = """
        1 GIVE_WATER_PISTOL
        4 SWITCH_PISTOL
        7 DUMP_WATER_PISTOL
    """
    events = []
    def setup(d):
        eric = d.eric
        def dump_water_pistol(method=eric.dump_water_pistol):
            events.append((d.tick, 'dump_water_pistol', sorted(eric.inventory), _desks_with(d.skool, items.WATER_PISTOL)))
            method()
            events.append((d.tick, 'dumped', sorted(eric.inventory), _desks_with(d.skool, items.WATER_PISTOL)))
        eric.dump_water_pistol = dump_water_pistol
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 15, seed=5, setup=setup,
                   options=['--config', 'Cheat,1'])

    # Eric dropped the sherry-filled water pistol, which was then filled with
    # water and hidden in a randomly chosen (empty) desk
    assert events == [
        (8, 'dump_water_pistol', [items.SHERRY_PISTOL], [('MiddleRoom', 167)]),
        (8, 'dumped', [], [('MiddleRoom', 167), ('UpperRoom', 170)])
    ]
    assert _desk_with(d.skool, items.SHERRY_PISTOL) is None

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_open_desk_while_lid_is_up(monkeypatch, capsys, tmp_path):
    # Eric starts beside an empty desk in the Blue Room; he sits down, opens
    # the desk, and then tries to open it again while the lid is still up
    inputs = """
        1 SIT_STAND
        10 OPEN_DESK
        14 OPEN_DESK
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 15, 3, -1
        desk = [desk for desk in d.skool.rooms['BlueRoom'].desks if desk.x == 15][0]
        assert desk.contents is None
        lid = d.skool.cast.desk_lid
        def raise_lid(desk, character, method=lid.raise_lid):
            events.append((d.tick, 'raise_lid', desk.x, lid.is_visible()))
            method(desk, character)
        def hide(method=lid.hide):
            events.append((d.tick, 'hide'))
            method()
        lid.raise_lid, lid.hide = raise_lid, hide
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 50, setup=setup)

    # Eric raised the lid of the desk; the second attempt (while the lid was
    # still up) had no effect, and the lid was lowered as usual
    assert events == [
        (11, 'raise_lid', 15, False),
        (15, 'raise_lid', 15, True),
        (39, 'hide')
    ]
    assert d.eric.is_sitting_on_chair()
    assert not d.skool.cast.desk_lid.is_visible()

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_fire_water_pistol_at_floor(monkeypatch, capsys, tmp_path):
    # Eric has the water pistol; he walks left, away from the plant pots by
    # the skool gate, and fires it to the left, away from any cups or plants
    inputs = """
        1 GIVE_WATER_PISTOL
        1 LEFT 20
        30 FIRE_WATER_PISTOL
    """
    events = []
    def setup(d):
        water = d.eric.water
        def launch(*args, method=water.launch):
            method(*args)
            events.append((d.tick, 'launch', water.x, water.y))
        water.launch = launch
        for name in ('hit_cup', 'hit_plant', 'hit_floor'):
            def hit(name=name, method=getattr(water, name)):
                if method():
                    events.append((d.tick, name, water.x, water.y))
                    return True
                return False
            setattr(water, name, hit)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 60, seed=5, setup=setup,
                   options=['--config', 'Cheat,1'])

    # The water left the pistol at (126,15), and hit the floor (and nothing
    # else) at (121,17), where it disappeared
    assert events == [
        (35, 'launch', 126, 15),
        (54, 'hit_floor', 121, 17)
    ]
    assert not d.eric.water.is_visible()

    # Eric still has the water pistol
    assert items.WATER_PISTOL in d.eric.inventory

    # Nobody gave Eric lines
    assert lines == []

def test_skool_daze_little_boy_repeats_message(monkeypatch, capsys, tmp_path):
    # A little boy tells Eric not to let Angelface (who has mumps) touch him;
    # Eric doesn't press 'U' until the boy has started repeating the message
    inputs = """
        300 UNDERSTOOD
    """
    events = []
    def setup(d):
        boy = d.skool.cast.get('BOY10')
        def say(words, shift, method=boy.say):
            if shift == -4:
                events.append((d.tick, 'say', words.split(' - ')[0]))
            return method(words, shift)
        def remove_bubble(method=boy.remove_bubble):
            if boy.bubble:
                events.append((d.tick, 'finished speaking'))
            method()
        boy.say, boy.remove_bubble = say, remove_bubble
        eric = d.eric
        def unfreeze(method=eric.unfreeze):
            if eric.frozen:
                events.append((d.tick, 'unfreeze Eric'))
            method()
        eric.unfreeze = unfreeze
        def signal(signal_id, method=d.skool.signal):
            events.append((d.tick, 'signal', signal_id))
            method(signal_id)
        d.skool.signal = signal
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-Mumps', inputs, 460, setup=setup)

    # The boy gave Eric the message, waited for him to press 'U', and then
    # gave him the message again; Eric pressed 'U' during the repeat, and when
    # the boy had finished speaking, Eric was unfrozen and the boy signalled
    # that Eric had been told about Angelface
    assert events == [
        (3, 'say', "Don't let ANGELFACE touch you this playtime"),
        (176, 'finished speaking'),
        (277, 'say', "Don't let ANGELFACE touch you this playtime"),
        (451, 'finished speaking'),
        (451, 'unfreeze Eric'),
        (451, 'signal', 'EricWasToldAboutBully')
    ]
    assert not d.eric.frozen

    # Angelface walked past Eric (at tick 223) before Eric was told about him,
    # so Eric didn't catch mumps
    assert d.endings == []
    assert lines == []

def test_skool_daze_walk_into_wall(monkeypatch, capsys, tmp_path):
    # Eric walks left until he reaches the far left wall, and keeps trying to
    # walk left
    inputs = """
        1 LEFT 200
    """
    events = []
    demos = []
    def setup(d):
        demos.append(d)
    is_door = barrier.Barrier.is_door
    def recording_is_door(b):
        result = is_door(b)
        eric = demos[0].eric
        events.append((demos[0].tick, b.barrier_id, (eric.x, eric.y), result))
        return result
    monkeypatch.setattr(barrier.Barrier, 'is_door', recording_is_door)
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 200, setup=setup)

    # Each time Eric tried to walk into the wall, he checked whether it was a
    # door (it wasn't), and stayed where he was
    assert events == [
        (195, 'FarLeftWall', (0, 17), False),
        (197, 'FarLeftWall', (0, 17), False),
        (199, 'FarLeftWall', (0, 17), False)
    ]
    assert (d.eric.x, d.eric.y) == (0, 17)

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_fall_off_dying_plant(monkeypatch, capsys, tmp_path):
    # Eric has the water pistol; he walks right to a spot 7 paces to the right
    # of the plant pot just right of the skool gate, turns round, fires the
    # water pistol at the plant pot, walks to it, and jumps onto it before the
    # plant starts growing
    inputs = """
        1 GIVE_WATER_PISTOL
        1 RIGHT 38
        45 LEFT
        50 FIRE_WATER_PISTOL
        59 LEFT 28
        88 JUMP
    """
    events = []
    def setup(d):
        plant = d.skool.plant_pots['RightGatePlant'].plant
        for name in ('grow', 'appear', 'finish_growing', 'die'):
            def recorded(name=name, method=getattr(plant, name)):
                method()
                events.append((d.tick, name, (d.eric.x, d.eric.y)))
            setattr(plant, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 160, seed=5, setup=setup,
                   options=['--config', 'Cheat,1'])

    # The water hit the plant pot while Eric was walking towards it; Eric
    # jumped onto the plant pot at (135,16), was lifted as the plant grew to
    # half and then full height, and was dropped when the plant died
    assert events == [
        (72, 'grow', (139, 17)),
        (106, 'appear', (135, 15)),
        (127, 'finish_growing', (135, 14)),
        (148, 'die', (135, 14))
    ]

    # Eric fell to the floor, and is now sitting on it
    assert (d.eric.x, d.eric.y) == (135, 17)
    assert d.eric.is_sitting_on_floor()

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_kiss_nobody(monkeypatch, capsys, tmp_path):
    # Eric, facing left, tries to kiss Hayley, who is just behind him (at
    # (136,17)) and facing away from him
    inputs = """
        10 KISS
    """
    events = []
    def setup(d):
        eric, cast = d.eric, d.skool.cast
        def kissee(method=cast.kissee):
            c = method()
            events.append((d.tick, 'kissee', c and c.name))
            return c
        cast.kissee = kissee
        for name in ('walk', 'stand_up'):
            def recorded(*args, name=name, method=getattr(eric, name)):
                method(*args)
                events.append((d.tick, name, (eric.x, eric.y), eric.animatory_state))
            setattr(eric, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 30, setup=setup)

    # There was nobody in front of Eric to kiss, so he moved midstride (without
    # changing his location), and then returned to the standing position
    assert events == [
        (13, 'kissee', None),
        (13, 'walk', (133, 17), 'WALK1'),
        (17, 'stand_up', (133, 17), 'WALK0')
    ]
    assert d.eric.controller is None

    # Eric's lines total didn't change (as it would have if Hayley had kissed
    # him)
    assert lines == []
    assert d.skool.scoreboard.lines == 0

def test_back_to_skool_knock_out_hayley(monkeypatch, capsys, tmp_path):
    # Eric turns round and fires his catapult at Hayley as she walks away from
    # him
    inputs = """
        1 RIGHT 4
        40 FIRE_CATAPULT
    """
    events = []
    def setup(d):
        hayley = d.skool.cast.get('HEROINE')
        def deck(*args, method=hayley.deck):
            kisses = hayley.kisses
            method(*args)
            events.append((d.tick, (hayley.x, hayley.y), kisses, hayley.kisses))
        hayley.deck = deck
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 80, setup=setup)

    # The pellet knocked Hayley out, and her kiss counter went down from 40 to
    # 39
    assert events == [(73, (142, 17), 40, 39)]
    assert d.skool.cast.get('HEROINE').animatory_state == 'KNOCKED_OUT'

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_slapped_by_hayley(monkeypatch, capsys, tmp_path):
    # Hayley's kiss counter is 0 to begin with; Eric turns round to face her
    # as she walks towards him, and tries to kiss her when she is 2 paces in
    # front of him
    inputs = """
        1 RIGHT
        9 KISS
    """
    events = []
    def setup(d):
        eric = d.eric
        hayley = d.skool.cast.get('HEROINE')
        hayley.kisses = 0
        for c, name in ((hayley, 'raise_arm'), (hayley, 'kiss_eric'), (hayley, 'lower_arm'), (eric, 'deck')):
            def recorded(*args, c=c, name=name, method=getattr(c, name)):
                method(*args)
                events.append((d.tick, c.name, name, (c.x, c.y), c.animatory_state))
            setattr(c, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-3', inputs, 20, setup=setup)

    # Hayley raised her arm instead of kissing Eric, and then slapped him
    # (knocking him out)
    assert events == [
        (11, 'HAYLEY', 'raise_arm', (135, 17), 'ARM_UP'),
        (13, 'HAYLEY', 'lower_arm', (135, 17), 'WALK0'),
        (13, 'ERIC', 'deck', (133, 17), 'KNOCKED_OUT')
    ]
    assert d.eric.is_knocked_out()

    # Hayley's kiss counter is still 0
    assert d.skool.cast.get('HEROINE').kisses == 0

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_frog_mid_hop_is_not_catchable(monkeypatch, capsys, tmp_path):
    # Eric starts in the Science Lab storeroom, facing the frog; it hops back
    # and forth while he's near it, and he tries to catch it while it's
    # mid-hop
    inputs = """
        157 CATCH
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 56, 10, 1
        frog = d.skool.cast.frogs[0]
        def is_catchable_at(x, y, method=frog.is_catchable_at):
            catchable = method(x, y)
            events.append((d.tick, (x, y), (frog.x, frog.y), frog.animatory_state, catchable))
            return catchable
        frog.is_catchable_at = is_catchable_at
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 163, setup=setup)

    # Eric's hand was where a sitting frog at (57,10) would be caught, but the
    # frog there was mid-hop, so Eric didn't catch it
    assert events == [(158, (58, 13), (57, 10), 'HOP1', False)]
    assert items.FROG not in d.eric.inventory

    # The frog then landed and sat at (57,10)
    frog = d.skool.cast.frogs[0]
    assert (frog.x, frog.y) == (57, 10)
    assert frog.animatory_state == 'SIT'

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_catch_released_mouse(monkeypatch, capsys, tmp_path):
    # Eric starts on the top floor near the Revision Library, facing the
    # mouse; he catches it, releases it, and then catches it again
    inputs = """
        30 CATCH
        40 RELEASE_MICE
        54 CATCH
    """
    events = []
    def setup(d):
        eric, cast = d.eric, d.skool.cast
        eric.x, eric.y, eric.direction = 16, 3, 1
        for name in ('caught_mouse', 'kill_mouse'):
            def recorded(mouse, name=name, method=getattr(cast, name)):
                events.append((d.tick, name, mouse.character_id, (mouse.x, mouse.y), mouse.immortal))
                method(mouse)
            setattr(cast, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 70, setup=setup)

    # Eric caught the immortal mouse (which was then relocated), released a
    # mortal mouse in its place, and then caught the mortal mouse, which was
    # removed from the game
    assert events == [
        (32, 'caught_mouse', 'MOUSE', (17, 3), True),
        (55, 'caught_mouse', 'MortalMouse1', (17, 3), False),
        (55, 'kill_mouse', 'MortalMouse1', (17, 3), False)
    ]
    assert [a.character_id for a in d.skool.cast.animals if a.is_mouse()] == ['MOUSE']
    assert d.eric.mice == 1

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_seated_girls_sit_down_again_after_evading_mice(monkeypatch, capsys, tmp_path):
    # Eric walks through the skool gate and closes all the doors (so that Miss
    # Take stops waiting for the boys' skool door to be shut, and goes to
    # teach her class in the Middle Room), and gives himself some mice; then
    # he goes up to the Middle Room, and releases the mice in front of the
    # girls sitting there
    inputs = """
        1 RIGHT 172
        45 CLOSE_DOORS
        50 GIVE_ALL
        1000 UP 40
        1040 LEFT 70
        1115 RELEASE_MICE
    """
    events = []
    def setup(d):
        execute = ai.EvadeMouse.execute
        def recorded(command):
            c = command.character
            starting = command.old_as is None
            old_as = c.animatory_state
            val = execute(command)
            if c.character_id.startswith('GIRL') and (starting or val is command):
                chair = c.chair()
                events.append((d.tick, 'start' if starting else 'end', c.name, (c.x, c.y), old_as, c.animatory_state,
                               chair.occupant.name if chair and chair.occupant else None))
            return val
        monkeypatch.setattr(ai.EvadeMouse, 'execute', recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Withit-YellowRoom-1', inputs, 1275, setup=setup, options=['--config', 'Cheat,1'])

    # Sarah-Jane, Amelia and Philippa got out of their seats (vacating them)
    # to evade the mice, and when they'd finished evading, each sat down again
    # in the same seat (and so occupied it again); Sarah-Jane and Amelia then
    # got up again to evade the mice once more
    assert events == [
        (1120, 'start', 'SARAH-JANE', (171, 10), 'SITTING_ON_CHAIR', 'WALK0', None),
        (1155, 'start', 'AMELIA', (173, 10), 'SITTING_ON_CHAIR', 'WALK0', None),
        (1162, 'start', 'PHILIPPA', (175, 10), 'SITTING_ON_CHAIR', 'WALK0', None),
        (1234, 'end', 'SARAH-JANE', (171, 10), 'WALK0', 'SITTING_ON_CHAIR', 'SARAH-JANE'),
        (1239, 'start', 'SARAH-JANE', (171, 10), 'SITTING_ON_CHAIR', 'WALK0', None),
        (1269, 'end', 'AMELIA', (173, 10), 'WALK0', 'SITTING_ON_CHAIR', 'AMELIA'),
        (1274, 'start', 'AMELIA', (173, 10), 'SITTING_ON_CHAIR', 'WALK0', None),
        (1274, 'end', 'PHILIPPA', (175, 10), 'WALK0', 'SITTING_ON_CHAIR', 'PHILIPPA')
    ]

def test_back_to_skool_bike_runs_out_of_momentum(monkeypatch, capsys, tmp_path):
    # The bike is unchained from the start, and stands at the base of the
    # tree (at (100,17)); Eric walks left to it, turns round, gets on, pedals
    # for a while (pressing 'left' and 'right' alternately), and then stops
    # pedalling
    inputs = """
        1 LEFT 132
        135 RIGHT
        138 MOUNT_BIKE
        142 RIGHT
        146 LEFT
        150 RIGHT
        154 LEFT
        158 RIGHT
        162 LEFT
    """
    events = []
    def setup(d):
        d.skool.unchain_bike()
        eric, bike = d.eric, d.skool.cast.bike
        for c, name in ((bike, 'prepare'), (bike, 'pedal'), (bike, 'fall'), (eric, 'fall_to_floor')):
            def recorded(*args, c=c, name=name, method=getattr(c, name)):
                method(*args)
                events.append((d.tick, name, (eric.x, eric.y), bike.momentum))
            setattr(c, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 210, setup=setup)

    # Eric got on the bike (which was given a momentum of 3), pedalled it six
    # times (each pedal adding 2 to its momentum, and the bike losing 1 every
    # time it moved), and then rode it along until it ran out of momentum and
    # fell over
    assert events == [
        (139, 'prepare', (100, 17), 3),
        (144, 'pedal', (101, 17), 4),
        (147, 'pedal', (102, 17), 6),
        (150, 'pedal', (103, 17), 8),
        (156, 'pedal', (105, 17), 9),
        (159, 'pedal', (106, 17), 11),
        (162, 'pedal', (107, 17), 13),
        (201, 'fall', (120, 17), 0),
        (204, 'fall_to_floor', (120, 17), 0)
    ]

    # Eric fell off the bike, and is now sitting on the floor next to it
    assert (d.eric.x, d.eric.y) == (120, 17)
    assert d.eric.is_sitting_on_floor()
    assert d.eric.controller is None
    bike = d.skool.cast.bike
    assert (bike.x, bike.y, bike.animatory_state) == (120, 17, 'BIKE_ON_FLOOR')

    # Nobody gave Eric lines
    assert lines == []

def _shut_door_with_bike_nearby(monkeypatch, capsys, tmp_path, bike_x, ticks):
    """Run Back to Skool with the bike lying at (bike_x,17) and Eric in the
    Blue Room, and return the Demo object, the lines given, and a list of
    (tick, door ID, bike location before, bike location after) tuples
    recording when the bike was checked for being in the way of a door that
    was about to be shut."""
    events = []
    def setup(d):
        d.skool.unchain_bike()
        eric, cast = d.eric, d.skool.cast
        cast.bike.x = bike_x
        eric.x, eric.y = 20, 3
        def move_bike_away(door, method=cast.move_bike_away):
            before = (cast.bike.x, cast.bike.y)
            method(door)
            events.append((d.tick, door.barrier_id, before, (cast.bike.x, cast.bike.y)))
        cast.move_bike_away = move_bike_away
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Creak-BlueRoom-1', '', ticks, setup=setup)
    return d, lines, events

def test_back_to_skool_albert_moves_bike_away_from_skool_gate(monkeypatch, capsys, tmp_path):
    # The bike is lying just inside the skool gate when Albert goes to shut it
    d, lines, events = _shut_door_with_bike_nearby(monkeypatch, capsys, tmp_path, 133, 440)

    # Albert moved the bike to the other side of the gate, and then shut it
    assert events == [(433, 'SkoolGate', (133, 17), (135, 17))]
    assert d.skool.is_door_shut('SkoolGate')
    bike = d.skool.cast.bike
    assert (bike.x, bike.y, bike.animatory_state) == (135, 17, 'BIKE_ON_FLOOR')

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_albert_moves_bike_away_from_boys_skool_door(monkeypatch, capsys, tmp_path):
    # The bike is lying just inside the boys' skool door when Albert goes to
    # shut it (after shutting the skool gate)
    d, lines, events = _shut_door_with_bike_nearby(monkeypatch, capsys, tmp_path, 94, 810)

    # The bike wasn't in the way of the gate; Albert moved it to the other
    # side of the door, and then shut the door
    assert events == [
        (433, 'SkoolGate', (94, 17), (94, 17)),
        (803, 'SkoolDoor', (94, 17), (96, 17))
    ]
    assert d.skool.is_door_shut('SkoolDoor')
    bike = d.skool.cast.bike
    assert (bike.x, bike.y, bike.animatory_state) == (96, 17, 'BIKE_ON_FLOOR')

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_wacker_smells_stinkbomb_in_his_study(monkeypatch, capsys, tmp_path):
    # Eric has stinkbombs, and stands just outside Mr Wacker's study door,
    # facing it; he drops a stinkbomb while Mr Wacker is walking about in his
    # study
    inputs = """
        1 GIVE_STINKBOMBS
        50 DROP_STINKBOMB
    """
    events = []
    wacker_xy = {}  # tick -> Mr Wacker's location
    demos = []
    def setup(d):
        demos.append(d)
        eric, skool = d.eric, d.skool
        eric.x, eric.y, eric.direction = 85, 3, -1
        wacker = skool.cast.get('WACKER')
        def open_window(window, method=wacker.open_window):
            events.append((d.tick, 'open_window', window.barrier_id, (wacker.x, wacker.y),
                           [type(c).__name__ for c in wacker.command_list.stack]))
            method(window)
        wacker.open_window = open_window
        def move_door(barrier_id, shut, method=skool.move_door):
            events.append((d.tick, 'move_door', barrier_id, shut, (wacker.x, wacker.y)))
            method(barrier_id, shut)
        skool.move_door = move_door
    main_loop = demo.game.Game._main_loop
    def recording_main_loop(g):
        result = main_loop(g)
        if demos:
            wacker = demos[0].skool.cast.get('WACKER')
            wacker_xy[demos[0].tick] = (wacker.x, wacker.y)
        return result
    monkeypatch.setattr(demo.game.Game, '_main_loop', recording_main_loop)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Creak-BlueRoom-1', inputs, 300, setup=setup,
                   options=['--config', 'Cheat,1'])

    # Mr Wacker smelt the stinkbomb while walking about in his study (and so
    # not under the control of a GoTo command); he opened the study door,
    # walked to the upper window, and opened it
    assert events == [
        (58, 'open_window', 'UpperWindow', (81, 3), ['MoveAboutUntil', 'WalkAround', 'GoToXY']),
        (83, 'move_door', 'StudyDoor', False, (82, 3)),
        (178, 'move_door', 'UpperWindow', False, (90, 3))
    ]
    assert not d.skool.is_door_shut('UpperWindow')

    # Mr Wacker then went back to where he smelt the stinkbomb, and resumed
    # walking about in his study
    back = min(t for t in wacker_xy if t > 178 and wacker_xy[t] == (81, 3))
    assert back == 278
    assert all(wacker_xy[t][0] < 84 for t in range(back, 300))

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_no_lines_for_jumping(monkeypatch, capsys, tmp_path):
    # Eric stands in Mr Wacker's study, facing him, and jumps (Back to Skool
    # has no NO_JUMPING lines message)
    inputs = """
        5 JUMP
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 82, 3, -1
        # Scroll the screen to show the study (as it would if Eric had walked
        # there), so that Mr Wacker is on screen and can give lines
        d.skool.screen.column = 64
        wacker = d.skool.cast.get('WACKER')
        def print_lines_message(recipient_id, message_id, method=wacker.print_lines_message):
            events.append((d.tick, (wacker.x, wacker.y), recipient_id, message_id,
                           d.skool.screen.contains(wacker), message_id in wacker.lines_messages))
            method(recipient_id, message_id)
        wacker.print_lines_message = print_lines_message
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Creak-BlueRoom-1', inputs, 20, setup=setup)

    # Mr Wacker, on screen, saw Eric jump and tried to give him lines, but
    # had no NO_JUMPING lines message to give
    assert events == [(8, (76, 3), 'HERO', 'NO_JUMPING', True, False)]

    # So Eric got no lines
    assert lines == []
    assert d.skool.scoreboard.lines == 0

def test_back_to_skool_hayleys_lines_added_to_erics_total(monkeypatch, capsys, tmp_path):
    # Eric fires his catapult at Mr Withit, who is facing away from him; when
    # Mr Withit gets up, Hayley is the nearest lines recipient
    inputs = """
        3 FIRE_CATAPULT
    """
    events = []
    def setup(d):
        eric, withit = d.eric, d.skool.cast.get('WITHIT')
        eric.x, eric.y, eric.direction = 124, 17, 1
        withit.x, withit.y, withit.direction = 136, 17, 1
        for name in ('knock_over', 'print_lines_message'):
            def recorded(*args, name=name, method=getattr(withit, name)):
                events.append((d.tick, name, (withit.x, withit.y)) + args)
                method(*args)
            setattr(withit, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 80, setup=setup)

    # The pellet knocked Mr Withit over, and when he got up he gave lines to
    # Hayley (she was nearer to him than Eric or Angelface)
    assert events == [
        (34, 'knock_over', (133, 17)),
        (74, 'print_lines_message', (133, 17), 'HEROINE', 'NEVER_AGAIN')
    ]

    # Hayley's lines were added to Eric's total
    assert lines == [(75, 700, 'MR WITHIT', 'NEVER_AGAIN', 'HAYLEY')]
    assert d.skool.scoreboard.lines == 700

def test_back_to_skool_turn_round_on_stairs(monkeypatch, capsys, tmp_path):
    # Eric is halfway up the stairs to the Revision Library, facing up them;
    # he turns round and walks back down
    inputs = """
        1 DOWN 14
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 22, 7, 1
        def turn(method=eric.turn):
            method()
            events.append((d.tick, (eric.x, eric.y), eric.direction))
        eric.turn = turn
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 32, setup=setup)

    # Eric turned round to face down the stairs without moving, and then
    # walked down them to the bottom
    assert events == [(3, (22, 7), -1)]
    assert (d.eric.x, d.eric.y, d.eric.direction) == (19, 10, -1)

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_lines_for_telling_tale_about_absent_eric(monkeypatch, capsys, tmp_path):
    # Eric stays where he is (in the playground) and misses Mr Creak's lesson
    # in the Yellow Room; Einstein tells Mr Creak that Eric is absent, and
    # with seed 2, Mr Creak decides to give Einstein lines for telling tales
    # before going to fetch Eric
    events = []
    demos = []
    def setup(d):
        demos.append(d)
        # Show the Yellow Room on screen, so that Mr Creak can give lines
        d.skool.screen.column = 32
    fetch_eric = demo.lesson.Lesson.fetch_eric
    def recording_fetch_eric(lesson):
        events.append((demos[0].tick, 'fetch_eric', lesson.teacher.name))
        return fetch_eric(lesson)
    monkeypatch.setattr(demo.lesson.Lesson, 'fetch_eric', recording_fetch_eric)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', None, '', 960, seed=2, setup=setup)

    # Mr Creak gave Einstein lines for telling tales (which were added to
    # Eric's score) before setting off to fetch Eric
    assert events == [(947, 'fetch_eric', 'MR CREAK')]
    assert lines == [(948, 500, 'MR CREAK', 'NO_TALES', 'EINSTEIN')]
    assert d.skool.scoreboard.score == 500

def _return_to_base_after_fetching_eric(monkeypatch, capsys, tmp_path, game, lesson_id, seed, eric_xy, inputs, ticks):
    """Run a lesson with Eric starting (facing left) at a given location
    outside the classroom, and return the Demo object, the lines given, and
    a list of (tick, teacher location, teacher direction, command returned,
    teacher's next action, next actor) tuples recording each call to
    Lesson.return_to_base()."""
    events = []
    demos = []
    def setup(d):
        demos.append(d)
        d.eric.x, d.eric.y = eric_xy
        d.eric.direction = -1
    return_to_base = demo.lesson.Lesson.return_to_base
    def recording_return_to_base(lesson):
        command = return_to_base(lesson)
        teacher = lesson.teacher
        events.append((demos[0].tick, (teacher.x, teacher.y), teacher.direction, command and type(command).__name__,
                       lesson.teacher_action, lesson.actor.name))
        return command
    monkeypatch.setattr(demo.lesson.Lesson, 'return_to_base', recording_return_to_base)
    d, lines = run(monkeypatch, capsys, tmp_path, game, lesson_id, inputs, ticks, seed=seed, setup=setup)
    return d, lines, events

def test_back_to_skool_teacher_returns_to_blackboard_after_fetching_eric(monkeypatch, capsys, tmp_path):
    # Eric is just outside the Yellow Room at the start of Mr Creak's lesson;
    # Einstein tells Mr Creak that Eric is absent, and when Mr Creak sets off
    # to fetch him, Eric walks into the classroom
    inputs = """
        949 LEFT 20
    """
    d, lines, events = _return_to_base_after_fetching_eric(monkeypatch, capsys, tmp_path, 'bts', 'Creak-YellowRoom-1', 0, (66, 3), inputs, 1000)

    # Mr Creak went back to where he stood at the start of the lesson,
    # arrived facing the wrong way and turned round, and then (since the
    # Yellow Room has a blackboard and Einstein had not yet told any other
    # tales) handed over to Einstein
    assert events == [
        (961, (51, 3), 1, 'GoToXY', 'return_to_base', 'MR CREAK'),
        (984, (49, 3), -1, 'GoTowardsXY', 'return_to_base', 'MR CREAK'),
        (989, (49, 3), 1, None, 'return_to_base', 'EINSTEIN')
    ]

    # Nobody gave Eric lines
    assert lines == []

def test_skool_daze_teacher_returns_to_ask_question_after_fetching_eric(monkeypatch, capsys, tmp_path):
    # Eric is just outside the Map Room at the start of Mr Withit's lesson;
    # Einstein tells Mr Withit that Eric is absent, and when Mr Withit sets
    # off to fetch him, Eric walks into the classroom
    inputs = """
        1446 LEFT 40
    """
    d, lines, events = _return_to_base_after_fetching_eric(monkeypatch, capsys, tmp_path, 'sd', 'Withit-MapRoom-1', 0, (80, 3), inputs, 1540)

    # Mr Withit went back to where he stood at the start of the lesson,
    # arrived facing the wrong way and turned round, and then (since the Map
    # Room has no blackboard, and this lesson has a question-and-answer
    # session) asked a question
    assert events == [
        (1476, (67, 3), 1, 'GoToXY', 'return_to_base', 'MR WITHIT'),
        (1529, (62, 3), -1, 'GoTowardsXY', 'return_to_base', 'MR WITHIT'),
        (1534, (62, 3), 1, None, 'ask_question', 'MR WITHIT')
    ]

    # Nobody gave Eric lines
    assert lines == []

def test_skool_daze_teacher_returns_to_walk_up_and_down_after_fetching_eric(monkeypatch, capsys, tmp_path):
    # Eric is just outside the Map Room at the start of Mr Withit's lesson
    # (which, with seed 4, has no question-and-answer session); Einstein
    # tells Mr Withit that Eric is absent, and when Mr Withit sets off to
    # fetch him, Eric walks into the classroom
    inputs = """
        1451 LEFT 40
    """
    d, lines, events = _return_to_base_after_fetching_eric(monkeypatch, capsys, tmp_path, 'sd', 'Withit-MapRoom-1', 4, (80, 3), inputs, 1580)

    # Mr Withit went back to where he stood at the start of the lesson, and
    # arrived facing the wrong way; instead of turning round, he started
    # walking up and down straight away
    assert events == [
        (1481, (67, 3), 1, 'GoToXY', 'return_to_base', 'MR WITHIT'),
        (1534, (62, 3), -1, 'GoToXY', 'walk_up_or_down', 'MR WITHIT')
    ]

    # Eric didn't sit down, so Mr Withit gave him lines
    assert lines == [(1576, 700, 'MR WITHIT', 'SIT_DOWN', None)]

def _write_on_blue_room_blackboard(monkeypatch, capsys, tmp_path, text):
    """Make Eric (starting beside the Blue Room blackboard) write some text on
    it, and return the Demo object, the lines given, and a list of events
    recording when a new line was started on the blackboard, and when the
    blackboard was checked for a combination."""
    inputs = f"""
        5 WRITE
        5 TYPE {text}
        60 ENTER
    """
    events = []
    def setup(d):
        eric = d.eric
        eric.x, eric.y, eric.direction = 6, 3, -1
        blackboard = d.skool.rooms['BlueRoom'].blackboard
        def newline(method=blackboard.newline):
            events.append((d.tick, 'newline', list(blackboard.lines)))
            method()
        def shows(text, in_order=True, method=blackboard.shows):
            result = method(text, in_order)
            events.append((d.tick, 'shows', list(blackboard.lines), text, in_order, result))
            return result
        blackboard.newline, blackboard.shows = newline, shows
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 80, setup=setup)
    return d, lines, events

def test_back_to_skool_write_short_word_on_blackboard(monkeypatch, capsys, tmp_path):
    # Eric writes a word that is shorter than the bike and storeroom
    # combinations (8016 and WZVU)
    d, lines, events = _write_on_blue_room_blackboard(monkeypatch, capsys, tmp_path, 'AB')

    # The word was checked against the bike combination (since the bike is
    # still chained to the tree) and the storeroom combination (since Eric
    # doesn't have the storeroom key), and matched neither (being too short)
    assert events == [
        (62, 'shows', ['AB'], '8016', False, False),
        (62, 'shows', ['AB'], 'WZVU', False, False)
    ]
    assert not d.skool.cast.is_bike_visible()
    assert items.STOREROOM_KEY not in d.eric.inventory

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_write_long_line_on_blackboard(monkeypatch, capsys, tmp_path):
    # Eric writes some text that is too long to fit on one line of the
    # blackboard
    d, lines, events = _write_on_blue_room_blackboard(monkeypatch, capsys, tmp_path, 'HELLOWORLDAGAIN')

    # When the first line was full, a new line was started; the text was then
    # checked against the bike and storeroom combinations (8016 and WZVU),
    # and matched neither (its first four letters being HELL)
    assert events == [
        (57, 'newline', ['HELLOWORLDAG']),
        (71, 'shows', ['HELLOWORLDAG', 'AIN'], '8016', False, False),
        (71, 'shows', ['HELLOWORLDAG', 'AIN'], 'WZVU', False, False)
    ]
    assert d.skool.rooms['BlueRoom'].blackboard.lines == ['HELLOWORLDAG', 'AIN']
    assert not d.skool.cast.is_bike_visible()
    assert items.STOREROOM_KEY not in d.eric.inventory

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_stand_on_bike_saddle_and_sit_down_again(monkeypatch, capsys, tmp_path):
    # The bike is unchained from the start, and stands at the base of the
    # tree (at (100,17)); Eric walks left to it, turns round, gets on, and
    # pedals for a while; he then stands on the saddle, sits back down on it
    # shortly afterwards, and pedals some more
    inputs = """
        1 LEFT 132
        135 RIGHT
        138 MOUNT_BIKE
        142 RIGHT
        146 LEFT
        150 RIGHT
        154 LEFT
        158 RIGHT
        162 LEFT
        166 RIGHT
        170 LEFT
        174 UP
        183 DOWN
        189 RIGHT
        193 LEFT
        197 RIGHT
    """
    events = []
    def setup(d):
        d.skool.unchain_bike()
        eric, bike = d.eric, d.skool.cast.bike
        for c, name in ((bike, 'pedal'), (eric, 'stand_on_saddle'), (eric, 'get_back_on_saddle')):
            def recorded(*args, c=c, name=name, method=getattr(c, name)):
                method(*args)
                events.append((d.tick, name, (eric.x, eric.y), eric.animatory_state, bike.momentum))
            setattr(c, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 200, setup=setup)

    # Eric pedalled the bike eight times, stood on the saddle (one square up
    # and one square back from where he was sitting), rode along standing on
    # the saddle (during which time the bike lost momentum twice as quickly),
    # sat back down on the saddle, and then pedalled three more times
    assert events == [
        (144, 'pedal', (101, 17), 'RIDING_BIKE1', 4),
        (147, 'pedal', (102, 17), 'RIDING_BIKE0', 6),
        (150, 'pedal', (103, 17), 'RIDING_BIKE1', 8),
        (156, 'pedal', (105, 17), 'RIDING_BIKE0', 9),
        (159, 'pedal', (106, 17), 'RIDING_BIKE1', 11),
        (162, 'pedal', (107, 17), 'RIDING_BIKE0', 13),
        (168, 'pedal', (109, 17), 'RIDING_BIKE1', 14),
        (171, 'pedal', (110, 17), 'RIDING_BIKE0', 16),
        (174, 'stand_on_saddle', (110, 16), 'WALK0', 16),
        (183, 'get_back_on_saddle', (113, 17), 'RIDING_BIKE0', 10),
        (189, 'pedal', (115, 17), 'RIDING_BIKE1', 10),
        (195, 'pedal', (117, 17), 'RIDING_BIKE0', 11),
        (198, 'pedal', (118, 17), 'RIDING_BIKE1', 13)
    ]

    # Eric is still riding the bike, sitting on the saddle
    assert d.eric.sitting_on_saddle
    assert type(d.eric.controller).__name__ == 'RideBike'

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_albert_stops_eric_escaping(monkeypatch, capsys, tmp_path):
    # Eric has the water pistol, and the middle-floor window in the boys'
    # skool is open; he goes into the boys' skool (before Albert shuts the
    # skool door), up to the stage, and up again to the middle floor, where he
    # waits until Albert has shut the skool door and is keeping watch outside
    # it; he then waters the plant next to the window, jumps onto the plant
    # pot, steps out of the window when the plant is fully grown, and walks
    # right towards Albert; after Mr Wacker has come to collect him and opened
    # the skool door, Eric walks back into the boys' skool
    inputs = """
        1 GIVE_WATER_PISTOL
        1 LEFT 200
        201 UP 14
        215 RIGHT 25
        1642 FIRE_WATER_PISTOL
        1651 RIGHT 28
        1680 JUMP
        1725 RIGHT
        1765 RIGHT 60
        2032 LEFT 28
    """
    events = []
    beside = {}  # tick -> whether Mr Wacker was beside Eric
    eric_xy = {}  # tick -> Eric's location
    bells = []
    demos = []

    def setup(d):
        demos.append(d)
        eric = d.eric
        d.skool.move_door('MiddleWindow', False)
        albert = d.skool.cast.get('ALBERT')
        def raise_alarm(message, alertee_id, command_list_id, method=albert.raise_alarm):
            method(message, alertee_id, command_list_id)
            events.append((d.tick, 'alarm', (albert.x, albert.y), albert.animatory_state, (eric.x, eric.y),
                           alertee_id, command_list_id))
        albert.raise_alarm = raise_alarm
    main_loop = demo.game.Game._main_loop
    def recording_main_loop(g):
        result = main_loop(g)
        if demos:
            d = demos[0]
            beside[d.tick] = d.skool.cast.get('WACKER').is_beside_eric()
            eric_xy[d.tick] = (d.eric.x, d.eric.y)
        return result
    monkeypatch.setattr(demo.game.Game, '_main_loop', recording_main_loop)
    next_lesson = demo.timetable_mod.Timetable.next_lesson
    def recording_next_lesson(timetable):
        next_lesson(timetable)
        bells.append(demos[0].tick)
    monkeypatch.setattr(demo.timetable_mod.Timetable, 'next_lesson', recording_next_lesson)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 2500, seed=5, setup=setup,
                   options=['--config', 'Cheat,1'])

    # Albert raised his arm when Eric came within range (2-6 paces in front
    # of him), and alerted Mr Wacker (sending him off to shadow Eric); Eric
    # took one more step, and was then stopped by Albert's raised arm
    assert events == [(1785, 'alarm', (103, 17), 'ARM_UP', (100, 17), 'WACKER', 'ShadowEric')]
    assert {eric_xy[t] for t in range(1800, 2032)} == {(101, 17)}

    # Mr Wacker opened the skool door, Eric walked back in, and Mr Wacker
    # stayed beside him until the bell rang, after which he went away (the
    # bell also rang at tick 0, when the first lesson started)
    assert bells == [0, 2405]
    arrived = min(t for t, b in beside.items() if b)
    assert arrived == 2044
    assert all(beside[t] for t in range(arrived, bells[1] + 1))
    assert not beside[2499]
    assert (d.eric.x, d.eric.y) == (94, 17)

    # Mr Wacker gave Eric lines for being out of skool (the tick here is one
    # more than d.tick, following demo.py's '--lines' output) on his way to
    # the skool door, but none after Eric had gone back in
    assert lines == [(2011, 600, 'MR WACKER', 'BACK_TO_SKOOL', None)]

def test_back_to_skool_eric_is_not_a_bird(monkeypatch, capsys, tmp_path):
    # Eric has the water pistol, and every door and window (including the
    # top-floor window in the boys' skool) is opened; he goes into the boys' skool and waits just inside the door
    # until Mr Wacker has gone past on his way to the dinner hall; he then
    # goes up to the stage, up again to the middle floor, and up again to the
    # top floor (outside Mr Wacker's study), waters the plant next to the
    # window, jumps onto the plant pot, and steps out of the window when the
    # plant is fully grown
    inputs = """
        1 GIVE_WATER_PISTOL
        1 OPEN_DOORS
        1 LEFT 160
        461 LEFT 40
        499 UP 14
        513 RIGHT 45
        559 LEFT
        561 UP 30
        593 RIGHT
        596 FIRE_WATER_PISTOL
        605 RIGHT 28
        634 JUMP
        680 RIGHT
    """
    events = []
    def setup(d):
        eric, wacker = d.eric, d.skool.cast.get('WACKER')
        def paralyse(command_list_id, method=eric.paralyse):
            method(command_list_id)
            events.append((d.tick, 'paralysed', (eric.x, eric.y), eric.animatory_state, command_list_id))
        eric.paralyse = paralyse
        def say(words, shift, method=wacker.say):
            if shift == -4:
                events.append((d.tick, 'say', (wacker.x, wacker.y), words))
            return method(words, shift)
        wacker.say = say
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Dinner-Wacker', inputs, 1140, seed=5, setup=setup,
                   options=['--config', 'Cheat,1'])

    # Eric was paralysed when he hit the ground, and Mr Wacker came out of the
    # dinner hall to find him and tell him he's expelled
    assert events == [
        (724, 'paralysed', (97, 17), 'KNOCKED_OUT', 'ExpelEric:NotABird'),
        (1035, 'say', (93, 17), "YOU ARE NOT A BIRD ERIC         YOU'RE EXPELLED")
    ]

    # The game ended (the tick here is one more than d.tick, following
    # demo.py's '--endings' output), and a new one started, with Eric back at
    # his starting position
    assert d.endings == [(1131, 'MR WACKER (expelled)')]
    assert (d.eric.x, d.eric.y) == (133, 17)
    assert not d.eric.expelled

    # Nobody gave Eric lines
    assert lines == []

def test_back_to_skool_miss_take_chases_eric_out(monkeypatch, capsys, tmp_path):
    # Eric walks right into the girls' skool and waits on the bottom floor
    # until Miss Take comes down and spots him; he then walks left until he's
    # just to the right of the skool gate (at x=134), and waits there for a
    # while, before walking back towards the girls' skool
    inputs = """
        1 RIGHT 130
        340 LEFT 120
        700 RIGHT 40
    """
    events = []
    take_states = {}  # tick -> (Miss Take's x-coordinate, direction)
    eric_xs = {}  # tick -> Eric's x-coordinate
    demos = []

    def setup(d):
        demos.append(d)
        take = d.skool.cast.get('TAKE')
        def change_command_list(command_list_id, method=take.change_command_list):
            method(command_list_id)
            events.append((d.tick, command_list_id, (take.x, take.y), (d.eric.x, d.eric.y)))
        take.change_command_list = change_command_list
    main_loop = demo.game.Game._main_loop
    def recording_main_loop(g):
        result = main_loop(g)
        if demos:
            d = demos[0]
            take = d.skool.cast.get('TAKE')
            take_states[d.tick] = (take.x, take.direction)
            eric_xs[d.tick] = d.eric.x
        return result
    monkeypatch.setattr(demo.game.Game, '_main_loop', recording_main_loop)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Dinner-Wacker', inputs, 760, seed=5, setup=setup)

    # Miss Take spotted Eric in the girls' skool as soon as she reached the
    # bottom floor, and started chasing him
    assert events == [(272, 'ChaseEricOut-Take', (176, 17), (165, 17))]

    # Miss Take followed Eric to within 4 paces of the skool gate, and stayed
    # there, facing left (towards Eric), while Eric waited
    assert {eric_xs[t] for t in range(460, 700)} == {136}
    assert {take_states[t] for t in range(530, 700)} == {(140, -1)}

    # When Eric walked back past her, Miss Take turned round to face him, and
    # then followed him
    turned = min(t for t in range(700, 760) if take_states[t][1] > 0)
    assert (turned, take_states[turned], eric_xs[turned]) == (724, (140, 1), 141)
    assert take_states[759] == (141, 1)

    # Miss Take gave Eric lines for being in the girls' skool, and then lines
    # every 62 ticks for being out of skool during dinner
    assert lines == [
        (339, 100, 'MISS TAKE', 'GET_OUT', None),
        (401, 100, 'MISS TAKE', 'BACK_TO_SKOOL', None),
        (487, 400, 'MISS TAKE', 'BACK_TO_SKOOL', None),
        (549, 200, 'MISS TAKE', 'BACK_TO_SKOOL', None),
        (611, 100, 'MISS TAKE', 'BACK_TO_SKOOL', None),
        (673, 400, 'MISS TAKE', 'BACK_TO_SKOOL', None),
        (735, 500, 'MISS TAKE', 'BACK_TO_SKOOL', None)
    ]

def test_skool_daze_expelled_for_too_many_lines(monkeypatch, capsys, tmp_path):
    # Eric has 10000 lines to begin with; he overtakes the teachers on their
    # way up to the staff room, turns round on the top step, and fires his
    # catapult in front of Mr Wacker
    inputs = """
        1 LEFT 118
        119 UP 24
        143 RIGHT
        144 FIRE_CATAPULT
    """
    events = []
    def setup(d):
        d.skool.scoreboard.add_lines(10000)
        eric, wacker, cast = d.eric, d.skool.cast.get('WACKER'), d.skool.cast
        def expel_eric(character_id, command_list_id, method=cast.expel_eric):
            method(character_id, command_list_id)
            events.append((d.tick, 'expel', character_id, command_list_id, d.skool.scoreboard.lines))
        cast.expel_eric = expel_eric
        def say(words, shift, method=wacker.say):
            if shift == -4:
                events.append((d.tick, 'say', (wacker.x, wacker.y), (eric.x, eric.y), words))
            return method(words, shift)
        wacker.say = say
    # demo.py raises the lines limit to stop Eric being expelled; restore the
    # game's default limit
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 370, setup=setup,
                   options=['--config', 'MaxLines,10000'])

    # Mr Wacker gave Eric lines for firing his catapult, taking him over the
    # limit
    assert lines == [(151, 600, 'MR WACKER', 'NO_CATAPULTS', None)]

    # Mr Wacker was sent to find Eric, and when he did, told him he was
    # expelled
    assert events == [
        (150, 'expel', 'WACKER', 'ExpelEric:TooManyLines', 10600),
        (168, 'say', (12, 10), (13, 11),
         "YOU HAVE OVER 10000 LINES TO WRITE ERIC. DON'T COME BACK TO SCHOOL TILL YOU HAVE DONE THEM ALL. . . .")
    ]

    # The game ended (the tick here is one more than d.tick, following
    # demo.py's '--endings' output), and a new one started, with Eric back at
    # his starting position and no lines
    assert d.endings == [(363, 'MR WACKER (expelled)')]
    assert (d.eric.x, d.eric.y) == (48, 17)
    assert d.skool.scoreboard.lines == 0
    assert not d.eric.expelled

def test_skool_daze_high_score_set_when_eric_is_expelled(monkeypatch, capsys, tmp_path):
    # Eric has 10000 lines to begin with; he walks to the staff room stairs,
    # climbs part of the way up, turns round in front of Mr Wacker, and fires
    # his catapult at the shield at (26,14)
    inputs = """
        0 LEFT 118
        118 UP 16
        134 RIGHT
        136 FIRE_CATAPULT
    """
    events = []
    def setup(d):
        d.skool.scoreboard.add_lines(10000)
        scoreboard = d.skool.scoreboard
        def add_to_score(addend, method=scoreboard.add_to_score):
            method(addend)
            events.append((d.tick, 'score', addend, scoreboard.score, scoreboard.hiscore))
        scoreboard.add_to_score = add_to_score
        def reinitialise(method=scoreboard.reinitialise):
            method()
            events.append((d.tick, 'reinitialise', scoreboard.score, scoreboard.hiscore))
        scoreboard.reinitialise = reinitialise
    # demo.py raises the lines limit to stop Eric being expelled; restore the
    # game's default limit
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 370, setup=setup,
                   options=['--config', 'MaxLines,10000'])

    # Mr Wacker gave Eric lines for firing his catapult, taking him over the
    # limit
    assert lines == [(143, 400, 'MR WACKER', 'NO_CATAPULTS', None)]

    # The pellet hit the shield, scoring 400 points; then Mr Wacker expelled
    # Eric, and when the game ended, the score became the new high score (and
    # was then reset to zero)
    assert events == [
        (174, 'score', 400, 400, 0),
        (359, 'reinitialise', 0, 400)
    ]
    assert d.endings == [(360, 'MR WACKER (expelled)')]
    assert d.skool.scoreboard.lines == 0

def test_skool_daze_jump_at_safe_without_combination(monkeypatch, capsys, tmp_path):
    # All the shields are flashing, but the safe combination is not written
    # on any blackboard; Eric stands under the safe and jumps
    inputs = """
        5 JUMP
    """
    events = []
    def setup(d):
        skool = d.skool
        for shield in skool.shields:
            shield.flash()
        skool.shield_mode = 2
        d.eric.x, d.eric.y, d.eric.direction = 10, 10, -1
        def got_safe_combination(method=skool.got_safe_combination):
            result = method()
            events.append((d.tick, (d.eric.x, d.eric.y), d.eric.animatory_state, result))
            return result
        skool.got_safe_combination = got_safe_combination
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 30, setup=setup)

    # When Eric reached the top of his jump, the skool checked for the safe
    # combination on the blackboards, and didn't find it
    assert events == [(11, (10, 9), 'ARM_UP', False)]

    # So the safe didn't open, and Eric scored no points
    assert d.skool.shield_mode == 2
    assert not d.skool.safe.flashing
    assert d.skool.scoreboard.score == 0

    # Nobody gave Eric lines
    assert lines == []

def test_skool_daze_einstein_knocked_out_of_seat_while_speaking(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room), and stands in front of Einstein's seat (the back seat),
    # facing him; when Einstein is part of the way through answering Mr
    # Withit's first question, Eric punches him
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 94
        1150 HIT
    """
    events = []
    shifts = {}  # tick -> how far through his answer Einstein is
    def setup(d):
        einstein, withit = d.skool.cast.get('SWOT'), d.skool.cast.get('WITHIT')
        def say(words, shift, method=einstein.say):
            if shift == -4:
                events.append((d.tick, 'say', words))
            if events:
                shifts[d.tick] = shift
            return method(words, shift)
        einstein.say = say
        for name in ('deck', 'stand_up', 'sit', 'remove_bubble'):
            def recorded(*args, name=name, method=getattr(einstein, name)):
                chair = einstein.chair()
                method(*args)
                if events:
                    events.append((d.tick, name, (einstein.x, einstein.y), einstein.animatory_state,
                                   bool(einstein.bubble), (chair or einstein.chair()).x))
            setattr(einstein, name, recorded)
        def withit_say(words, shift, method=withit.say):
            if shift == -4 and events:
                events.append((d.tick, 'Withit says', words))
            return method(words, shift)
        withit.say = withit_say
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 1300, setup=setup)

    # Einstein started answering Mr Withit's question, and was knocked out of
    # his seat (with his speech bubble still showing); he got up, sat back
    # down in the same seat, and finished his answer, after which Mr Withit
    # asked the next question
    assert events == [
        (1132, 'say', 'Please Sir I cannot tell a lie . . it is Helsinki'),
        (1162, 'deck', (37, 10), 'KNOCKED_OUT', True, 37),
        (1194, 'stand_up', (37, 10), 'WALK0', True, 37),
        (1197, 'sit', (37, 10), 'SITTING_ON_CHAIR', True, 37),
        (1259, 'remove_bubble', (37, 10), 'SITTING_ON_CHAIR', False, 37),
        (1263, 'Withit says', "WHAT'S THE CAPITAL OF Chile?")
    ]

    # Einstein didn't speak while he was out of his seat, and resumed his
    # answer where he left off as soon as he sat back down
    assert [t for t in shifts if 1159 < t < 1197] == []
    assert (shifts[1159], shifts[1197]) == (4, 5)
    assert sorted(shifts.values()) == list(range(-4, 26))

    # Mr Withit gave Eric lines for punching Einstein, and also for standing
    # instead of sitting down (the ticks here are one more than d.tick,
    # following demo.py's '--lines' output); earlier, on the top floor, Mr
    # Creak gave Boy Wander lines after Boy Wander's catapult pellet knocked
    # him over
    assert lines == [
        (591, 400, 'MR CREAK', 'NEVER_AGAIN', 'BOY WANDER'),
        (1028, 100, 'MR WITHIT', 'SIT_DOWN', None),
        (1090, 200, 'MR WITHIT', 'SIT_DOWN', None),
        (1152, 200, 'MR WITHIT', 'SIT_DOWN', None),
        (1160, 200, 'MR WITHIT', 'NO_HITTING', None),
        (1217, 500, 'MR WITHIT', 'SIT_DOWN', None),
        (1279, 100, 'MR WITHIT', 'SIT_DOWN', None)
    ]

def test_skool_daze_boy_wander_gets_up_to_write_on_blackboard(monkeypatch, capsys, tmp_path):
    # With seed 2, Boy Wander ends Mr Wacker's Map Room lesson sitting in the
    # Exam Room at (51,10), with the blackboard clean; Eric gets up (after
    # being knocked out), goes to the Exam Room, and sits in Boy Wander's seat
    # three times, pushing him along to (45,10), which is also where he goes
    # to write on the blackboard at the start of the next lesson
    inputs = """
        2000 SIT_STAND
        2010 RIGHT 95
        2105 UP 40
        2145 LEFT 109
        2265 SIT_STAND
        2303 SIT_STAND
        2306 LEFT 8
        2316 SIT_STAND
        2359 SIT_STAND
        2362 LEFT 8
        2372 SIT_STAND
    """
    events = []
    def setup(d):
        boy_wander = d.skool.cast.get('TEARAWAY')
        def dethrone(method=boy_wander.dethrone):
            if d.tick >= 2000:
                events.append((d.tick, 'dethrone', (boy_wander.x, boy_wander.y)))
            method()
        boy_wander.dethrone = dethrone
        execute = ai.WriteOnBoard.execute
        def recorded(command):
            c = command.character
            was_sitting = c.is_sitting()
            dirty = bool(d.skool.rooms['ExamRoom'].blackboard_dirty())
            val = execute(command)
            if c is boy_wander and was_sitting:
                events.append((d.tick, 'WriteOnBoard', (c.x, c.y), dirty, c.animatory_state, val))
            return val
        monkeypatch.setattr(ai.WriteOnBoard, 'execute', recorded)
        def write_on_board(message, index, method=boy_wander.write_on_board):
            if index == 1 and d.tick >= 2000:
                events.append((d.tick, 'write_on_board', (boy_wander.x, boy_wander.y), message))
            return method(message, index)
        boy_wander.write_on_board = write_on_board
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Wacker-MapRoom', inputs, 2500, seed=2, setup=setup)

    # Eric knocked Boy Wander out of his seat at (51,10), (49,10) and (47,10);
    # when the next lesson started, Boy Wander went to the blackboard (which
    # he was already beside) and began writing on it while still sitting at
    # (45,10), so he stood up first, and then wrote on the blackboard
    assert events == [
        (2265, 'dethrone', (51, 10)),
        (2317, 'dethrone', (49, 10)),
        (2373, 'dethrone', (47, 10)),
        (2435, 'WriteOnBoard', (45, 10), False, 'WALK0', None),
        (2440, 'write_on_board', (45, 10), 'i hate^fizziks')
    ]
    assert d.skool.rooms['ExamRoom'].blackboard_dirty()

def test_skool_daze_dinner_duty_restarts_if_too_early(monkeypatch, capsys, tmp_path):
    # Mr Withit (on dinner duty) starts the lesson 2 paces from the far end of
    # the dinner hall (instead of outside the staff room), so he reaches the
    # near end before it's time to start dinner
    events = []
    withit_xs = [60]  # Mr Withit's x-coordinates, as they change
    demos = []
    def setup(d):
        demos.append(d)
        withit = d.skool.cast.get('WITHIT')
        assert (withit.x, withit.y) == (10, 17)
        withit.x = 60
        for name in ('restart_command_list', 'deck', 'set_home_room'):
            def recorded(*args, name=name, method=getattr(withit, name)):
                events.append((d.tick, name, (withit.x, withit.y), d.skool.is_time_to_start_lesson()))
                return method(*args)
            setattr(withit, name, recorded)
    main_loop = demo.game.Game._main_loop
    def recording_main_loop(g):
        result = main_loop(g)
        if demos:
            d = demos[0]
            withit = d.skool.cast.get('WITHIT')
            if withit.x != withit_xs[-1]:
                withit_xs.append(withit.x)
                if withit.x in (33, 62):
                    events.append((d.tick, 'reach', (withit.x, withit.y), d.skool.is_time_to_start_lesson()))
        return result
    monkeypatch.setattr(demo.game.Game, '_main_loop', recording_main_loop)
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Dinner-Withit', '', 1000, setup=setup)

    # Mr Withit walked to the far end of the dinner hall (DinnerHall:FarEnd,
    # at x=62) and then to the near end (DinnerHall:NearEnd, at x=33); it
    # wasn't time to start dinner yet, so he restarted his command list (when
    # he had finished his last stride), walked to the far end and back again
    # (being knocked over by a catapult pellet on the way), and then started
    # dinner
    assert events == [
        (22, 'reach', (62, 17), False),
        (317, 'reach', (33, 17), False),
        (322, 'restart_command_list', (33, 17), False),
        (505, 'deck', (51, 17), False),
        (696, 'reach', (62, 17), True),
        (991, 'reach', (33, 17), True),
        (996, 'set_home_room', (33, 17), True)
    ]
    assert withit_xs == list(range(60, 63)) + list(range(61, 32, -1)) + list(range(34, 63)) + list(range(61, 32, -1))
    assert d.skool.get_home_room().name == 'DINNER'

    # Mr Withit gave Eric lines after being knocked over (the tick here is one
    # more than d.tick, following demo.py's '--lines' output)
    assert lines == [(546, 100, 'MR WITHIT', 'NEVER_AGAIN', None)]

def test_back_to_skool_boy_too_late_to_sit_for_assembly(monkeypatch, capsys, tmp_path):
    # Eric follows one of the little boys (BOY09) to the assembly hall,
    # throwing punches now and then (none of which knock him over); after
    # assembly has started, while the boy is still walking about (instead of
    # sitting down), Eric knocks him over three times, so that he doesn't
    # start looking for a spot to sit until assembly has finished (these
    # inputs were found by a script that steered Eric to a spot two or three
    # paces in front of the boy and punched him whenever possible); the punches
    # that don't knock the boy over are still needed, because each one keeps
    # Eric busy for a few ticks, alerts any teachers nearby (who stop to give
    # lines), and uses a random number (for the sound effect), all of which
    # affect the timings that follow; removing any of them makes the test fail
    inputs = """
        3 LEFT 85
        91 RIGHT 1
        95 HIT
        110 LEFT 35
        148 RIGHT 1
        150 HIT
        165 LEFT 35
        203 RIGHT 1
        205 HIT
        220 LEFT 35
        258 RIGHT 1
        260 HIT
        275 LEFT 35
        313 RIGHT 1
        315 HIT
        332 LEFT 23
        358 RIGHT 23
        384 LEFT 31
        418 RIGHT 31
        452 LEFT 11
        466 RIGHT 11
        480 LEFT 19
        502 RIGHT 19
        524 LEFT 23
        550 RIGHT 23
        576 LEFT 31
        610 RIGHT 39
        652 LEFT 1
        658 HIT
        673 LEFT 33
        709 RIGHT 1
        713 HIT
        732 LEFT 1
        734 RIGHT 23
        760 LEFT 1
        766 HIT
        783 RIGHT 3
        789 LEFT 1
        843 HIT
        860 RIGHT 3
        868 LEFT 1
        922 HIT
    """
    events = []
    demos = []
    def setup(d):
        demos.append(d)
        boy = d.skool.cast.get('BOY09')
        def deck(*args, method=boy.deck):
            method(*args)
            events.append((d.tick, 'deck', (boy.x, boy.y)))
        boy.deck = deck
        def signal(signal_id, method=d.skool.signal):
            events.append((d.tick, 'signal', signal_id))
            method(signal_id)
        d.skool.signal = signal
    find_spot_to_sit = ai.SitForAssembly.find_spot_to_sit
    def recording_find_spot_to_sit(command):
        result = find_spot_to_sit(command)
        if command.character.character_id == 'BOY09':
            events.append((demos[0].tick, 'find_spot_to_sit', result is command))
        return result
    monkeypatch.setattr(ai.SitForAssembly, 'find_spot_to_sit', recording_find_spot_to_sit)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Assembly', inputs, 1010, setup=setup)

    # The boy was knocked over three times while walking about after assembly
    # started; by the time he started looking for a spot to sit, assembly had
    # finished, so SitForAssembly terminated without making him sit down
    assert events == [
        (716, 'signal', 'AssemblyStarted'),
        (775, 'deck', (72, 17)),
        (852, 'deck', (73, 17)),
        (931, 'deck', (74, 17)),
        (971, 'signal', 'AssemblyFinished'),
        (1003, 'find_spot_to_sit', True)
    ]
    boy = d.skool.cast.get('BOY09')
    assert not boy.is_sitting()
    assert [type(c).__name__ for c in boy.command_list.stack] == ['GoToRandomLocation']

    # Mr Creak, Mr Withit and Mr Wacker gave Eric lines for throwing punches,
    # and Mr Withit and Mr Wacker gave him lines for not sitting down for
    # assembly (the ticks here are one more than d.tick, following demo.py's
    # '--lines' output)
    assert lines == [
        (322, 100, 'MR CREAK', 'NO_HITTING', None),
        (720, 600, 'MR WITHIT', 'NO_HITTING', None),
        (729, 600, 'MR WITHIT', 'SIT_DOWN', None),
        (761, 700, 'MR WACKER', 'SIT_DOWN', None),
        (773, 700, 'MR WACKER', 'NO_HITTING', None),
        (796, 800, 'MR WITHIT', 'SIT_DOWN', None),
        (828, 600, 'MR WACKER', 'SIT_DOWN', None),
        (850, 100, 'MR WACKER', 'NO_HITTING', None),
        (863, 500, 'MR WITHIT', 'SIT_DOWN', None),
        (895, 100, 'MR WACKER', 'SIT_DOWN', None),
        (929, 600, 'MR WACKER', 'NO_HITTING', None),
        (960, 800, 'MR WACKER', 'SIT_DOWN', None)
    ]

def test_back_to_skool_assembly_finishes_before_boy_sits_down(monkeypatch, capsys, tmp_path):
    # Eric follows one of the little boys (BOY09) to the assembly hall, and
    # punches him now and then, as in the previous test (with the same inputs
    # up to tick 868), knocking him over twice after assembly has started;
    # but here Eric stops punching sooner, so the boy starts looking for a
    # spot to sit before assembly has finished; while the boy is walking back
    # to that spot, Eric runs past him, turns round, and knocks him over
    # again before he can sit down (these inputs were found by the same
    # script, followed by some trial and error; as in the previous test, the
    # punches that don't knock the boy over are still needed, because they
    # affect the timings that follow)
    inputs = """
        3 LEFT 85
        91 RIGHT 1
        95 HIT
        110 LEFT 35
        148 RIGHT 1
        150 HIT
        165 LEFT 35
        203 RIGHT 1
        205 HIT
        220 LEFT 35
        258 RIGHT 1
        260 HIT
        275 LEFT 35
        313 RIGHT 1
        315 HIT
        332 LEFT 23
        358 RIGHT 23
        384 LEFT 31
        418 RIGHT 31
        452 LEFT 11
        466 RIGHT 11
        480 LEFT 19
        502 RIGHT 19
        524 LEFT 23
        550 RIGHT 23
        576 LEFT 31
        610 RIGHT 39
        652 LEFT 1
        658 HIT
        673 LEFT 33
        709 RIGHT 1
        713 HIT
        732 LEFT 1
        734 RIGHT 23
        760 LEFT 1
        766 HIT
        783 RIGHT 3
        789 LEFT 1
        843 HIT
        860 RIGHT 3
        868 LEFT 1
        920 LEFT 16
        937 RIGHT
        944 HIT
    """
    events = []
    demos = []
    def setup(d):
        demos.append(d)
        boy = d.skool.cast.get('BOY09')
        def deck(*args, method=boy.deck):
            method(*args)
            events.append((d.tick, 'deck', (boy.x, boy.y)))
        boy.deck = deck
        def signal(signal_id, method=d.skool.signal):
            events.append((d.tick, 'signal', signal_id))
            method(signal_id)
        d.skool.signal = signal
    for name in ('find_spot_to_sit', 'sit_down'):
        def recorded(command, name=name, method=getattr(ai.SitForAssembly, name)):
            result = method(command)
            boy = command.character
            if boy.character_id == 'BOY09':
                outcome = 'finished' if result is command else ('turned' if result is False else 'continued')
                events.append((demos[0].tick, name, (boy.x, boy.y), outcome))
            return result
        monkeypatch.setattr(ai.SitForAssembly, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Assembly', inputs, 1020, setup=setup)

    # The boy was knocked over twice while walking about after assembly
    # started, and then found a spot to sit before assembly finished; he was
    # knocked over again on his way to that spot, and by the time he was
    # ready to sit down, assembly had finished, so SitForAssembly terminated
    # without making him sit down
    assert events == [
        (716, 'signal', 'AssemblyStarted'),
        (775, 'deck', (72, 17)),
        (852, 'deck', (73, 17)),
        (938, 'find_spot_to_sit', (75, 17), 'continued'),
        (953, 'deck', (74, 17)),
        (973, 'signal', 'AssemblyFinished'),
        (1015, 'sit_down', (74, 17), 'finished')
    ]
    boy = d.skool.cast.get('BOY09')
    assert not boy.is_sitting()
    assert [type(c).__name__ for c in boy.command_list.stack] == ['GoToRandomLocation']

    # Mr Creak, Mr Withit and Mr Wacker gave Eric lines for throwing punches,
    # and Mr Withit and Mr Wacker gave him lines for not sitting down for
    # assembly (the ticks here are one more than d.tick, following demo.py's
    # '--lines' output)
    assert lines == [
        (322, 100, 'MR CREAK', 'NO_HITTING', None),
        (720, 600, 'MR WITHIT', 'NO_HITTING', None),
        (729, 600, 'MR WITHIT', 'SIT_DOWN', None),
        (761, 700, 'MR WACKER', 'SIT_DOWN', None),
        (773, 700, 'MR WACKER', 'NO_HITTING', None),
        (796, 800, 'MR WITHIT', 'SIT_DOWN', None),
        (828, 600, 'MR WACKER', 'SIT_DOWN', None),
        (850, 100, 'MR WACKER', 'NO_HITTING', None),
        (863, 500, 'MR WITHIT', 'SIT_DOWN', None),
        (895, 100, 'MR WACKER', 'SIT_DOWN', None),
        (927, 300, 'MR WITHIT', 'SIT_DOWN', None),
        (951, 500, 'MR WACKER', 'NO_HITTING', None),
        (962, 500, 'MR WITHIT', 'SIT_DOWN', None)
    ]

def test_skool_daze_little_boy_waits_for_eric_to_finish_writing(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room (via the stairs up to the staff room) and
    # waits by the blackboard; when the little boy who has a message for him
    # (that Einstein is going to tell Mr Wacker what he's up to) is nearly
    # there, Eric starts writing on the blackboard, and he doesn't press
    # ENTER (to finish writing) until the boy has been waiting beside him for
    # a while
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 54
        1000 WRITE
        1100 ENTER
    """
    attempts = []
    events = []
    def setup(d):
        boy = d.skool.cast.get('BOY10')
        def freeze_eric(method=boy.freeze_eric):
            frozen = method()
            attempts.append((d.tick, (boy.x, boy.y), d.eric.writing, frozen, d.skool.timetable.counter))
            return frozen
        boy.freeze_eric = freeze_eric
        def say(words, shift, method=boy.say):
            if shift == -4:
                events.append((d.tick, 'say', words))
            return method(words, shift)
        boy.say = say
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-SwotGrass', inputs, 1110, setup=setup)

    # The boy arrived beside Eric (within 4 paces of him) while Eric was
    # writing, and so couldn't freeze him; he tried again every time he
    # moved, with the skool clock stopped, until Eric had finished writing,
    # and then froze him and started giving him the message
    assert attempts[0] == (1039, (21, 10), True, False, 1919)
    assert [a[0] for a in attempts] == list(range(1039, 1106, 3))
    assert {a[1:] for a in attempts[:-1]} == {((21, 10), True, False, 1919)}
    assert attempts[-1] == (1105, (21, 10), False, True, 1919)
    assert events == [
        (1105, 'say', "EINSTEIN is going to tell MR WACKER what you're up to. You must stop him getting to his "
                      "study this break         Press 'U' if you understood")
    ]
    assert (d.eric.x, d.eric.y) == (25, 10)
    assert d.eric.frozen

    # Teachers walking past the White Room told Eric to get along (the ticks
    # here are one more than d.tick, following demo.py's '--lines' output)
    assert lines == [
        (204, 500, 'MR WACKER', 'GET_ALONG', None),
        (236, 500, 'MR ROCKITT', 'GET_ALONG', None),
        (548, 600, 'MR WITHIT', 'GET_ALONG', None),
        (580, 200, 'MR CREAK', 'GET_ALONG', None),
        (692, 600, 'MR WITHIT', 'GET_ALONG', None)
    ]

@pytest.mark.parametrize('action,attempts', [
    ('HIT', [
        (1039, (25, 10), 'WALK2', 'Hit', False),
        (1043, (25, 10), 'HITTING1', 'Hit', False),
        (1046, (25, 10), 'HITTING1', 'Hit', False),
        (1049, (25, 10), 'WALK0', 'Hit', False),
        (1052, (25, 10), 'WALK0', None, True)
    ]),
    ('FIRE_CATAPULT', [
        (1039, (25, 10), 'WALK2', 'FireCatapult', False),
        (1042, (25, 10), 'CATAPULT1', 'FireCatapult', False),
        (1045, (25, 10), 'CATAPULT1', 'FireCatapult', False),
        (1048, (25, 10), 'WALK0', 'FireCatapult', False),
        (1051, (25, 10), 'WALK0', None, True)
    ]),
    ('JUMP', [
        (1039, (25, 10), 'WALK2', 'Jump', False),
        (1042, (25, 9), 'ARM_UP', 'Jump', False),
        (1046, (25, 10), 'WALK2', 'Jump', False),
        (1049, (25, 10), 'WALK2', None, True)
    ])
], ids=['HIT', 'FIRE_CATAPULT', 'JUMP'])
def test_skool_daze_little_boy_waits_for_eric_to_finish_action(monkeypatch, capsys, tmp_path, action, attempts):
    # Eric goes to the White Room (via the stairs up to the staff room) and
    # waits by the blackboard; just before the little boy who has a message
    # for him (that Einstein is going to tell Mr Wacker what he's up to)
    # arrives, Eric hits, fires his catapult or jumps
    inputs = f"""
        1 LEFT 118
        119 UP 28
        147 RIGHT 54
        1036 {action}
    """
    recorded_attempts = []
    events = []
    def setup(d):
        eric, boy = d.eric, d.skool.cast.get('BOY10')
        def freeze_eric(method=boy.freeze_eric):
            controller = type(eric.controller).__name__ if eric.controller else None
            state = ((eric.x, eric.y), eric.animatory_state, controller)
            frozen = method()
            recorded_attempts.append((d.tick, *state, frozen))
            return frozen
        boy.freeze_eric = freeze_eric
        def say(words, shift, method=boy.say):
            if shift == -4:
                events.append((d.tick, 'say', words))
            return method(words, shift)
        boy.say = say
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-SwotGrass', inputs, 1060, setup=setup)

    # The boy arrived beside Eric while Eric was busy, and so couldn't freeze
    # him; he tried again every time he moved, until Eric had finished what he
    # was doing (and was standing on the floor again), and then froze him and
    # started giving him the message
    assert recorded_attempts == attempts
    assert events == [
        (attempts[-1][0], 'say', "EINSTEIN is going to tell MR WACKER what you're up to. You must stop him getting to "
                                 "his study this break         Press 'U' if you understood")
    ]
    assert d.eric.frozen

@pytest.mark.parametrize('action,attempts', [
    ('CATCH', [
        (475, 'BENDING_OVER', 'Catch', False),
        (478, 'WALK0', None, True)
    ]),
    ('RELEASE_MICE', [
        (475, 'BENDING_OVER', 'ReleaseMice', False),
        (478, 'WALK0', None, True)
    ]),
    ('DUMP_WATER_PISTOL', [
        (475, 'BENDING_OVER', 'DumpWaterPistol', False),
        (478, 'WALK0', None, True)
    ]),
    ('FIRE_WATER_PISTOL', [
        (475, 'WATERPISTOL', 'FireWaterPistol', False),
        (478, 'WALK0', 'FireWaterPistol', False),
        (481, 'WALK0', None, True)
    ]),
    ('DROP_STINKBOMB', [
        (475, 'ARM_UP', 'DropStinkbomb', False),
        (478, 'WALK0', 'DropStinkbomb', False),
        (481, 'WALK0', None, True)
    ])
], ids=['CATCH', 'RELEASE_MICE', 'DUMP_WATER_PISTOL', 'FIRE_WATER_PISTOL', 'DROP_STINKBOMB'])
def test_back_to_skool_wacker_waits_for_eric_to_finish_action(monkeypatch, capsys, tmp_path, action, attempts):
    # Eric has 10000 lines to begin with, and is given the water pistol,
    # stinkbombs and mice; he adds some lines (taking him over the limit), and
    # then waits where he is for Mr Wacker to come and expel him; just before
    # Mr Wacker arrives, Eric bends over (to catch or release mice, or drop the
    # water pistol), fires the water pistol, or drops a stinkbomb
    inputs = f"""
        1 GIVE_ALL
        5 ADD_LINES
        471 {action}
    """
    recorded_attempts = []
    def setup(d):
        d.skool.scoreboard.add_lines(10000)
        eric, wacker = d.eric, d.skool.cast.get('WACKER')
        def freeze_eric(method=wacker.freeze_eric):
            controller = type(eric.controller).__name__ if eric.controller else None
            state = (eric.animatory_state, controller)
            frozen = method()
            recorded_attempts.append((d.tick, *state, frozen))
            return frozen
        wacker.freeze_eric = freeze_eric
    # demo.py raises the lines limit to stop Eric being expelled; restore the
    # game's default limit
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 500, setup=setup,
                   options=['--config', 'MaxLines,10000', '--config', 'Cheat,1'])

    # Mr Wacker arrived beside Eric while Eric was busy, and so couldn't freeze
    # him; he tried again every time he moved, until Eric had finished what he
    # was doing, and then froze him
    assert recorded_attempts == attempts
    assert (d.eric.x, d.eric.y) == (133, 17)
    assert d.eric.frozen

def test_skool_daze_wacker_expels_eric_after_adding_lines(monkeypatch, capsys, tmp_path):
    # Eric has 8100 lines to begin with; he walks right to the gym, where the
    # little boy waiting there tells him that Boy Wander has hidden a
    # pea-shooter on the fire escape, and that Eric will get lines if Mr
    # Wacker gets there first (Eric presses 'U' as soon as the boy starts
    # speaking); Eric then goes up to the top floor and waits near the fire
    # escape, making no attempt to stop Mr Wacker getting there (as in
    # test_skool_daze_pea_shooter_found_by_wacker in test_special_playtimes.py)
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
    events = []
    demos = []
    def setup(d):
        demos.append(d)
        d.skool.scoreboard.add_lines(8100)
        wacker = d.skool.cast.get('WACKER')
        def say(words, shift, method=wacker.say):
            if shift == -4:
                events.append((d.tick, 'say', (wacker.x, wacker.y), (d.eric.x, d.eric.y), words))
            return method(words, shift)
        wacker.say = say
        def set_command_list_template(template, method=wacker.set_command_list_template):
            events.append((d.tick, 'command list', template.command_list_id, [type(c).__name__ for c in wacker.command_list.stack]))
            method(template)
        wacker.set_command_list_template = set_command_list_template
    is_interruptible = ai.AddLines.is_interruptible
    def recording_is_interruptible(command):
        result = is_interruptible(command)
        events.append((demos[0].tick, 'AddLines.is_interruptible', command.character.character_id, result))
        return result
    monkeypatch.setattr(ai.AddLines, 'is_interruptible', recording_is_interruptible)
    # demo.py raises the lines limit to stop Eric being expelled; restore the
    # game's default limit
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-HiddenPeaShooter', inputs, 2400, setup=setup,
                   options=['--config', 'MaxLines,10000'])

    # Mr Wacker found the pea-shooter, and told Eric he would get 2000 lines;
    # when those lines (added by Mr Wacker's AddLines command) took Eric over
    # the limit, Mr Wacker's command list was switched (while the AddLines
    # command was still on his command stack, so the command was asked
    # whether it was interruptible) to the one for expelling Eric for having
    # too many lines; Mr Wacker, still beside Eric, then told him he was
    # expelled, and when the game had ended and a new one started, Mr
    # Wacker's command list was set for the first lesson again
    assert events == [
        (0, 'command list', 'HiddenPeaShooter-Wacker', []),
        (1944, 'say', (90, 3), (86, 3), 'TAKE 2000 LINES YOU NASTY BOY'),
        (2012, 'command list', 'ExpelEric:TooManyLines', ['AddLines']),
        (2012, 'AddLines.is_interruptible', 'WACKER', False),
        (2012, 'say', (90, 3), (86, 3),
         "YOU HAVE OVER 10000 LINES TO WRITE ERIC. DON'T COME BACK TO SCHOOL TILL YOU HAVE DONE THEM ALL. . . ."),
        (2208, 'command list', 'HiddenPeaShooter-Wacker', [])
    ]

    # Mr Wacker's 2000 lines were the only lines Eric got, and the game
    # ended with Eric expelled (the ticks here are one more than d.tick,
    # following demo.py's '--lines' and '--endings' output); in the new game,
    # Eric is back at his starting position with no lines
    assert lines == [(2013, 2000, 'MR WACKER', 'AddLines', None)]
    assert d.endings == [(2208, 'MR WACKER (expelled)')]
    assert (d.eric.x, d.eric.y) == (48, 17)
    assert d.skool.scoreboard.lines == 0
    assert not d.eric.expelled
