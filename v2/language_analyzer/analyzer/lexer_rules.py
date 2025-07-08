# analyzer/lexer_rules.py

# TOKENS
common_tokens = [
    'FUNCTION_CALL', 'FUNCTIONDEF', 'FUNCTION_DECL', 'VAR_DECL',
    'ASSIGN', 'RETURN', 'CALCULATIONS', 'IDENTIFIERS',
    'BRANCH', 'FOR_LOOP', 'WHILE_LOOP', 'ACCESS_SPECIFIERS', 'CLASS'
]

python_tokens = [
    'PYTHON_DEF', 'PYTHON', 'PYTHON_CLASS'
]

cpp_tokens = [
    'CPP', 'CPP_INCLUDE', 'CPPPRINT'
]

java_tokens = [
    'JAVA'
]

tokens = common_tokens + python_tokens + cpp_tokens + java_tokens + [
    'NUMBER', 'STRING', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET', 'SEMICOLON', 'COMMA', 'DOT',
    'COLON', 'LT', 'GT', 'NEWLINE'
]

# LITERALES
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r':'
t_LT = r'<'
t_GT = r'>'
t_ignore = ' \t'

# PALABRAS RESERVADAS
reserved_common = {
    'if': 'BRANCH', 'else': 'BRANCH', 'goto': 'BRANCH',
    'for': 'FOR_LOOP', 'while': 'WHILE_LOOP', 'return': 'RETURN',
    'public': 'ACCESS_SPECIFIERS', 'private': 'ACCESS_SPECIFIERS', 'protected': 'ACCESS_SPECIFIERS',
    'class': 'CLASS', 'function': 'FUNCTIONDEF'
}

reserved_python = {
    'def': 'PYTHON_DEF', 'import': 'PYTHON', 'from': 'PYTHON', 'as': 'PYTHON',
    'with': 'PYTHON', 'lambda': 'PYTHON', 'yield': 'PYTHON',
    'global': 'PYTHON', 'nonlocal': 'PYTHON', 'pass': 'PYTHON',
    'in': 'PYTHON', 'is': 'PYTHON', 'not': 'PYTHON', 'and': 'PYTHON', 'or': 'PYTHON'
}

reserved_cpp = {
    'namespace': 'CPP', 'using': 'CPP', 'template': 'CPP', 'typename': 'CPP',
    'const': 'CPP', 'static': 'CPP', 'virtual': 'CPP', 'override': 'CPP',
    'this': 'CPP', 'new': 'CPP', 'delete': 'CPP', 'cout': 'CPPPRINT',
    'cin': 'CPPPRINT', 'endl': 'CPPPRINT', 'std': 'CPP'
}

reserved_java = {
    'finally': 'JAVA', 'this': 'JAVA', 'super': 'JAVA', 'extends': 'JAVA',
    'implements': 'JAVA', 'interface': 'JAVA', 'package': 'JAVA',
    'throws': 'JAVA', 'synchronized': 'JAVA', 'final': 'JAVA',
    'abstract': 'JAVA', 'static': 'JAVA', 'try': 'JAVA', 'catch': 'JAVA'
}

reserved = {**reserved_common, **reserved_python, **reserved_cpp, **reserved_java}

# FUNCIONES DEL LEXER
def t_CPP_INCLUDE(t):
    r'\#include\s*<[^>]+>|\#include\s*"[^"]+"'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    return t

def t_CLASS_KEYWORD(t):
    r'class'
    t.type = 'CLASS'
    return t

def t_FUNCTION_CALL(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*\s*\('
    t.value = t.value.rstrip().rstrip('(')
    t.type = reserved.get(t.value, 'FUNCTION_CALL')
    return t

def t_IDENTIFIERS(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == 'class':
        t.type = 'CLASS'
    else:
        t.type = reserved.get(t.value, 'IDENTIFIERS')
    return t

def t_ASSIGN(t):
    r'='
    return t

def t_CALCULATIONS(t):
    r'[+\-*/]'
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)
