"""Premium Astrology Life Path PDF renderer using existing Veshann styling."""
from __future__ import annotations

from datetime import date
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, NextPageTemplate

from pdfbuild_base import ReportDoc, ST, GoldRule, Panel, bullets, GOLD, GOLD_L, GOLD_D, CREAM, MUTE, LINE, PW, MARGIN
import astrology as A
import astro_content as AC
from quality_gate import audit_story

MONTHS=["","January","February","March","April","May","June","July","August","September","October","November","December"]
HOUSE_THEMES={1:"identity, body and direction",2:"family, speech and savings",3:"effort, courage and skills",4:"home, mother and peace",5:"education, creativity and children",6:"workload, health routines and competition",7:"marriage, clients and public dealings",8:"transformation, hidden matters and longevity themes",9:"fortune, dharma and mentors",10:"career, status and karma",11:"income, networks and gains",12:"foreign lands, sleep, expenses and liberation"}

def limitation_panel(c):
    """Panel listing data limitations when birth time/place were estimated."""
    notes=[]
    if c.get("birth_time_estimated"): notes.append(AC.DISCLAIMERS["limited_time"])
    if c.get("place_estimated"): notes.append(AC.DISCLAIMERS["limited_place"])
    if not notes: return None
    return Panel([h3("Data Limitation — Please Read")] + [body(n) for n in notes], bg=HexColor("#F6ECEC"), border=GOLD_D)

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
    t=Table(data, colWidths=[110, None])
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
    lg=AC.lagna_reading(c["ascendant"]["sign"]); mn=AC.moon_reading(c["moon_sign"])
    nk_theme, nk_advice = AC.nakshatra_reading(c["moon_nakshatra"]["name"])
    dl=AC.dasha_reading(md["lord"])
    strong=c["strengths"]["strong_planets"]; weak=c["strengths"]["challenged_planets"]
    parts=[
        lead(f"{c['name']}, this summary is the report in miniature: your overall life pattern, your strongest resources, "
             f"the phase you are standing in right now, and the one thing to focus on next. Every statement here is expanded, "
             f"with its calculation basis, in the chapters that follow."),
        Spacer(1,7),
        Panel([h3("Overall Life Pattern"), body(
            f"With {c['ascendant']['sign']} rising, the chart suggests {lg['essence']}. The Moon in {c['moon_sign']} adds an inner life where "
            f"{mn['pattern']}. Your Moon nakshatra, {c['moon_nakshatra']['name']}, colours this with the theme of {nk_theme}. "
            f"Read together, the strongest signal here is a life that grows through {lg['direction']}, provided the emotional need for "
            f"{mn['need']} is respected rather than suppressed.")], border=GOLD_D),
        Spacer(1,7),
        Panel([h3("Key Strengths & Main Caution")] + bullets([
            f"<b>Strengths:</b> {', '.join(strong)} score strongest in this chart by dignity, house position and aspects. In daily life this appears as {lg['strength']}.",
            f"<b>Caution:</b> {', '.join(weak)} carry the most pressure and mature later. The main behavioural caution is {lg['risk']} — this matters because most avoidable setbacks in a chart come from over-using its own strengths.",
        ])),
        Spacer(1,7),
        Panel([h3("Current Phase")] + bullets([
            f"You are in <b>{md['lord']} Mahadasha</b> ({pd(md['start'])} to {pd(md['end'])}) with <b>{ad['lord']} Antardasha</b>. This period broadly supports {dl['supports']}, and it tests {dl['tests']}.",
            f"{md['lord']} sits in your house {c['planets'][md['lord']]['house']} ({HOUSE_THEMES[c['planets'][md['lord']]['house']]}), so that life area is where the period's events concentrate.",
            f"Jupiter currently transits house {tr['Jupiter']['from_lagna']} from Lagna, lending growth to {HOUSE_THEMES[tr['Jupiter']['from_lagna']]}; Saturn transits house {tr['Saturn']['from_lagna']}, asking for patience in {HOUSE_THEMES[tr['Saturn']['from_lagna']]}.",
        ]), border=GOLD_D),
        Spacer(1,7),
        Panel([h3("Best Next Focus"), body(
            f"For your stated focus — <b>{focus}</b> — the practical way to work with this phase is: {dl['use']}. "
            f"For your nakshatra pattern specifically: {nk_advice}. "
            "Act when dasha and transit both support a decision; pause major irreversible steps when Saturn or Rahu pressure is louder than Jupiter support. "
            "This should be treated as a timing indicator, not a fixed guarantee.")], bg=HexColor("#F6ECEC")),
        Spacer(1,7),
        premium_block(
            f"Lagna {c['ascendant']['sign']}, Moon {c['moon_sign']} in {c['moon_nakshatra']['name']}, {md['lord']}-{ad['lord']} dasha, Jupiter H{tr['Jupiter']['from_lagna']} and Saturn H{tr['Saturn']['from_lagna']}",
            f"This is a {focus}-sensitive timing phase with clearly identified strengths ({', '.join(strong)}) and pressure points ({', '.join(weak)}).",
            f"The dasha lords activate houses {c['planets'][md['lord']]['house']} and {c['planets'][ad['lord']]['house']}, while slow transits set the outer pressure and support.",
            "Read the career, money, relationship and timing chapters next in that order; each converts this summary into specific decisions."),
    ]
    lim=limitation_panel(c)
    if lim: parts=[lim, Spacer(1,7)]+parts
    return page("Executive Summary","Premium Executive Summary",parts)

def foundation(c):
    md=c["dasha"]["current_mahadasha"]; ad=c["dasha"]["current_antardasha"]
    pdasha=c["dasha"]["current_pratyantardasha"]
    settings=c.get("calculation_settings", {})
    lim=limitation_panel(c)
    return page("Chart Data","Birth Data & Calculation Basis",([lim, Spacer(1,7)] if lim else [])+[
        kv([
            ("Name", c["name"]),
            ("Date of birth", fmt_date(c["dob"])),
            ("Birth time", c["birth_time"] + (" (estimated — not provided)" if c.get("birth_time_estimated") else "")),
            ("Birth place", (c["birth_place"] or "Not provided") + (" (approximate)" if c.get("place_estimated") else "")),
            ("Gender", c.get("gender").title() if c.get("gender") else "Not provided"),
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
        Panel([h3("Why Precision Matters"), body(
            "The Lagna moves through a full sign roughly every two hours, so the accuracy of every house-based conclusion in this report "
            "depends directly on the precision of the birth time and place above. The Moon sign, nakshatra and dasha sequence are more forgiving "
            "— they usually hold even with a time error of an hour or two. If you later confirm a more precise birth time, the report can be "
            "recalculated and Lagna-dependent sections may sharpen or shift.")]),
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
    lg=AC.lagna_reading(asc["sign"])
    lord_h=c["planets"][lord]["house"]
    caution="" if not c.get("birth_time_estimated") else " Because birth time was estimated, this Lagna reading should be treated as indicative rather than exact."
    return page("Self And Direction","Core Personality & Life Direction",[
        lead(f"The Lagna, or ascendant, is the sign rising on the eastern horizon at your birth. It is the lens through which the whole chart "
             f"operates: personality, body, instinctive decision style, and the pattern life keeps repeating until it is understood.{caution}"),
        Spacer(1,8),
        Panel([h3(f"What Was Found: {asc['sign']} Rising"), body(
            f"In your chart, {asc['sign']} rises at {deg(asc['degree'])}. The chart suggests {lg['essence']}. "
            f"Your natural strengths in this pattern are {lg['strength']}. The recurring risk — the shadow side of the same energy — is {lg['risk']}.")], border=GOLD_D),
        Spacer(1,8),
        Panel([h3("Why This Matters"), body(
            f"The Lagna lord is {lord}, and where it sits shows which arena of life carries your identity. Here, {planet_line(c, lord)}. "
            f"This matters because it makes house {lord_h} — {HOUSE_THEMES[lord_h]} — the stage where your sense of self is built or tested. "
            f"Decisions in that area are never 'just practical' for you; they touch who you are, which is why they deserve extra deliberation and less impulse.")]),
        Spacer(1,8),
        Panel([h3("How To Work With It"), body(
            f"A practical way to work with this pattern is to steer your major commitments toward {lg['direction']}. "
            f"When you notice the risk pattern ({lg['risk']}) activating — usually under time pressure — deliberately slow the decision by one day. "
            f"That single habit converts this Lagna's biggest liability into experience.")], bg=HexColor("#F6ECEC")),
        Spacer(1,8), basis(c,[f"Lagna {asc['sign']} at {deg(asc['degree'])}", f"Lagna lord {lord} placed in house {lord_h}", f"Lagna nakshatra {asc['nakshatra']['name']} pada {asc['nakshatra']['pada']}"])
    ])

def moon(c):
    v=c["planets"]["Moon"]
    mn=AC.moon_reading(v["sign"])
    return page("Inner Life","Moon Sign & Emotional Pattern",[
        lead(f"In Vedic astrology the Moon is the mind itself — emotional rhythm, inner security, the mother connection, and the tone in which "
             f"you experience everything else the chart promises. Your Moon is in {v['sign']}, in {v['nakshatra']['name']} nakshatra."),
        Spacer(1,8),
        Panel([h3(f"What Was Found: Moon in {v['sign']}"), body(
            f"The chart suggests a tendency toward an emotional life where {mn['pattern']}. What this mind genuinely needs to stay steady is {mn['need']}. "
            f"When that need is met, decisions become clear and intuition reliable; when it is ignored for long stretches, reactions and restlessness rise.")], border=GOLD_D),
        Spacer(1,8),
        Panel([h3("Why This Matters"), body(
            f"Your Moon sits in house {v['house']} ({HOUSE_THEMES[v['house']]}), so emotional wellbeing and that life area rise and fall together. "
            f"This matters because when dasha or transits pressure house {v['house']}, the mind feels it first — often before events are visible. "
            f"Currently Saturn transits house {c['transits']['Saturn']['from_moon']} from your Moon, which sets the emotional weather described in the timing chapters.")]),
        Spacer(1,8),
        Panel([h3("How To Work With It"), body(
            f"A practical way to work with this pattern is: {mn['care']}. Treat this as maintenance, not correction — this Moon is an asset when its operating conditions are respected.")], bg=HexColor("#F6ECEC")),
        Spacer(1,8), basis(c,[planet_line(c,"Moon"), f"Moon nakshatra lord: {v['nakshatra']['lord']}", f"Saturn transit from Moon: house {c['transits']['Saturn']['from_moon']}"])
    ])

def sun(c):
    v=c["planets"]["Sun"]
    return page("Soul Authority","Sun Sign & Soul Identity",[
        lead(f"The Sun is the chart's core vitality: confidence, authority, the father's imprint, and the part of you that does not negotiate. "
             f"Your Sun is in {v['sign']} in house {v['house']}, with dignity '{v['dignity']}'."),
        Spacer(1,8),
        Panel([h3("What Was Found"), body(AC.planet_in_house("Sun", v["house"], v["dignity"], v["retrograde"]))], border=GOLD_D),
        Spacer(1,8),
        Panel([h3("Why This Matters"), body(
            f"This Sun placement asks you to build self-respect through the affairs of house {v['house']}: {HOUSE_THEMES[v['house']]}. "
            f"This matters because confidence built anywhere else tends to feel borrowed in this chart, while confidence earned in that arena becomes permanent. "
            f"Leadership phases open most naturally when dasha timing also activates the Sun, the 10th house or the Lagna — the timing chapters mark these windows.")]),
        Spacer(1,8),
        Panel([h3("How To Work With It"), body(
            "A practical way to work with this pattern is to take formal, visible responsibility in the Sun's house area in measured steps — "
            "and to protect the relationship with authority figures (including the father, where applicable) from ego contests. "
            "Respect given consciously returns as authority in this placement.")], bg=HexColor("#F6ECEC")),
        Spacer(1,8), basis(c,[planet_line(c,"Sun"), f"Sun dignity: {v['dignity']}", f"10th lord: {c['house_lords'][10]}"])
    ])

def nakshatra_page(c):
    n=c["moon_nakshatra"]
    theme, advice = AC.nakshatra_reading(n["name"])
    return page("Karmic Instinct","Nakshatra & Pada Analysis",[
        lead(f"The Moon's nakshatra is the finest personality grain the chart offers — 27 divisions instead of 12, each with its own myth, "
             f"motivation and life instruction. Your Moon occupies {n['name']}, pada {n['pada']}, ruled by {n['lord']}."),
        Spacer(1,8),
        Panel([h3(f"What Was Found: {n['name']}"), body(
            f"{n['name']} carries the theme of {theme}. This is the emotional fingerprint under everything the Moon-sign chapter described — "
            f"the motivation that operates even when you are not watching it.")], border=GOLD_D),
        Spacer(1,8),
        Panel([h3("Why This Matters"), body(
            f"Because the nakshatra lord is {n['lord']}, its condition in your chart becomes psychologically important: {planet_line(c, n['lord'])}. "
            f"Emotional triggers and karmic lessons therefore tend to arrive through house {c['planets'][n['lord']]['house']} matters "
            f"({HOUSE_THEMES[c['planets'][n['lord']]['house']]}). The nakshatra also seeds your Vimshottari dasha sequence, which is why the timing chapters begin from it.")]),
        Spacer(1,8),
        Panel([h3("How To Work With It"), body(f"A practical way to work with this pattern is simple and specific: {advice}.")], bg=HexColor("#F6ECEC")),
        Spacer(1,8), basis(c,[f"Moon longitude {deg(c['planets']['Moon']['longitude'])}", f"Nakshatra {n['name']} pada {n['pada']}", f"Nakshatra lord {n['lord']} in house {c['planets'][n['lord']]['house']}"])
    ])

def planet_table(c):
    rows=[[Paragraph("<b>Planet</b>",ST["mute"]),Paragraph("<b>Sign</b>",ST["mute"]),Paragraph("<b>Deg</b>",ST["mute"]),Paragraph("<b>House</b>",ST["mute"]),Paragraph("<b>Nakshatra</b>",ST["mute"]),Paragraph("<b>Status</b>",ST["mute"])]]
    for p,v in c["planets"].items():
        rows.append([Paragraph(p,ST["body"]),Paragraph(v["sign"],ST["body"]),Paragraph(deg(v["degree"]),ST["body"]),Paragraph(str(v["house"]),ST["body"]),Paragraph(f"{v['nakshatra']['name']} {v['nakshatra']['pada']}",ST["body"]),Paragraph((v["dignity"] + (" R" if v["retrograde"] else "")),ST["body"])])
    t=Table(rows, colWidths=[45,55,38,34,86,62])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.25,LINE),("BACKGROUND",(0,0),(-1,0),HexColor("#EAEDF3")),("FONTSIZE",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    strong=c["strengths"]["strong_planets"]; weak=c["strengths"]["challenged_planets"]
    strong_read=[AC.planet_in_house(p, c["planets"][p]["house"], c["planets"][p]["dignity"], c["planets"][p]["retrograde"]) for p in strong[:2]]
    weak_read=[AC.planet_in_house(p, c["planets"][p]["house"], c["planets"][p]["dignity"], c["planets"][p]["retrograde"]) for p in weak[:2]]
    return page("Calculated Positions","Planetary Strengths & Challenges",[
        lead("The table below is the raw calculated data behind this report. Beneath it, the strongest and most challenged planets are "
             "translated into plain language — what each one gives you, and what each one asks of you."),
        Spacer(1,6), t, Spacer(1,8),
        Panel([h3(f"Your Strongest Planets: {', '.join(strong)}")] + [body(x) for x in strong_read] + [body(
            "This matters because strong planets deliver with less effort — they are where you should place your biggest bets, "
            "especially in the periods (dashas) they rule.")], border=GOLD_D),
        Spacer(1,7),
        Panel([h3(f"Your Challenged Planets: {', '.join(weak)}")] + [body(x) for x in weak_read] + [body(
            "A challenged planet is not a defect; it is a slower curriculum. Its themes improve with conscious habits, honest handling "
            "and time — and its dasha periods, when they come, reward preparation over speed. The remedies chapter addresses these planets specifically.")]),
    ])

def houses_page(c):
    items=[]
    for h in range(1,13):
        lord=c["house_lords"][h]
        p=c["planets"][lord]
        items.append(f"<b>House {h}</b> ({HOUSE_THEMES[h]}): lord {lord} is in house {p['house']} in {p['sign']}.")
    return page("Life Areas","12-House Life Map",[lead("Each house describes a life department. The house lord shows where that department expresses itself."),Spacer(1,8),Panel([h3("House Map")] + bullets(items[:6]), border=GOLD_D),Spacer(1,7),Panel([h3("Houses 7-12")] + bullets(items[6:]))])

def topic_page(c, title, kick, houses, planets, extra_basis, text, profile=None):
    """A full topic chapter. `profile` (optional) supplies authored depth:
    {opening, interpretation_note, actions: [..], disclaimer: key-in-AC.DISCLAIMERS}"""
    profile = profile or {}
    b=[f"House {h} lord {c['house_lords'][h]} placed in house {c['planets'][c['house_lords'][h]]['house']}" for h in houses]
    b += [planet_line(c,p) for p in planets]
    b += extra_basis
    md=c["dasha"]["current_mahadasha"]["lord"]; ad=c["dasha"]["current_antardasha"]["lord"]
    verdict = f"This area is activated through houses {', '.join(map(str,houses))}, with current timing from {md}-{ad}."
    why = f"{md} sits in house {c['planets'][md]['house']} and {ad} sits in house {c['planets'][ad]['house']}; this is why the period must be read through those houses."
    guidance = "Take action when the relevant house lord, dasha lord and Jupiter support agree; use Saturn periods for discipline and correction."
    # authored, placement-specific interpretation of the topic's key planet
    key_planet = planets[0] if planets else c["house_lords"][houses[0]]
    kp = c["planets"][key_planet]
    parts=[lead(profile.get("opening", text)), Spacer(1,8)]
    parts += [Panel([h3("What Was Found")] + bullets(prediction_lines(c, houses, planets)) + [Spacer(1,3), body(
        AC.planet_in_house(key_planet, kp["house"], kp["dignity"], kp["retrograde"]))], border=GOLD_D), Spacer(1,8)]
    if profile.get("interpretation_note"):
        parts += [Panel([h3("How To Interpret This"), body(profile["interpretation_note"])]), Spacer(1,8)]
    if profile.get("actions"):
        parts += [Panel([h3("Practical Next Steps")] + bullets(profile["actions"]), bg=HexColor("#F6ECEC")), Spacer(1,8)]
    parts += [premium_block("; ".join(b[:5]), verdict, why, guidance), Spacer(1,8), basis(c,b[:8])]
    if profile.get("disclaimer"):
        parts += [Spacer(1,4), Paragraph(AC.DISCLAIMERS[profile["disclaimer"]], ST["mute"])]
    return page(kick,title,parts)

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
    dl=AC.dasha_reading(md["lord"]); al=AC.dasha_reading(ad["lord"])
    return page("Operating Period","Current Mahadasha / Antardasha / Pratyantardasha Prediction",[
        lead(f"Vimshottari dasha is Vedic astrology's timing system: long planetary chapters (Mahadasha), sub-chapters (Antardasha) and "
             f"near-term triggers (Pratyantardasha), all seeded from your Moon nakshatra. You are currently in {md['lord']} Mahadasha, "
             f"{ad['lord']} Antardasha and {pdasha['lord']} Pratyantardasha."),
        Spacer(1,8),
        Panel([h3(f"What The {md['lord']} Chapter Supports"), body(
            f"The {md['lord']} Mahadasha ({pd(md['start'])} to {pd(md['end'])}) broadly supports {dl['supports']}. "
            f"What it tests is {dl['tests']}. The practical way to use it: {dl['use']}.")], border=GOLD_D),
        Spacer(1,7),
        Panel([h3(f"The {ad['lord']} Sub-Period Right Now"), body(
            f"Within that chapter, the {ad['lord']} Antardasha ({pd(ad['start'])} to {pd(ad['end'])}) sharpens the focus toward {al['supports']} — "
            f"while testing {al['tests']}. Sub-periods are where events actually land, so near-term decisions should be read against this lens first.")]),
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
        f"Q1: Use {md} dasha themes and prepare around house {c['planets'][md]['house']} ({HOUSE_THEMES[c['planets'][md]['house']]}).",
        f"Q2: Jupiter transits {tr['Jupiter']['sign']} and supports house {jh}: {HOUSE_THEMES[jh]}.",
        f"Q3: Saturn transits {tr['Saturn']['sign']} and asks discipline in house {sh}: {HOUSE_THEMES[sh]}.",
        f"Q4: Rahu in house {rh} can bring urgency around {HOUSE_THEMES[rh]}; review commitments and avoid forcing decisions without dasha support.",
    ]
    dl=AC.dasha_reading(md)
    return page(f"Year {n}",f"Year {n} Detailed Forecast - {year}",[
        lead(f"The chart indicates that {year} should be read through {md} Mahadasha, Jupiter house {jh} support and Saturn house {sh} discipline. "
             f"This should be treated as a timing indicator, not a fixed guarantee — the transits set the weather, your handling sets the outcome."),
        Spacer(1,8), Panel([h3("Quarter-wise Guidance")] + bullets(qs), border=GOLD_D),
        Spacer(1,8),
        Panel([h3("Where To Focus This Year")] + bullets([
            f"<b>Career:</b> growth attempts land best where Jupiter's house {jh} overlaps your work — {HOUSE_THEMES[jh]}. Time launches, applications and expansions to that support.",
            f"<b>Money:</b> let Saturn's house {sh} pressure set the savings discipline — avoid new leveraged risk in that area and consolidate instead.",
            f"<b>Relationships:</b> protect connection during Rahu-driven urgency (house {rh}); postpone relationship ultimatums to calmer windows.",
            f"<b>Personal growth:</b> keep working with the {md} Mahadasha instruction from the timing chapter: {dl['use']}.",
        ]), bg=HexColor("#F6ECEC")),
        Spacer(1,8), basis(c,[f"Mahadasha lord {md} in house {c['planets'][md]['house']}", f"Calculated Jupiter transit: {tr['Jupiter']['sign']} house {jh}", f"Calculated Saturn transit: {tr['Saturn']['sign']} house {sh}", f"Calculated Rahu transit: {tr['Rahu']['sign']} house {rh}", f"Focus area: {c['focus_area']}"])
    ])

def dosha_page(c):
    entries=AC.detect_doshas(c)
    parts=[lead("This chapter reviews the classical patterns people most often worry about — calmly, from calculation, and with a working "
                "method for each. A dosha is a pattern, not a punishment: it describes where extra maturity is asked of you, and every one "
                "of them has a practical balancing approach.")]
    for e in entries:
        status = "Present" if e["present"] else "Not formed"
        parts += [Spacer(1,7), Panel([h3(f"{e['name']} — {status}")] + bullets([
            f"<b>Calculation basis:</b> {e['basis']}.",
            f"<b>What it means:</b> {e['meaning']}",
            f"<b>Balancing approach:</b> {e['balance']}",
        ]), border=GOLD_D if e["present"] else LINE)]
    parts += [Spacer(1,7), Paragraph(AC.DISCLAIMERS["general"], ST["mute"])]
    return page("Karmic Patterns","Dosha & Karmic Pattern Review",parts)

def action_plan(c):
    md=c["dasha"]["current_mahadasha"]["lord"]; ad=c["dasha"]["current_antardasha"]["lord"]
    dl=AC.dasha_reading(md)
    lg=AC.lagna_reading(c["ascendant"]["sign"]); mn=AC.moon_reading(c["moon_sign"])
    weak=c["strengths"]["challenged_planets"][0]
    jh=c["transits"]["Jupiter"]["from_lagna"]
    return page("Your Plan","One-Page Action Plan",[
        lead("Everything in this report, reduced to one page you can actually follow. Review it monthly; adjust as circumstances change."),
        Spacer(1,8),
        Panel([h3("Next 7 Days")] + bullets([
            "Verify your birth data on the Birth Data page; if the time was estimated, try to confirm it from records or family.",
            f"Write down the one decision in your focus area ({c['focus_area']}) that you have been forcing. Park it for this week and gather facts instead.",
            f"Begin the single remedy discipline chosen for {weak} from the remedies chapter — small and daily beats large and occasional.",
        ]), border=GOLD_D),
        Spacer(1,7),
        Panel([h3("Next 30 Days")] + bullets([
            f"Apply the current period instruction: {dl['use']}",
            f"Emotional maintenance: {mn['care']}",
            f"Take one concrete step where Jupiter currently supports you — house {jh}: {HOUSE_THEMES[jh]}.",
        ])),
        Spacer(1,7),
        Panel([h3("Next 6 Months")] + bullets([
            f"Align one significant commitment with your chart's natural direction: {lg['direction']}.",
            f"Use the {ad}-Antardasha window consciously — its start and end dates are on the dasha page; review progress when it changes.",
            "Re-read the five-year forecast at each new year boundary and adjust the plan rather than abandoning it.",
        ])),
        Spacer(1,7),
        Panel([h3("Next 1–2 Years")] + bullets([
            f"Build depth in the house {c['planets'][md]['house']} arena ({HOUSE_THEMES[c['planets'][md]['house']]}) — this is where the {md} Mahadasha concentrates results.",
            f"Guard consciously against the chart's one repeating risk: {lg['risk']}.",
            "Revisit this report after any major life event or when the Antardasha changes; timing chapters are designed to be re-read, not read once.",
        ]), bg=HexColor("#F6ECEC")),
    ])

def remedies(c):
    weak=c["strengths"]["challenged_planets"][:3]
    items=[]
    for p in weak:
        day={"Sun":"Sunday","Moon":"Monday","Mars":"Tuesday","Mercury":"Wednesday","Jupiter":"Thursday","Venus":"Friday","Saturn":"Saturday","Rahu":"Saturday","Ketu":"Tuesday"}.get(p,"Thursday")
        h=c["planets"][p]["house"]
        items.append(f"<b>{p}</b> (challenged in your chart): a simple {day} discipline — mantra practice, modest donation, or focused routine — "
                     f"paired with honest correction of house {h} matters ({HOUSE_THEMES[h]}). <b>Why:</b> {p} governs {AC.PLANET_DOMAIN[p]}; "
                     f"the ritual is the reminder, the behaviour change in that life area is the actual remedy.")
    items.append("Gemstones are deliberately NOT prescribed here: they amplify a planet and should be worn only after personal confirmation by an astrologer who has your exact birth time. No purchase is required for any remedy in this report.")
    items.append("Every remedy above is free or near-free by design. Consistency for 90 days matters far more than intensity or expense.")
    return page("Chart Remedies","Remedies / Upaya",[lead("Remedies here are selected only from the planets actually challenged in your calculation, and each one is explained — what to do, and why that specific practice fits that specific planet. None of them requires fear, and none requires spending."),Spacer(1,8),Panel([h3("Recommended Supports")] + bullets(items), border=GOLD_D),Spacer(1,8),premium_block(
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
    md=c["dasha"]["current_mahadasha"]["lord"]
    lg=AC.lagna_reading(c["ascendant"]["sign"])
    return page("Final Verdict","Final Verdict & Closing Guidance",[
        lead(f"{c['name']}, this chart does not remove your free will. It shows the weather around your path, the timing of effort, and the houses where life asks you to grow."),
        Spacer(1,8),
        Panel([h3("The Chart In One Paragraph"), body(
            f"You carry {lg['essence']}. Your strongest planetary resources are {', '.join(c['strengths']['strong_planets'])}, and your "
            f"current {md} Mahadasha decides which doors are open right now. Nothing in this report predicts a fixed fate; every indication "
            f"is a probability pattern that improves with conscious handling. The strongest signal in the whole chart is this: your results "
            f"track your timing discipline more than your effort volume.")], border=GOLD_D),
        Spacer(1,8),
        Panel([h3("Final Message"), body(f"The next five years are best handled by respecting the {md} dasha, using Jupiter's support wisely, and allowing Saturn to mature what cannot be rushed. Your best action is steady alignment, not fear. Keep the One-Page Action Plan visible, and treat this document as a working companion — it is designed to be re-read at each dasha and year boundary.")]),
        Spacer(1,8),
        Paragraph(AC.DISCLAIMERS["general"], ST["mute"]),
        Spacer(1,4),
        Paragraph("This report was prepared confidentially for the named client. Birth details and personal concerns are never shared. "
                  "For clarifications, reply to your delivery email — a genuine question about your own report is always answered.", ST["mute"]),
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
    lg=AC.lagna_reading(c["ascendant"]["sign"])
    l10=c["house_lords"][10]; h10=c["planets"][l10]["house"]
    S += topic_page(c,"Career & Work Direction","Career",[10,6,2],["Saturn","Sun","Mercury","Jupiter"],[f"D10 Sun: {c['divisional_charts']['D10 Dashamsa']['Sun']}", f"D10 Saturn: {c['divisional_charts']['D10 Dashamsa']['Saturn']}"],"",profile={
        "opening": f"Career in a Vedic chart is read from the 10th house and its lord, the D10 divisional chart, and the planets of authority and effort — Saturn, Sun, Mercury and Jupiter. Your 10th lord {l10} sits in house {h10}, which links your professional life to {HOUSE_THEMES[h10]}. Your temperament points toward {lg['direction']}.",
        "interpretation_note": f"The strongest signal here is the 10th lord's position: work satisfies you when it engages house {h10} themes, and frustrates you when it doesn't. Professional blocks in this chart usually appear as {lg['risk']} — recognising this pattern early is worth more than any transit prediction. Growth windows open when the dasha lord or Jupiter's transit touches houses 10, 6 or 2; the five-year chapters mark them year by year.",
        "actions": [
            f"Steer your role, over the next two review cycles, toward work that genuinely uses your strong planets ({', '.join(c['strengths']['strong_planets'])}).",
            f"Time job changes, launches and negotiations to Jupiter-supported windows from the forecast chapters, and use Saturn-heavy phases to consolidate skills instead.",
            "Keep one written career review per quarter — Saturn rewards documented, patient progression in almost every chart, and specifically in this one.",
        ]})
    l2=c["house_lords"][2]; l11=c["house_lords"][11]
    S += topic_page(c,"Money & Wealth Pattern","Wealth",[2,5,9,11],["Jupiter","Venus","Saturn"],[f"Focus area: {c['focus_area']}"],"",profile={
        "opening": f"Wealth is read from the 2nd house (savings and accumulation), the 11th (income and gains), the 5th and 9th (fortune and intelligent risk), and from Jupiter, Venus and Saturn. Your 2nd lord {l2} sits in house {c['planets'][l2]['house']} and your 11th lord {l11} in house {c['planets'][l11]['house']} — together these describe how money enters and where it tends to leave.",
        "interpretation_note": f"Read earning style from the 11th lord's house ({HOUSE_THEMES[c['planets'][l11]['house']]}) and leakage risk from pressure on the 2nd. This matters because most financial stress in a chart comes not from low income but from a mismatch between earning style and spending structure. Timing support for wealth arrives when Jupiter transits or dasha periods activate houses 2, 5, 9 or 11 — marked in the forecast chapters.",
        "actions": [
            "Automate savings so discipline does not depend on mood — this chart's money pattern responds better to structure than to willpower.",
            "Route intelligent risk (5th/9th) through small, reviewed positions; avoid leverage during Saturn or Rahu pressure phases named in the yearly chapters.",
            "Review one recurring expense category each month; leakage in a chart is almost always specific, not general.",
        ], "disclaimer": "finance"})
    l7=c["house_lords"][7]; mn=AC.moon_reading(c["moon_sign"])
    S += topic_page(c,"Marriage & Relationship Pattern","Marriage",[7,2,4],["Venus","Jupiter","Moon"],[f"D9 Venus: {c['divisional_charts']['D9 Navamsa']['Venus']}", f"D9 Jupiter: {c['divisional_charts']['D9 Navamsa']['Jupiter']}"],"",profile={
        "opening": f"Marriage and committed partnership are read from the 7th house and its lord, Venus, Jupiter, the Moon, and the D9 Navamsa. Your 7th lord {l7} sits in house {c['planets'][l7]['house']}, and your Moon's emotional needs — {mn['need']} — set what partnership must provide for you to feel settled.",
        "interpretation_note": f"The chart suggests a tendency toward friction where the emotional pattern ({mn['pattern']}) meets a partner's different rhythm — this is a compatibility texture, not a verdict. Commitment deepens in this chart when Venus/Jupiter support is active and when house {c['planets'][l7]['house']} matters are stable. Relationship timing windows should be read from the dasha and transit chapters; none of them guarantees or forbids anything.",
        "actions": [
            f"Tell your partner (or future partner) plainly what steadies you: {mn['need']}. Unspoken needs are this pattern's main friction source.",
            "Schedule difficult conversations in calm transit windows rather than at emotional peaks; the do/don't chapter lists the principle.",
            "Judge compatibility by observed behaviour over full months, not by single events — the 7th house rewards evidence over intensity.",
        ], "disclaimer": "relationship"})
    S += topic_page(c,"Family & Home Karma","Home",[2,4],["Moon"],[f"D12 Moon: {c['divisional_charts']['D12 Dwadashamsa']['Moon']}"],"",profile={
        "opening": f"Family and home life are read from the 2nd and 4th houses, the Moon, and the D12 lineage chart. Your 4th lord {c['house_lords'][4]} sits in house {c['planets'][c['house_lords'][4]]['house']}, linking inner peace to {HOUSE_THEMES[c['planets'][c['house_lords'][4]]['house']]}.",
        "interpretation_note": "The 4th house is where the chart recharges. When it is supported, everything else costs less energy; when it is pressured by dasha or transit, unrelated areas feel harder than they are. Treat home stability as infrastructure for the whole chart, not as a separate topic.",
        "actions": [
            "Protect one weekly ritual of genuine rest at home — this chart's productivity depends on it more than it appears to.",
            "Resolve family financial matters (2nd house) in writing and in daylight; ambiguity is the main family-karma amplifier.",
        ]})
    S += topic_page(c,"Health & Energy Tendencies","Wellbeing",[1,6,8,12],["Saturn","Mars","Moon"],[],"",profile={
        "opening": "This chapter describes energy and stress tendencies only — where the chart suggests vitality is spent and how it is best protected. It is read from the Lagna, the 6th, 8th and 12th houses, and from Saturn, Mars and the Moon. It is not a medical assessment of any kind.",
        "interpretation_note": f"The practical reading: your energy dips track the Moon's condition ({mn['pattern']}), and workload pressure shows through the 6th house. A chart never diagnoses; it only suggests where routine protects you most. The strongest signal here is that consistent sleep and a steady daily rhythm do disproportionate work in this chart.",
        "actions": [
            "Keep sleep and meal timing steady through high-pressure dasha windows — rhythm is this chart's cheapest medicine.",
            "Use physical activity as the pressure valve for Mars energy, especially during conflict-heavy periods.",
            "For any actual health concern, consult a qualified medical professional promptly; use this chapter only for lifestyle rhythm.",
        ], "disclaimer": "health"})
    S += topic_page(c,"Education, Skills & Intelligence","Learning",[4,5],["Mercury","Jupiter","Moon"],[],"",profile={
        "opening": f"Learning capacity is read from the 4th and 5th houses, Mercury (analysis), Jupiter (wisdom) and the Moon (retention). Your 5th lord {c['house_lords'][5]} sits in house {c['planets'][c['house_lords'][5]]['house']}, colouring how your intelligence prefers to express itself.",
        "interpretation_note": "Skills compound fastest in this chart when learning is attached to real projects in the houses the dasha currently activates — abstract study during unrelated periods tends to evaporate. Time certifications and deep-study phases to Mercury or Jupiter sub-periods where possible.",
        "actions": [
            "Pick one skill per Antardasha window and finish it; the timing chapters give you natural start and end dates.",
            "Teach or write what you learn — this chart retains through expression more than through revision.",
        ]})
    S += topic_page(c,"Spirituality & Karmic Pattern","Dharma",[8,9,12],["Ketu","Saturn","Jupiter"],[f"D9 Ketu: {c['divisional_charts']['D9 Navamsa']['Ketu']}"],"",profile={
        "opening": f"The spiritual thread of a chart is read from the 8th, 9th and 12th houses, Ketu (release), Saturn (discipline) and Jupiter (grace). Your Ketu sits in house {c['planets']['Ketu']['house']}, marking the area of life you already carry unusual instinct for — and are asked to hold lightly.",
        "interpretation_note": f"Ketu's house ({HOUSE_THEMES[c['planets']['Ketu']['house']]}) often feels simultaneously easy and unsatisfying: past mastery without present hunger. The karmic instruction is to serve through that area without demanding identity from it, while Rahu's opposite house shows where growth hunger genuinely lives this lifetime.",
        "actions": [
            "Keep one small, private spiritual discipline independent of results — Saturn periods in particular reward it.",
            "When the Ketu-house area of life feels flat, treat it as a signal to give rather than to acquire; the flatness usually resolves.",
        ]})
    S += divisional(c)
    S += ashtakavarga(c)
    S += shadbala(c)
    S += dasha_page(c)
    S += forecast_overview(c)
    for i in range(1,6):
        S += year_detail(c,i)
    S += dosha_page(c)
    S += remedies(c)
    S += lucky(c)
    S += dos_donts(c)
    S += action_plan(c)
    S += closing(c)
    return S

def build_astrology_report(chart, out_path, strict=False):
    S = story(chart)
    audit_story(S, report_name="premium_astrology_life_path",
                required_disclaimers=[("health professional note", "medical professionals"),
                                      ("tendency-not-fate note", "tendencies and timing, not fixed fate")],
                strict=strict)
    doc=ReportDoc(out_path, footer_title="Vedic Astrology Life Path Report")
    doc.build(S)
    return out_path
