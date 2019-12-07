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

    def pointer_shift(self, pointer):
        return pointer + self.num_of_args + 1


class Add(Operation):
    opcode = 1
    num_of_args = 3

    def execute(self, computer, pointer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = v1 + v2
        return False, self.pointer_shift(pointer)


class Mul(Operation):
    opcode = 2
    num_of_args = 3

    def execute(self, computer, pointer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = v1 * v2
        return False, self.pointer_shift(pointer)


class In(Operation):
    opcode = 3
    num_of_args = 1

    def execute(self, computer, pointer):
        res_address = self.get_address(0)
        computer.tape[res_address] = computer.read()
        return False, self.pointer_shift(pointer)


class Out(Operation):
    opcode = 4
    num_of_args = 1

    def execute(self, computer, pointer):
        v = self.get_value(0, computer)
        computer.write(v)
        return False, self.pointer_shift(pointer)


class JumpIfTrue(Operation):
    opcode = 5
    num_of_args = 2

    def execute(self, computer, pointer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        ptr = v2 if v1 != 0 else self.pointer_shift(pointer)
        return False, ptr


class JumpIfFalse(Operation):
    opcode = 6
    num_of_args = 2

    def execute(self, computer, pointer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        ptr = v2 if v1 == 0 else self.pointer_shift(pointer)
        return False, ptr


class LessThan(Operation):
    opcode = 7
    num_of_args = 3

    def execute(self, computer, pointer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = int(v1 < v2)
        return False, self.pointer_shift(pointer)


class Equals(Operation):
    opcode = 8
    num_of_args = 3

    def execute(self, computer, pointer):
        v1 = self.get_value(0, computer)
        v2 = self.get_value(1, computer)
        res_address = self.get_address(2)
        computer.tape[res_address] = int(v1 == v2)
        return False, self.pointer_shift(pointer)


class Halt(Operation):
    opcode = 99
    num_of_args = 0

    def execute(self, computer, pointer):
        return True, pointer


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

class Computer:
    def __init__(self, inq=None, outq=None):
        self.inq = inq
        self.outq = outq

    def load(self, tape):
        self.tape = [int(x) for x in tape.split(',')]

    def read(self):
        return self.inq.get_message()

    def write(self, out):
        self.outq.put_message(out)

    def is_halted(self):
        return self.halted

    def run(self, v=False):
        pointer = 0
        halt = False
        while(not halt):
            if v:
                print("pointer:", pointer)
                print(self.tape[:50])
            operation = OperationProvider.get_next(pointer, self.tape)
            halt, pointer = operation.execute(self, pointer)
        self.halted = True


def check_setting(phase_setting, tape, v=False):
    queues = [Queue(name=idx) for idx in range(5)]

    for idx, inp in enumerate(phase_setting):
        queues[idx].put_message(inp)

    queues[0].put_message(0) # first input

    computers = []
    for idx in range(5):
        computer = Computer(inq=queues[idx], outq=queues[idx+1 % 5])
        computer.load(tape)
        computers.append(computer)
        
        
    for phase, computer in zip(phase_setting, computers):
        computer.add_input(phase)
        computer.add_input(current_result)
        computer.run(v=True)
        current_result = computer.get_output()
        if v:
            print("-----------result of computer:", current_result)

    return None

def solve(tape):
    results = []

    for phase_setting in list(itertools.permutations(list(range(6, 10)))):
        results.append(check_setting(phase_setting, tape))

    return max(results)


# tape = "3,8,1001,8,10,8,105,1,0,0,21,34,59,68,89,102,183,264,345,426,99999,3,9,102,5,9,9,1001,9,5,9,4,9,99,3,9,101,3,9,9,1002,9,5,9,101,5,9,9,1002,9,3,9,1001,9,5,9,4,9,99,3,9,101,5,9,9,4,9,99,3,9,102,4,9,9,101,3,9,9,102,5,9,9,101,4,9,9,4,9,99,3,9,1002,9,5,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,99"

# if True:
#     t1 = solve("3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5") == 139629729
#     print(t1)
#     t2 = solve("3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10") == 18216
#     print(t2)
#     tests = [t1, t2]
#     assert(all([tests]))

# print(solve(tape))