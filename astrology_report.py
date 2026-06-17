"""Premium Astrology Life Path PDF renderer using existing Veshann styling."""
from __future__ import annotations

from datetime import date
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, NextPageTemplate

from pdfbuild_base import ReportDoc, ST, GoldRule, Panel, bullets, GOLD, GOLD_L, GOLD_D, CREAM, MUTE, LINE, PW, MARGIN
import astrology as A

MONTHS=["","January","February","March","April","May","June","July","August","September","October","November","December"]
HOUSE_THEMES={1:"identity, body and direction",2:"family, speech and savings",3:"effort, courage and skills",4:"home, mother and peace",5:"education, creativity and children",6:"workload, health routines and competition",7:"marriage, clients and public dealings",8:"transformation, hidden matters and longevity themes",9:"fortune, dharma and mentors",10:"career, status and karma",11:"income, networks and gains",12:"foreign lands, sleep, expenses and liberation"}

def fmt_date(d): return f"{d.day} {MONTHS[d.month]} {d.year}"
def fmt_dt(dt): return dt.strftime("%d %B %Y, %H:%M %Z")
def deg(x): return f"{x:.2f} deg"
def kicker(t): return Paragraph(t.upper(), ST["kicker"])
def h1(t): return Paragraph(t, ST["h1"])
def h2(t): return Paragraph(t, ST["h2"])
def h3(t): return Paragraph(t, ST["h3"])
def body(t): return Paragraph(t, ST["body"])
def lead(t): return Paragraph(t, ST["lead"])

def page(kick, title, parts):
    return [NextPageTemplate("content"), kicker(kick), h1(title), GoldRule(), Spacer(1,4)] + parts + [PageBreak()]

def kv(rows):
    data=[[Paragraph(f'<font color="#8C8472">{k}</font>', ST["mute"]), Paragraph(v, ST["body"])] for k,v in rows if v is not None]
    t=Table(data, colWidths=[42, None])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),("LINEBELOW",(0,0),(-1,-2),0.35,LINE)]))
    return t

def rashi_chart_table(c):
    cells = []
    for sidx in range(12):
        cell = c["rashi_chart"][sidx]
        planets = ", ".join(cell["planets"]) or "-"
        cells.append(Paragraph(
            f'<font color="#8C8472" size="7">House {cell["house"]}</font><br/>'
            f'<font color="#1E2C50" face="Cinzel-B" size="10">{cell["sign"]}</font><br/>'
            f'<font color="#262E3D" size="8">{planets}</font>', ST["mutec"]))
    t=Table([cells[0:4], cells[4:8], cells[8:12]], colWidths=[(PW-2*MARGIN)/4]*4, rowHeights=[52,52,52])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.35,LINE),("BACKGROUND",(0,0),(-1,-1),HexColor("#F8F2E8")),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return t

def pd(d):
    if hasattr(d, "date"):
        return d.strftime("%d %b %Y")
    return str(d)

def planet_line(c, p):
    v=c["planets"][p]
    asp = ", aspected by " + ", ".join(v.get("aspected_by", [])) if v.get("aspected_by") else ""
    return f"{p} in {v['sign']} house {v['house']} ({v['nakshatra']['name']} pada {v['nakshatra']['pada']}, {v['dignity']}{asp})"

def basis(c, items):
    return Panel([h3("Calculation Basis")] + bullets(items), bg=HexColor("#EAEDF3"))

def premium_block(basis_txt, verdict, why, guidance):
    return Panel([h3("Premium Reading")] + bullets([
        f"<b>Calculation basis:</b> {basis_txt}",
        f"<b>Clear verdict:</b> {verdict}",
        f"<b>Why this result came:</b> {why}",
        f"<b>Practical guidance:</b> {guidance}",
    ]), border=GOLD_D)

def cover(c):
    S=[NextPageTemplate("content"), Spacer(1,42), Paragraph("VESHANN ASTRO", ParagraphStyle("acv",fontName="Cinzel-B",fontSize=22,textColor=GOLD_L,alignment=TA_CENTER,leading=26,tracking=4))]
    S += [Paragraph("VEDIC ASTROLOGY LIFE PATH", ParagraphStyle("acv2",fontName="Jost-L",fontSize=8.5,textColor=MUTE,alignment=TA_CENTER,tracking=3,spaceBefore=4))]
    S += [Spacer(1,16), GoldRule(), Spacer(1,16)]
    S += [Paragraph("Premium", ParagraphStyle("at1",fontName="Cormorant-I",fontSize=30,textColor=CREAM,alignment=TA_CENTER,leading=30))]
    S += [Paragraph("ASTROLOGY LIFE PATH REPORT", ParagraphStyle("at2",fontName="Cinzel-B",fontSize=24,textColor=GOLD,alignment=TA_CENTER,leading=30,tracking=1))]
    S += [Spacer(1,20), Paragraph("Prepared exclusively for", ST["mutec"]), Spacer(1,4)]
    S += [Paragraph(c["name"].upper(), ParagraphStyle("anm",fontName="Cinzel-B",fontSize=18,textColor=GOLD_L,alignment=TA_CENTER,leading=24,tracking=1))]
    S += [Spacer(1,4), Paragraph(f"Born {fmt_date(c['dob'])} at {c['birth_time']} - {c['birth_place']}", ST["quote"])]
    S += [Spacer(1,22)]
    strip=Table([[
        Paragraph(f'<font color="#8C8472" size="7">LAGNA</font><br/><font color="#1E2C50" size="17" face="Cinzel-B">{c["ascendant"]["sign"]}</font>', ST["mutec"]),
        Paragraph(f'<font color="#8C8472" size="7">MOON</font><br/><font color="#1E2C50" size="17" face="Cinzel-B">{c["moon_sign"]}</font>', ST["mutec"]),
        Paragraph(f'<font color="#8C8472" size="7">NAKSHATRA</font><br/><font color="#1E2C50" size="15" face="Cinzel-B">{c["moon_nakshatra"]["name"]}</font>', ST["mutec"]),
        Paragraph(f'<font color="#8C8472" size="7">FOCUS</font><br/><font color="#1E2C50" size="14" face="Cinzel-B">{c["focus_area"].title()}</font>', ST["mutec"]),
    ]], colWidths=[(PW-2*MARGIN)/4]*4)
    strip.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LINEAFTER",(0,0),(-2,-1),0.5,LINE)]))
    S += [strip, Spacer(1,26), GoldRule()]
    S += [Paragraph(f"Prepared {fmt_date(c['prepared_date'])} - Lahiri ayanamsa - Swiss Ephemeris calculations", ST["mutec"]), PageBreak()]
    return S

def how_to_read(c):
    return page("Begin Here","How to Read This Report",[
        lead("This is a Vedic astrology life path guide based on calculated chart data: Lahiri sidereal positions, Lagna, Moon nakshatra, Vimshottari dasha, divisional charts and current gochar."),
        Spacer(1,8),
        Panel([h3("Prediction Rule"), body("Every prediction in this report is tied to at least one visible basis: house, planet, dasha, transit, divisional chart, nakshatra or Lagna/Moon reference. If a calculation is unavailable, it is not invented.")], border=GOLD_D),
        Spacer(1,8),
        Panel([h3("How To Use It")] + bullets(["Read the Executive Prediction Summary first.", "Use the dasha and five-year forecast for timing.", "Use remedies as supportive spiritual discipline, not as a replacement for practical effort."]))
    ])

def executive(c):
    md=c["dasha"]["current_mahadasha"]; ad=c["dasha"]["current_antardasha"]
    focus=c["focus_area"]
    tr=c["transits"]
    return page("Prediction Summary","Executive Prediction Summary",[
        lead(f"The chart indicates a {c['ascendant']['sign']} Lagna with Moon in {c['moon_sign']} and {c['moon_nakshatra']['name']} nakshatra. The current operating period is {md['lord']} Mahadasha with {ad['lord']} Antardasha, making this a {focus}-sensitive phase."),
        Spacer(1,7),
        Panel([h3("Current Phase")] + bullets([
            f"{md['lord']} Mahadasha can bring themes of house {c['planets'][md['lord']]['house']} because the dasha lord sits there in D1.",
            f"{ad['lord']} Antardasha activates {planet_line(c, ad['lord'])}.",
            f"Jupiter currently transits {tr['Jupiter']['sign']} in house {tr['Jupiter']['from_lagna']} from Lagna, supporting growth where that house is active.",
            f"Saturn currently transits {tr['Saturn']['sign']} in house {tr['Saturn']['from_lagna']} from Lagna, requiring discipline and patience."
        ]), border=GOLD_D),
        Spacer(1,7),
        Panel([h3("Best Action"), body(f"Your best action is to make {focus} decisions through timing, preparation and maturity rather than urgency. Avoid forcing decisions during periods when Saturn or Rahu activate pressure houses without dasha support.")], bg=HexColor("#F6ECEC")),
        Spacer(1,7),
        premium_block(
            f"Lagna {c['ascendant']['sign']}, Moon {c['moon_sign']}, {md['lord']}-{ad['lord']} dasha, Jupiter H{tr['Jupiter']['from_lagna']} and Saturn H{tr['Saturn']['from_lagna']}",
            f"This is a {focus}-sensitive timing phase, not a random general forecast.",
            f"The dasha lords activate houses {c['planets'][md['lord']]['house']} and {c['planets'][ad['lord']]['house']}, while slow transits set the outer pressure and support.",
            "Act when dasha and transit both support the decision; pause when Saturn/Rahu pressure is louder than Jupiter support."),
    ])

def foundation(c):
    md=c["dasha"]["current_mahadasha"]; ad=c["dasha"]["current_antardasha"]
    pdasha=c["dasha"]["current_pratyantardasha"]
    settings=c.get("calculation_settings", {})
    return page("Chart Data","Birth Chart Foundation",[
        kv([
            ("Lagna", f"{c['ascendant']['sign']} {deg(c['ascendant']['degree'])}"),
            ("Moon sign", c["moon_sign"]),
            ("Sun sign", c["sun_sign"]),
            ("Nakshatra / Pada", f"{c['moon_nakshatra']['name']} pada {c['moon_nakshatra']['pada']}"),
            ("Current dasha", f"{md['lord']} Mahadasha ({pd(md['start'])} to {pd(md['end'])})"),
            ("Current antardasha", f"{ad['lord']} Antardasha ({pd(ad['start'])} to {pd(ad['end'])})"),
            ("Current pratyantardasha", f"{pdasha['lord']} Pratyantardasha ({pd(pdasha['start'])} to {pd(pdasha['end'])})"),
            ("Strongest planets", ", ".join(c["strengths"]["strong_planets"])),
            ("Challenged planets", ", ".join(c["strengths"]["challenged_planets"])),
            ("House system", c.get("house_system", "Lahiri sidereal whole-sign houses from Lagna")),
        ]),
        Spacer(1,8),
        rashi_chart_table(c),
        Spacer(1,8),
        Panel([h3("Calculation Settings")] + bullets([
            f"Engine: {settings.get('engine', 'Swiss Ephemeris / pyswisseph')}",
            f"Ayanamsa: {settings.get('ayanamsa', 'Lahiri')} ({c.get('ayanamsa', 0):.4f} deg)",
            f"Zodiac: {settings.get('zodiac', 'Sidereal')}",
            f"Nodes: {settings.get('node_type', 'Mean Rahu/Ketu')}",
            f"Birth place source: {settings.get('place_source', c.get('place',{}).get('source','unknown'))}",
        ]), bg=HexColor("#EAEDF3")),
        Spacer(1,7),
        premium_block(
            "Swiss Ephemeris sidereal planetary longitudes, Lahiri ayanamsa, whole-sign houses, Moon nakshatra and Vimshottari dasha",
            "The report is calculation-led and only prints available systems.",
            "Ascendant, Moon and dasha establish the operating chart; divisional charts and transits are used as confirmation, not decoration.",
            "Use this page to verify birth data first; wrong time or place changes Lagna, houses and dasha interpretation."),
    ])

def lagna(c):
    asc=c["ascendant"]
    lord=c["house_lords"][1]
    return page("Self And Direction","Lagna / Ascendant Analysis",[
        lead(f"{asc['sign']} rises in the birth chart. The Lagna shows personality, body, direction and the repeating life pattern."),
        Spacer(1,8),
        Panel([h3("Life Pattern"), body(f"The Lagna lord is {lord}; {planet_line(c, lord)}. This makes house {c['planets'][lord]['house']} a central arena for identity and major life decisions.")], border=GOLD_D),
        Spacer(1,8), basis(c,[f"Lagna {asc['sign']} at {deg(asc['degree'])}", f"Lagna lord {lord} placed in house {c['planets'][lord]['house']}", f"Lagna nakshatra {asc['nakshatra']['name']} pada {asc['nakshatra']['pada']}"])
    ])

def moon(c):
    v=c["planets"]["Moon"]
    return page("Inner Life","Moon Sign & Mind Pattern",[
        lead(f"The Moon is in {v['sign']} and {v['nakshatra']['name']} nakshatra. This describes emotional rhythm, peace, mother connection and decision style."),
        Spacer(1,8),
        Panel([h3("Mind Pattern"), body(f"The chart indicates that emotional decisions are filtered through house {v['house']} matters. When this house is pressured by dasha or transit, the mind can feel more reactive; when supported, intuition becomes reliable.")], border=GOLD_D),
        Spacer(1,8), basis(c,[planet_line(c,"Moon"), f"Moon nakshatra lord: {v['nakshatra']['lord']}", f"Saturn transit from Moon: house {c['transits']['Saturn']['from_moon']}"])
    ])

def sun(c):
    v=c["planets"]["Sun"]
    return page("Soul Authority","Sun Sign & Soul Identity",[
        lead(f"The Sun is in {v['sign']} in house {v['house']}. It shows confidence, authority, father karma, leadership and self-respect."),
        Spacer(1,8),
        Panel([h3("Authority Pattern"), body(f"This Sun placement asks you to build confidence through the affairs of house {v['house']}: {HOUSE_THEMES[v['house']]}. The period supports leadership when dasha timing also activates Sun, 10th house or Lagna.")], border=GOLD_D),
        Spacer(1,8), basis(c,[planet_line(c,"Sun"), f"Sun dignity: {v['dignity']}", f"10th lord: {c['house_lords'][10]}"])
    ])

def nakshatra_page(c):
    n=c["moon_nakshatra"]
    return page("Karmic Instinct","Nakshatra & Pada Analysis",[
        lead(f"The Moon nakshatra is {n['name']} pada {n['pada']}, ruled by {n['lord']}. This is the emotional fingerprint of the chart."),
        Spacer(1,8),
        Panel([h3("Hidden Motivation"), body(f"Because the nakshatra lord is {n['lord']}, its placement becomes psychologically important: {planet_line(c, n['lord'])}. Emotional triggers and spiritual lessons often appear through house {c['planets'][n['lord']]['house']} matters.")], border=GOLD_D),
        Spacer(1,8), basis(c,[f"Moon longitude {deg(c['planets']['Moon']['longitude'])}", f"Nakshatra {n['name']} pada {n['pada']}", f"Nakshatra lord {n['lord']} in house {c['planets'][n['lord']]['house']}"])
    ])

def planet_table(c):
    rows=[[Paragraph("<b>Planet</b>",ST["mute"]),Paragraph("<b>Sign</b>",ST["mute"]),Paragraph("<b>Deg</b>",ST["mute"]),Paragraph("<b>House</b>",ST["mute"]),Paragraph("<b>Nakshatra</b>",ST["mute"]),Paragraph("<b>Status</b>",ST["mute"])]]
    for p,v in c["planets"].items():
        rows.append([Paragraph(p,ST["body"]),Paragraph(v["sign"],ST["body"]),Paragraph(deg(v["degree"]),ST["body"]),Paragraph(str(v["house"]),ST["body"]),Paragraph(f"{v['nakshatra']['name']} {v['nakshatra']['pada']}",ST["body"]),Paragraph((v["dignity"] + (" R" if v["retrograde"] else "")),ST["body"])])
    t=Table(rows, colWidths=[45,55,38,34,86,62])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.25,LINE),("BACKGROUND",(0,0),(-1,0),HexColor("#EAEDF3")),("FONTSIZE",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return page("Calculated Positions","Planetary Position Table",[t])

def houses_page(c):
    items=[]
    for h in range(1,13):
        lord=c["house_lords"][h]
        p=c["planets"][lord]
        items.append(f"<b>House {h}</b> ({HOUSE_THEMES[h]}): lord {lord} is in house {p['house']} in {p['sign']}.")
    return page("Life Areas","12-House Life Map",[lead("Each house describes a life department. The house lord shows where that department expresses itself."),Spacer(1,8),Panel([h3("House Map")] + bullets(items[:6]), border=GOLD_D),Spacer(1,7),Panel([h3("Houses 7-12")] + bullets(items[6:]))])

def topic_page(c, title, kick, houses, planets, extra_basis, text):
    b=[f"House {h} lord {c['house_lords'][h]} placed in house {c['planets'][c['house_lords'][h]]['house']}" for h in houses]
    b += [planet_line(c,p) for p in planets]
    b += extra_basis
    md=c["dasha"]["current_mahadasha"]["lord"]; ad=c["dasha"]["current_antardasha"]["lord"]
    verdict = f"This area is activated through houses {', '.join(map(str,houses))}, with current timing from {md}-{ad}."
    why = f"{md} sits in house {c['planets'][md]['house']} and {ad} sits in house {c['planets'][ad]['house']}; this is why the period must be read through those houses."
    guidance = "Take action when the relevant house lord, dasha lord and Jupiter support agree; use Saturn periods for discipline and correction."
    return page(kick,title,[lead(text),Spacer(1,8),Panel([h3("Prediction")] + bullets(prediction_lines(c, houses, planets)), border=GOLD_D),Spacer(1,8),premium_block("; ".join(b[:5]), verdict, why, guidance),Spacer(1,8),basis(c,b[:8])])

def prediction_lines(c, houses, planets):
    md=c["dasha"]["current_mahadasha"]["lord"]; ad=c["dasha"]["current_antardasha"]["lord"]
    lines=[f"The current {md}-{ad} dasha activates houses {c['planets'][md]['house']} and {c['planets'][ad]['house']}, so decisions should be timed through those life areas."]
    for h in houses[:2]:
        lord=c["house_lords"][h]
        lines.append(f"House {h} matters are carried by {lord}; its placement in house {c['planets'][lord]['house']} shows the practical channel for results.")
    if planets:
        p=planets[0]; v=c["planets"][p]
        lines.append(f"{p} in {v['sign']} house {v['house']} adds {v['dignity'].lower()} support and should be handled with maturity during transits.")
    return lines

def divisional(c):
    parts=[lead("Divisional charts confirm whether D1 promises receive support in specialised areas. D60 is intentionally not printed as a prediction because it is extremely birth-time sensitive.")]
    for name, data in c["divisional_charts"].items():
        if isinstance(data, dict) and data.get("available") is False:
            parts += [Spacer(1,5), Panel([h3(name), body(data["reason"])])]
        else:
            parts += [Spacer(1,5), Panel([h3(name), body(", ".join(f"{p}: {s}" for p,s in list(data.items())[:7]))])]
    return page("Varga Confirmation","Divisional Chart Deep Dive",parts)

def ashtakavarga(c):
    av=c["ashtakavarga"]
    if not av["available"]:
        return page("Strength Scores","Ashtakavarga Strength Analysis",[lead("Exact Ashtakavarga scoring is unavailable in this implementation, so no fake bindu scores are printed."),Spacer(1,8),Panel([h3("Unavailable") , body(av["reason"])], bg=HexColor("#F6ECEC"), border=GOLD_D),Spacer(1,8),Panel([h3("Replacement Used"), body(f"The report uses calculated planet dignity, house placement and house occupancy strength instead. Strong houses: {', '.join(map(str,c['houses']['strong_houses']))}. Caution houses: {', '.join(map(str,c['houses']['weak_houses']))}.")])])
    return []

def shadbala(c):
    sb=c.get("shadbala", {"available": False, "reason": "Full Shadbala is unavailable."})
    if not sb.get("available"):
        return page("Planetary Strength Module","Shadbala Status",[
            lead("Shadbala is not printed unless a validated bala calculation module is present."),
            Spacer(1,8),
            Panel([h3("Unavailable"), body(sb.get("reason", "Unavailable"))], bg=HexColor("#F6ECEC"), border=GOLD_D),
            Spacer(1,8),
            Panel([h3("Current Replacement"), body("The report uses dignity, house placement, retrograde status, graha drishti and dasha activation as transparent strength factors.")])
        ])
    return []

def dasha_page(c):
    md=c["dasha"]["current_mahadasha"]; ad=c["dasha"]["current_antardasha"]; pdasha=c["dasha"]["current_pratyantardasha"]
    upcoming=[f"{x['lord']}: {pd(x['start'])} to {pd(x['end'])}" for x in c["dasha"]["upcoming_antardashas"]]
    upcoming_p=[f"{x['lord']}: {pd(x['start'])} to {pd(x['end'])}" for x in c["dasha"].get("upcoming_pratyantardashas", [])]
    return page("Operating Period","Current Mahadasha / Antardasha / Pratyantardasha Prediction",[
        lead(f"The current period is {md['lord']} Mahadasha, {ad['lord']} Antardasha and {pdasha['lord']} Pratyantardasha."),
        Spacer(1,8),
        Panel([h3("What Opens And Tests")] + bullets([
            f"{md['lord']} opens house {c['planets'][md['lord']]['house']} themes because the Mahadasha lord is placed there.",
            f"{ad['lord']} gives immediate events through house {c['planets'][ad['lord']]['house']} and its sign {c['planets'][ad['lord']]['sign']}.",
            f"{pdasha['lord']} Pratyantardasha gives the near-term trigger through house {c['planets'][pdasha['lord']]['house']}.",
            f"This period requires caution where {md['lord']} or {ad['lord']} are challenged by dignity, retrograde status or pressure houses."
        ]), border=GOLD_D),
        Spacer(1,8), Panel([h3("Upcoming Antardashas")] + bullets(upcoming)),
        Spacer(1,8), Panel([h3("Upcoming Pratyantardashas")] + bullets(upcoming_p or ["Current pratyantardasha sequence is complete."]))
        ,Spacer(1,8),premium_block(
            f"Current Mahadasha {md['lord']}, Antardasha {ad['lord']}, Pratyantardasha {pdasha['lord']}",
            "Current events should be judged first through dasha, then through transit.",
            f"{md['lord']} shows the main chapter, {ad['lord']} shows the active sub-plot, and {pdasha['lord']} shows the near trigger.",
            "Avoid irreversible decisions when active dasha planets are weak, afflicted or placed in pressure houses unless practical circumstances require action.")
    ])

def forecast_overview(c):
    rows=[[Paragraph("<b>Year</b>",ST["mute"]),Paragraph("<b>Main Theme</b>",ST["mute"]),Paragraph("<b>Career</b>",ST["mute"]),Paragraph("<b>Money</b>",ST["mute"]),Paragraph("<b>Relationship</b>",ST["mute"]),Paragraph("<b>Best Action / Avoid</b>",ST["mute"])]]
    for snap in c["five_year_transits"]:
        tr=snap["transits"]
        jh=tr["Jupiter"]["from_lagna"]; sh=tr["Saturn"]["from_lagna"]; rh=tr["Rahu"]["from_lagna"]
        rows.append([Paragraph(str(snap["year"]),ST["body"]),Paragraph(f"Jupiter H{jh}, Saturn H{sh}",ST["body"]),Paragraph("Grow where D10 and H10 agree",ST["body"]),Paragraph("Use H2/H11 support cautiously",ST["body"]),Paragraph("Watch Venus/Jupiter timing",ST["body"]),Paragraph(f"Act with Jupiter H{jh} / avoid Rahu H{rh} haste",ST["body"])])
    t=Table(rows, colWidths=[30,70,70,58,68,82])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.25,LINE),("BACKGROUND",(0,0),(-1,0),HexColor("#EAEDF3")),("FONTSIZE",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    md=c["dasha"]["current_mahadasha"]["lord"]
    return page("Five-Year View","Five-Year Forecast Overview",[lead("This table combines current dasha, slow transits and activated houses from the report date."),Spacer(1,8),t,Spacer(1,8),premium_block(
        f"{md} Mahadasha plus annual Jupiter, Saturn and Rahu/Ketu transit snapshots",
        "The forecast gives timing themes, not guaranteed events.",
        "Slow planets create the climate, while dasha decides which part of the chart can actually deliver results.",
        "Use supportive Jupiter periods to initiate and Saturn periods to consolidate, repair or wait.")])

def year_detail(c, n):
    md=c["dasha"]["current_mahadasha"]["lord"]
    snap=c["five_year_transits"][n-1]
    year=snap["year"]
    tr=snap["transits"]
    jh=tr["Jupiter"]["from_lagna"]
    sh=tr["Saturn"]["from_lagna"]
    rh=tr["Rahu"]["from_lagna"]
    qs=[
        f"Q1: Use {md} dasha themes and prepare around house {c['planets'][md]['house']}.",
        f"Q2: Jupiter transits {tr['Jupiter']['sign']} and supports house {jh}: {HOUSE_THEMES[jh]}.",
        f"Q3: Saturn transits {tr['Saturn']['sign']} and asks discipline in house {sh}: {HOUSE_THEMES[sh]}.",
        f"Q4: Rahu in house {rh} can bring urgency; review commitments and avoid forcing decisions without dasha support.",
    ]
    return page(f"Year {n}",f"Year {n} Detailed Forecast - {year}",[
        lead(f"The chart indicates that {year} should be read through {md} Mahadasha, Jupiter house {jh} support and Saturn house {sh} discipline."),
        Spacer(1,8), Panel([h3("Quarter-wise Guidance")] + bullets(qs), border=GOLD_D),
        Spacer(1,8), basis(c,[f"Mahadasha lord {md} in house {c['planets'][md]['house']}", f"Calculated Jupiter transit: {tr['Jupiter']['sign']} house {jh}", f"Calculated Saturn transit: {tr['Saturn']['sign']} house {sh}", f"Calculated Rahu transit: {tr['Rahu']['sign']} house {rh}", f"Focus area: {c['focus_area']}"])
    ])

def remedies(c):
    weak=c["strengths"]["challenged_planets"][:3]
    items=[]
    for p in weak:
        day={"Sun":"Sunday","Moon":"Monday","Mars":"Tuesday","Mercury":"Wednesday","Jupiter":"Thursday","Venus":"Friday","Saturn":"Saturday","Rahu":"Saturday","Ketu":"Tuesday"}.get(p,"Thursday")
        items.append(f"{p}: strengthen through discipline on {day}, simple donation, mantra practice and ethical correction of house {c['planets'][p]['house']} matters.")
    items.append("Gemstones should be worn only after personal astrologer confirmation.")
    items.append("Every remedy must be paired with behaviour correction in the house ruled or occupied by that planet.")
    return page("Chart Remedies","Personalized Remedies",[lead("Remedies are selected from actually challenged planets and the current dasha context."),Spacer(1,8),Panel([h3("Recommended Supports")] + bullets(items), border=GOLD_D),Spacer(1,8),premium_block(
        "Challenged planets from dignity, house placement, retrograde status and malefic/benefic aspects",
        "Remedies are supportive discipline, not a shortcut or guarantee.",
        "A weak or pressured planet improves in lived experience when its behaviour is corrected consistently.",
        "Choose one mantra/day/donation/lifestyle discipline and repeat it steadily before adding more.")])

def lucky(c):
    lag=c["ascendant"]["sign"]; moon=c["moon_sign"]
    return page("Supports","Lucky Colours, Numbers, Directions & Timing",[
        lead("These supports are based on Lagna, Moon and current dasha lord, and should be used as gentle timing aids."),
        Spacer(1,8),
        kv([("Favourable colours", "Gold, white, yellow and clean earthy tones when they suit the occasion"),("Avoid colours", "Overly dull or heavy colours during low-energy periods"),("Favourable days", "Use the weekday of the current dasha lord and Lagna lord"),("Supportive directions", "East for clarity, North-East for learning, North for planning"),("Best timing windows", "When Jupiter supports Lagna/Moon houses and Saturn is not forcing rushed commitments"),("Manifestation routine", f"State the intention, act through {lag} Lagna discipline, and review with {moon} Moon emotional honesty")])
    ])

def dos_donts(c):
    return page("Practical Choices","What To Do / What Not To Do",[
        lead("This page converts the chart into grounded decision rules."),
        Spacer(1,8),
        Panel([h3("Do")] + bullets(["Use dasha-supported houses for major decisions.", "Let Saturn transits set the pace for long-term commitments.", "Use Jupiter periods for learning, mentors and expansion.", "Keep health routines simple and repeatable."]), border=GOLD_D),
        Spacer(1,7),
        Panel([h3("Do Not")] + bullets(["Do not force decisions during pressure periods.", "Do not treat remedies as substitutes for action.", "Do not use relationship timing to create fear.", "Do not take medical, legal or financial risks based only on astrology."]), bg=HexColor("#F6ECEC"))
    ])

def closing(c):
    return page("Closing","Closing Guidance",[
        lead(f"{c['name']}, this chart does not remove your free will. It shows the weather around your path, the timing of effort, and the houses where life asks you to grow."),
        Spacer(1,8),
        Panel([h3("Final Message"), body(f"The next five years are best handled by respecting the {c['dasha']['current_mahadasha']['lord']} dasha, using Jupiter's support wisely, and allowing Saturn to mature what cannot be rushed. Your best action is steady alignment, not fear.")], border=GOLD_D)
    ])

def story(c):
    S=cover(c)
    S += how_to_read(c)
    S += executive(c)
    S += foundation(c)
    S += lagna(c)
    S += moon(c)
    S += sun(c)
    S += nakshatra_page(c)
    S += planet_table(c)
    S += houses_page(c)
    S += topic_page(c,"Career Prediction","Career",[10,6,2],["Saturn","Sun","Mercury","Jupiter"],[f"D10 Sun: {c['divisional_charts']['D10 Dashamsa']['Sun']}", f"D10 Saturn: {c['divisional_charts']['D10 Dashamsa']['Saturn']}"],"Career prediction uses 10th house, 10th lord, D10, Saturn, Sun, Mercury, Jupiter and current dasha.")
    S += topic_page(c,"Money & Wealth Prediction","Wealth",[2,5,9,11],["Jupiter","Venus","Saturn"],[f"Focus area: {c['focus_area']}"],"Money prediction uses 2nd, 5th, 9th and 11th houses, Jupiter, Venus, Saturn and dasha timing.")
    S += topic_page(c,"Love & Marriage Prediction","Marriage",[7,2,4],["Venus","Jupiter","Moon"],[f"D9 Venus: {c['divisional_charts']['D9 Navamsa']['Venus']}", f"D9 Jupiter: {c['divisional_charts']['D9 Navamsa']['Jupiter']}"],"Marriage prediction uses 7th house, 7th lord, Venus, Jupiter, Moon and D9 support.")
    S += topic_page(c,"Family & Home Karma","Home",[2,4],["Moon"],[f"D12 Moon: {c['divisional_charts']['D12 Dwadashamsa']['Moon']}"],"Family and home karma uses 2nd house, 4th house, Moon and D12 lineage indicators.")
    S += topic_page(c,"Health & Vitality","Wellbeing",[1,6,8,12],["Saturn","Mars","Moon"],[],"This is astrology-based wellness tendency only, not medical diagnosis. It uses Lagna, 6th, 8th, 12th, Saturn, Mars and Moon.")
    S += topic_page(c,"Education, Skills & Intelligence","Learning",[4,5],["Mercury","Jupiter","Moon"],[],"Education and skill analysis uses 4th, 5th, Mercury, Jupiter and Moon.")
    S += topic_page(c,"Spirituality & Karmic Pattern","Dharma",[8,9,12],["Ketu","Saturn","Jupiter"],[f"D9 Ketu: {c['divisional_charts']['D9 Navamsa']['Ketu']}"],"Spirituality and karmic pattern use 8th, 9th, 12th, Ketu, Saturn, Jupiter and D9.")
    S += divisional(c)
    S += ashtakavarga(c)
    S += shadbala(c)
    S += dasha_page(c)
    S += forecast_overview(c)
    for i in range(1,6):
        S += year_detail(c,i)
    S += remedies(c)
    S += lucky(c)
    S += dos_donts(c)
    S += closing(c)
    return S

def build_astrology_report(chart, out_path):
    doc=ReportDoc(out_path)
    doc.build(story(chart))
    return out_path
