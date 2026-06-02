# AI Coding Mentor

An intelligent coding mentor platform that helps students improve programming skills through AI-powered code review, bug detection, DSA optimization, coding challenges, and progress tracking.

Built with **Python**, **Streamlit**, **Gemini API**, and **SQLite**.

## Features (4 core tabs)

| Tab | Description |
|-----|-------------|
| **Upload Code** | Paste or upload Python, Java, C++, JavaScript |
| **AI Review** | Quality score and feedback |
| **Bug Detection** | Issues with suggested fixes |
| **DSA Analysis** | Time/space complexity and tips |

One **Analyze** button runs a single API call (saves quota). Offline fallback runs if quota is exceeded.

## Project Structure

```
AI_Coding_Mentor/
├── app.py                 # Main entry & home dashboard
├── pages/                 # Streamlit multipage routes
├── components/            # UI components (sidebar, charts, editor)
├── database/              # SQLite schema & db_manager
├── models/                # Gemini client & session state
├── prompts/               # Prompt engineering templates
├── utils/                 # Helpers, PDF, GitHub
├── assets/                # Custom CSS
├── reports/               # Generated PDF reports
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- [Google AI Studio](https://aistudio.google.com/) API key for Gemini

### 2. Installation

```bash
cd AI_Coding_Mentor
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuration

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env`:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-lite
```

### 4. Run the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Usage Workflow

1. Open the app — all 4 features are tabs on one page
2. **Upload Code** tab — paste code, click **Analyze (1 API call)**
3. Switch tabs for **Review**, **Bugs**, and **DSA** (no extra API calls)

## Database Schema

SQLite database (`database/mentor.db`) includes:

- `users` — User accounts
- `code_sessions` — Uploaded code snapshots
- `reviews` — AI review results and scores
- `bugs` — Detected bugs and fix status
- `dsa_analyses` — Complexity analysis records
- `challenges` — Generated challenges and completion
- `learning_recommendations` — Personalized learning plans
- `interview_sessions` — Mock interview history

## Deployment Guide

### Streamlit Community Cloud

1. Push the project to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set **Main file path**: `app.py`
5. Add secrets in the dashboard:

```toml
GEMINI_API_KEY = "your_key"
GEMINI_MODEL = "gemini-2.0-flash"
```

### Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t ai-coding-mentor .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key ai-coding-mentor
```

### Local Production

```bash
streamlit run app.py --server.port 8501 --server.headless true
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GEMINI_MODEL` | Model name | `gemini-2.0-flash` |

## Supported Languages

- Python (`.py`)
- Java (`.java`)
- C++ (`.cpp`, `.cc`, `.cxx`, `.hpp`)
- JavaScript (`.js`, `.jsx`, `.ts`, `.tsx`)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key error | Verify `.env` has `GEMINI_API_KEY` and restart Streamlit |
| JSON parse errors | Re-run analysis; model occasionally returns non-JSON |
| PDF generation fails | Ensure `fpdf2` is installed |
| Voice not working | `pip install gTTS` and check internet for TTS |
| GitHub rate limit | Unauthenticated API has low limits; add delays between requests |

## License

MIT License — use freely for education and projects.

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [Google Gemini](https://ai.google.dev/)
- [Pygments](https://pygments.org/) for syntax highlighting
