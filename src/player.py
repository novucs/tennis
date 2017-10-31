#!/usr/bin/env python

"""

Represents a tennis player.

"""

from hash_table import HashTable


class Player:
    """A tennis player profile.

    Attributes:
        name: The name of the player.
        scores: The players scores, indexed by the tournament name.
    """

    def __init__(self, name, tournament_count=4):
        self.name = name
        self.ranking_points = 0
        self.scores = HashTable(initial_capacity=tournament_count)

    def __str__(self):
        return "{name=" + self.name + ", score=" + str(self.scores) + "}"

    def __eq__(self, other):
        if other is None or not isinstance(other, Player):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
