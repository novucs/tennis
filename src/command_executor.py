from config import HELP_MESSAGE
from loader import save_circuit
from user_input import next_string


class CommandExecutor:
    def __init__(self, circuit):
        self.circuit = circuit
        self.running = True
        self.commands = {
            'help': self.help,
            'quit': self.quit,
            'exit': self.quit,
            'start': self.start,
            'stats': self.stats
        }

    def run(self):
        print('Type "help" to see all commands.')

        while self.running:
            command = next_string('Enter command')
            self.execute(command)

    def execute(self, command):
        # Find the executor.
        args = command.split(' ')
        executor = self.commands.get(args[0])

        # Error on no command found.
        if executor is None:
            print('Command not recognised. Type "help" to see all commands.')
            return

        # Execute the command.
        executor(args[1:])

    @staticmethod
    def help(args):
        print(HELP_MESSAGE)

    def quit(self, args):
        save_circuit(self.circuit)
        self.running = False

    def start(self, args):
        # Get the tournament name from the provided arguments.
        tournament_name = args[0]

        # Get the next incomplete season.
        season = self.circuit.next_incomplete_season()

        # Start the tournament.
        season.run(tournament_name)

    def stats(self, args):
        pass
