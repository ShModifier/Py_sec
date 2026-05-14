import ast
from core.context import AnalysisContext
from core.visitor import AuditVisitor
from rules.rule_registry import load_rules


class Scanner:
    def __init__(self, filename: str, code: str):
        self.filename = filename
        self.code = code

    def scan(self):
        tree = ast.parse(self.code, filename=self.filename)

        context = AnalysisContext(self.filename)
        rules = load_rules()

        visitor = AuditVisitor(context, rules)
        visitor.visit(tree)

        return context