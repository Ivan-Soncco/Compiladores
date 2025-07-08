import sys
from analyzer.language_analyzer import LanguageAnalyzer

def analyze_file(filename):
    analyzer = LanguageAnalyzer()
    print(f"\n{'='*80}")
    print(f"ANALIZANDO ARCHIVO: {filename}")
    print('='*80)

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            source_code = file.read().strip()

        if not source_code:
            print("Error: El archivo está vacío")
            return

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {filename}")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    tokens = analyzer.tokenize(source_code)
    print("\nCÓDIGO FUENTE:")
    print("-" * 60)
    print(source_code)
    print("-" * 60)

    analyzer.print_lexer_output()
    detected_language = analyzer.detect_language()

    print("\n" + "="*80)
    print("RESULTADO DE DETECCIÓN")
    print("="*80)
    print(f"LENGUAJE DETECTADO: {detected_language}")
    print("="*80)

def main():
    print("="*80)
    print("ANALIZADOR DE LENGUAJES DE PROGRAMACIÓN")
    print("Soporta detección de: C++, Python, Java")
    print("="*80)

    if len(sys.argv) < 2:
        print("\nUso: python main.py <archivo1> <archivo2> ...")
        return

    for filename in sys.argv[1:]:
        analyze_file(filename)

if __name__ == "__main__":
    main()
