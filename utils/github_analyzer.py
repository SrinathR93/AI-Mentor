"""GitHub repository analysis utilities."""

import re
from typing import Any, Optional

import requests


def parse_github_url(url: str) -> Optional[tuple[str, str]]:
    patterns = [
        r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"github\.com/([^/]+)/([^/]+)/",
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            owner, repo = match.group(1), match.group(2).replace(".git", "")
            return owner, repo
    return None


def fetch_repo_info(owner: str, repo: str) -> dict[str, Any]:
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        resp = requests.get(api_url, timeout=15, headers={"Accept": "application/vnd.github+json"})
        if resp.status_code != 200:
            return {"error": f"GitHub API returned {resp.status_code}"}
        data = resp.json()
        return {
            "name": data.get("full_name"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "topics": data.get("topics", []),
            "url": data.get("html_url"),
        }
    except requests.RequestException as e:
        return {"error": str(e)}


def fetch_repo_readme(owner: str, repo: str) -> str:
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    try:
        resp = requests.get(
            api_url,
            timeout=15,
            headers={"Accept": "application/vnd.github.raw"},
        )
        if resp.status_code == 200:
            return resp.text[:8000]
    except requests.RequestException:
        pass
    return ""
