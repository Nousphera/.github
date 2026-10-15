"""Generate the profile's theme-aware SVG artwork; see assets for attribution."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "profile/assets"


def brand_mark(color):
    """Three precise nodes, linked as one collective; transparent at every size."""
    return f'''<g fill="{color}" stroke="{color}" stroke-linecap="round" stroke-linejoin="round">
<path d="M10 10L30 17L16 31Z" fill="none" stroke-width="2.2" opacity=".35"/>
<circle cx="10" cy="10" r="5.7" stroke="none"/>
<circle cx="30" cy="17" r="5.7" stroke="none" opacity=".82"/>
<circle cx="16" cy="31" r="5.7" stroke="none" opacity=".62"/>
</g>'''


def hero(dark=False, mobile=False, static=False):
    bg, fg, muted, blue, green, purple, border = (
        ("#101923", "#e9f0f8", "#a3b3c5", "#87b6fb", "#72d0bd", "#c4afff", "#2b3c51")
        if dark else ("#f5f8fc", "#20334d", "#5b6e86", "#2b62b9", "#177d6b", "#7354b6", "#d6e0ec")
    )
    w, h = (520, 292) if mobile else (960, 310)
    left, size = (28, 45) if mobile else (42, 56)
    y1, y2, yp = (127, 183, 242) if mobile else (137, 204, 263)
    network = "" if mobile else f'''
<g transform="translate(766 165)" fill="none" stroke="{border}" stroke-width="1.5">
  <circle r="105" stroke-dasharray="2 8"/>
  <path d="M0 0L0 -96M0 0L-84 49M0 0L84 49"/>
  <g stroke="{blue}" stroke-width="2" stroke-dasharray="4 15" opacity=".65" class="flow">
    <path d="M0 -84V-22M-74 43L-19 11M74 43L19 11"/>
  </g>
  <g fill="{bg}" stroke="{blue}">
    <rect x="-29" y="-29" width="58" height="58" rx="15"/>
    <g stroke-width="1.8" stroke-linecap="round">
      <rect x="-13" y="-17" width="26" height="9" rx="2.5"/>
      <rect x="-13" y="-4.5" width="26" height="9" rx="2.5"/>
      <rect x="-13" y="8" width="26" height="9" rx="2.5"/>
      <path d="M-8 -12.5H-6M-8 0H-6M-8 12.5H-6"/>
    </g>
    <circle cy="-96" r="22"/>
    <circle cx="-84" cy="49" r="22"/>
    <circle cx="84" cy="49" r="22"/>
    <g stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="-9" y="-104" width="18" height="12" rx="2"/><path d="M0 -92V-88M-4 -88H4"/>
      <rect x="-93" y="41" width="18" height="12" rx="2"/><path d="M-84 53V57M-88 57H-80"/>
      <rect x="75" y="41" width="18" height="12" rx="2"/><path d="M84 53V57M80 57H88"/>
    </g>
  </g>
  <circle r="35" stroke="{blue}" opacity=".16" class="pulse"/>
</g>'''
    static_css = ".phrase,.flow,.pulse{animation:none}.p1{opacity:1}.p2,.p3{display:none}" if static else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">Noösphere — intelligence, closer to the edge</title>
<desc id="desc">Learn together. Adapt efficiently. Build trust. Research in collaborative and efficient machine learning.</desc>
<style>
  text {{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}}
  .phrase {{opacity:0;animation:words 12s ease-in-out infinite}}
  .p1 {{opacity:1}} .p2 {{animation-delay:-8s}} .p3 {{animation-delay:-4s}}
  .flow {{animation:flow 5s linear infinite}}
  .pulse {{transform-origin:center;animation:pulse 4s ease-in-out infinite}}
  @keyframes words {{0%,30%,100%{{opacity:0}} 5%,25%{{opacity:1}} 33%,99%{{opacity:0}}}}
  @keyframes flow {{to{{stroke-dashoffset:-76}}}}
  @keyframes pulse {{50%{{opacity:.4}}}}
  @media(prefers-reduced-motion:reduce) {{.phrase,.flow,.pulse{{animation:none}} .p1{{opacity:1}} .p2,.p3{{display:none}}}}
{static_css}
</style>

<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="22" fill="{bg}" stroke="{border}"/>
<g transform="translate({left-3} 26) scale(.8)">{brand_mark(blue)}</g>
<text x="{left+41}" y="53" fill="{fg}" font-size="22" font-weight="650" letter-spacing="-.4">Noösphere</text>
<text x="{left}" y="{y1}" fill="{fg}" font-size="{size}" font-weight="650" letter-spacing="-2">Intelligence,</text>
<text x="{left}" y="{y2}" fill="{fg}" font-size="{size}" font-weight="650" letter-spacing="-2">closer to the edge.</text>
<g transform="translate({left} {yp})" font-size="24" font-weight="500">
  <text class="phrase p1" fill="{blue}" x="0" y="0">Learn together.</text>
  <text class="phrase p2" fill="{green}" x="0" y="0">Adapt efficiently.</text>
  <text class="phrase p3" fill="{purple}" x="0" y="0">Build trust.</text>
</g>
{network}
</svg>\n'''


ICONS = {
    "projects-nav": '<rect x="3" y="3" width="7" height="7" rx="1.7"/><rect x="14" y="3" width="7" height="7" rx="1.7"/><rect x="3" y="14" width="7" height="7" rx="1.7"/><rect x="14" y="14" width="7" height="7" rx="1.7"/>',
    "profile-nav": '<rect x="2.5" y="3.5" width="19" height="17" rx="3"/><circle cx="8" cy="9.5" r="2.3"/><path d="M4.5 17v-.5a3.5 3.5 0 0 1 7 0v.5M15 8h3M15 12h3M15 16h3"/>',
    "projects": '<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4H20v16H6.5A2.5 2.5 0 0 1 4 17.5ZM4 17.5A2.5 2.5 0 0 1 6.5 15H20"/><path d="m11 7-2 2 2 2m4-4 2 2-2 2" stroke-width="1.6"/>',
    # GitHub Octicons mark-github-24, MIT; license retained in profile/assets.
    "github": '<path fill="currentColor" stroke="none" d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943"/>',
    "person": '<circle cx="12" cy="7.5" r="3.5"/><path d="M5 20v-1.5a7 7 0 0 1 14 0V20"/>',
    "article": '<path d="M13 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10Z" fill="currentColor" fill-opacity=".07"/><path d="M13 3v5a2 2 0 0 0 2 2h5M8 14h8M8 17.5h5"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5ZM3 12l9 5 9-5M3 16l9 5 9-5"/>',
    "efficiency": '<path d="M4 18a9 9 0 1 1 16 0M5 12h2M12 5v2M17 12h2M12 14l4-5"/><circle cx="12" cy="14" r="1.5" fill="currentColor" stroke="none"/>',
    "shield": '<path d="m12 3 8 3v5c0 4.8-3.4 8.2-8 10-4.6-1.8-8-5.2-8-10V6ZM8.5 11.5l2.5 2.5 4.5-5"/>',
    "audio": '<path d="M4 9v6M8 6v12M12 3v18M16 6v12M20 9v6"/>',
    "star": '<path d="m12 3 2.78 5.64 6.22.9-4.5 4.39 1.06 6.2L12 17.2l-5.56 2.93 1.06-6.2L3 9.54l6.22-.9Z" fill="currentColor" fill-opacity=".14"/>',
}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        for mobile in (False, True):
            name = f'hero-{"mobile-" if mobile else ""}{"dark" if dark else "light"}.svg'
            (ROOT/name).write_text(hero(dark, mobile))
            (ROOT/name.replace(".svg", "-static.svg")).write_text(hero(dark, mobile, True))
    for theme, default_color, brand, text in [("light", "#496786", "#2b62b9", "#20334d"), ("dark", "#a9bdd5", "#87b6fb", "#e9f0f8")]:
        accents = {"projects-nav": ("#3263a8", "#9ac2ff"),
                   "profile-nav": ("#6c50a2", "#c4afff"),
                   "github": ("#34455b", "#d6e2f1"),
                   "article": ("#34455b", "#d6e2f1"),
                   "layers": ("#3263a8", "#9ac2ff"),
                   "efficiency": ("#217568", "#80d1c0"),
                   "shield": ("#6c50a2", "#c4afff"),
                   "audio": ("#996321", "#e5bb78")}
        for name, paths in ICONS.items():
            color = accents.get(name, (default_color, default_color))[theme == "dark"]
            (ROOT/f"{name}-{theme}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" color="{color}" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>\n')
        (ROOT/f"brand-mark-{theme}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" role="img"><title>Noösphere</title>{brand_mark(brand)}</svg>\n')
        (ROOT/f"wordmark-{theme}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 228 44" role="img"><title>Noösphere</title><g transform="translate(0 2)">{brand_mark(brand)}</g><text x="51" y="31" fill="{text}" font-family="Inter,system-ui,-apple-system,Segoe UI,sans-serif" font-weight="650" font-size="28" letter-spacing="-.6">Noösphere</text></svg>\n')


if __name__ == "__main__":
    main()
