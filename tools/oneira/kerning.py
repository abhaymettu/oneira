"""Class kerning. Values are set at Regular and scale with weight; accented
composites join the classes of their base letter."""

from .geom import lerp
from .params import COMPOSITES

# first glyph, grouped by its right side
LEFT = {
    "T": ["T"],
    "V": ["V"],
    "W": ["W"],
    "Y": ["Y", "yen"],
    "A": ["A"],
    "L": ["L"],
    "P": ["P", "Thorn"],
    "F": ["F"],
    "K": ["K", "X"],
    "r": ["r"],
    "v": ["v", "w", "y"],
    "f": ["f"],
    "round": ["o", "b", "p", "thorn", "oslash", "e"],
    "c": ["c"],  # its lower tip reaches for the comma at lucid
    "kx": ["k", "x"],  # wedges at the x-height, like v
    "quote": ["quoteright", "quotedblright", "quoteleft", "quotedblleft", "quotesingle", "quotedbl"],
    "stop": ["period", "comma", "ellipsis", "quotesinglbase", "quotedblbase"],
    "dash": ["hyphen", "uni00AD", "endash", "emdash"],
    "desc": ["g", "q", "j", "Q"],  # something under the baseline on the right, where j's hook hangs
    "open": ["parenleft", "bracketleft", "braceleft"],
}

# second glyph, grouped by its left side
RIGHT = {
    "T": ["T"],
    "V": ["V"],
    "W": ["W"],
    "Y": ["Y"],
    "A": ["A", "AE"],
    "O": ["O", "C", "G", "Q", "Oslash"],
    "J": ["J"],
    "o": ["o", "c", "d", "e", "q", "g", "a", "s", "oslash", "ae", "eth"],
    "n": ["m", "n", "p", "r", "u", "mu", "dotlessi", "z", "x"],
    "v": ["v", "w", "y"],
    "j": ["j"],
    "quote": ["quoteright", "quotedblright", "quoteleft", "quotedblleft", "quotesingle", "quotedbl"],
    "stop": ["period", "comma", "ellipsis"],
    "dash": ["hyphen", "uni00AD", "endash", "emdash"],
}

# (left class, right class): kern at Regular, or (Thin, Black) where the
# need grows faster than the weight, as with hooks that collide
PAIRS = {
    ("T", "o"): -88, ("T", "n"): -66, ("T", "v"): -56, ("T", "A"): -66, ("T", "J"): -50,
    ("T", "stop"): -96, ("T", "dash"): -64, ("T", "O"): -12,
    ("V", "o"): -62, ("V", "n"): -40, ("V", "v"): -24, ("V", "A"): -64, ("V", "J"): -44,
    ("V", "stop"): -96, ("V", "dash"): -40, ("V", "O"): -18,
    ("W", "o"): -48, ("W", "n"): -30, ("W", "v"): -16, ("W", "A"): -50, ("W", "J"): -36,
    ("W", "stop"): -80, ("W", "dash"): -30, ("W", "O"): -12,
    ("Y", "o"): -96, ("Y", "n"): -64, ("Y", "v"): -44, ("Y", "A"): -78, ("Y", "J"): -60,
    ("Y", "stop"): -110, ("Y", "dash"): -72, ("Y", "O"): -28,
    ("A", "T"): -66, ("A", "V"): -64, ("A", "W"): -50, ("A", "Y"): -78, ("A", "v"): -40,
    ("A", "quote"): -84, ("A", "O"): -20, ("A", "o"): -10,
    ("L", "T"): -96, ("L", "V"): -84, ("L", "W"): -64, ("L", "Y"): -96, ("L", "v"): -50,
    ("L", "quote"): -120, ("L", "O"): -28, ("L", "dash"): -64,
    ("P", "A"): -62, ("P", "stop"): -120, ("P", "o"): -22, ("P", "J"): -46,
    ("F", "A"): -48, ("F", "stop"): -96, ("F", "o"): -26, ("F", "J"): -40,
    ("K", "O"): -30, ("K", "o"): -24, ("K", "dash"): -50, ("K", "v"): -30,
    ("T", "j"): -40, ("F", "j"): -34, ("P", "j"): -24, ("V", "j"): -30, ("Y", "j"): -40,
    ("desc", "j"): (110, 160), ("open", "j"): (110, 200),  # collisions: (Thin, Black)
    ("r", "stop"): -76, ("r", "o"): -10, ("r", "dash"): -30,
    ("v", "stop"): -64, ("v", "o"): -14, ("v", "dash"): -14,
    ("f", "quote"): 40, ("f", "stop"): -30, ("f", "o"): -8,
    ("round", "v"): -14, ("round", "stop"): -16, ("round", "quote"): -20,
    ("c", "v"): -14, ("c", "stop"): -16, ("c", "quote"): -20,
    ("quote", "A"): -84, ("quote", "o"): -40, ("quote", "J"): -60,
    ("stop", "T"): -96, ("stop", "V"): -96, ("stop", "W"): -80, ("stop", "Y"): -110,
    ("stop", "v"): -64, ("stop", "quote"): -110,
    ("dash", "T"): -64, ("dash", "V"): -40, ("dash", "W"): -30, ("dash", "Y"): -72, ("dash", "A"): -24,
}


def _expand(classes):
    out = {}
    for cls, names in classes.items():
        members = list(names)
        members += [c for c, (_, base, _m) in COMPOSITES.items() if base in names]
        out[cls] = members
    return out


def groups():
    g = {}
    for cls, names in _expand(LEFT).items():
        g[f"public.kern1.{cls}"] = names
    for cls, names in _expand(RIGHT).items():
        g[f"public.kern2.{cls}"] = names
    return g


# added at LUCD 100, (Thin, Black): pairs whose wedges or tips meet once
# the triangles grow in
LUCID = {
    ("v", "v"): (30, 12), ("kx", "v"): (30, 12), ("v", "x"): (30, 12), ("kx", "x"): (30, 12),
    ("r", "dash"): (0, 30), ("c", "stop"): (0, 18),
    ("desc", "j"): (-50, 0),  # the dream hook's round end reaches further
}


def kerning(t, w):
    """Pair values for weight t (0 Thin, 1 Black) and Lucidity w. Heavier
    weights fill their counters, so the same shapes need a little more kern."""
    k = lerp(0.88, 1.14, t)
    out = {}
    for (a, b), v in PAIRS.items():
        out[a, b] = lerp(*v, t) if isinstance(v, tuple) else v * k
    for (a, b), v in LUCID.items():
        out[a, b] = out.get((a, b), 0) + w * lerp(*v, t)
    # a name that is not a class is a glyph (x sits in the n class on its left)
    return {(f"public.kern1.{a}" if a in LEFT else a, f"public.kern2.{b}" if b in RIGHT else b): round(v)
            for (a, b), v in out.items()}
