#!/usr/bin/env python

"""

Solution for static data.

"""

import math

import numpy as np

from hash_table import HashTable
from linked_list import List
from pipe_sort import Sorter
from player import Player
from tournament import Tournament


def parse_csv_line(line):
    """Parses a CSV (comma separated values) line.

    :param line: The line to parse.
    :return: The array of values in this line.
    """

    if line == "":
        return np.empty(0)

    values = List()
    value = ""
    quotes = False

    for character in line:
        if character == '\n':
            break
        elif character == '"':
            quotes = not quotes
        elif not quotes and character == ',':
            values.append(value)
            value = ""
        else:
            value += character

    values.append(value)
    return values.to_array()


def handle_duplicates(file_name, previous_lines, line):
    """Handles duplicate entries found in files.

    :param file_name: The file name.
    :param previous_lines: The hash table of all previous found lines.
    :param line: The current line read in.
    :return: True if a duplicate was found otherwise false.
    """

    if previous_lines[line]:
        print("Skipping duplicate line found in " + file_name)
        print(line)
        return True

    previous_lines[line] = True
    return False


def load_tournaments_file(file_name):
    """Loads tournaments from a file.

    :return: A hash table of tournaments, mapped by their name.
    """

    tournaments = HashTable()

    with open(file_name, "r") as the_file:
        header = True
        first_entry = True
        current_name = ""
        current_difficulty = 0
        prizes = HashTable()
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(file_name, previous_lines, line):
                continue

            if header:
                header = False
                continue

            values = parse_csv_line(line)
            name = values[0]
            place = int(values[1])
            prize = values[2]
            difficulty = values[3]

            if len(name) > 0:
                if first_entry:
                    current_name = name
                    current_difficulty = float(difficulty)
                    first_entry = False
                else:
                    tournament = Tournament(current_name, prizes,
                                            current_difficulty)
                    tournaments.insert(current_name, tournament)
                    current_name = name
                    prizes = HashTable()

            prizes.insert(place, prize)

    tournament = Tournament(current_name, prizes, current_difficulty)
    tournaments.insert(current_name, tournament)
    return tournaments


def load_players_file(file_name, tournament_count):
    """Loads players from file.

    :param file_name: The name of the player names file.
    :param tournament_count: The number of tournaments this circuit has.
    :return: The hash table of player profiles by name.
    """

    players = HashTable()

    with open(file_name, "r") as the_file:
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(file_name, previous_lines, line):
                continue

            values = parse_csv_line(line)
            name = values[0]
            player = Player(name, tournament_count)
            players.insert(name, player)

    return players


def load_ranking_points_file(file_name):
    """Loads the ranking points file.

    :param file_name: The name of the ranking points file.
    :return: The hash table of place to tournament ranking points.
    """

    ranking_points = HashTable()

    with open(file_name, "r") as the_file:
        header = True
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(file_name, previous_lines, line):
                continue

            if header:
                header = False
                continue

            values = parse_csv_line(line)
            points = int(values[0])
            rank = int(values[1])
            ranking_points.insert(rank, points)

    return ranking_points


def load_round_file(file_name, tournament_name, players_by_name):
    """Loads a round from file and updates each players scores.

    :param file_name: The file name.
    :param tournament_name: The name of the tournament.
    :param players_by_name: The players participating in this round.
    :return: None
    """

    with open(file_name, "r") as the_file:
        header = True
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(file_name, previous_lines, line):
                continue

            if header:
                header = False
                continue

            values = parse_csv_line(line)
            player_a_name = values[0]
            player_a_score = int(values[1])
            player_b_name = values[2]
            player_b_score = int(values[3])
            player_a = players_by_name[player_a_name]
            player_b = players_by_name[player_b_name]

            if player_a is None or player_b is None:
                raise ValueError("A player in this round does not exist in "
                                 "this tournament")

            if player_a.scores[tournament_name] is None:
                player_a.scores[tournament_name] = player_a_score
            else:
                player_a.scores[tournament_name] += player_a_score

            if player_b.scores[tournament_name] is None:
                player_b.scores[tournament_name] = player_b_score
            else:
                player_b.scores[tournament_name] += player_b_score


def tally_and_print(tournament, players, ranking_points):
    """Tallies the tournament results and prints all the prizes each player is
    owed.

    :param tournament: The tournament to print.
    :param players: The sorted list of players in this tournament.
    :param ranking_points: A hash table of rank to points.
    :return: None
    """

    rank = 0
    previous_score = math.inf

    for player in players:
        current_score = player.scores[tournament.name]

        if previous_score > current_score:
            rank += 1

        previous_score = current_score
        prize = tournament.prizes[rank]
        points = ranking_points[rank]

        if prize is not None:
            print(player.name + " wins " + prize)

        if points is not None:
            player.ranking_points += points * tournament.difficulty


def run():
    print("Solution - Static")

    # Load tournaments, players and ranking points.
    tournaments = load_tournaments_file("../resources/tournaments.csv")
    men_by_name = load_players_file("../resources/male_players.csv", len(tournaments))
    women_by_name = load_players_file("../resources/female_players.csv", len(tournaments))
    ranking_points = load_ranking_points_file("../resources/ranking_points.csv")

    for tournament_name, tournament in tournaments:
        # Collect all statistics for each round in the tournament.
        male_round_file_names = ["../resources/round1_men.csv"]
        female_round_file_names = ["../resources/round1_ladies.csv"]

        for file_name in male_round_file_names:
            load_round_file(file_name, tournament_name, men_by_name)

        for file_name in female_round_file_names:
            load_round_file(file_name, tournament_name, women_by_name)

        # Sort each of the players by score.
        male_sorter = Sorter(lambda a, b: b.scores[tournament_name] - a.scores[tournament_name])
        female_sorter = Sorter(lambda a, b: b.scores[tournament_name] - a.scores[tournament_name])

        for player_name, profile in men_by_name:
            male_sorter.consume(profile)

        for player_name, profile in women_by_name:
            female_sorter.consume(profile)

        tournament.sorted_men = male_sorter.sort()
        tournament.sorted_women = female_sorter.sort()

        # Print all players that have earned prizes.
        print("--------------------------------\n")
        print("Results for tournament " + tournament.name + "\n")
        print("--------------------------------\n")

        print("Men's Prizes")
        tally_and_print(tournament, tournament.sorted_men, ranking_points)

        print()

        print("Women's Prizes")
        tally_and_print(tournament, tournament.sorted_women, ranking_points)

        print("\n\n")

    # Sort all players by the overall circuit ranking points.
    male_sorter = Sorter(lambda a, b: b.ranking_points - a.ranking_points)
    female_sorter = Sorter(lambda a, b: b.ranking_points - a.ranking_points)

    for player_name, profile in men_by_name:
        male_sorter.consume(profile)

    for player_name, profile in women_by_name:
        female_sorter.consume(profile)

    sorted_men = male_sorter.sort()
    sorted_women = female_sorter.sort()

    # Print all players ordered by ranking points.
    print("--------------------------------\n")
    print("Total ranking points\n")
    print("--------------------------------\n")

    print("Men:")

    for player in sorted_men:
        print(player.name + "\t" + str(player.ranking_points))

    print()
    print("Women:")

    for player in sorted_women:
        print(player.name + "\t" + str(player.ranking_points))


if __name__ == '__main__':
    run()
