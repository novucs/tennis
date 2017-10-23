from node import Node
from node import NodeColor


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

    def insert(self, key, value=None):
        n = Node(key, value)
        self.insert_recurse(self.root, n)
        self.insert_repair_tree(n)
        self.root = n
        while self.root.parent is not None:
            self.root = self.root.parent
        return n

    def insert_recurse(self, root, n):
        if root is not None:
            if n.key < root.key:
                if root.left is not None:
                    self.insert_recurse(root.left, n)
                    return
                else:
                    root.left = n
            else:
                if root.right is not None:
                    self.insert_recurse(root.right, n)
                    return
                else:
                    root.right = n
        n.parent = root
        n.left = None
        n.right = None
        n.color = NodeColor.RED

    def insert_repair_tree(self, n):
        if n.parent is None:
            self.insert_case1(n)
        elif n.parent.color is NodeColor.BLACK:
            self.insert_case2(n)
        else:
            uncle = n.get_uncle()
            if uncle is not None and uncle.color is NodeColor.RED:
                self.insert_case3(n)
            else:
                self.insert_case4(n)

    # noinspection PyMethodMayBeStatic
    def insert_case1(self, n):
        n.color = NodeColor.BLACK

    def insert_case2(self, n):
        return

    def insert_case3(self, n):
        n.get_parent().color = NodeColor.BLACK
        n.get_uncle().color = NodeColor.BLACK
        n.get_grandparent().color = NodeColor.RED
        self.insert_repair_tree(n.get_grandparent())

    def insert_case4(self, n):
        p = n.get_parent()
        g = n.get_grandparent()

        if g.left is not None and n is g.left.right:
            self.rotate_left(p)
            n = n.left
        elif g.right is not None and n is g.right.left:
            self.rotate_right(p)
            n = n.right
        self.insert_case4step2(n)

    def insert_case4step2(self, n):
        p = n.get_parent()
        g = n.get_grandparent()

        if n is p.left:
            self.rotate_right(g)
        else:
            self.rotate_left(g)

        p.color = NodeColor.BLACK
        g.color = NodeColor.RED

    def find(self, key):
        node = self.root
        while node is not None:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def delete(self, key):
        node = self.find(key)

