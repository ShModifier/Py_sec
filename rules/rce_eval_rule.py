import ast
from .ast_rule import ASTRule


class EvalRule(ASTRule):
    def __init__(self):
        super().__init__()
        self.id = "RCE001"
        self.name = "Eval Call"
        self.severity = "LOW"
        self.description = "Use of eval() is dangerous"
        self.enabled = True

    def match(self, node: ast.AST, context) -> bool:
        return isinstance(node, ast.Call)

    def check(self, node: ast.AST, context):
        if not isinstance(node, ast.Call):
            return None
        func = node.func
        # eval / exec
        if isinstance(func, ast.Name):
            if func.id in ("eval", "exec"):
                return {
                    "type": "eval",
                    "node": node,
                    "rule": self,
                    "args": node.args
                }
        # builtins.eval
        elif isinstance(func, ast.Attribute):
            if func.attr in ("eval", "exec"):
                return {
                    "type": "eval",
                    "node": node,
                    "rule": self,
                    "args": node.args
                }

        return None