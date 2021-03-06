from config import MAX_PLAYERS
from hash_table import HashTable
from linked_list import List
from user_input import next_string, next_int, next_bool


class Track:
    """A track for a tournament, this holds all statistics and ranking for
    players of a given gender.

    Attributes:
        name: The name of the track, this represents the gender this track uses.
        track_round: The round this track is part of.
        stats: The statistics mappings of player name to tournament statistics.
        remaining: The remaining players in this round.
        winning_score: The score required to win a match.
        forfeit_score: The score given to a player withdrawn from a match.
        scoreboard: The tournament scoreboard for this track.
        previous_stats: The player statistics of this track for the previous
                        season.
        previous_season_scoreboard: The scoreboard of the previous season for
                                    this track.
    """

    def __init__(self, name, track_round, stats, remaining, winning_score, forfeit_score, scoreboard, previous_stats,
                 previous_season_scoreboard):
        self.name = name
        self.round = track_round
        self.stats = stats
        self.remaining = remaining
        self.winning_score = winning_score
        self.forfeit_score = forfeit_score
        self.scoreboard: List = scoreboard
        self.previous_stats = previous_stats
        self.previous_season_scoreboard = previous_season_scoreboard
        self.player_count = MAX_PLAYERS

        # Find and cache all the players considered highly ranked from the
        # previous season scoreboard.
        self.high_ranked = HashTable()

        if self.previous_season_scoreboard is not None:
            rank = 0
            for points, stats in self.previous_season_scoreboard:
                rank += 1
                if rank > (MAX_PLAYERS / 2):
                    break
                self.high_ranked.insert(stats.player.name, True)

        self.previous_winners = HashTable()
        self.previous_losers = HashTable()

    def update_previous_winners(self):
        """Updates the track with the previous winners and losers for the
        current round.
        """
        if self.previous_stats is None:
            return

        self.previous_losers = HashTable()
        self.previous_winners = HashTable()

        for name, stats in self.previous_stats:
            if self.remaining.find(name) is None:
                continue

            if stats.round_achieved > self.round:
                self.previous_winners.insert(name, stats)
            else:
                self.previous_losers.insert(name, stats)


class Match:
    """A single match for a track in the tournament, provides helper functions
    to ensure the two participants and their scores are valid.

    Attributes:
        track: The track this match is taking place in.
        player_a: The first player's name taking part in this match.
        score_a: The first player's score.
        player_b: The second player's name taking part in this match.
        score_b: The second player's score.
    """

    def __init__(self, track: Track, player_a=None, score_a=None, player_b=None, score_b=None):
        self.track = track
        self.player_name_a = player_a
        self.score_a = score_a
        self.player_name_b = player_b
        self.score_b = score_b

    def run(self, winning_score, player_stats: HashTable):
        """Runs a match, ensuring all scores and names are valid.

        :param winning_score: The winning score one player must achieve.
        :param player_stats: The stats of all the remaining players in this
                             round.
        :return: Winners stats and their score, then the looser stats and
                 their score.
        """
        if self.player_name_a is not None and self.score_a is None:
            # Validate players, both must still be able to play this round.
            self.player_name_a = self.ensure_player_exists(self.player_name_a, player_stats)
            # Prevent players playing any more matches this round, and load their
            # relevant tournament stats for returning later.
            player_stats_a = player_stats.delete(self.player_name_a)
            self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
            self.ensure_players_compatible(player_stats)
            player_stats_b = player_stats.delete(self.player_name_b)
            print('%s vs %s' % (self.player_name_a, self.player_name_b))
            self.score_a = next_int("Enter %s's score" % self.player_name_a)
            self.score_b = next_int("Enter %s's score" % self.player_name_b)
        elif self.player_name_a is not None:
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
        """Ensures players are compatible with the second season seeding rules.

        :param player_stats: The player statistics mappings for this round.
        """
        # Do nothing if we're on the first season.
        if self.track.previous_season_scoreboard is None:
            return

        if self.track.round == 1:
            # Ensure both players were not ranked the same half for the previous seasons.
            player_a_high_ranked: bool = self.track.high_ranked.find(self.player_name_a, False)
            player_b_high_ranked: bool = self.track.high_ranked.find(self.player_name_b, False)

            # Check if both players are similarly ranked ...
            while player_a_high_ranked == player_b_high_ranked:
                # ... get user to re-enter different user so they're not
                #     similarly ranked.
                print("Players %s and %s may not play each other as they're both %s ranked" %
                      (self.player_name_a, self.player_name_b, "high" if player_a_high_ranked else "low"))
                self.player_name_b = next_string('Enter player B')
                self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
                player_b_high_ranked: bool = self.track.high_ranked.find(self.player_name_b, False)

            self.track.high_ranked.delete(self.player_name_a)
            self.track.high_ranked.delete(self.player_name_b)
        elif self.track.previous_stats is not None:
            # Do not enforce match seeding when impossible to do so.
            if len(self.track.previous_winners) == 0 or len(self.track.previous_winners) == self.track.player_count:
                return

            # Ensure both players were not winners for the previous seasons tournament.
            player_a_winner: bool = self.is_previous_winner(self.player_name_a)
            player_b_winner: bool = self.is_previous_winner(self.player_name_b)

            while not (player_a_winner ^ player_b_winner):
                print("Players %s and %s may not play each other as they're "
                      "both %s of this tournament for the previous "
                      "season" % (self.player_name_a, self.player_name_b,
                                  'winners' if player_a_winner else 'losers'))
                self.player_name_b = next_string('Enter player B')
                self.player_name_b = self.ensure_player_exists(self.player_name_b, player_stats)
                player_b_winner: bool = self.is_previous_winner(self.player_name_b)

        # Remove previous winners from mapping, we're no longer using them.
        self.track.previous_winners.delete(self.player_name_a)
        self.track.previous_winners.delete(self.player_name_b)

    def is_previous_winner(self, player_name):
        """Checks if a player has won the current round in the previous season.

        :param player_name: The player name to check.
        """
        return self.track.previous_winners.find(player_name) is not None

    def validate_scores(self, winning_score):
        """Validates all scores so one person is the winner and no scores are
        out of bounds.

        :param winning_score: The score required to win this round.
        """
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
        """Fetch the next set of validated scores from the user.

        :param winning_score: The score required to win this round.
        """
        self.score_a = self.next_score(self.player_name_a)
        self.score_a = self.validate_score(self.score_a, winning_score)
        self.score_b = self.next_score(self.player_name_b)
        self.score_b = self.validate_score(self.score_b, winning_score)

    @staticmethod
    def next_score(player_name):
        """Fetches the next score from the user.

        :param player_name: The player name that achieved this score.
        """
        return next_int('Enter score for player %s' % player_name)

    def validate_score(self, score, winning_score):
        """Validates a score is within bounds.

        :param score: The score to validate.
        :param winning_score: The score required to win this round.
        :return: The validated score.
        """
        if score > winning_score or score < 0:
            message = 'Invalid score for round %s with %d, vs %s with %d. Culprit: %d' % \
                      (self.player_name_a, self.score_a, self.player_name_b, self.score_b, score)
            print(message)

        while score > winning_score or score < 0:
            score = next_int('Score must be between 0 and %d, try again' % winning_score)

        return score

    @staticmethod
    def ensure_player_exists(player_name, player_stats):
        """Ensures a player is allowed to play the current match.

        :param player_name: The player name to check.
        :param player_stats: All remaining players valid for this match.
        :return: The validated player name.
        """
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
