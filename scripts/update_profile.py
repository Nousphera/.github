"""Build the organization profile from public repository metadata; no dependencies."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ORG = "Nousphera"
EXCLUDED = {".github", "nousphera.github.io"}
ASSET = f"https://raw.githubusercontent.com/{ORG}/.github/main/profile/assets"
# Bump when changing icons so GitHub's image proxy refreshes existing profiles.
ICON_REVISION = "2"


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
        projects.append({
            "name": name,
            "url": f"https://github.com/{ORG}/{name}",
            "description": item.get("description") or "Research code and resources.",
            "archived": bool(item.get("archived")),
            "fork": bool(item.get("fork")),
        })
    if not projects:
        raise ValueError("No public projects returned; preserving the previous snapshot")
    return sorted(projects, key=lambda p: p["name"].lower())


def safe_text(value):
    text = escape(value).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")
    for char in "[]`*_\\":
        text = text.replace(char, f"&#{ord(char)};")
    return text


def icon(name, size=18, label=""):
    return f'<picture><source media="(prefers-color-scheme: dark)" srcset="{ASSET}/{name}-dark.svg?v={ICON_REVISION}"><img src="{ASSET}/{name}-light.svg?v={ICON_REVISION}" width="{size}" height="{size}" align="absmiddle" alt="{escape(label, quote=True)}"></picture>'


def breakable_text(text):
    """Allow narrow GitHub table cells to wrap long compound terms naturally."""
    text = escape(text)
    for word, split in (("autoencoders", "auto<wbr>encoders"),
                        ("FedCompress", "Fed<wbr>Compress"),
                        ("EncCluster", "Enc<wbr>Cluster"),
                        ("DeltaMask", "Delta<wbr>Mask"),
                        ("semi-supervised", "semi-<wbr>supervised"),
                        ("Semi-supervised", "Semi-<wbr>supervised"),
                        ("Trustworthy", "Trust<wbr>worthy")):
        text = text.replace(word, split)
    return text


def concept_summary(project):
    """Emphasize one curated concept while keeping all text HTML-escaped."""
    summary = project["summary"]
    highlight = project.get("highlight")
    if not highlight:
        return breakable_text(summary)
    if highlight not in summary:
        raise ValueError(f"Highlight missing from summary: {project['repo']}")
    before, concept, after = summary.partition(highlight)
    return f"{breakable_text(before)}<strong>{breakable_text(concept)}</strong>{breakable_text(after)}"


def render_catalog(catalog, projects):
    """Four research directions in a GitHub-native, two-column table."""
    live = {p["name"]: p for p in projects}
    known, cells = set(), []
    for group in catalog:
        entries = []
        for project in group["projects"]:
            name = project["repo"]
            if name in known:
                raise ValueError(f"Duplicate catalog entry: {name}")
            known.add(name)
            if name not in live or not project.get("highlighted", True):
                continue
            label = project.get("label", name)
            target = project.get("project") or live[name]["url"]
            links = []
            if project.get("project"):
                links.append(f'<a href="{escape(live[name]["url"], quote=True)}" title="{escape(label)} · Code repository">{icon("github", 24, "Code repository")}</a>')
            if project.get("paper"):
                links.append(f'<a href="{escape(project["paper"], quote=True)}" title="{escape(label)} · Read paper">{icon("article", 24, "Read paper")}</a>')
            # Word joiners keep the two image links on the same line on phones.
            resources = " " + "&nbsp;".join(f"&#8288;{link}&#8288;" for link in links) if links else ""
            entries.append(f'<p><a href="{escape(target, quote=True)}"><b>{breakable_text(label)}</b></a>{resources}'
                           f'<br>{concept_summary(project)}</p>')
        if entries:
            cells.append(f'<td width="50%" valign="top">\n<h4>{icon(group["icon"], 24)} {breakable_text(group["title"])}</h4>\n'
                         + "\n".join(entries) + "\n</td>")
    rows = ["<tr>\n" + "\n".join(cells[i:i+2]) + "\n</tr>" for i in range(0, len(cells), 2)]
    grid = '<table width="100%">\n' + "\n".join(rows) + "\n</table>"
    extra = [p for p in projects if p["name"] not in known]
    if extra:
        rows = [f'| **[{p["name"]}]({p["url"]})** | {safe_text(p["description"])} |' for p in extra]
        grid += "\n\n### More projects\n\n| Project | Focus |\n| :--- | :--- |\n" + "\n".join(rows)
    return grid


def render_profile(template, catalog, projects):
    return (template.replace("{{ASSET}}", ASSET).replace("{{ICON_REVISION}}", ICON_REVISION)
            .replace("{{CATALOG}}", render_catalog(catalog, projects)))


def build(root, records, today):
    projects = select_projects(records)
    catalog = json.loads((root / "profile/catalog.json").read_text())
    template = (root / "profile/README.template.md").read_text()
    readme = render_profile(template, catalog, projects)
    latest = {"organization": ORG, "date": today, "excluded": sorted(EXCLUDED), "projects": projects}
    return {"README.md": readme, "profile/README.md": readme,
            "data/latest.json": json.dumps(latest, indent=2)+"\n"}



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
