class Symbol(object):
    pass


class VariableSymbol(Symbol):
    def __init__(self, name, type, value=None):
        self.name = name
        self.type = type
        self.value = value


class MatrixSymbol(Symbol):
    def __init__(self, name, type, value=None, dim1=0, dim2=0):
        self.name = name
        self.type = type
        self.value = value
        self.dim1 = dim1
        self.dim2 = dim2


class SymbolTable(object):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.scope = 0
        self.nesting = 0
        self.symbols = {}

    def put(self, name, symbol):
        self.symbols[name] = symbol

    def get(self, name):
        return self.symbols[name]

    def getParentScope(self):
        return self.parent

    def pushScope(self, name):
        self.scope += 1

    def popScope(self):
        self.scope -= 1

    def pushNesting(self):
        self.nesting += 1

    def popNesting(self):
        self.nesting -= 1
