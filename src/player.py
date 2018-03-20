from hash_table import HashTable


class CircuitStats:
    """Player's statistics for the entire circuit.

    Attributes:
        player: The player profile that owns these statistics.
        wins: The number of wins the player has overall in this circuit.
        losses: The number of losses the player has overall in this circuit.
        scores: All the score mappings the player has achieved this circuit.
        season_stats: All statistics for each season the player has.
    """

    def __init__(self, player, wins=0, losses=0, scores=HashTable(), season_stats=HashTable()):
        self.player = player
        self.wins = wins
        self.losses = losses
        self.scores = scores.clone()  # <score, count>
        self.season_stats = season_stats.clone()  # <season name, season stats>

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.player)

    def add_score(self, our_score, opponent_score):
        """Adds a score a player has achieved at the end of a match.

        :param our_score: The players score.
        :param opponent_score: The opponents score.
        """
        count = self.scores.find((our_score, opponent_score), 0) + 1
        self.scores.insert((our_score, opponent_score), count)


class SeasonStats:
    """Player's statistics for a season.

    Attributes:
        player: The player profile that owns these statistics.
        circuit: The circuit statistics this season is part of.
        points: The total points the player has achieved this season.
        wins: The number of wins the player has overall in this season.
        losses: The number of losses the player has overall in this season.
        scores: All the score mappings the player has achieved this season.
        tournament_stats: All statistics for each tournament in this season the player has.
    """

    def __init__(self, player, circuit: CircuitStats, points=0.0, wins=0, losses=0, scores=HashTable(),
                 tournament_stats=HashTable()):
        self.player = player
        self.circuit = circuit
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores.clone()  # <score, count>
        self.tournament_stats = tournament_stats.clone()  # <tournament name, tournament stats>

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.player)

    def add_score(self, our_score, opponent_score):
        """Adds a score a player has achieved at the end of a match.

        :param our_score: The players score.
        :param opponent_score: The opponents score.
        """
        count = self.scores.find((our_score, opponent_score), 0) + 1
        self.scores.insert((our_score, opponent_score), count)
        self.circuit.add_score(our_score, opponent_score)


class TournamentStats:
    """Player's statistics for a tournament.

    Attributes:
        player: The player profile that owns these statistics.
        season: The season statistics this tournament is part of.
        round_achieved: The round the player achieved this tournament.
        multiplier: The multiplier the player has achieved this tournament.
        points: The points the player has achieved this tournament.
        wins: The number of wins the player has overall in this tournament.
        losses: The number of losses the player has overall in this tournament.
        scores: All the score mappings the player has achieved this tournament.
    """

    def __init__(self, player, season: SeasonStats, round_achieved=1, multiplier=1.0, points=0.0, wins=0, losses=0,
                 scores=HashTable()):
        self.player = player
        self.season = season
        self.round_achieved = round_achieved
        self.multiplier = multiplier
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores.clone()  # <score, count>

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.player)

    def add_points(self, points):
        """Adds points to the players total stats.

        :param points: The points to add.
        """
        self.points += points
        self.season.points += points

    def add_score(self, our_score, opponent_score):
        """Adds a score a player has achieved at the end of a match.

        :param our_score: The players score.
        :param opponent_score: The opponents score.
        """
        # Increment number of times player has had this score.
        count = self.scores.find((our_score, opponent_score), 0) + 1
        self.scores.insert((our_score, opponent_score), count)
        self.season.add_score(our_score, opponent_score)

    def win(self):
        """Updates the players statistics for when they have won the round,
        incrementing the tournament, season and circuit wins. Also bumps the
        round this player has achieved.
        """
        self.wins += 1
        self.season.wins += 1
        self.season.circuit.wins += 1
        self.round_achieved += 1

    def loss(self):
        """Updates the players statistics for when they have lost the round,
        decrementing the tournament, season and circuit losses.
        """
        self.losses += 1
        self.season.losses += 1
        self.season.circuit.losses += 1


class Player:
    """The main player profile, stores both the players name and all their
    statistics throughout the entire circuit they are a part of.

    Attributes:
        name: The name of the player.
        stats: The statistics the player has achived throughout the circuit
               they are in.
    """

    def __init__(self, name, stats: CircuitStats = None):
        self.name = name
        self.stats = stats

    def __repr__(self):
        return '%s' % self.name
