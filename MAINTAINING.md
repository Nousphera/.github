# Maintaining the organization profile

The public organization profile and repository landing page share one generated
README. Edit `profile/README.template.md` for prose and layout, and
`profile/catalog.json` for the curated research groups. Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_visuals.py
python3 scripts/update_profile.py
```

Python 3.10+ and its standard library are sufficient. No packages or API keys are
required for a local refresh. `GITHUB_TOKEN` is used when available to increase
the GitHub API rate limit. Never commit a token.

## Project catalog

- The catalog refreshes daily at **06:17 UTC**, on relevant main-branch changes,
  and through **Actions → Organization profile → Run workflow**.
- Only public project repositories owned by Nousphera are shown; `.github` and
  `nousphera.github.io` are excluded. Newly public projects appear in **More
  projects** until assigned a direction in `profile/catalog.json`.
- The four curated directions share an animated overview: one row on desktop,
  two columns on phones, with a matching strip of colored project tags below.
  Each tag links to its project page when available, otherwise to its repository.
  Paper and code links live in a native, collapsed disclosure. Add only published
  resources. Set `highlighted: false` to
  omit a project from the profile while keeping it in the full project catalog.
- `data/latest.json` records the current public repository catalog. API failures,
  malformed records and duplicates abort generation before any files are changed.
- The compact star meter sums stars across all public project repositories,
  including projects omitted from the highlighted grid, forks and archives.
  The profile repository and website are excluded. It refreshes with the daily
  catalog workflow; the displayed number is a snapshot, not a real-time stream.
  Invalid or missing counts abort the refresh, preserving the last valid total.
- The workflow uses GitHub's built-in token. Write access is limited to this
  repository; pull requests run validation only.

## Visuals and accessibility

`scripts/build_visuals.py` creates the local SVG header and icons. The header has
desktop/mobile and light/dark variants. Its subtle word and network animation
uses a dedicated static image under `prefers-reduced-motion`, including when
embedded in GitHub’s image renderer. Essential meaning is present in the image
alt text and visible prose, so animation is never required to understand the page.
The research overview has static reduced-motion variants. Project tags use normal
links with meaningful alternative text and hover descriptions. A native horizontal
table scrolls on narrow screens and brings focused links into view. Color and
category icons identify each direction together.
The collapsed resource grid uses native tables and ordinary links that work with keyboards
and touch. Original vector assets are included under this repository's license. The GitHub
mark retains its upstream MIT license in `profile/assets/LICENSE-octicons.txt`.

The organization profile is a GitHub README, so layout uses supported Markdown,
`<picture>` images, a native disclosure and tables. Custom page scripts are not used;
tags navigate to projects rather than filtering the README in place.
