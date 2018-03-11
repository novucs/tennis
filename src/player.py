from hash_table import HashTable


class CircuitStats:
    def __init__(self, player, wins=0, losses=0, scores=HashTable(), season_stats=HashTable()):
        self.player = player
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>
        self.season_stats = season_stats  # <season name, season stats>


class SeasonStats:
    def __init__(self, player, circuit: CircuitStats, points=0.0, wins=0, losses=0, scores=HashTable(),
                 tournament_stats=HashTable()):
        self.player = player
        self.circuit = circuit
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>
        self.tournament_stats = tournament_stats  # <tournament name, tournament stats>


class TournamentStats:
    def __init__(self, player, season: SeasonStats, round_achieved=1, multiplier=1.0, points=0.0, wins=0, losses=0,
                 scores=HashTable()):
        self.player = player
        self.season = season
        self.round_achieved = round_achieved
        self.multiplier = multiplier
        self.points = points
        self.wins = wins
        self.losses = losses
        self.scores = scores  # <score, count>

    def add_points(self, points):
        self.points += points
        self.season.points += points

    def add_score(self, opponent_score, our_score):
        # Increment number of times player has had this score.
        count = self.scores.find((our_score, opponent_score), 0) + 1
        self.scores.insert((our_score, opponent_score), count)

    def win(self):
        self.wins += 1
        self.season.wins += 1
        self.season.circuit.wins += 1

    def loss(self):
        self.losses += 1
        self.season.losses += 1
        self.season.circuit.losses += 1


class Player:
    def __init__(self, name, stats: CircuitStats = None):
        self.name = name
        self.stats = stats
