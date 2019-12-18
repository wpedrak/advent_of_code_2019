from collections import deque
from point import Point


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
                    self.board[point] = Maze.EMPTY
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
        visited = set()
        to_visit = deque([p, 'LVL_UP'])
        dist = 0

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
                res.append([value, dist])
                continue

            to_visit += deque([n for n in self.get_neighbours(current) if n not in visited])

        return res


def solve(inp):
    maze = Maze(inp)
    propositions = maze.get_propositions(maze.player)

    print(propositions)


maze = """
########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################
""".strip()

res = solve(maze)

print(res)
