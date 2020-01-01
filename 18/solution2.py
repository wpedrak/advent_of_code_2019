from collections import deque
from point import Point
from collections import defaultdict as dd


class Maze():

    WALL = '#'
    EMPTY = '.'
    BOT = '@'
    BOT_NAMES = ['%', '$', '!', '&']

    def __init__(self, inp):
        bot_names = iter(Maze.BOT_NAMES)
        rows = inp.split()
        self.board = {}
        self.num_of_keys = 0
        self.bots = []
        self.knd = {}  # keys and doors

        for y in range(len(rows)):
            for x in range(len(rows[0])):
                value = rows[y][x]
                point = Point(x, y)

                if value == Maze.BOT:
                    self.bots.append(point)
                    bot_name = next(bot_names)
                    self.board[point] = bot_name
                    self.knd[bot_name] = point
                    continue
                elif value.isalpha():
                    self.knd[value] = point

                if value.islower():
                    self.num_of_keys += 1

                self.board[point] = value

    def get_neighbours(self, p):
        potential = [
            Point(p.x, p.y + 1),
            Point(p.x, p.y - 1),
            Point(p.x - 1, p.y),
            Point(p.x + 1, p.y)
        ]

        return list(filter(lambda x: self.board[x] != Maze.WALL, potential))

    def get_propositions(self, p):
        visited = set([p])
        to_visit = deque(self.get_neighbours(p) + ['LVL_UP'])
        dist = 1

        res = []

        while len(to_visit) > 1:
            current = to_visit.popleft()
            visited.add(current)

            if current == 'LVL_UP':
                dist += 1
                to_visit.append('LVL_UP')
                continue

            value = self.board[current]

            if value in self.knd:
                res.append((value, dist))
                continue

            to_visit += deque([n for n in self.get_neighbours(current) if n not in visited])

        return list(set(res))

    def get_value(self, p):
        return self.board[p]


class Pricer:

    def __init__(self, graph):
        self.cost = 0
        self.graph = graph

        self.locations = {x: x for x in Maze.BOT_NAMES}

    def get_cost(self):
        return self.cost

    def price(self, item):
        part_of_graph = self.graph.graph_part[item]
        location = self.locations[part_of_graph]

        self.cost += self.graph.dist(location, item)

        # print('From', location, 'to', item, '->', self.graph.dist(location, item))

        self.locations[part_of_graph] = item


class Graph:

    def __init__(self, maze):
        self.edges = {}
        self.graph_part = {}

        for item, point in maze.knd.items():
            self.edges[item] = maze.get_propositions(point)

        edges_for_dists = dict(self.edges)
        self.distances = Graph.all_distances(edges_for_dists)

    def show_edges(self):
        for k, v in self.edges.items():
            print(f"{k} -> {v}")

    def dist(self, char_a, char_b):
        a = ord(char_a)
        b = ord(char_b)
        return self.distances[a][b]

    def cost_of_order(self, order):
        pricer = Pricer(self)

        for item in reversed(order):
            pricer.price(item)

        return pricer.get_cost()

    @staticmethod
    def all_distances(edges):
        size = ord('z') + 1
        dists = [[1e20] * size for _ in range(size)]

        all_edges = [(ord(from_v), ord(to_v), weight) for from_v, lst in edges.items() for to_v, weight in lst]

        for from_v, to_v, val in all_edges:
            dists[from_v][to_v] = val
            dists[to_v][from_v] = val

        for v in range(size):
            dists[v][v] = 0

        for k in range(size):
            for i in range(size):
                for j in range(size):
                    dists[i][j] = min(dists[i][j], dists[i][k] + dists[k][j])

        return dists

    @staticmethod
    def get_blockings_in_tree(node, edges):
        def aux(node, blockings):
            if not edges[node]:
                return {node: blockings}

            new_blockings = blockings[:]
            if node.isupper():
                new_blockings.append(node.lower())

            small_blockings = [aux(n, new_blockings) for n in edges[node]]

            result = {node: new_blockings} if node.islower() else {}
            for sb in small_blockings:
                result.update(sb)

            return result

        return aux(node, [])

    @staticmethod
    def treefy(edges, root):
        tree_edges = {}
        visited = set()
        used_in_tree = {root}
        to_visit = deque([root])

        while to_visit:
            current = to_visit.popleft()

            if current in visited:
                continue

            visited.add(current)

            neighbours = set(edges[current])
            tree_edges[current] = list(neighbours - used_in_tree)

            used_in_tree = used_in_tree | neighbours

            to_visit += deque([n for n in neighbours if n not in visited])

        return tree_edges

    @staticmethod
    def extend_blocking(blocking):
        new_blocking = dict(blocking)

        for blocker, is_blocking in blocking.items():
            for arr in new_blocking.values():
                if blocker in arr:
                    arr += is_blocking

        return new_blocking

    @staticmethod
    def reverse_arrows(edges):
        new_edges = {}
        for k in edges:
            new_edges[k] = []

        for k, lst in edges.items():
            for v in lst:
                new_edges[v].append(k)

        return dict(new_edges)

    @staticmethod
    def get_preceedings_in_tree(node, edges):
        def aux(node, preceedings):
            if not edges[node]:
                return {node: preceedings}

            new_preceedings = preceedings[:]
            if node.islower():
                new_preceedings.append(node)

            small_preceedings = [aux(n, new_preceedings) for n in edges[node]]

            result = {node: preceedings[:]} if node.islower() else {}
            for sb in small_preceedings:
                result.update(sb)

            return result

        return aux(node, [])

    def get_blockings(self):
        letters_edges = {}
        for n, vals in self.edges.items():
            letters_edges[n] = [k for k, _ in vals]

        extended_is_blocked_by = {}
        is_preceded_by = {}

        for bot_name in Maze.BOT_NAMES:
            # print(bot_name)
            tree_edges = Graph.treefy(letters_edges, bot_name)

            is_blocked_by = Graph.get_blockings_in_tree(bot_name, tree_edges)
            local_extended_is_blocked_by = Graph.extend_blocking(is_blocked_by)
            extended_is_blocked_by.update(local_extended_is_blocked_by)

            local_is_preceded_by = Graph.get_preceedings_in_tree(bot_name, tree_edges)
            is_preceded_by.update(local_is_preceded_by)

            for k in local_is_preceded_by:
                self.graph_part[k] = bot_name

        dependency = dd(lambda: [])
        for k, v in extended_is_blocked_by.items():
            dependency[k] += v
        for k, v in is_preceded_by.items():
            dependency[k] += v

        return Graph.reverse_arrows(dict(dependency))

    @staticmethod
    def all_topological_sorts(will_unlock):
        def aux(vertices):
            if not vertices:
                return [[]]

            all_locked = set([item for k, items in will_unlock.items() if k in vertices for item in items])
            unlocked = vertices - all_locked
            res = []

            for item in unlocked:
                smaller_sorts = aux(vertices - set([item]))
                res += [srt + [item] for srt in smaller_sorts]

            return res

        return aux(set(will_unlock))


def add_if_key(keys_set, keys):
    additional_keys = filter(
        lambda x: x.islower(),
        keys
    )

    return keys_set | frozenset(additional_keys)


def get_values(maze, bots):
    return list(map(
        lambda x: maze.get_value(x),
        bots
    ))


def legal_door(maze, tup):
    (bots, keys_set) = tup
    values = get_values(maze, bots)

    return all(map(
        lambda x: not x.isupper() or x.lower() in keys_set,
        values
    ))


def all_moves(maze, bots):
    lbots = list(bots)
    res = []

    for idx in range(len(bots)):
        bot = bots[idx]
        for neighbour in maze.get_neighbours(bot):
            lbots[idx] = neighbour
            res.append(tuple(lbots))

        lbots[idx] = bot

    return res


def solve(inp):
    print('Building graph...', end='')

    maze = Maze(inp)
    knd_graph = Graph(maze)

    print('Done!')
    print('Getting blockings...', end='')

    blockings = knd_graph.get_blockings()

    # print(blockings)

    print('Done!')
    print('Calculating top sorts...', end='')

    # those top_sorts are reversed
    top_sorts = Graph.all_topological_sorts(blockings)
    print('Done!')

    # print(top_sorts)

    print('There were', len(top_sorts), 'top_sorts')
    print('Evaluating paths...')

    local_min = 1e20

    for top_sort in top_sorts:
        cost_of_order = knd_graph.cost_of_order(top_sort)
        if local_min > cost_of_order:
            local_min = cost_of_order
            print(local_min, '->', top_sort)

    print('Done!')

    return local_min


# 8
# maze = '''
# #######
# #a.#Cd#
# ##@#@##
# #######
# ##@#@##
# #cB#.b#
# #######
# '''.strip()

# 24
# maze = '''
# ###############
# #d.ABC.#.....a#
# ######@#@######
# ###############
# ######@#@######
# #b.....#.....c#
# ###############
# '''.strip()

# 32
# maze = '''
# #############
# #DcBa.#.GhKl#
# #.###@#@#I###
# #e#d#####j#k#
# ###C#@#@###J#
# #fEbA.#.FgHi#
# #############
# '''.strip()

# 72
maze = '''
#############
#g#f.D#..h#l#
#F###e#E###.#
#dCba@#@BcIJ#
#############
#nK.L@#@G...#
#M###N#H###.#
#o#m..#i#jk.#
#############
'''.strip()


# maze = '''
# #################################################################################
# ###########.........#####################.....................#...###c#.......###
# ###########.#######.#####################.#######.###########.#.#.###.#.#####.###
# #######e..#...###...#####################..b#####.###########...#.....#.#.T..r###
# #######.#.###.###.#########################.#####.#####################.#.#######
# #######.#...#.###.#########################.#####.###...#######...#####.#.......#
# #######.###.#.###.#########################.#####.###.#.#######.#.#####.#######.#
# #######...#...#...#########################.#####.....#.###.....#.#####.###.....#
# #########.#####.###########################.###########.###O#####.#####.###.#####
# #########...###.....#####################...#x#########.###...#z#.....#.###.#####
# ###########.#######.#####################.###.#########.#####.#.#####.#.###.#####
# ###########.#######.#####################...#.#########.###.....###...#...#.....#
# ###########.#######.#######################.#.#########.###.#######.#####.#####.#
# ###########...#####.#######################.#...#######.###.#######.......#....q#
# #############.#####.#######################.###.#######.###.###############.#####
# #############.#####...#####..h#############.....#######...#.###############.#####
# #############.#######.#####.#############################.#.###############.#####
# #############.#######.###...#############################...#########.......#####
# #############.#######.###F###########################################.###########
# ###########...#######...#.#############s#############################.###########
# ###########.###########.#.#############.#############################.###########
# ###d#####...###########...#############.#############################.###########
# ###.#####.#############################.#############################.###########
# ###.....#...###########################.###########################...###########
# #######.###.###########################.###########################.#############
# #######.###...#...#.......###.........#.#.....#####################...###########
# #######.#####.#.#.#.#####.###.#######.#.#.###.#######################.###########
# #####...#####.#.#...#.....#...###.....#.#.###...#################.....###########
# #####.#######.#.#####.#####.#####.#####.#.#####.#################.#.#############
# #####.#######.#...###.#...#.....#.###...#.....#.#################.#j#.....###.W.#
# #####.#######.###.###.#.#.#####.#.###.#.#####.#.#################.###.###.###.#.#
# #...#.#######.#...###.#.#.......#.....#.###...#.......###########...#.###...#.#.#
# #.#.#.#######.#.#####.#.###############.###.#########.#############.#.#####.#.#.#
# #.#...#...###.#w..#...#...#############.###.#####...#...#######...#...#.V.#...#.#
# #.#####.#.###.###.#.#####.#############.###.#####.#.###.#######.#M#####.#.#####.#
# #.....#.#...#.....#.#####.#########.....###.......#...#...#####.#.......#.......#
# #####.#.###.#######.#####.#########.#################.###.#####.#################
# #.....#.###.......#.#####.#########.....#...#.....###.###.#####.....#############
# #.#####.#########.#.#####.#############.#.#.#.###.###.###.#########.#############
# #............v###.........#############@#@#...###.....###...........#############
# #################################################################################
# ###.....#############.......#.........#@#@......#####...#################...#####
# ###.###.#############.#####.#.###.###.#.#######.#####.#.#################.#.#####
# ###.###.....#########.#####...###.###...#######......a#.......#########...#.#####
# ###.#######.#########.###########.###########################.#########.###.#####
# ###..n....#.#########.###########.....###########...###...###...#######...#.#####
# #########.#.#########.###############.###########.#.###.#.#####.#########P#.#####
# #######...#...#u..#...###############.#########...#.....#.#####.....#...#.#.#####
# #######.#####.#.#.#.#################.#########.#########.#########.#.#U#.#.#####
# #######p..###...#...#################.#########.###...#...#####...#...#.#.#...###
# #########.###########################.#########.###.#.#.#######.#.#####.#.###.###
# #...###...#################..k..#...#...#######.#...#.#.#####...#...#...#...#.###
# #.#.###.###################.###.#.#.###.#######.#.###C#Z#####.#####.#.#####.#.###
# #.#.....###################.#...#.#...#.#######.#.#...#...###...###.#...###.#.###
# #.#########################.#.###.###.#.#######.#.#.#####.#####.###.###.###.#.###
# #m#####...........#######...#...#...#.#.#######.#.#.#.....#####.#...#..g#.N.#...#
# #######.#########.#######.#####.###.#.#.#######.#B#.#.#########.#.###.###.#####.#
# ###.....#######...#######.#####.#...#...#######...#.#.......#...#...#...#.#i###.#
# ###.###########.#########.#####.#.#################.#######.#.#####.###.#.#.###.#
# #...#.......#...#####y....#...#.#.#.....#########...#######...#####.#...#.#.###.#
# #.###.#####.#.#############.#.#.#.#.###.#########.#################.#.###.#.###.#
# #...#.###...#.#############.#...#...###.#########...#############...#.....#.###.#
# ###.#.###.###.#############.###########.###########X#############.#########.###.#
# #...#.###...#.....#########...#####.....###########.###########...#######.......#
# #Q###.#####.#####.###########.#####.###############.###########.#########.#######
# #.....#####.#####.........#...###...###############...#########.#.......#.......#
# ###########.#############.#.#####.###################.#########.#D#####.#######.#
# ###...#####.###.....#####...###...###################..l#####...#.#####.......#.#
# ###.#.#####.###.###.###########.#############################.###.###########.#.#
# #...#...###.....#...###########.........#####################.###...#########...#
# #.#####.#########.#####################.#####################.#####.#############
# #.###t#.#######...#####################.#####################.###...###...#######
# #.###.#.#######.#######################.#####################.###.#####.#.#######
# #...#...###...#.#######.......#######...#############.........###.......#.#######
# ###.#######.#.#.#######.#####.#######.###############.#####.#############.#######
# ###.#####...#.#...#####.#####...#####...#...###.....#.#####.....#####.....#######
# ###.#####.###I###.#####.#######.#######.#.#.###.###.#.#########.#####.###########
# #...#...#...#.###.###...#######.#...###.#.#..f..###...#######...#.....###########
# #.###.#.###.#.###.###.#########.#.#.###.#.###################.###.###############
# #.J...#.....#.........#########...#.....#.............H....o#.....###############
# #################################################################################
# '''.strip()

res = solve(maze)

print(res)
