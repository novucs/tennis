from config import get_forfeit_score, get_winning_score
from hash_table import HashTable
from linked_list import List
from match import Track
from player import TournamentStats, SeasonStats
from tournament import Tournament


class Season:
    """A season, contains multiple tournaments and retains a scoreboard for
    both men and women player tracks.

    Attributes:
        circuit: The tournament circuit this season uses.
        previous: The previous season in this circuit.
        name: The name of the season.
        men_stats: Maps all male player names to their season statistics.
        women_stats: Maps all female player names to their season statistics.
        men_scoreboard: An array of male statistics for this season sorted by points.
        women_scoreboard: An array of female statistics for this season sorted by points.
    """

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
        """Runs the season, given a tournament name.

        :param tournament_name: The tournament to run.
        """
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

        if len(self.tournaments) == len(self.circuit.tournament_types):
            self.complete = True
            print('Season %s has successfully complete!' % self.name)
            self.print_scoreboard('men')
            self.print_scoreboard('women')

    def create_track(self, tournament, gender):
        """Creates a new track for a given tournament and gender. Starts off
        with an empty scoreboard and mappings for the player stats.

        :param tournament: The tournament to create the track for.
        :param gender: The gender of the track to create.
        :return: The newly created track.
        """
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
        scoreboard = List()

        return Track(gender, track_round, stats, remaining, winning_score, forfeit_score, scoreboard, previous_stats,
                     previous_season_scoreboard)

    def get_stats(self, gender):
        """Gets the season stat mappings for a given gender.

        :param gender: The track gender.
        :return: The stat mappings.
        """
        return self.men_stats if gender == 'men' else self.women_stats

    def get_scoreboard(self, gender):
        return self.men_scoreboard if gender == 'men' else self.women_scoreboard

    def set_scoreboard(self, gender, scoreboard):
        """Updates the scoreboard for a given gender in the season.

        :param gender: The gender of the track scoreboard to update.
        :param scoreboard: The new scoreboard to update the current with.
        """
        if gender == 'men':
            self.men_scoreboard = scoreboard
        else:
            self.women_scoreboard = scoreboard

    def print_scoreboard(self, gender):
        """Prints the scoreboard for the season, given the gender of the
        scoreboard track to print.

        :param gender: The gender of the track to use in printing the scoreboard.
        """
        print('Scoreboard for track %s in season %s' % (gender, self.name))
        rank = 1
        scoreboard = self.get_scoreboard(gender)
        for points, stats in scoreboard:
            print('#%d. %s at %.2f points' % (rank, stats.player.name, stats.points))
            rank += 1
