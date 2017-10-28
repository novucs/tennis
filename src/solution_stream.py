#!/usr/bin/env python

"""

Solution for streamed data.

"""

from hash_table import HashTable
from player import Player
from ranked_tree import Tree

players_by_name = HashTable()
sorted_players = Tree()


def create_player(player_name):
    players_by_name[player_name] = Player(player_name)


def accept_score(player_name, score):
    # Do nothing if player did not score anything.
    if score == 0:
        return

    # Fetch the players profile.
    player = players_by_name[player_name]

    # Update the players ranking.
    sorted_players.delete(player.score, player)
    player.score += score
    sorted_players.insert(player.score, player)


if __name__ == '__main__':
    print("Solution - Stream")
