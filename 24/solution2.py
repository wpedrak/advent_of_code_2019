from point import Point
from collections import defaultdict as dd


class Bugs():

    BUG = '#'
    EMPTY = '.'

    def __init__(self, inp):
        rows = inp.split()
        self.board = dd(lambda: Bugs.EMPTY)

        for y in range(5):
            for x in range(5):
                value = rows[y][x]
                point = Point(x, y)
                level = 0
                self.board[(point, level)] = value

    def get_neighbours(self, point, level):
        assert(0 <= point.x <= 5)
        assert(0 <= point.y <= 5)
        # assert(point != Point(2, 2))

        on_this_level = []
        if point.x != 0:
            on_this_level.append((Point(point.x - 1, point.y), level))
        if point.x != 4:
            on_this_level.append((Point(point.x + 1, point.y), level))
        if point.y != 0:
            on_this_level.append((Point(point.x, point.y - 1), level))
        if point.y != 4:
            on_this_level.append((Point(point.x, point.y + 1), level))

        on_this_level = list(filter(lambda x: x[0] != Point(2, 2), on_this_level))

        on_level_below = []
        if point.x == 0:
            on_level_below.append((Point(1, 2), level - 1))
        if point.x == 4:
            on_level_below.append((Point(3, 2), level - 1))
        if point.y == 0:
            on_level_below.append((Point(2, 1), level - 1))
        if point.y == 4:
            on_level_below.append((Point(2, 3), level - 1))

        on_level_above = []
        if point == Point(1, 2):
            on_level_above += [(Point(0, y), level + 1) for y in range(5)]
        if point == Point(3, 2):
            on_level_above += [(Point(4, y), level + 1) for y in range(5)]
        if point == Point(2, 1):
            on_level_above += [(Point(x, 0), level + 1) for x in range(5)]
        if point == Point(2, 3):
            on_level_above += [(Point(x, 4), level + 1) for x in range(5)]

        assert(len(on_this_level + on_level_below + on_level_above) in [4, 8])

        return on_this_level + on_level_below + on_level_above

    def evolve(self):
        evolution = dd(lambda: 0)

        for (point, level), val in dict(self.board).items():
            if val != Bugs.BUG:
                continue

            if not (point, level) in evolution:
                evolution[(point, level)] = 0

            neighbours = self.get_neighbours(point, level)
            # print(point)
            # print(neighbours)
            # print()
            for pl in neighbours:  # pl = point and level
                # print(pl)
                evolution[pl] += 1

        # print(evolution)

        for pl, num_of_neighbours in evolution.items():
            # print(pl, num_of_neighbours)
            assert(num_of_neighbours >= 0)
            if self.board[pl] == Bugs.BUG:
                self.board[pl] = Bugs.BUG if num_of_neighbours == 1 else Bugs.EMPTY
            elif self.board[pl] == Bugs.EMPTY:
                self.board[pl] = Bugs.BUG if num_of_neighbours in [1, 2] else Bugs.EMPTY
            else:
                raise Exception('Wrong value in board')

    def count(self):
        return sum([1 for val in self.board.values() if val == Bugs.BUG])

    def display_level(self, level_nr):
        level = dd(lambda: Bugs.EMPTY)
        for (k, _), v in filter(lambda x: x[0][1] == level_nr, self.board.items()):
            level[k] = v

        rows = []

        for y in range(5):
            row = []
            for x in range(5):
                row.append(str(level[Point(x, y)]))
            rows.append(row)

        image = "\n".join(map(lambda x: "".join(x), rows))

        print(image)


def solve(inp, time):
    bugs = Bugs(inp)

    for i in range(time):
        print("Evolution", i)
        bugs.evolve()

    # for x in range(5):
    #     for y in range(5):
    #         p = Point(x, y)
    #         print(p, bugs.get_neighbours(p, 0))

    # for i in range(-5, 6):
    #     print(i)
    #     print(bugs.display_level(i))
    #     print()
    return bugs.count()


bugs = '''
##.#.
#..#.
.....
....#
#.###
'''.strip()

res = solve(bugs, 200)

print(res)
