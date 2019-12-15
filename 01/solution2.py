file = open("input.txt", "r")
lines = [line.rstrip('\n') for line in file]


def fuel(mass):
    needed = mass // 3 - 2
    if needed <= 0:
        return 0
    return needed + fuel(needed)


print(sum([fuel(int(line)) for line in lines]))
