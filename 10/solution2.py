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

    def __hash__(self):
        return hash((self.x, self.y))

    def __sub__(self, p):
        return Point(self.x-p.x, self.y-p.y)


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


def all_visible(a, asteroids):
    res = []

    for candidate in asteroids:
        if candidate == a:
            continue
        if not is_visible(a, candidate, asteroids):
            continue
        res.append(candidate)

    return set(res)


def destroy_until_last_rotation(laser, asteroids, to_destroy):
    will_destroy = all_visible(laser, asteroids)
    if len(will_destroy) >= to_destroy:
        return will_destroy, to_destroy

    return destroy_until_last_rotation(laser, asteroids - will_destroy, to_destroy - len(will_destroy))


def select_nth(laser, asteroids, n):
    def angle_to_north(p):
        angle_from_pos_x = math.atan2(p.y - laser.y, p.x - laser.x)
        return 2 * math.pi + angle_from_pos_x if angle_from_pos_x < - math.pi / 2 else angle_from_pos_x
    # print(len(asteroids))
    return sorted(asteroids, key=angle_to_north)[n-1]  # .index(Point(8,2))


def solve(laser, asteroid_map_input):
    asteroids = set(parse(asteroid_map_input)) - set([laser])
    last_rotation_asteroids, n = destroy_until_last_rotation(laser, asteroids, 200)

    return select_nth(laser, last_rotation_asteroids, n)


laser_point = Point(23, 19)

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


print(solve(laser_point, asteroid_map))
