"""Metrics, the stroke model, and the glyph registry."""

from .geom import Shape, Tip, lerp

UPM = 1000
CAP = 700
XH = 520
ASC = 750
DESC = -220
OV = 12


class P:
    """Everything a drawing needs for one master. t = weight 0..1 (Thin..Black),
    w = Lucidity 0..1 (dream..lucid)."""

    def __init__(self, t, w, sharp=False):
        self.t, self.w = t, w
        self.stem = lerp(30, 176, t)
        self.rv = self.stem * 1.06  # round verticals read lighter, so draw them heavier
        self.sh = self.stem * lerp(0.86, 0.74, t)  # horizontals
        self.dstem = self.stem * 0.94  # diagonals
        self.join = self.stem * lerp(0.86, 0.6, t)  # curve meeting a stem
        self.fl = w * lerp(48, 64, t)  # wedge flare
        self.soft = lerp(5, 16, t)  # corner radius of every triangle
        # stroke-end rounding in the dream state; sharp leaves it out, for
        # measuring spacing, so rounding an end never moves a glyph's advance
        self.end_r = 0.0 if sharp else lerp(self.stem * 0.3, 0, w)
        self.bar_r = lerp(self.sh * 0.3, self.soft * 0.4, w)
        # in the dream state a wedge hides inside its stroke end; its base
        # corners round with the end so they never poke out of it
        self.wedge_r = (self.soft + self.end_r, self.soft)

    def tip(self):
        return Tip(self.w, self.soft)

    def W(self, thin, black):
        """A width that grows with weight."""
        return lerp(thin, black, self.t)


GLYPHS = {}


def glyph(name, uni, sides=None, air=None):
    """Register a drawing. sides: two of S (straight), R (round), D (diagonal),
    O (open: bars, arms, terminals), or None for a fixed advance."""
    if air is None:  # capitals want more room than lowercase
        air = 1.28 if name[:1].isupper() else 1.0

    def deco(fn):
        GLYPHS[name] = (uni, fn, sides, air)
        return fn
    return deco


COMPOSITES = {}


def composite(name, uni, base, marks):
    """An accented glyph built from components. base is a glyph name, or None
    for a spacing mark; marks are (mark glyph, anchor) where anchor is "lc",
    "cap" or "cedilla"."""
    COMPOSITES[name] = (uni, base, marks)


def mark_offset(anchor, p):
    """Height a mark sits at. Marks rest on y = 0 (the cedilla hangs from it)."""
    return {"lc": XH + p.W(80, 68), "cap": CAP + p.W(58, 48), "cedilla": p.sh * 0.4}[anchor]


def sidebearing(kind, p):
    base = lerp(58, 42, p.t)
    allowance = 0.62 * p.fl
    return {"S": base + allowance, "R": base * 0.74, "D": base * 0.16 + allowance,
            "O": base * 0.34, "W": base * 0.5 + allowance}[kind]


TIP_ROOM = 0.6  # share of a tip's growth past the dream outline that spacing gives back


def build(name, t, w):
    """Shape and advance for one master. Spaced glyphs return a Shape and are
    measured on the dream state (w=0), so wedges hang into the gap like serifs.
    Ink that grows past the dream outline on a side without wedges (the tips
    of c, e, r, braces, quotes) gets part of its growth back as room, or it
    runs into the next letter at lucid. Unspaced glyphs return (Shape, advance)."""
    uni, fn, sides, air = GLYPHS[name]
    p = P(t, w)
    if sides is None:
        return fn(p)
    shape = fn(p)
    x0, x1 = fn(P(t, 0, sharp=True)).xbounds()
    l0, l1 = shape.xbounds()
    room = [0.0 if k in "SDW" else TIP_ROOM * max(0.0, grow) for k, grow in zip(sides, (x0 - l0, l1 - x1))]
    lsb = sidebearing(sides[0], p) * air + room[0]
    rsb = sidebearing(sides[1], p) * air + room[1]
    return shape.moved(lsb - x0), x1 - x0 + lsb + rsb
