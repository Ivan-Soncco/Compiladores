# src/analyzer.py

class LineAnalyzer:
    COMMON_TOKENS_MAP = {
        'FUNCTION_CALL': 'Llamada a Función',
        'FUNCTION_DEF': 'Definición de Función',
        'FUNCTION_DECL': 'Declaración de Función',
        'VAR_DECL': 'Declaración de Variable',
        'ASSIGN': 'Asignación de Variable',
        'RETURN': 'Sentencia de Retorno',
        'CALCULATIONS': 'Cálculo/Expresión',
        'IDENTIFIERS': 'Uso de Identificador',
        'BRANCH': 'Sentencia Condicional (if/else)',
        'FOR_LOOP': 'Bucle For',
        'WHILE_LOOP': 'Bucle While',
        'ACCESS_SPECIFIERS': 'Especificador de Acceso',
        'CLASS_DEF': 'Definición de Clase',
        'INCLUDE_DIRECTIVE': 'Directiva de Inclusión',
        'USING_NAMESPACE': 'Uso de Namespace',
        'PRINT_STMT': 'Sentencia de Impresión',
        'INPUT_STMT': 'Sentencia de Entrada',
        'COMMENT': 'Comentario',
        'EMPTY_LINE': 'Línea Vacía/Ignorada',
        'UNKNOWN': 'Desconocido',
    }

    def __init__(self, lang_type="cpp"):
        self.lang_type = lang_type

    def analyze_line_tokens(self, tokens_in_line):
        if not tokens_in_line:
            return "EMPTY_LINE", self.COMMON_TOKENS_MAP["EMPTY_LINE"]

        token_types = [t.type for t in tokens_in_line]
        token_values = [t.value for t in tokens_in_line]

        if self.lang_type == "cpp":
            if 'HASH' in token_types and 'INCLUDE' in token_types:
                return "INCLUDE_DIRECTIVE", self.COMMON_TOKENS_MAP["INCLUDE_DIRECTIVE"]
            if 'USING' in token_types and 'NAMESPACE' in token_types:
                return "USING_NAMESPACE", self.COMMON_TOKENS_MAP["USING_NAMESPACE"]
            if 'INT' in token_types and 'MAIN' in token_types and 'LPAREN' in token_types and 'RPAREN' in token_types:
                return "FUNCTION_DEF", self.COMMON_TOKENS_MAP["FUNCTION_DEF"]
            if 'RETURN' in token_types:
                return "RETURN", self.COMMON_TOKENS_MAP["RETURN"]
            if 'COUT' in token_types and 'LSHIFT' in token_types:
                return "PRINT_STMT", self.COMMON_TOKENS_MAP["PRINT_STMT"]
            if 'CIN' in token_types and 'RSHIFT' in token_types:
                return "INPUT_STMT", self.COMMON_TOKENS_MAP["INPUT_STMT"]
            if 'ID' in token_types and any(kw in ['INT', 'FLOAT', 'DOUBLE', 'CHAR', 'BOOL', 'VOID'] for kw in token_types):
                if 'ASSIGN' in token_types or 'AMPERSAND_OP' in token_types or 'ASTERISK_OP' in token_types:
                     return "VAR_DECL", self.COMMON_TOKENS_MAP["VAR_DECL"]
                return "VAR_DECL", self.COMMON_TOKENS_MAP["VAR_DECL"]
            if 'ID' in token_types and 'LPAREN' in token_types and token_types[0] == 'ID':
                if any(t.type in ['TIMES', 'DIVIDE', 'PLUS', 'MINUS', 'MODULO'] for t in tokens_in_line):
                    return "CALCULATIONS", self.COMMON_TOKENS_MAP["CALCULATIONS"]
                return "FUNCTION_CALL", self.COMMON_TOKENS_MAP["FUNCTION_CALL"]
            if 'IF' in token_types or 'ELSE' in token_types or 'SWITCH' in token_types:
                return "BRANCH", self.COMMON_TOKENS_MAP["BRANCH"]
            if 'FOR' in token_types:
                return "FOR_LOOP", self.COMMON_TOKENS_MAP["FOR_LOOP"]
            if 'WHILE' in token_types:
                return "WHILE_LOOP", self.COMMON_TOKENS_MAP["WHILE_LOOP"]
            if any(kw in ['PUBLIC', 'PRIVATE', 'PROTECTED'] for kw in token_types):
                return "ACCESS_SPECIFIERS", self.COMMON_TOKENS_MAP["ACCESS_SPECIFIERS"]
            if 'CLASS' in token_types and 'ID' in token_types:
                return "CLASS_DEF", self.COMMON_TOKENS_MAP["CLASS_DEF"]
            if 'COMMENT_SINGLE' in token_types or 'COMMENT_MULTI' in token_types:
                return "COMMENT", self.COMMON_TOKENS_MAP["COMMENT"]

        elif self.lang_type == "python":
            # Si el token PRINT o INPUT fue reconocido
            if 'PRINT' in token_types:
                return "PRINT_STMT", self.COMMON_TOKENS_MAP["PRINT_STMT"]
            if 'INPUT' in token_types:
                return "INPUT_STMT", self.COMMON_TOKENS_MAP["INPUT_STMT"]
            if 'DEF' in token_types and 'ID' in token_types and 'LPAREN' in token_types:
                return "FUNCTION_DEF", self.COMMON_TOKENS_MAP["FUNCTION_DEF"]
            if 'CLASS' in token_types and 'ID' in token_types:
                return "CLASS_DEF", self.COMMON_TOKENS_MAP["CLASS_DEF"]
            if 'RETURN' in token_types:
                return "RETURN", self.COMMON_TOKENS_MAP["RETURN"]
            if 'IF' in token_types or 'ELIF' in token_types or 'ELSE' in token_types:
                return "BRANCH", self.COMMON_TOKENS_MAP["BRANCH"]
            if 'FOR' in token_types:
                return "FOR_LOOP", self.COMMON_TOKENS_MAP["FOR_LOOP"]
            if 'WHILE' in token_types:
                return "WHILE_LOOP", self.COMMON_TOKENS_MAP["WHILE_LOOP"]
            if 'ID' in token_types and 'ASSIGN' in token_types:
                return "ASSIGN", self.COMMON_TOKENS_MAP["ASSIGN"]
            if 'COMMENT' in token_types:
                return "COMMENT", self.COMMON_TOKENS_MAP["COMMENT"]
            # Heurística para llamadas o expresiones simples
            if 'LPAREN' in token_types and 'ID' in token_types:
                 return "FUNCTION_CALL", self.COMMON_TOKENS_MAP["FUNCTION_CALL"]
            if any(op in token_types for op in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'FLOOR_DIVIDE', 'EXPONENT']):
                 return "CALCULATIONS", self.COMMON_TOKENS_MAP["CALCULATIONS"]


        # Regla de asignación genérica (después de las específicas de var_decl)
        if 'ID' in token_types and 'ASSIGN' in token_types:
            return "ASSIGN", self.COMMON_TOKENS_MAP["ASSIGN"]

        # Si solo hay IDs, es un uso simple
        if all(t.type == 'ID' for t in tokens_in_line):
            return "IDENTIFIERS", self.COMMON_TOKENS_MAP["IDENTIFIERS"]

        return "UNKNOWN", self.COMMON_TOKENS_MAP["UNKNOWN"]