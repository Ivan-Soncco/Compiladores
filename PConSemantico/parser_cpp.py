import ply.yacc as yacc
from lexer_cpp import CPPLexer

class ASTNode:
    """Nodo base para el Árbol de Sintaxis Abstracta"""
    def __init__(self, type_node, value=None, children=None, line=None):
        self.type = type_node
        self.value = value
        self.children = children or []
        self.line = line

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, {len(self.children)} children)"


class CPPParser:

    def __init__(self):
        self.lexer = CPPLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
        self.ast = None
        self.errors = []

    # -------- PRECEDENCIA --------
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'LT', 'GT', 'LE', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MODULO'),
        ('right', 'UMINUS', 'UNOT'),
    )

    # ==================== REGLAS DE PRODUCCIÓN ====================
    def p_program(self, p):
        'program : declaration_list'
        self.ast = ASTNode('PROGRAM', children=p[1])
        p[0] = self.ast

    # --- Declaraciones de alto nivel --------------------------------
    def p_declaration_list(self, p):
        '''declaration_list : declaration_list declaration
                            | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_declaration(self, p):
        '''declaration : var_declaration
                       | fun_declaration'''
        p[0] = p[1]

    # --- Declaración de variables -----------------------------------
    def p_var_declaration(self, p):
        'var_declaration : type init_declarator_list SEMICOLON'
        p[0] = ASTNode('VAR_DECL', children=[ASTNode('TYPE', value=p[1])] + p[2], line=p.lineno(1))

    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                                | init_declarator_list COMMA init_declarator'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_init_declarator(self, p):
        'init_declarator : ID opt_initializer'
        p[0] = ASTNode('INIT_DECL', value=p[1], children=([p[2]] if p[2] else []), line=p.lineno(1))

    def p_opt_initializer(self, p):
        '''opt_initializer : ASSIGN expression
                           | empty'''
        p[0] = p[2] if len(p) == 3 else None

    # --- Definición de funciones ------------------------------------
    def p_fun_declaration(self, p):
        'fun_declaration : type ID LPAREN params RPAREN compound_stmt'
        p[0] = ASTNode('FUN_DEF', value=p[2], children=[ASTNode('TYPE', value=p[1]), p[4], p[6]], line=p.lineno(2))

    def p_params(self, p):
        '''params : param_list
                  | VOID
                  | empty'''
        if len(p) == 2 and isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = []

    def p_param_list(self, p):
        '''param_list : param
                      | param_list COMMA param'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_param(self, p):
        'param : type ID'
        p[0] = ASTNode('PARAM', value=p[2], children=[ASTNode('TYPE', value=p[1])], line=p.lineno(2))

    # --- Bloques y declaraciones locales -----------------------------
    def p_compound_stmt(self, p):
        'compound_stmt : LBRACE local_declarations statement_list RBRACE'
        p[0] = ASTNode('BLOCK', children=p[2] + p[3], line=p.lineno(1))

    def p_local_declarations(self, p):
        '''local_declarations : local_declarations var_declaration
                              | empty'''
        p[0] = p[1] + [p[2]] if len(p) == 3 else []

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                          | empty'''
        p[0] = p[1] + [p[2]] if len(p) == 3 else []

    # --- Sentencias --------------------------------------------------
    def p_statement(self, p):
        '''statement : expression_stmt
                     | compound_stmt
                     | selection_stmt
                     | iteration_stmt
                     | return_stmt
                     | io_stmt'''
        p[0] = p[1]

    def p_expression_stmt(self, p):
        'expression_stmt : expression_opt SEMICOLON'
        p[0] = p[1] if p[1] else ASTNode('EMPTY', line=p.lineno(2))

    def p_expression_opt(self, p):
        '''expression_opt : expression
                          | empty'''
        p[0] = p[1]

    # --- If / else ---------------------------------------------------
    def p_selection_stmt(self, p):
        '''selection_stmt : IF LPAREN expression RPAREN statement
                          | IF LPAREN expression RPAREN statement ELSE statement'''
        p[0] = ASTNode('IF', children=[p[3], p[5]] + ([p[7]] if len(p) == 8 else []), line=p.lineno(1))

    # --- While / for -------------------------------------------------
    def p_iteration_stmt(self, p):
        '''iteration_stmt : WHILE LPAREN expression RPAREN statement
                          | FOR LPAREN expression_opt SEMICOLON expression_opt SEMICOLON expression_opt RPAREN statement'''
        if p[1] == 'while':
            p[0] = ASTNode('WHILE', children=[p[3], p[5]], line=p.lineno(1))
        else:
            p[0] = ASTNode('FOR', children=[p[3], p[5], p[7], p[9]], line=p.lineno(1))

    # --- Return ------------------------------------------------------
    def p_return_stmt(self, p):
        'return_stmt : RETURN expression_opt SEMICOLON'
        p[0] = ASTNode('RETURN', children=([p[2]] if p[2] else []), line=p.lineno(1))

    # --- E/S ---------------------------------------------------------
    def p_io_stmt(self, p):
        '''io_stmt : CIN io_in_list SEMICOLON
                   | COUT io_out_list SEMICOLON'''
        node_type = 'CIN' if p[1] == 'cin' else 'COUT'
        p[0] = ASTNode(node_type, children=p[2], line=p.lineno(1))

    def p_io_in_list(self, p):
        '''io_in_list : io_in_list SHIFT_IN var_ref
                      | SHIFT_IN var_ref'''
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[2]]

    def p_io_out_list(self, p):
        '''io_out_list : io_out_list SHIFT_OUT io_item
                        | SHIFT_OUT io_item'''
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[2]]

    def p_var_ref(self, p):
        'var_ref : ID'
        p[0] = ASTNode('ID', value=p[1], line=p.lineno(1))

    def p_io_item(self, p):
        'io_item : expression'
        p[0] = p[1]

    # --------------------- Expresiones -------------------------------
    def p_expression(self, p):
        'expression : assignment_expression'
        p[0] = p[1]

    def p_assignment_expression(self, p):
        '''assignment_expression : var_ref ASSIGN assignment_expression
                                 | logical_or_expression'''
        if len(p) == 4:
            p[0] = ASTNode('ASSIGN', children=[p[1], p[3]], line=p.lineno(2))
        else:
            p[0] = p[1]

    def p_logical_or_expression(self, p):
        '''logical_or_expression : logical_or_expression OR logical_and_expression
                                 | logical_and_expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]], line=p.lineno(2)) if len(p) == 4 else p[1]

    def p_logical_and_expression(self, p):
        '''logical_and_expression : logical_and_expression AND equality_expression
                                  | equality_expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]], line=p.lineno(2)) if len(p) == 4 else p[1]

    def p_equality_expression(self, p):
        '''equality_expression : equality_expression EQ relational_expression
                               | equality_expression NE relational_expression
                               | relational_expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]], line=p.lineno(2)) if len(p) == 4 else p[1]

    def p_relational_expression(self, p):
        '''relational_expression : relational_expression LT additive_expression
                                 | relational_expression GT additive_expression
                                 | relational_expression LE additive_expression
                                 | relational_expression GE additive_expression
                                 | additive_expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]], line=p.lineno(2)) if len(p) == 4 else p[1]

    def p_additive_expression(self, p):
        '''additive_expression : additive_expression PLUS multiplicative_expression
                               | additive_expression MINUS multiplicative_expression
                               | multiplicative_expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]], line=p.lineno(2)) if len(p) == 4 else p[1]

    def p_multiplicative_expression(self, p):
        '''multiplicative_expression : multiplicative_expression TIMES unary_expression
                                     | multiplicative_expression DIVIDE unary_expression
                                     | multiplicative_expression MODULO unary_expression
                                     | unary_expression'''
        p[0] = ASTNode('BINOP', value=p[2], children=[p[1], p[3]], line=p.lineno(2)) if len(p) == 4 else p[1]

    def p_unary_expression(self, p):
        '''unary_expression : MINUS unary_expression %prec UMINUS
                            | NOT unary_expression %prec UNOT
                            | primary_expression'''
        if len(p) == 3:
            p[0] = ASTNode('UNARY', value=p[1], children=[p[2]], line=p.lineno(1))
        else:
            p[0] = p[1]

    def p_primary_expression(self, p):
        '''primary_expression : ID
                              | NUMBER
                              | FLOAT_NUM
                              | STRING_LITERAL
                              | CHAR_LITERAL
                              | TRUE
                              | FALSE
                              | LPAREN expression RPAREN
                              | function_call'''
        if len(p) == 2:
            tok = p.slice[1]
            if tok.type == 'ID':
                p[0] = ASTNode('ID', value=p[1], line=p.lineno(1))
            elif tok.type in {'NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'CHAR_LITERAL'}:
                p[0] = ASTNode(tok.type, value=p[1], line=p.lineno(1))
            else:
                p[0] = ASTNode('BOOLEAN', value=p[1], line=p.lineno(1))
        elif len(p) == 4 and p[1] == '(':
            p[0] = p[2]
        else:  # function_call
            p[0] = p[1]

    def p_function_call(self, p):
        'function_call : ID LPAREN argument_list RPAREN'
        p[0] = ASTNode('CALL', value=p[1], children=p[3], line=p.lineno(1))

    def p_argument_list(self, p):
        '''argument_list : empty
                         | arg_seq'''
        p[0] = p[1] if p[1] else []

    def p_arg_seq(self, p):
        '''arg_seq : expression
                   | arg_seq COMMA expression'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    # --- Tipos -------------------------------------------------------
    def p_type(self, p):
        '''type : INT
                | FLOAT
                | DOUBLE
                | CHAR
                | VOID'''
        p[0] = p[1]

    # --- Regla vacía -------------------------------------------------
    def p_empty(self, p):
        'empty :'
        p[0] = None

    # --- Manejo de errores ------------------------------------------
    def p_error(self, p):
        msg = f"Error sintáctico en token '{p.value}' línea {p.lineno}" if p else "Error sintáctico: fin de archivo inesperado"
        print(msg)
        self.errors.append(msg)
        if p:
            self.parser.errok()

    # --- API pública -------------------------------------------------
    def parse(self, source):
        self.errors = []
        return self.parser.parse(source, lexer=self.lexer.lexer, debug=False)

    def has_errors(self):
        return bool(self.errors)
