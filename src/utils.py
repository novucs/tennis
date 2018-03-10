#!/usr/bin/env python

"""

General utilities used by both tennis player ranking solutions.

"""

import os

# import numpy as np
from hash_table import HashTable
from linked_list import List
from main import *


def save_tournament(tournament: Tournament):
    tournament_folder = "../output/%s/%s/" % (tournament.season.name, tournament.name)
    men_file = prepare_persist(tournament_folder + "men.csv")
    women_file = prepare_persist(tournament_folder + "women.csv")
    progress_file = prepare_persist(tournament_folder + "progress.csv")
    stats_file = prepare_persist(tournament_folder + "stats.csv")

    with open(men_file, "rw") as the_file:
        for name, profile in tournament.men_stats:
            the_file.write("%s,%d\n" % (name, profile.temp.multiplier))

    with open(women_file, "rw") as the_file:
        for name, profile in tournament.women_stats:
            the_file.write("%s,%d\n" % (name, profile.temp.multiplier))

    with open(progress_file, "rw") as the_file:
        the_file.write("%s,%s\n" % (tournament.round.name, tournament.complete))

    with open(stats_file, "rw") as the_file:
        for name, profile in tournament.men_stats:
            stats = tournament.stats.find(name)

            the_file.write(
                "%s,%d,%d,%d,\"%s\"\n" % (name, profile.temp.round, profile.temp.wins, profile.temp.losses, ""))


def prepare_persist(file_name):
    # Delete file if already exists.
    if os.path.isfile(file_name):
        os.remove(file_name)

    # Ensure directory exists.
    directory_name = os.path.dirname(os.path.realpath(file_name))
    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)

    return file_name
