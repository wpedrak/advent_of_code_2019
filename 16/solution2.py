import numpy as np
import itertools


def get_pattern(length_of_single, length_of_pattern):
    base = ([0] * length_of_single) + ([1] * length_of_single) + ([0] * length_of_single) + ([-1] * length_of_single)
    it = itertools.cycle(base)
    next(it)
    return [next(it) for _ in range(length_of_pattern)]


def fft(numbers):
    res = []
    arr_numbers = np.array(numbers).reshape(-1, 1)
    for idx in range(len(numbers)):
        pattern = np.array(get_pattern(idx+1, len(numbers))).reshape(1, -1)
        new_number = (np.abs(pattern.dot(arr_numbers)) % 10)[0, 0]
        res.append(new_number)

    return res


def solve(message, iterations):
    offset = int(message[:7])
    # print(offset)
    numbers = [int(x) for x in message] * 10000
    for i in range(iterations):
        print("Iteration", i)
        numbers = fft(numbers)

    return [str(x) for x in numbers][offset:offset + 8]


message = "03036732577212944063491565474664"
res = solve(message, 100)
print("".join(res))
