from collections import deque, defaultdict as dd
from point import Point


class Maze():

    WALL = '#'
    EMPTY = '.'
    UNKNOWN = ' '

    def __init__(self, inp):
        rows = inp.split("\n")
        self.board = dd(lambda: Maze.UNKNOWN)
        self.teleports = dd(lambda: [])

        for y in range(len(rows)):
            for x in range(len(rows[0])):
                value = rows[y][x]
                point = Point(x, y)
                self.board[point] = value

        # print(self.board)

        for p, item in dict(self.board).items():
            if item.isalpha():
                print(p)
                name, refer_to = self.parse_teleport(p)
                if name:
                    self.teleports[name].append(refer_to)

    def parse_teleport(self, point):
        neighbours = self.get_neighbours(point)
        snd_letter_point = list(filter(
            lambda x: self.board[point].isalpha(),
            neighbours
        ))[0]

        potential_tlp_from = list(filter(
            lambda x: self.board[x] == Maze.EMPTY,
            neighbours
        ))

        # name is read from empty tile
        potential_name = self.board[point] + self.board[snd_letter_point]

        if potential_tlp_from:
            return potential_name, potential_tlp_from[0]

        tlp_from = list(filter(
            lambda x: self.board[x] == Maze.EMPTY,
            self.get_neighbours(snd_letter_point)
        ))

        print(point)
        print(potential_name)
        print(snd_letter_point)
        print(self.get_neighbours(snd_letter_point))
        print(tlp_from)

        return ''.join(list(reversed(potential_name))), tlp_from[0]

    def get_neighbours(self, p):
        potential = [
            Point(p.x, p.y + 1),
            Point(p.x, p.y - 1),
            Point(p.x - 1, p.y),
            Point(p.x + 1, p.y)
        ]

        return list(filter(lambda x: self.board[x] != Maze.WALL, potential))

    def expand_tlp(self, tlp_point, point):
        if not self.board[point].isalpha():
            return point

        hunt_for_snd_letter = list(filter(
            lambda p: self.board[p].isalpha(),
            self.get_neighbours(point)
        ))

        name = self.board[point] + self.board[hunt_for_snd_letter[0]]

        return list(filter(
            lambda p: p != tlp_point,
            self.teleports[name]
        ))

    def get_all_neighbours(self, point):
        return [self.expand_tlp(point, n) for n in self.get_neighbours(point)]
        

    def find_path(self):
        visited = set()
        to_visit = deque(self.teleports['AA'][0] ['LVL_UP'])
        dist = 0

        target = self.teleports['ZZ'][0]

        while len(to_visit) > 1:
            current = to_visit.popleft()
            visited.add(current)

            if current == 'LVL_UP':
                dist += 1
                to_visit.append('LVL_UP')
                continue

            if current == target:
                return dist

            to_visit += deque([n for n in self.get_all_neighbours(current) if n not in visited])

        raise Exception('Failed to reach ZZ')


def solve(inp):
    maze = Maze(inp)
    return maze.find_path()


maze = '''         A           
         A           
  #######.#########  
  #######.........#  
  #######.#######.#  
  #######.#######.#  
  #######.#######.#  
  #####  B    ###.#  
BC...##  C    ###.#  
  ##.##       ###.#  
  ##...DE  F  ###.#  
  #####    G  ###.#  
  #########.#####.#  
DE..#######...###.#  
  #.#########.###.#  
FG..#########.....#  
  ###########.#####  
             Z       
             Z       '''

res = solve(maze)

print(res)
