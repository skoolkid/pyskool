# -*- coding: utf-8 -*-
# Copyright 2008, 2010, 2013-2016 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of Pyskool.
#
# Pyskool is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Pyskool is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pyskool. If not, see <http://www.gnu.org/licenses/>.

"""
Classes concerned with the screen and drawing things on it.
"""

import os
import pygame

from . import debug

#: ID of the speech bubble image.
SPEECH_BUBBLE = 'SPEECH_BUBBLE'
#: ID of the font image.
FONT = 'FONT'
#: ID of the sprites image.
SPRITES = 'SPRITES'
#: ID of the inventory items image.
INVENTORY = 'INVENTORY'
#: ID of the logo image.
LOGO = 'LOGO'
#: ID of the mutables image.
MUTABLES = 'MUTABLES'
#: ID of the ink-only mutables image.
MUTABLES_INK = 'MUTABLES_INK'
#: ID of the paper-only mutables image.
MUTABLES_PAPER = 'MUTABLES_PAPER'
#: ID of the message box image.
MESSAGE_BOX = 'MESSAGE_BOX'
#: ID of the lesson box image.
LESSON_BOX = 'LESSON_BOX'
#: ID of the score box image.
SCOREBOX = 'SCOREBOX'
#: ID of the play area image.
SKOOL = 'SKOOL'
#: ID of the ink-only play area image.
SKOOL_INK = 'SKOOL_INK'
#: ID of the paper-only play area image.
SKOOL_PAPER = 'SKOOL_PAPER'

class Screen(object):
    """Represents the screen upon which everything is drawn.

    :type config: dict
    :param config: Configuration parameters from the ini file.
    :type gallery: :class:`Gallery`
    :param gallery: The gallery of images to use for drawing.
    :param title_prefix: The window title prefix.
    """
    def __init__(self, config, gallery, title_prefix):
        self.gallery = gallery
        self.screen = None
        self.width = config.get('Width', 32)
        self.height = config.get('Height', 24)
        self.title = title_prefix + config.get('Name', 'Unknown Skool Game')
        self.icon_fname = config.get('Icon', 'icon.png')
        self.fps = config.get('GameFps', 20)
        self.mode = config.get('GraphicsMode', 1)
        self.background = config.get('Background', 2)
        self.scroll_fps = config.get('ScrollFps', 20)
        self.message_box_key = config.get('MessageBoxKey', (1, 1, 1))
        self.lesson_box_pos = config.get('LessonBoxPos', (12, 21))
        self.lesson_box_ink = config.get('LessonBoxInk', (0, 198, 197))
        self.lesson_box_key = ((self.lesson_box_ink[0] + 1) % 256, 0, 0)
        self.logo_coords = config.get('LogoPos', (0, 21))
        self.score_box_coords = config.get('ScoreBoxPos', (24, 21))
        self.score_box_ink = config.get('ScoreBoxInk', (197, 198, 0))
        self.score_box_key = ((self.score_box_ink[0] + 1) % 256, 0, 0)
        self.score_label = config.get('ScoreLabel', 'Score')
        self.lines_label = config.get('LinesTotalLabel', 'Lines')
        self.hi_score_label = config.get('HiScoreLabel', 'Hi-Sc')
        self.score_offset = config.get('ScoreOffset', 1)
        self.lines_offset = config.get('LinesOffset', 9)
        self.hi_score_offset = config.get('HiScoreOffset', 17)
        self.mouse_box_coords = config.get('MouseInventoryPos')
        self.mouse_box_size = config.get('MouseInventorySize', (8, 1))
        self.mouse_box_ink = config.get('MouseInventoryInk', (205, 199, 205))
        self.inventory_coords = config.get('InventoryPos')
        self.inventory_size = config.get('InventorySize', (0, 0))
        self.inventory_key = config.get('InventoryKey', (0, 0, 0))
        self.scroll_right_offset = config.get('ScrollRightOffset', 9)
        self.scroll_left_offset = config.get('ScrollLeftOffset', 10)
        self.scroll_columns = config.get('ScrollColumns', 8)
        self.bubble_lip_size = config.get('SpeechBubbleLipSize', (1, 1))
        self.speech_bubble_size = config.get('SpeechBubbleSize', (8, 3))
        self.speech_bubble_ink = config.get('SpeechBubbleInk', (0, 0, 0))
        self.speech_bubble_colorkey = config.get('SpeechBubbleKey', (0, 254, 0))
        self.speech_bubble_inset = config.get('SpeechBubbleInset', (4, 4))
        self.skool_colorkey = config.get('SkoolInkKey', (255, 255, 255))
        self.initial_column = config.get('InitialColumn', -1)

        pygame.display.set_mode(self.scale_coords((self.width, self.height)))
        self.message_box = gallery.get_image(MESSAGE_BOX)
        self.message_box.set_colorkey(config.get('MessageBoxColour', (197, 0, 0)))
        self.lesson_box = gallery.get_image(LESSON_BOX)
        self.logo = gallery.get_image(LOGO)
        self.score_box = gallery.get_image(SCOREBOX)
        self.bubble = gallery.get_image(SPEECH_BUBBLE)
        bubble_lip_coords = config.get('SpeechBubbleLipCoords', (8, 0))
        self.bubble_lip = self.bubble.subsurface(bubble_lip_coords, self.bubble_lip_size)
        self.font = Font(gallery.get_image(FONT), config.get('FontInk', (0, 1, 2)), config.get('FontPaper', (255, 254, 253)))

    def __getstate__(self):
        d = self.__dict__.copy()
        d['screen'] = None
        return d

    def _get_scale(self):
        return self.gallery.scale
    def _set_scale(self, value):
        self.gallery.scale = value
    scale = property(_get_scale, _set_scale)

    def setup(self, set_mode=False):
        """Set up the following things:

          * the window title and icon
          * the screen background
          * the logo image
          * the score box
          * (optionally) the size of the screen

        :param set_mode: If `True`, the size of the screen will be set.
        """
        if set_mode:
            pygame.display.set_mode(self.scale_coords((self.width, self.height)))
        pygame.display.set_caption(self.title)
        if os.path.isfile(self.icon_fname):
            pygame.display.set_icon(pygame.image.load(self.icon_fname).convert())
        self.screen = pygame.display.get_surface()
        self.screen.fill(self.background)
        self._build_images()
        self.screen.blit(self.logo.surface, self.scale_coords(self.logo_coords))

        # Write the 'Score', 'Lines' and 'Hi-Sc' labels in the scorebox
        score_label = self.get_text(self.score_label, self.score_box_ink, self.score_box_key)
        self.score_box.blit(score_label, (0, self.scale * self.score_offset))
        lines_label = self.get_text(self.lines_label, self.score_box_ink, self.score_box_key)
        self.score_box.blit(lines_label, (0, self.scale * self.lines_offset))
        hi_score_label = self.get_text(self.hi_score_label, self.score_box_ink, self.score_box_key)
        self.score_box.blit(hi_score_label, (0, self.scale * self.hi_score_offset))
        self.screen.blit(self.score_box.surface, self.scale_coords(self.score_box_coords))

    def _rescale(self):
        """Redraw the screen after a scale change."""
        pygame.display.set_mode(self.scale_coords((self.width, self.height)))
        self._build_images()

    def _build_images(self):
        """Build the following images:

        * message box
        * lesson box
        * score box
        * logo
        * speech bubble
        * speech bubble lip
        * font
        """
        self.message_box.build()
        self.lesson_box.build()
        self.score_box.build()
        self.logo.build()
        self.bubble.build()
        self.bubble_lip.build()
        self.font.build_image()

    def scale_up(self):
        """Increase the scale factor by 1, and redraw the screen."""
        self.gallery.scale_up()
        self._rescale()

    def scale_down(self):
        """Decrease the scale factor by 1 (if it is greater than 1), and redraw
        the screen.
        """
        if self.gallery.scale_down():
            self._rescale()
            return True
        return False

    def scale_coords(self, coords):
        """Scale up a pair of coordinates and return them.

        :param coords: The coordinates.
        """
        return self.gallery.scale_coords(coords)

    def initialise_column(self, skool_width, eric_x):
        """Set the leftmost column of the play area that will appear on the
        screen when the game starts.

        :param skool_width: The width of the entire play area (in pixels).
        :param eric_x: Eric's initial x-coordinate.
        """
        self.max_column = skool_width // (8 * self.scale) - self.width
        default_initial_column = min(self.max_column, max((eric_x - self.width // 2) // 8 * 8, 0))
        column = min(self.max_column, default_initial_column if self.initial_column < 0 else self.initial_column)
        self.column = self.initial_column = max(0, 8 * (column // 8))

    def reinitialise(self):
        """Reinitialise the screen for a new game."""
        self.column = self.initial_column
        self.print_lesson('', '')
        self.print_inventory()
        self.print_mice()

    def add_font_character(self, char, offset, width):
        """Define the location and width of a font character bitmap in the font
        image.

        :param char: The font character.
        :param offset: The offset (in pixels) of the font character bitmap from
                       the left edge of the font image.
        :param width: The width of the font character bitmap.
        """
        self.font.add_character(char, offset, width)

    def get_scroll_increment(self, x):
        """Return the direction in which the screen should be scrolled when
        Eric is at a given x-coordinate.

        :param x: Eric's x-coordinate.
        :return: -1 if the screen should scroll right, 1 if it should scroll
                 left, or 0 if it should not scroll.
        """
        offset = x - self.column
        if self.width - self.scroll_left_offset <= offset < self.width:
            return 1
        if -3 < offset <= self.scroll_right_offset:
            return -1
        return 0

    def scroll_skool(self, skool, clock):
        """Scroll the skool across the entire width of the screen from right to
        left.

        :type skool: :class:`~pyskool.skool.Skool`
        :param skool: The skool.
        :type clock: `pygame.time.Clock`
        :param clock: The clock to use to time the scrolling.
        """
        self.column -= self.width
        background = pygame.Surface((self.screen.get_width(), skool.get_height()))
        for n in range(self.width):
            self.column += 1
            skool.draw(False)
            self.screen.blit(background, (-8 * (n + 1) * self.scale, 0))
            self._update()
            clock.tick(self.scroll_fps)

    def scroll(self, inc, skool, clock):
        """Scroll the skool a number of columns across the screen.

        :param inc: The scroll increment (-1 to scroll one column at a time
                    rightwards, 1 to scroll one column at a time leftwards).
        :type skool: :class:`~pyskool.skool.Skool`
        :param skool: The skool.
        :type clock: `pygame.time.Clock`
        :param clock: The clock to use to time the scrolling.
        """
        scroll_inc = 0
        num_cols = self.scroll_columns
        if inc > 0:
            scroll_inc = 1
            num_cols = min(num_cols, self.max_column - self.column)
        elif inc < 0:
            scroll_inc = -1
            num_cols = min(num_cols, self.column)
        for i in range(num_cols):
            self.column += scroll_inc
            skool.draw()
            self._update()
            clock.tick(self.scroll_fps)

    def get_text(self, words, ink, paper, transparent=True):
        """Return a `pygame.Surface` displaying some text in the skool font.

        :param words: The text.
        :param ink: The ink colour to use.
        :param paper: The paper colour to use.
        :param transparent: Whether the paper colour should be transparent.
        """
        surface = self.font.render(words, ink, paper)
        if transparent:
            surface.set_colorkey(paper)
        return surface

    def get_text_width(self, text):
        """Return the width (in pixels) of `text` when rendered at scale 1."""
        return self.font.get_width(text)

    def print_lesson(self, *text_lines):
        """Print some text in the lesson box.

        :param text_lines: The lines of text to print.
        """
        while len(text_lines) < 2:
            text_lines.append('')
        line1, line2 = text_lines[:2]
        lesson_box = self.lesson_box.surface.copy()
        line1_text = self.get_text(line1, self.lesson_box_ink, self.lesson_box_key)
        line2_text = self.get_text(line2, self.lesson_box_ink, self.lesson_box_key)
        font_height = self.scale * 8
        line1_x = (lesson_box.get_width() - line1_text.get_width()) // 2
        line1_y = (lesson_box.get_height() - 2 * font_height) // 2
        lesson_box.blit(line1_text, (line1_x, line1_y))
        line2_x = (lesson_box.get_width() - line2_text.get_width()) // 2
        line2_y = line1_y + font_height
        lesson_box.blit(line2_text, (line2_x, line2_y))
        coords = self.scale_coords(self.lesson_box_pos)
        self.screen.blit(lesson_box, coords)
        self._update(pygame.Rect(coords, lesson_box.get_size()))

    def _print_number(self, surface, number, y_offset):
        """Print a number right-aligned on a surface.

        :type surface: `pygame.Surface`
        :param surface: The surface.
        :param number: The number.
        :param y_offset: The y-offset at which to print the number.
        """
        number_text = self.get_text(str(number), self.score_box_ink, self.score_box_key)
        surface.blit(number_text, (surface.get_width() - number_text.get_width() - self.scale, y_offset * self.scale))

    def print_score_box(self, score, lines, hi_score):
        """Print the score, lines total and hi-score in the score box.

        :param score: The score.
        :param lines: The lines total.
        :param hi_score: The hi-score.
        """
        background = self.score_box.surface.copy()
        self._print_number(background, score, self.score_offset)
        self._print_number(background, lines, self.lines_offset)
        self._print_number(background, hi_score, self.hi_score_offset)
        coords = self.scale_coords(self.score_box_coords)
        self.screen.blit(background, coords)
        self._update(pygame.Rect(coords, background.get_size()))

    def print_inventory(self, item_images=()):
        """Print the inventory. If no inventory is defined, nothing happens.

        :param item_images: A sequence of item images to draw in the inventory
                            box.
        """
        if not self.inventory_coords:
            return
        inventory_box = pygame.Surface(self.scale_coords(self.inventory_size))
        inventory_box.fill(self.inventory_key)
        inventory_box.set_colorkey(self.inventory_key)
        x = 0
        for image in item_images:
            if image:
                inventory_box.blit(image.surface, (x, 0))
                x += image.get_width()
        background = pygame.Surface(inventory_box.get_size())
        background.fill(self.background)
        coords = self.scale_coords(self.inventory_coords)
        self.screen.blit(background, coords)
        self.screen.blit(inventory_box, coords)
        self._update(pygame.Rect(coords, inventory_box.get_size()))

    def print_mice(self, count=0, mouse_image=None):
        """Print the mouse inventory. If no mouse inventory is defined, nothing
        happens.

        :param count: The number of mice to draw.
        :param mouse_image: An image of a captured mouse.
        """
        if not self.mouse_box_coords:
            return
        mouse_box = pygame.Surface(self.scale_coords(self.mouse_box_size))
        mouse_box.fill(self.inventory_key)
        mouse_box.set_colorkey(self.inventory_key)
        if mouse_image and count * mouse_image.get_width() > mouse_box.get_width():
            mouse_box.blit(mouse_image.surface, (0, 0))
            counter_text = self.get_text('x%i' % count, self.mouse_box_ink, self.inventory_key)
            mouse_box.blit(counter_text, (mouse_image.get_width(), (mouse_box.get_height() - mouse_image.get_height()) // 2))
        else:
            for x in range(count):
                mouse_box.blit(mouse_image.surface, (x * mouse_image.get_width(), 0))
        background = pygame.Surface(mouse_box.get_size())
        background.fill(self.background)
        coords = self.scale_coords(self.mouse_box_coords)
        self.screen.blit(background, coords)
        self.screen.blit(mouse_box, coords)
        self._update(pygame.Rect(coords, mouse_box.get_size()))

    def contains(self, character, full=True):
        """Return whether a character is on-screen.

        :type character: :class:`~pyskool.character.Character`
        :param character: The character to check.
        :param full: If `True`, return whether the character's entire sprite
                     is on-screen; if `False`, return whether any part of the
                     character's sprite is on-screen.
        """
        return self.column <= character.x <= self.column + self.width - (3 if full else 1)

    def print_message_box(self, x, y, message, ink, paper):
        """Print a message box.

        :param x: The x-coordinate of the messenger's head.
        :param y: The y-coordinate of the messenger's head.
        :type message: tuple
        :param message: The lines of text to write in the box.
        :type ink: RGB triplet
        :param ink: The ink colour of the box.
        :type paper: RGB triplet
        :param paper: The paper colour of the box.
        """
        box = pygame.Surface(self.message_box.get_size())
        box.fill(paper)
        box.blit(self.message_box.surface, (0, 0))
        box_width, box_height = box.get_size()
        line_height = self.scale * 8
        text_y = (box_height - line_height * len(message)) // 2
        for line in message:
            text_image = self.get_text(line, ink, paper, False)
            text_x = (box_width - text_image.get_width()) // 2
            box.blit(text_image, (text_x, text_y))
            text_y += line_height
        box.set_colorkey(self.message_box_key)

        box_x, box_y = self.scale_coords((x - self.column, y))
        box_x += 4 * self.scale - box_width // 2
        box_y -= box_height
        if box_x < 0:
            box_x = 0
        elif box_x + box_width > self.screen.get_width():
            box_x = self.screen.get_width() - box_width
        self.screen.blit(box, (box_x, box_y))
        self._update(pygame.Rect((box_x, box_y), (box_width, box_height)))

    def get_bubble(self, words, lip_pos, shift):
        """Create a speech bubble displaying a portion of a message.

        :param words: The text of the message.
        :param lip_pos: The offset (in tiles) from the left edge of the speech
                        bubble at which to place the lip.
        :param shift: The offset (in tiles) by which to shift the text image
                      before displaying it in the bubble; if negative, leading
                      spaces will be displayed.
        :return: A 2-tuple, `(bubble, done)`, where `bubble` is the speech
                 bubble image (an :class:`Image`), and `done` is `True` if the
                 entire message has been spoken, `False` otherwise.
        """
        bubble = pygame.Surface(self.scale_coords(self.speech_bubble_size))
        bubble.fill(self.speech_bubble_colorkey)
        bubble.set_colorkey(self.speech_bubble_colorkey)
        bubble.blit(self.bubble.surface, (0, 0))
        lip_x = min(lip_pos, self.speech_bubble_size[0] - self.bubble_lip_size[0])
        lip_coords = self.scale_coords((lip_x, self.speech_bubble_size[1] - self.bubble_lip_size[1]))
        bubble.blit(self.bubble_lip.surface, lip_coords)

        # Open the lip of the speech bubble
        open_lip_xy = (lip_coords[0], lip_coords[1] - self.scale)
        open_lip_area = (0, 0, self.bubble_lip.get_width(), self.scale)
        bubble.blit(self.bubble_lip.surface, open_lip_xy, open_lip_area)

        text = self.get_text(words, self.speech_bubble_ink, self.speech_bubble_colorkey)
        tile_width = 8 * self.scale
        min_inset_x = self.speech_bubble_inset[0] * self.scale
        inset_x = min_inset_x - tile_width * min(shift, 0)
        inset_y = self.speech_bubble_inset[1] * self.scale
        text_x = max(shift, 0) * tile_width
        max_width = tile_width * self.speech_bubble_size[0] - 2 * min_inset_x
        width = min(min_inset_x + max_width - inset_x, text.get_width() - text_x)
        text_window = text.subsurface((text_x, 0), (width, tile_width))
        bubble.blit(text_window, (inset_x, inset_y))
        return (Image(None, None, bubble), width < 0)

    def _update(self, *args):
        """Update the display.

        :param args: Arguments passed to `pygame.display.update`.
        """
        pygame.display.update(*args)

    def draw(self, skool_images, cast, speech_bubbles, update):
        """Draw everything on the screen.

        :param skool_images: The play area images.
        :param cast: The cast (3-tuples, `(x, y, image)`, where `x` and `y`
                     are the coordinates, and `image` is an image of a cast
                     member).
        :param speech_bubbles: Speech bubbles (3-tuples, `(x, y, image)`).
        :param update: Whether to update the screen after drawing.
        """
        if self.mode == 0:
            self._draw_skool(self.screen, skool_images[0].surface)
            for x, y, image in cast:
                self._draw_image(self.screen, x, y, image)
        else:
            skool_ink = skool_images[1].surface
            height = skool_ink.get_height()
            scratch = pygame.Surface((self.width * 8 * self.scale, height))
            self._draw_skool(scratch, skool_ink)
            for x, y, image in cast:
                self._draw_image(scratch, x, y, image)
            self._draw_skool(self.screen, skool_images[2].surface)
            scratch.set_colorkey(self.skool_colorkey)
            self.screen.blit(scratch, (0, 0))
        for x, y, image in speech_bubbles:
            self._draw_image(self.screen, x, y, image)
        if update:
            self._update()

    def _draw_skool(self, surface, skool):
        """Draw the skool.

        :type surface: `pygame.Surface`
        :param surface: The surface on which to draw the skool.
        :type skool: `pygame.Surface`
        :param skool: An image of the play area.
        """
        surface.blit(skool, self.scale_coords((-self.column, 0)))

    def _draw_image(self, surface, x, y, image):
        """Draw an image on a surface.

        :type surface: `pygame.Surface`
        :param surface: The surface on which to draw the image.
        :param x: The x-coordinate of the image.
        :param y: The y-coordinate of the image.
        :type image: :class:`Image`
        :param image: The image.
        """
        if image and image.surface:
            surface.blit(image.surface, self.scale_coords((x - self.column, y)))

    def take_screenshot(self, filename):
        """Take a screenshot and save it to a file.

        :param filename: The name of the file.
        """
        pygame.image.save(self.screen, filename)

    def has_font_char(self, char):
        """Return whether the skool font contains a bitmap for a given
        character.

        :param char: The character to look for.
        """
        return self.font.has_char(char)

    def draw_menu(self, menu, refresh=False):
        """Draw the menu and update the screen.

        :type menu: :class:`~pyskool.game.Menu`
        :param menu: The menu.
        :param refresh: If `True`, the entire screen will be updated; if
                        `False`, only the part of the screen occupied by the
                        menu will be updated.
        """
        screen_size = self.screen.get_size()
        menu_width = int(screen_size[0] * menu.width)
        padding = 2 * self.scale

        label_width = menu_width - 2 * padding
        labels_height = 0
        labels = []
        for i, item in enumerate(menu.images):
            background = menu.highlight if i == menu.selected_index else menu.paper
            label_height = item.get_height() + padding
            label_surface = pygame.Surface((label_width, label_height))
            label_surface.fill(background)
            item_pos = ((label_width - item.get_width()) // 2, (label_height - item.get_height()) // 2)
            label_surface.blit(item, item_pos)
            labels.append(label_surface)
            labels_height += label_height

        text = menu.title
        title = pygame.Surface((label_width, label_height))
        title.fill(menu.title_paper)
        text_pos = ((label_width - text.get_width()) // 2, (label_height - text.get_height()) // 2)
        title.blit(text, text_pos)
        labels_height += padding + label_height

        if menu.status_bar:
            text = self.get_text(menu.status, menu.ink, menu.paper)
            status = pygame.Surface((label_width, label_height))
            status.fill(menu.status_paper)
            text_pos = ((label_width - text.get_width()) // 2, (label_height - text.get_height()) // 2)
            status.blit(text, text_pos)
            labels_height += padding + label_height

        menu_height = labels_height + 2 * padding
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill(menu.paper)
        labels_x = (menu_width - label_width) // 2
        labels_y = (menu_height - labels_height) // 2
        menu_surface.blit(title, (labels_x, labels_y))
        labels_y += label_height + padding
        for label in labels:
            menu_surface.blit(label, (labels_x, labels_y))
            labels_y += label_height
        labels_y += padding
        if menu.status_bar:
            menu_surface.blit(status, (labels_x, labels_y))
        menu_surface.set_alpha(menu.alpha)

        menu_pos = ((screen_size[0] - menu_width) // 2, (screen_size[1] - menu_height) // 2)
        if menu.backdrop:
            self.screen.blit(menu.backdrop, menu_pos)
        else:
            menu.backdrop = self.screen.subsurface(menu_pos, menu_surface.get_size()).copy()
        self.screen.blit(menu_surface, menu_pos)
        if refresh:
            self._update()
        else:
            self._update(pygame.Rect(menu_pos, menu_surface.get_size()))

class Gallery:
    """A container for all the images used in a game.

    :param images_dir: The path to the `images` directory.
    :param image_set: The name of the set of images to use.
    :param scale: The desired scale of the images.
    :type images: dict
    :param images: Key-value pairs (image ID, path) from the `Images` section.
    """
    def __init__(self, images_dir, image_set, scale, images):
        self.images_dir = images_dir
        self.image_set = image_set
        self.images = images
        self.reset(scale)

    def __getstate__(self):
        d = self.__dict__.copy()
        d['images_dir'] = None
        d['surfaces'] = {}
        return d

    def restore(self, images_dir):
        """Perform tasks required immediately after loading a saved game.

        :param images_dir: The path to the `images` directory.
        """
        self.images_dir = images_dir

    def reset(self, scale):
        """Set the scale and clear the image cache.

        :param scale: The scale.
        """
        self.scale = scale
        self.surfaces = {}

    def scale_coords(self, coords):
        """Scale up a pair of coordinates and return them.

        :param coords: The coordinates.
        """
        return (8 * self.scale_length(coords[0]), 8 * self.scale_length(coords[1]))

    def scale_length(self, length):
        """Scale up a length and return it."""
        return self.scale * length

    def scale_up(self):
        """Increase the scale factor by 1. The image cache will be cleared."""
        self.reset(self.scale + 1)

    def scale_down(self):
        """Decrease the scale factor by 1 (if it is greater than 1). The image
        cache will be cleared.

        :return: `True` if the scale factor was decreased, `False` otherwise.
        """
        if self.scale > 1:
            self.reset(self.scale - 1)
            return True
        return False

    def get_image(self, image_id):
        """Return an :class:`Image` from the gallery, or `None` if there is no
        image in the gallery with the given ID. The image will be scaled up as
        necessary.

        :param image_id: The ID of the image.
        """
        return Image(self, image_id, self.get_surface(image_id))

    def get_surface(self, image_id):
        """Return an image (a `pygame.Surface`) from the gallery, or `None`
        if there is no image in the gallery with the given ID. The image will
        be scaled up as necessary.

        :param image_id: The ID of the image.
        """
        if image_id in self.surfaces:
            return self.surfaces[image_id]
        if image_id not in self.images:
            return None
        scale_up = True
        image_set_dir = os.path.join(self.images_dir, '%sx%i' % (self.image_set, self.scale))
        if os.path.isdir(image_set_dir):
            scale_up = False
        else:
            image_set_dir = os.path.join(self.images_dir, '%sx1' % self.image_set)
        fname = os.path.join(*self.images[image_id].split('/'))
        image_file = os.path.join(image_set_dir, fname)
        if not os.path.isfile(image_file):
            debug.log("Unable to load image '%s' from %s: file not found" % (image_id, image_file))
            return None
        img = pygame.image.load(image_file).convert()
        if scale_up:
            img = pygame.transform.scale(img, (self.scale * img.get_width(), self.scale * img.get_height()))
        self.surfaces[image_id] = img
        return img

class Image:
    """A container for a `pygame.Surface`. This is used to handle the saving
    and restoring of images, because a `pygame.Surface` cannot be pickled
    directly.

    :type gallery: :class:`Gallery`
    :param gallery: The gallery of images.
    :param image_id: The ID of the image (the parent image) from which this
                     image is derived.
    :type surface: `pygame.Surface`
    :param surface: The image itself.
    :param top_left: The coordinates of the top-left corner of this image
                     inside the parent image.
    :param flipped: If `True`, the image will be flipped before use.
    :param colorkey: The colour key.
    """
    def __init__(self, gallery, image_id, surface, top_left=None, size=None, flipped=False, colorkey=None):
        self.gallery = gallery
        self.image_id = image_id
        self.surface = surface
        self.top_left = top_left
        self.flipped = flipped
        self.size = size
        self.colorkey = colorkey
        if self.surface and flipped:
            self._flip_surface()

    def __getstate__(self):
        d = self.__dict__.copy()
        d['surface'] = None
        return d

    def _scale_coords(self, coords):
        """Scale up a pair of coordinates and return them.

        :param coords: The coordinates.
        """
        return self.gallery.scale_coords(coords)

    def scale_length(self, length):
        """Scale up a length and return it."""
        return self.gallery.scale_length(length)

    def build(self):
        """Build the image. This method is called after rescaling the screen or
        loading a saved game.
        """
        self.surface = self.gallery.get_surface(self.image_id)
        if self.top_left and self.size:
            self.surface = self.surface.subsurface(self._scale_coords(self.top_left), self._scale_coords(self.size))
        if self.flipped:
            self._flip_surface()
        if self.colorkey:
            self.surface.set_colorkey(self.colorkey)

    def _flip_surface(self):
        """Flip the image."""
        self.surface = pygame.transform.flip(self.surface, True, False)

    def subsurface(self, coords, size):
        """Return a subsurface of the image.

        :param coords: The coordinates of the top-left corner of the
                       subsurface.
        :param size: The size of the subsurface.
        """
        surface = self.surface.subsurface(self._scale_coords(coords), self._scale_coords(size))
        return Image(self.gallery, self.image_id, surface, coords, size, self.flipped, self.colorkey)

    def copy(self):
        """Return a copy of the image."""
        return Image(self.gallery, self.image_id, self.surface.copy(), self.top_left, self.size, self.flipped, self.colorkey)

    def get_width(self):
        """Return the width of the image."""
        if self.surface:
            return self.surface.get_width()

    def get_height(self):
        """Return the width of the image."""
        if self.surface:
            return self.surface.get_height()

    def get_size(self):
        """Return the size (width, height) of the image."""
        if self.surface:
            return self.surface.get_size()

    def set_colorkey(self, colorkey):
        """Set the colour key of the image.

        :param colorkey: The colour key.
        """
        self.colorkey = colorkey
        if self.surface:
            self.surface.set_colorkey(colorkey)

    def flip(self):
        """Return a flipped copy of the image."""
        return Image(self.gallery, self.image_id, self.surface, self.top_left, self.size, True, self.colorkey)

    def blit(self, *args):
        """Blit a `pygame.Surface` onto this image.

        :param args: Arguments passed to `pygame.Surface.blit()`.
        """
        self.surface.blit(*args)

    def scale_blit(self, source, dest, area=None):
        """Draw an image on this image using scaled coordinates.

        :type source: `pygame.Surface`
        :param source: The image to draw.
        :param dest: The coordinates at which to draw the image.
        :param area: A 4-tuple - `(left, top, width, height)` - defining the
                     subsurface of the image to draw.
        """
        if area:
            x, y = self._scale_coords(area[:2])
            w, h = self._scale_coords(area[2:])
            self.surface.blit(source, self._scale_coords(dest), (x, y, w, h))
        else:
            self.surface.blit(source, self._scale_coords(dest))

class Font:
    """The skool font.

    :type image: :class:`Image`
    :param image: The font image.
    :type ink_key: RGB triplet
    :param ink_key: The ink colour in `font.png` (used to create transparency).
    :type paper_key: RGB triplet
    :param paper_key: The paper colour in `font.png` (used to create
                      transparency).
    """
    def __init__(self, image, ink_key, paper_key):
        self.image = image
        self.ink_key = ink_key
        self.paper_key = paper_key
        self.characters = {}

    def build_image(self):
        """Build the font image. This method is called after rescaling the
        screen or loading a saved game.
        """
        self.image.build()

    def add_character(self, char, offset, width):
        """Define the location and width of a font character bitmap in the font
        image.

        :param char: The font character.
        :param offset: The offset (in pixels) of the font character bitmap from
                       the left edge of the font image.
        :param width: The width of the font character bitmap.
        """
        self.characters[char] = (offset, width)

    def render(self, words, ink, paper):
        """Return an image (a `pygame.Surface`) of a text message written in
        the skool font.

        :param words: The message.
        :type ink: RGB triplet
        :param ink: The desired ink colour.
        :type paper: RGB triplet
        :param paper: The desired paper colour.
        """
        character_images = []
        total_width = 0
        height = self.image.get_height()
        for c in words:
            offset, width = self.characters[c]
            image = self.image.surface.subsurface((self.image.scale_length(offset), 0), (self.image.scale_length(width), height))
            character_images.append(image)
            total_width += width
        text = pygame.Surface((self.image.scale_length(total_width), height))
        offset = 0
        for image in character_images:
            text.blit(image, (offset, 0))
            offset += image.get_width()
        paper_surface = pygame.Surface((text.get_width(), text.get_height()))
        paper_surface.fill(paper)
        ink_surface = pygame.Surface((text.get_width(), text.get_height()))
        ink_surface.fill(ink)
        text.set_colorkey(self.ink_key)
        ink_surface.blit(text, (0, 0))
        ink_surface.set_colorkey(self.paper_key)
        paper_surface.blit(ink_surface, (0, 0))
        return paper_surface

    def has_char(self, char):
        """Return whether the skool font contains a bitmap for a given
        character.

        :param char: The character to look for.
        """
        return char in self.characters

    def get_width(self, text):
        """Return the width (in pixels) of `text` when rendered at scale 1."""
        return sum([self.characters[char][1] for char in text])
