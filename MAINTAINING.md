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

## Star tracker

- The workflow runs daily at **06:17 UTC**, on relevant main-branch changes, and
  through **Actions → Organization profile → Run workflow**. GitHub may delay
  scheduled runs; the profile shows the date of the latest successful snapshot.
- Counts include **all public project repositories owned by Nousphera**, including
  forks and archived repositories. Only `.github` and `nousphera.github.io` are
  excluded. Newly public repositories are included automatically and appear in
  **More projects** until added to a curated group.
- The total is the sum of repository stars, **not unique people**. It can decrease
  when users remove stars or repositories leave the public set.
- `data/latest.json` contains the current per-repository counts.
  `data/star-history.json` retains one actual observation per UTC date. A second
  run on the same date refreshes that day's observation. Earlier dates are kept;
  no historical counts are inferred. The plot shows up to 90 daily snapshots.
- All API pages must succeed. Empty, malformed and duplicate responses abort
  generation, preserving the previous published snapshot.
- The workflow uses GitHub's built-in token, with write access confined to this
  repository. Pull requests run tests only. There is no external statistics service.

## Visuals and accessibility

`scripts/build_visuals.py` creates the local SVG header and icons. The header has
desktop/mobile and light/dark variants. Its subtle word and network animation
stops under `prefers-reduced-motion`. Essential meaning is present in the image
alt text and visible prose, so animation is never required to understand the page.
Expandable groups use native GitHub `<details>` elements and work with keyboards
and touch. Original vector assets are included under this repository's license.

The organization profile is a GitHub README, so layout uses supported Markdown,
`<picture>` images and native disclosure controls. Custom page scripts are not used.
