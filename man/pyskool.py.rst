======================
%{script}
======================

---------------------------------------
run Pyskool in %{game} mode
---------------------------------------

:Author: rjdymond@gmail.com
:Date: 2012-12-07
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
--version  show Pyskool's version number and exit
-h, --help  show this help message and exit
-s SCALE, --scale=SCALE  scale graphics by this factor (1=original Speccy size)
-i INIDIR, --inidir=INIDIR  read ini files from this directory instead of ini/%{gamedir}
-q, --quick-start  start the game quickly
-c, --cheat  enable cheat keys
-l SAVEFILE, --load=SAVEFILE  load a saved game from the specified file
-r SAVEDIR, --load-last=SAVEDIR  load the most recently saved game in the specified directory
--create-ini  create the ini files required by the game and exit
--get-images  get any missing images required by the game and exit

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
