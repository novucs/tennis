import numpy as np

from linked_list import List


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.key == other.key
        else:
            return self.key == other

    def __str__(self):
        return "(" + str(self.key) + ", " + str(self.value) + ")"


class HashTable:
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
        for entry in self:
            target += str(entry) + ", "
        target = target[:-2] + "]"
        return target

    def find(self, key):
        if self._size == 0:
            return None

        code = id(key) % self._table.size
        return self._table[code].find(key)

    def insert(self, key, value):
        self.__ensure_capacity(self._size + 1)

        node = Node(key, value)
        code = id(key) % self._table.size
        replaced = self._table[code].replace(node)

        if replaced:
            return False

        self._table[code].append(node)
        self._size += 1
        return True

    def delete(self, key):
        if self._size == 0:
            return False

        code = id(key) % self._table.size

        if self._table[code].delete(key):
            self._size -= 1
            return True
        else:
            return False

    def __ensure_capacity(self, min_capacity):
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
