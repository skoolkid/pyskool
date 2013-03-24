.. _example-customisations:

Example customisations
======================
So now you know everything there is to know about the ini files and command
lists, you're ready to don your 'modding' hat and get customising. Right? Well,
if not, you might want to follow the example customisations below to get a feel
for what's possible.

Cursing CREAK
-------------
Maybe the simplest thing to customise is what the characters say. In this
example we customise Mr Creak's sit down message (i.e. how he tells the kids to
sit down when it's time to start a lesson).

To do this, find the ``[SitDownMessages]`` section in `skool_daze/messages.ini`
and edit the line::

  CREAK, BE QUIET AND SEATED YOU NASTY LITTLE BOYS

so that it reads::

  CREAK, ARSES ON SEATS YOU SCUMMY LITTLE BUGGERS

(or whatever other polite request you'd like to see Mr Creak utter). Then run
`skool_daze.py` and giggle like a schoolboy (or girl) as the profanities pour
from the history teacher's mouth.

Blackboard blasphemy
--------------------
An equally simple and giggle-inducing trick is to change what the characters
write on the blackboards. In this example we'll modify Mr Withit's blackboard
messages in Back to Skool.

Open up `back_to_skool/messages.ini` and find the
``[BlackboardMessages WITHIT]`` section. In there you will see the following
messages::

  ARTESIAN^WELLS
  THE DOLDRUMS
  TASTY^GEYSERS
  THE GREEN^REVOLUTION
  TREACLE^MINING
  FROG FARMING

For fun, you can replace these messages with something more interesting, or add
more messages (having only six to choose from makes Mr Withit a dull man). Note
that the ``^`` character will be replaced with a newline.

Then run `back_to_skool.py` and smile with satisfaction as Mr Withit complies
with your particular blackboard message whims.

800 LINES PERKINS
-----------------
Did you ever think it was unfair that the little kids in Skool Daze (i.e. not
Eric, the swot, the tearaway or the bully) never got lines? Eric would down a
teacher with a catapult pellet, but any little kids in the vicinity could
breeze past the teacher with complete impunity while Eric (or, if he was lucky,
one of the other big kids) got slapped in the face with a bunch of lines.

Well this is Pyskool, and we can change all that. To make the little kids in
Skool Daze potential lines recipients, go to the ``[Characters]`` section in
`skool_daze/sprites.ini` and find the lines corresponding to the little boys::

  BOY01, PERKINS, BOY, WALK0, -1, (43, 17), (1, 1), F
  BOY02, GIBSON, BOY, WALK0, 1, (44, 17), (1, 1), F
  BOY03, FANSHAW, BOY, WALK0, -1, (45, 17), (1, 1), F
  ...

The last field in each line (which contains ``F`` by default) is the character
flags field. The character flag that turns a character into a potential lines
recipient is ``R``. So add that flag to each line, thus::

  BOY01, PERKINS, BOY, WALK0, -1, (43, 17), (1, 1), FR
  BOY02, GIBSON, BOY, WALK0, 1, (44, 17), (1, 1), FR
  BOY03, FANSHAW, BOY, WALK0, -1, (45, 17), (1, 1), FR
  ...

Now run `skool_daze.py`, find a teacher milling about with a bunch of little
kids, let rip with the catapult, and experience the satisfaction of seeing the
hitherto nameless ones get their come-uppance.

Punch the pedagogue
-------------------
The teachers in Skool Daze and Back to Skool - well, Mr Wacker and Mr Creak in
particular - were always asking for a smack. Unfortunately, in the original
games teachers were inexplicably impervious to Eric's pugilistic efforts. Eric
could always whip out his catapult and send a teacher to the floor with a
pellet, but it's not quite the same thing.

Anyway, with Pyskool, you get to change the rules. To make the teachers
punchable with effect, open up `skool_daze/sprites.ini` or
`back_to_skool/sprites.ini` and go to the ``[Characters]`` section. There you
will find the lines corresponding to the teachers; in `skool_daze/sprites.ini`
they look like this::

  WACKER, MR WACKER/Sir, WACKER, WALK0, -1, (10, 17), (1, 0), ALPSTW
  ROCKITT, MR ROCKITT/Sir, ROCKITT, WALK0, -1, (10, 17), (1, 0), ALPSTW
  WITHIT, MR WITHIT/Sir, WITHIT, WALK0, -1, (10, 17), (1, 0), ALPSTW
  CREAK, MR CREAK/Sir, CREAK, WALK0, -1, (10, 17), (1, 0), ALPSTW

The last field in each of these lines is the `flags` field (see
:ref:`characters`). To make a teacher punchable, we need to add the ``F`` flag.
For example::

  WACKER, MR WACKER/Sir, WACKER, WALK0, -1, (10, 17), (1, 0), AFLPSTW

Make the change for each teacher you'd like to see Eric (and, as a side effect,
the bully too) be able to punch, and off you go and get your long-awaited
revenge.

History in the Map Room
-----------------------
A somewhat more involved customisation is creating a new lesson. In this example
we'll create a lesson where Mr Creak teaches Eric in the Map Room. In the
original Skool Daze, Mr Creak never taught anywhere but in the Reading and White
Rooms, so it'll be good for him to stretch his ageing legs and get on over to
the Map Room.

Adding an entry to the timetable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
First we are going to add an entry to the ``[Timetable]`` section. So, open up
`skool_daze/lessons.ini`, head over to the ``[Timetable]`` section, and insert
a new lesson ID or replace an existing one - preferably near the top, so you
don't have to flick through too many lessons in Pyskool in order to test it.
The top few lessons in the stock `lessons.ini` are::

  [Timetable]
  Playtime-4
  Withit-MapRoom-2
  RevisionLibrary-3

You could replace ``Withit-MapRoom-2`` with ``Creak-MapRoom-1``::

  [Timetable]
  Playtime-4
  Creak-MapRoom-1
  RevisionLibrary-3

This means that the second lesson of the day will be the one with ID
``Creak-MapRoom-1``. But that lesson doesn't exist yet, because we just made it
up. So now it's time to create the lesson.

Creating the lesson
^^^^^^^^^^^^^^^^^^^
Now that the ``[Timetable]`` section contains a brand new lesson ID, we have to
make sure there is a corresponding ``[Lesson ...]`` section. For this we're
going to take a short cut. Since a lesson with Mr Creak in the Map Room is
going to be almost the same as a lesson in the Map Room with any other teacher,
we're going to find one such lesson, copy and paste it, and make the necessary
modifications.

A good candidate for this copy/paste/modify plan is the lesson
``Withit-MapRoom-1``, so find the section named
``[Lesson Withit-MapRoom-1 WITHIT, MapRoom]``, copy and paste it somewhere else
amid the ``[Lesson ...]`` sections, and rename it thus::

  [Lesson Creak-MapRoom-1 CREAK, MapRoom]
  BOY01, ReadingRoom-Boy
  BOY02, WhiteRoom-Boy
  BOY03, ReadingRoom-Boy
  BOY04, WhiteRoom-Boy
  BOY05, ReadingRoom-Boy
  BOY06, WhiteRoom-Boy
  BOY07, ExamRoom-Boy
  BOY08, ReadingRoom-Boy
  BOY09, ExamRoom-Boy
  BOY10, ExamRoom-Boy
  BOY11, MapRoom-Boy
  WACKER, ExamRoom-Teacher
  ROCKITT, WhiteRoom-Teacher
  WITHIT, MapRoom-Teacher
  CREAK, ReadingRoom-Teacher
  TEARAWAY, ExamRoom-Tearaway
  BULLY, MapRoom-Bully
  SWOT, MapRoom-Swot

Now we're almost done. All that remains is to assign the appropriate command
list to Mr Creak, and an alternative appropriate command list to Mr Withit. The
simplest thing to do is switch their command lists round, thus::

  WITHIT, ReadingRoom-Teacher
  CREAK, MapRoom-Teacher

And that's it. Now run `skool_daze.py`, and give Mr Creak a round of applause
as he makes it to the Map Room for the first time in his long career.

All aboard the Science Lab
--------------------------
Let's try our hand at a completely new lesson in Back to Skool this time. What
about one where every boy and girl piles into the Science Lab with Mr Rockitt?
That should be interesting.

Adding an entry to the timetable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You're an old hand at this now. Open up `back_to_skool/lessons.ini` and inspect
the ``[Timetable]`` section::

  [Timetable]
  Playtime-5
  Creak-YellowRoom-2
  Assembly

Let's replace that ``Creak-YellowRoom-2`` entry with a carefully chosen unique
ID for our new lesson::

  [Timetable]
  Playtime-5
  Rockitt-ScienceLab-AllAboard
  Assembly

Time to create the lesson itself.

Creating the lesson
^^^^^^^^^^^^^^^^^^^
We'll use the copy/paste/modify trick again, but this time there will be a lot
more modifying to do. The lesson ``Rockitt-ScienceLab-1`` would be a good
template to use, so find the lesson section named
``[Lesson Rockitt-ScienceLab-1 ROCKITT, ScienceLab]``, copy and paste it
somewhere else amid the lesson sections, and rename it thus::

  [Lesson Rockitt-ScienceLab-AllAboard ROCKITT, ScienceLab]

The next step is to assign appropriate command lists to the characters. The
appropriate command list for the little boys and girls is ``ScienceLab-Boy`` -
don't be fooled by the ``-Boy`` suffix. So modify those command lists thus::

  GIRL01, ScienceLab-Boy
  GIRL02, ScienceLab-Boy
  ...
  BOY01, ScienceLab-Boy
  BOY02, ScienceLab-Boy
  ...
  BOY10, ScienceLab-Boy

Now for the teachers. Mr Rockitt will obviously have to be in the Science Lab
and the other teachers might as well just wander around, since they'll have
nothing better to do::

  WITHIT, Walkabout1-Teacher
  ROCKITT, ScienceLab-Teacher
  CREAK, Walkabout2-Teacher
  TAKE, GirlsSkoolWalkabout-Teacher

Mr Wacker and Albert are fine as they are. Next, the main kids. They all need
to pile into the Science Lab::

  TEARAWAY, ScienceLab-Tearaway
  BULLY, ScienceLab-Bully
  SWOT, ScienceLab-Swot
  HEROINE, ScienceLab-Boy

Now we're ready. Run `back_to_skool.py`, and watch the Science Lab fill to
bursting point. Fun.

Where's the chalk?
------------------
So you've modified messages and lessons, but to be brutally honest, you haven't
proved yourself as a Pyskool modder until you've created your own command list.
Recall that a command list is a list of commands (!) that control a character
during a lesson.

In this exercise we'll take the command list that controls the tearaway when
he's on a blackboard-defacing spree in Skool Daze::

  [CommandList WriteOnBoards-Tearaway]
  GoTo, ExamRoomBlackboard:Middle
  WriteOnBoardUnless, Dirty
  GoTo, WhiteRoomBlackboard:Middle
  WriteOnBoardUnless, Dirty
  GoTo, ReadingRoomBlackboard:Middle
  WriteOnBoardUnless, Dirty
  SetControllingCommand, FireNowAndThen
  GoToRandomLocation
  WalkAround, 10
  Restart

and turn it into a command list that leaves the tearaway frustrated by the
global chalk shortage. One simple way to do this is to replace the three
``WriteOnBoardUnless`` commands with these commands::

  Say, "Hey, where's the chalk?"
  Say, "OMG, no chalk here, either!"
  Say, "WTF? Has Mr Creak been eating the chalk or something?"

And for good measure we'll insert another ``Say`` command after
``GoToRandomLocation``::

  Say, "Anybody got any chalk?"

When these modifications are complete, the command list should look like this::

  [CommandList WriteOnBoards-Tearaway]
  GoTo, ExamRoomBlackboard:Middle
  Say, "Hey, where's the chalk?"
  GoTo, WhiteRoomBlackboard:Middle
  Say, "OMG, no chalk here, either!"
  GoTo, ReadingRoomBlackboard:Middle
  Say, "WTF? Has Mr Creak been eating the chalk or something?"
  SetControllingCommand, FireNowAndThen
  GoToRandomLocation
  Say, "Anybody got any chalk?"
  WalkAround, 10
  Restart

Now run `skool_daze.py` and watch as the hapless tearaway's blackboard-daubing
career is dashed to the ground.

.. _ready-made:

Ready-made customisations
-------------------------
Some ready-made customised ini files are distributed with Pyskool to
demonstrate what's possible with the Pyskool engine. These customisations are
described in the following sections.

Skool Daze Take Too
^^^^^^^^^^^^^^^^^^^
To play 'Skool Daze Take Too', double-click `skool_daze_take_too.py` or run it
from the command line thus:

``$ ./skool_daze_take_too.py``

and say hello to Skool Daze's new philosophy teacher, who may look somewhat
familiar.

Ezad Looks
^^^^^^^^^^
To play 'Ezad Looks', double-click `ezad_looks.py` or run it from the command
line thus:

``$ ./ezad_looks.py``

and prepare to feel a little disoriented for a while.

Back to Skool Daze
^^^^^^^^^^^^^^^^^^
To play 'Back to Skool Daze', double-click `back_to_skool_daze.py` or run it
from the command line thus:

``$ ./back_to_skool_daze.py``

and hit some shields for old times' sake.
