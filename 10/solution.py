import math

EMPTY = '.'
ASTEROID = '#'


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist(self, p):
        return math.sqrt((self.x - p.x) ** 2 + (self.y - p.y) ** 2)

    def is_between(self, p1, p2):
        return self.dist(p1) + self.dist(p2) - p1.dist(p2) < 1e-8

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return str(self)

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y


def parse(inp):
    str_rows = inp.split()
    points = []

    for y, str_row in enumerate(str_rows):
        for x, field in enumerate(str_row):
            if field == EMPTY:
                continue
            points.append(Point(x, y))

    return points


def is_visible(p1, p2, points):
    for obstacle in points:
        if obstacle.is_between(p1, p2) and obstacle != p1 and obstacle != p2:
            return False

    return True


def visible(a, asteroids):
    print("Calculate", a)
    count = 0

    for candidate in asteroids:
        if candidate == a:
            continue
        if not is_visible(a, candidate, asteroids):
            continue
        count += 1

    return count


def solve(asteroid_map_input):
    asteroids = parse(asteroid_map_input)
    asteroids_with_visible = [(a, visible(a, asteroids)) for a in asteroids]
    # print("part res", visible(Point(11, 13), asteroids))
    return max(asteroids_with_visible, key=lambda x: x[1])


asteroid_map = '''.#......#...#.....#..#......#..##..#
..#.......#..........#..##.##.......
##......#.#..#..#..##...#.##.###....
..#........#...........#.......##...
.##.....#.......#........#..#.#.....
.#...#...#.....#.##.......#...#....#
#...#..##....#....#......#..........
....#......#.#.....#..#...#......#..
......###.......#..........#.##.#...
#......#..#.....#..#......#..#..####
.##...##......##..#####.......##....
.....#...#.........#........#....#..
....##.....#...#........#.##..#....#
....#........#.###.#........#...#..#
....#..#.#.##....#.........#.....#.#
##....###....##..#..#........#......
.....#.#.........#.......#....#....#
.###.....#....#.#......#...##.##....
...##...##....##.........#...#......
.....#....##....#..#.#.#...##.#...#.
#...#.#.#.#..##.#...#..#..#..#......
......#...#...#.#.....#.#.....#.####
..........#..................#.#.##.
....#....#....#...#..#....#.....#...
.#####..####........#...............
#....#.#..#..#....##......#...#.....
...####....#..#......#.#...##.....#.
..##....#.###.##.#.##.#.....#......#
....#.####...#......###.....##......
.#.....#....#......#..#..#.#..#.....
..#.......#...#........#.##...#.....
#.....####.#..........#.#.......#...
..##..#..#.....#.#.........#..#.#.##
.........#..........##.#.##.......##
#..#.....#....#....#.#.......####..#
..............#.#...........##.#.#..'''

print(solve(asteroid_map))
