#!/usr/bin/env python

"""

Solution for streamed data.

"""

from game import Game
from hash_table import HashTable
from player import Player
from ranked_tree import Tree
from tournament import Tournament

# Defines the two possible genders.
MALE = False
FEMALE = True


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

        if user_input is not None:
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
        difficulty = fetch_float("Enter the tournament difficulty", 1.0)
        prizes = HashTable()
        creating_prizes = fetch_boolean("Would you like to enter a prize?", True)

        while creating_prizes:
            rank = fetch_int("Enter rank for prize", 1)
            overwrite = True

            if prizes.find(rank) is not None:
                print("A prize for rank " + str(rank) + " already exists")
                overwrite = fetch_boolean("Do you wish to overwrite it?", False)

            if overwrite:
                prize = fetch_string("Enter the prize money to give", "1,000")
                prizes.insert(rank, prize)
                print("Successfully added a prize to " + name)

            creating_prizes = fetch_boolean("Would you like to enter another prize?", True)

        tournament = Tournament(name, prizes, difficulty)
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

    while True:
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

        if score_a != max_score and score_b != max_score:
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
        print("Starting round " + str(current_round) + " of tournament " +
              tournament.name)

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


def run():
    """Runs the stream solution program.

    :return: None
    """
    print("Solution - Stream")
    print("Please create all tournaments in this circuit")
    tournaments = create_tournaments()
    print("Please enter all the male player names")
    men_by_name = create_players(len(tournaments))
    print("Please enter all the female player names")
    women_by_name = create_players(len(tournaments))
    print("Please enter all the ranking points")
    ranking_points = create_ranking_points()
    print("All properties of this circuit are complete")
    print("Starting the circuit")
    unfinished_tournaments = HashTable()
    ranked_men = Tree(lambda a, b: b - a)
    ranked_women = Tree(lambda a, b: b - a)

    for tournament_name, tournament in tournaments:
        unfinished_tournaments.insert(tournament_name, True)

    while len(unfinished_tournaments) > 0:
        # Select the next tournament to play through.
        tournament = fetch_next_tournament(tournaments, unfinished_tournaments)
        print("Playing the tournament " + tournament.name)

        # The tournament is no longer required to run.
        unfinished_tournaments.delete(tournament.name)

        # Get the next gender playing.
        first_gender = fetch_gender("Are the men or the women playing first?", MALE)

        if first_gender == MALE:
            print("Men are now playing tournament " + tournament.name)
            play_tournament(tournament, men_by_name, ranking_points, ranked_men)
            print("Women are now playing tournament " + tournament.name)
            play_tournament(tournament, women_by_name, ranking_points, ranked_women)
        else:
            print("Women are now playing tournament " + tournament.name)
            play_tournament(tournament, women_by_name, ranking_points, ranked_women)
            print("Men are now playing tournament " + tournament.name)
            play_tournament(tournament, men_by_name, ranking_points, ranked_men)

    # Print all players ordered by ranking points.
    print("--------------------------------\n")
    print("Total ranking points\n")
    print("--------------------------------\n")

    print("Men:")

    for points, player in ranked_men:
        print(player.name + " " + str(points))

    print()
    print("Women:")

    for points, player in ranked_women:
        print(player.name + " " + str(points))


if __name__ == '__main__':
    run()
