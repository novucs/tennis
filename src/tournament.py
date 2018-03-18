import math

from config import MAX_ROUNDS, apply_multiplier, MAX_PLAYERS
from hash_table import HashTable
from linked_list import List
from match import Track, Match
from player import TournamentStats
from user_input import next_gender, next_bool, next_input_type, FILE, next_string, MALE


class TournamentType:
    def __init__(self, name: str, prizes: HashTable, difficulty: float):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty


class Tournament:
    def __init__(self, season, tournament_type: TournamentType, previous, complete):
        self.type = tournament_type
        self.season = season
        self.previous = previous
        self.complete = complete
        self.men_track: Track = None
        self.women_track: Track = None

    def run(self):
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
            self.update_points(winner, track)
            track.round += 1
            self.print_scoreboard(track.name)
            return

        print('Winners for round %d:' % track.round)

        for name, stats in winners:
            print('- %s' % name)

        track.remaining = winners
        track.round += 1

    def update_points(self, stats: TournamentStats, track: Track):
        rank = MAX_PLAYERS - len(track.scoreboard)
        points = self.season.circuit.ranking_points.find(rank, 0) * self.type.difficulty

        if track.previous_stats is None:
            points *= stats.multiplier
        else:
            previous_stats: TournamentStats = track.previous_stats.find(stats.player.name)
            if stats.round_achieved >= previous_stats.round_achieved:
                points *= stats.multiplier

        stats.add_points(points)
        track.scoreboard.insert(stats.points, stats)

    def get_track(self, gender):
        return self.men_track if gender == 'men' else self.women_track

    def print_scoreboard(self, gender):
        track: Track = self.get_track(gender)

        if track.round <= MAX_ROUNDS:
            print('Track %s incomplete for tournament %s in season %s' % (gender, self.type.name, self.season.name))
            return

        print('Scoreboard for track %s in tournament %s' % (track.name, self.type.name))
        rank = 1

        for points, stats in track.scoreboard:
            prize = self.type.prizes.find(rank, '0')
            print('#%d. %s at %d points wins £%s' % (rank, stats.player.name, points, prize))
            rank += 1
