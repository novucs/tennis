from tree import Tree

if __name__ == '__main__':
    tree = Tree()
    tree.insert(5)
    tree.insert(3)
    tree.insert(2)
    tree.insert(6)
    tree.insert(7)
    tree.insert(1)
    tree.insert(4)
    tree.delete(3)
    print(tree)
