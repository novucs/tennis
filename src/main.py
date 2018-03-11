from command_executor import CommandExecutor
from loader import load_circuit


def main():
    # Load the circuit from database.
    circuit = load_circuit()

    # Create and run the command executor.
    command_executor = CommandExecutor(circuit)
    command_executor.run()


if __name__ == '__main__':
    main()
