"""Accent marks and the accented letters built from them as composites.

Every mark is drawn centred on x = 0 with its lowest ink on y = 0 (cedilla:
highest ink on y = 0), so placing one is a plain offset."""

import math

from fontTools.pens.boundsPen import BoundsPen

from .geom import SQRT3, Shape, Tip, _area, arc, chevron, lerp, ring, tittle
from .params import composite, glyph


def _settle(s, hang=False):
    """Centre the mark on x = 0; rest it on y = 0, or hang it from y = 0."""
    bp = BoundsPen(None)
    s.draw(bp)
    x0, y0, x1, y1 = bp.bounds
    dx, dy = -(x0 + x1) / 2, (-y1 if hang else -y0)
    out = Shape()
    out.contours = [[(k, [(x + dx, y + dy) for x, y in pts]) for k, pts in c] for c in s.contours]
    return out, 0


def _taper(s, p, lo, hi, w_lo, w_hi):
    """A stroke that narrows toward `lo`: the triangle drawn long."""
    ln = math.dist(lo, hi)
    n = (-(hi[1] - lo[1]) / ln, (hi[0] - lo[0]) / ln)
    pts = [(lo[0] - n[0] * w_lo / 2, lo[1] - n[1] * w_lo / 2), (lo[0] + n[0] * w_lo / 2, lo[1] + n[1] * w_lo / 2),
           (hi[0] + n[0] * w_hi / 2, hi[1] + n[1] * w_hi / 2), (hi[0] - n[0] * w_hi / 2, hi[1] - n[1] * w_hi / 2)]
    rl = lerp(w_lo * 0.49, p.soft * 0.4, p.w)
    rh = lerp(p.end_r, p.soft, p.w)
    radii = [rl, rl, rh, rh]
    if _area(pts) < 0:
        pts, radii = pts[::-1], radii[::-1]
    s.poly(pts, radii)


def _slant(p, sign):
    s = Shape()
    ln = p.W(200, 210)
    a = math.radians(52)
    _taper(s, p, (0, 0), (sign * ln * math.cos(a), ln * math.sin(a)),
           lerp(p.stem * 0.36, 3, p.w), p.stem * p.W(1.05, 0.9))
    return _settle(s)


@glyph("acutecomb", 0x0301)
def acutecomb(p):
    return _slant(p, 1)


@glyph("gravecomb", 0x0300)
def gravecomb(p):
    return _slant(p, -1)


@glyph("circumflexcomb", 0x0302)
def circumflexcomb(p):
    s = Shape()
    w, h = p.W(156, 186), p.W(150, 160)
    chevron(s, (0, h), (-w, 0), (w, 0), p.stem * p.W(0.86, 0.74),
            lerp(p.stem * 0.3, p.soft, p.w), lerp(p.stem * 0.2, p.soft * 0.5, p.w))
    return _settle(s)


def _mark_dot(s, p, cx):
    r = p.stem * 0.5 + 14
    side = lerp(2 * SQRT3, 2.5, p.w) * r
    inr = side / (2 * SQRT3)
    tittle(s, cx, lerp(r, 2 * inr, p.w), r, p.w, p.soft)
    return side


@glyph("dieresiscomb", 0x0308)
def dieresiscomb(p):
    s = Shape()
    gap = (p.stem * 0.5 + 14) * 2.5 + p.W(80, 60)
    _mark_dot(s, p, -gap / 2)
    _mark_dot(s, p, gap / 2)
    return _settle(s)


@glyph("ringcomb", 0x030A)
def ringcomb(p):
    s = Shape()
    sw = p.stem * p.W(0.8, 0.62)
    r = sw + p.W(70, 54)
    ring(s, (0, r, r * 1.04, r), (0, r, r * 1.04 - sw, r - sw * 0.9))
    return _settle(s)


@glyph("tildecomb", 0x0303)
def tildecomb(p):
    s = Shape()
    sw = p.stem * p.W(0.84, 0.6)
    t = p.sh * p.W(0.92, 0.6)
    rx, ry = sw + p.W(46, 30), p.W(62, 84)
    arc(s, (rx, 0, rx, ry), (rx, 0, rx - sw, ry - t), 0, 180, (None, Tip(0, p.soft)))
    arc(s, (3 * rx - sw, 0, rx, ry), (3 * rx - sw, 0, rx - sw, ry - t), 176, 360, (None, Tip(0, p.soft)))
    return _settle(s)


@glyph("macroncomb", 0x0304)
def macroncomb(p):
    s = Shape()
    w = p.W(260, 300)
    s.rect(-w / 2, 0, w / 2, p.sh, r=p.bar_r)
    return _settle(s)


@glyph("cedillacomb", 0x0327)
def cedillacomb(p):
    s = Shape()
    ln = p.W(190, 210)
    a = math.radians(-118)
    _taper(s, p, (ln * math.cos(a), ln * math.sin(a)), (0, 0),
           lerp(p.stem * 0.36, 3, p.w), p.stem * p.W(0.95, 0.8))
    return _settle(s, hang=True)


# ---------- spacing marks ----------

SPACING = {"grave": (0x60, "gravecomb"), "acute": (0xB4, "acutecomb"), "dieresis": (0xA8, "dieresiscomb"),
           "macron": (0xAF, "macroncomb"), "cedilla": (0xB8, "cedillacomb"), "circumflex": (0x2C6, "circumflexcomb"),
           "tilde": (0x2DC, "tildecomb"), "ring": (0x2DA, "ringcomb")}
for _name, (_uni, _mark) in SPACING.items():
    composite(_name, _uni, None, [(_mark, "cedilla" if _mark == "cedillacomb" else "lc")])

# ---------- accented letters ----------

ACCENTS = {"grave": "gravecomb", "acute": "acutecomb", "circumflex": "circumflexcomb", "tilde": "tildecomb",
           "dieresis": "dieresiscomb", "ring": "ringcomb", "cedilla": "cedillacomb"}

LATIN1 = [
    ("A", "grave", 0xC0), ("A", "acute", 0xC1), ("A", "circumflex", 0xC2), ("A", "tilde", 0xC3),
    ("A", "dieresis", 0xC4), ("A", "ring", 0xC5), ("C", "cedilla", 0xC7),
    ("E", "grave", 0xC8), ("E", "acute", 0xC9), ("E", "circumflex", 0xCA), ("E", "dieresis", 0xCB),
    ("I", "grave", 0xCC), ("I", "acute", 0xCD), ("I", "circumflex", 0xCE), ("I", "dieresis", 0xCF),
    ("N", "tilde", 0xD1), ("O", "grave", 0xD2), ("O", "acute", 0xD3), ("O", "circumflex", 0xD4),
    ("O", "tilde", 0xD5), ("O", "dieresis", 0xD6), ("U", "grave", 0xD9), ("U", "acute", 0xDA),
    ("U", "circumflex", 0xDB), ("U", "dieresis", 0xDC), ("Y", "acute", 0xDD), ("Y", "dieresis", 0x178),
]

for base, acc, uni in LATIN1:
    anchor = "cedilla" if acc == "cedilla" else "cap"
    composite(base + acc, uni, base, [(ACCENTS[acc], anchor)])
    lc = base.lower()
    lc_uni = 0xFF if (base, acc) == ("Y", "dieresis") else uni + 0x20
    lc_base = "dotlessi" if lc == "i" else lc
    composite(lc + acc, lc_uni, lc_base, [(ACCENTS[acc], "cedilla" if acc == "cedilla" else "lc")])

