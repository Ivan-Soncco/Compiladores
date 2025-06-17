#semantic_analyzer.py

class SymbolTable:
    """Tabla de símbolos para manejar variables y funciones"""
    
    def __init__(self):
        self.symbols = {}
        self.parent = None
    
    def define(self, name, symbol_type, value=None):
        """Define un símbolo en la tabla actual"""
        if name in self.symbols:
            raise Exception(f"Variable '{name}' ya está definida")
        self.symbols[name] = {'type': symbol_type, 'value': value}
    
    def lookup(self, name):
        """Busca un símbolo en la tabla actual o en las tablas padre"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None
    
    def enter_scope(self):
        """Entra en un nuevo ámbito"""
        new_table = SymbolTable()
        new_table.parent = self
        return new_table

class SemanticAnalyzer:
    """
    Analizador semántico básico para C++
    Verifica tipos, variables definidas, etc.
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_type = None
        self.errors = []
    
    def analyze(self, ast):
        """Analiza el AST y verifica reglas semánticas"""
        self.errors = []
        try:
            self.visit(ast)
            return len(self.errors) == 0, self.errors
        except Exception as e:
            self.errors.append(str(e))
            return False, self.errors
    
    def visit(self, node):
        """Visita un nodo del AST"""
        if node is None:
            return None
        
        method_name = f'visit_{node.type.lower()}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Visita genérica para nodos no implementados"""
        for child in node.children:
            self.visit(child)
    
    def visit_program(self, node):
        """Visita el nodo raíz del programa"""
        for child in node.children:
            self.visit(child)
    
    def visit_include(self, node):
        """Visita directivas include - no necesita verificación semántica"""
        pass
    
    def visit_declaration(self, node):
        """Visita declaraciones de variables"""
        var_name = node.value
        var_type = node.children[0].value
        
        # Verificar que el tipo sea válido
        if var_type not in ['int', 'float', 'char', 'void']:
            self.errors.append(f"Tipo '{var_type}' no válido para variable '{var_name}'")
            return
        
        # Verificar que no sea void para variables
        if var_type == 'void':
            self.errors.append(f"Variable '{var_name}' no puede ser de tipo void")
            return
        
        # Definir la variable en la tabla de símbolos
        try:
            self.symbol_table.define(var_name, var_type)
        except Exception as e:
            self.errors.append(str(e))
        
        # Si hay inicialización, verificar compatibilidad de tipos
        if len(node.children) > 1:
            init_type = self.visit(node.children[1])
            if init_type and not self.is_compatible_type(var_type, init_type):
                self.errors.append(f"Tipo incompatible en inicialización de '{var_name}': {var_type} vs {init_type}")
    
    def visit_assignment(self, node):
        """Visita asignaciones"""
        var_name = node.value
        
        # Verificar que la variable esté definida
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            self.errors.append(f"Variable '{var_name}' no está definida")
            return
        
        # Verificar compatibilidad de tipos
        expr_type = self.visit(node.children[0])
        if expr_type and not self.is_compatible_type(symbol['type'], expr_type):
            self.errors.append(f"Tipo incompatible en asignación a '{var_name}': {symbol['type']} vs {expr_type}")
    
    def visit_function_def(self, node):
        """Visita definiciones de funciones"""
        func_name = node.value
        func_type = node.children[0].value
        
        # Guardar el tipo de función actual para verificar returns
        self.current_function_type = func_type
        
        # Definir la función en la tabla de símbolos
        try:
            self.symbol_table.define(func_name, f"function_{func_type}")
        except Exception as e:
            self.errors.append(str(e))
        
        # Entrar en nuevo ámbito para el cuerpo de la función
        self.symbol_table = self.symbol_table.enter_scope()
        
        # Visitar el cuerpo de la función
        self.visit(node.children[1])
        
        # Salir del ámbito
        self.symbol_table = self.symbol_table.parent
        self.current_function_type = None
    
    def visit_return(self, node):
        """Visita sentencias return"""
        if not self.current_function_type:
            self.errors.append("Return fuera de función")
            return
        
        if len(node.children) == 0:  # return sin valor
            if self.current_function_type != 'void':
                self.errors.append(f"Función de tipo '{self.current_function_type}' debe retornar un valor")
        else:  # return con valor
            if self.current_function_type == 'void':
                self.errors.append("Función void no puede retornar un valor")
            else:
                return_type = self.visit(node.children[0])
                if return_type and not self.is_compatible_type(self.current_function_type, return_type):
                    self.errors.append(f"Tipo de retorno incompatible: {self.current_function_type} vs {return_type}")
    
    def visit_if(self, node):
        """Visita sentencias if"""
        # Verificar que la condición sea válida
        condition_type = self.visit(node.children[0])
        if condition_type and condition_type not in ['int', 'float', 'boolean']:
            self.errors.append(f"Condición del if debe ser de tipo numérico o booleano, no '{condition_type}'")
        
        # Visitar el bloque then
        self.visit(node.children[1])
        
        # Visitar el bloque else si existe
        if len(node.children) > 2:
            self.visit(node.children[2])
    
    def visit_while(self, node):
        """Visita bucles while"""
        # Verificar que la condición sea válida
        condition_type = self.visit(node.children[0])
        if condition_type and condition_type not in ['int', 'float', 'boolean']:
            self.errors.append(f"Condición del while debe ser de tipo numérico o booleano, no '{condition_type}'")
        
        # Visitar el cuerpo del bucle
        self.visit(node.children[1])
    
    def visit_for(self, node):
        """Visita bucles for"""
        # Entrar en nuevo ámbito
        self.symbol_table = self.symbol_table.enter_scope()
        
        # Visitar inicialización, condición e incremento
        self.visit(node.children[0])  # inicialización
        
        condition_type = self.visit(node.children[1])  # condición
        if condition_type and condition_type not in ['int', 'float', 'boolean']:
            self.errors.append(f"Condición del for debe ser de tipo numérico o booleano, no '{condition_type}'")
        
        self.visit(node.children[2])  # incremento
        self.visit(node.children[3])  # cuerpo
        
        # Salir del ámbito
        self.symbol_table = self.symbol_table.parent
    
    def visit_binop(self, node):
        """Visita operaciones binarias"""
        left_type = self.visit(node.children[0])
        right_type = self.visit(node.children[1])
        
        operator = node.value
        
        # Verificar compatibilidad de tipos según el operador
        if operator in ['+', '-', '*', '/']:
            if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                self.errors.append(f"Operador '{operator}' requiere operandos numéricos")
                return 'int'  # Asumir int por defecto
            # Promoción de tipos: float + int = float
            return 'float' if 'float' in [left_type, right_type] else 'int'
        
        elif operator in ['==', '!=', '<', '>', '<=', '>=']:
            if not self.is_compatible_type(left_type, right_type):
                self.errors.append(f"Comparación entre tipos incompatibles: {left_type} vs {right_type}")
            return 'boolean'
        
        return 'int'  # Tipo por defecto
    
    def visit_unary(self, node):
        """Visita operaciones unarias"""
        operand_type = self.visit(node.children[0])
        operator = node.value
        
        if operator == '-':
            if operand_type not in ['int', 'float']:
                self.errors.append(f"Operador unario '-' requiere operando numérico")
            return operand_type
        
        return operand_type
    
    def visit_number(self, node):
        """Visita números literales"""
        if isinstance(node.value, int):
            return 'int'
        else:
            return 'float'
    
    def visit_string(self, node):
        """Visita cadenas literales"""
        return 'string'
    
    def visit_id(self, node):
        """Visita identificadores"""
        var_name = node.value
        symbol = self.symbol_table.lookup(var_name)
        
        if not symbol:
            self.errors.append(f"Variable '{var_name}' no está definida")
            return 'int'  # Tipo por defecto para continuar
        
        return symbol['type']
    
    def visit_block(self, node):
        """Visita bloques de código"""
        for child in node.children:
            self.visit(child)
    
    def visit_cout(self, node):
        """Visita sentencias cout"""
        for child in node.children:
            self.visit(child)
    
    def visit_cin(self, node):
        """Visita sentencias cin"""
        for child in node.children:
            self.visit(child)
    
    def visit_expression_stmt(self, node):
        """Visita expresiones como sentencias"""
        self.visit(node.children[0])
    
    def is_compatible_type(self, type1, type2):
        """Verifica si dos tipos son compatibles"""
        if type1 == type2:
            return True
        
        # int y float son compatibles
        if {type1, type2} == {'int', 'float'}:
            return True
        
        return False