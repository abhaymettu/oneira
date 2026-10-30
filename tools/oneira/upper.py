"""Uppercase."""

import math

from .geom import Shape, Tip, arc, clipped, diag, ept, hwidth, lerp, limb, wedge
from .params import CAP, OV, glyph
from .parts import ell_x, hook, pointed, round_o, stem, zee

YC = CAP / 2
BAR = 0.52  # bars sit a little above centre so the top counter does not look small


def _bar(s, p, x0, x1, y_mid):
    s.rect(x0, y_mid - p.sh / 2, x1, y_mid + p.sh / 2, r=p.bar_r)


def _arm(s, p, y0, x1):
    """Arm of E, F, L: starts inside the stem, soft only at its free end."""
    r = p.bar_r
    s.poly([(p.stem / 2, y0), (x1, y0), (x1, y0 + p.sh), (p.stem / 2, y0 + p.sh)], [0, r, r, 0])


# ---------- straight ----------

@glyph("H", 0x48, "SS")
def H(p):
    s = Shape()
    W = p.W(520, 660)
    stem(s, p, 0, 0, CAP)
    stem(s, p, W - p.stem, 0, CAP)
    _bar(s, p, 0, W, CAP * BAR)
    return s


@glyph("I", 0x49, "SS")
def I(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    return s


@glyph("E", 0x45, "SO")
def E(p):
    s = Shape()
    W = p.W(410, 530)
    stem(s, p, 0, 0, CAP)
    _arm(s, p, CAP - p.sh, W)
    _arm(s, p, CAP * BAR - p.sh / 2, W * 0.93)
    _arm(s, p, 0, W * 1.02)
    return s


@glyph("F", 0x46, "SO")
def F(p):
    s = Shape()
    W = p.W(400, 520)
    stem(s, p, 0, 0, CAP)
    _arm(s, p, CAP - p.sh, W)
    _arm(s, p, CAP * 0.5 - p.sh / 2, W * 0.92)
    return s


@glyph("L", 0x4C, "SO")
def L(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    _arm(s, p, 0, p.W(390, 510))
    return s


@glyph("T", 0x54, "OO")
def T(p):
    s = Shape()
    W = p.W(540, 680)
    s.rect(0, CAP - p.sh, W, CAP, r=p.bar_r)
    stem(s, p, (W - p.stem) / 2, 0, CAP - p.sh / 2, head=False)
    return s


# ---------- round ----------

def _O_r(p):
    return p.W(372, 424)


@glyph("O", 0x4F, "RR")
def O(p):
    s = Shape()
    rx = _O_r(p)
    round_o(s, p, rx, rx, YC, YC + OV)
    return s


@glyph("Q", 0x51, "RR")
def Q(p):
    s = Shape()
    rx = _O_r(p)
    round_o(s, p, rx, rx, YC, YC + OV)
    # the tail grows out of the bowl's lower right and ends below the baseline
    # in a tip; its square start hides inside the bowl stroke
    a = math.radians(-58)
    mid_r = (rx - p.rv / 2, YC + OV - p.sh / 2)
    start = (rx + mid_r[0] * math.cos(a), YC + mid_r[1] * math.sin(a))
    d = (math.cos(math.radians(-40)), math.sin(math.radians(-40)))
    ln = (start[1] + p.W(80, 96)) / -d[1]
    end = (start[0] + d[0] * ln, start[1] + d[1] * ln)
    pts = limb(s, start, end, p.dstem * 0.96)
    p.tip().draw(s, pts[1], pts[2], (-d[0], -d[1]))
    return s


@glyph("C", 0x43, "RO")
def C(p):
    s = Shape()
    rx, ry = p.W(356, 404), YC + OV
    arc(s, (rx, YC, rx, ry), (rx, YC, rx - p.rv, ry - p.sh), 48, 312, (p.tip(), p.tip()))
    return s


@glyph("G", 0x47, "RS")
def G(p):
    s = Shape()
    rx, ry = p.W(364, 414), YC + OV
    outer = (rx, YC, rx, ry)
    yt = YC + p.sh * 0.1  # bar top: the arc ends exactly here, so the two meet flush
    a1 = 360 + math.degrees(math.asin((yt - YC) / ry))
    arc(s, outer, (rx, YC, rx - p.rv, ry - p.sh), 46, a1, (p.tip(), None))
    yb = yt - p.sh
    x1 = ell_x(outer, yb, 1) - 1  # the bar's lower corner stays inside the bowl
    s.poly([(rx * 1.06, yb), (x1, yb), (x1, yt), (rx * 1.06, yt)], [p.bar_r, 0, 0, p.bar_r])
    return s


@glyph("S", 0x53, "RR")
def S(p):
    s = Shape()
    top, bot = CAP + OV, -OV
    total = top - bot + p.sh
    ry1 = total * 0.24
    ry2 = total / 2 - ry1
    rx2 = p.W(292, 352)
    rx1 = rx2 * 0.9
    cx = rx2
    cy1, cy2 = top - ry1, bot + ry2
    sv = p.rv * 0.94
    arc(s, (cx, cy1, rx1, ry1), (cx, cy1, rx1 - sv, ry1 - p.sh), 30, 277, (p.tip(), None))
    arc(s, (cx, cy2, rx2, ry2), (cx, cy2, rx2 - sv, ry2 - p.sh), 210, 457, (p.tip(), None))
    return s


def _half_bowl(s, p, x_stem, y0, y1, right):
    """D-style bowl from the stem to `right`: straight bars into a half ellipse."""
    ry = (y1 - y0) / 2
    # size the bowl from its counter, so the counter stays round at Black
    rx = min((ry - p.sh) * 1.02 + p.rv, right - x_stem - p.stem * 0.6)
    bx = right - rx
    cy = y0 + ry
    arc(s, (bx, cy, rx, ry), (bx, cy, rx - p.rv, ry - p.sh), -93, 93)
    # bars start inside the stem so they never poke past its softened corner
    xs = x_stem + p.stem / 2
    s.rect(xs, y1 - p.sh, bx + 2, y1)
    s.rect(xs, y0, bx + 2, y0 + p.sh)
    return bx, rx


@glyph("D", 0x44, "SR")
def D(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    ry = YC  # the bowl meets flat bars, so no overshoot: it would leave a step
    W = p.W(600, 720)
    rx = ry * 0.98
    bx = W - rx
    arc(s, (bx, YC, rx, ry), (bx, YC, rx - p.rv, ry - p.sh), -92, 92)
    xs = p.stem / 2
    s.rect(xs, CAP - p.sh, bx + 2, CAP)
    s.rect(xs, 0, bx + 2, p.sh)
    return s


@glyph("P", 0x50, "SR")
def P_(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    _half_bowl(s, p, 0, CAP * 0.40, CAP, p.W(470, 600))
    return s


@glyph("R", 0x52, "SD")
def R(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    yb = CAP * lerp(0.42, 0.40, p.t)
    bx, rx = _half_bowl(s, p, 0, yb, CAP, p.W(470, 600))
    foot = bx + rx + p.W(20, 40)
    top = (bx - rx * 0.05, yb + p.sh / 2)
    tw = hwidth(top[0], top[1], foot, 0, p.dstem)
    diag(s, top[0], top[1], foot - tw / 2, 0, p.dstem)
    wedge(s, foot - tw / 2, 0, tw / 2, p.fl, p.soft, slope=(top[0] - foot + tw / 2) / top[1])
    return s


@glyph("B", 0x42, "SR")
def B(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    ym = CAP * 0.54
    _half_bowl(s, p, 0, ym - p.sh / 2, CAP, p.W(440, 560))
    _half_bowl(s, p, 0, 0, ym + p.sh / 2, p.W(490, 620))
    return s


@glyph("U", 0x55, "SS")
def U(p):
    s = Shape()
    W = p.W(540, 670)
    rx = W / 2
    ry = rx * 1.04  # a taller cup eases the curvature jump into the straight stems
    cy = -OV + ry
    left, right = p.stem, W - p.stem
    arc(s, (rx, cy, rx, ry), ((left + right) / 2, cy, (right - left) / 2, ry - p.sh), 174, 366)
    stem(s, p, 0, cy - 4, CAP, foot=False)
    stem(s, p, W - p.stem, cy - 4, CAP, foot=False)
    return s


@glyph("J", 0x4A, "OS")
def J(p):
    s = Shape()
    rxh = p.W(150, 124) + p.stem * 1.03  # the counter stays open at Black
    x = 2 * rxh - p.stem  # stem left edge; the hook hangs to the left of it
    cyh = hook(s, p, x + p.stem, -OV, rxh, p.W(236, 262), a0=192)
    stem(s, p, x, cyh - 4, CAP, foot=False)
    return s


# ---------- diagonals ----------

@glyph("A", 0x41, "DD")
def A(p):
    s = Shape()
    W = p.W(640, 840)
    tw0 = p.dstem * 1.25
    for _ in range(4):
        tw_l, tw_r = pointed(Shape(), p, tw0 / 2, W - tw0 / 2, 0, W / 2, CAP + OV, (False, False))
        tw0 = tw_l
    pointed(s, p, tw0 / 2, W - tw0 / 2, 0, W / 2, CAP + OV)
    yb = CAP * lerp(0.3, 0.27, p.t)  # lower at Black so the top counter stays open
    f = yb / (CAP + OV)
    xl = lerp(0, W / 2, f) + tw0 * 0.5
    xr = lerp(W, W / 2, f) - tw0 * 0.5
    _bar(s, p, xl, xr, yb)
    return s


@glyph("V", 0x56, "DD")
def V(p):
    s = Shape()
    W = p.W(640, 790)
    tw0 = p.dstem * 1.25
    for _ in range(4):
        tw0 = pointed(Shape(), p, tw0 / 2, W - tw0 / 2, CAP, W / 2, -OV, (False, False))[0]
    pointed(s, p, tw0 / 2, W - tw0 / 2, CAP, W / 2, -OV)
    return s


@glyph("W", 0x57, "DD")
def W_(p):
    s = Shape()
    W = p.W(960, 1170)
    q = W / 4
    tw0 = p.dstem * 1.25
    for _ in range(4):
        tw0 = pointed(Shape(), p, tw0 / 2, 2 * q - tw0 * 0.2, CAP, q, -OV, (False, False))[0]
    pointed(s, p, tw0 / 2, 2 * q, CAP, q + tw0 * 0.1, -OV, (True, False))
    pointed(s, p, 2 * q, W - tw0 / 2, CAP, 3 * q - tw0 * 0.1, -OV, (False, True))
    return s


@glyph("M", 0x4D, "SS")
def M(p):
    s = Shape()
    W = p.W(720, 900)
    st = p.stem
    # outer legs: vertical stems with feet; the pointed V hangs between them
    stem(s, p, 0, 0, CAP - 2, head=False)
    stem(s, p, W - st, 0, CAP - 2, head=False)
    tw0 = p.dstem * 1.25
    for _ in range(4):
        tw0 = pointed(Shape(), p, tw0 / 2, W - tw0 / 2, CAP, W / 2, -OV, (False, False))[0]
    pointed(s, p, tw0 / 2, W - tw0 / 2, CAP, W / 2, -OV, (False, False))
    return s


@glyph("N", 0x4E, "SS")
def N(p):
    s = Shape()
    W = p.W(560, 700)
    st = p.stem
    stem(s, p, 0, 0, CAP, head=False)
    stem(s, p, W - st, 0, CAP, foot=False)
    tw = p.dstem * 1.3
    for _ in range(4):
        tw = hwidth(tw / 2, CAP, W - tw / 2, 0, p.dstem)
    diag(s, tw / 2, CAP, W - tw / 2, 0, p.dstem)
    return s


@glyph("X", 0x58, "DD")
def X(p):
    s = Shape()
    W = p.W(600, 760)
    tw = p.dstem * 1.3
    for _ in range(4):
        tw = hwidth(tw / 2, 0, W - tw / 2, CAP, p.dstem)
    diag(s, tw / 2, 0, W - tw / 2, CAP, p.dstem)
    diag(s, W - tw / 2, 0, tw / 2, CAP, p.dstem)
    run = (W - tw) / CAP
    for x, y, up, sl in ((tw / 2, 0, True, run), (W - tw / 2, 0, True, -run),
                         (tw / 2, CAP, False, run), (W - tw / 2, CAP, False, -run)):
        wedge(s, x, y, tw / 2, p.fl, p.soft, up=up, slope=sl)
    return s


@glyph("Y", 0x59, "DD")
def Y(p):
    s = Shape()
    W = p.W(620, 770)
    cx = W / 2
    yj = CAP * 0.42
    xs = cx - p.stem / 2
    stem(s, p, xs, 0, yj + 4, head=False)
    for xe in (0, W):
        tw = p.dstem * 1.3
        for _ in range(4):
            xc = xe + (tw / 2 if xe == 0 else -tw / 2)
            tw = hwidth(xc, CAP, cx, yj, p.dstem)
        clipped(s, (xc, CAP), (cx, yj), p.dstem, (cx, 0), (0, 1))
        wedge(s, xc, CAP, tw / 2, p.fl, p.soft, up=False, slope=(cx - xc) / (CAP - yj))
    return s


@glyph("K", 0x4B, "SD")
def K(p):
    s = Shape()
    Wk = p.W(560, 720)
    stem(s, p, 0, 0, CAP)
    xs = p.stem / 2
    j_ = (xs, CAP * 0.3)
    tw = hwidth(j_[0], j_[1], Wk, CAP, p.dstem)
    top = (Wk - tw / 2, CAP)
    clipped(s, top, j_, p.dstem, (xs, 0), (0, 1))
    wedge(s, top[0], CAP, tw / 2, p.fl, p.soft, up=False, slope=(j_[0] - top[0]) / (CAP - j_[1]))
    lj = (lerp(j_[0], top[0], 0.4), lerp(j_[1], CAP, 0.4))
    tw2 = hwidth(lj[0], lj[1], Wk + p.W(10, 30), 0, p.dstem)
    foot = (Wk + p.W(10, 30) - tw2 / 2, 0)
    clipped(s, foot, lj, p.dstem, lj, (top[0] - j_[0], top[1] - j_[1]))
    wedge(s, foot[0], 0, tw2 / 2, p.fl, p.soft, slope=(lj[0] - foot[0]) / lj[1])
    return s


@glyph("Z", 0x5A, "OO")
def Z(p):
    s = Shape()
    W = p.W(540, 680)
    zee(s, p, W, CAP)
    return s
