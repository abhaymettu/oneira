"""Figures: lining, proportional, cap height."""

import math

from .geom import Shape, arc, lerp, limb, ring, wedge
from .params import CAP, OV, glyph
from .parts import ell_at, ring_mid, ring_thickness, round_o, stem, tangent_from

FH = CAP
YF = FH / 2
AIR = 1.15


def _fig(name, uni, sides):
    return glyph(name, uni, sides, air=AIR)


@_fig("zero", 0x30, "RR")
def zero(p):
    s = Shape()
    rx = p.W(250, 314)
    round_o(s, p, rx, rx, YF, YF + OV)
    return s


@_fig("one", 0x31, "OS")
def one(p):
    s = Shape()
    ln = p.W(170, 230)
    ang = math.radians(212)  # the flag falls to the left
    xs = ln * -math.cos(ang) - p.stem * 0.5 + 6
    stem(s, p, xs, 0, FH, head=False)
    w = p.sh * 1.05
    a = (xs + p.stem * 0.5, FH - w * 0.62)
    b = (a[0] + ln * math.cos(ang), a[1] + ln * math.sin(ang))
    pts = limb(s, a, b, w)
    p.tip().draw(s, pts[1], pts[2], (-math.cos(ang), -math.sin(ang)))
    return s


@_fig("two", 0x32, "OO")
def two(p):
    s = Shape()
    W = p.W(440, 580)
    rx = W / 2
    ry = rx * 0.9
    cy = FH + OV - ry
    outer = (rx, cy, rx, ry)
    mid = ring_mid(outer, p.rv, p.sh)
    w = p.stem * 0.92
    # the diagonal leaves the bowl on its tangent and lands on the bar's corner
    tw = w * 1.4
    for _ in range(6):
        bot = (tw / 2, p.sh)
        th = tangent_from(mid, bot, -89, 10)
        m = ell_at(mid, th)
        k = (m[0] - bot[0]) / (m[1] - bot[1])
        tw = w * math.hypot(1, k)
    xl = lambda y: (y - p.sh) * k
    y0, e = p.sh * 0.5, 0.5
    # square cut at the top, a hair past the tangent point, so it hides in the bowl
    ln = math.hypot(m[0] - bot[0], m[1] - bot[1])
    d = ((m[0] - bot[0]) / ln, (m[1] - bot[1]) / ln)
    c = (m[0] + d[0] * 2, m[1] + d[1] * 2)
    n = (d[1] * w / 2, -d[0] * w / 2)  # toward the right-hand edge
    s.poly([(e, p.sh), (e, y0), (xl(y0) + tw, y0), (c[0] + n[0], c[1] + n[1]), (c[0] - n[0], c[1] - n[1])])
    arc(s, outer, (rx, cy, rx - p.rv, ry - p.sh), th - 6, 158, (None, p.tip()))
    r = p.bar_r
    s.poly([(0, 0), (W, 0), (W, p.sh), (0, p.sh)], [r, r, r, 0])
    return s


def _stack(p, rx2, k1, sw):
    """Two stacked ellipses sharing one horizontal stroke at the waist (3, 8)."""
    top, bot = FH + OV, -OV
    total = top - bot + p.sh
    ry1 = total * 0.236
    ry2 = total / 2 - ry1
    rx1 = rx2 * k1
    return (rx2, top - ry1, rx1, ry1), (rx2, bot + ry2, rx2, ry2)


@_fig("three", 0x33, "OR")
def three(p):
    s = Shape()
    rx2 = p.W(226, 300)
    sw = p.rv * 0.9
    e1, e2 = _stack(p, rx2, 0.88, sw)
    inner = lambda e: (e[0], e[1], e[2] - sw, e[3] - p.sh)
    # the bowls share a centre, so their middle ends coincide; the middle is a
    # stroke end like any other and carries the tip
    arc(s, e1, inner(e1), -90, 150, (p.tip(), p.tip()))
    arc(s, e2, inner(e2), -150, 90, (p.tip(), None))
    return s


@_fig("four", 0x34, "OO")
def four(p):
    s = Shape()
    W = p.W(480, 620)
    xs = W - p.W(96, 120) - p.stem
    yb = FH * 0.22
    stem(s, p, xs, 0, FH, head=False)
    top_r = xs + p.stem
    lo = yb + p.sh
    w = p.dstem * 0.92
    tw = w * 1.3
    for _ in range(6):
        k = (top_r - tw) / (FH - lo)
        tw = w * math.hypot(1, k)
    xl = lambda y: (y - lo) * k
    y0, e = yb + p.sh * 0.5, 0.5
    rt = lerp(p.stem * 0.3, p.soft, p.w)
    s.poly([(e, lo), (e, y0), (xl(y0) + tw, y0), (top_r, FH), (xl(FH), FH)], [0, 0, 0, 0, rt])
    r = p.bar_r
    s.poly([(0, yb), (W, yb), (W, yb + p.sh), (0, yb + p.sh)], [r, r, r, 0])
    return s


@_fig("five", 0x35, "OR")
def five(p):
    s = Shape()
    rx = p.W(232, 300)
    ry = FH * 0.33 + OV / 2
    cy = ry - OV
    outer = (rx, cy, rx, ry)
    inner = (rx, cy, rx - p.rv, ry - p.sh)
    a1 = 146
    arc(s, outer, inner, -148, a1, (p.tip(), None))
    # the stem's foot swallows the arc's cut
    xo, _ = ell_at(outer, a1)
    _, yi = ell_at(inner, a1)
    xv = xo - 2
    w = p.stem * 0.96
    s.rect(xv, yi - 2, xv + w, FH - p.sh / 2)
    r = p.bar_r
    s.poly([(xv, FH - p.sh), (rx + rx * 0.86, FH - p.sh), (rx + rx * 0.86, FH), (xv, FH)], [0, r, r, 0])
    return s


@_fig("six", 0x36, "RR")
def six(p):
    s = Shape()
    rx = p.W(236, 300)
    ry = FH * 0.34
    cy = ry - OV
    outer = (rx, cy, rx, ry)
    round_o(s, p, rx, rx, cy, ry)
    mid = ring_mid(outer, p.rv, p.sh)
    top = (rx + rx * p.W(0.52, 0.46), FH)
    th = tangent_from(mid, top, 95, 179)
    m = ell_at(mid, th)
    w = ring_thickness(p, th, p.rv)
    d = ((top[0] - m[0]), (top[1] - m[1]))
    ln = math.hypot(*d)
    a = (m[0] - d[0] / ln * 2, m[1] - d[1] / ln * 2)  # start a hair inside the ring: overlap, no seam
    pts = limb(s, a, top, w, ("perp", "h"))
    tw = abs(pts[2][0] - pts[1][0])
    wedge(s, top[0], FH, tw / 2, p.fl, p.soft, up=False, slope=(m[0] - top[0]) / (FH - m[1]))
    return s


@_fig("seven", 0x37, "OO")
def seven(p):
    s = Shape()
    W = p.W(450, 570)
    foot = W * 0.3
    hi = FH - p.sh
    w = p.dstem
    tw = w * 1.3
    for _ in range(6):
        k = (W - tw / 2 - foot) / hi  # centre dx per dy
        tw = w * math.hypot(1, k)
    xr = lambda y: W + (y - hi) * k  # right edge, through the bar's lower corner
    y1, e = FH - p.sh * 0.5, 0.5
    s.poly([(xr(0) - tw, 0), (xr(0), 0), (W - e, hi), (W - e, y1), (xr(y1) - tw, y1)])
    wedge(s, xr(0) - tw / 2, 0, tw / 2, p.fl, p.soft, up=True, slope=k)
    r = p.bar_r
    s.poly([(0, FH - p.sh), (W, FH - p.sh), (W, FH), (0, FH)], [r, 0, r, r])
    return s


@_fig("eight", 0x38, "RR")
def eight(p):
    s = Shape()
    rx2 = p.W(232, 304)
    sw = p.rv * 0.88
    e1, e2 = _stack(p, rx2, 0.9, sw)
    for e in (e1, e2):
        ring(s, e, (e[0], e[1], e[2] - sw, e[3] - p.sh))
    return s


@_fig("nine", 0x39, "RR")
def nine(p):
    six_shape = six(p)
    x0, x1 = six_shape.xbounds()
    return six_shape.rotated((x0 + x1) / 2, FH / 2)
