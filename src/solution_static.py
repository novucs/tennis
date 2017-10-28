#!/usr/bin/env python

"""

Solution for static data.

"""

from random import randint
from random import seed

from pipe_sort import Sorter

seed(1)

if __name__ == '__main__':
    print("Solution - Static")
    to_sort = []

    for _ in range(0, 500):
        to_sort.append(randint(0, 100))

    sorter = Sorter()

    # Consume the sample data.
    for element in to_sort:
        sorter.consume(element)

    # Finalize sort and print the results.
    target = sorter.sort()
    print(str(target))
