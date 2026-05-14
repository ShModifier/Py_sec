# rules/path_traversal_rule.py
import ast
from .base_rule import BaseRule


class PathTraversalRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.id = "PATH001"
        self.name = "Path Traversal"
        self.severity = "MEDIUM"
        self.description = "File path may be constructed from user input"
        self.enabled = True

    def match(self, node, context):
        return isinstance(node, ast.Call)

    def check(self, node, context):
        if not isinstance(node, ast.Call):
            return None

        # open(...)
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if not node.args:
                return None

            arg = node.args[0]

            # 只要是“动态路径”，交给污点分析判断
            if isinstance(arg, (ast.BinOp, ast.JoinedStr, ast.Name)):
                return {
                    "type": "path_traversal",
                    "node": node,
                    "rule": self,
                    "args": [arg]
                }

        return None