#!/usr/bin/env python

"""

General utilities used by both tennis player ranking solutions.

"""

import os
import sys

# import numpy as np
from hash_table import HashTable
from linked_list import List
from main import Tournament
from player import Player

# Define the two possible genders.
MALE = False
FEMALE = True

# Define pretty banners.
HEADER = "\n" + "-" * 40 + "\n\n"
FOOTER = "\n\n" + "-" * 40 + "\n"

OUTPUT = "../output"
RESOURCES = "../resources"
TOURNAMENTS_FILE = "%s/tournaments.csv" % RESOURCES
MEN_FILE = "%s/stats.csv" % RESOURCES
WOMEN_FILE = "%s/women.csv" % RESOURCES
RANKING_POINTS_FILE = "%s/ranking_points.csv" % RESOURCES

TOURNAMENT_COUNT = 4


def parse_csv_line(line):
    """Parses a CSV (comma separated values) line.

    :param line: The line to parse.
    :return: The array of values in this line.
    """

    if line == "":
        # return np.empty(0)
        return []

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


def load_tournaments(tournaments):
    with open(TOURNAMENTS_FILE, "r") as the_file:
        header = True
        first_entry = True
        current_name = ""
        current_difficulty = 0
        prizes = HashTable()
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(TOURNAMENTS_FILE, previous_lines, line):
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
                    tournament = Tournament(current_name, prizes, current_difficulty)
                    tournaments.insert(current_name, tournament)
                    current_name = name
                    prizes = HashTable()

            prizes.insert(place, prize)

    tournament = Tournament(current_name, prizes, current_difficulty)
    tournaments.insert(current_name, tournament)


def load_players(file_name, players):
    """Loads players from file.

    :param players: The collection to load into.
    :param file_name: The name of the player names file.
    """

    with open(file_name, "r") as the_file:
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(file_name, previous_lines, line):
                continue

            values = parse_csv_line(line)
            name = values[0]
            player = Player(name)
            players.insert(name, player)


def load_men(men):
    load_players(MEN_FILE, men)


def load_women(women):
    load_players(WOMEN_FILE, women)


def load_ranking_points(ranking_points):
    """Loads the ranking points file.

    :param ranking_points: The collection to load into.
    :param file_name: The name of the ranking points file.
    """

    with open(RANKING_POINTS_FILE, "r") as the_file:
        header = True
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(RANKING_POINTS_FILE, previous_lines, line):
                continue

            if header:
                header = False
                continue

            values = parse_csv_line(line)
            points = int(values[0])
            rank = int(values[1])
            ranking_points.insert(rank, points)


class CircuitStats:
    def __init__(self, wins, losses, scores, season_stats=HashTable()):
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>
        self.season_stats = season_stats  # <season name, season stats>


class SeasonStats:
    def __init__(self, circuit: CircuitStats, points, wins, losses, scores, tournament_stats=HashTable()):
        self.circuit = circuit
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>
        self.tournament_stats = tournament_stats  # <tournament name, tournament stats>


class TournamentStats:
    def __init__(self, season: SeasonStats, round, multiplier, points, wins, losses, scores):
        self.season = season
        self.round = round
        self.multiplier = multiplier
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>

    def add_points(self, points):
        self.points += points
        self.season.points += points

    def round(self, our_score, opponent_score):
        # Increment number of times player has had this score.
        count = self.scores.find((our_score, opponent_score), 0) + 1
        self.scores.insert((our_score, opponent_score), count)

        # Increment number of wins or losses depending on game outcome.
        if our_score > opponent_score:
            self.wins += 1
            self.season.wins += 1
            self.season.circuit.wins += 1
        else:
            self.losses += 1
            self.season.losses += 1
            self.season.circuit.losses += 1


class Circuit:
    def __init__(self):
        self.season = None
        self.men = HashTable()
        self.women = HashTable()
        self.ranking_points = HashTable()


class Player:
    def __init__(self, name: str, stats: CircuitStats):
        self.name = name
        self.stats = stats


class Season:
    def __init__(self, circuit: Circuit, name, previous=None):
        self.circuit = circuit
        self.previous = previous
        self.name = name
        self.men = HashTable()
        self.women = HashTable()
        self.tournaments = HashTable()  # <tournament name, tournament>


class Tournament:
    def __init__(self, season: Season, previous, name, complete):
        self.previous = previous
        self.season = season
        self.name = name
        self.complete = complete
        self.men = HashTable()
        self.women = HashTable()


def load_scores(text):
    scores = HashTable()
    for score in text.split(","):
        data = score.split(":")
        scores.insert((int(data[0]), int(data[1])), int(data[2]))
    return scores


def load_stats(season):
    stats_file = "%s/%s/stats.csv" % (output_folder, season)

    with open(stats_file, "r") as the_file:
        for line in the_file:
            # player name, wins, losses, scores (won:lost:count,...)
            values = parse_csv_line(line)
            player_name = values[0]
            points = int(values[1])
            wins = int(values[2])
            losses = int(values[3])
            scores = load_scores(values[4])
            SeasonStats()


def load_seasons(circuit: Circuit):
    progress_file = "%s/progress.csv" % OUTPUT

    # Create a new season if none found.
    if not os.path.isfile(progress_file):
        print("No seasons found.")
        print("Enter a new season name: ")
        name = sys.stdin.readline()
        return Season(name)

    complete = True
    name = None
    previous_name = None

    with open(progress_file, "r") as the_file:
        for line in the_file:
            values = parse_csv_line(line)
            complete = bool(values[1])
            name = values[0]
            if not complete:
                break
            previous_name = name

    if previous_name is not None:
        previous = Season(previous_name)

    if complete:
        print("Previous season is complete.")
        print("Enter a new season name: ")
        name = sys.stdin.readline()
        # TODO: Load previous season.
        return Season(name)


#####################################################################
#                                                                   #
#                       PLAYER STATS LOADING                        #
#                                                                   #
#####################################################################

def load_tournament(tournament: Tournament):
    # Load the men stats.
    with open("%s/%s/%s/men.csv" % (OUTPUT, tournament.season.name, tournament.name)) as stats_file:
        for line in stats_file:
            csv = parse_csv_line(line)
            tournament.men = TournamentStats(season=tournament.season.men.find(csv[0]), round=int(csv[1]),
                                             multiplier=float(csv[2]), points=float(csv[3]), wins=int(csv[4]),
                                             losses=int(csv[5]), scores=load_scores(csv[6]))

    # Load the women stats.
    with open("%s/%s/%s/women.csv" % (OUTPUT, tournament.season.name, tournament.name)) as stats_file:
        for line in stats_file:
            csv = parse_csv_line(line)
            tournament.men = TournamentStats(season=tournament.season.women.find(csv[0]), round=int(csv[1]),
                                             multiplier=float(csv[2]), points=float(csv[3]), wins=int(csv[4]),
                                             losses=int(csv[5]), scores=load_scores(csv[6]))


def load_season(season: Season):
    # Load the men stats.
    with open("%s/%s/men.csv" % (OUTPUT, season.name)) as stats_file:
        for line in stats_file:
            csv = parse_csv_line(line)
            season.men = SeasonStats(circuit=season.circuit.men.find(csv[0]), points=float(csv[1]),
                                     wins=int(csv[2]), losses=int(csv[3]), scores=load_scores(csv[4]))

    # Load the women stats.
    with open("%s/%s/women.csv" % (OUTPUT, season.name)) as stats_file:
        for line in stats_file:
            csv = parse_csv_line(line)
            season.women = SeasonStats(circuit=season.circuit.women.find(csv[0]), points=float(csv[1]),
                                       wins=int(csv[2]), losses=int(csv[3]), scores=load_scores(csv[4]))

    # Load the progress of this season.
    with open("%s/%s/progress.csv" % (OUTPUT, season.name)) as tournaments_file:
        for line in tournaments_file:
            csv = parse_csv_line(line)
            tournament = Tournament(season=season, name=csv[0], complete=bool(csv[1]))
            load_tournament(tournament)
            season.tournaments.insert(tournament.name, tournament)


def load_circuit_stats(gender, players: HashTable):
    with open("%s/%s.csv" % (OUTPUT, gender), "r") as stats_file:
        for line in stats_file:
            csv = parse_csv_line(line)

            # Load player name.
            name = csv[0]

            # Load player stats.
            wins = csv[1]
            losses = csv[2]
            scores = load_scores(csv[3])
            stats = CircuitStats(wins, losses, scores)

            # Create and add newly loaded player.
            player = Player(name, stats)
            players.insert(player.name, player)


def load_circuit():
    circuit = Circuit()

    load_circuit_stats("men", circuit.men)
    load_circuit_stats("women", circuit.women)

    with open("%s/progress.csv" % OUTPUT, "r") as seasons_file:
        for line in seasons_file:
            name = parse_csv_line(line)[0]
            previous = circuit.season
            season = Season(circuit, name, previous)
            load_season(season)
            circuit.season = season

    return circuit


def save_tournament(tournament: Tournament):
    tournament_folder = "../output/%s/%s/" % (tournament.season.name, tournament.name)
    men_file = prepare_persist(tournament_folder + "men.csv")
    women_file = prepare_persist(tournament_folder + "women.csv")
    progress_file = prepare_persist(tournament_folder + "progress.csv")
    stats_file = prepare_persist(tournament_folder + "stats.csv")

    with open(men_file, "rw") as the_file:
        for name, profile in tournament.men:
            the_file.write("%s,%d\n" % (name, profile.temp.multiplier))

    with open(women_file, "rw") as the_file:
        for name, profile in tournament.women:
            the_file.write("%s,%d\n" % (name, profile.temp.multiplier))

    with open(progress_file, "rw") as the_file:
        the_file.write("%s,%s\n" % (tournament.round.name, tournament.complete))

    with open(stats_file, "rw") as the_file:
        for name, profile in tournament.men:
            stats = tournament.stats.find(name)

            the_file.write(
                "%s,%d,%d,%d,\"%s\"\n" % (name, profile.temp.round, profile.temp.wins, profile.temp.losses, ""))


def prepare_persist(file_name):
    # Delete file if already exists.
    if os.path.isfile(file_name):
        os.remove(file_name)

    # Ensure directory exists.
    directory_name = os.path.dirname(os.path.realpath(file_name))
    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)

    return file_name
