import json


def parse_result(text):
    import json

    try:
        # 如果已经是 dict，就直接返回
        if isinstance(text, dict):
            return text

        if isinstance(text, str):
            text = text.strip()

            if text.startswith("```json"):
                text = text[len("```json"):].strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            return json.loads(text)

        # 其他类型
        raise ValueError("不支持的输入类型")

    except Exception as e:
        return {
            "has_vuln": False,
            "vuln_type": "解析失败",
            "description": str(text),
            "fix": "请检查AI输出格式"
        }