.. _main-ini-file:

Main ini file
=============
The main ini file - `pyskool.ini` - defines key bindings and the appearance and
content of the game menus. Each section is described below.

.. _keys:

[Keys]
------
The ``Keys`` section defines the key bindings. Each line in the section has the
form::

  actionId, key1, key2, ...

where ``actionId`` is the identifier of the action to bind to the keys
``key1``, ``key2`` and so on. Any number of keys may be bound to an action.

Pyskool recognises the following action identifiers for moving Eric:

* ``LEFT`` - move left
* ``RIGHT`` - move right
* ``UP`` - move up
* ``DOWN`` - move down
* ``SIT_STAND`` - sit down or stand up
* ``OPEN_DESK`` - open a desk
* ``FIRE_CATAPULT`` - fire the catapult
* ``FIRE_WATER_PISTOL`` - fire the water pistol
* ``DROP_STINKBOMB`` - drop a stinkbomb
* ``HIT`` - throw a punch
* ``JUMP`` - jump
* ``WRITE`` - start writing on a blackboard
* ``ENTER`` - finish writing on a blackboard
* ``CATCH`` - try to catch a mouse or frog
* ``UNDERSTOOD`` - acknowledge understanding of a message
* ``MOUNT_BIKE`` - mount the bike
* ``DUMP_WATER_PISTOL`` - throw away the water pistol
* ``RELEASE_MICE`` - release some mice
* ``KISS`` - try to kiss someone

In addition, Pyskool recognises the following identifiers for actions not
related to moving Eric:

* ``QUIT`` - quit Pyskool
* ``FULL_SCREEN`` - toggle full-screen mode
* ``PAUSE`` - pause the game
* ``SCREENSHOT`` - take a screenshot
* ``SAVE`` - save the game
* ``LOAD`` - load the most recently saved game
* ``MENU`` - show the menu
* ``MENU_EXIT`` - hide the menu and resume the game
* ``MENU_PREV`` - move to the previous item in the menu
* ``MENU_NEXT`` - move to the next item in the menu
* ``MENU_EXEC`` - execute the selected menu item

Pygame uses keyboard constants to identify keys; a full list of those constants
can be found in the
`pygame documentation <http://pygame.org/docs/ref/key.html>`_. The key names
(``key1``, ``key2`` etc.) declared in a line of the ``Keys`` section should
match the names of the Pygame keyboard constants, but with the ``K_`` prefix
removed.

+---------+---------------------------------------------+
| Version | Changes                                     |
+=========+=============================================+
| 1.0     | Added the ``FULL_SCREEN`` action identifier |
+---------+---------------------------------------------+
| 0.5     | New                                         |
+---------+---------------------------------------------+

.. _menu:

[Menu ...]
----------
Each ``Menu ...`` section defines a menu and its appearance. The section name
has the form::

  Menu menuId

where ``menuId`` is a unique identifier for the menu. The section may contain
the following configuration parameters:

* ``Alpha`` - the transparency of the menu (0=fully transparent, 255=fully
  opaque)
* ``Highlight`` - the background colour of the selected menu item
* ``Ink`` - the ink colour to use for the title, menu items and status bar
* ``Paper`` - the main background colour
* ``StatusBar`` - whether to show a status bar (0=no, 1=yes)
* ``StatusPaper`` - the background colour of the status bar
* ``Title`` - the menu title
* ``TitlePaper`` - the background colour of the title bar
* ``Width`` - the width of the menu (as a fraction of the screen width)

`pyskool.ini` contains the definitions for two menus, whose unique IDs must be
``Main`` and ``Quit``.

+---------+-----------------------------------+
| Version | Changes                           |
+=========+===================================+
| 1.1.1   | Added the ``StatusBar`` parameter |
+---------+-----------------------------------+
| 0.5     | New                               |
+---------+-----------------------------------+

.. _menuItems:

[MenuItems ...]
---------------
Each ``MenuItems ...`` section defines the menu items for a menu. The section
name has the form::

  MenuItems menuId

where ``menuId`` is the unique identifier of the menu (defined by a :ref:`menu`
section).

Each line in the section has the form::

  operation, text

where:

* ``operation`` is the unique ID of the operation to which the menu item is
  bound
* ``text`` is the text of the menu item

The operation IDs recognised by Pyskool are:

* ``LOAD`` - load the most recently saved game
* ``QUIT`` - quit Pyskool
* ``RESUME`` - hide the menu and resume the game
* ``SAVE`` - save the game
* ``SCALE_DOWN`` - decrease the scale factor by 1
* ``SCALE_UP`` - increase the scale factor by 1
* ``TOGGLE_FULLSCREEN`` - toggle fullscreen mode

+---------+-------------------------------------------+
| Version | Changes                                   |
+=========+===========================================+
| 1.1.1   | Added the ``TOGGLE_FULLSCREEN`` operation |
+---------+-------------------------------------------+
| 0.5     | New                                       |
+---------+-------------------------------------------+
