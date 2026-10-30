"""Outline primitives for Oneira.

Every primitive emits a fixed number of points whatever its parameters, so
masters drawn by the same code always interpolate. Outer contours run
counter-clockwise (PostScript direction). Ellipses are (cx, cy, rx, ry).
"""

import math

from fontTools.pens.boundsPen import BoundsPen

SQRT3 = math.sqrt(3)
MIN_R = 2.0


def lerp(a, b, t):
    return a + (b - a) * t


class Shape:
    def __init__(self):
        self.contours = []  # each: [("line", [pt]) | ("curve", [h1, h2, pt])], first entry = start

    def poly(self, pts, radii=None):
        """Closed polygon, counter-clockwise. radii rounds each corner; a
        rounded polygon always emits two on-curve points per corner, so point
        counts never change. A corner is never rounded by less than MIN_R:
        a zero radius would leave a zero-length curve in the font."""
        if radii is None:
            self.contours.append([("line", [p]) for p in pts])
            return
        c = []
        n = len(pts)
        # a corner may use a whole edge when the corner at its other end is sharp
        share = [(0.5 if radii[i - 1] else 1.0, 0.5 if radii[(i + 1) % n] else 1.0) for i in range(n)]
        used = [_round_corner(pts[i - 1], v, pts[(i + 1) % n], radii[i], share[i])[2] for i, v in enumerate(pts)]
        for i, v in enumerate(pts):
            prev, nxt = pts[i - 1], pts[(i + 1) % n]
            if radii[i]:
                a, b, _ = _round_corner(prev, v, nxt, radii[i], share[i])
            else:  # a sharp corner takes MIN_R from what its neighbours leave
                room = min(math.dist(prev, v) - used[i - 1], math.dist(v, nxt) - used[(i + 1) % n]) / 2
                a, b, _ = _round_corner(prev, v, nxt, MIN_R, (1.0, 1.0), max(room, 0.0))
            c.append(("line", [a[0]]))
            c.append(("curve", [a[1], b[1], b[0]]))
        self.contours.append(c)

    def rect(self, x0, y0, x1, y1, r=None):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        self.poly(pts, None if r is None else [r] * 4)

    def moved(self, dx):
        out = Shape()
        out.contours = [[(k, [(x + dx, y) for x, y in pts]) for k, pts in c] for c in self.contours]
        return out

    def scaled(self, k, dx=0.0, dy=0.0):
        """Uniform scale about the origin, then a shift."""
        out = Shape()
        out.contours = [[(kind, [(x * k + dx, y * k + dy) for x, y in pts]) for kind, pts in c]
                        for c in self.contours]
        return out

    def merged(self, *others):
        out = Shape()
        out.contours = self.contours + [c for o in others for c in o.contours]
        return out

    def rotated(self, cx, cy):
        """Half turn about (cx, cy). A rotation keeps contour direction."""
        out = Shape()
        out.contours = [[(k, [(2 * cx - x, 2 * cy - y) for x, y in pts]) for k, pts in c]
                        for c in self.contours]
        return out

    def xbounds(self):
        """Exact ink extent, curve extremes included (an arc's widest point is
        often not an on-curve point)."""
        bp = BoundsPen(None)
        self.draw(bp)
        return bp.bounds[0], bp.bounds[2]

    def draw(self, pen):
        for c in self.contours:
            first = c[0][1][-1]
            pen.moveTo(first)
            for j, (kind, pts) in enumerate(c[1:], 1):
                if j == len(c) - 1 and math.dist(pts[-1], first) < 1e-6:
                    pts = list(pts[:-1]) + [first]
                if kind == "line":
                    pen.lineTo(pts[0])
                else:
                    pen.curveTo(*pts)
            pen.closePath()


def _round_corner(prev, v, nxt, r, share=(0.5, 0.5), cap=math.inf):
    """The corner's two tangent points with their handles, and how far along
    each edge the rounding reaches."""
    e1 = (prev[0] - v[0], prev[1] - v[1])
    e2 = (nxt[0] - v[0], nxt[1] - v[1])
    l1, l2 = max(math.hypot(*e1), 1e-9), max(math.hypot(*e2), 1e-9)
    u1, u2 = (e1[0] / l1, e1[1] / l1), (e2[0] / l2, e2[1] / l2)
    alpha = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1])))
    half_t = math.tan(alpha / 2)
    d = r / half_t if half_t > 1e-9 else 0.0
    d = min(d, l1 * share[0], l2 * share[1], cap)
    r = d * half_t
    k = 4 / 3 * math.tan((math.pi - alpha) / 4) * r
    a = (v[0] + u1[0] * d, v[1] + u1[1] * d)
    b = (v[0] + u2[0] * d, v[1] + u2[1] * d)
    return (a, (a[0] - u1[0] * k, a[1] - u1[1] * k)), (b, (b[0] - u2[0] * k, b[1] - u2[1] * k)), d


# ---------- ellipses ----------

def ept(e, deg):
    t = math.radians(deg)
    return (e[0] + e[2] * math.cos(t), e[1] + e[3] * math.sin(t))


def _arc_segments(e, a0, a1):
    """Cubic segments for an elliptical arc a0 -> a1 (degrees). The segment
    count depends only on the sweep, so keep sweeps in the same 90-degree
    band across masters."""
    cx, cy, rx, ry = e
    n = max(1, math.ceil(abs(a1 - a0) / 90 - 1e-9))
    step = math.radians(a1 - a0) / n
    k = 4 / 3 * math.tan(step / 4)
    pt = lambda a: (cx + rx * math.cos(a), cy + ry * math.sin(a))
    d = lambda a: (-rx * math.sin(a), ry * math.cos(a))
    segs, a = [], math.radians(a0)
    for _ in range(n):
        b = a + step
        p0, p1, d0, d1 = pt(a), pt(b), d(a), d(b)
        segs.append(((p0[0] + k * d0[0], p0[1] + k * d0[1]),
                     (p1[0] - k * d1[0], p1[1] - k * d1[1]), p1))
        a = b
    return pt(math.radians(a0)), segs


def ellipse(shape, e, clockwise=False):
    a0, a1 = (360, 0) if clockwise else (0, 360)
    start, segs = _arc_segments(e, a0, a1)
    shape.contours.append([("line", [start])] + [("curve", list(x)) for x in segs])


def _check_inner(inner):
    if inner[2] <= 0 or inner[3] <= 0:
        raise ValueError(f"stroke is thicker than its curve: inner ellipse {inner}")


def ring(shape, outer, inner):
    """Closed bowl. The inner ellipse is free, so the stroke can thin toward a
    join or thicken on the round sides."""
    _check_inner(inner)
    ellipse(shape, outer)
    ellipse(shape, inner, clockwise=True)


def arc(shape, outer, inner, a0, a1, tips=(None, None)):
    """Open stroke between two ellipses from a0 to a1 (counter-clockwise),
    cut along the line joining the matching points. tips=(start, end) takes
    Tip objects or None."""
    _check_inner(inner)
    s_out, out = _arc_segments(outer, a0, a1)
    s_in, inn = _arc_segments(inner, a1, a0)
    c = [("line", [s_out])] + [("curve", list(s)) for s in out]
    c.append(("line", [s_in]))
    c += [("curve", list(s)) for s in inn]
    shape.contours.append(c)
    for tip, a, sign in ((tips[0], a0, 1), (tips[1], a1, -1)):
        if tip is not None:
            tip.draw(shape, ept(outer, a), ept(inner, a), _tangent(outer, inner, a, sign))


def _tangent(outer, inner, a, sign):
    """Unit direction pointing from the cut into the stroke body."""
    t = math.radians(a)
    rx, ry = (outer[2] + inner[2]) / 2, (outer[3] + inner[3]) / 2
    tx, ty = -rx * math.sin(t) * sign, ry * math.cos(t) * sign
    ln = math.hypot(tx, ty)
    return tx / ln, ty / ln


class Tip:
    """The curved-stroke version of the triangle. growth 1 is a 60 degree tip
    with a soft apex; growth 0 is a round cap, the dream-state terminal. Both
    are the same six-point outline so they interpolate."""

    def __init__(self, growth, soft, scale=1.0):
        self.growth, self.soft, self.scale = growth, soft, scale

    def reach(self, half):
        """How far the end reaches past its cut, for a stroke 2 * half wide."""
        return lerp(half, half * SQRT3 * self.scale, self.growth)

    def draw(self, shape, po, pi, into):
        half = math.dist(po, pi) / 2
        mid = ((po[0] + pi[0]) / 2, (po[1] + pi[1]) / 2)
        out = (-into[0], -into[1])
        cut = ((po[0] - mid[0]) / half, (po[1] - mid[1]) / half)  # unit, toward po
        g = self.growth
        at = lambda base, a, b: (base[0] + out[0] * a + cut[0] * b, base[1] + out[1] * a + cut[1] * b)
        # round cap: shoulders straight out from the cut corners; tip: shoulders
        # either side of the apex, so the two soft corners read as one round point
        h = half * SQRT3 * self.scale
        e = self.soft * 0.5
        q1 = lerp_pt(at(po, half, 0), at(mid, h, e), g)
        q2 = lerp_pt(at(pi, half, 0), at(mid, h, -e), g)
        depth = 6  # the base tucks inside the stroke: overlap, no seam
        p1 = at(po, -depth, -1.5)
        p2 = at(pi, -depth, 1.5)
        pts = [p1, po, q1, q2, pi, p2]
        r = lerp(half, self.soft, g)
        radii = [0, 0, r, r, 0, 0]
        if _area(pts) < 0:
            pts, radii = pts[::-1], radii[::-1]
        shape.poly(pts, radii)


def lerp_pt(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


# ---------- straight strokes ----------

def diag(shape, x0, y0, x1, y1, stem, r=None):
    """Straight stroke between two centre points with horizontal cuts, sized so
    the perpendicular thickness equals stem. Returns the horizontal width."""
    if y1 < y0:
        x0, y0, x1, y1 = x1, y1, x0, y0
    tw = stem * math.hypot(x1 - x0, y1 - y0) / abs(y1 - y0)
    h = tw / 2
    pts = [(x0 - h, y0), (x0 + h, y0), (x1 + h, y1), (x1 - h, y1)]
    shape.poly(pts, None if r is None else [r] * 4)
    return tw


def limb(shape, a, b, width, cuts=("perp", "perp"), r=None):
    """Straight stroke from a to b. Each end is cut square to the stroke
    ("perp") or along the horizontal ("h"). Returns the four corners
    (a-side, b-side, b-side, a-side), so a tip or wedge can sit on an end.
    r rounds the corners at each end."""
    ln = math.dist(a, b)
    d = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)

    n = (-d[1] * width / 2, d[0] * width / 2)

    def ends(c, cut):
        """The end's two corners, on the -n side first so both ends pair up."""
        if cut == "h":
            hw = width / 2 / max(abs(d[1]), 1e-9)
            lo, hi = (c[0] - hw, c[1]), (c[0] + hw, c[1])
            return (lo, hi) if n[0] > 0 else (hi, lo)
        return (c[0] - n[0], c[1] - n[1]), (c[0] + n[0], c[1] + n[1])
    a1, a2 = ends(a, cuts[0])
    b1, b2 = ends(b, cuts[1])
    pts = [a1, b1, b2, a2]
    radii = None if r is None else [r[0], r[1], r[1], r[0]]  # r: (a-end, b-end) corner radii
    if _area(pts) > 0:
        shape.poly(pts, radii)
    else:
        shape.poly(pts[::-1], None if radii is None else radii[::-1])
    return pts


def hwidth(x0, y0, x1, y1, stem):
    return stem * math.hypot(x1 - x0, y1 - y0) / abs(y1 - y0)


def clipped(shape, end, toward, stem, a, u):
    """Stroke from `end` (horizontal cut) toward a point, stopped where it meets
    the line through `a` with direction `u`, so the join hides inside the
    stroke it meets. Returns the horizontal width at the cut."""
    dx, dy = toward[0] - end[0], toward[1] - end[1]
    ln = math.hypot(dx, dy)
    d = (dx / ln, dy / ln)
    tw = stem * ln / abs(dy)
    out = []
    for side in (-1, 1):
        c = (end[0] + side * tw / 2, end[1])
        det = d[0] * -u[1] - d[1] * -u[0]
        l_ = ((a[0] - c[0]) * -u[1] - (a[1] - c[1]) * -u[0]) / det
        out.append((c, (c[0] + l_ * d[0], c[1] + l_ * d[1])))
    pts = [out[0][0], out[1][0], out[1][1], out[0][1]]
    if _area(pts) < 0:
        pts = pts[::-1]
    shape.poly(pts)
    return tw


def wedge(shape, cx, y, half, flare, soft, up=True, slope=0.0):
    """The one serif: an equilateral triangle whose base sits on y, reaching
    `flare` past the stroke on each side. slope (stroke dx per unit dy away
    from the cut) keeps the apex on the stroke's centre line."""
    b = half + flare
    h = b * SQRT3
    apex_dx = h * slope
    if up:
        pts = [(cx - b, y), (cx + b, y), (cx + apex_dx, y + h)]
    else:
        pts = [(cx + apex_dx, y - h), (cx + b, y), (cx - b, y)]
    shape.poly(pts, [soft] * 3)


def tittle(shape, cx, cy, r, w, soft):
    """Dot as a rounded downward triangle: a circle of radius r at w=0 (corner
    radius = inradius), a soft triangle at w=1."""
    side = lerp(2 * SQRT3, 2.5, w) * r
    inr = side / (2 * SQRT3)
    radius = lerp(inr * 0.999, soft, w)
    top = cy + inr
    shape.poly([(cx, cy - 2 * inr), (cx + side / 2, top), (cx - side / 2, top)], [radius] * 3)


def _meet(p, d, q, e):
    """Intersection of the lines p + s*d and q + r*e."""
    det = d[0] * -e[1] - d[1] * -e[0]
    s = ((q[0] - p[0]) * -e[1] - (q[1] - p[1]) * -e[0]) / det
    return (p[0] + s * d[0], p[1] + s * d[1])


def chevron(shape, apex, e1, e2, t, r_apex=0.0, r_end=0.0):
    """Two arms of thickness t from e1 and e2 meeting in a mitred point at
    apex (< > ^ and guillemets). Ends are cut square to each arm."""
    us, outs = [], []
    for e in (e1, e2):
        ln = math.dist(apex, e)
        us.append(((e[0] - apex[0]) / ln, (e[1] - apex[1]) / ln))
    for i in (0, 1):
        u, other = us[i], us[1 - i]
        n = (-u[1], u[0])
        if n[0] * other[0] + n[1] * other[1] > 0:
            n = (-n[0], -n[1])
        outs.append((n[0] * t / 2, n[1] * t / 2))
    off = lambda pt, o, k: (pt[0] + o[0] * k, pt[1] + o[1] * k)
    outer = _meet(off(apex, outs[0], 1), us[0], off(apex, outs[1], 1), us[1])
    inner = _meet(off(apex, outs[0], -1), us[0], off(apex, outs[1], -1), us[1])
    pts = [off(e1, outs[0], 1), outer, off(e2, outs[1], 1), off(e2, outs[1], -1), inner, off(e1, outs[0], -1)]
    radii = [r_end, r_apex, r_end, r_end, 0, r_end]
    if _area(pts) < 0:
        pts, radii = pts[::-1], radii[::-1]
    shape.poly(pts, radii)
