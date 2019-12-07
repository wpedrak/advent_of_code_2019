import itertools


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
        computer.tape[res_address] = computer.get_input()
        return False, self.pointer_shift(pointer)


class Out(Operation):
    opcode = 4
    num_of_args = 1

    def execute(self, computer, pointer):
        v = self.get_value(0, computer)
        computer.add_output(v)
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


class Computer:
    def __init__(self):
        self.inp = []
        self.out = []

    def load(self, tape):
        self.tape = [int(x) for x in tape.split(',')]

    def add_input(self, inp):
        self.inp.append(inp)

    def get_input(self):
        return self.inp.pop(0)

    def add_output(self, out):
        self.out.append(out)

    def output(self):
        return self.out[:]

    def run(self):
        pointer = 0
        halt = False
        while(not halt):
            # print("pointer:", pointer)
            # print(self.tape[:50])
            operation = OperationProvider.get_next(pointer, self.tape)
            halt, pointer = operation.execute(self, pointer)


# tape = "3,8,1001,8,10,8,105,1,0,0,21,34,59,68,89,102,183,264,345,426,99999,3,9,102,5,9,9,1001,9,5,9,4,9,99,3,9,101,3,9,9,1002,9,5,9,101,5,9,9,1002,9,3,9,1001,9,5,9,4,9,99,3,9,101,5,9,9,4,9,99,3,9,102,4,9,9,101,3,9,9,102,5,9,9,101,4,9,9,4,9,99,3,9,1002,9,5,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,99"
tape = "3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0"

results = []

for phase_setting in list(itertools.product(range(0, 5), repeat=5)):
    current_result = 0
    for phase in phase_setting:
        computer = Computer()
        computer.load(tape)
        computer.add_input(phase)
        computer.add_input(current_result)
        computer.run()
        current_result = computer.output()[0]
    results.append(current_result)


print(results)

res = max(results)

print(res)
