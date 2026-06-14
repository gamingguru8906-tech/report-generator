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
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    PageBreak, Table, TableStyle, Flowable, KeepTogether, Image, NextPageTemplate)
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Drawing
import content as C
import numerology as N

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
def _reg(name, file): pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, file)))
_reg("Cinzel", "Cinzel-Med.ttf"); _reg("Cinzel-B", "Cinzel-Bold.ttf")
_reg("Cormorant", "Cormorant-Reg.ttf"); _reg("Cormorant-M", "Cormorant-Med.ttf")
_reg("Cormorant-SB", "Cormorant-SemiBold.ttf"); _reg("Cormorant-I", "Cormorant-Italic.ttf")
_reg("Jost", "Jost-Reg.ttf"); _reg("Jost-M", "Jost-Med.ttf"); _reg("Jost-L", "Jost-Light.ttf")

# ---- Brand palette (light editorial: ivory / beige / grey · navy + maroon) ----
# Names kept stable so the rest of the engine maps automatically to their *role*.
DEEP   = HexColor("#FAF6EC")   # page background — warm ivory   (role: surface)
DEEP2  = HexColor("#F1E9D6")   # panel / card fill — soft beige  (role: panel)
GOLD   = HexColor("#7C2E38")   # PRIMARY ACCENT — maroon (kickers, subheads, rules, circles)
GOLD_L = HexColor("#1E2C50")   # HEADINGS & NUMBERS — navy
GOLD_D = HexColor("#5E222B")   # deep maroon (secondary strokes)
CREAM  = HexColor("#262E3D")   # body text — deep navy-charcoal on light
MUTE   = HexColor("#8C8472")   # muted warm grey (labels, footer)
LINE   = HexColor("#DAD1BF")   # hairline / borders — soft taupe
ROSE   = HexColor("#9C5A62")   # soft maroon accent
NAVY   = GOLD_L
MAROON = GOLD
PAPER  = DEEP
WATERMARK = HexColor("#1E2C50")  # navy, drawn at very low alpha as a paper watermark

PW, PH = A4
MARGIN = 20*mm

# ---------------- Decorative canvas painting ----------------
def _ground(c, cover=False):
    """Soft ivory paper — a whisper of warmth toward the foot."""
    if cover:
        c.linearGradient(0, 0, 0, PH,
            [HexColor("#F2EAD8"), HexColor("#F8F2E6"), HexColor("#FBF7EE")],
            positions=[0.0, 0.55, 1.0], extend=True)
    else:
        c.linearGradient(0, 0, 0, PH,
            [HexColor("#F7F1E4"), HexColor("#FBF7EE")],
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

def _footer(c, page_num):
    c.setFont("Jost-L", 7); c.setFillColor(MUTE)
    c.drawString(MARGIN, 11*mm, "VESHANN  ASTRO")
    c.drawCentredString(PW/2, 11*mm, "Numerology Report")
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

# ---------------- Page template machinery ----------------
class ReportDoc(BaseDocTemplate):
    def __init__(self, path, **kw):
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
        _bg(c, cover=True, seed=7)
    def _content_bg(self, c, d):
        self._pnum+=1
        _bg(c, cover=False, seed=self._pnum*13+3); _page_frame(c); _footer(c, self._pnum)
