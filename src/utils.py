#!/usr/bin/env python

"""

General utilities used by both tennis player ranking solutions.

"""

import os

# import numpy as np
from hash_table import HashTable
from linked_list import List

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
    def __init__(self, season: SeasonStats, round_achieved, multiplier, points, wins, losses, scores):
        self.season = season
        self.round_achieved = round_achieved
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


class TournamentType:
    def __init__(self, name, prizes, difficulty):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty


class Circuit:
    def __init__(self, season=None, men=HashTable(), women=HashTable(), tournament_types=HashTable(),
                 ranking_points=HashTable()):
        self.season = season
        self.men = men
        self.women = women
        self.tournament_types = tournament_types
        self.ranking_points = ranking_points


class Player:
    def __init__(self, name, stats: CircuitStats = None):
        self.name = name
        self.stats = stats


class Season:
    def __init__(self, circuit, name, previous=None):
        self.circuit = circuit
        self.previous = previous
        self.name = name
        self.men_stats = HashTable()
        self.women_stats = HashTable()
        self.tournaments = HashTable()  # <tournament name, tournament>


class Tournament:
    def __init__(self, tournament_type, season, previous, complete):
        self.type = tournament_type
        self.season = season
        self.previous = previous
        self.complete = complete
        self.men_stats = HashTable()
        self.women_stats = HashTable()


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


#####################################################################
#                                                                   #
#                       PLAYER STATS LOADING                        #
#                                                                   #
#####################################################################

def load_scores(text):
    scores = HashTable()
    for score in text.split(","):
        data = score.split(":")
        scores.insert((int(data[0]), int(data[1])), int(data[2]))
    return scores


def load_tournament_player_stats(tournament, gender, season_player_stats, tournament_player_stats):
    with open("%s/%s/%s/%s.csv" % (OUTPUT, tournament.season.name, tournament.type.name, gender)) as the_file:
        for line in the_file:
            # Parse player stats.
            csv = parse_csv_line(line)
            player_name = csv[0]
            round_achieved = int(csv[1])
            multiplier = float(csv[2])
            points = float(csv[3])
            wins = int(csv[4])
            losses = int(csv[5])
            scores = load_scores(csv[6])

            # Create the players' tournament stats profile.
            season_stats = season_player_stats.find(player_name)
            tournament_stats = TournamentStats(season_stats, round_achieved, multiplier, points, wins, losses, scores)

            # Add this profile to the tournament players.
            tournament_player_stats.insert(player_name, tournament_stats)


def load_tournament(tournament: Tournament):
    load_tournament_player_stats(tournament, "men", tournament.season.men_stats, tournament.men_stats)
    load_tournament_player_stats(tournament, "women", tournament.season.women_stats, tournament.women_stats)


def load_season_player_stats(season, gender, circuit_players, season_player_stats):
    with open("%s/%s/%s.csv" % (OUTPUT, season.name, gender)) as the_file:
        for line in the_file:
            # Parse player stats.
            csv = parse_csv_line(line)
            player_name = csv[0]
            points = float(csv[1])
            wins = int(csv[2])
            losses = int(csv[3])
            scores = load_scores(csv[4])

            # Create the players' season stats profile.
            circuit_stats = circuit_players.find(player_name)
            season_stats = SeasonStats(circuit_stats, points, wins, losses, scores)

            # Add this profile to the season players.
            season_player_stats.insert(player_name, season_stats)


def load_season(season: Season):
    load_season_player_stats(season, "men", season.circuit.men, season.men_stats)
    load_season_player_stats(season, "women", season.circuit.women, season.women_stats)

    # Load the progress of this season.
    with open("%s/%s/progress.csv" % (OUTPUT, season.name)) as the_file:
        for line in the_file:
            # Parse the seasons name and whether it's complete.
            csv = parse_csv_line(line)
            name = csv[0]
            complete = bool(csv[1])
            tournament_type = season.circuit.tournament_types.find(name)

            # Find the previous seasons tournament, if there is any.
            previous = None

            if season.previous is not None:
                previous = season.previous.tournaments.find(name)

            # Create and load the tournament.
            tournament = Tournament(tournament_type, season, previous, complete)
            load_tournament(tournament)

            # Add newly created tournament to this season.
            season.tournaments.insert(tournament.type.name, tournament)


def load_circuit_players(gender, players: HashTable):
    players_file_name = "%s/%s.csv" % (RESOURCES, gender)

    with open(players_file_name, "r") as the_file:
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(players_file_name, previous_lines, line):
                continue

            values = parse_csv_line(line)
            name = values[0]
            player = Player(name)
            players.insert(name, player)

    with open("%s/%s.csv" % (OUTPUT, gender), "r") as the_file:
        for line in the_file:
            # Parse the players' circuit stats.
            csv = parse_csv_line(line)
            name = csv[0]
            wins = csv[1]
            losses = csv[2]
            scores = load_scores(csv[3])

            # Create the players circuit stats profile.
            stats = CircuitStats(wins, losses, scores)
            player = players.find(name)
            player.stats = stats


def load_tournament_types(tournaments):
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
                    tournament = TournamentType(current_name, prizes, current_difficulty)
                    tournaments.insert(current_name, tournament)
                    current_name = name
                    prizes = HashTable()

            prizes.insert(place, prize)

    tournament = TournamentType(current_name, prizes, current_difficulty)
    tournaments.insert(current_name, tournament)


def load_ranking_points(ranking_points):
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


def load_circuit():
    circuit = Circuit()

    load_tournament_types(circuit.tournament_types)
    load_ranking_points(circuit.ranking_points)
    load_circuit_players("men", circuit.men)
    load_circuit_players("women", circuit.women)

    with open("%s/progress.csv" % OUTPUT, "r") as the_file:
        for line in the_file:
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
        for name, profile in tournament.men_stats:
            the_file.write("%s,%d\n" % (name, profile.temp.multiplier))

    with open(women_file, "rw") as the_file:
        for name, profile in tournament.women_stats:
            the_file.write("%s,%d\n" % (name, profile.temp.multiplier))

    with open(progress_file, "rw") as the_file:
        the_file.write("%s,%s\n" % (tournament.round.name, tournament.complete))

    with open(stats_file, "rw") as the_file:
        for name, profile in tournament.men_stats:
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
