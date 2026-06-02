"""PDF report generation for code reviews."""

from datetime import datetime
from pathlib import Path

from fpdf import FPDF

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


class MentorReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "AI Coding Mentor - Review Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")


def generate_review_pdf(
    language: str,
    code: str,
    review: dict,
    bugs: list | None = None,
    dsa: dict | None = None,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = REPORTS_DIR / f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    pdf = MentorReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Language: {language}", ln=True)
    pdf.cell(0, 8, f"Quality Score: {review.get('quality_score', 'N/A')}/100", ln=True)
    pdf.ln(5)

    sections = [
        ("Summary", review.get("summary", "")),
        ("Readability", review.get("readability", {}).get("analysis", "")),
        ("Maintainability", review.get("maintainability", {}).get("analysis", "")),
        ("Best Practices", "\n".join(f"- {p}" for p in review.get("best_practices", []))),
        ("Naming Conventions", review.get("naming_conventions", {}).get("feedback", "")),
    ]

    for title, content in sections:
        if content:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, title, ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, str(content)[:2000])
            pdf.ln(3)

    if bugs:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Bugs Detected", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for i, bug in enumerate(bugs[:10], 1):
            pdf.multi_cell(
                0,
                6,
                f"{i}. [{bug.get('severity', '')}] {bug.get('type', '')}: {bug.get('description', '')[:300]}",
            )

    if dsa:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "DSA Analysis", ln=True)
        pdf.set_font("Helvetica", "", 10)
        current = dsa.get("current", {})
        pdf.multi_cell(
            0,
            6,
            f"Time: {current.get('time_complexity', 'N/A')} | Space: {current.get('space_complexity', 'N/A')}",
        )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Source Code", ln=True)
    pdf.set_font("Courier", "", 8)
    for line in code.split("\n")[:80]:
        pdf.multi_cell(0, 4, line[:100])

    pdf.output(str(filename))
    return filename
