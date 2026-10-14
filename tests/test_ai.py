from pyskooltest import demo, run
from pyskool import ai, items

def _desk_with(skool, item):
    """Return the (room ID, x-coordinate) of the desk containing an item, or
    None if no desk contains it."""
    for room_id, room in skool.rooms.items():
        for desk in room.desks:
            if desk.contents == item:
                return (room_id, desk.x)

def _give_water_pistol(d):
    """Take the water pistol out of whichever desk it's in, and give it to
    Eric."""
    for room in d.skool.rooms.values():
        for desk in room.desks:
            if desk.contents == items.WATER_PISTOL:
                desk.empty()
    d.eric.inventory.add(items.WATER_PISTOL)

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

def test_back_to_skool_fire_water_pistol_at_floor(monkeypatch, capsys, tmp_path):
    # Eric has the water pistol; he walks left, away from the plant pots by
    # the skool gate, and fires it to the left, away from any cups or plants
    inputs = """
        1 LEFT 20
        30 FIRE_WATER_PISTOL
    """
    events = []
    def setup(d):
        _give_water_pistol(d)
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
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 60, seed=5, setup=setup)

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
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-Mumps', inputs, 460, setup=setup,
                   options=['--no-auto-understood'])

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

def test_back_to_skool_fall_off_dying_plant(monkeypatch, capsys, tmp_path):
    # Eric has the water pistol; he walks right to a spot 7 paces to the right
    # of the plant pot just right of the skool gate, turns round, fires the
    # water pistol at the plant pot, walks to it, and jumps onto it before the
    # plant starts growing
    inputs = """
        1 RIGHT 38
        45 LEFT
        50 FIRE_WATER_PISTOL
        59 LEFT 28
        88 JUMP
    """
    events = []
    def setup(d):
        _give_water_pistol(d)
        plant = d.skool.plant_pots['RightGatePlant'].plant
        for name in ('grow', 'appear', 'finish_growing', 'die'):
            def recorded(name=name, method=getattr(plant, name)):
                method()
                events.append((d.tick, name, (d.eric.x, d.eric.y)))
            setattr(plant, name, recorded)
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 160, seed=5, setup=setup)

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
        _give_water_pistol(d)
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
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'RevisionLibrary-1', inputs, 2500, seed=5, setup=setup)

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
    # Eric has the water pistol, and the top-floor window in the boys' skool
    # is open; he goes into the boys' skool and waits just inside the door
    # until Mr Wacker has gone past on his way to the dinner hall; he then
    # goes up to the stage, up again to the middle floor, and up again to the
    # top floor (outside Mr Wacker's study), waters the plant next to the
    # window, jumps onto the plant pot, and steps out of the window when the
    # plant is fully grown
    inputs = """
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
        _give_water_pistol(d)
        d.skool.move_door('UpperWindow', False)
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
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Dinner-Wacker', inputs, 1140, seed=5, setup=setup)

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
        # demo.py raises the lines limit to stop Eric being expelled; restore
        # the game's default limit
        d.skool.max_lines = 10000
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
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 370, setup=setup)

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

def test_skool_daze_wacker_expels_eric_after_adding_lines(monkeypatch, capsys, tmp_path):
    # Eric has 8100 lines to begin with; he walks right to the gym, where the
    # little boy waiting there tells him that Boy Wander has hidden a
    # pea-shooter on the fire escape, and that Eric will get lines if Mr
    # Wacker gets there first; Eric then goes up to the top floor and waits
    # near the fire escape, making no attempt to stop Mr Wacker getting there
    # (as in test_skool_daze_pea_shooter_found_by_wacker in
    # test_special_playtimes.py)
    inputs = """
        1 RIGHT 184
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
        # demo.py raises the lines limit to stop Eric being expelled; restore
        # the game's default limit
        d.skool.max_lines = 10000
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
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-HiddenPeaShooter', inputs, 2400, setup=setup)

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
