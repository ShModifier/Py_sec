#上下文分析Context

from typing import Dict, List, Optional, Any

class AnalysisContext:
    def __init__(self, filename: str):
        self.filename: str = filename

        # 当前所在函数空间
        self.current_function: Optional[str] = None
        self.current_class: Optional[str] = None
        self.scope_stack: List[Dict[str, Any]] = [{}]    # 作用域栈：每进入一个函数/作用域压栈，退出时弹栈
        self.call_graph: Dict[str, List[str]] = {}  # 调用关系图：函数 -> 调用的函数列表
        self.node_stack: List[Any] = []# AST节点路径栈（用于获取上下文）

        self.taint_map: Dict[str, str] = {}# 污点变量记录：var_name -> taint_source


        self.imports: set[str] = set() # 导入模块记录
        self.globals: set[str] = set()# 全局变量记录

        self.candidates = []  #候选漏洞池
        self.results = []  # 最终结果

    # ---------- 作用域管理 ----------

    def push_scope(self):
        """进入新作用域"""
        self.scope_stack.append({})

    def pop_scope(self):
        """退出当前作用域"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def set_variable(self, name: str, value: Any):
        """在当前作用域记录变量"""
        self.scope_stack[-1][name] = value

    def get_variable(self, name: str) -> Optional[Any]:
        """从内到外查找变量定义"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None

    # ---------- 调用关系管理 ----------

    def add_call(self, caller: Optional[str], callee: str):
        """记录函数调用关系"""
        if caller is None:
            caller = "<module>"

        if caller not in self.call_graph:
            self.call_graph[caller] = []

        self.call_graph[caller].append(callee)

    # ---------- AST路径管理 ----------

    def push_node(self, node: Any):
        self.node_stack.append(node)

    def pop_node(self):
        if self.node_stack:
            self.node_stack.pop()

    def current_node(self) -> Optional[Any]:
        if self.node_stack:
            return self.node_stack[-1]
        return None

    # ---------- 污点源管理 ----------

    def add_taint(self, var: str, source: str):
        self.taint_map[var] = source

    def is_tainted(self, var: str) -> bool:
        return var in self.taint_map