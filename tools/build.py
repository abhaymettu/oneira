"""Draw the masters, write the designspace, compile the variable font.
usage: python tools/build.py [--no-compile] [--release]
--release also writes static instances (overlaps removed) and WOFF2 files."""

import shutil
import subprocess
import sys
from pathlib import Path

import ufoLib2
from fontTools.designspaceLib import (AxisDescriptor, AxisLabelDescriptor, DesignSpaceDocument, InstanceDescriptor,
                                      SourceDescriptor)
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).parent))
from oneira import figures, kerning, latin1, lower, marks, punct, symbols, upper  # noqa: E402,F401  (registers glyphs)
from oneira.params import ASC, CAP, COMPOSITES, DESC, GLYPHS, UPM, XH, P, build, mark_offset  # noqa: E402
from ufoLib2.objects import Component  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
FAMILY = "Oneira"
WEIGHTS = (100, 400, 900)
LUCIDITY = (0, 100)
VF = ROOT / "fonts" / "variable" / f"{FAMILY}[LUCD,wght].ttf"
NAMES = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
         600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
FAMILIES = {100: FAMILY, 0: f"{FAMILY} Dream"}  # static families, one per end of Lucidity
# where each named weight sits between the masters, so the grey of running
# text darkens by equal steps on each side of Regular (tools/ramp.py --solve)
WGHT_MAP = {100: 100, 200: 194, 300: 294, 400: 400, 500: 490, 600: 585, 700: 684, 800: 789, 900: 900}


def notdef(f):
    g = f.newGlyph(".notdef")
    g.width = 500
    pen = g.getPen()
    for c in ([(50, 0), (450, 0), (450, 700), (50, 700)], [(90, 40), (90, 660), (410, 660), (410, 40)]):
        pen.moveTo(c[0])
        for pt in c[1:]:
            pen.lineTo(pt)
        pen.closePath()


def master(wght, lucd):
    t, w = (wght - 100) / 800, lucd / 100
    f = ufoLib2.Font()
    i = f.info
    i.familyName = FAMILY
    i.styleName = "Regular" if (wght, lucd) == (400, 100) else f"wght{wght} LUCD{lucd}"
    i.unitsPerEm, i.ascender, i.descender = UPM, ASC, DESC
    i.capHeight, i.xHeight = CAP, XH
    i.versionMajor, i.versionMinor = 0, 200
    i.copyright = "Copyright 2026 The Oneira Project Authors (https://github.com/abhaymettu/oneira)"
    i.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                             "This license is available with a FAQ at: https://openfontlicense.org")
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1100, 300  # clears the tallest accented capital at Black
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = 960, -260, 0
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = 960, -260, 0
    i.openTypeOS2WeightClass = wght
    f.glyphOrder = [".notdef"] + list(GLYPHS) + list(COMPOSITES)
    notdef(f)
    ink = {}
    for name, (uni, *_) in GLYPHS.items():
        shape, adv = build(name, t, w)
        g = f.newGlyph(name)
        if uni is not None:
            g.unicodes = [uni]
        g.width = round(adv)
        shape.draw(g.getPen())
        ink[name] = shape.xbounds() if shape.contours else (0, 0)
    p = P(t, w)
    for name, (uni, base, marks) in COMPOSITES.items():
        g = f.newGlyph(name)
        g.unicodes = [uni]
        if base is None:  # a spacing mark: the mark alone, centred in its own advance
            x0, x1 = ink[marks[0][0]]
            g.width = round(x1 - x0 + 2 * p.W(70, 60))
            cx = g.width / 2
        else:
            # a mark wider than its base (I, dotless i) widens the glyph so it
            # never runs into the neighbours
            widest = max(ink[m][1] - ink[m][0] for m, _ in marks)
            pad = max(0.0, (widest + 2 * p.W(36, 30) - f[base].width) / 2)
            g.width = round(f[base].width + 2 * pad)
            g.components.append(Component(baseGlyph=base, transformation=(1, 0, 0, 1, round(pad), 0)))
            cx = sum(ink[base]) / 2 + round(pad)
        for mark, anchor in marks:
            g.components.append(Component(baseGlyph=mark, transformation=(1, 0, 0, 1,
                                                                          round(cx), round(mark_offset(anchor, p)))))
    f.groups.update(kerning.groups())
    f.kerning.update(kerning.kerning(t, w))
    return f


def main():
    if SRC.exists():
        shutil.rmtree(SRC)
    (SRC / "masters").mkdir(parents=True)
    ds = DesignSpaceDocument()
    wght_axis = AxisDescriptor(tag="wght", name="Weight", minimum=100, default=400, maximum=900)
    wght_axis.axisLabels = [AxisLabelDescriptor(name=n, userValue=v, elidable=v == 400) for v, n in NAMES.items()]
    wght_axis.map = list(WGHT_MAP.items())
    lucd_axis = AxisDescriptor(tag="LUCD", name="Lucidity", minimum=0, default=100, maximum=100)
    lucd_axis.axisLabels = [AxisLabelDescriptor(name="Dream", userValue=0),
                            AxisLabelDescriptor(name="Lucid", userValue=100, elidable=True)]
    ds.addAxis(wght_axis)
    ds.addAxis(lucd_axis)
    for wght in WEIGHTS:
        for lucd in LUCIDITY:
            name = f"{FAMILY}-wght{wght}-LUCD{lucd}.ufo"
            master(wght, lucd).save(SRC / "masters" / name)
            ds.addSource(SourceDescriptor(filename=f"masters/{name}", familyName=FAMILY,
                                          styleName="Regular" if (wght, lucd) == (400, 100) else f"wght{wght} LUCD{lucd}",
                                          location={"Weight": wght, "Lucidity": lucd}))
    # the variable font names its instances "Bold", "Dream Bold"; the static
    # families are "Oneira" and "Oneira Dream", so they get their own document
    static = DesignSpaceDocument.fromstring(ds.tostring())
    for lucd, fam in FAMILIES.items():
        for wght, style in NAMES.items():
            loc = {"Weight": wght, "Lucidity": lucd}
            vf_style = style if lucd == 100 else ("Dream" if style == "Regular" else f"Dream {style}")
            ds.addInstance(InstanceDescriptor(familyName=FAMILY, styleName=vf_style, userLocation=loc))
            ps = f"{fam.replace(' ', '')}-{style}"
            static.addInstance(InstanceDescriptor(
                familyName=fam, styleName=style, postScriptFontName=ps,
                styleMapFamilyName=fam if style in ("Regular", "Bold") else f"{fam} {style}",
                styleMapStyleName="bold" if style == "Bold" else "regular",
                userLocation=loc, filename=f"instances/{ps}.ufo"))
    ds.write(SRC / f"{FAMILY}.designspace")
    static.write(SRC / f"{FAMILY}-static.designspace")
    print(f"{len(GLYPHS) + len(COMPOSITES)} glyphs x {len(WEIGHTS) * len(LUCIDITY)} masters")
    if "--no-compile" in sys.argv:
        return
    VF.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(ROOT / ".venv/bin/fontmake"), "-m", str(SRC / f"{FAMILY}.designspace"),
                        "-o", "variable", "--output-path", str(VF)], capture_output=True, text=True)
    errs = [ln for ln in (r.stdout + r.stderr).splitlines() if "ERROR" in ln or "Error" in ln or "rror:" in ln]
    if r.returncode:
        print("\n".join(errs[-20:]) or r.stderr[-2000:])
        sys.exit(1)
    finish(VF)
    print("built", VF.relative_to(ROOT))
    if "--release" in sys.argv:
        release()


def finish(path):
    """Unhinted fonts still ask rasterizers for smart dropout control, and
    smooth rendering at every size."""
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables import ttProgram
    f = TTFont(path)
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    f["prep"] = prep
    gasp = newTable("gasp")
    gasp.version, gasp.gaspRange = 1, {0xFFFF: 15}
    f["gasp"] = gasp
    f.save(path)


def drop_repeated_points(path):
    """Removing overlaps and rounding to whole units leaves a few points on
    top of the point before them, or a one unit spike out and back. A static
    font never interpolates, so they can go."""
    f = TTFont(path)
    glyf = f["glyf"]
    for name in glyf.keys():
        g = glyf[name]
        if g.isComposite() or g.numberOfContours <= 0:
            continue
        coords, ends, flags = g.getCoordinates(glyf)
        pts, new_ends, new_flags, start = [], [], [], 0
        for end in ends:
            contour = list(zip(coords[start:end + 1], flags[start:end + 1]))
            kept = []
            for pt, fl in contour:
                if kept and tuple(pt) == tuple(kept[-1][0]):
                    if fl & 1:  # keep the on-curve one of the pair
                        kept[-1] = (pt, fl)
                    continue
                if len(kept) > 1 and tuple(pt) == tuple(kept[-2][0]):  # out one unit and back
                    kept.pop()
                    continue
                kept.append((pt, fl))
            while len(kept) > 1 and tuple(kept[0][0]) == tuple(kept[-1][0]):
                last = kept.pop()
                if last[1] & 1:
                    kept[0] = last
            if len(kept) >= 3:
                pts += [p for p, _ in kept]
                new_flags += [fl for _, fl in kept]
                new_ends.append(len(pts) - 1)
            start = end + 1
        g.coordinates = type(coords)(pts)
        g.flags = bytearray(new_flags)
        g.endPtsOfContours = new_ends
        g.numberOfContours = len(new_ends)
        g.recalcBounds(glyf)
    f.save(path)


def release():
    static = ROOT / "fonts" / "static"
    if static.exists():
        shutil.rmtree(static)
    r = subprocess.run([str(ROOT / ".venv/bin/fontmake"), "-m", str(SRC / f"{FAMILY}-static.designspace"),
                        "-i", "-o", "ttf", "--output-dir", str(static)], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(1)
    shutil.rmtree(SRC / "instances", ignore_errors=True)
    for ttf in static.glob("*.ttf"):
        drop_repeated_points(ttf)
        finish(ttf)
    web = ROOT / "fonts" / "webfonts"
    web.mkdir(parents=True, exist_ok=True)
    for ttf in [VF, *sorted(static.glob("*.ttf"))]:
        f = TTFont(ttf)
        f.flavor = "woff2"
        f.save(web / (ttf.stem + ".woff2"))
    print(f"static {len(list(static.glob('*.ttf')))} + woff2 in fonts/")


if __name__ == "__main__":
    main()
