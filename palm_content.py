"""Veshann Astro — palmistry interpretation content library.

Authored, deterministic interpretation text keyed to the guided palm
self-observation inputs collected on the booking page (dominant hand, hand
shape, and the four major lines). Same editorial rules as astro_content.py:
calm, logic-based, practical, tendency-not-fate, no fear language.

Every profile is a dict with the same keys so the renderer can build a full
premium section from any answer:
  meaning  – what this feature classically indicates
  strength – the gift side of the pattern
  caution  – the over-use / shadow side
  action   – one practical way to work with it
"""
from __future__ import annotations

# ── hand shape (elemental typology) ─────────────────────────────────────────
HAND_SHAPE = {
    "earth": {
        "label": "Earth hand (square palm, shorter fingers)",
        "meaning": "a practical, grounded temperament that trusts what can be built, touched and finished. Decisions are made from experience rather than theory",
        "strength": "reliability, stamina, common sense and the ability to turn plans into finished work",
        "caution": "resistance to change and a tendency to dismiss what cannot be immediately used",
        "action": "schedule deliberate exposure to new methods and ideas once a month — novelty is this hand's vitamin, not its enemy",
    },
    "air": {
        "label": "Air hand (square palm, longer fingers)",
        "meaning": "an intellectual, communicative temperament that processes life through ideas, words and systems",
        "strength": "analysis, articulate expression, curiosity and fairness in judgement",
        "caution": "over-thinking, restlessness, and living in the head while the body and relationships wait",
        "action": "pair every important analysis with one concrete physical step the same day, so thought keeps converting into motion",
    },
    "fire": {
        "label": "Fire hand (longer palm, shorter fingers)",
        "meaning": "an energetic, initiating temperament that needs movement, goals and visible progress",
        "strength": "enthusiasm, courage, leadership in action and fast recovery from setbacks",
        "caution": "impatience, scattered starts, and boredom once the exciting phase of a project ends",
        "action": "finish one thing before starting the next — completion, not initiation, is where this hand's growth lives",
    },
    "water": {
        "label": "Water hand (longer palm, longer fingers)",
        "meaning": "a sensitive, intuitive temperament that reads moods and undercurrents others miss",
        "strength": "empathy, imagination, artistic perception and depth in one-to-one connection",
        "caution": "absorbing other people's emotional weather, and retreating instead of negotiating",
        "action": "protect a daily quiet recharge and practise saying one honest, uncomfortable sentence early instead of withdrawing",
    },
}

# ── life line ───────────────────────────────────────────────────────────────
LIFE_LINE = {
    "long_curved": {
        "label": "Long, clearly curved around the thumb ball",
        "meaning": "classically read as robust vitality and a wide 'engagement with life' — energy that supports long projects and full participation",
        "strength": "physical resilience, appetite for experience, and steady recovery capacity",
        "caution": "taking that stamina for granted — this pattern often under-rests precisely because it can",
        "action": "treat rest as scheduled maintenance rather than a reward; the line describes capacity, and capacity lasts longest when serviced",
    },
    "short_faint": {
        "label": "Shorter or fainter line",
        "meaning": "traditionally read not as a short life — that is a myth worth discarding — but as energy that runs in focused bursts and needs conscious recharging",
        "strength": "efficiency: this pattern often achieves in concentrated sprints what others do in long grinds",
        "caution": "over-committing to always-on schedules that suit other people's energy pattern, not yours",
        "action": "structure work in sprint-and-recover cycles, guard sleep, and treat food and routine as energy engineering",
    },
    "broken_chained": {
        "label": "Visible breaks, islands or chained sections",
        "meaning": "classically read as chapters — periods where life circumstances changed course or health and energy asked for attention. In practice it marks a life that renews itself in stages rather than one straight road",
        "strength": "adaptability and the lived proof of having restarted before",
        "caution": "reading every disruption as damage; in palm tradition a break is a bend in the road, not the end of it",
        "action": "during transition periods, double the basics — sleep, routine, trusted company — and let the new chapter form before judging it",
    },
    "double": {
        "label": "A parallel sister line beside the life line",
        "meaning": "traditionally called a guardian or Mars line — read as an extra reserve of vitality and protection, often felt as strong family support or an inner second wind",
        "strength": "unusual resilience under pressure; recovery that surprises people",
        "caution": "leaning on the reserve habitually instead of exceptionally",
        "action": "acknowledge the people and habits that form this backup, and invest in them deliberately — reserves last when they are refilled",
    },
}

# ── head line ───────────────────────────────────────────────────────────────
HEAD_LINE = {
    "straight_long": {
        "label": "Straight and long across the palm",
        "meaning": "a structured, logical thinking style — step-by-step, realistic, strong with facts, plans and systems",
        "strength": "clarity, consistency and dependable judgement under pressure",
        "caution": "dismissing intuition and imagination as noise; over-planning where a leap is required",
        "action": "when a decision stalls despite complete analysis, deliberately consult the gut once — then decide",
    },
    "sloping": {
        "label": "Sloping gently toward the wrist",
        "meaning": "an imaginative, creative thinking style — ideas arrive as pictures and possibilities before they arrive as steps",
        "strength": "originality, vision and the ability to see options others miss",
        "caution": "drift — beautiful plans that stay unbuilt, and moods colouring judgement",
        "action": "attach every idea you love to one dated, physical first step within 48 hours of having it",
    },
    "short": {
        "label": "Short, ending near the palm centre",
        "meaning": "a direct, decisive thinking style — quick assessment, quick action, little appetite for endless deliberation",
        "strength": "speed, practicality and freedom from over-analysis",
        "caution": "deciding before the full picture arrives, especially in matters with long consequences",
        "action": "for irreversible decisions only, impose a 24-hour pause; for everything else, your speed is an asset",
    },
    "forked": {
        "label": "Forked at the end (writer's fork)",
        "meaning": "a mind that naturally holds two perspectives — logic and imagination, head and heart — classically linked to communication and balanced judgement",
        "strength": "seeing both sides genuinely; explaining complex things simply",
        "caution": "internal debate that postpones commitment",
        "action": "give yourself a decision deadline whenever you notice both inner voices are fully heard — at that point more debate adds nothing",
    },
}

# ── heart line ──────────────────────────────────────────────────────────────
HEART_LINE = {
    "ends_index": {
        "label": "Ending under the index finger",
        "meaning": "an idealistic, devoted emotional style — love is taken seriously and given loyally, with high standards for how people treat each other",
        "strength": "constancy, principle and depth of commitment",
        "caution": "expectations doing silent damage: partners are measured against an ideal they were never told about",
        "action": "say the expectation out loud before scoring anyone against it — including yourself",
    },
    "ends_middle": {
        "label": "Ending under the middle finger",
        "meaning": "a self-contained, realistic emotional style — affection is real but expressed practically, and personal space matters",
        "strength": "emotional independence and low drama; love shown through acts rather than declarations",
        "caution": "partners may read the containment as distance; needs go unstated until they surface as frustration",
        "action": "translate care into words on a schedule the other person can feel — weekly, plainly, without occasion",
    },
    "deep_curved": {
        "label": "Deep and clearly curved upward",
        "meaning": "a warm, expressive emotional style — feelings are strong, visible and generously given",
        "strength": "openness, passion and the ability to make people feel genuinely valued",
        "caution": "emotional weather setting the agenda; generosity extended past the point of self-respect",
        "action": "in conflict, delay the big conversation until the first wave passes — this heart line argues best after an hour's walk",
    },
    "straight_faint": {
        "label": "Straight or fainter line",
        "meaning": "a cautious, observing emotional style — trust is extended in instalments and feelings are examined before they are declared",
        "strength": "steadiness, discretion and immunity to infatuation-driven mistakes",
        "caution": "waiting so long to open that the relationship account never funds itself",
        "action": "practise one small, voluntary disclosure per week with the people who matter; intimacy is built in increments this style can control",
    },
}

# ── fate line ───────────────────────────────────────────────────────────────
FATE_LINE = {
    "strong": {
        "label": "Strong and unbroken up the palm",
        "meaning": "classically read as a clear career spine — a life that organises itself around direction, duty and cumulative achievement",
        "strength": "focus, follow-through and a reputation that compounds",
        "caution": "identity fusing with occupation; drift into rigidity when circumstances demand a pivot",
        "action": "keep one serious interest that is not your work — it protects both judgement and identity",
    },
    "faint": {
        "label": "Faint or partial",
        "meaning": "read as a self-steered path — direction comes from choices, not circumstances, and the career story is written in chapters you author",
        "strength": "freedom, versatility and low dependence on any single employer or role",
        "caution": "the absence of external rails means drift is possible when no goal is actively chosen",
        "action": "set your own 12-month professional theme each year and review it quarterly — you are the structure this line expects",
    },
    "broken_shifting": {
        "label": "Broken or starting again in a new position",
        "meaning": "classically read as career redirection — a working life with more than one distinct chapter, often by conscious reinvention",
        "strength": "courage to change lanes and the compound skill-set that reinvention builds",
        "caution": "restlessness disguised as reinvention; leaving just before compounding pays",
        "action": "before each change, write what the last chapter earned you and what the next must — change with an invoice, not an impulse",
    },
    "absent": {
        "label": "Not clearly visible",
        "meaning": "common and entirely unalarming — read as a life not defined by a single occupation; meaning is drawn from several sources rather than one ladder",
        "strength": "flexibility and immunity to career-identity crises that trouble single-track lives",
        "caution": "under-investing in any one direction long enough to reach its rewards",
        "action": "choose one skill or venture as your 'main quest' for the next two years while the rest stay hobbies — sequencing, not sacrifice",
    },
}

# ── mounts overview (general, honest about self-assessment limits) ─────────
MOUNTS = [
    ("Mount of Jupiter", "below the index finger", "ambition, leadership and self-respect; prominent development is read as natural authority, flatness as authority that must be consciously claimed"),
    ("Mount of Saturn", "below the middle finger", "discipline, seriousness and duty; prominence favours structure and research, flatness favours lightness and dislikes heavy routine"),
    ("Mount of Apollo (Sun)", "below the ring finger", "creativity, recognition and warmth; prominence seeks expression and appreciation, flatness prefers substance over spotlight"),
    ("Mount of Mercury", "below the little finger", "communication and commerce; prominence supports persuasion, trade and wit"),
    ("Mount of Venus", "the ball of the thumb", "vitality, affection and appetite for life; a full, firm Venus mount is classically the palm's battery"),
    ("Mount of Luna (Moon)", "opposite Venus, near the wrist edge", "imagination, intuition and travel; prominence deepens inner life and creative instinct"),
    ("Plains of Mars", "the central palm and its edges", "courage and resistance — how you fight, endure and recover"),
]

DOMINANT_HAND_NOTE = (
    "In palmistry the dominant hand (the one you write with) is read as the life you are actively building — choices, work, "
    "developed character. The non-dominant hand is read as inheritance and potential — temperament, early conditioning, latent gifts. "
    "Differences between the two hands are therefore the most interesting finding in any reading: they show where you have grown "
    "beyond your starting settings, and where unclaimed potential still waits."
)

DISCLAIMERS = {
    "photo": ("Palm photographs are two-dimensional and lighting-dependent; fine features such as minor lines, islands and mount firmness "
              "cannot be judged from an image with full confidence. Where photo quality limits certainty, this report says so and keeps "
              "the interpretation proportionate. Your photos are stored confidentially with your order and are reviewed by Veshannastro."),
    "self_observation": ("Line readings below are based on the guided observations you selected while looking at your own palm, supported by "
                         "your uploaded photographs. Where an observation was not provided, the report presents the balanced range of "
                         "meanings rather than guessing a specific one."),
    "general": ("Palmistry describes tendencies of temperament and pattern, not fixed fate. Lines change subtly over years — the palm "
                "records the road travelled and the traveller's habits, and habits can be chosen. Nothing in this report is a guarantee "
                "or a medical, legal or financial assessment; health concerns belong with qualified medical professionals."),
}

UNKNOWN = {
    "meaning": "this feature was not clearly identifiable from the provided inputs, so the balanced range of classical meanings is given instead of a specific verdict",
    "strength": "reading the general pattern of this line in your own palm using the guide on this page",
    "caution": "drawing firm conclusions from an unclear feature — palmistry rewards honest uncertainty over confident guessing",
    "action": "re-photograph the palm in bright, indirect daylight with fingers gently spread, and request a re-read; the interpretation can then be sharpened",
}


def line_reading(table: dict, key: str) -> dict:
    """Return the profile for an observed option, or the honest UNKNOWN profile."""
    return table.get((key or "").strip().lower(), UNKNOWN)
