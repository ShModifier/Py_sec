'''
这里我们检测三种典型 SQL 注入模式：

字符串拼接	"select * from user where id=" + uid
f-string	f"select * from user where id={uid}"
execute调用	cursor.execute(...)

对应 AST：
ast.BinOp → 字符串拼接
ast.JoinedStr → f-string
'''

import ast
from .base_rule import BaseRule

class SQLInjectionRule(BaseRule):
    def __init__(self):
        super().__init__()
        self.id = "RCE003"
        self.name = "SQL Injection"
        self.severity = "HIGH"
        self.description = "Possible SQL injection via string concatenation"
        self.enabled = True

    def match(self,node,context):
        return isinstance(node, ast.Call)

    def check(self, node, context):
        if not isinstance(node, ast.Call):
            return None

        # *.execute(...)
        if not isinstance(node.func, ast.Attribute):
            return None

        if node.func.attr != "execute":
            return None

        if not node.args:
            return None

        arg = node.args[0]

        # 只要是“动态 SQL”，交给污点分析判断
        if isinstance(arg, (ast.BinOp, ast.JoinedStr, ast.Name)):
            return {
                "type": "sql_injection",
                "node": node,
                "rule": self,
                "args": [arg]
            }

        return None