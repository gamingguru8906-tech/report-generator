"""Design themes for the Personal Year Forecast, one per Mulank (psychic number 1-9).

Every page is built from colour roles (named after the first theme, Rosette: PINK, LBLUE, CREAM, NAVY, COBALT,
BERRY, GREEN, ORANGE ...), a display face, a reading face, a paper texture and a "look" (looks.py) that draws the
theme's own shapes, marks, plates, page frame, footer and cover.

Light roles (PINK, LBLUE, CREAM, ORANGE, WHITE) carry dark ink; dark roles (NAVY, COBALT, BERRY, GREEN) carry
white text. Each theme keeps that contract, so every page reads in every theme.

Owner's mapping (18 Oct 2026): Mulank 1 Dabba, 2 Broadcast Cookbook, 4 Torn, 7 Contour Stack, 8 Daktilo
Dispatch; every other Mulank gets Rosette, the base design.
"""
import os

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def _f(family, *faces):
    """faces: (file, weight, style)"""
    return {"family": family, "files": list(faces)}


ROSETTE = {
    "id": "rosette", "label": "Rosette", "look": "Rosette",
    "PINK": "#F68EEA", "LBLUE": "#98CDFF", "CREAM": "#EFEDEA", "NAVY": "#394B71",
    "COBALT": "#4B6DD9", "BERRY": "#A54476", "GREEN": "#41724B", "ORANGE": "#F2784B",
    "INK": "#353535", "DEEP": "#1F2B4A", "BERRY_D": "#6C2D4D", "WHITE": "#FFFFFF",
    "CTA": "#C2410C", "CARE": "#B4471E", "RULE": "#F68EEA", "TH_BG": "#98CDFF", "TH_FG": "#1F2B4A",
    "display": _f("Savate", ("Savate-450.ttf", 450, "normal"), ("Savate-640.ttf", 640, "normal"),
                  ("Savate-700.ttf", 700, "normal"), ("Savate-Italic-380.ttf", 380, "italic")),
    "body": _f("Albert", ("Albert-400.ttf", 400, "normal"), ("Albert-600.ttf", 600, "normal"),
               ("Albert-700.ttf", 700, "normal"), ("Albert-Italic-400.ttf", 400, "italic")),
    "extra_fonts": [],
    "type": {"disp_w": 450, "disp_bw": 640, "plate_w": 700, "num_w": 450, "case": "none", "track": "-.005em",
             "lh": ".98", "scale": 1.0, "it_family": None, "it_w": 380, "it_style": "italic",
             "caps_family": None, "caps_w": 600},
    "grain": "grain.png", "grain_size": 110, "square": False,
}

# Mulank 8: an investigative case file. Cream manila folders on a black ground, heavy geometric capitals,
# typewritten memo copy, hairline ledgers. Black is the only accent.
DAKTILO = {
    "id": "daktilo", "label": "Daktilo Dispatch", "look": "Daktilo",
    "PINK": "#EEE8E1", "LBLUE": "#E4DED6", "CREAM": "#FFFAF6", "NAVY": "#151617",
    "COBALT": "#151617", "BERRY": "#2C2C2F", "GREEN": "#3B3B3E", "ORANGE": "#D8D1C7",
    "INK": "#151617", "DEEP": "#151617", "BERRY_D": "#151617", "WHITE": "#FFFFFF",
    "CTA": "#151617", "CARE": "#151617", "RULE": "#151617", "TH_BG": "#151617", "TH_FG": "#FFFAF6",
    "display": _f("Montserrat", ("montserrat-latin-700-normal.woff2", 700, "normal"),
                  ("montserrat-latin-800-normal.woff2", 800, "normal")),
    "body": _f("Inconsolata", ("inconsolata-latin-400-normal.woff2", 400, "normal"),
               ("inconsolata-latin-600-normal.woff2", 600, "normal"), ("inconsolata-latin-700-normal.woff2", 700, "normal")),
    "extra_fonts": [],
    "type": {"disp_w": 800, "disp_bw": 800, "plate_w": 800, "num_w": 800, "case": "uppercase", "track": "-.01em",
             "lh": ".92", "scale": 0.86, "it_family": "Inconsolata", "it_w": 400, "it_style": "normal",
             "caps_family": "Inconsolata", "caps_w": 600},
    "grain": "paper-soft.png", "grain_size": 256, "square": True,
}

# Mulank 1: a warm field with colour in pairs. Square flat plates, one oversized lowercase word against the
# edge, small serif print opposite.
DABBA = {
    "id": "dabba", "label": "Dabba", "look": "Dabba",
    "PINK": "#F2B4C2", "LBLUE": "#93C5D6", "CREAM": "#FFF2DD", "NAVY": "#3B2416",
    "COBALT": "#16505C", "BERRY": "#7A1F4A", "GREEN": "#3F7A47", "ORANGE": "#F2B632",
    "INK": "#3B2416", "DEEP": "#2C1A0F", "BERRY_D": "#6E0D46", "WHITE": "#FFF9EE",
    "CTA": "#16505C", "CARE": "#9A3412", "RULE": "#3B2416", "TH_BG": "#3B2416", "TH_FG": "#FFF2DD",
    "display": _f("Bagel", ("bagel-fat-one-latin-400-normal.woff2", 400, "normal")),
    "body": _f("SourceSerif", ("source-serif-4-latin-400-normal.woff2", 400, "normal"),
               ("source-serif-4-latin-600-normal.woff2", 600, "normal"), ("source-serif-4-latin-400-italic.woff2", 400, "italic")),
    "extra_fonts": [],
    "type": {"disp_w": 400, "disp_bw": 400, "plate_w": 400, "num_w": 400, "case": "none", "track": "-.02em",
             "lh": ".98", "scale": 0.92, "it_family": "SourceSerif", "it_w": 400, "it_style": "italic",
             "caps_family": "Bagel", "caps_w": 400},
    "grain": "grain.png", "grain_size": 110, "square": True,
}

# Mulank 2: a printed cookbook object. Plum, mustard and cream fields; blunt soft-serif capitals with a shallow
# offset shadow, crossed by one looping script phrase; Bodoni titles; tracked tab labels.
BROADCAST = {
    "id": "broadcast", "label": "Broadcast Cookbook", "look": "Broadcast",
    "PINK": "#F6DFA8", "LBLUE": "#BFD691", "CREAM": "#FBF4E6", "NAVY": "#3B1430",
    "COBALT": "#5A1F45", "BERRY": "#B83A1F", "GREEN": "#2A1610", "ORANGE": "#EBA42A",
    "INK": "#2A1610", "DEEP": "#2A1610", "BERRY_D": "#3B1430", "WHITE": "#FFFCF5",
    "CTA": "#B83A1F", "CARE": "#B83A1F", "RULE": "#D9C49A", "TH_BG": "#3B1430", "TH_FG": "#FBF4E6",
    "display": _f("Bodoni", ("bodoni-moda-latin-400-normal.woff2", 400, "normal"), ("bodoni-moda-latin-600-normal.woff2", 600, "normal"),
                  ("bodoni-moda-latin-400-italic.woff2", 400, "italic")),
    "body": _f("Newsreader", ("newsreader-latin-400-normal.woff2", 400, "normal"), ("newsreader-latin-600-normal.woff2", 600, "normal"),
               ("newsreader-latin-400-italic.woff2", 400, "italic")),
    "extra_fonts": [_f("Corben", ("corben-latin-700-normal.woff2", 700, "normal"), ("corben-latin-400-normal.woff2", 400, "normal")),
                    _f("Ballet", ("ballet-latin-400-normal.woff2", 400, "normal")),
                    _f("Rethink", ("rethink-sans-latin-600-normal.woff2", 600, "normal"), ("rethink-sans-latin-700-normal.woff2", 700, "normal"))],
    "type": {"disp_w": 400, "disp_bw": 600, "plate_w": 700, "num_w": 400, "case": "none", "track": "-.01em",
             "lh": "1.0", "scale": 0.96, "it_family": "Newsreader", "it_w": 400, "it_style": "italic",
             "caps_family": "Rethink", "caps_w": 600},
    "grain": "grain.png", "grain_size": 110, "square": True,
}

# Mulank 4: a tactile torn-paper collage. Kraft, dusty blue, rose and cream papers with torn white edges,
# compressed tabloid capitals, literary serif copy.
TORN = {
    "id": "torn", "label": "Torn", "look": "Torn",
    "PINK": "#DDB1A9", "LBLUE": "#A8B8CC", "CREAM": "#EEE7D7", "NAVY": "#1C1D20",
    "COBALT": "#4A5C7A", "BERRY": "#7A4842", "GREEN": "#4A4F3E", "ORANGE": "#E2C541",
    "INK": "#141416", "DEEP": "#141416", "BERRY_D": "#5A2F2B", "WHITE": "#F7F3EA",
    "CTA": "#7A4842", "CARE": "#7A4842", "RULE": "#8C7A62", "TH_BG": "#1C1D20", "TH_FG": "#EEE7D7",
    "KRAFT": "#C6A47C",
    "display": _f("Anton", ("anton-latin-400-normal.woff2", 400, "normal")),
    "body": _f("Newsreader", ("newsreader-latin-500-normal.woff2", 400, "normal"), ("newsreader-latin-600-normal.woff2", 600, "normal"),
               ("newsreader-latin-400-italic.woff2", 400, "italic")),
    "extra_fonts": [_f("Franklin", ("libre-franklin-latin-600-normal.woff2", 600, "normal"), ("libre-franklin-latin-700-normal.woff2", 700, "normal"))],
    "type": {"disp_w": 400, "disp_bw": 400, "plate_w": 400, "num_w": 400, "case": "none", "track": "0",
             "lh": "1.0", "scale": 1.04, "it_family": "Newsreader", "it_w": 400, "it_style": "italic",
             "caps_family": "Franklin", "caps_w": 600},
    "grain": "paper-torn.png", "grain_size": 256, "square": True,
}

# Mulank 7: tabletop landscapes of stacked contour-cut paper. Yellow paper, greens and a warm red, compressed
# capitals over a friendly sans, rounded layer tags, plateau plates.
CONTOUR = {
    "id": "contour", "label": "Contour Stack", "look": "Contour",
    "PINK": "#FBF5DA", "LBLUE": "#C4DE8E", "CREAM": "#F5ECC2", "NAVY": "#1F2A14",
    "COBALT": "#3E6A21", "BERRY": "#B8462A", "GREEN": "#4E7C22", "ORANGE": "#EE8059",
    "INK": "#1F2A14", "DEEP": "#1F2A14", "BERRY_D": "#7A2A14", "WHITE": "#FCF8E6",
    "CTA": "#B8462A", "CARE": "#B8462A", "RULE": "#9CC163", "TH_BG": "#AFD472", "TH_FG": "#1F2A14",
    "display": _f("Smooch", ("smooch-sans-latin-900-normal.woff2", 900, "normal"), ("smooch-sans-latin-800-normal.woff2", 800, "normal")),
    "body": _f("Rubik", ("rubik-latin-400-normal.woff2", 400, "normal"), ("rubik-latin-500-normal.woff2", 500, "normal"),
               ("rubik-latin-700-normal.woff2", 700, "normal")),
    "extra_fonts": [],
    "type": {"disp_w": 900, "disp_bw": 900, "plate_w": 900, "num_w": 900, "case": "uppercase", "track": ".005em",
             "lh": ".9", "scale": 1.22, "it_family": "Rubik", "it_w": 500, "it_style": "normal",
             "caps_family": "Rubik", "caps_w": 500},
    "grain": "paper-soft.png", "grain_size": 256, "square": False,
}

THEMES = {t["id"]: t for t in (ROSETTE, DAKTILO, DABBA, BROADCAST, TORN, CONTOUR)}

# Mulank -> theme id (owner's choice). Any Mulank not listed gets Rosette.
THEME_FOR_MULANK = {1: "dabba", 2: "broadcast", 4: "torn", 7: "contour", 8: "daktilo"}


def theme_for(mulank):
    return THEMES[THEME_FOR_MULANK.get(int(mulank), "rosette")]
