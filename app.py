"""AI Coding Mentor — 4 features, single app, one API call."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

from components.sidebar import render_sidebar
from database.db_manager import init_db, save_bugs, save_code_session, save_dsa_analysis, save_review
from models.gemini_client import GeminiClient, QuotaExceededError
from models.session_state import init_session_state
from utils.code_parser import validate_code
from utils.helpers import SUPPORTED_LANGUAGES
from utils.local_analyzer import analyze_locally

load_dotenv(ROOT / ".env")

st.set_page_config(
    page_title="AI Coding Mentor",
    page_icon="🧑‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
init_db()

client = GeminiClient()
st.session_state.gemini_configured = client.is_configured
render_sidebar()

st.title("AI Coding Mentor")
st.caption("Upload → Analyze once → View Review, Bugs, and DSA (saves API quota)")

tab_upload, tab_review, tab_bugs, tab_dsa = st.tabs(
    ["1. Upload Code", "2. AI Review", "3. Bug Detection", "4. DSA Analysis"]
)

# —— Tab 1: Upload ——
with tab_upload:
    col_lang, col_file = st.columns([1, 2])
    with col_lang:
        language = st.selectbox(
            "Language",
            list(SUPPORTED_LANGUAGES.keys()),
            index=list(SUPPORTED_LANGUAGES.keys()).index(
                st.session_state.get("language", "Python")
            )
            if st.session_state.get("language") in SUPPORTED_LANGUAGES
            else 0,
        )
    with col_file:
        uploaded = st.file_uploader("Upload file", type=["py", "java", "cpp", "js", "ts", "cc"])

    code = st.text_area(
        "Paste code",
        value=st.session_state.get("code", ""),
        height=280,
        placeholder="# Paste your code here...",
    )

    if uploaded:
        raw = uploaded.read()
        code = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
        from utils.code_parser import detect_language_from_filename

        detected = detect_language_from_filename(uploaded.name)
        if detected:
            language = detected

    c1, c2, c3 = st.columns(3)
    with c1:
        save_clicked = st.button("Save Code", type="primary", use_container_width=True)
    with c2:
        analyze_clicked = st.button("Analyze (1 API call)", type="primary", use_container_width=True)
    with c3:
        if st.button("Clear", use_container_width=True):
            for key in ("code", "analysis_result", "session_id"):
                st.session_state[key] = None if key != "code" else ""
            st.rerun()

    if save_clicked:
        ok, msg = validate_code(code, language)
        if ok:
            sid = save_code_session(language, code)
            st.session_state.code = code
            st.session_state.language = language
            st.session_state.session_id = sid
            st.success("Code saved.")
        else:
            st.error(msg)

    if analyze_clicked:
        ok, msg = validate_code(code, language)
        if not ok:
            st.error(msg)
        else:
            st.session_state.code = code
            st.session_state.language = language
            if not st.session_state.get("session_id"):
                st.session_state.session_id = save_code_session(language, code)

            result = None
            if client.is_configured:
                with st.spinner("Analyzing (one request)..."):
                    try:
                        result = client.analyze_all(code, language)
                        st.session_state.active_model = client.model_name
                    except QuotaExceededError as e:
                        st.warning(
                            f"API quota exceeded. Using offline analysis. "
                            f"Retry AI in ~{int(e.retry_seconds)}s or use another model in .env"
                        )
                        result = analyze_locally(code, language)
                    except Exception as e:
                        err = str(e)
                        if "429" in err or "quota" in err.lower():
                            st.warning("API quota exceeded — offline analysis used.")
                            result = analyze_locally(code, language)
                        else:
                            st.error(f"Analysis failed: {e}")
            else:
                st.warning("No API key — using offline analysis.")
                result = analyze_locally(code, language)

            if result:
                st.session_state.analysis_result = result
                sid = st.session_state.session_id
                save_review(
                    sid,
                    {
                        "quality_score": result.get("quality_score", 0),
                        "readability_score": 0,
                        "maintainability_score": 0,
                        "summary": result.get("summary", ""),
                        "readability": {"analysis": result.get("readability", "")},
                        "maintainability": {"analysis": result.get("maintainability", "")},
                        "improvements": result.get("improvements", []),
                    },
                )
                if result.get("bugs"):
                    save_bugs(sid, result["bugs"])
                dsa = result.get("dsa", {})
                if dsa:
                    save_dsa_analysis(
                        sid,
                        {
                            "current": {
                                "time_complexity": dsa.get("time_complexity"),
                                "space_complexity": dsa.get("space_complexity"),
                            },
                            "optimized": {"time_complexity": dsa.get("optimized_time")},
                        },
                    )
                if result.get("_offline"):
                    st.info("Offline mode — set GEMINI_API_KEY and GEMINI_MODEL=gemini-2.0-flash-lite in .env")
                else:
                    st.success(f"Done using {client.model_name}")

    if st.session_state.get("code") and not analyze_clicked:
        st.caption("Click **Analyze (1 API call)** to run review, bugs, and DSA together.")

# —— Shared analysis ——
data = st.session_state.get("analysis_result")

def _need_analysis():
    if not st.session_state.get("code"):
        st.warning("Upload code in tab 1 and click **Analyze**.")
        return False
    if not data:
        st.warning("Click **Analyze (1 API call)** on the Upload tab first.")
        return False
    return True

# —— Tab 2: Review ——
with tab_review:
    if _need_analysis():
        if data.get("_offline"):
            st.info("Showing offline results — API quota was exceeded.")
        st.metric("Quality Score", f"{data.get('quality_score', 0)}/100")
        st.subheader("Summary")
        st.write(data.get("summary", ""))
        st.subheader("Readability")
        st.write(data.get("readability", ""))
        st.subheader("Maintainability")
        st.write(data.get("maintainability", ""))
        st.subheader("Improvements")
        for item in data.get("improvements", []):
            st.markdown(f"- {item}")

# —— Tab 3: Bugs ——
with tab_bugs:
    if _need_analysis():
        bugs = data.get("bugs", [])
        st.metric("Bugs Found", len(bugs))
        if not bugs:
            st.success("No major bugs detected.")
        for i, bug in enumerate(bugs, 1):
            st.markdown(f"**{i}. [{bug.get('severity', '')}] {bug.get('type', '')}**")
            st.write(bug.get("description", ""))
            if bug.get("affected_code"):
                st.code(bug["affected_code"])
            if bug.get("suggested_fix"):
                st.markdown("Fix:")
                st.code(bug["suggested_fix"])

# —— Tab 4: DSA ——
with tab_dsa:
    if _need_analysis():
        dsa = data.get("dsa", {})
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Time", dsa.get("time_complexity", "N/A"))
            st.metric("Space", dsa.get("space_complexity", "N/A"))
        with c2:
            st.metric("Optimized Time", dsa.get("optimized_time", "N/A"))
        st.write(dsa.get("explanation", ""))
        if dsa.get("optimization_tip"):
            st.info(dsa["optimization_tip"])
