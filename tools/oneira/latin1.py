"""The Latin-1 letters that are not accent composites: Æ Ø Ð Þ ß æ ø ð þ."""

import math

from .geom import Shape, arc, hwidth, lerp, limb, wedge
from .lower import _bowl_right, a as a_lower, e as e_lower, o as o_lower
from .params import ASC, CAP, DESC, OV, XH, glyph
from .parts import bowl, ell_at, ring_mid, ring_thickness, round_o, stem, tangent_from
from .upper import BAR, D, _O_r, _half_bowl

YC = CAP / 2


def _merge(*shapes):
    out = Shape()
    for s in shapes:
        out.contours += s.contours
    return out


def _slash(s, p, x0, x1, y0, y1):
    """The stroke through Ø and ø."""
    limb(s, (x0, y0), (x1, y1), p.dstem * 0.78, ("h", "h"))


@glyph("Oslash", 0xD8, "RR")
def Oslash(p):
    s = Shape()
    rx = _O_r(p)
    round_o(s, p, rx, rx, YC, YC + OV)
    _slash(s, p, rx * 0.16, rx * 1.84, -46, CAP + 46)
    return s


@glyph("oslash", 0xF8, "RR")
def oslash(p):
    s = o_lower(p)
    x0, x1 = s.xbounds()
    _slash(s, p, x0 + (x1 - x0) * 0.1, x1 - (x1 - x0) * 0.1, -40, XH + 40)
    return s


@glyph("Eth", 0xD0, "SR")
def Eth(p):
    s = D(p)
    # the bar crosses the stem: it starts in the left sidebearing
    s.rect(-p.W(84, 70), YC - p.sh / 2, p.stem + p.W(150, 160), YC + p.sh / 2, r=p.bar_r)
    return s


@glyph("Thorn", 0xDE, "SR")
def Thorn(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    _half_bowl(s, p, 0, CAP * 0.19, CAP * 0.81, p.W(480, 610))
    return s


@glyph("thorn", 0xFE, "SR")
def thorn(p):
    s = Shape()
    rx = p.W(268, 326)
    stem(s, p, 0, DESC, ASC)
    bowl(s, p, rx, rx, "left")
    return s


@glyph("eth", 0xF0, "RR")
def eth(p):
    s = Shape()
    rx = p.W(276, 330)
    ry = XH / 2 + OV
    cy = XH / 2
    outer = (rx, cy, rx, ry)
    round_o(s, p, rx, rx, cy, ry)
    # the ascender leaves the bowl on its tangent and rises to the left
    top = (rx * 0.62, ASC)
    mid = ring_mid(outer, p.rv, p.sh)
    th = tangent_from(mid, top, 1, 89)
    m = ell_at(mid, th)
    w = ring_thickness(p, th, p.rv)
    d = (top[0] - m[0], top[1] - m[1])
    ln = math.hypot(*d)
    pts = limb(s, (m[0] - d[0] / ln * 2, m[1] - d[1] / ln * 2), top, w, ("perp", "h"))
    tw = abs(pts[2][0] - pts[1][0])
    wedge(s, top[0], ASC, tw / 2, p.fl, p.soft, up=False, slope=(m[0] - top[0]) / (ASC - m[1]))
    # the crossing stroke
    yc = XH + (ASC - XH) * 0.42
    xc = m[0] + (yc - m[1]) * d[0] / d[1]
    half = p.W(118, 136)
    ang = math.radians(16)
    limb(s, (xc - half * math.cos(ang), yc - half * math.sin(ang)),
         (xc + half * math.cos(ang), yc + half * math.sin(ang)), p.sh * 1.05)
    return s


@glyph("germandbls", 0xDF, "SR")
def germandbls(p):
    s = Shape()
    top = ASC + OV
    rx1, ry1 = p.W(176, 214), p.W(162, 176)
    cy1 = top - ry1
    left, right = p.stem, 2 * rx1 - p.rv
    inner1 = ((left + right) / 2, cy1, (right - left) / 2, ry1 - p.sh)
    arc(s, (rx1, cy1, rx1, ry1), inner1, -90, 180, (p.tip(), None))
    stem(s, p, 0, 0, cy1 + 4, head=False)
    # the lower bowl is larger and sits further right; it starts inside the
    # upper bowl's bottom stroke and ends in a tip near the stem
    ry2 = (cy1 - ry1 + p.sh + OV) / 2
    cy2 = -OV + ry2
    rx2 = p.W(206, 252)
    cx2 = p.stem + rx2 * 0.66
    mid_rx = rx2 - p.rv / 2
    a_s = math.degrees(math.acos(max(-1, min(1, (rx1 - cx2) / mid_rx))))
    arc(s, (cx2, cy2, rx2, ry2), (cx2, cy2, rx2 - p.rv, ry2 - p.sh), -118, a_s, (p.tip(), None))
    return s


@glyph("AE", 0xC6, "DO")
def AE(p):
    s = Shape()
    W = p.W(860, 1060)
    xs = W * 0.4
    tx = xs + p.stem / 2
    tw = p.dstem * 1.3
    for _ in range(6):
        tw = hwidth(tw / 2, 0, tx, CAP, p.dstem)
    fx = tw / 2
    limb(s, (fx, 0), (tx, CAP), p.dstem, ("h", "h"))
    wedge(s, fx, 0, tw / 2, p.fl, p.soft, up=True, slope=(tx - fx) / CAP)
    stem(s, p, xs, 0, CAP, head=False)
    r = p.bar_r
    x_tl = tx - tw / 2  # the diagonal's outer edge runs into the top arm's corner
    s.poly([(x_tl, CAP - p.sh), (W, CAP - p.sh), (W, CAP), (x_tl, CAP)], [0, r, r, 0])
    s.poly([(tx, CAP * BAR - p.sh / 2), (W * 0.93, CAP * BAR - p.sh / 2),
            (W * 0.93, CAP * BAR + p.sh / 2), (tx, CAP * BAR + p.sh / 2)], [0, r, r, 0])
    s.poly([(tx, 0), (W * 1.02, 0), (W * 1.02, p.sh), (tx, p.sh)], [0, r, r, 0])
    yb = CAP * lerp(0.3, 0.27, p.t)
    xb = fx + (tx - fx) * (yb / CAP)
    s.rect(xb, yb - p.sh / 2, tx, yb + p.sh / 2)
    return s


@glyph("ae", 0xE6, "RO")
def ae(p):
    a_s = a_lower(p)
    rx, cx = _bowl_right(p)
    stem_c = cx + rx - p.stem / 2
    # the e's left side sits on the a's stem
    return _merge(a_s, e_lower(p).moved(stem_c - p.rv / 2))
