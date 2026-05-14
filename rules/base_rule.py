from abc import ABC, abstractmethod
import ast
from core.context import AnalysisContext


class BaseRule(ABC):
    def __init__(self):
        self.id = "BASE"
        self.name = "Base Rule"
        self.severity = "LOW"
        self.description = ""
        self.enabled = True

    def match(self, node: ast.AST, context: AnalysisContext) -> bool:
        #判断当前AST节点是否需要检查（默认全部检查）
        return True

    def check(self, node: ast.AST, context: AnalysisContext) -> bool:
        #具体漏洞检测逻辑
        raise NotImplementedError

    def report(self, node: ast.AST,**kwargs):
        result = {
            "rule_id": self.id,
            "name": self.name,
            "severity": self.severity,
            "lineno": getattr(node, "lineno", 0),
            "message": self.description
        }

        result.update(kwargs)

        return result