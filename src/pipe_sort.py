#!/usr/bin/env python

"""

PipeSort. An optimal sorting algorithm for binding to data streams. Makes use
of a combination of natural "runs" in data and merges each run to the next
closest in size.

"""

import numpy as np

from linked_list import List
from ranked_tree import Tree


class Sorter:
    """An optimal pipe-line sorting implementation.

    Attributes:
        _compare: How two elements should be compared.
        _runs: The tree of runs, sorted by their size.
        _run: The current run to append to.
        _previous: The previous element consumed by the pipe line.
        consume: The function pointer to however the next element should be
                 consumed.
    """

    def __init__(self, comparator=lambda a, b: a - b):
        self._compare = comparator
        self._runs = Tree()
        self._run = List()
        self._previous = None
        self.consume = self.__run_init

    def __run_init(self, x):
        """Initializes the first run.

        :param x: The element to append to the run.
        :return: None
        """
        self._run.append(x)
        self._previous = x
        self.consume = self.__run_front

    def __run_front(self, x):
        """Continues appending to the run if still running upwards in value.
        Otherwise changes state to start creating reverse runs.

        :param x: The element to append to the run.
        :return: None
        """
        if self._compare(x, self._previous) < 0:
            self._runs.insert(len(self._run), self._run)
            self._run = List()
            self._run.append(x)
            self._previous = x
            self.consume = self.__run_back
        else:
            self._run.append(x)
            self._previous = x

    def __run_back(self, x):
        """Continues appending to the front of the run if still running in
        reverse. Otherwise changes state to start creating forwards runs.

        :param x: The element to append to the run.
        :return: None
        """
        if self._compare(x, self._previous) > 0:
            self._runs.insert(len(self._run), self._run)
            self._run = List()
            self._run.append(x)
            self._previous = x
            self.consume = self.__run_front
        else:
            self._run.append_front(x)
            self._previous = x

    def sort(self):
        """Collects all runs and iteratively merges each, smallest first.

        :return: The sorted array.
        """
        # Collect the final run.
        self._runs.insert(len(self._run), self._run)
        self._run = List()
        self.consume = self.__run_init

        # Iteratively merge each of the runs, smallest first.
        while len(self._runs) > 1:
            new_runs = Tree()
            iterator = iter(self._runs)

            run_a = next_run(iterator)
            run_b = next_run(iterator)

            while run_a is not None and run_b is not None:
                merged = self._merge(run_a, run_b)
                new_runs.insert(len(merged), merged)
                run_a = next_run(iterator)
                run_b = next_run(iterator)

            if run_a is not None:
                new_runs.insert(len(run_a), run_a)

            self._runs = new_runs

        sorted_run = next_run(iter(self._runs))

        # Convert the run to an array if currently a linked list.
        if isinstance(sorted_run, List):
            iterator = iter(sorted_run)
            length = len(sorted_run)
            sorted_run = np.empty(length, dtype=object)

            for i in range(0, length):
                sorted_run[i] = next(iterator)

        # Return the final sorted run.
        return sorted_run

    def _merge(self, run_a, run_b):
        """Merges two runs.

        :param run_a: The first run.
        :param run_b: The second run.
        :return: Both runs, A and B, merged.
        """
        merged = np.empty(len(run_a) + len(run_b), dtype=object)
        iterator_a = iter(run_a)
        iterator_b = iter(run_b)
        element_a = next(iterator_a, None)
        element_b = next(iterator_b, None)
        index = 0

        while element_a is not None and element_b is not None:
            if self._compare(element_a, element_b) > 0:
                merged[index] = element_b
                element_b = next(iterator_b, None)
            else:
                merged[index] = element_a
                element_a = next(iterator_a, None)

            index += 1

        while element_a is not None:
            merged[index] = element_a
            element_a = next(iterator_a, None)
            index += 1

        while element_b is not None:
            merged[index] = element_b
            element_b = next(iterator_b, None)
            index += 1

        return merged


def next_run(iterator):
    """Finds the next run in the tree iterator.

    :param iterator: The "runs" tree iterator.
    :return: The next element in the tree iterator, otherwise None.
    """
    run_tuple = next(iterator, None)
    return run_tuple[1] if run_tuple else None
