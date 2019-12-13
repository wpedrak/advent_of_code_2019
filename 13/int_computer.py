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
