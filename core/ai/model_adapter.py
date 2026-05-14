import os
from abc import ABC, abstractmethod
from openai import OpenAI
import json

class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        #输入prompt，返回模型输出
        pass

class DeepSeekModel(BaseModel):
    def __init__(self, base_url: str, model_name: str, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model_name = model_name
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码安全审计专家"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                stream=False
            )
            text = response.choices[0].message.content
            if text.startswith("```json"):
                text = text[len("```json"):].strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            try:
                result = json.loads(text.strip())  # strip 去掉前后空行
                # 确保返回格式完整
                if "has_vuln" not in result:
                    result = {
                        "has_vuln": False,
                        "vuln_type": "AI返回缺少has_vuln",
                        "description": text.strip(),
                        "fix": "请检查AI模型返回格式"
                    }
            except json.JSONDecodeError:
                # JSON解析失败
                result = {
                    "has_vuln": False,
                    "vuln_type": "AI返回格式错误",
                    "description": text.strip() or "AI返回空内容",
                    "fix": "请检查AI模型返回格式"
                }
            return result
        except Exception as e:
            print("API调用异常：", e)
            return f"""
{{
    "has_vuln": false,
    "vuln_type": "API调用失败",
    "description": "{str(e)}",
    "fix": "请检查API Key或网络连接"
}}
"""

class QwenModel(BaseModel):
    def __init__(self, base_url: str, model_name: str, api_key: str):
        self.client = OpenAI(
        api_key=api_key,
        base_url=base_url
        )
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码安全审计专家"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            text = response.choices[0].message.content
            result = json.loads(text)
            return result

        except Exception as e:
            return f"""
{{
    "has_vuln": false,
    "vuln_type": "API调用失败",
    "description": "{str(e)}",
    "fix": "请检查通义千问API Key或网络"
}}
"""

class OpenAIModel(BaseModel):
    def __init__(self, api_key: str, model_name: str, base_url: str = None):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码安全审计专家"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0
            )

            text = response.choices[0].message.content.strip()

            if text.startswith("```json"):
                text = text[len("```json"):].strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            # ===== JSON解析 =====
            try:
                result = json.loads(text)

                if "has_vuln" not in result:
                    return {
                        "has_vuln": False,
                        "vuln_type": "missing_field",
                        "description": text,
                        "fix": "AI返回缺少字段"
                    }

                return result

            except json.JSONDecodeError:
                return {
                    "has_vuln": False,
                    "vuln_type": "json_parse_error",
                    "description": text,
                    "fix": "模型输出不是合法JSON"
                }

        except Exception as e:
            return {
                "has_vuln": False,
                "vuln_type": "api_error",
                "description": str(e),
                "fix": "请检查API Key / 网络 / 模型名称"
            }








def get_model(model_type, **kwargs):
    if model_type == "deepseek":
        return DeepSeekModel(api_key=kwargs.get("api_key"))

    elif model_type == "qwen":
        return QwenModel(api_key=kwargs.get("api_key"))

    else:
        raise ValueError(f"Unsupported model: {model_type}")