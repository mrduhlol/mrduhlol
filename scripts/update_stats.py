"""Render the terminal header with the current public GitHub profile totals."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


USERNAME = os.getenv("USERNAME", "mrduhlol")
TOKEN = os.getenv("GITHUB_TOKEN")
API_URL = "https://api.github.com"


def github_request(path: str) -> tuple[object, str]:
    """Return a GitHub REST response body and its Link header."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mrduhlol-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = Request(f"{API_URL}{path}", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response), response.headers.get("Link", "")


def paginated(path: str) -> list[dict[str, object]]:
    """Fetch every page from a GitHub list endpoint."""
    items: list[dict[str, object]] = []
    page = 1
    while True:
        response, _ = github_request(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
        current_page = response if isinstance(response, list) else []
        items.extend(item for item in current_page if isinstance(item, dict))
        if len(current_page) < 100:
            return items
        page += 1


def commit_count(repository: str) -> int:
    """Count commits authored by this profile, rather than repository history."""
    try:
        response, link_header = github_request(
            f"/repos/{USERNAME}/{quote(repository)}/commits?author={quote(USERNAME)}&per_page=1"
        )
    except HTTPError as error:
        # Empty repositories return 409 from this endpoint.
        if error.code == 409:
            return 0
        raise

    if not response:
        return 0
    match = re.search(r"[?&]page=(\d+)>; rel=\"last\"", link_header)
    return int(match.group(1)) if match else 1


def main() -> None:
    profile, _ = github_request(f"/users/{quote(USERNAME)}")
    repositories = paginated(f"/users/{quote(USERNAME)}/repos?type=owner&sort=updated")

    original_repositories = [repository for repository in repositories if not repository.get("fork", False)]
    stars = 0
    commits = 0
    loc = 0
    for repository in original_repositories:
        stars += int(repository.get("stargazers_count", 0))
        name = str(repository["name"])
        commits += commit_count(name)
        languages, _ = github_request(f"/repos/{USERNAME}/{quote(name)}/languages")
        if isinstance(languages, dict):
            loc += sum(int(bytes_of_code) for bytes_of_code in languages.values())

    template_path = Path("assets/terminal.svg.j2")
    output_path = Path("assets/terminal.svg")
    svg = template_path.read_text(encoding="utf-8")
    values = {
        # Match the public repository count shown on the GitHub profile itself.
        "repos": int(profile["public_repos"]),
        "stars": stars,
        "followers": int(profile["followers"]),
        "commits": commits,
        "loc": f"{loc:,}",
    }
    for key, value in values.items():
        svg = svg.replace(f"{{{{ {key} }}}}", str(value))

    output_path.write_text(svg, encoding="utf-8", newline="\n")
    print("Generated assets/terminal.svg")


if __name__ == "__main__":
    main()
