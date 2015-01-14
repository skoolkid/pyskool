.. _graphics:

Graphics
========
The stock Pyskool graphics are stored in PNG files in subdirectories under
`images/originalx1`. The PNG files are:

* `bubble.png` - speech bubble and lip
* `font.png` - the skool font
* `inventory.png` - mouse, frog, water pistol etc.
* `lesson_box.png` - the lesson box background
* `logo.png` - the, er, logo
* `message_box.png` - the message box background
* `mutables_ink.png` - doors, windows, shields, safe etc. (ink colours only)
* `mutables_paper.png` - doors, windows, shields, safe etc. (paper colours
  only)
* `mutables.png` - doors, windows, shields, safe etc. (full colour)
* `scorebox.png` - the score/lines/hi-score box background
* `skool_ink.png` - the skool (ink colours only)
* `skool_paper.png` - the skool (paper colours only)
* `skool.png` - the skool (full colour)
* `sprites.png` - the characters in various 'animatory states'

These images were extracted straight from memory snapshots of Skool Daze and
Back to Skool, and are therefore identical to the graphics in the original
games (hence the `original` prefix in the directory name), except for minor
glitches that have been fixed. (See `Skool Daze graphic glitches`_ and
`Back to Skool graphic glitches`_.)

The `*_ink.png` and `*_paper.png` files are used in ``GraphicsMode`` 1 (see
:ref:`screenConfig`) in order to emulate the Spectrum display, which was
restricted to two colours ('ink' and 'paper') per 8x8-pixel block.

`sprites.png` is an 8x16 array of sprites for the characters in the game. These
sprites are all facing left, and are flipped to obtain the corresponding
right-facing sprites.

Any of these images can be customised using your favourite image editor.

Pyskool performs the following steps to determine the base directory for
graphics to use in the game:

* Collect the values of ``ImageSet`` and ``Scale`` from the :ref:`gameConfig`
  and :ref:`screenConfig` sections of the config file
* Look for the directory `images/<ImageSet>x<Scale>`
* Use images from that directory if it exists, or...
* ...use images from `images/<ImageSet>x1` and scale them up

The actual image files used from the base directory are defined in the
:ref:`images` section.

If you wanted to create your own hi-res graphics at 2x the original Spectrum
size, you could place them under a base directory called `images/Customx2`
and use the following parameter value in the :ref:`gameConfig` section::

  ImageSet, Custom

and the following parameter values in the :ref:`screenConfig` section::

  Scale, 2
  GraphicsMode, 0

.. _Skool Daze graphic glitches: http://skoolkit.ca/disassemblies/skool_daze/graphics/glitches.html
.. _Back to Skool graphic glitches: http://skoolkit.ca/disassemblies/back_to_skool/graphics/glitches.html
