# DADSA Assignment 1
**A tennis player ranking system.**

Takes in the score of each match for a given tournament and updates each
players position, calculates each players ranking points and produces a list
of the players ranking in descending order.

## Solutions
This system can be designed in two different ways, depending on how data is
presented to the application: static, and streamed.

### Stream
Data could be streamed into the application if games are still ongoing.
Players in this state may still score points, thus changing their position in
the current tournament. Therefore an algorithm that can quickly update
individual positions in the tournament should be favoured.

A well-programmed sort algorithm will have an average sort time complexity of
`O(n log n)`. However self balancing trees tend to have modification time
complexities of `O(log n)`. Since we are optimising for sorting on individual
element modifications, it would be very expensive to reorganize and verify the
entire data structure. A self balancing tree would then be the most optimal
route to take when streaming data.

We must take into account that third parties, whom are feeding us the data, may
not understand nor wish to feed us our direct object references. Instead we
will probably be given either player names or other types of identification.
These can be used as keys which may then be used for indexing our own player
profiles. Hash tables provide a speedy average lookup time of `O(1)` for this
operation, so these will be used as a form of compatibility when interfacing
with the data provider.

#### Red-black order statistic tree
- Space complexity: `O(n)`
- Best case access, search, insertion and deletion: `O(log n)`
- Average case access, search, insertion and deletion: `O(log n)`
- Worst case access, search, insertion and deletion: `O(n)`
- The red-black self balancing method was chosen as it is guaranteed `O(log n)`
  lookup and modification time within the tree itself (forgetting node
  operations).
- Multiple players may have the same score, so each node in the tree must allow
  for storing multiple players. In this scenario, I have chosen to simply
  supply a linked list for holding the node values.
- We may be required to find all players at a specified rank, or find the rank
  of a specified player. Each node is given a size, which can be used for
  performing these `O(log n)` operations.

#### Hash table
- Space complexity: `O(n)`
- Best case search, insertion and deletion: `O(1)`
- Average case search, insertion and deletion: `O(1)`
- Worst case search, insertion and deletion: `O(n)`

#### Pseudo code
```
# === Data structure definitions === #

# Apply seperate definitions for each tournament.
players_by_name = HashTable()
sorted_players = Tree()

# === Data streaming functions === #

create_player(player_name):
    players_by_name[player_name] = Player(player_name)

accept_score(player_name, score):
    # Do nothing if player did not score anything.
    if score == 0:
        return

    # Fetch the players profile.
    player = players_by_name[player_name]

    # Update the players ranking.
    sorted_players.delete(player.score, player)
    player.score += score
    sorted_players.insert(player.score, player)
```

### Static
Static (immutable) data may be provided to the application if all games are
finished. We can still use the solution provided with streamed data. Though
there are some downfalls that can be avoided since we are certain the data
cannot change.

Some operations in our previous solution have a worst case time complexity of
`O(n)`, therefore processing the entire data set will give us an overall worst
case time complexity of `O(n^2)`. As stated before, there are sorting
algorithms that provide a worst case scenario of `O(n log n)`. Sorting is also
able to put the data into an array data structure. Arrays have a guaranteed
lookup time of `O(1)`, which is more optimal than the trees `O(log n)`. Hence
a sorting algorithm would be better than a tree for static data.

This then leaves the question "What sorting algorithm should be used?". There
tons of different sorting algorithms, all with their own sets of advantages and
disadvantages. Selecting an optimal sorting algorithm is generally down to what
is to be expected of the input data. As this assignment is vague on the
specifics on what to expect, it's probably best to use a general purpose
sorting algorithm that has the best all-round statistics.

Tim sort was the first general purpose sorting algorithm that popped into my
head. It is the main sorting algorithm used by Python and Java as it offers
excellent benchmarks on sorting real world data. Tim sort achieves this by
taking advantage of already sorted sections or "runs" of the provided data set.
Though Tim sort is not the only algorithm that does this.

Block sort is a newer sorting algorithm that, like Tim sort, is a combination of
merge sort and insertion sort and uses runs. Block sort is almost identical to
Tim sort when ran on real world data, but it provides one extra advantage over
Tim sort, a space complexity of `O(1)`. For comparison, Tim sort has a space
complexity of `O(n)`.

#### Block sort
- Space complexity: `O(1)`
- Best case: `O(n)`
- Average case: `O(n log n)`
- Worst case: `O(n log n)`

#### Pseudo code
```
load_tournament_results(tournament_file):
    results = []
    for line in file(tournament_file):
        name, score = line.split(",")
        player = Player(name, score)
        results.append(player)
    return results

# Load a player profile array as tournament results.
tournament_results = load_tournament_results("tournament 1.csv")
block_sort(tournament_reuslts)
```
