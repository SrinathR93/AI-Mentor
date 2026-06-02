"""SQLite database manager for AI Coding Mentor."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parent / "mentor.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def init_db() -> None:
    """Initialize database with schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username, email) VALUES (1, 'default_user', 'user@example.com')"
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_code_session(language: str, code: str, filename: Optional[str] = None) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO code_sessions (user_id, language, code_snippet, filename) VALUES (1, ?, ?, ?)",
            (language, code, filename),
        )
        conn.commit()
        return cur.lastrowid


def save_review(session_id: int, data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO reviews (session_id, quality_score, readability_score,
               maintainability_score, review_json) VALUES (?, ?, ?, ?, ?)""",
            (
                session_id,
                data.get("quality_score", 0),
                data.get("readability_score", 0),
                data.get("maintainability_score", 0),
                json.dumps(data),
            ),
        )
        conn.commit()
        return cur.lastrowid


def save_bugs(session_id: int, bugs: list[dict]) -> None:
    with get_connection() as conn:
        for bug in bugs:
            conn.execute(
                """INSERT INTO bugs (session_id, bug_type, severity, description,
                   affected_code, suggested_fix) VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    bug.get("type", "unknown"),
                    bug.get("severity", "medium"),
                    bug.get("description", ""),
                    bug.get("affected_code", ""),
                    bug.get("suggested_fix", ""),
                ),
            )
        conn.commit()


def save_dsa_analysis(session_id: int, data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO dsa_analyses (session_id, time_complexity, space_complexity, analysis_json)
               VALUES (?, ?, ?, ?)""",
            (
                session_id,
                data.get("current", {}).get("time_complexity", "N/A"),
                data.get("current", {}).get("space_complexity", "N/A"),
                json.dumps(data),
            ),
        )
        conn.commit()
        return cur.lastrowid


def save_challenge(session_id: Optional[int], challenge: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO challenges (session_id, difficulty, challenge_type,
               problem_statement, examples, constraints, expected_complexity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                challenge.get("difficulty", "medium"),
                challenge.get("type", "DSA"),
                challenge.get("problem_statement", ""),
                challenge.get("examples", ""),
                challenge.get("constraints", ""),
                challenge.get("expected_complexity", ""),
            ),
        )
        conn.commit()
        return cur.lastrowid


def mark_challenge_completed(challenge_id: int) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE challenges SET is_completed = 1 WHERE id = ?", (challenge_id,))
        conn.commit()


def mark_bug_fixed(bug_id: int) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE bugs SET is_fixed = 1 WHERE id = ?", (bug_id,))
        conn.commit()


def save_learning_recommendations(session_id: int, data: dict) -> int:
    with get_connection() as conn:
        weak = json.dumps(data.get("weak_areas", []))
        cur = conn.execute(
            """INSERT INTO learning_recommendations (session_id, weak_areas, recommendations_json)
               VALUES (?, ?, ?)""",
            (session_id, weak, json.dumps(data)),
        )
        conn.commit()
        return cur.lastrowid


def save_interview_session(resume_text: str, role: str, questions: dict, feedback: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO interview_sessions (resume_text, role, questions_json, feedback_json)
               VALUES (?, ?, ?, ?)""",
            (resume_text, role, json.dumps(questions), json.dumps(feedback)),
        )
        conn.commit()
        return cur.lastrowid


def get_dashboard_stats() -> dict[str, Any]:
    with get_connection() as conn:
        total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        bugs_fixed = conn.execute("SELECT COUNT(*) FROM bugs WHERE is_fixed = 1").fetchone()[0]
        challenges_done = conn.execute(
            "SELECT COUNT(*) FROM challenges WHERE is_completed = 1"
        ).fetchone()[0]
        avg_score_row = conn.execute("SELECT AVG(quality_score) FROM reviews").fetchone()
        avg_score = round(avg_score_row[0] or 0, 1)

        score_history = conn.execute(
            """SELECT quality_score, created_at FROM reviews
               ORDER BY created_at DESC LIMIT 20"""
        ).fetchall()

        recent_reviews = conn.execute(
            """SELECT r.quality_score, r.created_at, cs.language
               FROM reviews r JOIN code_sessions cs ON r.session_id = cs.id
               ORDER BY r.created_at DESC LIMIT 10"""
        ).fetchall()

    history = [
        {"score": row["quality_score"], "date": row["created_at"][:10]}
        for row in reversed(score_history)
    ]

    return {
        "total_reviews": total_reviews,
        "bugs_fixed": bugs_fixed,
        "challenges_completed": challenges_done,
        "average_score": avg_score,
        "score_history": history,
        "recent_reviews": [dict(r) for r in recent_reviews],
    }


def get_recent_bugs(limit: int = 10) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, bug_type, severity, description, is_fixed, created_at
               FROM bugs ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_recent_challenges(limit: int = 10) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, difficulty, challenge_type, problem_statement, is_completed, created_at
               FROM challenges ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
