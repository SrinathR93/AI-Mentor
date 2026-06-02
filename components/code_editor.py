"""Syntax-highlighted code display component."""

import streamlit as st
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from utils.helpers import SUPPORTED_LANGUAGES

LEXER_MAP = {
    "Python": "python",
    "Java": "java",
    "C++": "cpp",
    "JavaScript": "javascript",
}


def render_code_display(code: str, language: str, height: int = 400) -> None:
    lexer_name = LEXER_MAP.get(language, "python")
    try:
        lexer = get_lexer_by_name(lexer_name)
    except Exception:
        lexer = guess_lexer(code)

    formatter = HtmlFormatter(style="monokai", noclasses=False, cssstyles="padding: 1em;")
    highlighted = highlight(code, lexer, formatter)
    css = formatter.get_style_defs(".highlight")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="max-height:{height}px; overflow:auto; border-radius:8px;">{highlighted}</div>',
        unsafe_allow_html=True,
    )


def render_code_input() -> tuple[str, str]:
    col1, col2 = st.columns([2, 1])
    with col1:
        language = st.selectbox(
            "Programming Language",
            list(SUPPORTED_LANGUAGES.keys()),
            index=list(SUPPORTED_LANGUAGES.keys()).index(
                st.session_state.get("language", "Python")
            )
            if st.session_state.get("language") in SUPPORTED_LANGUAGES
            else 0,
        )
    with col2:
        uploaded = st.file_uploader(
            "Upload file",
            type=["py", "java", "cpp", "cc", "js", "jsx", "ts", "tsx", "hpp"],
            help="Supported: Python, Java, C++, JavaScript",
        )

    default_code = st.session_state.get("code", "")
    code = st.text_area(
        "Paste your code here",
        value=default_code,
        height=350,
        placeholder="# Paste or upload your code...",
    )

    if uploaded:
        from utils.code_parser import read_uploaded_file

        file_content, detected_lang = read_uploaded_file(uploaded)
        if file_content:
            code = file_content
            if detected_lang:
                language = detected_lang
            st.session_state.filename = uploaded.name

    return code, language
