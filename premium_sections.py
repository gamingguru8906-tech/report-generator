"""Reusable premium report sections for focused numerology PDFs.

Each builder returns reportlab flowables and may return [] when its required
optional input is missing. Report recipes decide which builders are used.
"""
from datetime import date
import calendar
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, NextPageTemplate

from pdfbuild_base import ST, GoldRule, LoShuGrid, Panel, bullets, GOLD_D, DEEP2, LINE, PW, MARGIN
import content as C
import numerology as N

MONTHS = ["","January","February","March","April","May","June","July","August","September","October","November","December"]

def fmt_date(d): return f"{d.day} {MONTHS[d.month]} {d.year}"
def core(num): return C.CORE.get(num, C.CORE.get(N.reduce_num(num, False), C.CORE[1]))
def root(num): return N.reduce_num(num, keep_masters=False)
def short_planet(num): return core(num)["planet"].split(" (")[0].replace("Higher ", "")
def kicker(t): return Paragraph(t.upper(), ST["kicker"])
def h1(t): return Paragraph(t, ST["h1"])
def h2(t): return Paragraph(t, ST["h2"])
def h3(t): return Paragraph(t, ST["h3"])
def body(t): return Paragraph(t, ST["body"])
def lead(t): return Paragraph(t, ST["lead"])

def _page(kick, title, parts):
    return [NextPageTemplate("content"), kicker(kick), h1(title), GoldRule(), Spacer(1, 4)] + parts + [PageBreak()]

def _two(left_title, left_items, right_title, right_items):
    tbl = Table([[
        Panel([h3(left_title)] + bullets(left_items), bg=DEEP2),
        Panel([h3(right_title)] + bullets(right_items, glyph="◇"), bg=HexColor("#EAEDF3")),
    ]], colWidths=[(PW - 2 * MARGIN - 12) / 2 - 4] * 2)
    tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (0,0), 8), ("RIGHTPADDING", (1,0), (1,0), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    return tbl

def _kv(rows):
    data = [[Paragraph(f'<font color="#8C8472">{k}</font>', ST["mute"]),
             Paragraph(v, ST["body"])] for k, v in rows if v]
    t = Table(data, colWidths=[42, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4), ("LINEBELOW", (0,0), (-1,-2), 0.35, LINE),
    ]))
    return t

def _num_line(num):
    cr = core(num)
    return f"<b>{num} - {cr['archetype']}.</b> {cr['essence']}"

def _remedy_items(r, focus="core"):
    cr = core(r["life_path"])
    items = [
        f"<b>Issue addressed:</b> Life Path {r['life_path']} shadow. <b>Why:</b> this is the main long-term pattern in the chart. <b>How:</b> begin on {cr['day']} and repeat: {cr['remedy']}",
        f"<b>Number correction:</b> use supportive numbers {', '.join(map(str, r['lucky_numbers'][:4]))} for dates, pins, launches and repeated choices because these roots sit friendlier with the birth chart.",
        "<b>Behaviour change:</b> keep the remedy practical and consistent; small weekly repetition is stronger than one intense burst.",
    ]
    if focus == "money":
        items[1] = "Schedule savings, invoices and launch pushes on your supportive numbers before adding risk."
    elif focus == "relationship":
        items[1] = "Use your supportive days for important conversations and repair rituals."
    elif focus == "mobile":
        items[1] = "Prefer mobile totals reducing to your supportive numbers; avoid changing numbers impulsively."
    elif focus == "name":
        items[1] = "Use one spelling consistently across signatures, documents, domains and social profiles."
    return items

def _premium_reading(r, basis, verdict, why, guidance):
    """Compact consultation-style block used across focused reports."""
    return Panel([h3("Premium Reading")]+bullets([
        f"<b>Calculation basis:</b> {basis}",
        f"<b>Clear verdict:</b> {verdict}",
        f"<b>Why this result came:</b> {why}",
        f"<b>Practical guidance:</b> {guidance}",
    ]), border=GOLD_D)

def sec_executive_summary(r):
    py = r["personal_year"]
    parts = [
        lead(f"{r['name']}'s chart is led by Life Path {r['life_path']}, Driver {r['driver']} and Destiny {r['destiny']}. This page translates the full report into the decisions that matter most now."),
        Spacer(1, 7),
        Panel([h3("Strongest Signals")] + bullets([
            _num_line(r["life_path"]),
            f"<b>Name vibration {r['destiny']}.</b> {'It supports the birth chart and can be used confidently.' if r['name_friendly'] else 'It needs conscious use or correction before major branding decisions.'}",
            f"<b>Personal Year {py}.</b> {C.PERSONAL_YEAR[py]}",
        ]), border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Priority Action")] + bullets(_remedy_items(r)[:2]), bg=HexColor("#F6ECEC")),
        Spacer(1, 7),
        _premium_reading(r,
            f"Birth Number {r['driver']}, Life Path {r['life_path']}, Destiny {r['destiny']}, Personal Year {py}, Lo Shu missing {', '.join(map(str,r['missing'])) or 'none'}",
            "Use Life Path for direction, Destiny for public choices, and Personal Year for timing.",
            f"The chart repeats the {short_planet(r['life_path'])} life-direction frequency while the name carries {short_planet(r['destiny'])}; the current year adds Personal Year {py} pressure.",
            "Prioritise one decision, one habit and one timing window instead of trying to change everything at once."),
    ]
    return _page("Premium Overview", "Executive Summary", parts)

def sec_core_blueprint(r):
    rows = [
        ("Life Path", f"{r['life_path']} - {short_planet(r['life_path'])}: {core(r['life_path'])['archetype']}"),
        ("Driver / Birth", f"{r['driver']} - {short_planet(r['driver'])}: daily nature and instinct"),
        ("Destiny / Name", f"{r['destiny']} - {short_planet(r['destiny'])}: public mission and reputation"),
        ("Soul Urge", f"{r['soul_urge']} - private motivation"),
        ("Personality", f"{r['personality']} - first impression"),
        ("Maturity", f"{r['maturity']} - second-half growth theme"),
    ]
    return _page("Number Architecture", "Core Number Blueprint", [
        lead("A premium reading starts by separating the role of each number. When these numbers are read together, the chart becomes practical instead of generic."),
        Spacer(1, 8), _kv(rows), Spacer(1, 8),
        Panel([h3("How To Use This Blueprint"), body("Let Life Path guide direction, Driver guide timing and day-to-day rhythm, Destiny guide naming and public identity, and Soul Urge guide emotional fulfilment.")]),
        Spacer(1, 7),
        _premium_reading(r,
            f"Driver {r['driver']}, Life Path {r['life_path']}, Destiny {r['destiny']}, Soul Urge {r['soul_urge']} and Personality {r['personality']}",
            "The chart should be read as one operating system, not isolated numbers.",
            "Short results become misleading when Driver, Life Path and name vibration are separated; together they show behaviour, direction and public outcome.",
            "When making decisions, check whether at least two of the three core numbers agree before acting."),
    ])

def sec_basic_details(r):
    rows = [
        ("Full name", r["name"]),
        ("Date of birth", fmt_date(r["dob"])),
        ("Gender", r.get("gender") or "Not specified"),
        ("Report type", (r.get("report_type") or "complete_numerology").replace("_", " ").title()),
        ("Prepared on", fmt_date(date.today())),
    ]
    return _page("Client Details", "Basic Details", [
        lead("These are the inputs used for the numerology calculations in this report."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 8),
        Panel([body("If any spelling or date detail is incorrect, regenerate the report after correction because name totals and birth-number calculations depend on exact input.")], bg=HexColor("#F6ECEC")),
    ])

def sec_core_number_summary(r):
    rows = [
        ("Birth Number", f"{r['driver']} - {short_planet(r['driver'])}"),
        ("Destiny Number", f"{r['destiny']} - {short_planet(r['destiny'])}"),
        ("Life Path", f"{r['life_path']} - {short_planet(r['life_path'])}"),
        ("Soul Urge", f"{r['soul_urge']} - {short_planet(r['soul_urge'])}"),
        ("Personality", f"{r['personality']} - {short_planet(r['personality'])}"),
        ("Personal Year", str(r["personal_year"])),
    ]
    return _page("At A Glance", "Core Number Summary", [
        lead("This summary gives the working numbers for the full report before each one is interpreted in detail."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 8),
        Panel([h3("Reading Priority"), body("Birth Number explains daily behaviour, Destiny explains name vibration, Life Path explains long direction, and Personal Year explains the current timing.")], border=GOLD_D),
    ])

def sec_birth_number(r):
    cr = core(r["driver"])
    return _page("Daily Engine", "Birth Number Analysis", [
        lead(f"Born on {fmt_date(r['dob'])}, your Driver or Mulank is {r['driver']}, ruled by {cr['planet']}."),
        Spacer(1, 7), body(cr["essence"]), Spacer(1, 8),
        _two("Natural Advantages", cr["strengths"], "Pressure Patterns", cr["shadow"]),
        Spacer(1, 8), Panel([h3("Best Use"), body(f"Use {cr['day']} for important starts, repairs and personal discipline. This is your easiest day to realign your own energy.")], border=GOLD_D),
        Spacer(1, 7),
        _premium_reading(r,
            f"Birth date {r['dob'].day} reduces to Birth Number {r['driver']} ruled by {cr['planet']}",
            f"Your daily behaviour is strongest when it uses the {cr['archetype']} quality consciously.",
            f"This result came because the day of birth shows instinctive reaction, while Life Path {r['life_path']} shows where that instinct must be directed.",
            f"Use {cr['day']} for habit resets and avoid acting from the first shadow pattern: {cr['shadow'][0].lower()}."),
    ])

def sec_destiny_number(r):
    cr = core(r["destiny"])
    return _page("Public Mission", "Destiny Number Analysis", [
        lead(f"The full name {r['name']} totals {r['destiny_total']} and reduces to Destiny {r['destiny']}, ruled by {cr['planet']}."),
        Spacer(1, 7), body(cr["essence"]), Spacer(1, 8),
        Panel([h3("Name And Birth Compatibility"), body("This name is harmonious with the birth chart." if r["name_friendly"] else f"This name is not fully harmonised with Driver {r['driver']}. Use the Name Vibration Audit before changing spelling, brand name or signature style.")], border=GOLD_D),
        Spacer(1, 7),
        _premium_reading(r,
            f"Chaldean name total {r['destiny_total']} reduces to Destiny {r['destiny']}; compared with Driver {r['driver']} and Life Path {r['life_path']}",
            "The name is supportive." if r["name_friendly"] else "The name needs conscious strengthening or careful correction.",
            f"The result came because name vibration {r['destiny']} {'matches' if r['name_friendly'] else 'does not fully match'} the friendly number set {', '.join(map(str,r['lucky_numbers'][:5]))}.",
            "Use one spelling consistently. If correction is needed, tune toward a friendly root rather than changing randomly."),
    ])

def sec_name_vibration_audit(r):
    cr = core(r["destiny"])
    parts = [
        lead(f"Your name acts like a repeated sound-code. Every signature, introduction and document repeats the {r['destiny']} vibration."),
        Spacer(1, 7),
        _kv([
            ("Analysed spelling", r["name"]),
            ("Chaldean total", f"{r['destiny_total']} -> {r['destiny']}"),
            ("Compatibility", "Aligned with birth numbers" if r["name_friendly"] else "Correction or consistent remedial use advised"),
            ("Target roots", ", ".join(map(str, r["lucky_numbers"][:5]))),
        ]),
        Spacer(1, 8),
        Panel([h3("Career, Money And Relationship Effect"), body(f"A {r['destiny']} name broadcasts {', '.join(s.lower() for s in cr['strengths'][:3])}. In career it shapes recall value; in money it affects trust and conversion; in relationships it colours first impression and communication style.")]),
        Spacer(1, 7),
        Panel([h3("Before / After Correction"), body("Before correction, use the current spelling consistently and strengthen its planet. After correction, avoid mixing spellings; the new name must be repeated everywhere for the vibration to settle.")], border=GOLD_D),
        Spacer(1, 7),
        _premium_reading(r,
            f"Name total {r['destiny_total']} -> {r['destiny']}; birth anchors Driver {r['driver']} and Life Path {r['life_path']}",
            "Aligned name vibration." if r["name_friendly"] else "Correction target should be considered before major branding or signature decisions.",
            f"The name creates the {core(r['destiny'])['archetype']} public field, but birth numbers decide whether that field converts smoothly.",
            f"Keep the current spelling if aligned; otherwise tune toward roots {', '.join(map(str,r['lucky_numbers'][:4]))} and use one final spelling everywhere."),
    ]
    return _page("Name Frequency", "Name Vibration Audit", parts)

def sec_lo_shu_advanced(r):
    present = [str(n) for n, c in r["grid_counts"].items() if c]
    parts = [
        lead("The advanced Lo Shu view separates abundance, absence and structural planes instead of treating the grid as a pass-fail chart."),
        Spacer(1, 7), LoShuGrid(r["grid_counts"]), Spacer(1, 8),
        Panel([h3("Grid Summary"), body(f"Present numbers: <b>{', '.join(present) or 'none'}</b>. Missing numbers: <b>{', '.join(map(str, r['missing'])) or 'none'}</b>. Complete planes: <b>{len(r['complete_planes'])}</b>.")], border=GOLD_D),
    ]
    if r["complete_planes"]:
        parts += [Spacer(1, 7), Panel([h3("Active Planes")] + bullets([C.PLANE_MEANING.get(p, p) for p in r["complete_planes"]]))]
    parts += [Spacer(1, 7), _premium_reading(r,
        f"Lo Shu present numbers {', '.join(present) or 'none'}, missing {', '.join(map(str,r['missing'])) or 'none'}, repeated {', '.join(map(str,r['repeated'].keys())) or 'none'}",
        "The grid is balanced." if not r["missing"] else "The grid needs conscious strengthening in missing-number areas.",
        "Missing cells show underused behavioural muscles; repeated cells show habits that become loud under pressure.",
        "Strengthen one missing number through weekly behaviour and moderate one repeated-number shadow before adding more remedies.")]
    return _page("Grid Intelligence", "Lo Shu Grid Advanced Analysis", parts)

def sec_lo_shu_grid_chart(r):
    present = [str(n) for n, c in r["grid_counts"].items() if c]
    return _page("Birth Grid", "Lo Shu Grid Chart", [
        lead("The Lo Shu Grid places the digits of the birth date, Birth Number and Life Path into the classical 3 by 3 grid."),
        Spacer(1, 7), LoShuGrid(r["grid_counts"]), Spacer(1, 8),
        Panel([h3("Grid Snapshot"), body(f"Present numbers: <b>{', '.join(present) or 'none'}</b>. Missing numbers: <b>{', '.join(map(str, r['missing'])) or 'none'}</b>. Repeated numbers: <b>{', '.join(str(n) for n in r['repeated']) or 'none'}</b>.")], border=GOLD_D),
    ])

def sec_missing_number_analysis(r):
    items = [f"<b>{n}</b>: {C.MISSING.get(n, 'Develop this number through steady conscious practice.')}" for n in r["missing"]]
    if not items:
        items = ["No missing numbers are present in the grid. Maintain balance rather than trying to force a remedy."]
    return _page("Grid Gaps", "Missing Number Analysis", [
        lead("Missing numbers show qualities that need conscious practice. They are not defects or fixed limitations."),
        Spacer(1, 8), Panel([h3("Numbers To Strengthen")] + bullets(items), border=GOLD_D),
        Spacer(1, 7), _premium_reading(r,
            f"Missing Lo Shu numbers: {', '.join(map(str,r['missing'])) or 'none'}",
            "No missing-number weakness is dominant." if not r["missing"] else "The missing numbers are the main training area in the birth grid.",
            "The result came because these digits do not appear naturally in the birth-date grid, so the behaviour must be developed consciously.",
            "Choose one missing number at a time and practise its behaviour in a measurable weekly action."),
    ])

def sec_repeated_number_analysis(r):
    items = [f"<b>{n} appears {c} times</b>: {C.REPEATED.get(n, 'This planet is amplified in daily behaviour.')}" for n, c in sorted(r["repeated"].items())]
    if not items:
        items = ["No strong repeated-number pressure is present. The grid is relatively even."]
    return _page("Amplified Energy", "Repeated Number Analysis", [
        lead("Repeated numbers show energies that become loud in behaviour, habits and decision-making."),
        Spacer(1, 8), Panel([h3("Amplified Numbers")] + bullets(items), border=GOLD_D),
        Spacer(1, 7), _premium_reading(r,
            f"Repeated Lo Shu numbers: {', '.join(f'{n}x{c}' for n,c in sorted(r['repeated'].items())) or 'none'}",
            "Amplified energy is present." if r["repeated"] else "No repeated-number pressure dominates the grid.",
            "Repeats intensify a planet's strength and shadow, so the same quality can become talent or excess depending on behaviour.",
            "Use the strength deliberately and watch the first shadow response during stress."),
    ])

def sec_planes_analysis(r):
    active = [C.PLANE_MEANING.get(p, p) for p in r["complete_planes"]]
    if not active:
        active = ["No complete plane is present. This is common; the report should focus on strengthening missing numbers and balancing repeated ones."]
    return _page("Grid Planes", "Mental, Emotional & Practical Plane", [
        lead("Planes show whether mental, emotional and practical energy forms a complete line in the grid."),
        Spacer(1, 8), Panel([h3("Active Planes")] + bullets(active), border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("How To Use This"), body("A complete plane is a natural pathway. A missing plane is a training area. Neither should be read as a guarantee or a fear-based prediction.")]),
    ])

def sec_personality_strengths(r):
    nums = [r["life_path"], r["destiny"], r["driver"], r["personality"]]
    seen, items = set(), []
    for n in nums:
        rn = root(n)
        if rn in seen:
            continue
        seen.add(rn)
        items.append(f"<b>{core(n)['archetype']} ({n})</b>: {core(n)['strengths'][0]}; {core(n)['strengths'][1].lower()}.")
    return _page("Natural Gifts", "Personality Strengths", [
        lead("These are the strengths that can be used consciously in career, relationships, money and personal growth."),
        Spacer(1, 8), Panel([h3("Dominant Strengths")] + bullets(items), border=GOLD_D),
    ])

def sec_hidden_weaknesses(r):
    nums = [r["life_path"], r["driver"], r["destiny"]]
    items = [f"<b>{n} shadow</b>: {core(n)['shadow'][0]}" for n in nums]
    if r["missing"]:
        items.append(f"<b>Missing-number sensitivity</b>: {C.MISSING.get(r['missing'][0], 'A missing grid number needs conscious practice.')}")
    return _page("Growth Edges", "Hidden Weaknesses", [
        lead("Hidden weaknesses are better read as growth edges. The purpose is awareness and correction, not fear."),
        Spacer(1, 8), Panel([h3("Patterns To Watch")] + bullets(items), bg=HexColor("#F6ECEC"), border=GOLD_D),
    ])

def sec_missing_repeated(r):
    missing = [f"<b>{n}</b>: {C.MISSING.get(n, 'Develop this number through steady conscious practice.')}" for n in r["missing"]]
    repeated = [f"<b>{n} appears {c} times</b>: {C.REPEATED.get(n, 'This planet is amplified in daily behaviour.')}" for n, c in sorted(r["repeated"].items())]
    if not missing:
        missing = ["No missing grid numbers. The task is balance, not repair."]
    if not repeated:
        repeated = ["No strong repeated-number pressure. Your grid is relatively even."]
    return _page("Grid Balance", "Missing / Repeated Number Analysis", [
        lead("Missing numbers show underused muscles. Repeated numbers show overactive habits. Both are useful only when read as training notes."),
        Spacer(1, 8), _two("Missing Numbers", missing[:5], "Repeated Numbers", repeated[:5]),
    ])

def sec_current_blockage(r):
    if r["karmic_lessons"]:
        title = f"Karmic lesson {', '.join(map(str, r['karmic_lessons'][:3]))}"
        detail = C.KARMIC_LESSON.get(r["karmic_lessons"][0], "")
    elif r["missing"]:
        title = f"Missing grid number {r['missing'][0]}"
        detail = C.MISSING.get(r["missing"][0], "")
    else:
        title = f"Life Path {r['life_path']} shadow"
        detail = core(r["life_path"])["shadow"][0]
    return _page("Where Energy Sticks", "Current Life Blockage", [
        lead("This section identifies the most practical blockage to work with now. It is guidance, not a verdict."),
        Spacer(1, 8), Panel([h3(title), body(detail)], bg=HexColor("#F6ECEC"), border=GOLD_D),
        Spacer(1, 8), Panel([h3("Correction Path"), body("Turn the blockage into one repeated weekly habit: one conversation, one saved amount, one practice session, one completed promise. Numerology becomes useful when it changes behaviour.")]),
    ])

def sec_query_resolution(r):
    q = (r.get("query") or r.get("extra") or "").strip()
    if not q or r.get("report_type") in {"mobile", "mobile_number_analysis", "business", "business_name_report", "baby", "baby_name_report"}:
        return []
    return _page("Personal Focus", "Personal Query Resolution", [
        lead(f"Your stated focus: {q}"),
        Spacer(1, 8),
        Panel([h3("Numerology Lens"), body(f"Read this question through Life Path {r['life_path']} for direction, Driver {r['driver']} for timing, and Personal Year {r['personal_year']} for the current cycle. The answer is strongest when it respects all three.")], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Recommended Next Step"), body("Choose the option that increases alignment, consistency and responsibility without relying on fear or guaranteed outcomes.")]),
    ])

def sec_career_direction(r):
    cr = core(r["life_path"])
    return _page("Work And Calling", "Career Direction", [
        lead(f"Your career should pay you for the natural gifts of Life Path {r['life_path']}, then use Destiny {r['destiny']} as your public style."),
        Spacer(1, 7),
        Panel([h3("Core Direction"), body(C.CAREER.get(r["life_path"], C.CAREER[root(r["life_path"])]))], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Job vs Business Suitability"), body("Business is favoured when your chart shows strong 1, 4, 5, 8 or 9 influence; job or advisory tracks are easier when 2, 3, 6 or 7 need stability first. Your current chart should prioritise roles that use " + ", ".join(s.lower() for s in cr["strengths"][:2]) + ".")]),
        Spacer(1, 7),
        _premium_reading(r,
            f"Life Path {r['life_path']} for vocation, Destiny {r['destiny']} for public skill, Driver {r['driver']} for work rhythm",
            f"Career should centre on {core(r['life_path'])['archetype']} strengths and present through Destiny {r['destiny']}.",
            "This result came because Life Path shows the work that sustains motivation, while Destiny shows how others recognise value.",
            "Choose roles where your natural strength is paid directly; avoid roles that reward the opposite of your core number."),
    ])

def sec_profession_matrix(r):
    nums = [r["life_path"], r["destiny"], r["driver"]]
    rows = []
    for n in nums:
        rows.append((f"Number {n} - {short_planet(n)}", C.CAREER.get(n, C.CAREER[root(n)])))
    return _page("Career Fit", "Profession Compatibility Matrix", [
        lead("The best profession sits where birth direction, name expression and daily temperament overlap."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 8), Panel([h3("Personal Brand Potential"), body(f"Build public recall around the {core(r['destiny'])['archetype']} quality of Destiny {r['destiny']}; this is what your name can become known for.")], border=GOLD_D),
    ])

def sec_money_pattern(r):
    return _page("Wealth Behaviour", "Money Pattern", [
        lead("This reading focuses on earning style, saving rhythm, money leakage and the difference between job income and business flow."),
        Spacer(1, 7),
        Panel([h3("Earning Style"), body(C.WEALTH.get(r["life_path"], C.WEALTH[root(r["life_path"])]))], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Saving / Spending Pattern"), body(C.WEALTH.get(r["driver"], C.WEALTH[root(r["driver"])]))]),
        Spacer(1, 7),
        Panel([h3("Money Leakage"), body("The main leakage usually appears through the shadow of your Life Path: " + core(r["life_path"])["shadow"][0] + ". Track this in real expenses, not emotion.")], bg=HexColor("#F6ECEC")),
        Spacer(1, 7),
        _premium_reading(r,
            f"Life Path {r['life_path']} for earning style, Driver {r['driver']} for spending rhythm, Personal Year {r['personal_year']} for timing",
            "Money improves through behaviour correction before risk-taking.",
            f"The leakage is linked to the shadow of Life Path {r['life_path']} and the daily reaction pattern of Driver {r['driver']}.",
            "Use supportive dates for invoices/savings and track one leakage category for 90 days."),
    ])

def sec_relationship_pattern(r):
    return _page("Heart Pattern", "Relationship & Marriage Pattern", [
        lead("Relationship numerology reads behaviour, emotional need, communication pattern and compatibility potential. It should never be used to create fear."),
        Spacer(1, 7),
        Panel([h3("Relationship Behaviour"), body(C.LOVE.get(r["life_path"], C.LOVE[root(r["life_path"])]))], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Emotional Needs"), body(C.LOVE.get(r["soul_urge"], C.LOVE[root(r["soul_urge"])]))]),
        Spacer(1, 7),
        Panel([h3("Conflict Pattern And Communication Advice"), body(f"Under pressure, the shadow of Life Path {r['life_path']} can show as {core(r['life_path'])['shadow'][0].lower()}. Repair it by naming needs early, asking one clear question, and avoiding silent scorekeeping.")], bg=HexColor("#F6ECEC")),
        Spacer(1, 7),
        _premium_reading(r,
            f"Life Path {r['life_path']} for behaviour, Soul Urge {r['soul_urge']} for emotional need, Driver {r['driver']} for reaction style",
            "Relationship harmony depends on making the private Soul Urge visible before conflict starts.",
            "This result came because outer behaviour and inner need are read from different numbers; mismatch creates misunderstanding.",
            "State the need directly, use one clear question, and do not let the Life Path shadow become the communication style."),
    ])

def sec_karmic_lesson_analysis(r):
    lessons = r.get("karmic_lessons") or []
    if lessons:
        items = [f"<b>{n}</b>: {C.KARMIC_LESSON.get(n, 'Practice this number consciously through daily behaviour.')}" for n in lessons]
    else:
        items = ["No formal Chaldean karmic lesson is missing from the name. Focus on balancing repeated numbers, grid gaps and Life Path shadow patterns."]
    if r.get("karmic_debts"):
        items.append(f"Karmic debt numbers present: <b>{', '.join(map(str, r['karmic_debts']))}</b>. Treat these as accelerated lessons, not punishment.")
    return _page("Soul Curriculum", "Karmic Lesson Analysis", [
        lead("Karmic lessons show qualities the name does not naturally carry. They are developed through repetition, humility and practical action."),
        Spacer(1, 8), Panel([h3("Lessons To Develop")] + bullets(items), border=GOLD_D),
    ])

def sec_mobile_compatibility(r):
    m = r.get("mobile")
    if not m:
        return []
    cr = core(m["root"])
    friendly = m["root"] in set(r["lucky_numbers"])
    return _page("Number Match", "Mobile Number Compatibility", [
        lead(f"The mobile number {m['number']} reduces to {m['root']}, ruled by {cr['planet']}."),
        Spacer(1, 8),
        Panel([h3("Compatibility Result"), body("This mobile number is compatible with the core chart." if friendly else f"This mobile number is usable but not ideal. A stronger daily-use number would reduce to {', '.join(map(str, r['lucky_numbers'][:4]))}.")], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Practical Guidance"), body("Do not change a working number out of fear. If changing naturally, choose a total that supports the birth chart and has balanced repeated digits.")]),
    ])

def sec_name_correction_suggestions(r):
    targets = r["lucky_numbers"][:5] or [root(r["driver"])]
    rows = []
    for tr in targets:
        cr = core(tr)
        rows.append((f"Target root {tr}", f"{short_planet(tr)} - supports {', '.join(s.lower() for s in cr['strengths'][:2])}."))
    return _page("Name Tuning", "Name Correction Suggestions", [
        lead("Name correction should be handled carefully. This automated section gives safe target vibrations, not a forced spelling."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 8),
        Panel([h3("Correction Rule"), body("If correcting the name, tune spelling toward one of the target roots and use the final spelling consistently across signature, documents, brand handles and public profiles.")], border=GOLD_D),
    ])

def sec_compatibility_analysis(r):
    p = r.get("partner")
    if not p:
        return _page("Compatibility", "Compatibility Analysis", [
            lead("A complete compatibility section needs the partner's name and date of birth. Since that data is missing, this report keeps the guidance focused on your own relationship pattern."),
            Spacer(1, 8), Panel([h3("Your Harmonious Numbers"), body(f"Partner numbers that tend to feel easier with your chart: <b>{', '.join(map(str, r['lucky_numbers'][:5]))}</b>. Conscious communication matters more than any single number.")], border=GOLD_D),
            Spacer(1, 7), _premium_reading(r,
                f"Your Life Path {r['life_path']}, Soul Urge {r['soul_urge']} and lucky roots {', '.join(map(str,r['lucky_numbers'][:5]))}",
                "Compatibility cannot be fully judged without partner DOB/name.",
                "This limitation exists because couple analysis needs both charts; using only one chart would create false certainty.",
                "Use this page as your relationship style guide until partner data is available."),
        ])
    rows = [
        ("Driver", f"You {r['driver']} / Partner {p['driver']}"),
        ("Life Path", f"You {r['life_path']} / Partner {p['life_path']}"),
        ("Destiny", f"You {r['destiny']} / Partner {p['destiny']}"),
        ("Soul Urge", f"You {r['soul_urge']} / Partner {p['soul_urge']}"),
    ]
    return _page("Two Charts", "Compatibility Analysis", [
        lead(f"Compatibility for {r['name']} and {p['name']} is read by comparing daily nature, life direction, public style and emotional need."),
        Spacer(1, 8), _kv(rows), Spacer(1, 8),
        Panel([h3("Marriage Delay Indicators"), body("Delay indicators are treated as timing friction, not fixed fate. Strong 4, 7 or 8 pressure, difficult personal years, or clashing Drivers suggest patience, family clarity and mature communication before formal commitment.")], bg=HexColor("#F6ECEC")),
        Spacer(1, 7), _premium_reading(r,
            f"Driver, Life Path, Destiny and Soul Urge compared for both partners",
            "Compatibility depends on rhythm and emotional need, not one number alone.",
            "The result came because Driver shows daily friction, Life Path shows direction, Destiny shows public style and Soul Urge shows private need.",
            "Repair works best when both people respect the other's Soul Urge instead of arguing only from Driver reactions."),
    ])

def sec_mobile_analysis(r):
    m = r.get("mobile")
    if not m:
        return []
    cr = core(m["root"])
    digits = [int(d) for d in re.findall(r"\d", m["number"])]
    counts = {i: digits.count(i) for i in range(1, 10)}
    missing = [str(i) for i, c in counts.items() if c == 0]
    repeated = [f"{i}x{c}" for i, c in counts.items() if c >= 2]
    friendly = m["root"] in set(r["lucky_numbers"])
    return _page("Daily Contact Code", "Mobile Number Analysis", [
        lead(f"Mobile number {m['number']} totals {m['total']} and reduces to {m['root']}, ruled by {cr['planet']}."),
        Spacer(1, 7), body(cr["essence"]), Spacer(1, 7),
        _two("Repeated / Missing Digits", [f"Repeated: {', '.join(repeated) or 'none'}", f"Missing: {', '.join(missing) or 'none'}"], "Money / Stress Effect", [
            "Supportive for business and payments." if friendly else f"Not fully aligned; prefer totals {', '.join(map(str, r['lucky_numbers'][:3]))}.",
            "Repeated daily exposure can amplify the number's shadow: " + cr["shadow"][0],
        ]),
        Spacer(1, 8),
        Panel([h3("Ideal Patterns And Digits To Avoid"), body(f"Choose totals reducing to <b>{', '.join(map(str, r['lucky_numbers'][:4]))}</b>. Avoid totals that repeatedly trigger your weak grid numbers unless balanced by a strong total.")], border=GOLD_D),
        Spacer(1, 7), Panel([h3("Mobile Remedy Plan")] + bullets(_remedy_items(r, "mobile"))),
        Spacer(1, 7), _premium_reading(r,
            f"Mobile total {m['total']} -> root {m['root']}; compared with Driver {r['driver']}, Life Path {r['life_path']} and lucky roots {', '.join(map(str,r['lucky_numbers'][:4]))}",
            "Compatible daily number." if friendly else "Usable but not ideal for repeated daily use.",
            "The mobile number repeats through calls, payments and OTPs, so its root becomes a daily environmental vibration.",
            "Keep it if life is stable; if changing naturally, choose a total that supports the birth chart and has balanced digit distribution."),
    ])

def sec_business_name_analysis(r):
    b = r.get("business")
    if not b:
        return []
    cr = core(b["root"])
    return _page("Commercial Frequency", "Business Name Analysis", [
        lead(f"{b['name']} totals {b['total']} and reduces to {b['root']}, ruled by {cr['planet']}."),
        Spacer(1, 7),
        Panel([h3("Brand Energy And Customer Attraction"), body(cr["essence"])], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Money Vibration And Industry Compatibility"), body(f"This name works best where {', '.join(s.lower() for s in cr['strengths'][:3])} are commercially valuable. Compare this with the owner's Driver {r['driver']} and Life Path {r['life_path']} before final registration.")]),
        Spacer(1, 7),
        Panel([h3("Launch Date Guidance And Correction Options"), body(f"Launch on dates reducing to {', '.join(map(str, r['lucky_numbers'][:4]))}. If correcting, tune spellings toward those roots and keep the final name consistent across GST, domain, signage and invoices.")], bg=HexColor("#F6ECEC")),
        Spacer(1, 7),
        _premium_reading(r,
            f"Business name total {b['total']} -> {b['root']}; owner Driver {r['driver']} and Life Path {r['life_path']}",
            "The name can work commercially when its root supports the industry and owner rhythm.",
            f"This result came because the name broadcasts {short_planet(b['root'])} energy while the owner must operate from Driver {r['driver']}.",
            "Use one final spelling on registration, domain, signage and invoices; launch on a supportive date rather than during scattered preparation."),
    ])

def sec_baby_name_analysis(r):
    if r.get("report_type") != "baby_name_report" and not r.get("baby"):
        return []
    baby = r.get("baby") or {}
    pref = baby.get("pref", "")
    targets = baby.get("target_roots") or r["lucky_numbers"][:4]
    bank = N.names_by_root(C.BABY_NAME_POOL)
    suggestions = []
    for tr in targets:
        names = bank.get(tr, [])[:5]
        if names:
            suggestions.append(f"<b>Root {tr}:</b> {', '.join(names)}")
    return _page("Naming Support", "Baby Name Analysis", [
        lead(f"The child's birth chart shows Driver {r['driver']} and Life Path {r['life_path']}. A name should support both emotional steadiness and future talent expression."),
        Spacer(1, 7),
        Panel([h3("Compatibility With DOB"), body(f"Recommended name roots: <b>{', '.join(map(str, targets))}</b>. These support the birth vibration without forcing a personality.")], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Emotional, Education, Talent And Future Career Support"), body(f"Names in these roots strengthen {', '.join(core(t)['strengths'][0].lower() for t in targets[:3])}. Final selection should also respect family meaning, pronunciation and culture.")]),
        Spacer(1, 7),
        Panel([h3("Name Suggestions")] + bullets(suggestions or ["Share preferred initials or shortlisted names for a tighter personalised list."])),
        Spacer(1, 5), body(f"Parent preference noted: {pref}" if pref else ""),
        Spacer(1, 7),
        _premium_reading(r,
            f"Child Driver {r['driver']}, Life Path {r['life_path']} and target name roots {', '.join(map(str,targets))}",
            "Choose a name that supports birth vibration rather than forcing a fashionable sound.",
            "The recommendation comes from matching the name root to the child's birth numbers and friendly roots.",
            "Shortlist names by meaning and pronunciation first, then finalise only if the Chaldean root stays supportive."),
    ])

def sec_house_number_analysis(r):
    h = r.get("house")
    if not h:
        return []
    cr = core(h["root"])
    return _page("Home Frequency", "House Number Analysis", [
        lead(f"House number {h['number']} totals {h['total']} and reduces to {h['root']}, ruled by {cr['planet']}."),
        Spacer(1, 7),
        Panel([h3("Family Peace And Rest Energy"), body(cr["essence"])], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Money Flow And Work From Home"), body(f"This home supports {', '.join(s.lower() for s in cr['strengths'][:2])}. If business is run from home, keep accounts, signage and work zones cleanly separated.")]),
        Spacer(1, 7),
        Panel([h3("Remedies")] + bullets([cr["remedy"], "Keep the entrance bright, uncluttered and marked with a supportive colour for the house root."])),
        Spacer(1, 7),
        _premium_reading(r,
            f"House total {h['total']} -> root {h['root']}; compared with resident Driver {r['driver']} and Life Path {r['life_path']}",
            "The home vibration is supportive when the household routine matches the house root.",
            "This result came because house numbers affect the repeated entry, rest and family-energy field.",
            "Strengthen the entrance, reduce clutter, and use the remedy as a household habit rather than a superstition."),
    ])

def sec_vehicle_number_analysis(r):
    v = r.get("vehicle")
    if not v:
        return []
    cr = core(v["root"])
    friendly = v["root"] in set(r["lucky_numbers"])
    return _page("Travel Frequency", "Vehicle Number Analysis", [
        lead(f"Vehicle number {v['number']} totals {v['total']} and reduces to {v['root']}, ruled by {cr['planet']}."),
        Spacer(1, 7),
        Panel([h3("Travel Smoothness And Safety Tendency"), body(cr["essence"])], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Driver Compatibility"), body("This number supports the driver chart." if friendly else f"This number is usable but not ideal for the driver chart. Favour future numbers reducing to {', '.join(map(str, r['lucky_numbers'][:3]))}.")]),
        Spacer(1, 7),
        Panel([h3("Remedies")] + bullets([cr["remedy"], "Keep the vehicle clean, serviced on time, and avoid risky driving on emotionally heavy days."])),
        Spacer(1, 7),
        _premium_reading(r,
            f"Vehicle total {v['total']} -> root {v['root']}; compared with Driver {r['driver']} and lucky roots {', '.join(map(str,r['lucky_numbers'][:3]))}",
            "The vehicle number supports the driver." if friendly else "The vehicle number is usable but should be handled with more discipline.",
            "This result came because vehicle numbers repeat during travel and should not sharply conflict with the driver's core number.",
            "Do the practical remedy: service on time, avoid speed during emotional stress, and choose supportive dates for major travel."),
    ])

def sec_personal_year_forecast(r):
    py = r["personal_year"]
    return _page("Current Cycle", "Personal Year Forecast", [
        lead(f"{r['personal_year_for']} is Personal Year {py} for this chart."),
        Spacer(1, 8),
        Panel([h3(f"Theme Of {r['personal_year_for']}"), body(C.PERSONAL_YEAR[py])], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("How To Use It"), body("Make major moves with the year's theme instead of forcing last year's strategy into a new cycle.")]),
        Spacer(1, 7),
        _premium_reading(r,
            f"DOB day/month plus calendar year {r['personal_year_for']} reduce to Personal Year {py}",
            f"{r['personal_year_for']} should be handled as a Personal Year {py} cycle.",
            "This timing result came from the annual numerology cycle, which changes the best strategy even when your core numbers stay the same.",
            "Plan major actions according to the year theme and use monthly forecasts for timing, not guarantees."),
    ])

def sec_twelve_month_forecast(r):
    today = date.today()
    rows = []
    for k in range(12):
        m = today.month + k
        y = today.year
        while m > 12:
            m -= 12; y += 1
        py = N.reduce_num(sum(N.digits(r["dob"].day)) + sum(N.digits(r["dob"].month)) + sum(N.digits(y)), False)
        pm = N.reduce_num(py + N.reduce_num(m, False), False)
        theme = C.PERSONAL_MONTH[pm][0]
        rows.append((f"{MONTHS[m]} {y}", f"Personal Month {pm}: {theme}"))
    return _page("Month By Month", "12-Month Forecast", [
        lead("The next twelve months show when to push, consolidate, repair, study or release."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 7), _premium_reading(r,
            f"Personal Year and calendar month roots calculated from {fmt_date(r['dob'])}",
            "Each month changes the best action style; the year theme remains the main background.",
            "The result comes from combining the current Personal Year with each month number, so the timing is personal rather than generic.",
            "Use high-action months for launches and low-action months for repair, review and preparation."),
    ])

def sec_best_dates_calendar(r):
    today = date.today()
    targets = set([r["driver"]]) | set(r["lucky_numbers"][:4])
    rows = []
    for k in range(3):
        m = today.month + k
        y = today.year
        while m > 12:
            m -= 12; y += 1
        ndays = calendar.monthrange(y, m)[1]
        start = today.day if k == 0 else 1
        days = [str(d) for d in range(start, ndays + 1) if N.reduce_num(d, False) in targets][:9]
        rows.append((f"{MONTHS[m]} {y}", ", ".join(days) or "Use your power weekday instead"))
    return _page("Practical Timing", "Best Dates Calendar", [
        lead("These dates are supportive windows for launches, calls, interviews, proposals, repairs and intentional starts."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 8), Panel([body("Dates support effort; they do not replace preparation, ethics or practical judgement.")], bg=HexColor("#F6ECEC")),
        Spacer(1, 7), _premium_reading(r,
            f"Target dates reduce to Driver {r['driver']} or friendly roots {', '.join(map(str,r['lucky_numbers'][:4]))}",
            "These dates are supportive, not magical guarantees.",
            "The date list came from matching daily roots with your chart's friendlier numbers.",
            "Use them for prepared action; avoid using a good date to justify a rushed decision."),
    ])

def sec_lucky_colours_numbers_directions(r):
    cr_driver = core(r["driver"])
    cr_life = core(r["life_path"])
    directions = {
        1: "East", 2: "North-West", 3: "North-East", 4: "South-West",
        5: "North", 6: "South-East", 7: "West", 8: "West / South-West", 9: "South",
    }
    rows = [
        ("Lucky numbers", ", ".join(map(str, r["lucky_numbers"][:6]))),
        ("Birth-number colours", cr_driver["colour"]),
        ("Life-path colours", cr_life["colour"]),
        ("Power day", cr_driver["day"]),
        ("Supportive direction", directions.get(root(r["driver"]), "Use the cleanest, brightest direction available")),
        ("Supportive gemstone", f"{cr_driver['gem']} (consult before wearing)"),
    ]
    return _page("Daily Supports", "Lucky Colors, Numbers, Directions", [
        lead("These supports are practical reminders for timing, clothing, workspace choices, branding accents and repeated decisions."),
        Spacer(1, 8), _kv(rows),
        Spacer(1, 8), Panel([body("Use these as gentle supports, not rigid rules. Practical fit and personal comfort matter.")], bg=HexColor("#F6ECEC")),
        Spacer(1, 7), _premium_reading(r,
            f"Birth Number {r['driver']} and Life Path {r['life_path']} planetary correspondences",
            "Use supports as reminders for discipline and alignment.",
            "The colours, days and directions come from the planetary rulers of your strongest core numbers.",
            "Select what is practical and repeatable; comfort and context matter more than blind ritual."),
    ])

def sec_ninety_day_remedy_plan(r):
    return _page("Action Practice", "90-Day Remedy Plan", [
        lead("This plan turns the reading into steady practice without fear-based claims or unrealistic promises."),
        Spacer(1, 8),
        Panel([h3("Days 1-30")] + bullets(_remedy_items(r)[:2]), border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Days 31-60")] + bullets(["Repair one repeated behavioural pattern named in this report.", "Use one supportive date for a meaningful practical action."])),
        Spacer(1, 7),
        Panel([h3("Days 61-90")] + bullets(["Review what improved through consistency.", "Keep the smallest useful ritual and remove anything you cannot sustain."])),
    ])

def sec_manifestation_code(r):
    code = f"{r['driver']}-{r['life_path']}-{r['destiny']}"
    return _page("Personal Code", "Manifestation Code", [
        lead(f"Your practical manifestation code is <b>{code}</b>: act through Driver {r['driver']}, choose direction through Life Path {r['life_path']}, and present yourself through Destiny {r['destiny']}."),
        Spacer(1, 8),
        Panel([h3("How To Use The Code"), body(f"Before a decision, ask: does it match my daily nature ({r['driver']}), long path ({r['life_path']}) and public identity ({r['destiny']})? If two of three say no, slow down.")], border=GOLD_D),
        Spacer(1, 7), _premium_reading(r,
            f"Driver {r['driver']} + Life Path {r['life_path']} + Destiny {r['destiny']}",
            "Manifestation improves when action, direction and identity agree.",
            "This code is not a wish formula; it is a decision filter based on your three most practical numerology anchors.",
            "Use it before launches, conversations, branding decisions and commitments."),
    ])

def sec_personalized_affirmations(r):
    first = (r["name"].split() or ["I"])[0]
    affirmations = [
        f"I act with the clear strength of my Birth Number {r['driver']}.",
        f"I choose the long path of my Life Path {r['life_path']} with patience and confidence.",
        f"My name vibration {r['destiny']} supports the right people, work and opportunities finding me.",
        f"I use my Personal Year {r['personal_year']} wisely and take grounded action at the right time.",
        f"{first}, I turn awareness into steady practice.",
    ]
    return _page("Inner Practice", "Personalized Affirmations", [
        lead("Affirmations work best when paired with action. Read these before practical work, not as a substitute for it."),
        Spacer(1, 8), Panel([h3("Affirmations")] + bullets(affirmations), border=GOLD_D),
    ])

def sec_health_energy_pattern(r):
    cr = core(r["driver"])
    return _page("Wellbeing Rhythm", "Health / Energy Pattern", [
        lead("This is an energy and routine reading only. It is not a medical diagnosis or a substitute for qualified health advice."),
        Spacer(1, 8),
        Panel([h3("Energy Pattern"), body(f"Driver {r['driver']} shows how stress tends to move through behaviour. Watch the shadow pattern: {cr['shadow'][0].lower()}.")], border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Supportive Routine"), body(f"Use {cr['day']} as a weekly reset day. Keep sleep, hydration, food rhythm and movement simple enough to repeat.")]),
        Spacer(1, 7), _premium_reading(r,
            f"Driver {r['driver']} stress pattern and Life Path {r['life_path']} shadow",
            "Focus on routine stability, not diagnosis.",
            "The energy tendency comes from daily behaviour patterns, not medical testing.",
            "Use this as lifestyle awareness only and consult qualified professionals for health concerns."),
    ])

def sec_final_guidance(r):
    return _page("Closing Synthesis", "Final Guidance", [
        lead(f"{r['name']}, the strongest report is not the longest one. It is the one you can apply. Your first step is to honour Life Path {r['life_path']} and bring the name, dates and daily habits into that direction."),
        Spacer(1, 8),
        Panel([h3("Keep This Simple")] + bullets([
            f"Use supportive numbers: {', '.join(map(str, r['lucky_numbers'][:5]))}.",
            f"Repeat the core remedy for {short_planet(r['life_path'])} steadily.",
            "Treat challenges as training notes, never as fixed fate.",
        ]), border=GOLD_D),
        Spacer(1, 7),
        _premium_reading(r,
            f"Life Path {r['life_path']}, Destiny {r['destiny']}, Personal Year {r['personal_year']} and Lo Shu grid",
            "The next step is practical alignment, not more information.",
            "The report points to the same pattern repeatedly: use core strengths, correct shadows, and time decisions with the current cycle.",
            "Choose one remedy, one date window and one behavioural correction for the next 30 days."),
    ])

def sec_disclaimer(r):
    return _page("Important Note", "Disclaimer", [
        lead("This report is a numerology-based guidance document for reflection, timing and self-awareness."),
        Spacer(1, 8),
        Panel([h3("Use With Discernment")] + bullets([
            "Numerology describes tendencies and timing patterns; it does not guarantee fixed outcomes.",
            "This report is not medical, legal, financial or psychological advice.",
            "Health and safety concerns should be discussed with qualified professionals.",
            "Remedies are spiritual and behavioural supports, not substitutes for practical action.",
            "Free will, effort, ethics and context remain central in every decision.",
        ]), border=GOLD_D),
    ])

PREMIUM_SECTIONS = {
    "executive_summary": sec_executive_summary,
    "basic_details": sec_basic_details,
    "core_number_summary": sec_core_number_summary,
    "core_number_blueprint": sec_core_blueprint,
    "birth_number_analysis": sec_birth_number,
    "destiny_number_analysis": sec_destiny_number,
    "name_vibration_audit": sec_name_vibration_audit,
    "lo_shu_grid_advanced": sec_lo_shu_advanced,
    "lo_shu_grid_chart": sec_lo_shu_grid_chart,
    "missing_number_analysis": sec_missing_number_analysis,
    "repeated_number_analysis": sec_repeated_number_analysis,
    "planes_analysis": sec_planes_analysis,
    "missing_repeated_analysis": sec_missing_repeated,
    "personality_strengths": sec_personality_strengths,
    "hidden_weaknesses": sec_hidden_weaknesses,
    "current_life_blockage": sec_current_blockage,
    "personal_query_resolution": sec_query_resolution,
    "career_direction": sec_career_direction,
    "profession_compatibility_matrix": sec_profession_matrix,
    "money_pattern": sec_money_pattern,
    "relationship_pattern": sec_relationship_pattern,
    "compatibility_analysis": sec_compatibility_analysis,
    "karmic_lesson_analysis": sec_karmic_lesson_analysis,
    "mobile_compatibility": sec_mobile_compatibility,
    "name_correction_suggestions": sec_name_correction_suggestions,
    "mobile_number_analysis": sec_mobile_analysis,
    "business_name_analysis": sec_business_name_analysis,
    "baby_name_analysis": sec_baby_name_analysis,
    "house_number_analysis": sec_house_number_analysis,
    "vehicle_number_analysis": sec_vehicle_number_analysis,
    "personal_year_forecast": sec_personal_year_forecast,
    "twelve_month_forecast": sec_twelve_month_forecast,
    "best_dates_calendar": sec_best_dates_calendar,
    "lucky_colours_numbers_directions": sec_lucky_colours_numbers_directions,
    "ninety_day_remedy_plan": sec_ninety_day_remedy_plan,
    "manifestation_code": sec_manifestation_code,
    "personalized_affirmations": sec_personalized_affirmations,
    "health_energy_pattern": sec_health_energy_pattern,
    "final_guidance": sec_final_guidance,
    "disclaimer": sec_disclaimer,
}
