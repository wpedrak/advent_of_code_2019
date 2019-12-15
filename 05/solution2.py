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
    operations = [Add, Mul, In, Out, Halt, JumpIfTrue, JumpIfFalse, LessThan, Equals]

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


tape = "3,225,1,225,6,6,1100,1,238,225,104,0,1,191,196,224,1001,224,-85,224,4,224,1002,223,8,223,1001,224,4,224,1,223,224,223,1101,45,50,225,1102,61,82,225,101,44,39,224,101,-105,224,224,4,224,102,8,223,223,101,5,224,224,1,224,223,223,102,14,187,224,101,-784,224,224,4,224,102,8,223,223,101,7,224,224,1,224,223,223,1001,184,31,224,1001,224,-118,224,4,224,102,8,223,223,1001,224,2,224,1,223,224,223,1102,91,18,225,2,35,110,224,101,-810,224,224,4,224,102,8,223,223,101,3,224,224,1,223,224,223,1101,76,71,224,1001,224,-147,224,4,224,102,8,223,223,101,2,224,224,1,224,223,223,1101,7,16,225,1102,71,76,224,101,-5396,224,224,4,224,1002,223,8,223,101,5,224,224,1,224,223,223,1101,72,87,225,1101,56,77,225,1102,70,31,225,1102,29,15,225,1002,158,14,224,1001,224,-224,224,4,224,102,8,223,223,101,1,224,224,1,223,224,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,1007,226,226,224,1002,223,2,223,1006,224,329,1001,223,1,223,8,226,677,224,1002,223,2,223,1005,224,344,1001,223,1,223,107,226,677,224,1002,223,2,223,1006,224,359,1001,223,1,223,8,677,677,224,1002,223,2,223,1005,224,374,1001,223,1,223,1108,226,226,224,1002,223,2,223,1005,224,389,1001,223,1,223,7,677,226,224,1002,223,2,223,1005,224,404,101,1,223,223,7,226,226,224,102,2,223,223,1006,224,419,1001,223,1,223,1108,226,677,224,102,2,223,223,1005,224,434,1001,223,1,223,1107,226,226,224,1002,223,2,223,1006,224,449,1001,223,1,223,1007,677,677,224,102,2,223,223,1006,224,464,1001,223,1,223,107,226,226,224,1002,223,2,223,1005,224,479,101,1,223,223,1107,677,226,224,1002,223,2,223,1005,224,494,1001,223,1,223,1008,677,677,224,102,2,223,223,1005,224,509,101,1,223,223,107,677,677,224,102,2,223,223,1005,224,524,1001,223,1,223,1108,677,226,224,1002,223,2,223,1005,224,539,1001,223,1,223,7,226,677,224,102,2,223,223,1006,224,554,1001,223,1,223,8,677,226,224,1002,223,2,223,1006,224,569,101,1,223,223,108,226,226,224,1002,223,2,223,1006,224,584,1001,223,1,223,1107,226,677,224,1002,223,2,223,1006,224,599,101,1,223,223,1008,226,226,224,102,2,223,223,1005,224,614,1001,223,1,223,1007,226,677,224,1002,223,2,223,1006,224,629,1001,223,1,223,108,677,226,224,102,2,223,223,1005,224,644,101,1,223,223,1008,226,677,224,1002,223,2,223,1005,224,659,101,1,223,223,108,677,677,224,1002,223,2,223,1006,224,674,1001,223,1,223,4,223,99,226"
# tape = "3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99"

computer = Computer()
computer.load(tape)
computer.add_input(5)
computer.run()
res = computer.output()
print(res)
