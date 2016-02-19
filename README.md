Pyskool
=======
In 1984, Microsphere published
[Skool Daze](http://en.wikipedia.org/wiki/Skool_Daze), a game for the
[Sinclair ZX Spectrum](http://en.wikipedia.org/wiki/ZX_Spectrum). In 1985, the
sequel [Back to Skool](http://en.wikipedia.org/wiki/Back_to_Skool) was
published.

Each game is based in a boys' school (though Back to Skool adds a playground
and a girls' school) and revolves around the antics of Eric, the hero. In Skool
Daze, Eric must steal his report card from the school safe - the combination of
which must be extracted from the teachers' brains using flashing shields or, in
the case of the history teacher, post-hypnotic suggestion. In Back to Skool,
Eric must get his report card back into the school safe, this time with the
extra help provided by a water pistol, stinkbombs, a bike, mice, a frog and a
girlfriend.

Pyskool is a re-implementation of these classic games in Python and Pygame,
with the aim of making them easy to customise by editing a configuration file
or - for more advanced customisation - writing some Python code.

See the [documentation](http://skoolkid.github.io/pyskool/) for more details
(mirror [here](https://skoolkid.gitlab.io/pyskool/)).

Playing Pyskool
---------------
Before playing Pyskool for the first time from a checkout of this repository,
you will need to create the game launcher scripts, images, ini files and sound
files:

    $ make scripts images ini sounds

Then you can run one of the game launcher scripts:

    $ ./skool_daze.py
    $ ./back_to_skool.py
    $ ./skool_daze_take_too.py
    $ ./ezad_looks.py
    $ ./back_to_skool_daze.py
