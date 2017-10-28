#!/usr/bin/env python


class Player:
    def __init__(self, name, score=0):
        self.name = name
        self.score = score

    def __str__(self):
        return "{name=" + self.name + ", score=" + str(self.score) + "}"

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name
