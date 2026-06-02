"""Offline fallback when Gemini quota is unavailable."""

import re
from typing import Any


def analyze_locally(code: str, language: str) -> dict[str, Any]:
    """Basic static checks — no API needed."""
    lines = code.splitlines()
    bugs = []

    if "eval(" in code:
        bugs.append({
            "type": "security",
            "severity": "high",
            "description": "eval() can execute arbitrary code.",
            "affected_code": "eval(...)",
            "suggested_fix": "Use safe parsing instead of eval.",
        })
    if re.search(r"except\s*:", code):
        bugs.append({
            "type": "runtime",
            "severity": "medium",
            "description": "Bare except catches all errors and hides bugs.",
            "affected_code": "except:",
            "suggested_fix": "except SpecificError as e:",
        })
    if language == "Python" and re.search(r"==\s*None|None\s*==", code):
        bugs.append({
            "type": "logical",
            "severity": "low",
            "description": "Compare None with 'is None' not ==.",
            "affected_code": "== None",
            "suggested_fix": "is None",
        })

    long_lines = sum(1 for ln in lines if len(ln) > 100)
    score = 75
    if long_lines > 3:
        score -= 10
    if len(lines) > 200:
        score -= 10
    score = max(40, min(90, score))

    nested = code.count("for ") + code.count("while ")
    time_c = "O(n)" if nested <= 1 else "O(n²) or higher"
    if "sort(" in code or ".sort(" in code:
        time_c = "O(n log n)"

    return {
        "quality_score": score,
        "summary": "Offline analysis (API quota exceeded). Connect a valid Gemini API key for full AI review.",
        "readability": "Check line length and add comments for complex logic.",
        "maintainability": "Split large functions and use clear names.",
        "improvements": ["Enable Gemini API for detailed feedback", "Add unit tests"],
        "bugs": bugs,
        "dsa": {
            "time_complexity": time_c,
            "space_complexity": "O(n)" if "[]" in code or "list" in code else "O(1)",
            "explanation": "Estimated from loop/nesting patterns (offline).",
            "optimized_time": time_c,
            "optimization_tip": "Use hash maps or sorting where lookups repeat.",
        },
        "_offline": True,
    }
