from point import Point
from collections import defaultdict as dd


class Bugs():

    BUG = '#'
    EMPTY = '.'

    def __init__(self, inp):
        rows = inp.split()
        self.board = dd(lambda: Bugs.EMPTY)
        self.width = len(rows[0])
        self.height = len(rows)

        for y in range(self.height):
            for x in range(self.width):
                value = rows[y][x]
                point = Point(x, y)
                self.board[point] = value

    def get_neighbours_num(self, p):
        potential = [
            Point(p.x, p.y + 1),
            Point(p.x, p.y - 1),
            Point(p.x - 1, p.y),
            Point(p.x + 1, p.y)
        ]

        return len(list(filter(lambda x: self.board[x] == Bugs.BUG, potential)))

    def rating(self):
        rating = 0

        for x in range(self.width):
            for y in range(self.height):
                p = Point(x, y)
                potential_point_raiting = 2 ** (5*y + x)
                rating += potential_point_raiting * (self.board[p] == Bugs.BUG)

        return rating

    def evolve(self):
        evolution = dd(lambda: 0)

        for x in range(self.width):
            for y in range(self.height):
                p = Point(x, y)
                evolution[p] = self.get_neighbours_num(p)

        for x in range(self.width):
            for y in range(self.height):
                p = Point(x, y)
                num_of_neighbours = evolution[p]
                if self.board[p] == Bugs.BUG:
                    self.board[p] = Bugs.BUG if num_of_neighbours == 1 else Bugs.EMPTY
                elif self.board[p] == Bugs.EMPTY:
                    self.board[p] = Bugs.BUG if num_of_neighbours in [1, 2] else Bugs.EMPTY
                else:
                    raise Exception('Wrong walue in board')

    def display(self):
        rows = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(str(self.board[Point(x, y)]))
            rows.append(row)

        image = "\n".join(map(lambda x: "".join(x), rows))

        print(image)


def solve(inp):
    bugs = Bugs(inp)
    rating = bugs.rating()
    visited_ratings = set()

    while rating not in visited_ratings:
        visited_ratings.add(rating)
        bugs.evolve()
        rating = bugs.rating()

    return rating


bugs = '''
##.#.
#..#.
.....
....#
#.###
'''.strip()

res = solve(bugs)

print(res)
