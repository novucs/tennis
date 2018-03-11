from hash_table import HashTable
from player import SeasonStats
from season import Season
from user_input import next_string


class Circuit:
    def __init__(self, current_season=None, seasons=HashTable(), men=HashTable(), women=HashTable(),
                 tournament_types=HashTable(), ranking_points=HashTable()):
        self.running = True
        self.current_season = current_season
        self.seasons = seasons
        self.men = men
        self.women = women
        self.tournament_types = tournament_types
        self.ranking_points = ranking_points

    def next_incomplete_season(self):
        if self.current_season is not None and not self.current_season.complete:
            return self.current_season

        while True:
            season_name = next_string('Enter a new season name')

            if season_name is None:
                continue

            if self.seasons.find(season_name) is not None:
                print('A season by that name already exists')
                continue

            previous_season = self.current_season
            men_season_stats = self.create_season_stats(self.men)
            women_season_stats = self.create_season_stats(self.women)
            season = Season(self, previous_season, season_name, False, men_season_stats, women_season_stats)

            self.current_season = season
            self.seasons.insert(season_name.lower(), season)
            return self.current_season

    @staticmethod
    def create_season_stats(profiles):
        target = HashTable()

        for player_name, player_profile in profiles:
            circuit_stats = player_profile.stats
            season_stats = SeasonStats(player_profile, circuit_stats)
            target.insert(player_name, season_stats)

        return target
