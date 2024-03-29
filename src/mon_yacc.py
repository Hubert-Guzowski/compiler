import sys

import ply.yacc as yacc

import mon_lex
from AST import *

tokens = mon_lex.tokens

precedence = (
    ("nonassoc", 'IFX'),
    ("nonassoc", 'ELSE'),
    ("nonassoc", 'ASSIGN', 'ADDASSIGN', 'MINASSIGN', 'MULASSIGN', 'DIVASSIGN', 'RELASSIGN'),
    ("left", 'ADD', 'MIN', 'DOTADD', 'DOTMIN'),
    ("left", 'MUL', 'DIV', 'DOTMUL', 'DOTDIV'),
    ("left", 'LT', 'GT', 'LTE', 'GTE', 'NE'),
    ("left", '(', ')', '{', '}'),
    ("nonassoc", 'TRANSPOSE'),
    ("right", 'UMINUS')  # Unary minus operator
)


def p_program(p):
    """program : instructions_opt"""
    p[0] = p[1]


def p_instructions_opt(p):
    """instructions_opt : instructions"""
    p[0] = InstructionsOpt(p[1])
    p[0].line = mon_lex.lexer.lineno


def p_instructions_opt2(p):
    """instructions_opt : """
    p[0] = InstructionsOpt()
    p[0].line = mon_lex.lexer.lineno


def p_instructions(p):
    """instructions : instructions instruction
                    | instruction"""

    if len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
    elif len(p) == 2:
        p[0] = Instructions(p[1])
        p[0].line = mon_lex.lexer.lineno


def p_block(p):
    """ block : '{' instructions '}' """
    p[0] = p[2]


def p_instruction(p):
    """instruction : block
                    | if
                    | for
                    | while
                    | break ';'
                    | continue ';'
                    | return ';'
                    | print ';'
                    | assign ';'"""
    p[0] = p[1]


def p_if(p):
    """if : IF BOOLEAN_IN_PARENTHESES instruction %prec IFX
          | IF BOOLEAN_IN_PARENTHESES instruction ELSE instruction"""
    if len(p) == 4:
        p[0] = If(p[2], p[3])
    if len(p) == 6:
        p[0] = IfElse(p[2], p[3], p[5])
        p[0].line = mon_lex.lexer.lineno


def p_for(p):
    """for :  FOR ID ASSIGN RANGE instruction """
    id = Id(p[2])
    p[0] = For(id, p[4], p[5])
    id.line = mon_lex.lexer.lineno
    p[0].line = mon_lex.lexer.lineno


def p_range1(p):
    """RANGE : EXPRESSION ':' EXPRESSION"""
    p[0] = Range(p[1], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_while(p):
    """while : WHILE BOOLEAN_IN_PARENTHESES instruction """
    p[0] = While(p[2], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_break(p):
    """break : BREAK """
    p[0] = Break()
    p[0].line = mon_lex.lexer.lineno


def p_continue(p):
    """continue : CONTINUE """
    p[0] = Continue()
    p[0].line = mon_lex.lexer.lineno


def p_return(p):
    """return : RETURN
              | RETURN EXPRESSION
              | RETURN BOOLEAN_EXPRESSION"""
    if len(p) == 3:
        p[0] = Return(p[2])
    elif len(p) == 2:
        p[0] = Return()

    p[0].line = mon_lex.lexer.lineno


def p_expression_assignment(p):
    """assign : ID ASSIGN EXPRESSION"""
    id = Id(p[1])
    id.line = mon_lex.lexer.lineno
    p[0] = Assign(id, p[3])
    p[0].line = mon_lex.lexer.lineno


def p_expression_assignment1(p):
    """assign : ID ADDASSIGN EXPRESSION
              | ID MINASSIGN EXPRESSION
              | ID MULASSIGN EXPRESSION
              | ID DIVASSIGN EXPRESSION"""
    id = Id(p[1])
    id.line = mon_lex.lexer.lineno
    p[0] = AssignOperators(p[2], id, p[3])
    p[0].line = mon_lex.lexer.lineno


def p_expression_assignment_ref(p):
    """assign : REF ASSIGN EXPRESSION"""
    p[0] = AssignRef(p[1], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_expression_ref(p):
    """REF : ID '[' EXPRESSION  ',' EXPRESSION ']'"""
    id = Id(p[1])
    id.line = mon_lex.lexer.lineno
    p[0] = Ref(id, p[3], p[5])
    p[0].line = mon_lex.lexer.lineno


def p_expression_rel(p):
    """BOOLEAN_EXPRESSION : EXPRESSION LT EXPRESSION
                          | EXPRESSION GT EXPRESSION
                          | EXPRESSION LTE EXPRESSION
                          | EXPRESSION GTE EXPRESSION
                          | EXPRESSION NE EXPRESSION
                          | EXPRESSION RELASSIGN EXPRESSION"""

    p[0] = BooleanExpression(p[2], p[1], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_expression_sum(p):
    """EXPRESSION : EXPRESSION ADD EXPRESSION
                  | EXPRESSION MIN EXPRESSION
                  | EXPRESSION MUL EXPRESSION
                  | EXPRESSION DIV EXPRESSION"""
    p[0] = Expression(p[2], p[1], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_expression_mul(p):
    """EXPRESSION : EXPRESSION DOTADD EXPRESSION
                  | EXPRESSION DOTMIN EXPRESSION
                  | EXPRESSION DOTMUL EXPRESSION
                  | EXPRESSION DOTDIV EXPRESSION"""
    p[0] = Expression(p[2], p[1], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_expr_uminus(p):
    """EXPRESSION : MIN EXPRESSION %prec UMINUS"""
    #  %prec UMINUS overrides the default rule precedence--setting it to that of UMINUS in the precedence specifier.
    p[0] = UMinusExpression(p[2])
    p[0].line = mon_lex.lexer.lineno


def p_transpose(p):
    """EXPRESSION : EXPRESSION TRANSPOSE"""
    p[0] = Transposition(p[1])
    p[0].line = mon_lex.lexer.lineno


def p_expression_1(p):
    """EXPRESSION : MATRIX
                  | MATRIX_FUNCTIONS
                  | REF
                  | NUMBER"""
    p[0] = p[1]


def p_expression_2(p):
    """EXPRESSION : STR"""
    p[0] = String(p[1])
    p[0].line = mon_lex.lexer.lineno


def p_expression_3(p):
    """EXPRESSION : ID"""
    p[0] = Id(p[1])
    p[0].line = mon_lex.lexer.lineno


def p_number_int(p):
    """NUMBER : INT
              | FLOAT"""
    p[0] = Constant(p[1])
    p[0].line = mon_lex.lexer.lineno


def p_matrix(p):
    """MATRIX : '[' ROWS ']'"""
    # p[0] = Matrix(p[2])
    p[0] = p[2]


def p_matrix_rows(p):
    """ ROWS : ROWS ';' ROW
             | ROW"""
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    if len(p) == 2:
        p[0] = Rows(p[1])
        p[0].line = mon_lex.lexer.lineno


def p_matrix_row(p):
    """ ROW : ROW ',' EXPRESSION
            | EXPRESSION"""
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    elif len(p) == 2:
        p[0] = Row(p[1])
        p[0].line = mon_lex.lexer.lineno


def p_expression_matrix_functions(p):
    """MATRIX_FUNCTIONS : EYE '(' MATRIX_FUNCTIONS_EXPRESSION ')'
                         | ZEROS '(' MATRIX_FUNCTIONS_EXPRESSION ')'
                         | ONES '(' MATRIX_FUNCTIONS_EXPRESSION ')'"""

    p[0] = MatrixFunctions(p[1], p[3])
    p[0].line = mon_lex.lexer.lineno


def p_boolean_in_parentheses(p):
    """BOOLEAN_IN_PARENTHESES : '(' BOOLEAN_EXPRESSION ')'"""
    p[0] = p[2]


def p_multiple_expression(p):
    """MULTIPLE_EXPR : MULTIPLE_EXPR ',' EXPRESSION
                     | EXPRESSION"""
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    elif len(p) == 2:
        p[0] = MultipleExpression(p[1])
        p[0].line = mon_lex.lexer.lineno


def p_expression_matrix_functions_expression(p):
    """MATRIX_FUNCTIONS_EXPRESSION : MATRIX_FUNCTIONS_EXPRESSION ',' EXPRESSION
                                   | EXPRESSION"""
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    elif len(p) == 2:
        p[0] = MatrixFunctionsExpression(p[1])
        p[0].line = mon_lex.lexer.lineno


def p_print(p):
    """print : PRINT MULTIPLE_EXPR """
    p[0] = Print(p[2])
    p[0].line = mon_lex.lexer.lineno


def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken({1}, '{2}')".format(p.lineno, p.type, p.value))
        sys.exit()
    else:
        print("Unexpected end of input")


parser = yacc.yacc()