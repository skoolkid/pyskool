Changelog
=========

1.2.1 (2016-05-21)
------------------
* Added missing verbs to the :ref:`assemblyMessages` section for Back to Skool
* When Eric is writing on a blackboard, the text now automatically wraps to the
  second line when the end of the first line is reached
* Updated the worldofspectrum.org URLs in `images.ini`
* Fixed links to classes, methods and variables in the API documentation

1.2 (2015-01-14)
----------------
* Dropped support for Python 2.6 and Pygame 1.7
* Added support for Python 3.4
* The Insert (screenshot), F2 (save), F6 (load), F11 (toggle full-screen mode)
  and F12 (menu) keys now work when Eric is writing on a blackboard
* Fixed the quit menu so that it works when Eric is writing on a blackboard

1.1.2 (2014-06-14)
------------------
* Customised the theme tunes, 'all shields' tunes, 'open safe' tunes and 'up a
  year' tunes in Skool Daze Take Too, Ezad Looks and Back to Skool Daze
* Customised the lesson questions and answers in Skool Daze Take Too, Ezad
  Looks and Back to Skool Daze
* Customised the 'sit down' messages and 'lesson' messages in Back to Skool
  Daze
* Added the ``--config`` command line option (to set the value of a
  configuration parameter)

1.1.1 (2014-01-26)
------------------
* Added the ``ConfirmClose`` and ``ConfirmQuit`` parameters to the
  :ref:`gameConfig` section (to control whether a confirmation screen is shown
  when Escape or the window close button is pressed)
* Added the ``Volume`` parameter to the :ref:`gameConfig` section (to set the
  volume for sound effects)
* Added support for appending content to existing ini file sections by adding a
  '+' suffix to the section name (e.g. `[SkoolLocations+]`)
* Added a menu item to switch between full-screen and windowed mode
* Added the ``--force`` command line option (to overwrite existing images, ini
  files and sound files)
* Added the ``--sample-rate`` command line option (to set the sample rate of
  the sound files created by ``--create-sounds``)
* Fixed the bug that freezes the game if Eric's lines total goes over 10000
  while he's being fetched by the teacher on dinner duty

1.1 (2013-12-01)
----------------
* Replaced all the sound files with high-quality (44.1kHz) versions
* Added hitting sound effects (``HIT0``, ``HIT1``) to Skool Daze
* Added the ``ALARM`` sound effect ID (for when Albert is telling Mr Wacker
  that Eric's escaping)
* Screenshots are now saved to the `screenshots` directory by default
* Added the ``--create-sounds`` command line option (to create the sound files
  required by a game)
* Added the ``--package-dir`` command line option (for showing the path to the
  pyskool package directory)
* Added the ``--search-dirs`` command line option (for showing the locations
  that Pyskool searches for data files)
* Added the ``--setup`` command line option (to create the images, ini files
  and sound files required by a game)
* Added a second source for the Skool Daze TZX file to `images.ini`
* Removed the documentation sources from the Pyskool distribution (they can be
  obtained from GitHub_)

.. _GitHub: https://github.com/skoolkid/pyskool

1.0.1 (2012-12-07)
------------------
* Moved the man pages to section 6

1.0 (2012-12-03)
----------------
* Added the ``--get-images`` command line option (to download TZX files of
  Skool Daze and Back to Skool from sources listed in `images.ini` and extract
  images from them)
* Added the ``--create-ini`` command line option (to create the stock game ini
  files)
* Added the ability to switch between full-screen and windowed mode by pressing
  F11
* Man pages for the game launcher scripts are included in the `man` directory
* Fixed the audio latency that can occur when using Pygame 1.8+
* Fixed the bug that enables Eric to ride the bike past Albert when he has his
  arm raised
* Fixed the bug that makes Eric remain aloft after the knocked out kid he's
  standing on (near a staircase) has risen
* Fixed the bug in Back to Skool Daze that makes the shield on the shelf in the
  boys' skool turn into a cup when Eric goes onto the next year
* Fixed the `ezad_looks/mutables.png` image (each pair of shield/safe images
  was in the wrong order)

0.6 (2011-06-05)
----------------
* Pyskool can be installed as a Python package using ``setup.py install``
* Changed the menu show/hide key from F10 (which activates the menu bar in
  Windows) to F12
* Added default key bindings to `pyskool.ini`
* Fixed the bug that enables Eric to kiss Hayley while she's sitting down
* Fixed the bug that makes Mr Wacker give Eric lines for being on the floor or
  not in skool while expelling him for jumping out of the top-floor window
* Fixed the bug that causes sprite graphics to lose their transparency when a
  game saved at one colour depth is loaded at a higher colour depth

0.5.4 (2011-03-15)
------------------
Fixed the bug that causes a crash when Eric tries to get on the bike.

0.5.3 (2010-12-16)
------------------
Fixed the bug that prevented a saved game from loading when using
``GraphicsMode`` 0 (hi-res colour).

0.5.2 (2010-11-03)
------------------
* Added a jumping sound effect to Skool Daze
* Fixed a graphic glitch in the girls' shoes

0.5.1 (2010-06-21)
------------------
Fixed the bug that causes a crash during a non-question-and-answer lesson when
the teacher has returned to the blackboard after fetching the truant Eric.

0.5 (2010-06-08)
----------------
* Added an in-game menu
* Screen can be rescaled while Pyskool is running
* Key bindings are defined in `pyskool.ini`

0.4 (2010-05-28)
----------------
* Added the ability to save and load games
* The score box is drawn using labels defined in the :ref:`messageConfig`
  section
* Added lesson box background images
* Added message box images (now the message boxes in Skool Daze mode look like
  those used in the original game)

0.3 (2010-05-18)
----------------
* Moved data that was embedded in the Python code into the ini files: there are
  now over 100 more parameters to tweak in the :ref:`gameConfig`,
  :ref:`screenConfig`, :ref:`lessonConfig`, :ref:`timetableConfig`,
  :ref:`timingConfig` and :ref:`animationPhases` sections, and extra
  character-controlling arguments to play with in the :ref:`walkAround`,
  :ref:`moveAboutUntil`, :ref:`moveMouse`, :ref:`moveFrog`, and
  :ref:`watchForEric` commands (for example)
* Added utility scripts `createini.py` (generates ini files) and
  `extract-png.py` (extracts graphics from memory snapshots of the original
  skool games)
* Added documentation sources in `docs-src`

0.2.4 (2010-04-30)
------------------
Added the following features:

* 'Back to Skool Daze' example customisation
* Keyboard is checked during long sound effects (so you can pause or quit while
  the tune is playing, for example)
* Screenshots can be taken while the game is paused
* [Screen] section in the ini files
* API documentation

0.2.3 (2010-04-13)
------------------
Added the 'Ezad Looks' example customisation.

0.2.2 (2010-04-02)
------------------
Added the following features in Back to Skool mode:

* Eric is paralysed and expelled after jumping out of the top-floor window
* Albert alerts Mr Wacker if he spots Eric trying to escape
* Mr Wacker shadows Eric after being alerted by Albert
* Mr Creak and Mr Rockitt behave correctly during assembly
* Mr Withit does assembly duty
* Eric gets lines for not sitting down facing the stage during assembly
* Eric gets lines for standing on plants
* Miss Take chases Eric out of the girls' skool if she spots him there when
  it's not playtime

Also fixed the following bugs:

* Game crashes if Eric tries to sit back on the saddle of the bike after
  standing on it
* Eric gets lines for riding the bike in the playground
* Eric gets lines if spotted falling from a window
* Screen scrolls right every time Eric kisses Hayley

0.2.1 (2010-03-26)
------------------
Added the following features in Back to Skool mode:

* Eric can release mice
* The girls and Miss Take will jump up and down or stand on a chair if they
  spot a mouse nearby
* Eric can kiss (or try to kiss) Hayley
* Eric can open desks and collect the water pistol or stinkbombs
* Eric can drop stinkbombs
* Mr Wacker will open a nearby window if he smells a stinkbomb
* Eric can fire the water pistol
* Eric can fill the water pistol with sherry
* Eric can throw away the water pistol
* Cups can be filled with water or sherry
* Plants grow when watered
* Eric can stand on plant pots
* Eric is lifted by a growing plant
* Eric can step off a fully grown plant through an open window
* Eric can step off a fully grown plant over the skool gate
* Drops of water or sherry can be knocked out of a cup with a catapult pellet
* Teachers reveal bike combination digits when hit by a drop of water
* Eric can unchain the bike by writing the combination on a blackboard
* Eric can ride the bike
* Eric can stand on the saddle of the bike
* Eric can jump off the saddle of the bike
* Eric is launched over the closed skool gate if he hits it while standing on
  the saddle of the bike
* Teachers reveal storeroom combination letters when hit by a drop of sherry
* Eric can get the storeroom key (and hence the frog) by writing the
  combination on a blackboard
* Conker falls from the tree when hit by a catapult pellet
* Falling conker can knock people out
* Eric can place the frog in a cup
* Eric can get the safe key by knocking the frog from a cup onto Miss Take's
  head
* Eric can open the safe by jumping up to it when he has the key

Also fixed the following bugs:

* Game crashes if a character is chasing or looking for Eric while Eric is on a
  staircase or jumping
* Eric does not get lines if caught writing on a blackboard
* Eric gets lines for being in the assembly hall during non-assembly periods

0.2 (2010-03-16)
----------------
* Added mice and frogs and the ability to catch them
* Fixed glitches in the animatory state graphics (`sprites.png`)
* Added the `SHERRY` sound sample
* Added the `GameFps` and `ScrollFps` configuration parameters

Also fixed the following bugs:

* Game crashes if you press 'Delete' while writing on a blackboard
* If a little boy talks to ERIC while he's writing on a blackboard, pressing
  'U' has no effect
* During dinner, the teacher on duty keeps giving Eric lines for not finding a
  seat

0.1.2 (2009-07-22)
------------------
Fixed bug in Skool Daze mode where shields stay flashing after Eric's been
expelled.

0.1.1 (2009-04-29)
------------------
Fixed bug where Eric gets trapped in his seat if he's knocked out of it by a
catapult pellet and then tries to stand up.

0.1 (2008-11-12)
----------------
* Eric is expelled after exceeding the lines limit
* The swot tells tales
* Teachers track down Eric if he tries to skip class

In Skool Daze mode:

* Special playtimes have been implemented
* Teachers give lines for all possible infractions
* All commands required in Skool Daze mode have been implemented

0.0.4 (2008-10-24)
------------------
* Eric can write on blackboards
* Improved keyboard responsiveness
* Added ready-made example customisation: Skool Daze Take Too

In Skool Daze mode:

* Teachers reveal safe combination letters when all shields are flashing
* Eric can open the safe after writing the combination code on a blackboard
* Eric can unflash all the shields after opening the safe

0.0.3 (2008-10-08)
------------------
* Sound effects and tunes
* Teachers give lines for some infractions
* Eric can jump (into the air and onto other kids, too)
* Eric can make shields flash

0.0.2 (2008-09-23)
------------------
* Added ``--scale`` and ``--ini`` command line options
* Bully can knock people out
* Tearaway can fire catapult pellets
* Eric can do these things too
* Tearaway writes on the blackboards
* Implemented several previously unimplemented commands

0.0.1 (2008-09-09)
------------------
Initial public release.
