from hash_table import HashTable
from linked_list import List
from player import SeasonStats, CircuitStats
from ranked_tree import Tree
from season import Season
from user_input import next_string


class Circuit:
    """A circuit for the tennis tournament system. This holds two tracks of
    players, all the tournaments played, and the seasons and statistics gained
    over all previous matches.

    Attributes:
        ordered_seasons: All seasons in order of first played to last played.
        seasons: Season mappings by name.
        men: Male player mappings by name.
        women: Female player mappings by name.
        tournament_types: All types of tournaments, mapped by name.
        ranking_points: The number of points earned for a given rank, mapped by
                        rank.
    """

    def __init__(self, ordered_seasons=List(), seasons=HashTable(), men=HashTable(), women=HashTable(),
                 tournament_types=HashTable(), ranking_points=List()):
        self.running = True
        self.seasons = seasons.clone()
        self.ordered_seasons = ordered_seasons.clone()
        self.current_season = self.ordered_seasons.last()
        self.men = men.clone()
        self.women = women.clone()
        self.tournament_types = tournament_types.clone()
        self.ranking_points = ranking_points.clone()

    def next_incomplete_season(self):
        """Fetches the next incomplete season for this circuit. Asks the user
        to create a new one if either the previous season is complete or does
        not exist.

        :return: the next incomplete season.
        """
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
        """Creates a scoreboard for all player profiles.

        :param profiles: The player profiles used add to the new scoreboard.
        :return: The newly created, unordered, scoreboard.
        """
        scoreboard = Tree(lambda a, b: b - a)
        for name, stats in profiles:
            scoreboard.insert(stats.points, stats)
        return scoreboard

    @staticmethod
    def create_season_stats(season_name, profiles):
        """Creates player statistics for a given season, and adds them all into
        the players circuit profiles.

        :param season_name: The name of the season to create the statistics for.
        :param profiles: The player circuit profiles to create season
                         statistics for.
        :return: The newly created player season statistic mappings.
        """
        target = HashTable()

        for player_name, player_profile in profiles:
            circuit_stats: CircuitStats = player_profile.stats
            season_stats = SeasonStats(player_profile, circuit_stats)
            circuit_stats.season_stats.insert(season_name, season_stats)
            target.insert(player_name, season_stats)

        return target

    def get_players(self, gender):
        """Gets the player circuit mappings for a given gender.

        :param gender: The gender of the players to get.
        :return: The players.
        """
        return self.men if gender == 'men' else self.women
