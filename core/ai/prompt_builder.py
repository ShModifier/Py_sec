def build_full_prompt(code: str) -> str:
    return f"""
你是一个专业的Python代码安全审计专家，请分析以下代码是否存在安全漏洞。

【分析要求】
1. 可以识别多个漏洞
2. 每个漏洞必须独立描述
3. 尽量给出具体行号（lineno）
4. 漏洞类型要标准化（如 RCE、SQL注入、命令执行等）
5. 给出修复建议，修复建议要具体
【代码如下】
{code}
【输出格式】（必须严格JSON！！！）
{{
    "has_vuln": true/false,
    "vulnerabilities": [
        {{
            "severity": "HIGH/MEDIUM/LOW"
            "vuln_type": "...",
            "lineno": 10,
            "description": "...",
            "fix": "..."
        }}
    ]
}}
【注意】
- 如果没有漏洞，返回：
{{
    "has_vuln": false,
    "vulnerabilities": []
}}
"""


def build_snippet_prompt(issues, source_code: str) -> str:
    lines = source_code.splitlines()

    prompt = """
你是一个专业的Python代码安全审计专家。
以下是通过静态分析筛选出的“疑似漏洞代码片段”，请进行进一步确认，并给出修复建议。

【分析要求】
1. 每个问题独立分析
2. 判断是否真实漏洞（可能存在误报）,
确定为误报就可以从结果中删除，如果判定为“可能是漏洞但无法判别”就将severity设置为LOW并在description中标注ai分析后认定为可疑代码
3. 漏洞类型要标准化（如 RCE、SQL注入、命令执行等）
4. 给出修复建议，修复建议要具体
5. 返回JSON格式

"""

    MAX_ITEMS = 10

    seen = set()
    filtered = []
    for r in issues:
        key = (r.get("lineno"), r.get("rule_id"))
        if key not in seen:
            seen.add(key)
            filtered.append(r)

    filtered = filtered[:MAX_ITEMS]
    for i, r in enumerate(filtered, 1):
        lineno = r.get("lineno", 1)
        start = max(0, lineno - 5)
        end = min(len(lines), lineno + 5)
        snippet = "\n".join(lines[start:end])
        prompt += f"""
【问题 {i}】
漏洞类型（静态分析）：{r.get("rule_id")}
位置：第 {lineno} 行
描述：{r.get("message")}

代码片段：
{snippet}
----------------------
"""
    prompt += """
    
【输出格式】（必须严格JSON！！！）

{{
    "has_vuln": true/false,
    "vulnerabilities": [
        {{
            "severity": "HIGH/MEDIUM/LOW"
            "vuln_type": "...",
            "lineno": 10,
            "description": "...",
            "fix": "..."
        }}
    ]
}}

【注意】
- 如果没有漏洞，返回：
{{
    "has_vuln": false,
    "vulnerabilities": []
}}
"""
    return prompt