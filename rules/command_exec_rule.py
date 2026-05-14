'''
目标检测：
os.system(cmd)
subprocess.Popen(cmd, shell=True)
subprocess.call(cmd, shell=True)
subprocess.run(cmd, shell=True)
'''

import ast
from .ast_rule import ASTRule


class CommandExecRule(ASTRule):
    def __init__(self):
        super().__init__()
        self.id = "RCE002"
        self.name = "System Command Execution"
        self.severity = "HIGH"
        self.description = "Potential command execution via os.system or subprocess with shell=True"
        self.enabled = True

    def match(self, node: ast.AST, context) -> bool:
        # 只关心函数调用节点
        return isinstance(node, ast.Call)

    def check(self, node: ast.AST, context):
        if not isinstance(node, ast.Call):
            return None
        func = node.func
        func_name = self._get_func_name(func)
        # os.system(...)
        if func_name == "system" and self._is_os_system(func):
            return {
                "type": "command_exec",
                "node": node,
                "rule": self,
                "args": node.args
            }
        # subprocess.* + shell=True
        if func_name in {"Popen", "call", "run"} and self._has_shell_true(node):
            return {
                "type": "command_exec",
                "node": node,
                "rule": self,
                "args": node.args
            }
        return None


    # ---------- 工具函数 ----------

    def _get_func_name(self, func):
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _is_os_system(self, func):
        """
        判断是否 os.system
        """
        return (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "os"
            and func.attr == "system"
        )

    def _has_shell_true(self, node: ast.Call) -> bool:
        """
        判断是否存在 shell=True 参数
        """
        for keyword in node.keywords:
            if keyword.arg == "shell":
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    return True
        return False