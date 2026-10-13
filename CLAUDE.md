# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Pyskool is a Pygame re-implementation of the ZX Spectrum games Skool Daze and Back to Skool. It is really five games sharing one engine: Skool Daze, Back to Skool, Skool Daze Take Too, Ezad Looks and Back to Skool Daze. It needs Python 3.10+, and its only runtime dependency is Pygame.

## Commands

From a checkout, set things up once (this downloads the original game TZX files from the URLs in `pyskool/data/images.ini`):

    make scripts images ini sounds

- `make scripts` creates the five launcher symlinks (`skool_daze.py` etc. → `pyskool.py`). They are gitignored.
- `make images` / `make ini` / `make sounds` write generated assets into `~/.pyskool` using `utils/create-*.py`. These scripts need `PYSKOOL_HOME` set to the repo root (the Makefile sets it).

Run a game with `./skool_daze.py`, `./back_to_skool.py` and so on. Useful flags: `-q` (quick start), `-c` (cheat keys), `-s N` (scale), `-i DIR` (alternative ini dir), `--config P,V`, `--search-dirs`.

`make test` runs the pytest suite in `tests/` in parallel (it needs `pytest-xdist`), and `make test-cover` runs it under coverage. To run the tests without make, use `PYSKOOL_HOME=$(pwd) pytest tests`. The tests drive `utils/demo.py` headless (see below), so they need the generated assets in `~/.pyskool`:
- `test_replays.py` plays the five replays.
- `test_lines.py` checks lines-giving scenarios.
- `test_special_playtimes.py` checks special playtimes.

`tests/pyskooltest.py` holds the shared helpers. `.github/workflows/tests.yml` runs the suite on every push to master.

Other targets: `make doc` builds the Sphinx docs (`sphinx/source` → `sphinx/build/html`). `make release`, `make deb` and `make rpm` package the project via `utils/mkpstarball` and `utils/mkpspkg`. `utils/psrelease` holds the release checks, such as comparing generated images, sounds and ini files against a previous release. It needs `PYSKOOL_HOME`.

## Architecture

**Launch.** Every launcher calls `pyskool.run.main()`. It picks the game from the **script's filename** (`sys.argv[0]`). That filename sets the game name, the ini subdirectory (`ini/<script name without .py>`) and the image, ini and sound variant. `main()` finds `pyskool.ini` and the `images`, `sounds` and `ini/<game>` dirs by searching, in order: cwd, `~/.pyskool`, the scripts dir, `/usr/share/pyskool`, then `pyskool/data`. Before it builds `game.Game`, it chdirs to `~/.pyskool`, so saves and screenshots go there.

**Generated data.** The game ini files (`config.ini`, `skool.ini`, `command_lists.ini`, `lessons.ini`, `messages.ini`, `sprites.ini`, `font.ini`) are not checked in. Python code generates them:
- `skoolini.SkoolIniMaker` is the base class. Its `build_ini()` calls `create_*` methods, one per ini section.
- `sdini.SDIniMaker(custom)` and `btsini.BTSIniMaker(custom)` subclass it. `custom` picks the variant: `SKOOL_DAZE`/`SKOOL_DAZE_TAKE_TOO`/`EZAD_LOOKS` = 0/1/2, and `BACK_TO_SKOOL`/`BACK_TO_SKOOL_DAZE` = 0/1.
- `sdtaps.py` and `btstaps.py` generate the "tap" (AI command list) definitions. `skooltaps.py` holds their base class and the command-name constants.

To change default game data, edit these makers, not the output ini files. Images are built by `image.get_images()`. It reads a TZX/snapshot (`snapshot.py`) and extracts graphics from Spectrum memory (`skoolimage.SDMemory`/`BTSMemory`), then writes PNGs with `pngwriter.py`. Sounds are synthesised by `skoolsound.py`.

**Runtime.** `skoolbuilder.SkoolBuilder` (an `IniParser`) reads the ini sections into a `skool.Skool`. The Skool holds the cast (`cast.py`, with `character.py` and `eric.py`), rooms, floors, staircases, timetable, lessons and the mutable skool graphics. `game.Game` runs the main loop, menus, save/load (pickle) and cheat keys.

**AI.** Character behaviour comes from command lists defined in `command_lists.ini`. Each command name in the ini is resolved by name to a class in `ai.py`, using `ai.get_command_class()` (a `getattr` on the module). Renaming or adding a command class therefore changes the ini format. Animatory state names are in `animatorystates.py`, and the shared ini IDs are in `skoolids.py`.

## Demo runner

`utils/demo.py` runs a game deterministically: headless and unthrottled by default, or in a window at normal speed with `--screen` (add `--sounds` for sound, and `--speed N` to run at N times normal speed). It needs `PYSKOOL_HOME` set to the repo root. It reports crashes, hangs, and characters found off every floor and staircase.

Eric can be controlled in three ways:
- automatically, with `-e follow|random|idle`;
- by replaying an inputs file, with `-i FILE`;
- from the keyboard while recording, with `-r FILE` (needs `--screen`).

Other options: `-g` picks the game (default `sd`), `-s` the random seed (default 0), `-t` the number of ticks to stop after, and `-l` restricts the timetable to one lesson. `--images-dir`, `--sounds-dir` and `--ini-dir` override the default asset dirs in `~/.pyskool`.

`--trace TICK` prints Eric's location, animatory state, controlling command, score and lines after every tick from TICK on. `--watch NAME,...` adds the locations of other characters or objects (by name or ID, e.g. `MOUSE`) to each line.

`--lines` prints a `LINES` line whenever Eric's lines total changes. It shows the tick, the change, the new total, who caused it and where, the reason, and Eric's location. The reason is a lines message ID such as `NEVER_AGAIN`, or `AddLines` for a lump sum given by a command list (e.g. the 2000 lines when Einstein grasses in Skool Daze Take Too), or `KISS`. It also prints a `LINES` line, without the new total, whenever lines are given to another character whose lines don't count towards Eric's total, e.g. `LINES 306: +500 by MR WITHIT (36,17) [NEVER_AGAIN] to EINSTEIN Eric (30,17)`. Einstein's and Angelface's lines are added to Eric's score; Boy Wander's go nowhere.

`--ffwd TICKS` (with `--screen`) runs the first TICKS ticks unthrottled, with no sound and no window updates, then shows the current frame and carries on at normal speed (or at `--speed`). For example, `utils/demo.py -g btsd -i replays/back_to_skool_daze.txt --screen --sounds --ffwd 59900 -t 61200` shows just the safe being opened. The tick numbers and results are the same as in a headless run.

`--bells` prints a `BELL` line, with the tick and lesson ID, whenever a lesson starts. `--doors` prints a `DOOR` line whenever a door or window opens or shuts. It shows the tick, the door or window ID, who moved it and where (or `automatically` for a self-shutting door, such as Mr Wacker's study door), and Eric's location. `--signals` prints a `SIGNAL` line whenever a signal used by the command lists (e.g. `SwotGrassed` in Skool Daze's Playtime-SwotGrass) is raised or lowered. It shows the tick, the signal, `raised` or `lowered`, who did it and where, and Eric's location. All signals are cleared, without a `SIGNAL` line, when a lesson starts.

`--lessons` prints three kinds of line. A `LESSON` line appears whenever a teacher starts a lesson by setting Eric's home room (`started`), or Mr Wacker finishes assembly (`finished`). A `TALE` line appears whenever Einstein starts telling a teacher that someone is absent (`ABSENT`), hit him (`HIT`) or wrote on the blackboard (`WRITE`), and shows who the tale is about. A `FETCH` line appears whenever a teacher sets off to fetch Eric, from a lesson, dinner or assembly duty. Each line shows the tick, who was involved and where, and Eric's location. For example, `TALE 857: ABSENT ERIC by EINSTEIN (37,10) to MR WITHIT (34,10) Eric (20,10)`. The teacher's response to a tale (lines for Eric, or `NO_TALES` for Einstein) appears in `--lines`.

`--endings` prints an `UP_A_YEAR` line whenever Eric goes up a year, and a `GAME_OVER` line whenever the game ends. A `GAME_OVER` line says why the game ended: `up a year`, or who ended it and where (e.g. Mr Rockitt sending Eric home with mumps), followed by `expelled` if Eric was expelled. Both lines show the tick and Eric's location. Skool Daze carries on after Eric goes up a year, so it prints no `GAME_OVER` line then. After a game ends, the demo restarts it.

Each line of an inputs file is `TICK ACTION [DURATION]`. ACTION is a key action from `pyskool/keys.py` or `WAIT`. A line `TICK TYPE TEXT` types TEXT on a blackboard after `WRITE`; follow it with `ENTER`. Anything after `#` is a comment. The same game, seed, lesson and inputs always give an identical replay.

`replays/skool_daze.txt` makes Eric complete Skool Daze with seed 0; he goes up a year at tick 16478. To replay it, run `utils/demo.py -i replays/skool_daze.txt -t 16600 --screen`. Likewise, `replays/back_to_skool.txt` makes Eric complete Back to Skool with seed 0; he opens the safe and goes up a year at tick 39167 (`utils/demo.py -g bts -i replays/back_to_skool.txt -t 39300 --screen`). And `replays/skool_daze_take_too.txt` makes Eric complete Skool Daze Take Too with seed 0; he jumps to open the safe at tick 15276, and goes up a year at tick 25205 after unflashing the shields (`utils/demo.py -g sdtt -i replays/skool_daze_take_too.txt -t 25300 --screen`). `replays/ezad_looks.txt` does the same for Ezad Looks; Eric jumps to open the safe at tick 9774, and goes up a year at tick 23813 (`utils/demo.py -g el -i replays/ezad_looks.txt -t 23900 --screen`). And `replays/back_to_skool_daze.txt` completes Back to Skool Daze with seed 0. Eric jumps to hit the last of the 16 shields at tick 41293 and to open the safe at tick 60483, and he goes up a year at tick 86686 after unflashing the shields (`utils/demo.py -g btsd -i replays/back_to_skool_daze.txt -t 86800 --screen`). The safe and shield ticks are the `JUMP` input ticks in the replay files. The game state changes about 6–7 ticks later, when Eric reaches the top of the jump or the shield sound finishes. The up-a-year ticks are the event ticks. `tests/test_replays.py` asserts them.

`utils/demoscan.py` finds input timings. It runs a game to tick `--at`, then forks a copy for each alternative continuation and runs it to tick `--to`. An alternative is the `-c` template (input lines separated by `;`) with each `{expr}` evaluated for one value `v` of the `-v` expression. `--until COND` stops an alternative early, and `--report EXPR` sets what is printed; both are Python evaluated with `demo`, `skool`, `eric`, `cast`, `tick`, `secrets` and `char(name)` available. Other options go to `demo.py`. For example: `utils/demoscan.py -g bts -i FILE --at 1287 --to 1600 -c '{v} CATCH' -v 'range(1300,1600,2)' --until 'eric.mice>0'`. It needs `os.fork()`, and must restore `random`'s state in each child, because Python reseeds it after a fork.

`demo.py` is importable, with its run behind a `__main__` guard. Analysis scripts can therefore `import demo`, build `demo.Demo(demo.parse_args([...]))`, and wrap `demo.game.Game._main_loop` to inspect state each tick. The `Demo` object's `tick` attribute holds the current tick.

## Conventions

- The Sphinx docs in `sphinx/source` document the ini file format (`inifile.rst`, `mainini.rst`, `commands.rst`) and the API (one `.rst` per module). Update them, and `changelog.rst`, alongside behaviour or ini-format changes.
- Packaging metadata is spread across `setup.py`, `pyskool/__init__.py` (`version`), `debian/`, `rpm/pyskool.spec`, `xdg/` and `man/`. Version bumps touch several of these.
