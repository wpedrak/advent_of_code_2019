ROOT = "COM"


def all_dist_to_root_aux(node, tree, acc, dist):
    new_acc = acc + [(node, dist)]
    if node == ROOT:
        return new_acc
    return all_dist_to_root_aux(tree[node], tree, new_acc, dist+1)


def all_dist_to_root(node, tree):
    return all_dist_to_root_aux(node, tree, [], 0)


file = open("input.txt", "r")
lines = [line.rstrip('\n') for line in file]

parent = {}
nodes = []

for line in lines:
    top, bot = line.split(")")
    parent[bot] = top
    nodes.append(bot)

you_dists = all_dist_to_root("YOU", parent)
san_dists = all_dist_to_root("SAN", parent)

dist = 1e9

for you in you_dists:
    for san in san_dists:
        if you[0] != san[0]:
            continue
        dist = min(dist, you[1]+san[1])


print(dist - 2)
