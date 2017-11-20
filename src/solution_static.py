#!/usr/bin/env python

"""

Solution for static data.

"""

import os.path

from hash_table import HashTable
from pipe_sort import Sorter
from player import Player
from tournament import Tournament
from utils import *


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

    :return: A list of tournaments.
    """

    tournaments = List()

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
                    tournaments.append(tournament)
                    current_name = name
                    prizes = HashTable()

            prizes.insert(place, prize)

    tournament = Tournament(current_name, prizes, current_difficulty)
    tournaments.append(tournament)
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


def load_round_file(file_name, tournament_name, players_by_name, gender):
    """Loads a round from file and updates each players scores.

    :param file_name: The file name.
    :param tournament_name: The name of the tournament.
    :param players_by_name: The players participating in this round.
    :param gender: The gender of the players in this round.
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

            if (gender == MALE and player_a_score == 3 and player_b_score == 3) or \
                    (gender == FEMALE and player_a_score == 2 and player_b_score == 2):
                print("Skipping erroneous entry in " + file_name)
                print("No two players in the same match can win the match point")
                print(line)
                continue

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
    previous_score = float('inf')

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


def get_file(name, default):
    """Gets the path to a file from the user.

    :param name: The simple name of the files purpose.
    :param default: The default path for this file.
    :return: A valid path to the requested file.
    """

    while True:
        file_name = input("Please enter the path to the " + name + " file ( " + default + "): ")

        if file_name == "":
            return default
        elif os.path.isfile(file_name):
            return file_name
        else:
            print("The file you specified does not exist")


def get_file_list(name):
    """Gets the path to a list of files from the user.

    :param name: The simple name of the files purpose.
    :return: A valid list of paths to the requested files.
    """

    print("Please enter a list of " + name + " files. Enter 'done' when finished.")
    files = List()

    while True:
        file_name = input("Entry " + str(len(files) + 1) + ": ")

        if file_name == "done":
            break
        elif os.path.isfile(file_name):
            files.append(file_name)
        else:
            print("The file you specified does not exist")

    return files


def run(tournaments, men_by_name, women_by_name, ranking_points, complete_tournaments):
    """Runs the static solution program.

    :return: None
    """

    for tournament in tournaments:
        # Do nothing if tournament is already complete.
        if complete_tournaments.find(tournament.name, False):
            continue

        # Collect all statistics for each round in the tournament.
        print("Now beginning processing for tournament " + tournament.name)
        male_round_file_names = get_file_list(tournament.name + " male round")
        female_round_file_names = get_file_list(tournament.name + " female round")

        for file_name in male_round_file_names:
            load_round_file(file_name, tournament.name, men_by_name, MALE)

        for file_name in female_round_file_names:
            load_round_file(file_name, tournament.name, women_by_name, FEMALE)

        # Sort each of the players by score.
        male_sorter = Sorter(lambda a, b: b.scores[tournament.name] - a.scores[tournament.name])
        female_sorter = Sorter(lambda a, b: b.scores[tournament.name] - a.scores[tournament.name])

        for player_name, profile in men_by_name:
            male_sorter.consume(profile)

        for player_name, profile in women_by_name:
            female_sorter.consume(profile)

        tournament.sorted_men = male_sorter.sort()
        tournament.sorted_women = female_sorter.sort()
        complete_tournaments.insert(tournament.name, True)

        # Print all players that have earned prizes.
        print(HEADER + "Results for tournament " + tournament.name + FOOTER)
        print("Men's Prizes")
        tally_and_print(tournament, tournament.sorted_men, ranking_points)

        print()
        print("Women's Prizes")
        tally_and_print(tournament, tournament.sorted_women, ranking_points)

        print("\n\n")

    print(HEADER + "CIRCUIT COMPLETE" + FOOTER)

    # Print all players ordered by ranking points.
    print_ranked_players(men_by_name, women_by_name)


def print_ranked_players(men_by_name, women_by_name):
    """Sort and print all ranked players.

    :param men_by_name: The male players to print.
    :param women_by_name: The female players to print.
    :return: None
    """
    # Sort all players by the overall circuit ranking points.
    male_sorter = Sorter(lambda a, b: b.ranking_points - a.ranking_points)
    female_sorter = Sorter(lambda a, b: b.ranking_points - a.ranking_points)

    for player_name, profile in men_by_name:
        male_sorter.consume(profile)

    for player_name, profile in women_by_name:
        female_sorter.consume(profile)

    sorted_men = male_sorter.sort()
    sorted_women = female_sorter.sort()

    print("Male ranking points:")

    for player in sorted_men:
        print(player.name + " " + str(player.ranking_points))

    print()
    print("Female ranking points:")

    for player in sorted_women:
        print(player.name + " " + str(player.ranking_points))


def load_circuit_progress(file_name, complete_tournaments):
    """Loads the circuit progress.

    :param file_name: The file name to load from.
    :param complete_tournaments: The hash table to load progress into.
    :return: None
    """
    if os.path.isfile(file_name):
        with open(file_name, "r") as file:
            for line in file:
                values = parse_csv_line(line)
                tournament_name = values[0]
                complete_tournaments.insert(tournament_name, True)


def load_player_progress(file_name, players_by_name):
    """Loads player progress from file.

    :param file_name: The file name to load from.
    :param players_by_name: The players hash table to load data into.
    :return: None
    """
    if os.path.isfile(file_name):
        with open(file_name, "r") as file:
            for line in file:
                values = parse_csv_line(line)
                player_name = values[0]
                ranking_points = float(values[1])
                player = players_by_name.find(player_name)
                if player is not None:
                    player.ranking_points = ranking_points
                else:
                    player = Player(player_name)
                    player.ranking_points = ranking_points
                    players_by_name.insert(player_name, player)


def persist_tournaments(file_name, complete_tournaments):
    """Persists all tournaments to file.

    :param file_name: The file name to persist to.
    :param complete_tournaments: The complete tournaments.
    :return: None
    """
    prepare_persist(file_name)
    with open(file_name, "a") as file:
        for name, _ in complete_tournaments:
            file.write(name + "\n")


def persist_players(file_name, players_by_name):
    """Persists all players to file.

    :param file_name: The file name to save to.
    :param players_by_name: The players to persist.
    :return: None
    """
    prepare_persist(file_name)
    with open(file_name, "a") as file:
        for _, player in players_by_name:
            file.write(player.name + "," + str(player.ranking_points) + "\n")


def persist(complete_tournaments_file, complete_tournaments,
            male_progress_file, men_by_name,
            female_progress_file, women_by_name):
    """Persists all completed tournaments state.

    :param complete_tournaments_file: The file name to save completed tournaments to.
    :param complete_tournaments: The tournaments completed.
    :param male_progress_file: The file name to save the male progress to.
    :param men_by_name: The male players.
    :param female_progress_file: The file name to save the female progress to.
    :param women_by_name: The female players.
    :return: None
    """
    print("Saving progress...")
    persist_tournaments(complete_tournaments_file, complete_tournaments)
    persist_players(male_progress_file, men_by_name)
    persist_players(female_progress_file, women_by_name)
    print("Save complete!")


def handle_interrupt(complete_tournaments, complete_tournaments_file,
                     female_progress_file, male_progress_file,
                     men_by_name, women_by_name):
    """Handles a keyboard interrupt on score input.

    :param complete_tournaments: The tournaments completed.
    :param complete_tournaments_file: The file name to save completed tournaments to.
    :param female_progress_file: The file name to save the female progress to.
    :param male_progress_file: The file name to save the male progress to.
    :param men_by_name: The male players.
    :param women_by_name: The female players.
    :return: True
    """
    print(HEADER + "CIRCUIT INTERRUPTED" + FOOTER)
    print_ranked_players(men_by_name, women_by_name)
    persist(complete_tournaments_file, complete_tournaments,
            male_progress_file, men_by_name,
            female_progress_file, women_by_name)
    return True


def main():
    """Runs the static solution.

    :return: None
    """
    print(HEADER + "STATIC SOLUTION" + FOOTER)

    # Load tournaments and players from file. Retaining progress saved.
    tournaments_file = get_file("tournaments", "../resources/tournaments.csv")
    male_players_file = get_file("male players", "../resources/male_players.csv")
    female_players_file = get_file("female players", "../resources/female_players.csv")
    ranking_points_file = get_file("ranking points", "../resources/ranking_points.csv")
    complete_tournaments_file = "../output/static/tournaments.csv"
    male_progress_file = "../output/static/men.csv"
    female_progress_file = "../output/static/women.csv"

    tournaments = load_tournaments_file(tournaments_file)
    men_by_name = load_players_file(male_players_file, len(tournaments))
    women_by_name = load_players_file(female_players_file, len(tournaments))
    ranking_points = load_ranking_points_file(ranking_points_file)
    complete_tournaments = HashTable()

    load_circuit_progress(complete_tournaments_file, complete_tournaments)
    load_player_progress(male_progress_file, men_by_name)
    load_player_progress(female_progress_file, women_by_name)
    done = False

    try:
        # Run the remaining tournaments from where we left off.
        print(HEADER + "STARTING THE CIRCUIT" + FOOTER)
        print("Press CTRL+C if you wish to pause and save the")
        print("circuit progress for another day.\n")
        run(tournaments, men_by_name, women_by_name, ranking_points, complete_tournaments)
    except (EOFError, KeyboardInterrupt):
        while not done:
            try:
                done = handle_interrupt(complete_tournaments, complete_tournaments_file,
                                        female_progress_file, male_progress_file,
                                        men_by_name, women_by_name)
            except KeyboardInterrupt:
                print("Retrying...")
                continue

        return

    persist(complete_tournaments_file, complete_tournaments,
            male_progress_file, men_by_name,
            female_progress_file, women_by_name)


if __name__ == '__main__':
    main()
