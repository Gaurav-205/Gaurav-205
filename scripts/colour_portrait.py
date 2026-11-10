#!/usr/bin/env python3
"""
Draw the hero portrait (gaurav-ascii.svg) as colour ASCII from the GitHub avatar.

Same canvas and row format as the reference make_ascii_svg.py (180 x 96 cells,
x=20, textLength=800), so render_readme_cards.py reads it unchanged. Each run of
characters gets a <tspan fill> sampled from the avatar. Because colour carries the
picture, every non-background cell uses a dense glyph; thin ones like '.' would
hide the colour.

The avatar is a flat drawing on a solid blue (#02BAFF) background, which is keyed
out to blank cells. Light colours (white hair, glasses) are darkened so they still
read on the paper card.

Run by hand; needs Pillow.
    python scripts/colour_portrait.py [avatar.png]
"""
import colorsys
import html
import io
import os
import sys
import urllib.request

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "gaurav-ascii.svg")
COLS, ROWS = 180, 96          # same grid as make_ascii_svg.py
TOP, STEP_Y = 43.2, 8.333     # row baselines, as in the reference portrait
RAMP = "-=+*#%@"              # light -> dark, dense glyphs only
MAX_LUM = 0.46                # lighter colours are scaled down to this
SAT = 1.6                     # saturation boost
QUANT = 24                    # colour rounding, so neighbours share one tspan

if len(sys.argv) > 1:
    avatar = Image.open(sys.argv[1])
else:
    avatar = Image.open(io.BytesIO(urllib.request.urlopen("https://github.com/Gaurav-205.png?size=460").read()))
avatar = avatar.convert("RGB")


def is_bg(r, g, b):
    return b > 200 and r < 90 and g > 150


# key the background before resizing, so edge cells don't pick up blue
full = avatar.copy()
fp = full.load()
mask = Image.new("L", full.size, 0)
mp = mask.load()
for y in range(full.size[1]):
    for x in range(full.size[0]):
        if is_bg(*fp[x, y]):
            mp[x, y] = 255
img = full.resize((COLS, ROWS), Image.LANCZOS).load()
bg = mask.resize((COLS, ROWS), Image.LANCZOS).load()


def cell(x, y):
    if bg[x, y] > 128:
        return " ", None
    r, g, b = (v / 255 for v in img[x, y])
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    ch = RAMP[min(len(RAMP) - 1, int((1 - lum) * len(RAMP)))]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l, min(1, s * SAT))
    if lum > MAX_LUM:
        r, g, b = (v * MAX_LUM / lum for v in (r, g, b))
    r, g, b = (min(255, int(round(v * 255 / QUANT) * QUANT)) for v in (r, g, b))
    return ch, f"#{r:02x}{g:02x}{b:02x}"


rows = []
for y in range(ROWS):
    parts, run, fill = [], "", None
    for x in range(COLS):
        ch, f = cell(x, y)
        if f != fill and run:
            parts.append(html.escape(run) if fill is None else f'<tspan fill="{fill}">{html.escape(run)}</tspan>')
            run = ""
        fill = f
        run += ch
    parts.append(html.escape(run) if fill is None else f'<tspan fill="{fill}">{html.escape(run)}</tspan>')
    rows.append(f'<text xml:space="preserve" x="20" y="{TOP + y * STEP_Y:.1f}" font-size="7.2" '
                f'textLength="800" lengthAdjust="spacing">{"".join(parts)}</text>')

svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="840" height="880" viewBox="0 0 840 880" '
       f'font-family="ui-monospace, monospace">{"".join(rows)}</svg>')
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT} ({len(svg) // 1024} KB)")
