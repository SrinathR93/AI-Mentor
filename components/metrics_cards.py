"""Metric cards for dashboard display."""

import streamlit as st


def render_metric_row(stats: dict) -> None:
    cols = st.columns(4)
    metrics = [
        ("Total Reviews", stats.get("total_reviews", 0), "🔍"),
        ("Bugs Fixed", stats.get("bugs_fixed", 0), "🐛"),
        ("Challenges Done", stats.get("challenges_completed", 0), "🎯"),
        ("Avg Code Score", f"{stats.get('average_score', 0)}/100", "⭐"),
    ]
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.metric(label=f"{icon} {label}", value=value)


def score_color_class(score: int) -> str:
    if score >= 80:
        return "score-excellent"
    if score >= 60:
        return "score-good"
    if score >= 40:
        return "score-fair"
    return "score-poor"


def render_score_badge(score: int, label: str = "Quality Score") -> None:
    css_class = score_color_class(score)
    st.markdown(
        f'<p class="{css_class}" style="font-size:2rem;font-weight:bold;">{label}: {score}/100</p>',
        unsafe_allow_html=True,
    )
