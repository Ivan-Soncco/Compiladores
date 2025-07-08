# analyzer/language_analyzer.py

import ply.lex as lex
from . import lexer_rules

class LanguageAnalyzer:
    def __init__(self):
        self.lexer = lex.lex(module=lexer_rules)
        self.tokens_list = []

    def tokenize(self, source_code):
        self.tokens_list = []
        self.lexer.input(source_code)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            self.tokens_list.append(tok)
        return self.tokens_list

    def print_lexer_output(self):
        print("\n" + "="*80)
        print("LEXER OUTPUT")
        print("="*80)
        print(f"{'TOKEN TYPE':<20} {'VALUE':<20} {'CATEGORY':<20}")
        print("-"*80)
        for token in self.tokens_list:
            category = self.get_token_category(token.type)
            print(f"{token.type:<20} {str(token.value):<20} {category:<20}")

    def get_token_category(self, token_type):
        if token_type in lexer_rules.common_tokens:
            return "COMMON"
        elif token_type in lexer_rules.python_tokens:
            return "PYTHON"
        elif token_type in lexer_rules.cpp_tokens:
            return "C++"
        elif token_type in lexer_rules.java_tokens:
            return "JAVA"
        else:
            return "LITERAL"

    def detect_language(self):
        if not self.tokens_list:
            return "No se pudieron detectar tokens"
        
        token_types = [tok.type for tok in self.tokens_list]
        common_detected = any(t in lexer_rules.common_tokens for t in token_types)
        cpp_detected = any(t in lexer_rules.cpp_tokens for t in token_types)
        py_detected = any(t in lexer_rules.python_tokens for t in token_types)
        java_detected = any(t in lexer_rules.java_tokens for t in token_types)
        class_detected = any(t in ['CLASS', 'PYTHON_CLASS'] for t in token_types)

        if cpp_detected:
            return "C++"
        elif py_detected:
            return "Python"
        elif java_detected:
            return "Java"
        elif common_detected and class_detected:
            return "C++ and Java"
        elif common_detected:
            return "C++, Java and Python"
        else:
            return "Unable to detect the Language"
