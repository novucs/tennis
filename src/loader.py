import os

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
    # Delete file if already exists.
    if os.path.isfile(filename):
        os.remove(filename)

    # Ensure directory exists.
    directory_name = os.path.dirname(os.path.realpath(filename))
    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)

    return filename


def load_scores(text):
    scores = HashTable()

    if len(text) == 0:
        return scores

    for score in text.split(','):
        data = score.split(':')
        scores.insert((int(data[0]), int(data[1])), int(data[2]))

    return scores


def parse_bool(v):
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


def load_track(tournament, gender, track_round):
    stats = HashTable()
    remaining = HashTable()
    scoreboard = Tree()

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
            season_stats: SeasonStats = tournament.season.get_stats(gender).find(player_name)
            tournament_stats = TournamentStats(season_stats.player, season_stats, round_achieved, multiplier, points,
                                               wins, losses, scores)

            # Add this profile to the tournament players.
            stats.insert(player_name, tournament_stats)

            if not tournament.complete and track_round <= round_achieved:
                remaining.insert(player_name, tournament_stats)

            if tournament.complete or track_round > round_achieved:
                scoreboard.insert(points, tournament_stats)

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
    sorter = Sorter(lambda a, b: a.points - b.points)
    for name, player_stats in season_stats:
        sorter.consume(player_stats)
    return sorter.sort()


def load_season_player_stats(season_name, gender, circuit_players):
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

            # Add this profile to the season players.
            stats.insert(player_name, season_stats)
    return stats


def load_tournaments(season: Season):
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
            complete = parse_bool(csv[1])

            previous = circuit.current_season

            men_stats = load_season_player_stats(name, 'men', circuit.men)
            women_stats = load_season_player_stats(name, 'women', circuit.women)
            men_scoreboard = load_season_player_scoreboard(men_stats)
            women_scoreboard = load_season_player_scoreboard(women_stats)

            season = Season(circuit, previous, name, complete, men_stats, women_stats, men_scoreboard, women_scoreboard)
            season.tournaments = load_tournaments(season)

            # TODO: Create and sort season scoreboard.
            circuit.current_season = season
            circuit.seasons.insert(name, season)

    return circuit


def save_scores(scores):
    target = ''
    for (our_score, opponent_score), count in scores:
        target += '%d:%d:%d,' % (our_score, opponent_score, count)
    target = target[:-1]
    return target


def save_track(tournament: Tournament, track: Track):
    filename = '%s/%s/%s/%s.csv' % (OUTPUT, tournament.season.name, tournament.type.name, track.name)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, stats in track.stats:
            stats: TournamentStats = stats
            scores = save_scores(stats.scores)
            the_file.write('%s,%d,%.2f,%d,%d,%d,"%s"\n' % (name, stats.round_achieved, stats.multiplier, stats.points,
                                                           stats.wins, stats.losses, scores))


def save_tournament(tournament: Tournament):
    save_track(tournament, tournament.men_track)
    save_track(tournament, tournament.women_track)


def save_season_player_stats(season: Season, gender, player_stats):
    filename = '%s/%s/%s.csv' % (OUTPUT, season.name, gender)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, stats in player_stats:
            stats: SeasonStats = stats
            scores = save_scores(stats.scores)
            the_file.write('%s,%d,%d,%d,"%s"\n' % (name, stats.points, stats.wins, stats.losses, scores))


def save_season(season: Season):
    filename = '%s/%s/progress.csv' % (OUTPUT, season.name)
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        # name = csv[0]
        # complete = parse_bool(csv[1])
        # men_round = int(csv[2])
        # women_round = int(csv[3])
        for name, tournament in season.tournaments:
            men_round = tournament.men_track.round
            women_round = tournament.women_track.round
            the_file.write('%s,%s,%d,%d\n' % (name, tournament.complete, men_round, women_round))

    save_season_player_stats(season, 'men', season.men_stats)
    save_season_player_stats(season, 'women', season.women_stats)

    for name, tournament in season.tournaments:
        save_tournament(tournament)


def save_circuit(circuit: Circuit):
    filename = '%s/progress.csv' % OUTPUT
    prepare_persist(filename)
    with open(filename, 'a') as the_file:
        for name, season in circuit.seasons:
            the_file.write('%s,%s\n' % (name, season.complete))

    for name, season in circuit.seasons:
        save_season(season)
