# src/lexer_python.py

import ply.lex as lex
from src.lexer_base import BaseLexer

class PythonLexer(BaseLexer):
    """
    Extiende BaseLexer para incluir tokens específicos de Python.
    """
    # *** La línea crucial: Combina explícitamente los tokens base con los nuevos. ***
    tokens = BaseLexer.tokens + (
        # Palabras clave Python
        'DEF', 'CLASS', 'IMPORT', 'FROM', 'AS', 'NONE', 'TRUE', 'FALSE',
        'AND_PY', 'OR_PY', 'NOT_PY', # Operadores lógicos de Python (palabras)
        'IN', 'IS', 'ELIF', 'PASS', 'BREAK_PY', 'CONTINUE_PY',
        'GLOBAL', 'NONLOCAL', 'YIELD', 'ASYNC', 'AWAIT', 'WITH', 'LAMBDA',
        'FINALLY', 'EXCEPT', 'RAISE', 'ASSERT',
        'PRINT', 'INPUT', # Aseguramos que 'PRINT' y 'INPUT' estén en la lista de tokens

        # Operadores Python específicos
        'FLOOR_DIVIDE', # //
        'EXPONENT',     # **
        'AT',           # @ (decoradores)

        # Otros símbolos específicos de Python
        'NEWLINE',      # Nueva línea (importante para indentación)
        'COMMENT',      # Comentarios de Python
    )

    # Palabras clave reservadas de Python
    reserved_keywords = {
        'def': 'DEF', 'class': 'CLASS', 'import': 'IMPORT', 'from': 'FROM', 'as': 'AS',
        'None': 'NONE', 'True': 'TRUE', 'False': 'FALSE',
        'and': 'AND_PY', 'or': 'OR_PY', 'not': 'NOT_PY',
        'in': 'IN', 'is': 'IS', 'elif': 'ELIF', 'pass': 'PASS',
        'break': 'BREAK_PY', 'continue': 'CONTINUE_PY',
        'global': 'GLOBAL', 'nonlocal': 'NONLOCAL', 'yield': 'YIELD',
        'async': 'ASYNC', 'await': 'AWAIT', 'with': 'WITH', 'lambda': 'LAMBDA',
        'finally': 'FINALLY', 'except': 'EXCEPT', 'raise': 'RAISE', 'assert': 'ASSERT',
        'return': 'RETURN',
        'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
        'print': 'PRINT', # Añadimos print como palabra clave si queremos un token específico
        'input': 'INPUT' # Añadimos input como palabra clave
    }

    # Reglas para tokens heredados (no las re-declaramos si ya están en BaseLexer)
    # Reglas específicas de Python
    t_FLOOR_DIVIDE  = r'//'
    t_EXPONENT      = r'\*\*'
    t_AT            = r'@'

    def t_COMMENT(self, t):
        r'\#.*'
        pass

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    # Sobrescribir t_ID para usar las palabras clave de Python
    # Esta regla debe venir después de las reglas para operadores y palabras clave específicas.
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # La clave está en que 'IF' u otros tipos que t_ID va a producir,
        # DEBEN estar en la tupla `tokens` definida arriba en esta clase.
        t.type = self.reserved_keywords.get(t.value, 'ID')
        return t

    t_ignore = ' \t'

    def t_error(self, t):
        print(f"[{t.lexer.lineno}:{t.lexer.lexpos}] Carácter ilegal (PythonLexer): '{t.value[0]}'")
        t.lexer.skip(1)

    def __init__(self):
        # Cuando se construye el lexer, PLY buscará la tupla 'tokens' en 'self'.
        # Por lo tanto, `BaseLexer.tokens` ya debe haber sido combinado correctamente
        # con los tokens de PythonLexer en la definición de `tokens` de PythonLexer.
        self.lexer = lex.lex(module=self)