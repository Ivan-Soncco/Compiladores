# src/lexer_base.py

import ply.lex as lex

class BaseLexer:
    tokens = (
        'ID', 'NUMBER', 'STRING_LITERAL', 'CHAR_LITERAL',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'ASSIGN',
        'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
        'AND', 'OR', 'NOT',
        'INC', 'DEC',
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'LBRACE', 'RBRACE',
        'SEMICOLON', 'COMMA', 'DOT', 'COLON', 'QUESTION',
    )

    t_PLUS          = r'\+'
    t_MINUS         = r'-'
    t_TIMES         = r'\*'
    t_DIVIDE        = r'/'
    t_MODULO        = r'%'
    t_ASSIGN        = r'='
    t_EQ            = r'=='
    t_NE            = r'!='
    t_LT            = r'<'
    t_LE            = r'<='
    t_GT            = r'>'
    t_GE            = r'>='
    t_AND           = r'&&'
    t_OR            = r'\|\|'
    t_NOT           = r'!'
    t_INC           = r'\+\+'
    t_DEC           = r'--'
    t_LPAREN        = r'\('
    t_RPAREN        = r'\)'
    t_LBRACKET      = r'\['
    t_RBRACKET      = r'\]'
    t_LBRACE        = r'\{'
    t_RBRACE        = r'\}'
    t_SEMICOLON     = r';'
    t_COMMA         = r','
    t_DOT           = r'\.'
    t_COLON         = r':'
    t_QUESTION      = r'\?'

    def t_NUMBER(self, t):
        r'\d+\.\d*([eE][-+]?\d+)?|\d+'
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_STRING_LITERAL(self, t):
        r'"([^"\\]|\\.)*"'
        t.value = t.value[1:-1]
        return t

    def t_CHAR_LITERAL(self, t):
        r"'([^'\\]|\\.)'"
        t.value = t.value[1:-1]
        return t

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"[{t.lexer.lineno}:{t.lexer.lexpos}] Carácter ilegal (BaseLexer): '{t.value[0]}'")
        t.lexer.skip(1)

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def tokenize(self, data):
        self.lexer.input(data)
        tokens_list = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens_list.append(tok)
        return tokens_list