import ast

class ASTEngine:
    def __init__(self, code: str, filename: str = "<unknown>"):
        self.code = code
        self.filename = filename
        self.tree = None

    def parse(self):
        """将源码解析为 AST"""
        try:
            self.tree = ast.parse(self.code, filename=self.filename)
            return self.tree
        except SyntaxError as e:
            raise Exception(f"Syntax error in {self.filename}: {e}")