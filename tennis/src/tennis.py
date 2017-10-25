from tree import Tree
from random import randint
from random import seed

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


if __name__ == '__main__':
    tree = Tree()
    numbers = []
    numbers2 = set()

    for i in range(0, 10000):
        numbers.append(randint(0, 100))

    for j in range(0, 100):
        for i in rand_range():
            tree.insert(numbers[i], numbers[i] * 2)
            numbers2.add(numbers[i])
            check = check_tree(tree._root)
            if not check["valid"]:
                print("broken")
            if (not tree._root and len(tree) != 0) or tree._root and tree._root.size != len(tree):
                print("a " + str(i) + " " + str(j))

        for i in rand_range():
            tree.delete(numbers[i])
            check = check_tree(tree._root)
            if not check["valid"]:
                print("broken")
            if (not tree._root and len(tree) != 0) or tree._root and tree._root.size != len(tree):
                print("b " + str(i) + " " + str(j))
            if numbers2.__contains__(numbers[i]):
                numbers2.remove(numbers[i])

    print(len(tree))