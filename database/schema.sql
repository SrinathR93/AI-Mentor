-- AI Coding Mentor - SQLite Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS code_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    language TEXT NOT NULL,
    code_snippet TEXT NOT NULL,
    filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    quality_score INTEGER,
    readability_score INTEGER,
    maintainability_score INTEGER,
    review_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES code_sessions(id)
);

CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    bug_type TEXT,
    severity TEXT,
    description TEXT,
    affected_code TEXT,
    suggested_fix TEXT,
    is_fixed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES code_sessions(id)
);

CREATE TABLE IF NOT EXISTS dsa_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    time_complexity TEXT,
    space_complexity TEXT,
    analysis_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES code_sessions(id)
);

CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    difficulty TEXT,
    challenge_type TEXT,
    problem_statement TEXT,
    examples TEXT,
    constraints TEXT,
    expected_complexity TEXT,
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES code_sessions(id)
);

CREATE TABLE IF NOT EXISTS learning_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    weak_areas TEXT,
    recommendations_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES code_sessions(id)
);

CREATE TABLE IF NOT EXISTS interview_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_text TEXT,
    role TEXT,
    questions_json TEXT,
    feedback_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_session ON reviews(session_id);
CREATE INDEX IF NOT EXISTS idx_bugs_session ON bugs(session_id);
CREATE INDEX IF NOT EXISTS idx_challenges_completed ON challenges(is_completed);
