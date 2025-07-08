# src/calculator.py

from src.lexer_cpp import CPPLexer
from src.lexer_python import PythonLexer
from src.analyzer import LineAnalyzer
# from src.parser import CalcParser # Puedes mantenerlo si quieres la funcionalidad de parsing formal

class CodeAnalyzer:
    """
    Clase principal que integra los lexers y el analizador de líneas.
    """
    def __init__(self, lang_type="cpp"):
        self.lang_type = lang_type
        if lang_type == "cpp":
            self.lexer = CPPLexer()
        elif lang_type == "python":
            self.lexer = PythonLexer()
        else:
            raise ValueError(f"Tipo de lenguaje no soportado: {lang_type}")

        self.line_analyzer = LineAnalyzer(lang_type=lang_type)
        # self.parser = CalcParser() # Si vas a usar el parser, inicialízalo aquí

    def analyze_file_by_line(self, file_path):
        """
        Lee el contenido de un archivo línea por línea, lo tokeniza
        y luego clasifica cada línea en un token semántico de alto nivel.
        Retorna una lista de tuplas (line_content, semantic_token_type, semantic_token_desc).
        """
        results = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print(f"\n--- Analizando el archivo '{file_path}' ({self.lang_type}) ---\n")
            print("Contenido del archivo:\n")
            print("".join(lines))
            print("\n----------------------------------------------------\n")

            for i, line_content in enumerate(lines):
                # Eliminar espacios al inicio/final para una mejor clasificación de línea vacía
                stripped_line = line_content.strip()
                if not stripped_line or stripped_line.startswith('//') or stripped_line.startswith('#'):
                    # Manejar líneas vacías o de comentario directamente para evitar tokens léxicos
                    if not stripped_line:
                        results.append((line_content.strip(), "EMPTY_LINE", self.line_analyzer.COMMON_TOKENS_MAP["EMPTY_LINE"]))
                    elif stripped_line.startswith('//') or stripped_line.startswith('#'):
                         results.append((line_content.strip(), "COMMENT", self.line_analyzer.COMMON_TOKENS_MAP["COMMENT"]))
                    continue # No tokenizar si es comentario o vacío

                # Tokenizar la línea individualmente
                tokens_in_line = self.lexer.tokenize(line_content)
                semantic_type, semantic_desc = self.line_analyzer.analyze_line_tokens(tokens_in_line)
                results.append((line_content.strip(), semantic_type, semantic_desc))

        except FileNotFoundError:
            print(f"Error: El archivo '{file_path}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al leer o analizar el archivo: {e}")

        return results