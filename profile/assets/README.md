# Profile vector assets

Noösphere artwork is covered by the repository license, except the GitHub mark credited below.

- **Brand mark:** `brand-mark-light.svg` and `brand-mark-dark.svg`; transparent, 40-unit grid.
- **Wordmark:** `wordmark-light.svg` and `wordmark-dark.svg`; transparent, scalable header identity.
- **Icons:** 24-unit grid with explicit light/dark versions; 1.8-unit rounded strokes and a solid GitHub mark. Resource and direction icons display at 24 px; navigation icons at 28 px. The efficiency gauge represents computation and communication efficiency.
- **Hero:** desktop/mobile layouts, light/dark palettes, animated and static versions.

Edit `scripts/build_visuals.py` and regenerate the artwork. Match each theme explicitly with a `<picture>` element; keep descriptive text beside decorative icons. Do not stretch the brand mark or change stroke widths independently.

## GitHub mark

The code-link icon (`github-light.svg` / `github-dark.svg`) uses [GitHub Octicons `mark-github-24`](https://github.com/primer/octicons/blob/main/icons/mark-github-24.svg), copyright GitHub Inc., under the [MIT license](LICENSE-octicons.txt). Its path is unchanged; light/dark foreground colors are supplied by the profile. Other icons are original artwork.

Inline images use GitHub-supported `align="absmiddle"` to keep symbols centered beside their labels. Keep explicit width and height so the grid remains stable while images load.

After changing icon artwork, increment `ICON_REVISION` in `scripts/update_profile.py` before regenerating the profile. This refreshes GitHub’s image proxy without changing the stable asset filenames.

The paper-sheet and gauge artwork use `article-*.svg` and `efficiency-*.svg`. Earlier filenames are retained for cached README versions. Resource pairs use Unicode word joiners so their two links wrap together on small screens.

## Compact navigation

`projects-nav-*.svg` and `profile-nav-*.svg` link to the project website and personal profile. `scripts/update_profile.py` generates `star-meter-*.svg` from the validated public repository total. The meter contains only a star and its count; accessible labels and hover text describe the destination and scope. Light/dark variants share the same geometry and baseline.

## Research overview and project tags

`research-overview-*.svg` is one visual key for the four directions, with desktop/mobile,
light/dark and reduced-motion variants. Gentle color emphasis and traveling underline
signals are decorative; titles remain visible throughout. The overview does not imply
that the categories form sequential stages.

`project-<repository>-*.svg` tags repeat each direction's icon and color. They are normal
links in the README, with an accessible project/category label and a compact hover
description. A single horizontal strip scrolls on smaller screens. The scheduled workflow
rebuilds these assets alongside the catalog so changes stay consistent.
