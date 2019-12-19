import math


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
        if not isinstance(p, Point):
            return False
        return self.x == p.x and self.y == p.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __sub__(self, p):
        return Point(self.x-p.x, self.y-p.y)

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)
