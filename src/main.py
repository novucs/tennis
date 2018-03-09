import sys

from hash_table import HashTable
from utils import load_circuit

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


class Round:
    def __init__(self, tournament):
        self.tournament = tournament


class Tournament:
    """A tennis tournament profile.

    Attributes:
        name: The name of the tournament.
        prizes: A hash table of prizes, keys being the place in the tournament.
        difficulty: The difficulty rating of this tournament.
    """

    def __init__(self, name, prizes, difficulty):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty

    def __str__(self):
        return "{name=" + self.name + \
               ", prizes=" + str(self.prizes) + \
               ", difficulty=" + str(self.difficulty) + "}"


class Circuit:
    def __init__(self):
        self.running = True
        self.command_executor = CommandExecutor(self)
        self.tournaments = HashTable()
        self.men = HashTable()
        self.women = HashTable()
        self.ranking_points = HashTable()

    def run(self):
        load_tournaments(self.tournaments)
        load_men(self.men)
        load_women(self.women)
        load_ranking_points(self.ranking_points)

        print("Type 'help' to see all commands.")

        while self.running:
            print("> ", end='', flush=True)
            command = sys.stdin.readline()[:-1]
            self.command_executor.execute(command)

    def quit(self):
        self.running = False


class CommandExecutor:
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.commands = {
            "help": self.help,
            "quit": self.quit,
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

    def help(self, args):
        print(HELP_MESSAGE)

    def quit(self, args):
        self.circuit.quit()

    def start(self, args):
        tournament_name = args[0].lower()
        tournament = self.circuit.complete_tournaments.find(tournament_name)

        if tournament is not None:
            print("Tournament has already ran")
            return

        tournament = self.circuit.tournaments.find(tournament_name)

        if tournament is None:
            print("No such tournament exists.")
            return

    def stats(self, args):
        pass


class Season:
    def __init__(self, name):
        self.complete_tournaments = HashTable()


def main():
    circuit = Circuit()
    circuit.run()


if __name__ == '__main__':
    main()
