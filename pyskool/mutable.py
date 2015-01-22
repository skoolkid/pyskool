# -*- coding: utf-8 -*-
# Copyright 2008-2010, 2014, 2015 Richard Dymond (rjdymond@gmail.com)
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
Classes for things in the skool that change appearance depending on their
state. For example, a cup that may be empty or contain water or sherry.
"""

class Flashable:
    """Abstract superclass for objects that flash (shields and the safe).

    :param x: The x-coordinate of the object.
    :param y: The y-coordinate of the object.
    :param images: A list of normal images of the object.
    :param inverse_images: A list of inverse images of the object.
    :param score: The points awarded for hitting the object.
    """
    def __init__(self, x, y, images, inverse_images, score=0):
        self.x = x
        self.y = y
        self.score = score
        self.images = images
        self.inverse_images = inverse_images
        self.flashing = False

    def flash(self):
        """Mark the object as flashing."""
        self.flashing = True

    def unflash(self):
        """Mark the object as not flashing."""
        self.flashing = False

    def get_images(self, inverse):
        """Return a 2-tuple containing a list of images of the object, and the
        coordinates at which it should be drawn.

        :param inverse: If `True`, return the inverse images; otherwise return
                        the normal images.
        """
        images = self.inverse_images if inverse else self.images
        return images, (self.x, self.y)

    def build_images(self):
        """Build the images for this object. This method is called after
        rescaling the screen or loading a saved game.
        """
        for image in self.images:
            image.build()
        for image in self.inverse_images:
            image.build()

class Shield(Flashable):
    """A shield that will flash or unflash when hit."""
    pass

class Safe(Flashable):
    """A safe that will flash or unflash when hit."""
    pass

class Cup:
    """A cup that may be empty or filled with water or sherry.

    :param cup_id: The ID of the cup.
    :param coords: The coordinates of the cup.
    :param water_id: The ID of the liquid for which the water-filled image
                     should be used.
    :param sherry_id: The ID of the liquid for which the sherry-filled image
                      should be used.
    """
    def __init__(self, cup_id, coords, water_id, sherry_id):
        self.cup_id = cup_id
        self.x, self.y = coords
        self.water_id = water_id
        self.sherry_id = sherry_id
        self.contents = None
        self.frogs = []

    def set_images(self, empty_images, water_images, sherry_images):
        """Define the images to use for the cup.

        :param empty_images: A list of images of the cup when empty.
        :param water_images: A list of images of the cup when filled with
                             water.
        :param sherry_images: A list of images of the cup when filled with
                              sherry.
        """
        self.empty_images = empty_images
        self.water_images = water_images
        self.sherry_images = sherry_images

    def build_images(self):
        """Build the images for the cup. This method is called after rescaling
        the screen or loading a saved game.
        """
        for image in self.empty_images:
            image.build()
        for image in self.water_images:
            image.build()
        for image in self.sherry_images:
            image.build()

    def is_empty(self):
        """Return whether the cup is empty (contains no liquid or frogs)."""
        return not (self.contents or self.frogs)

    def fill(self, contents):
        """Fill the cup with a liquid, or empty it.

        :param contents: The liquid to fill the cup with, or `None` to empty
                         it.
        :return: The images for and location of the cup.
        """
        self.contents = contents
        return self.get_images()

    def get_images(self):
        """Return a 2-tuple containing a list of images of the current state of
        the cup, and the coordinates at which to draw the cup.
        """
        if self.contents == self.water_id:
            images = self.water_images
        elif self.contents == self.sherry_id:
            images = self.sherry_images
        else:
            images = self.empty_images
        return images, (self.x, self.y)

    def insert_frog(self, frog):
        """Insert a frog into the cup.

        :type frog: :class:`~pyskool.animal.Frog`
        :param frog: The frog.
        """
        self.frogs.append(frog)
        frog.insert_into_cup(self)

    def remove_frog(self, frog):
        """Remove a frog from the cup.

        :type frog: :class:`~pyskool.animal.Frog`
        :param frog: The frog.
        """
        if frog in self.frogs:
            self.frogs.remove(frog)

class Bike:
    """Represents the portion of the tree that may or may not have a bike
    chained to it.

    :param x: The x-coordinate of the bike-on-a-tree image.
    :param y: The y-coordinate of the bike-on-a-tree image.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.unchained_images = None
        self.chained_images = None
        self.chained = True

    def set_images(self, unchained_images, chained_images):
        """Define the images to use for the bike-on-a-tree.

        :param unchained_images: A list of images to use when the bike is not
                                 chained to the tree.
        :param chained_images: A list of images to use when the bike is chained
                               to the tree.
        """
        self.unchained_images = unchained_images
        self.chained_images = chained_images

    def build_images(self):
        """Build the images for the bike. This method is called after rescaling
        the screen or loading a saved game.
        """
        for image in self.unchained_images:
            image.build()
        for image in self.chained_images:
            image.build()

    def unchain(self):
        """Return a 3-tuple containing a list of the images to use when the
        bike is not chained to the tree, and the coordinates of the images.
        """
        self.chained = False
        return self.get_images()

    def chain(self):
        """Return a 2-tuple containing a list of the images to use when the
        bike is chained to the tree, and the coordinates of the images.
        """
        self.chained = True
        return self.get_images()

    def get_images(self):
        """Return a 2-tuple containing a list of images of the current state of
        the bike, and the coordinates at which to draw the bike.
        """
        if self.chained:
            return self.chained_images, (self.x, self.y)
        return self.unchained_images, (self.x, self.y)
