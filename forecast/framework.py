"""The Veshannastro 12-parameter framework: the calculations and the reading tables for the parameters added on
31 October 2026 (elements, Vedic sun sign, pinnacles, 10-year life graph).

Everything a customer reads on those pages comes from the tables in this file, so a meaning can be changed here
without touching the page code (deck_more.py). Owner's rules:

- Elements: Earth 2, 5, 8 · Fire 1, 9 · Wood 3, 4 · Metal 6, 7 · Water 2. The 2 counts for both Earth and Water.
  Counted on the Lo Shu grid, destiny number included.
- Zodiac: the Vedic (sidereal, Lahiri) sun sign, worked out from the exact birth date with the Swiss Ephemeris.
- Pinnacles: month + day, day + year, first + second, month + year (month, day and year reduced to 1-9 first);
  11 and 22 are kept as master pinnacles. The first ends at 36 minus the destiny number; the next two last 9 years.
- 10-year life graph: (day and month as one number) x (birth year). Each digit k of the result is a point at age
  10k + digit with that digit as its level, repeating after the last digit; the life-need line is the digits' total
  divided by their count. The window runs from the age on 1 January of the forecast year, ten years forward (born
  2003, read for 2027: ages 23 to 33), and every age is labelled with the year whose 1 January finds you at that age,
  so the chart, the table and the text agree.
"""
from datetime import date

PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}


def root(n):
    n = abs(int(n))
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


# ═══════════════════════════════ 3. Elements ═══════════════════════════════
ELEMENT_ORDER = ["Earth", "Fire", "Wood", "Metal", "Water"]
ELEMENT_NUMBERS = {"Earth": (2, 5, 8), "Fire": (1, 9), "Wood": (3, 4), "Metal": (6, 7), "Water": (2,)}

ELEMENTS = {
    "Earth": dict(
        gives="stability, patience and trust: the ability to hold on to what you build, from money to a home to a commitment",
        strong="You are steady and dependable, and people lean on you. Too much Earth can make you slow to change and stubborn when plans need to move.",
        weak="Plans keep shifting, money comes and goes, and it can be hard to stay with one thing long enough for it to pay.",
        colour="yellow and earthy brown",
        remedies=["Walk barefoot on grass or soil for ten minutes in the morning.",
                  "Keep a clay pot or a natural crystal on your desk or in the centre of your home.",
                  "Eat your meals at fixed times: routine is how Earth is built."]),
    "Fire": dict(
        gives="energy, courage and recognition: the drive to start, to be seen and to lead",
        strong="You have drive, confidence and warmth, and people notice you. Too much Fire burns out: impatience, anger and rushing.",
        weak="Motivation runs low, you wait to be noticed, and good ideas stay unstarted.",
        colour="red, orange and gold",
        remedies=["Offer water to the rising Sun, or sit in the morning sunlight for ten minutes.",
                  "Light a diya or a candle at home in the evening.",
                  "Wear a touch of red or orange on days you need to be heard."]),
    "Wood": dict(
        gives="growth, planning and flexibility: the ability to learn, to expand and to see a few steps ahead",
        strong="You grow, plan and keep learning, and you bend without breaking. Too much Wood spreads you thin across too many plans.",
        weak="It is hard to plan ahead or to keep growing; you stall when things need patience and a long view.",
        colour="green",
        remedies=["Keep healthy green plants at home, a money plant or tulsi in the east.",
                  "Wear a wooden or Rudraksha bead.",
                  "Spend time with trees: a walk in a park counts."]),
    "Metal": dict(
        gives="structure, discipline and clarity: the ability to decide, to cut out what is not needed and to finish",
        strong="You are organised, clear and decisive, and you finish what you start. Too much Metal turns rigid and critical.",
        weak="Decisions drag, clutter builds up, and things are started but not finished.",
        colour="white, silver and gold",
        remedies=["Keep a brass or copper item where you work.",
                  "Clear one drawer or one shelf every week.",
                  "Wear white or a little silver on days you must decide."]),
    "Water": dict(
        gives="emotion, intuition and flow: the ability to feel, to adapt and to let things move",
        strong="You are intuitive, adaptable and emotionally aware. Too much Water makes you moody and easily swayed by other people's feelings.",
        weak="Feelings stay bottled up, you second-guess your instinct, and life can feel dry and rigid.",
        colour="white, silver and light blue",
        remedies=["Drink your first glass of water each morning from a silver or copper vessel.",
                  "Keep a small bowl of clean water or a fountain in the north of your home.",
                  "Spend quiet time near water once a week."]),
}


def element_level(count):
    if count == 0:
        return "missing"
    if count == 1:
        return "light"
    if count <= 3:
        return "balanced"
    return "strong"


LEVEL_WORD = {"missing": "Missing", "light": "Light", "balanced": "Balanced", "strong": "Strong"}


def elements_of(counts):
    """counts: Lo Shu grid counts by digit (destiny included). Returns the five elements in order, each with its
    count, level and the digits that fed it."""
    out = []
    for name in ELEMENT_ORDER:
        nums = ELEMENT_NUMBERS[name]
        c = sum(int(counts.get(n, 0)) for n in nums)
        out.append(dict(name=name, numbers=nums, count=c, level=element_level(c),
                        present=[n for n in nums if counts.get(n)], **ELEMENTS[name]))
    return out


# ═══════════════════════════════ 4. Vedic sun sign ═══════════════════════════════
SIGNS = [
    dict(en="Aries", sa="Mesha", lord=9, dignity="exalted",
         nature="Direct, brave and quick to start. You lead from the front and feel most alive when there is something to win.",
         strength="Initiative: you go first when others wait.", watch="Impatience, and fighting battles that are not yours."),
    dict(en="Taurus", sa="Vrishabha", lord=6, dignity="",
         nature="Steady, loyal and sensual. You build slowly and you keep what you build: money, comfort and people.",
         strength="Staying power and a sure sense of value.", watch="Stubbornness, and comfort that turns into resistance to change."),
    dict(en="Gemini", sa="Mithuna", lord=5, dignity="",
         nature="Curious, quick and talkative. You think by connecting people and ideas, and you learn faster than most.",
         strength="Communication and adaptability.", watch="Scattered attention and too many open threads."),
    dict(en="Cancer", sa="Karka", lord=2, dignity="",
         nature="Caring, protective and attached to home and family. You remember how things felt, and you look after your people.",
         strength="Emotional intelligence.", watch="Moods that follow other people's moods, and holding on too long."),
    dict(en="Leo", sa="Simha", lord=1, dignity="own",
         nature="Warm, proud and generous. You want to be respected, and you rise to responsibility.",
         strength="Leadership and the confidence to be visible.", watch="Ego when you are not acknowledged."),
    dict(en="Virgo", sa="Kanya", lord=5, dignity="",
         nature="Precise, practical and helpful. You notice what others miss and you improve whatever you touch.",
         strength="Analysis and craft.", watch="Overthinking, worry and self-criticism."),
    dict(en="Libra", sa="Tula", lord=6, dignity="debilitated",
         nature="Fair, charming and relationship-minded. You look for balance, and you are good at bringing people together.",
         strength="Diplomacy and taste.", watch="Indecision, and keeping the peace at your own cost."),
    dict(en="Scorpio", sa="Vrishchika", lord=9, dignity="",
         nature="Intense, private and determined. You go deep, you keep confidences, and you do not give up easily.",
         strength="Focus and resilience in a crisis.", watch="Suspicion and holding grudges."),
    dict(en="Sagittarius", sa="Dhanu", lord=3, dignity="",
         nature="Optimistic, principled and freedom-loving. You look for meaning, and you teach without trying.",
         strength="Faith, ethics and the big picture.", watch="Over-promising and restlessness."),
    dict(en="Capricorn", sa="Makara", lord=8, dignity="",
         nature="Disciplined, patient and ambitious. You take responsibility early, and your success tends to come later and last.",
         strength="Endurance and structure.", watch="Being too hard on yourself: all work and no rest."),
    dict(en="Aquarius", sa="Kumbha", lord=8, dignity="",
         nature="Independent, original and community-minded. You think differently, and you care about the larger group.",
         strength="Vision and fairness.", watch="A detachment that others read as distance."),
    dict(en="Pisces", sa="Meena", lord=3, dignity="",
         nature="Gentle, intuitive and imaginative. You feel your way to answers, and you are generous with help.",
         strength="Compassion and intuition.", watch="Avoiding hard decisions, and blurred boundaries."),
]
DIGNITY_LINE = {
    "exalted": "The Sun is exalted in Mesha: this is where it is strongest, so self-belief and authority come naturally.",
    "own": "Simha is the Sun's own sign: you are most yourself when you lead and are seen.",
    "debilitated": "The Sun is debilitated in Tula: confidence grows through partnership rather than on its own, and it grows with every year you trust yourself.",
}

_IST = 5.5


def _sun_sign_at(y, m, d, hour_ist):
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(y, m, d, hour_ist - _IST)
    lon = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_MOSEPH)[0][0]
    return int(lon // 30) % 12, lon % 30


def solar_month(sign_index, year):
    """The dates in `year` when the Sun is back in the given sidereal sign (the native's solar month)."""
    from datetime import timedelta
    d, run = date(year, 1, 1), []
    while d <= date(year + 1, 1, 31):
        if _sun_sign_at(d.year, d.month, d.day, 12.0)[0] == sign_index:
            run.append(d)
        d += timedelta(days=1)
    runs, cur = [], []
    for x in run:
        if cur and (x - cur[-1]).days > 1:
            runs.append(cur); cur = []
        cur.append(x)
    if cur:
        runs.append(cur)
    runs = [r for r in runs if r[0].year == year or r[-1].year == year]
    best = max(runs, key=len) if runs else []
    return (best[0], best[-1]) if best else (None, None)


# the generating cycle: which element feeds which
FEEDS = {"Wood": "Water", "Fire": "Wood", "Earth": "Fire", "Metal": "Earth", "Water": "Metal"}


def sun_sign(dob):
    """Vedic sun sign for a date of birth (no birth time needed): the sign the Sun held at noon IST. If the Sun
    changed sign during that day, cusp is True and other names the sign at the other end of the day."""
    s_noon, deg = _sun_sign_at(dob.year, dob.month, dob.day, 12.0)
    s_start, _ = _sun_sign_at(dob.year, dob.month, dob.day, 0.0)
    s_end, _ = _sun_sign_at(dob.year, dob.month, dob.day, 23.99)
    other = s_start if s_start != s_noon else (s_end if s_end != s_noon else None)
    return dict(index=s_noon, degree=round(deg, 1), cusp=other is not None,
                other=SIGNS[other] if other is not None else None, **SIGNS[s_noon])


# ═══════════════════════════════ 5. Pinnacles ═══════════════════════════════
PINNACLES = {
    1: dict(name="Independence", brings="a cycle of standing on your own: new starts, leadership and decisions that are yours to make.",
            work="Lead, start something, or take charge of a team.", money="Grows through your own initiative; promotions and your own venture favour you.",
            love="You need a partner who gives you room.", use="Say yes to responsibility, and stop waiting for permission."),
    2: dict(name="Partnership", brings="a cycle of cooperation, patience and quiet progress through other people.",
            work="Advisory, support and partnership roles; progress comes through alliances.", money="Steady rather than sudden; joint ventures and family money matter.",
            love="Marriage and close bonds are at the centre.", use="Choose your partners well, and be patient with timing."),
    3: dict(name="Expression", brings="a cycle of creativity, visibility and social growth.",
            work="Teaching, speaking, writing, sales: anything where you are seen and heard.", money="Comes through your talent and your network.",
            love="A warm, sociable period; friendships open doors.", use="Show your work, and do not scatter your energy."),
    4: dict(name="Foundation", brings="a cycle of hard work, structure and building something solid.",
            work="Systems, property, engineering and long projects.", money="Builds slowly through discipline and saving, and what you gain stays.",
            love="Family duty is heavy, and it is rewarding.", use="Make a plan and keep it; shortcuts cost more in this cycle."),
    5: dict(name="Freedom", brings="a cycle of change, travel and new experience.",
            work="Sales, media, travel and trade; a change of field is likely.", money="Comes and goes quickly: good earning, so keep a buffer.",
            love="Variety and restlessness; commitment has to be chosen.", use="Adapt fast, without dropping everything you have built."),
    6: dict(name="Responsibility", brings="a cycle of home, family, love and service.",
            work="Care, design, hospitality, education: work that serves.", money="Comfortable when family and work are in balance; much of it goes into the home.",
            love="Marriage, children and family come first.", use="Give care without carrying everyone's load."),
    7: dict(name="Wisdom", brings="a cycle of study, introspection and specialised knowledge.",
            work="Research, analysis and expertise; the depth you build now pays later.", money="Comes through expertise rather than hustle; avoid speculation.",
            love="You need time alone; choose depth over drama.", use="Learn one thing deeply, and protect your health and your quiet time."),
    8: dict(name="Power", brings="a cycle of ambition, authority and material results.",
            work="Management, business, finance and positions of responsibility.", money="The strongest money cycle: earning, assets and recognition, earned through effort.",
            love="Work can crowd out family; plan time for them.", use="Aim high, stay ethical, and do not neglect rest."),
    9: dict(name="Completion", brings="a cycle of endings, service and broad horizons.",
            work="Public work, healing, teaching, and causes larger than yourself.", money="Follows generosity and reputation; let go of what has run its course.",
            love="Old chapters close, and compassion grows.", use="Finish things, forgive, and make room for what comes next."),
    11: dict(name="Illumination (master 11)", brings="a master cycle of intuition and inspiration, read through the 2.",
             work="Guiding, counselling, and spiritual or creative leadership.", money="Follows purpose; nervous energy can disturb it.",
             love="Sensitive and idealistic.", use="Trust your intuition, and ground it in a daily routine."),
    22: dict(name="The master builder (master 22)", brings="a master cycle for building something large, read through the 4.",
             work="Large projects, institutions, and businesses that outlast you.", money="Big potential when vision meets discipline.",
             love="Shared purpose holds your relationships together.", use="Think big, then plan in detail."),
}


def _pin(n):
    return n if n in (11, 22) else root(n)


def pinnacles(dob, destiny, year):
    """The four pinnacles with their ages, and which one runs on 1 January of `year`."""
    m, d, y = root(dob.month), root(dob.day), root(sum(int(c) for c in str(dob.year)))
    p1 = _pin(m + d)
    p2 = _pin(d + y)
    p3 = _pin(root(p1) + root(p2))
    p4 = _pin(m + y)
    end1 = 36 - root(destiny)
    spans = [(0, end1), (end1, end1 + 9), (end1 + 9, end1 + 18), (end1 + 18, None)]
    age = age_on_jan1(dob, year)
    out = []
    for i, (n, (a, b)) in enumerate(zip((p1, p2, p3, p4), spans)):
        out.append(dict(i=i + 1, num=n, root=root(n), label=f"{n}/{root(n)}" if n in (11, 22) else str(n),
                        start=a, end=b, current=(a <= age and (b is None or age < b)), **PINNACLES[n]))
    parts = dict(month=m, day=d, year=y, first_end=end1)
    return out, parts


def age_on_jan1(dob, year):
    a = year - dob.year - 1
    return a + 1 if (dob.month, dob.day) == (1, 1) else a


# ═══════════════════════════════ 6. 10-year life graph ═══════════════════════════════
GRAPH_STRETCH = {
    ("up", "above"): ("An open stretch", "Life rises and sits above what you need to feel satisfied. Effort turns into results quickly: this is the time to take on the bigger thing."),
    ("up", "below"): ("A climbing stretch", "Life improves year by year, even if it still feels short of what you want. Keep going: the line is heading your way."),
    ("down", "above"): ("A stretch to secure", "Still good, but the line is turning down. Finish what you started, save, and protect what you have built."),
    ("down", "below"): ("A working stretch", "The same result asks more effort here. It is not a bad period; it is a working one. Keep commitments small, steady and close to home."),
    ("flat", "above"): ("A steady high", "A settled, satisfying stretch. Use it to consolidate and to plan the next climb."),
    ("flat", "below"): ("A steady stretch", "Little changes on its own here. Small, regular effort is what moves the line."),
}
GRAPH_NEED = ("Your life need is the level at which life feels satisfying to you. The higher it is, the more you expect of yourself and of life. "
              "Where the graph runs above it, life feels better than you hoped; where it runs below, the same results take more effort. "
              "A low stretch does not mean a bad life: it means a working one.")


def graph_points(dob, upto_age=130):
    """The graph's points (age, level), from the birth point at (0, 0), repeating the digits after the last one."""
    main = int(f"{dob.day:02d}{dob.month:02d}") * dob.year
    digits = [int(c) for c in str(main)]
    pts = [(0, 0)]
    k = 1
    while True:
        dgt = digits[(k - 1) % len(digits)]
        age = 10 * k + dgt
        pts.append((age, dgt))
        if age > upto_age:
            break
        k += 1
    need = round(sum(digits) / len(digits), 1)
    return dict(main=main, digits=digits, need=need, points=pts)


def level_at(points, age):
    for (a0, v0), (a1, v1) in zip(points, points[1:]):
        if a0 <= age <= a1:
            return v0 if a1 == a0 else v0 + (v1 - v0) * (age - a0) / (a1 - a0)
    return points[-1][1]


def life_graph(dob, year, span=10):
    g = graph_points(dob)
    a0 = age_on_jan1(dob, year)
    a1 = a0 + span
    # the whole life, as the video draws it: birth to 90 (further for older readers), every peak and dip named
    life_end = min(120, max(90, ((a1 + 15) // 10 + 1) * 10))
    life = [(a, v) for a, v in g["points"] if a <= life_end]
    nxt = next(((a, v) for a, v in g["points"] if a > life_end), None)
    if nxt:
        life.append((life_end, level_at(g["points"], life_end)))
    turns = []
    for (pa, pv), (a, v), (na, nv) in zip(life, life[1:], life[2:]):
        if v > pv and v >= nv:
            turns.append(dict(kind="peak", age=a, level=v, year=year + (a - a0)))
        elif v < pv and v <= nv:
            turns.append(dict(kind="dip", age=a, level=v, year=year + (a - a0)))
    years = [dict(age=a, year=year + (a - a0), level=round(level_at(g["points"], a), 1)) for a in range(a0, a1 + 1)]
    inside = [(a, v) for a, v in g["points"] if a0 < a < a1]
    path = [(a0, level_at(g["points"], a0))] + inside + [(a1, level_at(g["points"], a1))]
    # stretches between the turning points inside the window
    stretches = []
    need = g["need"]
    cut = []                                    # split each segment where it crosses the life need, so a stretch is all
    for (sa, sv), (ea, ev) in zip(path, path[1:]):   # above or all below
        if (sv - need) * (ev - need) < 0:
            xa = sa + (need - sv) / (ev - sv) * (ea - sa)
            cut += [((sa, sv), (xa, need)), ((xa, need), (ea, ev))]
        else:
            cut.append(((sa, sv), (ea, ev)))
    for (sa, sv), (ea, ev) in cut:
        if ea - sa < 0.5:
            continue
        d = "up" if ev - sv > 0.25 else ("down" if sv - ev > 0.25 else "flat")
        mid = (sv + ev) / 2
        side = "above" if mid >= need else "below"
        title, text = GRAPH_STRETCH[(d, side)]
        y0 = year + int(round(sa)) - a0
        y1 = year + int(round(ea)) - a0
        if stretches and stretches[-1]["dir"] == d and stretches[-1]["side"] == side:
            stretches[-1].update(end_age=ea, end_year=y1, end_level=round(ev, 1))
            continue
        stretches.append(dict(dir=d, side=side, title=title, text=text, start_age=sa, end_age=ea, start_year=y0, end_year=y1,
                              start_level=round(sv, 1), end_level=round(ev, 1)))
    above = sum(1 for y in years if y["level"] >= g["need"])
    peak = max(years, key=lambda y: (y["level"], -y["age"]))
    low = min(years, key=lambda y: (y["level"], y["age"]))
    return dict(g, start_age=a0, end_age=a1, years=years, path=path, stretches=stretches, above=above, peak=peak, low=low,
                dm=f"{dob.day:02d}{dob.month:02d}", life=life, life_end=life_end, turns=turns)
