import itertools
from collections import deque


class Argument:
    POSITION = 'POSITION'
    IMMEDIATE = 'IMMEDIATE'

    modes = {
        '0': POSITION,
        '1': IMMEDIATE
    }

    def __init__(self, value, mode):
        self.value = value
        self.mode = Argument.modes[mode]

    def get_address(self):
        if self.mode != Argument.POSITION:
            raise Exception("get_address not on POSITION")
        return self.value

    def get_value(self, tape):
        if self.mode == Argument.POSITION:
            # print("return position", tape[self.value])
            return tape[self.value]
        elif self.mode == Argument.IMMEDIATE:
            # print("return immediate", self.value)
            return self.value

        raise Exception("Argument.get_value")


class Operation:
    num_of_args = None

    def __init__(self, arg_description, args):
        description = str(''.join(reversed(arg_description))) + "0" * \
            (len(args)-len(arg_description))

        self.args = [Argument(*arg) for arg in zip(args, description)]

    def get_value(self, arg_idx, computer):
        arg = self.args[arg_idx]
        return arg.get_value(computer.tape)

    def get_address(self, arg_idx):
        arg = self.args[arg_idx]
        return arg.get_address()

    def shift_pointer(self, computer):
        computer.pointer += self.num_of_args + 1


class Add(Operation):
    opcode = 1
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = v1 + v2
        self.shift_pointer(computer)


class Mul(Operation):
    opcode = 2
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = v1 * v2
        self.shift_pointer(computer)


class In(Operation):
    opcode = 3
    num_of_args = 1

    def execute(self, computer):
        # print('--------------------------IN-----------------')
        res_address = self.get_address(0)
        should_pause = not computer.can_read()
        # print("can" + ("'t" if should_pause else "") + " read")
        if should_pause:
            computer.pause()
            return
        # print("In.execute:", should_pause)
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
        res_address = self.get_address(2)
        computer.tape[res_address] = int(v1 < v2)
        self.shift_pointer(computer)


class Equals(Operation):
    opcode = 8
    num_of_args = 3

    def execute(self, computer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = int(v1 == v2)
        self.shift_pointer(computer)


class Halt(Operation):
    opcode = 99
    num_of_args = 0

    def execute(self, computer):
        computer.halt()


class OperationProvider:
    operations = [Add, Mul, In, Out, Halt,
                  JumpIfTrue, JumpIfFalse, LessThan, Equals]

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
        # print("queue.is_empty:", True if self.q else False, self.q)
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

    def load(self, tape):
        self.tape = [int(x) for x in tape.split(',')]

    def read(self):
        if self.inq.is_empty():
            raise Exception('Try to reead from empty in-query')
        # print('reading:', self.inq.is_empty())
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
        # print("computer say it is " +  ("possible" if res else "impossible") + " to read from in-queue")
        return res

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


def check_setting(phase_setting, tape, v=False):
    queues = [Queue(name=idx) for idx in range(5)]

    for idx, inp in enumerate(phase_setting):
        queues[idx].put_message(inp)

    queues[0].put_message(0)  # first input

    computers = []
    for idx in range(5):
        computer = Computer(inq=queues[idx], outq=queues[(idx+1) % 5])
        computer.load(tape)
        computers.append(computer)

    running_computer_idx = 0

    # x = 0
    while not Computer.all_halted(computers):  # and x < 10:
        # x +=1
        # print("states", [x.state for x in computers])
        # print(queues)
        # print("computer idx:", running_computer_idx)
        computer = computers[running_computer_idx]
        if computer.is_halted():
            continue
        # print('running')
        computer.run(v=v)
        # print('running fin')
        running_computer_idx = (running_computer_idx + 1) % 5

    # print(queues)

    return queues[0].get_message()


def solve(tape):
    results = []

    for phase_setting in list(itertools.permutations(list(range(5, 10)))):
        results.append(check_setting(phase_setting, tape))

    return max(results)


tape = "3,8,1001,8,10,8,105,1,0,0,21,34,59,68,89,102,183,264,345,426,99999,3,9,102,5,9,9,1001,9,5,9,4,9,99,3,9,101,3,9,9,1002,9,5,9,101,5,9,9,1002,9,3,9,1001,9,5,9,4,9,99,3,9,101,5,9,9,4,9,99,3,9,102,4,9,9,101,3,9,9,102,5,9,9,101,4,9,9,4,9,99,3,9,1002,9,5,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,99"

if True:
    t1 = solve("3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5") == 139629729
    print(t1)
    t2 = solve("3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10") == 18216
    print(t2)
    tests = [t1, t2]
    assert(all([tests]))

print(solve(tape))
