Installing and running Pyskool
==============================

Requirements
------------
Pyskool requires `Python <https://www.python.org/downloads/>`_ (version 2.7)
and `Pygame <http://www.pygame.org/download.shtml>`_ (version 1.8+).

On Linux/\*BSD, Python and Pygame are available via the package management
system. Python is in the `python` package on all systems; Pygame is in the
`python-pygame` package on Debian-based distros and openSUSE, the `pygame`
package on Fedora, the `devel/py-game` port on FreeBSD and NetBSD, and the
`devel/pygame` port on OpenBSD.

Windows and Mac OS X users should take care to select the Pygame installer that
matches the version of Python that is installed.

Installing Pyskool
------------------
There are various ways to install the latest stable release of Pyskool:

* from the zip archive or tarball available at
  `pyskool.ca <http://pyskool.ca/?page_id=44>`_
* from the DEB package or RPM package available at `pyskool.ca`_
* from `PyPI <https://pypi.python.org/pypi/pyskool>`_ by using
  `easy_install <https://pythonhosted.org/setuptools/easy_install.html>`_ or
  `pip <http://www.pip-installer.org/>`_

If you choose the zip archive or tarball, note that Pyskool can be used
wherever it is unpacked: it does not need to be installed in any particular
location.

However, if you would like to install Pyskool as a Python package, you can do
so by using the supplied ``setup.py`` script. After installation, the required
images, ini files and sound files for each game will need to be created. This
can be done by using the ``--setup`` option; for example::

  $ skool_daze.py --setup

Windows
^^^^^^^
To install Pyskool as a Python package on Windows, open a command prompt,
change to the directory where Pyskool was unpacked, and run the following
command::

  > setup.py install

This should install the Pyskool game launcher scripts in
`C:\\Python2X\\Scripts` (assuming you have installed Python in `C:\\Python2X`),
which means you can run them from anywhere (assuming you have added
`C:\\Python2X\\Scripts` to the ``Path`` environment variable).

Linux/\*BSD/Mac OS X
^^^^^^^^^^^^^^^^^^^^
To install Pyskool as a Python package on Linux/\*BSD/Mac OS X, open a terminal
window, change to the directory where Pyskool was unpacked, and run the
following command as root::

  # ./setup.py install

This should install the Pyskool game launcher scripts in `/usr/local/bin` (or
some other suitable location in your ``PATH``), which means you can run them
from anywhere.

Running Pyskool
---------------

Windows
^^^^^^^
To run Pyskool in Skool Daze mode, double-click the `skool_daze.py` file in
the Pyskool directory. To run Pyskool in Back to Skool mode, double-click
`back_to_skool.py`.

If that doesn't work, try the command line. Open a command prompt, change to
the Pyskool directory, and do::

  > skool_daze.py

to run Pyskool in Skool Daze mode; or, to run Pyskool in Back to Skool mode::

  > back_to_skool.py

Linux/\*BSD/Mac OS X
^^^^^^^^^^^^^^^^^^^^
To run Pyskool in Skool Daze mode, open a terminal window, change to the
Pyskool directory, and do::

 $ ./skool_daze.py

or, to run Pyskool in Back to Skool mode::

 $ ./back_to_skool.py

Pyskool data files
------------------
When `skool_daze.py`, `back_to_skool.py` or one of the other game launcher
scripts is executed, it looks for the following things:

* a file named `pyskool.ini` (the main ini file)
* a directory named `images`
* a directory named `sounds`
* a directory named `ini/<game_name>` (where `<game_name>` is `skool_daze`,
  `back_to_skool`, or whatever)

Each of these things must be present in one of the following directories in
order for Pyskool to find it:

* the current working directory
* `$HOME/.pyskool`
* the directory containing the game launcher script
* `/usr/share/pyskool`
* `$PACKAGE_DIR/data`

`$HOME` refers to the user's home directory. On Windows this is typically
`C:\\Users\\username` or `C:\\Documents and Settings\\username`.

`$PACKAGE_DIR` refers to the directory in which the `pyskool` package is
installed (as shown by the ``--package-dir`` command line option).

When you need a reminder of the locations that Pyskool searches for data files,
run one of the game launcher scripts with the ``--search-dirs`` option.

If Pyskool doesn't start, run the game launcher script from the command line
and read the diagnostic messages that are printed to the console for clues
about what's going wrong.

When Pyskool is running, it will dump screenshots to, save games to, and load
games from either `$HOME/.pyskool` (if it exists or can be created), or the
current working directory.

Command line options
--------------------
`skool_daze.py`, `back_to_skool.py` and the other game launcher scripts support
the following command line options:

* ``--version`` - show the version number of Pyskool and exit
* ``-h`` or ``--help`` - show a summary of the available options
* ``-c`` or ``--cheat`` - enable cheat keys; equivalent to
  ``--config=Cheat,1``, this option overrides the `Cheat` parameter in the
  :ref:`gameConfig` section
* ``--config=P,V`` - set the value of the configuration parameter ``P`` to
  ``V``; this option may be used multiple times
* ``--create-images`` - create the images required by the game and exit
* ``--create-ini`` - create the ini files required by the game in
  `$HOME/.pyskool/ini/<game_name>` and exit
* ``--create-sounds`` - create the sound files required by the game in
  `$HOME/.pyskool/sounds` and exit
* ``--force`` - overwrite existing images, ini files and sound files (when
  using the ``--create-images``, ``--create-ini``, ``--create-sounds`` or
  ``--setup`` option)
* ``-i INIDIR`` or ``--inidir=INIDIR`` - use ini files from a specified
  directory
* ``-l SAVEFILE`` or ``--load=SAVEFILE`` - load a previously saved game
* ``--package-dir`` - show the path to the pyskool package directory and exit
* ``-q`` or ``--quick-start`` - start the game quickly by skipping the
  scroll-skool-into-view and theme tune sequence; equivalent to
  ``--config=QuickStart,1``, this option overrides the `QuickStart` parameter
  in the :ref:`gameConfig` section
* ``-r SAVEDIR`` or ``--load-last=SAVEDIR`` - load the most recently saved game
  from the specified directory
* ``--sample-rate=RATE`` - set the sample rate of the sound files created by
  ``--create-sounds`` (default: 44100)
* ``-s SCALE`` or ``--scale=SCALE`` - set the scale of the display; equivalent
  to ``--config=Scale,SCALE``, this option overrides the `Scale` parameter in
  the :ref:`screenConfig` section
* ``--search-dirs`` - show the locations that Pyskool searches for data files
  and exit
* ``--setup`` - create the images, ini files and sound files required by the
  game in `$HOME/.pyskool` and exit

The ``--create-images`` option first looks for Skool Daze and Back to Skool
tape or snapshot files by the following names in `$HOME/.pyskool`:

* `skool_daze.tzx`
* `skool_daze.sna`
* `skool_daze.z80`
* `skool_daze.szx`
* `back_to_skool.tzx`
* `back_to_skool.sna`
* `back_to_skool.z80`
* `back_to_skool.szx`

If no such files are found, TZX files are downloaded from one of the sources
listed in `images.ini` and saved to `$HOME/.pyskool`. Then the required images
are built from the tape or snapshot files and saved to the appropriate
subdirectories under `$HOME/.pyskool/images/originalx1`.
