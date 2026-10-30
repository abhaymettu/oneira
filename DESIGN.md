# Oneira design spec

Oneira is a geometric typeface with one rule: **every stroke end is the same
triangle.** Straight stems that land on a metric line stand on an equilateral
wedge. Curved strokes end in a 60 degree tip. The dot on *i* and *j* is the
triangle itself. Corners are softened, never razor sharp.

The second axis, **Lucidity** (`LUCD`), runs from dream to waking. At 0 the
face is a soft geometric sans: no wedges, round dots, rounder corners. At 100
the triangles have fully grown in and the corners tighten. Weight (`wght`)
runs from 100 (Thin) to 900 (Black).

## Metrics

| Metric        | Value |
| ------------- | ----- |
| UPM           | 1000  |
| Cap height    | 700   |
| x-height      | 520   |
| Ascender      | 750   |
| Descender     | -220  |
| Overshoot     | 12 (round), 0 (flat) |

## Stroke model

| Weight | Stem | Horizontal | Diagonal | Wedge flare at LUCD 100 |
| ------ | ---- | ---------- | -------- | ----------------------- |
| 100    | 30   | 0.86 x stem | 0.94 x stem | 48 |
| 400    | 85   | 0.82 x stem | 0.94 x stem | 54 |
| 900    | 176  | 0.74 x stem | 0.94 x stem | 64 |

Optical rules, applied everywhere:

1. **Round strokes are heavier.** Vertical sides of bowls are 1.06 x stem so
   that round letters do not look lighter than straight ones.
2. **Joins thin out.** Where an arch or bowl meets a stem (n, m, h, u, a, b,
   d, g, p, q) the curved stroke thins to about 0.7 x stem at the join, more
   at heavy weights. This keeps the crotch open at Black.
3. **Bars sit above centre.** The bar of H, the middle of E, F and B, and the
   join of R and P sit at 0.52 of the cap height or higher, so the upper
   counter does not look smaller than the lower one.
4. **Round shapes overshoot** the baseline, x-height and cap height by 12.
5. **Counters stay open at Black.** Widths grow with weight; horizontals thin
   faster than verticals.
6. **Triangles are equilateral.** Flare grows the base; the 60 degree angle never
   changes. Soft corner radius is 5 at Thin and 16 at Black.
7. **No corner is razor sharp.** Every free stroke end, straight or diagonal,
   rounds in the dream state. A pointed vertex (A, V, W, M) is a small flat
   with soft corners, twice as soft at dream as at lucid, and still reaches
   the overshoot. Even a hidden corner rounds by at least 2 units.

The weight axis has an avar: the named weights sit where the grey of
running text darkens by equal steps on each side of Regular
(`tools/ramp.py --solve`).

## Spacing

Sidebearings are measured from the plain sans skeleton (LUCD 0, ends
unrounded), so wedges hang into the gap the way serifs do. A tip that grows
past that outline on a side without wedges (c, e, r, braces, quotes) gets 60
percent of its growth back as room. Kerning follows weight and Lucidity:
pairs whose wedges or tips meet at lucid ease off as the triangles grow in. Each glyph side is one of: straight, round,
diagonal, or open (bars, arms, terminals), plus per-glyph overrides. Control
strings: `nnonnoon`, `HHOHHOOH`, `nnannbnndnn`.

## Glyph notes

Lowercase is single-story (a, g) and geometric. Shapes come from circles and
straight lines; the personality comes from the triangles and the soft
corners, not from quirky skeletons.

- **n m h u r**: circular arch, thinned where it springs from the stem. The
  stem head at the x-height gets a wedge; the arch does not.
- **o c e**: near-circles, o is 1.03 x as wide as tall. c and e end in tips.
  The bar of e drops at heavy weights to keep the eye open.
- **a d b p q g**: one shared bowl, thinned toward the stem. Stems carry
  wedges at every metric-line end, including the a's head.
- **s**: two stacked arcs, upper smaller; tips on both terminals.
- **i j l**: stems with wedges; i and j carry the triangle dot.
- **t f**: tall stems, bars at the x-height, f hooks right with a tip.
- **k v w x y z**: diagonals with wedges cut horizontally on the metric line,
  apex following the stroke.
- **Caps**: H and O set proportions; E F L T narrow; A V W pointed apexes; M
  splayed; R leg from the bowl; S from two arcs; G with a bar and no spur.
- **Figures**: lining, proportional by default. Zero is an ellipse, one is a
  stem with a wedged flag.

## Character set (v1)

Basic Latin (A-Z, a-z, 0-9, punctuation), the Latin-1 letters with accents
built as composites, and common symbols. Kerning is class based.
