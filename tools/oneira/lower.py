"""Lowercase."""

import math

from .geom import Shape, arc, clipped, diag, ept, hwidth, lerp, wedge
from .params import ASC, DESC, OV, XH, P, glyph, sidebearing
from .parts import arch, bowl, cup, dot, hook, round_o, stem, zee

YM = XH / 2


# ---------- round ----------

@glyph("o", 0x6F, "RR")
def o(p):
    s = Shape()
    rx = p.W(284, 338)
    round_o(s, p, rx, rx, YM, YM + OV)
    return s


@glyph("c", 0x63, "RO")
def c(p):
    s = Shape()
    rx, ry = p.W(270, 318), YM + OV
    outer = (rx, YM, rx, ry)
    inner = (rx, YM, rx - p.rv, ry - p.sh)
    arc(s, outer, inner, 46, 314, (p.tip(), p.tip()))
    return s


@glyph("e", 0x65, "RO")
def e(p):
    s = Shape()
    rx, ry = p.W(278, 330), YM + OV
    cx = rx
    outer = (cx, YM, rx, ry)
    inner = (cx, YM, rx - p.rv, ry - p.sh)
    bar = p.sh * lerp(0.96, 0.76, p.t)
    yb = YM - lerp(0.1, 0.72, p.t) * bar  # bar drops as weight rises to keep the eye open
    a0 = math.degrees(math.asin((yb - YM) / ry))
    arc(s, outer, inner, a0, lerp(324, 302, p.t), (None, p.tip()))  # aperture opens with weight
    xo, _ = ept(outer, a0)
    # the bar runs out to the outer edge: it squares off the slanted cut and
    # leaves no sliver of counter between bar and bowl
    s.rect(cx - rx + p.rv * 0.5, yb, xo - 1, yb + bar)
    return s


@glyph("s", 0x73, "RR")
def s_(p):
    s = Shape()
    top, bot = XH + OV, -OV
    # two stacked ellipses; the spine is where they overlap by one stroke
    total = top - bot + p.sh
    ry1 = total * 0.236
    ry2 = total / 2 - ry1
    rx2 = p.W(226, 292)
    rx1 = rx2 * 0.9
    cx = rx2
    cy1, cy2 = top - ry1, bot + ry2
    sv = p.rv * 0.92  # s strokes run thinner: it is the darkest letter otherwise
    arc(s, (cx, cy1, rx1, ry1), (cx, cy1, rx1 - sv, ry1 - p.sh), 30, 277, (p.tip(), None))
    arc(s, (cx, cy2, rx2, ry2), (cx, cy2, rx2 - sv, ry2 - p.sh), 210, 457, (p.tip(), None))
    return s


# ---------- bowl + stem ----------

def _bowl_right(p):
    rx = p.W(268, 326)
    return rx, rx  # rx, cx


@glyph("a", 0x61, "RS")
def a(p):
    s = Shape()
    rx, cx = _bowl_right(p)
    bowl(s, p, cx, rx, "right")
    stem(s, p, cx + rx - p.stem, 0, XH, head=False)  # the top is a join, not a free end
    return s


@glyph("d", 0x64, "RS")
def d(p):
    s = Shape()
    rx, cx = _bowl_right(p)
    bowl(s, p, cx, rx, "right")
    stem(s, p, cx + rx - p.stem, 0, ASC)
    return s


@glyph("q", 0x71, "RS")
def q(p):
    s = Shape()
    rx, cx = _bowl_right(p)
    bowl(s, p, cx, rx, "right")
    stem(s, p, cx + rx - p.stem, DESC, XH, head=False)
    return s


@glyph("b", 0x62, "SR")
def b(p):
    s = Shape()
    rx = p.W(268, 326)
    stem(s, p, 0, 0, ASC)
    bowl(s, p, rx, rx, "left")
    return s


@glyph("p", 0x70, "SR")
def p_(p):
    s = Shape()
    rx = p.W(268, 326)
    stem(s, p, 0, DESC, XH)
    bowl(s, p, rx, rx, "left")
    return s


@glyph("g", 0x67, "RS")
def g(p):
    s = Shape()
    rx, cx = _bowl_right(p)
    bowl(s, p, cx, rx, "right")
    x_right = cx + rx
    cyh = hook(s, p, x_right, DESC - OV, rx * 0.94, p.W(150, 168), a0=208)
    stem(s, p, x_right - p.stem, cyh - 4, XH, foot=False, head=False)
    return s


# ---------- arches ----------

def _n_width(p):
    return p.W(466, 610)


@glyph("n", 0x6E, "SS")
def n(p):
    s = Shape()
    W = _n_width(p)
    stem(s, p, 0, 0, XH)
    cy = arch(s, p, 0, W)
    stem(s, p, W - p.stem, 0, cy + 4, head=False)
    return s


@glyph("h", 0x68, "SS")
def h(p):
    s = Shape()
    W = _n_width(p)
    stem(s, p, 0, 0, ASC)
    cy = arch(s, p, 0, W)
    stem(s, p, W - p.stem, 0, cy + 4, head=False)
    return s


@glyph("m", 0x6D, "SS")
def m(p):
    s = Shape()
    a_w = p.W(404, 520)  # each arch, outer width
    stem(s, p, 0, 0, XH)
    cy = arch(s, p, 0, a_w)
    x2 = a_w - p.stem
    stem(s, p, x2, 0, cy + 4, head=False)
    arch(s, p, x2, x2 + a_w)
    stem(s, p, x2 + a_w - p.stem, 0, cy + 4, head=False)
    return s


@glyph("u", 0x75, "SS")
def u(p):
    s = Shape()
    W = _n_width(p)
    cy = cup(s, p, 0, W)
    stem(s, p, 0, cy - 4, XH, foot=False)
    stem(s, p, W - p.stem, 0, XH)
    return s


@glyph("r", 0x72, "SO")
def r(p):
    s = Shape()
    W = p.W(420, 540)
    stem(s, p, 0, 0, XH)
    arch(s, p, 0, W, a0=56, tip=True, right_rv=True)
    return s


# ---------- straight ----------

@glyph("i", 0x69, "SS")
def i(p):
    s = Shape()
    stem(s, p, 0, 0, XH)
    dot(s, p, p.stem / 2, p.W(118, 84))
    return s


@glyph("dotlessi", 0x131, "SS")
def dotlessi(p):
    s = Shape()
    stem(s, p, 0, 0, XH)
    return s


@glyph("l", 0x6C, "SS")
def l(p):
    s = Shape()
    stem(s, p, 0, 0, ASC)
    return s


def _j(p):
    s = Shape()
    rxh = p.W(118, 100) + p.stem * 1.03  # the counter stays open at Black
    x = 2 * rxh - p.stem  # stem left edge; the hook hangs to the left of it
    cyh = hook(s, p, x + p.stem, DESC - OV, rxh, p.W(132, 156), a0=208)
    stem(s, p, x, cyh - 4, XH, foot=False)
    dot(s, p, x + p.stem / 2, p.W(118, 84))
    return s, x


@glyph("j", 0x6A)
def j(p):
    """Spaced from its stem like i, with most of the hook hanging under the
    letter before it: it lives in the descender, where little else does.
    Measured on the dream state, like every spaced glyph."""
    s, x = _j(p)
    x0, x1 = _j(P(p.t, 0))[0].xbounds()
    sb = sidebearing("S", p)
    dx = sb - x + (x - x0) * lerp(0.25, 0.5, p.t)  # less hang at Black, where the hook is wide
    return s.moved(dx), x1 + dx + sb


@glyph("t", 0x74, "OO")
def t(p):
    s = Shape()
    left, right = p.W(118, 140), p.W(150, 176)
    x = left
    stem(s, p, x, 0, XH + p.W(160, 132), head=False, top_tip=True)
    s.rect(0, XH - p.sh, x + p.stem + right, XH, r=p.bar_r)
    return s


@glyph("f", 0x66, "OO")
def f(p):
    s = Shape()
    left = p.W(110, 132)
    x = left
    rxh, ryh = p.W(156, 214), p.W(150, 170)
    top = ASC + OV
    cyh = top - ryh
    outer = (x + rxh, cyh, rxh, ryh)
    li, ri = x + p.stem, x + 2 * rxh - p.rv
    inner = ((li + ri) / 2, cyh, (ri - li) / 2, ryh - p.sh)
    arc(s, outer, inner, 42, 186, (p.tip(), None))
    stem(s, p, x, 0, cyh + 4, head=False)
    s.rect(0, XH - p.sh, x + p.stem + p.W(150, 170), XH, r=p.bar_r)
    return s


# ---------- diagonals ----------

def _vee(s, p, xl, xr, top, bot):
    """Two diagonals meeting at a point centred between xl and xr. Wedges at
    the open ends. Returns horizontal stroke width."""
    cx = (xl + xr) / 2
    tw = p.dstem * 1.3
    for _ in range(4):
        tw = hwidth(xl + tw / 2, top, cx, bot, p.dstem)
    diag(s, xl + tw / 2, top, cx, bot, p.dstem, ends=(p.end_r, 0))
    diag(s, xr - tw / 2, top, cx, bot, p.dstem, ends=(p.end_r, 0))
    run = (cx - (xl + tw / 2)) / abs(top - bot)
    up = top < bot
    wedge(s, xl + tw / 2, top, tw / 2, p.fl, p.wedge_r, up=up, slope=run)
    wedge(s, xr - tw / 2, top, tw / 2, p.fl, p.wedge_r, up=up, slope=-run)
    return tw


@glyph("v", 0x76, "DD")
def v(p):
    s = Shape()
    _vee(s, p, 0, p.W(504, 650), XH, 0)
    return s


@glyph("w", 0x77, "DD")
def w(p):
    s = Shape()
    W = p.W(770, 990)
    half = W / 2
    over = p.dstem * 0.55
    _vee(s, p, 0, half + over, XH, 0)
    _vee(s, p, half - over, W, XH, 0)
    return s


@glyph("x", 0x78, "DD")
def x(p):
    s = Shape()
    W = p.W(486, 630)
    tw = p.dstem * 1.3
    for _ in range(4):
        tw = hwidth(tw / 2, 0, W - tw / 2, XH, p.dstem)
    diag(s, tw / 2, 0, W - tw / 2, XH, p.dstem, r=p.end_r)
    diag(s, W - tw / 2, 0, tw / 2, XH, p.dstem, r=p.end_r)
    run = (W - tw) / XH
    wedge(s, tw / 2, 0, tw / 2, p.fl, p.wedge_r, up=True, slope=run)
    wedge(s, W - tw / 2, 0, tw / 2, p.fl, p.wedge_r, up=True, slope=-run)
    wedge(s, tw / 2, XH, tw / 2, p.fl, p.wedge_r, up=False, slope=run)
    wedge(s, W - tw / 2, XH, tw / 2, p.fl, p.wedge_r, up=False, slope=-run)
    return s


@glyph("y", 0x79, "DD")
def y(p):
    s = Shape()
    W = p.W(504, 650)
    cx = W / 2
    tw = p.dstem * 1.3
    for _ in range(4):
        tw = hwidth(W - tw / 2, XH, cx, 0, p.dstem)
    # the right stroke runs on past the baseline into the descender
    xr_top = W - tw / 2
    run = (xr_top - cx) / XH
    tail = (cx - run * (0 - DESC), DESC)
    diag(s, xr_top, XH, tail[0], DESC, p.dstem, r=p.end_r)
    wedge(s, xr_top, XH, tw / 2, p.fl, p.wedge_r, up=False, slope=-run)
    wedge(s, tail[0], DESC, tw / 2, p.fl, p.wedge_r, up=True, slope=run)
    # the left stroke stops on the right stroke's centre line
    clipped(s, (tw / 2, XH), (cx, 0), p.dstem, (cx, 0), (tail[0] - xr_top, DESC - XH), p.end_r)
    wedge(s, tw / 2, XH, tw / 2, p.fl, p.wedge_r, up=False, slope=(cx - tw / 2) / XH)
    return s


@glyph("z", 0x7A, "OO")
def z(p):
    s = Shape()
    W = p.W(430, 560)
    zee(s, p, W, XH)
    return s


@glyph("k", 0x6B, "SD")
def k(p):
    s = Shape()
    Wk = p.W(426, 600)
    stem(s, p, 0, 0, ASC)
    xs = p.stem / 2
    j_ = (xs, XH * lerp(0.26, 0.32, p.t))
    tw = hwidth(j_[0], j_[1], Wk, XH, p.dstem)
    top = (Wk - tw / 2, XH)
    clipped(s, top, j_, p.dstem, (xs, 0), (0, 1), p.end_r)
    wedge(s, top[0], XH, tw / 2, p.fl, p.wedge_r, up=False, slope=(j_[0] - top[0]) / (XH - j_[1]))
    lj = (lerp(j_[0], top[0], 0.42), lerp(j_[1], XH, 0.42))
    tw2 = hwidth(lj[0], lj[1], Wk, 0, p.dstem)
    foot = (Wk - tw2 / 2, 0)
    clipped(s, foot, lj, p.dstem, lj, (top[0] - j_[0], top[1] - j_[1]), p.end_r)
    wedge(s, foot[0], 0, tw2 / 2, p.fl, p.wedge_r, slope=(lj[0] - foot[0]) / lj[1])
    return s


@glyph("space", 0x20)
def space(p):
    return Shape(), round(p.W(250, 270))
