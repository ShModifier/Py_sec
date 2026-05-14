# core/visitor.py
import ast
from typing import List
from core.context import AnalysisContext
from rules.rule_registry import load_rules
#这里我不知道为啥在main函数里调用visior的时候必须要用根目录对应的相对路径
#不然会显示ModuleNotFoundError: No module named 'context'

class AuditVisitor(ast.NodeVisitor):
    def __init__(self, context: AnalysisContext, rules: List):
        self.context = context
        self.rules = rules
        context.visitor = self

    def visit(self, node):
        self.context.push_node(node)
        for rule in self.rules:
            try:
                if rule.match(node, self.context):
                    ret = rule.check(node, self.context)
                    if isinstance(ret, dict):
                        self.context.candidates.append(ret)
                    elif ret is True:
                        result = rule.report(node)
                        self.context.results.append(result)

            except Exception as e:
                print(f"[Rule Error] {rule.__class__.__name__}: {e}")

        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, None)

        if visitor is not None:
            visitor(node)
        else:
            self.generic_visit(node)

        self.context.pop_node()

    # ===============================
    # 作用域管理
    # ===============================
    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_func = self.context.current_function
        self.context.current_function = node.name

        self.context.push_scope()
        self.generic_visit(node)
        self.context.pop_scope()

        self.context.current_function = prev_func

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_class = self.context.current_class
        self.context.current_class = node.name

        self.context.push_scope()
        self.generic_visit(node)
        self.context.pop_scope()

        self.context.current_class = prev_class

    # ===============================
    # 污点源判断
    # ===============================
    def _is_source(self, node):
        if isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            return func_name in ['input']
        return False

    # ===============================
    #污点判断
    # ===============================
    def _is_tainted(self, node):
        if isinstance(node, ast.Name):
            source = self.context.taint_map.get(node.id)
            return source not in [None, "sanitized"]

        elif isinstance(node, ast.BinOp):
            return self._is_tainted(node.left) or self._is_tainted(node.right)
            print("TAINT CHECK:", ast.dump(node))

        elif isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            if func_name == "input":
                return True

            return any(self._is_tainted(arg) for arg in node.args)

        return False

    def is_tainted(self, node):
        return self._is_tainted(node)

    def _is_sanitizer(self, node):
        if isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            return func_name in ['int', 'str', 'escape', 'sanitize']
        return False

    # ===============================
    # 变量赋值 + 污点传播
    # ===============================
    def visit_Assign(self, node: ast.Assign):
        value = node.value

        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id

                if self._is_source(value):
                    self.context.add_taint(var_name, "input")

                elif isinstance(value, ast.Name):
                    if value.id in self.context.taint_map:
                        source = self.context.taint_map[value.id]
                        self.context.add_taint(var_name, source)

                elif isinstance(value, ast.BinOp):
                    '''
                    if self._is_tainted(value):
                        self.context.add_taint(var_name, "propagated")
                    '''
                    if isinstance(value.op, ast.Mod):
                        # 只要右边变量是安全的，就认为安全
                        if isinstance(value.right, ast.Name):
                            source = self.context.taint_map.get(value.right.id)
                            if source == "sanitized":
                                self.context.taint_map.pop(var_name, None)
                            elif self._is_tainted(value.right):
                                self.context.add_taint(var_name, "propagated")
                    else:
                        if self._is_tainted(value):
                            self.context.add_taint(var_name, "propagated")

                elif isinstance(value, ast.Call):
                    func_name = self._get_func_name(value.func)

                    if func_name in ["int", "str"]:
                        self.context.taint_map[var_name] = "sanitized"

                    else:
                        if any(self._is_tainted(arg) for arg in value.args):
                            self.context.add_taint(var_name, f"from {func_name}")

                self.context.set_variable(var_name, value)

        self.generic_visit(node)

    # ===============================
    # 函数调用 + Sink检测
    # ===============================
    def visit_Call(self, node: ast.Call):
        func_name = self._get_func_name(node.func)

        # 调用图
        if func_name:
            self.context.add_call(self.context.current_function, func_name)

        # =======================
        # Sink检测
        # =======================
        dangerous_funcs = ['exec', 'eval']

        self.generic_visit(node)

    # ===============================
    # Import
    # ===============================
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.context.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.context.imports.add(node.module)
        self.generic_visit(node)

    # ===============================
    # 工具函数
    # ===============================
    def _get_func_name(self, func):
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None