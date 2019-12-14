import math
from collections import defaultdict as dd


class Reaction:

    def __init__(self, ing, res):
        self.ing = ing
        self.name = res[1]
        self.q = res[0]

    def produce(self, quantity, bag, reactions):
        in_bag = bag[self.name]
        if in_bag >= quantity:
            return

        to_produce = quantity - in_bag
        number_of_reactions = math.ceil(to_produce / self.q)

        for q, name in self.ing:
            reactions[name].produce(q * number_of_reactions, bag, reactions)
            bag[name] -= q * number_of_reactions

        bag[self.name] += number_of_reactions * self.q


class OreReaction:

    def produce(self, quantity, bag, reactions):
        bag['YOU_WILL_PAY'] += quantity
        bag['ORE'] += quantity


def parse_pair(pair):
    num, name = (pair.strip().split())
    return (int(num), name)


def parse_ingredients(ingridients):
    partial = ingridients.split(',')
    return [parse_pair(p) for p in partial]


def parse_reactions(in_file):
    file = open("input.txt", "r")
    lines = [line.rstrip('\n') for line in file]
    reactions = {}

    for line in lines:
        ingredients, result = line.split('=>')
        ingredients = parse_ingredients(ingredients)
        result = parse_pair(result)
        reaction = Reaction(ingredients, result)

        reactions[result[1]] = reaction

    return reactions


reactions = parse_reactions("input.txt")
reactions['ORE'] = OreReaction()

bag = dd(lambda: 0)
res = reactions['FUEL'].produce(1, bag, reactions)

print(bag['YOU_WILL_PAY'])

# for k, v in bag.items():
#     if v:
#         print(k, '->', v)
