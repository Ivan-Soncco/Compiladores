import ply.lex as lex
import re

class CPPLexer:
    # ---------- PALABRAS RESERVADAS ----------
    reserved = {
        'int':    'INT',
        'float':  'FLOAT',
        'double': 'DOUBLE',
        'char':   'CHAR',
        'void':   'VOID',

        'if':     'IF',
        'else':   'ELSE',
        'while':  'WHILE',
        'for':    'FOR',
        'return': 'RETURN',

        'cin':    'CIN',
        'cout':   'COUT',

        'true':   'TRUE',
        'false':  'FALSE',
    }

    # ---------- LISTA DE TOKENS ----------
    tokens = [
        # Identificadores y literales
        'ID', 'NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'CHAR_LITERAL',
        # Operadores
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'ASSIGN',
        'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',
        'AND', 'OR', 'NOT',
        'SHIFT_IN',   # >>
        'SHIFT_OUT',  # <<
        # Delimitadores
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA',
    ] + list(reserved.values())

    # ---------- CONSTRUCTOR ----------
    def __init__(self):
        self.lexer = lex.lex(module=self)

    # ---------- LITERALES NUMÉRICOS ----------
    def t_FLOAT_NUM(self, t):
        r"\d+\.\d+([eE][+-]?\d+)?([fF])?"
        t.value = float(t.value.rstrip('fF'))
        return t

    def t_NUMBER(self, t):
        r"0[xX][0-9a-fA-F]+|0[0-7]+|\d+"
        t.value = int(t.value, 0)
        return t

    def t_STRING_LITERAL(self, t):
        r'"([^"\\]|\\.)*"'
        t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
        return t

    def t_CHAR_LITERAL(self, t):
        r"'([^'\\]|\\.)'"
        t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
        return t

    # ---------- OPERADORES (multicaracter primero) ----------
    t_SHIFT_IN  = r'>>'
    t_SHIFT_OUT = r'<<'
    t_EQ        = r'=='
    t_NE        = r'!='
    t_LE        = r'<='
    t_GE        = r'>='
    t_AND       = r'&&'
    t_OR        = r'\|\|'

    # ---------- OPERADORES simples ----------
    t_PLUS   = r'\+'
    t_MINUS  = r'-'
    t_TIMES  = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_ASSIGN = r'='
    t_LT     = r'<'
    t_GT     = r'>'
    t_NOT    = r'!'

    # ---------- DELIMITADORES ----------
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACE    = r'\{'
    t_RBRACE    = r'\}'
    t_SEMICOLON = r';'
    t_COMMA     = r','

    # ---------- IDENTIFICADORES / RESERVADAS ----------
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    # ---------- COMENTARIOS ----------
    def t_COMMENT_MULTI(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    def t_COMMENT_SINGLE(self, t):
        r'//.*'

    # ---------- CONTADOR DE LÍNEAS ----------
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # ---------- CARACTERES A IGNORAR ----------
    t_ignore = ' \t\r'

    # ---------- MANEJO DE ERRORES ----------
    def t_error(self, t):
        print(f"Carácter ilegal {t.value[0]!r} en línea {t.lineno}")
        t.lexer.skip(1)

    # ---------- UTILIDADES ----------
    def tokenize(self, source):
        self.lexer.input(source)
        return list(iter(self.lexer.token, None))