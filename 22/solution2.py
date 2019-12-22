import functools

DECK_SIZE = 119315717514047
# DECK_SIZE = 10007


def get_line_params(line):
    splitted = line.split()
    first = splitted[0]
    second = splitted[1]
    if first == 'cut':
        return 1, - int(second)
    elif second == 'into':
        return -1, -1
    elif second == 'with':
        return int(splitted[-1]), 0


def input_as_single_operator():
    file = open("input.txt", "r")
    lines = [line.rstrip('\n') for line in file]

    mul = 1
    add = 0

    for line in lines:
        a, b = get_line_params(line)
        mul = mul * a
        add = add * a + b

    mul %= DECK_SIZE
    add %= DECK_SIZE

    return lambda x: (x * mul + add) % DECK_SIZE
    # return mul, add


def solve(check_idx, num_to_apply):
    solver = input_as_single_operator()


res = solve(2020, 101741582076661)
print(res)
