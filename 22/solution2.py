import functools

DECK_SIZE = 119315717514047
# DECK_SIZE = 10007


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


def solve_once():
    file = open("input.txt", "r")
    lines = [line.rstrip('\n') for line in file]
    functions = list(map(
        parse_line,
        lines
    ))

    return lambda idx: functools.reduce(lambda e, f: f(e), functions, idx)


def get_period(check_idx):
    solver = solve_once()

    visited = set()
    idx = check_idx

    while True:
        print(len(visited))
        idx = solver(idx)
        if idx in visited:
            return len(visited)
        visited.add(idx)


def solve(check_idx, num_to_apply):
    period = get_period(check_idx)
    num_to_apply %= period

    solver = solve_once()
    idx = check_idx
    for _ in range(num_to_apply):
        idx = solver(idx)

    return idx


res = solve(2020, 101741582076661)
print(res)
