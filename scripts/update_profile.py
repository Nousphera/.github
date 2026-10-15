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
        stars = item.get("stargazers_count")
        if type(stars) is not int or stars < 0:
            raise ValueError(f"Invalid star count for {name}")
        projects.append({
            "name": name,
            "url": f"https://github.com/{ORG}/{name}",
            "description": item.get("description") or "Research code and resources.",
            "archived": bool(item.get("archived")),
            "fork": bool(item.get("fork")),
            "stars": stars,
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


def star_meter_width(total):
    return 36 + 11 * len(f"{total:,}")


def render_star_meter(total, dark=False):
    """A single crisp star and count, without a badge label or background."""
    accent, foreground = ("#f2cc60", "#d6e2f1") if dark else ("#9a6700", "#34455b")
    width = star_meter_width(total)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28" role="img" aria-labelledby="title">
<title id="title">{total:,} GitHub stars</title>
<g transform="translate(0 2)"><path d="m12 3 2.78 5.64 6.22.9-4.5 4.39 1.06 6.2L12 17.2l-5.56 2.93 1.06-6.2L3 9.54l6.22-.9Z" fill="{accent}" fill-opacity=".12" stroke="{accent}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>
<text x="31" y="20" fill="{foreground}" font-family="Inter,system-ui,-apple-system,Segoe UI,sans-serif" font-size="18" font-weight="600">{total:,}</text>
</svg>\n'''


def render_navigation(projects):
    total = sum(project["stars"] for project in projects)
    description = f"{total:,} GitHub stars across {len(projects)} public project repositories"
    meter = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{ASSET}/star-meter-dark.svg?v={ICON_REVISION}-{total}">'
             f'<img src="{ASSET}/star-meter-light.svg?v={ICON_REVISION}-{total}" width="{star_meter_width(total)}" height="28" '
             f'align="absmiddle" alt="{description}"></picture>')
    links = [
        f'<a href="https://nousphera.github.io/" title="Noösphere · Research projects">{icon("projects-nav", 28, "Noösphere projects")}</a>',
        f'<a href="https://vtsouval.github.io/" title="Vasileios Tsouvalas · Personal website">{icon("profile-nav", 28, "Personal website")}</a>',
        f'<a href="https://github.com/orgs/{ORG}/repositories?sort=stargazers" title="{description}">{meter}</a>',
    ]
    return '<p align="center">\n  ' + ' &nbsp; · &nbsp;\n  '.join(links) + '\n</p>'


def breakable_text(text):
    """Allow narrow GitHub table cells to wrap long compound terms naturally."""
    text = escape(text)
    for word, split in (("autoencoders", "auto<wbr>encoders"),
                        ("FedCompress", "Fed<wbr>Compress"),
                        ("EncCluster", "Enc<wbr>Cluster"),
                        ("DeltaMask", "Delta<wbr>Mask"),
                        ("semi-supervised", "semi-<wbr>supervised"),
                        ("Semi-supervised", "Semi-<wbr>supervised"),
                        ("Collaborative", "Collab<wbr>orative"),
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


def project_tag_width(label):
    """Readable 12px labels with room for the direction icon and touch target."""
    return round(37 + sum(3.5 if c in "ilI" else 4.5 if c == "-" else
                          9.5 if c in "MWmw" else 7.5 if c.isupper() else 6.5
                          for c in label))


def render_overview(catalog, projects):
    live = {p["name"]: p for p in projects}
    description = "; ".join(group["title"] for group in catalog)
    sources = []
    for mobile, reduced, dark in ((True, True, True), (True, True, False),
                                   (False, True, True), (False, True, False),
                                   (True, False, True), (True, False, False),
                                   (False, False, True)):
        media = []
        if reduced:
            media.append("(prefers-reduced-motion: reduce)")
        if mobile:
            media.append("(max-width: 600px)")
        if dark:
            media.append("(prefers-color-scheme: dark)")
        name = f'research-overview-{"phone-" if mobile else ""}{"dark" if dark else "light"}{"-static" if reduced else ""}.svg'
        sources.append(f'<source media="{" and ".join(media)}" srcset="{ASSET}/{name}?v=2">')
    picture = '<p align="center"><picture>\n' + "\n".join(sources)
    picture += f'\n<img src="{ASSET}/research-overview-light.svg?v=2" width="960" alt="{escape(description, quote=True)}">\n</picture></p>'
    tags = []
    for group in catalog:
        for project in group["projects"]:
            name = project["repo"]
            if name not in live or not project.get("highlighted", True):
                continue
            label = project.get("label", name)
            target = project.get("project") or live[name]["url"]
            hint = f'{label} · {group["title"]} · {project["summary"]}'
            tag = (f'<a href="{escape(target, quote=True)}" title="{escape(hint, quote=True)}">'
                        f'<picture><source media="(prefers-color-scheme: dark)" srcset="{ASSET}/project-{name}-dark.svg">'
                        f'<img src="{ASSET}/project-{name}-light.svg" width="{project_tag_width(label)}" height="30" '
                        f'align="absmiddle" alt="Open {escape(label, quote=True)} · {escape(group["title"], quote=True)}"></picture></a>')
            resources = []
            if project.get("project"):
                resources.append(f'<a href="{escape(live[name]["url"], quote=True)}" title="{escape(label, quote=True)} · Code repository">'
                                 f'{icon("github", 24, label + " code repository")}</a>')
            if project.get("paper"):
                resources.append(f'<a href="{escape(project["paper"], quote=True)}" title="{escape(label, quote=True)} · Read paper">'
                                 f'{icon("article", 24, "Read " + label + " paper")}</a>')
            # A group stays together when space permits; normal spaces between
            # groups allow the browser to wrap them without a scrolling table.
            if resources:
                tag += '&#8288;&nbsp;&#8288;' + '&#8288;'.join(resources) + '&#8288;'
            tags.append('<span>' + tag + '</span>')
    return picture + '\n\n<p align="center">\n' + '\n'.join(tags) + '\n</p>'


def render_catalog(catalog, projects):
    """One research section with wrapping project, code and paper links."""
    live = {p["name"] for p in projects}
    known, visible = set(), False
    for group in catalog:
        for project in group["projects"]:
            name = project["repo"]
            if name in known:
                raise ValueError(f"Duplicate catalog entry: {name}")
            known.add(name)
            visible |= name in live and project.get("highlighted", True)
    grid = render_overview(catalog, projects) if visible else ""
    extra = [p for p in projects if p["name"] not in known]
    if extra:
        rows = [f'| **[{p["name"]}]({p["url"]})** | {safe_text(p["description"])} |' for p in extra]
        grid += "\n\n### More projects\n\n| Project | Focus |\n| :--- | :--- |\n" + "\n".join(rows)
    return grid


def render_profile(template, catalog, projects):
    return (template.replace("{{ASSET}}", ASSET).replace("{{ICON_REVISION}}", ICON_REVISION)
            .replace("{{NAVIGATION}}", render_navigation(projects))
            .replace("{{CATALOG}}", render_catalog(catalog, projects)))


def build(root, records, today):
    projects = select_projects(records)
    catalog = json.loads((root / "profile/catalog.json").read_text())
    template = (root / "profile/README.template.md").read_text()
    readme = render_profile(template, catalog, projects)
    stars = sum(project["stars"] for project in projects)
    latest = {"organization": ORG, "date": today, "excluded": sorted(EXCLUDED), "stars": stars, "projects": projects}
    return {"README.md": readme, "profile/README.md": readme,
            "data/latest.json": json.dumps(latest, indent=2)+"\n",
            "profile/assets/star-meter-light.svg": render_star_meter(stars),
            "profile/assets/star-meter-dark.svg": render_star_meter(stars, dark=True)}



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
