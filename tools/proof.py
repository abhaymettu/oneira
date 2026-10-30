"""Proof sheets rendered by headless Chromium (the renderer people will use).
usage: proof.py OUT.png [--size N] [--axes "wght,LUCD;wght,LUCD"] [--width PX] line [line ...]"""

import argparse
import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VF = ROOT / "fonts" / "variable" / "Oneira[LUCD,wght].ttf"
CHROME = next(Path.home().glob(
    "Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
TMP = Path("/tmp/oneira-proof")


def render(out, rows, size=120, width=2000, bg="#fff", fg="#000", label="#2a6bff"):
    """rows: list of (wght, lucd, text)."""
    TMP.mkdir(exist_ok=True)
    body = "".join(
        f'<div class=r><span class=l>{w} / {l}</span>'
        f'<span class=t style="font-variation-settings:\'wght\' {w},\'LUCD\' {l}">{html.escape(t)}</span></div>'
        for w, l, t in rows)
    page = f"""<html><head><style>
@font-face{{font-family:O;src:url('file://{VF}')}}
body{{margin:0;padding:24px 32px;background:{bg};color:{fg};width:{width - 64}px}}
.r{{display:flex;align-items:baseline;gap:24px;margin:0 0 {size * 0.18:.0f}px}}
.l{{font:14px Menlo;color:{label};width:90px;flex:none}}
.t{{font-family:O;font-size:{size}px;line-height:1.25;white-space:nowrap;font-kerning:normal}}
</style></head><body>{body}<div id=end></div></body></html>"""
    f = TMP / "proof.html"
    f.write_text(page)
    height = int(24 + len(rows) * size * 1.43 + 40)
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={TMP / 'ud'}", f"--screenshot={Path(out).resolve()}",
                    f"--window-size={width},{height}", "--allow-file-access-from-files", f"file://{f}"],
                   capture_output=True, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("lines", nargs="+")
    ap.add_argument("--size", type=int, default=120)
    ap.add_argument("--width", type=int, default=2000)
    ap.add_argument("--axes", default="100,100;400,100;900,100;400,0")
    a = ap.parse_args()
    axes = [tuple(int(v) for v in s.split(",")) for s in a.axes.split(";")]
    rows = [(w, l, t) for w, l in axes for t in a.lines]
    render(a.out, rows, a.size, a.width)


if __name__ == "__main__":
    main()
