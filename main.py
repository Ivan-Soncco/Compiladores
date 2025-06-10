# main.py

from src.calculator import CodeAnalyzer
from tabulate import tabulate

def run_cli():

    print("--- Analizador de Código por Línea ---")

    cpp_file_path = 'archivo_cpp.txt'
    python_file_path = 'archivo_python.txt'

    print("\nAnalizando archivo C++...")
    analyzer_cpp = CodeAnalyzer(lang_type="cpp")
    cpp_analysis_results = analyzer_cpp.analyze_file_by_line(cpp_file_path)

    if cpp_analysis_results:
        table_headers = ["Línea de Código", "Tipo de Token Semántico", "Descripción"]
        table_data = []
        for line_content, sem_type, sem_desc in cpp_analysis_results:
            table_data.append([line_content, sem_type, sem_desc])

        print(f"\n--- Resultados del Análisis (C++: {cpp_file_path}) ---")
        print(tabulate(table_data, headers=table_headers, tablefmt="grid"))
        print("---------------------------------------------------\n")
    else:
        print("No se pudo analizar el archivo C++.")


    # --- Análisis de Python ---
    print("\nAnalizando archivo Python...")
    analyzer_python = CodeAnalyzer(lang_type="python")
    python_analysis_results = analyzer_python.analyze_file_by_line(python_file_path)

    if python_analysis_results:
        table_headers = ["Línea de Código", "Tipo de Token Semántico", "Descripción"]
        table_data = []
        for line_content, sem_type, sem_desc in python_analysis_results:
            table_data.append([line_content, sem_type, sem_desc])

        print(f"\n--- Resultados del Análisis (Python: {python_file_path}) ---")
        print(tabulate(table_data, headers=table_headers, tablefmt="grid"))
        print("-----------------------------------------------------\n")
    else:
        print("No se pudo analizar el archivo Python.")


if __name__ == '__main__':
    run_cli()