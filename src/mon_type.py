#!/usr/bin/python
import inspect

import AST
from SemanticRules import SemanticRules
from SymbolTable import *

verbose = False


class NodeVisitor(object):
    def __init__(self):
        self.semantic_rules = SemanticRules()
        self.symbol_table = SymbolTable(None, 'Program')
        self.error = False

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):  # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            nodeChildren = node.__dict__.values()
            for child in nodeChildren:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    def handle_error(self, message):
        self.error = True
        print(message)

    def printFunctionName(self):
        print(inspect.stack()[1][3])


class TypeChecker(NodeVisitor):

    def visit_InstructionsOpt(self, node):
        if (verbose): self.printFunctionName()
        self.visit(node.instructions)

    def visit_Instructions(self, node):
        if (verbose): self.printFunctionName()
        for instruction in node.instructions:
            self.visit(instruction)

    def visit_If(self, node):
        if (verbose): self.printFunctionName()
        self.symbol_table.pushScope('if')

        self.visit(node.booleanInParentheses)
        self.visit(node.instruction)

        self.symbol_table.popScope()

    def visit_IfElse(self, node):
        if (verbose): self.printFunctionName()
        self.symbol_table.pushScope('if')
        self.visit(node.booleanInParentheses)
        self.visit(node.instruction)
        self.symbol_table.popScope()

        self.symbol_table.pushScope('else')
        self.visit(node.else_instruction)
        self.symbol_table.popScope()

    def visit_For(self, node):
        if (verbose): self.printFunctionName()
        self.symbol_table.pushNesting()
        self.symbol_table.pushScope('for')

        self.symbol_table.put(node.id.name, Symbol(name=node.id.name, type='int'))
        self.visit(node.id)
        self.visit(node.range)
        self.visit(node.instruction)

        self.symbol_table.popScope()
        self.symbol_table.popNesting()

    def visit_Range(self, node):
        if (verbose): self.printFunctionName()
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
        if start_type == 'unknown' or end_type == 'unknown':
            return 'unknown'
        elif start_type != 'int' or end_type != 'int':
            self.handle_error('Line {}: Range of unsupported types: {} and {}'.format(node.line, start_type, end_type))
            return 'unknown'
        return 'int'

    def visit_While(self, node):
        if (verbose): self.printFunctionName()
        self.symbol_table.pushNesting()
        self.symbol_table.pushScope('while')

        self.visit(node.booleanInParentheses)
        self.visit(node.instruction)

        self.symbol_table.popScope()
        self.symbol_table.popNesting()

    def visit_Break(self, node):
        if (verbose): self.printFunctionName()
        if (self.symbol_table.nesting == 0):
            self.handle_error('Line {}: Trying to break from outside of a loop'.format(node.line))

    def visit_Continue(self, node):
        if (verbose): self.printFunctionName()
        if (self.symbol_table.nesting == 0):
            self.handle_error("Line {}: Trying to call continue from outside of a loop".format(node.line))

    def visit_Return(self, node):
        if (verbose): self.printFunctionName()
        self.visit(node.expr)

    def visit_Assign(self, node):
        if (verbose): self.printFunctionName()

        right_type = self.visit(node.expression)

        if right_type == 'unknown':
            return 'unknown'

        if right_type == 'matrix':
            matrix = node.expression

            dim1 = dim2 = None
            if isinstance(matrix, AST.MatrixFunctions):  # zeros(a,b,c) TODO: modify matrices to be multiple-dim
                matrix_func_dims = []
                for expr in matrix.mfe.expressions:
                    if isinstance(expr, AST.Id):
                        if self.visit(expr) == 'unknown':
                            return 'unknown'

                        value = self.symbol_table.get(expr.name).val
                        matrix_func_dims.append(value)
                    else:
                        matrix_func_dims.append(expr.value)

                if len(matrix.mfe.expressions) == 1:  # zeros(2) <=> zeros(2,2)
                    dim1 = matrix_func_dims[0]
                    dim2 = dim1
                elif len(matrix.mfe.expressions) == 2:  # zeros(3,1), zeros(2,2)
                    dim1 = matrix_func_dims[0]
                    dim2 = matrix_func_dims[1]
            elif isinstance(matrix, AST.Expression):  # it's a matrix expression
                dim1, dim2 = self.get_matrix_dims_depending_on_instance(matrix.left)
            elif isinstance(matrix, AST.Rows):  # it's a Rows object
                dim1, dim2 = self.get_matrix_dimensions(matrix)
            elif isinstance(matrix, AST.Id):
                dim1, dim2 = self.get_matrix_dimensions_for_id(matrix)

            # if right expr is an instance of Id, then we put its name to the symbol_table. Otherwise, we put there its
            # value
            symbol = MatrixSymbol(name=node.id.name, type=right_type, val=node.expression, dim1=dim1, dim2=dim2)
        else:
            symbol = Symbol(name=node.id.name, type=right_type, val=node.expression)

        self.symbol_table.put(node.id.name, symbol)
        return right_type

    def visit_AssignOperators(self, node):  # x += , -=, *=, /=
        if (verbose): self.printFunctionName()

        left_type = self.visit(node.id)
        right_type = self.visit(node.expression)

        if left_type == 'unknown' or right_type == 'unknown':
            return 'unknown'

        left = self.symbol_table.get(node.id.name)
        return_type = self.semantic_rules.types[node.oper][left_type][right_type]

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

    def visit_AssignRef(self, node):  # x[1,2] = 6
        if (verbose): self.printFunctionName()
        self.visit(node.ref)
        self.visit(node.expression)

    def visit_Ref(self, node):  # x[1,2]
        if (verbose): self.printFunctionName()
        node_type = self.visit(node.id)
        if node_type != 'matrix':
            self.handle_error('Line {}: Reference to: {}'.format(node.line, node_type))
            return 'unknown'

        ind1_type = self.visit(node.ind1)
        ind2_type = self.visit(node.ind2)

        for t in {ind1_type, ind2_type}:
            if t != 'int':
                self.handle_error('Line {}: Matrix index is not an integer: {}'.format(node.line, t))
                return 'unknown'

    def visit_Expression(self, node):
        if (verbose): self.printFunctionName()
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == 'unknown' or right_type == 'unknown':
            return 'unknown'

        if left_type == 'matrix' and right_type == 'matrix':
            left_dim1, left_dim2 = self.get_matrix_dims_depending_on_instance(node.left)
            right_dim1, right_dim2 = self.get_matrix_dims_depending_on_instance(node.right)

            if node.oper == '*':
                if left_dim2 == right_dim1:
                    return 'matrix'
                else:
                    self.handle_error('Line {}: Unsupported operation "{}" between matrices of different dimensions: '
                                      '({}, {}) ({}, {})'.format(node.line, node.oper, left_dim1, left_dim2,
                                                                 right_dim1, right_dim2))
                    return 'unknown'
            if left_dim1 != right_dim1 or left_dim2 != right_dim2:
                self.handle_error(
                    'Line {}: Unsupported operation between matrices of different dimensions'.format(node.line))
                return 'unknown'

        return_type = self.semantic_rules.types[node.oper][left_type][right_type]
        if return_type == 'unknown':
            self.handle_error(
                'Line {}: Operation {} unsupported between types: {} and {}'.format(node.line, node.oper, left_type,
                                                                                    right_type))
            return 'unknown'
        return return_type

    def visit_MatrixFunctions(self, node):
        if (verbose): self.printFunctionName()  # zeros(1,3)

        if node.func == 'eye' and len(node.mfe.expressions) > 2:
            self.handle_error(self.get_error_message_for_matrix_fun(node) +
                              " eye must be square, we allow only eye(5) or eye(5,5)")
            return 'unknown'

        dim_type = self.visit(node.mfe)

        # print 1, [2,4,3], 5
        if dim_type != 'mfe':
            self.handle_error(self.get_error_message_for_matrix_fun(node))
            return 'unknown'
        return 'matrix'

    def visit_MatrixFunctionsExpression(self, node):
        if (verbose): self.printFunctionName()

        if len(node.expressions) == 1:
            dim_type = self.visit(node.expressions[0])
            if dim_type != 'int':
                return 'unknown'
            return 'mfe'
        elif len(node.expressions) == 2:
            dim_type1 = self.visit(node.expressions[0])
            dim_type2 = self.visit(node.expressions[1])
            if dim_type1 != 'int' or dim_type2 != 'int':
                return 'unknown'
            return 'mfe'
        else:
            return 'unknown'

    def visit_MultipleExpression(self, node):  # designed for printing as well as matrix functions
        if (verbose): self.printFunctionName()
        for expr in node.expressions:
            if self.visit(expr) == 'unknown':
                return 'unknown'

        return 'multiple_expression'

    def visit_BooleanExpression(self, node):
        if (verbose): self.printFunctionName()
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type == 'unknown' or right_type == 'unknown':
            return 'boolean'

        return_type = self.semantic_rules.types[node.oper][left_type][right_type]
        if return_type == 'unknown':
            self.handle_error(
                'Line {}: Operation {} unsupported between types: {} and {}'.format(node.line, node.oper, left_type,
                                                                                    right_type))
        return 'boolean'

    def visit_UMinusExpression(self, node):
        if (verbose): self.printFunctionName()
        return self.visit(node.expression)

    def visit_Transposition(self, node):
        if (verbose): self.printFunctionName()
        return self.visit(node.expression)

    def visit_Rows(self, node):
        if (verbose): self.printFunctionName()
        # [ 1, 2.3;
        #  4.66666, 5];

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

    def visit_Row(self, node):
        if (verbose): self.printFunctionName()
        row_types = [self.visit(number) for number in node.numbers]

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

    def visit_Constant(self, node):
        if (verbose): self.printFunctionName()
        val = node.value
        if type(val) is int:
            return 'int'
        if type(val) is float:
            return 'float'

    def visit_Id(self, node):
        if (verbose): self.printFunctionName()
        try:
            symbol = self.symbol_table.get(node.name)
        except KeyError:
            self.handle_error('Line {}: Id {} is used but not declared'.format(node.line, node.name))
            return "unknown"

        return symbol.type

    def visit_Error(self, node):
        if (verbose): self.printFunctionName()
        pass

    def visit_String(self, node):
        return 'string'

    def get_error_message_for_matrix_fun(self, node):
        error_msg = 'Line {}: Illegal matrix initialization: {}('.format(node.line, node.func)

        matrix_functions_expressions = node.mfe.expressions
        if len(matrix_functions_expressions):
            commas_count = len(matrix_functions_expressions) - 1
            for i in range(0, len(matrix_functions_expressions)):
                error_msg += '{}'.format(matrix_functions_expressions[i])
                if commas_count:
                    error_msg += ', '
                    commas_count -= 1
                else:
                    error_msg += ' '

        error_msg += ')'
        return error_msg

    def get_matrix_dims_depending_on_instance(self, node):
        k = node
        while isinstance(k, AST.Expression):
            k = k.left
        node = k
        if isinstance(node, AST.MatrixFunctions):
            if len(node.mfe.expressions) == 1:
                dim = self.get_mfe_dim_at_index(node, 0)
                return dim, dim
            if len(node.mfe.expressions) == 2:
                left_dims = self.get_mfe_dim_at_index(node, 0), self.get_mfe_dim_at_index(node, 1)
                return left_dims
        if isinstance(node, AST.Rows):
            return self.get_matrix_dimensions(node)
        if isinstance(node, AST.Id):
            return self.get_matrix_dimensions_for_id(node)

    def get_mfe_dim_at_index(self, node, index):
        expr = node.mfe.expressions
        if isinstance(expr[index], AST.Id):
            value = self.get_matrix_dimensions_for_id(expr[index])
            return value
        if isinstance(expr[index], AST.Constant):
            return expr[index].value

    def get_matrix_dimensions(self, matrix):
        # it must be matrix of correct dimensions - otherwise
        # node.expression wouldn't have returned that matrix type is 'matrix'
        return len(matrix.rows), len(matrix.rows[0].numbers)

    def get_matrix_dimensions_for_id(self, node):
        symbol = self.symbol_table.get(node.name)
        if isinstance(symbol.dim1, Symbol):
            symbol.dim1 = self.symbol_table.get(symbol.dim1.name)
        if isinstance(symbol.dim2, Symbol):
            symbol.dim2 = self.symbol_table.get(symbol.dim2.name)

        return symbol.dim1, symbol.dim2