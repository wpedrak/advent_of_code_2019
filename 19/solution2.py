from int_computer import Computer, Queue
from point import Point
from collections import defaultdict as dd

import numpy as np


class Laser:

    LASER = '#'
    EMPTY = '.'
    UNKNOWN = ' '

    def __init__(self, tape):
        self.in_queue = Queue(name="in")
        self.out_queue = Queue(name="out")
        self.tape = tape
        self.points = dd(lambda: Laser.UNKNOWN)

    def get_info(self, p):
        current_knowlage = self.points[p]
        if current_knowlage != Laser.UNKNOWN:
            return current_knowlage

        computer = Computer(inq=self.in_queue, outq=self.out_queue)
        computer.load(self.tape)

        self.in_queue.put_message(p.x)
        self.in_queue.put_message(p.y)
        computer.run()

        res = self.out_queue.get_message()
        symbol = Laser.LASER if res else Laser.EMPTY
        self.points[p] = symbol

        return symbol

    def display(self):
        max_x = max(self.points, key=lambda x: x.x).x
        max_y = max(self.points, key=lambda x: x.y).y

        rows = []

        for y in range(max_y):
            row = []
            for x in range(max_x):
                row.append(str(self.points[Point(x, y)]))
            rows.append(row)

        image = "\n".join(map(lambda x: "".join(x), rows))

        print(image)

    def find_borders(self, iters, start_point=None):
        if not start_point:
            start_point = Point(8, 9)  # checked on image

        if self.get_info(start_point) != Laser.LASER:
            raise Exception('Wrong start')

        self.top = []
        self.bot = []

        curr_top = start_point  # any LASER in line
        curr_bot = start_point  # first empty in line
        while self.get_info(curr_bot) != Laser.EMPTY:
            curr_bot = curr_bot - Point(1, 0)

        while iters:
            while self.get_info(curr_top) != Laser.EMPTY:
                curr_top = Point(curr_top.x + 1, curr_top.y)
            self.top.append(curr_top - Point(1, 0))
            curr_top = Point(curr_top.x, curr_top.y + 1)

            while self.get_info(curr_bot) != Laser.LASER:
                curr_bot = Point(curr_bot.x + 1, curr_bot.y)
            self.bot.append(curr_bot)
            curr_bot = Point(curr_bot.x, curr_bot.y + 1)

            if iters % 10 == 0:
                print(iters)

            iters -= 1

    @staticmethod
    def linear_regression(X_list, Y_list):
        X = np.array(X_list).reshape(1, -1)
        Y = np.array(Y_list).reshape(1, -1)

        return np.linalg.inv(X.dot(X.T)).dot(X).dot(Y.T)[0, 0]

    def aprox(self):
        top_X = [p.x for p in self.top]
        top_Y = [p.y for p in self.top]
        bot_X = [p.x for p in self.bot]
        bot_Y = [p.y for p in self.bot]

        top_theta = Laser.linear_regression(top_X, top_Y)
        bot_theta = Laser.linear_regression(bot_X, bot_Y)

        self.top_theta = top_theta
        self.bot_theta = bot_theta
        self.approx = (top_theta + bot_theta) / 2

    def get_point_where_gap_is(self, gap):
        # print(self.top_theta)
        # print(self.bot_theta)
        x = int(gap / (self.bot_theta - self.top_theta))
        # print(x)
        res = Point(x, int(self.approx * x))

        if self.get_info(res) != Laser.LASER:
            raise Exception('Gap point in not laser')

        return res

    # def check_gap_size(self, p):

    def find_square(self, desired_size):
        best = 0
        minim = 1e9

        for top in self.top:
            for bot in self.bot:
                if bot.y - top.y != desired_size:
                    continue
                size = top.x - bot.x
                best = max(best, size)
                minim = min(minim, size)
                if size == desired_size:
                    return Point(bot.x, top.y)

        raise Exception(f"Best found was {best}, worst was {minim}")

    def check_square(self, p):
        vertexes = [
            p,
            p + Point(99, 0),
            p + Point(0, 99)
        ]
        return all([self.get_info(x) == Laser.LASER for x in vertexes])


def solve(tape):
    laser = Laser(tape)
    print('Estimating borders...')
    laser.find_borders(50)
    laser.aprox()
    print(laser.top_theta, laser.bot_theta)
    print('Borders estimated')

    search_point = laser.get_point_where_gap_is(141)

    print('Searching for points on border...')
    laser.find_borders(200, start_point=search_point)
    print('Points found')

    print('Checkoing points...')
    result = laser.find_square(99)
    print('Points checked')

    # above gave me Point(1848, 2006)

    # not_working_point = Point(1848, 2006)
    # print(laser.check_square(not_working_point))
    # print(laser.check_square(not_working_point + Point(0, -1)))
    # print(laser.check_square(not_working_point + Point(-1, 0)))
    # print(laser.check_square(not_working_point + Point(-1, -1)))

    return result


tape = "109,424,203,1,21102,11,1,0,1106,0,282,21101,18,0,0,1106,0,259,2101,0,1,221,203,1,21102,31,1,0,1106,0,282,21102,1,38,0,1105,1,259,20102,1,23,2,22101,0,1,3,21101,0,1,1,21101,0,57,0,1106,0,303,1202,1,1,222,21001,221,0,3,20102,1,221,2,21102,259,1,1,21101,80,0,0,1105,1,225,21102,1,149,2,21101,0,91,0,1105,1,303,1202,1,1,223,21002,222,1,4,21102,259,1,3,21102,225,1,2,21102,225,1,1,21101,118,0,0,1105,1,225,20102,1,222,3,21101,0,127,2,21102,133,1,0,1105,1,303,21202,1,-1,1,22001,223,1,1,21102,1,148,0,1106,0,259,1201,1,0,223,21001,221,0,4,21002,222,1,3,21102,14,1,2,1001,132,-2,224,1002,224,2,224,1001,224,3,224,1002,132,-1,132,1,224,132,224,21001,224,1,1,21101,195,0,0,106,0,108,20207,1,223,2,20102,1,23,1,21101,0,-1,3,21102,214,1,0,1106,0,303,22101,1,1,1,204,1,99,0,0,0,0,109,5,1202,-4,1,249,22102,1,-3,1,21201,-2,0,2,21201,-1,0,3,21102,1,250,0,1105,1,225,22102,1,1,-4,109,-5,2106,0,0,109,3,22107,0,-2,-1,21202,-1,2,-1,21201,-1,-1,-1,22202,-1,-2,-2,109,-3,2105,1,0,109,3,21207,-2,0,-1,1206,-1,294,104,0,99,21202,-2,1,-2,109,-3,2106,0,0,109,5,22207,-3,-4,-1,1206,-1,346,22201,-4,-3,-4,21202,-3,-1,-1,22201,-4,-1,2,21202,2,-1,-1,22201,-4,-1,1,22101,0,-2,3,21101,343,0,0,1106,0,303,1106,0,415,22207,-2,-3,-1,1206,-1,387,22201,-3,-2,-3,21202,-2,-1,-1,22201,-3,-1,3,21202,3,-1,-1,22201,-3,-1,2,22101,0,-4,1,21102,1,384,0,1106,0,303,1105,1,415,21202,-4,-1,-4,22201,-4,-3,-4,22202,-3,-2,-2,22202,-2,-4,-4,22202,-3,-2,-3,21202,-4,-1,-2,22201,-3,-2,1,22102,1,1,-4,109,-5,2106,0,0"

res = solve(tape)

print(res)
