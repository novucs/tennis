#!/usr/bin/env python

"""

A hash table with linked list buckets.

"""

import numpy as np

from linked_list import List


class Node:
    """A node or entry in the hash table.

    Attributes:
        key: The key to be used as an index in the table.
        value: The value, an extra object to store anything relating to the key
               that will not be used for indexing.
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __eq__(self, other):
        if other is None:
            return False
        elif isinstance(other, Node):
            return self.key == other.key
        else:
            return self.key == other

    def __hash__(self):
        return hash(self.key)


class HashTable:
    """A hash table with linked list buckets.

    Attributes:
        _table: The table, an array of linked lists.
        _size: The number of elements stored in this hash table.
    """

    def __init__(self, initial_capacity=10):
        self._table = np.empty(initial_capacity, dtype=object)

        for i in range(0, initial_capacity):
            self._table[i] = List()

        self._size = 0

    def __len__(self):
        return self._size

    def __getitem__(self, key):
        return self.find(key)

    def __delitem__(self, key):
        return self.delete(key)

    def __setitem__(self, key, value):
        return self.insert(key, value)

    def __iter__(self):
        for i in range(0, self._table.size):
            for node in self._table[i]:
                yield (node.key, node.value)

    def __str__(self):
        if self._size == 0:
            return "[]"
        target = "["
        for key, value in self:
            target += "(" + str(key) + ", " + str(value) + "), "
        target = target[:-2] + "]"
        return target

    def find(self, key, default=None):
        """Finds the value associated with the provided key.

        :param key: The key to search with.
        :param default: The value to return if not found.
        :return: The associated value if found, otherwise default.
        """
        if self._size == 0:
            return default

        code = hash(key) % self._table.size
        node = self._table[code].find(key)

        if node is None:
            return default

        return node.value

    def insert(self, key, value):
        """Inserts a new key and value into the hash table.

        :param key: The key to index with.
        :param value: The value to store under the provided key.
        :return: The old value associated with this key if previously existed,
                 otherwise None.
        """
        self.__ensure_capacity(self._size + 1)

        node = Node(key, value)
        code = hash(key) % self._table.size
        old_node = self._table[code].replace(node)

        if old_node is not None:
            return old_node.value

        self._table[code].append(node)
        self._size += 1
        return None

    def delete(self, key):
        """Deletes the entry associated with the provided key.

        :param key: The key of the entry to delete.
        :return: The old value if existed, otherwise None.
        """
        if self._size == 0:
            return False

        code = hash(key) % self._table.size
        old_node = self._table[code].delete(key)

        if old_node is None:
            return None
        else:
            self._size -= 1
            return old_node.value

    def __ensure_capacity(self, min_capacity):
        """Ensures the number of possible positions in the hash table is at
        least as much as the number of nodes in the table.

        :param min_capacity: The minimum capacity required of the table.
        :return: None
        """
        if self._table.size >= min_capacity:
            return

        old_table = self._table
        new_capacity = int((self._table.size * 3) / 2) + 1

        if new_capacity < min_capacity:
            new_capacity = min_capacity

        self._table = np.empty(new_capacity, dtype=object)

        for i in range(0, new_capacity):
            self._table[i] = List()

        self._size = 0

        for bucket in old_table:
            for node in bucket:
                self.insert(node.key, node.value)
