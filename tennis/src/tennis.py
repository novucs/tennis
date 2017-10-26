from random import randint
from random import seed

from ranked_tree import BLACK
from ranked_tree import Tree

seed(1)


def rand_range():
    num1 = randint(0, 100)
    num2 = randint(0, 100)
    if num1 > num2:
        return range(num2, num1)
    else:
        return range(num1, num2)


def check_tree(node):
    if not node:
        return {
            "actual": 0,
            "expected": 0,
            "valid": True
        }

    if not node.right and not node.left:
        return {
            "actual": node.size,
            "expected": 1,
            "valid": True
        }

    left = check_tree(node.left)
    right = check_tree(node.right)
    actual = node.size
    expected = left["actual"] + right["actual"] + 1
    valid = left["valid"] and actual == expected

    return {
        "actual": actual,
        "expected": expected,
        "valid": valid
    }


def get_height(node):
    if not node:
        return 0

    left = get_height(node.left)
    right = get_height(node.right)

    if left == -1 or right == -1 or left != right:
        return -1

    return left + (1 if node.color == BLACK else 0)


def is_valid(node):
    return get_height(node) >= 0


if __name__ == '__main__':
    tree = Tree()
    numbers = []
    numbers2 = set()

    for i in range(0, 10000):
        numbers.append(randint(0, 20))

    for j in range(0, 75):
        for i in rand_range():
            num = numbers[i]
            tree[num] = num * 2
            numbers2.add(numbers[i])

            if not is_valid(tree._root):
                print("broken1")
            check = check_tree(tree._root)
            if not check["valid"]:
                print("broken2")
            if (not tree._root and len(tree) != 0) or tree._root and tree._root.size != len(tree):
                print("a " + str(i) + " " + str(j))

        for i in rand_range():
            num = numbers[i]
            tree[num] = None

            if numbers2.__contains__(numbers[i]):
                numbers2.remove(numbers[i])

            if not is_valid(tree._root):
                print("broken3")
            check = check_tree(tree._root)
            if not check["valid"]:
                print("broken4")
            if (not tree._root and len(tree) != 0) or tree._root and tree._root.size != len(tree):
                print("b " + str(i) + " " + str(j))

    for key, value in tree:
        print(str(key))

    print(tree)
    print(len(tree))
