"""Streamlit session state."""

import streamlit as st

from database.db_manager import init_db


def init_session_state() -> None:
    defaults = {
        "code": "",
        "language": "Python",
        "session_id": None,
        "analysis_result": None,
        "active_model": None,
        "db_initialized": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.db_initialized:
        init_db()
        st.session_state.db_initialized = True
