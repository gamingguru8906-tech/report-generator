"""Prototype the bottom-anchored cover for the geometric header (pink band)."""
import os
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
IMG = os.path.join(ASSET, "cover_geometric.png")

def _reg(n, f): pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f)))
_reg("Cor-SB","Cormorant-SemiBold.ttf"); _reg("Cor-I","Cormorant-Italic.ttf")
_reg("Cin-B","Cinzel-Bold.ttf"); _reg("Jost-Lt","Jost-Light.ttf")

# ink palette for text on the pink band
INK   = HexColor("#2B1650")   # deep plum
SOFT  = HexColor("#5A3D7A")
FAINT = HexColor("#7A5C97")
LINE  = HexColor("#B98FB0")

NAME="Ananya Sharma"; BORN="Born 21 August 1995"
NUMS=[("LIFE PATH","8"),("DESTINY","3"),("SOUL URGE","5"),("DRIVER","3")]

def ghost(num, out, px=1400, tint=(90,45,120), blur=30):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    img=Image.new("RGBA",(px,px),(0,0,0,0)); d=ImageDraw.Draw(img)
    fnt=ImageFont.truetype(os.path.join(FONTS,"Cinzel-Bold.ttf"),int(px*0.82))
    s=str(num); bb=d.textbbox((0,0),s,font=fnt); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    d.text(((px-tw)/2-bb[0],(px-th)/2-bb[1]),s,font=fnt,fill=tint+(255,))
    img=img.filter(ImageFilter.GaussianBlur(blur)); img.save(out); return out

def draw_tracked_c(c,cx,y,text,font,size,color,track):
    t=c.beginText(); t.setFont(font,size); t.setFillColor(color); t.setCharSpace(track)
    w=c.stringWidth(text,font,size)+track*max(len(text)-1,0)
    t.setTextOrigin(cx-w/2,y); t.textOut(text); c.drawText(t)

def centred(c,cx,y,text,font,size,color):
    c.setFont(font,size); c.setFillColor(color)
    w=c.stringWidth(text,font,size); c.drawString(cx-w/2,y,text)

def wrap(c,title,font,size,maxw):
    words=title.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if c.stringWidth(t,font,size)<=maxw or not cur: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def build(path, title):
    c=canvas.Canvas(path,pagesize=A4)
    ir=ImageReader(IMG); iw,ih=ir.getSize(); s=max(PW/iw,PH/ih); w,h=iw*s,ih*s
    c.drawImage(ir,(PW-w)/2,PH-h,w,h,mask='auto')
    cx=PW/2
    pink_top=PH*(1-1052/1754)   # ~336pt
    # ghost numeral centred in the pink band
    g=ghost(NUMS[0][1], os.path.join(os.path.dirname(path),"_geoghost.png"))
    gh=250; gy=pink_top*0.52
    c.saveState(); c.setFillAlpha(0.22); c.drawImage(g,cx-gh/2,gy-gh/2,gh,gh,mask='auto'); c.restoreState()
    # top cluster flows down from just inside the pink band
    y=pink_top-24
    draw_tracked_c(c,cx,y,"VESHANN ASTRO","Cin-B",13,INK,2.6)
    draw_tracked_c(c,cx,y-13,"VEDIC NUMEROLOGY  ·  ASTROLOGY  ·  DELHI","Jost-Lt",7,FAINT,2.2)
    oy=y-29
    c.setStrokeColor(LINE); c.setLineWidth(0.8)
    c.line(cx-46,oy,cx-9,oy); c.line(cx+9,oy,cx+46,oy)
    c.saveState(); c.translate(cx,oy); c.rotate(45); c.setFillColor(LINE); c.rect(-2.5,-2.5,5,5,fill=1,stroke=0); c.restoreState()
    lines=wrap(c,title,"Cor-SB",32,PW-60*MM)
    ty=y-52
    for i,ln in enumerate(lines): centred(c,cx,ty-i*32,ln,"Cor-SB",32,INK)
    py=ty-32*len(lines)-22
    centred(c,cx,py,"a private reading prepared for","Cor-I",12.5,SOFT)
    centred(c,cx,py-25,NAME,"Cor-SB",23,INK)
    draw_tracked_c(c,cx,py-40,BORN.upper(),"Jost-Lt",7.5,FAINT,2.0)
    # number strip pinned near bottom
    sy=70; n=len(NUMS); gap=33*MM
    xs=[cx+(i-(n-1)/2)*gap for i in range(n)]
    for i,(lbl,val) in enumerate(NUMS):
        x=xs[i]; centred(c,x,sy,val,"Cin-B",22,INK)
        draw_tracked_c(c,x,sy-14,lbl,"Jost-Lt",6.5,FAINT,1.6)
        if i<n-1:
            mx=(xs[i]+xs[i+1])/2; c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(mx,sy-5,mx,sy+18)
    c.setFillColor(HexColor("#FBEAF0")); c.setFont("Jost-Lt",7.5)
    c.drawCentredString(cx,34,"V E S H A N N A S T R O . C O . I N")
    c.showPage(); c.save()

if __name__=="__main__":
    out=os.environ.get("OUT",".")
    build(os.path.join(out,"geo_cover_complete.pdf"),"Complete Numerology Report")
    build(os.path.join(out,"geo_cover_forecast.pdf"),"Personal Year Forecast")
    build(os.path.join(out,"geo_cover_business.pdf"),"Business Name Report")
    print("done")
