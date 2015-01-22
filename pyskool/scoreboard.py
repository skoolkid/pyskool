# -*- coding: utf-8 -*-
# Copyright 2008-2010, 2015 Richard Dymond (rjdymond@gmail.com)
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
Keep track of the score, lines total and high score.
"""

class Scoreboard:
    """The scoreboard.

    :type screen: :class:`~pyskool.graphics.Screen`
    :param screen: The screen on which the scoreboard is displayed.
    """
    def __init__(self, screen):
        self.screen = screen
        self.hiscore = 0
        self._reset()

    def _reset(self):
        """Set the lines total and the score to zero."""
        self.score = self.lines = 0

    def print_score_box(self):
        """Print the score, lines total and hi-score."""
        self.screen.print_score_box(self.score, self.lines, self.hiscore)

    def add_to_score(self, addend):
        """Add points to the score and print it.

        :param addend: The number of points to add.
        """
        self.score += addend
        self.print_score_box()

    def add_lines(self, addend):
        """Add lines to the lines total and print it.

        :param addend: The number of lines to add.
        """
        self.lines = max(self.lines + addend, 0)
        self.print_score_box()

    def reinitialise(self):
        """Reinitialise the scoreboard after a game has ended. The current
        score becomes the new high score if necessary, the score and lines
        total are reset to zero, and all three numbers are printed.
        """
        if self.score > self.hiscore:
            self.hiscore = self.score
        self._reset()
        self.print_score_box()
