"""Code parsing and validation utilities."""

from pathlib import Path
from typing import Optional

from utils.helpers import LANGUAGE_MAP, SUPPORTED_LANGUAGES


def read_uploaded_file(uploaded_file) -> tuple[str, Optional[str]]:
    """Read Streamlit uploaded file and detect language."""
    content = uploaded_file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    filename = uploaded_file.name
    language = None
    for ext, lang in LANGUAGE_MAP.items():
        if filename.lower().endswith(ext):
            language = lang
            break
    return content, language


def validate_code(code: str, language: str) -> tuple[bool, str]:
    if not code or not code.strip():
        return False, "Code cannot be empty."
    if language not in SUPPORTED_LANGUAGES:
        return False, f"Unsupported language: {language}"
    if len(code) > 50000:
        return False, "Code exceeds maximum length (50,000 characters)."
    return True, ""


def get_file_extension(language: str) -> str:
    ext_map = {"Python": ".py", "Java": ".java", "C++": ".cpp", "JavaScript": ".js"}
    return ext_map.get(language, ".txt")
