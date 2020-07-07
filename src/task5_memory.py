class Memory:

    def __init__(self, name):
        self.name = name
        self.symbols = dict()

    def has_key(self, name):
        return self.symbols.__contains__(name)

    def get(self, name):
        if name in self.symbols:
            return self.symbols[name]
        return None

    def put(self, name, value):  # puts into memory current value of variable <name>
        self.symbols[name] = value


class MemoryStack:
                                                                             
    def __init__(self):
        self.stack = []
        self.stack.append(Memory("global"))

    def get(self, name):  # gets from memory stack current value of variable <name>
        for memory in reversed(self.stack):
            if name in memory:
                return memory.get(name)
        raise KeyError(name)

    def insert(self, name, value):  # inserts into memory stack variable <name> with value <value>
        self.stack[-1].put(name, value)

    def set(self, name, value):  # sets variable <name> to value <value>
        for memory in reversed(self.stack):
            if name in memory:
                memory.put(name, value)
                return True
        raise False

    def push(self, memory):  # pushes memory <memory> onto the stack
        if not isinstance(memory, Memory):
            raise ValueError("Argument is not instance of Memory")
        self.stack.append(memory)

    def pop(self):  # pops the top memory from the stack
        return self.stack.pop()
