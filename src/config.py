import math

MAX_PLAYERS = 32

MAX_ROUNDS = math.log(MAX_PLAYERS, 2)

MEN_WIN_SCORE = 3
MEN_FORFEIT_SCORE = 2

WOMEN_WIN_SCORE = 2
WOMEN_FORFEIT_SCORE = 1

TOURNAMENT_COUNT = 4

HELP_MESSAGE = """
=== TENNIS HELP ===

> help
Displays all commands.

> quit
Quits the program.

> start <tournament>
Starts the next tournament.

> scoreboard <season> [tournament]
Shows the scoreboard for the given season or tournament.

> stats
Shows the player with most wins and player with most losses.

> stats score <player> <score> [season] [tournament]
Gets number of times a player got a specific score in a tournament or season.

> stats wins <player> [season] [tournament]
Gets total number of times a player won in a tournament, season, or overall.

> stats losses <player> [season] [tournament]
Gets total number of times a player lost in a tournament, season, or overall.

===================
"""

OUTPUT = '../output'
RESOURCES = '../resources'
TOURNAMENTS_FILE = '%s/tournaments.csv' % RESOURCES
MEN_FILE = '%s/stats.csv' % RESOURCES
WOMEN_FILE = '%s/women.csv' % RESOURCES
RANKING_POINTS_FILE = '%s/ranking_points.csv' % RESOURCES

if MAX_ROUNDS % 1 != 0:
    raise ValueError('Maximum players must be a power of two')


def get_winning_score(gender):
    return MEN_WIN_SCORE if gender == 'men' else WOMEN_WIN_SCORE


def get_forfeit_score(gender):
    return MEN_FORFEIT_SCORE if gender == 'men' else WOMEN_FORFEIT_SCORE


def apply_multiplier(gender, winner, loser_score):
    if gender == 'men':
        if loser_score == 0:
            winner.multiplier += 2.5
        elif loser_score == 1:
            winner.multiplier += 1.5
    elif loser_score == 0:
        winner.multiplier += 2.5
