# Profile vector assets

Original Noösphere artwork, covered by the repository license.

- **Brand mark:** `brand-mark-light.svg` and `brand-mark-dark.svg`; transparent, 40-unit grid.
- **Wordmark:** `wordmark-light.svg` and `wordmark-dark.svg`; transparent, scalable header identity.
- **Icons:** eight matched symbols, 24-unit grid, 1.8-unit rounded strokes, explicit light/dark versions. Display at 18–24 px.
- **Hero:** desktop/mobile layouts, light/dark palettes, animated and static versions.
- **Star charts:** generated from the actual daily snapshots in `data/`.

Edit `scripts/build_visuals.py` and regenerate the artwork. Match each theme explicitly with a `<picture>` element; keep descriptive text beside decorative icons. Do not stretch the brand mark or change stroke widths independently.
