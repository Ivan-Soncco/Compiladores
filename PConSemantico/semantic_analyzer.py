class SymbolTable:
    """Tabla de símbolos con anidamiento de ámbitos"""

    def __init__(self):
        self.symbols: dict[str, dict] = {}
        self.parent: 'SymbolTable | None' = None

    # ------------------------------------------------------------
    def define(self, name: str, symbol_type: str, value=None):
        if name in self.symbols:
            raise Exception(f"Identificador '{name}' ya está definido en este ámbito")
        self.symbols[name] = {"type": symbol_type, "value": value}

    def lookup(self, name: str):
        if name in self.symbols:
            return self.symbols[name]
        return self.parent.lookup(name) if self.parent else None

    def enter_scope(self):
        child = SymbolTable()
        child.parent = self
        return child


# =============================================================
class SemanticAnalyzer:
    """Analizador semántico simple para el subconjunto C++"""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_type: str | None = None
        self.errors: list[str] = []

    # ------------------------------------------------------------
    def analyze(self, ast):
        self.errors = []
        self.symbol_table = SymbolTable()
        try:
            self.visit(ast)
        except Exception as e:
            self.errors.append(str(e))
        return len(self.errors) == 0, self.errors

    # =================== VISITADORES GENERALES ===================
    def visit(self, node):
        """Despacha según el tipo de nodo; acepta listas"""
        if node is None:
            return None
        if isinstance(node, list):  # listas de nodos
            ret = None
            for item in node:
                tmp = self.visit(item)
                ret = tmp if tmp is not None else ret
            return ret
        method = getattr(self, f"visit_{node.type.lower()}", self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    # ======================== NODOS TOP ==========================
    def visit_program(self, node):
        for child in node.children:
            self.visit(child)

    # ===================== DECLARACIONES VAR =====================
    def visit_var_decl(self, node):
        # children[0]  -> TYPE ; children[1..] -> INIT_DECL
        base_type = node.children[0].value  # int / float / char / double / void
        if base_type == 'void':
            self.errors.append("No se puede declarar variable de tipo void")
            return
        for init_node in node.children[1:]:
            self._handle_init_decl(init_node, base_type)

    def _handle_init_decl(self, init_node, base_type):
        name = init_node.value
        try:
            self.symbol_table.define(name, base_type)
        except Exception as e:
            self.errors.append(str(e))
        if init_node.children:  # inicializador presente
            expr_type = self.visit(init_node.children[0])
            if expr_type and not self.is_compatible_type(base_type, expr_type):
                self.errors.append(f"Inicialización incompatible de '{name}': {base_type} vs {expr_type}")

    # =================== DEFINICIÓN DE FUNCIÓN ===================
    def visit_fun_def(self, node):
        ret_type = node.children[0].value  # TYPE nodo
        name = node.value
        try:
            self.symbol_table.define(name, f"function_{ret_type}")
        except Exception as e:
            self.errors.append(str(e))
        # Nuevo ámbito para parámetros + cuerpo (params se integran como lista sencilla)
        prev_table = self.symbol_table
        self.symbol_table = self.symbol_table.enter_scope()
        # Parametros:
        params = node.children[1]
        for param in params:  # cada param = ASTNode('PARAM', value=id, children=[TYPE])
            p_name = param.value
            p_type = param.children[0].value
            try:
                self.symbol_table.define(p_name, p_type)
            except Exception as e:
                self.errors.append(str(e))

        # Cuerpo
        prev_func = self.current_function_type
        self.current_function_type = ret_type
        self.visit(node.children[2])  # BLOCK
        self.current_function_type = prev_func
        self.symbol_table = prev_table

    # ========================= BLOQUES ===========================
    def visit_block(self, node):
        prev_table = self.symbol_table
        self.symbol_table = self.symbol_table.enter_scope()
        for child in node.children:
            self.visit(child)
        self.symbol_table = prev_table

    # ===================== SENTENCIAS RETURN =====================
    def visit_return(self, node):
        if self.current_function_type is None:
            self.errors.append("Return fuera de cualquier función")
            return None
        if not node.children:  # return;
            if self.current_function_type != 'void':
                self.errors.append(f"Función de tipo '{self.current_function_type}' debe retornar un valor")
            return None
        expr_type = self.visit(node.children[0])
        if self.current_function_type == 'void':
            self.errors.append("Función void no puede retornar un valor")
        elif not self.is_compatible_type(self.current_function_type, expr_type):
            self.errors.append(f"Tipo de retorno incompatible: {self.current_function_type} vs {expr_type}")
        return expr_type

    # ================= SENTENCIAS DE CONTROL =====================
    def visit_if(self, node):
        cond_type = self.visit(node.children[0])
        if cond_type not in {None, 'int', 'float', 'boolean'}:
            self.errors.append(f"La condición del if debe ser numérica o booleana, no '{cond_type}'")
        self.visit(node.children[1])  # then
        if len(node.children) > 2:
            self.visit(node.children[2])  # else

    def visit_while(self, node):
        cond_type = self.visit(node.children[0])
        if cond_type not in {None, 'int', 'float', 'boolean'}:
            self.errors.append(f"La condición del while debe ser numérica o booleana, no '{cond_type}'")
        self.visit(node.children[1])

    def visit_for(self, node):
        prev = self.symbol_table
        self.symbol_table = self.symbol_table.enter_scope()
        # init, cond, incr, body
        self.visit(node.children[0])
        cond_type = self.visit(node.children[1])
        if cond_type not in {None, 'int', 'float', 'boolean'}:
            self.errors.append(f"La condición del for debe ser numérica o booleana, no '{cond_type}'")
        self.visit(node.children[2])
        self.visit(node.children[3])
        self.symbol_table = prev

    # ====================== ASIGNACIÓN ===========================
    def visit_assign(self, node):
        # children[0] -> ID  , children[1] -> expr
        target_node = node.children[0]
        if target_node.type != 'ID':
            self.errors.append("El lado izquierdo de '=' debe ser un identificador")
            return None
        var_name = target_node.value
        sym = self.symbol_table.lookup(var_name)
        if sym is None:
            self.errors.append(f"Variable '{var_name}' no declarada")
            return None
        expr_type = self.visit(node.children[1])
        if expr_type and not self.is_compatible_type(sym['type'], expr_type):
            self.errors.append(f"Tipo incompatible en asignación a '{var_name}': {sym['type']} vs {expr_type}")
        return sym['type']

    # ===================== OPERACIONES BINARIAS ==================
    def visit_binop(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        op = node.value
        if op in {'+', '-', '*', '/'}:
            if left not in {'int', 'float'} or right not in {'int', 'float'}:
                self.errors.append(f"Operación '{op}' requiere operandos numéricos")
            return 'float' if 'float' in {left, right} else 'int'
        elif op in {'==', '!=', '<', '>', '<=', '>='}:
            if not self.is_compatible_type(left, right):
                self.errors.append(f"Comparación entre tipos incompatibles: {left} vs {right}")
            return 'boolean'
        return left  # otro operador

    # ===================== OPERACIONES UNARIAS ===================
    def visit_unary(self, node):
        operand_type = self.visit(node.children[0])
        op = node.value
        if op == '-' and operand_type not in {'int', 'float'}:
            self.errors.append("El operador '-' requiere operando numérico")
        return operand_type

    # ======================== LITERALES ==========================
    def visit_number(self, _):
        return 'int'

    def visit_float_num(self, _):
        return 'float'

    def visit_string_literal(self, _):
        return 'string'

    def visit_char_literal(self, _):
        return 'char'

    def visit_boolean(self, _):
        return 'boolean'

    # ======================== IDENTIFICADOR ======================
    def visit_id(self, node):
        sym = self.symbol_table.lookup(node.value)
        if sym is None:
            self.errors.append(f"Variable '{node.value}' no declarada")
            return None
        return sym['type']

    # ==================== CALL, COUT, CIN ========================
    def visit_call(self, node):
        # Por simplicidad, asumimos que la función existe y devuelve int
        for arg in node.children:
            self.visit(arg)
        return 'int'

    def visit_cout(self, node):
        for child in node.children:
            self.visit(child)

    def visit_cin(self, node):
        for child in node.children:
            if child.type == 'ID':
                # Se supone que ID es l‑value válido
                if self.symbol_table.lookup(child.value) is None:
                    self.errors.append(f"Variable '{child.value}' no declarada antes de usar en cin")
            else:
                self.visit(child)

    # =================== UTILIDAD COMPATIBILIDAD ================
    def is_compatible_type(self, t1, t2):
        if t1 == t2:
            return True
        if {t1, t2} <= {'int', 'float'}:
            return True
        return False
