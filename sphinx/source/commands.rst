.. _command-ref:

Commands
========
The :ref:`commandList` sections contain commands and parameters that control
the characters. These commands are described in the following sections.

AddLines
--------
The :class:`~pyskool.ai.AddLines` command is used to add to Eric's lines total
after he has been found guilty of misdeeds. The number of lines to be added to
the total is specified by the command's sole argument.

Catch
-----
The :class:`~pyskool.ai.Catch` command is used internally to control Eric while
he's trying to catch a mouse or frog. It makes Eric bend over, checks to see
whether an animal is present (and if it is, adds it to the appropriate
inventory), and then makes Eric stand up.

.. _chaseEricOut:

ChaseEricOut
------------
The :class:`~pyskool.ai.ChaseEricOut` command controls Miss Take as she chases
Eric, with the intent of making him leave the girls' skool and return to the
boys'.  It is very similar to the :ref:`shadowEric` command, except that it
makes the headmistress go no further than the skool gate (the x-coordinate of
which is supplied as the command's sole argument).

.. _checkIfTouchingEric:

CheckIfTouchingEric
-------------------
The :class:`~pyskool.ai.CheckIfTouchingEric` command is used by the bully when
he has mumps. It checks whether the bully is touching Eric, and if he is,
raises the signal that is being watched by whoever is on mumps duty (Mr Rockitt
by default).

ConductAssembly
---------------
The :class:`~pyskool.ai.ConductAssembly` command makes the headmaster tell the
kids they're in detention.

.. _conductClass:

ConductClass
------------
The :class:`~pyskool.ai.ConductClass` command is used by teachers to make them
conduct lessons. The command controls a teacher from the point where he reaches
the edge of the blackboard. If the teacher is teaching Eric, it makes the
teacher wait until the swot shows up, and then hands over control to the
:ref:`conductClassWithEric` command. Otherwise it immediately hands over
control to the :ref:`conductClassWithoutEric` command.

The command takes two optional arguments:

* the name of the signal that indicates that the swot is ready
* the name of the group of questions and answers to use for the lesson (see
  :ref:`questionsAndAnswers`); if not specified, the questions and answers will
  be chosen at random

.. _conductClassWithEric:

ConductClassWithEric
--------------------
The :class:`~pyskool.ai.ConductClassWithEric` command is used internally to
control a teacher who is teaching Eric and the swot. It takes over control from
the :ref:`conductClass` command as soon as the swot shows up and sits
down. It's responsible for making the teacher:

* listen to the swot's tales (if any)
* dish out lines after the swot has told tales
* wipe the blackboard
* walk to the middle of the blackboard
* write on the blackboard (occasionally)
* tell the kids what to do during class, or ask questions and wait for the
  answers
* hunt down Eric if he's playing truant

The command takes a single, optional argument: the name of the group of
questions and answers to use for the lesson (see :ref:`questionsAndAnswers`);
if not specified, the questions and answers will be chosen at random.

.. _conductClassWithoutEric:

ConductClassWithoutEric
-----------------------
The :class:`~pyskool.ai.ConductClassWithoutEric` command is used internally to
control a teacher who is teaching a class that does not contain Eric and the
swot. It takes over control from the :ref:`conductClass` command
immediately. It controls a teacher from the point where he reaches the edge of
the blackboard and is responsible for making him:

* wipe the blackboard
* walk to the middle of the blackboard
* write on the blackboard (occasionally)
* tell the kids what to do during class

.. _doAssemblyDuty:

DoAssemblyDuty
--------------
The :class:`~pyskool.ai.DoAssemblyDuty` command is used to control Mr Withit as
he does assembly duty. It makes Mr Withit do nothing (i.e. stand still) unless
Eric is absent from the assembly hall, in which case it hands over control to
the :ref:`fetchEric` command; when that command exits, the command list is
restarted. The ``DoAssemblyDuty`` command itself exits when assembly is over
(i.e. Mr Wacker has finished speaking).

The command takes two arguments that inform Mr Withit when to start and when to
stop assembly duty:

* the signal that indicates when assembly has started
* the signal that indicates when assembly has finished

These signals are raised by Mr Wacker.

.. _dropStinkbomb:

DropStinkbomb
-------------
The :class:`~pyskool.ai.DropStinkbomb` command is used internally to make a
stinkbomb-carrying character (i.e. Eric) drop a stinkbomb.

.. _dumpWaterPistol:

DumpWaterPistol
---------------
The :class:`~pyskool.ai.DumpWaterPistol` command is used internally to make
Eric throw away the water pistol. The water pistol will be relocated in a
random desk, and will contain water (as opposed to sherry).

.. _endGame:

EndGame
-------
The :class:`~pyskool.ai.EndGame` command is used to end the game (when Eric has
exceeded the lines limit, for example).

.. _evadeMouse:

EvadeMouse
----------
The :class:`~pyskool.ai.EvadeMouse` command is used internally to control a
character who is scared of mice and has spotted one nearby. It makes the
character either jump up and down or stand on a chair.

.. _fall:

Fall
----
The :class:`~pyskool.ai.Fall` command is used to control the descent of a drop
of water or sherry from a cup, or the descent of a conker from a tree. Until
the object has been knocked out of its resting place, the command does
nothing. Otherwise, it guides the object to the floor, and interacts
appropriately with any character it hits. After the object has hit somebody or
the floor, it is hidden from view.

.. _fallToFloor:

FallToFloor
-----------
The :class:`~pyskool.ai.FallToFloor` command is used internally to control
Eric's descent to the floor. It is invoked in the following situations:

* by the :ref:`rideBike` command when Eric falls off a bike that has lost
  momentum
* when Eric falls off a fully grown plant that has just died

.. _fetchEric:

FetchEric
---------
The :class:`~pyskool.ai.FetchEric` command is used internally by the
:ref:`conductClassWithEric` command to make a teacher track down the truant
Eric and shepherd him back to the classroom.

.. _findEric:

FindEric
--------
The :class:`~pyskool.ai.FindEric` command is used to make a character look for
Eric (to give him a message); it also stops the skool clock (which can be
restarted later on with a :ref:`setClock` command) to allow Eric to be found
before the bell rings. When Eric has been found, he is frozen so that he has no
choice but to listen to the message.

FindEricIfMissing
-----------------
The :class:`~pyskool.ai.FindEricIfMissing` command is used by whichever teacher
is on dinner duty to make him go and look for Eric if he's not in the dinner
hall.

.. _findSeat:

FindSeat
--------
The :class:`~pyskool.ai.FindSeat` command is used to make a boy or girl find a
seat in a classroom and sit down; it also makes the character find another seat
if he's knocked out of one (unless the character is the swot, who must return
to the same seat to avoid having to move his speech bubble during lessons).

The command takes two optional True (1) or False (0) arguments (which are both
True by default). When the first argument is True, the character will seek out
the back seat in the classroom first. Otherwise, when the second argument is
True, the character will go to the next seat in front of him, or to the back
seat if there isn't one (which is what happens when a character is pushed out
of his seat). When both arguments are False, the character will sit in the seat
he's standing next to (which is what happens when a character rises after being
decked while seated).

.. _fireCatapult:

FireCatapult
------------
The :class:`~pyskool.ai.FireCatapult` command is used internally to make a
catapult-carrying character (i.e. Eric or the tearaway) fire his catapult.

.. _fireNowAndThen:

FireNowAndThen
--------------
The :class:`~pyskool.ai.FireNowAndThen` command is used as an argument to the
:ref:`setControllingCommand` command to make the tearaway fire his catapult
occasionally. If the command decides that the time is ripe to send a projectile
whizzing through the air, it passes control to the :ref:`fireCatapult` command.

.. _fireWaterPistol:

FireWaterPistol
---------------
The :class:`~pyskool.ai.FireWaterPistol` command is used internally to make a
water pistol-carrying character (i.e. Eric) fire his water pistol.

.. _flight:

Flight
------
The :class:`~pyskool.ai.Flight` command is used internally to control Eric when
he is either stepping off a fully grown plant through an open window or over
the closed skool gate, or flying over the closed skool gate (after hitting it
while standing on the saddle of the bike - see the :ref:`rideBike`
command). The command guides Eric through his trajectory to the ground, upon
which he may land with his feet, his backside, or his back.

.. _floored:

Floored
-------
The :class:`~pyskool.ai.Floored` command is used internally to control a child
character who has been pushed out of his seat or knocked out cold (by Eric, the
bully, or the tearaway). The command keeps the character on the floor for a
brief period and then makes him stand up; after that, the character will
either resume whatever he was doing before, or look for another seat (see
:ref:`findSeat`).

Follow
------
The :class:`~pyskool.ai.Follow` command is used by little boys 2-11 to sync
their movements with those of the stampede leader, little boy 1. (Internally it
syncs destinations, and hands over control to the :ref:`goTo` command.) The
command takes a single argument: the unique ID of the character to follow.

Freeze
------
The :class:`~pyskool.ai.Freeze` command is used internally by the
:ref:`findEric` command to freeze Eric once he has been found. It continually
monitors the keyboard to check whether Eric has acknowledged delivery of a
message (by pressing 'U'). It is then up to the :ref:`tellEric` or
:ref:`tellEricAndWait` command to unfreeze Eric as appropriate.

.. _goTo:

GoTo
----
The :class:`~pyskool.ai.GoTo` command is arguably the most important command
ever in the history of Pyskool. Without it, the characters would stay rooted to
the spot, Pyskool would be boring, and you wouldn't be reading this. Sad.
Anyway, ``GoTo`` takes a single argument, which must be one of the following:

* a skool location identifier (as found in the :ref:`skoolLocations` section)
* an identifier of the form ``Location:characterId``, where ``characterId`` is
  the unique ID of a character

A ``Location:characterId`` identifier resolves to the current location of the
character with the given ID. To change the recognised prefix of such
identifiers, set the ``LocationMarker`` configuration parameter in the
:ref:`gameConfig` section of the ini file.

I leave it to the reader to guess what the ``GoTo`` command does.

GoToRandomLocation
------------------
The :class:`~pyskool.ai.GoToRandomLocation` command is used in many command
lists to make a character go to one of his :ref:`random locations
<randomLocations>`.

GoTowardsXY
-----------
The :class:`~pyskool.ai.GoTowardsXY` command is used internally to make a
character turn round or take one step in the direction of the destination ``x``
and ``y`` coordinates specified in the two arguments, instead of continuing all
the way to the destination. The command is used primarily by the
:ref:`findEric` and :ref:`fetchEric` commands, which require tracking of a
moving target (our hero) rather than a fixed destination.

GoToXY
------
The :class:`~pyskool.ai.GoToXY` command is used internally to make a character
go to a location specified by an `(x, y)` pair of coordinates. In fact, the
:ref:`goTo` command resolves its location ID parameter into an `(x, y)` pair of
coordinates and then hands over control to ``GoToXY``. Unsurprisingly,
``GoToXY`` takes two arguments: `x` and `y`, as in::

  GoToXY, 23, 17

Although ``GoToXY`` is not used explicitly in any of the stock command lists,
there is nothing to stop you using it in a command list if you wish.

.. _grassAndAnswerQuestions:

GrassAndAnswerQuestions
-----------------------
The :class:`~pyskool.ai.GrassAndAnswerQuestions` command is used by the swot to
make him tell tales to the teacher just before class starts, and answer the
teacher's questions later.

.. _grow:

Grow
----
The :class:`~pyskool.ai.Grow` command is used to control the growth of a plant
after it has been watered. If the plant is not growing, the command does
nothing.  Otherwise, it animates the plant growth, and lifts any characters who
are standing on the plant. When the plant dies, it drops any characters who
were standing on the plant, and hides it from view.

The ``Grow`` command takes three arguments, which specify the delay between the
plant being watered and:

* appearing at half-height
* growing to full height
* dying

.. _hit:

Hit
---
The :class:`~pyskool.ai.Hit` command is used internally to make a fist-wielding
character (i.e. Eric or the bully) throw a punch.

.. _hitNowAndThen:

HitNowAndThen
-------------
The :class:`~pyskool.ai.HitNowAndThen` command is used as an argument to the
:ref:`setControllingCommand` command to make the bully throw a punch
occasionally. If the command decides that the time is ripe to send a fist
whizzing through the air, it passes control to the :ref:`hit` command.

.. _hop:

Hop
---
The :class:`~pyskool.ai.Hop` command is used internally by the :ref:`moveFrog`
command to control the movements of a frog as it embarks on a long hop or a
short hop, or turns round.

.. _jump:

Jump
----
The :class:`~pyskool.ai.Jump` command is used internally to control Eric while
he's jumping. It lifts him into the air, checks to see whether he has reached a
shield, a cup, or the safe, and then lets him drop (unless there is an
unconscious kid or a plant pot below).

.. _jumpIfOpen:

JumpIfOpen
----------
The :class:`~pyskool.ai.JumpIfOpen` command is used to jump back or forward in
the command list if a door is open. The command takes two arguments: the door's
unique ID (see :ref:`doors`), and the number of commands to jump back or
forward, as in::

  JumpIfOpen, SkoolDoor, -5

.. _jumpIfShut:

JumpIfShut
----------
The :class:`~pyskool.ai.JumpIfShut` command is used to jump back or forward in
the command list if a door is shut. The command takes two arguments: the door's
unique ID (see :ref:`doors`), and the number of commands to jump back or
forward, as in::

  JumpIfShut, SkoolGate, 3

.. _jumpOffSaddle:

JumpOffSaddle
-------------
The :class:`~pyskool.ai.JumpOffSaddle` command is used internally to control
Eric when he is jumping off the saddle of the bike (see the :ref:`rideBike`
command). It lifts him into the air, checks to see whether he has reached a cup
(into which a frog may be placed), and then lets him drop to the floor.

.. _kiss:

Kiss
----
The :class:`~pyskool.ai.Kiss` command is used internally to control Eric while
he's kissing (or trying to kiss) Hayley. If Hayley is neither facing Eric nor
in front of him at the time of the attempted kiss, Eric will take a step
forward and then back again, with no kiss scored. If Hayley is in front of Eric
and facing him, one of two things will happen: (a) Eric will score a kiss,
or (b) Hayley will smack Eric in the face (if she feels he's tried to grab one
kiss too many already). If Eric does land a kiss, his lines total will be
reduced by 1000 (or to zero if he has less than 1000 lines).

KnockedOver
-----------
The :class:`~pyskool.ai.KnockedOver` command is used internally to control an
adult character who has been downed by a catapult pellet or a stampeding boy.
``KnockedOver`` stuns the character, makes him reveal his safe combination
letter (if appropriate), also makes him give lines to the nearest main child
character (if any), and then helps him up off the floor; after that, the
character will resume whatever he was doing before.

.. _monitorEric:

MonitorEric
-----------
The :class:`~pyskool.ai.MonitorEric` command is used as a subcommand (set by
the :ref:`setSubcommand` command) by Miss Take; it makes her keep an eye out
for Eric in the girls' skool when it's not playtime. It takes two arguments:

* the ID of the command list to switch to in order to chase Eric
* the x-coordinate beyond which Eric must be to be regarded as worth chasing

.. _moveAboutUntil:

MoveAboutUntil
--------------
The :class:`~pyskool.ai.MoveAboutUntil` command is used to make a character
repeatedly walk a random number of paces away from a fixed point (the walkabout
origin) and back again. The walkabout origin is the point the character reached
before ``MoveAboutUntil`` was invoked.

The command takes two arguments:

* a signal to listen for; when it is raised, the character will proceed to the
  next command in the command list
* (optional) the minimum and maximum distances to walk away from the walkabout
  origin; the default is ``(1, 7)``

.. _moveBike:

MoveBike
--------
The :class:`~pyskool.ai.MoveBike` command is used to control the bike when Eric
is not sitting on the saddle. If the bike has not been unchained yet, or is
resting on the ground, the command does nothing. Otherwise, it moves the bike
along until it runs out of momentum, at which point it will fall over.

.. _moveDeskLid:

MoveDeskLid
-----------
The :class:`~pyskool.ai.MoveDeskLid` command is used to control a desk lid when
it has been raised (by Eric). When the desk lid is not raised, the command does
nothing. Otherwise, it transfers the contents of the desk (if any) to Eric's
pocket. When the desk lid is ready to drop - after the delay specified by the
command's sole argument - it is hidden from view.

.. _moveFrog:

MoveFrog
--------
The :class:`~pyskool.ai.MoveFrog` command is used to control the movements of a
frog.  When a frog decides to move, it chooses from three options: turn round,
short hop, and long hop. Each of these movements is controlled by the
:ref:`hop` command.

The ``MoveFrog`` command takes three arguments, which specify the probability
that the frog will:

* keep still if Eric is not nearby
* turn round (if he decides to move at all)
* attempt a short hop (instead of a long hop) if not turning round

.. _moveMouse:

MoveMouse
---------
The :class:`~pyskool.ai.MoveMouse` command is used to control the movements of
a mouse: sprint up and down a few times, hide for a brief period, repeat.

The ``MoveMouse`` command takes four arguments:

* the minimum and maximum delays before the mouse comes out of hiding (e.g.
  ``(5, 20)``)
* the minimum and maximum number of sprints the mouse will make before hiding
  (e.g. ``(2, 5)``)
* the minimum and maximum distances of a sprint (e.g. ``(2, 5)``)
* the minimum and maximum number of sprint sessions the mouse will engage in
  before dying (if released by Eric; e.g. ``(10, 41)``)

.. _movePellet:

MovePellet
----------
The :class:`~pyskool.ai.MovePellet` command is used to control a catapult
pellet. If the pellet has not been launched, the command does nothing.
Otherwise, it moves the pellet through the air, checking whether any shields or
unfortunate characters lie in its path. When a pellet has finished its flight,
it is hidden from view.

.. _moveWater:

MoveWater
---------
The :class:`~pyskool.ai.MoveWater` command is used to control a jet of water
fired from a water pistol. If the water has not been fired, the command does
nothing.  Otherwise, it moves the water through the air, checking whether any
cups or plant pots lie in its path. When the water has finished its flight, it
is hidden from view.

OpenDoor
--------
The :class:`~pyskool.ai.OpenDoor` command makes a character open a door. It
takes one argument: the unique ID of the door (see :ref:`doors`) to open. If
the door is already open, the command does nothing.

.. _pause:

Pause
-----
The :class:`~pyskool.ai.Pause` command is used internally by the :ref:`kiss`
command to occupy Hayley (i.e. prevent her from executing her current command
list) while she is responding to an attempted kiss from Eric. The command exits
(and Hayley will resume her current command list) after the response (a kiss or
slap in the face) has been made.

.. _releaseMice:

ReleaseMice
-----------
The :class:`~pyskool.ai.ReleaseMice` command is used internally to control Eric
when he's releasing mice. It makes Eric bend over, releases up to five mice
(depending on how many Eric has caught) at the spot in front of Eric, and then
makes Eric stand up.

.. _restart:

Restart
-------
The :class:`~pyskool.ai.Restart` command is used to return to the first command
in the command list.

.. _rideBike:

RideBike
--------
The :class:`~pyskool.ai.RideBike` command is used internally to control Eric
while he's on the bike. It may hand over control to another command depending
on what happens while Eric is on the bike:

* :ref:`fallToFloor` (if the bike runs out of momentum)
* :ref:`jumpOffSaddle` (if Eric jumps off the saddle)
* :ref:`flight` (if the bike hits the closed skool gate while Eric is standing
  on the saddle)

Say
---
The :class:`~pyskool.ai.Say` command is used internally to make a character say
something. It takes two arguments: the thing to say, and an optional second
argument specifying whether to notify listeners when done (which defaults to
`False`, and is set to `True` only during lessons so that the teacher and the
swot don't talk over each other). For example::

  Say, 'Hello mum!'

would make a character say 'Hello mum!'.

Although ``Say`` is not used explicitly in any of the stock command lists,
there is nothing to stop you using it in a command list if you wish.

.. _setClock:

SetClock
--------
The :class:`~pyskool.ai.SetClock` command restarts the skool clock with a
certain amount of time remaining until the bell rings, specified by the sole
parameter.  It is used (for example) to ensure that the bell rings shortly
after Mr Wacker has finished delivering the detention message in assembly.

.. _setControllingCommand:

SetControllingCommand
---------------------
The :class:`~pyskool.ai.SetControllingCommand` command is an awkwardly named
command that takes another command - and that command's parameters - as its
arguments, as in::

  SetControllingCommand, OtherCommand, SomeParameter

What happens then is that on every pass through the main loop of the game,
``OtherCommand`` (the 'controlling' command) will be called for the character
so controlled. The idea is that ``OtherCommand`` will make the character do
something continuously (e.g. walk fast) or occasionally (e.g. fire a catapult
or throw a punch).

The 'controlling' command remains in effect until the following command in the
command list has completed.

SetRestartPoint
---------------
The :class:`~pyskool.ai.SetRestartPoint` command has the effect of discarding
itself and all previous commands in the command list, so that any
:ref:`restart` or :ref:`startLessonIfReady` command appearing further down the
command list will bring control back up the list to the command following
``SetRestartPoint`` instead of the top of the list.

.. _setSubcommand:

SetSubcommand
-------------
The :class:`~pyskool.ai.SetSubcommand` command places a subcommand in the
character's current command list. This subcommand is then executed on each pass
through the main loop, before and in addition to the current command in the
character's command list. The parameters of ``SetSubcommand`` are the
subcommand name and the subcommand's parameters, as in::

  SetSubcommand, SomeSubcommand, SomeParameter1, SomeParameter2

``SetSubcommand`` is used (for example) by Miss Take to place the
:ref:`monitorEric` subcommand in her command list, which makes her keep an eye
out for Eric in the girls' skool when it's not playtime.

The subcommand persists for the duration of the command list (which is usually
until the end of the lesson).

.. _shadowEric:

ShadowEric
----------
The :class:`~pyskool.ai.ShadowEric` command is used by Mr Wacker when he's been
alerted that Eric is trying to escape (see the :ref:`watchForEric`
command). The command makes Mr Wacker track down Eric and shadow him until the
bell rings.

ShutDoor
--------
The :class:`~pyskool.ai.ShutDoor` command makes a character shut a door. It
takes one argument: unique ID of the door (see :ref:`doors`) to shut. If the
door is already shut, the command does nothing.

.. _signal:

Signal
------
The :class:`~pyskool.ai.Signal` command is used to raise a signal. Signals are
used, for example, by the :ref:`moveAboutUntil` command to make a character
pace up and down until the time is right to proceed to the next command in the
command list. This scheme allows characters' movements to be coordinated.

The ``Signal`` command takes a single argument: the name of the signal to
raise.

See also the :ref:`unsignal` command.

.. _sitForAssembly:

SitForAssembly
--------------
The :class:`~pyskool.ai.SitForAssembly` command makes a character find a spot
to sit down in the assembly hall until the headmaster has finished speaking.
The command takes three arguments:

* the signal to wait for before standing up (see :ref:`startAssemblyIfReady`)
* the direction to face when sitting down (``-1`` for left, ``1`` for right)
* (optional) the minimum and maximum distances the character should walk back
  to find a spot to sit; the default is ``(1, 4)``

.. _sitStill:

SitStill
--------
The :class:`~pyskool.ai.SitStill` command is always found immediately after the
``FindSeat`` command when it appears in a command list. It makes the character
stay seated (in other words, do nothing).

.. _stalkAndHit:

StalkAndHit
-----------
It sounds brutal, but there really was a command list in Back to Skool that
contained instructions to make the bully track down Eric's girlfriend in order
to knock her about. In Pyskool, the equivalent (but more flexible) command is
:class:`~pyskool.ai.StalkAndHit`, which takes a single argument: the unique ID
of the character to track down.

``StalkAndHit`` should be used as an argument to the
:ref:`setControllingCommand` command, as in::

  SetControllingCommand, StalkAndHit, HEROINE

As a controlling command, ``StalkAndHit`` continually updates the character's
destination to match that of the target, and makes him throw punches now and
then along the way.

.. _startAssemblyIfReady:

StartAssemblyIfReady
--------------------
The :class:`~pyskool.ai.StartAssemblyIfReady` command makes Mr Wacker return to
the start of the command list unless it's time to go down to the stage for
assembly, at which point the signal named by the command's sole argument will
be raised (so that the kids know when to sit down; see :ref:`sitForAssembly`).

StartDinnerIfReady
------------------
The :class:`~pyskool.ai.StartDinnerIfReady` command is used by teachers on
dinner duty.  It restarts the command list unless it's time to start looking
out for Eric during dinner.

.. _startLessonIfReady:

StartLessonIfReady
------------------
The :class:`~pyskool.ai.StartLessonIfReady` command is used by teachers to get
a lesson under way (if enough time has passed since the bell rang). The command
takes a single argument: the name of the signal that indicates which room the
teacher will teach in (which is listened for by the kids in the classroom so
that they know when to sit down). If it's not time to start the lesson yet, the
command list is restarted.

Stink
-----
The :class:`~pyskool.ai.Stink` command is used to control a stinkbomb after
it's been dropped. If the stinkbomb has not been dropped, the command does
nothing.  Otherwise, it animates the stinkbomb cloud, checking whether any
characters with a sensitive nose are nearby, and compelling them to open the
nearest window. When the stench has dissipated - after a period specified by
the command's sole argument - the cloud is hidden from view.

.. _stopEric:

StopEric
--------
The :class:`~pyskool.ai.StopEric` command is used internally by the
:ref:`watchForEric` command to make Albert raise his arm and alert Mr Wacker
when he has spotted Eric trying to escape. The command exits when Eric leaves
the 'danger zone' near Albert.

TellClassWhatToDo
-----------------
The :class:`~pyskool.ai.TellClassWhatToDo` command is used internally by the
:ref:`conductClassWithEric` and :ref:`conductClassWithoutEric` commands to make
a teacher tell the class what to do (which usually involves writing an essay,
turning to a certain page in their books, or revising for their exams).

.. _tellEric:

TellEric
--------
The :class:`~pyskool.ai.TellEric` command is used to make a character deliver
the message specified in the command's sole argument, and then unfreeze Eric
(if he was frozen, as by the :ref:`findEric` command).

.. _tellEricAndWait:

TellEricAndWait
---------------
The :class:`~pyskool.ai.TellEricAndWait` command is used to make a character
deliver the message specified in the command's sole argument, and then unfreeze
Eric (if he was frozen, as by the :ref:`findEric` command) as soon as he has
registered understanding of the message so delivered. If Eric is slow to
respond, the message will be repeated periodically.

TellKidsToSitDown
-----------------
The :class:`~pyskool.ai.TellKidsToSitDown` command is used internally by the
:ref:`startLessonIfReady` command to make a character (a teacher, normally)
tell the kids to sit down when it's time to start class.

.. _tripPeopleUp:

TripPeopleUp
------------
The :class:`~pyskool.ai.TripPeopleUp` command is used as an argument to the
:ref:`setControllingCommand` command to make a character trip up anyone in his
path as he proceeds to his destination.

.. _unsignal:

Unsignal
--------
The :class:`~pyskool.ai.Unsignal` command is used to lower a signal previously
raised.  It takes a signal name as its sole argument.

WaitAtDoor
----------
The :class:`~pyskool.ai.WaitAtDoor` command is used to make Albert wait at the
skool door or the skool gate until all the characters are on the correct side
and it's therefore safe to shut the door or gate. The character flags `B` and
`G` (see :ref:`characters`) are used to determine which skool (and hence which
side of the door) a character belongs to. The ``WaitAtDoor`` command takes a
single argument: the unique ID of the door or gate (see :ref:`doors`).

.. _waitUntil:

WaitUntil
---------
The :class:`~pyskool.ai.WaitUntil` command is used to make a character do
nothing (i.e.  stand still) until a signal is raised. The command takes a
single argument: the name of the signal to wait for.

.. _walkAround:

WalkAround
----------
The :class:`~pyskool.ai.WalkAround` command makes a character walk up and down
about a fixed point (the walkabout origin).

The command takes two arguments:

* the number of walkarounds to do - a "walkaround" being a short trip away from
  the walkabout origin (wherever the character was when the ``WalkAround``
  command was invoked) and back again
* (optional) the minimum and maximum distances to walk away from the walkabout
  origin; the default is ``(1, 7)``

The ``WalkAround`` command is also used internally by the :ref:`moveAboutUntil`
command.

.. _walkFast:

WalkFast
--------
The :class:`~pyskool.ai.WalkFast` command is used as an argument to
:ref:`setControllingCommand` to make a character walk fast.

WalkUpOrDown
------------
The :class:`~pyskool.ai.WalkUpOrDown` command is used internally by the
:ref:`conductClassWithEric` and :ref:`conductClassWithoutEric` commands to make
a teacher turn round and walk three paces. Called repeatedly, it makes the
teacher walk up and down.

.. _watchForEric:

WatchForEric
------------
The :class:`~pyskool.ai.WatchForEric` command is used as an argument to
:ref:`setControllingCommand` to make Albert keep his eyes peeled for our hero
jumping out of skool windows. If Albert does spot Eric trying to escape,
control is handed over to the :ref:`stopEric` command.

The ``WatchForEric`` command takes five arguments

* the ID of the character who will be alerted by Albert when he spots Eric
  trying to escape
* the ID of the command list to use for the character who will be alerted
* the alert message to be screamed by Albert
* the x-coordinate beyond which Eric should be regarded as trying to escape (96
  in the stock Pyskool, which is the x-coordinate of the boys' skool door)
* the minimum and maximum distances to the left of Albert that Eric would have
  to be between for Albert to raise the alarm

WipeBoard
---------
The :class:`~pyskool.ai.WipeBoard` command is used internally by the
:ref:`conductClassWithEric` and :ref:`conductClassWithoutEric` commands to make
a character wipe a blackboard clean.

Write
-----
The :class:`~pyskool.ai.Write` command is used internally to control Eric while
he's writing on a blackboard. It would be of no use in a command list.

WriteOnBoard
------------
The :class:`~pyskool.ai.WriteOnBoard` command is used internally by the
:ref:`conductClassWithEric`, :ref:`conductClassWithoutEric` and
:ref:`writeOnBoardUnless` commands to make a character write on a blackboard.
The character should (ideally) be standing at the target blackboard before this
command is invoked.

The command takes a single argument, namely the message to be written on the
board. So if you wanted to use the command explicitly in a command list, you
could put something like::

  GoTo, ExamRoomBlackboard:Middle
  WriteOnBoard, 'Pyskool rox!'

.. _writeOnBoardUnless:

WriteOnBoardUnless
------------------
The :class:`~pyskool.ai.WriteOnBoardUnless` command is used by the tearaway to
make him write on a blackboard unless the board has already been written on or
the signal named in the command's sole argument has been raised.
