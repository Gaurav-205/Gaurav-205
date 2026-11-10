#!/usr/bin/env python3
"""
Draw the profile README's cards as animated SVGs into cards/.

Theme: a night sky over Pune. The hero is a small solar system where the planets
are my projects, the contribution graph is a star chart (one star per day), and
the monthly bars are a flight log.

GitHub shows each card through <img>, so they only use what works there: CSS
animations, SMIL, and fonts embedded as data URIs (fonts/, SIL OFL). No JS.

Numbers come from data/contributions.json (fetch_contributions.py). Run daily by
.github/workflows/refresh-cards.yml. STATIC=1 renders every animation at its end
state, which is handy for previews.
"""
import base64
import datetime
import json
import math
import os
import random
import re
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
USER = "Gaurav-205"

# ---- palette --------------------------------------------------------------------
SKY = "#0a0e1a"
SKY_2 = "#111729"
LINE = "#232b42"
STAR = "#eef1f8"
SOFT = "#b9c0d4"
DIM = "#7d86a0"
SUN = "#ffb547"
BLUE = "#7aa2ff"
MINT = "#5fe0b7"
ROSE = "#ff7a8a"
W = 880

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

CSS = """
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.2)}100%{opacity:1;transform:none}}
@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes glow{0%,100%{opacity:.35}50%{opacity:.7}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade 1s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out both}
.tw{animation:twinkle 3s ease-in-out infinite}
.gl{animation:glow 4s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.tw,.gl{animation:none!important;opacity:1!important;transform:none!important}}
"""
STATIC_CSS = ".r,.f,.g,.p,.tw,.gl{animation:none!important;opacity:1!important;transform:none!important}"

GAP = 12        # space under each card and between cards in a row, baked in so rows tile exactly
COL_W = W / 3 - 8


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        b64 = base64.b64encode(open(os.path.join(FONTS, fn), "rb").read()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                   f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(out)


def svg(w, h, body, fonts, label, left=0, right=0):
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + GAP
    css = font_face(fonts) + CSS + (STATIC_CSS if os.environ.get("STATIC") else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
            f"<style>{css}</style>{body}</svg>")


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def text_lines(x, y, lines, lh, attrs):
    return "".join(f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines))


def starfield(w, h, n, seed, avoid=None):
    """Same sky every run (fixed seed), so the daily refresh only changes real numbers."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(6, w - 6), rnd.uniform(6, h - 6)
        if avoid and avoid(x, y):
            continue
        r = rnd.choice([0.5, 0.6, 0.8, 0.8, 1.0, 1.3])
        o = rnd.uniform(0.25, 0.9)
        cls = f' class="tw" style="animation-delay:{rnd.uniform(0, 3):.2f}s;animation-duration:{rnd.uniform(2.5, 5):.1f}s"' \
            if rnd.random() < 0.3 else ""
        out.append(f'<circle{cls} cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{STAR}" fill-opacity="{o:.2f}"/>')
    return "".join(out)


def card_bg(w, h, cid):
    return (f'<defs><clipPath id="{cid}"><rect width="{w:.3f}" height="{h}" rx="14"/></clipPath>'
            f'<radialGradient id="{cid}-neb" cx=".8" cy=".1" r=".9"><stop offset="0" stop-color="#1d2547"/>'
            f'<stop offset="1" stop-color="{SKY}"/></radialGradient></defs>'
            f'<rect width="{w:.3f}" height="{h}" rx="14" fill="url(#{cid}-neb)"/>'
            f'<rect x=".5" y=".5" width="{w - 1:.3f}" height="{h - 1}" rx="13.5" fill="none" stroke="{LINE}"/>')


# ---- 1 · hero: name on the left, a solar system of projects on the right ---------------
# (label, orbit rx, colour, seconds per lap, start phase 0..1)
PLANETS = [
    ("kalbot", 72, MINT, 14, 0.15),
    ("Munim", 116, SUN, 22, 0.55),
    ("Bharosa", 116, BLUE, 22, 0.05),
    ("KampusKart", 158, ROSE, 34, 0.35),
    ("Nova", 158, MINT, 34, 0.85),
]
CX, CY, TILT = 676, 206, 0.42


def orbit_path(rx):
    ry = rx * TILT
    return f"M {CX - rx},{CY} a {rx},{ry} 0 1,0 {2 * rx},0 a {rx},{ry} 0 1,0 {-2 * rx},0"


def hero():
    h = 420
    rings = sorted({p[1] for p in PLANETS})
    ring_svg = "".join(
        f'<ellipse class="f" {d(0.4 + i * 0.15)} cx="{CX}" cy="{CY}" rx="{rx}" ry="{rx * TILT:.1f}" '
        f'fill="none" stroke="{SOFT}" stroke-opacity=".22" stroke-dasharray="2 5"/>'
        for i, rx in enumerate(rings))
    planets = []
    for name, rx, color, dur, phase in PLANETS:
        if os.environ.get("STATIC"):  # park the planet on its ring at its start phase
            ang = 3.14159 * 2 * phase
            pos = f'transform="translate({CX - rx * math.cos(ang):.1f} {CY + rx * TILT * math.sin(ang):.1f})"'
            motion = ""
        else:
            pos = ""
            motion = (f'<animateMotion dur="{dur}s" begin="-{dur * phase:.2f}s" repeatCount="indefinite" '
                      f'path="{orbit_path(rx)}"/>')
        planets.append(
            f'<g {pos}>{motion}'
            f'<circle r="11" fill="{color}" fill-opacity=".18"/><circle r="5" fill="{color}"/>'
            f'<text y="-15" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{SOFT}">{name}</text></g>')
    stars = starfield(W, h, 170, 205, avoid=lambda x, y: 30 < x < 470 and 150 < y < 380)
    intro = ["Student at MIT ADT University. I write software", "for the places around me: my campus,",
             "small suppliers, and weather desks on the coast."]
    body = f"""
{card_bg(W, h, "hero")}
<g clip-path="url(#hero)">{stars}</g>
<g class="f" {d(0)}>
  <circle class="tw" cx="52" cy="52" r="4" fill="{SUN}"/>
  <text x="66" y="56" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{DIM}">PUNE  18.52&#176;N 73.86&#176;E  ·  BUILDING AT ORBIT</text>
</g>
<text class="r" {d(0.15)} x="42" y="176" font-family="{SERIF}" font-size="104" letter-spacing="-2" fill="{STAR}">Gaurav</text>
<text class="r" {d(0.3)} x="42" y="262" font-family="{SERIF}" font-style="italic" font-size="104" letter-spacing="-2" fill="{SUN}">Khandelwal</text>
<g class="r" {d(0.55)}>{text_lines(46, 304, intro, 25, f'font-family="{SANS}" font-size="16.5" fill="{SOFT}"')}</g>
<g class="f" {d(0.9)}>
  <text x="46" y="388" font-family="{MONO}" font-size="13" fill="{STAR}">gauravkhandelwal.codes <tspan fill="{SUN}">&#8599;</tspan></text>
</g>
<circle class="gl" cx="{CX}" cy="{CY}" r="30" fill="{SUN}" fill-opacity=".22"/>
<circle class="p" {d(0.3)} cx="{CX}" cy="{CY}" r="16" fill="{SUN}"/>
<text class="f" {d(0.6)} x="{CX}" y="{CY + 4}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{SKY}">me</text>
{ring_svg}
<g class="f" {d(1.0)}>{''.join(planets)}</g>
<text class="f" {d(1.2)} x="{CX}" y="{h - 30}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{DIM}">things currently in orbit</text>
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                          "Gaurav Khandelwal. Student at MIT ADT University in Pune, building at Orbit. "
                          "I write software for the places around me: my campus, small suppliers, and weather desks on the coast."))


# ---- 2 · star chart: the contribution graph, one star per day ---------------------------
def radius(c):
    return 1.1 if c == 0 else 2.2 if c <= 3 else 3.2 if c <= 10 else 4.3 if c <= 25 else 5.4


def sky(data):
    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7  # sunday on top
    step, gx, gy = 15, 50, 104
    top = sorted(days, key=lambda x: -x["count"])[:12]
    top_dates = {t["date"] for t in top if t["count"] > 0}
    dots, months, seen = [], [], set()
    for i, day in enumerate(days):
        col, row = divmod(i + lead, 7)
        date = datetime.date.fromisoformat(day["date"])
        if row == 0 and date.day <= 7 and (date.year, date.month) not in seen:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        x, y = gx + col * step, gy + row * step
        delay = 0.6 + col * 0.025 + row * 0.015
        fill = SUN if day["date"] in top_dates else (STAR if c else DIM)
        op = 0.35 if c == 0 else min(1, 0.55 + c / 40)
        tip = f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title>'
        dots.append(f'<circle class="p" style="animation-delay:{delay:.2f}s" cx="{x}" cy="{y}" '
                    f'r="{radius(c)}" fill="{fill}" fill-opacity="{op:.2f}">{tip}</circle>')
        if day["date"] in top_dates:
            dots.append(f'<circle class="tw" style="animation-delay:{(i % 7) * 0.4:.1f}s" cx="{x}" cy="{y}" '
                        f'r="{radius(c) + 3}" fill="none" stroke="{SUN}" stroke-opacity=".5"/>')
    ncols = (len(days) + lead + 6) // 7
    right = gx + (ncols - 1) * step
    base = gy + 6 * step + 30
    labels = "".join(f'<text x="{gx + col * step}" y="{base}" font-family="{MONO}" font-size="11" fill="{DIM}">{m}</text>'
                     for col, m in months if col < ncols - 2)
    h = base + 30
    body = f"""
{card_bg(W, h, "sky")}
<text class="r" {d(0.3)} x="44" y="62" font-family="{SERIF}" font-size="34" fill="{STAR}">One star <tspan font-style="italic" fill="{SUN}">per day</tspan></text>
<text class="f" {d(0.3)} x="{right + 6}" y="60" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{DIM}">BRIGHTER = MORE COMMITS  ·  REFRESHED DAILY</text>
{''.join(dots)}
<g class="f" {d(2.2)}>{labels}</g>
"""
    write("sky.svg", svg(W, h, body, ["serif", "serif-i", "mono"],
                         f'Contribution graph drawn as stars: {data["total_contributions"]:,} contributions in the last year'))


# ---- 3 · flight log: monthly bars + streaks -----------------------------------------------
def log(data):
    h = 330
    monthly = data["monthly"][-12:]
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    x0, x1, base, maxh, gap = 44, 596, 282, 140, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / len(monthly)
    bars = []
    for i, m in enumerate(monthly):
        bh = max(4, round(m["total"] / best["total"] * maxh)) if m["total"] else 3
        bh = min(bh, maxh + 10)
        x = x0 + i * (bw + gap)
        partial = i == len(monthly) - 1
        fill = SUN if m is best else (LINE if partial else BLUE)
        label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        delay = 0.4 + i * 0.07
        bars.append(
            f'<rect class="g" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{base - bh}" width="{bw:.1f}" '
            f'height="{bh}" rx="4" fill="{fill}"><title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{delay:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{DIM}">{label}</text>')
        if m is best:
            bars.append(f'<text class="p" style="animation-delay:1.5s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                        f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{SUN}">{m["total"]:,}</text>')
    cs, ls = data["current_streak"]["length"], data["longest_streak"]["length"]
    best_day = datetime.date.fromisoformat(data["best_day"]["date"]).strftime("%-d %b %Y")
    stats = [
        (f'{ls} <tspan font-style="italic">days</tspan>', f"longest streak (now {cs})"),
        (f'{data["active_days"]}<tspan fill="{DIM}"> / {len(data["days"])}</tspan>', "days with a commit"),
        (f'{data["best_day"]["count"]}', f"commits on {best_day}"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 100 + i * 88
        side.append(f'<g class="r" {d(1.0 + i * 0.15)}>'
                    f'<text x="648" y="{y}" font-family="{SERIF}" font-size="38" fill="{STAR}">{big}</text>'
                    f'<text x="648" y="{y + 23}" font-family="{SANS}" font-size="13" fill="{DIM}">{escape(small)}</text></g>')
        if i < 2:
            side.append(f'<rect class="f" {d(1.0)} x="648" y="{y + 42}" width="190" height="1" fill="{LINE}"/>')
    body = f"""
{card_bg(W, h, "log")}
<text class="f" {d(0.1)} x="44" y="56" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{DIM}">FLIGHT LOG  ·  LAST 12 MONTHS</text>
<text class="r" {d(0.2)} x="42" y="110" font-family="{SERIF}" font-size="50" fill="{STAR}">{data["total_contributions"]:,} <tspan font-style="italic" fill="{SUN}">contributions</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write("log.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                         f'{data["total_contributions"]:,} contributions in the last year, longest streak {ls} days'))


# ---- 4 · section heading + project cards -------------------------------------------------
REPOS = [
    ("KampusKart", "Everything on campus in one app: events, lost and found, complaints, clubs and live chat.", "TypeScript", ROSE),
    ("Munim", "Reads an invoice, a challan and a PO, checks them, and works out what an MSME is owed.", "Python", SUN),
    ("SIH-2026", "Blends physics and AI weather models for 29 districts, weighted by recent skill.", "Python", BLUE),
    ("Kalvium-Quiz-Automaion", "Walks a whole Kalvium semester and fills in quizzes and assignments, with a review step before submit.", "Python", MINT),
    ("Nova-Career", "Resumes, applications, contacts and prep in one place, built around a career instead of a job.", "TypeScript", MINT),
    ("AI-IoT-Based-Smart-Screen", "Campus screens on Raspberry Pi, with scheduled and approved broadcasts.", "TypeScript", ROSE),
]
SHORT = {"SIH-2026": "Bharosa", "Kalvium-Quiz-Automaion": "kalbot", "Nova-Career": "Nova",
         "AI-IoT-Based-Smart-Screen": "Smart Screens"}
REPO_H = 180


def heading():
    h = 70
    body = (f'{card_bg(W, h, "hd")}<g clip-path="url(#hd)">{starfield(W, h, 40, 7)}</g>'
            f'<text class="r" {d(0.2)} x="44" y="46" font-family="{SERIF}" font-size="32" fill="{STAR}">'
            f'Things <tspan font-style="italic" fill="{SUN}">in orbit</tspan></text>'
            f'<text class="f" {d(0.3)} x="{W - 44}" y="44" text-anchor="end" font-family="{MONO}" font-size="11" '
            f'letter-spacing="1" fill="{DIM}">CLICK A CARD TO OPEN THE REPO</text>')
    write("heading.svg", svg(W, h, body, ["serif", "serif-i", "mono"], "Things in orbit"))


def repo_card(i, name, desc, lang, color, stars):
    pos = i % 3
    delay = 0.2 + i * 0.1
    meta = f"{lang}  ·  ★ {stars}" if stars else lang
    cid = f"c{i}"
    body = f"""
{card_bg(COL_W, REPO_H, cid)}
<g class="r" {d(delay)}>
  <circle cx="30" cy="36" r="9" fill="{color}" fill-opacity=".18"/><circle cx="30" cy="36" r="4.5" fill="{color}"/>
  <text x="48" y="42" font-family="{SANS}" font-weight="600" font-size="18" fill="{STAR}">{escape(SHORT.get(name, name))}</text>
  {text_lines(24, 76, wrap(desc, 33), 21, f'font-family="{SANS}" font-size="14" fill="{SOFT}"')}
  <text x="24" y="{REPO_H - 22}" font-family="{MONO}" font-size="12" fill="{DIM}">{escape(meta)}</text>
  <text x="{COL_W - 24:.1f}" y="{REPO_H - 22}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{color}">&#8599;</text>
</g>
"""
    write(f"repo-{i + 1}.svg", svg(COL_W, REPO_H, body, ["sans", "sans-b", "mono"], f"{SHORT.get(name, name)}: {desc}",
                                   left=4 * pos, right=8 - 4 * pos))


def repo_stars():
    stars = {}
    try:
        import requests
        headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {}
        for name, *_ in REPOS:
            r = requests.get(f"https://api.github.com/repos/{USER}/{name}", headers=headers, timeout=10)
            if r.ok:
                stars[name] = r.json().get("stargazers_count", 0)
    except Exception as e:  # offline: cards still render, just without star counts
        print(f"stars unavailable: {e}")
    return stars


if __name__ == "__main__":
    data = json.load(open(DATA))
    hero()
    sky(data)
    log(data)
    heading()
    stars = repo_stars()
    for i, repo in enumerate(REPOS):
        repo_card(i, *repo, stars.get(repo[0], 0))
