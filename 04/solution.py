rfrom = 272091
rto = 815432

possible_numbers = range(rfrom, rto+1)


def check_prop1(n):
    return 1e5 <= n < 1e6


def check_prop3(n):
    sn = str(n)
    shifted = 'a' + sn
    pairs = zip(shifted, sn)
    return any(map(lambda x: x[0] == x[1], pairs))


def check_prop4(n):
    sn = str(n)
    shifted = '0' + sn
    pairs = [(int(a), int(b)) for a, b in zip(shifted, sn)]
    # print(pairs)
    return all(map(lambda x: x[0] <= x[1], pairs))


non_filtered = list(possible_numbers)
print(len(non_filtered))
filtered1 = list(filter(check_prop1, non_filtered))
print(len(filtered1))
filtered3 = list(filter(check_prop3, filtered1))
print(len(filtered3))
filtered4 = list(filter(check_prop4, filtered3))
print(len(filtered4))

all_ok = filtered4

print(len(all_ok))

# print(check_prop4(111111))
