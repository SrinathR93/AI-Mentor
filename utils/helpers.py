"""Shared helper utilities."""

import json
import re
from typing import Any, Optional

SUPPORTED_LANGUAGES = {
    "Python": {"ext": [".py"], "lexer": "python"},
    "Java": {"ext": [".java"], "lexer": "java"},
    "C++": {"ext": [".cpp", ".cc", ".cxx", ".hpp"], "lexer": "cpp"},
    "JavaScript": {"ext": [".js", ".jsx", ".ts", ".tsx"], "lexer": "javascript"},
}

LANGUAGE_MAP = {
    ".py": "Python",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "JavaScript",
    ".tsx": "JavaScript",
}


def detect_language_from_filename(filename: str) -> Optional[str]:
    for ext, lang in LANGUAGE_MAP.items():
        if filename.lower().endswith(ext):
            return lang
    return None


def extract_json_from_response(text: str) -> dict[str, Any]:
    """Extract JSON object from LLM response, with fallback parsing."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"raw_response": text, "parse_error": True}


def truncate_text(text: str, max_len: int = 12000) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "\n\n... [truncated for API limits]"


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
