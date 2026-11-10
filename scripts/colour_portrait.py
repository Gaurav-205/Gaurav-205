#!/usr/bin/env python3
"""
Colour the ASCII portrait with the GitHub avatar's colours.

Step 1 makes the black-and-white portrait with the reference converter:
    python make_ascii_svg.py prepped.png base-ascii.svg
(prepped.png = the avatar with its flat blue backdrop keyed to white, then
grayscale). Step 2, this script, keeps every character of that portrait and
wraps runs of them in <tspan fill> sampled from the same spot of the avatar.
make_ascii_svg.py resizes the whole image to COLS x ROWS without cropping, so
cell (x, y) maps straight onto the resized avatar.

Colours are darkened and saturated, because pale colours on the paper card read
as washed out, and glyphs are bold for the same reason. White hair and glasses take a deep slate version of the avatar blue.

    python scripts/colour_portrait.py base-ascii.svg [avatar.png]
"""
import colorsys
import html
import io
import os
import re
import sys
import urllib.request

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "gaurav-ascii.svg")
MAX_LUM = 0.34       # every colour is at most this light, so glyphs stay strong
SAT = 1.7            # saturation boost
TINT_HUE, TINT_SAT = 0.56, 0.45  # whites and greys become a slate blue
QUANT = 24           # colour rounding, so neighbours share one tspan

base = open(sys.argv[1]).read()
if len(sys.argv) > 2:
    avatar = Image.open(sys.argv[2])
else:
    avatar = Image.open(io.BytesIO(urllib.request.urlopen("https://github.com/Gaurav-205.png?size=460").read()))

rows = re.findall(r'<text xml:space="preserve"[^>]*\by="([\d.]+)"[^>]*>(.*?)</text>', base, re.S)
lines = [html.unescape(re.sub(r"<[^>]+>", "", t)) for _, t in rows]
cols = max(len(l) for l in lines)
img = avatar.convert("RGB").resize((cols, len(lines)), Image.LANCZOS).load()


def colour(x, y):
    r, g, b = (v / 255 for v in img[x, y])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < 0.15:
        h, s = TINT_HUE, TINT_SAT
    r, g, b = colorsys.hls_to_rgb(h, l, min(1, s * SAT))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if lum > MAX_LUM:
        r, g, b = (v * MAX_LUM / lum for v in (r, g, b))
    r, g, b = (min(255, int(round(v * 255 / QUANT) * QUANT)) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


out = []
for (y, _), line in zip(rows, lines):
    parts, run, fill = [], "", None
    for x, ch in enumerate(line):
        f = None if ch == " " else colour(x, len(out))
        if f != fill and run:
            parts.append(html.escape(run) if fill is None else f'<tspan fill="{fill}">{html.escape(run)}</tspan>')
            run = ""
        fill = f
        run += ch
    if run:
        parts.append(html.escape(run) if fill is None else f'<tspan fill="{fill}">{html.escape(run)}</tspan>')
    out.append(f'<text xml:space="preserve" x="20" y="{y}" font-size="7.2" textLength="800" '
               f'lengthAdjust="spacing"><tspan font-weight="700">{"".join(parts)}</tspan></text>')

svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="840" height="880" viewBox="0 0 840 880" '
       f'font-family="ui-monospace, monospace">{"".join(out)}</svg>')
open(OUT, "w").write(svg)
print(f"wrote {OUT}: {len(out)} rows x {cols} cols ({len(svg) // 1024} KB)")
