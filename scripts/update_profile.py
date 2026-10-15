"""Build the organization profile from public repository metadata; no dependencies."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ORG = "Nousphera"
EXCLUDED = {".github", "nousphera.github.io"}
ASSET = f"https://raw.githubusercontent.com/{ORG}/.github/main/profile/assets"


def fetch_repositories(request=None):
    """Read every page. Any incomplete/failed response aborts the update."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Nousphera-profile"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def read(url):
        for attempt in range(3):
            try:
                with urlopen(Request(url, headers=headers), timeout=30) as response:
                    return json.load(response)
            except (HTTPError, URLError) as error:
                retry = not isinstance(error, HTTPError) or error.code in (429, 500, 502, 503, 504)
                if not retry or attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    request = request or read
    records = []
    for page in range(1, 101):
        batch = request(f"https://api.github.com/orgs/{ORG}/repos?type=public&sort=full_name&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Expected a repository list")
        records.extend(batch)
        if len(batch) < 100:
            return records
    raise ValueError("Repository pagination exceeded its safety limit")


def select_projects(records):
    projects, seen = [], set()
    for item in records:
        name = item["name"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name.lower() in seen:
            raise ValueError(f"Invalid or repeated repository name: {name}")
        seen.add(name.lower())
        if item.get("owner", {}).get("login", "").lower() != ORG.lower():
            raise ValueError("Unexpected repository owner")
        if item.get("private") is not False or name.lower() in EXCLUDED:
            continue
        stars = item["stargazers_count"]
        if isinstance(stars, bool) or not isinstance(stars, int) or stars < 0:
            raise ValueError("Invalid star count")
        projects.append({
            "name": name,
            "url": f"https://github.com/{ORG}/{name}",
            "description": item.get("description") or "Research code and resources.",
            "stars": stars,
            "archived": bool(item.get("archived")),
            "fork": bool(item.get("fork")),
        })
    if not projects:
        raise ValueError("No public projects returned; preserving the previous snapshot")
    return sorted(projects, key=lambda p: (-p["stars"], p["name"].lower()))


def update_history(history, projects, today):
    """Keep one actual snapshot per UTC date; never synthesize earlier counts."""
    date.fromisoformat(today)
    snapshot = {"date": today, "stars": sum(p["stars"] for p in projects),
                "repositories": {p["name"]: p["stars"] for p in projects}}
    indexed = {row["date"]: row for row in history}
    if indexed and today < max(indexed):
        raise ValueError("Refusing to replace history with a snapshot from the past")
    indexed[today] = snapshot
    return [indexed[day] for day in sorted(indexed)]


def safe_text(value):
    text = escape(value).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")
    for char in "[]`*_\\":
        text = text.replace(char, f"&#{ord(char)};")
    return text


def icon(name):
    return f'<picture><source media="(prefers-color-scheme: dark)" srcset="{ASSET}/{name}-dark.svg"><img src="{ASSET}/{name}-light.svg" width="18" height="18" alt=""></picture>'


def render_catalog(catalog, projects):
    live = {p["name"]: p for p in projects}
    known, blocks = set(), []
    for group in catalog:
        rows = []
        for p in group["projects"]:
            name = p["repo"]
            if name in known:
                raise ValueError(f"Duplicate catalog entry: {name}")
            known.add(name)
            if name not in live:
                continue
            rows.append(f'| **[{name}]({live[name]["url"]})** | {p["summary"]}<br>[Project]({p["project"]}) · [Paper]({p["paper"]}) |')
        if rows:
            blocks.append(f'<details>\n<summary>{icon(group["icon"])} <b>{group["title"]}</b> · {len(rows)} projects</summary>\n\n{group["summary"]}\n\n| Project | Method and resources |\n| :--- | :--- |\n' + "\n".join(rows) + "\n\n</details>")
    extra = [p for p in projects if p["name"] not in known]
    if extra:
        rows = [f'| **[{p["name"]}]({p["url"]})** | {safe_text(p["description"])} |' for p in extra]
        blocks.append('<details>\n<summary><b>More projects</b></summary>\n\n| Project | Focus |\n| :--- | :--- |\n' + "\n".join(rows) + "\n\n</details>")
    return "\n\n".join(blocks)


def render_trend(history, dark=False):
    bg, fg, muted, line = ("#0d1117", "#e6edf3", "#9daebf", "#79b8ff") if dark else ("#f6f8fb", "#1f3048", "#5d6b80", "#245bb2")
    values = history[-90:]
    counts = [x["stars"] for x in values]
    top = max(max(counts), 1)
    points = [(70 + (720 * i / (len(values)-1) if len(values)>1 else 360), 164 - 85 * y / top) for i,y in enumerate(counts)]
    label = "First daily snapshot" if len(values)==1 else f"{len(values)} daily snapshots"
    dates = escape(values[0]["date"] + (" → " + values[-1]["date"] if len(values)>1 else ""))
    polyline = f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="none" stroke="{line}" stroke-width="3"/>' if len(points)>1 else ""
    x,y = points[-1]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 230" role="img" aria-labelledby="title desc">
<title id="title">Public project stars: {counts[-1]}</title><desc id="desc">{label}; {dates}. Daily totals can increase or decrease.</desc>
<rect width="860" height="230" rx="18" fill="{bg}"/>
<g font-family="system-ui,-apple-system,Segoe UI,sans-serif"><text x="30" y="38" fill="{fg}" font-size="19" font-weight="650">{counts[-1]} stars across {len(values[-1]['repositories'])} public projects</text>
<text x="30" y="62" fill="{muted}" font-size="13">{label}</text>
<path d="M70 174H790" stroke="{muted}" opacity=".3"/>{polyline}
<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{line}"/>
<text x="{x:.1f}" y="{y-13:.1f}" text-anchor="middle" fill="{fg}" font-size="16" font-weight="650">{counts[-1]}</text>
<text x="430" y="207" text-anchor="middle" fill="{muted}" font-size="13">{dates}</text></g></svg>\n'''


def render_profile(template, catalog, projects, history):
    total, today = history[-1]["stars"], history[-1]["date"]
    metrics = f'**[{len(projects)} projects](https://github.com/orgs/{ORG}/repositories)** &nbsp; · &nbsp; **[★ {total} stars](#star-tracker)**'
    table = "\n".join(f'| [{p["name"]}]({p["url"]}) | {p["stars"]} |' for p in projects)
    tracker = f'''<a name="star-tracker"></a>
<details>
<summary>{icon('star')} <b>Star tracker</b> · {total} stars across {len(projects)} public projects</summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{ASSET}/stars-dark.svg">
  <img src="{ASSET}/stars-light.svg" width="860" alt="{total} stars across {len(projects)} public projects; tracking since {history[0]['date']}.">
</picture>

| Repository | Stars |
| :--- | ---: |
{table}

<sub>Updated {today} UTC · refreshes daily · public project repositories · [Snapshot history](https://github.com/{ORG}/.github/blob/main/data/star-history.json)</sub>

</details>'''
    return template.replace("{{ASSET}}", ASSET).replace("{{METRICS}}", metrics).replace("{{CATALOG}}", render_catalog(catalog, projects)).replace("{{TRACKER}}", tracker)


def build(root, records, today):
    projects = select_projects(records)
    history_path = root / "data/star-history.json"
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    history = update_history(history, projects, today)
    catalog = json.loads((root / "profile/catalog.json").read_text())
    template = (root / "profile/README.template.md").read_text()
    readme = render_profile(template, catalog, projects, history)
    latest = {"organization": ORG, "date": today, "excluded": sorted(EXCLUDED), "projects": projects}
    return {"README.md": readme, "profile/README.md": readme,
            "data/latest.json": json.dumps(latest, indent=2)+"\n",
            "data/star-history.json": json.dumps(history, indent=2)+"\n",
            "profile/assets/stars-light.svg": render_trend(history),
            "profile/assets/stars-dark.svg": render_trend(history, True)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos-file", type=Path, help="Use a saved GitHub API response")
    args = parser.parse_args()
    records = json.loads(args.repos_file.read_text()) if args.repos_file else fetch_repositories()
    output = build(ROOT, records, datetime.now(timezone.utc).date().isoformat())
    # Complete all validation and rendering before touching any generated file.
    for name, value in output.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(value)
        temporary.replace(path)
    print(f"Updated {ORG}: {len(select_projects(records))} public project repositories")


if __name__ == "__main__":
    main()
