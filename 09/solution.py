from collections import deque


class Argument:
    POSITION = 'POSITION'
    IMMEDIATE = 'IMMEDIATE'
    RELATIVE = 'RELATIVE'

    modes = {
        '0': POSITION,
        '1': IMMEDIATE,
        '2': RELATIVE
    }

    def __init__(self, value, mode):
        self.value = value
        self.mode = Argument.modes[mode]

    def get_address(self, computer):
        if self.mode == Argument.POSITION:
            return self.value
        elif self.mode == Argument.RELATIVE:
            return self.value + computer.relative_base

        raise Exception("get_address with mode", self.mode)

    def get_value(self, computer):
        tape = computer.tape

        if self.mode == Argument.POSITION:
            # print("return position", tape[self.value])
            return tape[self.value]
        elif self.mode == Argument.IMMEDIATE:
            # print("return immediate", self.value)
            return self.value
        elif self.mode == Argument.RELATIVE:
            # print("return relative", self.value)
            return tape[self.value + computer.relative_base]

        raise Exception("Argument.get_value")


class Operation:
    num_of_args = None

    def __init__(self, arg_description, args):
        description = str(''.join(reversed(arg_description))) + "0" * \
            (len(args)-len(arg_description))

        self.args = [Argument(*arg) for arg in zip(args, description)]

    def get_value(self, arg_idx, computer):
        arg = self.args[arg_idx]
        return arg.get_value(computer)

    def get_address(self, arg_idx, computer):
        arg = self.args[arg_idx]
        return arg.get_address(computer)

    def shift_pointer(self, computer):
        computer.pointer += self.num_of_args + 1


class Add(Operation):
    opcode = 1
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2, computer)
        computer.tape[res_address] = v1 + v2
        self.shift_pointer(computer)


class Mul(Operation):
    opcode = 2
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2, computer)
        computer.tape[res_address] = v1 * v2
        self.shift_pointer(computer)


class In(Operation):
    opcode = 3
    num_of_args = 1

    def execute(self, computer):
        res_address = self.get_address(0, computer)
        should_pause = not computer.can_read()
        if should_pause:
            computer.pause()
            return
        computer.tape[res_address] = computer.read()
        self.shift_pointer(computer)


class Out(Operation):
    opcode = 4
    num_of_args = 1

    def execute(self, computer):
        v = self.get_value(0, computer)
        computer.write(v)
        self.shift_pointer(computer)


class JumpIfTrue(Operation):
    opcode = 5
    num_of_args = 2

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        self.shift_pointer(computer)
        if v1 != 0:
            computer.pointer = v2


class JumpIfFalse(Operation):
    opcode = 6
    num_of_args = 2

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        self.shift_pointer(computer)
        if v1 == 0:
            computer.pointer = v2


class LessThan(Operation):
    opcode = 7
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2, computer)
        computer.tape[res_address] = int(v1 < v2)
        self.shift_pointer(computer)


class Equals(Operation):
    opcode = 8
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2, computer)
        computer.tape[res_address] = int(v1 == v2)
        self.shift_pointer(computer)


class ChangeRelativeBase(Operation):
    opcode = 9
    num_of_args = 1

    def execute(self, computer):
        v = self.get_value(0, computer)
        self.shift_pointer(computer)
        computer.add_to_relative_base(v)


class Halt(Operation):
    opcode = 99
    num_of_args = 0

    def execute(self, computer):
        computer.halt()


class OperationProvider:
    operations = [Add, Mul, In, Out, Halt, JumpIfTrue, JumpIfFalse, LessThan, Equals, ChangeRelativeBase]

    @staticmethod
    def operation_class_by_opcode(opcode):
        for op in OperationProvider.operations:
            if op.opcode == opcode:
                return op

        raise Exception("unknown opcode:", opcode)

    @staticmethod
    def get_next(pointer, tape):
        description = str(tape[pointer])
        opcode = int(description[-2:])
        args_description = description[:-2]
        operation_class = OperationProvider.operation_class_by_opcode(opcode)

        operation = operation_class(
            args_description,
            tape[pointer+1: pointer+1+operation_class.num_of_args]
        )

        return operation


class Queue:
    def __init__(self, name=None):
        self.q = deque()
        self.name = name

    def get_message(self):
        return self.q.popleft()

    def put_message(self, message):
        self.q.append(message)

    def is_empty(self):
        return False if self.q else True

    def __str__(self):
        return str(self.name) + " " + str(list(self.q))

    def __repr__(self):
        return str(self)


class Computer:
    PAUSED = "PAUSED"
    RUNNING = "RUNNING"
    HALTED = "HALTED"

    def __init__(self, inq=None, outq=None):
        self.inq = inq
        self.outq = outq
        self.state = Computer.PAUSED
        self.pointer = 0
        self.relative_base = 0

    def load(self, tape):
        self.tape = [int(x) for x in tape.split(',')]
        self.tape += [0] * int(1e6)

    def read(self):
        if self.inq.is_empty():
            raise Exception('Try to reead from empty in-query')
        return self.inq.get_message()

    def write(self, out):
        self.outq.put_message(out)

    def is_halted(self):
        return self.state == Computer.HALTED

    def halt(self):
        self.state = Computer.HALTED

    def pause(self):
        self.state = Computer.PAUSED

    def can_read(self):
        res = not self.inq.is_empty()
        return res

    def add_to_relative_base(self, v):
        self.relative_base += v

    def run(self, v=False):
        self.state = Computer.RUNNING

        while self.state == Computer.RUNNING:
            if v:
                print("pointer:", self.pointer)
                print(self.tape[:50])
            operation = OperationProvider.get_next(self.pointer, self.tape)
            operation.execute(self)

    @staticmethod
    def all_halted(computers):
        return all([c.state == Computer.HALTED for c in computers])


# def check_setting(phase_setting, tape, v=False):
#     queues = [Queue(name=idx) for idx in range(5)]

#     for idx, inp in enumerate(phase_setting):
#         queues[idx].put_message(inp)

#     queues[0].put_message(0)  # first input

#     computers = []
#     for idx in range(5):
#         computer = Computer(inq=queues[idx], outq=queues[(idx+1) % 5])
#         computer.load(tape)
#         computers.append(computer)

#     running_computer_idx = 0

#     while not Computer.all_halted(computers):  # and x < 10:
#         computer = computers[running_computer_idx]
#         if computer.is_halted():
#             continue
#         computer.run(v=v)
#         running_computer_idx = (running_computer_idx + 1) % 5

#     return queues[0].get_message()


def solve(tape):
    in_queue = Queue(name="in")
    out_queue = Queue(name="out")

    in_queue.put_message(1)

    computer = Computer(inq=in_queue, outq=out_queue)
    computer.load(tape)
    computer.run()

    print(out_queue)
    return out_queue.get_message()


tape = "1102,34463338,34463338,63,1007,63,34463338,63,1005,63,53,1102,1,3,1000,109,988,209,12,9,1000,209,6,209,3,203,0,1008,1000,1,63,1005,63,65,1008,1000,2,63,1005,63,904,1008,1000,0,63,1005,63,58,4,25,104,0,99,4,0,104,0,99,4,17,104,0,99,0,0,1102,26,1,1005,1101,0,24,1019,1102,1,32,1007,1101,0,704,1027,1102,0,1,1020,1101,0,348,1029,1102,28,1,1002,1101,34,0,1016,1102,29,1,1008,1102,1,30,1013,1102,25,1,1012,1101,0,33,1009,1102,1,37,1001,1101,31,0,1017,1101,245,0,1022,1102,39,1,1000,1101,27,0,1011,1102,770,1,1025,1101,0,22,1015,1102,1,1,1021,1101,711,0,1026,1101,20,0,1004,1101,0,23,1018,1101,242,0,1023,1102,21,1,1003,1101,38,0,1010,1101,0,35,1014,1101,0,36,1006,1101,0,357,1028,1102,1,775,1024,109,-3,2102,1,9,63,1008,63,36,63,1005,63,203,4,187,1105,1,207,1001,64,1,64,1002,64,2,64,109,8,21101,40,0,5,1008,1010,41,63,1005,63,227,1106,0,233,4,213,1001,64,1,64,1002,64,2,64,109,16,2105,1,2,1105,1,251,4,239,1001,64,1,64,1002,64,2,64,109,1,21107,41,40,-4,1005,1018,271,1001,64,1,64,1105,1,273,4,257,1002,64,2,64,109,-18,1207,0,21,63,1005,63,295,4,279,1001,64,1,64,1105,1,295,1002,64,2,64,109,-3,1207,0,36,63,1005,63,311,1105,1,317,4,301,1001,64,1,64,1002,64,2,64,109,6,2108,20,-3,63,1005,63,339,4,323,1001,64,1,64,1106,0,339,1002,64,2,64,109,28,2106,0,-7,4,345,1001,64,1,64,1106,0,357,1002,64,2,64,109,-18,1206,4,373,1001,64,1,64,1105,1,375,4,363,1002,64,2,64,109,-6,2107,31,-4,63,1005,63,397,4,381,1001,64,1,64,1105,1,397,1002,64,2,64,109,1,21102,42,1,-1,1008,1011,39,63,1005,63,421,1001,64,1,64,1106,0,423,4,403,1002,64,2,64,109,-2,2108,26,-2,63,1005,63,439,1106,0,445,4,429,1001,64,1,64,1002,64,2,64,109,6,21102,43,1,-5,1008,1011,43,63,1005,63,467,4,451,1105,1,471,1001,64,1,64,1002,64,2,64,109,6,21101,44,0,-3,1008,1019,44,63,1005,63,493,4,477,1105,1,497,1001,64,1,64,1002,64,2,64,109,-9,1206,7,511,4,503,1105,1,515,1001,64,1,64,1002,64,2,64,109,14,1205,-7,531,1001,64,1,64,1106,0,533,4,521,1002,64,2,64,109,-27,1201,0,0,63,1008,63,39,63,1005,63,555,4,539,1105,1,559,1001,64,1,64,1002,64,2,64,109,10,2101,0,-5,63,1008,63,24,63,1005,63,583,1001,64,1,64,1105,1,585,4,565,1002,64,2,64,109,-11,2107,21,5,63,1005,63,601,1105,1,607,4,591,1001,64,1,64,1002,64,2,64,109,10,1208,0,36,63,1005,63,627,1001,64,1,64,1106,0,629,4,613,1002,64,2,64,109,15,21108,45,45,-9,1005,1015,647,4,635,1105,1,651,1001,64,1,64,1002,64,2,64,109,-19,2101,0,-4,63,1008,63,37,63,1005,63,677,4,657,1001,64,1,64,1106,0,677,1002,64,2,64,109,22,1205,-6,695,4,683,1001,64,1,64,1105,1,695,1002,64,2,64,109,-10,2106,0,10,1001,64,1,64,1105,1,713,4,701,1002,64,2,64,109,-9,1201,-8,0,63,1008,63,36,63,1005,63,733,1105,1,739,4,719,1001,64,1,64,1002,64,2,64,109,7,21107,46,47,0,1005,1015,757,4,745,1106,0,761,1001,64,1,64,1002,64,2,64,109,14,2105,1,-5,4,767,1105,1,779,1001,64,1,64,1002,64,2,64,109,-34,2102,1,6,63,1008,63,39,63,1005,63,799,1105,1,805,4,785,1001,64,1,64,1002,64,2,64,109,25,21108,47,49,-4,1005,1016,825,1001,64,1,64,1106,0,827,4,811,1002,64,2,64,109,-6,1208,-8,36,63,1005,63,845,4,833,1106,0,849,1001,64,1,64,1002,64,2,64,109,-10,1202,2,1,63,1008,63,36,63,1005,63,875,4,855,1001,64,1,64,1105,1,875,1002,64,2,64,109,-5,1202,10,1,63,1008,63,30,63,1005,63,895,1106,0,901,4,881,1001,64,1,64,4,64,99,21101,27,0,1,21101,0,915,0,1105,1,922,21201,1,65916,1,204,1,99,109,3,1207,-2,3,63,1005,63,964,21201,-2,-1,1,21101,942,0,0,1105,1,922,21201,1,0,-1,21201,-2,-3,1,21102,1,957,0,1105,1,922,22201,1,-1,-2,1106,0,968,22102,1,-2,-2,109,-3,2105,1,0"

if True:
    t1 = 1e15 <= solve("1102,34915192,34915192,7,4,7,99,0") < 1e16
    print(t1)
    t2 = solve("104,1125899906842624,99") == 1125899906842624
    print(t2)
    t3 = solve("109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99")
    print(t3)
    tests = [t1, t2]
    assert(all([tests]))

print(solve(tape))
