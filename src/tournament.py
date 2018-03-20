import math

from config import MAX_ROUNDS, apply_multiplier, MAX_PLAYERS, get_multiplier
from hash_table import HashTable
from linked_list import List
from match import Track, Match
from player import TournamentStats
from ranked_tree import Tree
from user_input import next_gender, next_bool, next_input_type, FILE, next_string, MALE


class TournamentType:
    """Represents a type of tournament, used for storing the configuration data
    from ../resources/tournaments.csv

    Attributes:
        name: The name of the tournament.
        prizes: The prizes to win, indexed by rank.
        difficulty: The difficulty multiplier.
    """

    def __init__(self, name: str, prizes: HashTable, difficulty: float):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty


class Tournament:
    """A tournament, held in the season.

    Attributes:
        type: The type of tournament this is.
        season: The season this tournament was held in.
        previous: The same type of tournament held last season.
        complete: True when the tournament is complete.
        men_track: The men's track for this tournament.
        women_track: The women's track for this tournament.
    """

    def __init__(self, season, tournament_type: TournamentType, previous, complete):
        self.type = tournament_type
        self.season = season
        self.previous = previous
        self.complete = complete
        self.men_track: Track = None
        self.women_track: Track = None

    def run(self):
        """Runs the tournament."""
        if self.complete:
            print("Tournament is already complete")
            return

        running = True

        while running:
            gender = next_gender('Select the track to play for the next round', self.men_track.round > MAX_ROUNDS)

            track = self.men_track if gender == MALE else self.women_track
            self.play_round(track)

            if self.men_track.round > MAX_ROUNDS and self.women_track.round > MAX_ROUNDS:
                self.complete = True
                print("Tournament is complete")
                return

            running = next_bool('Would you like to start the next round?', True)

    def play_round(self, track: Track):
        """Plays a round in the tournament for a track.

        :param track: The track that is playing this round.
        """
        if track.round > MAX_ROUNDS:
            print('This track is already complete')
            return

        print('Playing the %s\'s track' % track.name)
        input_type = next_input_type('How should data be entered?')
        winners = HashTable()
        winner = None
        matches = List()

        if input_type == FILE:
            # Get the file to load the round data from.
            default_round_file = '../resources/%s/%s/%s/round_%d.csv' % \
                                 (self.season.name, self.type.name.lower(), track.name, track.round)
            round_file = next_string('Enter file for round %d' % track.round, default_round_file)
            from loader import load_round
            matches = load_round(round_file, track)
        else:
            match_count = int(math.pow(2, MAX_ROUNDS - track.round))

            for i in range(0, match_count):
                match = Match(track)
                matches.append(match)

        track.update_previous_winners()

        # Run each match.
        for match in matches:
            # Find the winner and add them to the next batch.
            winner, winner_score, loser, loser_score = match.run(track.winning_score, track.remaining)
            winners.insert(winner.player.name, winner)
            winner: TournamentStats = winner
            loser: TournamentStats = loser

            # Update the winner profile.
            winner.win()
            winner.add_score(winner_score, loser_score)

            # Update the loser profile.
            loser.loss()
            loser.add_score(loser_score, winner_score)

            apply_multiplier(track.name, winner, loser_score)
            self.update_points(loser, track)

        if track.round == MAX_ROUNDS:
            print('Tournament %s successfully complete for the %s\'s track' % (self.type.name, track.name))
            print('Winner for the final round: %s' % winner.player.name)
            track.round += 1
            self.update_points(winner, track)
            self.print_scoreboard(track.name)
            return

        print('Winners for round %d:' % track.round)

        for name, stats in winners:
            print('- %s' % name)

        track.remaining = winners
        track.round += 1

    def update_points(self, stats: TournamentStats, track: Track):
        """Updates the points of a players stats once they've either lost the
        tournament, or the tournament has been complete.

        :param stats: The players statistics profile for this tournament.
        :param track: The track the player is in.
        """

        total_points = 0
        ranking_points_iterator = iter(self.season.circuit.ranking_points)
        opponent_scores_iterator = iter(stats.opponent_scores)
        previous = track.previous_stats

        for i in range(0, max(0, track.round - 1)):
            points = next(ranking_points_iterator)
            loser_score = next(opponent_scores_iterator)

            # Do not add semi-finals score to the winner.
            if track.round > MAX_ROUNDS and i == (MAX_ROUNDS - 2):
                continue

            multiplier = 1.0

            # Do not apply multiplier if player has not achieved at last as
            # much as the previous season.
            if previous is None or previous.find(stats.player.name).round_achieved >= track.round:
                multiplier = get_multiplier(track.name, loser_score)

            total_points += points * multiplier

        total_points *= self.type.difficulty

        season_scoreboard: Tree = self.season.get_scoreboard(track.name)
        season_scoreboard.delete(stats.season.points, stats.season)
        stats.add_points(total_points)
        season_scoreboard.insert(stats.season.points, stats.season)
        track.scoreboard.append_front(stats)

    def get_track(self, gender):
        """Gets the track of this tournament for a gender.

        :param gender: The gender of the track to get.
        :return the track.
        """
        return self.men_track if gender == 'men' else self.women_track

    def print_scoreboard(self, gender):
        """Prints a scoreboard for a track of this tournament.

        :param gender: The gender of the track.
        """
        track: Track = self.get_track(gender)

        if track.round <= MAX_ROUNDS:
            print('Track %s incomplete for tournament %s in season %s' % (gender, self.type.name, self.season.name))
            return

        print('Scoreboard for track %s in tournament %s' % (track.name, self.type.name))
        rank = 1

        for stats in track.scoreboard:
            prize = self.type.prizes.find(rank, '0')
            print('#%d. %s at %.2f points wins £%s' % (rank, stats.player.name, stats.points, prize))
            rank += 1
