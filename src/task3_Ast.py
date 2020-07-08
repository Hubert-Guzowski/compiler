from __future__ import print_function


class Node(object):

    def __init__(self):
        self.line = 0
        self.column = 0

    def accept(self, visitor):
        return visitor.visit(self)


class Instructions(Node):
    def __init__(self, instruction):
        self.instructions = [instruction]

    def append(self, instruction):
        self.instructions.append(instruction)


class Instruction(Node):
    def __init__(self, code=None):
        self.code = code


class If(Node):
    def __init__(self, condition, instruction):
        self.condition = condition
        self.instruction = instruction


class IfElse(Node):
    def __init__(self, condition, if_instruction, else_instruction):
        self.condition = condition
        self.if_instruction = if_instruction
        self.else_instruction = else_instruction


class For(Node):
    def __init__(self, var_id, left, right, instruction):
        self.id = var_id
        self.left = left
        self.right = right
        self.instruction = instruction


class While(Node):
    def __init__(self, condition, instruction):
        self.condition = condition
        self.instruction = instruction


class Break(Node):
    def __init__(self):
        pass


class Continue(Node):
    def __init__(self):
        pass


class Return(Node):
    def __init__(self, expression=None):
        self.expression = expression


class Print(Node):
    def __init__(self, parameters):
        self.parameters = parameters


class AssignDirect(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class AssignOperation(Node):
    def __init__(self, left, op, right):
        self.op = op
        self.left = left
        self.right = right


class Condition(Node):
    def __init__(self, left, relation, right):
        self.left = left
        self.relation = relation
        self.right = right


class Expression(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class ExpressionUminus(Node):
    def __init__(self, expression):
        self.expression = expression


class Transpose(Node):
    def __init__(self, expression):
        self.expression = expression


class Matrix(Node):
    def __init__(self, rows):
        self.rows = rows


class MatrixRows(Node):
    def __init__(self, row):
        self.rows = [row]

    def append(self, row):
        self.rows.append(row)


class Vector(Node):
    def __init__(self, parameters):
        self.parameters = parameters


class MatrixFunction(Node):
    def __init__(self, operator, parameters):
        self.operator = operator
        self.parameters = parameters


class Eye(MatrixFunction):
    pass


class Zeros(MatrixFunction):
    pass


class Ones(MatrixFunction):
    pass


class Parameters(Node):
    def __init__(self, parameter):
        self.parameters = [parameter]

    def append(self, parameter):
        self.parameters.append(parameter)


class Reference(Node):
    def __init__(self, variable, parameters):
        self.variable = variable
        self.parameters = parameters


class String(Node):
    def __init__(self, value):
        self.value = value


class Number(Node):
    def __init__(self, value):
        self.value = value


class IntNum(Number):
    pass


class FloatNum(Number):
    pass


class ID(Node):
    def __init__(self, name):
        self.name = name


class Error(Node):
    def __init__(self):
        pass
