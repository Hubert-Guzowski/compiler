import sys

import ply.yacc as yacc

import task1_Lex
from task3_Ast import *

tokens = task1_Lex.tokens

precedence = (
    ("nonassoc", 'IFX'),
    ("nonassoc", 'ELSE'),
    ("nonassoc", 'ASSIGN', 'ADDASSIGN', 'MINASSIGN', 'MULASSIGN', 'DIVASSIGN', 'EQ'),
    ("left", 'ADD', 'MIN', 'DOTADD', 'DOTMIN'),
    ("left", 'MUL', 'DIV', 'DOTMUL', 'DOTDIV'),
    ("left", 'LT', 'GT', 'LTE', 'GTE', 'NE'),
    ("left", '(', ')', '{', '}'),
    ("nonassoc", 'TRANSPOSE'),
    ("right", 'UMINUS')  # Unary minus operator
)


def p_program(p):
    """program : instructions
               |"""
    p[0] = p[1]


def p_instructions(p):
    """instructions : instructions instruction
                    | instruction"""
    if len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
    elif len(p) == 2:
        p[0] = Instructions(p[1])
        p[0].line = task1_Lex.lexer.lineno


def p_instruction(p):
    """instruction : block
                   | if
                   | for
                   | while
                   | break ';'
                   | continue ';'
                   | return ';'
                   | print ';'
                   | statement ';'"""
    p[0] = p[1]


def p_instruction_block(p):
    """block : '{' instructions '}' """
    p[0] = p[2]


# zmiana składni języka
# def p_if(p):
#     """if : IF condition instruction %prec IFX
#           | IF condition instruction ELSE instruction"""


def p_if(p):
    """if : IF '(' condition ')' instruction %prec IFX
          | IF '(' condition ')' instruction ELSE instruction"""
    if len(p) == 6:
        p[0] = If(p[3], p[5])
    elif len(p) == 8:
        p[0] = IfElse(p[3], p[5], p[7])
        p[0].line = task1_Lex.lexer.lineno


def p_for(p):
    """for : FOR variable ASSIGN expression ':' expression instruction"""
    p[0] = For(p[2], p[4], p[6], p[7])
    p[0].line = task1_Lex.lexer.lineno


# zmiana składni języka
# def p_while(p):
#     """while : WHILE condition instruction"""


def p_while(p):
    """while : WHILE '(' condition ')' instruction"""
    p[0] = While(p[3], p[5])
    p[0].line = task1_Lex.lexer.lineno


def p_break(p):
    """break : BREAK"""
    p[0] = Break()
    p[0].line = task1_Lex.lexer.lineno


def p_continue(p):
    """continue : CONTINUE"""
    p[0] = Continue()
    p[0].line = task1_Lex.lexer.lineno


def p_return(p):
    """return : RETURN
              | RETURN expression
              | RETURN condition"""
    if len(p) == 2:
        p[0] = Return()
    elif len(p) == 3:
        p[0] = Return(p[2])


def p_print(p):
    """print : PRINT parameters"""
    p[0] = Print(p[2])


def p_statement(p):
    """statement : assign
                 | expression"""
    p[0] = p[1]


def p_assign_direct(p):
    """assign : assignable ASSIGN expression"""
    p[0] = AssignDirect(p[1], p[2], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_assign_operation(p):
    """assign : assignable ADDASSIGN expression
              | assignable MINASSIGN expression
              | assignable MULASSIGN expression
              | assignable DIVASSIGN expression"""
    p[0] = AssignOperation(p[1], p[2], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_assignable(p):
    """assignable : variable
                  | reference"""
    p[0] = p[1]


def p_condition(p):
    """condition : expression LT expression
                 | expression GT expression
                 | expression LTE expression
                 | expression GTE expression
                 | expression NE expression
                 | expression EQ expression"""
    p[0] = Condition(p[1], p[2], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_exp_arithmetic(p):
    """expression : expression ADD expression
                  | expression MIN expression
                  | expression MUL expression
                  | expression DIV expression"""
    p[0] = Expression(p[1], p[2], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_exp_arithmetic_matrix(p):
    """expression : expression DOTADD expression
                  | expression DOTMIN expression
                  | expression DOTMUL expression
                  | expression DOTDIV expression"""
    p[0] = Expression(p[1], p[2], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_exp_uminus(p):
    """expression : MIN expression %prec UMINUS"""
    p[0] = ExpressionUminus(p[2])
    p[0].line = task1_Lex.lexer.lineno


def p_exp_transpose(p):
    """expression : matrix_obj TRANSPOSE
                  | variable TRANSPOSE"""
    p[0] = Transpose(p[1])
    p[0].line = task1_Lex.lexer.lineno


def p_exp_string(p):
    """expression : STR"""
    p[0] = String(p[1])
    p[0].line = task1_Lex.lexer.lineno


def p_exp_other(p):
    """expression : matrix_obj
                  | vector
                  | assignable
                  | number"""
    p[0] = p[1]


def p_matrix_obj(p):
    """matrix_obj : matrix
                  | matrix_function"""
    p[0] = p[1]


def p_matrix(p):
    """matrix : '[' rows ';' ']'"""
    p[0] = p[2]


# zmiana składni języka
def p_rows(p):
    """rows : rows ';' row
            | row"""
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    if len(p) == 2:
        p[0] = MatrixRows(p[1])
        p[0].line = task1_Lex.lexer.lineno

# zmiana składni języka
# def p_rows(p):
#     """rows : rows ',' '[' row ']'
#             | '[' row ']'"""
#     if len(p) == 6:
#         p[0] = p[1]
#         p[0].append(p[4])
#     if len(p) == 4:
#         p[0] = MatrixRows(p[2])
#         p[0].line = task1_Lex.lexer.lineno


def p_row(p):
    """row : parameters"""
    p[0] = Vector(p[1])
    p[0].line = task1_Lex.lexer.lineno


def p_vector(p):
    """vector : '[' parameters ']'"""
    p[0] = Vector(p[2])
    p[0].line = task1_Lex.lexer.lineno


def p_matrix_function(p):
    """matrix_function : EYE '(' parameters ')'
                       | ZEROS '(' parameters ')'
                       | ONES '(' parameters ')'"""
    p[0] = MatrixFunction(p[1], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_parameters(p):
    """parameters : parameters ',' expression
                  | expression"""
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    elif len(p) == 2:
        p[0] = Parameters(p[1])
        p[0].line = task1_Lex.lexer.lineno


def p_reference(p):
    """reference : variable '[' parameters ']' """
    p[0] = Reference(p[1], p[3])
    p[0].line = task1_Lex.lexer.lineno


def p_number(p):
    """number : INT
              | FLOAT"""
    p[0] = Number(p[1])
    p[0].line = task1_Lex.lexer.lineno


def p_variable(p):
    """variable : ID"""
    p[0] = ID(p[1])
    p[0].line = task1_Lex.lexer.lineno


def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken({1}, '{2}')".format(p.lineno, p.type, p.value))
        sys.exit()
    else:
        print("Unexpected end of input")


parser = yacc.yacc()
