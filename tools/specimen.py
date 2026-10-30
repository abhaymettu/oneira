"""Specimen sheets rendered by headless Chromium.
usage: specimen.py OUT.png [--sheet overview|axis|charset] [--theme dark|light]"""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VF = ROOT / "fonts" / "variable" / "Oneira[LUCD,wght].ttf"
CHROME = next(Path.home().glob(
    "Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
TMP = Path("/tmp/oneira-proof")

THEMES = {
    "dark": {"bg": "#0e0e13", "fg": "#ecebe6", "dim": "#8a8995", "rule": "#26252e"},
    "light": {"bg": "#f4f2ec", "fg": "#141318", "dim": "#77757f", "rule": "#dcd9d0"},
}


def v(w, l):
    return f"font-variation-settings:'wght' {w},'LUCD' {l}"


def overview():
    lucd = "".join(f'<span style="{v(500, l)}">s</span>' for l in range(0, 101, 10))
    weights = "".join(f'<div class=w style="{v(w, 100)}">Hamburgefonts<i>{w}</i></div>'
                      for w in (100, 300, 500, 700, 900))
    return f"""
<div class=hero style="{v(800, 100)}">Oneira</div>
<div class=sub>Every stroke ends in the same triangle. Lucidity takes it from dream to waking.</div>
<div class=row><div class=lab>LUCD 0 &rarr; 100</div><div class=axis>{lucd}</div></div>
<div class=pair>
  <div><div class=lab>Dream &middot; LUCD 0</div><div class=big style="{v(600, 0)}">Sweet dreams</div></div>
  <div><div class=lab>Lucid &middot; LUCD 100</div><div class=big style="{v(600, 100)}">Sweet dreams</div></div>
</div>
<div class=row><div class=lab>Weight 100 &rarr; 900</div><div>{weights}</div></div>
<div class=text style="{v(400, 100)}">The night was quiet. Above the river, 24 lanterns drifted toward
the hills, small and bright and patient. Whoever dreams them keeps the light: (ÀÉÎÕÜ) &amp; 98.6&deg;!</div>
<div class=chars style="{v(400, 100)}">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789 .,:;!?&lsquo;&rsquo;&ldquo;&rdquo;()[]{{}}@#$%&amp;*+=&lt;&gt;</div>
"""


def page(body, t, width):
    return f"""<html><head><style>
@font-face{{font-family:O;src:url('file://{VF}')}}
*{{box-sizing:border-box}}
body{{margin:0;padding:72px 80px;background:{t['bg']};color:{t['fg']};width:{width}px;font-family:O}}
.hero{{font-size:220px;line-height:1;letter-spacing:-2px}}
.sub{{font:22px/1.4 Menlo;color:{t['dim']};margin:18px 0 56px}}
.row{{border-top:1px solid {t['rule']};padding:28px 0}}
.lab{{font:13px Menlo;letter-spacing:.08em;text-transform:uppercase;color:{t['dim']};margin-bottom:14px}}
.axis{{font-size:150px;line-height:1;display:flex;justify-content:space-between}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:40px;border-top:1px solid {t['rule']};padding:28px 0}}
.big{{font-size:104px;line-height:1.05}}
.w{{font-size:64px;line-height:1.2}}
.w i{{font:13px Menlo;color:{t['dim']};margin-left:18px;font-style:normal}}
.text{{font-size:40px;line-height:1.35;border-top:1px solid {t['rule']};padding:32px 0;max-width:1500px}}
.chars{{font-size:48px;line-height:1.35;border-top:1px solid {t['rule']};padding:32px 0;color:{t['dim']}}}
</style></head><body>{body}</body></html>"""


def render(out, sheet="overview", theme="dark", width=1800, height=2600):
    TMP.mkdir(exist_ok=True)
    f = TMP / "specimen.html"
    f.write_text(page({"overview": overview}[sheet](), THEMES[theme], width))
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={TMP / 'ud'}", f"--screenshot={Path(out).resolve()}",
                    f"--window-size={width},{height}", "--allow-file-access-from-files", f"file://{f}"],
                   capture_output=True, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--sheet", default="overview")
    ap.add_argument("--theme", default="dark")
    ap.add_argument("--height", type=int, default=2600)
    a = ap.parse_args()
    render(a.out, a.sheet, a.theme, height=a.height)


if __name__ == "__main__":
    main()
