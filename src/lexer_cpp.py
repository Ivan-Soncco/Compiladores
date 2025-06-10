# src/lexer_cpp.py

import ply.lex as lex
from src.lexer_base import BaseLexer

class CPPLexer(BaseLexer):
    """
    Extiende BaseLexer para incluir tokens específicos de C++.
    """
    # Definición explícita de TODOS los tokens para este lexer.
    # Combinamos los de la base con los específicos de C++.
    tokens = BaseLexer.tokens + (
        # Palabras clave C++
        'INCLUDE', 'USING', 'NAMESPACE', 'STD', 'INT', 'MAIN', 'COUT', 'CIN', 'ENDL', 'RETURN',
        'IF', 'ELSE', 'WHILE', 'FOR', 'DO', 'SWITCH', 'CASE', 'BREAK', 'CONTINUE', 'VOID',
        'FLOAT', 'DOUBLE', 'CHAR', 'BOOL', 'STRUCT', 'CLASS', 'TYPEDEF', 'CONST', 'STATIC',
        'PRIVATE', 'PUBLIC', 'PROTECTED', 'THIS', 'NEW', 'DELETE', 'VIRTUAL', 'OVERRIDE',
        'FINAL', 'TEMPLATE', 'TYPENAME', 'SIZEOF',

        # Operadores C++ específicos
        'ARROW',        # -> (para punteros a miembros)
        'COLON_COLON',  # :: (operador de ámbito)
        'AMPERSAND_OP', # & (operador de dirección de) - renombro para evitar colisión con AND
        'ASTERISK_OP',  # * (operador de desreferencia) - renombro para claridad
        'LSHIFT', 'RSHIFT', # << >> (stream operators)

        # Preprocesador y delimitadores angulares
        'HASH',         # #
        'LANGLE', 'RANGLE', # < > (para includes, templates)

        # Comentarios
        'COMMENT_SINGLE', 'COMMENT_MULTI',
    )

    # Palabras clave reservadas de C++
    reserved_keywords = {
        '#include': 'INCLUDE',
        'using': 'USING', 'namespace': 'NAMESPACE', 'std': 'STD',
        'int': 'INT', 'main': 'MAIN', 'cout': 'COUT', 'cin': 'CIN', 'endl': 'ENDL',
        'return': 'RETURN', 'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
        'do': 'DO', 'switch': 'SWITCH', 'case': 'CASE', 'break': 'BREAK', 'continue': 'CONTINUE',
        'void': 'VOID', 'float': 'FLOAT', 'double': 'DOUBLE', 'char': 'CHAR', 'bool': 'BOOL',
        'struct': 'STRUCT', 'class': 'CLASS', 'typedef': 'TYPEDEF', 'const': 'CONST', 'static': 'STATIC',
        'private': 'PRIVATE', 'public': 'PUBLIC', 'protected': 'PROTECTED', 'this': 'THIS',
        'new': 'NEW', 'delete': 'DELETE', 'virtual': 'VIRTUAL', 'override': 'OVERRIDE',
        'final': 'FINAL', 'template': 'TEMPLATE', 'typename': 'TYPENAME', 'sizeof': 'SIZEOF',
    }

    # Reglas específicas de C++ (que no están en BaseLexer o tienen una prioridad especial)
    t_ARROW         = r'->'
    t_COLON_COLON   = r'::'
    t_AMPERSAND_OP  = r'&' # Renombrado
    t_ASTERISK_OP   = r'\*' # Renombrado (para desreferencia, o sigue siendo TIMES si no se usa para desref)
                            # Nota: PLY preferirá la regla más larga. Si tienes `t_TIMES = r'\*'` en BaseLexer
                            # y `t_ASTERISK_OP = r'\*'` aquí, la que esté definida en la clase más específica o
                            # la que sea un método tendrá prioridad. Para `*`, a menudo se deja como `TIMES` y el
                            # parser distingue si es multiplicación o desreferencia.
    t_LSHIFT        = r'<<'
    t_RSHIFT        = r'>>'
    t_HASH          = r'\#'
    t_LANGLE        = r'<'
    t_RANGLE        = r'>'

    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        pass

    def t_COMMENT_MULTI(self, t):
        r'/\*[\s\S]*?\*/'
        t.lexer.lineno += t.value.count('\n')
        pass

    # Sobrescribir t_ID para usar las palabras clave de C++
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved_keywords.get(t.value, 'ID')
        return t

    def t_error(self, t):
        print(f"[{t.lexer.lineno}:{t.lexer.lexpos}] Carácter ilegal (CPPLexer): '{t.value[0]}'")
        t.lexer.skip(1)

    def __init__(self):
        # Asegúrate de que el lexer se construya con las reglas de ESTA clase (CPPLexer).
        self.lexer = lex.lex(module=self)