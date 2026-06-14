"""Story assembly — builds all 25 pages per the Veshann Astro blueprint."""
from datetime import date
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, NextPageTemplate, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from pdfbuild_base import (ReportDoc, ST, HR, GoldRule, LoShuGrid, Panel, bullets,
    GOLD, GOLD_L, GOLD_D, CREAM, MUTE, LINE, DEEP, DEEP2, PW, MARGIN, _crest)
import content as C
import numerology as N
from reportlab.platypus import Flowable

MONTHS=["","January","February","March","April","May","June","July","August","September","October","November","December"]
def fmt_date(d): return f"{d.day} {MONTHS[d.month]} {d.year}"
def ordinal(n): return f"{n}{'th' if 11<=n%100<=13 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"

def core(num):  # safe lookup
    return C.CORE.get(num, C.CORE.get(N.reduce_num(num, False), C.CORE[1]))

def short_planet(num):
    p = core(num)['planet']
    if 'Master' in p or 'Higher' in p:
        return f"Master {num}"
    return p.split(' (')[0]

def kicker(t): return Paragraph(t.upper(), ST['kicker'])
def h1(t): return Paragraph(t, ST['h1'])
def h2(t): return Paragraph(t, ST['h2'])
def h3(t): return Paragraph(t, ST['h3'])
def body(t): return Paragraph(t, ST['body'])
def lead(t): return Paragraph(t, ST['lead'])
def mute(t): return Paragraph(t, ST['mute'])

class CrestF(Flowable):
    def __init__(self, R=44): super().__init__(); self.R=R
    def wrap(self, aw, ah): self.aw=aw; return (aw, self.R*2+8)
    def draw(self): _crest(self.canv, self.aw/2, self.R+4, self.R)

class BigNum(Flowable):
    """Centerpiece number with planet caption."""
    def __init__(self, num, caption, sz=58):
        super().__init__(); self.num=str(num); self.cap=caption; self.sz=sz
    def wrap(self, aw, ah): self.aw=aw; self.R=self.sz/2+14; self.H=self.R*2+26; return (aw, self.H)
    def draw(self):
        import math
        c=self.canv; cx=self.aw/2; R=self.R; cy=self.H-R-2
        c.setStrokeColor(GOLD); c.setLineWidth(1.3); c.circle(cx,cy,R,stroke=1,fill=0)
        c.setStrokeColor(GOLD_D); c.setLineWidth(0.5); c.circle(cx,cy,R-5,stroke=1,fill=0)
        for i in range(36):
            a=math.radians(i*10); c.setStrokeColor(GOLD_L); c.setLineWidth(0.3)
            c.line(cx+(R-5)*math.cos(a),cy+(R-5)*math.sin(a),cx+(R-8)*math.cos(a),cy+(R-8)*math.sin(a))
        c.setFont("Cinzel-B", self.sz); c.setFillColor(GOLD_L)
        c.drawCentredString(cx, cy-self.sz*0.34, self.num)
        c.setFont("Cormorant-I", 12); c.setFillColor(MUTE)
        c.drawCentredString(cx, 4, self.cap)

def core_section(kick, title, num, intro, *, value_label=None, value_note=None, extra_paras=None):
    """A reusable two-page-style core-number section."""
    cr=core(num)
    el=[NextPageTemplate('content'), kicker(kick), h1(title), GoldRule(), Spacer(1,4)]
    el.append(BigNum(num, cr['planet']))
    el.append(Spacer(1,2))
    if value_label:
        el.append(Paragraph(value_label, ST['mutec'])); el.append(Spacer(1,4))
    el.append(Paragraph(f'<i>“{cr["archetype"]}”</i>', ST['quote'])); el.append(Spacer(1,8))
    el.append(lead(intro)); el.append(Spacer(1,8))
    el.append(body(cr['essence'])); el.append(Spacer(1,6))
    if value_note: el.append(Panel([body(value_note)])); el.append(Spacer(1,8))
    # strengths + shadow panels side by side
    sp = Table([[
        Panel([h3('Your Strengths')]+bullets(cr['strengths']), bg=DEEP2),
        Panel([h3('Growth Edges')]+bullets(cr['shadow'], glyph='◇'), bg=HexColor("#EAEDF3")),
    ]], colWidths=[(PW-2*MARGIN-12)/2-4]*2)
    sp.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(0,0),8),('RIGHTPADDING',(1,0),(1,0),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    el.append(sp); el.append(Spacer(1,8))
    if extra_paras:
        for p in extra_paras: el.append(p); el.append(Spacer(1,4))
    el.append(Spacer(1,4))
    el.append(Panel([Paragraph(f'<font color="#7C2E38"><b><font face="Cormorant-M">◆</font> Vedic Remedy &nbsp;·&nbsp; {cr["planet"]}</b></font>', ST['h3']),
                     Spacer(1,3), body(cr['remedy'])], bg=HexColor("#F6ECEC"), border=GOLD_D))
    el.append(PageBreak())
    return el

def kv_table(rows):
    data=[[Paragraph(f'<font color="#8C8472">{k}</font>', ST['mute']),
           Paragraph(f'<font color="#262E3D">{v}</font>', ST['body'])] for k,v in rows]
    t=Table(data, colWidths=[42*mm, None])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3),
        ('BOTTOMPADDING',(0,0),(-1,-1),3),('LINEBELOW',(0,0),(-1,-2),0.4,LINE)]))
    return t

# ============ MODULAR PAGE BUILDERS ============
# Each section returns a list of flowables ending in PageBreak().
# Reports are composed from these by RECIPES, so the same engine produces
# the full 25-page premium report AND shorter focused reports.

def sec_cover(r, tier="Premium", title="COMPLETE NUMEROLOGY REPORT"):
    S=[NextPageTemplate('content'), Spacer(1,18*mm), CrestF(46), Spacer(1,6)]
    S+=[Paragraph("VESHANN ASTRO", ParagraphStyle('cv',fontName="Cinzel-B",fontSize=22,textColor=GOLD_L,alignment=TA_CENTER,leading=26,tracking=4))]
    S+=[Paragraph("VEDIC NUMEROLOGY &nbsp;·&nbsp; ASTROLOGY", ParagraphStyle('cv2',fontName="Jost-L",fontSize=8.5,textColor=MUTE,alignment=TA_CENTER,tracking=3,spaceBefore=4))]
    S+=[Spacer(1,16), GoldRule(), Spacer(1,14)]
    S+=[Paragraph(tier, ParagraphStyle('t1',fontName="Cormorant-I",fontSize=30,textColor=CREAM,alignment=TA_CENTER,leading=30))]
    S+=[Paragraph(title, ParagraphStyle('t2',fontName="Cinzel-B",fontSize=24,textColor=GOLD,alignment=TA_CENTER,leading=30,tracking=1,spaceBefore=2))]
    S+=[Spacer(1,18)]
    S+=[Paragraph("Prepared exclusively for", ST['mutec']), Spacer(1,4)]
    S+=[Paragraph(r['name'].upper(), ParagraphStyle('nm',fontName="Cinzel-B",fontSize=18,textColor=GOLD_L,alignment=TA_CENTER,leading=24,tracking=1))]
    S+=[Spacer(1,3), Paragraph(f"Born {fmt_date(r['dob'])}", ST['quote'])]
    S+=[Spacer(1,26)]
    strip=Table([[
        Paragraph(f'<font color="#8C8472" size="7">LIFE PATH</font><br/><font color="#1E2C50" size="20" face="Cinzel-B">{r["life_path"]}</font>', ST['mutec']),
        Paragraph(f'<font color="#8C8472" size="7">DESTINY</font><br/><font color="#1E2C50" size="20" face="Cinzel-B">{r["destiny"]}</font>', ST['mutec']),
        Paragraph(f'<font color="#8C8472" size="7">SOUL URGE</font><br/><font color="#1E2C50" size="20" face="Cinzel-B">{r["soul_urge"]}</font>', ST['mutec']),
        Paragraph(f'<font color="#8C8472" size="7">DRIVER</font><br/><font color="#1E2C50" size="20" face="Cinzel-B">{r["driver"]}</font>', ST['mutec']),
    ]], colWidths=[(PW-2*MARGIN)/4]*4)
    strip.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEAFTER',(0,0),(-2,-1),0.5,LINE)]))
    S+=[strip, Spacer(1,30)]
    S+=[GoldRule()]
    S+=[Paragraph("veshannastro.co.in &nbsp;·&nbsp; @veshann.astro", ParagraphStyle('cf',fontName="Jost-L",fontSize=8,textColor=MUTE,alignment=TA_CENTER,tracking=2,spaceBefore=8))]
    S+=[Paragraph("This report is generated using the authentic Chaldean numerology system integrated with Vedic Graha wisdom.", ST['mutec'])]
    S+=[PageBreak()]
    return S

def sec_how_to_read(r):
    S=[kicker("Begin Here"), h1("How To Read This Report"), GoldRule(), Spacer(1,6)]
    S+=[lead("This is not a horoscope to glance at once. It is a personal operating manual — built from the precise mathematics of your name and birth date, decoded through India's oldest numerical science. Treat it as a reference you return to at every crossroad.")]
    S+=[Spacer(1,10)]
    for t,d in C.HOW_TO_READ:
        S+=[Panel([Paragraph(f'<font color="#1E2C50">{t}</font>', ST['h3']), Spacer(1,2), body(d)])]
        S+=[Spacer(1,6)]
    S+=[PageBreak()]
    return S

def sec_snapshot(r):
    S=[kicker("At A Glance"), h1("Your Numerology Snapshot"), GoldRule(), Spacer(1,4)]
    S+=[body("Every number below is a member of your cosmic team. The first impression others receive, the road your soul travels, the private fuel that drives you — read together, they form a single portrait.")]
    S+=[Spacer(1,10)]
    def card(lbl, num, sub):
        return Panel([Paragraph(lbl.upper(), ST['cardlbl']), Spacer(1,2),
                      Paragraph(str(num), ST['cardnum']),
                      Paragraph(sub, ST['cardsub'])], pad=8, bg=DEEP2)
    cards=[
        ("Life Path", r['life_path'], short_planet(r['life_path'])),
        ("Destiny", r['destiny'], short_planet(r['destiny'])),
        ("Soul Urge", r['soul_urge'], short_planet(r['soul_urge'])),
        ("Personality", r['personality'], short_planet(r['personality'])),
        ("Birthday / Driver", r['driver'], short_planet(r['driver'])),
        ("Maturity", r['maturity'], short_planet(r['maturity'])),
        ("Personal Year", r['personal_year'], str(r['personal_year_for'])),
        ("Hidden Passion", "·".join(map(str,r['hidden_passion'])), "core drive"),
        ("Lucky Numbers", "·".join(map(str,r['lucky_numbers'][:4])), "harmonised"),
    ]
    rows=[]; row=[]
    for l,n,s in cards:
        row.append(card(l,n,s))
        if len(row)==3: rows.append(row); row=[]
    if row:
        while len(row)<3: row.append(Spacer(1,1))
        rows.append(row)
    grid=Table(rows, colWidths=[(PW-2*MARGIN-12)/3-6]*3)
    grid.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
    S+=[grid, Spacer(1,8)]
    extra=[]
    if r['karmic_debts']: extra.append(f"Karmic Debt(s) present: <b>{', '.join(map(str,r['karmic_debts']))}</b>")
    if r['missing']: extra.append(f"Missing in Lo Shu grid: <b>{', '.join(map(str,r['missing']))}</b>")
    if r['complete_planes']: extra.append(f"Power planes active: <b>{len(r['complete_planes'])}</b>")
    extra.append(f"Name vibration vs birth: <b>{'Harmonious ✓' if r['name_friendly'] else 'Needs tuning'}</b>")
    S+=[Panel([Paragraph('<font color="#1E2C50">Key Flags</font>', ST['h3'])]+[Paragraph(f'<font face="Cormorant-M" color="#7C2E38">◆</font>&nbsp; {e}', ST['bullet']) for e in extra], border=GOLD_D)]
    S+=[PageBreak()]
    return S

def sec_life_path(r):
    cr_lp=core(r['life_path'])
    lp_note=f"Your Life Path is <b>{r['life_path']}</b>, derived from your full birth date {fmt_date(r['dob'])} (total {r['life_path_total']} <font face='Cormorant-M'>\u2192</font> {r['life_path']}). In Vedic terms this is your Conductor (Bhagyank) — the force that steers your overall destiny and the lessons your soul chose before birth."
    return core_section("The Master Road","Life Path Number",r['life_path'],C.LIFE_PATH_INTRO,
        value_note=lp_note,
        extra_paras=[h2("Living Your Life Path Well"),
            body(f"When you move in the direction of the {cr_lp['planet']} — leading, building, or serving in the ways described above — life feels supported and synchronicities multiply. When you drift against it (chasing approval, comfort, or someone else's road), even success will feel hollow.")])

def sec_destiny(r):
    d_note=f"Your Destiny Number is <b>{r['destiny']}</b>, the Chaldean total of every letter in <b>{r['name']}</b> ({r['destiny_total']} <font face='Cormorant-M'>\u2192</font> {r['destiny']})." + ("" if r['name_friendly'] else " Note: this vibration is not fully harmonised with your birth numbers — the Name Analysis section suggests a refinement.")
    return core_section("Your Public Mission","Destiny / Expression Number",r['destiny'],C.DESTINY_INTRO,
        value_note=d_note,
        extra_paras=[h2("How The World Receives You"),
            body(f"Your name broadcasts the {core(r['destiny'])['planet']} frequency. This is the talent-set and reputation the universe organises around you — the 'what you're known for'. Where your Life Path ({r['life_path']}) is the road, this {r['destiny']} is the vehicle you drive it in.")])

def sec_soul_urge(r):
    return core_section("Your Heart's Desire","Soul Urge Number",r['soul_urge'],C.SOUL_INTRO,
        value_note=f"Your Soul Urge is <b>{r['soul_urge']}</b>, from the vowels of your name ({r['soul_urge_total']} <font face='Cormorant-M'>\u2192</font> {r['soul_urge']}). This is your private compass — what truly satisfies you beneath every public achievement.",
        extra_paras=[h2("Feeding Your Soul"),
            body(f"You will feel deeply fulfilled in life only when your daily reality honours this {core(r['soul_urge'])['planet']} need. Many people achieve their Destiny number's goals yet feel empty — that emptiness is almost always a starved Soul Urge. Build at least one part of your life that feeds it directly.")])

def sec_personality(r):
    cr_p=core(r['personality'])
    S=[kicker("Your First Impression"), h1("Personality Number"), GoldRule(), Spacer(1,4)]
    S+=[BigNum(r['personality'], cr_p['planet']), Spacer(1,4)]
    S+=[Paragraph(f"From the consonants of your name &nbsp;·&nbsp; total {r['personality_total']} <font face='Cormorant-M'>\u2192</font> {r['personality']}", ST['mutec']), Spacer(1,8)]
    S+=[lead(C.PERSONALITY_INTRO), Spacer(1,8)]
    S+=[body(f"Your outer gateway runs on the {cr_p['planet']} vibration — the {cr_p['archetype']} energy. Before anyone meets your inner Soul Urge ({r['soul_urge']}) or understands your Destiny ({r['destiny']}), they meet this. " + cr_p['essence'])]
    S+=[Spacer(1,8)]
    S+=[Panel([h3("What People Notice First")]+bullets(cr_p['strengths'][:4]))]
    S+=[Spacer(1,6), Panel([h3("The Mask vs The Truth")], bg=HexColor("#F6ECEC")), Spacer(1,2)]
    S+=[body(f"Remember: this is the wrapping, not the gift. People who only know your Personality number see the {cr_p['archetype']}; those who earn your trust discover the full depth of your Soul Urge {r['soul_urge']} and Life Path {r['life_path']}.")]
    S+=[PageBreak()]
    return S

def sec_birthday(r):
    cr_b=core(r['driver']); cr_lp=core(r['life_path'])
    S=[kicker("Your Daily Engine"), h1("Birthday Number (Driver / Mulank)"), GoldRule(), Spacer(1,4)]
    S+=[BigNum(r['driver'], cr_b['planet']), Spacer(1,4)]
    S+=[Paragraph(f"You were born on the {ordinal(r['birthday_raw'])} &nbsp;·&nbsp; Mulank {r['driver']}", ST['mutec']), Spacer(1,8)]
    S+=[lead(C.BIRTHDAY_INTRO), Spacer(1,8)]
    S+=[body(cr_b['essence']), Spacer(1,8)]
    S+=[Panel([h3(f"Driver {r['driver']} + Conductor {r['life_path']} — Your Inner Pairing"), Spacer(1,2),
        body(f"Your Driver ({cr_b['planet'].split(' ')[0]}) sets how you act day to day; your Conductor — Life Path {r['life_path']} ({cr_lp['planet'].split(' ')[0]}) — sets where that action is meant to go. " + ("These energies cooperate naturally, giving you a smooth inner rhythm." if r['name_friendly'] else "Learning to align these two energies is one of your life's quiet but important tasks."))], border=GOLD_D)]
    S+=[Spacer(1,6), Panel([h3("Lucky Days & Colours")]+bullets([
        f"Power day: <b>{cr_b['day']}</b>",
        f"Favourable colours: <b>{cr_b['colour']}</b>",
        f"Supportive gemstone: <b>{cr_b['gem']}</b> (consult before wearing)",
        f"Harmonised numbers: <b>{', '.join(map(str,r['lucky_numbers'][:5]))}</b>",
    ])) ]
    S+=[PageBreak()]
    return S

def sec_maturity(r):
    cr_m=core(r['maturity'])
    S=[kicker("Your Second Half"), h1("Maturity Number"), GoldRule(), Spacer(1,4)]
    S+=[BigNum(r['maturity'], cr_m['planet']), Spacer(1,4)]
    S+=[Paragraph(f"Life Path {r['life_path']} + Destiny {r['destiny']} <font face='Cormorant-M'>\u2192</font> {r['maturity']}", ST['mutec']), Spacer(1,8)]
    S+=[lead(C.MATURITY_INTRO), Spacer(1,8)]
    S+=[body(f"From roughly age 35–40 onward, the {cr_m['planet']} vibration of the {cr_m['archetype']} rises to the surface of your life. " + cr_m['essence'])]
    S+=[Spacer(1,8), Panel([h3("Preparing For Your Harvest")]+bullets(cr_m['strengths'][:4]))]
    S+=[Spacer(1,6), body("Knowing this early is a gift: you can consciously plant, through your 20s and 30s, the seeds whose fruit this number describes — so that your second half arrives as fulfilment rather than surprise.")]
    S+=[PageBreak()]
    return S

def sec_lo_shu(r):
    S=[kicker("Your Cosmic Blueprint Grid"), h1("Lo Shu Grid Analysis"), GoldRule(), Spacer(1,4)]
    S+=[body("The Lo Shu Grid is an ancient 3×3 magic square. By placing the digits of your birth date (with your Driver and Conductor) into their fixed cells, we reveal which planetary energies you carry in abundance, which are missing, and which rare 'arrows' or planes you possess.")]
    S+=[Spacer(1,8), LoShuGrid(r['grid_counts']), Spacer(1,8)]
    present=[f"<b>{n}×{c}</b>" for n,c in sorted(r['grid_counts'].items()) if c>0]
    S+=[Panel([h3("Numbers Present In Your Grid"), Spacer(1,2),
               body("&nbsp;&nbsp;".join(present) if present else "—")])]
    S+=[Spacer(1,6)]
    if r['repeated']:
        rep=[h3("Repeated Numbers — Amplified Energies")]
        for n,c in sorted(r['repeated'].items()):
            rep.append(Paragraph(f'<font face="Cormorant-M" color="#7C2E38">◆</font>&nbsp; <b>{str(n)*c} ({n} appears {c}×):</b> {C.REPEATED.get(n,"")}', ST['bullet']))
            rep.append(Spacer(1,3))
        S+=[Panel(rep)]; S+=[Spacer(1,6)]
    if r['complete_planes']:
        pl=[h3("Power Planes & Arrows You Possess")]
        for p in r['complete_planes']:
            pl.append(Paragraph(f'<font face="Cormorant-M" color="#7C2E38">◆</font>&nbsp; {C.PLANE_MEANING.get(p,p)}', ST['bullet']))
            pl.append(Spacer(1,3))
        S+=[Panel(pl, border=GOLD_D)]
    else:
        S+=[Panel([h3("Planes"), body("No fully-complete plane or arrow is present — common and not a weakness. Strengthening your missing numbers is the fastest way to begin forming one.")])]
    S+=[PageBreak()]
    return S

def sec_hidden_passion(r):
    hp=r['hidden_passion']
    S=[kicker("Your Driving Force"), h1("Hidden Passion Number"), GoldRule(), Spacer(1,4)]
    S+=[body("Your Hidden Passion is the number that appears most often in your name's Chaldean values — the talent so natural you may not even notice it. It is the secret engine behind your ambitions.")]
    S+=[Spacer(1,8)]
    for n in hp:
        crh=core(n)
        S+=[Panel([Paragraph(f'<font color="#1E2C50" size="22" face="Cinzel-B">{n}</font> &nbsp; <font color="#8C8472" face="Cormorant-I" size="13">{crh["planet"]} — {crh["archetype"]}</font>', ST['h3']),
                   Spacer(1,4),
                   body(f"A dominant {n} means {crh['archetype']}'s energy runs through everything you do. " + crh['essence'])], border=GOLD_D)]
        S+=[Spacer(1,6)]
        S+=[Panel([h3("How This Passion Shows Up In You")]+bullets(crh['strengths'][:4]))]
        S+=[Spacer(1,6)]
    S+=[body("Channelled consciously, your Hidden Passion becomes your signature strength — the thing people seek you out for. Ignored, it leaks out as restlessness. Build a life that lets it express.")]
    S+=[PageBreak()]
    return S

def sec_karmic_lessons(r):
    kl=r['karmic_lessons']
    S=[kicker("What Your Soul Came To Learn"), h1("Karmic Lessons"), GoldRule(), Spacer(1,4)]
    S+=[body("Karmic Lessons are the number-energies missing from your name in the Chaldean system. They mark the qualities your soul has not yet mastered across lifetimes — the areas life will lovingly (and repeatedly) push you to develop.")]
    S+=[Spacer(1,8)]
    if kl:
        for n in kl:
            S+=[Panel([Paragraph(f'<font face="Cormorant-M" color="#7C2E38">◆</font>&nbsp; <b>{C.KARMIC_LESSON.get(n,"")}</b>', ST['bullet'])])]
            S+=[Spacer(1,5)]
        S+=[Spacer(1,4), body("These are not flaws — they are your curriculum. Each time you consciously practice the missing quality instead of avoiding it, you 'complete' that lesson and unlock the planet's gift.")]
    else:
        S+=[Panel([h3("A Rare Completeness"), body("Remarkably, your name contains every Chaldean number value — you carry no formal Karmic Lessons. This suggests a soul that has balanced these energies in past cycles. Your work this life is less about learning missing qualities and more about masterfully applying what you already hold.")], border=GOLD_D)]
    S+=[PageBreak()]
    return S

def sec_karmic_debt(r):
    kd=r['karmic_debts']
    S=[kicker("Debts Carried Forward"), h1("Karmic Debt Analysis"), GoldRule(), Spacer(1,4)]
    S+=[body("Certain numbers — 13, 14, 16 and 19 — when they appear in your core calculations, indicate Karmic Debt: energy borrowed in a past cycle, repaid in this one. They are not punishments but accelerated lessons. Recognising them is the first step to clearing them.")]
    S+=[Spacer(1,8)]
    if kd:
        for n in kd:
            S+=[Panel([Paragraph(f'<font color="#1E2C50" size="18" face="Cinzel-B">{n}</font>', ST['h3']), Spacer(1,3),
                       body(C.KARMIC_DEBT.get(n,""))], border=GOLD_D)]
            S+=[Spacer(1,6)]
        S+=[body("The remedy for every karmic debt is the same in spirit: stop avoiding the lesson. The moment you embrace the discipline it demands, the 'debt' converts into one of your most powerful assets.")]
    else:
        S+=[Panel([h3("No Karmic Debt Numbers Present"), body("Your core numbers carry none of the karmic-debt vibrations (13, 14, 16, 19). This is fortunate — your path is less burdened by repayment cycles, leaving more energy free for forward growth. Focus your attention on your Karmic Lessons and Pinnacle cycles instead.")], border=GOLD_D)]
    S+=[PageBreak()]
    return S

def sec_pinnacles(r):
    S=[kicker("The Four Seasons Of Your Life"), h1("Pinnacle Cycles"), GoldRule(), Spacer(1,4)]
    S+=[body("Your life unfolds in four great Pinnacle cycles, each governed by a number and a ruling planet. Each pinnacle brings its own opportunities, themes and 'cosmic weather'. Knowing which season you are in lets you plant the right seeds at the right time.")]
    S+=[Spacer(1,8)]
    rows=[[Paragraph('<font color="#1E2C50">Pinnacle</font>',ST['mute']),
           Paragraph('<font color="#1E2C50">Number</font>',ST['mute']),
           Paragraph('<font color="#1E2C50">Age Span</font>',ST['mute']),
           Paragraph('<font color="#1E2C50">Cosmic Theme</font>',ST['mute'])]]
    for i,p in enumerate(r['pinnacles'],1):
        note=C.PINNACLE_NOTE.get(p['num'], C.PINNACLE_NOTE.get(N.reduce_num(p['num'],False),''))
        rows.append([Paragraph(f"{i}st" if i==1 else f"{i}{'nd' if i==2 else 'rd' if i==3 else 'th'}",ST['body']),
                     Paragraph(f'<font color="#1E2C50" face="Cinzel-B" size="13">{p["num"]}</font>',ST['body']),
                     Paragraph(p['span'],ST['body']),
                     Paragraph(note,ST['body'])])
    t=Table(rows, colWidths=[16*mm,16*mm,34*mm,None])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),0.4,LINE),
        ('LINEBELOW',(0,0),(-1,0),0.8,GOLD_D)]))
    S+=[t, Spacer(1,8)]
    S+=[Panel([body("Tip: when a new pinnacle begins, the transition year often feels turbulent — old structures end to make room for the new theme. This is normal. Lean into the incoming number's energy rather than clinging to the last cycle.")])]
    S+=[PageBreak()]
    return S

def sec_challenges(r):
    S=[kicker("Lessons Disguised As Obstacles"), h1("Challenge Numbers"), GoldRule(), Spacer(1,4)]
    S+=[body("Running alongside your Pinnacles are four Challenge numbers — the specific inner obstacles you must work through in each phase. They are low (0–8) by design: small, repeated tests rather than grand catastrophes. Mastering a challenge is what unlocks the corresponding pinnacle's reward.")]
    S+=[Spacer(1,8)]
    labels=["First Challenge (early life)","Second Challenge (mid life)","Main Challenge (lifelong)","Fourth Challenge (later life)"]
    for lbl,ch in zip(labels, r['challenges']):
        S+=[Panel([Paragraph(f'<font color="#1E2C50" face="Cinzel-B" size="16">{ch}</font> &nbsp; <font color="#8C8472">{lbl}</font>', ST['h3']),
                   Spacer(1,2), body(C.CHALLENGE.get(ch, C.CHALLENGE[0]))])]
        S+=[Spacer(1,5)]
    S+=[body("Notice your Main Challenge especially — it recurs throughout life until consciously resolved. The good news: every challenge is winnable, and each victory permanently strengthens that part of your character.")]
    S+=[PageBreak()]
    return S

def sec_career(r):
    cr_lp=core(r['life_path'])
    S=[kicker("Where You Are Built To Win"), h1("Career Blueprint"), GoldRule(), Spacer(1,4)]
    S+=[body(f"Your career direction is read primarily from your Life Path ({r['life_path']}, {cr_lp['planet'].split(' ')[0]}) and Destiny ({r['destiny']}, {core(r['destiny'])['planet'].split(' ')[0]}). Together they reveal the fields where your natural wiring becomes a paid advantage.")]
    S+=[Spacer(1,8)]
    S+=[Panel([h3(f"Life Path {r['life_path']} — Your Core Vocation"), Spacer(1,2),
               body(C.CAREER.get(r['life_path'], C.CAREER[N.reduce_num(r['life_path'],False)]))], border=GOLD_D)]
    S+=[Spacer(1,6)]
    if N.reduce_num(r['destiny'],False)!=N.reduce_num(r['life_path'],False):
        S+=[Panel([h3(f"Destiny {r['destiny']} — Your Professional Style"), Spacer(1,2),
                   body(C.CAREER.get(r['destiny'], C.CAREER[N.reduce_num(r['destiny'],False)]))])]
        S+=[Spacer(1,6)]
    S+=[Panel([h3("The Veshann Astro Career Rule"), body("Choose roles where your Life Path energy is the main skill being paid for. A natural leader in a follower's seat, or a free-spirited 5 trapped in rigid routine, will underperform no matter how talented. Align the chair to the number.")])]
    S+=[PageBreak()]
    return S

def sec_wealth(r):
    cr_lp=core(r['life_path'])
    S=[kicker("Your Money Frequency"), h1("Wealth Blueprint"), GoldRule(), Spacer(1,4)]
    S+=[body("Money flows differently for every number. Your wealth pattern is shaped by your Driver and Life Path — how you naturally attract, hold and grow resources, and where your characteristic money-leaks appear.")]
    S+=[Spacer(1,8)]
    S+=[Panel([h3(f"Life Path {r['life_path']} — How Wealth Comes To You"), Spacer(1,2),
               body(C.WEALTH.get(r['life_path'], C.WEALTH[N.reduce_num(r['life_path'],False)]))], border=GOLD_D)]
    S+=[Spacer(1,6)]
    if N.reduce_num(r['driver'],False)!=N.reduce_num(r['life_path'],False):
        S+=[Panel([h3(f"Driver {r['driver']} — Your Spending Nature"), Spacer(1,2),
                   body(C.WEALTH.get(r['driver'], C.WEALTH[N.reduce_num(r['driver'],False)]))])]
        S+=[Spacer(1,6)]
    S+=[Panel([h3("Wealth Activation"), body(f"Strengthen the planet of your Life Path ({cr_lp['planet']}) through its remedy, keep your harmonised numbers ({', '.join(map(str,r['lucky_numbers'][:4]))}) near key financial decisions and dates, and plug the specific leak named above. Consistency, not intensity, compounds wealth.")], border=GOLD_D)]
    S+=[PageBreak()]
    return S

def sec_love(r):
    S=[kicker("Your Heart In Relationship"), h1("Love & Relationship Blueprint"), GoldRule(), Spacer(1,4)]
    S+=[body(f"In love, your Soul Urge ({r['soul_urge']}) reveals what your heart secretly needs, while your Life Path ({r['life_path']}) shapes how you show up for a partner. Read both together for the full picture.")]
    S+=[Spacer(1,8)]
    S+=[Panel([h3(f"Life Path {r['life_path']} — How You Love"), Spacer(1,2),
               body(C.LOVE.get(r['life_path'], C.LOVE[N.reduce_num(r['life_path'],False)]))], border=GOLD_D)]
    S+=[Spacer(1,6)]
    if N.reduce_num(r['soul_urge'],False)!=N.reduce_num(r['life_path'],False):
        S+=[Panel([h3(f"Soul Urge {r['soul_urge']} — What Your Heart Craves"), Spacer(1,2),
                   body(C.LOVE.get(r['soul_urge'], C.LOVE[N.reduce_num(r['soul_urge'],False)]))])]
        S+=[Spacer(1,6)]
    S+=[Panel([h3("Compatibility Note"), body(f"Your most harmonious partner numbers are <b>{', '.join(map(str,r['lucky_numbers'][:5]))}</b>. But numbers describe tendency, not destiny — conscious love, communication and the remedies in this report can harmonise almost any pairing. For a full couple's compatibility reading, a personal Veshann Astro consultation is recommended.")])]
    S+=[PageBreak()]
    return S

def sec_personal_year(r):
    py=r['personal_year']
    S=[kicker("Your Cosmic Weather"), h1(f"Personal Year Forecast — {r['personal_year_for']}"), GoldRule(), Spacer(1,4)]
    S+=[BigNum(py, f"Personal Year {py}"), Spacer(1,4)]
    S+=[lead(f"You are currently in a Personal Year {py}. Within the nine-year cycle that governs every life, this year carries a distinct theme — and aligning your major decisions with it is one of the most practical uses of numerology.")]
    S+=[Spacer(1,8), Panel([h3(f"The Theme Of Your {r['personal_year_for']}"), Spacer(1,2), body(C.PERSONAL_YEAR[py])], border=GOLD_D)]
    S+=[Spacer(1,8), h2("The Nine-Year Cycle Ahead")]
    nxt=[]
    for k in range(1,4):
        ny=N.reduce_num(py+k if py+k<=9 else py+k-9, False)
        nxt.append(f"<b>{r['personal_year_for']+k} (Personal Year {ny}):</b> {C.PERSONAL_YEAR[ny].split('.')[0]}.")
    S+=[Panel([Paragraph(f'<font face="Cormorant-M" color="#7C2E38">◆</font>&nbsp; {n}', ST['bullet']) for n in nxt])]
    S+=[PageBreak()]
    return S

def sec_roadmap(r):
    S=[kicker("Your Next 90 Days"), h1("90-Day Career & Luck Roadmap"), GoldRule(), Spacer(1,4)]
    S+=[lead(C.ROADMAP_INTRO), Spacer(1,10)]
    crd=core(r['driver'])
    for ph in r['roadmap']:
        theme, career_txt, luck_txt = C.PERSONAL_MONTH[ph['pm']]
        crp=core(ph['pm'])
        mlabel=f"{MONTHS[ph['month']]} {ph['year']}"
        pdates=", ".join(str(d) for d in ph['power_dates']) if ph['power_dates'] else "all favourable days below"
        head=Paragraph(
            f'<font color="#1E2C50" face="Cinzel-B" size="15">{ph["pm"]}</font>'
            f'&nbsp;&nbsp;<font color="#8C8472" face="Jost-M" size="8">{ph["day_range"].upper()} &nbsp;·&nbsp; {mlabel.upper()}</font><br/>'
            f'<font color="#1E2C50" face="Cormorant-SB" size="14">{theme}</font>'
            f'&nbsp; <font color="#8C8472" face="Cormorant-I" size="11">— Personal Month {ph["pm"]}, {crp["planet"].split(" (")[0]}</font>',
            ST['h3'])
        rows=[head, Spacer(1,4), body(career_txt), Spacer(1,3), body(luck_txt), Spacer(1,5),
              Paragraph(f'<font face="Cormorant-M" color="#7C2E38">◆</font>&nbsp; <font color="#8C8472">Power dates:</font> <b>{pdates}</b>'
                        f'&nbsp;&nbsp;|&nbsp;&nbsp; <font color="#8C8472">Lucky day:</font> <b>{crd["day"]}</b>'
                        f'&nbsp;&nbsp;|&nbsp;&nbsp; <font color="#8C8472">Colour:</font> <b>{crd["colour"].split(",")[0]}</b>', ST['bullet'])]
        S+=[Panel(rows, border=GOLD_D)]
        S+=[Spacer(1,8)]
    S+=[Panel([body("Print this page or set three calendar reminders — one per month. Acting on the right energy at the right time is the single highest-leverage habit in practical numerology. For a deeper, date-by-date personal forecast, a live Veshann Astro consultation maps your entire year.")])]
    S+=[PageBreak()]
    return S

def sec_name_analysis(r):
    S=[kicker("Tuning Your Vibration"), h1("Name Analysis & Correction"), GoldRule(), Spacer(1,4)]
    S+=[body(f"In the Chaldean system, your name is a living sound-frequency. The name <b>{r['name']}</b> carries a Destiny vibration of <b>{r['destiny']}</b> ({core(r['destiny'])['planet']}), while your birth gives a Driver of <b>{r['driver']}</b> and Conductor of <b>{r['life_path']}</b>.")]
    S+=[Spacer(1,8)]
    S+=[kv_table([
        ("Name (as analysed)", r['name']),
        ("Chaldean name total", f"{r['destiny_total']} <font face='Cormorant-M'>\u2192</font> {r['destiny']}"),
        ("Destiny planet", core(r['destiny'])['planet']),
        ("Birth Driver / Conductor", f"{r['driver']} / {r['life_path']}"),
        ("Vibration match", "Harmonious ✓" if r['name_friendly'] else "Mismatch — tuning advised"),
    ])]
    S+=[Spacer(1,10)]
    if r['name_friendly']:
        S+=[Panel([h3("Good News — Your Name Already Supports You"), body(f"Your name's Destiny vibration ({r['destiny']}) sits in harmony with your birth numbers. No correction is required. You may simply ensure you consistently use this spelling in signatures, branding and official documents to keep the frequency strong.")], border=GOLD_D)]
    else:
        S+=[Panel([h3("A Gentle Tuning Is Advised"), body(f"Your name's Destiny vibration ({r['destiny']}) is not fully aligned with your Driver ({r['driver']}) and Conductor ({r['life_path']}). This can create subtle friction — effort that doesn't quite convert into result. A small adjustment (an added or altered letter, or a preferred spelling) can shift the total toward a harmonised number such as {', '.join(map(str,r['lucky_numbers'][:3]))}.")], border=GOLD_D)]
        S+=[Spacer(1,6), Panel([h3("Why We Don't Print A 'Corrected' Spelling Here"), body("Name correction is delicate — it must account for your full chart, family naming, numerological gender rules and practical use. An automated suggestion can mislead. Your Veshann Astro numerologist will hand-craft 2–3 safe, powerful spelling options in a personal session. This is one of our most-requested services for a reason.")])]
    S+=[Spacer(1,6), Paragraph('<font color="#1E2C50" face="Cormorant-I" size="13">Book a personal Name Correction consultation at veshannastro.co.in</font>', ST['quote'])]
    S+=[PageBreak()]
    return S

def sec_action_plan(r):
    cr_lp=core(r['life_path']); kl=r['karmic_lessons']; py=r['personal_year']
    S=[kicker("From Insight To Action"), h1("Your Veshann Astro Action Plan"), GoldRule(), Spacer(1,4)]
    S+=[body("Knowledge without action is just entertainment. Here is your personalised starter plan, drawn from everything above. Begin with three; add more as they become habit.")]
    S+=[Spacer(1,6)]
    actions=[
        f"Adopt the core remedy for your Life Path {r['life_path']} ({cr_lp['planet']}) — start this {cr_lp['day']}.",
        f"Keep your harmonised numbers ({', '.join(map(str,r['lucky_numbers'][:4]))}) in mind for important dates, mobile numbers and decisions.",
        f"Strengthen your weakest area: " + (f"work consciously on your Karmic Lesson(s) {', '.join(map(str,kl))}." if kl else f"activate your missing grid number(s) {', '.join(map(str,r['missing']))}." if r['missing'] else "maintain balance across all your strong numbers."),
        f"Align this year's big moves with your Personal Year {py} theme.",
        "Wear or keep your supportive colours on your power day each week.",
    ]
    S+=[Panel([Paragraph(f'<font color="#7C2E38" face="Cinzel-B">{i}.</font>&nbsp;&nbsp; {a}', ST['bullet']) for i,a in enumerate(actions,1)], border=GOLD_D)]
    S+=[Spacer(1,10)]
    S+=[h2("The Veshann Astro Difference")]
    usp_rows=[]; row=[]
    for t,d in C.USP_POINTS:
        row.append(Panel([Paragraph(f'<font color="#1E2C50"><font face="Cormorant-M">◆</font> {t}</font>', ST['h3']), Spacer(1,2),
                          Paragraph(d, ST['mute'])], pad=9, bg=DEEP2))
        if len(row)==2: usp_rows.append(row); row=[]
    if row: row.append(Spacer(1,1)); usp_rows.append(row)
    ut=Table(usp_rows, colWidths=[(PW-2*MARGIN-12)/2-4]*2)
    ut.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
    S+=[ut]
    S+=[PageBreak()]
    return S

def sec_book_ad(r):
    S=[Spacer(1,8*mm)]
    S+=[Paragraph("GO DEEPER", ParagraphStyle('gd',fontName="Jost-M",fontSize=9,textColor=GOLD,alignment=TA_CENTER,tracking=4)), Spacer(1,4)]
    S+=[Paragraph("Continue Your Cosmic Journey", ST['h1c']), Spacer(1,4), GoldRule(), Spacer(1,10)]
    S+=[Paragraph("From the Veshann Astro library", ST['quote']), Spacer(1,12)]
    S+=[BookAd(BOOK)]
    S+=[Spacer(1,16)]
    S+=[Panel([Paragraph('<font color="#1E2C50" face="Cinzel">Your reading doesn\'t end here</font>', ST['h3']), Spacer(1,3),
        body("This report reveals your map. A live consultation reveals the road. Explore One-Question Voice Consultations, in-depth Numerology Reports, Palmistry and complete Kundli analysis — each crafted personally by our practising astrologer.")], border=GOLD_D)]
    S+=[Spacer(1,10), Paragraph('<font color="#1E2C50" face="Cormorant-I" size="15">veshannastro.co.in &nbsp;·&nbsp; @veshann.astro</font>',
        ParagraphStyle('fin',fontName="Cormorant-I",fontSize=15,textColor=GOLD_L,alignment=TA_CENTER))]
    S+=[Spacer(1,4), Paragraph("Thank you for trusting Veshann Astro with your cosmic blueprint.", ST['mutec'])]
    return S

def _two_panels(left_title, left_items, right_title, right_items, rg='◇'):
    sp = Table([[
        Panel([h3(left_title)] + bullets(left_items), bg=DEEP2),
        Panel([h3(right_title)] + bullets(right_items, glyph=rg), bg=HexColor("#EAEDF3")),
    ]], colWidths=[(PW-2*MARGIN-12)/2-4]*2)
    sp.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(0,0),8),('RIGHTPADDING',(1,0),(1,0),0),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    return sp

def sec_mobile(r):
    m = r.get('mobile') or dict(number='(not provided)', total=0, root=r['driver'], planet=core(r['driver'])['planet'])
    cr = core(m['root']); friendly = m['root'] in set(r['lucky_numbers'])
    S = [NextPageTemplate('content'), kicker("Your Number's Vibration"), h1("Mobile Number Analysis"), GoldRule(), Spacer(1,4)]
    S += [BigNum(m['root'], cr['planet']), Spacer(1,2)]
    S += [Paragraph(f"Number analysed: {m['number']} &nbsp;·&nbsp; total {m['total']} <font face='Cormorant-M'>\u2192</font> {m['root']}", ST['mutec']), Spacer(1,6)]
    S += [lead(f"Every number you carry repeats a frequency. Your mobile number reduces to {m['root']}, ruled by {short_planet(m['root'])} \u2014 the energy travelling with every call, payment and contact you make.")]
    S += [body(cr['essence']), Spacer(1,6)]
    S += [_two_panels('What This Number Supports', cr['strengths'], 'What To Watch', cr['shadow']), Spacer(1,8)]
    S += [Panel([h3("Harmony With Your Chart"), body(
        f"Your Driver is {r['driver']} and Life Path {r['life_path']}. A mobile root of {m['root']} is " +
        ("in natural harmony with your core numbers \u2014 this is a supportive number to keep."
         if friendly else
         f"not fully aligned with your core numbers. Numbers whose digits add to {', '.join(map(str,r['lucky_numbers'][:3]))} would support you more strongly."))],
        border=GOLD_D), Spacer(1,8)]
    S += [Panel([h3("Lucky-Number Recommendations"), body(
        f"When choosing any number you use daily \u2014 SIM, UPI handle, key account \u2014 favour totals that reduce to "
        f"<b>{', '.join(map(str,r['lucky_numbers'][:4]))}</b>. Add all the digits; if the final single digit is one of these, the number sits with your fortune. "
        "A number is only as strong as the vibration it reduces to \u2014 the individual digits matter less than their total.")])]
    S += [PageBreak()]
    return S

def sec_business(r):
    b = r.get('business') or dict(name='(not provided)', total=0, root=r['destiny'], planet=core(r['destiny'])['planet'])
    cr = core(b['root']); friendly = b['root'] in set(r['lucky_numbers'])
    S = [NextPageTemplate('content'), kicker("Your Business Name's Vibration"), h1("Business Name Report"), GoldRule(), Spacer(1,4)]
    S += [BigNum(b['root'], cr['planet']), Spacer(1,2)]
    S += [Paragraph(f"Name analysed: {b['name']} &nbsp;·&nbsp; Chaldean total {b['total']} <font face='Cormorant-M'>\u2192</font> {b['root']}", ST['mutec']), Spacer(1,6)]
    S += [lead(f"A business name is its energetic signature \u2014 the frequency every customer, invoice and signboard repeats. \u201c{b['name']}\u201d reduces to {b['root']}, the vibration of {short_planet(b['root'])}.")]
    S += [body(cr['essence']), Spacer(1,6)]
    S += [Panel([h3("Alignment With Growth & Prosperity"), body(
        "This vibration broadcasts " + ", ".join(s.lower() for s in cr['strengths'][:3]) + ". " +
        (f"It harmonises with your own numbers (Driver {r['driver']}, Life Path {r['life_path']}) \u2014 a strong foundation to build on."
         if friendly else
         f"It is not fully aligned with your own numbers (Driver {r['driver']}, Life Path {r['life_path']}); the alternatives below tune it toward stronger support."))],
        border=GOLD_D), Spacer(1,8)]
    S += [h3("Three to Five Aligned Alternatives"), Spacer(1,3)]
    rows = []
    for tr in (r['lucky_numbers'][:5] or [1,3,5]):
        crt = core(tr)
        rows.append((f"Root {tr} · {short_planet(tr)}",
                     f"{crt['archetype']} energy \u2014 names totalling {tr} attract {', '.join(s.lower() for s in crt['strengths'][:2])}. Tune the spelling so the Chaldean total reduces to {tr}."))
    S += [kv_table(rows), Spacer(1,8)]
    S += [Panel([h3("Putting It Into Practice"), body(
        "Adopt the chosen name consistently across signage, domain, invoices and social handles \u2014 repetition is what charges a name. "
        "A small spelling change (an added or doubled letter) is usually enough to reach a target total. For a hand-tuned shortlist verified against your full chart, a personal consultation refines the final choice.")])]
    S += [PageBreak()]
    return S

def sec_baby(r):
    cd, cl = r['driver'], r['life_path']
    targets = (r.get('baby') or {}).get('target_roots') or (r['lucky_numbers'][:4] or [cd])
    pref = (r.get('baby') or {}).get('pref', '')
    bank = N.names_by_root(C.BABY_NAME_POOL)
    S = [NextPageTemplate('content'), kicker("Your Child's Core Numbers"), h1("Baby Name Report"), GoldRule(), Spacer(1,4)]
    S += [BigNum(cl, core(cl)['planet']), Spacer(1,2)]
    S += [Paragraph(f"Born {fmt_date(r['dob'])} &nbsp;·&nbsp; Driver {cd} &nbsp;·&nbsp; Life Path {cl}", ST['mutec']), Spacer(1,6)]
    S += [lead(f"Your child arrives carrying a Driver of {cd} and a Life Path of {cl} ({short_planet(cl)}). A well-chosen name is one whose vibration supports \u2014 never fights \u2014 these birth numbers.")]
    S += [body(core(cl)['essence']), Spacer(1,6)]
    if pref:
        S += [Panel([h3("Your Preference"), body(f"You noted: \u201c{pref}\u201d. The suggestions below honour this where the numbers allow.")]), Spacer(1,6)]
    S += [Panel([h3("What Makes a Name Harmonious"), body(
        f"In the Chaldean system a name's letters add to a total that reduces to a single root. For this child, names reducing to "
        f"<b>{', '.join(map(str,targets))}</b> sit in harmony with the birth numbers and gently amplify their strengths.")],
        border=GOLD_D), Spacer(1,8)]
    S += [h3("Name Suggestions"), Spacer(1,3)]
    rows = []
    for tr in targets:
        names = bank.get(tr, [])[:5]
        if names:
            crt = core(tr)
            rows.append((f"Root {tr} · {short_planet(tr)}",
                         ", ".join(names) + f" \u2014 carrying {', '.join(s.lower() for s in crt['strengths'][:2])}."))
    if not rows:
        rows = [("Guidance", "Choose a name whose Chaldean letters total a number reducing to one of the harmonious roots above.")]
    S += [kv_table(rows), Spacer(1,8)]
    S += [Panel([body(
        "Every name above already reduces to a harmonious root for your child. The final choice should also feel right to you as parents \u2014 sound, family meaning and tradition matter. "
        "For a hand-verified shortlist tuned to an exact birth time, a personal consultation is available.")])]
    S += [PageBreak()]
    return S

def sec_compatibility(r):
    p = r.get('partner')
    S = [NextPageTemplate('content'), kicker("Your Two Signatures"), h1("Numerology Compatibility"), GoldRule(), Spacer(1,4)]
    if not p or not p.get('dob'):
        note = f" (\u201c{r.get('extra','')}\u201d)" if r.get('extra') else ""
        S += [lead("A full compatibility reading compares two complete charts. I could not read a clear partner birth date from your entry" + note +
                   ", so this section focuses on your own relational numbers. Reply with your partner's name and date of birth and the complete couple's reading will follow.")]
        S += [PageBreak()]; return S
    rows = [
        ("", "<b>You</b> &nbsp;&nbsp; <b>Partner</b>"),
        ("Driver / Mulank", f"{r['driver']} &nbsp;&nbsp;&nbsp; {p['driver']}"),
        ("Life Path", f"{r['life_path']} &nbsp;&nbsp;&nbsp; {p['life_path']}"),
        ("Destiny", f"{r['destiny']} &nbsp;&nbsp;&nbsp; {p['destiny']}"),
        ("Soul Urge", f"{r['soul_urge']} &nbsp;&nbsp;&nbsp; {p['soul_urge']}"),
    ]
    harmonious = (p['life_path'] in set(r['lucky_numbers'])) or (r['life_path'] in set(p.get('lucky_numbers', [])))
    S += [body(f"Comparing <b>{r['name']}</b> and <b>{p['name']}</b> \u2014 two birth dates, one combined picture."), Spacer(1,6)]
    S += [kv_table(rows), Spacer(1,8)]
    S += [Panel([h3("Where You Harmonise"), body(
        ("Your Life Paths sit in a naturally supportive relationship \u2014 a strong foundation of shared rhythm and instinctive understanding."
         if harmonious else
         "Your Life Paths run on different tracks \u2014 not a barrier, but it means harmony is built consciously rather than assumed.") +
        f" Your Soul Urge ({r['soul_urge']}) and your partner's ({p['soul_urge']}) reveal what each heart privately needs; honouring both is the quiet key to closeness.")],
        border=GOLD_D), Spacer(1,8)]
    S += [Panel([h3("Where You'll Need Effort"), body(
        f"Differences between your Drivers ({r['driver']} and {p['driver']}) shape daily friction \u2014 pace, decision-making and how each of you reacts under stress. "
        "Name these openly; most conflict between numbers is mistranslation, not incompatibility.")], bg=HexColor("#EAEDF3")), Spacer(1,8)]
    S += [Panel([h3("Growing Closer"), body(
        "Numbers describe tendency, not destiny. Conscious communication, shared rituals and the remedies in each of your charts can harmonise almost any pairing. "
        "For a full session reading both charts together \u2014 timing, children, shared ventures \u2014 a personal Veshann Astro consultation goes deeper.")])]
    S += [PageBreak()]
    return S

# ---- section registry, recipes, tiers ----
SECTIONS = {
    'how_to_read': sec_how_to_read, 'snapshot': sec_snapshot, 'life_path': sec_life_path,
    'destiny': sec_destiny, 'soul_urge': sec_soul_urge, 'personality': sec_personality,
    'birthday': sec_birthday, 'maturity': sec_maturity, 'lo_shu': sec_lo_shu,
    'hidden_passion': sec_hidden_passion, 'karmic_lessons': sec_karmic_lessons,
    'karmic_debt': sec_karmic_debt, 'pinnacles': sec_pinnacles, 'challenges': sec_challenges,
    'career': sec_career, 'wealth': sec_wealth, 'love': sec_love,
    'personal_year': sec_personal_year, 'roadmap': sec_roadmap,
    'name_analysis': sec_name_analysis, 'action_plan': sec_action_plan,
    'mobile': sec_mobile, 'business': sec_business, 'baby': sec_baby, 'compatibility': sec_compatibility,
}

RECIPES = {
    'complete': ['how_to_read','snapshot','life_path','destiny','soul_urge','personality',
        'birthday','maturity','lo_shu','hidden_passion','karmic_lessons','karmic_debt',
        'pinnacles','challenges','career','wealth','love','personal_year','roadmap',
        'name_analysis','action_plan'],
    'snapshot': ['snapshot','life_path','destiny','birthday','action_plan'],
    'career':   ['snapshot','life_path','career','wealth','roadmap','action_plan'],
    'love':     ['snapshot','life_path','soul_urge','personality','love','compatibility','personal_year','action_plan'],
    'name':     ['snapshot','life_path','destiny','lo_shu','hidden_passion','name_analysis','action_plan'],
    'forecast': ['snapshot','life_path','personal_year','roadmap','pinnacles','challenges','action_plan'],
    'mobile':   ['snapshot','life_path','birthday','mobile','lo_shu','personal_year','action_plan'],
    'baby':     ['snapshot','life_path','birthday','maturity','lo_shu','pinnacles','baby','action_plan'],
    'business': ['snapshot','life_path','destiny','business','career','wealth','action_plan'],
}

TIERS = {
    'complete': ("Premium",             "COMPLETE NUMEROLOGY REPORT"),
    'snapshot': ("Personal",            "NUMEROLOGY SNAPSHOT"),
    'career':   ("Career & Wealth",     "NUMEROLOGY BLUEPRINT"),
    'love':     ("Love & Relationship", "NUMEROLOGY COMPATIBILITY"),
    'name':     ("Name & Lo Shu",       "NUMEROLOGY ANALYSIS"),
    'forecast': ("The Year Ahead",      "NUMEROLOGY FORECAST"),
    'mobile':   ("Mobile Number",       "NUMEROLOGY ANALYSIS"),
    'baby':     ("Baby Name",           "NUMEROLOGY REPORT"),
    'business': ("Business Name",       "NUMEROLOGY REPORT"),
}

def build_story(r, report_type='complete'):
    keys = RECIPES.get(report_type, RECIPES['complete'])
    tier, title = TIERS.get(report_type, TIERS['complete'])
    S = sec_cover(r, tier=tier, title=title)
    for k in keys:
        S += SECTIONS[k](r)
    S += sec_book_ad(r)
    return S

# ---- Book advertisement flowable ----
BOOK = dict(
    title="Numerology and Navagraha",
    subtitle="The Sacred Science of Numbers & the Nine Planets",
    blurb="The definitive guide blending Chaldean numerology with Vedic Navagraha wisdom — the very system this report is built on. Decode your numbers, understand the planets behind them, and apply authentic remedies. Now available on Amazon.",
    url="https://www.amazon.in/dp/B0H4P498S4",
    cover=None,
)

class BookAd(Flowable):
    def __init__(self, book, h=210):
        super().__init__(); self.b=book; self.h=h
    def wrap(self, aw, ah): self.aw=aw; return (aw, self.h)
    def draw(self):
        from reportlab.lib.utils import ImageReader
        c=self.canv; aw=self.aw; h=self.h
        c.setFillColor(DEEP2); c.setStrokeColor(GOLD_D); c.setLineWidth(0.8)
        c.roundRect(0,0,aw,h,8,stroke=1,fill=1)
        c.setFillColor(GOLD); c.rect(0,0,3,h,stroke=0,fill=1)
        cover_w=120; cover_h=170; cx=24; cy=(h-cover_h)/2
        if self.b.get('cover'):
            try:
                img=ImageReader(self.b['cover'])
                c.drawImage(img, cx, cy, cover_w, cover_h, mask='auto', preserveAspectRatio=True)
            except Exception:
                self._placeholder(c,cx,cy,cover_w,cover_h)
        else:
            self._placeholder(c,cx,cy,cover_w,cover_h)
        tx=cx+cover_w+24; tw=aw-tx-24
        from reportlab.platypus import Paragraph as PP
        def para(txt,style):
            p=PP(txt,style); _,ph=p.wrap(tw, h); return p,ph
        y=h-34
        p,ph=para('<font color="#8C8472" size="8">AMAZON BESTSELLER · VESHANN ASTRO</font>', ST['kicker']); p.drawOn(c,tx,y); y-=16
        p,ph=para(f'<font color="#1E2C50">{self.b["title"]}</font>', ST['h2']); p.drawOn(c,tx,y-ph+14); y-=ph+2
        p,ph=para(f'<font color="#262E3D" face="Cormorant-I" size="12">{self.b["subtitle"]}</font>', ST['cardsub']); p.drawOn(c,tx,y-ph+10); y-=ph+8
        p,ph=para(self.b['blurb'], ST['mute']); p.drawOn(c,tx,y-ph+12); y-=ph+12
        bw=150; bh=26; bx=tx; by=y-bh
        c.setFillColor(GOLD); c.roundRect(bx,by,bw,bh,4,stroke=0,fill=1)
        c.setFont("Jost-M",10); c.setFillColor(DEEP)
        c.drawCentredString(bx+bw/2-8, by+bh/2-3.5, "BUY ON AMAZON")
        ax=bx+bw/2+50; ay=by+bh/2
        c.setFillColor(DEEP)
        p=c.beginPath(); p.moveTo(ax,ay+3); p.lineTo(ax+6,ay); p.lineTo(ax,ay-3); p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setLineWidth(1.2); c.setStrokeColor(DEEP); c.line(ax-7,ay,ax+4,ay)
        c.linkURL(self.b['url'], (bx,by,bx+bw,by+bh), relative=0, thickness=0)
        c.linkURL(self.b['url'], (cx,cy,cx+cover_w,cy+cover_h), relative=0, thickness=0)
    def _placeholder(self, c, x, y, w, hh):
        import math
        c.setFillColor(HexColor("#EFE7D5")); c.setStrokeColor(GOLD); c.setLineWidth(1)
        c.roundRect(x,y,w,hh,4,stroke=1,fill=1)
        c.saveState(); c.translate(x+w/2, y+hh*0.62)
        c.setStrokeColor(GOLD_L); c.setLineWidth(0.6)
        for i in range(9):
            a=math.radians(i*40); c.line(0,0,16*math.cos(a),16*math.sin(a))
        c.setFillColor(GOLD); c.circle(0,0,3,fill=1,stroke=0); c.restoreState()
        c.setFont("Cinzel-B",10); c.setFillColor(GOLD_L)
        c.drawCentredString(x+w/2, y+hh*0.30, "NUMEROLOGY")
        c.drawCentredString(x+w/2, y+hh*0.30-13, "&")
        c.drawCentredString(x+w/2, y+hh*0.30-28, "NAVAGRAHA")
        c.setFont("Jost-L",6); c.setFillColor(MUTE)
        c.drawCentredString(x+w/2, y+10, "VESHANN ASTRO")

def build_report(r, out_path, book_cover=None, report_type='complete'):
    if book_cover: BOOK['cover']=book_cover
    doc=ReportDoc(out_path)
    doc.build(build_story(r, report_type=report_type))
    return out_path
