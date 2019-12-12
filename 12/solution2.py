import math


class Moon():

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0

    def apply_gravity(self, moon):
        self.vx += Moon.gravity_change(self.x, moon.x)
        self.vy += Moon.gravity_change(self.y, moon.y)
        self.vz += Moon.gravity_change(self.z, moon.z)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

    def potential_energy(self):
        return abs(self.x) + abs(self.y) + abs(self.z)

    def kinetic_energy(self):
        return abs(self.vx) + abs(self.vy) + abs(self.vz)

    def total_energy(self):
        return self.potential_energy() * self.kinetic_energy()

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z}) -> <{self.vx}, {self.vy}, {self.vz}>"

    @staticmethod
    def gravity_change(x1, x2):
        if x1 == x2:
            return 0
        return 1 if x1 < x2 else -1


def apply_gravitys(moon, rest):
    for another in rest:
        moon.apply_gravity(another)


def lcm(x, y):
    return (x * y) // math.gcd(x, y)


def velocity_change(pos, positions):
    change = 0
    for pos2 in positions:
        change += Moon.gravity_change(pos, pos2)

    return change


def solve1d(moons_pos, moons_v):
    positions = moons_pos[:]
    velocity = moons_v[:]
    steps = 0

    state = (tuple(positions), tuple(velocity))
    visited = set()

    while state not in visited:
        visited.add(state)

        for idx, pos in enumerate(positions):
            velocity[idx] += velocity_change(pos, positions)

        for idx, v in enumerate(velocity):
            positions[idx] += v

        steps += 1
        state = (tuple(positions), tuple(velocity))

    return steps


moons = [
    Moon(13, -13, -2),
    Moon(16, 2, -15),
    Moon(7, -18, -12),
    Moon(-3, -8, -8)
]
# moons = [
#     Moon(-1, 0, 2),
#     Moon(2, -10, -7),
#     Moon(4, -8, 8),
#     Moon(3, 5, -1)
# ]  # 2772 steps

steps_x = solve1d([m.x for m in moons], [m.vx for m in moons])
steps_y = solve1d([m.y for m in moons], [m.vy for m in moons])
steps_z = solve1d([m.z for m in moons], [m.vz for m in moons])

steps = lcm(lcm(steps_x, steps_y), steps_z)

print(steps)
