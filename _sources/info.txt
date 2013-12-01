General info
============

.. _contact:

Contact details
---------------
To make complaints about or suggest improvements to Pyskool, or to submit some
other piece of constructive criticism, contact me (Richard Dymond) at
*<rjdymond AT gmail.com>*, or leave a comment on the `Pyskool blog
<http://pyskool.ca/>`_.

To report bugs, please use the `bug tracker`_.

.. _bug tracker: https://github.com/skoolkid/pyskool/issues

.. _todo:

TODO
----
Pyskool is now functionally complete, by which I mean that it does everything
that the original Skool games do. (Except for a demo mode; if you think there's
something else it should do but doesn't, let me know.) However, there are a few
things left on my TODO list, the main ones being:

* Tidy up the code
* Optimise the sprite-drawing and screen update code
* Add a demo mode
* Write a :ref:`Command <command-ref>`-writing HOWTO (demonstrating how to add
  commands to Pyskool)

.. _bugs:

Bugs
----
No doubt there are bugs in Pyskool - and in this documentation - or ways it
deviates unacceptably from the original games. Please `report any bugs`_
(reproducible crashes, especially) you find, and help to make Pyskool a solid
and stable platform for developing new Skool-based games. If you can provide a
saved game that demonstrates the bug shortly after being loaded, all the
better.

.. _report any bugs: `bug tracker`_

Frequently asked questions
--------------------------
At the time of writing this, there are no frequently asked questions, or even
any infrequently asked questions. So for now I'll fill this section with
questions made up by me.

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
Plus it enables rapid development, which is good because I'm writing Pyskool in
my limited spare time. Pygame's pretty good too. I don't know how else I'd do
graphics with Python.

**Why Skool Daze and Back to Skool?**

If you need to ask, you probably shouldn't be here. Actually, what *are* you
doing here? Go and play Jet Set Willy, or something.
