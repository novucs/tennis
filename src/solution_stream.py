#!/usr/bin/env python

"""

Solution for streamed data.

"""

from game import Game
from hash_table import HashTable
from player import Player
from ranked_tree import Tree
from tournament import Tournament
from utils import *


def fetch_string(message, default=None):
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


def fetch_boolean(message, default=None):
    """Fetches a boolean from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input boolean.
    """

    while True:
        default_text = "Y/n" if default else "y/N"
        user_input = fetch_string(message, default_text)

        if user_input == default_text:
            return default

        parsed = user_input.lower()

        if parsed.startswith("y") or parsed.startswith("t"):
            return True
        elif parsed.startswith("n") or parsed.startswith("f"):
            return False

        print("Invalid boolean entered, try again")


def fetch_int(message, default=None):
    """Fetches an int from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input int.
    """

    while True:
        default_text = None if default is None else str(default)
        user_input = fetch_string(message, default_text)

        if user_input is not None:
            try:
                parsed = int(user_input)
                return parsed
            except ValueError:
                pass

        print("Invalid integer entered, try again")


def fetch_float(message, default=None):
    """Fetches a float from the user.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user input float.
    """

    while True:
        default_text = None if default is None else str(default)
        user_input = fetch_string(message, default_text)

        if user_input is not None:
            try:
                parsed = float(user_input)
                return parsed
            except ValueError:
                pass

        print("Invalid float entered, try again")


def create_tournaments():
    """Creates a hash table of tournaments from user input.

    :return: The created tournaments, indexed by name.
    """

    tournaments = HashTable()
    creating_tournaments = True

    while creating_tournaments:
        name = None
        while name is None:
            name = fetch_string("Enter a new tournament name")

        tournament = Tournament(name, prizes=HashTable(), difficulty=1)
        tournaments.insert(name, tournament)
        print("Tournament " + name + " successfully created")

        creating_tournaments = fetch_boolean("Do you wish to continue making "
                                             "tournaments?", True)

    return tournaments


def create_players(tournament_count):
    """Creates a hash table of players from user input.

    :param tournament_count: The total number of tournaments in this circuit.
    :return: The created player profiles, indexed by name.
    """

    players_by_name = HashTable()
    creating_players = True

    while creating_players:
        name = fetch_string("Enter a new player name")

        if players_by_name.find(name) is not None:
            print("Player " + name + " already exists")
        elif name is None:
            print("No player created")
        else:
            player = Player(name, tournament_count)
            players_by_name.insert(name, player)
            print("Player " + name + " successfully created")

        if len(players_by_name) >= 2:
            creating_players = fetch_boolean("Do you with to continue making "
                                             "players?", True)

    return players_by_name


def create_ranking_points():
    """Creates a hash table of ranking points from user input.

    :return: The created table of tournament rank to circuit points earned.
    """

    ranking_points = HashTable()
    creating_ranking_points = True

    while creating_ranking_points:
        rank = fetch_int("Enter a rank that wins points", 1)
        overwrite = True

        if ranking_points.find(rank) is not None:
            print("The points for rank " + str(rank) + " has already been set")
            overwrite = fetch_boolean("Do you wish to overwrite?", False)

        if overwrite:
            points = fetch_int("Enter the points this rank wins", 100)
            ranking_points.insert(rank, points)

        creating_ranking_points = fetch_boolean("Do you wish to continue "
                                                "adding ranking points?", True)

    return ranking_points


def fetch_next_tournament(tournaments, unfinished_tournaments):
    """Fetches the next tournament to run from the user.

    :param tournaments: The tournaments available.
    :param unfinished_tournaments: The unfinished tournaments.
    :return: The next tournament to run.
    """

    print("Please select the next tournament to win")
    print("Here are the unfinished tournaments:")

    for name, _ in unfinished_tournaments:
        print("- " + name)

    tournament = None

    while tournament is None:
        name = fetch_string("Enter the next tournament name")
        tournament = tournaments.find(name)

    return tournament


def fetch_gender(message, default=None):
    """Fetches a gender from user input.

    :param message: The message to prompt the user.
    :param default: The default value.
    :return: The user submitted gender.
    """

    while True:
        default_text = "m/F" if default else "M/f"
        user_input = fetch_string(message, default_text)

        if user_input is not None:
            parsed = user_input.lower()

            if parsed.startswith("f"):
                return True
            elif parsed.startswith("m"):
                return False

        print("Invalid gender entered, try again")


def fetch_player(message, players_by_name):
    """Fetches a player from user input.

    :param message: The message to prompt the user.
    :param players_by_name: The available players.
    :return: The player chosen.
    """

    print("Players in this tournament:")

    for name, player in players_by_name:
        print("- " + name)

    player = None

    while player is None:
        user_input = fetch_string(message)
        player = players_by_name.find(user_input)

        if player is None:
            print("That player is currently not playing this round")

    return player


def fetch_score(message, max_score):
    """Fetches the score from user input.

    :param message: The message to send to the user.
    :param max_score: The maximum score the user can enter.
    :return: The score.
    """

    while True:
        score = fetch_int(message, 0)

        if score < 0 or score > max_score:
            print("Scores must be within the range of 0 and " + str(max_score))
        else:
            return score


def play_game(tournament, sorted_players, players_by_name, max_score):
    """Plays a tournament game between two players.

    :param tournament: The active tournament.
    :param sorted_players: The sorted players for this tournament.
    :param players_by_name: The players by name playing this tournament.
    :param max_score: The maximum score players can achieve.
    :return: The game results.
    """

    default_max_score = max_score

    while True:
        max_score = default_max_score
        player_a = fetch_player("Enter player A", players_by_name)
        score_a = fetch_score("Enter " + player_a.name + "'s score", max_score)
        print(player_a.name + " scored " + str(score_a) + " points")
        player_b = fetch_player("Enter player B", players_by_name)

        if player_a == player_b:
            print("Players cannot play themselves")
            continue

        if score_a == max_score:
            max_score = max_score - 1

        score_b = fetch_score("Enter " + player_b.name + "'s score", max_score)
        print(player_b.name + " scored " + str(score_b) + " points")

        if score_a != default_max_score and score_b != default_max_score:
            print("Error, nobody won this game, please try again")
            continue

        old_score_a = player_a.scores.find(tournament.name, 0)
        old_score_b = player_a.scores.find(tournament.name, 0)

        score_a += old_score_a
        score_b += old_score_b

        sorted_players.delete(old_score_a, player_a)
        sorted_players.delete(old_score_b, player_b)

        player_a.scores.insert(tournament.name, score_a)
        player_b.scores.insert(tournament.name, score_b)

        sorted_players.insert(score_a, player_a)
        sorted_players.insert(score_b, player_b)

        return Game(player_a, score_a, player_b, score_b)


def play_tournament(tournament, players_by_name, ranking_points, ranked_players):
    """Plays an entire tournament.

    :param tournament: The tournament to play.
    :param players_by_name: The participants of this tournament.
    :param ranking_points: The number of circuit points earned by each rank.
    :param ranked_players: The overall ranked tree of players.
    :return: The sorted players of this tournament.
    """

    if len(players_by_name) == 0:
        print("There are no players in this tournament")
        return Tree(lambda a, b: b - a)

    tournament.difficulty = fetch_float("Enter the tournament difficulty", 1.0)

    if len(tournament.prizes) == 0:
        creating_prizes = fetch_boolean("Are there prizes in this tournament?", True)

        while creating_prizes:
            rank = fetch_int("Enter rank for prize", 1)
            overwrite = True

            if tournament.prizes.find(rank) is not None:
                print("A prize for rank " + str(rank) + " already exists")
                overwrite = fetch_boolean("Do you wish to overwrite it?", False)

            if overwrite:
                prize = fetch_string("Enter the prize money to give", "1,000")
                if tournament.prizes.insert(rank, prize) is not None:
                    print("Successfully modified prize in " + tournament.name)
                else:
                    print("Successfully added a prize to " + tournament.name)

            creating_prizes = fetch_boolean("Is there another prize in this tournament?", True)

    current_round = 1
    another_round = True
    sorted_players = Tree(lambda a, b: b - a)
    max_score = None

    while max_score is None:
        max_score = fetch_int("Enter the score to win this tournament", 3)

        if max_score <= 0:
            max_score = None
            print("The score to win must be more than 0")

    while another_round:
        print("\nStarting a new round of tournament " + tournament.name)

        another_game = True

        while another_game:
            game = play_game(tournament, sorted_players, players_by_name, max_score)
            winner = game.player_a if game.score_a > game.score_b else game.player_b
            print("Congratulations to " + winner.name + " for winning")
            another_game = fetch_boolean("Will there be another game in this "
                                         "round?", True)

        another_round = fetch_boolean("Will there be another round?", True)
        current_round += 1

    for rank, prize in tournament.prizes:
        if rank > len(sorted_players):
            continue

        players = sorted_players.select(rank - 1)

        if players is None:
            continue

        for player in players:
            print(player.name + " wins " + prize)

    for rank, points in ranking_points:
        if rank > len(sorted_players):
            continue

        players = sorted_players.select(rank - 1)

        if players is None:
            continue

        for player in players:
            ranked_players.delete(player.ranking_points, player)
            player.ranking_points += points * tournament.difficulty
            ranked_players.insert(player.ranking_points, player)

    return sorted_players


def load_tournaments():
    """Loads all tournaments from file.

    :return: The tournaments.
    """
    tournaments = HashTable()
    with open("../output/stream/remaining_tournaments.csv", "r") as file:
        for line in file:
            values = parse_csv_line(line)
            name = values[0]
            prizes = HashTable()
            difficulty = 1
            tournament = Tournament(name, prizes, difficulty)
            tournaments.insert(name, tournament)
    return tournaments


def load_players(file_name):
    """Loads all players from file.

    :param file_name: The file name.
    :return: The players.
    """
    players = HashTable()
    with open(file_name, "r") as file:
        for line in file:
            values = parse_csv_line(line)
            name = values[0]
            points = float(values[1])
            player = Player(name)
            player.ranking_points = points
            players.insert(name, player)
    return players


def load_ranking_points():
    """Loads all ranking points from file.

    :return: The ranking points.
    """
    ranking_points = HashTable()
    with open("../output/stream/ranking_points.csv", "r") as file:
        for line in file:
            values = parse_csv_line(line)
            rank = int(values[0])
            points = float(values[1])
            ranking_points.insert(rank, points)
    return ranking_points


def load_tournament_scores(tournament, players_by_name):
    """Loads tournament scores from file.

    :param tournament: The tournament.
    :param players_by_name: The players.
    :return: None
    """
    with open("../output/stream/scores.csv", "r") as file:
        for line in file:
            values = parse_csv_line(line)
            name = values[0]
            score = int(values[1])
            player = players_by_name.find(name)
            player.scores.insert(tournament.name, score)


def persist_current_tournament(file_name, first_gender, first_gender_complete, tournament, tournament_complete):
    """Saves the current tournament to a file.

    :param file_name: The file name.
    :param first_gender: The first gender played.
    :param first_gender_complete: True if the first gender has finished.
    :param tournament: The tournament.
    :param tournament_complete: True if the tournament is complete.
    :return: None
    """
    prepare_persist(file_name)
    with open(file_name, "a") as file:
        tournament_name = tournament.name if tournament is not None else ""
        file.write(tournament_name + "," + ("m" if first_gender == MALE else "f") + "," + str(first_gender_complete) +
                   "," + str(tournament_complete))


def persist_tournament_scores(file_name, players_by_name, tournament):
    """Saves tournament scores to file.

    :param file_name: The file name.
    :param players_by_name: The players.
    :param tournament: The tournament.
    :return: None
    """
    prepare_persist(file_name)

    if tournament is None:
        return

    with open(file_name, "a") as file:
        for name, player in players_by_name:
            score = player.scores.find(tournament.name, 0)
            file.write(name + "," + str(score) + "\n")


def persist_circuit_points(file_name, players_by_name):
    """Saves the current points.

    :param file_name: The file name.
    :param players_by_name: The players.
    :return: None
    """
    prepare_persist(file_name)
    with open(file_name, "a") as file:
        for name, player in players_by_name:
            file.write(name + "," + str(player.ranking_points) + "\n")


def persist_ranking_points(file_name, ranking_points):
    """Saves the ranking points to file.

    :param file_name: The file name.
    :param ranking_points: The ranking points.
    :return: None
    """
    prepare_persist(file_name)
    with open(file_name, "a") as file:
        for rank, points in ranking_points:
            file.write(str(rank) + "," + str(points) + "\n")


def persist_remaining_tournaments(file_name, remaining_tournaments):
    """Saves the remaining tournaments to file.

    :param file_name: The file name,
    :param remaining_tournaments: The remaining tournaments.
    :return: None
    """
    prepare_persist(file_name)
    with open(file_name, "a") as file:
        for name, _ in remaining_tournaments:
            file.write(name + "\n")


class Circuit:
    def __init__(self,
                 tournaments=HashTable(),
                 remaining_tournaments=HashTable(),
                 ranking_points=HashTable(),
                 men_by_name=HashTable(),
                 women_by_name=HashTable(),
                 ranked_men=Tree(lambda a, b: b - a),
                 ranked_women=Tree(lambda a, b: b - a),
                 active_tournament=None,
                 active_tournament_complete=False,
                 first_gender=MALE,
                 first_gender_complete=False):
        self.tournaments = tournaments
        self.men_by_name = men_by_name
        self.women_by_name = women_by_name
        self.ranked_men = ranked_men
        self.ranked_women = ranked_women
        self.ranking_points = ranking_points
        self.remaining_tournaments = remaining_tournaments
        self.active_tournament = active_tournament
        self.active_tournament_complete = active_tournament_complete
        self.first_gender = first_gender
        self.first_gender_complete = first_gender_complete

    def run(self):
        """Runs the stream solution program.

        :return: None
        """

        print(HEADER + "STREAMED SOLUTION" + FOOTER)

        load_previous_circuit = fetch_boolean("Do you wish to load circuit data from a previous session?", False)

        if load_previous_circuit:
            if self.load_previous_session():
                return

            print_circuit_start()

            if self.active_tournament is not None or not self.active_tournament_complete:
                if self.continue_unfinished_game():
                    return
        else:
            self.fetch_new_session()
            print_circuit_start()

        self.active_tournament = None
        self.first_gender = MALE
        self.first_gender_complete = False

        if self.run_circuit():
            return

        print(HEADER + "CIRCUIT COMPLETE" + FOOTER)
        print_ranking_points(self.ranked_men, self.ranked_women)
        self.save()

    def run_circuit(self):
        """Runs all the circuits until either interrupted or complete.

        :return: True if interrupted, otherwise False.
        """
        while len(self.remaining_tournaments) > 0:
            try:
                # Select the next tournament to play through.
                self.active_tournament = fetch_next_tournament(self.tournaments, self.remaining_tournaments)
                self.active_tournament_complete = False
                print("Playing the tournament " + self.active_tournament.name)

                # Get the next gender playing.
                self.first_gender = fetch_gender("Are the men or the women playing first?", MALE)
                self.first_gender_complete = False

                if self.first_gender == MALE:
                    print("\nMen are now playing tournament " + self.active_tournament.name)
                    play_tournament(self.active_tournament, self.men_by_name, self.ranking_points, self.ranked_men)
                    self.first_gender_complete = True
                    print("\nWomen are now playing tournament " + self.active_tournament.name)
                    play_tournament(self.active_tournament, self.women_by_name, self.ranking_points, self.ranked_women)
                else:
                    print("\nWomen are now playing tournament " + self.active_tournament.name)
                    play_tournament(self.active_tournament, self.women_by_name, self.ranking_points, self.ranked_women)
                    self.first_gender_complete = True
                    print("\nMen are now playing tournament " + self.active_tournament.name)
                    play_tournament(self.active_tournament, self.men_by_name, self.ranking_points, self.ranked_men)

                # The tournament is no longer required to run.
                self.remaining_tournaments.delete(self.active_tournament.name)
                self.active_tournament_complete = True
            except (EOFError, KeyboardInterrupt):
                self.handle_interrupt()
                return True
        return False

    def fetch_new_session(self):
        """Fetches a new circuit session from user input.

        :return: None
        """
        print("Please create all tournaments in this circuit")
        self.tournaments = create_tournaments()
        print("Please enter all the male player names")
        self.men_by_name = create_players(len(self.tournaments))
        print("Please enter all the female player names")
        self.women_by_name = create_players(len(self.tournaments))
        print("Please enter all the ranking points")
        self.ranking_points = create_ranking_points()
        print("All properties of this circuit are complete")
        for tournament_name, tournament in self.tournaments:
            self.remaining_tournaments.insert(tournament_name, True)

        for name, profile in self.men_by_name:
            self.ranked_men.insert(profile.ranking_points, profile)

        for name, profile in self.women_by_name:
            self.ranked_women.insert(profile.ranking_points, profile)

    def continue_unfinished_game(self):
        """Continues a previously unfinished tournament.

        :return: True if interrupted halfway through.
        """
        try:
            print("Playing the tournament " + self.active_tournament.name)

            # Load the scores for the current tournament.
            load_tournament_scores(self.active_tournament,
                                   self.men_by_name if (self.first_gender == MALE) ^ self.first_gender_complete else
                                   self.women_by_name)

            if self.first_gender == MALE:
                if not self.first_gender_complete:
                    print("\nMen are now playing tournament " + self.active_tournament.name)
                    play_tournament(self.active_tournament, self.men_by_name, self.ranking_points, self.ranked_men)
                self.first_gender_complete = True
                print("\nWomen are now playing tournament " + self.active_tournament.name)
                play_tournament(self.active_tournament, self.women_by_name, self.ranking_points, self.ranked_women)
            else:
                if not self.first_gender_complete:
                    print("\nWomen are now playing tournament " + self.active_tournament.name)
                    play_tournament(self.active_tournament, self.women_by_name, self.ranking_points, self.ranked_women)
                self.first_gender_complete = True
                print("\nMen are now playing tournament " + self.active_tournament.name)
                play_tournament(self.active_tournament, self.men_by_name, self.ranking_points, self.ranked_men)

            # The tournament is no longer required to run.
            self.remaining_tournaments.delete(self.active_tournament.name)
            self.active_tournament_complete = True
        except (EOFError, KeyboardInterrupt):
            self.handle_interrupt()
            return True
        return False

    def load_previous_session(self):
        """Loads the previously saved session for the current circuit.

        :return: True if failed to load, otherwise False.
        """
        # noinspection PyBroadException
        try:
            self.tournaments = load_tournaments()
            self.men_by_name = load_players("../output/stream/ranked_men.csv")
            self.women_by_name = load_players("../output/stream/ranked_women.csv")
            self.ranking_points = load_ranking_points()

            for name, profile in self.men_by_name:
                self.ranked_men.insert(profile.ranking_points, profile)

            for name, profile in self.women_by_name:
                self.ranked_women.insert(profile.ranking_points, profile)

            for tournament_name, tournament in self.tournaments:
                self.remaining_tournaments.insert(tournament_name, True)

            if len(self.remaining_tournaments) == 0:
                print(HEADER + "CIRCUIT COMPLETE" + FOOTER)
                print_ranking_points(self.ranked_men, self.ranked_women)
                return True

            with open("../output/stream/current_tournament.csv") as file:
                line = file.readline()
                values = parse_csv_line(line)
                self.active_tournament = self.tournaments.find(values[0])
                self.first_gender = MALE if values[1].lower().startswith("m") else FEMALE
                self.first_gender_complete = values[2] == "True"
                self.active_tournament_complete = values[3] == "True"

            if self.active_tournament_complete:
                self.remaining_tournaments.delete(self.active_tournament.name)

        except Exception as exception:
            print("Failed to load circuit data for previous session.")
            print("This is probably due to there not being a previous session, or the saved data was corrupt.")
            print(exception)
            return True
        return False

    def handle_interrupt(self):
        """Handles when the circuit has been interrupted.

        :return: None
        """
        while True:
            try:
                if self.active_tournament is None:
                    print(HEADER + "CIRCUIT COMPLETE" + FOOTER)
                    print_ranking_points(self.ranked_men, self.ranked_women)
                    break

                print(HEADER + "CIRCUIT INTERRUPTED" + FOOTER)
                self.save()
                print_ranking_points(self.ranked_men, self.ranked_women)
                break
            except KeyboardInterrupt:
                print("Received keyboard interrupt, retrying")
                continue

    def save(self):
        """Saves the circuit progress.

        :return: None
        """
        print("\nSaving progress...")
        base_directory = "../output/stream/"
        current_tournament_csv = base_directory + "current_tournament.csv"
        ranked_men_csv = base_directory + "ranked_men.csv"
        ranked_women_csv = base_directory + "ranked_women.csv"
        ranking_points_csv = base_directory + "ranking_points.csv"
        remaining_tournaments_csv = base_directory + "remaining_tournaments.csv"
        tournament_scores_csv = base_directory + "scores.csv"
        persist_current_tournament(current_tournament_csv, self.first_gender, self.first_gender_complete,
                                   self.active_tournament, self.active_tournament_complete)
        persist_circuit_points(ranked_men_csv, self.men_by_name)
        persist_circuit_points(ranked_women_csv, self.women_by_name)
        persist_ranking_points(ranking_points_csv, self.ranking_points)
        persist_remaining_tournaments(remaining_tournaments_csv, self.remaining_tournaments)
        players_by_name = self.men_by_name if (self.first_gender == MALE) ^ self.first_gender_complete \
            else self.women_by_name
        persist_tournament_scores(tournament_scores_csv, players_by_name, self.active_tournament)
        print("Saving complete!\n")


def print_circuit_start():
    """Prints the circuit start message.

    :return: None
    """
    print(HEADER + "STARTING THE CIRCUIT" + FOOTER)
    print("Press CTRL+C if you wish to pause and save the")
    print("circuit progress for another day.\n")


def print_ranking_points(ranked_men, ranked_women):
    """Prints the ranking points.

    :param ranked_men: The ranked men.
    :param ranked_women: The ranked women.
    :return:
    """
    # Print all players ordered by ranking points.
    print("Male ranking points:")
    for points, player in ranked_men:
        print(player.name + " " + str(points))
    print()
    print("Female ranking points:")
    for points, player in ranked_women:
        print(player.name + " " + str(points))


def main():
    circuit = Circuit()
    circuit.run()


if __name__ == '__main__':
    main()
