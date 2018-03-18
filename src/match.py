from config import MAX_PLAYERS
from hash_table import HashTable
from ranked_tree import Tree
from user_input import next_string, next_int, next_bool


class Track:
    def __init__(self, name, track_round, stats, remaining, winning_score, forfeit_score, scoreboard, previous_stats,
                 previous_season_scoreboard):
        self.name = name
        self.round = track_round
        self.stats = stats
        self.remaining = remaining
        self.winning_score = winning_score
        self.forfeit_score = forfeit_score
        self.scoreboard: Tree = scoreboard
        self.previous_stats = previous_stats
        self.previous_season_scoreboard = previous_season_scoreboard


class Match:
    def __init__(self, track: Track, player_a=None, score_a=None, player_b=None, score_b=None):
        self.track = track
        self.player_name_a = player_a
        self.score_a = score_a
        self.player_name_b = player_b
        self.score_b = score_b

    def run(self, winning_score, player_stats: HashTable):
        if self.player_name_a is not None:
            # Validate players, both must still be able to play this round.
            self.player_name_a = self.ensure_player_exists(self.player_name_a, player_stats)
            # Prevent players playing any more matches this round, and load their
            # relevant tournament stats for returning later.
            player_stats_a = player_stats.delete(self.player_name_a)
            self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
            self.ensure_players_compatible(player_stats)

            player_stats_b = player_stats.delete(self.player_name_b)
        else:
            self.player_name_a = next_string('Enter player A')
            self.player_name_a = self.ensure_player_exists(self.player_name_a, player_stats)
            player_stats_a = player_stats.delete(self.player_name_a)
            self.score_a = next_int('Enter score A')

            self.player_name_b = next_string('Enter player B')
            self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
            self.ensure_players_compatible(player_stats)

            player_stats_b = player_stats.delete(self.player_name_b)
            self.score_b = next_int('Enter Score B')

        # Validate scores:
        # - Only one may be a winner.
        # - Both must be no bigger than the winning score.
        # - Both must be no smaller than zero.
        self.validate_scores(winning_score)

        # Find and return the winner and loser with their scores.
        if self.score_a > self.score_b:
            return player_stats_a, self.score_a, player_stats_b, self.score_b
        else:
            return player_stats_b, self.score_b, player_stats_a, self.score_a

    def ensure_players_compatible(self, player_stats):
        # Do nothing if we're on the first season.
        if self.track.previous_season_scoreboard is None:
            return

        if self.track.round == 1:
            # Ensure both players were not ranked the same half for the previous seasons.
            player_a_high_ranked: bool = self.is_high_ranked(self.player_name_a)
            player_b_high_ranked: bool = self.is_high_ranked(self.player_name_b)

            # Check if both players are similarly ranked ...
            while player_a_high_ranked == player_b_high_ranked:
                # ... get user to re-enter different user so they're not
                #     similarly ranked.
                print("Players may not play each other as they're both %s ranked" %
                      ("high" if player_a_high_ranked else "low"))
                self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
                player_b_high_ranked: bool = self.is_high_ranked(self.player_name_b)
        elif self.track.previous_stats is not None:
            # Ensure both players were not winners for the previous seasons tournament.
            player_a_winner: bool = self.is_previous_winner(self.player_name_a)
            player_b_winner: bool = self.is_previous_winner(self.player_name_b)

            while player_a_winner and player_b_winner:
                self.player_name_b = next_string('Enter player B')
                self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
                player_b_winner: bool = self.is_previous_winner(self.player_name_b)

    def is_previous_winner(self, player_name):
        return self.track.previous_stats.find(player_name).round > self.track.round

    def is_high_ranked(self, player_name):
        return self.track.previous_season_scoreboard.rank(player_name) > (MAX_PLAYERS / 2)

    def validate_scores(self, winning_score):
        while True:
            self.score_a = self.validate_score(self.score_a, winning_score)
            self.score_b = self.validate_score(self.score_b, winning_score)

            if self.score_a == winning_score and self.score_b == winning_score:
                print('Both players cannot be winners')
                self.next_scores(winning_score)
                continue

            if self.score_a == winning_score or self.score_b == winning_score:
                return

            injured = next_bool('Incomplete scores. Has a player been injured?', True)

            if injured:
                player_a_injured = next_bool('Was %s injured?' % self.player_name_a, True)

                if player_a_injured:
                    print('%s was injured and has been withdrawn from the tournament' % self.player_name_a)
                    self.score_a = self.track.forfeit_score
                    self.score_b = self.track.winning_score
                else:
                    print('%s was injured and has been withdrawn from the tournament' % self.player_name_b)
                    self.score_a = self.track.winning_score
                    self.score_b = self.track.forfeit_score

                return

            print('Please re-enter the scores so they are complete')
            self.next_scores(winning_score)

    def next_scores(self, winning_score):
        self.score_a = self.next_score(self.player_name_a)
        self.score_a = self.validate_score(self.score_a, winning_score)
        self.score_b = self.next_score(self.player_name_b)
        self.score_b = self.validate_score(self.score_b, winning_score)

    @staticmethod
    def next_score(player_name):
        return next_int('Enter score for player %s' % player_name)

    def validate_score(self, score, winning_score):
        if score > winning_score or score < 0:
            message = 'Invalid score for round %s with %d, vs %s with %d. Culprit: %d' % \
                      (self.player_name_a, self.score_a, self.player_name_b, self.score_b, score)
            print(message)

        while score > winning_score or score < 0:
            score = next_int('Score must be between 0 and %d, try again' % winning_score)

        return score

    @staticmethod
    def ensure_player_exists(player_name, player_stats):
        while True:
            if player_stats.find(player_name) is None:
                print('\n=== WARNING ===')
                print('%s cannot play this match.' % player_name)
                print('Valid players:')
                for name, _ in player_stats:
                    print('- %s' % name)
                player_name = next_string('Enter a valid player to take their place')
                print()
            else:
                return player_name
