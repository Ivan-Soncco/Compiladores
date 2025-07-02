class SemanticLineAnalyzer:
    """Clasifica cada línea de código según construcciones del AST"""

    def __init__(self):
        self.line_classifications: list[dict] = []
        self.source_lines: list[str] = []

    def analyze_lines(self, source_code, ast):
        self.source_lines = source_code.strip().split('\n')
        self.line_classifications = [
            {
                'line_number': i,
                'line_content': line.rstrip(),
                'semantic_type': 'UNKNOWN',
                'description': 'Unknown'
            }
            for i, line in enumerate(self.source_lines, 1)
            if line.strip() and not line.strip().startswith('//')
        ]
        self._walk_ast(ast)
        return self.line_classifications

    # ======================= RECORRIDO AST =======================
    def _walk_ast(self, node, ctx=None):
        if node is None:
            return
        if isinstance(node, list):
            for n in node:
                self._walk_ast(n, ctx)
            return

        handler = getattr(self, f"_t_{node.type.lower()}", None)
        if handler:
            handler(node, ctx)

        for child in node.children:
            self._walk_ast(child, ctx)

    # ------------------- manejadores por tipo -------------------
    def _mark(self, keyword, sem_type, desc):
        for cls in self.line_classifications:
            if keyword in cls['line_content'] and cls['semantic_type'] == 'UNKNOWN':
                cls['semantic_type'] = sem_type
                cls['description'] = desc
                break

    def _t_fun_def(self, node, _):
        self._mark(node.value, 'FUNCTION_DEF', 'Function Definition')

    def _t_var_decl(self, node, _):
        for init in node.children[1:]:
            kw = init.value
            if init.children:
                self._mark(kw, 'VAR_DECL_INIT', 'Variable Decl+Init')
            else:
                self._mark(kw, 'VAR_DECL', 'Variable Declaration')

    def _t_assign(self, node, _):
        self._mark(node.children[0].value, 'ASSIGN', 'Assignment')

    def _t_if(self, *_):
        self._mark('if', 'BRANCH', 'If Statement')

    def _t_while(self, *_):
        self._mark('while', 'WHILE_LOOP', 'While Loop')

    def _t_for(self, *_):
        self._mark('for', 'FOR_LOOP', 'For Loop')

    def _t_return(self, *_):
        self._mark('return', 'RETURN', 'Return Statement')

    def _t_cout(self, node, _):
        self._mark('cout', 'OUTPUT', 'Output Statement')
        for child in node.children:
            self._walk_ast(child, ctx='cout')

    def _t_cin(self, node, _):
        self._mark('cin', 'INPUT', 'Input Statement')
        for child in node.children:
            self._walk_ast(child, ctx='cin')

    def _t_binop(self, node, ctx):
        # Solo se marca como cálculo si está fuera de contexto como cout, return, etc.
        if ctx is None:
            self._mark(node.value, 'CALCULATIONS', 'Math Calculation')

    # --------------------- Impresión y resumen ---------------------
    def print_semantic_table(self):
        print("\n5. ANÁLISIS SEMÁNTICO POR LÍNEAS:")
        print("-" * 60)
        print(f"{'Línea':<6} | {'Tipo':<15} | {'Descripción':<22} | Código")
        print("-" * 60)
        for cls in self.line_classifications:
            code = cls['line_content']
            if len(code) > 45:
                code = code[:42] + '...'
            print(f"{cls['line_number']:<6} | {cls['semantic_type']:<15} | {cls['description']:<22} | {code}")
        print("-" * 60)

    def get_semantic_statistics(self):
        total = len(self.line_classifications)
        classified = sum(1 for c in self.line_classifications if c['semantic_type'] != 'UNKNOWN')
        unclassified = total - classified
        return {
            'total_lines': total,
            'classified_lines': classified,
            'unclassified_lines': unclassified,
            'type_counts': self._type_histogram()
        }

    def _type_histogram(self):
        hist = {}
        for cls in self.line_classifications:
            hist[cls['semantic_type']] = hist.get(cls['semantic_type'], 0) + 1
        return hist
