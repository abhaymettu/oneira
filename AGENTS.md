# Working on Oneira

Read [DESIGN.md](DESIGN.md) first. It is the spec every glyph is checked against.

## Layout

| Path | What it does |
| --- | --- |
| `tools/oneira/geom.py` | Outline primitives: `Shape`, rounded polygons, ellipse arcs and rings, `limb`, `wedge`, `Tip`, `chevron`, exact bounds |
| `tools/oneira/params.py` | Metrics, the stroke model `P(t, w)`, glyph and composite registries, spacing classes |
| `tools/oneira/parts.py` | Shared construction: stems, bowls, arches, cups, hooks, dots, pointed vertices, Z |
| `tools/oneira/lower.py`, `upper.py`, `figures.py`, `punct.py`, `marks.py`, `latin1.py`, `symbols.py` | The glyphs |
| `tools/oneira/kerning.py` | Kerning classes and pair values (set at Regular, scaled by weight) |
| `tools/build.py` | Draws six masters to `sources/`, compiles the variable font; `--release` adds statics and WOFF2 |
| `tools/proof.py` | Proof sheets in headless Chromium |
| `tools/inspect_glyph.py` | One glyph's outline, points and handles from a master UFO |
| `tools/readme_images.py` | The README images, dark and light |

`sources/` and `fonts/` are build output. Edit the Python, never the UFOs.

## Rules that keep the font valid

- **Every primitive emits a fixed number of points**, whatever its parameters, so the masters interpolate. Arc sweeps must stay in the same 90 degree band across masters, or fontmake fails its compatibility check.
- **Never let two contours share an exact edge.** Antialiasing shows a hairline seam. Overlap them by a few units instead.
- **Arcs and rings raise if the stroke is thicker than the curve.** Size small curves from their stroke, not the other way round.
- **Spacing is measured on the dream state** (`LUCD 0`), so wedges hang into the gap the way serifs do. A glyph whose shape changes width with Lucidity will collide.
- **Proof only in Chromium.** Pillow and some previewers render overlapping contours wrongly.
- **Check the exit status of `build.py`.** Piping it into `tail` hides a failed build.

## Workflow

```sh
.venv/bin/python tools/build.py && echo ok
.venv/bin/python tools/proof.py /tmp/p.png --size 200 --axes "900,100;400,0;100,100" "Hamburgefonts"
.venv/bin/python tools/inspect_glyph.py /tmp/g.png sources/masters/Oneira-wght900-LUCD100.ufo germandbls
.venv/bin/python tools/build.py --release
.venv/bin/fontbakery check-universal 'fonts/variable/Oneira[LUCD,wght].ttf'
```

Look at Black and Thin, at both ends of Lucidity, at a large size, before calling a glyph done. Black is where most problems show.

## Writing

No em dashes in any text that ships: README, specimens, commit messages.
