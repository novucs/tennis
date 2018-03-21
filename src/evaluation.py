import cProfile, pstats, io
import random

from hash_table import HashTable
from linked_list import List
from pipe_sort import Sorter
from ranked_tree import Tree


def profile(func):
    def wrapper(*args, **kwargs):
        # Create the profiler.
        profiler = cProfile.Profile()

        # Enable the profiler, run the function, then disable the profiler.
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        # Get the stats for the profile.
        output = io.StringIO()
        stats = pstats.Stats(profiler, stream=output).sort_stats('cumulative')
        stats.print_stats()

        # Print the profiling result stats.
        print('Results for function: %s' % func.__name__)
        print(output.getvalue())

        return result

    return wrapper


@profile
def bubble_sort(array):
    half = int(len(array) / 2)
    for i in range(0, half):
        for j in range(0, half):
            if array[i] > array[j]:
                array[i], array[j] = array[j], array[i]


@profile
def pipe_sort(sorter):
    sorter.sort()


def bubble_vs_pipe():
    print('-' * 120)
    print('Pitting bubble sort against pipe sort.')
    print('Pipe sort is expected to be faster.')
    print('Anywhere entire collection sorts are required, pipe sort is used for this reason.')
    print('Bubble Sort = Compares and swaps neighbours, average O(n^2)')
    print('Pipe Sort = Merges data runs, average O(n log n)')
    print('-' * 120)
    array = []
    sorter = Sorter()
    for i in range(0, 5000):
        value = random.randint(0, 5000)
        array.append(value)
        sorter.consume(value)
    bubble_sort(array)
    pipe_sort(sorter)


@profile
def pipe_single(array, element):
    array.append(element)
    sorter = Sorter()
    for element in array:
        sorter.consume(element)
    sorter.sort()


@profile
def tree_single(tree, element):
    tree.insert(element, element)


def pipe_vs_tree():
    print('-' * 120)
    print('Pitting trees against pipe sort for single modification ranking.')
    print('The tree is expected to be faster.')
    print('Season ranking uses trees for this reason.')
    print('Pipe Sort = Uses runs then merges, average O(n log n)')
    print('Trees = Binary search then insertion, average O(log n)')
    print('-' * 120)
    array = []
    tree = Tree()
    for i in range(0, 5000):
        value = random.randint(0, 5000)
        array.append(value)
        tree.insert(value, value)

    value = random.randint(0, 5000)
    pipe_single(array, value)
    tree_single(tree, value)


@profile
def tree_multiple(array):
    tree = Tree()
    for element in array:
        tree.insert(element, element)


@profile
def list_multiple(array):
    linked_list = List()
    for element in array:
        linked_list.append(element)


def tree_vs_list():
    print('-' * 120)
    print('Pitting trees against doubly linked lists for adding new, sorted values.')
    print('The doubly linked list is expected to be faster.')
    print('Tournament ranking uses doubly linked lists for this reason.')
    print('Trees = Binary search then insertion, average O(log n)')
    print('Lists = Append front (push), average O(1)')
    print('-' * 120)
    array = []
    for i in range(0, 5000):
        value = random.randint(0, 5000)
        array.append(value)
    array.sort()
    tree_multiple(array)
    list_multiple(array)


@profile
def list_search(linked_list):
    for i in range(0, 10000, 20):
        linked_list.contains(i)


@profile
def tree_search(tree):
    for i in range(0, 10000, 20):
        tree.find(i)


@profile
def hash_search(hash_table):
    for i in range(0, 10000, 20):
        hash_table.find(i)


def list_vs_tree_vs_hash():
    print('-' * 120)
    print('Pitting lists, trees and hash tables against each other for search.')
    print('Hashing is expected to be the fastest, followed by trees, then by lists.')
    print('All player statistics use hash tables for indexing.')
    print('Lists = Sequential search, average O(n)')
    print('Trees = Binary search, average O(log n)')
    print('Hash Tables = Hashing, average O(1)')
    print('-' * 120)
    linked_list = List()
    tree = Tree()
    hash_table = HashTable()
    for i in range(0, 5000):
        value = random.randint(0, 5000)
        linked_list.append(value)
        tree.insert(value, True)
        hash_table.insert(value, True)
    list_search(linked_list)
    tree_search(tree)
    hash_search(hash_table)


def main():
    bubble_vs_pipe()
    pipe_vs_tree()
    tree_vs_list()
    list_vs_tree_vs_hash()


if __name__ == '__main__':
    main()
