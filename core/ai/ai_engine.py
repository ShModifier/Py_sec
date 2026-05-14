from .prompt_builder import build_full_prompt,build_snippet_prompt
from .result_parser import parse_result


class AIAnalyzer:
    def __init__(self, model):
        self.model = model

    def analyze(self, code: str):
        prompt = build_full_prompt(code)
        raw_result = self.model.generate(prompt)

        return parse_result(raw_result)

    def analyze_with_issues(self, code: str, issues):
        prompt = build_snippet_prompt(issues, code)
        raw_result = self.model.generate(prompt)
        return parse_result(raw_result)