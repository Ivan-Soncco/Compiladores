# semantic_line_analyzer.py

class SemanticLineAnalyzer:
    """
    Analizador que identifica el tipo semántico de cada línea de código
    """
    
    def __init__(self):
        self.line_classifications = []
        self.source_lines = []
        
    def analyze_lines(self, source_code, ast):
        """
        Analiza cada línea del código fuente y la clasifica semánticamente
        """
        self.source_lines = source_code.strip().split('\n')
        self.line_classifications = []
        
        # Inicializar todas las líneas como desconocidas
        for i, line in enumerate(self.source_lines, 1):
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith('//'):
                self.line_classifications.append({
                    'line_number': i,
                    'line_content': stripped_line,
                    'semantic_type': 'UNKNOWN',
                    'description': 'Unknown'
                })
        
        # Analizar el AST y clasificar las líneas
        self._analyze_ast_node(ast)
        
        return self.line_classifications
    
    def _analyze_ast_node(self, node, context=None):
        """
        Analiza recursivamente los nodos del AST
        """
        if node is None:
            return
            
        # Clasificar según el tipo de nodo
        if node.type == 'PROGRAM':
            for child in node.children:
                self._analyze_ast_node(child)
                
        elif node.type == 'INCLUDE':
            self._classify_line_by_content('#include', 'PREPROCESSING', 'Preprocessor Directive')
            
        elif node.type == 'FUNCTION_DEF':
            if node.value == 'main':
                self._classify_line_by_content('main', 'FUNCTION_DEF', 'Main Function Definition')
            else:
                self._classify_line_by_content(node.value, 'FUNCTION_DEF', 'Function Definition')
            # Analizar el cuerpo de la función
            for child in node.children:
                self._analyze_ast_node(child, context='function_body')
                
        elif node.type == 'DECLARATION':
            var_name = node.value
            if len(node.children) > 1:  # Declaración con inicialización
                self._classify_line_by_content(var_name, 'VAR_DECL_INIT', 'Variable Declaration with Initialization')
            else:  # Solo declaración
                self._classify_line_by_content(var_name, 'VAR_DECL', 'Variable Declaration')
            # Analizar la expresión de inicialización si existe
            for child in node.children[1:]:
                self._analyze_ast_node(child, context='initialization')
                
        elif node.type == 'ASSIGNMENT':
            var_name = node.value
            self._classify_line_by_content(var_name, 'ASSIGN', 'Variable Assignment')
            # Analizar la expresión asignada
            for child in node.children:
                self._analyze_ast_node(child, context='assignment')
                
        elif node.type == 'IF':
            self._classify_line_by_content('if', 'BRANCH', 'If Statement')
            # Analizar condición y bloques
            for child in node.children:
                self._analyze_ast_node(child, context='if_statement')
                
        elif node.type == 'ELSE':
            self._classify_line_by_content('else', 'BRANCH', 'Else Statement')
            for child in node.children:
                self._analyze_ast_node(child, context='else_statement')
                
        elif node.type == 'WHILE':
            self._classify_line_by_content('while', 'WHILE_LOOP', 'While Loop')
            for child in node.children:
                self._analyze_ast_node(child, context='while_loop')
                
        elif node.type == 'FOR':
            self._classify_line_by_content('for', 'FOR_LOOP', 'For Loop')
            for child in node.children:
                self._analyze_ast_node(child, context='for_loop')
                
        elif node.type == 'RETURN':
            self._classify_line_by_content('return', 'RETURN', 'Return Statement')
            for child in node.children:
                self._analyze_ast_node(child, context='return_value')
                
        elif node.type == 'COUT':
            self._classify_line_by_content('cout', 'OUTPUT', 'Output Statement')
            for child in node.children:
                self._analyze_ast_node(child, context='output')
                
        elif node.type == 'CIN':
            self._classify_line_by_content('cin', 'INPUT', 'Input Statement')
            for child in node.children:
                self._analyze_ast_node(child, context='input')
                
        elif node.type == 'BINOP':
            if context not in ['initialization', 'assignment', 'return_value', 'output', 'if_statement', 'while_loop', 'for_loop']:
                # Solo clasificar como cálculo si no está dentro de otro contexto
                self._classify_line_by_content(node.value, 'CALCULATIONS', 'Mathematical Calculation')
            for child in node.children:
                self._analyze_ast_node(child, context)
                
        elif node.type == 'BLOCK':
            for child in node.children:
                self._analyze_ast_node(child, context)
                
        else:
            # Para otros tipos de nodos, continuar el análisis recursivo
            for child in node.children:
                self._analyze_ast_node(child, context)
    
    def _classify_line_by_content(self, search_term, semantic_type, description):
        """
        Clasifica una línea basándose en su contenido
        """
        for classification in self.line_classifications:
            if search_term.lower() in classification['line_content'].lower():
                if classification['semantic_type'] == 'UNKNOWN':  # Solo actualizar si no está clasificada
                    classification['semantic_type'] = semantic_type
                    classification['description'] = description
                break
    
    def print_semantic_table(self):
        """
        Imprime la tabla de clasificación semántica
        """
        print("\n5. ANÁLISIS SEMÁNTICO POR LÍNEAS:")
        print("-" * 60)
        print(f"{'Línea':<6} | {'Tipo Semántico':<20} | {'Descripción':<25} | {'Código'}")
        print("-" * 60)
        
        for classification in self.line_classifications:
            line_num = classification['line_number']
            sem_type = classification['semantic_type']
            description = classification['description']
            content = classification['line_content'][:40] + "..." if len(classification['line_content']) > 40 else classification['line_content']
            
            print(f"{line_num:<6} | {sem_type:<20} | {description:<25} | {content}")
        
        print("-" * 60)
        
        # Mostrar resumen de tipos encontrados
        type_counts = {}
        for classification in self.line_classifications:
            sem_type = classification['semantic_type']
            type_counts[sem_type] = type_counts.get(sem_type, 0) + 1
        
        print("\nRESUMEN DE CONSTRUCCIONES SEMÁNTICAS:")
        for sem_type, count in sorted(type_counts.items()):
            type_descriptions = {
                'PREPROCESSING': 'Directivas de Preprocesador',
                'FUNCTION_DEF': 'Definiciones de Función',
                'VAR_DECL': 'Declaraciones de Variable',
                'VAR_DECL_INIT': 'Declaraciones con Inicialización',
                'ASSIGN': 'Asignaciones de Variable',
                'RETURN': 'Sentencias Return',
                'CALCULATIONS': 'Cálculos Matemáticos',
                'BRANCH': 'Control de Flujo (if/else)',
                'FOR_LOOP': 'Bucles For',
                'WHILE_LOOP': 'Bucles While',
                'OUTPUT': 'Sentencias de Salida',
                'INPUT': 'Sentencias de Entrada',
                'UNKNOWN': 'No Clasificadas'
            }
            desc = type_descriptions.get(sem_type, sem_type)
            print(f"  - {desc}: {count}")
    
    def get_semantic_statistics(self):
        """
        Retorna estadísticas sobre los tipos semánticos encontrados
        """
        type_counts = {}
        total_lines = len(self.line_classifications)
        
        for classification in self.line_classifications:
            sem_type = classification['semantic_type']
            type_counts[sem_type] = type_counts.get(sem_type, 0) + 1
        
        return {
            'total_lines': total_lines,
            'type_counts': type_counts,
            'classified_lines': sum(1 for c in self.line_classifications if c['semantic_type'] != 'UNKNOWN'),
            'unclassified_lines': sum(1 for c in self.line_classifications if c['semantic_type'] == 'UNKNOWN')
        }