#!/usr/bin/env python3
"""Generate assets/banner.svg — an animated Matrix-rain header for the profile README.

Stdlib only. Deterministic (seeded) so re-running produces the same file.
GitHub renders SMIL-animated SVGs from the repo; no external fonts or scripts are used.

    python3 assets/make_banner.py
"""
import random
from html import escape
from pathlib import Path

W, H = 1200, 320
COLS = 46            # rain columns
CHARS_PER_COL = 22   # glyphs per column
FONT_PX = 15
GREEN = "#00ff41"
HEAD = "#d8ffe0"
BG = "#020703"

GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:・=*+-<>¦|"

NAME = "ALEX ALVORD"
TAGLINE = "> hybrid multicloud · NC2 · invisible infrastructure · Seattle, WA"

rng = random.Random(3764699)  # GitHub user id, for a stable seed


def column(i: int) -> str:
    x = int((i + 0.5) * (W / COLS))
    n = rng.randint(CHARS_PER_COL - 8, CHARS_PER_COL)
    dur = rng.uniform(6.0, 14.0)
    begin = -rng.uniform(0, dur)  # negative begin = already mid-fall on load
    spans = []
    for k in range(n):
        ch = escape(rng.choice(GLYPHS))
        # brightest glyph at the bottom (the "head"); tail fades upward
        if k == n - 1:
            fill, op = HEAD, 1.0
        else:
            fill, op = GREEN, round(0.12 + 0.75 * (k / n), 2)
        dy = FONT_PX if k else 0
        spans.append(f'<tspan x="{x}" dy="{dy}" fill="{fill}" fill-opacity="{op}">{ch}</tspan>')
    body = "".join(spans)
    col_h = n * FONT_PX
    return (
        f'<text font-size="{FONT_PX}" y="0">{body}'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 {-col_h}" to="0 {H + FONT_PX}" dur="{dur:.1f}s" begin="{begin:.1f}s" '
        f'repeatCount="indefinite"/></text>'
    )


def build() -> str:
    rain = "\n".join(column(i) for i in range(COLS))
    tag_chars = len(TAGLINE)
    tag_w = int(tag_chars * 10.2)  # ~ advance width at 17px monospace
    tagline = escape(TAGLINE)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace">
  <title>Alex Alvord</title>
  <defs>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG}" stop-opacity="0"/>
      <stop offset="0.35" stop-color="{BG}" stop-opacity="0.82"/>
      <stop offset="0.65" stop-color="{BG}" stop-opacity="0.82"/>
      <stop offset="1" stop-color="{BG}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g opacity="0.85">
{rain}
  </g>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>

  <g text-anchor="middle">
    <text x="{W // 2}" y="{H // 2 - 4}" font-size="64" font-weight="700" letter-spacing="10" fill="{GREEN}" filter="url(#glow)">{NAME}</text>
    <text x="{(W - tag_w) // 2}" y="{H // 2 + 46}" font-size="17" text-anchor="start" fill="{GREEN}" fill-opacity="0.9">{tagline}</text>
    <!-- typewriter: a cover the colour of the background slides off the tagline.
         (Chrome ignores SMIL on clipPath children, so no clip-based reveal.) -->
    <rect x="{(W - tag_w) // 2}" y="{H // 2 + 28}" width="{tag_w + 12}" height="26" fill="{BG}">
      <animate attributeName="x" from="{(W - tag_w) // 2}" to="{(W + tag_w) // 2 + 12}" dur="3.2s" begin="0.6s" fill="freeze"/>
      <animate attributeName="width" from="{tag_w + 12}" to="0" dur="3.2s" begin="0.6s" fill="freeze"/>
    </rect>
    <rect x="{(W + tag_w) // 2 + 2}" y="{H // 2 + 32}" width="9" height="18" fill="{GREEN}">
      <animate attributeName="opacity" values="1;0;1" dur="1s" begin="3.8s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).with_name("banner.svg")
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")
