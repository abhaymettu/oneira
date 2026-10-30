"""README images, rendered by headless Chromium from the variable font.
usage: readme_images.py [OUTDIR]   (default docs/images)
Writes NAME-dark.png and NAME-light.png for each panel."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VF = ROOT / "fonts" / "variable" / "Oneira[LUCD,wght].ttf"
CHROME = next(Path.home().glob(
    "Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
TMP = Path("/tmp/oneira-proof")
W = 1600

THEMES = {
    "dark": {"bg": "#0d0c12", "fg": "#ecebe6", "dim": "#7d7b88", "rule": "#24232c"},
    "light": {"bg": "#f4f2ec", "fg": "#141318", "dim": "#7a7882", "rule": "#dedbd2"},
}


def v(w, l):
    return f"font-variation-settings:'wght' {w},'LUCD' {l}"


def hero():
    word = "Oneira"
    letters = "".join(f'<span style="{v(820, round(100 * i / (len(word) - 1)))}">{c}</span>'
                      for i, c in enumerate(word))
    return 560, f"""
<div class=hero>{letters}</div>
<div class=foot><span>A variable typeface where every stroke ends in the same triangle</span>
<span>Lucidity 0 &rarr; 100</span></div>"""


def axes():
    cells = []
    for l in (0, 50, 100):
        for w in (100, 400, 900):
            cells.append(f'<div class=cell><div class=g style="{v(w, l)}">Ag</div>'
                         f'<div class=lab>wght {w} &middot; LUCD {l}</div></div>')
    return 1190, f"""
<div class=head><span>Two axes</span><span>Weight 100 to 900, Lucidity 0 (dream) to 100 (lucid)</span></div>
<div class=grid>{"".join(cells)}</div>"""


def rule():
    return 620, f"""
<div class=head><span>The one rule</span><span>Stems stand on wedges, curves end in tips, the dot is the triangle</span></div>
<div class=pair>
  <div><div class=rbig style="{v(900, 0)}">nij&rsquo;s</div><div class=lab>Dream &middot; LUCD 0 &middot; round caps</div></div>
  <div><div class=rbig style="{v(900, 100)}">nij&rsquo;s</div><div class=lab>Lucid &middot; LUCD 100 &middot; triangles</div></div>
</div>"""


def text():
    para = ("The night was quiet. Above the river, twenty-four lanterns drifted toward the hills, "
            "small and bright and patient. Whoever dreams them keeps the light, and whoever wakes "
            "remembers only the shape of it: a point, a curve, a triangle at every end.")
    return 720, f"""
<div class=head><span>Text</span><span>Regular and Light at reading sizes, kerned</span></div>
<div class=t1 style="{v(700, 100)}">Lucid dreams at 3:40 a.m.</div>
<div class=t2 style="{v(400, 100)}">{para}</div>
<div class=t3 style="{v(300, 40)}">{para}</div>"""


def charset():
    rows = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz",
            "0123456789 &amp;@#%$&cent;&pound;&yen;&euro; &frac14;&frac12;&frac34; &sup1;&sup2;&sup3;",
            "&Agrave;&Aacute;&Acirc;&Atilde;&Auml;&Aring;&AElig;&Ccedil;&Egrave;&Eacute;&Ecirc;&Euml;"
            "&Igrave;&Iacute;&Icirc;&Iuml;&ETH;&Ntilde;&Ograve;&Oacute;&Ocirc;&Otilde;&Ouml;&Oslash;"
            "&Ugrave;&Uacute;&Ucirc;&Uuml;&Yacute;&THORN;",
            "&agrave;&aacute;&acirc;&atilde;&auml;&aring;&aelig;&ccedil;&egrave;&eacute;&ecirc;&euml;"
            "&igrave;&iacute;&icirc;&iuml;&eth;&ntilde;&ograve;&oacute;&ocirc;&otilde;&ouml;&oslash;"
            "&ugrave;&uacute;&ucirc;&uuml;&yacute;&thorn;&yuml;&szlig;",
            ".,:;&hellip;!?&iexcl;&iquest; &lsquo;&rsquo;&ldquo;&rdquo;&laquo;&raquo; ()[]{} "
            "+&minus;&times;&divide;=&plusmn;&lt;&gt; &copy;&reg;&sect;&para;&deg;&micro;"]
    body = "".join(f'<div class=cs style="{v(500, 100)}">{r}</div>' for r in rows)
    return 780, f"""<div class=head><span>Character set</span><span>Basic Latin and Latin-1, 218 glyphs</span></div>{body}"""


PANELS = {"hero": hero, "axes": axes, "rule": rule, "text": text, "charset": charset}

CSS = """
@font-face{{font-family:O;src:url('file://{vf}')}}
*{{margin:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;background:{bg};color:{fg};font-family:O;padding:72px 88px;
  display:flex;flex-direction:column;overflow:hidden;font-kerning:normal}}
.head{{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:22px;
  border-bottom:1px solid {rule};margin-bottom:28px;font-size:24px;{lab}}}
.head span:last-child{{color:{dim}}}
.lab{{font-size:19px;color:{dim};letter-spacing:0.01em;{lab}}}
.hero{{font-size:340px;line-height:1;letter-spacing:-0.025em;margin:auto 0 0 -14px}}
.foot{{display:flex;justify-content:space-between;margin-top:42px;padding-top:22px;
  border-top:1px solid {rule};font-size:24px;color:{dim};{lab}}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;flex:1}}
.cell{{border-top:1px solid {rule};padding:10px 0 28px}}
.cell:nth-child(-n+3){{border-top:0;padding-top:0}}
.g{{font-size:184px;line-height:1.36;letter-spacing:-0.02em}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:48px;flex:1;align-items:end}}
.rbig{{font-size:250px;line-height:1.05;letter-spacing:-0.02em;margin-bottom:18px}}
.t1{{font-size:96px;line-height:1.05;letter-spacing:-0.02em;margin-bottom:44px}}
.t2{{font-size:34px;line-height:1.5;max-width:1260px;margin-bottom:40px}}
.t3{{font-size:22px;line-height:1.6;max-width:980px;color:{dim}}}
.cs{{font-size:58px;line-height:1.42;letter-spacing:0.01em;white-space:nowrap}}
"""


def render(name, theme, out):
    h, body = PANELS[name]()
    t = THEMES[theme]
    css = CSS.format(vf=VF, w=W, h=h, lab=v(500, 100), **t)
    TMP.mkdir(exist_ok=True)
    page = TMP / f"readme-{name}-{theme}.html"
    page.write_text(f"<html><head><style>{css}</style></head><body>{body}</body></html>")
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--user-data-dir={TMP / 'ud'}",
                    f"--screenshot={out.resolve()}", f"--window-size={W},{h}",
                    "--allow-file-access-from-files", f"file://{page}"], capture_output=True, check=True)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "images"
    out.mkdir(parents=True, exist_ok=True)
    for name in PANELS:
        for theme in THEMES:
            render(name, theme, out / f"{name}-{theme}.png")
    print("wrote", len(PANELS) * len(THEMES), "images to", out)


if __name__ == "__main__":
    main()
