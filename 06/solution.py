def is_root(node):
    return node == "COM"


def dist_to_root(node, tree):
    if is_root(node):
        return 0
    return 1 + dist_to_root(tree[node], tree)


file = open("input.txt", "r")
lines = [line.rstrip('\n') for line in file]

parent = {}
nodes = []

for line in lines:
    top, bot = line.split(")")
    parent[bot] = top
    nodes.append(bot)

dist = 0
for node in nodes:
    dist += dist_to_root(node, parent)

print(dist)
