"""Pages for the parameters added on 31 October 2026: the Vedic sun sign, the five elements, the four pinnacles and
the 10-year life graph. What they say comes from framework.py; this file only lays it out, through the same page
kit and look as every other page, so each Mulank design draws them in its own style."""
from . import framework as F
from .content import PLANET, join_and, ordinal, pl, Pl, reduce
from .kit import esc

REL_SAYS = {
    "friend": "counts {o} as a friend",
    "enemy": "does not count {o} as a friend",
    "neutral": "is neutral to {o}",
    "mixed": "treats {o} as both friend and rival",
}
YEAR_FIT = {
    "same": "The year is ruled by your sign's own lord, so {Y} should feel like your own year.",
    "friend": "So {Y}'s themes suit your sign: lean into them.",
    "neutral": "So {Y} neither helps nor fights your sign: results follow effort.",
    "mixed": "So {Y} helps you and tests you in turn: push on the good months, go gently on the careful ones.",
    "enemy": "So {Y} asks for things your sign resists: go a little slower, and lean on your support numbers.",
    None: "Read the year's themes against your sign's nature.",
}
HARMONY = {
    3: ("In tune with you", "both your numbers welcome it"),
    2: ("Mixed", "one of your numbers welcomes it"),
    1: ("Demanding", "it asks you to stretch"),
}


class MorePages:
    # ── small helpers ──
    def _rel(self, own, other):
        own, other = reduce(own), reduce(other)
        if own == other:
            return "same"
        return self.r.rel(own, other)

    def _harmony(self, n):
        """How well a pinnacle number sits with the person's Mulank and Bhagyank: 3 in tune, 2 mixed, 1 demanding."""
        r = self.r
        rp, rd = self._rel(r.P, n), self._rel(r.D, n)
        good = sum(1 for x in (rp, rd) if x in ("friend", "same"))
        return 3 if good == 2 else (2 if good == 1 else 1)

    # ═══════════════ 4. Vedic sun sign ═══════════════
    def zodiac_page(self):
        r, T, Y = self.r, self.T, self.Y
        s = F.sun_sign(r.dob_date)
        self.sun = s
        lord = s["lord"]
        cusp = (f' The Sun changed sign on the day you were born: it moved between {s["other"]["sa"]} ({s["other"]["en"]}) and {s["sa"]}. '
                f'Without your birth time we read {s["sa"]}, the sign it held at midday.') if s["cusp"] else ""
        dig = F.DIGNITY_LINE.get(s["dignity"], "")
        own = self._rel(r.P, lord)
        own_txt = (f"Your Mulank {r.P} is ruled by {pl(r.P)}, the same planet that rules your sun sign: the two read as one." if own == "same" else
                   f"Your Mulank {r.P} is ruled by {pl(r.P)}, which {REL_SAYS.get(own, 'meets {o}').format(o=pl(lord))}, your sign's lord.")
        fit = self._rel(lord, r.PY)
        year_txt = (YEAR_FIT["same"].format(Y=Y) if fit == "same" else
                    f"{Y} is your {PLANET[r.PY]} year, and {pl(lord)} {REL_SAYS.get(fit, 'meets {o}').format(o=pl(r.PY))}. {YEAR_FIT.get(fit, YEAR_FIT[None]).format(Y=Y)}")
        inner = f"""
{self.L.blob(T.PINK, 250, 250, 420, 70, "disc")}
<div class="abs num" style="left:{545 - 24 * len(str(lord))}px;top:140px;font-size:96px;color:{T.NAVY}">{lord}</div>
<div class="abs caps" style="left:420px;top:338px;width:250px;text-align:center;font-size:10.5px;color:{T.NAVY}">Lord: {PLANET[lord]}</div>
<div style="height:304px"><div style="margin-top:6px">{self.L.plate("Your sun", 54, -5, T.NAVY, width=340)}</div>
<div style="margin:-8px 0 0 40px">{self.L.plate(f"in {s['sa']}", 54, 3, T.NAVY, width=340)}</div></div>
<div class="lead" style="margin-top:0;width:620px">On {r.dob_text} the Sun stood in {s["sa"]} ({s["en"]}) in the Vedic zodiac, which measures the signs against the fixed stars. {s["sa"]} is ruled by {pl(lord)}, number {lord} in numerology.{cusp}</div>
{f'<div class="it" style="font-size:20px;margin-top:14px;width:620px;color:{T.BERRY_D}">{dig}</div>' if dig else ""}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:22px">
{self.panel(T.WHITE, self.ptitle("Your nature", T.NAVY, 19) + f'<div class="small">{s["nature"]}</div>')}
{self.panel(T.WHITE, self.ptitle("Your sign and your numbers", T.NAVY, 19) + f'<div class="small">{own_txt}</div>')}
{self.panel(T.ORANGE, self.ptitle(f"Strength to use in {Y}", T.DEEP, 19) + f'<div class="small">{s["strength"]}</div>')}
{self.panel(T.PINK, self.ptitle("Watch for", T.DEEP, 19) + f'<div class="small">{s["watch"]}</div>')}
</div>
<div class="lead" style="margin-top:20px;width:620px">{year_txt}</div>
{self._solar_month_panel(s)}
"""
        self.pg.add(T.LBLUE, inner)

    def _solar_month_panel(self, s):
        T, Y = self.T, self.Y
        a, b = F.solar_month(s["index"], Y)
        if not a:
            return ""
        fmt = lambda d: f"{d.day} {d.strftime('%B')}" + (f" {d.year}" if d.year != Y else "")
        return self.panel(T.WHITE, self.ptitle(f"Your solar month in {Y}: {fmt(a)} to {fmt(b)}", T.NAVY, 19)
                          + f'<div class="small">These are the days the Sun is back in {s["sa"]}, where it stood when you were born. '
                          f'Use them to renew a commitment, start something personal, and look after your energy.</div>', extra="margin-top:18px")

    # ═══════════════ 3. Elements ═══════════════
    def _element_colours(self):
        T = self.T
        return {"Earth": T.ORANGE, "Fire": T.BERRY, "Wood": T.GREEN, "Metal": T.NAVY, "Water": T.COBALT}

    def elements_page(self):
        r, T, Y = self.r, self.T, self.Y
        els = F.elements_of(r.cnt)
        self.els = els
        cols = self._element_colours()
        top = max(6, max(e["count"] for e in els))
        bars = ""
        for e in els:
            w = 0 if not e["count"] else max(24, int(330 * e["count"] / top))
            bars += (f'<div style="display:flex;align-items:center;gap:16px;padding:12px 0">'
                     f'<div style="width:150px"><div class="disp b" style="font-size:24px;color:{T.NAVY}">{e["name"]}</div>'
                     f'<div class="caps" style="font-size:10px;margin-top:4px">Numbers {" &#183; ".join(map(str, e["numbers"]))}</div></div>'
                     f'<div style="flex:1;position:relative;height:30px;background:rgba(0,0,0,.05)">'
                     f'<div style="position:absolute;left:0;top:0;bottom:0;width:{w}px;background:{cols[e["name"]]}"></div></div>'
                     f'<div style="width:96px;text-align:right"><span class="num" style="font-size:28px;color:{T.NAVY}">{e["count"]}</span>'
                     f'<div class="caps" style="font-size:10px;margin-top:2px">{F.LEVEL_WORD[e["level"]]}</div></div></div>')
        strong = [e for e in els if e["level"] == "strong"] or sorted(els, key=lambda e: -e["count"])[:1]
        weak = [e for e in els if e["level"] in ("missing", "light")]
        s_txt = f"Your strongest element is {join_and([e['name'] for e in strong])}: {strong[0]['gives']}."
        miss = [e["name"] for e in weak if e["level"] == "missing"]
        light = [e["name"] for e in weak if e["level"] == "light"]
        bits = ([f"{join_and(miss)} {'is' if len(miss) == 1 else 'are'} missing"] if miss else []) + ([f"{join_and(light)} {'is' if len(light) == 1 else 'are'} light"] if light else [])
        w_txt = (f" {' and '.join(bits)} on your grid: the energ{'y' if len(weak) == 1 else 'ies'} you build in {Y}." if weak
                 else " No element is missing or light: your grid is unusually balanced.")
        inner = f"""
{self.head("Elemental theory", "Your five<br>elements", sub="Every number belongs to an element: Earth 2, 5 and 8; Fire 1 and 9; Wood 3 and 4; Metal 6 and 7; Water 2. Counted on your Lo Shu grid, they show which energies you were born with in plenty, and which you build.")}
<div class="ruled" style="width:620px">{bars}</div>
<div class="lead" style="margin-top:24px;width:620px">{s_txt}{w_txt}</div>
<div class="small" style="margin-top:12px;width:620px">The 2 belongs to both Earth and Water, so it counts for both. Your grid includes your destiny number {r.D}.</div>
{self.L.sparkle(T.PINK, 50, 610, 66)}
"""
        self.pg.add(T.CREAM, inner)

    def elements_balance(self):
        r, T, Y = self.r, self.T, self.Y
        els = getattr(self, "els", None) or F.elements_of(r.cnt)
        weak = sorted([e for e in els if e["level"] in ("missing", "light")], key=lambda e: e["count"])[:3]
        strong = [e for e in els if e["level"] == "strong"][:1]
        cards = []
        for e in weak:
            what = "missing" if e["level"] == "missing" else "light"
            feeder = next(x for x in els if x["name"] == F.FEEDS[e["name"]])
            feed = (f"{feeder['name']} feeds {e['name']}, and yours is {F.LEVEL_WORD[feeder['level']].lower()}, so building {e['name']} comes easily."
                    if feeder["level"] in ("balanced", "strong") else
                    f"{feeder['name']} feeds {e['name']}, and yours is {F.LEVEL_WORD[feeder['level']].lower()} too: start with one {feeder['name']} habit as well.")
            body = (f'<div class="small">{e["weak"]}</div>'
                    f'<ul class="dots small" style="margin-top:10px">' + "".join(f'<li class="good">{x}</li>' for x in e["remedies"]) + "</ul>"
                    f'<div class="small" style="margin-top:6px"><b>Colours:</b> {e["colour"]}. {feed}</div>')
            cards.append(self.panel(T.WHITE, self.ptitle(f"Build your {e['name']} ({what})", T.NAVY, 20) + body))
        for e in strong:
            body = f'<div class="small">{e["strong"]}</div><div class="small" style="margin-top:8px"><b>Use it for:</b> {e["gives"]}.</div>'
            cards.append(self.panel(T.ORANGE, self.ptitle(f"Your {e['name']} is strong", T.DEEP, 20) + body))
        if not weak:
            cards.insert(0, self.panel(T.WHITE, self.ptitle("Keep the balance", T.NAVY, 20) +
                                       '<div class="small">With every element present, the work is to keep it that way: a few minutes of morning sunlight, a plant at home, a tidy desk, regular meals and enough water cover all five.</div>'))
        inner = f"""
{self.head("Elemental theory", "Bringing your<br>elements into balance", sub=f"Small, daily changes that add what your grid lacks. They are built into your month-by-month plan for {Y}.")}
<div style="display:grid;gap:12px;width:620px">{"".join(cards)}</div>
{self.L.petal_flower(T.PINK, 56, 610, 62, hole=T.CREAM)}
"""
        self.pg.add(T.PINK, inner)

    # ═══════════════ 5. Pinnacles ═══════════════
    def pinnacles_page(self):
        r, T, Y = self.r, self.T, self.Y
        pins, parts = F.pinnacles(r.dob_date, r.D, Y)
        self.pins = pins
        cur = next((p for p in pins if p["current"]), pins[0])
        by = r.dob_date.year
        cards = ""
        for p in pins:
            h = self._harmony(p["root"])
            p["harmony"] = h
            short = p["name"].split(" (")[0]
            on = p["current"]
            bg, fg = (T.WHITE, T.INK) if on else ("rgba(255,255,255,.08)", "#E7ECF7")
            ages = f"Age {p['start']} to {p['end']}" if p["end"] is not None else f"From age {p['start']}"
            years = f"{by + p['start']} to {by + p['end']}" if p["end"] is not None else f"from {by + p['start']}"
            cards += (f'<div class="tile" style="background:{bg};color:{fg};padding:18px 16px;display:flex;flex-direction:column;gap:8px;min-height:300px;'
                      f'{"box-shadow:0 0 0 4px " + T.PINK + ";" if on else "border:1px solid rgba(255,255,255,.25);"}">'
                      f'<div class="caps" style="font-size:10px">Pinnacle {p["i"]}{" &#183; now" if on else ""}</div>'
                      f'<div class="num" style="font-size:{56 if len(p["label"]) < 3 else 44}px;color:{T.NAVY if on else T.WHITE}">{p["label"]}</div>'
                      f'<div class="disp b" style="font-size:{min(19, max(11, int(112 / (len(short) * max(self.L.plate_em, .55)))))}px;white-space:nowrap;color:{T.NAVY if on else T.WHITE}">{short}</div>'
                      f'<div class="small">{ages}<br>{years}</div>'
                      f'<div class="caps" style="font-size:9.5px;margin-top:auto;color:{T.BERRY_D if on else T.PINK}">{HARMONY[h][0]}</div></div>')
        future = [p for p in pins if p["end"] is None or p["end"] > F.age_on_jan1(r.dob_date, Y)]
        best = max(future, key=lambda p: (p["harmony"], -p["i"]))
        nxt = next((p for p in pins if p["i"] == cur["i"] + 1), None)
        if best["current"]:
            best_txt = f"Your strongest stretch is the one you are in: pinnacle {best['i']}, {best['name'].lower()}, where {HARMONY[best['harmony']][1]}."
        else:
            best_txt = (f"Your strongest stretch ahead is pinnacle {best['i']}, {best['name'].lower()}, from age {best['start']} "
                        f"({by + best['start']}): {HARMONY[best['harmony']][1]}.")
        now_txt = (f"You are in pinnacle {cur['i']}, {cur['name'].lower()}, "
                   + (f"until age {cur['end']} ({by + cur['end']})." if cur["end"] is not None else "which runs for the rest of your life."))
        inner = f"""
<h2 class="disp t2" style="margin-top:20px;line-height:1">Your life in<br>four pinnacles</h2>
<div class="lead" style="margin-top:20px;width:620px;color:#E7ECF7">Pinnacles divide your life into four long cycles. Each has its own number: the kind of work that comes to you, how money moves, and what you are building at that age.</div>
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:30px">{cards}</div>
{self._life_bar(pins, F.age_on_jan1(r.dob_date, Y))}
<div class="lead" style="margin-top:26px;width:620px;color:#FFFFFF">{now_txt} {best_txt}</div>
<div class="small" style="margin-top:18px;width:620px;color:#C9D3EA">How it is worked out: birth month {parts["month"]}, day {parts["day"]} and year {parts["year"]}, each reduced. First: month + day. Second: day + year. Third: first + second. Fourth: month + year. 11 and 22 are kept as master pinnacles. The first ends at 36 minus your destiny number {r.D}: age {parts["first_end"]}. The next two last nine years each.</div>
{self.L.sparkle(T.WHITE, 46, 616, 64)}
"""
        self.pg.add(T.NAVY, inner)

    def _life_bar(self, pins, age):
        T = self.T
        span = pins[3]["start"] + 18
        X = lambda a: 620 * min(a, span) / span
        cols = [T.PINK, T.LBLUE, T.ORANGE, T.GREEN]
        segs = "".join(f'<div style="position:absolute;left:{X(p["start"]):.0f}px;width:{X(p["end"] if p["end"] is not None else span) - X(p["start"]):.0f}px;top:0;height:16px;'
                       f'background:{cols[k]};border-right:2px solid {T.NAVY}"></div>'
                       f'<div class="caps" style="position:absolute;left:{X(p["start"]) + 4:.0f}px;top:24px;font-size:10px;color:#E7ECF7">{p["start"]}</div>'
                       for k, p in enumerate(pins))
        here = (f'<div style="position:absolute;left:{X(age) - 1:.0f}px;top:-14px;width:3px;height:44px;background:{T.WHITE}"></div>'
                f'<div class="caps" style="position:absolute;left:{max(0, min(X(age) - 50, 520)):.0f}px;top:-34px;width:100px;text-align:center;font-size:10px;color:{T.WHITE}">You, age {age}</div>')
        return f'<div style="position:relative;width:620px;height:46px;margin-top:58px">{segs}{here}</div>'

    def pinnacle_now(self):
        r, T, Y = self.r, self.T, self.Y
        pins = getattr(self, "pins", None) or F.pinnacles(r.dob_date, r.D, Y)[0]
        cur = next((p for p in pins if p["current"]), pins[0])
        nxt = next((p for p in pins if p["i"] == cur["i"] + 1), None)
        by = r.dob_date.year
        rows = "".join(f'<div style="display:flex;gap:18px"><span class="caps" style="width:130px;font-size:11px;padding-top:3px;color:{T.NAVY}">{k}</span>'
                       f'<span class="body" style="flex:1">{v}</span></div>'
                       for k, v in (("Work", cur["work"]), ("Money potential", cur["money"]), ("Love and family", cur["love"]), ("How to use it", cur["use"])))
        span = f"ages {cur['start']} to {cur['end']}" if cur["end"] is not None else f"from age {cur['start']}"
        more = ""
        if nxt:
            more = self.panel(T.WHITE, self.ptitle(f"Next: pinnacle {nxt['i']}, {nxt['label']}, from age {nxt['start']} ({by + nxt['start']})", T.NAVY, 19)
                              + f'<div class="small"><b>{nxt["name"]}:</b> {nxt["brings"]} {nxt["use"]}</div>')
            if cur["end"] is not None and cur["end"] - F.age_on_jan1(r.dob_date, Y) <= 10:
                more += self.panel(T.ORANGE, self.ptitle("The change falls inside your next ten years", T.DEEP, 18)
                                   + f'<div class="small">Your pinnacle turns from {cur["label"]} to {nxt["label"]} in {by + cur["end"]}. Your 10-year life graph, next, shows how that decade moves.</div>')
        else:
            more = self.panel(T.WHITE, self.ptitle("Your last and longest pinnacle", T.NAVY, 19)
                              + '<div class="small">This cycle runs for the rest of your life. Everything earlier was preparation for it.</div>')
        inner = f"""
<div style="margin-top:6px">{self.L.plate(f"Pinnacle {cur['i']}:", 54, -5, T.BERRY, width=420)}</div>
<div style="margin:-8px 0 0 40px">{self.L.plate(cur["name"].split(" (")[0].lower(), 54, 3, T.BERRY, width=480)}</div>
<div class="lead" style="margin-top:28px;width:620px">Number {cur["label"]}, {span}: {cur["brings"]} Under {pl(cur["root"])}, {HARMONY[cur.get("harmony", self._harmony(cur["root"]))][1]}.</div>
<div class="ruled" style="width:620px;margin-top:22px">{rows}</div>
<div style="display:grid;gap:12px;margin-top:24px;width:620px">{more}</div>
{self.L.asterisk(T.BERRY, 70, 600, 60, 14)}
"""
        self.pg.add(T.CREAM, inner)

    # ═══════════════ 6. 10-year life graph ═══════════════
    def _graph_svg(self, g, W=620, H=420):
        T = self.T
        L, R, Tp, B = 34, 14, 18, 56
        a0, a1 = g["start_age"], g["end_age"]
        X = lambda a: L + (a - a0) / (a1 - a0) * (W - L - R)
        Yv = lambda v: Tp + (9 - v) / 9 * (H - Tp - B)
        fam = self.T.body["family"]
        grid = "".join(f'<line x1="{L}" x2="{W - R}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="{T.INK}" stroke-opacity="{.16 if v in (0, 9) else .07}"/>'
                       f'<text x="{L - 10}" y="{Yv(v) + 4:.1f}" text-anchor="end" font-family="{fam}" font-size="11" fill="{T.INK}" fill-opacity=".6">{v}</text>'
                       for v in range(10))
        ticks = "".join(f'<line x1="{X(y["age"]):.1f}" x2="{X(y["age"]):.1f}" y1="{H - B}" y2="{H - B + 5}" stroke="{T.INK}" stroke-opacity=".4"/>'
                        f'<text x="{X(y["age"]):.1f}" y="{H - B + 20}" text-anchor="middle" font-family="{fam}" font-size="11.5" font-weight="700" fill="{T.INK}">{y["age"]}</text>'
                        f'<text x="{X(y["age"]):.1f}" y="{H - B + 36}" text-anchor="middle" font-family="{fam}" font-size="10" fill="{T.INK}" fill-opacity=".65">{y["year"]}</text>'
                        for y in g["years"])
        pts = " ".join(f"{X(a):.1f},{Yv(v):.1f}" for a, v in g["path"])
        ny = Yv(g["need"])
        area = f'{pts} {X(a1):.1f},{ny:.1f} {X(a0):.1f},{ny:.1f}'
        turns = "".join(f'<circle cx="{X(a):.1f}" cy="{Yv(v):.1f}" r="7" fill="{T.BERRY}" stroke="#FFFFFF" stroke-width="2"/>'
                        f'<text x="{X(a):.1f}" y="{Yv(v) - 14:.1f}" text-anchor="middle" font-family="{fam}" font-size="11" font-weight="700" fill="{T.BERRY}">age {a}</text>'
                        for a, v in g["path"][1:-1])
        dots = "".join(f'<circle cx="{X(y["age"]):.1f}" cy="{Yv(y["level"]):.1f}" r="3.2" fill="{T.NAVY}"/>' for y in g["years"])
        return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="display:block;overflow:visible">
<defs><clipPath id="lgA"><rect x="0" y="0" width="{W}" height="{ny:.1f}"/></clipPath><clipPath id="lgB"><rect x="0" y="{ny:.1f}" width="{W}" height="{H}"/></clipPath></defs>
{grid}
<polygon points="{area}" fill="{T.GREEN}" fill-opacity=".22" clip-path="url(#lgA)"/>
<polygon points="{area}" fill="{T.ORANGE}" fill-opacity=".35" clip-path="url(#lgB)"/>
<line x1="{L}" x2="{W - R}" y1="{ny:.1f}" y2="{ny:.1f}" stroke="{T.BERRY}" stroke-width="2" stroke-dasharray="7 6"/>
<text x="{W - R}" y="{ny - 8:.1f}" text-anchor="end" font-family="{fam}" font-size="12" font-weight="700" fill="{T.BERRY}">Life need {g["need"]}</text>
<polyline points="{pts}" fill="none" stroke="{T.NAVY}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>
{dots}{turns}
<line x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}" stroke="{T.INK}" stroke-opacity=".4"/>
{ticks}
<text x="{L}" y="{H - 2}" font-family="{fam}" font-size="10" fill="{T.INK}" fill-opacity=".6">AGE AND YEAR</text>
</svg>"""

    def graph_page(self):
        r, T, Y = self.r, self.T, self.Y
        g = F.life_graph(r.dob_date, Y)
        self.graph = g
        n = len(g["years"])
        pk, lw = g["peak"], g["low"]
        first, last = g["years"][0]["level"], g["years"][-1]["level"]
        trend = "rises" if last - first > .3 else ("eases" if first - last > .3 else "holds steady")
        if g["above"] == n:
            head = f"All {n} years run at or above your life need of {g['need']}: a decade that should feel better than you hoped."
        elif g["above"] == 0:
            head = f"Through these {n} years your line stays under your life need of {g['need']}: a working decade, where steady effort is what brings results."
        else:
            head = f"{g['above']} of these {n} years run at or above your life need of {g['need']}."
        summary = (f"{head} Over the decade the line {trend}, from {first} to {last}; its highest point is {pk['year']}, at age {pk['age']}"
                   + (f", and its lowest {lw['year']}, at age {lw['age']}." if lw["year"] != pk["year"] else "."))
        inner = f"""
{self.head("10-year life graph", f"Your life, age<br>{g['start_age']} to {g['end_age']}", sub=f"Your birth day and month, {g['dm']}, multiplied by your birth year, {r.dob_date.year}, give {g['main']:,}. Each digit marks a point in your life, and the dotted line is your life need: the level at which life feels satisfying to you.")}
<div style="margin-top:6px">{self._graph_svg(g)}</div>
<div style="display:flex;gap:22px;margin-top:12px" class="small"><span><span style="display:inline-block;width:14px;height:14px;background:{T.GREEN};opacity:.5;vertical-align:-2px"></span> above your life need</span>
<span><span style="display:inline-block;width:14px;height:14px;background:{T.ORANGE};opacity:.7;vertical-align:-2px"></span> below it: more effort for the same result</span></div>
<div class="lead" style="margin-top:18px;width:620px">{summary}</div>
"""
        self.pg.add(T.CREAM, inner)

    def graph_read(self):
        r, T, Y = self.r, self.T, self.Y
        g = getattr(self, "graph", None) or F.life_graph(r.dob_date, Y)
        cards = ""
        for s in g["stretches"][:4]:
            ages = f"age {round(s['start_age'])} to {round(s['end_age'])}"
            col = T.WHITE if s["side"] == "above" else T.ORANGE
            cards += self.panel(col, self.ptitle(f"{s['start_year']} to {s['end_year']} &#183; {s['title']}", T.NAVY if col == T.WHITE else T.DEEP, 19)
                                + f'<div class="caps" style="font-size:10px;margin:-2px 0 8px">{ages} &#183; level {s["start_level"]} to {s["end_level"]}</div>'
                                + f'<div class="small">{s["text"]}</div>')
        rows = "".join(f'<tr><td>{y["year"]}</td><td>{y["age"]}</td><td>{y["level"]}</td><td>{"above" if y["level"] >= g["need"] else "below"}</td></tr>'
                       for y in g["years"])
        inner = f"""
{self.head("Reading your graph", "Your decade,<br>stretch by stretch")}
<div class="body" style="width:620px">{F.GRAPH_NEED}</div>
<div style="display:grid;gap:10px;margin-top:20px;width:620px">{cards}</div>
<table class="t" style="margin-top:20px;width:620px"><tr><th>Year</th><th>Age</th><th>Level</th><th>Against your life need</th></tr>{rows}</table>
{self.L.heart(T.BERRY, 46, 616, 64)}
"""
        self.pg.add(T.LBLUE, inner)
