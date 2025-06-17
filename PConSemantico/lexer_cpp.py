# lexer_cpp.py

import ply.lex as lex

class CPPLexer:
    """
    Analizador léxico simplificado para C++ básico
    """
    
    # Palabras reservadas
    reserved = {
        'int': 'INT',
        'float': 'FLOAT', 
        'char': 'CHAR',
        'void': 'VOID',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'return': 'RETURN',
        'include': 'INCLUDE',
        'main': 'MAIN',
        'cout': 'COUT',
        'cin': 'CIN',
        'endl': 'ENDL'
    }
    
    # Lista de tokens
    tokens = [
        'ID', 'NUMBER', 'STRING',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'ASSIGN', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'SEMICOLON', 'COMMA',
        'LSHIFT', 'RSHIFT',  # << >>
        'HASH',  # #
        'LANGLE', 'RANGLE',  # < > para #include
    ] + list(reserved.values())
    
    # Reglas de tokens
    t_PLUS     = r'\+'
    t_MINUS    = r'-'
    t_TIMES    = r'\*'
    t_DIVIDE   = r'/'
    t_ASSIGN   = r'='
    t_EQ       = r'=='
    t_NE       = r'!='
    t_LT       = r'<'
    t_GT       = r'>'
    t_LE       = r'<='
    t_GE       = r'>='
    t_LPAREN   = r'\('
    t_RPAREN   = r'\)'
    t_LBRACE   = r'\{'
    t_RBRACE   = r'\}'
    t_SEMICOLON = r';'
    t_COMMA    = r','
    t_LSHIFT   = r'<<'
    t_RSHIFT   = r'>>'
    t_HASH     = r'\#'
    t_LANGLE   = r'<'
    t_RANGLE   = r'>'
    
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t
    
    def t_STRING(self, t):
        r'"([^"\\]|\\.)*"'
        t.value = t.value[1:-1]  # Remover comillas
        return t
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t
    
    def t_COMMENT(self, t):
        r'//.*'
        pass  # Ignorar comentarios
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    t_ignore = ' \t'
    
    def t_error(self, t):
        print(f"Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
        t.lexer.skip(1)
    
    def __init__(self):
        self.lexer = lex.lex(module=self)
    
    def tokenize(self, data):
        self.lexer.input(data)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens