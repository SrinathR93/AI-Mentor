"""Chart components for analytics."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_score_trend(history: list[dict]) -> None:
    if not history:
        st.info("Complete code reviews to see your improvement trend.")
        return

    df = pd.DataFrame(history)
    fig = px.line(
        df,
        x="date",
        y="score",
        markers=True,
        title="Code Quality Score Over Time",
        labels={"score": "Quality Score", "date": "Date"},
    )
    fig.update_layout(
        template="plotly_dark",
        height=350,
        yaxis_range=[0, 100],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_score_distribution(recent: list[dict]) -> None:
    if not recent:
        return

    scores = [r.get("quality_score", 0) for r in recent]
    langs = [r.get("language", "Unknown") for r in recent]

    fig = go.Figure(data=[
        go.Bar(x=langs, y=scores, marker_color="#6366f1")
    ])
    fig.update_layout(
        title="Recent Review Scores by Language",
        template="plotly_dark",
        height=300,
        yaxis_range=[0, 100],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_bug_severity_chart(bugs: list[dict]) -> None:
    if not bugs:
        return

    severity_counts = {}
    for bug in bugs:
        sev = bug.get("severity", "medium")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    df = pd.DataFrame(list(severity_counts.items()), columns=["Severity", "Count"])
    fig = px.pie(df, names="Severity", values="Count", title="Bug Severity Distribution")
    fig.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig, use_container_width=True)
