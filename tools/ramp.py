"""The weight ramp, measured as the grey of running text.
usage: ramp.py [--solve]
Prints each named weight's coverage (ink over a line box) and its CIE L*
(paper 100), and the step from the weight before. --solve ignores the
font's avar and prints the WGHT_MAP for build.py that makes the steps
equal on each side of Regular (Regular sits on its master)."""

import sys
from pathlib import Path

import pathops
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
VF = ROOT / "fonts" / "variable" / "Oneira[LUCD,wght].ttf"
TEXT = "Hamburgefontsiv The quick brown fox jumps over the lazy dog nnonnoon"
LINE = 1220  # line box height in units: ascender to descender


def lightness(vf, wght, keep_avar=True):
    """L* of TEXT at a weight, averaged over both ends of Lucidity."""
    total = 0.0
    for lucd in (0, 100):
        f = TTFont(vf)
        if not keep_avar and "avar" in f:
            del f["avar"]
        f = instancer.instantiateVariableFont(f, {"wght": wght, "LUCD": lucd})
        cmap, gs, hm = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
        ink = {}
        for name in {cmap[ord(c)] for c in TEXT if c != " "}:
            path = pathops.Path()
            gs[name].draw(pathops.PathPen(path, gs))
            path.simplify(fix_winding=True)  # overlapping contours count once
            ink[name] = abs(path.area)
        area = sum(ink[cmap[ord(c)]] for c in TEXT if c != " ")
        cover = area / (sum(hm[cmap[ord(c)]][0] for c in TEXT) * LINE)
        total += 116 * (1 - cover) ** (1 / 3) - 16
    return total / 2


def solve(vf):
    L = lambda d: lightness(vf, d, keep_avar=False)
    l100, l400, l900 = L(100), L(400), L(900)
    goal = {200: l100 + (l400 - l100) / 3, 300: l100 + 2 * (l400 - l100) / 3}
    goal.update({400 + 100 * i: l400 + i * (l900 - l400) / 5 for i in range(1, 5)})
    out = {100: 100, 400: 400, 900: 900}
    for user, target in goal.items():
        lo, hi = (100, 400) if user < 400 else (400, 900)
        for _ in range(16):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if L(mid) > target else (lo, mid)
        out[user] = round((lo + hi) / 2)
    print("WGHT_MAP =", dict(sorted(out.items())))


def main():
    if "--solve" in sys.argv:
        solve(VF)
        return
    prev, steps = None, []
    for wght in range(100, 1000, 100):
        L = lightness(VF, wght)
        step = "" if prev is None else f"  step {prev - L:.2f}"
        if prev is not None:
            steps.append(prev - L)
        print(f"{wght}: L* {L:.2f}{step}")
        prev = L
    light, heavy = steps[:3], steps[3:]
    print(f"steps max/min: Thin to Regular {max(light) / min(light):.3f}, "
          f"Regular to Black {max(heavy) / min(heavy):.3f}, all {max(steps) / min(steps):.3f}")


if __name__ == "__main__":
    main()
