#!/usr/bin/env python

"""

A doubly-linked list.

"""


class Node:
    def __init__(self, item):
        self.item = item
        self.left = None
        self.right = None


class List:
    def __init__(self):
        self._first = None
        self._last = None
        self._size = 0

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        return self.select(index)

    def __delitem__(self, item):
        return self.delete(item)

    def __setitem__(self, index, item):
        return self.update(index, item)

    def __contains__(self, item):
        return self.contains(item)

    def __iter__(self):
        node = self._first
        while node:
            yield node.item
            node = node.right

    def __str__(self):
        if self._size == 0:
            return "[]"
        target = "["
        for item in self:
            target += str(item) + ", "
        target = target[:-2] + "]"
        return target

    def __select_node(self, index):
        if index < 0 or index >= self._size:
            raise ValueError("Index out of bounds")

        if index <= self._size / 2:
            node = self._first
            while index > 0:
                node = node.right
                index -= 1
        else:
            node = self._last
            while index < self._size:
                node = node.left
                index += 1
        return node

    def select(self, index):
        return self.__select_node(index).item

    def __find_node(self, item):
        if self._size <= 0:
            return None

        node = self._first
        while node and node.item != item:
            node = node.right
        return node

    def find(self, item):
        node = self.__find_node(item)
        return node.item if node else None

    def delete(self, item):
        node = self.__find_node(item)

        if node is None:
            return False

        self._size -= 1

        if self._first == node:
            self._first = node.right

        if self._last == node:
            self._last = node.left

        if node.left:
            node.left.right = node.right

        if node.right:
            node.right.left = node.left

        return True

    def contains(self, item):
        return self.__find_node(item) is not None

    def append(self, item):
        self._size += 1
        node = Node(item)
        if self._last:
            node.left = self._last
            self._last.right = node
        else:
            self._first = node
        self._last = node

    def append_front(self, item):
        self._size += 1
        node = Node(item)
        if self._first:
            node.right = self._first
            self._first.left = node
        else:
            self._last = node
        self._first = node

    def replace(self, item):
        node = self.__find_node(item)

        if node is None:
            return False

        node.item = item
        return True

    def update(self, index, item):
        node = self.__select_node(index)
        node.item = item
