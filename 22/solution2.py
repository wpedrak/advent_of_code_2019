import math
from stolen_code import modinv

DECK_SIZE = 119315717514047


def get_line_params(line):
    splitted = line.split()
    first = splitted[0]
    second = splitted[1]
    if first == 'cut':
        return (1, int(second))
    elif second == 'into':
        return (-1, -1)
    elif second == 'with':
        return (modinv(int(splitted[-1]), DECK_SIZE), 0)


def input_as_operator(nrepeat=1):
    file = open("input.txt", "r")
    lines = [line.rstrip('\n') for line in file]

    mul = 1
    add = 0

    for line in reversed(lines):
        a, b = get_line_params(line)
        mul = mul * a
        add = add * a + b

    mul %= DECK_SIZE
    add %= DECK_SIZE

    master_mul = 1
    master_add = 0

    for _ in range(nrepeat):
        master_mul = (master_mul * mul) % DECK_SIZE
        master_add = (master_add * mul + add) % DECK_SIZE

    return lambda x: (x * master_mul + master_add) % DECK_SIZE


def solve(check_idx, num_to_apply):
    sqrt_num = int(math.sqrt(num_to_apply))
    print('getting solver for', sqrt_num)
    sqrt_solver = input_as_operator(nrepeat=sqrt_num)
    print('solver generated')
    idx = check_idx

    print('applying solver', sqrt_num, 'times')
    for _ in range(sqrt_num):
        idx = sqrt_solver(idx)

    print('solver applied')

    solver = input_as_operator()
    rest = num_to_apply - (sqrt_num * sqrt_num)

    print('finishing with small solver', rest)

    for _ in range(rest):
        idx = solver(idx)

    print('done')

    return idx


res = solve(2020, 101741582076661)
print(res)
