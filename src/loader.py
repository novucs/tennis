import os

import math

from circuit import Circuit
from config import TOURNAMENTS_FILE, RANKING_POINTS_FILE, OUTPUT, RESOURCES, get_winning_score, get_forfeit_score
from hash_table import HashTable
from linked_list import List
from match import Match, Track
from pipe_sort import Sorter
from player import SeasonStats, TournamentStats, Player, CircuitStats
from ranked_tree import Tree
from season import Season
from tournament import TournamentType, Tournament


def prepare_persist(filename):
    """Prepares a file for persistence, by deleting it and ensuring the
    directory and parent directories exist.

    :param filename: The file name to prepare for persistence.
    :return: The prepared filename.
    """
    # Delete file if already exists.
    if os.path.isfile(filename):
        os.remove(filename)

    # Ensure directory exists.
    directory_name = os.path.dirname(os.path.realpath(filename))
    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)

    return filename


def load_scores(text):
    """Loads all scores from formatted text "score1:score2:count".

    :param text: The text to parse.
    :return: The parsed scores.
    """
    scores = HashTable()

    if len(text) == 0:
        return scores

    for score in text.split(','):
        data = score.split(':')
        scores.insert((int(data[0]), int(data[1])), int(data[2]))

    return scores


def parse_bool(v):
    """Parses a boolean from text.

    :param v: The text to parse.
    :return: The boolean value of the text.
    """
    return v.lower() in ("yes", "true", "t", "1")


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
        elif character == '"':
            quotes = not quotes
        elif not quotes and character == ',':
            values.append(value.strip())
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


def load_round(file_name, track):
    """Loads a round from resources.

    :param file_name: The filename to load.
    :param track: The track of the round to load.
    :return: All matches loaded from file.
    """
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
            match = Match(track, player_a, score_a, player_b, score_b)
            matches.append(match)
    return matches


def load_track(tournament, gender, track_round):
    """Loads a track from file.

    :param tournament: The tournament this track is part of.
    :param gender: The gender of players on this track.
    :param track_round: The round the track is starting from.
    :return: The track loaded from file.
    """
    stats = HashTable()
    remaining = HashTable()
    sorter = Sorter(lambda a, b: b.round_achieved - a.round_achieved)

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
            opponent_scores = List()

            for score in csv[7:]:
                opponent_scores.append(int(score))

            # Create the players' tournament stats profile.
            season_stats: SeasonStats = tournament.season.get_stats(gender).find(player_name)
            tournament_stats = TournamentStats(season_stats.player, season_stats, round_achieved, multiplier, points,
                                               wins, losses, scores, opponent_scores)
            tournament_stats.season.tournament_stats.insert(tournament.type.name, tournament_stats)

            # Add this profile to the tournament players.
            stats.insert(player_name, tournament_stats)

            if not tournament.complete and track_round <= round_achieved:
                remaining.insert(player_name, tournament_stats)

            if tournament.complete or track_round > round_achieved:
                sorter.consume(tournament_stats)

    scoreboard = sorter.sort()

    if not tournament.complete:
        linked_scoreboard = List()
        for stats in scoreboard:
            linked_scoreboard.append(stats)
        scoreboard = linked_scoreboard

    winning_score = get_winning_score(gender)
    forfeit_score = get_forfeit_score(gender)

    previous_stats = None
    previous_season_scoreboard = None

    if tournament.previous is not None:
        previous_stats = tournament.previous.get_track(gender).stats
        previous_season_scoreboard = tournament.previous.season.get_scoreboard(gender)

    return Track(gender, track_round, stats, remaining, winning_score, forfeit_score, scoreboard, previous_stats,
                 previous_season_scoreboard)


def load_season_player_scoreboard(season_stats):
    """Loads and sorts a player scoreboard for a given season.

    :param season_stats: The seasons player statistics.
    :return: The sorted player statistics for the given season.
    """
    scoreboard = Tree(lambda a, b: b - a)
    for name, player_stats in season_stats:
        scoreboard.insert(player_stats.points, player_stats)
    return scoreboard


def load_season_player_stats(season_name, gender, circuit_players):
    """Loads all player statistics for a season from file.

    :param season_name: The name of the season to load.
    :param gender: The gender of the players to load.
    :param circuit_players: All players of this gender participating in the
                            circuit.
    :return: All the mapped player statistics for the season.
    """
    stats = HashTable()
    with open('%s/%s/%s.csv' % (OUTPUT, season_name, gender)) as the_file:
        for line in the_file:
            # Parse player stats.
            csv = parse_csv_line(line)
            player_name = csv[0]
            points = float(csv[1])
            wins = int(csv[2])
            losses = int(csv[3])
            scores = load_scores(csv[4])

            # Create the players' season stats profile.
            player: Player = circuit_players.find(player_name)
            season_stats = SeasonStats(player, player.stats, points, wins, losses, scores)
            player.stats.season_stats.insert(season_name, season_stats)

            # Add this profile to the season players.
            stats.insert(player_name, season_stats)
    return stats


def load_tournaments(season: Season):
    """Loads all tournaments progress for a season from file.

    :param season: The season to load the tournaments progress for.
    :return: The newly loaded tournaments.
    """
    tournaments = HashTable()

    with open('%s/%s/progress.csv' % (OUTPUT, season.name)) as the_file:
        for line in the_file:
            # Parse the seasons name and whether it's complete.
            csv = parse_csv_line(line)
            name = csv[0]
            complete = parse_bool(csv[1])
            men_round = int(csv[2])
            women_round = int(csv[3])
            tournament_type = season.circuit.tournament_types.find(name)

            # Find the previous seasons tournament, if there is any.
            previous = None

            if season.previous is not None:
                previous = season.previous.tournaments.find(name)

            # Create and load the tournament.
            tournament = Tournament(season, tournament_type, previous, complete)
            tournament.men_track = load_track(tournament, 'men', men_round)
            tournament.women_track = load_track(tournament, 'women', women_round)

            # Add newly created tournament to this season.
            tournaments.insert(tournament.type.name, tournament)

    return tournaments


def load_circuit_players(gender, players):
    """Loads all the players for a circuit from file.

    :param gender: The gender of the players to load.
    :param players: The players mapping collection to load into.
    """
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
            wins = int(csv[1])
            losses = int(csv[2])
            scores = load_scores(csv[3])

            # Create the players circuit stats profile.
            player = players.find(name)
            player.stats.wins = wins
            player.stats.losses = losses
            player.stats.scores = scores


def load_ranking_points(ranking_points):
    """Loads all ranking points from user configuration file in resources.

    :param ranking_points: The ranking points collection to load into.
    """
    with open(RANKING_POINTS_FILE, 'r') as the_file:
        header = True
        previous_lines = HashTable()
        previous_rank = float('inf')

        for line in the_file:
            if handle_duplicates(RANKING_POINTS_FILE, previous_lines, line):
                continue

            if header:
                header = False
                continue

            values = parse_csv_line(line)
            points = int(values[0])
            rank = math.ceil(math.log(int(values[1]), 2)) + 1
            # rank = int(values[1])
            # ranking_points.insert(rank, points)
            if rank != previous_rank:
                previous_rank = rank
                ranking_points.append_front(points)


def load_tournament_types(tournaments):
    """Loads all tournament types from user configuration file in resources.

    :param tournaments: The tournament types collection to load into.
    """
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
                    current_difficulty = float(difficulty)
                    prizes = HashTable()

            prizes.insert(place, prize)

    tournament = TournamentType(current_name, prizes, current_difficulty)
    tournaments.insert(current_name, tournament)


def load_circuit():
    """Loads a circuit from resources file, then loads all its progress via
    the previous sessions outputs.

    :return: the newly loaded circuit.
    """
    circuit = Circuit()

    load_tournament_types(circuit.tournament_types)
    load_ranking_points(circuit.ranking_points)
    load_circuit_players('men', circuit.men)
    load_circuit_players('women', circuit.women)

    circuit_progress_file = '%s/progress.csv' % OUTPUT

    if not os.path.isfile(circuit_progress_file):
        return circuit

    season = None

    with open(circuit_progress_file, 'r') as the_file:
        for line in the_file:
            csv = parse_csv_line(line)
            name = csv[0]
            complete = parse_bool(csv[1])

            previous = season

            men_stats = load_season_player_stats(name, 'men', circuit.men)
            women_stats = load_season_player_stats(name, 'women', circuit.women)
            men_scoreboard = load_season_player_scoreboard(men_stats)
            women_scoreboard = load_season_player_scoreboard(women_stats)

            season = Season(circuit, previous, name, complete, men_stats, women_stats, men_scoreboard, women_scoreboard)
            season.tournaments = load_tournaments(season)
            circuit.seasons.insert(name, season)
            circuit.ordered_seasons.append(season)
            circuit.current_season = season

    return circuit


def save_scores(scores):
    """Puts all scores into a formatted output.

    :return The formatted scores text, to be saved in CSV files.
    """
    target = ''
    for (our_score, opponent_score), count in scores:
        target += '%d:%d:%d,' % (our_score, opponent_score, count)
    target = target[:-1]
    return target


def save_track(tournament: Tournament, track: Track):
    """Saves all the track information for this session.

    :param tournament: The tournament the saved track belongs to.
    :param track: The track to save.
    """
    filename = '%s/%s/%s/%s.csv' % (OUTPUT, tournament.season.name, tournament.type.name, track.name)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, stats in track.stats:
            stats: TournamentStats = stats
            scores = save_scores(stats.scores)
            the_file.write('%s,%d,%.2f,%d,%d,%d,"%s"' % (name, stats.round_achieved, stats.multiplier, stats.points,
                                                         stats.wins, stats.losses, scores))
            for score in stats.opponent_scores:
                the_file.write(',%d' % score)

            the_file.write('\n')


def save_tournament(tournament: Tournament):
    """Saves progress for a tournament to the output files.

    :param tournament: The tournament to save.
    """
    save_track(tournament, tournament.men_track)
    save_track(tournament, tournament.women_track)


def save_season_player_stats(season: Season, gender, player_stats):
    """Saves all player statistics for a season.

    :param season: The season the player statistics belong to.
    :param gender: The gender of the players being saved.
    :param player_stats: All the player statistics to save.
    """
    filename = '%s/%s/%s.csv' % (OUTPUT, season.name, gender)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, stats in player_stats:
            stats: SeasonStats = stats
            scores = save_scores(stats.scores)
            the_file.write('%s,%d,%d,%d,"%s"\n' % (name, stats.points, stats.wins, stats.losses, scores))


def save_season(season: Season):
    """Saves all season progress to output files.

    :param season: The season to save the progress of.
    """
    filename = '%s/%s/progress.csv' % (OUTPUT, season.name)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, tournament in season.tournaments:
            men_round = tournament.men_track.round
            women_round = tournament.women_track.round
            the_file.write('%s,%s,%d,%d\n' % (name, tournament.complete, men_round, women_round))

    save_season_player_stats(season, 'men', season.men_stats)
    save_season_player_stats(season, 'women', season.women_stats)

    for name, tournament in season.tournaments:
        save_tournament(tournament)


def save_circuit_player_stats(gender, players):
    """Saves all player statistics for the entire circuit.

    :param gender: The gender of the players being saved.
    :param players: The players to save.
    """
    filename = '%s/%s.csv' % (OUTPUT, gender)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, player in players:
            stats: CircuitStats = player.stats
            scores = save_scores(stats.scores)
            the_file.write('%s,%d,%d,"%s"\n' % (name, stats.wins, stats.losses, scores))


def save_circuit(circuit: Circuit):
    """Saves all circuit progress to the output files.

    :param circuit: The circuit to save.
    """
    filename = '%s/progress.csv' % OUTPUT
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for season in circuit.ordered_seasons:
            the_file.write('%s,%s\n' % (season.name, season.complete))

    save_circuit_player_stats('men', circuit.men)
    save_circuit_player_stats('women', circuit.women)

    for name, season in circuit.seasons:
        save_season(season)
