"""Veshann Astro — Branded PDF Report Generator
Renders the 25-page Premium Numerology Report in the Veshannastro design language.
Usage: build_report(result_dict, out_path, book_cover_path=None)
"""
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import Font
from reportlab.lib import fonts
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    PageBreak, Table, TableStyle, Flowable, KeepTogether, Image, NextPageTemplate)
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Drawing
import content as C
import numerology as N

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
def _reg(name, file, fallback="Times-Roman"):
    path = os.path.join(FONT_DIR, file)
    try:
        pdfmetrics.registerFont(TTFont(name, path))
    except Exception:
        pdfmetrics.registerFont(Font(name, fallback, "WinAnsiEncoding"))
# ---- Brand fonts (2026 refresh): Verdana headlines · Helvetica body ----
# True Verdana is not freely redistributable. Drop Verdana.ttf / Verdana-Bold.ttf
# (or verdana.ttf / verdanab.ttf from C:\Windows\Fonts) into fonts/ for the real
# thing; until then the bundled DejaVu Sans (metrically Verdana-like) is used.
# The legacy slot names (Cinzel*, Cormorant*, Jost*) are kept and re-pointed so
# every style in the engine picks up the new faces without further changes.
def _first_font(candidates):
    for f in candidates:
        p = os.path.join(FONT_DIR, f)
        if os.path.exists(p):
            return p
    return None
_HEAD_R = _first_font(["Verdana.ttf", "verdana.ttf", "DejaVuSans.ttf"])
_HEAD_B = _first_font(["Verdana-Bold.ttf", "verdanab.ttf", "DejaVuSans-Bold.ttf"])
def _reg_ttf(name, path, builtin_fallback):
    try:
        pdfmetrics.registerFont(TTFont(name, path))
    except Exception:
        pdfmetrics.registerFont(Font(name, builtin_fallback, "WinAnsiEncoding"))
def _alias(name, builtin):
    pdfmetrics.registerFont(Font(name, builtin, "WinAnsiEncoding"))
# headline slots (regular + bold)
_reg_ttf("Headline", _HEAD_R or "", "Helvetica")
_reg_ttf("Headline-B", _HEAD_B or "", "Helvetica-Bold")
_reg_ttf("Cinzel", _HEAD_B or "", "Helvetica-Bold")      # legacy heading slot -> headline bold
_reg_ttf("Cinzel-B", _HEAD_B or "", "Helvetica-Bold")
# body slots -> Helvetica family (built into every PDF viewer)
_alias("Cormorant", "Helvetica"); _alias("Cormorant-M", "Helvetica-Bold")
_alias("Cormorant-SB", "Helvetica-Bold"); _alias("Cormorant-I", "Helvetica-Oblique")
_alias("Jost", "Helvetica"); _alias("Jost-M", "Helvetica-Bold"); _alias("Jost-L", "Helvetica")
# ---- Cover-only faces: the REAL serifs (used exclusively on the premium cover) ----
_reg("CoverTitle",   "Cormorant-SemiBold.ttf", "Helvetica-Bold")
_reg("CoverItalic",  "Cormorant-Italic.ttf",   "Helvetica-Oblique")
_reg("CoverEngrave", "Cinzel-Bold.ttf",        "Helvetica-Bold")
_reg("CoverSans",    "Jost-Light.ttf",         "Helvetica")
fonts.addMapping("Headline", 0, 0, "Headline"); fonts.addMapping("Headline", 1, 0, "Headline-B")
fonts.addMapping("Headline-B", 0, 0, "Headline-B"); fonts.addMapping("Headline-B", 1, 0, "Headline-B")
fonts.addMapping("Cinzel", 0, 0, "Cinzel"); fonts.addMapping("Cinzel", 1, 0, "Cinzel-B")
fonts.addMapping("Cinzel-B", 0, 0, "Cinzel-B"); fonts.addMapping("Cinzel-B", 1, 0, "Cinzel-B")
fonts.addMapping("Cormorant", 0, 0, "Cormorant"); fonts.addMapping("Cormorant", 1, 0, "Cormorant-SB")
fonts.addMapping("Cormorant", 0, 1, "Cormorant-I"); fonts.addMapping("Cormorant", 1, 1, "Cormorant-I")
fonts.addMapping("Cormorant-M", 0, 0, "Cormorant-M"); fonts.addMapping("Cormorant-M", 1, 0, "Cormorant-SB")
fonts.addMapping("Cormorant-SB", 0, 0, "Cormorant-SB"); fonts.addMapping("Cormorant-SB", 1, 0, "Cormorant-SB")
fonts.addMapping("Cormorant-I", 0, 1, "Cormorant-I"); fonts.addMapping("Cormorant-I", 1, 1, "Cormorant-I")
fonts.addMapping("Jost", 0, 0, "Jost"); fonts.addMapping("Jost", 1, 0, "Jost-M")
fonts.addMapping("Jost-M", 0, 0, "Jost-M"); fonts.addMapping("Jost-M", 1, 0, "Jost-M")
fonts.addMapping("Jost-L", 0, 0, "Jost-L"); fonts.addMapping("Jost-L", 1, 0, "Jost-M")

# Full-bleed cover artwork (the supplied agave front page).
# First match wins: assets/cover_bg.png / .jpg / .jpeg
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
def _cover_image_path():
    for ext in ("png", "jpg", "jpeg"):
        p = os.path.join(ASSET_DIR, f"cover_bg.{ext}")
        if os.path.exists(p):
            return p
    return None

# ---- Brand palette (2026 refresh: agave — warm paper · leaf greens · olive) ----
# Names kept stable so the rest of the engine maps automatically to their *role*.
DEEP   = HexColor("#F5F3E6")   # page background — warm handmade paper (role: surface)
DEEP2  = HexColor("#EAE9D4")   # panel / card fill — soft sage-tinted paper (role: panel)
GOLD   = HexColor("#5A6E2A")   # PRIMARY ACCENT — olive (kickers, subheads, rules, circles)
GOLD_L = HexColor("#26321B")   # HEADINGS & NUMBERS — deep leaf-green ink
GOLD_D = HexColor("#3E5024")   # deep olive (secondary strokes)
CREAM  = HexColor("#2A3220")   # body text — near-black green on paper
MUTE   = HexColor("#84836B")   # muted warm grey-olive (labels, footer)
LINE   = HexColor("#D7D5BC")   # hairline / borders — dry-grass taupe
ROSE   = HexColor("#4E7A66")   # agave teal accent
NAVY   = GOLD_L
MAROON = GOLD
PAPER  = DEEP
WATERMARK = HexColor("#3E5024")  # olive, drawn at very low alpha as a paper watermark

# ---- Interior theming ------------------------------------------------------
# The whole engine reads colour from the shared objects above (imported by name
# into report.py / premium_sections.py and baked into the ST styles). We keep
# those SAME objects and mutate their RGB in place, so a single call re-themes
# every heading, rule, panel, footer and paragraph at once. 'geometric' matches
# the bold pink cover (plum ink · orchid accents · soft pink paper).
_PALETTES = {
    "agave": dict(DEEP="#F5F3E6", DEEP2="#EAE9D4", GOLD="#5A6E2A", GOLD_L="#26321B",
                  GOLD_D="#3E5024", CREAM="#2A3220", MUTE="#84836B", LINE="#D7D5BC",
                  ROSE="#4E7A66", WATERMARK="#3E5024"),
    "geometric": dict(DEEP="#FBF1F6", DEEP2="#F1E3EE", GOLD="#8A3F86", GOLD_L="#2B1650",
                      GOLD_D="#4A2C6E", CREAM="#2E2340", MUTE="#94789E", LINE="#E7D3E4",
                      ROSE="#D96B93", WATERMARK="#6A3E86"),
}
_ACTIVE_STYLE = "agave"

def _apply_hex(colorobj, hexstr):
    nc = HexColor(hexstr)
    colorobj.red, colorobj.green, colorobj.blue = nc.red, nc.green, nc.blue

def apply_theme(style="agave"):
    """Re-colour the interior palette in place for the given cover style."""
    global _ACTIVE_STYLE
    pal = _PALETTES.get(style, _PALETTES["agave"])
    _ACTIVE_STYLE = style if style in _PALETTES else "agave"
    for name, obj in (("DEEP", DEEP), ("DEEP2", DEEP2), ("GOLD", GOLD), ("GOLD_L", GOLD_L),
                      ("GOLD_D", GOLD_D), ("CREAM", CREAM), ("MUTE", MUTE), ("LINE", LINE),
                      ("ROSE", ROSE), ("WATERMARK", WATERMARK)):
        _apply_hex(obj, pal[name])

PW, PH = A4
MARGIN = 20*mm

# ---------------- Decorative canvas painting ----------------
_PAPER_TEX = os.path.join(ASSET_DIR, "paper_texture.png")
def _ground(c, cover=False):
    """High-texture handmade paper (assets/paper_texture.png), full bleed.
    Falls back to a flat warm-paper gradient if the texture file is absent.
    The geometric theme uses a clean soft-pink paper instead of the beige tex."""
    if _ACTIVE_STYLE == "geometric":
        c.linearGradient(0, 0, 0, PH,
            [HexColor("#FCF3F8"), HexColor("#FBEFF5"), HexColor("#FDF8FB")],
            positions=[0.0, 0.5, 1.0], extend=True)
        return
    if os.path.exists(_PAPER_TEX):
        try:
            c.drawImage(_PAPER_TEX, 0, 0, PW, PH)
            return
        except Exception:
            pass
    if cover:
        c.linearGradient(0, 0, 0, PH,
            [HexColor("#EFEDDC"), HexColor("#F5F3E6"), HexColor("#F8F6EC")],
            positions=[0.0, 0.55, 1.0], extend=True)
    else:
        c.linearGradient(0, 0, 0, PH,
            [HexColor("#F1EFDE"), HexColor("#F8F6EC")],
            positions=[0.0, 1.0], extend=True)

def _nebula(c, blobs):
    """Soft translucent radial washes — cosmic clouds caught in moonlight."""
    for (x, y, R, col, a) in blobs:
        col = HexColor(col)
        c.radialGradient(x, y, R,
            [Color(col.red, col.green, col.blue, alpha=a), Color(col.red, col.green, col.blue, alpha=0)],
            positions=[0.0, 1.0], extend=False)

def _vignette(c, strength=0.55):
    """Darken the edges to concentrate the eye at the reading center."""
    R = max(PW, PH) * 0.75
    c.radialGradient(PW/2, PH*0.54, R,
        [Color(0,0,0, alpha=0), Color(0,0,0, alpha=strength)],
        positions=[0.62, 1.0], extend=True)

def _star(c, x, y, s, a, glow=False):
    if glow:
        # gentle cross-glow for the rare bright star
        c.setStrokeColor(Color(0.91,0.78,0.40, alpha=a*0.5)); c.setLineWidth(0.4)
        c.line(x-s*3.2,y,x+s*3.2,y); c.line(x,y-s*3.2,x,y+s*3.2)
        c.setFillColor(Color(1,0.97,0.86, alpha=min(1,a*0.18)))
        c.circle(x,y,s*2.0, stroke=0, fill=1)
    c.setFillColor(Color(0.95,0.86,0.55, alpha=a))
    c.circle(x, y, s, stroke=0, fill=1)

def _starfield(c, seed, density=1.0):
    """Three patient layers of light: dust, scatter, and a rare bright few."""
    import random
    r = random.Random(seed)
    # layer 1 — faint dust
    for _ in range(int(70*density)):
        _star(c, r.uniform(0,PW), r.uniform(0,PH), r.uniform(0.25,0.55), r.uniform(0.04,0.18))
    # layer 2 — mid scatter
    for _ in range(int(22*density)):
        _star(c, r.uniform(0,PW), r.uniform(0,PH), r.uniform(0.55,0.95), r.uniform(0.18,0.42))
    # layer 3 — rare luminous, with glow
    for _ in range(int(4*density)):
        _star(c, r.uniform(PW*0.08,PW*0.92), r.uniform(PH*0.08,PH*0.92),
              r.uniform(0.9,1.3), r.uniform(0.45,0.7), glow=True)

def _nakshatra_wheel(c, cx, cy, R, alpha=0.05, full=True):
    """Faint gold sacred-geometry watermark: 27 nakshatra ticks, 12 zodiac spokes, 8-petal lotus heart."""
    import math
    g = WATERMARK
    col = Color(g.red, g.green, g.blue, alpha=alpha)
    colf = Color(g.red, g.green, g.blue, alpha=alpha*0.85)
    c.saveState(); c.translate(cx, cy)
    c.setStrokeColor(col)
    # concentric rings
    for rr in (R, R*0.86, R*0.52, R*0.30):
        c.setLineWidth(0.6); c.circle(0,0,rr, stroke=1, fill=0)
    # 27 nakshatra ticks between the two outer rings
    c.setLineWidth(0.5)
    for i in range(27):
        a = math.radians(i*(360/27))
        c.line(R*math.cos(a), R*math.sin(a), R*0.86*math.cos(a), R*0.86*math.sin(a))
    # 12 zodiac spokes
    c.setLineWidth(0.45)
    for i in range(12):
        a = math.radians(i*30)
        c.line(R*0.30*math.cos(a), R*0.30*math.sin(a), R*0.86*math.cos(a), R*0.86*math.sin(a))
    # 8-petal lotus heart (vesica petals)
    c.setStrokeColor(colf); c.setLineWidth(0.5)
    pr = R*0.30
    for i in range(8):
        a = math.radians(i*45)
        px, py = pr*math.cos(a), pr*math.sin(a)
        c.saveState(); c.translate(px,py); c.rotate(i*45)
        p = c.beginPath()
        p.moveTo(0,0)
        p.curveTo(pr*0.5,pr*0.32, pr*0.5,-pr*0.32, 0,0)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()
    # central bindu
    c.setFillColor(colf); c.circle(0,0,1.6, stroke=0, fill=1)
    c.restoreState()

def _bg(c, cover=False, seed=7):
    c.saveState()
    _ground(c, cover=cover)
    if cover:
        _nakshatra_wheel(c, PW*0.5, PH*0.80, PW*0.34, alpha=0.055)   # faint watermark behind crest
    else:
        _nakshatra_wheel(c, PW*0.87, PH*0.12, PW*0.20, alpha=0.035)  # subtle, contained corner watermark
    c.restoreState()

def _corner_flourish(c, x, y, flip=1, scale=1.0):
    c.saveState(); c.translate(x,y); c.scale(flip*scale, scale)
    c.setStrokeColor(GOLD_D); c.setLineWidth(0.8)
    c.line(0,0,22,0); c.line(0,0,0,22)
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.line(5,5,16,5); c.line(5,5,5,16)
    c.setFillColor(GOLD); c.circle(5,5,1.4, stroke=0, fill=1)
    c.restoreState()

def _page_frame(c):
    c.setStrokeColor(LINE); c.setLineWidth(0.5)
    c.rect(MARGIN-6, MARGIN-6, PW-2*(MARGIN-6), PH-2*(MARGIN-6), stroke=1, fill=0)
    _corner_flourish(c, MARGIN-6, PH-MARGIN+6, flip=1, scale=1)
    c.saveState(); c.translate(PW-(MARGIN-6), PH-MARGIN+6); c.scale(-1,1); _corner_flourish(c,0,0); c.restoreState()
    c.saveState(); c.translate(MARGIN-6, MARGIN-6); c.scale(1,-1); _corner_flourish(c,0,0); c.restoreState()
    c.saveState(); c.translate(PW-(MARGIN-6), MARGIN-6); c.scale(-1,-1); _corner_flourish(c,0,0); c.restoreState()

def _footer(c, page_num, title="Numerology Report"):
    c.setFont("Jost-L", 7); c.setFillColor(MUTE)
    c.drawString(MARGIN, 11*mm, "VESHANN  ASTRO")
    c.drawCentredString(PW/2, 11*mm, title)
    c.drawRightString(PW-MARGIN, 11*mm, f"{page_num:02d}")
    c.setStrokeColor(LINE); c.setLineWidth(0.4)
    c.line(MARGIN, 14*mm, PW-MARGIN, 14*mm)

# crest: stylised Veshann Astro mark (vector — replace with logo PNG if provided)
def _crest(c, cx, cy, R=42):
    c.saveState(); c.translate(cx, cy)
    # outer ring
    c.setStrokeColor(GOLD); c.setLineWidth(1.2); c.circle(0,0,R, stroke=1, fill=0)
    c.setStrokeColor(GOLD_D); c.setLineWidth(0.6); c.circle(0,0,R-5, stroke=1, fill=0)
    # 12 ray ticks (zodiac)
    import math
    for i in range(12):
        a = math.radians(i*30)
        x1,y1 = (R-5)*math.cos(a),(R-5)*math.sin(a)
        x2,y2 = (R-11)*math.cos(a),(R-11)*math.sin(a)
        c.setStrokeColor(GOLD_L); c.setLineWidth(0.5); c.line(x1,y1,x2,y2)
    # central star (8-point)
    c.setFillColor(GOLD)
    for i in range(8):
        a = math.radians(i*45); a2 = math.radians(i*45+22.5)
        rr = R*0.42 if i%2==0 else R*0.42
        # draw simple radiating lines
        c.setStrokeColor(GOLD); c.setLineWidth(0.8)
        c.line(0,0, (R*0.4)*math.cos(a), (R*0.4)*math.sin(a))
    c.setFillColor(GOLD_L); c.circle(0,0,3.2, stroke=0, fill=1)
    c.setFillColor(DEEP); c.circle(0,0,1.3, stroke=0, fill=1)
    c.restoreState()

# ---------------- Paragraph styles ----------------
def S(name, **kw):
    base = dict(fontName="Jost", fontSize=10.2, leading=16, textColor=CREAM, alignment=TA_JUSTIFY)
    base.update(kw); return ParagraphStyle(name, **base)

ST = {
 'kicker'  : S('kicker', fontName="Jost-M", fontSize=8.5, textColor=GOLD, alignment=TA_LEFT, leading=12, spaceAfter=2, tracking=2),
 'h1'      : S('h1', fontName="Cinzel-B", fontSize=21, textColor=GOLD_L, alignment=TA_LEFT, leading=25, spaceAfter=2),
 'h1c'     : S('h1c', fontName="Cinzel-B", fontSize=22, textColor=GOLD_L, alignment=TA_CENTER, leading=27),
 'h2'      : S('h2', fontName="Cinzel", fontSize=13, textColor=GOLD, alignment=TA_LEFT, leading=18, spaceBefore=8, spaceAfter=4),
 'h3'      : S('h3', fontName="Jost-M", fontSize=10.5, textColor=GOLD_L, alignment=TA_LEFT, leading=15, spaceBefore=6, spaceAfter=2, autoLeading="max"),
 'body'    : S('body'),
 'bodyc'   : S('bodyc', alignment=TA_CENTER, textColor=CREAM),
 'lead'    : S('lead', fontName="Cormorant-M", fontSize=13.5, leading=19, textColor=CREAM, alignment=TA_JUSTIFY),
 'quote'   : S('quote', fontName="Cormorant-I", fontSize=13, leading=18, textColor=GOLD, alignment=TA_CENTER),
 'mute'    : S('mute', fontName="Jost-L", fontSize=9, textColor=MUTE, leading=14),
 'mutec'   : S('mutec', fontName="Jost-L", fontSize=9, textColor=MUTE, leading=14, alignment=TA_CENTER),
 'bullet'  : S('bullet', fontName="Jost", fontSize=9.8, leading=15, textColor=CREAM, leftIndent=12, alignment=TA_LEFT),
 'big'     : S('big', fontName="Cinzel-B", fontSize=46, textColor=GOLD, alignment=TA_CENTER, leading=46),
 'planet'  : S('planet', fontName="Cormorant-I", fontSize=14, textColor=GOLD_L, alignment=TA_CENTER, leading=16),
 'cardlbl' : S('cardlbl', fontName="Jost-M", fontSize=7.5, textColor=MUTE, alignment=TA_CENTER, leading=10, tracking=1),
 'cardnum' : S('cardnum', fontName="Cinzel-B", fontSize=24, textColor=GOLD_L, alignment=TA_CENTER, leading=26),
 'cardsub' : S('cardsub', fontName="Cormorant-I", fontSize=10, textColor=MUTE, alignment=TA_CENTER, leading=12),
}

# ---------------- Custom flowables ----------------
class HR(Flowable):
    def __init__(self, w=None, color=LINE, lw=0.6, pad=4):
        super().__init__(); self.w=w; self.color=color; self.lw=lw; self.pad=pad
    def wrap(self, aw, ah): self._w = self.w or aw; return (self._w, self.pad*2)
    def draw(self):
        self.canv.setStrokeColor(self.color); self.canv.setLineWidth(self.lw)
        self.canv.line(0, self.pad, self._w, self.pad)

class GoldRule(Flowable):
    """Centered ornamental divider with a diamond."""
    def __init__(self, w=None): super().__init__(); self.w=w
    def wrap(self, aw, ah): self._w=self.w or aw; return (self._w, 14)
    def draw(self):
        c=self.canv; w=self._w; m=w/2
        c.setStrokeColor(GOLD_D); c.setLineWidth(0.7)
        c.line(m-70,7,m-9,7); c.line(m+9,7,m+70,7)
        c.setFillColor(GOLD); c.saveState(); c.translate(m,7); c.rotate(45)
        c.rect(-3,-3,6,6, stroke=0, fill=1); c.restoreState()
        c.setFillColor(GOLD_L); c.circle(m-72,7,1.3,fill=1,stroke=0); c.circle(m+72,7,1.3,fill=1,stroke=0)

class NumberBadge(Flowable):
    """Large circular number badge with planet ring."""
    def __init__(self, num, planet, size=120):
        super().__init__(); self.num=str(num); self.planet=planet; self.size=size
    def wrap(self, aw, ah): return (aw, self.size+8)
    def draw(self):
        c=self.canv; aw=self._frame._aW if hasattr(self,'_frame') else self.size
        cx = self.size/2 + (self.canv._pagesize[0]); # not used
        R=self.size/2; cx=R; cy=R
        import math
        c.saveState(); c.translate(self.size/2, R)
        c.setStrokeColor(GOLD); c.setLineWidth(1.4); c.circle(0,0,R-4, stroke=1, fill=0)
        c.setStrokeColor(GOLD_D); c.setLineWidth(0.6); c.circle(0,0,R-10, stroke=1, fill=0)
        for i in range(24):
            a=math.radians(i*15); c.setStrokeColor(GOLD_L); c.setLineWidth(0.4)
            c.line((R-10)*math.cos(a),(R-10)*math.sin(a),(R-7)*math.cos(a),(R-7)*math.sin(a))
        c.setFont("Cinzel-B", R*0.8); c.setFillColor(GOLD_L)
        c.drawCentredString(0, -R*0.28, self.num)
        c.restoreState()

class LoShuGrid(Flowable):
    """Draws the 3x3 Lo Shu magic-square grid filled with the native's digits."""
    def __init__(self, counts, cell=44):
        super().__init__(); self.counts=counts; self.cell=cell; self.W=cell*3; self.H=cell*3
    def wrap(self, aw, ah): self.ox=(aw-self.W)/2; return (aw, self.H+10)
    def draw(self):
        c=self.canv; cell=self.cell; ox=self.ox; oy=6
        order=[[4,9,2],[3,5,7],[8,1,6]]
        for ri,row in enumerate(order):
            for ci,n in enumerate(row):
                x=ox+ci*cell; y=oy+(2-ri)*cell
                cnt=self.counts.get(n,0)
                c.setStrokeColor(LINE); c.setLineWidth(0.8)
                if cnt>0:
                    c.setFillColor(Color(0.12,0.17,0.31, alpha=0.07)); c.rect(x,y,cell,cell,stroke=1,fill=1)
                else:
                    c.setFillColor(DEEP2); c.rect(x,y,cell,cell,stroke=1,fill=1)
                if cnt>0:
                    txt=str(n)*cnt
                    fs = cell*0.42 if len(txt)<=2 else (cell*0.30 if len(txt)==3 else cell*0.22)
                    c.setFont("Cinzel-B", fs); c.setFillColor(GOLD_L)
                    c.drawCentredString(x+cell/2, y+cell/2-fs*0.35, txt)
                else:
                    c.setFont("Cormorant-I", cell*0.28); c.setFillColor(HexColor("#B7AD99"))
                    c.drawCentredString(x+cell/2, y+cell/2-cell*0.10, str(n))
        c.setStrokeColor(GOLD); c.setLineWidth(1.2); c.rect(ox,oy,self.W,self.H,stroke=1,fill=0)

class Panel(Flowable):
    """A rounded translucent panel behind a set of flowables."""
    def __init__(self, flowables, pad=12, bg=DEEP2, border=LINE, radius=6):
        super().__init__(); self.fl=flowables; self.pad=pad; self.bg=bg; self.border=border; self.radius=radius
    def wrap(self, aw, ah):
        self.aw=aw; self._heights=[]; tot=0
        for f in self.fl:
            w,h=f.wrap(aw-2*self.pad, ah); self._heights.append(h); tot+=h
        self.h=tot+2*self.pad; return (aw, self.h)
    def draw(self):
        c=self.canv
        c.setFillColor(self.bg); c.setStrokeColor(self.border); c.setLineWidth(0.6)
        c.roundRect(0,0,self.aw,self.h,self.radius,stroke=1,fill=1)
        # gold left accent
        c.setFillColor(GOLD); c.rect(0,0,2.5,self.h,stroke=0,fill=1)
        y=self.h-self.pad
        for f,h in zip(self.fl,self._heights):
            y-=h; f.drawOn(c, self.pad, y)

def bullets(items, style='bullet', glyph='◆'):
    out=[]
    for it in items:
        out.append(Paragraph(f'<font face="Cormorant-M" color="#7C2E38" size="9">{glyph}</font>&nbsp;&nbsp;{it}', ST[style]))
        out.append(Spacer(1,2))
    return out

# ---------------- Premium cover: blurred ghost numeral + centred serif block ----
import tempfile as _tempfile
_GHOST_CACHE = {}
def _ghost_numeral_png(num, px=1400, tint=(120, 140, 74), blur=30):
    """Render a large numeral, softly Gaussian-blurred, on a transparent canvas.
    Cached per numeral. Returns a file path, or None if PIL is unavailable."""
    key = (str(num), px, tint, blur)
    if key in _GHOST_CACHE:
        return _GHOST_CACHE[key]
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except Exception:
        return None
    try:
        img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        fp = os.path.join(FONT_DIR, "Cinzel-Bold.ttf")
        fnt = ImageFont.truetype(fp, int(px * 0.82))
        s = str(num)
        bb = d.textbbox((0, 0), s, font=fnt)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text(((px - tw) / 2 - bb[0], (px - th) / 2 - bb[1]), s, font=fnt, fill=tint + (255,))
        img = img.filter(ImageFilter.GaussianBlur(blur))
        out = os.path.join(_tempfile.gettempdir(), f"va_ghost_{s}.png")
        img.save(out)
        _GHOST_CACHE[key] = out
        return out
    except Exception:
        return None

# palette for cover ink (deep leaf on the olive field)
_CV_INK   = HexColor("#243019")
_CV_SOFT  = HexColor("#3E4A2B")
_CV_FAINT = HexColor("#5A6A3C")
_CV_LINE  = HexColor("#7C8A55")

def _cv_centred(c, cx, y, text, font, size, color, track=0.0):
    t = c.beginText(); t.setFont(font, size); t.setFillColor(color)
    t.setCharSpace(track)
    w = c.stringWidth(text, font, size) + track * max(len(text) - 1, 0)
    t.setTextOrigin(cx - w / 2, y); t.textOut(text); c.drawText(t)

def _fit_title_lines(c, title, font, size, max_w):
    """Greedy word-wrap to <=max_w; return list of lines."""
    words = title.split(); lines = []; cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

# Named cover styles: colour palette, ghost tint, text anchor + title size.
# 'agave'     -> olive field is at the TOP, so text is top-anchored (deep green ink).
# 'geometric' -> clean pink band is at the BOTTOM, so text is bottom-anchored
#                (dark-purple ink that reads on pink).
COVER_STYLES = {
    "agave": dict(image="cover_bg.png", anchor="top",
                  ink="#243019", soft="#3E4A2B", faint="#5A6A3C", line="#7C8A55",
                  ghost_tint=(120, 140, 74), ghost_alpha=0.30, title_size=44,
                  footer_ink="#F4F7EC"),
    "geometric": dict(image="cover_geometric.png", anchor="bottom",
                      ink="#2B1650", soft="#5A3D7A", faint="#7A5C97", line="#B98FB0",
                      ghost_tint=(90, 45, 120), ghost_alpha=0.22, title_size=32,
                      footer_ink="#FBEAF0"),
}

# fraction of the geometric image height that is solid pink band (measured)
_GEO_PINK_TOP_FRAC = 1052 / 1754

def draw_premium_cover(c, cd):
    """Draw the centred serif cover text + soft ghost numeral behind it.
    Agave style is top-anchored (clean olive field up top); geometric style is
    bottom-anchored (clean pink band along the bottom).
    cd = dict(title, name, born, nums=[(label,value),...], ghost, style)."""
    st = COVER_STYLES.get(cd.get("style", "agave"), COVER_STYLES["agave"])
    INK, SOFT, FAINT, LINE = (HexColor(st["ink"]), HexColor(st["soft"]),
                              HexColor(st["faint"]), HexColor(st["line"]))
    cx = PW / 2
    bottom = st["anchor"] == "bottom"
    if bottom:
        pink_top = PH * (1 - _GEO_PINK_TOP_FRAC)   # ~336pt band along the bottom
        yT = pink_top - 24
        ghost_gy, ghost_gh = pink_top * 0.52, 250
    else:
        yT = PH - 28 * mm
        ghost_gy, ghost_gh = PH - 300, 340
    # --- soft blurred ghost numeral, centred behind the text block ---
    g = _ghost_numeral_png(cd.get("ghost", ""), tint=st["ghost_tint"])
    if g:
        c.saveState(); c.setFillAlpha(st["ghost_alpha"])
        try:
            c.drawImage(g, cx - ghost_gh / 2, ghost_gy - ghost_gh / 2,
                        ghost_gh, ghost_gh, mask='auto')
        except Exception:
            pass
        c.restoreState()
    # --- masthead wordmark ---
    _cv_centred(c, cx, yT, "VESHANN ASTRO", "CoverEngrave", 13 if bottom else 14, INK, 2.8)
    _cv_centred(c, cx, yT - 14, "VEDIC NUMEROLOGY  ·  ASTROLOGY  ·  DELHI",
                "CoverSans", 7 if bottom else 7.5, FAINT, 2.3)
    # ornament: line — diamond — line
    oy = yT - 30
    c.setStrokeColor(LINE); c.setLineWidth(0.8)
    c.line(cx - 50, oy, cx - 9, oy); c.line(cx + 9, oy, cx + 50, oy)
    c.saveState(); c.translate(cx, oy); c.rotate(45)
    c.setFillColor(LINE); c.rect(-2.8, -2.8, 5.6, 5.6, fill=1, stroke=0); c.restoreState()
    # title — real Cormorant serif, wrapped & centred
    tsize = st["title_size"]
    lines = _fit_title_lines(c, cd["title"], "CoverTitle", tsize,
                             PW - (60 if bottom else 70) * mm)
    ty = yT - (52 if bottom else 64)
    for i, line in enumerate(lines):
        _cv_centred(c, cx, ty - i * tsize, line, "CoverTitle", tsize, INK)
    # prepared-for + name
    py = ty - tsize * len(lines) - (20 if bottom else 26)
    _cv_centred(c, cx, py, "a private reading prepared for", "CoverItalic",
                13 if bottom else 14, SOFT)
    _cv_centred(c, cx, py - (25 if bottom else 30), cd["name"], "CoverTitle",
                23 if bottom else 27, INK)
    _cv_centred(c, cx, py - (40 if bottom else 48), cd["born"].upper(), "CoverSans",
                7.5 if bottom else 8, FAINT, 2.1)
    # number strip — engraved numeral over tiny label, hairline dividers.
    # Bottom-anchored covers pin the strip near the page foot so it never
    # collides with a two-line title; top-anchored covers flow it below the name.
    nums = cd.get("nums", [])
    if nums:
        sy = 72 if bottom else (py - 84)
        n = len(nums); gap = 33 * mm
        xs = [cx + (i - (n - 1) / 2) * gap for i in range(n)]
        for i, (lbl, val) in enumerate(nums):
            x = xs[i]
            _cv_centred(c, x, sy, str(val), "CoverEngrave", 22 if bottom else 24, INK)
            _cv_centred(c, x, sy - 14, lbl.upper(), "CoverSans", 6.5, FAINT, 1.6)
            if i < n - 1:
                mx = (xs[i] + xs[i + 1]) / 2
                c.setStrokeColor(LINE); c.setLineWidth(0.6)
                c.line(mx, sy - 6, mx, sy + 18)
    # geometric cover fills the foot with text, so draw the web footer here
    if bottom:
        c.setFillColor(HexColor(st["footer_ink"])); c.setFont("CoverSans", 7.5)
        c.drawCentredString(cx, 32, "V E S H A N N A S T R O . C O . I N")

# ---------------- Page template machinery ----------------
class ReportDoc(BaseDocTemplate):
    def __init__(self, path, footer_title="Numerology Report", cover_data=None, **kw):
        self._footer_title = footer_title
        self._cover_data = cover_data
        super().__init__(path, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=MARGIN, bottomMargin=22*mm, **kw)
        fr = Frame(MARGIN, 22*mm, PW-2*MARGIN, PH-MARGIN-22*mm, id='main',
                   leftPadding=6, rightPadding=6, topPadding=2, bottomPadding=2)
        self.addPageTemplates([
            PageTemplate(id='cover', frames=[Frame(MARGIN,MARGIN,PW-2*MARGIN,PH-2*MARGIN,id='c')], onPage=self._cover_bg),
            PageTemplate(id='content', frames=[fr], onPage=self._content_bg),
        ])
        self._pnum=1
    def _cover_bg(self, c, d):
        cd = self._cover_data or {}
        style = COVER_STYLES.get(cd.get("style", "agave"), COVER_STYLES["agave"])
        # per-service cover image (falls back to the global default)
        img = os.path.join(ASSET_DIR, style["image"])
        if not os.path.exists(img):
            img = _cover_image_path()
        if img:
            try:
                from reportlab.lib.utils import ImageReader
                ir = ImageReader(img)
                iw, ih = ir.getSize()
                # scale to FILL the page (center-crop horizontally)
                scale = max(PW / iw, PH / ih)
                w, h = iw * scale, ih * scale
                c.saveState()
                c.drawImage(ir, (PW - w) / 2, PH - h, w, h, mask='auto')
                # premium centred serif cover text + ghost numeral
                if self._cover_data:
                    try:
                        draw_premium_cover(c, self._cover_data)
                    except Exception:
                        pass
                # small web footer — only on the agave (top-anchored) cover, where
                # the lower photo area is empty; the geometric cover fills it with text.
                if style["anchor"] == "top":
                    c.setFillColor(HexColor("#F4F7EC"))
                    c.setFont("CoverSans", 8)
                    c.drawCentredString(PW / 2, 12 * mm, "V E S H A N N A S T R O . C O . I N")
                c.restoreState()
                return
            except Exception:
                pass
        _bg(c, cover=True, seed=7)
    def _content_bg(self, c, d):
        self._pnum+=1
        _bg(c, cover=False, seed=self._pnum*13+3); _page_frame(c); _footer(c, self._pnum, self._footer_title)
