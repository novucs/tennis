import math
import sys

from utils import *

MALE = False
FEMALE = True

FILE = True
TYPED = False

MAX_PLAYERS = 32

MAX_ROUNDS = math.log(MAX_PLAYERS, 2)

MEN_WIN_SCORE = 3
MEN_FORFEIT_SCORE = 2

WOMEN_WIN_SCORE = 2
WOMEN_FORFEIT_SCORE = 1

TOURNAMENT_COUNT = 4

HELP_MESSAGE = '''
=== TENNIS HELP ===

> help
Displays all commands.

> quit
Quits the program.

> start <tournament>
Starts the next tournament.

> stats
Shows the player with most wins and player with most losses.

> stats <player> score <score> season <season> [tournament <tournament>]
Gets number of times a player got a specific score in a tournament or season.

> stats <player> wins [season [tournament <tournament>]]
Gets total number of times a player won in a tournament, season, or overall.

> stats <player> losses [season [tournament <tournament>]]
Gets total number of times a player lost in a tournament, season, or overall.

===================
'''

OUTPUT = "../output"
RESOURCES = "../resources"
TOURNAMENTS_FILE = "%s/tournaments.csv" % RESOURCES
MEN_FILE = "%s/stats.csv" % RESOURCES
WOMEN_FILE = "%s/women.csv" % RESOURCES
RANKING_POINTS_FILE = "%s/ranking_points.csv" % RESOURCES


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


def load_tournament_player_stats(tournament, gender, season_player_stats, tournament_player_stats,
                                 tournament_remaining_player_stats, active_round):
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
            season_stats: SeasonStats = season_player_stats.find(player_name)
            tournament_stats = TournamentStats(season_stats.player, season_stats, round_achieved, multiplier,
                                               points, wins, losses, scores)

            # Add this profile to the tournament players.
            tournament_player_stats.insert(player_name, tournament_stats)

            if not tournament.complete and active_round <= round_achieved:
                tournament_remaining_player_stats.insert(player_name, tournament_stats)


def load_tournament(tournament):
    load_tournament_player_stats(tournament, "men", tournament.season.men_stats, tournament.men_stats,
                                 tournament.remaining_men_stats, tournament.men_round)
    load_tournament_player_stats(tournament, "women", tournament.season.women_stats, tournament.women_stats,
                                 tournament.remaining_women_stats, tournament.women_round)


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
            season_stats = SeasonStats(circuit_stats.player, circuit_stats, points, wins, losses, scores)

            # Add this profile to the season players.
            season_player_stats.insert(player_name, season_stats)


def load_season(season):
    load_season_player_stats(season, "men", season.circuit.men, season.men_stats)
    load_season_player_stats(season, "women", season.circuit.women, season.women_stats)

    # Load the progress of this season.
    with open("%s/%s/progress.csv" % (OUTPUT, season.name)) as the_file:
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


def load_circuit_players(gender, players):
    player_data_file = "%s/%s.csv" % (RESOURCES, gender)
    player_stats_file = "%s/%s.csv" % (OUTPUT, gender)

    with open(player_data_file, "r") as the_file:
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

    with open(player_stats_file, "r") as the_file:
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

    circuit_progress_file = "%s/progress.csv" % OUTPUT

    if not os.path.isfile(circuit_progress_file):
        return circuit

    with open(circuit_progress_file, "r") as the_file:
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


def load_round(file_name, context):
    matches = List()
    with open(file_name, "r") as the_file:
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


def next_string(message, default=None):
    """Fetches a string from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input string.
    """

    while True:
        if default is None:
            user_input = input(message + ": ")
        else:
            user_input = input(message + " (" + default + "): ")

        if user_input == "":
            return default
        else:
            return user_input


def next_bool(message, default=None):
    """Fetches a boolean from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input boolean.
    """

    while True:
        default_text = "Y/n" if default else "y/N"
        user_input = next_string(message, default_text)

        if user_input == default_text:
            return default

        parsed = user_input.lower()

        if parsed.startswith("y") or parsed.startswith("t"):
            return True
        elif parsed.startswith("n") or parsed.startswith("f"):
            return False


def next_int(message, default=None):
    """Fetches an int from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input int.
    """

    while True:
        default_text = None if default is None else str(default)
        user_input = next_string(message, default_text)

        if user_input is not None:
            try:
                parsed = int(user_input)
                return parsed
            except ValueError:
                pass


def next_float(message, default=None):
    """Fetches a float from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input float.
    """

    while True:
        default_text = None if default is None else str(default)
        user_input = next_string(message, default_text)

        if user_input is not None:
            try:
                parsed = float(user_input)
                return parsed
            except ValueError:
                pass


def next_gender(message, default=None):
    """Fetches a gender from user input.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user submitted gender.
    """

    while True:
        default_text = "m/F" if default else "M/f"
        user_input = next_string(message, default_text)

        if user_input is not None:
            parsed = user_input.lower()

            if parsed.startswith("f"):
                return FEMALE
            elif parsed.startswith("m"):
                return MALE


def next_input_type(message, default: bool = None):
    while True:
        default_text = "file/TYPED" if default else "FILE/typed"
        user_input = next_string(message, default_text)

        if user_input is not None:
            parsed = user_input.lower()

            if parsed.startswith("f"):
                return FILE
            elif parsed.startswith("t"):
                return TYPED


class CircuitStats:
    def __init__(self, player, wins=0, losses=0, scores=HashTable(), season_stats=HashTable()):
        self.player = player
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>
        self.season_stats = season_stats  # <season name, season stats>


class SeasonStats:
    def __init__(self, player, circuit: CircuitStats, points=0.0, wins=0, losses=0, scores=HashTable(),
                 tournament_stats=HashTable()):
        self.player = player
        self.circuit = circuit
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>
        self.tournament_stats = tournament_stats  # <tournament name, tournament stats>


class TournamentStats:
    def __init__(self, player, season: SeasonStats, round_achieved=1, multiplier=1.0, points=0.0, wins=0, losses=0,
                 scores=HashTable()):
        self.player = player
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

    def add_score(self, opponent_score, our_score):
        # Increment number of times player has had this score.
        count = self.scores.find((our_score, opponent_score), 0) + 1
        self.scores.insert((our_score, opponent_score), count)

    def win(self):
        self.wins += 1
        self.season.wins += 1
        self.season.circuit.wins += 1

    def loss(self):
        self.losses += 1
        self.season.losses += 1
        self.season.circuit.losses += 1


class TournamentType:
    def __init__(self, name: str, prizes: HashTable, difficulty: float):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty


class Circuit:
    def __init__(self, current_season=None, seasons=HashTable(), men=HashTable(), women=HashTable(),
                 tournament_types=HashTable(), ranking_points=HashTable()):
        self.running = True
        self.command_executor = CommandExecutor(self)
        self.current_season = current_season
        self.seasons = seasons
        self.men = men
        self.women = women
        self.tournament_types = tournament_types
        self.ranking_points = ranking_points

    def run(self):
        print("Type 'help' to see all commands.")

        while self.running:
            print("> ", end='', flush=True)
            command = sys.stdin.readline()[:-1]
            self.command_executor.execute(command)

    def quit(self):
        self.running = False

    def next_incomplete_season(self):
        if self.current_season is not None and not self.current_season.complete:
            return self.current_season

        while True:
            season_name = next_string("Enter a new season name")

            if season_name is None:
                continue

            if self.seasons.find(season_name) is not None:
                print("A season by that name already exists")
                continue

            previous_season = self.current_season
            men_season_stats = self.create_season_stats(self.men)
            women_season_stats = self.create_season_stats(self.women)
            season = Season(self, previous_season, season_name, False, men_season_stats, women_season_stats)

            self.current_season = season
            self.seasons.insert(season_name.lower(), season)
            return self.current_season

    @staticmethod
    def create_season_stats(profiles):
        target = HashTable()

        for player_name, player_profile in profiles:
            circuit_stats = player_profile.stats
            season_stats = SeasonStats(player_profile, circuit_stats)
            target.insert(player_name, season_stats)

        return target


class Player:
    def __init__(self, name, stats: CircuitStats = None):
        self.name = name
        self.stats = stats


class Season:
    def __init__(self, circuit: Circuit, previous, name: str, complete: bool, men_stats=HashTable(),
                 women_stats=HashTable(), tournaments=HashTable()):
        self.circuit = circuit
        self.previous = previous
        self.name = name
        self.complete = complete
        self.men_stats = men_stats
        self.women_stats = women_stats
        self.tournaments = tournaments  # <tournament name, tournament>

    def start(self, tournament_name):
        tournament: Tournament = self.tournaments.find(tournament_name)

        if tournament is None or tournament.complete:
            print("Starting a new tournament")

            # Check tournament type is valid.
            tournament_type = self.circuit.tournament_types.find(tournament_name)

            if tournament_type is None:
                print("A tournament by the name %s does not exist" % tournament_name)
                return

            # Create the tournament.
            previous_tournament = None

            if self.previous is not None:
                previous_tournament = self.previous.tournaments.find(tournament_name)

            men_tournament_stats = self.create_tournament_stats(self.circuit.men, self.men_stats)
            women_tournament_stats = self.create_tournament_stats(self.circuit.women, self.women_stats)

            tournament = Tournament(tournament_type, self, previous_tournament, False, 1, 1,
                                    men_tournament_stats, women_tournament_stats)

            self.tournaments.insert(tournament_name, tournament)
        else:
            print("Continuing tournament from saved progress")

        tournament.run()

    @staticmethod
    def create_tournament_stats(profiles, stats):
        target = HashTable()

        for player_name, player_profile in profiles:
            season_stats = stats.find(player_name)
            tournament_stats = TournamentStats(player_profile, season_stats)
            target.insert(player_name, tournament_stats)

        return target


class TournamentTrackContext:
    def __init__(self, name, track_round, stats, remaining, winning_score, forfeit_score):
        self.name = name
        self.round = track_round
        self.stats = stats
        self.remaining = remaining
        self.winning_score = winning_score
        self.forfeit_score = forfeit_score


class Tournament:
    def __init__(self, tournament_type: TournamentType, season, previous, complete, men_round, women_round,
                 men_stats=HashTable(), women_stats=HashTable()):
        self.type = tournament_type
        self.season = season
        self.previous = previous
        self.complete = complete
        self.men_round = men_round
        self.women_round = women_round
        self.men_stats = men_stats
        self.women_stats = women_stats
        self.remaining_men_stats = men_stats.clone()
        self.remaining_women_stats = women_stats.clone()

    def run(self):
        running = True

        while running:
            gender = next_gender("Select the track to play for the next round")
            if gender == MALE:
                context = TournamentTrackContext("men", self.men_round, self.men_stats, self.remaining_men_stats,
                                                 MEN_WIN_SCORE, MEN_FORFEIT_SCORE)
                self.play_track(context)
                self.men_round = context.round
                self.men_stats = context.stats
                self.remaining_men_stats = context.remaining
            else:
                context = TournamentTrackContext("women", self.women_round, self.women_stats,
                                                 self.remaining_women_stats, WOMEN_WIN_SCORE, WOMEN_FORFEIT_SCORE)
                self.play_track(context)
                self.women_round = context.round
                self.women_stats = context.stats
                self.remaining_women_stats = context.remaining
            running = next_bool("Would you like to start the next round?", True)

    def play_track(self, context):
        if context.round > MAX_ROUNDS:
            print("This track is already complete")
            return

        print("Playing the %s's track" % context.name)
        input_type = next_input_type("How should data be entered?")
        winners = HashTable()
        winner = None
        matches = List()

        if input_type == FILE:
            # Get the file to load the round data from.
            default_round_file = "../resources/%s/%s/%s/round_%d.csv" % \
                                 (self.season.name, self.type.name.lower(), context.name, context.round)
            round_file = next_string("Enter file for round %d" % context.round, default_round_file)
            matches = load_round(round_file, context)
        else:
            match_count = int(math.pow(2, MAX_ROUNDS - context.round))

            for i in range(0, match_count):
                match = Match(context)
                matches.append(match)

        # Run each match.
        for match in matches:
            # Find the winner and add them to the next batch.
            winner, winner_score, loser, loser_score = match.run(context.winning_score, context.remaining)
            winners.insert(winner.player.name, winner)

            # Update the winner profile.
            winner.win()
            winner.add_score(winner_score, loser_score)

            # Update the loser profile.
            loser.loss()
            loser.add_score(loser_score, winner_score)

        if context.round == MAX_ROUNDS:
            print("Tournament %s successfully complete for the men's track" % self.type.name)
            print("Winner: %s" % winner.player.name)
            context.round += 1
            return

        print("Winners for round %d:" % context.round)

        for name, stats in winners:
            print("- %s" % name)

        context.remaining = winners
        context.round += 1


class Match:
    def __init__(self, context, player_a=None, score_a=None, player_b=None, score_b=None):
        self.context = context
        self.player_name_a = player_a
        self.score_a = score_a
        self.player_name_b = player_b
        self.score_b = score_b

    def run(self, winning_score, player_stats: HashTable):
        if self.player_name_a is not None:
            # Validate players, both must still be able to play this round.
            self.player_name_a = self.validate_player(self.player_name_a, player_stats)
            # Prevent players playing any more matches this round, and load their
            # relevant tournament stats for returning later.
            player_stats_a = player_stats.delete(self.player_name_a)
            self.player_name_b = self.validate_player(self.player_name_b, player_stats)
            player_stats_b = player_stats.delete(self.player_name_b)
        else:
            self.player_name_a = next_string("Enter player A")
            self.player_name_a = self.validate_player(self.player_name_a, player_stats)
            player_stats_a = player_stats.delete(self.player_name_a)
            self.score_a = next_int("Enter score A")

            self.player_name_b = next_string("Enter player B")
            self.player_name_b = self.validate_player(self.player_name_b, player_stats)
            player_stats_b = player_stats.delete(self.player_name_b)
            self.score_b = next_int("Enter Score B")

        # Validate scores:
        # - Only one may be a winner.
        # - Both must be no bigger than the winning score.
        # - Both must be no smaller than zero.
        self.validate_scores(winning_score)

        # Find and return the winner and loser with their scores.
        if self.score_a > self.score_b:
            return player_stats_a, self.score_a, player_stats_b, self.score_b
        else:
            return player_stats_b, self.score_b, player_stats_a, self.score_a

    def validate_scores(self, winning_score):
        while True:
            self.score_a = self.validate_score(self.score_a, winning_score)
            self.score_b = self.validate_score(self.score_b, winning_score)

            if self.score_a == winning_score and self.score_b == winning_score:
                print("Both players cannot be winners")
                self.next_scores(winning_score)
                continue

            if self.score_a == winning_score or self.score_b == winning_score:
                return

            injured = next_bool("Incomplete scores. Has a player been injured?", True)

            if injured:
                player_a_injured = next_bool("Was %s injured?" % self.player_name_a, True)

                if player_a_injured:
                    print("%s was injured and has been withdrawn from the tournament" % self.player_name_a)
                    self.score_a = self.context.forfeit_score
                    self.score_b = self.context.winning_score
                else:
                    print("%s was injured and has been withdrawn from the tournament" % self.player_name_b)
                    self.score_a = self.context.winning_score
                    self.score_b = self.context.forfeit_score

                return

            print("Please re-enter the scores so they are complete")
            self.next_scores(winning_score)

    def next_scores(self, winning_score):
        self.score_a = self.next_score(self.player_name_a)
        self.score_a = self.validate_score(self.score_a, winning_score)
        self.score_b = self.next_score(self.player_name_b)
        self.score_b = self.validate_score(self.score_b, winning_score)

    @staticmethod
    def next_score(player_name):
        return next_int("Enter score for player %s" % player_name)

    def validate_score(self, score, winning_score):
        if score > winning_score or score < 0:
            message = "Invalid score for round %s with %d, vs %s with %d. Culprit: %d" % \
                      (self.player_name_a, self.score_a, self.player_name_b, self.score_b, score)
            print(message)

        while score > winning_score or score < 0:
            score = next_int("Score must be between 0 and %d, try again" % winning_score)

        return score

    @staticmethod
    def validate_player(player_name, player_stats):
        while True:
            if player_stats.find(player_name) is None:
                print("\n=== WARNING ===")
                print("%s cannot play this match." % player_name)
                print("Valid players:")
                for name, _ in player_stats:
                    print("- %s" % name)
                player_name = next_string("Enter a valid player to take their place")
                print()
            else:
                return player_name


class CommandExecutor:
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.commands = {
            "help": self.help,
            "quit": self.quit,
            "exit": self.quit,
            "start": self.start,
            "stats": self.stats
        }

    def execute(self, command):
        # Find the executor.
        args = command.split(" ")
        executor = self.commands.get(args[0])

        # Error on no command found.
        if executor is None:
            print("Command not recognised. Type 'help' to see all commands.")
            return

        # Execute the command.
        executor(args[1:])

    @staticmethod
    def help(args):
        print(HELP_MESSAGE)

    def quit(self, args):
        # TODO: Save all data.
        self.circuit.quit()

    def start(self, args):
        # Get the tournament name from the provided arguments.
        tournament_name = args[0]

        # Get the next incomplete season.
        season: Season = self.circuit.next_incomplete_season()

        # Start the tournament.
        season.start(tournament_name)

    def stats(self, args):
        pass


def main():
    if MAX_ROUNDS % 1 != 0:
        print("Maximum players must be a power of two")
        return

    circuit = load_circuit()
    circuit.run()


if __name__ == '__main__':
    main()
