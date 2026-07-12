"""Veshann Astro — interpretation content library for premium astrology reports.

Deterministic, human-authored interpretation text keyed to calculated chart
factors (Lagna sign, Moon sign, nakshatra, dasha lord, planet placements).
No text here claims certainty: everything is written as tendency + timing,
in the Veshannastro voice — calm, logic-based, practical, never fear-based.
"""
from __future__ import annotations

HOUSE_THEMES = {
    1: "identity, body, confidence and personal direction",
    2: "family, speech, savings and accumulated resources",
    3: "effort, courage, communication and self-built skills",
    4: "home, mother, inner peace and emotional security",
    5: "education, creativity, children and intelligent risk",
    6: "workload, service, health routines and competition",
    7: "marriage, partnership, clients and public dealings",
    8: "transformation, shared assets, research and hidden matters",
    9: "fortune, dharma, mentors and long-range vision",
    10: "career, status, authority and visible karma",
    11: "income, networks, gains and fulfilment of goals",
    12: "foreign connections, expenses, rest and inner release",
}

# ── Lagna (ascendant) profiles ──────────────────────────────────────────────
LAGNA = {
    "Aries": {
        "essence": "a direct, initiating temperament that prefers to act first and refine later. Life keeps handing you situations where courage, speed and self-reliance are the entry ticket",
        "strength": "decisiveness, physical energy and the ability to restart after setbacks without carrying old weight",
        "risk": "impatience — commitments made in heat, and a tendency to treat waiting as losing",
        "direction": "roles and life structures where you lead from the front and see quick, visible results of your own effort",
    },
    "Taurus": {
        "essence": "a steady, build-and-hold temperament. You grow through accumulation — of skills, savings, relationships and reputation — rather than through sudden pivots",
        "strength": "reliability, patience with long projects, and a natural sense for value and comfort",
        "risk": "over-attachment to the familiar; opportunities can pass while you are still weighing the cost of change",
        "direction": "life structures with tangible assets and long compounding — property, finance, craft, food, design, anything that rewards consistency",
    },
    "Gemini": {
        "essence": "a quick, connective temperament that processes life through words, information and variety. You are at your best when two or more interests run in parallel",
        "strength": "adaptability, communication, negotiation and the ability to learn faster than most people around you",
        "risk": "scattering — starting more than you finish, and letting restlessness be mistaken for progress",
        "direction": "work and relationships that reward exchange of ideas: writing, trade, teaching, media, analysis, anything with movement in it",
    },
    "Cancer": {
        "essence": "a protective, feeling-first temperament. Decisions pass through the heart before the head, and belonging matters more to you than winning",
        "strength": "emotional intelligence, memory, loyalty and the ability to build environments where people feel safe",
        "risk": "mood-led decision making and holding hurt privately until it hardens",
        "direction": "roles where care, continuity and trust are the product — teams, family enterprises, hospitality, healing, management of people",
    },
    "Leo": {
        "essence": "a dignified, centre-stage temperament. You need your work and your relationships to carry meaning and recognition, not just function",
        "strength": "natural authority, generosity, and the ability to hold responsibility visibly without collapsing under it",
        "risk": "pride — difficulty accepting correction, and over-investing in image during low phases",
        "direction": "leadership, creative direction, teaching, and any arena where your name stands behind the work",
    },
    "Virgo": {
        "essence": "a precise, improvement-driven temperament. You instinctively see what is broken and how to fix it, in systems and in people",
        "strength": "analysis, discipline, service-mindedness and quality control others cannot match",
        "risk": "over-criticism — of yourself first — and losing the larger opportunity while perfecting a detail",
        "direction": "professions built on accuracy and refinement: analysis, health, writing, operations, finance, research",
    },
    "Libra": {
        "essence": "a balancing, relationship-centred temperament. You read situations through fairness and partnership, and life repeatedly places you in the negotiator's seat",
        "strength": "diplomacy, aesthetic judgement, and the ability to make opposing sides feel heard",
        "risk": "decision-delay — weighing both sides so long that others decide for you",
        "direction": "partnership-driven work: law, business dealing, counselling, design, client-facing leadership",
    },
    "Scorpio": {
        "essence": "an intense, depth-seeking temperament. You do not do anything halfway — trust, work, or endings — and life transforms you in chapters rather than gradual slopes",
        "strength": "resilience, penetration into hidden causes, and loyalty that survives storms",
        "risk": "holding control too tightly, and letting suspicion or old wounds steer present decisions",
        "direction": "research, crisis management, healing, finance, psychology — anywhere depth and nerve are assets",
    },
    "Sagittarius": {
        "essence": "an expansive, principle-driven temperament. You need a horizon — a philosophy, a goal, a journey — and you lose energy when life becomes purely administrative",
        "strength": "optimism, honesty, teaching ability, and luck that follows genuine conviction",
        "risk": "over-promising and restlessness with detail; freedom can be defended even when structure would serve better",
        "direction": "teaching, guidance, law, publishing, travel-linked or vision-linked work where meaning and growth stay visible",
    },
    "Capricorn": {
        "essence": "a structured, long-game temperament. You measure life in responsibilities carried and mountains climbed slowly, and your best decade is usually ahead of you, not behind",
        "strength": "endurance, realism, organisational skill and the ability to keep working when motivation fades",
        "risk": "over-seriousness — postponing joy and connection until 'after the next milestone'",
        "direction": "institutions, management, enterprise-building and any field where authority is earned through track record",
    },
    "Aquarius": {
        "essence": "an independent, systems-minded temperament. You think in networks and future patterns, and you often feel one step outside the group you serve",
        "strength": "originality, fairness at scale, and comfort with ideas others find too new",
        "risk": "detachment — intellectualising feelings, and resisting structure even when it would multiply your impact",
        "direction": "technology, community-scale work, research, reform — roles where an unconventional angle is the value",
    },
    "Pisces": {
        "essence": "an intuitive, boundary-soft temperament. You absorb the emotional weather around you and are guided as much by imagination and faith as by plans",
        "strength": "compassion, creativity, adaptability and a genuine spiritual undercurrent to practical life",
        "risk": "escapism and unclear boundaries — saying yes from empathy and paying for it later",
        "direction": "creative, healing, spiritual or service-oriented work where sensitivity is the skill, protected by firm practical routines",
    },
}

# ── Moon sign emotional profiles ────────────────────────────────────────────
MOON = {
    "Aries": {"pattern": "emotions arrive fast and burn clean — quick to anger, quick to forgive, allergic to being controlled",
              "need": "autonomy and honest, immediate conversation", "care": "build a pause between feeling and reaction; most regretted decisions in this chart pattern happen inside the first ten minutes of a strong emotion"},
    "Taurus": {"pattern": "emotions are steady and slow to shift — comfort, routine and loyalty regulate the mind",
               "need": "stability and tangible reassurance", "care": "watch for emotional stubbornness: refusing to revisit a feeling once it has settled, even when circumstances change"},
    "Gemini": {"pattern": "feelings are processed by talking and thinking them through; the mind is restless and dislikes emotional silence",
               "need": "conversation, variety and mental engagement", "care": "name the feeling underneath the words — this Moon can describe emotions endlessly without actually sitting with them"},
    "Cancer": {"pattern": "deep, tidal emotional life with strong memory — kindness is never forgotten, and neither is hurt",
               "need": "belonging, home and being needed", "care": "practise releasing old emotional accounts; the mind heals fastest here when the past is consciously closed, not just avoided"},
    "Leo": {"pattern": "warm, generous and dignity-sensitive — respect regulates this Moon more than affection does",
            "need": "appreciation and a sense of being central to the people you love", "care": "separate genuine disrespect from unpolished delivery; not every blunt word is an attack on your position"},
    "Virgo": {"pattern": "emotions are filtered through analysis — worry is this Moon's default way of caring",
              "need": "order, usefulness and problems it is allowed to solve", "care": "schedule worry instead of letting it run all day; and let some things stay imperfect without treating that as failure"},
    "Libra": {"pattern": "the mind seeks harmony and mirrors the emotional tone of the room; conflict is physically tiring",
              "need": "peace, partnership and aesthetic calm", "care": "practise saying the uncomfortable true sentence early — postponed conflict costs this Moon far more than expressed conflict"},
    "Scorpio": {"pattern": "intense, private and all-or-nothing — feelings run deep and are shown selectively",
                "need": "loyalty it can trust completely", "care": "let people earn trust in stages; testing everyone against a single past betrayal keeps the wound in charge"},
    "Sagittarius": {"pattern": "buoyant and meaning-seeking — the mind recovers through perspective, humour and movement",
                    "need": "freedom and a sense that life is going somewhere", "care": "stay with heavy feelings long enough to learn from them; optimism used too early becomes avoidance"},
    "Capricorn": {"pattern": "contained and duty-first — emotions are managed like responsibilities and rarely displayed raw",
                  "need": "respect, competence and being relied upon", "care": "tell the people close to you what you feel in words; they cannot read devotion that only appears as work"},
    "Aquarius": {"pattern": "cool-surfaced and observant — feelings are understood from a slight distance before they are allowed in",
                 "need": "mental freedom and friendship inside love", "care": "detachment is a skill, not a home; deliberately practise warmth in small daily doses"},
    "Pisces": {"pattern": "porous and compassionate — this Moon absorbs other people's moods and dreams vividly",
               "need": "quiet, creative or spiritual recharge time", "care": "guard your inputs: the company you keep becomes your inner weather faster than for almost any other Moon sign"},
}

# ── Nakshatra themes (Moon nakshatra) ───────────────────────────────────────
NAKSHATRA = {
    "Ashwini": ("the healer-pioneer: fast starts, quick recovery and an instinct to rescue", "act fast, but let one trusted person review irreversible decisions"),
    "Bharani": ("the bearer: carrying responsibility, transformation and creative life-force others avoid", "choose consciously what you carry — not everything heavy is yours"),
    "Krittika": ("the purifier: sharp discrimination, high standards and the courage to cut what is false", "aim the blade at problems, not at people or at yourself"),
    "Rohini": ("the grower: magnetism, beauty and the steady cultivation of material and emotional richness", "protect long timelines; your gifts compound and should not be rushed"),
    "Mrigashira": ("the seeker: perpetual curiosity and the search for the finer version of everything", "define 'enough' in advance, or the search itself becomes the address"),
    "Ardra": ("the storm: intensity, upheaval and the intelligence that is forged inside difficulty", "treat crises as renovations — this nakshatra rebuilds better than it preserves"),
    "Punarvasu": ("the return: renewal, second chances and the ability to restore what was lost", "trust cycles; what leaves your life in this pattern often returns improved"),
    "Pushya": ("the nourisher: dependable care, discipline and quiet spiritual authority", "accept the mentor role early; this chart matures into it anyway"),
    "Ashlesha": ("the serpent: perception, strategy and deep insight into human motives", "use insight to protect and heal, never to entangle — the same skill runs both ways"),
    "Magha": ("the throne: lineage, dignity and responsibility to something larger than yourself", "honour your roots while building your own name; both are required here"),
    "Purva Phalguni": ("the enjoyer: charm, creativity and the arts of rest and celebration", "build wealth and love with structure so the enjoyment has a floor under it"),
    "Uttara Phalguni": ("the ally: generosity, contracts and prosperity through committed partnership", "choose partners as carefully as goals; agreements shape this life path"),
    "Hasta": ("the craftsman: skill in the hands, wit and practical resourcefulness", "master one craft deeply; scattered cleverness is this pattern's only real enemy"),
    "Chitra": ("the architect: design intelligence and the drive to build something visibly excellent", "let the work be seen — hidden excellence frustrates this nakshatra"),
    "Swati": ("the independent wind: self-made movement, trade and balance found in motion", "roots are grown, not found; commit to one base and let everything else move"),
    "Vishakha": ("the focused victor: single-pointed ambition that intensifies near the goal", "celebrate milestones deliberately; otherwise no achievement ever feels finished"),
    "Anuradha": ("the devoted friend: loyalty, organisation and success in foreign or unfamiliar ground", "your gift is making unfamiliar places home — use it rather than fearing it"),
    "Jyeshtha": ("the elder: protective authority, sharp intellect and early responsibility", "lead without needing credit every time; quiet seniority is your natural rank"),
    "Mula": ("the root-cutter: research, radical honesty and the pull to reach the base of things", "when you dismantle something, plan the rebuild first — including in relationships"),
    "Purva Ashadha": ("the invincible declarer: conviction, persuasion and early victories", "pick battles that deserve your certainty; conviction spent everywhere wins nowhere"),
    "Uttara Ashadha": ("the lasting victor: slow, unstoppable achievement with ethical weight", "your wins are permanent when they are patient; avoid shortcuts that borrow from later"),
    "Shravana": ("the listener: learning, reputation and wisdom gathered through attention", "guard what you listen to and who you learn from — inputs write this life"),
    "Dhanishta": ("the drummer: rhythm, wealth-timing and group leadership", "sync ambition with timing — the same effort lands differently in different seasons"),
    "Shatabhisha": ("the healer of a hundred: research, secrecy and unconventional cures", "solitude is medicine here, isolation is not; keep the dosage deliberate"),
    "Purva Bhadrapada": ("the intense idealist: penetrating vision and transformation through conviction", "keep ideals connected to daily conduct, or intensity turns inward"),
    "Uttara Bhadrapada": ("the deep stabiliser: wisdom, restraint and support given quietly to many", "your calm is a public utility — but schedule genuine rest to maintain it"),
    "Revati": ("the safe harbour: compassion, completion and protection of travellers and endings", "learn to close chapters kindly — for others and for yourself; that is this chart's mastery"),
}

# ── Planet significations ───────────────────────────────────────────────────
PLANET_DOMAIN = {
    "Sun": "confidence, authority, father, vitality and self-respect",
    "Moon": "mind, emotional stability, mother and public connection",
    "Mars": "energy, courage, conflict-handling and physical drive",
    "Mercury": "intellect, speech, commerce and analytical skill",
    "Jupiter": "wisdom, growth, finances, teachers and grace",
    "Venus": "love, marriage, comfort, art and social ease",
    "Saturn": "discipline, delay, endurance and long-term karma",
    "Rahu": "ambition, obsession, unconventional growth and worldly hunger",
    "Ketu": "detachment, intuition, past mastery and spiritual pull",
}

DIGNITY_READ = {
    "Exalted": "operating near its best expression — its gifts come with unusual ease and should be built upon deliberately",
    "Own sign": "comfortable and self-supporting — a dependable strength you can lean on under pressure",
    "Debilitated": "working uphill — its themes need conscious effort, good habits and often a mentor's guidance before they mature. In practice this often becomes a late-blooming strength once handled honestly",
    "Neutral": "in workable condition — results depend more on timing (dasha) and your handling than on raw placement strength",
}

# ── Dasha lord period themes ────────────────────────────────────────────────
DASHA = {
    "Sun": {"supports": "visibility, promotion, government or authority matters, clarity about your own direction, and repair of confidence",
            "tests": "ego friction with seniors or father-figures, and the temptation to win arguments instead of outcomes",
            "use": "step into responsibility formally — titles, ownership, public accountability. Keep humility as policy, not mood"},
    "Moon": {"supports": "emotional connection, public-facing work, home matters, and decisions guided by settled intuition",
             "tests": "mood swings steering choices, and over-dependence on approval from family or the public",
             "use": "stabilise daily rhythm first — sleep, food, people. A regulated mind makes this period genuinely fortunate"},
    "Mars": {"supports": "bold execution, property and technical matters, physical fitness, and clearing backlogs through direct action",
             "tests": "haste, conflict escalation, and injuries or disputes born from impatience",
             "use": "channel the heat into scheduled effort — training, deadlines, competition. Decide in calm, execute with fire, never the reverse"},
    "Mercury": {"supports": "business, negotiation, writing, learning new skills, and income through intellect and networks",
                "tests": "over-thinking, scattered commitments, and clever shortcuts that cost trust",
                "use": "document everything, learn deliberately, and let your words be slightly more careful than the situation demands"},
    "Jupiter": {"supports": "expansion, teachers and mentors, finances, family growth, and ethical advancement that compounds",
                "tests": "over-optimism, over-commitment, and neglecting details because the direction feels blessed",
                "use": "say yes to growth but keep one disciplined reviewer — a person or a process — attached to every big decision"},
    "Venus": {"supports": "relationships, marriage matters, comfort, creative work, and income through people-facing value",
              "tests": "indulgence, comparison, and letting relationship harmony depend on unspoken expectations",
              "use": "invest in relationships with structure — honest conversations, shared plans — and enjoy comfort without letting it set the budget"},
    "Saturn": {"supports": "consolidation, mastery through repetition, long-term assets, and respect earned by reliability",
               "tests": "delay, workload, loneliness of responsibility, and pessimism if progress is measured weekly instead of yearly",
               "use": "shrink the promise, extend the timeline, keep showing up. Saturn periods pay in arrears — everything endured correctly returns with interest"},
    "Rahu": {"supports": "unconventional opportunities, foreign or technological gains, sudden elevation, and breaking out of old ceilings",
             "tests": "obsession, shortcuts, image-chasing and decisions made from hunger rather than judgement",
             "use": "ride the ambition but audit it monthly: is this desire mine, or borrowed? Keep one grounded advisor who is allowed to say no"},
    "Ketu": {"supports": "spiritual depth, research, release of what has finished its role, and mastery in narrow technical domains",
             "tests": "disinterest in worldly maintenance, sudden exits, and a sense of meaninglessness if life is measured only materially",
             "use": "simplify voluntarily before the period simplifies for you; invest in inner work and specialised skill rather than expansion"},
}

# ── Composers ───────────────────────────────────────────────────────────────
def planet_in_house(planet: str, house: int, dignity: str = "Neutral", retro: bool = False) -> str:
    """One rich sentence-set translating a placement into user language."""
    txt = (f"{planet} carries {PLANET_DOMAIN.get(planet, 'its significations')}, and from the "
           f"{_ord(house)} house it expresses these through {HOUSE_THEMES[house]}. "
           f"In this chart it is {DIGNITY_READ.get(dignity, DIGNITY_READ['Neutral'])}.")
    if retro:
        txt += (f" It is also retrograde, which in practice means {planet}'s themes are revisited, "
                "internalised and often mastered later but more deeply than average.")
    return txt


def _ord(n: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")


def lagna_reading(sign: str) -> dict:
    return LAGNA.get(sign, {"essence": "a distinct temperament pattern", "strength": "notable natural strengths",
                            "risk": "a specific over-use of those strengths", "direction": "work aligned with the ascendant's nature"})


def moon_reading(sign: str) -> dict:
    return MOON.get(sign, {"pattern": "a distinct emotional rhythm", "need": "specific emotional conditions", "care": "conscious emotional habits"})


def nakshatra_reading(name: str):
    return NAKSHATRA.get(name, ("a distinct karmic theme", "work with this theme consciously"))


def dasha_reading(lord: str) -> dict:
    return DASHA.get(lord, {"supports": "specific growth themes", "tests": "specific pressure themes", "use": "align effort with the period's nature"})


# ── Dosha / karmic-pattern detection (calculated, carefully worded) ─────────
def detect_doshas(chart: dict) -> list[dict]:
    """Detect classical patterns from calculated positions. Each entry:
    name, present(bool), basis, meaning, balance. Wording is deliberately
    non-fearful: every dosha is framed as a pattern with a working method."""
    out = []
    planets = chart["planets"]
    mars_h = planets["Mars"]["house"]
    mangal = mars_h in {1, 2, 4, 7, 8, 12}
    out.append({
        "name": "Mangal (Kuja) consideration",
        "present": mangal,
        "basis": f"Mars occupies house {mars_h} from Lagna" + (" — a classical Mangal-dosha house" if mangal else " — not a Mangal-dosha house from Lagna"),
        "meaning": ("Mars in this position tends to bring extra heat into close partnership: strong opinions, quick reactions and a need for respect inside marriage. "
                    "It is a temperament pattern, not a verdict on marital destiny — classical texts themselves list many cancellations, and lived maturity is the biggest one.")
                   if mangal else
                   ("Mars does not sit in a classical dosha house from the Lagna here, so no Mangal-based caution is applied. Partnership friction, where it appears, should be read from the 7th house and Venus instead."),
        "balance": ("Practical balancing: build a deliberate pause before reacting in close relationships, use physical activity as a pressure valve, "
                    "and match with a partner who respects directness. Ritual remedies may be used as supportive discipline if they are part of your practice.")
                   if mangal else "No balancing measure is needed for this pattern.",
    })
    # Kaal Sarp: all seven classical planets on one side of the Rahu-Ketu axis
    rahu = planets["Rahu"]["longitude"]; ketu = planets["Ketu"]["longitude"]
    def _between(x, a, b):
        return (x - a) % 360 < (b - a) % 360
    side1 = all(_between(planets[p]["longitude"], rahu, ketu) for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"])
    side2 = all(_between(planets[p]["longitude"], ketu, rahu) for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"])
    kaal = side1 or side2
    out.append({
        "name": "Kaal Sarp pattern",
        "present": kaal,
        "basis": ("All seven classical planets fall on one side of the Rahu–Ketu axis" if kaal
                  else "Planets are distributed on both sides of the Rahu–Ketu axis"),
        "meaning": ("This pattern tends to make life feel phase-locked: long stretches where effort seems to queue up, followed by concentrated periods where results arrive together. "
                    "It rewards persistence and punishes shortcuts — but it does not block success; many accomplished charts carry it.")
                   if kaal else
                   "No Kaal Sarp pattern is formed, so no such phase-locking is read into this chart.",
        "balance": ("Practical balancing: plan in longer cycles, bank progress during high-momentum windows, and treat slow phases as build phases rather than verdicts. "
                    "Rahu/Ketu-related observances may be kept as supportive discipline if they suit your practice.")
                   if kaal else "No balancing measure is needed for this pattern.",
    })
    # Sade Sati: Saturn transit in 12th, 1st or 2nd from natal Moon
    sat_from_moon = chart["transits"]["Saturn"]["from_moon"]
    sade = sat_from_moon in {12, 1, 2}
    out.append({
        "name": "Sade Sati status (current)",
        "present": sade,
        "basis": f"Transit Saturn is currently {_ord(sat_from_moon)} from the natal Moon",
        "meaning": ("Saturn's slow passage around the natal Moon is active, which classically marks a maturing period: responsibilities feel heavier, outcomes feel slower, and the mind is asked to grow up in some specific area. "
                    "Handled with routine and honesty, this period reliably builds the strongest decade that follows it. This should be treated as a timing indicator, not a fixed sentence.")
                   if sade else
                   ("Saturn is not currently transiting the Sade Sati zone around your natal Moon, so that particular weight is not part of the present period."),
        "balance": ("Practical balancing: protect sleep and routine, reduce debt-driven risk, serve elders or those under pressure, and measure progress yearly rather than weekly.")
                   if sade else "No balancing measure is needed at present.",
    })
    return out


# ── Standard disclaimers ────────────────────────────────────────────────────
DISCLAIMERS = {
    "health": ("Health notes in this report describe astrological tendencies only. They are not a medical diagnosis and must not delay or replace "
               "consultation with qualified medical professionals for any health concern."),
    "finance": ("Financial observations describe timing and temperament patterns. They are not investment advice; significant financial decisions "
                "should be checked with qualified financial professionals."),
    "relationship": ("Relationship analysis offers reflective guidance and timing context. Decisions about a marriage or separation are yours alone; "
                     "where legal rights, mental health or personal safety are involved, please involve qualified professionals without delay."),
    "general": ("Vedic astrology describes tendencies and timing, not fixed fate. Every indication in this report should be read as a probability "
                "pattern to work with, never as a guarantee of outcome."),
    "limited_time": ("Birth time was not provided or could not be confirmed, so a 12:00 noon chart has been used. The Moon sign, nakshatra and dasha "
                     "sequence are broadly reliable at this precision, but the Lagna (ascendant), house placements and any Lagna-dependent conclusion "
                     "should be read with caution. Where the data is limited, this interpretation is deliberately kept more general."),
    "limited_place": ("The exact birth place could not be resolved, so a central reference location was used for calculation. Planetary signs, "
                      "nakshatra and dasha timing remain broadly reliable, but the exact Lagna degree and house cusps should be read with caution. "
                      "Where the data is limited, this interpretation is deliberately kept more general."),
}
