from core.analyzer import analyze_entry


class ScanController:

    def run_scan(self, file_path, use_static=True, use_ai=False,use_assist=True):
        results = analyze_entry(
            file_path,
            use_static=use_static,
            use_ai=use_ai,
            use_assist=use_assist
        )

        if results is None:
            results = []

        if isinstance(results, dict):
            return {
                "status": results.get("status", "error"),
                "issues": results.get("issues", []) or []
            }

        if not isinstance(results, list):
            results = []

        return {
            "status": "ok",
            "issues": results
        }