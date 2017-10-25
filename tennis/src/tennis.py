from tree import Tree

if __name__ == '__main__':
    tree = Tree()
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    numbers2 = {}

    for i in range(0, len(numbers)):
        tree.insert(numbers[i], numbers[i] * 2)
        numbers2[numbers[i]] = 1

    for i in range(5, len(numbers)):
        tree.delete(numbers[i])
        numbers2[numbers[i]] = 0

    for i in range(3, 9):
        tree.insert(numbers[i], numbers[i] * 2)
        numbers2[numbers[i]] = 1

    for i in range(0, 2):
        tree.delete(numbers[i])
        numbers2[numbers[i]] = 0

    print(tree.find(10))
    print(len(tree))
    print(tree)
