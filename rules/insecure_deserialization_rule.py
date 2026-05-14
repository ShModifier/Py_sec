# rules/insecure_deserialization_rule.py
import ast
from .base_rule import BaseRule


class PickleLoadRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.id = "DES001"
        self.name = "Insecure Deserialization"
        self.severity = "HIGH"
        self.description = "Use of pickle.loads may lead to arbitrary code execution"
        self.enabled = True

    def match(self, node, context):
        return isinstance(node, ast.Call)

    def check(self, node, context):
        if not isinstance(node, ast.Call):
            return False

        func = node.func

        # pickle.loads(...)
        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name) and func.value.id == "pickle":
                if func.attr == "loads":
                    return True

        # from pickle import loads → loads(...)
        elif isinstance(func, ast.Name):
            if func.id == "loads" and "pickle" in context.imports:
                return True

        return False