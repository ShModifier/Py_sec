# 一个ast规则的基类
import ast
from .base_rule import BaseRule


class ASTRule(BaseRule):
    """
    专用于 AST 语法层面的规则
    """

    def match(self, node: ast.AST) -> bool:
        # 默认所有节点都检查（子类可重写）
        return True