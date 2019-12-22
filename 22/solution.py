DECK_SIZE = 10007


def deal_into_new(i):
    return (DECK_SIZE-1) - i


def cut(shift):
    def aux(i):
        return (i - shift) % DECK_SIZE

    return aux


def deal_with_increment(inc):
    def aux(i):
        return (i * inc) % DECK_SIZE

    return aux


def parse_line(line):
    splitted = line.split()
    first = splitted[0]
    second = splitted[1]
    if first == 'cut':
        return cut(int(second))
    elif second == 'into':
        return deal_into_new
    elif second == 'with':
        return deal_with_increment(int(splitted[-1]))


def solve(check_idx):
    file = open("input.txt", "r")
    lines = [line.rstrip('\n') for line in file]

    position = check_idx

    for line in lines:
        shuffle = parse_line(line)
        position = shuffle(position)

    return position


res = solve(2019)
print(res)
