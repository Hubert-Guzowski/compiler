import sys
import task1_Lex
import task2_Yacc
from task3_TreePrinter import AstPrinter
from task4_TypeChecker import TypeChecker
from task5_interpreter import Interpreter


if __name__ == '__main__':

    filename = "..\\resources\\task4\control_transfer.m"

    try:
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = task2_Yacc.parser
    text = file.read()
    ast_printer = parser.parse(text, lexer=task1_Lex.lexer)

    ast_printer.printTree()

    # if not task2_yacc.error_flag:
    #     ast_printer.printTree()
    # else:
    #     print("Error ocured")

    type_checker = TypeChecker()
    type_checker.visit(ast_printer)

    ast_printer.accept(Interpreter())
