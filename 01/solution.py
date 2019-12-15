file = open("input.txt", "r")
lines = [line.rstrip('\n') for line in file]

print(sum([int(line)//3 - 2 for line in lines]))
