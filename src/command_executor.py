from config import HELP_MESSAGE
from hash_table import HashTable
from linked_list import List
from loader import save_circuit
from pipe_sort import Sorter
from player import CircuitStats, SeasonStats, TournamentStats, Player
from season import Season
from tournament import Tournament
from user_input import next_string


class CommandExecutor:
    """Main programs command executor, handles all commands executed by the
    user.

    Attributes:
        circuit: The current circuit to work with.
        running: Whether the program should continue to run, or False if the
                 user requested to exit the program.
        commands: All command mappings from string to function.
        stats_commands: All command mappings of statistic sub-commands from
                        string to function.
    """

    def __init__(self, circuit):
        self.circuit = circuit
        self.running = True
        self.commands = HashTable()
        self.commands.insert('help', self.help)
        self.commands.insert('quit', self.quit)
        self.commands.insert('exit', self.quit)
        self.commands.insert('start', self.start)
        self.commands.insert('scoreboard', self.scoreboard)
        self.commands.insert('stats', self.stats)
        self.stats_commands = HashTable()
        self.stats_commands.insert('score', self.stats_score)
        self.stats_commands.insert('wins', self.stats_wins)
        self.stats_commands.insert('losses', self.stats_wins)

    def run(self):
        """Runs the command executor."""
        print('Type "help" to see all commands.')

        while self.running:
            command = next_string('Enter command')
            self.execute(command)

    def execute(self, command):
        """Executes a command given by the user.

        :param command: The command to execute.
        """
        if command is None:
            return

        # Find the executor.
        args = command.split(' ')
        executor = self.commands.find(args[0])

        # Error on no command found.
        if executor is None:
            print('Command not recognised. Type "help" to see all commands.')
            return

        # Execute the command.
        executor(args[1:])

    @staticmethod
    def help(args):
        """Prints the help message.

        :param args: The user arguments.
        """
        print(HELP_MESSAGE)

    def quit(self, args):
        """Quits the program.

        :param args: The user arguments.
        """
        save_circuit(self.circuit)
        self.running = False

    def start(self, args):
        """Starts a new tournament using the first argument of the command as
        the tournament name to start.

        :param args: The user arguments.
        """
        # Get the tournament name from the provided arguments.
        tournament_name = args[0]

        # Get the next incomplete season.
        season: Season = self.circuit.next_incomplete_season()

        # Start the tournament.
        season.run(tournament_name)

    def scoreboard(self, args):
        """Displays a scoreboard for a given season or tournament, depending on
        the arguments the user has supplied.

        :param args: The user arguments.
        """
        if len(args) == 0:
            self.circuit.print_scoreboard('men')
            self.circuit.print_scoreboard('women')
            return

        season: Season = self.circuit.seasons.find(args[0])

        if season is None:
            print('No season by the name %s was found' % args[0])
            return

        if len(args) > 1:
            tournament: Tournament = season.tournaments.find(args[1])
            if tournament is None:
                print('No tournament by the name %s was found' % args[1])
                return

            if len(args) > 2:
                gender = 'men' if args[2] == 'men' else 'women'
                tournament.print_scoreboard(gender)
            else:
                print('Displaying scoreboards for both men and women tracks')
                tournament.print_scoreboard('men')
                tournament.print_scoreboard('women')
            return

        print('Displaying scoreboards for both men and women tracks')
        season.print_scoreboard('men')
        season.print_scoreboard('women')

    def stats(self, args):
        """Displays circuit statistics or executes a statistics sub-command,
        depending on how many arguments were supplied by the user.

        :param args: The user arguments.
        """
        if len(args) == 0:
            self.print_circuit_stats('men')
            self.print_circuit_stats('women')
            return

        executor = self.stats_commands.find(args[0])

        if executor is None:
            print('No such "stats" sub command')
            return

        executor(args[1:])

    def stats_score(self, args):
        """Displays all scores a player has achieved or how many times the
        specified player has achieved a particular score.

        :param args: The user arguments.
        """
        player: Player = self.get_player(args)
        if player is None:
            return

        if len(args) == 1:
            rows = 3
            row_format = "| {:>15} |" * rows
            print(row_format.format('Player Score', 'Opponent Score', 'Count'))
            print(row_format.format('-' * 15, '-' * 15, '-' * 15))
            for (our_score, opponent_score), count in player.stats.scores:
                print(row_format.format(our_score, opponent_score, count))
            return

        scores = args[1].split(':')

        if len(scores) < 2:
            print('Invalid scores defined. Expected format: "score:opponent_score"')
            return

        our_score = int(scores[0])
        opponent_score = int(scores[1])
        stats = self.get_stats(args[2:], player.stats)
        if stats is None:
            return

        count = stats.scores.find((our_score, opponent_score), 0)
        print('%s earned a score of %s %d times' % (player.name, args[1], count))

    def stats_wins(self, args):
        """Displays all the wins, losses and percentage success for a given
        player.

        :param args: The user arguments.
        """
        player = self.get_player(args)
        if player is None:
            return

        stats = self.get_stats(args[1:], player.stats)
        if stats is None:
            return

        if stats.wins + stats.losses == 0:
            percent_success = 0
        else:
            percent_success = int(100 * stats.wins / float(stats.wins + stats.losses))

        print('%s has won %d times and lost %d times with %d percent success' % (
            player.name, stats.wins, stats.losses, percent_success))

    def print_circuit_stats(self, gender: str):
        """Prints all the statistics for a given track.

        :param gender: The player gender of the track to print statistics for.
        """
        season: Season = self.circuit.current_season
        if season is None:
            print('No season is currently running')
            return

        player_stats = season.get_stats(gender)
        win_count, winners = self.get_most_wins(player_stats)
        loss_count, losers = self.get_most_losses(player_stats)

        print('%s players with the most wins (%d wins) are as follows:' % (gender.title(), win_count))

        for player_stats in winners:
            print('- %s' % player_stats.player.name)

        print('%s players with the most losses (%d losses) are as follows:' % (gender.title(), loss_count))

        for player_stats in losers:
            print('- %s' % player_stats.player.name)

    def get_player(self, args):
        """Fetches a player from command arguments.

        :param args: The user arguments.
        """
        if len(args) == 0:
            print('Player not specified')
            return None

        player = self.circuit.men.find(args[0])

        if player is None:
            player = self.circuit.women.find(args[0])

        if player is None:
            print('No such player by the name %s was found' % args[0])

        return player

    def get_stats(self, args, stats):
        """Fetches a players statistics from command arguments.

        :param args: The user arguments.
        :param stats: All statistics in the track the player belongs.
        :return: The statistics found for the given player.
        """
        if len(args) >= 1:
            season: Season = self.circuit.seasons.find(args[0])
            if season is None:
                print('No season by the name %s found' % args[0])
                return None
            stats: SeasonStats = stats.season_stats.find(season.name)

            if len(args) >= 2:
                tournament: Tournament = season.tournaments.find(args[1])
                if tournament is None:
                    print('No tournament by the name %s found' % args[1])
                    return None
                stats: TournamentStats = stats.tournament_stats.find(tournament.type.name)
        return stats

    @staticmethod
    def get_most_wins(player_stats):
        """Sorts all player statistics by most wins and returns all the players
        that achieved the most number of wins, as well as the number of wins
        they achieved.

        :param player_stats: The player statistics mappings to sort and parse.
        :return: The amount of wins, and all the top-winning players.
        """
        sorter = Sorter(lambda a, b: b.wins - a.wins)

        for name, stats in player_stats:
            sorter.consume(stats)

        sorted_by_wins = sorter.sort()
        win_count = sorted_by_wins[0].wins
        target = List()

        for stats in sorted_by_wins:
            stats: CircuitStats = stats
            if stats.wins != win_count:
                break
            target.append(stats)

        return win_count, target

    @staticmethod
    def get_most_losses(player_stats):
        """Sorts all the player statistics by most losses and returns all the
        players that achieved the most number of losses, as well as the number
        of losses in total they achieved.

        :param player_stats: The player statistics mappings to sort and parse.
        :return: The amount of losses, and all the top-loosing players.
        """
        sorter = Sorter(lambda a, b: b.losses - a.losses)

        for name, stats in player_stats:
            sorter.consume(stats)

        sorted_by_losses = sorter.sort()
        loss_count = sorted_by_losses[0].losses
        target = List()

        for stats in sorted_by_losses:
            stats: CircuitStats = stats
            if stats.losses != loss_count:
                break
            target.append(stats)

        return loss_count, target
