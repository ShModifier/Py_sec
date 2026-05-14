# 支持插件化加载
# 编写新的插件之后只需要在此模块内导入
from typing import List
from .rce_eval_rule import EvalRule
from .command_exec_rule import CommandExecRule
from .sql_injection import SQLInjectionRule
from .xss import XSSRule
from .insecure_deserialization_rule import PickleLoadRule
from .path_traversal_rule import PathTraversalRule
from app.config_manager import load_config

def load_rules() -> List:
    #后续可动态加载插件规则
    config = load_config()
    enabled_rules = config.get("rules", {})
    all_rules =  [
        EvalRule(),
        CommandExecRule(),
        SQLInjectionRule(),
        XSSRule(),
        PickleLoadRule(),
        PathTraversalRule(),
    ]

    rules = []

    for rule in all_rules:

        rule_id = getattr(rule, "id", None)

        if rule_id is None:
            rules.append(rule)
            continue

        if enabled_rules.get(rule_id, True):
            rules.append(rule)
    return rules