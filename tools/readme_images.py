"""README images, rendered by headless Chromium from the variable font.
usage: readme_images.py [OUTDIR]   (default docs/images)
Writes NAME-dark.png and NAME-light.png for each panel. Backgrounds are
transparent and the ink matches GitHub's text colours, so each image sits on
the page in either theme with no frame."""

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
    "dark": {"fg": "#e6edf3", "dim": "#9198a1"},
    "light": {"fg": "#1f2328", "dim": "#59636e"},
}


def v(w, l):
    return f"font-variation-settings:'wght' {w},'LUCD' {l}"


def hero():
    word = "Oneira"
    letters = "".join(f'<span style="{v(820, round(100 * i / (len(word) - 1)))}">{c}</span>'
                      for i, c in enumerate(word))
    return 420, f"<div class=hero>{letters}</div>"


def weight():
    cells = "".join(f'<div><div class=wg style="{v(w, 100)}">Ag</div><div class=lab>{w}</div></div>'
                    for w in range(100, 1000, 100))
    return 300, f"<div class=wrow>{cells}</div>"


def lucidity():
    cells = "".join(f'<div><div class=lg style="{v(800, l)}">ri&rsquo;s</div><div class=lab>{l}</div></div>'
                    for l in (0, 25, 50, 75, 100))
    return 360, f"<div class=lrow>{cells}</div>"


def rule():
    return 440, f"""
<div class=pair>
  <div><div class=rbig style="{v(900, 0)}">nij&rsquo;s</div><div class=lab>Dream, round ends</div></div>
  <div><div class=rbig style="{v(900, 100)}">nij&rsquo;s</div><div class=lab>Lucid, triangles</div></div>
</div>"""


def text():
    para = ("The night was quiet. Above the river, twenty-four lanterns drifted toward the hills, "
            "small and bright and patient. Whoever dreams them keeps the light, and whoever wakes "
            "remembers only the shape of it: a point, a curve, a triangle at every end.")
    return 620, f"""
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
    return 560, body


PANELS = {"hero": hero, "weight": weight, "lucidity": lucidity, "rule": rule,
          "text": text, "charset": charset}

CSS = """
@font-face{{font-family:O;src:url('file://{vf}')}}
*{{margin:0;box-sizing:border-box}}
html,body{{background:transparent}}
body{{width:{w}px;height:{h}px;color:{fg};font-family:O;padding:40px 8px;
  display:flex;flex-direction:column;overflow:hidden;font-kerning:normal}}
.lab{{font-size:40px;margin-top:8px;color:{dim};{lab}}}
.hero{{font-size:400px;line-height:1;letter-spacing:-0.025em;margin:auto 0 0 -12px}}
.wrow{{display:grid;grid-template-columns:repeat(9,1fr);flex:1;align-items:end}}
.wg{{font-size:96px;line-height:1.3;letter-spacing:-0.02em}}
.lrow{{display:grid;grid-template-columns:repeat(5,1fr);flex:1;align-items:end}}
.lg{{font-size:168px;line-height:1.2;letter-spacing:-0.02em}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:48px;flex:1;align-items:end}}
.rbig{{font-size:250px;line-height:1.05;letter-spacing:-0.02em;margin-bottom:18px}}
.t1{{font-size:104px;line-height:1.05;letter-spacing:-0.02em;margin-bottom:40px}}
.t2{{font-size:38px;line-height:1.45;margin-bottom:36px}}
.t3{{font-size:30px;line-height:1.55;color:{dim}}}
.cs{{font-size:60px;line-height:1.42;letter-spacing:0.01em;white-space:nowrap}}
"""


def render(name, theme, out):
    h, body = PANELS[name]()
    t = THEMES[theme]
    css = CSS.format(vf=VF, w=W, h=h, lab=v(500, 100), **t)
    TMP.mkdir(exist_ok=True)
    page = TMP / f"readme-{name}-{theme}.html"
    page.write_text(f"<html><head><style>{css}</style></head><body>{body}</body></html>")
    subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--default-background-color=00000000",
                    f"--user-data-dir={TMP / 'ud'}", f"--screenshot={out.resolve()}",
                    f"--window-size={W},{h}", "--allow-file-access-from-files", f"file://{page}"],
                   capture_output=True, check=True)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "images"
    out.mkdir(parents=True, exist_ok=True)
    for name in PANELS:
        for theme in THEMES:
            render(name, theme, out / f"{name}-{theme}.png")
    print("wrote", len(PANELS) * len(THEMES), "images to", out)


if __name__ == "__main__":
    main()
