General info
============

.. _contact:

Contact details
---------------
To make complaints about or suggest improvements to Pyskool, or to submit some
other piece of constructive criticism, contact me (Richard Dymond) at
*<rjdymond AT gmail.com>*.

.. _bugs:

Bugs
----
No doubt there are bugs in Pyskool - and in this documentation - or ways it
deviates unacceptably from the original games. Please `report any bugs`_
(reproducible crashes, especially) you find, and help to make Pyskool a solid
and stable platform for developing new Skool-based games. If you can provide a
saved game that demonstrates the bug shortly after being loaded, all the
better.

.. _report any bugs: https://github.com/skoolkid/pyskool/issues

Frequently asked questions
--------------------------

**How does Pyskool differ from the original games?**

Though the conversion of the original games to Python/Pygame is pretty faithful
(I think), there are some differences, noted below.

General differences:

* More than one character can be talking at any given time
* Characters can talk while off-screen (so it's possible for the scrolling
  screen to reveal a character mid-sentence)
* Eric cannot walk slowly

In Skool Daze mode:

* Boys can find the back seat in the Reading Room
* Eric will not be expelled until he has *more than* 10000 lines (in the
  original game, he could be expelled when he had *exactly* 10000 lines)
* Eric will get lines if a teacher spots him writing on a blackboard
* The `broken jumping sound effect`_ has been fixed

.. _broken jumping sound effect: http://skoolkit.ca/disassemblies/skool_daze/reference/bugs.html#jumpSound

In Back to Skool mode:

* Eric can release mice anywhere (not just in the girls' skool)
* Eric can re-catch mice that he has released; well, why not?
* The frog is visible from the start of the game; I think the only reason it
  was hidden in the original game was a lack of RAM (the frog shares its
  character buffer with the mouse, and the mouse needs to be visible from the
  start)
* The 'conker' sound effect is played when Albert (instead of when Einstein or
  Angelface) is struck by a conker

**Why Python (and Pygame)?**

Because Python is an elegant, expressive, and excellent programming language.
Plus it enables rapid development, which is good because I develop Pyskool in
my limited spare time. Pygame's pretty good too. When I started Pyskool back in
2008, I don't know how else I'd have done graphics with Python.

**Why Skool Daze and Back to Skool?**

If you need to ask, you probably shouldn't be here. Actually, what *are* you
doing here? Go and play Jet Set Willy, or something.
