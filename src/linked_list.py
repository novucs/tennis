#!/usr/bin/env python

"""

A doubly-linked list.

"""

# import numpy as np


class Node:
    """A node stored in the linked list.

    Attributes:
        item: The item associated with this node.
        left: The node to the left.
        right: The node to the right.
    """

    def __init__(self, item):
        self.item = item
        self.left = None
        self.right = None


class List:
    """A doubly linked list implementation.

    Attributes:
        _first: The first node in the list.
        _last: The last node in the list.
        _size: The total number of nodes in this list.
    """

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
            return '[]'
        target = '['
        for item in self:
            target += str(item) + ', '
        target = target[:-2] + ']'
        return target

    def __select_node(self, index):
        """Selects a node by the provided index.

        :param index: The position in the list.
        :return: The node at the provided index.
        """
        if index < 0 or index >= self._size:
            raise ValueError('Index out of bounds')

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
        """Selects the item stored in this list at the provided index.

        :param index: The position in the list.
        :return: The item at the provided index.
        """
        return self.__select_node(index).item

    def __find_node(self, item):
        """Finds the first node in the list of the same item.

        :param item: The item to search for.
        :return: The node which stores the searched item if found, otherwise
                 None.
        """
        if self._size <= 0:
            return None

        node = self._first
        while node is not None and node.item != item:
            node = node.right
        return node

    def find(self, item):
        """Finds the first item in this list that equals to the item provided.

        :param item: The item to search for.
        :return: The item stored in this list, that equals to the item
                 provided.
        """
        node = self.__find_node(item)
        return node.item if node is not None else None

    def delete(self, item):
        """Deletes the first item that equals to the item provided.

        :param item: The item to delete from this list.
        :return: The item that was deleted if found, otherwise None.
        """
        node = self.__find_node(item)

        if node is None:
            return None

        self._size -= 1

        if self._first == node:
            self._first = node.right

        if self._last == node:
            self._last = node.left

        if node.left is not None:
            node.left.right = node.right

        if node.right is not None:
            node.right.left = node.left

        return node.item

    def contains(self, item):
        """Checks if the list contains a specific item.

        :param item: The item to search for.
        :return: True if the list contains the item, otherwise False.
        """
        return self.__find_node(item) is not None

    def append(self, item):
        """Appends a new item to the end of the list.

        :param item: The item to append.
        :return: None
        """
        self._size += 1
        node = Node(item)
        if self._last is not None:
            node.left = self._last
            self._last.right = node
        else:
            self._first = node
        self._last = node

    def append_front(self, item):
        """Appends a new item to the front of the list.

        :param item: The item to append.
        :return: None
        """
        self._size += 1
        node = Node(item)
        if self._first is not None:
            node.right = self._first
            self._first.left = node
        else:
            self._last = node
        self._first = node

    def replace(self, item):
        """Replaces the first item in the list that equals to the item
        provided.

        :param item: The item to match and replace.
        :return: The previous item if it was replaced, otherwise None.
        """
        node = self.__find_node(item)

        if node is None:
            return None

        old_item = node.item
        node.item = item
        return old_item

    def update(self, index, item):
        """Updates an item at a specified index in the list.

        :param index: The index of the node to replace.
        :param item: The new item.
        :return: The old item that was previously stored at this index.
        """
        node = self.__select_node(index)
        old_item = node.item
        node.item = item
        return old_item

    def to_array(self):
        """Converts this list to an array.

        :return: The newly created array.
        """
        iterator = iter(self)
        # target_array = np.empty(self._size, dtype=object)
        target_array = [None] * self._size

        for i in range(0, self._size):
            target_array[i] = next(iterator)

        return target_array

    def first(self):
        """Gets the first element in the list.

        :return: The first element if found, otherwise None.
        """
        return None if self._first is None else self._first.item

    def last(self):
        """Gets the last element in the list.

        :return: The last element if found, otherwise None.
        """
        return None if self._last is None else self._last.item

    def clone(self):
        """Shallow-clones the list elements into a new list.

        :return: The cloned list.
        """
        target = List()
        for element in self:
            target.append(element)
        return target
