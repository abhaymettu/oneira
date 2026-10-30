"""The Latin-1 letters that are not accent composites: Æ Ø Ð Þ ß æ ø ð þ."""

import math

from .geom import SQRT3, Shape, Tip, arc, hwidth, lerp, limb, wedge
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
    # the ascender leaves the bowl on its tangent and rises to the left, a
    # curved stroke's tail, so it ends in a tip rather than a wedge
    top = (rx * 0.58, ASC)
    mid = ring_mid(outer, p.rv, p.sh)
    th = tangent_from(mid, top, 1, 89)
    m = ell_at(mid, th)
    w = ring_thickness(p, th, p.rv) * lerp(1.0, 0.8, p.t)  # lighter tail, room for the bar
    d = (top[0] - m[0], top[1] - m[1])
    ln = math.hypot(*d)
    u = (d[0] / ln, d[1] / ln)
    scale = lerp(0.9, 0.75, p.t)
    reach = w / 2 * SQRT3 * scale * p.w + w / 2 * (1 - p.w)  # tip or round cap beyond the cut
    end = (top[0] - u[0] * reach, top[1] - u[1] * reach)
    pts = limb(s, (m[0] - u[0] * 2, m[1] - u[1] * 2), end, w)
    Tip(p.w, p.soft, scale).draw(s, pts[1], pts[2], (-u[0], -u[1]))
    # the crossing stroke: a short soft bar tilted up
    yc = lerp(XH + OV, end[1], 0.52)  # centred on the tail where it clears the bowl
    xc = m[0] + (yc - m[1]) * u[0] / u[1]
    half = p.W(118, 140)
    ang = math.radians(18)
    bar = Shape()
    limb(bar, (xc - half * math.cos(ang), yc - half * math.sin(ang)),
         (xc + half * math.cos(ang), yc + half * math.sin(ang)), p.sh * lerp(0.98, 0.68, p.t))
    c = bar.contours[0]
    s.poly([pt[1][0] for pt in c], [p.bar_r] * 4)
    return s


@glyph("germandbls", 0xDF, "SR")
def germandbls(p):
    """The stem rounds over into a small upper bowl that closes onto the stem
    at the waist; a larger lower bowl leaves the waist and ends in a tip that
    stays clear of the foot wedge."""
    s = Shape()
    top = ASC + OV
    waist = XH - p.sh  # the lower bowl's top stroke sits on the x-height
    ry1 = (top - waist) / 2
    cy1 = waist + ry1
    rx1 = p.W(168, 246)  # wide enough at Black that the upper counter stays open
    left, right = p.stem, 2 * rx1 - p.rv
    inner1 = ((left + right) / 2, cy1, (right - left) / 2, ry1 - p.sh)
    arc(s, (rx1, cy1, rx1, ry1), inner1, -90, 180)
    stem(s, p, 0, 0, cy1 + 4, head=False)
    ry2 = (XH + OV) / 2
    cy2 = -OV + ry2
    rx2 = p.W(206, 296)
    # the bottom stroke ends just past the bottom, its tip clear of the foot
    # wedge (sized for the lucid wedge, so the shape holds across Lucidity)
    a0 = -96
    clear = p.stem + lerp(48, 64, p.t) + p.sh * 0.87 + p.W(34, 20)
    cut = math.cos(math.radians(a0))
    cx2 = max(2 * rx1 + p.W(38, 44) - rx2, clear - rx2 * cut)
    # the waist bar closes the upper counter and carries the lower bowl's start
    s.rect(p.stem / 2, waist, max(rx1, cx2) + 2, waist + p.sh)
    arc(s, (cx2, cy2, rx2, ry2), (cx2, cy2, rx2 - p.rv, ry2 - p.sh), a0, 90, (p.tip(), None))
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
    """The a's bowl, then an e whose round left side sits on the a's stem. The
    stem is a spine between two rounds, so it carries no foot wedge."""
    s = Shape()
    rx, cx = _bowl_right(p)
    bowl(s, p, cx, rx, "right")
    xs = cx + rx - p.stem
    stem(s, p, xs, 0, XH, foot=False, head=False)
    return _merge(s, e_lower(p).moved(xs + p.stem / 2 - p.rv / 2))
