"""Draw the masters, write the designspace, compile the variable font.
usage: python tools/build.py [--no-compile]"""

import shutil
import subprocess
import sys
from pathlib import Path

import ufoLib2
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, SourceDescriptor

sys.path.insert(0, str(Path(__file__).parent))
from oneira import figures, latin1, lower, marks, punct, upper  # noqa: E402,F401  (registers glyphs)
from oneira.params import ASC, CAP, COMPOSITES, DESC, GLYPHS, UPM, XH, P, build, mark_offset  # noqa: E402
from ufoLib2.objects import Component  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
FAMILY = "Oneira"
WEIGHTS = (100, 400, 900)
LUCIDITY = (0, 100)
VF = ROOT / "fonts" / "variable" / f"{FAMILY}[LUCD,wght].ttf"


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
    i.familyName, i.styleName = FAMILY, f"wght{wght} LUCD{lucd}"
    i.unitsPerEm, i.ascender, i.descender = UPM, ASC, DESC
    i.capHeight, i.xHeight = CAP, XH
    i.versionMajor, i.versionMinor = 0, 200
    i.copyright = "Copyright 2026 The Oneira Project Authors (https://github.com/abhaymettu/oneira)"
    i.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                             "This license is available with a FAQ at: https://openfontlicense.org")
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1000, 300
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
    return f


def main():
    if SRC.exists():
        shutil.rmtree(SRC)
    (SRC / "masters").mkdir(parents=True)
    ds = DesignSpaceDocument()
    ds.addAxis(AxisDescriptor(tag="wght", name="Weight", minimum=100, default=400, maximum=900))
    ds.addAxis(AxisDescriptor(tag="LUCD", name="Lucidity", minimum=0, default=100, maximum=100))
    for wght in WEIGHTS:
        for lucd in LUCIDITY:
            name = f"{FAMILY}-wght{wght}-LUCD{lucd}.ufo"
            master(wght, lucd).save(SRC / "masters" / name)
            ds.addSource(SourceDescriptor(filename=f"masters/{name}", familyName=FAMILY,
                                          styleName=f"wght{wght} LUCD{lucd}",
                                          location={"Weight": wght, "Lucidity": lucd}))
    ds.write(SRC / f"{FAMILY}.designspace")
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
    print("built", VF.relative_to(ROOT))


if __name__ == "__main__":
    main()
