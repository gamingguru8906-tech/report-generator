"""Premium Divorce, Separation & Relationship Karma PDF report.

This renderer is calculation-first. It uses the existing astrology engine for
client and partner charts where data is complete, and numerology only for
partner data that lacks a reliable birth time/place.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
import json
import re

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, NextPageTemplate

from pdfbuild_base import ReportDoc, ST, GoldRule, Panel, bullets, GOLD, GOLD_L, GOLD_D, CREAM, MUTE, LINE, PW, MARGIN
import astrology as A
import numerology as N

MONTHS = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
MAL = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
BEN = {"Jupiter", "Venus", "Moon", "Mercury"}
REL_HOUSES = {2, 4, 7, 8, 11}
SEPARATION_HOUSES = {6, 8, 12}

def fmt_date(d):
    if not d:
        return "Unavailable"
    if isinstance(d, str):
        try:
            d = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except Exception:
            return d
    return f"{d.day} {MONTHS[d.month]} {d.year}"

def pd(dt):
    return dt.strftime("%d %b %Y") if hasattr(dt, "strftime") else str(dt)

def p(txt, style="body"):
    return Paragraph(str(txt), ST[style])

def h1(txt): return Paragraph(txt, ST["h1"])
def h3(txt): return Paragraph(txt, ST["h3"])
def lead(txt): return Paragraph(txt, ST["lead"])
def kicker(txt): return Paragraph(txt.upper(), ST["kicker"])

def page(kick, title, parts):
    return [NextPageTemplate("content"), kicker(kick), h1(title), GoldRule(), Spacer(1, 4)] + parts + [PageBreak()]

def parse_payload(extra="", **kwargs):
    data = {}
    if extra:
        try:
            if extra.strip().startswith("{"):
                data.update(json.loads(extra))
        except Exception:
            data["main_question"] = extra.strip()
    data.update({k: v for k, v in kwargs.items() if v not in (None, "")})
    return data

def parse_dob(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()

def reduce_num(n):
    return N.reduce_num(n, keep_masters=False)

def partner_numerology(name, dob):
    if not (name and dob):
        return None
    return N.compute(name, parse_dob(dob), "")

def planet_line(c, planet):
    v = c["planets"][planet]
    asp = ", aspected by " + ", ".join(v.get("aspected_by", [])) if v.get("aspected_by") else ""
    return f"{planet}: {v['sign']} house {v['house']}, {v['nakshatra']['name']} pada {v['nakshatra']['pada']}, {v['dignity']}{asp}"

def lord_line(c, house):
    lord = c["house_lords"][house]
    return f"{house}th lord {lord}: {planet_line(c, lord)}"

def d9(c, planet):
    return c["divisional_charts"]["D9 Navamsa"].get(planet, "Unavailable")

def house_afflictions(c, house):
    out = []
    for p, v in c["planets"].items():
        if v["house"] == house and p in MAL:
            out.append(f"{p} occupies house {house}")
    for p in c.get("aspects_by_house", {}).get(house, []):
        if p in MAL:
            out.append(f"{p} aspects house {house}")
    return out

def house_support(c, house):
    out = []
    for p, v in c["planets"].items():
        if v["house"] == house and p in BEN:
            out.append(f"{p} occupies house {house}")
    for p in c.get("aspects_by_house", {}).get(house, []):
        if p in {"Jupiter", "Venus"}:
            out.append(f"{p} aspects house {house}")
    return out

def active_houses(c):
    d = c["dasha"]
    planets = [d["current_mahadasha"]["lord"], d["current_antardasha"]["lord"], d["current_pratyantardasha"]["lord"]]
    return {p: c["planets"][p]["house"] for p in planets}

def relation_score(c):
    score = 0
    factors = []
    aff7 = house_afflictions(c, 7)
    sup7 = house_support(c, 7)
    lord7 = c["house_lords"][7]
    lord7_house = c["planets"][lord7]["house"]
    if aff7:
        score += 2; factors += aff7
    if sup7:
        score -= 2; factors += sup7
    if lord7_house in SEPARATION_HOUSES:
        score += 2; factors.append(f"7th lord {lord7} placed in separation house {lord7_house}")
    if c["planets"]["Venus"]["house"] in SEPARATION_HOUSES:
        score += 1; factors.append(f"Venus placed in house {c['planets']['Venus']['house']}")
    if c["planets"]["Jupiter"]["house"] in REL_HOUSES:
        score -= 1; factors.append(f"Jupiter supports relationship house {c['planets']['Jupiter']['house']}")
    if c["planets"]["Venus"]["dignity"] in {"Exalted", "Own sign"}:
        score -= 1; factors.append(f"Venus is {c['planets']['Venus']['dignity']}")
    if c["planets"]["Venus"]["dignity"] == "Debilitated":
        score += 1; factors.append("Venus is debilitated")
    for p, h in active_houses(c).items():
        if h in SEPARATION_HOUSES:
            score += 1; factors.append(f"Current dasha planet {p} activates house {h}")
        if h in {2, 7, 11}:
            score -= 1; factors.append(f"Current dasha planet {p} activates support house {h}")
    tr = c["transits"]
    if tr["Saturn"]["from_lagna"] in {7, 8, 12}:
        score += 1; factors.append(f"Saturn transit pressures house {tr['Saturn']['from_lagna']} from Lagna")
    if tr["Jupiter"]["from_lagna"] in {2, 5, 7, 9, 11}:
        score -= 1; factors.append(f"Jupiter transit supports house {tr['Jupiter']['from_lagna']} from Lagna")
    return score, factors

def level(score, low="Low", mid="Medium", high="High"):
    if score >= 4:
        return high
    if score >= 1:
        return mid
    return low

def strength_word(score):
    if score >= 4:
        return "Strong"
    if score >= 1:
        return "Moderate"
    return "Weak"

def repair_word(score):
    if score <= -1:
        return "Strong"
    if score <= 2:
        return "Moderate"
    return "Weak"

def verdict_path(score):
    if score >= 5:
        return "Prepare / Separate respectfully"
    if score >= 3:
        return "Mediate before final decision"
    if score >= 1:
        return "Wait and repair with structure"
    return "Repair"

def partner_chart_or_partial(data):
    name = data.get("partner_name", "").strip()
    dob = data.get("partner_dob", "").strip()
    ptime = data.get("partner_birth_time", "").strip()
    pplace = data.get("partner_birth_place", "").strip()
    result = {"name": name or "Partner", "dob": dob, "chart": None, "numerology": None, "status": []}
    if name and dob:
        try:
            result["numerology"] = partner_numerology(name, dob)
        except Exception as e:
            result["status"].append(f"Partner numerology unavailable: {e}")
    if name and dob and ptime and pplace:
        try:
            result["chart"] = A.compute_chart(name, parse_dob(dob), ptime, pplace, focus_area="relationship")
        except Exception as e:
            result["status"].append(f"Partner chart unavailable: {e}")
    else:
        result["status"].append("Partner birth time/place incomplete; partner D1/D9 houses and exact Lagna are not used.")
    return result

def table(rows, widths=(96, 248)):
    data = [[Paragraph(f'<font color="#8C8472">{k}</font>', ST["mute"]), Paragraph(str(v), ST["body"])] for k, v in rows]
    t = Table(data, colWidths=list(widths))
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),("LINEBELOW",(0,0),(-1,-2),0.35,LINE)]))
    return t

def premium_block(basis_txt, verdict, why, guidance):
    return Panel([h3("Premium Reading")] + bullets([
        f"<b>Calculation basis:</b> {basis_txt}",
        f"<b>Clear verdict:</b> {verdict}",
        f"<b>Why this result came:</b> {why}",
        f"<b>Practical guidance:</b> {guidance}",
    ]), border=GOLD_D)

def cover(c, data, partner):
    S = [NextPageTemplate("content"), Spacer(1, 38)]
    S += [Paragraph("VESHANN ASTRO", ParagraphStyle("dv-brand", fontName="Cinzel-B", fontSize=22, textColor=GOLD_L, alignment=TA_CENTER, leading=26, tracking=4))]
    S += [Paragraph("PREMIUM RELATIONSHIP KARMA REPORT", ParagraphStyle("dv-sub", fontName="Jost-L", fontSize=8.5, textColor=MUTE, alignment=TA_CENTER, tracking=3, spaceBefore=4))]
    S += [Spacer(1, 16), GoldRule(), Spacer(1, 14)]
    S += [Paragraph("Premium Divorce, Separation &", ParagraphStyle("dv-t1", fontName="Cormorant-I", fontSize=27, textColor=CREAM, alignment=TA_CENTER, leading=30))]
    S += [Paragraph("RELATIONSHIP KARMA REPORT", ParagraphStyle("dv-t2", fontName="Cinzel-B", fontSize=22, textColor=GOLD, alignment=TA_CENTER, leading=28, tracking=1))]
    S += [Spacer(1, 16)]
    S += [table([
        ("Client", f"{c['name']} - {fmt_date(c['dob'])}, {c['birth_time']}, {c['birth_place']}"),
        ("Partner", f"{partner['name']} - {fmt_date(partner.get('dob'))}"),
        ("Partner time/place", f"{data.get('partner_birth_time') or 'Unavailable'} - {data.get('partner_birth_place') or 'Unavailable'}"),
        ("Marriage date", fmt_date(data.get("marriage_date")) if data.get("marriage_date") else "Unavailable"),
        ("Current issue", data.get("current_issue") or "Not specified"),
        ("Children", data.get("children") or "Not specified"),
        ("Main question", data.get("main_question") or "Not specified"),
        ("Report date", fmt_date(date.today())),
    ], widths=(82, 280))]
    S += [Spacer(1, 14), Panel([h3("Calculation Rule"), p("This report uses calculated Vedic factors from the client's chart and partner factors only where reliable data exists. Unknown birth-time factors are not invented.")], border=GOLD_D)]
    S += [PageBreak()]
    return S

def snapshot(c, data, partner, score, factors):
    return page("Direct Conclusions", "Relationship Crisis Snapshot", [
        table([
            ("Separation risk", level(score)),
            ("Reconciliation possibility", repair_word(score)),
            ("Current phase", f"{c['dasha']['current_mahadasha']['lord']}-{c['dasha']['current_antardasha']['lord']} relationship test; active houses {active_houses(c)}"),
            ("Main conflict reason", factors[0] if factors else "No dominant severe separation factor in the calculated scan"),
            ("Best immediate action", "Pause escalation and document facts while Saturn/Jupiter timing is reviewed"),
            ("Best decision window", f"Use upcoming {c['dasha']['upcoming_antardashas'][0]['lord']} Antardasha window: {pd(c['dasha']['upcoming_antardashas'][0]['start'])} to {pd(c['dasha']['upcoming_antardashas'][0]['end'])}"),
            ("Biggest warning", next((f for f in factors if any(x in f for x in ["Saturn", "Rahu", "Mars", "6th", "8th", "12th", "separation"])), "Do not convert emotional pressure into legal escalation without timing review")),
            ("Biggest hope", next((f for f in factors if any(x in f for x in ["Jupiter", "Venus", "support"])), "Repair depends on structured communication and benefic timing rather than impulse")),
        ]),
        Spacer(1, 8),
        Panel([h3("Scoring Basis")] + bullets(factors[:8] or ["No major technical crisis factor exceeded the threshold."]), border=GOLD_D),
        Spacer(1, 8),
        premium_block(
            f"7th house, 7th lord, Venus, Jupiter, active dasha houses {active_houses(c)}, and Saturn/Jupiter/Rahu-Ketu transits",
            f"Separation risk is {level(score)} and reconciliation possibility is {repair_word(score)}.",
            "The verdict is not emotional wording; it comes from the weighted count of separation pressure versus benefic repair support.",
            "Do not act from one argument. Use the decision window and stabilise communication before legal or final emotional steps."),
    ])

def seventh_house(c):
    lord7 = c["house_lords"][7]
    return page("Marriage Karma", "7th House & Marriage Karma", [
        lead("This page reads marriage promise and pressure through the 7th house, 7th lord, Venus, Jupiter and direct affliction/support factors."),
        Spacer(1, 8),
        Panel([h3("Technical Findings")] + bullets([
            f"7th house sign: {A.SIGNS[A.sign_from_house(c['ascendant']['longitude'], 7)]}; 7th lord: {lord7}.",
            lord_line(c, 7),
            planet_line(c, "Venus"),
            planet_line(c, "Jupiter"),
            "Darakaraka is not printed because this engine does not yet validate Jaimini degrees for all grahas.",
            "Afflictions: " + ("; ".join(house_afflictions(c, 7)) or "No direct malefic occupation/aspect flagged."),
            "Benefic support: " + ("; ".join(house_support(c, 7)) or "No direct Jupiter/Venus support flagged."),
        ]), border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("Marriage Pattern Verdict"), p(f"The calculated 7th-house pattern points to a {level(relation_score(c)[0]).lower()} separation-risk profile. Stability improves when Venus/Jupiter support is active; distance increases when 6th/8th/12th dasha or Saturn/Rahu pressure dominates.")]),
        Spacer(1, 8),
        premium_block(
            f"7th lord {lord7}, afflictions {house_afflictions(c,7) or 'none direct'}, support {house_support(c,7) or 'none direct'}",
            "Marriage karma is repairable when benefic support is stronger than separation-house activation.",
            "This result came from the condition of the 7th house/lord, not from generic relationship advice.",
            "Handle the relationship through structured timing; avoid forcing decisions during pressure dasha/transit periods."),
    ])

def navamsa(c):
    d9c = c["divisional_charts"]["D9 Navamsa"]
    sep = relation_score(c)[0]
    return page("D9 Reality", "Navamsa D9 Relationship Truth", [
        lead("D9 is used here only as divisional confirmation of the D1 marriage promise. It is not read as a separate birth chart without validated D9 houses."),
        Spacer(1, 8),
        Panel([h3("D9 Factors")] + bullets([
            f"D9 Lagna sign by ascendant division: {A.divisional_sign(c['ascendant']['longitude'], 9)}.",
            f"D9 Venus: {d9c.get('Venus')}; D9 Jupiter: {d9c.get('Jupiter')}.",
            f"D9 7th lord is not printed as a house-lord result because this engine stores divisional signs, not full divisional cusps.",
            f"D1 7th lord confirmation: {lord_line(c, 7)}",
            f"D1 vs D9: Venus D1 {c['planets']['Venus']['sign']} / D9 {d9c.get('Venus')}; Jupiter D1 {c['planets']['Jupiter']['sign']} / D9 {d9c.get('Jupiter')}.",
        ]), border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("D9 Verdict"), p("D9 supports reconciliation when Venus/Jupiter are not severely weakened and D1 has benefic support. In this chart, the combined D1/D9 reading gives: " + ("separation pressure is stronger than repair support." if sep >= 4 else "repair remains technically possible if dasha/transit timing is handled carefully."))]),
        Spacer(1, 8),
        premium_block(
            f"D9 Venus {d9c.get('Venus')}, D9 Jupiter {d9c.get('Jupiter')}, D1 7th lord {c['house_lords'][7]}",
            "D9 is used as confirmation, not as a fake full chart.",
            "The engine stores divisional signs, so it does not invent D9 houses/aspects that are not calculated.",
            "Use D9 to confirm whether repair support exists; use D1 and dasha for practical timing."),
    ])

def compatibility(c, partner):
    items = []
    if partner.get("chart"):
        pc = partner["chart"]
        items += [
            f"Moon compatibility: client Moon {c['moon_sign']} / partner Moon {pc['moon_sign']}.",
            f"Venus-Mars pattern: client Venus {c['planets']['Venus']['sign']} and Mars {c['planets']['Mars']['sign']}; partner Venus {pc['planets']['Venus']['sign']} and Mars {pc['planets']['Mars']['sign']}.",
            f"7th house links: client 7th lord {c['house_lords'][7]} in house {c['planets'][c['house_lords'][7]]['house']}; partner 7th lord {pc['house_lords'][7]} in house {pc['planets'][pc['house_lords'][7]]['house']}.",
            f"Communication damage indicator: Mercury houses client {c['planets']['Mercury']['house']} / partner {pc['planets']['Mercury']['house']}.",
        ]
    else:
        items += partner.get("status", [])
    pn = partner.get("numerology")
    if pn:
        items += [
            f"DOB numerology: client Life Path {c.get('numerology',{}).get('life_path','n/a')} / partner Life Path {pn.get('life_path')}.",
            f"Name numerology: partner Destiny {pn.get('destiny')} and Soul Urge {pn.get('soul_urge')} are used as available non-time factors.",
        ]
    return page("Compatibility", "Compatibility & Conflict Pattern", [
        lead("Compatibility is calculated only from available data. Missing partner birth time means no partner Lagna, houses or D9 claims are used."),
        Spacer(1, 8),
        Panel([h3("Compared Factors")] + bullets(items or ["Partner data unavailable; compatibility comparison is limited to the client's marriage chart."]), border=GOLD_D),
        Spacer(1, 8),
        premium_block(
            "Partner Moon/Venus/Mars/7th factors if birth time exists; otherwise partner DOB numerology and available non-time factors",
            "Compatibility is complete only when both birth charts are complete.",
            "This prevents fake Lagna, D9 and house claims when partner birth time/place is unavailable.",
            "Treat partial compatibility as a caution map, not a final marriage verdict."),
    ])

def separation_indicators(c):
    d = active_houses(c)
    items = [
        f"6th/8th/12th link with 7th: 7th lord {c['house_lords'][7]} placed in house {c['planets'][c['house_lords'][7]]['house']}.",
        f"Rahu/Ketu 1/7 axis influence: Rahu house {c['planets']['Rahu']['house']}, Ketu house {c['planets']['Ketu']['house']}.",
        f"Saturn/Mars affliction to 7th: {'; '.join([x for x in house_afflictions(c,7) if 'Saturn' in x or 'Mars' in x]) or 'not directly flagged'}.",
        f"Weak 2nd-family continuity check: 2nd lord {c['house_lords'][2]} in house {c['planets'][c['house_lords'][2]]['house']}; afflictions: {'; '.join(house_afflictions(c,2)) or 'none direct'}.",
        f"Current dasha houses: {d}. Separation-house activation: {', '.join(p for p,h in d.items() if h in SEPARATION_HOUSES) or 'none'}.",
        f"D9 affliction proxy: Venus D9 {d9(c,'Venus')}, Jupiter D9 {d9(c,'Jupiter')}; full D9 aspects unavailable.",
        f"Transit pressure: Saturn H{c['transits']['Saturn']['from_lagna']}, Rahu H{c['transits']['Rahu']['from_lagna']}, Ketu H{c['transits']['Ketu']['from_lagna']} from Lagna.",
    ]
    return page("Risk Factors", "Separation / Divorce Indicators", [
        Panel([h3(f"Indication Level: {strength_word(relation_score(c)[0])}")] + bullets(items), border=GOLD_D),
        Spacer(1, 8),
        p("This is not a guaranteed divorce statement. It is a technical strength label based on calculated pressure factors.", "mute"),
        Spacer(1, 8),
        premium_block(
            "6th/8th/12th links, Rahu/Ketu axis, Saturn/Mars affliction, weak 2nd house, D9 proxy and transit pressure",
            f"Divorce indication is {strength_word(relation_score(c)[0])}.",
            "The indication rises only when multiple technical pressure factors repeat; one factor alone is not treated as destiny.",
            "Use this page for caution and timing. Do not convert it into fear or a guaranteed outcome."),
    ])

def reconciliation_indicators(c):
    score, factors = relation_score(c)
    items = [
        "Benefic aspect on 7th: " + ("; ".join(house_support(c, 7)) or "not directly flagged"),
        f"Venus strength: {c['planets']['Venus']['dignity']} in house {c['planets']['Venus']['house']}.",
        f"Jupiter strength: {c['planets']['Jupiter']['dignity']} in house {c['planets']['Jupiter']['house']}.",
        f"2nd house family support: lord {c['house_lords'][2]} in house {c['planets'][c['house_lords'][2]]['house']}.",
        f"11th house repair/support: lord {c['house_lords'][11]} in house {c['planets'][c['house_lords'][11]]['house']}.",
        f"Upcoming AD support: {', '.join(x['lord'] for x in c['dasha']['upcoming_antardashas'][:3])}.",
        f"Jupiter transit support: house {c['transits']['Jupiter']['from_lagna']} from Lagna and house {c['transits']['Jupiter']['from_moon']} from Moon.",
    ]
    verdict = "Repair possible" if score <= 2 else "Repair difficult" if score <= 4 else "Repair unlikely"
    return page("Repair Factors", "Reconciliation Indicators", [
        Panel([h3(f"Verdict: {verdict}")] + bullets(items), border=GOLD_D),
        Spacer(1, 8),
        premium_block(
            "Benefic support to 7th, Venus/Jupiter strength, 2nd/11th houses, upcoming dasha and Jupiter transit",
            verdict,
            "Repair is possible when marriage-support houses and benefic planets still have enough strength to counter pressure factors.",
            "Use repair periods for calm discussion and mediation, not for repeating the same argument pattern."),
    ])

def dasha_timing(c):
    d = c["dasha"]; md = d["current_mahadasha"]; ad = d["current_antardasha"]
    items = [
        f"Conflict is active now because {md['lord']} Mahadasha activates house {c['planets'][md['lord']]['house']} and {ad['lord']} Antardasha activates house {c['planets'][ad['lord']]['house']}.",
        f"Current dasha test: {planet_line(c, md['lord'])}; {planet_line(c, ad['lord'])}.",
        f"Period tendency: {'separation pressure' if c['planets'][md['lord']]['house'] in SEPARATION_HOUSES or c['planets'][ad['lord']]['house'] in SEPARATION_HOUSES else 'repair/decision pressure without direct separation-house activation'}.",
        f"Intensity can continue until {pd(ad['end'])}, then shifts to {d['upcoming_antardashas'][0]['lord']} Antardasha.",
        "Avoid impulsive legal escalation, public accusations, and irreversible decisions when Mars/Rahu/Saturn are the active trigger planets.",
    ]
    return page("Operating Period", "Current Dasha & Timing", [Panel([h3("Dasha Reading")] + bullets(items), border=GOLD_D)])

def transit_timing(c):
    today = date.today()
    j = c["transits"]["Jupiter"]; s = c["transits"]["Saturn"]; r = c["transits"]["Rahu"]
    rows = [
        ("Calm discussion", f"Prefer Jupiter-supported windows while Jupiter is H{j['from_lagna']} from Lagna; use Thursdays and non-Mars days."),
        ("Mediation", f"Use the next supportive AD: {c['dasha']['upcoming_antardashas'][0]['lord']} from {pd(c['dasha']['upcoming_antardashas'][0]['start'])}."),
        ("Risky arguments", f"Saturn H{s['from_lagna']} and Rahu H{r['from_lagna']} periods; avoid pressure conversations on emotionally reactive days."),
        ("Legal escalation risk", "Avoid escalation when current AD/PD lords activate houses 6, 8 or 12."),
        ("Final decision", f"Review after {pd(c['dasha']['current_antardasha']['end'])}, when the present Antardasha changes."),
        ("Healing", f"Use Moon remedy days and Jupiter H{j['from_moon']} from Moon for emotional reset."),
    ]
    return page("Gochar Timing", "Transit-Based Decision Timing", [
        table(rows),
        Spacer(1, 8),
        Panel([h3("Transit Basis")] + bullets([f"Saturn: {s['sign']} H{s['from_lagna']} from Lagna / H{s['from_moon']} from Moon", f"Jupiter: {j['sign']} H{j['from_lagna']} from Lagna / H{j['from_moon']} from Moon", f"Rahu: {r['sign']} H{r['from_lagna']} from Lagna / H{r['from_moon']} from Moon"]), border=GOLD_D),
    ])

def final_verdict(c):
    score, factors = relation_score(c)
    return page("Judgement", "Final Relationship Verdict", [
        table([
            ("Separation Risk", level(score)),
            ("Divorce Indication", strength_word(score)),
            ("Reconciliation Chance", repair_word(score)),
            ("Best Path", verdict_path(score)),
            ("Best timing window", f"After current AD ends on {pd(c['dasha']['current_antardasha']['end'])}, unless urgent safety/legal facts exist."),
            ("Should not be done", "Do not make irreversible decisions during high anger, public conflict, or unverified suspicion."),
            ("Must be done immediately", "Stabilise communication, protect children/family logistics if relevant, and separate facts from emotional triggers."),
        ]),
        Spacer(1, 8),
        Panel([h3("Basis")] + bullets(factors[:8] or ["No high-risk factor dominated the calculation."]), border=GOLD_D),
        Spacer(1, 8),
        premium_block(
            f"Total relationship risk score {score}; dasha houses {active_houses(c)}; transit Saturn H{c['transits']['Saturn']['from_lagna']} and Jupiter H{c['transits']['Jupiter']['from_lagna']}",
            verdict_path(score),
            "The best path is selected from repeated chart pressure/support, not from emotional filler.",
            "Follow the 90-day plan before finalising any non-urgent irreversible decision."),
    ])

def remedies(c):
    rows = [
        ("Venus", "Friday; white/pastel colour; offer fragrance/flowers; correct disrespect, comparison and affection withdrawal."),
        ("Jupiter", "Thursday; yellow; donate food/books; seek ethical guidance before final decisions."),
        ("Moon", "Monday; white; water-based prayer/meditation; regulate sleep and emotional reactions."),
        ("Mars", "Tuesday; red used sparingly; physical discipline; no anger texting or confrontational meetings."),
        ("Saturn", "Saturday; dark blue/black used soberly; serve elderly/poor; patience and documented responsibility."),
        ("Rahu/Ketu", "Saturday/Tuesday; smoky or neutral tones; detach from obsession, spying and confusion loops."),
    ]
    return page("Corrections", "Remedies & Practical Corrections", [
        table(rows),
        Spacer(1, 8),
        Panel([h3("Mantra & Warning")] + bullets([
            "Use the simple mantra of the active dasha lord daily for 108 counts if already part of your spiritual practice.",
            "Behavioural correction is mandatory: remedies do not replace truthful conversation, legal safety or practical action.",
            "Gemstones should be worn only after personal astrologer confirmation.",
        ]), border=GOLD_D),
        Spacer(1, 8),
        premium_block(
            "Venus, Jupiter, Moon, Mars, Saturn and Rahu/Ketu relationship functions",
            "Remedies are selected for relationship harmony, protection, emotional stability, anger control, patience and detachment.",
            "Each remedy targets a specific planetary behaviour; without behaviour correction the ritual has little practical value.",
            "Do one remedy consistently and pair it with the matching behavioural correction for 90 days."),
    ])

def action_plan(c):
    return page("Next Steps", "90-Day Action Plan", [
        Panel([h3("Astrology-Aligned Plan")] + bullets([
            "First 15 days: silence, observation, no impulsive final decision; watch Moon/emotional triggers.",
            "Days 16-30: calm conversation or written clarity; keep the discussion factual and time-bound.",
            "Days 31-45: mediation, counselling or family discussion only if it reduces pressure rather than increasing blame.",
            "Days 46-60: decide repair vs structured separation based on behaviour, not promises alone.",
            "Days 61-90: choose legal, emotional and practical direction after reviewing the current dasha/transit pressure.",
        ]), border=GOLD_D),
        Spacer(1, 8),
        p("This report is for spiritual and astrological guidance. It does not replace legal, medical, psychological, or financial advice.", "mute"),
    ])

def build_divorce_report(client_chart, out_path, extra="", **kwargs):
    data = parse_payload(extra, **kwargs)
    client_chart["numerology"] = N.compute(client_chart["name"], client_chart["dob"], client_chart.get("gender", ""))
    partner = partner_chart_or_partial(data)
    score, factors = relation_score(client_chart)
    story = []
    story += cover(client_chart, data, partner)
    story += snapshot(client_chart, data, partner, score, factors)
    story += seventh_house(client_chart)
    story += navamsa(client_chart)
    story += compatibility(client_chart, partner)
    story += separation_indicators(client_chart)
    story += reconciliation_indicators(client_chart)
    story += dasha_timing(client_chart)
    story += transit_timing(client_chart)
    story += final_verdict(client_chart)
    story += remedies(client_chart)
    story += action_plan(client_chart)
    doc = ReportDoc(out_path)
    doc.build(story)
    return out_path
