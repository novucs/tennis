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

        if y.left:
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

        if y.right:
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
        # Locate the parent and where the node should be placed
        node = Node(key, value)
        parent = self.root

        while parent:
            # Update node if same key already exists
            if node.key == parent.key:
                parent.value = node.value
                return False
            elif node.key < parent.key:
                if parent.left:
                    parent = parent.left
                else:
                    parent.left = node
                    break
            else:
                if parent.right:
                    parent = parent.right
                else:
                    parent.right = node
                    break

        # Repair the tree
        node.parent = parent
        node.left = None
        node.right = None
        node.color = NodeColor.RED
        self.insert_repair(node)

        # Find and set the new root node
        root = node
        while root.parent:
            root = root.parent
        self.root = root

        return True

    def insert_repair(self, node):
        if node.parent is None:
            self.insert_case1(node)
        elif node.parent.color == NodeColor.BLACK:
            self.insert_case2(node)
        else:
            uncle = node.get_uncle()
            if uncle and uncle.color == NodeColor.RED:
                self.insert_case3(node)
            else:
                self.insert_case4(node)

    # noinspection PyMethodMayBeStatic
    def insert_case1(self, node):
        node.color = NodeColor.BLACK

    def insert_case2(self, node):
        return

    def insert_case3(self, node):
        node.get_parent().color = NodeColor.BLACK
        node.get_uncle().color = NodeColor.BLACK
        node.get_grandparent().color = NodeColor.RED
        self.insert_repair(node.get_grandparent())

    def insert_case4(self, node):
        parent = node.get_parent()
        grandparent = node.get_grandparent()

        if grandparent.left and node is grandparent.left.right:
            self.rotate_left(parent)
            node = node.left
        elif grandparent.right and node is grandparent.right.left:
            self.rotate_right(parent)
            node = node.right

        if node is parent.left:
            self.rotate_right(grandparent)
        else:
            self.rotate_left(grandparent)

        parent.color = NodeColor.BLACK
        grandparent.color = NodeColor.RED

    def find(self, key):
        return self.root.find(key)

    def find_min(self):
        return self.root.find_min()

    def delete(self, key):
        node = self.find(key)

        if node:
            self.delete_node(node)

    def delete_node(self, node):
        if node.left and node.right:
            successor = node.right.find_min()
            node.key = successor.key
            node.value = successor.value
            self.delete_node(successor)
            return

        child = Node(color=NodeColor.BLACK)

        if node.right:
            child = node.right
        elif node.left:
            child = node.left

        node.key = child.key
        node.value = child.value
        node.replace_parent(child)

        if node.color == NodeColor.BLACK:
            if child.color == NodeColor.RED:
                child.color = NodeColor.BLACK
            else:
                self.delete_case1(child)

        if child.key is None:
            child.replace_parent(None)

    def delete_case1(self, node):
        if node.parent is None:
            if node.key:
                self.root = node
            else:
                self.root = None
            return

        self.delete_case2(node)

    def delete_case2(self, node):
        sibling = node.get_sibling()

        if sibling and sibling.color == NodeColor.RED:
            node.parent.color = NodeColor.RED
            sibling.color = NodeColor.BLACK

            if node is node.parent.left:
                self.rotate_left(node.parent)
            else:
                self.rotate_right(node.parent)

        self.delete_case3(node)

    def delete_case3(self, node):
        sibling = node.get_sibling()

        if (sibling and
                (node.parent.color == NodeColor.BLACK) and
                (sibling.color == NodeColor.BLACK) and
                (not sibling.left or sibling.left.color == NodeColor.BLACK) and
                (not sibling.right or sibling.right.color == NodeColor.BLACK)):
            sibling.color = NodeColor.RED
            self.delete_case1(node.parent)
        else:
            self.delete_case4(node)

    def delete_case4(self, node):
        sibling = node.get_sibling()

        if (sibling and
                (node.parent.color == NodeColor.RED) and
                (sibling.color == NodeColor.BLACK) and
                (not sibling.left or sibling.left.color == NodeColor.BLACK) and
                (not sibling.right or sibling.right.color == NodeColor.BLACK)):
            sibling.color = NodeColor.RED
            node.parent.color = NodeColor.BLACK
        else:
            self.delete_case5(node)

    def delete_case5(self, node):
        sibling = node.get_sibling()

        if sibling and sibling.color == NodeColor.BLACK:
            if ((node is node.parent.left) and
                    (not sibling.right or sibling.right.color == NodeColor.BLACK) and
                    (sibling.left and sibling.left.color == NodeColor.RED)):
                sibling.color = NodeColor.RED
                sibling.left.color = NodeColor.BLACK
                self.rotate_right(sibling)
            elif ((node is node.parent.left) and
                    (not sibling.left or sibling.left.color == NodeColor.BLACK) and
                    (sibling.right and sibling.right.color == NodeColor.RED)):
                sibling.color = NodeColor.RED
                sibling.right.color = NodeColor.BLACK
                self.rotate_left(sibling)

        self.delete_case6(node)

    def delete_case6(self, node):
        sibling = node.get_sibling()

        if sibling:
            sibling.color = node.parent.color

        node.parent.color = NodeColor.BLACK

        if node is node.parent.left:
            if sibling.right:
                sibling.right.color = NodeColor.BLACK

            self.rotate_left(node.parent)
        else:
            if sibling.left:
                sibling.left.color = NodeColor.BLACK

            self.rotate_right(node.parent)
