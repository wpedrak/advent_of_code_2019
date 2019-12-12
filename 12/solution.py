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


moons = [
    Moon(13, -13, -2),
    Moon(16, 2, -15),
    Moon(7, -18, -12),
    Moon(-3, -8, -8)
]

num_steps = 1000
# num_steps = 10

# moons = [
#     Moon(-1, 0, 2),
#     Moon(2, -10, -7),
#     Moon(4, -8, 8),
#     Moon(3, 5, -1)
# ]

for step in range(num_steps):
    for moon in moons:
        apply_gravitys(moon, moons)

    for moon in moons:
        moon.move()

moons_energy = [m.total_energy() for m in moons]

print(sum(moons_energy))
