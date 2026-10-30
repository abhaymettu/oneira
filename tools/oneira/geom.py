"""Outline primitives for Oneira.

Every primitive emits a fixed number of points whatever its parameters, so
masters drawn by the same code always interpolate. Outer contours run
counter-clockwise (PostScript direction). Ellipses are (cx, cy, rx, ry).
"""

import math

SQRT3 = math.sqrt(3)


def lerp(a, b, t):
    return a + (b - a) * t


class Shape:
    def __init__(self):
        self.contours = []  # each: [("line", [pt]) | ("curve", [h1, h2, pt])], first entry = start

    def poly(self, pts, radii=None):
        """Closed polygon, counter-clockwise. radii rounds each corner; a
        rounded polygon always emits two on-curve points per corner, even when
        a radius clamps to zero, so point counts never change."""
        if radii is None:
            self.contours.append([("line", [p]) for p in pts])
            return
        c = []
        n = len(pts)
        for i, v in enumerate(pts):
            a, b = _round_corner(pts[i - 1], v, pts[(i + 1) % n], radii[i])
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

    def xbounds(self):
        xs = [pts[-1][0] for c in self.contours for _, pts in c]
        return min(xs), max(xs)

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


def _round_corner(prev, v, nxt, r):
    e1 = (prev[0] - v[0], prev[1] - v[1])
    e2 = (nxt[0] - v[0], nxt[1] - v[1])
    l1, l2 = max(math.hypot(*e1), 1e-9), max(math.hypot(*e2), 1e-9)
    u1, u2 = (e1[0] / l1, e1[1] / l1), (e2[0] / l2, e2[1] / l2)
    alpha = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1])))
    half_t = math.tan(alpha / 2)
    d = r / half_t if half_t > 1e-9 else 0.0
    d = min(d, l1 * 0.5, l2 * 0.5)
    r = d * half_t
    k = 4 / 3 * math.tan((math.pi - alpha) / 4) * r
    a = (v[0] + u1[0] * d, v[1] + u1[1] * d)
    b = (v[0] + u2[0] * d, v[1] + u2[1] * d)
    return (a, (a[0] - u1[0] * k, a[1] - u1[1] * k)), (b, (b[0] - u2[0] * k, b[1] - u2[1] * k))


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


def ring(shape, outer, inner):
    """Closed bowl. The inner ellipse is free, so the stroke can thin toward a
    join or thicken on the round sides."""
    ellipse(shape, outer)
    ellipse(shape, inner, clockwise=True)


def arc(shape, outer, inner, a0, a1, tips=(None, None)):
    """Open stroke between two ellipses from a0 to a1 (counter-clockwise),
    cut along the line joining the matching points. tips=(start, end) takes
    Tip objects or None."""
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
    """The curved-stroke version of the triangle: a 60 degree point growing out
    of the cut. growth 0 leaves a soft rounded nub, 1 a full tip."""

    def __init__(self, growth, soft, scale=1.0):
        self.growth, self.soft, self.scale = growth, soft, scale

    def draw(self, shape, po, pi, into):
        half = math.dist(po, pi) / 2
        mid = ((po[0] + pi[0]) / 2, (po[1] + pi[1]) / 2)
        h = half * lerp(0.42, SQRT3, self.growth) * self.scale
        ap = (mid[0] - into[0] * h, mid[1] - into[1] * h)
        nudge = 3  # tuck the base inside the stroke: no seam
        p1 = (po[0] + into[0] * nudge, po[1] + into[1] * nudge)
        p2 = (pi[0] + into[0] * nudge, pi[1] + into[1] * nudge)
        pts = [p1, p2, ap]
        if _area(pts) < 0:
            pts = [p2, p1, ap]
        apex_r = lerp(half * 1.4, self.soft, self.growth)
        shape.poly(pts, [0, 0, apex_r])


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
