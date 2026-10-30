"""Shared construction: stems, bowls, arches, hooks, dots."""

import math

from .geom import SQRT3, Tip, arc, lerp, ring, tittle, wedge
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
