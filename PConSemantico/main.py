# main.py

from lexer_cpp import CPPLexer
from parser_cpp import CPPParser
from semantic_analyzer import SemanticAnalyzer
from semantic_line_analyzer import SemanticLineAnalyzer

def print_ast(node, indent=0):
    """Imprime el AST de forma legible"""
    if node is None:
        return
    
    print("  " * indent + f"{node.type}: {node.value}")
    for child in node.children:
        print_ast(child, indent + 1)

def analyze_code(code):
    """Analiza código C++ completo"""
    print("=" * 60)
    print("ANALIZADOR COMPLETO DE C++")
    print("=" * 60)
    
    print("\n1. CÓDIGO A ANALIZAR:")
    print("-" * 30)
    lines = code.strip().split('\n')
    for i, line in enumerate(lines, 1):
        print(f"{i:2d}: {line}")
    
    # Análisis Léxico
    print("\n2. ANÁLISIS LÉXICO:")
    print("-" * 30)
    lexer = CPPLexer()
    tokens = lexer.tokenize(code)
    
    for token in tokens:
        print(f"Token: {token.type:12} | Valor: {token.value}")
    
    # Análisis Sintáctico
    print("\n3. ANÁLISIS SINTÁCTICO:")
    print("-" * 30)
    parser = CPPParser()
    ast = parser.parse(code)
    
    if ast:
        print("✓ Análisis sintáctico exitoso")
        print("\nÁrbol de Sintaxis Abstracta (AST):")
        print_ast(ast)
    else:
        print("✗ Error en análisis sintáctico")
        return
    
    # Análisis Semántico
    print("\n4. ANÁLISIS SEMÁNTICO:")
    print("-" * 30)
    semantic_analyzer = SemanticAnalyzer()
    is_valid, errors = semantic_analyzer.analyze(ast)
    
    if is_valid:
        print("✓ Análisis semántico exitoso")
        print("El código es semánticamente correcto")
    else:
        print("✗ Errores semánticos encontrados:")
        for error in errors:
            print(f"  - {error}")
    
    # Análisis Semántico por Líneas
    line_analyzer = SemanticLineAnalyzer()
    line_classifications = line_analyzer.analyze_lines(code, ast)
    line_analyzer.print_semantic_table()
    
    # Estadísticas
    stats = line_analyzer.get_semantic_statistics()
    print(f"\nESTADÍSTICAS:")
    print(f"- Total de líneas analizadas: {stats['total_lines']}")
    print(f"- Líneas clasificadas: {stats['classified_lines']}")
    print(f"- Líneas sin clasificar: {stats['unclassified_lines']}")
    print(f"- Porcentaje de clasificación: {(stats['classified_lines']/stats['total_lines']*100):.1f}%")
    
    print("\n" + "=" * 60)

def main():
    # Código C++ de ejemplo más complejo
    complex_code = '''
    #include <iostream>
    
    int main() {
        int x;
        int y = 10;
        x = 5;
        int sum = x + y;
        
        if (sum > 10) {
            cout << "Sum is greater than 10" << endl;
        } else {
            cout << "Sum is not greater than 10" << endl;
        }
        
        int i = 0;
        while (i < 3) {
            cout << i << endl;
            i = i + 1;
        }
        
        for (int j = 0; j < 5; j = j + 1) {
            cout << "Loop iteration: " << j << endl;
        }
        
        return 0;
    }
    '''
    
    # Código C++ de ejemplo con errores
    error_code = '''
    int main() {
        int x = 5;
        y = x + 3;
        void z;
        
        if (x > 2) {
            cout << "x is greater than 2" << endl;
        }
        
        return "hello";
    }
    '''
    
    print("EJEMPLO 1: Código complejo válido")
    analyze_code(complex_code)
    
    print("\n\nEJEMPLO 2: Código con errores")
    analyze_code(error_code)

if __name__ == "__main__":
    main()