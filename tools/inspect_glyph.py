"""Draw glyph outlines from a master UFO as SVG: fill, contours, on-curve
points, handles, metrics. Then screenshot with headless Chromium.
usage: inspect_glyph.py OUT.png MASTER.ufo glyph [glyph ...]"""

import subprocess
import sys
from pathlib import Path

import ufoLib2

CHROME = next(Path.home().glob(
    "Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"))


def glyph_svg(font, name, x0):
    g = font[name]
    parts, dots = [], []
    for c in g.contours:
        pts = list(c.points)
        # rotate so we start on an on-curve point
        k = next(i for i, p in enumerate(pts) if p.type)
        pts = pts[k + 1:] + pts[:k + 1]
        d = f"M{pts[-1].x + x0},{-pts[-1].y}"
        buf = []
        for p in pts:
            if p.type is None:
                buf.append(p)
                continue
            if p.type == "curve":
                (a, b) = buf
                d += f" C{a.x + x0},{-a.y} {b.x + x0},{-b.y} {p.x + x0},{-p.y}"
            else:
                d += f" L{p.x + x0},{-p.y}"
            buf = []
        parts.append(d + " Z")
        prev = pts[-1]
        for p in pts:
            if p.type is None:
                dots.append(f'<circle cx="{p.x + x0}" cy="{-p.y}" r="5" fill="none" stroke="#e5484d" stroke-width="2"/>')
            else:
                dots.append(f'<rect x="{p.x + x0 - 5}" y="{-p.y - 5}" width="10" height="10" fill="#fff" stroke="#111" stroke-width="2"/>')
        for i, p in enumerate(pts):  # handles
            if p.type is None:
                q = pts[i - 1] if pts[i - 1].type else pts[(i + 1) % len(pts)]
                dots.append(f'<line x1="{q.x + x0}" y1="{-q.y}" x2="{p.x + x0}" y2="{-p.y}" stroke="#e5484d" stroke-width="1.5"/>')
    path = " ".join(parts)
    return (f'<path d="{path}" fill="#2a6bff" fill-opacity="0.18" fill-rule="nonzero"/>'
            f'<path d="{path}" fill="none" stroke="#111" stroke-width="1.5"/>' + "".join(dots)), g.width


def main():
    out, ufo, names = sys.argv[1], sys.argv[2], sys.argv[3:]
    f = ufoLib2.Font.open(ufo)
    i = f.info
    body, x = [], 0
    for n in names:
        s, w = glyph_svg(f, n, x)
        body.append(s)
        body.append(f'<line x1="{x}" y1="-1000" x2="{x}" y2="400" stroke="#aaa" stroke-dasharray="6 6"/>')
        x += w
    lines = "".join(
        f'<line x1="-50" y1="{-y}" x2="{x + 50}" y2="{-y}" stroke="#bbb" stroke-width="1"/>'
        for y in (0, i.xHeight, i.capHeight, i.ascender, i.descender))
    W = x + 100
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -900 {W} 1200" '
           f'width="{W * 0.9:.0f}" height="1080">{lines}{"".join(body)}</svg>')
    html = Path("/tmp/oneira-proof/inspect.html")
    html.parent.mkdir(exist_ok=True)
    html.write_text(f"<html><body style='margin:0;background:#fff'>{svg}</body></html>")
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--user-data-dir=/tmp/oneira-proof/ud",
                    f"--screenshot={Path(out).resolve()}", f"--window-size={int(W * 0.9)},1080",
                    f"file://{html}"], capture_output=True, check=True)


if __name__ == "__main__":
    main()
