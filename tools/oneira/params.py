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

    def __init__(self, t, w):
        self.t, self.w = t, w
        self.stem = lerp(30, 176, t)
        self.rv = self.stem * 1.06  # round verticals read lighter, so draw them heavier
        self.sh = self.stem * lerp(0.86, 0.74, t)  # horizontals
        self.dstem = self.stem * 0.94  # diagonals
        self.join = self.stem * lerp(0.86, 0.6, t)  # curve meeting a stem
        self.fl = w * lerp(48, 64, t)  # wedge flare
        self.soft = lerp(5, 16, t)  # corner radius of every triangle
        self.end_r = lerp(self.stem * 0.3, 0, w)  # stroke-end rounding in the dream state
        self.bar_r = lerp(self.sh * 0.3, self.soft * 0.4, w)

    def tip(self):
        return Tip(self.w, self.soft)

    def W(self, thin, black):
        """A width that grows with weight."""
        return lerp(thin, black, self.t)


GLYPHS = {}


def glyph(name, uni, sides=None):
    """Register a drawing. sides: two of S (straight), R (round), D (diagonal),
    O (open: bars, arms, terminals), or None for a fixed advance."""
    def deco(fn):
        GLYPHS[name] = (uni, fn, sides)
        return fn
    return deco


def sidebearing(kind, p):
    base = lerp(58, 42, p.t)
    allowance = 0.62 * p.fl
    return {"S": base + allowance, "R": base * 0.74, "D": base * 0.16 + allowance,
            "O": base * 0.34, "W": base * 0.5 + allowance}[kind]


def build(name, t, w):
    """Shape and advance for one master. Spaced glyphs return a Shape and are
    measured on the dream state (w=0), so wedges hang into the gap like serifs.
    Unspaced glyphs return (Shape, advance)."""
    uni, fn, sides = GLYPHS[name]
    p = P(t, w)
    if sides is None:
        return fn(p)
    x0, x1 = fn(P(t, 0)).xbounds()
    lsb, rsb = sidebearing(sides[0], p), sidebearing(sides[1], p)
    return fn(p).moved(lsb - x0), x1 - x0 + lsb + rsb
