"""Punctuation and symbols. Dots are the i's triangle dot; quotes and commas
are that dot with a falling tail."""

import math

from .geom import SQRT3, Shape, Tip, arc, chevron, lerp, limb, ring, tittle, wedge
from .params import ASC, CAP, DESC, OV, XH, P, glyph
from .parts import stem

MATH = 330  # centre line of math signs, dashes and guillemets
# a short point on a small stroke; shorter ones lose weight half way between
# dream and lucid, because the round cap and the point blend badly
SHORT_TIP = 0.7


def _dot_r(p):
    return p.stem * 0.5 + 14


def _dot(s, p, cx, low=0.0):
    """The triangle dot with its lowest point at `low`. Returns its top."""
    r = _dot_r(p)
    side = lerp(2 * SQRT3, 2.5, p.w) * r
    inr = side / (2 * SQRT3)
    down = lerp(r, 2 * inr, p.w)  # centre to lowest point
    tittle(s, cx, low + down, r, p.w, p.soft)
    return low + down + lerp(r, inr, p.w)


def _comma(s, p, cx, top, flip=False):
    """The dot with a tail falling to the left; flip turns it upside down (the
    opening quote)."""
    r = _dot_r(p)
    side = lerp(2, 2.5, p.w) * r
    # the tail's length follows weight alone: tied to the dot, it was a
    # stub at Thin (a comma read as a period) and a spike at Black lucid
    drop = p.W(185, 380)
    pts = [(cx + side * 0.5, top), (cx - side * 0.5, top), (cx - side * 0.32, top - drop)]
    radii = [lerp(r * 0.96, p.soft, p.w)] * 2 + [lerp(r * 0.22, p.soft * 0.7, p.w)]
    if flip:
        y_mid = top - drop / 2
        pts = [(2 * cx - x, 2 * y_mid - y) for x, y in pts]
    s.poly(pts, radii)
    return side


def _dot_top(p):
    r = _dot_r(p)
    inr = lerp(2 * SQRT3, 2.5, p.w) * r / (2 * SQRT3)
    return lerp(r, 2 * inr, p.w) + lerp(r, inr, p.w)


# ---------- dots ----------

@glyph("period", 0x2E, "OO", air=2.4)
def period(p):
    s = Shape()
    _dot(s, p, 0)
    return s


@glyph("comma", 0x2C, "OO", air=2.4)
def comma(p):
    s = Shape()
    _comma(s, p, 0, _dot_top(p))
    return s


@glyph("colon", 0x3A, "OO", air=2.4)
def colon(p):
    s = Shape()
    _dot(s, p, 0)
    _dot(s, p, 0, XH - _dot_top(p))
    return s


@glyph("semicolon", 0x3B, "OO", air=2.4)
def semicolon(p):
    s = Shape()
    _comma(s, p, 0, _dot_top(p))
    _dot(s, p, 0, XH - _dot_top(p))
    return s


@glyph("ellipsis", 0x2026, "OO", air=2.4)
def ellipsis(p):
    s = Shape()
    gap = _dot_r(p) * 2.5 + p.W(110, 90)
    for i in range(3):
        _dot(s, p, i * gap)
    return s


@glyph("periodcentered", 0xB7, "OO", air=2.4)
def periodcentered(p):
    s = Shape()
    _dot(s, p, 0, MATH - _dot_top(p) / 2)
    return s


@glyph("bullet", 0x2022, "OO", air=2.0)
def bullet(p):
    s = Shape()
    r = _dot_r(p) * 1.5
    side = lerp(2 * SQRT3, 2.5, p.w) * r
    inr = side / (2 * SQRT3)
    tittle(s, 0, MATH + lerp(0, inr * 0.5, p.w), r, p.w, p.soft)
    return s


def _gap(p):
    """Between a dot and the point above it (! ?)."""
    return p.W(90, 84)


def _bang(s, p, cx, y_lo, y_hi):
    """A stem that tapers to a point: the triangle drawn long."""
    top = p.stem * 1.12 / 2
    bot = lerp(p.stem * 0.24, 2, p.w)
    rt = lerp(p.end_r, p.soft, p.w)
    rb = lerp(bot * 0.98, p.soft * 0.4, p.w)
    s.poly([(cx - bot, y_lo), (cx + bot, y_lo), (cx + top, y_hi), (cx - top, y_hi)], [rb, rb, rt, rt])


@glyph("exclam", 0x21, "OO", air=2.0)
def exclam(p):
    s = Shape()
    t = _dot_top(p)
    _dot(s, p, 0)
    _bang(s, p, 0, t + _gap(p), CAP)
    return s


@glyph("exclamdown", 0xA1, "OO", air=2.0)
def exclamdown(p):
    return exclam(p).rotated(0, XH / 2)  # dot up at the x-height, point below the baseline


@glyph("question", 0x3F, "OO", air=1.3)
def question(p):
    s = Shape()
    w = p.stem * p.W(0.94, 0.8)
    # bottom up: the dot, the same gap as the exclam's, the stem's point, a
    # short neck; the hook gets what is left, so at Black it sits higher
    # rather than letting the point run into the dot
    tip = Tip(p.w, p.soft, scale=SHORT_TIP)
    y_lo = _dot_top(p) + _gap(p) + tip.reach(w / 2)
    rx = p.W(196, 258)
    ry = min(p.W(188, 214), (CAP + OV + p.sh * 0.5 - y_lo - p.W(60, 16)) / 2)
    cx, cy = rx, CAP + OV - ry
    arc(s, (cx, cy, rx, ry), (cx, cy, rx - p.rv, ry - p.sh), -90, 160, (None, p.tip()))
    # the stem hangs from the hook's end, its left edge flush with the cut
    s.rect(cx, y_lo, cx + w, cy - ry + p.sh * 0.5)
    tip.draw(s, (cx + w, y_lo), (cx, y_lo), (0, 1))
    _dot(s, p, cx + w / 2)
    return s


@glyph("questiondown", 0xBF, "OO", air=1.3)
def questiondown(p):
    q = question(p)
    x0, x1 = q.xbounds()
    return q.rotated((x0 + x1) / 2, XH / 2)


# ---------- quotes ----------

def _quote_top(p):
    return CAP + OV


@glyph("quoteright", 0x2019, "OO", air=2.4)
def quoteright(p):
    s = Shape()
    _comma(s, p, 0, _quote_top(p))
    return s


@glyph("quoteleft", 0x2018, "OO", air=2.4)
def quoteleft(p):
    s = Shape()
    _comma(s, p, 0, _quote_top(p), flip=True)
    return s


@glyph("quotesinglbase", 0x201A, "OO", air=2.4)
def quotesinglbase(p):
    return comma(p)


def _pair(fn, p):
    s = Shape()
    gap = _dot_r(p) * 2.5 + p.W(60, 50)
    for i in range(2):
        fn(s, i * gap)
    return s


@glyph("quotedblright", 0x201D, "OO", air=2.4)
def quotedblright(p):
    return _pair(lambda s, x: _comma(s, p, x, _quote_top(p)), p)


@glyph("quotedblleft", 0x201C, "OO", air=2.4)
def quotedblleft(p):
    return _pair(lambda s, x: _comma(s, p, x, _quote_top(p), flip=True), p)


@glyph("quotedblbase", 0x201E, "OO", air=2.4)
def quotedblbase(p):
    return _pair(lambda s, x: _comma(s, p, x, _dot_top(p)), p)


@glyph("quotesingle", 0x27, "OO", air=2.4)
def quotesingle(p):
    s = Shape()
    _bang(s, p, 0, CAP - p.W(230, 250), CAP + OV)
    return s


@glyph("quotedbl", 0x22, "OO", air=2.4)
def quotedbl(p):
    gap = p.stem * 1.12 + p.W(80, 70)
    s = Shape()
    for i in range(2):
        _bang(s, p, i * gap, CAP - p.W(230, 250), CAP + OV)
    return s


# ---------- dashes and lines ----------

def _hbar(s, p, x0, x1, y_mid, t=None):
    t = p.sh if t is None else t
    s.rect(x0, y_mid - t / 2, x1, y_mid + t / 2, r=p.bar_r)


@glyph("hyphen", 0x2D, "OO", air=1.6)
def hyphen(p):
    s = Shape()
    _hbar(s, p, 0, p.W(250, 290), MATH - 30, p.sh * 1.05)
    return s


@glyph("endash", 0x2013, "OO", air=1.0)
def endash(p):
    s = Shape()
    _hbar(s, p, 0, 500, MATH - 30, p.sh * 1.05)
    return s


@glyph("emdash", 0x2014)
def emdash(p):
    s = Shape()
    _hbar(s, p, 30, 970, MATH - 30, p.sh * 1.05)
    return s, 1000


@glyph("underscore", 0x5F, "OO", air=0.3)
def underscore(p):
    s = Shape()
    _hbar(s, p, 0, 520, DESC * 0.55)
    return s


@glyph("bar", 0x7C, "SS")
def bar(p):
    s = Shape()
    s.rect(0, DESC * 0.82, p.stem * 0.9, ASC + 40, r=p.end_r)
    return s


@glyph("brokenbar", 0xA6, "SS")
def brokenbar(p):
    s = Shape()
    w, mid = p.stem * 0.9, (DESC * 0.82 + ASC + 40) / 2
    s.rect(0, DESC * 0.82, w, mid - 50, r=p.end_r)
    s.rect(0, mid + 50, w, ASC + 40, r=p.end_r)
    return s


@glyph("slash", 0x2F, "OO", air=0.9)
def slash(p):
    s = Shape()
    limb(s, (0, DESC * 0.6), (p.W(330, 400), CAP + 60), p.dstem * 0.9, ("h", "h"))
    return s


@glyph("backslash", 0x5C, "OO", air=0.9)
def backslash(p):
    s = Shape()
    limb(s, (p.W(330, 400), DESC * 0.6), (0, CAP + 60), p.dstem * 0.9, ("h", "h"))
    return s


# ---------- brackets ----------

BR_LO, BR_HI = DESC * 0.62, CAP + 70


@glyph("parenleft", 0x28, "RO", air=1.2)
def parenleft(p):
    s = Shape()
    ry = (BR_HI - BR_LO) / 2
    rx = p.W(250, 300)
    cy = BR_LO + ry
    sw = p.rv * 0.94
    arc(s, (rx, cy, rx, ry), (rx, cy, rx - sw, ry - p.sh * 0.5), 112, 248, (p.tip(), p.tip()))
    return s


@glyph("parenright", 0x29, "OR", air=1.2)
def parenright(p):
    pl = parenleft(p)
    x0, x1 = pl.xbounds()
    return pl.rotated((x0 + x1) / 2, (BR_LO + BR_HI) / 2)


@glyph("bracketleft", 0x5B, "SO", air=1.1)
def bracketleft(p):
    s = Shape()
    w = p.W(190, 250)
    stem(s, p, 0, BR_LO, BR_HI, foot=False, head=False)
    for y0 in (BR_LO, BR_HI - p.sh):
        s.poly([(p.stem / 2, y0), (w, y0), (w, y0 + p.sh), (p.stem / 2, y0 + p.sh)], [0, p.bar_r, p.bar_r, 0])
    # outer corners soften in the dream state like every other free corner
    return s


@glyph("bracketright", 0x5D, "OS", air=1.1)
def bracketright(p):
    b = bracketleft(p)
    x0, x1 = b.xbounds()
    return b.rotated((x0 + x1) / 2, (BR_LO + BR_HI) / 2)


@glyph("braceleft", 0x7B, "OO", air=1.1)
def braceleft(p):
    s = Shape()
    sw = p.stem * p.W(0.92, 0.8)
    R = sw + p.W(84, 70)  # radius of the hooks at both ends; the counter stays open
    xs = R * 0.55  # stem's left edge; the point at the middle reaches x = 0
    mid = (BR_LO + BR_HI) / 2
    ry = R
    for sign, y_end in ((1, BR_HI), (-1, BR_LO)):
        cy = y_end - sign * ry
        e = (xs + R, cy, R, ry)
        ei = (xs + R, cy, R - sw, ry - p.sh)
        a0, a1 = (90, 180) if sign > 0 else (180, 270)
        tips = (p.tip(), None) if sign > 0 else (None, p.tip())
        arc(s, e, ei, a0, a1, tips)
        lo, hi = sorted((cy + sign * 2, mid - sign * 3))  # the halves overlap at the middle
        s.rect(xs, lo, xs + sw, hi)
    # the middle point: a triangle on its side, the brace's one wedge
    h = sw * lerp(1.0, 1.1, p.w)
    s.poly([(xs + sw * 0.5, mid - h), (xs + sw * 0.5, mid + h), (0, mid)],
           [0, 0, lerp(h * 0.6, p.soft, p.w)])
    return s


@glyph("braceright", 0x7D, "OO", air=1.1)
def braceright(p):
    b = braceleft(p)
    x0, x1 = b.xbounds()
    return b.rotated((x0 + x1) / 2, (BR_LO + BR_HI) / 2)


# ---------- math ----------

def math_sign(name, uni):
    """Math signs share one advance, so figures and signs line up in tables.
    Centred on the dream state, like every other glyph's spacing."""
    def deco(draw):
        def fn(p):
            A = p.W(600, 690)
            x0, x1 = draw(P(p.t, 0)).xbounds()
            return draw(p).moved((A - x0 - x1) / 2), A
        glyph(name, uni)(fn)
        return draw
    return deco

def _cross(s, p, cx, cy, half):
    _hbar(s, p, cx - half, cx + half, cy)
    v = p.stem * 0.86
    s.rect(cx - v / 2, cy - half, cx + v / 2, cy + half, r=p.bar_r)


@math_sign("plus", 0x2B)
def plus(p):
    s = Shape()
    half = p.W(240, 260)
    _cross(s, p, half, MATH, half)
    return s


@math_sign("minus", 0x2212)
def minus(p):
    s = Shape()
    _hbar(s, p, 0, 2 * p.W(240, 260), MATH)
    return s


@math_sign("equal", 0x3D)
def equal(p):
    s = Shape()
    w = 2 * p.W(240, 260)
    gap = p.W(120, 150) + p.sh
    _hbar(s, p, 0, w, MATH + gap / 2)
    _hbar(s, p, 0, w, MATH - gap / 2)
    return s


@math_sign("plusminus", 0xB1)
def plusminus(p):
    s = Shape()
    half = p.W(240, 260)
    _cross(s, p, half, MATH + 70, half * 0.86)
    _hbar(s, p, 0, 2 * half, MATH + 70 - half * 0.86 - p.W(70, 90) - p.sh / 2)
    return s


@math_sign("multiply", 0xD7)
def multiply(p):
    s = Shape()
    h = p.W(200, 210)
    w = p.stem * 0.86
    for dx in (1, -1):
        limb(s, (h - dx * h, MATH - h), (h + dx * h, MATH + h), w)
    return s


@math_sign("divide", 0xF7)
def divide(p):
    s = Shape()
    half = p.W(240, 260)
    _hbar(s, p, 0, 2 * half, MATH)
    q = P(p.t * 0.6, p.w)  # lighter dots, so they stay inside the plus at Black
    t = _dot_top(q)
    gap = p.W(70, 50) + p.sh / 2
    _dot(s, q, half, MATH + gap)
    _dot(s, q, half, MATH - gap - t)
    return s


@math_sign("less", 0x3C)
def less(p):
    s = Shape()
    w, h = p.W(400, 390), p.W(220, 230)
    chevron(s, (0, MATH), (w, MATH + h), (w, MATH - h), p.stem * 0.86,
            lerp(p.stem * 0.3, p.soft, p.w), p.bar_r)
    return s


@math_sign("greater", 0x3E)
def greater(p):
    s = Shape()
    w, h = p.W(400, 390), p.W(220, 230)
    chevron(s, (w, MATH), (0, MATH + h), (0, MATH - h), p.stem * 0.86,
            lerp(p.stem * 0.3, p.soft, p.w), p.bar_r)
    return s


@glyph("asciicircum", 0x5E, "OO", air=1.2)
def asciicircum(p):
    s = Shape()
    w, h = p.W(400, 460), p.W(250, 270)
    chevron(s, (w / 2, CAP), (0, CAP - h), (w, CAP - h), p.stem * 0.8,
            lerp(p.stem * 0.3, p.soft, p.w), p.bar_r)
    return s


def _guil(s, p, x, point_left, scale=1.0):
    w, h = p.W(200, 230) * scale, p.W(190, 210) * scale
    t = p.stem * 0.82
    tip_x, end_x = (x, x + w) if point_left else (x + w, x)
    chevron(s, (tip_x, MATH - 30), (end_x, MATH - 30 + h), (end_x, MATH - 30 - h), t,
            lerp(p.stem * 0.3, p.soft, p.w), p.bar_r)
    return w


@glyph("guilsinglleft", 0x2039, "OO", air=1.6)
def guilsinglleft(p):
    s = Shape()
    _guil(s, p, 0, True)
    return s


@glyph("guilsinglright", 0x203A, "OO", air=1.6)
def guilsinglright(p):
    s = Shape()
    _guil(s, p, 0, False)
    return s


@glyph("guillemotleft", 0xAB, "OO", air=1.6)
def guillemotleft(p):
    s = Shape()
    w = _guil(s, p, 0, True)
    _guil(s, p, w * 0.86 + p.stem * 0.4, True)
    return s


@glyph("guillemotright", 0xBB, "OO", air=1.6)
def guillemotright(p):
    s = Shape()
    w = _guil(s, p, 0, False)
    _guil(s, p, w * 0.86 + p.stem * 0.4, False)
    return s


@glyph("asciitilde", 0x7E, "OO", air=1.2)
def asciitilde(p):
    s = Shape()
    rx, ry = p.W(140, 170), p.W(88, 128)
    sw = p.stem * p.W(0.86, 0.66)  # a small sign: lighter at Black so it keeps a shape
    t = p.sh * p.W(1.0, 0.68)
    # two half ellipses, one over and one under, meeting at the centre
    arc(s, (rx, MATH, rx, ry), (rx, MATH, rx - sw, ry - t), 0, 180, (None, Tip(0, p.soft)))
    arc(s, (3 * rx - sw, MATH, rx, ry), (3 * rx - sw, MATH, rx - sw, ry - t), 176, 360, (None, Tip(0, p.soft)))
    return s


@glyph("asterisk", 0x2A, "OO", air=1.2)
def asterisk(p):
    s = Shape()
    R = p.W(150, 196)
    cy = CAP - R
    w = p.stem * p.W(0.84, 0.66)
    for k in range(6):
        a = math.radians(90 + 60 * k)
        end = (R + R * math.cos(a), cy + R * math.sin(a))
        start = (R - math.cos(a) * w * 0.2, cy - math.sin(a) * w * 0.2)
        pts = limb(s, start, end, w)
        Tip(p.w, p.soft, scale=SHORT_TIP).draw(s, pts[1], pts[2], (-math.cos(a), -math.sin(a)))
    return s


@glyph("numbersign", 0x23, "OO", air=1.0)
def numbersign(p):
    s = Shape()
    W = p.W(520, 600)
    lo, hi = 0, CAP - 40
    lean = 70
    w = p.stem * 0.84
    for x in (W * 0.34, W * 0.7):
        limb(s, (x - lean, lo), (x + lean, hi), w, ("h", "h"))
    for y in (hi * 0.33, hi * 0.67):
        _hbar(s, p, 0, W, y)
    return s


@glyph("percent", 0x25, "OO", air=1.0)
def percent(p):
    s = Shape()
    sw = p.rv * p.W(0.8, 0.7)
    rx, ry = sw + p.W(80, 84), p.W(140, 156)
    W = p.W(640, 760)
    ring(s, (rx, CAP - ry, rx, ry), (rx, CAP - ry, rx - sw, ry - p.sh * 0.8))
    ring(s, (W - rx, ry, rx, ry), (W - rx, ry, rx - sw, ry - p.sh * 0.8))
    limb(s, (W * 0.24, -OV), (W * 0.76, CAP + OV), p.dstem * 0.84, ("h", "h"))
    return s


@glyph("degree", 0xB0, "OO", air=1.2)
def degree(p):
    s = Shape()
    sw = p.stem * p.W(0.8, 0.64)
    r = sw + p.W(80, 62)
    ring(s, (r, CAP - r, r, r), (r, CAP - r, r - sw, r - sw * 0.92))
    return s


@glyph("at", 0x40, "RR", air=1.0)
def at(p):
    s = Shape()
    R = p.W(420, 520)
    cx, cy = R, CAP * 0.42
    sw = p.rv * 0.84
    ri = R * p.W(0.46, 0.43)
    # the inner a: a ring with a stem on its right
    xs = cx + ri - p.stem * 0.6
    ring(s, (cx, cy, ri, ri * 1.02), (cx + (sw - p.stem) * 0.25, cy, ri - (sw + p.join) / 2, ri * 1.02 - p.sh))
    outer = (cx, cy, R, R * 0.96)
    inner = (cx, cy, R - sw, R * 0.96 - p.sh)
    mid = (R - sw / 2, R * 0.96 - p.sh / 2)
    # the outer arc starts just left of the stem, so it swallows the stem's foot
    a0 = -math.degrees(math.acos((xs - 6 - cx) / (R - sw)))
    a_c = -math.degrees(math.acos((xs + p.stem / 2 - cx) / mid[0]))
    y_join = cy + mid[1] * math.sin(math.radians(a_c))
    s.rect(xs, y_join, xs + p.stem, cy + ri * 1.02)
    arc(s, outer, inner, a0, a0 + 326, (None, p.tip()))
    return s


@glyph("dollar", 0x24, "RR", air=1.0)
def dollar(p):
    from .upper import S
    s = S(p)
    x0, x1 = s.xbounds()
    cx = (x0 + x1) / 2
    w = p.stem * 0.7
    s.rect(cx - w / 2, -110, cx + w / 2, -OV + p.sh * 0.5, r=p.end_r * 0.6)
    s.rect(cx - w / 2, CAP + OV - p.sh * 0.5, cx + w / 2, CAP + 110, r=p.end_r * 0.6)
    return s


@glyph("ampersand", 0x26, "RD", air=1.0)
def ampersand(p):
    s = Shape()
    # a lower bowl open to the right, a small upper loop, and a leg that
    # falls from the loop to the baseline through the bowl's mouth
    W = p.W(600, 760)
    rx2, ry2 = p.W(250, 300), p.W(214, 236)
    cy2 = -OV + ry2
    sw = p.rv * 0.92
    arc(s, (rx2, cy2, rx2, ry2), (rx2, cy2, rx2 - sw, ry2 - p.sh), 40, 300, (p.tip(), None))
    rx1, ry1 = p.W(150, 190), p.W(150, 160)
    cx1, cy1 = rx2 * 0.86, CAP + OV - ry1
    ring(s, (cx1, cy1, rx1, ry1), (cx1, cy1, rx1 - sw * 0.92, ry1 - p.sh))
    # leg from the loop's lower left to the baseline at the right
    a = math.radians(214)
    start = (cx1 + (rx1 - sw / 2) * math.cos(a), cy1 + (ry1 - p.sh / 2) * math.sin(a))
    foot = (W - p.dstem * 0.7, 0)
    pts = limb(s, start, foot, p.dstem, ("perp", "h"))
    tw = abs(pts[2][0] - pts[1][0])
    wedge(s, foot[0], 0, tw / 2, p.fl, p.soft, up=True, slope=(start[0] - foot[0]) / start[1])
    return s
