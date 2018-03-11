import os

from circuit import Circuit
from config import TOURNAMENTS_FILE, RANKING_POINTS_FILE, OUTPUT, RESOURCES
from hash_table import HashTable
from linked_list import List
from match import Match
from player import SeasonStats, TournamentStats, Player, CircuitStats
from season import Season
from tournament import TournamentType, Tournament


def load_scores(text):
    scores = HashTable()
    for score in text.split(','):
        data = score.split(':')
        scores.insert((int(data[0]), int(data[1])), int(data[2]))
    return scores


def parse_csv_line(line):
    """Parses a CSV (comma separated values) line.

    :param line: The line to parse.
    :return: The array of values in this line.
    """

    if line == '':
        # return np.empty(0)
        return []

    values = List()
    value = ''
    quotes = False

    for character in line:
        if character == '\n':
            break
        elif character == "'":
            quotes = not quotes
        elif not quotes and character == ',':
            values.append(value)
            value = ''
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
        print('Skipping duplicate line found in ' + file_name)
        print(line)
        return True

    previous_lines[line] = True
    return False


def load_round(file_name, context):
    matches = List()
    with open(file_name, 'r') as the_file:
        header = True
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(file_name, previous_lines, line):
                continue

            if header:
                header = False
                continue

            csv = parse_csv_line(line)
            player_a = csv[0]
            score_a = int(csv[1])
            player_b = csv[2]
            score_b = int(csv[3])
            match = Match(context, player_a, score_a, player_b, score_b)
            matches.append(match)
    return matches


def load_tournament_types(tournaments):
    with open(TOURNAMENTS_FILE, 'r') as the_file:
        header = True
        first_entry = True
        current_name = ''
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
    with open(RANKING_POINTS_FILE, 'r') as the_file:
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
    load_circuit_players('men', circuit.men)
    load_circuit_players('women', circuit.women)

    circuit_progress_file = '%s/progress.csv' % OUTPUT

    if not os.path.isfile(circuit_progress_file):
        return circuit

    with open(circuit_progress_file, 'r') as the_file:
        for line in the_file:
            csv = parse_csv_line(line)
            name = csv[0]
            complete = bool(csv[1])

            previous = circuit.current_season
            season = Season(circuit, previous, name, complete)
            load_season(season)
            circuit.current_season = season
            circuit.seasons.insert(name, season)

    return circuit


def load_tournament_player_stats(tournament, gender, season_player_stats, tournament_player_stats,
                                 tournament_remaining_player_stats, active_round):
    with open('%s/%s/%s/%s.csv' % (OUTPUT, tournament.season.name, tournament.type.name, gender)) as the_file:
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
            season_stats: SeasonStats = season_player_stats.find(player_name)
            tournament_stats = TournamentStats(season_stats.player, season_stats, round_achieved, multiplier,
                                               points, wins, losses, scores)

            # Add this profile to the tournament players.
            tournament_player_stats.insert(player_name, tournament_stats)

            if not tournament.complete and active_round <= round_achieved:
                tournament_remaining_player_stats.insert(player_name, tournament_stats)


def load_season_player_stats(season, gender, circuit_players, season_player_stats):
    with open('%s/%s/%s.csv' % (OUTPUT, season.name, gender)) as the_file:
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
            season_stats = SeasonStats(circuit_stats.player, circuit_stats, points, wins, losses, scores)

            # Add this profile to the season players.
            season_player_stats.insert(player_name, season_stats)


def load_circuit_players(gender, players):
    player_data_file = '%s/%s.csv' % (RESOURCES, gender)
    player_stats_file = '%s/%s.csv' % (OUTPUT, gender)

    with open(player_data_file, 'r') as the_file:
        previous_lines = HashTable()

        for line in the_file:
            if handle_duplicates(player_data_file, previous_lines, line):
                continue

            values = parse_csv_line(line)
            name = values[0]
            player = Player(name)
            stats = CircuitStats(player)
            player.stats = stats
            players.insert(name, player)

    if not os.path.isfile(player_stats_file):
        return

    with open(player_stats_file, 'r') as the_file:
        for line in the_file:
            # Parse the players' circuit stats.
            csv = parse_csv_line(line)
            name = csv[0]
            wins = csv[1]
            losses = csv[2]
            scores = load_scores(csv[3])

            # Create the players circuit stats profile.
            player = players.find(name)
            player.stats.wins = wins
            player.stats.losses = losses
            player.stats.scores = scores


def load_season(season):
    load_season_player_stats(season, 'men', season.circuit.men, season.men_stats)
    load_season_player_stats(season, 'women', season.circuit.women, season.women_stats)

    # Load the progress of this season.
    with open('%s/%s/progress.csv' % (OUTPUT, season.name)) as the_file:
        for line in the_file:
            # Parse the seasons name and whether it's complete.
            csv = parse_csv_line(line)
            name = csv[0]
            complete = bool(csv[1])
            men_round = int(csv[2])
            women_round = int(csv[3])
            tournament_type = season.circuit.tournament_types.find(name)

            # Find the previous seasons tournament, if there is any.
            previous = None

            if season.previous is not None:
                previous = season.previous.tournaments.find(name)

            # Create and load the tournament.
            tournament = Tournament(tournament_type, season, previous, complete, men_round, women_round)
            load_tournament(tournament)

            # Add newly created tournament to this season.
            season.tournaments.insert(tournament.type.name, tournament)


def load_tournament(tournament):
    load_tournament_player_stats(tournament, 'men', tournament.season.men_stats, tournament.men_stats,
                                 tournament.remaining_men_stats, tournament.men_round)
    load_tournament_player_stats(tournament, 'women', tournament.season.women_stats, tournament.women_stats,
                                 tournament.remaining_women_stats, tournament.women_round)
