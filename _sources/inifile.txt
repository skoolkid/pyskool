.. _ini-file:

Game ini files
==============
The game ini files determine many aspects of the game, such as the names of the
characters, the order of the lessons, and what characters do during lessons.

By default, the ini files for a particular game are arranged in one of the
subdirectories of the `ini` directory thus:

* `command_lists.ini` - :ref:`command lists <commandList>`
* `config.ini` - configuration parameters
* `font.ini` - font character bitmap descriptions (see :ref:`font`)
* `lessons.ini` - the :ref:`main timetable <timetable>` and
  :ref:`lessons <lessons>`
* `messages.ini` - messages
* `skool.ini` - :ref:`walls <walls>`, :ref:`floors <floors>` and other parts of
  the skool
* `sprites.ini` - sprite and :ref:`character <characters>` definitions

However, this arrangement is quite arbitrary; Pyskool will read every file with
a `.ini` suffix in the subdirectory regardless of its name or contents. So you
could, if you wish, concatenate all the ini files into one large ini file, and
Pyskool will still work.

Pyskool reads ini files in alphabetical order of filename, and if a particular
section appears in more than one file, the contents of that section in the last
file read take precedence. So the best way to modify a game is to add
customised sections to a file named `zzz-custom.ini` (for example), which will
be read after all the stock ini files.

If you want to customise a section by adding lines to it rather than completely
replacing the existing contents, you can append a '+' to the section name. For
example, if `zzz-custom.ini` contains a section named `[SkoolLocations+]`, then
the contents of that section will be appended to the contents of the
:ref:`skoolLocations` section defined in `config.ini`. By this method, you can
customise the `[SkoolLocations]` section in a supplementary ini file without
copying its original contents first.

What follows is a description of every section of the ini files. Armed with
this knowledge, and by consulting the :ref:`command reference <command-ref>`
where necessary, you'll be able to start mucking around with how Pyskool works
and how the game characters behave.

If you can't be bothered to read any of this and instead just want to get your
modding hands dirty right now, head over to :ref:`example-customisations`.

If you're even lazier than that, head over to the
:ref:`ready-made customisations <ready-made>` that are distributed with
Pyskool.

.. _animationPhases:

[AnimationPhases ...]
---------------------
The ``AnimationPhases ...`` section names take the form::

  AnimationPhases phaseSetId

where ``phaseSetId`` is a descriptive unique ID for the list of animation
phases that follows.

The format of an animation phase depends on who uses the phase set.

Each phase in the phase sets used by the frog (``FrogTurnRound``,
``FrogShortHop`` and ``FrogLongHop``) looks like this::

  animatoryState, xInc, directionChange

where:

* ``animatoryState`` is the ID of the animatory state
* ``xInc`` is the x-coordinate increment
* ``directionChange`` is the direction multiplier (-1 to change direction, 1 to
  not)

Each phase in the phase sets used by Eric (``DescentMiddleWindow``,
``DescentUpperWindow``, ``ClimbSkoolGate`` and ``FlyOverSkoolGate``) looks like
this::

  xInc, yInc, animatoryState

where:

* ``xInc`` is the x-coordinate increment
* ``yInc`` is the y-coordinate increment
* ``animatoryState`` is the ID of Eric's animatory state

Each phase in the phase set used by the stream of water or sherry fired from a
water pistol (``Water``) looks like this::

  animatoryState, xInc, yInc, hit

where:

* ``animatoryState`` is the ID of the animatory state
* ``xInc`` is the x-coordinate increment
* ``yInc`` is the y-coordinate increment
* ``hit`` is 0 if the water cannot hit anything, 1 if it can hit a cup, or 2 if
  it can hit a plant or the ground in this phase

Each phase in the phase set used by a stinkbomb when dropped (``Stinkbomb``)
looks like this::

  animatoryState, direction

where:

* ``animatoryState`` is the ID of the animatory state
* ``direction`` is the direction (-1 for left, 1 for right)

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.3     | New     |
+---------+---------+

.. _assemblyMessages:

[AssemblyMessages]
------------------
The ``AssemblyMessages`` section contains all the information required to build
a message used by the headmaster during assembly.

There are two types of entry in this section. The first type of entry is the
message template entry::

  MESSAGE, assemblyMessageTemplate

which defines the template for an assembly message. The section can contain one
or more message templates.

The second type of entry is the macro replacement entry::

  MACRO, text

where ``MACRO`` is the name of a macro that appears in a message template
(prefixed by ``$``), and ``text`` is the text to which the macro should expand.
Multiple macro replacement entries may be defined for any given macro. When an
assembly message is created, the message template is chosen at random, and the
macro replacements are chosen at random.

In the stock Pyskool ini files, there is only one assembly message template,
which contains two macros (``$VERB`` and ``$NOUN``).

.. _bike:

[Bike]
------
The ``Bike`` section contains a single line of the form::

  bikeId, spriteGroupId, animatoryState, unchainXY, commandListId, topLeft, size, coords, moveDelay, pedalMomentum, maxMomentum

where:

* ``bikeId`` is the bike's ID
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the bike
* ``animatoryState`` is the bike's initial animatory state
* ``unchainXY`` is the bike's initial coordinates (in `(x, y)` form) after
  being unchained
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the bike will use
* ``topLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  image of the base of the tree with no bike attached
* ``size`` is the size of the image (in `(width, height)` form)
* ``coords`` are the coordinates (in `(x, y)` form) of the mutable image in the
  play area
* ``moveDelay`` is the delay between consecutive movements of the bike when
  wheeling along or being pedalled (the higher the number, the slower the bike
  will go)
* ``pedalMomentum`` is the momentum increment when the bike is pedalled
* ``maxMomentum`` is the maximum momentum the bike can have

The bike images can be found in `mutables.png` (or `mutables_ink.png` and
`mutables_paper.png` if ``GraphicsMode`` is 1 - see :ref:`screenConfig`).
`mutables.png` is arranged so that the image of the bike attached to the base
of the tree is at `(x + width, y)`, where `(x, y)` are the coordinates of the
image of the base of the tree with no bike attached. These two images are the
same size.

+---------+----------------------------------------------------------------+
| Version | Changes                                                        |
+=========+================================================================+
| 0.3     | Added the ``moveDelay``, ``pedalMomentum`` and ``maxMomentum`` |
|         | parameters                                                     |
+---------+----------------------------------------------------------------+
| 0.2.1   | New                                                            |
+---------+----------------------------------------------------------------+

.. _blackboardMessages:

[BlackboardMessages ...]
------------------------
The ``[BlackboardMessages ...]`` section names take the form::

  BlackboardMessages characterId

where ``characterId`` is the unique ID of a character (see :ref:`characters`).

Each ``BlackboardMessages`` section contains a list of messages (one per line)
that may be written on a blackboard by the character whose ID is
``characterId``.

There are two special characters used in blackboard messages: ``^`` and ``$``.
``^`` represents the newline character (as defined by the ``Newline``
configuration parameter in the :ref:`messageConfig` section). ``$`` is used to
prefix the unique ID of a character, as in::

  i hate^$WACKER

where ``$WACKER`` will be replaced by whatever name has been given to the
character whose unique ID is ``WACKER``.

If no blackboard messages are defined for a particular character, that
character will never write on a blackboard.

+---------+------------------------------------------------------------+
| Version | Changes                                                    |
+=========+============================================================+
| 0.3     | Each character gets his own ``BlackboardMessages`` section |
+---------+------------------------------------------------------------+

.. _blackboards:

[Blackboards]
-------------
The ``Blackboards`` section defines the blackboards in the classrooms. Each
line has the form::

  roomId, topLeft, size, chalk

where:

* ``roomId`` is the classroom's unique ID (see :ref:`rooms`)
* ``topLeft`` is the coordinates of the top-left of the blackboard
* ``size`` is the size (width, height) of the blackboard
* ``chalk`` is the chalk colour (as an RGB triplet) to use when writing on the
  blackboard

In the stock Pyskool ini files, ``chalk`` is set to (255, 255, 255) - bright
white - which coincides with the transparent colour used in the skool ink image
(see ``SkoolInkKey`` in the :ref:`screenConfig` section). This means that in
graphics mode 1 (see ``GraphicsMode`` in the :ref:`screenConfig` section),
anything written on the board will take on the background (paper) colour, which
is how blackboards worked in the original games.

+---------+---------------------------------------------+
| Version | Changes                                     |
+=========+=============================================+
| 0.3     | Added the ``size`` and ``chalk`` parameters |
+---------+---------------------------------------------+

.. _catapultPellets:

[CatapultPellets]
-----------------
Each line in the ``CatapultPellets`` section has the form::

  characterId, pelletId, spriteGroupId, commandListId, range, hitZone, hitXY

where:

* ``characterId`` is the unique ID of the catapult-wielding character
* ``pelletId`` is the unique ID of the catapult pellet
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the pellet
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the pellet will use
* ``range`` is the distance the pellet will fly after being launched
* ``hitZone`` is the size of the interval at the end of the pellet's flight
  where it can knock a character over
* ``hitXY`` is the coordinates of the pellet within its sprite (used for
  collision detection)

Each character whose unique ID appears in this section will be fitted out with
a catapult. In the stock Pyskool this will be Eric and the tearaway - the only
characters with catapult-firing sprites.

+---------+------------------------------------------------+
| Version | Changes                                        |
+=========+================================================+
| 0.3     | Added the ``hitXY`` parameter                  |
+---------+------------------------------------------------+
| 0.2.3   | Added the ``pelletId`` parameter               |
+---------+------------------------------------------------+
| 0.0.3   | Added the ``range`` and ``hitZone`` parameters |
+---------+------------------------------------------------+
| 0.0.2   | New                                            |
+---------+------------------------------------------------+

.. _chairs:

[Chairs]
--------
The ``Chairs`` section contains one line for each classroom in the skool. Each
line has the form::

  roomId, x1, x2, x3..., xN

where:

* ``roomId`` is the classroom's unique ID (see :ref:`rooms`)
* ``x1``, ``x2``, ``x3`` and so on are the x-coordinates of the chairs in the
  classroom

The order in which the x-coordinates are listed is significant: ``x1`` should
correspond to the 'front seat' and ``xN`` should correspond to the 'back seat'.
So if ``x1`` < ``xN``, characters will sit down facing left; if
``x1`` > ``xN``, characters will sit down facing right.

.. _characters:

[Characters]
------------
Each line in the ``Characters`` section has the form::

  characterId, name[/title], spriteGroupId, animatoryState, direction, (x, y), headXY, flags

and corresponds to a single character, where:

* ``characterId`` is the character's unique ID (which should be alphanumeric
  and is used to refer to the character in other parts of the ini file)
* ``name`` is the character's name (as displayed in the game), and ``title``
  (if supplied) is the name used by the swot to address the character
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the character
* ``animatoryState`` is the character's initial animatory state
* ``direction`` is the character's initial direction (-1 for left, 1 for right)
* ``(x, y)`` are the character's initial coordinates
* ``headXY`` are the coordinates of the character's head within his sprite when
  he's standing upright (used for collision detection)
* ``flags`` is a string of flags defining the character's abilities and
  vulnerabilities

Recognised flags and their meanings are:

* ``A`` - is an adult
* ``B`` - belongs in the boys' skool
* ``C`` - can be knocked over by a conker (see also ``Z``)
* ``D`` - can open doors and windows
* ``F`` - can be knocked out by a fist
* ``G`` - belongs in the girls' skool
* ``K`` - holds the key to the safe
* ``L`` - can give lines
* ``M`` - is scared of mice
* ``N`` - can smell stinkbombs (and will open a nearby window if possible)
* ``P`` - can be knocked over by a catapult pellet
* ``R`` - can receive lines
* ``S`` - holds a safe combination letter
* ``T`` - can be tripped up by a stampeding kid (see :ref:`tripPeopleUp`)
* ``U`` - lines received by this character will be added to Eric's total
* ``V`` - lines received by this character will be added to Eric's score
* ``W`` - usually walks (unlike kids who sometimes run)
* ``X`` - holds a bike combination digit
* ``Y`` - holds a storeroom door combination letter
* ``Z`` - will be temporarily paralysed if struck by a falling conker (see also
  ``C``)

+---------+--------------------------------------------------------------+
| Version | Changes                                                      |
+=========+==============================================================+
| 0.3     | Added the ``headXY`` parameter and the ``U`` and ``V`` flags |
+---------+--------------------------------------------------------------+
| 0.2.1   | Added the ``K``, ``N``, ``X``, ``Y`` and ``Z`` flags         |
+---------+--------------------------------------------------------------+
| 0.0.4   | Added the ``S`` flag                                         |
+---------+--------------------------------------------------------------+
| 0.0.3   | Added the ``R`` and ``T`` flags                              |
+---------+--------------------------------------------------------------+

.. _commandList:

[CommandList ...]
-----------------
The ``[CommandList ...]`` section names take the form::

  CommandList commandListId

where ``commandListId`` is a descriptive unique ID for the list of commands
that follows. These unique IDs are used in the :ref:`lessons` sections: for
each type of lesson there is, every character is assigned a single command list
to follow.

One example of a command list is::

  [CommandList Walkabout1-Wacker]
  GoTo, HeadsStudy:Window
  GoToRandomLocation
  Restart

This command list is used occasionally by the headmaster; it makes him
repeatedly go to one of his :ref:`random locations <randomLocations>` and then
back to his study.

Each line in a command list contains the command name followed by a
comma-separated list of arguments. See the
:ref:`command reference <command-ref>` for more details on the commands that may
be used to control a character.

.. _conker:

[Conker]
--------
The ``Conker`` section defines a conker (as knocked out of the tree by a
catapult pellet). It contains a single line of the form::

  objectId, spriteGroupId, commandListId, minX, maxX, minY, maxY, hitXY

where:

* ``objectId`` is a unique ID for the conker
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the conker
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the conker will use when knocked out of the tree
* ``minX``, ``maxX``, ``minY`` and ``maxY`` define the rectangle inside the
  tree that contains the conker; a pellet that hits a spot in that rectangle
  will cause a conker to fall
* ``hitXY`` is the coordinates of the conker within its sprite (used for
  collision detection)

+---------+-------------------------------+
| Version | Changes                       |
+=========+===============================+
| 0.3     | Added the ``hitXY`` parameter |
+---------+-------------------------------+
| 0.2.1   | New                           |
+---------+-------------------------------+

.. _cups:

[Cups]
------
The ``Cups`` section contains information about cups. Each line describes a
single cup, and has the form::

  cupId, emptyTopLeft, size, coords

where:

* ``cupId`` is the unique ID of the cup
* ``emptyTopLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  image of the cup when empty
* ``size`` is the size of the image (in `(width, height)` form)
* ``coords`` are the coordinates (in `(x, y)` form) of the cup in the skool

The cup images can be found in `mutables.png` (or `mutables_ink.png` and
`mutables_paper.png` if ``GraphicsMode`` is 1 - see :ref:`screenConfig`).
`mutables.png` is arranged so that the image of a cup when it contains water is
at `(x + width, y)`, and the image of a cup when it contains sherry is at
`(x + 2 * width, y)` (where `(x, y)` are the coordinates of the image of the
cup when empty). The three images for any given cup are the same size.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.2.1   | New     |
+---------+---------+

.. _deskLid:

[DeskLid]
---------
The ``DeskLid`` section contains a single line of the form::

  deskLidId, spriteGroupId, commandListId, xOffset

where:

* ``deskLidId`` is the unique ID of the desk lid
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the desk lid when raised
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the desk lid will use
* ``xOffset`` - the offset (relative to the desk being opened) at which the
  desk lid should be displayed

+---------+-----------------------------------+
| Version | Changes                           |
+=========+===================================+
| 0.3     | Added the ``xOffset`` parameter   |
+---------+-----------------------------------+
| 0.2.3   | Added the ``deskLidId`` parameter |
+---------+-----------------------------------+
| 0.2.1   | New                               |
+---------+-----------------------------------+

.. _desks:

[Desks]
-------
Each line in the ``Desks`` section has the form::

  roomId, x1, x2...

where

* ``roomId`` is a classroom's unique ID (see :ref:`rooms`)
* ``x1``, ``x2`` and so on are the x-coordinates of the desks in the classroom
  (which should be a subset of the x-coordinates of the chairs in the classroom
  - see :ref:`chairs`)

Any chair that is in a room and at an x-coordinate that appears in the
``Desks`` section will be fitted out with a desk lid that can be raised (see
:ref:`deskLid`).

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.2.1   | New     |
+---------+---------+

.. _doors:

[Doors]
-------
The ``Doors`` section contains details of the doors in the game. Each line
has the form::

  doorId, x, bottomY, topY, initiallyShut, autoShutDelay, shutTopLeft, size, coords[, climb[, fly]]

where:

* ``doorId`` is the door's unique ID
* ``x`` is the door's x-coordinate
* ``bottomY`` and ``topY`` are the y-coordinates of the bottom and top of the
  door
* ``initiallyShut`` is ``Y`` if the door should be shut when the game starts
* ``autoShutDelay`` is the delay before the door swings shut automatically; if
  zero or negative, the door will not shut automatically
* ``shutTopLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  image of the door when shut
* ``size`` is the size of the image (in `(width, height)` form)
* ``coords`` are the coordinates (in `(x, y)` form) of the door in the skool
* ``climb`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` to use for Eric if he climbs over
  the door when it's shut; if not defined, Eric will not be able to climb over
  the door
* ``fly`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` to use for Eric if he flies over
  the door after hitting it while standing on the saddle of the bike; if not
  defined, Eric will not be able to fly over the door

The door images can be found in `mutables.png` (or `mutables_ink.png` and
`mutables_paper.png` if ``GraphicsMode`` is 1 - see :ref:`screenConfig`).
`mutables.png` is arranged so that the image of a door when open is at
`(x + width, y)`, where `(x, y)` are the coordinates of the image of the same
door/window when shut. The open/shut images for any given door are the same
size.

+---------+---------------------------------------------------------------+
| Version | Changes                                                       |
+=========+===============================================================+
| 0.3     | Added the ``autoShutDelay``, ``climb`` and ``fly`` parameters |
+---------+---------------------------------------------------------------+

[Eric]
------
The ``Eric`` section describes our hero, Eric. It contains a single line in the
format::

  characterId, name, spriteGroupId, animatoryState, direction, (x, y), headXY, flags[, bendOverHandXY]

where:

* ``characterId`` is Eric's unique ID (which should be alphanumeric)
* ``name`` is Eric's name
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for Eric
* ``animatoryState`` is Eric's initial animatory state
* ``direction`` is Eric's initial direction (-1 for left, 1 for right)
* ``(x, y)`` are Eric's initial coordinates
* ``headXY`` are the coordinates of Eric's head within his sprite when he's
  standing upright (used for collision detection)
* ``flags`` is a string of flags defining Eric's abilities and vulnerabilities
* ``bendOverHandXY`` is the coordinates of Eric's hand within his left-facing
  `BENDING_OVER` sprite (used to determine where a mouse or frog should be when
  caught or released)

For a description of the available flags, see :ref:`characters`.

+---------+------------------------------------------------------------+
| Version | Changes                                                    |
+=========+============================================================+
| 0.3     | Added the ``direction``, ``headXY`` and ``bendOverHandXY`` |
|         | parameters                                                 |
+---------+------------------------------------------------------------+
| 0.0.2   | Added the ``animatoryState`` and ``flags`` parameters      |
+---------+------------------------------------------------------------+

.. _font:

[Font]
-----------------
The ``Font`` section is used to determine the location and size of the font
character bitmaps in the `font.png` graphic. Each line has the form::

  "char", offset, width

where:

* ``char`` is the font character (e.g. ``f``, ``@``, ``!``)
* ``offset`` is the font character's distance in pixels from the left of the
  image
* ``width`` is its width in pixels

+---------+------------------------------------+
| Version | Changes                            |
+=========+====================================+
| 0.3     | Renamed from ``[CharacterWidths]`` |
+---------+------------------------------------+
| 0.0.2   | Added the ``offset`` parameter     |
+---------+------------------------------------+

.. _floors:

[Floors]
--------
The ``Floors`` section contains details of the "floors" in the skool. A "floor"
(note the quotes) is a region of the skool that cannot be reached from another
region of the skool without navigating a staircase. For example, in Skool Daze,
the region to the left of the Map Room wall is one floor, and the region to the
right of the Map Room wall is another floor. You can't get from one to other
without going up or down a staircase (walking through walls is prohibited).

Each line in this section has the form::

  floorId, minX, maxX, y

where:

* ``floorId`` is the floor's unique ID
* ``minX`` and ``maxX`` are the x-coordinates of the left and right limits of
  the floor
* ``y`` is the y-coordinate of the floor (3 = top floor, 10 = middle floor,
  17 = bottom floor)

The unique IDs are used in the :ref:`routes` section.

.. _frogs:

[Frogs]
-------
Each line in the ``Frogs`` section has the form::

  frogId, spriteGroupId, animatoryState, (x, y), commandListId, turnRound, shortHop, longHop, sitXY, ericProximity

where:

* ``frogId`` is the unique ID of the frog
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the frog
* ``animatoryState`` is the frog's initial animatory state
* ``(x, y)`` are the frog's initial coordinates
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the frog will use
* ``turnRound`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` to use when the frog turns round
* ``shortHop`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` to use when the frog makes a short
  hop
* ``longHop`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` to use when the frog makes a long
  hop
* ``sitXY`` is the coordinates of the frog within its sprite when it's sitting
  (used for collision detection and placement in cups)
* ``ericProximity`` is the minimum distance from the frog that Eric can be
  before it will try to hop away

Any frog defined in this section will be catchable by ERIC, and show up in the
on-screen inventory when caught.

+---------+-------------------------------------------------------------------+
| Version | Changes                                                           |
+=========+===================================================================+
| 0.3     | Added the ``turnRound``, ``shortHop``, ``longHop``, ``sitXY`` and |
|         | ``ericProximity`` parameters                                      |
+---------+-------------------------------------------------------------------+
| 0.2.1   | New                                                               |
+---------+-------------------------------------------------------------------+

.. _gameConfig:

[GameConfig]
------------
The ``GameConfig`` section contains configuration parameters in the format::

  parameterName, parameterValue

Recognised parameters are:

* ``AllShieldsScore`` - points awarded for hitting all the shields
* ``AssemblyHallId`` - ID of the assembly hall (as defined in the :ref:`rooms`
  section); this is used to check whether Eric can sit or should be sitting on
  the floor
* ``AssemblySitDirection`` - the direction Eric should face when sitting down
  for assembly (``-1`` for left, ``1`` for right)
* ``BesideEricXRange`` - maximum horizontal distance from Eric at which a
  character can be to be considered beside him
* ``BikeCombinationScore`` - points awarded for writing the bike combination on
  a blackboard
* ``BikeSecrets`` - valid bike combination characters
* ``Cheat`` - 0 = disable cheat keys, 1 = enable cheat keys
* ``ConfirmClose`` - whether to show a confirmation screen when the window
  close button is pressed (1 = yes, 0 = no)
* ``ConfirmQuit`` - whether to show a confirmation screen when Escape is
  pressed to quit (1 = yes, 0 = no)
* ``ConkerClockTicks`` - the number of ticks by which the skool clock is
  rewound (that is, the number of ticks by which the current period is
  extended) when a character is paralysed by a falling conker
* ``ConkerWakeTime`` - the time (clock ticks remaining before the next bell
  ring) at which a character paralysed by a conker will remobilise
* ``DrinksCabinetDoorId`` - the ID of the drinks cabinet door (see
  :ref:`doors`); this is used to detect whether Eric has jumped up to it (to
  get the sherry)
* ``EvadeMouseDelay`` - the delay before a character frightened by a mouse will
  either get off a chair or stop jumping
* ``ExpellerId`` - the ID of the character who is responsible for expelling
  Eric
* ``FireCatapultProbability`` - the probability that the tearaway will fire his
  catapult if conditions are suitable
* ``HitProbability`` - the probability that the bully will throw a punch if
  conditions are suitable
* ``Icon`` - the name of the icon file to use
* ``ImageSet`` - the name of the image set to use
* ``GameFps`` - the number of frames per second at which the game should
  attempt to run; raise it to increase the game speed, or lower it to decrease
  the game speed
* ``KissCounter`` - the initial value of the kiss counter for a character
* ``KissCounterDeckrement`` - the amount by which a character's kiss counter is
  decreased after being knocked over
* ``KissCounterDecrement`` - the amount by which a character's kiss counter is
  decreased after kissing Eric
* ``KissDistance`` - the exact distance in front of Eric a character must be in
  order to be kissable
* ``KissLines`` - the number of lines a kissee does for Eric on each kiss
* ``LinesGivingRange`` - the maximum horizontal and vertical distances a
  character must be away from a target character to be considered close enough
  to give or be given lines
* ``LinesRange`` - minimum and maximum number of lines (divided by 100) that
  may be given out in one go
* ``LocationMarker`` - prefix used in a destination ID to denote the location
  of a character
* ``MaxLines`` - the maximum number of lines Eric may accumulate before being
  expelled
* ``MaxMiceRelease`` - the maximum number of mice to release per attempt
* ``MinimumLinesDelay`` - the minimum delay between two non-immediate
  lines-givings by the same teacher
* ``MouseCatchScore`` - points awarded for catching a mouse
* ``MouseProximity`` - maximum distance at which a musophobe can detect a mouse
  (and so be scared by it)
* ``Name`` - the name of the game
* ``Playground`` - the x-coordinates of the left and right boundaries of the
  playground (used for checking whether Eric's in the playground)
* ``PlayTuneOnRestart`` - 1 to play the theme tune after restarting the game
  for advancing a year; 0 otherwise
* ``QuickStart`` - 0 to scroll the skool into view and play the theme tune (as
  in the original games); 1 to skip this sequence
* ``RestartOnYearEnd`` - 1 if the game should restart after advancing a year
  (as in Back to Skool); 0 otherwise (as in Skool Daze)
* ``SafeKeyScore`` - points awarded when the safe key is obtained
* ``SafeOpenScore`` - points awarded for opening the safe with the correct
  combination
* ``SafeSecrets`` - valid safe combination characters
* ``SaveGameDir`` - the directory in which saved games will be stored
* ``SaveGameCompression`` - the compression level to use when saving a game
  (0 = no compression, 9 = maximum compression)
* ``ScreenshotDir`` - the directory in which screenshots are dumped
* ``SherryId`` - the ID to use for sherry fired from a water pistol; by default
  this is different from the value of ``WaterId`` so that sherry will not make
  plants grow
* ``SpriteSize`` - the width and height of a sprite (in tiles)
* ``StoreroomCombinationScore`` - points awarded for writing the storeroom
  combination on a blackboard
* ``StoreroomDoorId`` - the ID of the science lab storeroom door (see
  :ref:`doors`); this is used to detect whether Eric can open a door with the
  storeroom key
* ``StoreroomSecrets`` - valid storeroom combination characters
* ``TooManyLinesCommandList`` - the ID of the command list Mr Wacker should use
  to expel Eric after he's exceeded the lines limit
* ``UpAYearScore`` - points awarded for advancing a year
* ``Volume`` - the sound effects volume (0.0 = silent, 1.0 = maximum)
* ``WaterId`` - the ID to use for water fired from a water pistol; liquid with
  this ID will make plants grow (see ``SherryId``)
* ``WindowProximity`` - maximum distance at which a window is considered nearby
  (i.e. worth opening if a stinkbomb is smelt)

+---------+------------------------------------------------------------------+
| Version | Changes                                                          |
+=========+==================================================================+
| 1.1.1   | Added the ``ConfirmClose``, ``ConfirmQuit`` and ``Volume``       |
|         | parameters                                                       |
+---------+------------------------------------------------------------------+
| 0.5     | Added the ``MouseCatchScore`` parameter                          |
+---------+------------------------------------------------------------------+
| 0.4     | Added the ``Icon``, ``SaveGameDir``, ``SaveGameCompression`` and |
|         | ``ScreenshotDir`` parameters                                     |
+---------+------------------------------------------------------------------+
| 0.3     | New                                                              |
+---------+------------------------------------------------------------------+

[GrassMessages]
---------------
The ``GrassMessages`` section contains five lines of the form::

  Writers, characterId[, characterId...]
  WriteTale, <text>
  Hitters, characterId[, characterId...]
  HitTale, <text>
  AbsentTale, <text>

The information in this section is used by the swot to determine who can be
blamed for hitting him or writing on a blackboard, and what to say when telling
tales.

The ``Writers`` line contains a comma-separated list of IDs of characters who
can be blamed for writing on a blackboard. The ``WriteTale`` line contains the
text of the blackboard-writing tale.

The ``Hitters`` line contains a comma-separated list of IDs of characters who
can be blamed for hitting the swot. The ``HitTale`` line contains the text of
the so-and-so-hit-me tale.

The ``AbsentTale`` line contains the text that will be spoken by the swot when
he's telling on Eric for being absent during class.

The text of a tale may contain any of the following macros:

* ``$TITLE`` - which will be replaced by the teacher's title, as defined in the
  :ref:`characters` section; to change this macro, set the ``TitleMacro``
  configuration parameter in the :ref:`messageConfig` section
* ``$1`` - which will be replaced by the name of the hitter or writer chosen
  from the ``Hitters`` or ``Writers`` list; to change this macro, set the
  ``GrasseeMacro`` configuration parameter in the :ref:`messageConfig` section
* ``$characterId`` (where ``characterId`` is the unique ID of any character) -
  which will be replaced by the name of that character

+---------+--------------------------+
| Version | Changes                  |
+=========+==========================+
| 0.3     | Renamed from ``[Grass]`` |
+---------+--------------------------+
| 0.1     | New (as ``[Grass]``)     |
+---------+--------------------------+

.. _images:

[Images]
--------
Each line in the ``Images`` section has the form::

  imageId, path

where

* ``imageId`` is the unique ID of an image
* ``path`` is the location of the corresponding image file on disk (relative to
  the `images` directory)

Recognised image IDs and the images they refer to are:

* ``FONT``: the skool font
* ``INVENTORY``: mouse, frog, water pistol etc.
* ``LESSON_BOX``: the lesson box background
* ``LOGO``: the logo
* ``MESSAGE_BOX``: the message box used to display messages above a character's
  head (lines messages, escape alarm messages, and safe, bike, and storeroom
  combination characters)
* ``MUTABLES``: mutable objects (e.g. doors, windows, cups, shields, safe) -
  full colour
* ``MUTABLES_INK``: mutable objects (e.g. doors, windows, cups, shields, safe)
  - ink colours only
* ``MUTABLES_PAPER``: mutable objects (e.g. doors, windows, cups, shields,
  safe) - paper colours only
* ``SCOREBOX``: the score/lines/hi-score box background
* ``SKOOL``: the skool - full colour
* ``SKOOL_INK``: the skool - ink colours only
* ``SKOOL_PAPER``: the skool - paper colours only
* ``SPEECH_BUBBLE``: speech bubble and lip
* ``SPRITES``: the characters in various 'animatory states'

+---------+--------------------------------------------------------+
| Version | Changes                                                |
+=========+========================================================+
| 0.4     | Added the ``LESSON_BOX`` and ``MESSAGE_BOX`` image IDs |
+---------+--------------------------------------------------------+
| 0.0.4   | New                                                    |
+---------+--------------------------------------------------------+

.. _inventory:

[Inventory]
-----------
Each line in the ``Inventory`` section has the form::

  itemId, topLeft, size

where:

* ``itemId`` is the unique ID of an item that can be collected
* ``topLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  image of the item in `inventory.png`
* ``size`` is the size of the image (in `(width, height)` form)

The item IDs recognised by Pyskool are as follows:

* ``FROG`` - a frog
* ``MOUSE`` - a mouse
* ``SAFE_KEY`` - the key to the head's safe
* ``SHERRY_PISTOL`` - a water pistol (containing sherry)
* ``STINKBOMBS3`` - three stinkbombs
* ``STINKBOMBS2`` - two stinkbombs
* ``STINKBOMBS1`` - one stinkbomb
* ``STOREROOM_KEY`` - the key to the science lab storeroom
* ``WATER_PISTOL`` - a water pistol (containing water)

The order in which the items appear in the ``Inventory`` section determines the
order in which they will be printed in the on-screen inventory.

See also the :ref:`mice` and :ref:`frogs` sections (for details on those
animals), and the ``InventoryPos`` and ``MouseInventoryPos`` configuration
parameters in the :ref:`screenConfig` section.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.2     | New     |
+---------+---------+

.. _lessons:

[Lesson ...]
------------
The ``[Lesson ...]`` section names take the form::

  Lesson lessonId [*]characterId, roomId

if the lesson will take place with a teacher in a classroom or the dinner hall,
or::

  Lesson lessonId locationId

if the lesson is an unsupervised period, where:

* ``lessonId`` is the lesson ID as it appears in the :ref:`timetable` section
* ``characterId`` is the character ID of the teacher taking Eric's class
  (prefixed by '*' if the teacher's  name should not be printed in the lesson
  box, as during ``DINNER``)
* ``roomId`` is the ID of the room in which Eric's class will take place
* ``locationId`` is one of ``PLAYTIME``, ``REVISION LIBRARY``, and ``ASSEMBLY``

Each line in a ``[Lesson ...]`` section has the form::

  characterId, commandListId

where

* ``characterId`` is the unique ID of a character (see :ref:`characters`)
* ``commandListId`` is the ID of the :ref:`command list <commandList>` that
  will control the character's movements during the lesson

A command list is a sequence of commands - such as :ref:`goTo` or
:ref:`findSeat` - that make a character appear intelligent (kind of). See
:ref:`commandList` for more details.

In any ``[Lesson ...]`` section there should be one line for each character
defined in the :ref:`characters` section.

.. _lessonConfig:

[LessonConfig]
--------------
The ``LessonConfig`` section contains configuration parameters in the format::

  parameterName, parameterValue

Recognised parameters are:

* ``BlackboardBacktrack`` - the distance a teacher walks back after wiping a
  blackboard
* ``BlackboardPaceDistance`` - the distance a teacher should pace up and down
  in front of the blackboard during a lesson without a question-and-answer
  session
* ``EricsTeacherWriteOnBoardProbability`` - the probability that a teacher will
  write on the blackboard during a lesson with Eric and the swot
* ``GrassForHittingProbability`` - the probability that the swot will grass on
  someone for hitting him
* ``LinesForTalesProbability`` - the probability that the teacher will give the
  swot lines for telling tales
* ``QASessionProbability`` - the probability that the teacher will start a
  question-and-answer session with the swot
* ``WriteOnBoardProbability`` - the probability that a teacher will write on
  the blackboard during a lesson without Eric and the swot

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.3     | New     |
+---------+---------+

.. _lessonMessages:

[LessonMessages]
----------------
The ``LessonMessages`` section contains a list of messages that will be used by
teachers who are not teaching Eric, or teachers who are teaching Eric but have
chosen not to do a question-and-answer session. Each line in the section takes
the form::

  characterId|*, lessonMessage[, condition]

where:

* ``characterId`` is the unique ID of a teacher
* ``lessonMessage`` is the message to add to that teacher's repertoire
* ``condition`` is a condition identifier that must evaluate to true before the
  message can be used

If ``*`` is used instead of a specific character ID, the message will be placed
in every teacher's repertoire.

A lesson message may contain a character sequence ``$(N, M)`` (where `N` and
`M` are numbers); if so, it will be replaced by a random number between `N` and
`M`.

The only recognised condition identifier is:

* ``BoardDirty``

(as defined by the ``BoardDirtyConditionId`` parameter in the
:ref:`messageConfig` section) which, if specified, means the message will be
used only if the blackboard (if there is one) has been written on. Any other
condition identifier will evaluate to true.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.0.3   | New     |
+---------+---------+

.. _linesMessages:

[LinesMessages]
---------------
The ``LinesMessages`` section contains a list of admonitions delivered by
lines-givers when Eric has been spotted doing something he shouldn't. Each line
in this section has the form::

  characterId|*, linesMessageId, linesMessage

where

* ``characterId`` is the unique ID of the lines-giving character
* ``linesMessageId`` is the unique ID of the following message
* ``linesMessage`` is the admonition itself

If ``*`` is used instead of a character ID, the lines message will be used by
all lines-givers (unless they have been explicitly assigned a lines message
with the same lines message ID). For example::

  WITHIT, NO_HITTING, BE GENTLE^NOW
  *, NO_HITTING, DON'T HIT^YOUR MATES

would make Mr Withit scream "BE GENTLE NOW" whenever he sees Eric throwing a
punch, whereas every other teacher would scream "DON'T HIT YOUR MATES" instead.

A lines message always spans two lines on-screen. A caret (``^``) is used by
default to indicate where the words should be wrapped; to change this, set the
``Newline`` configuration parameter in the :ref:`messageConfig` section.

The recognised lines message IDs are:

* ``BACK_TO_SKOOL`` - Eric should be back in the boys' skool by now
* ``BE_PUNCTUAL`` - Eric was late for class
* ``COME_ALONG_1`` - the truant Eric is being guided to the classroom
* ``COME_ALONG_2`` - the truant Eric is still being guided to the classroom
* ``COME_ALONG_3`` - the truant Eric still hasn't made it to the classroom
* ``GET_ALONG`` - Eric is not in class when he should be
* ``GET_OFF_PLANT`` - Eric is standing on a plant
* ``GET_OUT`` - Eric is somewhere that only staff are allowed to be
* ``GET_UP`` - Eric is sitting on the floor
* ``NEVER_AGAIN`` - a teacher thinks Eric knocked him down
* ``NO_BIKES`` - Eric is riding a bike inside the skool
* ``NO_CATAPULTS`` - Eric is firing a catapult
* ``NO_HITTING`` - Eric is throwing a punch
* ``NO_JUMPING`` - Eric is jumping
* ``NO_SITTING_ON_STAIRS`` - Eric is sitting on the stairs
* ``NO_STINKBOMBS`` - Eric has dropped a stinkbomb
* ``NO_TALES`` - the swot gets his just deserts
* ``NO_WATERPISTOLS`` - Eric is firing a water pistol
* ``NO_WRITING`` - Eric is writing on a blackboard
* ``SIT_DOWN`` - Eric is standing up in class
* ``SIT_FACING_STAGE`` - Eric is not facing the headmaster during assembly
* ``STAY_IN_CLASS`` - Eric popped out of class and then returned

The lines message IDs are used internally, and should not be changed. If a
particular lines message ID is missing from the list, then lines will not be
given for the infraction it refers to. So if there were no entry in the
``LinesMessages`` section with the lines message ID ``NO_HITTING``, no lines
would ever be dished out for hitting.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.0.3   | New     |
+---------+---------+

.. _messageConfig:

[MessageConfig]
---------------
The ``MessageConfig`` section contains messages and message-related
configuration parameters that apply skool-wide. Each line in this section has
the form::

  parameterName, parameterValue

Recognised parameters are:

* ``BoardDirtyConditionId`` - the ID of the condition used to indicate that a
  blackboard is dirty; this identifier may be used in the :ref:`lessonMessages`
  section
* ``GrasseeMacro`` - the macro that expands to a grassee's name in the swot's
  speech
* ``HiScoreLabel`` - the label for the hi-score in the score box
* ``LinesMessageTemplate`` - the template used for lines messages
* ``LinesRecipientMacro`` - the macro that will be replaced in
  ``LinesMessageTemplate`` (see above) by the lines recipient's name
* ``LinesTotalLabel`` - the label for the lines total in the score box
* ``Newline`` - the character that will be replaced by a newline character in
  messages written on a blackboard, in a lines bubble, or in the lesson box
* ``NumberOfLinesMacro`` - the macro that will be replaced in
  ``LinesMessageTemplate`` (see above) by the number of lines being given
* ``ScoreLabel`` - the label for the score in the score box
* ``TitleMacro`` - the macro that expands to a teacher's title in the swot's
  speech
* ``UpAYearMessage`` - the message printed in the lesson box when Eric has
  completed the game and advanced a year

+---------+-----------------------------------------------------+
| Version | Changes                                             |
+=========+=====================================================+
| 0.4     | Added the ``HiScoreLabel``, ``LinesTotalLabel`` and |
|         | ``ScoreLabel`` parameters                           |
+---------+-----------------------------------------------------+
| 0.3     | New                                                 |
+---------+-----------------------------------------------------+

.. _mice:

[Mice]
------
Each line in the ``Mice`` section has the form::

  mouseId, spriteGroupId, animatoryState, (x, y), commandListId, spriteXY

where:

* ``mouseId`` is the unique ID of the mouse
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the mouse
* ``animatoryState`` is the mouse's initial animatory state
* ``(x, y)`` are the mouse's initial coordinates
* ``commandListId`` is the ID of the :ref:`command list <commandList>` that the
  mouse will use
* ``spriteXY`` is the coordinates of the mouse within its sprite (used for
  detecting whether Eric has caught it)

Any mouse defined in this section will be catchable by ERIC, and show up in the
on-screen mouse inventory when caught.

+---------+----------------------------------+
| Version | Changes                          |
+=========+==================================+
| 0.3     | Added the ``spriteXY`` parameter |
+---------+----------------------------------+
| 0.2.1   | New                              |
+---------+----------------------------------+

.. _mouseLocations:

[MouseLocations]
----------------
The ``MouseLocations`` section defines the locations at which a new immortal
mouse may appear after Eric catches one. Each line has the form::

  x, y

where ``(x, y)`` are the coordinates of the location.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.3     | New     |
+---------+---------+

[NoGoZones]
-----------
Each line in the ``NoGoZones`` section corresponds to a region of the skool
Eric is never supposed to enter. The lines take the form::

  zoneId, minX, maxX, bottomY, topY

where:

* ``zoneId`` is a descriptive ID for the zone (not used anywhere else)
* ``minX`` is the lower x-coordinate of the zone
* ``maxX`` is the upper x-coordinate of the zone
* ``bottomY`` is the y-coordinate of the bottom of the zone
* ``topY`` is the y-coordinate of the top of the zone

Whenever Eric is spotted in one of these zones by a teacher, the ``GET_OUT``
:ref:`lines message <linesMessages>` will be delivered in screeching tones.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.0.4   | New     |
+---------+---------+

.. _plants:

[Plants]
--------
The ``Plants`` section contains information about plants. Each line describes a
single plant, and has the form::

  plantId, spriteGroupId, x, y, commandListId

where:

* ``plantId`` is the unique ID of the plant
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the plant
* ``x`` and ``y`` are the coordinates of the plant (when it is growing or has
  grown)
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the plant will use when watered

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.2.1   | New     |
+---------+---------+

.. _questionsAndAnswers:

[QuestionsAndAnswers ...]
-------------------------
The ``[QuestionsAndAnswers ...]`` section names take the form::

  QuestionsAndAnswers characterId

where ``characterId`` is the unique ID of a teacher (see :ref:`characters`).

There are at least three types of entry in a ``[QuestionsAndAnswers ...]``
section. The first type of entry is the ``Question`` entry::

  Question, questionId, groupId, questionTemplate

where:

* ``questionId`` is a unique (within the section) ID for the question
* ``groupId`` is the ID of the group of Q&A pairs (see below) the question is
  associated with
* ``questionTemplate`` is the question template

There should be at least one ``Question`` entry in a
``[QuestionsAndAnswers ...]`` section.

The second type of entry is the ``Answer`` entry::

  Answer, questionId, answerTemplate

where:

* ``questionId`` is the ID of the question to which this is the answer
* ``answerTemplate`` is the answer template

There should be one ``Answer`` entry for each ``Question`` entry in a
``[QuestionsAndAnswers ...]`` section.

The third type of entry in this section is the Q&A pair entry::

  groupId, word1, word2

where

* ``groupId`` is the ID of the group of Q&A pairs to which this particular pair
  belongs; the ID should be something other than `Question`, `Answer`,
  `SpecialGroup`, `SpecialQuestion` or `SpecialAnswer`, which are reserved
  words in a ``[QuestionsAndAnswers ...]`` section
* ``word1`` and ``word2`` are the words that will replace the macros in
  ``questionTemplate`` and ``answerTemplate``

There should be at least one Q&A pair defined per ``[QuestionsAndAnswers ...]``
section (and ideally many more than one, to prevent the question-and-answer
sessions between teachers and the swot from being rather monotonous).

The optional fourth type of entry in a ``[QuestionsAndAnswers ...]`` section
consists of three lines::

  SpecialQuestion, question
  SpecialAnswer, answer
  SpecialGroup, groupId, qaPairIndex

and is used to define the "special" question Eric will need the answer to in
order to obtain the relevant teacher's safe combination letter. The
``SpecialQuestion`` keyword is followed by the text of the special question
(which will be posed by the teacher at the start of the lesson). The
``SpecialAnswer`` keyword is followed by the text of the swot's answer to the
special question (which will contain a macro to be expanded). The
``SpecialGroup`` keyword is followed by ``groupId`` (which specifies the ID of
the group of Q&A Pairs from which the "magic word" will be taken), and
``qaPairIndex`` (which is 0 or 1, and refers to the element of the Q&A pair
that will be the magic word). Once Eric has figured out what the magic word is,
he will need to write it on a blackboard and hope that the teacher sees it,
whereupon the teacher will reveal his safe combination letter.

If the ``SpecialQuestion``, ``SpecialAnswer`` and ``SpecialGroup`` lines are
not present, there will be no magic word associated with the teacher. In that
case, simply knocking the teacher over with a catapult pellet will make him
reveal his safe combination letter.

.. _randomLocations:

[RandomLocations]
-----------------
The ``RandomLocations`` section contains lists of suitable locations for the
characters to visit when they go on walkabouts (e.g. during playtime). Each
line has the form::

  characterId, (x1, y1), (x2, y2)...

where:

* ``characterId`` is the character's unique ID (see :ref:`characters`)
* ``(x1, y1)`` and so on are the coordinates of locations in the skool

There must be at least one pair of coordinates per line, and there should be
one line for each character defined in the :ref:`characters` section.

.. _rooms:

[Rooms]
-------
The ``Rooms`` section contains one line for each room or region in the skool
that Eric will be expected to show up at when the timetable requires it. Each
line has the form::

  roomId, name, topLeft, bottomRight, getAlong

where:

* ``roomId`` is the room's unique ID
* ``name`` is the room's name (as displayed in the lesson box at the bottom of
  the screen)
* ``topLeft`` is the coordinates of the top-left corner of the room
* ``bottomRight`` is the coordinates of the bottom-right corner of the room
* ``getAlong`` is ``Y`` if Eric should get lines for being in the room when the
  timetable does not require his presence

+---------+----------------------------------+
| Version | Changes                          |
+=========+==================================+
| 0.2.1   | Added the ``getAlong`` parameter |
+---------+----------------------------------+

.. _routes:

[Routes]
--------
The ``Routes`` section is one of the most important sections in the ini file.
It defines the routes (a route may be considered as a list of staircases) that
the characters must take to get from where they are to wherever they are going.
Any errors here will result in the characters wandering aimlessly around the
skool, unable to find classrooms, the playground, or the toilets. Disaster!

Anyway, each line in this section has the form::

  homeFloorId, *|destFloorId[, destFloorId[, ...]], nextStaircaseId

where:

* ``homeFloorId`` is the unique ID of one floor (see :ref:`floors`) - the
  'home' floor
* ``destFloorId`` is the unique ID of another floor (see :ref:`floors`) - the
  destination floor
* ``nextStaircaseId`` is the unique ID of the staircase (see :ref:`staircases`)
  that must be climbed or descended first on a journey from the home floor to
  the destination floor

How this works is best illustrated by example. Let's look at the routes defined
for the bottom floor in Back to Skool to everywhere else in the skool::

  Bottom, LeftMiddle, LeftTop, UpToToilets
  Bottom, GirlsMiddle, GirlsTop, GirlsSkoolLower
  Bottom, *, UpToStage

The first line says that to get from the bottom floor (``Bottom``) to the
floors called ``LeftMiddle`` and ``LeftTop`` (see :ref:`floors`), the first
staircase you need to navigate is ``UpToToilets`` (see :ref:`staircases`). The
second line says that to get from the bottom floor to the middle floor
(``GirlsMiddle``) or top floor (``GirlsTop``) in the girls' skool, you need to
use the ``GirlsSkoolLower`` staircase first. The third line says that to get
anywhere else (``*``) from the bottom floor, you need to take the stairs up to
the stage (``UpToStage``).

[Safe]
------
The ``Safe`` section contains a single line of the form::

  topLeft, size, coords

where:

* ``topLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  normal image of the safe
* ``size`` is the size of the image (in `(width, height)` form)
* ``coords`` are the coordinates (in `(x, y)` form) of the safe in the play
  area

The safe images can be found in `mutables.png` (or `mutables_ink.png` and
`mutables_paper.png` if ``GraphicsMode`` is 1 - see :ref:`screenConfig`).
`mutables.png` is arranged so that the inverse image of the safe is at
`(x + width, y)`, where `(x, y)` are the coordinates of the normal image of the
safe.

If the safe will never need to flash (as in Back to Skool), ``topLeft`` and
``size`` will not be used, and so may be set to any value.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.0.4   | New     |
+---------+---------+

.. _screenConfig:

[ScreenConfig]
--------------
The ``ScreenConfig`` section contains parameters that determine the appearance
and layout of the screen. Each line has the form::

  parameterName, parameterValue

Recognised parameters are:

* ``Background`` - the background colour of the screen
* ``EscapeAlarmInk`` - the ink colour to use for the escape alarm message box
  used by Albert
* ``EscapeAlarmPaper`` - the paper colour to use for the escape alarm message
  box used by Albert
* ``FlashCycle`` - length of the cycle in which a flashable object (such as a
  shield) flashes once
* ``FontInk`` - the ink colour in `font.png` (used to create transparency)
* ``FontPaper`` - the paper colour in `font.png` (used to create transparency)
* ``GraphicsMode`` - 0 = hi-res colour; 1 = spectrum mode, meaning just two
  colours (ink and paper) per 8x8-pixel block
* ``Height`` - the height of the screen (in tiles)
* ``HiScoreOffset`` - the y-coordinate offset used to position the printing of
  the hi-score
* ``InitialColumn`` - the x-coordinate of the leftmost column of the screen
  when the game starts
* ``InventoryKey`` - pixels of this colour in inventory item and captured mouse
  images will be made transparent when the items are drawn
* ``InventoryPos`` - the x, y coordinates of the inventory on screen
* ``InventorySize`` - the size of the inventory (width and height in tiles)
* ``LessonBoxInk`` - the ink colour to use when writing in the lesson box
* ``LessonBoxPos`` - the x, y coordinates of the lesson box on screen
* ``LinesInk`` - the ink colour used in a lines message box
* ``LinesOffset`` - the y-coordinate offset used to position the printing of
  the lines total
* ``LinesPaperEric`` - the paper colour used in a lines message box when Eric
  is the recipient
* ``LinesPaperOther`` - the paper colour used in a lines message box when Eric
  is not the recipient
* ``LogoPos`` - the x, y coordinates of the logo on screen
* ``MessageBoxColour`` - the colour of the 'inside' of the message box in the
  ``MESSAGE_BOX`` image (see :ref:`images`); pixels of this colour in the image
  will take on the designated paper colour (e.g. ``LinesPaperEric``) when the
  message box is drawn
* ``MessageBoxKey`` - pixels of this colour in the message box image will be
  made transparent when the message box is drawn; in the stock Pyskool, this
  feature is not used
* ``MouseInventoryInk`` - the ink colour to use when writing in the mouse
  inventory
* ``MouseInventoryPos`` - the x, y coordinates of the mouse inventory on screen
* ``MouseInventorySize`` - the size of the mouse inventory (width and height in
  tiles)
* ``Scale`` - the scale factor to use for graphics; 1 = original Spectrum size
* ``ScoreBoxInk`` - the ink colour to use when writing in the score box
* ``ScoreBoxPos`` - the x, y coordinates of the score box on screen
* ``ScoreOffset`` - the y-coordinate offset used to position the printing of
  the score
* ``ScrollFps`` - the number of frames per second at which the screen should be
  scrolled (when the game starts and during play); raise it to make the screen
  scroll faster, or lower it to scroll more slowly
* ``ScrollColumns`` - the number of columns to scroll when Eric approaches the
  left or right edge of the screen
* ``ScrollLeftOffset`` - how close Eric can get to the right edge of the screen
  before it scrolls left
* ``ScrollRightOffset`` - how close Eric can get to the left edge of the screen
  before it scrolls right
* ``SecretInk`` - the ink colour of the message box used to display a safe,
  bike or storeroom combination character
* ``SecretPaper`` - the paper colour of the message box used to display a safe,
  bike or storeroom combination character
* ``SkoolInkKey`` - the transparent colour used in the skool ink image
* ``SpeechBubbleInk`` - the ink colour to use when drawing text in a speech
  bubble
* ``SpeechBubbleKey`` - the transparent colour used in the speech bubble image
  (`bubble.png`)
* ``SpeechBubbleInset`` - the inset (in pixels at scale 1) of the text window
  from the top-left of a speech bubble
* ``SpeechBubbleLipCoords`` - the coordinates of the lip within the speech
  bubble image (`bubble.png`)
* ``SpeechBubbleLipSize`` - the size of the speech bubble lip (width and height
  in tiles)
* ``SpeechBubbleSize`` - the size of the bounding rectangle of a speech bubble,
  including the lip (width and height in tiles)
* ``SpriteKey`` - the transparent colour used in the sprite matrix image
* ``SpriteMatrixWidth`` - the number of sprites in a row of the sprite matrix
  image
* ``Width`` - the width of the screen (in tiles)

+---------+-------------------------------------------------------------------+
| Version | Changes                                                           |
+=========+===================================================================+
| 0.5     | Added the ``SpriteMatrixWidth`` parameter                         |
+---------+-------------------------------------------------------------------+
| 0.4     | Added the ``InventoryKey``, ``MessageBoxColour``,                 |
|         | ``MessageBoxKey``, ``MouseInventoryInk``, ``MouseInventorySize``, |
|         | ``SpeechBubbleKey``, ``SpeechBubbleLipCoords`` and                |
|         | ``SpeechBubbleLipSize`` parameters                                |
+---------+-------------------------------------------------------------------+
| 0.3     | New                                                               |
+---------+-------------------------------------------------------------------+

.. _sherryDrop:

[SherryDrop]
------------
The ``SherryDrop`` section defines a drop of sherry (as knocked out of a cup by
a catapult pellet). It contains a single line of the form::

  objectId, spriteGroupId, commandListId, hitXY

where:

* ``objectId`` is a unique ID for the drop of sherry
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the drop of sherry
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the drop of sherry will use when knocked out of a cup
* ``hitXY`` is the coordinates of the sherry drop within its sprite (used for
  collision detection)

+---------+-------------------------------+
| Version | Changes                       |
+=========+===============================+
| 0.3     | Added the ``hitXY`` parameter |
+---------+-------------------------------+
| 0.2.1   | New                           |
+---------+-------------------------------+

[Shields]
---------
The ``Shields`` section contains information about shields. Each line describes
a single shield, and has the form::

  score, topLeft, size, coords

where:

* ``score`` is the number of points awarded for making the shield flash or
  unflash
* ``topLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  normal image of the shield
* ``size`` is the size of the image (in `(width, height)` form)
* ``coords`` are the coordinates (in `(x, y)` form) of the shield in the play
  area

The shield images can be found in `mutables.png` (or `mutables_ink.png` and
`mutables_paper.png` if ``GraphicsMode`` is 1 - see :ref:`screenConfig`).
`mutables.png` is arranged so that the inverse image of a shield is at
`(x + width, y)`, where `(x, y)` are the coordinates of the normal image of the
shield.

+---------+-------------------------------+
| Version | Changes                       |
+=========+===============================+
| 0.0.4   | Added the ``score`` parameter |
+---------+-------------------------------+
| 0.0.3   | New                           |
+---------+-------------------------------+

.. _sitDownMessages:

[SitDownMessages]
-----------------
The ``SitDownMessages`` section contains one or more lines for each teacher of
the form::

  characterId, sitDownMessage

where

* ``characterId`` is the teacher's unique ID (see :ref:`characters`)
* ``sitDownMessage`` is what the teacher may say while standing at the
  classroom doorway at the start of a lesson

If multiple sit-down messages are defined for a teacher, he will choose one at
random when the time comes. If no sit-down messages are defined for a teacher,
he will say nothing at the classroom doorway.

.. _skoolLocations:

[SkoolLocations]
----------------
The ``SkoolLocations`` section contains a list of descriptive IDs for commonly
used locations in the skool. These descriptive IDs are used by the :ref:`goTo`
command in the :ref:`command lists <commandList>` that control the characters.
Each line in this section has the form::

  locationId, x, y

where

* ``locationId`` is the descriptive ID
* ``x`` and ``y`` are the coordinates of the location

An example of a location ID is ``BlueRoomDoorway``, which means exactly what
you think it means.

.. _sounds:

[Sounds]
--------
Each line in the ``Sounds`` section has the form::

  soundId, path

where

* ``soundId`` is the unique ID of a sound effect
* ``path`` is the location of the sound file on disk (relative to the `sounds`
  directory)

``path`` may be the full name of the sound file (e.g. `tune.wav`), or just the
base name (e.g. `tune`); in the latter case, Pyskool will look for a file with
the base name and a `.wav` or `.ogg` suffix.

Recognised IDs and the sound effects they refer to are:

* ``ALARM``: Albert is telling Mr Wacker that Eric is escaping
* ``ALL_SHIELDS``: Eric has hit all the shields
* ``BELL``: the bell
* ``BIKE``: Eric has written the bike combination on a blackboard
* ``CATAPULT``: Eric has fired his catapult
* ``CONKER``: Eric has knocked out Albert with a conker
* ``DESK``: Eric has found the water pistol or stinkbombs in a desk
* ``FROG``: Eric has caught the frog or placed it in a cup
* ``HIT0``, ``HIT1``: Eric has thrown a punch
* ``JUMP``: Eric has jumped into the air
* ``KISS``: Eric has kissed someone
* ``KNOCKED_OUT``: Eric has been knocked over or out of his chair
* ``LINES1``: lines screech 1
* ``LINES2``: lines screech 2
* ``MOUSE``: Eric has caught a mouse
* ``OPEN_SAFE``: Eric has opened the safe (by getting the combination)
* ``SAFE_KEY``: Eric has got the safe key
* ``SHERRY``: Eric has filled the water pistol with sherry
* ``SHIELD``: Eric has hit a shield
* ``STOREROOM_KEY``: Eric has written the storeroom combination on a blackboard
* ``TUNE``: opening tune
* ``UP_A_YEAR``: Eric has gone up a year
* ``WALK0``, ``WALK1``, ``WALK2``, ``WALK3``: Eric walking
* ``WATER_PISTOL``: Eric has fired his water pistol

If an entry for a given sound effect is not present in the ``Sounds`` section,
then that sound effect will never play. For example, if there is no
``CATAPULT`` entry, then Eric's firings of that weapon will be completely
silent.

+---------+--------------------------------------------------------+
| Version | Changes                                                |
+=========+========================================================+
| 1.1     | Added the ``ALARM``, ``HIT0`` and ``HIT1`` sound IDs   |
+---------+--------------------------------------------------------+
| 0.5.2   | Added the ``JUMP`` sound ID                            |
+---------+--------------------------------------------------------+
| 0.2.4   | Added the ``BIKE``, ``DESK``, ``KISS``, ``OPEN_SAFE``, |
|         | ``STOREROOM_KEY`` and ``WATER_PISTOL`` sound IDs       |
+---------+--------------------------------------------------------+
| 0.2     | Added the ``FROG``, ``MOUSE`` and ``SHERRY`` sound IDs |
+---------+--------------------------------------------------------+
| 0.0.3   | New                                                    |
+---------+--------------------------------------------------------+

.. _specialPlaytimes:

[SpecialPlaytimes]
------------------
The ``SpecialPlaytimes`` section contains a list of lesson IDs that refer to
playtimes which will be considered "special". A special playtime does not
appear in the timetable proper (though you could insert it), but with a given
probability (defined by the ``SpecialPlaytimeProbability`` parameter in the
:ref:`timetableConfig` section) a special playtime chosen at random is
substituted for an actual playtime from the main timetable. In Skool Daze the
``SpecialPlaytimes`` section looks like this::

  Playtime-Mumps
  Playtime-SwotGrass
  Playtime-HiddenPeaShooter

Thus, occasionally in Skool Daze mode a playtime will be one of those where you
have to steer clear of the pestilential bully, prevent the swot from reaching
the head's study, or fix the race to the fire escape between the tearaway and
the headmaster.

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.1     | New     |
+---------+---------+

.. _spriteGroup:

[SpriteGroup ...]
-----------------
The ``[SpriteGroup ...]`` section names take the form::

  SpriteGroup spriteGroupId

where ``spriteGroupId`` is a unique ID for a group of sprites in `sprites.png`
(see :ref:`graphics`) - such as ``BOY`` for the little boys, or ``TEARAWAY``
for the tearaway. The unique ID can be anything you like; it is used only in
the :ref:`characters` section later on to link a character to a specific group
of sprites.

Each line in a ``SpriteGroup`` section represents a single sprite from
`sprites.png` and has the form::

  spriteId, index

where

* ``spriteId`` is the descriptive ID for the sprite (unique within the section)
* ``index`` is the index of the sprite as it appears in `sprites.png`

Recognised sprite IDs and their meanings are:

* ``ARM_UP``: arm up (as if writing or opening door) - Eric, the tearaway, the
  Heroine and teachers
* ``BENDING_OVER``: bending over - Eric
* ``BIKE_ON_FLOOR``: bike resting on the floor
* ``BIKE_UPRIGHT``: bike upright
* ``CATAPULT0``: firing catapult (1) - Eric and the tearaway
* ``CATAPULT1``: firing catapult (2) - Eric and the tearaway
* ``CONKER``: conker
* ``DESK_EMPTY``: desk lid (empty desk)
* ``DESK_STINKBOMBS``: desk lid (with stinkbombs)
* ``DESK_WATER_PISTOL``: desk lid (with water pistol)
* ``FLY``: catapult pellet in flight
* ``HITTING0``: hitting (1) - Eric and the bully
* ``HITTING1``: hitting (2) - Eric and the bully
* ``HOP1``: frog hopping (phase 1)
* ``HOP2``: frog hopping (phase 2)
* ``KISSING_ERIC``: kissing Eric - the Heroine
* ``KNOCKED_OUT``: lying flat on back - kids
* ``KNOCKED_OVER``: sitting on floor holding head - adults
* ``PLANT_GROWING``: plant (half-grown)
* ``PLANT_GROWN``: plant (fully grown)
* ``RIDING_BIKE0``: riding bike (1) - Eric
* ``RIDING_BIKE1``: riding bike (2) - Eric
* ``RUN``: mouse
* ``SHERRY_DROP``: drop of sherry (knocked from a cup)
* ``SIT``: frog sitting
* ``SITTING_ON_CHAIR``: sitting on a chair - kids
* ``SITTING_ON_FLOOR``: sitting on the floor - kids
* ``STINKBOMB``: stinkbomb cloud
* ``WALK0``: standing/walking (1) - all characters
* ``WALK1``: midstride (1) - all characters
* ``WALK2``: standing/walking (2) - all characters
* ``WALK3``: midstride (2) - all characters
* ``WATER_DROP``: drop of water (knocked from a cup)
* ``WATER0``: water fired from a pistol (phase 1)
* ``WATER1``: water fired from a pistol (phase 2)
* ``WATER2``: water fired from a pistol (phase 3)
* ``WATER3``: water fired from a pistol (phase 4)
* ``WATER4``: water fired from a pistol (phase 5)
* ``WATERPISTOL``: shooting water pistol - Eric

+---------+----------------------------------------------------------------+
| Version | Changes                                                        |
+=========+================================================================+
| 0.2.1   | Added the ``BIKE_ON_FLOOR``, ``BIKE_UPRIGHT``, ``DESK_EMPTY``, |
|         | ``DESK_STINKBOMBS``, ``DESK_WATER_PISTOL``, ``KISSING_ERIC``,  |
|         | ``PLANT_GROWING``, ``PLANT_GROWN``, ``SHERRY_DROP``,           |
|         | ``WATER_DROP``, ``WATER0``, ``WATER1``, ``WATER2``, ``WATER3`` |
|         | and ``WATER4`` sprite IDs                                      |
+---------+----------------------------------------------------------------+
| 0.2     | Added the ``HOP1``, ``HOP2``, ``RUN`` and ``SIT`` sprite IDs   |
+---------+----------------------------------------------------------------+
| 0.0.3   | New                                                            |
+---------+----------------------------------------------------------------+

.. _staircases:

[Staircases]
------------
The ``Staircases`` section contains details of the staircases in the skool.
Each line has the form::

  staircaseId[:alias], bottom, top[, force]

where:

* ``staircaseId`` is the staircase's unique ID
* ``alias`` is an optional alias for the staircase (also unique)
* ``bottom`` and ``top`` are the coordinates of the bottom and top of the
  staircase (in `(x, y)` form)
* ``force``, if present, indicates that the staircase must be climbed or
  descended by Eric if he moves to a location between the bottom and the top

In the stock Pyskool, ``force`` is used for the staircase in Back to Skool that
leads down to the assembly hall stage; it's the only staircase in the game that
you must go up or down if you approach it.

An example of a line from the ``Staircases`` section is::

  UpToStudy:DownFromStudy, (91, 10), (84, 3)

which defines the staircase that leads up to the head's study in Back to Skool.
This staircase's unique ID is ``UpToStudy``, but it can also be referred to as
``DownFromStudy``. These unique IDs and aliases are used in the :ref:`routes`
section.

.. _stinkbombs:

[Stinkbombs]
------------
Each line in the ``Stinkbombs`` section has the form::

  characterId, stinkbombId, spriteGroupId, commandListId, animationPhases, stinkRange

where:

* ``characterId`` is the unique ID of the character to give stinkbomb-dropping
  ability to
* ``stinkbombId`` is the unique ID of the stinkbomb
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the stinkbomb when dropped
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the stinkbomb will use when dropped
* ``animationPhases`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` that the stinkbomb cloud will use
* ``stinkRange`` - the maximum distance at which the stinkbomb can be smelt

Each character whose unique ID appears in this section will be given the
ability to drop a stinkbomb. In the stock Pyskool this will be Eric.

+---------+-------------------------------------------------------------+
| Version | Changes                                                     |
+=========+=============================================================+
| 0.3     | Added the ``animationPhases`` and ``stinkRange`` parameters |
+---------+-------------------------------------------------------------+
| 0.2.3   | Added the ``stinkbombId`` parameter                         |
+---------+-------------------------------------------------------------+
| 0.2.1   | New                                                         |
+---------+-------------------------------------------------------------+

.. _timetable:

[Timetable]
-----------
The ``Timetable`` section contains an ordered list of lesson IDs. Lessons
happen starting with the first in the list, and proceed one by one to the end
of the list. When the last lesson in the list is finished, the game loops back
round to the first lesson in the list.

An example of a lesson ID is ``Creak-BlueRoom-1``, which refers to the first of
a set of lessons in which Eric and the swot are taught by Mr Creak in the Blue
Room. The lesson ID could be anything, but it's helpful to make it descriptive.

A lesson can be thought of as a set of entries from the personal timetables
of the characters. These sets of entries can be found in the :ref:`lessons`
sections.

.. _timetableConfig:

[TimetableConfig]
-----------------
The ``TimetableConfig`` section contains configuration parameters in the
format::

  parameterName, parameterValue

Recognised parameters are:

* ``AssemblyPrefix`` - what a :ref:`lesson ID <lessons>` must start with to be
  regarded as Assembly
* ``GetAlongTime`` - maximum time allowed to leave a classroom or the
  playground after the bell rings
* ``LessonLength`` - the length of a lesson period in frames (see ``GameFps``)
* ``LessonStartTime`` - when a lesson starts (i.e. teacher will tell kids to
  sit down) in frames (see ``GameFps``) from the start of the period
* ``PlaytimePrefix`` - what a :ref:`lesson ID <lessons>` must start with to be
  regarded as Playtime
* ``SpecialPlaytimeProbability`` - the probability that a playtime in the main
  timetable will be replaced by a :ref:`special playtime <specialPlaytimes>`

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.3     | New     |
+---------+---------+

.. _timingConfig:

[TimingConfig]
--------------
The ``TimingConfig`` section contains configuration parameters in the format::

  parameterName, parameterValue

Recognised parameters are:

* ``BendOverDelay`` - the delay (in frames) before Eric stands upright after
  bending over (as when releasing mice)
* ``DethronedDelay`` - the delay before a character rises after being pushed
  out of a seat
* ``EricWalkDelay`` - the number of frames between successive movements of
  Eric when he's walking
* ``JumpDelay`` - the delay (in frames) before Eric returns to the floor after
  jumping
* ``KnockedOverDelay`` - the delay before a knocked over teacher rises
* ``KnockoutDelay`` - the delay before a knocked out kid rises
* ``GoFast`` - the number of frames between successive movements of a character
  who is moving quickly; this parameter is used when a character is running or
  speaking
* ``GoFaster`` - the number of frames between successive movements of a
  character who is moving even quicker; this parameter is used when a character
  is throwing a punch or firing a catapult
* ``GoSlow`` - the number of frames between consecutive movements of a
  character who is moving slowly; this parameter is used when a character is
  walking at a normal pace
* ``ReprimandDelay`` - the delay before a knocked over teacher gives lines to
  someone for knocking him over
* ``SpeedChangeDelayRange`` - the minimum and maximum values of the delay
  between a character's walking speed changes (used by kids, who walk half the
  time and run the other half)
* ``TellEricDelay`` - the length of time a character will wait for Eric to
  respond to a message before repeating it

+---------+---------+
| Version | Changes |
+=========+=========+
| 0.3     | New     |
+---------+---------+

.. _walls:

[Walls]
-------
The ``Walls`` section contains details of the impenetrable barriers in the
skool. Each line has the form::

  wallId, x, bottomY, topY

where:

* ``wallId`` is the wall's unique ID
* ``x`` is the wall's x-coordinate
* ``bottomY`` and ``topY`` are the y-coordinates of the bottom and top of the
  wall

For example::

  FarLeftWall, 0, 20, 0

defines the wall at the far left (x=0) of the skool, which stretches from the
bottom floor (y=20) to the ceiling of the top floor (y=0).

+---------+--------------------------------+
| Version | Changes                        |
+=========+================================+
| 0.2.1   | Added the ``wallId`` parameter |
+---------+--------------------------------+

.. _water:

[Water]
-------
Each line in the ``Water`` section has the form::

  characterId, waterId, spriteGroupId, commandListId, animationPhases

where:

* ``characterId`` is the unique ID of the character to give water pistol-firing
  ability to
* ``waterId`` is the unique ID for the water sprite
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the water fired from the pistol
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the water will use when fired from the pistol
* ``animationPhases`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` that the water will use after being
  fired from the water pistol

Each character whose unique ID appears in this section will be given the
ability to fire a water pistol. In the stock Pyskool this will be Eric alone;
he is the only character with a water pistol-firing sprite.

+---------+-----------------------------------------+
| Version | Changes                                 |
+=========+=========================================+
| 0.3     | Added the ``animationPhases`` parameter |
+---------+-----------------------------------------+
| 0.2.3   | Added the ``waterId`` parameter         |
+---------+-----------------------------------------+
| 0.2.1   | New                                     |
+---------+-----------------------------------------+

.. _waterDrop:

[WaterDrop]
-----------
The ``WaterDrop`` section defines a drop of water (as knocked out of a cup by a
catapult pellet). It contains a single line of the form::

  objectId, spriteGroupId, commandListId, hitXY

where:

* ``objectId`` is a unique ID for the drop of water
* ``spriteGroupId`` is the ID of the :ref:`sprite group <spriteGroup>` to use
  for the drop of water
* ``commandListId`` is the unique ID of the :ref:`command list <commandList>`
  that the drop of water will use when knocked out of a cup
* ``hitXY`` is the coordinates of the water drop within its sprite (used for
  collision detection)

+---------+-------------------------------+
| Version | Changes                       |
+=========+===============================+
| 0.3     | Added the ``hitXY`` parameter |
+---------+-------------------------------+
| 0.2.1   | New                           |
+---------+-------------------------------+

.. _windows:

[Windows]
---------
The ``Windows`` section contains details of the windows in the game. Each line
has the form::

  windowId, x, bottomY, topY, initiallyShut, openerCoords, shutTopLeft, size, coords, descentPhases[, notABird]

where:

* ``windowId`` is the window's unique ID
* ``x`` is the window's x-coordinate
* ``bottomY`` and ``topY`` are the y-coordinates of the bottom and top of the
  window
* ``initiallyShut`` is ``Y`` if the window should be shut when the game starts
* ``openerCoords`` are the coordinates (in `(x, y)` form) at which a character
  should stand in order to open the window
* ``shutTopLeft`` is the coordinates (in `(x, y)` form) of the top left of the
  image of the window when shut
* ``size`` is the size of the image (in `(width, height)` form)
* ``coords`` are the coordinates (in `(x, y)` form) of the window in the skool
* ``descentPhases`` is the ID of the sequence of
  :ref:`animation phases <animationPhases>` to use for Eric if he jumps out of
  the window
* ``notABird`` is the ID of the command list Mr Wacker should switch to when
  Eric hits the ground after falling out of the window; if defined, Eric will
  be paralysed when he hits the ground

The window images can be found in `mutables.png` (or `mutables_ink.png` and
`mutables_paper.png` if ``GraphicsMode`` is 1 - see :ref:`screenConfig`).
`mutables.png` is arranged so that the image of a window when open is at
`(x + width, y)`, where `(x, y)` are the coordinates of the image of the same
window when shut. The open/shut images for any given window are the same size.

+---------+---------------------------------------------------------+
| Version | Changes                                                 |
+=========+=========================================================+
| 0.3     | Added the ``descentPhases`` and ``notABird`` parameters |
+---------+---------------------------------------------------------+
| 0.2.1   | New                                                     |
+---------+---------------------------------------------------------+
