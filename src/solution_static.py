#!/usr/bin/env python

"""

Solution for static data.

"""

from random import randint
from random import seed

from hash_table import HashTable
from pipe_sort import Sorter

seed(1)

players_by_name = HashTable()


def score_comparator(player_a, player_b):
    return player_a.score - player_b.score


if __name__ == '__main__':
    print("Solution - Static")
    sorter = Sorter()
    to_sort = []
    target = []
    for _ in range(0, 10):
        # Generate sample data.
        for _ in range(0, 10):
            to_sort.append(randint(0, 100))

    # Consume the sample data.
    for element in to_sort:
        sorter.consume(element)

    to_sort.clear()
    target = sorter.sort()

    # Finalize sort and print the results.
    print(str(target))
