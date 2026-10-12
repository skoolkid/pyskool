from pyskooltest import run

def test_skool_daze_sit_on_floor(monkeypatch, capsys, tmp_path):
    # Eric walks left to meet Mr Withit, who is walking right along the bottom
    # floor, and sits down in front of him
    inputs = """
        1 LEFT 100
        101 SIT_STAND
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 110)

    # Mr Withit told Eric to get off the floor
    assert lines == [(106, 500, 'MR WITHIT', 'GET_UP', None)]

    # Eric is still sitting on the floor
    assert d.eric.is_sitting_on_floor()

def test_skool_daze_sit_on_stairs(monkeypatch, capsys, tmp_path):
    # Eric overtakes the teachers on their way up to the staff room, turns
    # round on the top step and sits down
    inputs = """
        1 LEFT 118
        119 UP 24
        143 RIGHT
        144 SIT_STAND
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 150)

    # Mr Wacker told Eric not to sit on the stairs
    assert lines == [(149, 300, 'MR WACKER', 'NO_SITTING_ON_STAIRS', None)]

    # Eric is still sitting on the stairs
    assert d.eric.is_sitting_on_stairs()

def test_skool_daze_catapult(monkeypatch, capsys, tmp_path):
    # Eric walks left to meet Mr Withit, who is walking right along the bottom
    # floor, and fires his catapult in front of him
    inputs = """
        1 LEFT 100
        101 FIRE_CATAPULT
    """
    _, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 110)

    # Mr Withit told Eric that catapults are forbidden
    assert lines == [(109, 800, 'MR WITHIT', 'NO_CATAPULTS', None)]

def test_skool_daze_punch(monkeypatch, capsys, tmp_path):
    # Eric walks left to meet Mr Withit, who is walking right along the bottom
    # floor, and throws a punch in front of him
    inputs = """
        1 LEFT 100
        101 HIT
    """
    _, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 110)

    # Mr Withit told Eric not to hit his mates
    assert lines == [(110, 800, 'MR WITHIT', 'NO_HITTING', None)]

def test_skool_daze_jump(monkeypatch, capsys, tmp_path):
    # Eric walks left to meet Mr Withit, who is walking right along the bottom
    # floor, and jumps in front of him
    inputs = """
        1 LEFT 100
        101 JUMP
    """
    _, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 110)

    # Mr Withit told Eric that he is not a kangaroo
    assert lines == [(107, 700, 'MR WITHIT', 'NO_JUMPING', None)]

def test_skool_daze_knock_over_teacher(monkeypatch, capsys, tmp_path):
    # Eric walks left past Mr Withit, who is walking right along the bottom
    # floor, turns round, fires his catapult at Mr Withit's back, and stays
    # nearby while Mr Withit is knocked over
    inputs = """
        1 LEFT 126
        127 RIGHT
        128 FIRE_CATAPULT
    """
    _, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 200)

    # Mr Withit got up and told Eric not to do it again
    assert lines == [(198, 400, 'MR WITHIT', 'NEVER_AGAIN', None)]

def test_skool_daze_forbidden_area(monkeypatch, capsys, tmp_path):
    # Eric overtakes the teachers on their way up to the staff room, and steps
    # inside it
    inputs = """
        1 LEFT 118
        119 UP 36
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 160)

    # Mr Wacker told Eric that the room is private
    assert lines == [(159, 300, 'MR WACKER', 'GET_OUT', None)]

    # Eric is still in the staff room
    assert (d.eric.x, d.eric.y) == (10, 10)
    assert d.skool.in_no_go_zone(d.eric.x, d.eric.y)

def test_skool_daze_classroom_at_playtime(monkeypatch, capsys, tmp_path):
    # Eric goes up the stairs to the staff room ahead of the teachers, and then
    # right into the White Room, where he stays after the first 200 ticks of
    # playtime (when he should have left the classroom)
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 42
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 205)

    # Mr Wacker, walking along the middle floor towards the stairs up to the
    # top floor, told Eric to get to where he should be
    assert lines == [(203, 400, 'MR WACKER', 'GET_ALONG', None)]

    # Eric is still in the White Room
    assert d.skool.room(d.eric).name == 'WHITE ROOM'

def test_skool_daze_not_in_class(monkeypatch, capsys, tmp_path):
    # Eric is supposed to be in the Exam Room with Mr Wacker, but instead goes
    # up the stairs to the staff room ahead of the teachers, and then right
    # into the White Room, where he stays after the first 200 ticks of the
    # lesson (when he should have gone to the Exam Room)
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 42
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Wacker-ExamRoom', inputs, 205)

    # Mr Withit, walking along the middle floor towards the stairs up to the
    # top floor, told Eric to get to where he should be
    assert lines == [(203, 100, 'MR WITHIT', 'GET_ALONG', None)]

    # Eric is still in the White Room
    assert d.skool.room(d.eric).name == 'WHITE ROOM'

def test_skool_daze_write_on_blackboard(monkeypatch, capsys, tmp_path):
    # Eric is supposed to be in the White Room with Mr Wacker, and goes there
    # (via the stairs up to the staff room) ahead of the teachers; he then
    # writes on the blackboard as Mr Creak walks along the middle floor
    # towards the stairs up to the top floor
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 54
        201 WRITE
        202 TYPE E
        203 ENTER
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Wacker-WhiteRoom', inputs, 215)

    # Mr Creak told Eric not to touch blackboards, both when Eric started
    # writing and when he wrote a letter
    assert lines == [
        (205, 400, 'MR CREAK', 'NO_WRITING', None),
        (211, 100, 'MR CREAK', 'NO_WRITING', None)
    ]

    # Eric wrote on the White Room blackboard
    blackboard = d.skool.room(d.eric).blackboard
    assert blackboard.lines == ['E']
    assert blackboard.writer is d.eric

def test_skool_daze_stand_in_class(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room), and stands just inside the doorway instead of sitting
    # down
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 50
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 862)

    # Mr Withit started the lesson and told Eric to find a seat (and earlier,
    # on the top floor, Mr Creak gave Boy Wander lines after Boy Wander's
    # catapult pellet knocked him over)
    assert lines == [
        (591, 400, 'MR CREAK', 'NEVER_AGAIN', 'BOY WANDER'),
        (860, 100, 'MR WITHIT', 'SIT_DOWN', None)
    ]

    # Eric is still standing in the White Room, where the lesson is
    assert d.eric.is_standing()
    assert d.skool.get_home_room() is d.skool.room(d.eric)
    assert d.skool.room(d.eric).name == 'WHITE ROOM'

def test_skool_daze_late_for_class(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room), waits outside until the lesson has started (at tick
    # 857), and then steps inside while Einstein is telling Mr Withit that Eric
    # is absent; Eric stays out of Mr Withit's sight so as not to be told to
    # find a seat
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 34
        900 RIGHT 9
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 957)

    # Mr Withit told Eric never to be late again
    assert lines == [(955, 500, 'MR WITHIT', 'BE_PUNCTUAL', None)]

    # Eric is in the White Room, where the lesson is
    assert d.skool.get_home_room() is d.skool.room(d.eric)
    assert d.skool.room(d.eric).name == 'WHITE ROOM'

def test_skool_daze_not_staying_in_class(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room) and waits just inside the doorway (out of Mr Withit's
    # sight) until the lesson has started (at tick 859); he then leaves, and
    # waits at the top of the stairs (again out of Mr Withit's sight) until
    # Einstein starts telling Mr Withit that Eric is absent (at tick 1216);
    # finally he steps back inside while Mr Withit is facing the other way
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 42
        860 LEFT 43
        1220 RIGHT 43
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 1315)

    # Mr Withit told Eric to stay this time (and earlier, on the top floor, Mr
    # Creak gave Boy Wander lines after Boy Wander's catapult pellet knocked
    # him over)
    assert lines == [
        (591, 400, 'MR CREAK', 'NEVER_AGAIN', 'BOY WANDER'),
        (1313, 400, 'MR WITHIT', 'STAY_IN_CLASS', None)
    ]

    # Eric is in the White Room, where the lesson is
    assert d.skool.get_home_room() is d.skool.room(d.eric)
    assert d.skool.room(d.eric).name == 'WHITE ROOM'

def test_skool_daze_not_attending_class(monkeypatch, capsys, tmp_path):
    # Eric is supposed to be in the White Room with Mr Withit, but instead
    # waits outside (out of Mr Withit's sight) after going up the stairs to the
    # staff room; after Einstein has told Mr Withit that Eric is absent, Mr
    # Withit comes looking for him (but Eric stays put)
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 30
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 1172)

    # Mr Withit found Eric and told him to come along with him, and then
    # alternately told him to hurry up and not to try his patience
    assert lines == [
        (985, 300, 'MR WITHIT', 'COME_ALONG_1', None),
        (1047, 600, 'MR WITHIT', 'COME_ALONG_2', None),
        (1109, 600, 'MR WITHIT', 'COME_ALONG_3', None),
        (1171, 200, 'MR WITHIT', 'COME_ALONG_2', None)
    ]

    # Eric is still outside the White Room
    assert (d.eric.x, d.eric.y) == (19, 10)
    assert d.skool.room(d.eric) is None

def test_skool_daze_telling_tales(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room), and writes on the blackboard while Mr Withit is facing
    # the other way; he then waits just inside the doorway (out of Mr Withit's
    # sight) until the lesson has started (at tick 859), and leaves while
    # Einstein is telling Mr Withit that Eric wrote on the blackboard
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 54
        400 WRITE
        401 TYPE E
        402 ENTER
        420 LEFT 15
        860 LEFT 13
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 987)

    # Eric was not in the White Room when Einstein finished his tale, so Mr
    # Withit told Einstein not to tell tales (which added to Eric's score)
    assert lines == [(985, 300, 'MR WITHIT', 'NO_TALES', 'EINSTEIN')]
    assert d.skool.scoreboard.score == 300

    # Eric is outside the White Room, and the blackboard still has his writing
    # on it
    assert (d.eric.x, d.eric.y) == (19, 10)
    assert d.skool.room(d.eric) is None
    blackboard = d.skool.get_room('WhiteRoom').blackboard
    assert blackboard.lines == ['E']
    assert blackboard.writer is d.eric

def test_back_to_skool_stinkbomb(monkeypatch, capsys, tmp_path):
    # With seed 6, the stinkbombs are in the Science Lab desk nearest the door
    # (at x=52). Eric goes there (via the stairs up to the toilets), sits down
    # and opens the desk, and then goes back down the stairs and drops a
    # stinkbomb in front of Mr Wacker, who is walking along the bottom floor
    inputs = """
        1 LEFT 446
        447 UP 28
        475 RIGHT 150
        625 LEFT
        627 SIT_STAND
        629 OPEN_DESK
        631 SIT_STAND
        633 LEFT 149
        782 RIGHT
        784 DOWN 28
        812 RIGHT 24
        836 DROP_STINKBOMB
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 844, seed=6)

    # Mr Wacker told Eric that stinkbombs are not allowed
    assert lines == [(842, 300, 'MR WACKER', 'NO_STINKBOMBS', None)]

    # Eric has two stinkbombs left
    assert d.eric.inventory == {'STINKBOMBS2'}

def test_back_to_skool_water_pistol(monkeypatch, capsys, tmp_path):
    # With seed 10, the water pistol is in the Science Lab desk nearest the
    # door (at x=52). Eric goes there (via the stairs up to the toilets), sits
    # down and opens the desk, and then goes back down the stairs and fires the
    # water pistol in front of Mr Wacker, who is walking along the bottom floor
    inputs = """
        1 LEFT 446
        447 UP 28
        475 RIGHT 150
        625 LEFT
        627 SIT_STAND
        629 OPEN_DESK
        631 SIT_STAND
        633 LEFT 149
        782 RIGHT
        784 DOWN 28
        812 RIGHT 24
        836 FIRE_WATER_PISTOL
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 844, seed=10)

    # Mr Wacker told Eric that water pistols are not allowed
    assert lines == [(842, 200, 'MR WACKER', 'NO_WATERPISTOLS', None)]

    # Eric still has the water pistol
    assert d.eric.inventory == {'WATER_PISTOL'}

def test_back_to_skool_plant_pot(monkeypatch, capsys, tmp_path):
    # Eric steps left and jumps onto the plant pot beside the skool gate, and
    # stays there until Mr Wacker walks up to the gate
    inputs = """
        1 LEFT 4
        5 JUMP
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 713)

    # Mr Wacker told Eric to get off the plants
    assert lines == [(711, 500, 'MR WACKER', 'GET_OFF_PLANT', None)]

    # Eric is still standing on the plant pot
    assert (d.eric.x, d.eric.y) == (132, 16)
    assert d.skool.plant_pot(d.eric.x, d.eric.y)

def test_back_to_skool_bike(monkeypatch, capsys, tmp_path):
    # The bike is unchained up front (instead of Eric writing the combination
    # on a blackboard). Eric walks left to the bike, mounts it, and rides it
    # left through the skool door just as Mr Wacker turns round on the stage
    inputs = """
        1 LEFT 133
        250 MOUNT_BIKE
        252 LEFT
        255 RIGHT
        258 LEFT
        261 RIGHT
        264 LEFT
        267 RIGHT
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Playtime-1', inputs, 292,
                    setup=lambda d: d.skool.unchain_bike())

    # Mr Wacker told Eric not to ride bikes in the skool
    assert lines == [(290, 500, 'MR WACKER', 'NO_BIKES', None)]

    # Eric is still riding the bike, inside the skool
    assert d.eric.bike is not None
    assert not d.skool.in_playground(d.eric)

def test_back_to_skool_playground_during_lesson(monkeypatch, capsys, tmp_path):
    # With seed 28, the game starts with Playtime-4, followed by Mr Creak's
    # lesson in the Yellow Room (which starts at tick 2402). Eric steps left
    # and stays in the playground, where Mr Withit is still walking towards the
    # skool door after the bell
    inputs = """
        1 LEFT 33
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', None, inputs, 2607, seed=28)

    # Once Eric should have left the playground (200 ticks after the bell),
    # Mr Withit told him to get back to school
    assert lines == [(2605, 600, 'MR WITHIT', 'BACK_TO_SKOOL', None)]

    # Eric is still in the playground during Mr Creak's lesson
    assert d.skool.timetable.lesson_id == 'Creak-YellowRoom-1'
    assert (d.eric.x, d.eric.y) == (125, 17)
    assert d.skool.in_playground(d.eric)

def test_back_to_skool_sit_facing_away_from_stage(monkeypatch, capsys, tmp_path):
    # Eric walks left from the playground into the assembly hall, and sits
    # down just inside the doorway, facing away from the stage, in view of
    # Mr Creak
    inputs = """
        1 LEFT 234
        235 SIT_STAND
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Assembly', inputs, 240)

    # Mr Creak told Eric to sit facing the stage
    assert lines == [(238, 100, 'MR CREAK', 'SIT_FACING_STAGE', None)]

    # Eric is still sitting on the floor of the assembly hall, facing left
    assert d.eric.is_sitting_on_floor()
    assert d.eric.direction == -1
    assert d.skool.room(d.eric).name == 'ASSEMBLY'

def test_back_to_skool_stand_in_assembly(monkeypatch, capsys, tmp_path):
    # Eric walks left from the playground into the assembly hall, and stands
    # just inside the doorway until assembly starts (at tick 709)
    inputs = """
        1 LEFT 234
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Assembly', inputs, 712)

    # Mr Withit told Eric to sit down
    assert lines == [(710, 500, 'MR WITHIT', 'SIT_DOWN', None)]

    # Eric is still standing in the assembly hall
    assert d.eric.is_standing()
    assert d.skool.get_home_room() is d.skool.room(d.eric)
    assert d.skool.room(d.eric).name == 'ASSEMBLY'

def test_back_to_skool_not_attending_class(monkeypatch, capsys, tmp_path):
    # Eric is supposed to be in the dinner hall with Mr Withit, but instead
    # walks left to the edge of the playground and waits there; after Einstein
    # has told Mr Withit that Eric is absent, Mr Withit comes looking for him
    # (but Eric stays put)
    inputs = """
        1 LEFT 150
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'bts', 'Dinner-Withit', inputs, 1173)

    # Mr Withit found Eric and told him to come along, then told him not to
    # keep him waiting, and then started again (Back to Skool has only two
    # COME_ALONG messages); earlier, Mr Creak gave Boy Wander lines after Boy
    # Wander's catapult pellet knocked him over
    assert lines == [
        (431, 800, 'MR CREAK', 'NEVER_AGAIN', 'BOY WANDER'),
        (1047, 100, 'MR WITHIT', 'COME_ALONG_1', None),
        (1109, 500, 'MR WITHIT', 'COME_ALONG_2', None),
        (1171, 600, 'MR WITHIT', 'COME_ALONG_1', None)
    ]

    # Eric is still at the edge of the playground
    assert (d.eric.x, d.eric.y) == (96, 17)
    assert d.skool.in_playground(d.eric)

def test_skool_daze_knocked_out(monkeypatch, capsys, tmp_path):
    # With seed 29, Eric walks left into the path of a catapult pellet fired
    # by Boy Wander, and is knocked out (at tick 58); he is still lying on the
    # floor when Mr Rockitt, walking right along the bottom floor, comes into
    # view
    inputs = """
        1 LEFT 56
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-Stampede-1', inputs, 146, seed=29)

    # Mr Rockitt told Eric to get off the floor
    assert lines == [(144, 400, 'MR ROCKITT', 'GET_UP', None)]

    # Eric is still knocked out
    assert d.eric.is_knocked_out()
    assert (d.eric.x, d.eric.y) == (34, 17)

def test_skool_daze_tale_about_writing(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room), and writes on the blackboard while Mr Withit is facing
    # the other way; he then waits just inside the doorway (out of Mr Withit's
    # sight), where he stays while Einstein tells Mr Withit (from tick 859)
    # that Eric wrote on the blackboard
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 54
        400 WRITE
        401 TYPE E
        402 ENTER
        420 LEFT 15
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 987)

    # Eric was in the White Room when Einstein finished his tale, so Mr Withit
    # told Eric not to touch blackboards
    assert lines == [(985, 300, 'MR WITHIT', 'NO_WRITING', None)]

    # Eric is in the White Room, and the blackboard still has his writing on it
    assert (d.eric.x, d.eric.y) == (22, 10)
    assert d.skool.room(d.eric).name == 'WHITE ROOM'
    blackboard = d.skool.get_room('WhiteRoom').blackboard
    assert blackboard.lines == ['E']
    assert blackboard.writer is d.eric

def test_skool_daze_tale_about_hitting(monkeypatch, capsys, tmp_path):
    # Eric goes to the White Room for Mr Withit's lesson (via the stairs up to
    # the staff room), and waits just inside the doorway (out of Mr Withit's
    # sight); with seed 20, when the lesson starts (at tick 855), Einstein
    # tells Mr Withit that Eric hit him (Einstein's tales about hitting are
    # random, so Eric doesn't actually have to hit him)
    inputs = """
        1 LEFT 118
        119 UP 28
        147 RIGHT 42
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Withit-WhiteRoom', inputs, 942, seed=20)

    # Eric was in the White Room when Einstein finished his tale, so Mr Withit
    # told Eric not to hit his mates
    assert lines == [(940, 200, 'MR WITHIT', 'NO_HITTING', None)]

    # Eric is in the White Room
    assert (d.eric.x, d.eric.y) == (22, 10)
    assert d.skool.room(d.eric).name == 'WHITE ROOM'

def test_skool_daze_never_again_to_einstein(monkeypatch, capsys, tmp_path):
    # Eric walks left past Mr Withit, who is walking right along the bottom
    # floor, turns round, follows him, and fires his catapult at Mr Withit's
    # back just before Einstein (walking left) reaches him
    inputs = """
        1 LEFT 114
        115 RIGHT
        199 RIGHT 40
        240 FIRE_CATAPULT
    """
    d, lines = run(monkeypatch, capsys, tmp_path, 'sd', 'Playtime-4', inputs, 308)

    # Einstein was the kid nearest to Mr Withit when he got up, so Mr Withit
    # told Einstein not to do it again (which added to Eric's score)
    assert lines == [(306, 500, 'MR WITHIT', 'NEVER_AGAIN', 'EINSTEIN')]
    assert d.skool.scoreboard.score == 500
    assert d.skool.scoreboard.lines == 0
