"""Premium Palmistry PDF report renderer in the Veshann design language.

Driven entirely by palmistry.compute_palm_profile(): guided observations,
uploaded photos (embedded where available) and honest limitation notes.
"""
from __future__ import annotations

from datetime import date
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, NextPageTemplate, Image

from pdfbuild_base import ReportDoc, ST, GoldRule, Panel, bullets, GOLD, GOLD_L, GOLD_D, CREAM, MUTE, LINE, PW, MARGIN
import palm_content as PC
from quality_gate import audit_story

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

def fmt_date(d): return f"{d.day} {MONTHS[d.month]} {d.year}"
def h1(t): return Paragraph(t, ST["h1"])
def h3(t): return Paragraph(t, ST["h3"])
def body(t): return Paragraph(t, ST["body"])
def lead(t): return Paragraph(t, ST["lead"])
def kicker(t): return Paragraph(t.upper(), ST["kicker"])

def page(kick, title, parts):
    return [NextPageTemplate("content"), kicker(kick), h1(title), GoldRule(), Spacer(1, 4)] + parts + [PageBreak()]

def _photo_flowable(path, max_w=210, max_h=260):
    """Scaled palm photo, or None if unusable."""
    if not path:
        return None
    try:
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            w, h = im.size
        scale = min(max_w / w, max_h / h, 1.0)
        return Image(path, width=w * scale, height=h * scale)
    except Exception:
        return None

def photo_strip(c):
    """Side-by-side left/right palm photos with captions, or None."""
    cells, caps = [], []
    for side in ("left", "right"):
        fl = _photo_flowable(c["photos"].get(side))
        if fl:
            cells.append(fl)
            caps.append(Paragraph(f"{side.title()} palm (as submitted)", ST["mutec"]))
    if not cells:
        return None
    t = Table([cells, caps], colWidths=[(PW - 2 * MARGIN) / len(cells)] * len(cells))
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t

def cover(c):
    dom = c["dominant_hand"].title() if c["dominant_hand"] else "Not specified"
    S = [NextPageTemplate("content"), Spacer(1, 38)]
    S += [Paragraph("VESHANN ASTRO", ParagraphStyle("pcv", fontName="Cinzel-B", fontSize=22, textColor=GOLD_L, alignment=TA_CENTER, leading=26, tracking=4))]
    S += [Paragraph("HASTA SAMUDRIKA · PALMISTRY", ParagraphStyle("pcv2", fontName="Jost-L", fontSize=8.5, textColor=MUTE, alignment=TA_CENTER, tracking=3, spaceBefore=4))]
    S += [Spacer(1, 16), GoldRule(), Spacer(1, 14)]
    S += [Paragraph("Premium", ParagraphStyle("pt1", fontName="Cormorant-I", fontSize=30, textColor=CREAM, alignment=TA_CENTER, leading=30))]
    S += [Paragraph("PALMISTRY ANALYSIS REPORT", ParagraphStyle("pt2", fontName="Cinzel-B", fontSize=23, textColor=GOLD, alignment=TA_CENTER, leading=29, tracking=1))]
    S += [Spacer(1, 18), Paragraph("Prepared exclusively for", ST["mutec"]), Spacer(1, 4)]
    S += [Paragraph(c["name"].upper(), ParagraphStyle("pnm", fontName="Cinzel-B", fontSize=18, textColor=GOLD_L, alignment=TA_CENTER, leading=24, tracking=1))]
    S += [Spacer(1, 4), Paragraph(f"Born {fmt_date(c['dob'])} · Dominant hand: {dom} · Focus: {c['focus_area'].title()}", ST["quote"])]
    S += [Spacer(1, 18)]
    strip = photo_strip(c)
    if strip:
        S += [strip, Spacer(1, 12)]
    S += [GoldRule(), Paragraph(f"Prepared {fmt_date(date.today())} · Guided observation + photographic review method", ST["mutec"]), PageBreak()]
    return S

def how_to_read(c):
    return page("Begin Here", "How to Read This Report", [
        lead("Palmistry — Hasta Samudrika Shastra in the Indian tradition — reads the hand as a record of temperament and habit: "
             "the shape of the palm, the four major lines, and the mounts beneath the fingers. This report interprets your palm "
             "from the guided observations you provided and the photographs you submitted."),
        Spacer(1, 8),
        Panel([h3("Reading Rule"), body(
            "Every interpretation in this report is tied to a stated observation — an option you selected while looking at your own "
            "palm, or a feature visible in your photographs. Where an observation was not provided or a photo limits certainty, the "
            "report says so plainly and gives the balanced range of meanings instead of a confident guess. Nothing is invented.")], border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("How To Use It")] + bullets([
            "Read the hand-shape chapter first — it is the temperament frame every line sits inside.",
            "Each line chapter ends with one practical instruction; the closing action plan collects them in one place.",
            "Lines record tendencies and change subtly over years. Treat this as a mirror and a map, never a sentence.",
        ])),
        Spacer(1, 8),
        Paragraph(PC.DISCLAIMERS["general"], ST["mute"]),
    ])

def data_limits(c):
    provided = []
    if c["dominant_hand"]: provided.append(f"Dominant hand: {c['dominant_hand']}.")
    if c["hand_shape"]: provided.append(f"Hand shape observed: {PC.HAND_SHAPE[c['hand_shape']]['label']}.")
    for key, table, nm in (("life_line", PC.LIFE_LINE, "Life line"), ("head_line", PC.HEAD_LINE, "Head line"),
                           ("heart_line", PC.HEART_LINE, "Heart line"), ("fate_line", PC.FATE_LINE, "Fate line")):
        if c[key]:
            provided.append(f"{nm} observed: {table[c[key]]['label']}.")
    for side in ("left", "right"):
        if c["photos"].get(side):
            q = c["photo_quality"][side]
            provided.append(f"{side.title()} palm photo received ({q['width']}x{q['height']}px): " + "; ".join(q["notes"]) + ".")
    return page("Data & Limitations", "Palm Data & Limitations", [
        lead("A trustworthy reading begins by being honest about its inputs. This page lists exactly what this report is built on "
             "and where missing or limited data narrows what can responsibly be said."),
        Spacer(1, 8),
        Panel([h3("Observations & Photos Used")] + bullets(provided or ["No structured observations were received; this report presents the classical framework applied to the general palm, with your details used for personalisation."]), border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("Limitations Applied")] + bullets(c["limitations"] or ["All requested observations and photos were provided; no structural limitation applies."]), bg=HexColor("#F6ECEC")),
        Spacer(1, 8),
        Paragraph(PC.DISCLAIMERS["photo"], ST["mute"]),
        Spacer(1, 4),
        Paragraph("Confidentiality: your photographs and details are used only to prepare this report, are stored with your order for review, and are never shared or published.", ST["mute"]),
    ])

def hands_compare(c):
    dom = c["dominant_hand"]
    items = [PC.DOMINANT_HAND_NOTE]
    if dom:
        other = "left" if dom == "right" else "right"
        items.append(f"You write with your <b>{dom}</b> hand, so this report reads your {dom} palm as the life you are actively building, "
                     f"and your {other} palm as inherited temperament and latent potential.")
        if c["photos"].get(dom) and c["photos"].get(other):
            items.append("Both palms were submitted — a genuine comparison is possible. Look for lines that are clearer, longer or "
                         "differently shaped on the dominant hand: each such difference marks a trait you have consciously developed "
                         "beyond your starting settings. Features stronger on the non-dominant hand mark capacities not yet fully claimed.")
        elif c["photos"].get(dom) or c["photos"].get(other):
            items.append("Only one palm photograph was available, so the dominant/non-dominant comparison is described in method here "
                         "and can be completed if the second palm is submitted later.")
    return page("Two Hands", "Dominant & Non-Dominant Hand", [
        lead("Palmistry never reads one hand in isolation. The two palms answer two different questions: who you started as, "
             "and who you are becoming."),
        Spacer(1, 8),
        Panel([h3("The Method — And Your Hands")] + [body(x) for x in items], border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("Why This Matters"), body(
            "This matters because it converts palmistry from fortune-telling into feedback: the gap between your two palms is a record "
            "of effort already made, and a pointer to development still available. A practical way to work with this is to re-examine "
            "both palms once a year in good light — the comparison, not any single line, is the most personal finding a palm can offer.")]),
    ])

def _feature_page(kick, title, section_intro, profile, observed_label, extra_panels=None):
    parts = [lead(section_intro), Spacer(1, 8),
             Panel([h3(f"What Was Observed: {observed_label}"), body(
                 f"The strongest signal here is {profile['meaning']}.")], border=GOLD_D),
             Spacer(1, 8),
             Panel([h3("Gift & Caution")] + bullets([
                 f"<b>Gift:</b> {profile['strength']}.",
                 f"<b>Caution:</b> {profile['caution']}. This matters because a hand's challenges are almost always its gifts applied one notch too far.",
             ])),
             Spacer(1, 8),
             Panel([h3("How To Work With It"), body(
                 f"A practical way to work with this pattern is: {profile['action']}. "
                 "Treat this as a standing habit, not a one-time fix — lines describe tendencies, and tendencies respond to practice.")], bg=HexColor("#F6ECEC"))]
    if extra_panels:
        parts += extra_panels
    return page(kick, title, parts)

def shape_page(c):
    pr = c["shape_profile"]
    if pr:
        label = pr["label"]
        profile = pr
    else:
        label = "Not determined from the provided inputs"
        profile = PC.UNKNOWN
    return _feature_page("Temperament Frame", "Hand Shape & Temperament",
        "Before any line is read, the hand's overall shape sets the temperament frame — the elemental typology of palm and finger "
        "proportions used across palmistry traditions. Every line meaning in the following chapters is coloured by this frame.",
        profile, label,
        extra_panels=[Spacer(1, 8), Panel([h3("The Four Types At A Glance")] + bullets([
            f"<b>{v['label']}:</b> {v['meaning']}." for v in PC.HAND_SHAPE.values()]))])

def life_page(c):
    label = PC.LIFE_LINE[c["life_line"]]["label"] if c["life_line"] else "Not observed — balanced reading given"
    return _feature_page("Vitality", "The Life Line",
        "The life line curves around the ball of the thumb. Contrary to the popular myth, it does not measure lifespan — classical "
        "palmistry reads it as vitality, physical resilience and the depth of your engagement with life. It is the palm's energy meter, "
        "not its clock.", c["life_profile"], label)

def head_page(c):
    label = PC.HEAD_LINE[c["head_line"]]["label"] if c["head_line"] else "Not observed — balanced reading given"
    return _feature_page("Mind", "The Head Line",
        "The head line crosses the palm's centre and is read as your thinking style — how you analyse, decide and imagine. "
        "It is the most consequential line for career and decisions, because every choice passes through the style it describes.",
        c["head_profile"], label)

def heart_page(c):
    label = PC.HEART_LINE[c["heart_line"]]["label"] if c["heart_line"] else "Not observed — balanced reading given"
    return _feature_page("Feeling", "The Heart Line",
        "The heart line runs beneath the fingers and is read as your emotional style — how you love, trust, express and protect "
        "yourself in close relationships. It describes your manner of feeling, never your worthiness of love.",
        c["heart_profile"], label)

def fate_page(c):
    label = PC.FATE_LINE[c["fate_line"]]["label"] if c["fate_line"] else "Not observed — balanced reading given"
    return _feature_page("Direction", "The Fate Line",
        "The fate line rises up the centre of the palm toward the middle finger and is read as career spine and life direction — "
        "how strongly external structure organises your path. Many successful palms have faint or absent fate lines; the reading "
        "is about *how* direction forms for you, not whether you will succeed.",
        c["fate_profile"], label)

def mounts_page(c):
    items = [f"<b>{name}</b> ({where}): {meaning}." for name, where, meaning in PC.MOUNTS]
    return page("Elevations", "The Mounts of the Palm", [
        lead("The mounts are the fleshy elevations of the palm, each named for a planet and read as a reservoir of that planet's "
             "temperament. Mount firmness is a three-dimensional feature and cannot be judged confidently from photographs, so this "
             "chapter teaches you to read your own — press each area gently: firm and springy reads as active, flat as latent."),
        Spacer(1, 8),
        Panel([h3("The Seven Mounts")] + bullets(items), border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("How To Work With Them"), body(
            "A practical way to use the mounts is as a self-inventory: identify your one or two firmest mounts and ask whether your "
            "current work and relationships actually draw on those reservoirs. Where the data is limited, this interpretation should "
            "be read with caution — but the self-test above is reliable, repeatable and yours to keep.")]),
    ])

def synthesis(c):
    bits = []
    if c["shape_profile"]:
        bits.append(f"Your <b>{c['hand_shape']} hand</b> frame means {c['shape_profile']['meaning']}.")
    if c["head_line"]:
        bits.append(f"Within that frame, the head line suggests {c['head_profile']['meaning']}.")
    if c["heart_line"]:
        bits.append(f"Emotionally, the heart line indicates {c['heart_profile']['meaning']}.")
    if c["fate_line"]:
        bits.append(f"Direction-wise, the fate line points to {c['fate_profile']['meaning']}.")
    if c["life_line"]:
        bits.append(f"Underneath it all, the life line shows {c['life_profile']['meaning']}.")
    if not bits:
        bits.append("With no structured observations provided, the synthesis is methodological: read the shape chapter first, then the "
                    "four lines, and note which single caution repeated most — that repetition is your palm's main message.")
    return page("The Whole Hand", "Life Pattern Synthesis", [
        lead(f"{c['name']}, single features are notes; the reading is the chord. This chapter assembles your observed features into "
             f"one picture, read toward your stated focus: {c['focus_area']}."),
        Spacer(1, 8),
        Panel([h3("Your Pattern, Assembled")] + [body(b) for b in bits], border=GOLD_D),
        Spacer(1, 8),
        Panel([h3("Why This Matters"), body(
            "This matters because the palm's features moderate each other — a cautious heart line inside a fire hand behaves very "
            "differently from the same line in a water hand. The combined picture above is therefore more personal than any single "
            "chapter, and it is the picture to keep in mind when applying the action plan that follows.")]),
        Spacer(1, 8),
        Paragraph(PC.DISCLAIMERS["self_observation"], ST["mute"]),
    ])

def action_plan(c):
    acts = []
    for key in ("shape_profile", "head_profile", "heart_profile", "fate_profile", "life_profile"):
        pr = c[key]
        if pr and pr is not PC.UNKNOWN and pr.get("action"):
            acts.append(pr["action"])
    acts = acts[:4] or ["Re-photograph both palms in bright, indirect daylight and complete the guided observations for a sharpened re-read."]
    return page("Your Plan", "Practical Guidance & Action Plan", [
        lead("Everything in this reading, reduced to a plan you can actually follow."),
        Spacer(1, 8),
        Panel([h3("Next 7 Days")] + bullets([
            "Re-read the Data & Limitations page and, if any photo note flagged quality, retake that photo — a better image sharpens a future re-read.",
            "Do the mount self-test from the mounts chapter and note your two firmest mounts.",
        ]), border=GOLD_D),
        Spacer(1, 7),
        Panel([h3("Next 30 Days — One Habit Per Feature")] + bullets([a[0].upper() + a[1:] + "." for a in acts])),
        Spacer(1, 7),
        Panel([h3("Next 6 Months")] + bullets([
            f"Align one meaningful commitment in your focus area ({c['focus_area']}) with the temperament this reading described, rather than against it.",
            "Compare your two palms once in good light and note one difference — that is your development record.",
            "Revisit this report after any major life change; read it as a mirror, and let the mirror update.",
        ]), bg=HexColor("#F6ECEC")),
    ])

def closing(c):
    return page("Closing", "Final Guidance", [
        lead(f"{c['name']}, the palm records the road travelled and the traveller's habits — and habits can be chosen. Nothing in "
             "this reading fixes your future; every feature described is a tendency that conscious practice can direct."),
        Spacer(1, 8),
        Panel([h3("Final Message"), body(
            "The strongest signal in any palm is coherence: when work, relationships and daily habits draw on the hand's actual "
            "temperament instead of fighting it, everything costs less energy. Use the action plan, retake unclear photos for a "
            "sharper re-read, and treat this document as a working companion rather than a verdict.")], border=GOLD_D),
        Spacer(1, 8),
        Paragraph(PC.DISCLAIMERS["general"], ST["mute"]),
        Spacer(1, 4),
        Paragraph("This report was prepared confidentially for the named client. Photographs and personal details are never shared. "
                  "For clarifications, reply to your delivery email — a genuine question about your own report is always answered.", ST["mute"]),
    ])

def story(c):
    S = cover(c)
    S += how_to_read(c)
    S += data_limits(c)
    S += hands_compare(c)
    S += shape_page(c)
    S += life_page(c)
    S += head_page(c)
    S += heart_page(c)
    S += fate_page(c)
    S += mounts_page(c)
    S += synthesis(c)
    S += action_plan(c)
    S += closing(c)
    return S

def build_palmistry_report(profile, out_path, strict=False):
    S = story(profile)
    audit_story(S, report_name="premium_palmistry",
                required_disclaimers=[("tendency-not-fate note", "not fixed fate"),
                                      ("photo limitation note", "lighting-dependent")],
                strict=strict)
    doc = ReportDoc(out_path, footer_title="Premium Palmistry Report")
    doc.build(S)
    return out_path
