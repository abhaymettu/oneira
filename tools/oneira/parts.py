"""Shared construction: stems, bowls, arches, hooks, dots."""

import math

from .geom import SQRT3, Tip, _area, arc, hwidth, lerp, ring, tittle, wedge
from .params import OV, XH


def stem(s, p, x, y0, y1, foot=True, head=True, top_tip=False):
    """Vertical stem from y0 to y1 with wedges on the ends that land on a
    metric line. top_tip ends the stem in a point instead (t)."""
    s.rect(x, y0, x + p.stem, y1, r=p.end_r)
    cx = x + p.stem / 2
    if foot:
        wedge(s, cx, y0, p.stem / 2, p.fl, p.soft, up=True)
    if head:
        wedge(s, cx, y1, p.stem / 2, p.fl, p.soft, up=False)
    if top_tip:
        Tip(p.w, p.soft, scale=lerp(0.8, 0.5, p.t)).draw(s, (x + p.stem, y1), (x, y1), (0, -1))


def bowl(s, p, cx, rx, stem_side, cy=XH / 2, ry=XH / 2 + OV):
    """Closed bowl that meets a stem on one side. The stroke is heavier on the
    free round side and thins where it joins the stem."""
    outer = (cx, cy, rx, ry)
    if stem_side == "right":
        left, right = cx - rx + p.rv, cx + rx - p.join
    else:
        left, right = cx - rx + p.join, cx + rx - p.rv
    inner = ((left + right) / 2, cy, (right - left) / 2, ry - p.sh)
    ring(s, outer, inner)


def round_o(s, p, cx, rx, cy, ry):
    ring(s, (cx, cy, rx, ry), (cx, cy, rx - p.rv, ry - p.sh))


def arch(s, p, xl, xr, top=XH + OV, a0=-6, tip=False, flat=0.96, right_rv=False):
    """Shoulder of n, m, h, r. Thin where it springs from the left stem.
    Returns the centre height, where the right stem should stop."""
    rx = (xr - xl) / 2
    ry = rx * flat
    cy = top - ry
    left = xl + p.join
    right = xr - (p.rv if right_rv else p.stem)
    inner = ((left + right) / 2, cy, (right - left) / 2, ry - p.sh)
    arc(s, (xl + rx, cy, rx, ry), inner, a0, 186, (p.tip() if tip else None, None))
    return cy


def cup(s, p, xl, xr, bottom=-OV, flat=0.96):
    """Bottom of u: thin where it joins the right stem. Returns centre height."""
    rx = (xr - xl) / 2
    ry = rx * flat
    cy = bottom + ry
    left, right = xl + p.stem, xr - p.join
    inner = ((left + right) / 2, cy, (right - left) / 2, ry - p.sh)
    arc(s, (xl + rx, cy, rx, ry), inner, 174, 366)
    return cy


def hook(s, p, x_right, bottom, rx, ry, a0=205):
    """Descender hook of g and j, ending in a tip on the left. x_right is the
    right edge of the stem it hangs from. Returns the centre height."""
    cy = bottom + ry
    cx = x_right - rx
    inner = (cx + (p.rv - p.stem) / 2, cy, rx - (p.stem + p.rv) / 2, ry - p.sh)
    arc(s, (cx, cy, rx, ry), inner, a0, 368, (p.tip(), None))
    return cy


def dot(s, p, cx, base):
    """The triangle dot, its lowest point `base` units above the x-height."""
    r = p.stem * 0.5 + 14
    low = lerp(r, 2 * 2.5 * r / (2 * SQRT3), p.w)  # distance centre to lowest point
    tittle(s, cx, XH + base + low, r, p.w, p.soft)
    return r


def ell_x(e, y, side):
    """x on ellipse e at height y (side +1 right, -1 left)."""
    cx, cy, rx, ry = e
    v = max(-1.0, min(1.0, (y - cy) / ry))
    return cx + side * rx * math.sqrt(1 - v * v)


def _toward_vertex(p, xe, ye, xv, y_tip):
    """Centre-line height at x=xv, and horizontal width, for a stroke from the
    cut (xe, ye) whose outer edge reaches (xv, y_tip)."""
    dx = abs(xv - xe)
    yc = y_tip
    tw = p.dstem
    for _ in range(6):
        yc = ye + (y_tip - ye) / (1 + tw / (2 * dx))
        tw = hwidth(xe, ye, xv, yc, p.dstem)
    return yc, tw


def pointed(s, p, xe_l, xe_r, ye, xv, y_tip, wedges=(True, True)):
    """Two strokes from horizontal cuts at height ye (centres xe_l, xe_r) to a
    sharp vertex at (xv, y_tip). Each stroke runs a hair past the centre line so
    the halves overlap instead of sharing an edge. Returns the stroke widths."""
    tws = []
    for xe, side, wg in ((xe_l, -1, wedges[0]), (xe_r, 1, wedges[1])):
        yc, tw = _toward_vertex(p, xe, ye, xv, y_tip)
        dx = xv - xe
        t_in = (abs(dx) - tw / 2) / abs(dx)
        y_in = ye + t_in * (yc - ye)
        over = 3 * -side  # past the centre line, toward the other stroke
        slope = (yc - ye) / dx  # dy per dx along the centre line
        outer = (xe + side * tw / 2, ye)
        inner = (xe - side * tw / 2, ye)
        pts = [outer, inner, (xv + over, y_in + over * slope), (xv, y_tip)]
        if _area(pts) < 0:
            pts = pts[::-1]
        s.poly(pts)
        if wg:
            up = y_tip > ye
            run = dx / abs(yc - ye)
            wedge(s, xe, ye, tw / 2, p.fl, p.soft, up=up, slope=run)
        tws.append(tw)
    return tws
