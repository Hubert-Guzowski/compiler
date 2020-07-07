from task3_Ast import *
from task4_SymbolTable import *
from task4_OperationRules import OperationRules


class NodeVisitor(object):

    def __init__(self):
        self.error = False
        self.symbol_table = SymbolTable(None, 'Program')
        self.operation_rules = OperationRules()

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.__dict__.values():
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, Node):
                            self.visit(item)
                elif isinstance(child, Node):
                    self.visit(child)

    def handle_error(self, message):
        self.error = True
        print(message)


class TypeChecker(NodeVisitor):

    def visit_Instructions(self, node):
        for instruction in node.instructions:
            self.visit(instruction)

    def visit_If(self, node):
        self.symbol_table.pushScope('if')

        self.visit(node.condition)
        self.visit(node.instruction)

        self.symbol_table.popScope()

    def visit_IfElse(self, node):
        self.symbol_table.pushScope('if')
        self.visit(node.condition)
        self.visit(node.if_instruction)
        self.symbol_table.popScope()

        self.symbol_table.pushScope('else')
        self.visit(node.else_instruction)
        self.symbol_table.popScope()

    def visit_For(self, node):
        self.symbol_table.pushNesting()
        self.symbol_table.pushScope('for')

        self.visit(node.id)
        start_type = self.visit(node.left)
        end_type = self.visit(node.right)
        self.visit(node.instruction)

        self.symbol_table.popScope()
        self.symbol_table.popNesting()

        if start_type == 'unknown' or end_type == 'unknown':
            return 'unknown'
        elif start_type != 'int' or end_type != 'int':
            self.handle_error('Line {}: Range of unsupported types: {} and {}'.format(node.line, start_type, end_type))
            return 'unknown'
        return 'int'

    def visit_While(self, node):
        self.symbol_table.pushNesting()
        self.symbol_table.pushScope('while')

        self.visit(node.condition)
        self.visit(node.instruction)

        self.symbol_table.popScope()
        self.symbol_table.popNesting()

    def visit_Break(self, node):
        if self.symbol_table.nesting == 0:
            self.handle_error('Line {}: Break outside a scope'.format(node.line))

    def visit_Continue(self, node):
        if self.symbol_table.nesting == 0:
            self.handle_error('Line {}: Continue outside a scope'.format(node.line))

    def visit_Return(self, node):
        self.visit(node.expression)

    def visit_AssignDirect(self, node):
        if isinstance(node.left, Reference):
            self.visit(node.left)
            self.visit(node.right)

        elif isinstance(node.left, ID):
            right_type = self.visit(node.right)

            if right_type == 'unknown':
                return 'unknown'

            if right_type == 'matrix':
                matrix = node.right

                dim1 = dim2 = None
                if isinstance(matrix, MatrixFunction):
                    matrix_func_dims = []
                    for expr in matrix.parameters.parameters:
                        if isinstance(expr, ID):
                            if self.visit(expr) == 'unknown':
                                return 'unknown'

                            value = self.symbol_table.get(expr.name).val
                            matrix_func_dims.append(value)
                        else:
                            matrix_func_dims.append(expr.value)

                    if len(matrix.parameters.parameters) == 1:  # zeros(2) <=> zeros(2,2)
                        dim1 = matrix_func_dims[0]
                        dim2 = dim1
                    elif len(matrix.parameters.parameters) == 2:  # zeros(3,1), zeros(2,2)
                        dim1 = matrix_func_dims[0]
                        dim2 = matrix_func_dims[1]
                elif isinstance(matrix, Expression):  # it's a matrix expression
                    dim1, dim2 = self.get_matrix_dims_depending_on_instance(matrix.left)
                elif isinstance(matrix, Matrix):  # it's a Rows object
                    dim1, dim2 = self.get_matrix_dimensions(matrix)
                elif isinstance(matrix, ID):
                    dim1, dim2 = self.get_matrix_dimensions_for_id(matrix)

                # if right expr is an instance of Id, then we put its name to the symbol_table. Otherwise, we put there its
                # value
                symbol = MatrixSymbol(name=node.left.name, type=right_type, value=node.right, dim1=dim1, dim2=dim2)
            else:
                symbol = VariableSymbol(name=node.left.name, type=right_type, value=node.right)

            self.symbol_table.put(node.left.name, symbol)
            return right_type

    def visit_AssignOperation(self, node):
        if isinstance(node.left, Reference):
            self.visit(node.left)
            self.visit(node.right)
        elif isinstance(node.left, ID):
            left_type = self.visit(node.left)
            right_type = self.visit(node.right)

            if left_type == 'unknown' or right_type == 'unknown':
                return 'unknown'

            left = self.symbol_table.get(node.id.name)
            return_type = self.operation_rules.types[node.oper][left_type][right_type]

            if return_type == 'unknown':
                self.handle_error('Line {}: Unsupported operation between {} {}'.format(node.line, left.type, right_type))
                return 'unknown'

            if left_type == 'matrix' and right_type == 'matrix':
                right_dim1, right_dim2 = self.get_matrix_dims_depending_on_instance(node.expression)

                if node.oper == '*=':
                    if left.dim2 != right_dim1:
                        self.handle_error(
                            'Line {}: Matrices dimensions do not match in matrix multiplication'.format(node.line))
                        return 'unknown'
                    return return_type

                if left.dim1 != right_dim1 or left.dim2 != right_dim2:
                    self.handle_error('Line {}: Matrices dimensions do not match'.format(node.line))
                    return 'unknown'
            return return_type

    def visit_Condition(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == 'unknown' or right_type == 'unknown':
            return 'boolean'

        return_type = self.operation_rules.types[node.oper][left_type][right_type]
        if return_type == 'unknown':
            self.handle_error(
                'Line {}: Operation {} unsupported between types: {} and {}'.format(node.line, node.oper, left_type,
                                                                                    right_type))
        return 'boolean'

    def visit_Expression(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == 'unknown' or right_type == 'unknown':
            return 'unknown'

        if left_type == 'matrix' and right_type == 'matrix':
            left_dim1, left_dim2 = self.get_matrix_dims_depending_on_instance(node.left)
            right_dim1, right_dim2 = self.get_matrix_dims_depending_on_instance(node.right)

            if node.op == '*':
                if left_dim2 == right_dim1:
                    return 'matrix'
                else:
                    self.handle_error('Line {}: Unsupported operation "{}" between matrices of different dimensions: '
                                      '({}, {}) ({}, {})'.format(node.line, node.op, left_dim1, left_dim2,
                                                                 right_dim1, right_dim2))
                    return 'unknown'
            if left_dim1 != right_dim1 or left_dim2 != right_dim2:
                self.handle_error(
                    'Line {}: Unsupported operation between matrices of different dimensions'.format(node.line))
                return 'unknown'

        return_type = self.operation_rules.types[node.op][left_type][right_type]
        if return_type == 'unknown':
            self.handle_error(
                'Line {}: Operation {} unsupported between types: {} and {}'.format(node.line, node.op, left_type,
                                                                                    right_type))
            return 'unknown'
        return return_type

    def get_matrix_dims_depending_on_instance(self, node):
        k = node
        while isinstance(k, Expression):
            k = k.left
        node = k
        if isinstance(node, MatrixFunction):
            if len(node.parameters.expressions) == 1:
                dim = self.get_mfe_dim_at_index(node, 0)
                return dim, dim
            if len(node.parameters.expressions) == 2:
                left_dims = self.get_mfe_dim_at_index(node, 0), self.get_mfe_dim_at_index(node, 1)
                return left_dims
        if isinstance(node, MatrixRows):
            return self.get_matrix_dimensions(node)
        if isinstance(node, ID):
            return self.get_matrix_dimensions_for_id(node)

    def get_mfe_dim_at_index(self, node, index):
        params = node.parameters
        if isinstance(params[index], ID):
            value = self.get_matrix_dimensions_for_id(params[index])
            return value
        if isinstance(params[index], Number):
            return params[index].value
        if isinstance(params[index], String):
            return params[index].value

    def get_matrix_dimensions(self, matrix):
        # it must be matrix of correct dimensions - otherwise
        # node.expression wouldn't have returned that matrix type is 'matrix'
        return len(matrix.rows), len(matrix.rows[0].numbers)

    def get_matrix_dimensions_for_id(self, node):
        symbol = self.symbol_table.get(node.name)
        if isinstance(symbol.dim1, VariableSymbol):
            symbol.dim1 = self.symbol_table.get(symbol.dim1.name)
        if isinstance(symbol.dim2, VariableSymbol):
            symbol.dim2 = self.symbol_table.get(symbol.dim2.name)

        return symbol.dim1, symbol.dim2

    def visit_ExpressionUminus(self, node):
        return self.visit(node.expression)

    def visit_Transpose(self, node):
        return self.visit(node.expression)

    def visit_MatrixRows(self, node):
        matrix_of_types = []
        for row in node.rows:
            row_types = self.visit(row)
            if row_types == 'unknown':
                return 'unknown'
            matrix_of_types.append(row_types)

        if not len(set([len(l) for l in matrix_of_types])) == 1:
            self.handle_error('Line {}: Matrix initialization with vectors of different sizes'.format(node.line))
            return 'unknown'
        return 'matrix'

    def visit_Vector(self, node):
        row_types = [self.visit(param) for param in node.parameters.parameters]

        if row_types.__contains__('unknown'):
            return 'unknown'
        if not len(set(row_types)) == 1:
            self.handle_error('Line {}: Matrix row initialization with different types'.format(node.line))
            return 'unknown'

        coor_type = row_types[0]
        if coor_type == 'int' or coor_type == 'float':
            return row_types

        self.handle_error('Line {}: Matrix row initialization with illegal type: {}'.format(node.line, coor_type))
        return 'unknown'

    def visit_MatrixFunction(self, node):
        if len(node.parameters.parameters) == 1:
            param_type = self.visit(node.parameters.parameters[0])
            if param_type != 'int':
                return 'unknown'
            return 'matrix'
        elif len(node.parameters.parameters) == 2:
            param_type1 = self.visit(node.parameters.parameters[0])
            param_type2 = self.visit(node.parameters.parameters[1])
            if param_type1 != 'int' or param_type2 != 'int':
                return 'unknown'
            return 'matrix'
        else:
            return 'unknown'

    def visit_Parameters(self, node):
        for param in node.parameters:
            if self.visit(param) == 'unknown':
                return 'unknown'
        return self.visit(node.parameters[0])

    def visit_Reference(self, node):
        node_type = self.visit(node.variable)
        if node_type != 'matrix':
            self.handle_error('Line {}: Reference to: {}'.format(node.line, node_type))
            return 'unknown'

        param_type = self.visit(node.parameters)

        if param_type != 'int':
            self.handle_error('Line {}: Matrix index is not an integer: {}'.format(node.line, param_type))
            return 'unknown'

    def visit_String(self, node):
        return 'string'

    def visit_Number(self, node):
        if type(node.value) is int:
            return 'int'
        elif type(node.value) is float:
            return 'float'
        else:
            self.handle_error('Line {}: Integer initialized with incorrect value {}'.format(node.line, str(node.value)))

    def visit_ID(self, node):
        try:
            symbol = self.symbol_table.get(node.name)
        except KeyError:
            self.handle_error('Line {}: Id {} is referenced before declaration'.format(node.line, node.name))
            return "unknown"
        return symbol.type

    def visit_Error(self, node):
        pass
