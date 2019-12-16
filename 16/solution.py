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
    numbers = [int(x) for x in message]
    for i in range(iterations):
        print("Iteration", i)
        numbers = fft(numbers)

    return [str(x) for x in numbers]


message = "5972731042479623518947687806940387435291429226818921130171187957262146115559932358924341808253400617220924411865224341744614706346865536561788244183609411225788501102400269978290670307147139438239865673058478091682748114942700860895620690690625512670966265975462089087644554004423208369517716075591723905075838513598360188150158989179151879406086757964381549720210763972463291801513250953430219653258827586382953297392567981587028568433943223260723561880121205475323894070000380258122357270847092900809245133752093782889315244091880516672127950518799757198383131025701009960944008679555864631340867924665650332161673274408001712152664733237178121872"
res = solve(message, 100)
print("".join(res[:8]))
