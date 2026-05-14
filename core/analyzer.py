# core/analyzer.py
import ast
import parso
from core.context import AnalysisContext
from core.visitor import AuditVisitor
from rules.rule_registry import load_rules
from core.ai.ai_engine import AIAnalyzer
from app.config_manager import get_api_config
from core.ai.model_adapter import BaseModel, DeepSeekModel, QwenModel


def analyze_entry(filename,enabled_rules=None,use_static=True,use_ai=False,use_assist=True):
    static_issues = []

    if use_static:
        static_result = analyze_file(filename, enabled_rules)
        if isinstance(static_result, dict):
            if static_result.get("status") == "error":
                return static_result
            static_issues = static_result.get("issues", []) or []
        else:
            static_issues = static_result or []

        for i in static_issues:
            i["source"] = "static"

    ai_issues = []
    if use_ai:
        ai_result = ai_analyze(filename=filename,issues=static_issues if use_assist else None)
        ai_issues = ai_result or []
        for i in ai_issues:
            i["source"] = "ai"

    #assist=True
    if use_ai and use_assist:
        final = ai_issues
    #assist=False
    else:
        final = static_issues + ai_issues

    return {
        "status": "ok",
        "issues": final
    }



def analyze_file(filename: str, enabled_rules=None, use_ai=False):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
        lines = source.splitlines()
        tree = ast.parse(source, filename=filename)

    except SyntaxError as e:
        return {
            "status": "error",
            "issues":parse_with_recovery(source, filename)
        }

    except Exception as e:
        return  {
            "status": "error",
            "issues": [{
                "name": "未知解析错误",
                "severity": "ERROR",
                "lineno": 0,
                "message": str(e)
            }]
        }
    rules = load_rules()
    if enabled_rules:
        rules = [r for r in rules if r.rule_id in enabled_rules]

    context = AnalysisContext(filename)
    visitor = AuditVisitor(context, rules)
    visitor.visit(tree)
    post_analysis(context)
    context.results.sort(key=lambda x: x.get("lineno", 0))

    return {
        "status": "correct",
        "issues":context.results
    }


def ai_analyze(filename: str, issues=None, source_code: str = None):
    if source_code:
        source = source_code
    elif filename:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    else:
        raise ValueError("No input source")

    config = get_api_config()
    provider = config.get("provider", "")
    ApiKey = config.get("api_key", "")
    ApiUrl = config.get("base_url", "")
    Model = config.get("model", "")

    #模型选择
    model = None
    if provider == "DeepSeek":
        model = DeepSeekModel(ApiUrl, Model, ApiKey)
    elif provider == "通义千问（Qwen）":
        model = QwenModel( ApiUrl,Model, ApiKey)
    if model is None:
        raise ValueError("AI provider not configured")

    ai = AIAnalyzer(model)
    if issues:
        ai_result = ai.analyze_with_issues(source, issues)
    else:
        ai_result = ai.analyze(source)

    return convert_ai_result(ai_result, filename or "unknown")


#转换为字符串,和ui兼容一下不然总是报错
def format_results(results):
    if not results:
        return "No vulnerabilities found."

    lines = []
    lines.append("=" * 50)
    lines.append("Security Audit Results")
    lines.append("=" * 50)

    for res in results:
        source = res.get("source", "RULE")

        lines.append(
            f"[{source}][{res['severity']}] {res['rule_id']} {res['name']} "
            f"(line {res['lineno']}): {res['message']}"
        )

    return "\n".join(lines)

#解析ai返回的的json
def convert_ai_result(ai_result, filename):

    results = []

    if not ai_result or not ai_result.get("has_vuln"):
        return results

    vulns = ai_result.get("vulnerabilities", [])

    for idx, v in enumerate(vulns):
        results.append({
            "severity": v.get("severity", "MEDIUM"),
            "rule_id": f"AI-{idx+1:03d}",
            "name": v.get("vuln_type", "AI Detection"),
            "lineno": v.get("lineno", 0),
            "message": f"{v.get('description')} | 修复建议: {v.get('fix')}",
            "source": "AI"
        })


    return results


#AST错误检查
def parse_with_recovery(source, filename):
    import ast

    errors = []
    lines = source.splitlines()

    MAX_ERRORS = 20
    seen_lines = set()

    for _ in range(MAX_ERRORS):
        try:
            ast.parse("\n".join(lines), filename=filename)
            break

        except SyntaxError as e:
            lineno = e.lineno or 0
            msg = e.msg

            errors.append({
                "name": "AST解析错误",
                "severity": "ERROR",
                "lineno": lineno,
                "message": msg
            })

            if lineno in seen_lines:
                print(f"重复错误行 {lineno}，停止恢复")
                break
            seen_lines.add(lineno)

            if lineno <= 0 or lineno > len(lines):
                break

            lines[lineno - 1] = "pass  # patched"

    return errors

#污点分析-对候选漏洞进行二次验证
def post_analysis(context):
    visitor = getattr(context, "visitor", None)
    if visitor is None:
        return

    for c in context.candidates:
        rule = c["rule"]
        node = c["node"]

        is_tainted = any(
            visitor.is_tainted(arg) for arg in c.get("args", [])
        )

        severity = "HIGH" if is_tainted else rule.severity

        message = (
            "User-controlled input reaches dangerous sink"
            if is_tainted else rule.description
        )

        result = rule.report(
            node,
            severity=severity,
            message=message
        )

        context.results = [
            r for r in context.results
            if not (r["lineno"] == node.lineno and r["rule_id"] == rule.id)
        ]

        context.results.append(result)
