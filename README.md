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

#### Red-black order statistic tree pseudo code
```
root = null
size = 0

# Puts a new key/value mapping into the tree.
# Keep in mind each node + key may have multiple mappings.
put(key, value)
    size++
    new_node = {key: key, values: [value], color: red, size: 1}

    if root == null:
        root = new_node
        return
    
    parent = root
    
    while parent:
        parent.size++
        
        if key == parent.key:
            parent.values.append(value)
        
        if key < parent.key:
            if parent.left:
                parent = parent.left
            else:
                parent.left = new_node
        else:
            if parent.right:
                parent = parent.right
            else:
                parent.right = node
    
    node.parent = parent
    put_repair(node)

# Repairs the red-black tree balance after insertion.
put_repair(node)
    while node.parent.color == red:
        towards = left if node == node.parent.left else right
        against = opposite towards
        uncle = node.grandparent.against
        
        if uncle.color == red:
            node.parent.color = black
            uncle.color = black
            node.grandparent = red
            node = node.grandparent
            continue
        
        if node == node.parent.against:
            node = node.parent
            rotate_towards(node)
        
        node.parent.color = black
        node.grandparent.color = red
        rotate_against(node.grandparent)

# Finds the node associated with a key.
find(key)
    node = root
    while node:
        if key < node.key:
            node = node.left
        elif key > node.key:
            node = node.right
        else:
            return node
    return null

# Selects the list of values at a particular index in the tree.
select(index)
    node = root
    while node:
        size = node.left.size
        if index == size:
            return node.values
        
        if index < size:
            node = node.left
        else:
            index -= size + len(node.values)
            node = node.right
    return null

# Finds the rank of the key in this tree.
rank(key)
    node = find(key)
    
    if node == null:
        return null
        
    index = node.left.size
    
    while node.parent:
        if node.parent.left != node:
            if node.parent.left:
                index += node.parent.left.size
            index += len(node.parent.values)
        node = node.parent
    return index

# Deletes a key/value mapping from the tree.
delete(key, value)
    node = find(key)
    if node == null:
        return
    
    size--
    parent = node.parent
    while parent:
        parent.size--
        parent = parent.parent
    
    node.values.delete(value)
    
    if node.values.size > 0:
        node.size--
        return
    
    if node.left and node.right:
        node.size--
        successor = node.right
        while successor.left:
            successor = successor.left
        
        parent = successor.parent
        while parent != node:
            parent.size -= successor.size
            parent = parent.parent
        
        node.key = successor.key
        node.values = successor.values
        node = successor
    
    replacement = node.left == null ? node.left : node.right
    
    if replacement:
        replacement.parent = node.parent
        
        if node.parent == null:
            root = replacement
        elif node == node.parent.left:
            node.parent.left = replacement
        else:
            node.parent.right = replacement
        
        if node.color == black:
            delete_repair(replacement)
        return
        
    if node.parent == null:
        root = null
        return
    
    if node.color == black:
        delete_repair(node)
    
    if node.parent:
        if node == node.parent.left:
            node.parent.left = null
        elif node == node.parent.right:
            node.parent.right = null

# Repairs the red-black tree balance after deletion.
delete_repair(node)
    while node != root and node == black:
        towards = left if node == node.parent.left else right
        against = opposite towards
        sibling = node.parent.against
        
        if sibling.color == red:
            sibling.color = black
            node.parent.color = red
            rotate_towards(node.parent)
            sibling = node.parent.against
        
        if both siblings children color == black:
            sibling.color = red
            node = node.parent
            continue
        
        if node.against.color == black:
            sibling.color = red
            sibling.towards.color = black
            rotate_against(sibling)
            sibling = node.parent.against
        
        sibling.color = node.parent.color
        node.parent.color = black
        sibling.against = black
        rotate_towards(node.parent)
        node = root
    node.color = black

# Perform a left tree rotatation.
rotate_left(node)
    pivot = node.right
    node.right = pivot.left
    pivot.left.parent = node
    pivot_left_size = pivot.left.size
    pivot.parent = node.parent
    
    if node.parent == null:
        root = pivot
    elif node == node.parent.right:
        node.parent.left = pivot
    else:
        node.parent.right = pivot
    
    pivot.left = node
    node.size -= pivot.size
    pivot.size += node.size
    node.size += pivot_left_size
    root.parent = pivot

# Perform a right tree rotation.
rotate_right(node)
    # Same as rotate_left(node), but with left/right swapped.
```

#### Hash table
- Space complexity: `O(n)`
- Best case search, insertion and deletion: `O(1)`
- Average case search, insertion and deletion: `O(1)`
- Worst case search, insertion and deletion: `O(n)`

#### Hash table pseudo code
```
table = [] # Array of linked lists
size = 0

# Puts (replaces if already exists) the key/value mapping.
put(key, value)
    ensure_capacity(size + 1)
    hash_code = hash(key)
    bucket = table[hash_code]
    
    for element in bucket:
        if element.key == key:
            element.value = value
            return
    
    bucket.append({key: key, value: value})
    size++

# Gets the value associated with the given key.
get(key)
    hash_code = hash(key)
    bucket = table[hash_code]
    
    for element in bucket:
        if element.key == key:
            return element.value
    
    return null

# Deletes the value associated with the given key.
delete(key)
    hash_code = hash(key)
    bucket = table[hash_code]
    removed = bucket.remove(key)
    
    if removed:
        size--

# Increases the hash table size if too small to produce O(1) searches.
ensure_capacity(min_size)
    if table.size >= min_size:
        return
    
    new_size = (size * 3) / 2 + 1
    
    if new_size < min_size:
        new_size = min_size
    
    old_table = table
    table = [new_size]
    size = 0
    
    for key, value in old_table:
        put(key, value)
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

My original design was to use block sort. Though I've found while gradually
loading player data from a file, instead of putting it into an array, it could
be put into a better data structure that helps with the sorting process. Pipe
sort is a sorting algorithm I designed which was inspired by Tim sort. It's
similar to Tim sort in the way that it is able to detect runs, both forwards
and backwards. Even if the entire data set supplied was in reverse, pipe sort
should be able to sort it in `O(n)` time.

Pipe sort differs from Tim sort in two ways. When feeding data into pipe sort,
it not only finds runs in the data but it also groups these runs by their
relative sizes using the specialised tree data structure specified in the
stream solution. Note that this tree is indexed by the size of the runs, not
the data itself. The other difference is, insertion sort is now no longer
necessary as it is more optimal to recursively merge sort all similar sized
runs. We know all the data is sorted once there is only a single run remaining.

#### Pipe sort
- Space complexity: `O(n)`
- Time complexities:
  - Best: `O(n)`
  - Average: `O(n log n)`
  - Worst: `O(n log n)`

#### Pipe sort pseudo code
```
runs = Tree() # Any multi-value order statistic tree would work here.
run = List() # Linked lists ensure value insertion is O(1).
previous = null
consume_function=init # The current state of the value consuming pipeline.

# Initial consuming state.
init(value)
    run.append(value)
    previous = value
    consume_function = single

# Consume state when only 1 element exists in the current run.
single(value)
    if value >= previous:
        run.append(value)
        previous = value
        consume_function = front
    else:
        run.append(value)
        previous = value
        consume_function = back

# Consume state when current run is ascending.
front(value)
    if value >= previous:
        run.append(value)
        previous = value
    else:
        runs.insert(run.size, run)
        run = List()
        run.append(value)
        previous = value
        consume_function = single

# Consume state when current run is descending.
back(value)
    if value <= previous:
        run.append_front(value)
        previous = value
    else:
        runs.insert(run.size, run)
        run = List()
        run.append(value)
        previous = value
        consume_function = single

# Merges all runs and returns as array.
sort()
    runs.insert(run.size, run)
    run = List()
    consume_function = init
    
    outer: while runs.size > 1:
        new_runs = Tree()
        
        inner: for run_a, run_b in runs:
            if run_b == null:
                new_runs.insert(run_a.size, run_a)
                continue outer
            merged = merge(run_a, run_b)
            new_runs.insert(merged.size, merged)
        
        runs = new_runs
    
    sorted_run = runs[0]
    
    if sorted_run instance of linked list:
        sorted_run = sorted_run.to_array()
    
    return sorted_run

# Merges two runs.
merge(run_a, run_b)
    merged = [run_a.size + run_b.size]
    index = 0
    ia = 0
    ib = 0
    
    while ia < run_a.size and ib < run_b.size:
        if run_a[ia] > run_b[ib]:
            merged[index] = run_b[ib]
            ib++
        else:
            merged[index] = run_a[ia]
            ia++
        index++
    
    while ia < run_a.size:
        merged[index] = run_a[ia]
        ia++
    
    while ib < run_b.size:
        merged[index] = run_b[ib]
        ib++
    
    return merged
```

## Other notes
- The library numpy was used in this project, not for ease of use but to
  emulate a proper C-style array of immutable size.
- I am aware that focusing on algorithms like this being optimal is futile in a
  language like Python, and that creating these in a lower level language will
  probably provide a performance gain. This assignment specified for them to be
  written in this language. If the intention was to get us to create native
  bindings, then I'd be happy to oblige.
- There are already many great libraries out there for Python that have similar
  behaviour to what I have written, and reinventing the wheel is usually
  something that should be avoided in software development. I made the
  exception here as I assume the assignment was designed to show an
  understanding of common data structures and algorithms.
