"""Minimal sidebar — 4 features only."""

import streamlit as st


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## AI Coding Mentor")
        st.caption("4 core tools")
        st.divider()

        if st.session_state.get("code"):
            lang = st.session_state.get("language", "—")
            st.success(f"{lang} · {len(st.session_state.code.splitlines())} lines")
        else:
            st.info("No code loaded")

        if st.session_state.get("analysis_result"):
            st.caption("Analysis cached — switch tabs freely")

        st.divider()
        model = st.session_state.get("active_model", "—")
        if st.session_state.get("gemini_configured"):
            st.caption(f"Model: {model}")
        else:
            st.warning("Add GEMINI_API_KEY to .env")
