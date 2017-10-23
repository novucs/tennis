import enum


class NodeColor(enum.Enum):
    BLACK = 0
    RED = 1


class Node:
    def __init__(self, key, value, red=True, parent=None, left=None, right=None):
        self.key = key
        self.value = value
        self.red = red
        self.parent = parent
        self.left = left
        self.right = right

    def get_parent(self):
        return self.parent

    def get_grandparent(self):
        parent = self.get_parent()
        if parent is None:
            return None
        return parent.get_parent()

    def get_sibling(self):
        parent = self.get_parent()
        if parent is None:
            return None
        elif self is parent.left:
            return parent.right
        else:
            return parent.left

    def get_uncle(self):
        parent = self.get_parent()
        grandparent = self.get_grandparent()
        if grandparent is None:
            return None
        return parent.get_sibling()
