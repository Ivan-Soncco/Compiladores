# parser_cpp.py

import ply.yacc as yacc
from lexer_cpp import CPPLexer

class ASTNode:
    """Nodo base para el Árbol de Sintaxis Abstracta"""
    def __init__(self, type_node, value=None, children=None):
        self.type = type_node
        self.value = value
        self.children = children or []
    
    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, {len(self.children)} children)"

class CPPParser:
    """
    Analizador sintáctico para C++ básico
    """
    
    def __init__(self):
        self.lexer = CPPLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
        self.ast = None
    
    # Precedencia de operadores
    precedence = (
        ('left', 'EQ', 'NE'),
        ('left', 'LT', 'GT', 'LE', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
    )
    
    # Gramática
    
    def p_program(self, p):
        '''program : statements'''
        self.ast = ASTNode('PROGRAM', children=p[1])
        p[0] = self.ast
    
    def p_statements(self, p):
        '''statements : statements statement
                     | statement'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
    
    def p_statement(self, p):
        '''statement : include_stmt
                    | declaration
                    | assignment
                    | if_stmt
                    | while_stmt
                    | for_stmt
                    | return_stmt
                    | expression_stmt
                    | function_def
                    | cout_stmt
                    | cin_stmt'''
        p[0] = p[1]
    
    def p_include_stmt(self, p):
        '''include_stmt : HASH INCLUDE LANGLE ID RANGLE
                       | HASH INCLUDE STRING'''
        if len(p) == 6:
            p[0] = ASTNode('INCLUDE', value=p[4])
        else:
            p[0] = ASTNode('INCLUDE', value=p[3])
    
    def p_declaration(self, p):
        '''declaration : type ID SEMICOLON
                      | type ID ASSIGN expression SEMICOLON'''
        if len(p) == 4:
            p[0] = ASTNode('DECLARATION', value=p[2], children=[ASTNode('TYPE', value=p[1])])
        else:
            p[0] = ASTNode('DECLARATION', value=p[2], 
                          children=[ASTNode('TYPE', value=p[1]), p[4]])
    
    def p_type(self, p):
        '''type : INT
               | FLOAT
               | CHAR
               | VOID'''
        p[0] = p[1]
    
    def p_assignment(self, p):
        '''assignment : ID ASSIGN expression SEMICOLON'''
        p[0] = ASTNode('ASSIGNMENT', value=p[1], children=[p[3]])
    
    def p_if_stmt(self, p):
        '''if_stmt : IF LPAREN expression RPAREN LBRACE statements RBRACE
                  | IF LPAREN expression RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
        if len(p) == 8:
            p[0] = ASTNode('IF', children=[p[3], ASTNode('BLOCK', children=p[6])])
        else:
            p[0] = ASTNode('IF', children=[p[3], ASTNode('BLOCK', children=p[6]), 
                                         ASTNode('ELSE', children=[ASTNode('BLOCK', children=p[10])])])
    
    def p_while_stmt(self, p):
        '''while_stmt : WHILE LPAREN expression RPAREN LBRACE statements RBRACE'''
        p[0] = ASTNode('WHILE', children=[p[3], ASTNode('BLOCK', children=p[6])])
    
    def p_for_stmt(self, p):
        '''for_stmt : FOR LPAREN assignment expression SEMICOLON assignment RPAREN LBRACE statements RBRACE'''
        p[0] = ASTNode('FOR', children=[p[3], p[4], p[6], ASTNode('BLOCK', children=p[9])])
    
    def p_return_stmt(self, p):
        '''return_stmt : RETURN expression SEMICOLON
                      | RETURN SEMICOLON'''
        if len(p) == 4:
            p[0] = ASTNode('RETURN', children=[p[2]])
        else:
            p[0] = ASTNode('RETURN')
    
    def p_function_def(self, p):
        '''function_def : type ID LPAREN RPAREN LBRACE statements RBRACE
                       | type MAIN LPAREN RPAREN LBRACE statements RBRACE'''
        func_name = p[2]
        p[0] = ASTNode('FUNCTION_DEF', value=func_name, 
                      children=[ASTNode('TYPE', value=p[1]), ASTNode('BLOCK', children=p[6])])
    
    def p_cout_stmt(self, p):
        '''cout_stmt : COUT LSHIFT expression SEMICOLON
                    | COUT LSHIFT expression LSHIFT ENDL SEMICOLON'''
        if len(p) == 5:
            p[0] = ASTNode('COUT', children=[p[3]])
        else:
            p[0] = ASTNode('COUT', children=[p[3], ASTNode('ENDL')])
    
    def p_cin_stmt(self, p):
        '''cin_stmt : CIN RSHIFT ID SEMICOLON'''
        p[0] = ASTNode('CIN', children=[ASTNode('ID', value=p[3])])
    
    def p_expression_stmt(self, p):
        '''expression_stmt : expression SEMICOLON'''
        p[0] = ASTNode('EXPRESSION_STMT', children=[p[1]])
    
    def p_expression_binop(self, p):
        '''expression : expression PLUS expression
                     | expression MINUS expression
                     | expression TIMES expression
                     | expression DIVIDE expression
                     | expression EQ expression
                     | expression NE expression
                     | expression LT expression
                     | expression GT expression
                     | expression LE expression
                     | expression GE expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]])
    
    def p_expression_unary(self, p):
        '''expression : MINUS expression %prec UMINUS'''
        p[0] = ASTNode('UNARY', value=p[1], children=[p[2]])
    
    def p_expression_group(self, p):
        '''expression : LPAREN expression RPAREN'''
        p[0] = p[2]
    
    def p_expression_number(self, p):
        '''expression : NUMBER'''
        p[0] = ASTNode('NUMBER', value=p[1])
    
    def p_expression_string(self, p):
        '''expression : STRING'''
        p[0] = ASTNode('STRING', value=p[1])
    
    def p_expression_id(self, p):
        '''expression : ID'''
        p[0] = ASTNode('ID', value=p[1])
    
    def p_error(self, p):
        if p:
            print(f"Error sintáctico en token '{p.value}' (línea {p.lineno})")
        else:
            print("Error sintáctico: fin de archivo inesperado")
    
    def parse(self, code):
        """Parsea el código y retorna el AST"""
        tokens = self.lexer.tokenize(code)
        result = self.parser.parse(code, lexer=self.lexer.lexer)
        return result