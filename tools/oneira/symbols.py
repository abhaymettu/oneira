"""The rest of Latin-1: currency, signs, superiors, fractions, ordinals and
the invisible characters."""

import math

from . import figures, lower, upper
from .geom import Shape, arc, lerp, limb, ring, wedge
from .params import CAP, DESC, OV, XH, P, glyph
from .parts import cup, round_o, stem
from .punct import MATH, _hbar, hyphen

SUP = 0.62  # superiors and ordinals, as a share of full size


def small(p, k, keep=0.78):
    """A master for drawing at scale k: heavy enough that, once scaled, its
    stems are `keep` of the full-size stem."""
    t = (keep / k * p.stem - 30) / 146
    return P(min(t, 1.12), p.w)


def _sup(fn, p, k=SUP, y=CAP * (1 - SUP)):
    """fn drawn small, its baseline at y."""
    return fn(small(p, k)).scaled(k, 0, y)


def _left(s):
    x0, _ = s.xbounds()
    return s.moved(-x0)


# ---------- invisible ----------

@glyph("uni00A0", 0xA0)
def nbspace(p):
    return Shape(), round(p.W(250, 270))


@glyph("uni00AD", 0xAD, "OO", air=1.6)
def softhyphen(p):
    return hyphen(p)


# ---------- currency ----------

def _vbar(s, p, cx, y0, y1, w):
    s.rect(cx - w / 2, y0, cx + w / 2, y1, r=p.end_r * 0.6)


@glyph("cent", 0xA2, "RO")
def cent(p):
    s = lower.c(p)
    x0, x1 = s.xbounds()
    cx = x0 + (x1 - x0) * 0.52
    w = p.stem * 0.7
    _vbar(s, p, cx, -120, -OV + p.sh * 0.5, w)
    _vbar(s, p, cx, XH + OV - p.sh * 0.5, XH + 120, w)
    return s


@glyph("sterling", 0xA3, "OO")
def sterling(p):
    """An f-like stem with a hooked top, a cross bar, and a base bar it
    stands on."""
    s = Shape()
    W = p.W(500, 620)
    x = p.W(96, 120)
    rxh, ryh = p.W(170, 222), p.W(166, 182)
    top = CAP + OV
    cyh = top - ryh
    outer = (x + rxh, cyh, rxh, ryh)
    li, ri = x + p.stem, x + 2 * rxh - p.rv
    inner = ((li + ri) / 2, cyh, (ri - li) / 2, ryh - p.sh)
    arc(s, outer, inner, 30, 186, (p.tip(), None))
    stem(s, p, x, p.sh - 4, cyh + 4, foot=False, head=False)
    _hbar(s, p, 0, x + p.stem + p.W(170, 190), CAP * 0.42)
    s.rect(0, 0, W, p.sh, r=p.bar_r)
    return s


@glyph("yen", 0xA5, "OO")
def yen(p):
    s = upper.Y(p)
    x0, x1 = s.xbounds()
    cx = (x0 + x1) / 2
    half = p.W(196, 240)
    t = p.sh * 0.9
    for y in (CAP * 0.36, CAP * 0.36 - t * 1.9):
        _hbar(s, p, cx - half, cx + half, y, t)
    return s


@glyph("Euro", 0x20AC, "OR")
def euro(p):
    """A C with two bars that start in the left sidebearing."""
    s = Shape()
    rx, ry = p.W(330, 372), CAP / 2 + OV
    lead = p.W(90, 100)
    cx = rx + lead
    arc(s, (cx, CAP / 2, rx, ry), (cx, CAP / 2, rx - p.rv, ry - p.sh), 50, 310, (p.tip(), p.tip()))
    t = p.sh * 0.9
    gap = p.W(118, 150)
    for y in (CAP / 2 + gap / 2 + t / 2, CAP / 2 - gap / 2 - t / 2):
        _hbar(s, p, 0, cx + rx * 0.36, y, t)
    return s


@glyph("currency", 0xA4, "OO", air=1.2)
def currency(p):
    s = Shape()
    sw = p.stem * p.W(0.84, 0.66)
    r = p.W(150, 176)
    c = r + sw * 1.4
    ring(s, (c, MATH, r, r), (c, MATH, r - sw, r - sw * 0.92))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        u = (math.cos(a), math.sin(a))
        a_ = (c + u[0] * (r - sw / 2), MATH + u[1] * (r - sw / 2))
        b_ = (c + u[0] * (r + sw * 1.3), MATH + u[1] * (r + sw * 1.3))
        limb(s, a_, b_, sw, r=(0, p.bar_r))
    return s


# ---------- signs ----------

@glyph("logicalnot", 0xAC, "OO", air=1.2)
def logicalnot(p):
    s = Shape()
    W = p.W(440, 500)
    t = p.sh
    y = MATH + p.W(40, 50)
    s.poly([(0, y - t / 2), (W, y - t / 2), (W, y + t / 2), (0, y + t / 2)], [p.bar_r, 0, 0, p.bar_r])
    v = p.stem * 0.86
    drop = p.W(170, 190)
    s.poly([(W - v, y - drop), (W, y - drop), (W, y + t / 2), (W - v, y + t / 2)],
           [p.bar_r, p.bar_r, p.bar_r * 0.4, 0])
    return s


@glyph("mu", 0xB5, "SS")
def mu(p):
    s = Shape()
    W = lower._n_width(p)
    cy = cup(s, p, 0, W)
    stem(s, p, 0, DESC, XH)
    stem(s, p, W - p.stem, 0, XH)
    return s


@glyph("paragraph", 0xB6, "OS")
def paragraph(p):
    """Pilcrow: a solid half-round flag and two stems down to the descender."""
    s = Shape()
    W = p.W(470, 600)
    v = p.stem * 0.9
    x2 = W - v
    x1 = x2 - p.W(110, 150) - v
    y_low = CAP * 0.36
    ry = (CAP - y_low) / 2
    rx = min(ry * 1.05, x1 + v * 0.5)
    cx = x1 + v * 0.5
    s.contours.append(_close_flag(cx, y_low, ry, rx))  # the flag, closed by the first stem
    for x in (x1, x2):
        stem(s, p, x, DESC, CAP - 4, head=False)
    s.poly([(cx, CAP - p.sh), (W, CAP - p.sh), (W, CAP), (cx, CAP)], [0, p.bar_r, p.bar_r, 0])
    return s


def _close_flag(cx, y0, ry, rx):
    """Left half ellipse from top to bottom (counter-clockwise), closed by a
    straight edge just inside the first stem."""
    k = 0.5523
    cy = y0 + ry
    top, left, bot = (cx, cy + ry), (cx - rx, cy), (cx, y0)
    return [("line", [top]),
            ("curve", [(cx - rx * k, cy + ry), (cx - rx, cy + ry * k), left]),
            ("curve", [(cx - rx, cy - ry * k), (cx - rx * k, y0), bot]),
            ("line", [(cx + 6, y0)]),
            ("line", [(cx + 6, cy + ry)])]


@glyph("section", 0xA7, "RR")
def section(p):
    """Two s shapes stacked so the lower bowl of one and the upper bowl of
    the other close into a ring at the middle."""
    k = 0.8
    sp = small(p, k, 0.9)
    a = lower.s_(sp).scaled(k)
    h = (XH + OV) * k
    top = CAP + OV - h
    s = Shape().merged(a.moved(0).scaled(1, 0, top), a.scaled(1, 0, top - h * 0.5))
    return s


# ---------- superiors, ordinals, fractions ----------

@glyph("onesuperior", 0xB9, "OO", air=1.0)
def onesuperior(p):
    return _sup(figures.one, p)


@glyph("twosuperior", 0xB2, "OO", air=1.0)
def twosuperior(p):
    return _sup(figures.two, p)


@glyph("threesuperior", 0xB3, "OO", air=1.0)
def threesuperior(p):
    return _sup(figures.three, p)


@glyph("ordfeminine", 0xAA, "OO", air=1.0)
def ordfeminine(p):
    return _ordinal(lower.a, p)


@glyph("ordmasculine", 0xBA, "OO", air=1.0)
def ordmasculine(p):
    return _ordinal(lower.o, p)


def _ordinal(fn, p):
    k = SUP * 0.95
    sp = small(p, k)
    g = _left(fn(sp)).scaled(k)
    x0, x1 = g.xbounds()
    base = CAP - (XH + OV) * k
    t = p.sh * 0.8
    gap = p.W(70, 60)
    s = g.scaled(1, 0, base)
    s.rect(x0, base - gap - t, x1, base - gap, r=p.bar_r)
    return s


def _fraction(p, num, den):
    """Numerator raised, denominator on the baseline, a fraction slash between
    them. The figures tuck under the slash."""
    k = 0.56
    sp = small(p, k)
    n = _left(num(sp)).scaled(k, 0, CAP * (1 - k))
    d = _left(den(sp)).scaled(k)
    _, nx1 = n.xbounds()
    sl = Shape()
    w = p.dstem * 0.72
    lean = CAP * 0.46
    xs = nx1 + p.W(10, 20)
    limb(sl, (xs - lean * 0.5 + w, 0), (xs + lean * 0.5 + w, CAP), w, ("h", "h"))
    d = d.moved(xs + w + p.W(10, 20))
    return Shape().merged(n, sl, d)


@glyph("onequarter", 0xBC, "OO", air=0.9)
def onequarter(p):
    return _fraction(p, figures.one, figures.four)


@glyph("onehalf", 0xBD, "OO", air=0.9)
def onehalf(p):
    return _fraction(p, figures.one, figures.two)


@glyph("threequarters", 0xBE, "OO", air=0.9)
def threequarters(p):
    return _fraction(p, figures.three, figures.four)


# ---------- circled ----------

def _circled(p, fn):
    s = Shape()
    R = p.W(400, 450)
    sw = p.stem * p.W(0.8, 0.6)
    c = (R, CAP / 2)
    ring(s, (c[0], c[1], R, R), (c[0], c[1], R - sw, R - sw))
    k = 0.5
    g = _left(fn(small(p, k, 0.62))).scaled(k)
    x0, x1 = g.xbounds()
    return s.merged(g.moved(c[0] - (x1 - x0) / 2).scaled(1, 0, c[1] - CAP * k / 2))


@glyph("copyright", 0xA9, "RR", air=0.9)
def copyright(p):
    return _circled(p, upper.C)


@glyph("registered", 0xAE, "RR", air=0.9)
def registered(p):
    return _circled(p, upper.R)
