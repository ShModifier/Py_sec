import ast
from .base_rule import BaseRule

class XSSRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.id = "RCE004"
        self.name = "XSS"
        self.severity = "MEDIUM"
        self.description = "Potential XSS via unsafe HTML rendering"
        self.enabled = True

        self.sinks = {
            "render_html",
            "render_template",
            "html",
        }

    def match(self, node, context):
        return isinstance(node, ast.Call)

    def check(self, node, context):
        if not isinstance(node, ast.Call):
            return None

        func_name = self._get_func_name(node.func)
        if not func_name:
            return None

        if func_name not in self.sinks:
            return None

        args = list(node.args) + [kw.value for kw in node.keywords]

        if not args:
            return None

        for arg in args:
            if self._is_tainted_from_context(arg, context):
                return {
                    "type": "xss",
                    "node": node,
                    "rule": self,
                    "args": args
                }

        return None

    def _is_tainted_from_context(self, node, context):
        """
        ✔ 完全依赖 visitor 的 taint_map
        """

        # 变量污染
        if isinstance(node, ast.Name):
            return context.taint_map.get(node.id) not in [None, "sanitized"]

        # 表达式（你 visitor 已经处理过传播）
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            return True

        # 常量安全
        if isinstance(node, ast.Constant):
            return False

        # 函数返回值（保守）
        if isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)

            # 如果是已知 sink wrapper，也算污染
            if func_name in self.sinks:
                return True

            return True

        return False

    def _get_func_name(self, func):
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None