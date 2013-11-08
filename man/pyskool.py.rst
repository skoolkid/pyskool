======================
%{script}
======================

---------------------------------------
run Pyskool in %{game} mode
---------------------------------------

:Author: Richard Dymond
:Copyright: 2013, Richard Dymond
:Version: 1.0.2
:Date: 2013-11-08
:Manual section: 6

SYNOPSIS
========
``%{script}`` [options]

DESCRIPTION
===========
``%{script}`` runs Pyskool in %{game} mode. Pyskool is a remake of the classic
ZX Spectrum games Skool Daze and Back to Skool by Microsphere.

OPTIONS
=======
--version
  Show Pyskool's version number and exit.

-h, --help
  Show a summary of the available options.

-c, --cheat
  Enable cheat keys.

--create-ini
  Create the ini files required by the game in ``~/.pyskool/ini/%{gamedir}``
  and exit.

--get-images
  Get any missing images required by the game and exit.

-i, --inidir `INIDIR`
  Read ini files from this directory instead of ``ini/%{gamedir}``.

-l, --load `SAVEFILE`
  Load a saved game from the specified file.

--package-dir
  Show the path to the pyskool package directory and exit.

-q, --quick-start
  Start the game quickly by skipping the scroll-skool-into-view and theme tune
  sequence.

-r, --load-last `SAVEDIR`
  Load the most recently saved game in the specified directory.

-s, --scale `SCALE`
  Scale graphics by this factor (1=original Speccy size).

--search-dirs
  Show the locations that Pyskool searches for data files and exit.

FILES
=====
When Pyskool starts in %{game} mode, it looks for the following things:

|
| - a file named ``pyskool.ini`` (the main ini file)
| - a directory named ``images``
| - a directory named ``sounds``
| - a directory named ``ini/%{gamedir}``

Each of these things must be present in one of the following directories in
order for Pyskool to find it:

|
| - the current working directory
| - ``~/.pyskool``
| - the directory containing ``%{script}``
| - ``/usr/share/pyskool``
| - ``$PACKAGE_DIR/data``

where ``$PACKAGE_DIR`` is the directory in which the pyskool package is
installed, as shown by:

|
|  ``%{script} --package-dir``

When you need a reminder of these locations, run:

|
|  ``%{script} --search-dirs``

IMAGES
======
The ``--get-images`` option first looks for Skool Daze and Back to Skool tape
or snapshot files by the following names in ``~/.pyskool``:

|
| ``skool_daze.tzx``
| ``skool_daze.sna``
| ``skool_daze.z80``
| ``skool_daze.szx``
| ``back_to_skool.tzx``
| ``back_to_skool.sna``
| ``back_to_skool.z80``
| ``back_to_skool.szx``

If no such files are found, TZX files are downloaded from one of the sources
listed in ``images.ini`` and saved to ``~/.pyskool``. Then the required images
are built from the tape or snapshot files and saved to the appropriate
subdirectories under ``~/.pyskool/images/originalx1``.

EXAMPLE
=======
Get all the images required by %{game}, and then run Pyskool in %{game}
mode:

|
|   ``%{script} --get-images``
|   ``%{script}``

SEE ALSO
========
%{seealso}
