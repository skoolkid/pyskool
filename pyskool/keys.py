# -*- coding: utf-8 -*-
# Copyright 2010, 2012 Richard Dymond (rjdymond@gmail.com)
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
The keys that may be used in the game.
"""

import pygame

#//////////////////////////////////////////////////////////////////////////////
# Cheat keys
#//////////////////////////////////////////////////////////////////////////////

#: Slow the game down to half speed (key must be held down).
SLOW = [pygame.K_9]
#: Try to double the speed of the game (key must be held down).
FAST = [pygame.K_0]
#: Proceed to the next lesson.
NEXT_LESSON = [pygame.K_TAB]
#: Make all but one shield flash.
FLASH_MOST = [pygame.K_1]
#: Make all but one shield unflash.
UNFLASH_MOST = [pygame.K_2]
#: Prevent teachers from giving lines.
NO_LINES = [pygame.K_3]
#: Add a random number to Eric's lines total.
ADD_LINES = [pygame.K_4]
#: Set Eric's lines total to zero.
ZERO_LINES = [pygame.K_5]
#: Reveal all combinations, the locations of the stinkbombs and the water
#: pistol, and the answers to any special questions.
REVEAL = [pygame.K_6]
#: Fill Eric's inventory.
GIVE_ALL = [pygame.K_7]
#: Toggle between a water-filled and sherry-filled water pistol.
SWITCH_PISTOL = [pygame.K_8]
#: Open all doors and windows.
OPEN_DOORS = [pygame.K_PAGEUP]
#: Close all doors and windows.
CLOSE_DOORS = [pygame.K_PAGEDOWN]

#//////////////////////////////////////////////////////////////////////////////
# Special keys
#//////////////////////////////////////////////////////////////////////////////

#: Quit.
QUIT = [pygame.K_ESCAPE]
#: Toggle full-screen mode.
FULL_SCREEN = [pygame.K_F11]
#: Pause.
PAUSE = [pygame.K_END]
#: Take a screenshot.
SCREENSHOT = [pygame.K_INSERT]
#: Save the game.
SAVE = [pygame.K_F2]
#: Load the most recently saved game.
LOAD = [pygame.K_F6]
#: Display the menu.
MENU = [pygame.K_F12]
#: Exit the menu.
MENU_EXIT = [pygame.K_F12, pygame.K_ESCAPE]
#: Select the previous item in the menu.
MENU_PREV = [pygame.K_UP, pygame.K_q]
#: Select the next item in the menu.
MENU_NEXT = [pygame.K_DOWN, pygame.K_a]
#: Execute the selected menu item.
MENU_EXEC = [pygame.K_RETURN, pygame.K_SPACE]

#//////////////////////////////////////////////////////////////////////////////
# Movement keys
#//////////////////////////////////////////////////////////////////////////////

#: Left.
LEFT = [pygame.K_LEFT, pygame.K_o]
#: Right.
RIGHT = [pygame.K_RIGHT, pygame.K_p]
#: Up.
UP = [pygame.K_UP, pygame.K_q]
#: Down.
DOWN = [pygame.K_DOWN, pygame.K_a]
#: Sit/stand.
SIT_STAND = [pygame.K_s]
#: Open a desk.
OPEN_DESK = [pygame.K_o]
#: Fire the catapult.
FIRE_CATAPULT = [pygame.K_f]
#: Fire the water pistol.
FIRE_WATER_PISTOL = [pygame.K_g]
#: Drop a stinkbomb.
DROP_STINKBOMB = [pygame.K_d]
#: Throw a punch.
HIT = [pygame.K_h]
#: Jump.
JUMP = [pygame.K_j]
#: Start writing on a blackboard.
WRITE = [pygame.K_w]
#: Stop writing on a blackboard.
ENTER = [pygame.K_RETURN]
#: Try to catch a mouse or frog.
CATCH = [pygame.K_c]
#: Acknowledge understanding of a message.
UNDERSTOOD = [pygame.K_u]
#: Mount the bike.
MOUNT_BIKE = [pygame.K_m]
#: Throw away the water pistol.
DUMP_WATER_PISTOL = [pygame.K_t]
#: Release some mice.
RELEASE_MICE = [pygame.K_r]
#: Kiss.
KISS = [pygame.K_k]
