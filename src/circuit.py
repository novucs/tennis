from hash_table import HashTable
from linked_list import List
from player import SeasonStats, CircuitStats
from season import Season
from user_input import next_string


class Circuit:
    def __init__(self, ordered_seasons=List(), seasons=HashTable(), men=HashTable(), women=HashTable(),
                 tournament_types=HashTable(), ranking_points=HashTable()):
        self.running = True
        self.seasons = seasons.clone()
        self.ordered_seasons = ordered_seasons.clone()
        self.current_season = self.ordered_seasons.last()
        self.men = men.clone()
        self.women = women.clone()
        self.tournament_types = tournament_types.clone()
        self.ranking_points = ranking_points.clone()

    def next_incomplete_season(self):
        if self.current_season is not None and not self.current_season.complete:
            return self.current_season

        while True:
            season_name = next_string('Enter a new season name', 'season%d' % (len(self.seasons) + 1))

            if season_name is None:
                continue

            if self.seasons.find(season_name) is not None:
                print('A season by that name already exists')
                continue

            previous_season = self.current_season
            men_season_stats = self.create_season_stats(season_name, self.men)
            women_season_stats = self.create_season_stats(season_name, self.women)
            men_scoreboard = self.create_scoreboard(men_season_stats)
            women_scoreboard = self.create_scoreboard(women_season_stats)
            season = Season(self, previous_season, season_name, False, men_season_stats, women_season_stats,
                            men_scoreboard, women_scoreboard)

            self.current_season = season
            self.seasons.insert(season_name.lower(), season)
            self.ordered_seasons.append(season)
            return self.current_season

    @staticmethod
    def create_scoreboard(profiles):
        scoreboard = [None] * len(profiles)
        i = 0
        for _, player in profiles:
            scoreboard[i] = player
            i += 1
        return scoreboard

    @staticmethod
    def create_season_stats(season_name, profiles):
        target = HashTable()

        for player_name, player_profile in profiles:
            circuit_stats: CircuitStats = player_profile.stats
            season_stats = SeasonStats(player_profile, circuit_stats)
            circuit_stats.season_stats.insert(season_name, season_stats)
            target.insert(player_name, season_stats)

        return target

    def get_players(self, gender):
        return self.men if gender == 'men' else self.women
