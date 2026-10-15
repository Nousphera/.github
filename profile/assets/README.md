# Profile vector assets

Noösphere artwork is covered by the repository license, except the GitHub mark credited below.

- **Brand mark:** `brand-mark-light.svg` and `brand-mark-dark.svg`; transparent, 40-unit grid.
- **Wordmark:** `wordmark-light.svg` and `wordmark-dark.svg`; transparent, scalable header identity.
- **Icons:** 24-unit grid with explicit light/dark versions; 1.8-unit rounded strokes and a solid GitHub mark. Resource and direction icons display at 24 px; navigation icons at 20 px. The efficiency gauge represents computation and communication efficiency.
- **Hero:** desktop/mobile layouts, light/dark palettes, animated and static versions.

Edit `scripts/build_visuals.py` and regenerate the artwork. Match each theme explicitly with a `<picture>` element; keep descriptive text beside decorative icons. Do not stretch the brand mark or change stroke widths independently.

## GitHub mark

The code-link icon (`github-light.svg` / `github-dark.svg`) uses [GitHub Octicons `mark-github-24`](https://github.com/primer/octicons/blob/main/icons/mark-github-24.svg), copyright GitHub Inc., under the [MIT license](LICENSE-octicons.txt). Its path is unchanged; light/dark foreground colors are supplied by the profile. Other icons are original artwork.

Inline images use GitHub-supported `align="absmiddle"` to keep symbols centered beside their labels. Keep explicit width and height so the grid remains stable while images load.

After changing icon artwork, increment `ICON_REVISION` in `scripts/update_profile.py` before regenerating the profile. This refreshes GitHub’s image proxy without changing the stable asset filenames.

The paper-sheet and gauge artwork use `article-*.svg` and `efficiency-*.svg`. Earlier filenames are retained for cached README versions. Resource pairs use Unicode word joiners so their two links wrap together on small screens.
