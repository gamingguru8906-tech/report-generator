"""
build_fonts.py — fetch & instance the brand fonts at build time.

The report uses Cinzel, Cormorant Garamond and Jost (all open-source, OFL).
Instead of committing .ttf binaries to GitHub, this script downloads the
variable fonts from the official Google Fonts repo and instances the exact
static weights the report needs into ./fonts/.

Run automatically on Render via the build command:
    pip install -r requirements.txt && python build_fonts.py

Safe to re-run: it skips work if every required file already exists.
"""
import os, urllib.request
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib import TTFont

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl"

SOURCES = {
    "Cinzel":          f"{RAW}/cinzel/Cinzel%5Bwght%5D.ttf",
    "Cormorant":       f"{RAW}/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
    "CormorantItalic": f"{RAW}/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf",
    "Jost":            f"{RAW}/jost/Jost%5Bwght%5D.ttf",
}

# (source key, weight, output filename) — exactly what the report registers
INSTANCES = [
    ("Cinzel", 700, "Cinzel-Bold.ttf"),
    ("Cinzel", 500, "Cinzel-Med.ttf"),
    ("Cormorant", 400, "Cormorant-Reg.ttf"),
    ("Cormorant", 500, "Cormorant-Med.ttf"),
    ("Cormorant", 600, "Cormorant-SemiBold.ttf"),
    ("CormorantItalic", 500, "Cormorant-Italic.ttf"),
    ("Jost", 400, "Jost-Reg.ttf"),
    ("Jost", 500, "Jost-Med.ttf"),
    ("Jost", 300, "Jost-Light.ttf"),
]

def main():
    os.makedirs(FONT_DIR, exist_ok=True)
    needed = [out for *_ , out in INSTANCES]
    if all(os.path.exists(os.path.join(FONT_DIR, f)) for f in needed):
        print("Fonts already present — nothing to do.")
        return

    # download the variable source fonts
    raw_dir = os.path.join(FONT_DIR, "_src")
    os.makedirs(raw_dir, exist_ok=True)
    src_paths = {}
    for key, url in SOURCES.items():
        dest = os.path.join(raw_dir, key + ".ttf")
        if not os.path.exists(dest):
            print("Downloading", key)
            urllib.request.urlretrieve(url, dest)
        src_paths[key] = dest

    # instance the static weights the report needs
    for key, wght, out in INSTANCES:
        outpath = os.path.join(FONT_DIR, out)
        if os.path.exists(outpath):
            continue
        f = TTFont(src_paths[key])
        instantiateVariableFont(f, {"wght": wght}, inplace=True)
        f.save(outpath)
        print("Built", out)

    print("All fonts ready in", FONT_DIR)

if __name__ == "__main__":
    main()
