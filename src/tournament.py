#!/usr/bin/env python

"""

Represents a tennis tournament.

"""


class Tournament:
    """A tennis tournament profile.

    Attributes:
        name: The name of the tournament.
        prizes: A hash table of prizes, keys being the place in the tournament.
        difficulty: The difficulty rating of this tournament.
        sorted_men: The sorted male players of this tournament.
        sorted_women: The sorted female players of this tournament.
    """

    def __init__(self, name, prizes, difficulty, sorted_men=None, sorted_women=None):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty
        self.sorted_men = sorted_men
        self.sorted_women = sorted_women

    def __str__(self):
        return "{name=" + self.name + \
               ", prizes=" + str(self.prizes) + \
               ", difficulty=" + str(self.difficulty) + "}"
