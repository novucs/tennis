class Node:
    def __init__(self, element, red=True, parent=None, left=None, right=None):
        self.element = element
        self.red = red
        self.parent = parent
        self.left = left
        self.right = right
