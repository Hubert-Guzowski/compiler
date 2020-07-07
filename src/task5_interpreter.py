from task3_Ast import *
from task4_SymbolTable import *
from task5_memory import *
from task5_exceptions import *
from task5_visit import *
import sys
import operator
import numpy as np

sys.setrecursionlimit(10000)


class Interpreter(object):
    def __init__(self):
        self.memory_stack = MemoryStack()

        self.operators = dict()
        self.operators['*'] = operator.mul
        self.operators['/'] = operator.truediv
        self.operators['+'] = operator.add
        self.operators['-'] = operator.sub
        self.operators['.*'] = operator.mul
        self.operators['./'] = operator.truediv
        self.operators['.+'] = operator.add
        self.operators['.-'] = operator.sub
        self.operators['>'] = operator.gt
        self.operators['<'] = operator.lt
        self.operators['>='] = operator.ge
        self.operators['<='] = operator.le
        self.operators['=='] = operator.eq
        self.operators['!='] = operator.ne
        self.operators['+='] = operator.add
        self.operators['-='] = operator.sub
        self.operators['/='] = operator.truediv
        self.operators['*='] = operator.mul

    @on('node')
    def visit(self, node):
        pass

    @when(Instructions)
    def visit(self, node):
        try:
            for instruction in node.instructions:
                instruction.accept(self)
        except ReturnValueException as e:
            if e.value:
                print("\nRETURN: ")
                print(e.value)

    @when(If)
    def visit(self, node):
        if node.condition.accept(self):
            node.instruction.accept(self)

    @when(IfElse)
    def visit(self, node):
        if node.condition.accept(self):
            node.if_instruction.accept(self)
        else:
            node.else_instruction.accept(self)

    @when(For)
    def visit(self, node):
        self.memory_stack.push(Memory("For"))

        left = node.left.accept(self)
        right = node.right.accept(self)

        if not self.memory_stack.set(node.id.name, left):
            self.memory_stack.insert(node.id.name, left)

        while self.memory_stack.get(node.id.name) < right:
            try:
                node.instruction.accept(self)

                self.memory_stack.set(node.id.name, self.memory_stack.get(node.id.name) + 1)  # i+=1
            except ReturnValueException:
                return
            except ContinueException:
                self.memory_stack.set(node.id.name, self.memory_stack.get(node.id.name) + 1)  # i+=1
                continue
            except BreakException:
                break

        self.memory_stack.pop()

    @when(While)
    def visit(self, node):
        while node.condition.accept(self):
            try:
                self.memory_stack.push(Memory("While"))
                node.instruction.accept(self)
            except BreakException:
                break
            except ContinueException:
                continue
            except ReturnValueException:
                return
            finally:
                self.memory_stack.pop()

    @when(Break)
    def visit(self, node):
        raise BreakException

    @when(Continue)
    def visit(self, node):
        raise ContinueException

    @when(Return)
    def visit(self, node):
        raise ReturnValueException

    @when(Print)
    def visit(self, node):
        print_expressions = node.parameters.accept(self)
        for expression in print_expressions:
            print(expression, end="")
        print()

    @when(AssignDirect)
    def visit(self, node):
        pass

    @when(AssignOperation)
    def visit(self, node):
        pass

    @when(Condition)
    def visit(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)

        if node.relation in ('!=', '==') and isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
            return np.array_equal(left, right)

        return self.operators[node.oper](left, right)

    @when(Expression)
    def visit(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.op == '*' and isinstance(left, np.ndarray) and isinstance(right, np.ndarray):
            return np.matmul(left, right)
        return self.operators[node.op](left, right)

    @when(ExpressionUminus)
    def visit(self, node):
        return (-1) * node.expression.accept(self)

    @when(Transpose)
    def visit(self, node):
        matrix = node.expression.accept(self)
        return np.transpose(matrix)

    @when(MatrixRows)
    def visit(self, node):
        rows = []
        for row in node.rows:
            rows.append(row.accept(self))
        matrix = np.vstack(rows)
        return matrix

    @when(Vector)
    def visit(self, node):
        vector = []
        for param in node.parameters:
            vector.append(param.accept(self))

        return np.array(vector)

    # eye itp.
    # @when(MatrixFunction)
    # def visit(self, node):
    #     pass

    @when(MatrixFunction)
    def visit(self, node):
        pass

    @when(Reference)
    def visit(self, node):
        return node.parameters.accept(self)

    @when(Parameters)
    def visit(self, node):
        dims = []
        for param in node.parameters:
            dims.append(param.accept(self))
        return dims

    @when(String)
    def visit(self, node):
        return node.value[1:-1]

    @when(Number)
    def visit(self, node):
        return node.value

    @when(ID)
    def visit(self, node):
        return self.memory_stack.get(node.name)
