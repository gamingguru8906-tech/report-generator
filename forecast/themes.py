"""Design themes for the Personal Year Forecast, one per Mulank (psychic number 1-9).

Every page is built from eight colour roles (named after the first theme, Rosette) plus a display face, a
reading face and a paper grain. A new design for a Mulank is a new entry here: give it its colours, fonts and
grain, and point THEME_FOR_MULANK at it. Until the owner's per-Mulank designs arrive, every Mulank uses
Rosette. The cover and the letter tell the reader that the edition is designed for their Mulank.
"""
import os

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

ROSETTE = {
    "id": "rosette",
    "label": "Rosette",
    # colour roles
    "PINK": "#F68EEA", "LBLUE": "#98CDFF", "CREAM": "#EFEDEA", "NAVY": "#394B71",
    "COBALT": "#4B6DD9", "BERRY": "#A54476", "GREEN": "#41724B", "ORANGE": "#F2784B",
    "INK": "#353535", "DEEP": "#1F2B4A", "BERRY_D": "#6C2D4D", "WHITE": "#FFFFFF",
    "CTA": "#C2410C",
    # type
    # static instances of the variable fonts at the weights the pages use (smaller PDFs, less printer memory)
    "display": {"family": "Savate", "files": [("Savate-450.ttf", 450, "normal"), ("Savate-640.ttf", 640, "normal"),
                                               ("Savate-700.ttf", 700, "normal"), ("Savate-Italic-380.ttf", 380, "italic")]},
    "body": {"family": "Albert", "files": [("Albert-400.ttf", 400, "normal"), ("Albert-600.ttf", 600, "normal"),
                                            ("Albert-700.ttf", 700, "normal"), ("Albert-Italic-400.ttf", 400, "italic")]},
    # texture
    "grain": "grain.png", "grain_size": 110,
}

THEMES = {"rosette": ROSETTE}

# Mulank -> theme id. Replace an entry when that Mulank's own design is added.
THEME_FOR_MULANK = {n: "rosette" for n in range(1, 10)}


def theme_for(mulank):
    return THEMES[THEME_FOR_MULANK.get(int(mulank), "rosette")]
