from config import get_forfeit_score, get_winning_score
from hash_table import HashTable
from match import Track
from player import TournamentStats, SeasonStats
from ranked_tree import Tree
from tournament import Tournament


class Season:
    def __init__(self, circuit, previous, name: str, complete: bool, men_stats, women_stats, men_scoreboard,
                 women_scoreboard):
        self.circuit = circuit
        self.previous = previous
        self.name = name
        self.complete = complete
        self.men_stats = men_stats
        self.women_stats = women_stats
        self.men_scoreboard = men_scoreboard
        self.women_scoreboard = women_scoreboard
        self.tournaments = HashTable()  # <tournament name, tournament>

    def run(self, tournament_name):
        tournament: Tournament = self.tournaments.find(tournament_name)

        if tournament is None:
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

            tournament = Tournament(self, tournament_type, previous_tournament, False)
            tournament.men_track = self.create_track(tournament, 'men')
            tournament.women_track = self.create_track(tournament, 'women')

            self.tournaments.insert(tournament_name, tournament)
        else:
            print('Continuing tournament from saved progress')

        tournament.run()

    def create_track(self, tournament, gender):
        stats = HashTable()

        for player_name, player_profile in self.circuit.get_players(gender):
            season_stats: SeasonStats = self.get_stats(gender).find(player_name)
            tournament_stats = TournamentStats(player_profile, season_stats)
            season_stats.tournament_stats.insert(tournament.type.name, tournament_stats)
            stats.insert(player_name, tournament_stats)

        winning_score = get_winning_score(gender)
        forfeit_score = get_forfeit_score(gender)

        previous_stats = None
        previous_season_scoreboard = None

        if tournament.previous is not None:
            previous_stats = tournament.previous.get_track(gender).stats
            previous_season_scoreboard = tournament.previous.season.get_scoreboard(gender)

        track_round = 1
        remaining = stats.clone()
        scoreboard = Tree()

        return Track(gender, track_round, stats, remaining, winning_score, forfeit_score, scoreboard, previous_stats,
                     previous_season_scoreboard)

    def get_stats(self, gender):
        return self.men_stats if gender == 'men' else self.women_stats

    def get_scoreboard(self, gender):
        return self.men_scoreboard if gender == 'men' else self.women_scoreboard
