from hash_table import HashTable
from player import TournamentStats
from tournament import Tournament


class Season:
    def __init__(self, circuit, previous, name: str, complete: bool, men_stats=HashTable(),
                 women_stats=HashTable(), tournaments=HashTable()):
        self.circuit = circuit
        self.previous = previous
        self.name = name
        self.complete = complete
        self.men_stats = men_stats
        self.women_stats = women_stats
        self.tournaments = tournaments  # <tournament name, tournament>

    def run(self, tournament_name):
        tournament: Tournament = self.tournaments.find(tournament_name)

        if tournament is None or tournament.complete:
            print('Starting a new tournament')

            # Check tournament type is valid.
            tournament_type = self.circuit.tournament_types.find(tournament_name)

            if tournament_type is None:
                print('A tournament by the name %s does not exist' % tournament_name)
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
            print('Continuing tournament from saved progress')

        tournament.run()

    @staticmethod
    def create_tournament_stats(profiles, stats):
        target = HashTable()

        for player_name, player_profile in profiles:
            season_stats = stats.find(player_name)
            tournament_stats = TournamentStats(player_profile, season_stats)
            target.insert(player_name, tournament_stats)

        return target
