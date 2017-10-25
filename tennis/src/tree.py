from node import Node
from node import NodeColor


class Tree:
    """A red-black order statistic tree implementation.

    Attributes:
        _root: The root node of this tree.
        _size: The number of nodes currently stored in the tree.
    """

    def __init__(self):
        self._root = None
        self._size = 0

    def __len__(self):
        return self._size

    def __rotate_left(self, root: Node):
        """Performs a left rotation.

        Makes the provided root's right child (pivot) become the new root.
        Puts the pivot's left child in the newly empty right position in the
        old root node.

        :param root: The root node to rotate left.
        :return: None
        """

        pivot = root.right
        pivot_left_size = 0

        if pivot:
            root.right = pivot.left

            if pivot.left:
                pivot.left.parent = root
                pivot_left_size = pivot.left.size

            pivot.parent = root.parent

        if root.parent is None:
            self._root = pivot
        elif root is root.parent.left:
            root.parent.left = pivot
        else:
            root.parent.right = pivot

        if pivot:
            pivot.left = root
            root.size -= pivot.size
            pivot.size += root.size

        root.size += pivot_left_size
        root.parent = pivot

    def __rotate_right(self, root: Node):
        """Performs a right rotation.

        Makes the provided root's left child (pivot) become the new root.
        Puts the pivot's right child in the newly empty left position in the
        old root node.

        :param root: The root node to rotate left.
        :return: None
        """

        pivot = root.left
        pivot_right_size = 0

        if pivot:
            root.left = pivot.right

            if pivot.right:
                pivot.right.parent = root
                pivot_right_size = pivot.right.size

            pivot.parent = root.parent

        if root.parent is None:
            self._root = pivot
        elif root is root.parent.left:
            root.parent.left = pivot
        else:
            root.parent.right = pivot

        if pivot:
            pivot.right = root
            root.size -= pivot.size
            pivot.size += root.size

        root.size += pivot_right_size
        root.parent = pivot

    def insert(self, key, value=None):
        """Inserts a new node into the tree.

        Creates a new node from the provided key and values, then inserts into
        the red-black tree. Fixes any inconsistencies with the tree structure
        after insertion. Does not support NoneType keys.

        :param key: The key to insert.
        :param value: The optional value mapping for this key.
        :return: True if a new node was created, otherwise False.
        """

        if key is None:
            raise ValueError("Keys are not allowed to be of type None")

        # Locate the parent and where the node should be placed.
        node = Node(key, value)
        parent = self._root

        while parent:
            # Update node then return if same key already exists.
            if node.key == parent.key:
                parent.value = node.value
                return False

            # Otherwise keep searching for a free spot in the tree.
            if node.key < parent.key:
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

        # Repair the tree.
        temp = parent

        while temp:
            temp.size += 1
            temp = temp.parent

        node.parent = parent
        self.__insert_repair(node)

        # Find and set the new root node.
        root = node
        while root.parent:
            root = root.parent
        self._root = root

        # Increment the size of this tree.
        self._size += 1

        return True

    def __insert_repair(self, node: Node):
        """Begins red-black tree insertion repairs.

        :param node: The newly inserted node.
        :return: None
        """
        if node.parent is None:
            self.__insert_case1(node)
        elif node.parent.color == NodeColor.BLACK:
            self.__insert_case2(node)
        else:
            uncle = node.get_uncle()
            if uncle and uncle.color == NodeColor.RED:
                self.__insert_case3(node)
            else:
                self.__insert_case4(node)

    # noinspection PyMethodMayBeStatic
    def __insert_case1(self, node: Node):
        node.color = NodeColor.BLACK

    def __insert_case2(self, node: Node):
        return

    def __insert_case3(self, node: Node):
        node.parent.color = NodeColor.BLACK
        node.get_uncle().color = NodeColor.BLACK
        node.get_grandparent().color = NodeColor.RED
        self.__insert_repair(node.get_grandparent())

    def __insert_case4(self, node: Node):
        parent = node.parent
        grandparent = node.get_grandparent()

        if grandparent.left and node is grandparent.left.right:
            self.__rotate_left(parent)
            node = node.left
        elif grandparent.right and node is grandparent.right.left:
            self.__rotate_right(parent)
            node = node.right

        parent = node.parent
        grandparent = node.get_grandparent()

        if node is parent.left:
            self.__rotate_right(grandparent)
        else:
            self.__rotate_left(grandparent)

        parent.color = NodeColor.BLACK
        grandparent.color = NodeColor.RED

    def __find_node(self, key):
        """Finds the mapped node of this key in the tree.

        :param key: The key of the node to find.
        :return: The mapped node if found, otherwise None.
        """
        return self._root.find(key)

    def find(self, key):
        """Finds the value for a key stored in the tree.

        Searches the tree for a node with a matching key, then provides the
        value of the matched node. NoneType keys are not supported.

        :param key: The key to search for.
        :return: The found node's value if found, otherwise None.
        """

        if key is None:
            raise ValueError("Keys are not allowed to be of type None")

        node = self.__find_node(key)

        if node:
            return node.value

        return None

    def select(self, index):
        """Finds the value of the node at the specified index.

        :param index: The position in this tree.
        :return: The node's value if found, otherwise None.
        """

        if index < 0 or index >= self._size:
            raise ValueError("Index out of bounds")

        node = self._root

        while node:
            size = node.left.size if node.left else 0

            if index == size:
                return node.value

            if index < size:
                node = node.left
            else:
                node = node.right
                index -= size + 1

    def rank(self, key):
        """Finds the index of

        :param key:
        :return:
        """
        node = self.__find_node(key)

        if not node:
            return None

        index = node.left.size if node.left else 0

        while node.parent:
            if node.parent.left is not node:
                index += node.parent.left.size + 1 if node.parent.left else 1
            node = node.parent

        return index

    def delete(self, key):
        """Deletes the node with the provided key.

        Finds the node in this tree with the same key mapping and removes it.
        Automatically fixes any red-black tree violations. NoneType keys are
        not supported.

        :param key: The key of the node to delete from this tree.
        :return: True if the node previously existed, otherwise False.
        """

        if key is None:
            raise ValueError("Keys are not allowed to be of type None")

        if not self._root:
            return False

        node = self.__find_node(key)

        if not node:
            return False

        self._size -= 1
        temp = node.parent

        while temp:
            temp.size -= 1
            temp = temp.parent

        self.__delete_node(node)

        return True

    def __delete_node(self, node: Node):
        """Deletes the provided node from this tree.

        Fixes tree inconsistencies once complete.

        :param node: The node to delete.
        :return: None
        """

        if node.left and node.right:
            # Find the successor node and replace current.
            node.size -= 1
            successor = node.right
            while successor.left:
                successor.size -= 1
                successor = successor.left

            node.key = successor.key
            node.value = successor.value
            self.__delete_node(successor)
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
                if child.parent is None:
                    self._root = child
                child.color = NodeColor.BLACK
            else:
                self.__delete_case1(child)

        if child.key is None:
            child.replace_parent(None)

    def __delete_case1(self, node: Node):
        if node.parent is None:
            if node.key:
                self._root = node
            else:
                self._root = None
            return

        self.__delete_case2(node)

    def __delete_case2(self, node: Node):
        sibling = node.get_sibling()

        if sibling and sibling.color == NodeColor.RED:
            node.parent.color = NodeColor.RED
            sibling.color = NodeColor.BLACK

            if node is node.parent.left:
                self.__rotate_left(node.parent)
            else:
                self.__rotate_right(node.parent)

        self.__delete_case3(node)

    def __delete_case3(self, node: Node):
        sibling = node.get_sibling()

        if (sibling and
                (node.parent.color == NodeColor.BLACK) and
                (sibling.color == NodeColor.BLACK) and
                (sibling.left and sibling.left.color == NodeColor.BLACK) and
                (sibling.right and sibling.right.color == NodeColor.BLACK)):
            sibling.color = NodeColor.RED
            self.__delete_case1(node.parent)
        else:
            self.__delete_case4(node)

    def __delete_case4(self, node: Node):
        sibling = node.get_sibling()

        if (sibling and
                (node.parent.color == NodeColor.RED) and
                (sibling.color == NodeColor.BLACK) and
                (sibling.left and sibling.left.color == NodeColor.BLACK) and
                (sibling.right and sibling.right.color == NodeColor.BLACK)):
            sibling.color = NodeColor.RED
            node.parent.color = NodeColor.BLACK
        else:
            self.__delete_case5(node)

    def __delete_case5(self, node: Node):
        sibling = node.get_sibling()

        if sibling and sibling.color == NodeColor.BLACK:
            if ((node is node.parent.left) and
                    (sibling.right and sibling.right.color == NodeColor.BLACK) and
                    (sibling.left and sibling.left.color == NodeColor.RED)):
                sibling.color = NodeColor.RED
                sibling.left.color = NodeColor.BLACK
                self.__rotate_right(sibling)
            elif ((node is node.parent.left) and
                    (sibling.left and sibling.left.color == NodeColor.BLACK) and
                    (sibling.right and sibling.right.color == NodeColor.RED)):
                sibling.color = NodeColor.RED
                sibling.right.color = NodeColor.BLACK
                self.__rotate_left(sibling)

        self.__delete_case6(node)

    def __delete_case6(self, node: Node):
        sibling = node.get_sibling()

        node.parent.color = NodeColor.BLACK

        if sibling:
            sibling.color = node.parent.color

            if node is node.parent.left:
                if sibling.right:
                    sibling.right.color = NodeColor.BLACK

                self.__rotate_left(node.parent)
            else:
                if sibling.left:
                    sibling.left.color = NodeColor.BLACK

                self.__rotate_right(node.parent)
