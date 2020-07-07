from __future__ import print_function
import task3_Ast as ast


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class AstPrinter:

    @addToClass(ast.Node)
    def printTree(self, indent=0):
        raise Exception("define printTree for class " + self.__class__.__name__)

    @addToClass(ast.Instructions)
    def printTree(self, indent=0):
        for instruction in self.instructions:
            instruction.printTree(indent)

    @addToClass(ast.Instruction)
    def printTree(self, indent=0):
        if self.code:
            self.code.printTree(indent)

    @addToClass(ast.If)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("IF")
        self.condition.printTree(indent + 1)
        for i in range(indent):
            print("|  ", end='')
        print("THEN")
        self.instruction.printTree(indent + 1)

    @addToClass(ast.IfElse)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("IF")
        self.condition.printTree(indent + 1)
        for i in range(indent):
            print("|  ", end='')
        print("THEN")
        self.if_instruction.printTree(indent + 1)
        for i in range(indent):
            print("|  ", end='')
        print("ELSE")
        self.else_instruction.printTree(indent + 1)

    @addToClass(ast.For)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("FOR")
        self.id.printTree(indent + 1)
        for i in range(indent + 1):
            print("|  ", end='')
        print("RANGE")
        self.left.printTree(indent + 2)
        self.right.printTree(indent + 2)
        self.instruction.printTree(indent + 1)


    @addToClass(ast.While)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("WHILE")
        self.condition.printTree(indent + 1)
        self.instruction.printTree(indent + 1)

    @addToClass(ast.Break)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("BREAK")

    @addToClass(ast.Continue)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("CONTINUE")

    @addToClass(ast.Return)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("RETURN")
        if self.expression:
            self.expression.printTree(indent + 1)

    @addToClass(ast.Print)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("PRINT")
        self.parameters.printTree(indent + 1)

    @addToClass(ast.AssignDirect)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("=")
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(ast.AssignOperation)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.op)
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(ast.Condition)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.relation)
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(ast.Expression)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.op)
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(ast.ExpressionUminus)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("-")
        self.expression.printTree(indent + 1)

    @addToClass(ast.Transpose)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("TRANSPOSE")
        self.expression.printTree(indent + 1)

    @addToClass(ast.Matrix)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("VECTOR")
        self.rows.printTree(indent + 1)

    @addToClass(ast.MatrixRows)
    def printTree(self, indent=0):
        for row in self.rows:
            row.printTree(indent)

    @addToClass(ast.MatrixFunction)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.operator)
        self.parameters.printTree(indent + 1)

    @addToClass(ast.Vector)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("VECTOR")
        self.parameters.printTree(indent+1)

    @addToClass(ast.Parameters)
    def printTree(self, indent=0):
        for parameter in self.parameters:
            parameter.printTree(indent)

    @addToClass(ast.Reference)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print("REF")
        self.variable.printTree(indent + 1)
        self.parameters.printTree(indent + 1)

    @addToClass(ast.String)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.value)

    @addToClass(ast.Number)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.value)

    @addToClass(ast.ID)
    def printTree(self, indent=0):
        for i in range(indent):
            print("|  ", end='')
        print(self.name)

    @addToClass(ast.Error)
    def printTree(self, indent=0):
        pass
