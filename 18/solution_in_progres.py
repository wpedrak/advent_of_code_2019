from collections import deque
from point import Point
from collections import defaultdict as dd


class Maze():

    WALL = '#'
    EMPTY = '.'
    PLAYER = '@'

    def __init__(self, inp):
        rows = inp.split()
        self.board = {}
        self.knd = {}  # keys and doors

        for y in range(len(rows)):
            for x in range(len(rows[0])):
                value = rows[y][x]
                point = Point(x, y)

                if value == Maze.PLAYER:
                    self.player = point
                    self.board[point] = Maze.WALL
                    continue
                elif value.isalpha():
                    self.knd[value] = point

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
            # print(len(to_visit))
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


class Graph:

    def __init__(self, maze):
        self.edges = {}

        self.from_start = maze.get_propositions(maze.player)

        for item, point in maze.knd.items():
            self.edges[item] = maze.get_propositions(point)

        # print(self.edges)

        edges_for_dists = dict(self.edges)
        edges_for_dists.update({'@': self.from_start})

        self.distances = Graph.all_distances(edges_for_dists)
        self.from_player = dict(self.from_start)

    def show_edges(self):
        for k, v in self.edges.items():
            print(f"{k} -> {v}")

    def dist(self, char_a, char_b):
        a = ord(char_a)
        b = ord(char_b)
        return self.distances[a][b]

    def cost_of_order(self, order):
        cost = 0
        # print(order)
        for idx in range(len(order) - 1):
            a = order[idx]
            b = order[idx+1]
            cost += self.dist(a, b)

        return cost + self.dist('@', order[-1])

    @staticmethod
    def all_distances(edges):
        # print(edges)
        size = ord('z')
        dists = [[1e20] * size for _ in range(size)]

        # print(edges)

        all_edges = [(ord(from_v), ord(to_v), weight) for from_v, lst in edges.items() for to_v, weight in lst]
        # print(all_edges)

        for from_v, to_v, val in all_edges:
            # print(from_v, to_v, val)
            dists[from_v][to_v] = val
            dists[to_v][from_v] = val

        for v in range(size):
            dists[v][v] = 0

        for k in range(size):
            for i in range(size):
                for j in range(size):
                    dists[i][j] = min(dists[i][j], dists[i][k] + dists[k][j])

        # print(dists[])
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

        # print(aux(node, []))
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
            # print(current)
            # print(visited)
            # print('will point to ', list(neighbours - used_in_tree))

            tree_edges[current] = list(neighbours - used_in_tree)

            used_in_tree = used_in_tree | neighbours

            to_visit += deque([n for n in neighbours if n not in visited])


        # print(tree_edges)
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
        # print(edges)
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

        # print(edges)
        # print(aux(node, []))
        return aux(node, [])

    def get_blockings(self):
        letters_edges = {}
        for n, vals in self.edges.items():
            letters_edges[n] = [k for k, _ in vals]
        letters_edges['@'] = [k for k, _ in self.from_start]
        tree_edges = Graph.treefy(letters_edges, '@')
        # print(tree_edges)
        is_blocked_by = Graph.get_blockings_in_tree('@', tree_edges)
        extended_is_blocked_by = Graph.extend_blocking(is_blocked_by)
        # print(is_blocked_by)
        is_preceded_by = Graph.get_preceedings_in_tree('@', tree_edges)
        # print(is_preceded_by)
        # raise Exception()

        dependency = dd(lambda: [])
        for k, v in extended_is_blocked_by.items():
            dependency[k] += v
        for k, v in is_preceded_by.items():
            dependency[k] += v

        # print(dict(dependency))
        
        return Graph.reverse_arrows(dict(dependency))

    @staticmethod
    def all_topological_sorts(will_unlock):
        def aux(vertices):
            # print('vertices', vertices)
            if not vertices:
                return [[]]

            all_locked = set([item for k, items in will_unlock.items() if k in vertices for item in items])
            unlocked = vertices - all_locked

            # print('vertices', vertices)
            # print('all_locked', all_locked)
            # print('unlocked', unlocked)

            res = []

            for item in unlocked:
                # print('will go', unlocked - set([item]))
                smaller_sorts = aux(vertices - set([item]))
                res += [srt + [item] for srt in smaller_sorts]

            return res

        # print('will_unlock', will_unlock)
        return aux(set(will_unlock))


def solve(inp):
    print('building graph...', end='')

    maze = Maze(inp)
    knd_graph = Graph(maze)

    blockings = knd_graph.get_blockings()

    print('Done!')
    print('Calculating top sorts...', end='')

    # those top_sorts are reversed
    top_sorts = Graph.all_topological_sorts(blockings)
    print('Done!')

    # print(top_sorts)

    print('There were', len(top_sorts), 'top_sorts')
    print('Evaluating paths...', end='')

    local_min = 1e20
    cnt = 0

    for top_sort in top_sorts:
        cnt += 1
        if cnt % 1000000 == 0:
            print(cnt)
        cost_of_order = knd_graph.cost_of_order(top_sort)
        # print(cost_of_order)
        if local_min > cost_of_order:
            local_min = cost_of_order
            print(local_min, '->', top_sort)
    
    print('Done!')

    return local_min


def simplify(maze):
    deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    height = len(maze)
    width = len(maze[0])

    for y in range(1, height-1):
        row = maze[y]
        for x in range(1, width-1):
            neighbours = [(x + dx, y + dy) for dx, dy in deltas]
            num_hash = len(list(filter(
                lambda t: maze[t[1]][t[0]] == '#',
                neighbours
            )))

            if num_hash >= 3 and not row[x].islower():
                row[x] = '#'
                continue


def analize(inp):
    maze = [list(row) for row in inp.split()]

    for i in range(300):
        print(i)
        simplify(maze)

    for row in maze:
        print(''.join(row))

# 8
# maze = '''
# #########
# #b.A.@.a#
# #########
# '''.strip()

# 86
# maze = '''
# ########################
# #f.D.E.e.C.b.A.@.a.B.c.#
# ######################.#
# #d.....................#
# ########################
# '''.strip()

# 132
# maze = '''
# ########################
# #...............b.C.D.f#
# #.######################
# #.....@.a.B.c.d.A.e.F.g#
# ########################
# '''.strip()

# 136
maze = '''
#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################
'''.strip()

# 81
# maze = '''
# ########################
# #@..............ac.GI.b#
# ###d#e#f################
# ###A#B#C################
# ###g#h#i################
# ########################
# '''.strip()

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
# #............v###.........#############...#...###.....###...........#############
# #######################################.@.#######################################
# ###.....#############.......#.........#.........#####...#################...#####
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

# analize(maze)
