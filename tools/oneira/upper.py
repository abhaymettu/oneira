"""Uppercase."""

from .geom import Shape, Tip, arc, clipped, diag, ept, hwidth, lerp, wedge
from .params import CAP, OV, glyph
from .parts import hook, pointed, round_o, stem

YC = CAP / 2
BAR = 0.52  # bars sit a little above centre so the top counter does not look small


def _bar(s, p, x0, x1, y_mid):
    s.rect(x0, y_mid - p.sh / 2, x1, y_mid + p.sh / 2, r=p.bar_r)


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
    s.rect(0, CAP - p.sh, W, CAP, r=p.bar_r)
    _bar(s, p, 0, W * 0.93, CAP * BAR)
    s.rect(0, 0, W * 1.02, p.sh, r=p.bar_r)
    return s


@glyph("F", 0x46, "SO")
def F(p):
    s = Shape()
    W = p.W(400, 520)
    stem(s, p, 0, 0, CAP)
    s.rect(0, CAP - p.sh, W, CAP, r=p.bar_r)
    _bar(s, p, 0, W * 0.92, CAP * 0.5)
    return s


@glyph("L", 0x4C, "SO")
def L(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    s.rect(0, 0, p.W(390, 510), p.sh, r=p.bar_r)
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
    # the tail crosses the bowl and ends below the baseline in a point
    start = (rx + rx * 0.18, CAP * 0.24)
    end = (rx + rx * 0.86, -p.W(70, 80))
    tw = diag(s, *start, *end, p.dstem)
    into = (start[0] - end[0], start[1] - end[1])
    ln = (into[0] ** 2 + into[1] ** 2) ** 0.5
    p.tip().draw(s, (end[0] + tw / 2, end[1]), (end[0] - tw / 2, end[1]), (into[0] / ln, into[1] / ln))
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
    arc(s, (rx, YC, rx, ry), (rx, YC, rx - p.rv, ry - p.sh), 46, 364, (p.tip(), None))
    # the bar ends inside the stroke so its corner never pokes past the curve
    s.rect(rx * 1.06, YC - p.sh * 0.9, 2 * rx - p.rv * 0.5, YC + p.sh * 0.1, r=p.bar_r)
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
    rx = min(ry * 1.04, right - x_stem - p.stem * 0.6)
    bx = right - rx
    cy = y0 + ry
    arc(s, (bx, cy, rx, ry), (bx, cy, rx - p.rv, ry - p.sh), -93, 93)
    s.rect(x_stem, y1 - p.sh, bx + 2, y1)
    s.rect(x_stem, y0, bx + 2, y0 + p.sh)
    return bx, rx


@glyph("D", 0x44, "SR")
def D(p):
    s = Shape()
    stem(s, p, 0, 0, CAP)
    ry = YC + OV
    W = p.W(600, 720)
    rx = ry * 0.98
    bx = W - rx
    arc(s, (bx, YC, rx, ry), (bx, YC, rx - p.rv, ry - p.sh), -92, 92)
    s.rect(0, CAP - p.sh, bx + 2, CAP)
    s.rect(0, 0, bx + 2, p.sh)
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
    ry = rx * 0.9
    cy = -OV + ry
    left, right = p.stem, W - p.stem
    arc(s, (rx, cy, rx, ry), ((left + right) / 2, cy, (right - left) / 2, ry - p.sh), 174, 366)
    stem(s, p, 0, cy - 4, CAP, foot=False)
    stem(s, p, W - p.stem, cy - 4, CAP, foot=False)
    return s


@glyph("J", 0x4A, "OS")
def J(p):
    s = Shape()
    x = p.W(260, 330)  # stem left edge
    rxh = p.W(250, 320) / 2 + p.stem / 2
    cyh = hook(s, p, x + p.stem, -OV, rxh, p.W(220, 240), a0=200)
    stem(s, p, x, cyh - 4, CAP, foot=False)
    return s


# ---------- diagonals ----------

@glyph("A", 0x41, "DD")
def A(p):
    s = Shape()
    W = p.W(640, 790)
    tw0 = p.dstem * 1.25
    for _ in range(4):
        tw_l, tw_r = pointed(Shape(), p, tw0 / 2, W - tw0 / 2, 0, W / 2, CAP + OV, (False, False))
        tw0 = tw_l
    pointed(s, p, tw0 / 2, W - tw0 / 2, 0, W / 2, CAP + OV)
    yb = CAP * 0.3
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
    tw = p.dstem * 1.3
    for _ in range(4):
        tw = hwidth(tw / 2, 0, W - tw / 2, CAP, p.dstem)
    s.rect(0, CAP - p.sh, W, CAP, r=p.bar_r)
    s.rect(0, 0, W, p.sh, r=p.bar_r)
    diag(s, tw / 2 + p.sh * 0.15, p.sh * 0.5, W - tw / 2 - p.sh * 0.15, CAP - p.sh * 0.5, p.dstem)
    return s
