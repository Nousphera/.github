"""Generate the profile's original, theme-aware SVG artwork."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "profile/assets"


def hero(dark=False, mobile=False):
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
    <rect x="-27" y="-26" width="54" height="52" rx="14"/>
    <path d="M-12 -10H12M-12 0H12M-12 10H12" stroke-width="2.4" stroke-linecap="round"/>
    <circle cy="-96" r="22"/>
    <circle cx="-84" cy="49" r="22"/>
    <circle cx="84" cy="49" r="22"/>
    <path d="M-8 -104H8V-92H-8ZM-3 -88H3M-92 41H-76V53H-92ZM-87 57H-81M76 41H92V53H76ZM81 57H87" stroke-linejoin="round"/>
  </g>
  <circle r="35" stroke="{blue}" opacity=".16" class="pulse"/>
</g>'''
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
</style>

<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="22" fill="{bg}" stroke="{border}"/>
<g transform="translate({left} 36)" fill="{blue}"><circle cx="7" cy="2" r="7"/><circle cx="19" cy="8" r="7" opacity=".65"/><circle cx="10" cy="18" r="7" opacity=".35"/></g>
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
    "projects": '<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><rect x="14" y="14" width="7" height="7" rx="1.4"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
    "paper": '<path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6"/>',
}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        for mobile in (False, True):
            name = f'hero-{"mobile-" if mobile else ""}{"dark" if dark else "light"}.svg'
            (ROOT/name).write_text(hero(dark, mobile))
    for name, paths in ICONS.items():
        (ROOT/f"{name}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#6087b8" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>\n')


if __name__ == "__main__":
    main()
