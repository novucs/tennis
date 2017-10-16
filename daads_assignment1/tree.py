from daads_assignment1.node import *


class Tree:
    def __init__(self, root: Node = None, compare=lambda x, y: x > y):
        self.root = root
        self.compare = compare
        self.size = 0 if root is None else 1

    def rotate_left(self, x: Node):
        y = x.right
        x.right = y.left

        if y.left is not None:
            y.left.parent = x

        y.parent = x.parent

        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

    def rotate_right(self, x: Node):
        y = x.left
        x.left = y.right

        if y.right is not None:
            y.right.parent = x

        y.parent = x.parent

        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.right = x
        x.parent = y

    def insert(self, element):
        child = Node(element)
        parent = None
        temp = self.root

        while temp is not None:
            parent = temp
            if self.compare(temp.element, child.element):
                temp = temp.left
            else:
                temp = temp.right

        child.parent = parent

        if parent is None:
            self.root = child
        elif self.compare(parent.element, child.element):
            parent.left = child
        else:
            parent.right = child

        child.left = None
        child.right = None
        child.red = True

        while child is not self.root and child.parent.red:
            if child.parent == child.parent.parent.left:
                parent = child.parent.parent.right
                if parent and parent.red:
                    child.parent.red = False
                    parent.red = False
                    child.parent.parent.red = True
                    child = child.parent.parent
                else:
                    if child is child.parent.right:
                        child = child.parent
                        self.rotate_left(child)
                    child.parent.red = False
                    child.parent.parent.red = True
                    self.rotate_right(child.parent.parent)
            else:
                parent = child.parent.parent.left
                if parent and parent.red:
                    child.parent.red = False
                    parent.red = False
                    child.parent.parent.red = True
                    child = child.parent.parent
                else:
                    if child is child.parent.left:
                        child = child.parent
                        self.rotate_right(child)
                    child.parent.red = False
                    child.parent.parent.red = True
                    self.rotate_left(child.parent.parent)

        self.root.red = False
