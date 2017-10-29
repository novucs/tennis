#!/usr/bin/env python

"""

Represents a tennis player.

"""


class Player:
    """A tennis player profile.

    Attributes:
        name: The name of the player.
        score: The players current score.
    """

    def __init__(self, name, score=0):
        self.name = name
        self.score = score

    def __str__(self):
        return "{name=" + self.name + ", score=" + str(self.score) + "}"

    def __eq__(self, other):
        if other is None or not isinstance(other, Player):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
