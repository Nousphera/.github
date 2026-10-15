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
- The four curated directions form a two-by-two table. Each project title links
  to its project page when available, otherwise to its repository. Code and paper
  links are optional; add only published resources. Set `highlighted: false` to
  omit a project from the profile while keeping it in the full project catalog.
- `data/latest.json` records the current public repository catalog. API failures,
  malformed records and duplicates abort generation before any files are changed.
- The workflow uses GitHub's built-in token. Write access is limited to this
  repository; pull requests run validation only.

## Visuals and accessibility

`scripts/build_visuals.py` creates the local SVG header and icons. The header has
desktop/mobile and light/dark variants. Its subtle word and network animation
uses a dedicated static image under `prefers-reduced-motion`, including when
embedded in GitHub’s image renderer. Essential meaning is present in the image
alt text and visible prose, so animation is never required to understand the page.
The research grid uses native tables and ordinary links that work with keyboards
and touch. Original vector assets are included under this repository's license.

The organization profile is a GitHub README, so layout uses supported Markdown,
`<picture>` images and native tables. Custom page scripts are not used.
