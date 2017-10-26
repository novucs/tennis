from random import randint
from random import seed

from linked_list import List
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
        valid = node.size == len(node.values)
        to_return = {
            "actual": node.size,
            "expected": len(node.values),
            "valid": valid
        }
        if not valid:
            to_return["fault"] = {
                "actual": node.size,
                "expected": len(node.values),
                "node": str(node.key)
            }
        return to_return

    left = check_tree(node.left)
    right = check_tree(node.right)
    actual = node.size
    expected = left["actual"] + right["actual"] + len(node.values)
    valid = left["valid"] and actual == expected

    to_return = {
        "actual": actual,
        "expected": expected,
        "valid": valid
    }

    if not valid:
        to_return["fault"] = {
                "actual": node.size,
                "expected": expected,
                "node": str(node.key)
            }

    if not left["valid"]:
        to_return["fault"] = left["fault"]

    return to_return


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


class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name


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
            if i == 59 and j == 16:
                x = 0
            tree.delete(num, num*2)

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

    player1 = Player("bob", 1)
    player2 = Player("bob", 2)

    print(str(player1 == player2))

    players = Tree()
    players.insert(1, "jeff")
    players.insert(1, "bob")
    players.insert(1, "barry")
    players.delete(1, "bob")
    players.insert(2, "bob")
    players.insert(3, "garry")
    leader_board_position = 0

    print("players at selected position: " + str(players.select(leader_board_position)))
    print("maintree rank of 1: " + str(tree.rank(6)))
    print(str(players))

    # TODO: Add tests tests for tree selection


    # numbers = List()
    #
    # for i in range(0, 10):
    #     numbers.append(i)
    # for i in range(0, 10):
    #     numbers.delete(i)
    # print(numbers)
    # print(len(numbers))
