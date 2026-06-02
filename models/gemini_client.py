"""Gemini API client — single-call analysis with model fallback."""

import os
import re
import time
from pathlib import Path
from typing import Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

from utils.helpers import extract_json_from_response, truncate_text

load_dotenv()

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Models that often work on free tier (tried in order)
DEFAULT_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash",
]


class QuotaExceededError(Exception):
    """API quota or rate limit hit."""

    def __init__(self, message: str, retry_seconds: float = 60):
        super().__init__(message)
        self.retry_seconds = retry_seconds


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        env_model = model_name or os.getenv("GEMINI_MODEL", "")
        self.model_names = [env_model] if env_model else []
        for m in DEFAULT_MODELS:
            if m not in self.model_names:
                self.model_names.append(m)
        self._model = None
        self.model_name = self.model_names[0]

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self._set_model(self.model_name)

    def _set_model(self, name: str) -> None:
        self.model_name = name
        self._model = genai.GenerativeModel(name)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self._model)

    @staticmethod
    def _parse_retry_seconds(error_text: str) -> float:
        match = re.search(r"retry in ([\d.]+)s", error_text, re.I)
        if match:
            return float(match.group(1)) + 2
        match = re.search(r'retry_delay.*?seconds:\s*(\d+)', error_text)
        if match:
            return float(match.group(1)) + 2
        return 60

    def _generate(self, prompt: str) -> str:
        if not self.is_configured:
            raise ValueError("Set GEMINI_API_KEY in .env file")

        prompt = truncate_text(prompt, max_len=6000)
        last_error: Optional[Exception] = None

        for model_name in self.model_names:
            try:
                self._set_model(model_name)
                response = self._model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.2,
                        "max_output_tokens": 2048,
                    },
                )
                return response.text or ""
            except Exception as e:
                last_error = e
                err = str(e).lower()
                if "429" in err or "quota" in err or "rate" in err:
                    if model_name != self.model_names[-1]:
                        continue
                    raise QuotaExceededError(
                        str(e), self._parse_retry_seconds(str(e))
                    ) from e
                if "404" in err or "not found" in err or "not supported" in err:
                    continue
                raise

        if last_error:
            raise last_error
        raise RuntimeError("No model available")

    def _generate_json(self, prompt: str) -> dict[str, Any]:
        return extract_json_from_response(self._generate(prompt))

    def analyze_all(self, code: str, language: str) -> dict[str, Any]:
        """One API call: review + bugs + DSA."""
        path = PROMPTS_DIR / "combined_analysis.txt"
        prompt = path.read_text(encoding="utf-8").format(language=language, code=code)
        return self._generate_json(prompt)
