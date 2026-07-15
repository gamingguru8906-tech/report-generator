"""Render two alternative cover-page text layouts onto the real photo cover.
Outputs two preview PDFs + PNGs so the client can pick one. Non-destructive:
does NOT touch report.py.
"""
import os, glob
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PW, PH = A4
MM = 72/25.4
HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(HERE, "assets")
FONTS = os.path.join(HERE, "fonts")
COVER = os.path.join(ASSET, "cover_bg.png")

# Register the REAL serif fonts (the report itself only aliases these to Helvetica)
def _reg(name, fname):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, fname)))
_reg("Cor-SB",  "Cormorant-SemiBold.ttf")
_reg("Cor-M",   "Cormorant-Med.ttf")
_reg("Cor-R",   "Cormorant-Reg.ttf")
_reg("Cor-I",   "Cormorant-Italic.ttf")
_reg("Cin-B",   "Cinzel-Bold.ttf")
_reg("Cin-M",   "Cinzel-Med.ttf")
_reg("Jost-R",  "Jost-Reg.ttf")
_reg("Jost-Lt", "Jost-Light.ttf")
_reg("Jost-Md", "Jost-Med.ttf")

INK   = HexColor("#243019")   # deep leaf ink
SOFT  = HexColor("#3E4A2B")
FAINT = HexColor("#5A6A3C")
LINEC = HexColor("#7C8A55")

# sample data
NAME   = "Ananya Sharma"
BORN   = "Born 21 August 1995"
TITLE  = "Complete Numerology Report"
NUMS   = [("LIFE PATH","8"),("DESTINY","3"),("SOUL URGE","5"),("DRIVER","3")]

def draw_bg(c):
    ir = ImageReader(COVER); iw, ih = ir.getSize()
    s = max(PW/iw, PH/ih); w, h = iw*s, ih*s
    c.drawImage(ir, (PW-w)/2, PH-h, w, h, mask='auto')

def make_ghost_numeral(num, out_png, px=1400, tint=(120,140,74), blur=26):
    """Render a large numeral, softly blurred, on transparent bg (premium watermark)."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    W = H = px
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fp = os.path.join(FONTS, "Cinzel-Bold.ttf")
    fnt = ImageFont.truetype(fp, int(px*0.82))
    s = str(num)
    bb = d.textbbox((0, 0), s, font=fnt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((W-tw)/2 - bb[0], (H-th)/2 - bb[1]), s, font=fnt, fill=tint + (255,))
    img = img.filter(ImageFilter.GaussianBlur(blur))
    img.save(out_png)
    return out_png

def _draw_tracked(c, x, y, text, font, size, color, track):
    t = c.beginText(x, y); t.setFont(font, size)
    t.setFillColor(color); t.setCharSpace(track); t.textOut(text); c.drawText(t)

def _tracked_w(c, text, font, size, track):
    return c.stringWidth(text, font, size) + track*max(len(text)-1, 0)

def tracked_centred(c, cx, y, text, font, size, color, track):
    w = _tracked_w(c, text, font, size, track)
    _draw_tracked(c, cx - w/2, y, text, font, size, color, track)

def tracked_left(c, x, y, text, font, size, color, track):
    _draw_tracked(c, x, y, text, font, size, color, track)
    return _tracked_w(c, text, font, size, track)

def centred(c, cx, y, text, font, size, color):
    c.setFont(font, size); c.setFillColor(color)
    w = c.stringWidth(text, font, size); c.drawString(cx - w/2, y, text)

# --------------------------------------------------------------------------
# LAYOUT 1 — "Ceremonial Center" : symmetric, engraved serif, quiet luxury
# --------------------------------------------------------------------------
def layout_one(path):
    c = canvas.Canvas(path, pagesize=A4); draw_bg(c)
    cx = PW/2
    yT = PH - 28*MM
    tracked_centred(c, cx, yT, "VESHANN ASTRO", "Cin-B", 15, INK, 3.0)
    tracked_centred(c, cx, yT-15, "VEDIC NUMEROLOGY  ·  ASTROLOGY  ·  DELHI", "Jost-Lt", 7.5, FAINT, 2.4)
    # ornament: line — diamond — line
    oy = yT - 33
    c.setStrokeColor(LINEC); c.setLineWidth(0.8)
    c.line(cx-52, oy, cx-10, oy); c.line(cx+10, oy, cx+52, oy)
    c.saveState(); c.translate(cx, oy); c.rotate(45)
    c.setFillColor(LINEC); c.rect(-3, -3, 6, 6, fill=1, stroke=0); c.restoreState()
    # title — real Cormorant serif, two centred lines
    ty = yT - 70
    for i, line in enumerate(["Complete Numerology", "Report"]):
        centred(c, cx, ty - i*44, line, "Cor-SB", 44, INK)
    # prepared-for + name
    py = ty - 44 - 34
    centred(c, cx, py, "a private reading prepared for", "Cor-I", 14, SOFT)
    centred(c, cx, py-32, NAME, "Cor-SB", 28, INK)
    tracked_centred(c, cx, py-50, BORN.upper(), "Jost-Lt", 8, FAINT, 2.2)
    # number strip — engraved numeral over tiny label, hairline dividers
    sy = py - 90
    n = len(NUMS); gap = 33*MM
    xs = [cx + (i-(n-1)/2)*gap for i in range(n)]
    for i,(lbl,val) in enumerate(NUMS):
        x = xs[i]
        centred(c, x, sy, val, "Cin-B", 25, INK)
        tracked_centred(c, x, sy-15, lbl, "Jost-Lt", 6.5, FAINT, 1.6)
        if i < n-1:
            mx = (xs[i]+xs[i+1])/2
            c.setStrokeColor(LINEC); c.setLineWidth(0.6); c.line(mx, sy-6, mx, sy+20)
    c.showPage(); c.save()

# --------------------------------------------------------------------------
# LAYOUT 1P — "Ceremonial Center + ghost numeral" : Layout 1 text, big soft
#             blurred Life-Path numeral behind it for a premium-edition feel
# --------------------------------------------------------------------------
def layout_one_premium(path, ghost_alpha=0.30):
    c = canvas.Canvas(path, pagesize=A4); draw_bg(c)
    cx = PW/2
    # --- soft blurred ghost numeral, centred in the olive field, behind text ---
    ghost = os.path.join(os.path.dirname(path), "_ghost8.png")
    make_ghost_numeral(NUMS[0][1], ghost, tint=(120,140,74), blur=30)
    gh = 360           # drawn height in pt
    gy = PH - 300      # vertical centre-ish of the text block
    c.saveState(); c.setFillAlpha(ghost_alpha)
    c.drawImage(ghost, cx-gh/2, gy-gh/2, gh, gh, mask='auto')
    c.restoreState()
    # --- same centred serif text as Layout 1 ---
    yT = PH - 28*MM
    tracked_centred(c, cx, yT, "VESHANN ASTRO", "Cin-B", 15, INK, 3.0)
    tracked_centred(c, cx, yT-15, "VEDIC NUMEROLOGY  ·  ASTROLOGY  ·  DELHI", "Jost-Lt", 7.5, FAINT, 2.4)
    oy = yT - 33
    c.setStrokeColor(LINEC); c.setLineWidth(0.8)
    c.line(cx-52, oy, cx-10, oy); c.line(cx+10, oy, cx+52, oy)
    c.saveState(); c.translate(cx, oy); c.rotate(45)
    c.setFillColor(LINEC); c.rect(-3, -3, 6, 6, fill=1, stroke=0); c.restoreState()
    ty = yT - 70
    for i, line in enumerate(["Complete Numerology", "Report"]):
        centred(c, cx, ty - i*44, line, "Cor-SB", 44, INK)
    py = ty - 44 - 34
    centred(c, cx, py, "a private reading prepared for", "Cor-I", 14, SOFT)
    centred(c, cx, py-32, NAME, "Cor-SB", 28, INK)
    tracked_centred(c, cx, py-50, BORN.upper(), "Jost-Lt", 8, FAINT, 2.2)
    sy = py - 90
    n = len(NUMS); gap = 33*MM
    xs = [cx + (i-(n-1)/2)*gap for i in range(n)]
    for i,(lbl,val) in enumerate(NUMS):
        x = xs[i]
        centred(c, x, sy, val, "Cin-B", 25, INK)
        tracked_centred(c, x, sy-15, lbl, "Jost-Lt", 6.5, FAINT, 1.6)
        if i < n-1:
            mx = (xs[i]+xs[i+1])/2
            c.setStrokeColor(LINEC); c.setLineWidth(0.6); c.line(mx, sy-6, mx, sy+20)
    c.showPage(); c.save()

# --------------------------------------------------------------------------
# LAYOUT 2 — "Editorial Masthead" : asymmetric, giant ghost numeral, spec row
# --------------------------------------------------------------------------
def layout_two(path):
    c = canvas.Canvas(path, pagesize=A4); draw_bg(c)
    L = 22*MM
    R = PW - 22*MM
    # giant faint Life-Path numeral, top-right, as design texture
    c.saveState()
    c.setFillColor(HexColor("#8CA057")); c.setFillAlpha(0.32)
    c.setFont("Cin-B", 300)
    gw = c.stringWidth("8", "Cin-B", 300)
    c.drawString(R - gw + 26, PH - 330, "8")
    c.restoreState()
    # masthead row
    yM = PH - 26*MM
    tracked_left(c, L, yM, "VESHANN ASTRO", "Cin-B", 13, INK, 2.4)
    rt = "PREMIUM EDITION"
    rw = _tracked_w(c, rt, "Jost-Lt", 8, 2.2)
    _draw_tracked(c, R-rw, yM, rt, "Jost-Lt", 8, FAINT, 2.2)
    c.setStrokeColor(INK); c.setLineWidth(1.1); c.line(L, yM-9, R, yM-9)
    # kicker
    ky = yM - 26
    tracked_left(c, L, ky, "COMPLETE READING", "Jost-Md", 8.5, FAINT, 3.2)
    # big left title, real serif, stacked
    ty = ky - 34
    c.setFillColor(INK); c.setFont("Cor-SB", 50)
    for i,line in enumerate(["Numerology", "Report"]):
        c.drawString(L, ty - i*46, line)
    # name block
    ny = ty - 46 - 42
    tracked_left(c, L, ny, "PREPARED FOR", "Jost-Lt", 8, FAINT, 2.6)
    c.setFont("Cor-SB", 32); c.setFillColor(INK); c.drawString(L, ny-34, NAME)
    c.setFont("Cor-I", 14); c.setFillColor(SOFT); c.drawString(L, ny-53, BORN)
    # spec row: 4 columns, hairline above, label + engraved value
    sy = ny - 92
    c.setStrokeColor(INK); c.setLineWidth(0.9); c.line(L, sy+24, R, sy+24)
    colw = (R-L)/4
    for i,(lbl,val) in enumerate(NUMS):
        x = L + i*colw
        tracked_left(c, x, sy+11, lbl, "Jost-Lt", 7, FAINT, 1.8)
        c.setFont("Cin-B", 23); c.setFillColor(INK); c.drawString(x, sy-16, val)
        if i>0:
            c.setStrokeColor(LINEC); c.setLineWidth(0.5); c.line(x-12, sy-20, x-12, sy+20)
    c.setFont("Cor-I", 12); c.setFillColor(FAINT)
    c.drawString(L, sy-36, "Chaldean system, cross-checked with Vedic graha wisdom")
    c.showPage(); c.save()

if __name__ == "__main__":
    out = os.environ.get("OUT", ".")
    layout_one(os.path.join(out, "cover_layout_1_ceremonial.pdf"))
    layout_two(os.path.join(out, "cover_layout_2_masthead.pdf"))
    layout_one_premium(os.path.join(out, "cover_layout_1_premium.pdf"))
    print("done")
