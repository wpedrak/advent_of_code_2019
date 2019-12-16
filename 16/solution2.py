import numpy as np


def fft(numbers):
    arr_numbers = np.array(numbers)
    ones = 
    compl = np.fft.fft(arr_numbers)
    print('---------------------------------------------')
    print(arr_numbers)
    print(compl)
    print(np.absolute(compl))
    print('---------------------------------------------')
    mask = (np.sign(compl.real) + np.sign(compl.imag)) / 2
    results = np.absolute(compl) * mask
    return list(results)


def solve(message, iterations):
    # offset = int(message[:7])
    # print(offset)
    numbers = [int(x) for x in message]  # * 10000
    for i in range(iterations):
        print("Iteration", i)
        numbers = fft(numbers)
        print(numbers)

    return numbers
    # return [str(x) for x in numbers][offset:offset + 8]


message = "12345678"
res = solve(message, 4)
print("".join(res))
