import enum


class NodeColor(enum.Enum):
    BLACK = 0
    RED = 1


class Node:
    def __init__(self,
                 key=None,
                 value=None,
                 color=NodeColor.RED,
                 parent=None,
                 left=None,
                 right=None):
        self.key = key
        self.value = value
        self.color = color
        self.parent = parent
        self.left = left
        self.right = right

    def get_grandparent(self):
        parent = self.parent
        if parent is None:
            return None
        return parent.parent

    def get_sibling(self):
        parent = self.parent
        if parent is None:
            return None
        elif self is parent.left:
            return parent.right
        else:
            return parent.left

    def get_uncle(self):
        parent = self.parent
        grandparent = self.get_grandparent()
        if grandparent is None:
            return None
        return parent.get_sibling()

    def replace_parent(self, new_node=None):
        if self.parent is not None:
            if self == self.parent.left:
                self.parent.left = new_node
            elif self == self.parent.right:
                self.parent.right = new_node
        if new_node is not None:
            new_node.parent = self.parent

    def find(self, key):
        node = self
        while node is not None:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def find_min(self):
        node = self
        while node.left is not None:
            node = node.left
        return node
