"""Pages 22 onward: the year, life areas, timing, practices, watch, mobile number, next steps and close."""
from .content import care_part, pl, Pl, MONTHS, PLANET, PM, REL_WORD, clean, first_sentence, join_and, ordinal, reduce, soft
from .deck import (AREA_TITLES, LINKS, MAIL, PM_SHORT, SITE, WA_NUM, dots, plain)
from .kit import action_bar, asset, asterisk, blob, esc, heart, icon, petal_flower, photo, plate, ring, sparkle

VGRID = [[3, 1, 9], [6, 7, 5], [2, 8, 4]]
STATE_TAG = {"fav": "favourable", "careful": "careful", "steady": "steady", "mixed": "mixed"}


class YearPages:
    # ── year opener + cycle ──
    def year_open(self):
        r, T, Y = self.r, self.T, self.Y
        start = Y - (r.PY - 1)
        cyc = {c["year"]: c["py"] for c in r.d["cycle"]}
        from .content import PY_FRAME
        cols = [T.PINK, T.ORANGE, T.LBLUE, T.GREEN, T.COBALT, T.BERRY, T.PINK, T.LBLUE, T.ORANGE]
        discs = ""
        for i in range(9):
            y = start + i
            on = y == Y
            n = i + 1
            dk = not on and cols[i] in (T.NAVY, T.COBALT, T.BERRY, T.GREEN)
            discs += (f'<div style="text-align:center;width:66px"><div class="round" style="width:58px;height:58px;margin:0 auto;border-radius:50%;'
                      f'background:{T.WHITE if on else cols[i]};display:flex;align-items:center;justify-content:center;'
                      f'{"box-shadow:0 0 0 5px " + T.PINK + ";" if on else ""}{"border:1.5px solid rgba(255,255,255,.4);" if dk else ""}"><span class="num" style="font-size:30px;color:{T.WHITE if dk else T.NAVY}">{n}</span></div>'
                      f'<div class="caps" style="font-size:10px;margin-top:10px;color:{T.WHITE if on else "#C9D3EA"}">{y}</div>'
                      f'<div class="tiny" style="color:{T.WHITE if on else "#C9D3EA"}">{PY_FRAME[n]["cycle"]}</div></div>')
        prev_py = reduce(r.PY - 1) if r.PY > 1 else 9
        prev_lines = r.py_lines(["theme"], "prev")[:2]
        prev = " ".join(prev_lines) or PY_FRAME[prev_py]["gist"].capitalize() + "."
        word = "Moon" if r.PY == 2 else ("Sun" if r.PY == 1 else PLANET[r.PY])
        cycle_txt = (f"Your personal years run in cycles of nine. Year 1 plants seeds, year 9 clears the field, and every year between has its own job. "
                     f"{Y - 1} was your Personal Year {prev_py}. {Y} is year {r.PY} of {'a new' if r.PY == 1 else 'the'} cycle, and what you do in it shapes the "
                     + ("next eight." if r.PY == 1 else f"next {WORDS[9 - r.PY]}." if r.PY < 9 else "next cycle."))
        inner = f"""
<h2 class="disp" style="font-size:96px;margin-top:40px;line-height:.9">{Y},<br>your {word}<br>year</h2>
<div class="it" style="font-size:26px;color:{T.PINK};margin-top:22px">{r.frame["tag"]}</div>
<div class="lead" style="width:600px;margin-top:26px;color:#E7ECF7">{cycle_txt}</div>
<div style="position:relative;margin-top:44px">
<div style="position:absolute;left:30px;right:30px;top:29px;height:2px;background:{T.PINK}"></div>
<div style="display:flex;justify-content:space-between;position:relative">{discs}</div></div>
{self.panel("rgba(255,255,255,.1)", self.ptitle(f"Looking back: {Y - 1}, your {PY_FRAME[prev_py]['cycle'].lower()} year", T.PINK, 18) + f'<div class="small" style="color:#E7ECF7">Your rulebook describes a Personal Year {prev_py} this way: {prev[0].lower() + prev[1:]} What you started or learned then is what {Y} asks you to carry forward.</div>', T.WHITE, extra="margin-top:34px")}
{self.L.asterisk(T.PINK, 70, 600, 60, 14)}
"""
        self.pg.add(T.NAVY, inner)

    def year_rules(self):
        r, T, Y = self.r, self.T, self.Y
        lines = [("trait", t) for t in r.py_lines(["theme"])] + [("good", t) for t in r.py_lines(["do", "career", "money", "relationship", "health", "travel", "education", "home"])]
        lines += [("care", t) for t in r.py_lines(["avoid"])]
        lines = lines[:11]

        def meet(n, label):
            if n == r.PY:
                return f"The year carries the same number. {label.capitalize()} is switched on: its strengths come easily, and its cautions need watching."
            rel = r.rel(n, r.PY)
            return {"friend": f"{Pl(n)} meets {pl(r.PY)}: friends. The year supports {label}; lean on it.",
                    "enemy": f"{Pl(n)} meets {pl(r.PY)}: enemies. {label.capitalize()} and the year pull different ways; expect friction if you measure {Y} by output alone.",
                    "neutral": f"{Pl(n)} meets {pl(r.PY)}: neutral. The year neither helps nor blocks {label}; your choices decide.",
                    "mixed": f"{Pl(n)} meets {pl(r.PY)}: friends and rivals. Some months help {label}, others test it."}.get(rel, "")
        cards = [(f"With your {PLANET[r.D]} destiny ({r.D})", meet(r.D, "your direction"), T.LBLUE),
                 (f"With your {PLANET[r.P]} birth number ({r.P})", meet(r.P, "your everyday self"), T.ORANGE)]
        if r.M:
            cards.append((f"With your master {r.M}", f"The master number sits behind your destiny. In {Y}, intuition will be loud: trust it for people and timing, and check it with facts for money and documents.", T.PINK))
        elif r.K:
            cards.append((f"With your karmic {r.K}", f"A karmic day asks you to finish old lessons. In {Y}, the shortcut is the long way; do things properly the first time.", T.PINK))
        else:
            sup = r.support
            cards.append(("With your support numbers", f"{join_and(sup)} help both sides of your chart. In {Y}, months and dates that carry them are your easiest ground.", T.PINK))
        if r.NR:
            cards.append((f"With your name ({r.NR}, {PLANET[r.NR]})", meet(r.NR, "your name"), T.WHITE))
        mh = "".join(self.panel(bg, self.ptitle(t, T.NAVY, 16) + f'<div class="small">{d}</div>', pad="14px 16px") for t, d, bg in cards)
        inner = f"""
{self.head(f"Personal Year {r.PY}", f"What your rulebook<br>says about {Y}", T.BERRY)}
{dots(lines, "small")}
<div class="caps" style="color:{T.NAVY};margin:14px 0 10px">How {Y} meets your numbers</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">{mh}</div>
"""
        self.pg.add(T.CREAM, inner)

    def asks(self):
        r, T, Y = self.r, self.T, self.Y
        ages = r.age_lines()
        focus = r.frame["focus"]
        rewards, tests = [], []
        for b in focus + ["career", "money", "relationships", "health"]:
            for l in r.area_lines(b, ("good",), limit=3):
                s = first_sentence(l["text"], 110)
                if s not in rewards:
                    rewards.append(s)
            for l in r.area_lines(b, ("care", "mixed"), limit=4):
                s = care_part(l["text"], 110)
                if s and s not in tests:
                    tests.append(s)
        rewards, tests = rewards[:3], tests[:3]
        bday = f"{r.dob['d']} {MONTHS[r.dob['m'] - 1]}"
        if ages:
            a = ages[0]
            age = a["age"]
            when = (f"From your birthday on {bday} {Y - 1} to the day before it in {Y}, you are {age}." if age == Y - r.dob["y"] - 1
                    else f"From your birthday on {bday} {Y}, you are {age}.")
            text = (clean(a["say"]) + " This is not a prediction that something will go wrong. It is a reason to keep paperwork double-checked, avoid rash risks, "
                    f"keep savings for surprises, and respect the careful windows in your timing map.")
            head = self.head("A note on your age", f"The year you are {age}", sub=when)
            body = f'<div class="body">{text}</div>'
        else:
            head = self.head(f"Personal Year {r.PY}", f"What {Y}<br>asks of you", sub=f"{Y} is {r.frame['gist']}. Here is where it meets you.")
            body = ""

        def col(title, items, bg, tcol):
            rows = "".join(f'<div class="small" style="padding:9px 0;border-bottom:1.5px solid rgba(255,255,255,.55)">{t}</div>' for t in items)
            return self.panel(bg, f'<div class="disp b" style="font-size:22px;color:{tcol};margin-bottom:6px">{title}</div>{rows}')
        inner = f"""
{head}
{body}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:22px">
{col(f"What {Y} rewards in you", rewards or [f"The {PLANET[r.P]} habits you were born with, used at the right time"], T.LBLUE, T.NAVY)}
{col(f"What {Y} tests in you", tests or ["Patience in the careful windows"], T.PINK, T.BERRY_D)}
</div>
{self.L.blob(T.ORANGE, 240, 140, 205, 1150, "bumps")}
{self.L.sparkle(T.BERRY, 46, 616, 64)}
"""
        self.pg.add(T.CREAM, inner)

    # ── life areas ──
    def _quarters(self, area):
        r = self.r
        rows = []
        verbs = {"career": ("Act", "ask, apply or launch"), "money": ("Sign", "book, sign or invest"), "relationships": ("Decide", "have the big conversations")}
        for q, (a, z) in enumerate([(1, 3), (4, 6), (7, 9), (10, 12)]):
            ms = r.months[a - 1:z]
            states = {m["state"] for m in ms}
            if states & {"fav", "fav_part"}:
                focus = verbs.get(area, ("Act", "act"))[0]
            elif states <= {"careful", "careful_part"}:
                focus = "Prepare"
            elif "mixed" in states:
                focus = "Weigh up"
            elif states & {"careful", "careful_part"}:
                focus = "Prepare, then build"
            else:
                focus = "Build"
            bits = [f"{PM_SHORT[m['pm']]} in {m['name']}" for m in ms]
            text = "; ".join(bits)
            text = text[0].upper() + text[1:] + "."
            fav = [m for m in ms if m["state"] in ("fav", "fav_part")]
            car = [m for m in ms if m["state"] in ("careful", "careful_part")]
            if fav:
                text += f" {fav[0]['tag'].capitalize()} in {fav[0]['name']}: {verbs.get(area, ('', 'act'))[1]}."
            if car:
                text += f" {'Careful' if car[0]['state'] == 'careful' else car[0]['tag'].capitalize()} in {car[0]['name']}: no signatures."
            rows.append((f"{MONTHS[a - 1][:3]} to {MONTHS[z - 1][:3]}", focus, text))
        return rows

    def area_page(self, area):
        r, T, Y = self.r, self.T, self.Y
        kicker, title = AREA_TITLES[area]
        title = title.format(Y=Y)
        works = [first_sentence(l["text"], 120) for l in r.area_lines(area, ("good",), limit=4)]
        watch = [x for x in (care_part(l["text"], 120) for l in r.area_lines(area, ("care", "mixed"), limit=6)) if x][:3]
        cats = {"career": ["career", "education", "travel"], "money": ["money"], "relationships": ["relationship", "home"], "health": ["health"]}[area]
        actions = r.py_lines(cats)[:3]
        extra = ""
        intro = ""
        if area == "career":
            intro = f"{Y} is {r.frame['gist']}. At work, that means letting your {PLANET[r.P]} strengths do the talking and timing the big asks."
            sm = [m["name"] for m in r.months if m["pm"] in r.support]
            if sm:
                actions.append(f"Ask for the promotion, the new role or the client in a support-number month: {join_and(sm[:3])}")
            actions += r.everyone("well-lit place")[:1]
        elif area == "money":
            care = r.stretches("care")
            if care:
                watch.append(f"Careful windows: {join_and([c['label'] for c in care[:3]])}")
            intro = f"Your rulebook's money advice for a Personal Year {r.PY}, matched to your own numbers. The key is timing."
            actions += r.py_lines(["avoid"])[:1]
        elif area == "relationships":
            intro = f"How {Y} touches the people closest to you: partner, family and the friends you lean on."
            actions += r.everyone("Listen to others")[:1]
            extra = (f'<div style="margin-top:16px">' + self.panel(T.NAVY, self.ptitle("If a relationship decision is on the table", T.PINK, 17)
                     + f'<div class="small" style="color:#E7ECF7">A Numerology Compatibility reading puts your numbers and your partner\'s side by side: birth number, destiny and name, and where they help or rub against each other.</div>'
                     + '<div style="margin-top:12px">' + action_bar("See the reading", "Numerology Compatibility", LINKS["compat"], "or ask on WhatsApp", self.WA["compat"]) + "</div>", T.WHITE) + "</div>")
        elif area == "health":
            intro = f"Where to give extra care in {Y}. None of this is a diagnosis: it sits beside your doctor, never instead."
            actions += r.everyone("Tuesdays")[:1]
            actions.append("See a doctor for anything that persists; these practices sit beside medical care")
            wake = r.everyone("Wake early")
            day = r.py_lines(["do"])[:1]
            rhythm = [("Morning", first_sentence(wake[0], 110) if wake else "Wake early and plan the day on paper"),
                      ("Day", first_sentence(day[0], 110) if day else "A proper workstation, regular meals, one movement break"),
                      ("Evening", "10 to 15 minutes of a bhajan, the Hanuman Chalisa or another recitation between sunset and moonrise"),
                      ("Night", "A fixed bedtime; keep the night for rest")]
            rh = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rhythm)
            extra = (f'<div class="caps" style="color:{T.BERRY};margin:16px 0 8px">A daily rhythm for your {PLANET[r.PY]} year</div>'
                     f'<table class="t"><tr><th>When</th><th>What to do</th></tr>{rh}</table>')
        if not works:
            works = [f"The steady habits of your {PLANET[r.P]} birth number, kept on the right dates"]
        if not watch:
            watch = ["Nothing in your chart flags this area; keep the careful windows in mind"]
        q = ""
        if area in ("career", "money"):
            qs = self._quarters(area)
            q = (f'<div class="caps" style="color:{T.BERRY};margin:16px 0 8px">Quarter by quarter</div><table class="t"><tr><th>When</th><th>Focus</th><th>In practice</th></tr>'
                 + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in qs) + "</table>")
        inner = f"""
{self.head(kicker, title, sub=intro)}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
{self.panel(T.LBLUE, self.ptitle("What works for you", T.NAVY, 16) + plain(works, "small", "good"), pad="14px 16px")}
{self.panel(T.PINK, self.ptitle("What to watch", T.BERRY_D, 16) + plain(watch, "small", "care"), pad="14px 16px")}
</div>
<div class="caps" style="color:{T.BERRY};margin:16px 0 8px">Your {Y} actions</div>
{plain(actions, "small", "trait")}
{q}{extra}
"""
        self.pg.add(T.CREAM, inner)

    # ── timing ──
    def _mstyle(self, m):
        T = self.T
        st = m["state"]
        if st in ("fav", "fav_part"):
            return T.GREEN, T.WHITE
        if st in ("careful", "careful_part"):
            return T.ORANGE, T.INK
        if st == "mixed":
            return T.PINK, T.INK
        return T.WHITE, T.INK

    def timing_map(self):
        r, T, Y = self.r, self.T, self.Y
        strip = ""
        for m in r.months:
            bg, fg = self._mstyle(m)
            strip += (f'<div style="background:{bg};border-radius:12px;height:150px;padding:10px 4px;text-align:center;color:{fg};display:flex;flex-direction:column;justify-content:space-between">'
                      f'<div class="caps" style="font-size:10.5px">{m["short"]}</div><div class="num" style="font-size:40px">{m["pm"]}</div>'
                      f'<div class="tiny" style="font-weight:700;line-height:1.2">{m["tag"]}</div></div>')
        wl = [(w["pol"], f'<b>{w["label"]}</b>: {w["say"]}') for w in r.windows]
        inner = f"""
<div style="margin-top:6px">{self.L.plate("Your", 54, -5, T.BERRY)}</div>
<div style="margin:-8px 0 0 40px">{self.L.plate("timing map", 54, 3, T.BERRY)}</div>
<div class="lead" style="margin-top:28px;width:620px">Two kinds of timing run through your year. Your personal month number changes the theme each month. Your birth-number windows come from your rulebook for people born on a {r.P} day: the stretches for starting and investing, and the stretches for moving carefully.</div>
<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:26px">{strip}</div>
<div class="tiny" style="margin-top:8px;color:{T.DEEP}">The big number is your personal month. Green: favourable. Orange: move carefully. Pink: both overlap. White: steady.</div>
{self.panel(T.WHITE, self.ptitle("Your windows, as your rulebook gives them", T.NAVY, 17) + dots(wl, "small"), extra="margin-top:18px")}
{self.L.asterisk(T.NAVY, 70, 600, 64, 20)}
"""
        self.pg.add(T.PINK, inner)

    def stretches_page(self):
        r, T, Y = self.r, self.T, self.Y
        good, care = r.stretches("good"), r.stretches("care")
        blocks = ""
        if good:
            g = good[0]
            sup = [p for p in g["pms"] if p in r.support]
            txt = (f"{join_and([MONTHS[x - 1] for x in range(g['start'].month, g['end'].month + 1)])} "
                   f"{'carries' if g['start'].month == g['end'].month else 'carry'} personal month{'s' if len(g['pms']) > 1 else ''} {join_and(g['pms'])}"
                   + (f", {'one of your support numbers' if len(sup) == 1 else 'your support numbers'}," if sup else ",")
                   + f" inside your favourable window. The best time in {Y} to sign, start a venture, invest, ask for a promotion or make a public move. Prepare in the month before, act inside the window.")
            blocks += self.panel(T.GREEN, f'<div class="caps" style="color:{T.PINK};font-size:11px">Your strongest stretch</div><div class="disp" style="font-size:{40 if len(g["label"]) < 26 else 32}px;margin:6px 0 8px">{g["label"]}</div><div class="small">{txt}</div>', T.WHITE)
        if care:
            c = care[0]
            money = [MONTHS[x - 1] for x in range(c["start"].month, c["end"].month + 1) if reduce(r.PY + x) in (5, 8)]
            txt = ("It sits inside a careful window"
                   + (f", and {join_and(money)} {'is a' if len(money) == 1 else 'are'} money month{'s' if len(money) > 1 else ''} that will tempt you to close deals" if money else "")
                   + ". Do the research and make the calls; leave the signatures for later.")
            others = [x["label"] for x in care[1:3]]
            if others:
                txt += f" The same goes for {join_and(others)}."
            blocks += '<div style="height:12px"></div>' + self.panel(T.ORANGE, f'<div class="caps" style="color:{T.BERRY_D};font-size:11px">Your most protective stretch</div><div class="disp" style="font-size:{40 if len(c["label"]) < 26 else 32}px;margin:6px 0 8px;color:{T.DEEP}">{c["label"]}</div><div class="small">{txt}</div>')
        cols = [T.PINK, T.ORANGE, T.LBLUE]
        sd = r.support_dates()
        tiles = "".join(f'<div style="background:{cols[r.support.index(red) % 3]};border-radius:12px;padding:12px 0;text-align:center"><div class="num" style="font-size:40px;color:{T.NAVY}">{d}</div>'
                        f'<div class="tiny" style="color:{T.DEEP};font-weight:700">reduces to {red}</div></div>' for d, red in sd)
        best = r.best_dates()
        btxt = (" Inside your favourable window the best are " + join_and([f"<b>{join_and(map(str, ds))} {mn}</b>" for mn, ds in best[:2]]) + ".") if best else ""
        inner = f"""
{self.head("Use and protect", "Your best and<br>most careful stretches")}
{blocks}
<div class="caps" style="color:{T.BERRY};margin:22px 0 10px">Your support dates, every month</div>
<div style="display:grid;grid-template-columns:repeat({min(len(sd), 7)},1fr);gap:8px">{tiles}</div>
<div class="small" style="margin-top:12px">Dates that reduce to {join_and(r.support)} carry your support numbers. Use them for calls, meetings, applications and payments.{btxt}</div>
"""
        self.pg.add(T.LBLUE, inner)

    def month_text(self, m):
        r, Y = self.r, self.Y
        d = m["pm"]
        if d == r.P:
            s1 = "Your own number returns."
        elif d == r.D:
            s1 = "Your destiny number leads the month."
        elif d in r.support:
            s1 = f"{d} is a support number, so this month works in your favour."
        elif d in r.missing:
            s1 = f"{d} is missing from your Lo Shu grid, so this month asks for effort rather than ease."
        else:
            rel = r.rel(r.P, d)
            s1 = {"friend": f"{Pl(d)} is friendly to your {r.P}.", "enemy": f"{Pl(d)} and your {r.P} do not get along, so expect some friction.",
                  "neutral": f"A neutral month for your {r.P}.", "mixed": f"{Pl(d)} both helps and tests your {r.P}."}.get(rel, "")
        s2 = PM[d][1]
        st = m["state"]
        if st == "fav":
            s3 = "Your favourable window runs all month: sign, invest or launch."
        elif st == "fav_part":
            s3 = f"Your favourable window: {m['tag'].replace('best', 'open').replace('open to', 'open until')}. Line up what you prepared."
        elif st == "careful":
            s3 = "A careful window all month: research and prepare, and keep signatures and big decisions for later."
        elif st == "careful_part":
            s3 = f"The careful window: {m['tag'].replace('careful', 'in force')}. Keep signatures out of it."
        elif st == "mixed":
            s3 = "Favourable and careful days overlap: decide on the favourable dates, and double-check everything."
        else:
            s3 = ""
        if m["m"] == r.dob["m"]:
            s3 += f" Your birthday on the {ordinal(r.dob['d'])} begins a new year of your life."
        return " ".join(x for x in (s1, s2, s3) if x)

    def month_dates(self, m):
        r = self.r
        sd = [dd for dd, _ in r.support_dates() if dd <= m["days"]]
        if m["state"] == "careful":
            return "for calls and preparation only"
        if m["good"]:
            inside = [dd for dd in sd if dd in m["good"]]
            if inside:
                return ", ".join(map(str, inside)) + " (inside your window)"
        if m["care"]:
            out = [dd for dd in sd if dd not in m["care"]]
            return ", ".join(map(str, out)) + " (outside the careful days)" if out else "for calls and preparation only"
        return ", ".join(map(str, sd))

    def month_pages(self):
        r, T, Y = self.r, self.T, self.Y
        tag_col = lambda bg: T.PINK if bg == T.GREEN else T.BERRY_D
        stretch = []
        for a, z in [(1, 4), (5, 8), (9, 12)]:
            ms = r.months[a - 1:z]
            fav = [m["name"] for m in ms if m["state"] in ("fav", "fav_part")]
            car = [m["name"] for m in ms if m["state"] in ("careful", "careful_part")]
            if fav and car:
                s = f"Move carefully in {join_and(car)}, and act in {join_and(fav)}, when your favourable window opens."
            elif fav:
                s = f"Your favourable window falls in {join_and(fav)}: line everything up for it."
            elif car:
                s = f"A stretch to prepare in: {join_and(car)} {'is' if len(car) == 1 else 'are'} careful, so research and agree in principle, and keep signatures for later."
            else:
                s = f"{'Four' if len(ms) == 4 else 'Steady'} steady months. Build the routine and finish what is pending."
            stretch.append(s)
        marks = [lambda: self.L.petal_flower(T.PINK, 56, 610, 62, hole=T.CREAM), lambda: self.L.sparkle(T.PINK, 46, 616, 64), lambda: self.L.asterisk(T.BERRY, 56, 612, 62, 10)]
        for i, (a, z) in enumerate([(1, 4), (5, 8), (9, 12)]):
            tiles = ""
            for m in r.months[a - 1:z]:
                bg, fg = self._mstyle(m)
                title = PM[m["pm"]][0]
                tiles += (f'<div class="tile" style="background:{bg};color:{fg};padding:18px 22px">'
                          f'<div style="display:flex;justify-content:space-between;align-items:flex-start"><div><div class="disp b" style="font-size:27px">{m["name"]}</div>'
                          f'<div class="caps" style="font-size:10.5px;color:{tag_col(bg)};margin-top:4px">{m["tag"]} &#183; month {m["pm"]}, {PLANET[m["pm"]]}</div></div>'
                          f'<div class="num" style="font-size:54px">{m["pm"]}</div></div>'
                          f'<div class="body" style="margin-top:8px"><b>{title}.</b> {self.month_text(m)}</div>'
                          f'<div class="small" style="margin-top:10px;font-weight:700">Support dates: {self.month_dates(m)}</div></div>')
            sub = f"{MONTHS[a - 1]} to {MONTHS[z - 1]}"
            inner = (self.head(f"{Y}, month by month", sub, [T.BERRY, T.NAVY, T.GREEN][i])
                     + f'<div style="display:flex;flex-direction:column;gap:12px">{tiles}</div>'
                     + self.panel(T.NAVY, f'<div class="caps" style="color:{T.PINK};font-size:11px">This stretch in one line</div><div class="body" style="margin-top:6px;color:#E7ECF7">{stretch[i]}</div>', T.WHITE, extra="margin-top:14px")
                     + marks[i]())
            self.pg.add(T.CREAM, inner)

    # ── practices ──
    def practices(self):
        r, T, Y = self.r, self.T, self.Y
        do = r.py_lines(["do"])
        rem = r.py_lines(["remedy", "crystal"])
        ev = r.everyone()
        day = [first_sentence(t, 90) for t in do[:2]] + [first_sentence(x, 90) for x in r.everyone("Wake early")[:1]]
        week = r.everyone("Tuesdays")[:1] + r.everyone("blessings")[:1]
        evening = ["10 to 15 minutes of a bhajan or the Hanuman Chalisa between sunset and moonrise"] + [first_sentence(x, 80) for x in r.everyone("Listen to others")[:1]]
        once = [first_sentence(t, 100) for t in (rem[:1] + r.py_lines(["money"])[:1])] or [first_sentence(t, 100) for t in do[2:4]]
        groups = [("Every day", day, T.PINK), ("Every week", week, T.LBLUE), ("Every evening", evening, T.WHITE), ("Once this year", once, T.ORANGE)]
        gh = "".join(self.panel(bg, self.ptitle(t, T.NAVY, 17) + plain(items, "small", "good"), pad="14px 16px") for t, items, bg in groups if items)
        colours = r.py_lines(["colours"])
        lucky = [t for p, t in r.num_items("psychic") if "lucky" in t.lower()]
        colour_txt = (clean(colours[0]).rstrip(".") + f" (your Personal Year {r.PY} colours)." if colours else "")
        if lucky:
            colour_txt += " " + lucky[0]
        rem_r = r.d.get("remedy") or {}
        screen = rem_r.get("screen_saver")
        if rem_r.get("screen_saver_from") == "destiny" and r.d.get("remedyDestiny"):
            screen = r.d["remedyDestiny"].get("screen_saver") + " Or: " + rem_r.get("screen_saver", "")
        work = r.everyone("well-lit")
        rows = []
        if colour_txt:
            rows.append(("Colours", colour_txt))
        if screen:
            rows.append(("Phone screen", screen))
        if work:
            rows.append(("Workplace", work[0]))
        rh = "".join(f'<div class="small"><b style="color:{T.NAVY}">{a}:</b> {b}</div>' for a, b in rows)
        inner = f"""
{self.head("Chapter 9 &#183; Practices", "Small, steady,<br>all year", T.GREEN, sub="Your rulebook is clear that regular practice matters more than paperwork. Choose a few and keep them.")}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">{gh}</div>
<div class="ruled" style="margin-top:18px">{rh}</div>
"""
        self.pg.add(T.CREAM, inner)
        self._tracker_items = (day[:1] or ["Routine"])

    def bracelet(self):
        r, T = self.r, self.T
        b = r.d.get("bracelet")
        if not b:
            return False
        import os
        from .themes import ASSETS
        pic = self.L.product(b["sku"], 580, 580, 70, 300)
        if pic:
            link = f"https://www.veshannastro.co.in/shop-product.html?sku={b['sku']}"
        else:
            pic = self._bead_ring(b)
            link = LINKS["shop"]
        why = {1: "confidence, stamina and courage", 2: "emotional steadiness and intuition", 3: "clarity, optimism and growth",
               4: "focus, protection and grounded confidence", 5: "growth, luck and clear thinking", 6: "balance, harmony and love",
               7: "balance across body and mind", 8: "calm thinking, sleep balance and focus", 9: "strength, courage and grounded energy"}[r.P]
        inner = f"""
{pic}
{self.L.asterisk(T.PINK, 64, 600, 290, 12)}
{self.L.sparkle(T.WHITE, 44, 70, 860)}
<div class="caps" style="color:{T.PINK}">For birth number {r.P}</div>
<h2 class="disp t2" style="margin-top:14px">{b["gemstones"]}</h2>
<div class="lead" style="margin-top:12px;width:600px;color:#EAF3EC">The bracelet for birth number {r.P}, chosen for {why}: the {b["name"]} from the Veshannastro range.</div>
<div class="abs" style="left:50px;right:50px;top:930px">
<div class="disp" style="font-size:25px;color:#fff;margin-bottom:6px">How to wear it</div>
<div class="body" style="color:#EAF3EC;margin-bottom:18px">On the wrist that does not carry your watch, every day, through the whole year.</div>
{action_bar("View the bracelet", f"{b['name']} in the Veshannastro range", link)}</div>
"""
        self.pg.add(T.GREEN, inner)
        return True

    def _bead_ring(self, b):
        import math
        T = self.T
        cols = ["#F4F1EC", "#E9D8F2", "#F6C9D8", "#CFE3F2", "#EEDDC6"]
        beads = ""
        for i in range(22):
            a = 2 * math.pi * i / 22
            cx, cy = 290 + 200 * math.cos(a), 290 + 200 * math.sin(a)
            beads += (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="34" fill="{cols[i % len(cols)]}"/>'
                      f'<circle cx="{cx - 10:.0f}" cy="{cy - 12:.0f}" r="9" fill="#fff" opacity=".7"/>')
        return (f'<svg class="abs" style="left:70px;top:300px" width="580" height="580" viewBox="0 0 580 580">'
                f'<circle cx="290" cy="290" r="200" fill="none" stroke="{T.DEEP}" stroke-width="3" opacity=".25"/>{beads}</svg>')

    def tracker(self):
        r, T, Y = self.r, self.T, self.Y
        rows = "".join(f'<tr><td style="height:52px">{m}</td><td></td><td></td><td></td><td></td></tr>' for m in MONTHS)
        inner = f"""
{self.head("One page, twelve months", "Your practice<br>tracker", sub="Tick what you kept at the end of each month and write one thing that changed. Remedies show over months, not days.")}
<table class="t"><tr><th>Month</th><th>Routine</th><th>Weekly</th><th>Evening</th><th>One thing that changed</th></tr>{rows}</table>
<div class="small" style="margin-top:14px"><b>If twelve feels like too many, keep three:</b> a fixed bedtime, one daily practice from the last page, and the evening recitation.</div>
"""
        self.pg.add(T.CREAM, inner)

    # ── watch ──
    def watch_page(self):
        r, T, Y = self.r, self.T, self.Y
        w = r.d.get("watch") or {}
        acc = w.get("accessories") or []
        accessory = clean(acc[0]) if acc else ""
        # the T01 accessory line for PY1 carries the general watch idea; keep only its first sentence as the pick
        pick = first_sentence(accessory, 140) if accessory else "A watch you wear every day"
        dial_col = {"white": "#F4F4F2", "blue": T.COBALT, "green": T.GREEN, "gold": "#D8B45A", "silver": "#C9CED6"}
        dials = w.get("dials") or []
        face = dial_col.get(dials[-1]["colour"], T.COBALT) if dials else ("#D8B45A" if "gold" in pick.lower() else T.COBALT)
        case = "#D8B45A" if "gold" in pick.lower() and "silver" not in pick.lower() else ("#C9CED6" if "silver" in pick.lower() or "steel" in pick.lower() or "metal" in pick.lower() else "#D7DCE6")
        svg = f"""<svg class="abs" style="left:430px;top:110px" width="240" height="340" viewBox="0 0 240 340">
<rect x="78" y="0" width="84" height="100" rx="14" fill="{T.NAVY}"/><rect x="78" y="240" width="84" height="100" rx="14" fill="{T.NAVY}"/>
<circle cx="120" cy="170" r="98" fill="{case}"/><circle cx="120" cy="170" r="84" fill="{face}"/>
<line x1="120" y1="170" x2="120" y2="112" stroke="{T.NAVY if face in ("#F4F4F2", "#D8B45A", "#C9CED6") else "#fff"}" stroke-width="7" stroke-linecap="round"/>
<line x1="120" y1="170" x2="160" y2="190" stroke="{T.NAVY if face in ("#F4F4F2", "#D8B45A", "#C9CED6") else "#fff"}" stroke-width="5" stroke-linecap="round"/>
<circle cx="120" cy="170" r="8" fill="{T.NAVY if face in ("#F4F4F2", "#D8B45A", "#C9CED6") else "#fff"}"/><rect x="214" y="160" width="14" height="22" rx="4" fill="{case}"/></svg>"""
        rules = [("good", f"{d['colour'].capitalize()} dial: {first_sentence(d['say'], 130)}") for d in dials]
        wr = w.get("wrist") or {}
        if wr.get("left"):
            rules.append(("neutral", "Left wrist: " + first_sentence(wr["left"], 120)))
        if wr.get("right"):
            rules.append(("neutral", "Right wrist: " + first_sentence(wr["right"], 120)))
        g = [x["say"] for x in w.get("goals", []) if "3 to 6 months" in x["say"]]
        inner = f"""
{svg}
{self.L.blob(T.PINK, 290, 160, 175, 1130, "bumps")}
<div style="margin-top:20px">{self.L.plate("Your watch", 50, -5, T.COBALT, width=370)}</div>
<div style="margin:-8px 0 0 30px">{self.L.plate(f"in {Y}", 50, 3, T.COBALT, width=370)}</div>
<div class="lead" style="margin-top:250px;width:620px;color:#E7ECF7">A watch is a reminder of timing and decisions: choosing the right time to act is what makes an action lucky. Its dial, metal, numerals, date window, strap and even the wrist you wear it on carry a meaning, and the right watch changes with your personal year.</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px">
{self.panel(T.WHITE, self.ptitle(f"The watch for your {Y}", T.NAVY, 17) + f'<div class="small"><b>{pick}</b> Your rulebook names this watch for every Personal Year {r.PY}.</div>')}
{self.panel(T.LBLUE, self.ptitle("Which wrist", T.NAVY, 17) + '<div class="small">Choose by the relationships you want to ease this year: the left wrist for the women in your life, the right for the men.' + (" " + first_sentence(g[0], 100) if g else "") + '</div>')}
</div>
{self.panel("rgba(255,255,255,.1)", self.ptitle("A few of the rules a watch reading uses", T.PINK, 16) + dots(rules, "small"), T.WHITE, extra="margin-top:12px")}
"""
        self.pg.add(T.COBALT, inner)

    def watch_offer(self):
        r, T, Y = self.r, self.T, self.Y
        acc = (r.d.get("watch") or {}).get("accessories") or []
        pick = first_sentence(clean(acc[0]), 120).rstrip(".").lower() if acc else "the right watch"
        inner = f"""
{self.L.blob(T.LBLUE, 520, 420, 100, 60, "cloud")}
<div class="abs onblob" style="left:150px;top:220px">{self.L.plate("Your watch,", 54, -5, T.NAVY)}</div>
<div class="abs onblob" style="left:200px;top:314px">{self.L.plate("read", 54, 3, T.NAVY)}</div>
<div style="margin-top:520px">
<div class="disp t4" style="color:{T.NAVY}">Wristwatch Consultation</div>
<div class="body" style="margin-top:14px;width:610px">The watch you wear every day either supports {Y} or quietly works against it. Your rulebook's pick for the year is {pick}, but your current watch has its own story: its shape, numerals, date window and strap all count, and so does who gave it to you.</div>
<div class="rule" style="margin:18px 0;background:{T.NAVY}"></div>
{plain([f"Your own watch read from one clear photo, against your {r.P}-{r.D} chart", f"What it says about how you come across, and what it is doing to your {Y}",
        "Keep it, adjust it (strap or wrist) or change it, with the exact watch to choose", "When to switch, and what to expect"], "small")}
<div style="margin-top:20px">{action_bar("Send your watch photo", "on WhatsApp, and book the Wristwatch Consultation", self.WA["watch"])}</div>
</div>
{self.L.heart(T.BERRY, 46, 616, 1040)}
"""
        self.pg.add(T.PINK, inner)

    # ── mobile number ──
    def mobile_pages(self):
        r, T, Y = self.r, self.T, self.Y
        m = self.mob
        if not m:
            return False
        num = m["number"]
        pretty = f"+91 {num[:5]} {num[5:]}"
        cnt = {int(k): v for k, v in m["counts"].items()}
        cols = [T.COBALT, T.BERRY, T.GREEN, T.ORANGE, T.NAVY]
        cells = ""
        for row in VGRID:
            for d in row:
                n = cnt.get(d, 0)
                if n:
                    fs = 46 if n <= 2 else (38 if n == 3 else 28)
                    cells += (f'<div style="background:{cols[d % 5]};border-radius:12px;height:112px;position:relative;color:#fff">'
                              f'<span class="caps" style="position:absolute;left:10px;top:8px;font-size:9.5px;opacity:.85">{d}</span>'
                              f'<div class="num" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:{fs}px">{str(d) * n}</div></div>')
                else:
                    cells += (f'<div style="border:2px dashed rgba(57,75,113,.35);border-radius:12px;height:112px;position:relative;color:{T.NAVY}">'
                              f'<span class="caps" style="position:absolute;left:10px;top:8px;font-size:9.5px;opacity:.7">{d}</span></div>')
        by = {}
        for d in range(1, 10):
            if cnt.get(d):
                by.setdefault(cnt[d], []).append(d)
        on_grid = "; ".join(f"{join_and(ds)} {({1: 'once', 2: 'twice', 3: 'three times'}).get(k, str(k) + ' times')}{' each' if len(ds) > 1 and k > 1 else ''}" for k, ds in sorted(by.items(), reverse=True)) + "."
        adds = [d for d in r.missing if cnt.get(d)]
        still = [d for d in r.missing if not cnt.get(d)]
        sup_in = [d for d in r.support if cnt.get(d)]
        adds_txt = (f"<b>{join_and(adds)}</b>" + (f", {'one of your support numbers' if len([x for x in adds if x in r.support]) == 1 else 'including your support numbers'}" if any(x in r.support for x in adds) else "") + "." if adds else "Nothing new: every digit in it is already on your Lo Shu grid.")
        still_txt = (f"<b>{join_and(still)}</b>." + (f" Your support number{'s' if len([x for x in still if x in r.support]) > 1 else ''} {join_and([x for x in still if x in r.support])} {'is' if len([x for x in still if x in r.support]) == 1 else 'are'} not in it." if any(x in r.support for x in still) else "") if still else "None: together they fill your grid.")
        cl = m.get("clarity") or {}
        change = cl.get("change", True)
        verdict = (f"Change this number for the work that matters in {Y}" if change else f"Keep this number: it mostly supports your {Y}")
        why = clean(cl.get("why") or "").replace("what you shared", m["concern"])
        why = f"Read against what your {Y} is about. " + why
        page1 = f"""
{self.L.petal_flower(T.PINK, 64, 606, 60, hole=T.CREAM)}
<span class="kick pk">Included free with your forecast</span>
<h2 class="disp t3" style="color:{T.NAVY};margin-top:14px">Your mobile<br>number, read</h2>
<div class="accent" style="margin-top:16px"></div>
<div class="disp" style="font-size:52px;color:{T.BERRY};margin-top:22px;letter-spacing:.01em">{pretty}</div>
<div class="small" style="margin-top:6px">Your number, read with the same rulebook as the rest of this forecast. Zeros are skipped.</div>
<div style="display:flex;gap:22px;margin-top:22px;align-items:flex-start">
<div style="display:grid;grid-template-columns:repeat(3,112px);gap:10px">{cells}</div>
<div style="flex:1">
<div class="caps" style="color:{T.BERRY};font-size:11px">On the number's grid</div>
<div class="body" style="margin-top:6px">{on_grid}</div>
<div class="caps" style="color:{T.GREEN};font-size:11px;margin-top:14px">What it adds to your Lo Shu grid</div>
<div class="body" style="margin-top:6px">{adds_txt}</div>
<div class="caps" style="color:{T.ORANGE};font-size:11px;margin-top:14px">Still missing</div>
<div class="body" style="margin-top:6px">{still_txt}</div>
</div></div>
{self.panel(T.NAVY, f'<div class="caps" style="color:{T.PINK};font-size:11px">Our verdict</div><div class="disp" style="font-size:32px;margin:8px 0 12px;line-height:1.05">{verdict}</div><div class="body" style="color:#E7ECF7">{why}</div>', T.WHITE, extra="margin-top:22px")}
"""
        self.pg.add(T.CREAM, page1)

        def mrow(title, good, care, count=None):
            c = f' <span class="tiny" style="opacity:.75">&#215;{count}</span>' if count and count > 1 else ""
            g = f'<div class="small"><b style="color:{T.GREEN}">Helps:</b> {good}</div>' if good else ""
            k = f'<div class="small"><b style="color:{T.CARE}">Care:</b> {care}</div>' if care else ""
            return (f'<div style="display:flex;gap:14px;padding:9px 0;border-bottom:1.5px solid {T.PINK}">'
                    f'<span class="disp b" style="font-size:17px;color:{T.NAVY};width:150px;flex:0 0 150px">{title}{c}</span><div style="flex:1">{g}{k}</div></div>')
        rank = {"negative": 0, "mixed": 1, "positive": 2, "neutral": 3}
        plist = sorted(m["pairs"], key=lambda p: (rank.get(p["polarity"], 3), -p["count"]))
        ylist = sorted(m["yogas"], key=lambda y: rank.get(y["polarity"], 3))
        cap_p = 8 if len(ylist) <= 4 else 6
        cap_y = max(0, 13 - min(len(plist), cap_p))
        cap_y = min(cap_y, 6)
        more = max(0, len(plist) - cap_p) + max(0, len(ylist) - cap_y)
        plist, ylist = plist[:cap_p], ylist[:cap_y]
        pairs = "".join(mrow(p["pair"][0] + "-" + p["pair"][1], soft(p["good"] or "", p["areas"]) or None, soft(p["care"] or "", p["areas"]) or None, p["count"]) for p in plist)
        yogas = "".join(mrow(y["title"].replace(" (Intelligent Yoga)", "").replace("Mars Mercury", "Intelligent Yoga") if "Intelligent" in y["title"] else y["title"],
                             soft(y["good"] or "", y["areas"]) or None, soft(y["care"] or "", y["areas"]) or None) for y in ylist)
        nf = (cl.get("notFor") or {}).get("othersText") or ""
        prot = m.get("protection") or {}
        prot_txt = []
        if prot.get("bracelet"):
            prot_txt.append(f"wear the {prot['bracelet']}")
        if prot.get("mani"):
            prot_txt.append(f"keep {prot['mani']}")
        prot_line = ("Until you change it: set the phone screen saver from your practices page" + (", " + join_and(prot_txt) if prot_txt else "") + ".")
        panels = []
        if nf:
            panels.append(self.panel(T.PINK, self.ptitle("Not suitable for", T.BERRY_D, 16) + f'<div class="small">{nf}</div>', pad="14px 16px"))
        panels.append(self.panel(T.LBLUE, self.ptitle("Your protection", T.NAVY, 16) + f'<div class="small">{prot_line}</div>', pad="14px 16px"))
        yblock = (f'<div class="caps" style="color:{T.NAVY};margin:18px 0 4px">Yogas on the number\'s grid</div><div style="border-top:1.5px solid {T.PINK}">{yogas}</div>' if yogas else "")
        if more:
            yblock += f'<div class="tiny" style="margin-top:8px">{more} more {"patterns sit" if more > 1 else "pattern sits"} on your number; the consultation goes through every one.</div>'
        page2 = f"""
{self.head("Pair by pair", "What your number<br>is doing", T.BERRY)}
<div class="caps" style="color:{T.NAVY};margin-bottom:4px">Digit pairs side by side</div>
<div style="border-top:1.5px solid {T.PINK}">{pairs}</div>
{yblock}
<div style="display:grid;grid-template-columns:{"1fr 1fr" if len(panels) == 2 else "1fr"};gap:10px;margin-top:16px">{"".join(panels)}</div>
"""
        self.pg.add(T.CREAM, page2)

        b = m.get("better") or {}
        steps = {s.get("id"): s for s in (cl.get("steps") or [])}
        ch = steps.get("change") or {}
        avoid = ch.get("avoid") or [a["title"] for a in (b.get("avoid") or [])][:3]
        look = ch.get("lookFor") or []
        good_pairs = [p["pair"][0] + "-" + p["pair"][1] for p in m["pairs"] if p["polarity"] == "positive"]
        good_yogas = [y["title"] for y in m["yogas"] if y["polarity"] == "positive"]
        keep = good_pairs[:1] + good_yogas[:1]
        a1 = ("Keeps " + join_and(keep) + (" and drops " + join_and(avoid[:3]) if avoid else "") + "." if keep else
              ("Drops " + join_and(avoid[:3]) + "." if avoid else "Chosen to suit your birth date and your year."))
        a2 = (join_and(look) + ": the patterns your rulebook favours for your chart." if look else f"Patterns that bring in your missing {join_and(still) if still else 'numbers'} and your support numbers.")
        good = r.stretches("good")
        timing = (f"When to switch, so the change lands in a supportive window ({good[0]['label']}), not a careful one." if good else "When to switch, so the change lands on a supportive date.")
        cards = [("A number chosen for you", a1, T.WHITE), ("The patterns to look for", a2, T.LBLUE),
                 ("A switch plan", "Which accounts move first: bank and UPI, loans, investments, tax, property papers. And which can stay.", T.PINK),
                 (f"Your {Y} timing", timing, T.ORANGE)]
        ch_html = "".join(self.panel(bg, self.ptitle(t, T.NAVY, 17) + f'<div class="small">{d}</div>') for t, d, bg in cards)
        lead = (f"The last two pages are the free part: your number, read pair by pair against your date of birth. What they cannot give you on their own is the number to switch to. That is what the consultation is for."
                if change else
                f"The last two pages are the free part, and your number comes out well. A consultation still checks it against {Y} and tells you whether to keep it as it is or tune how you use it.")
        urgent = (f"Every loan, bank and property paper you sign in {Y} will carry the number you give it. Switch before the paperwork of the year begins, so the new number is the one on every document."
                  if change else f"If you are opening accounts or signing papers in {Y}, a quick check now saves changing numbers later.")
        page3 = f"""
{self.L.blob(T.PINK, 300, 300, 400, 70, "flower")}
{self.L.icon("phone", T.WHITE, 120, 1.4, 490, 160)}
<div style="margin-top:20px">{self.L.plate("From your number", 46, -5, T.COBALT, width=360)}</div>
<div style="margin:-8px 0 0 30px">{self.L.plate("to the right one" if change else "to the best use", 46, 3, T.COBALT, width=360)}</div>
<div class="lead" style="margin-top:190px;width:610px;color:#E7ECF7">{lead}</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:22px">{ch_html}</div>
<div class="caps" style="color:{T.PINK};margin-top:26px">Online, one to one</div>
<div class="disp t5" style="margin-top:6px">Mobile Number Correction Consultation</div>
<div class="small" style="margin-top:8px;color:#E7ECF7;width:610px">{urgent}</div>
<div style="margin-top:18px">{action_bar("Book on WhatsApp", "Mobile Number Correction Consultation, online", self.WA["mobile"])}</div>
"""
        self.pg.add(T.COBALT, page3)
        return True

    # ── close ──
    def further(self):
        r, T, Y = self.r, self.T, self.Y
        v = r.name_verdict()
        name_w = {"weak": "Your name is working below its strength; a corrected spelling lines it up with your birth numbers.",
                  "mixed": "Your name helps in some places and holds you back in others; a small correction keeps the help.",
                  "strong": "Your name already supports you; check that the version you sign with carries the same strength."}[v]
        if self.mob:
            ch = (self.mob.get("clarity") or {}).get("change", True)
            mob = ("mobile", "Mobile Number Correction Consultation",
                   ("Your number works against what " + str(Y) + " is about, and a new one can remove that." if ch else "Your number mostly supports you; a consultation tunes how you use it."),
                   self.WA["mobile"], "Book on WhatsApp")
        else:
            mob = ("mobile", "Mobile Number Correction Consultation", "Send us your number: we read it free against your birth date, then choose the right one with you.", self.WA["mobile_new"], "Book on WhatsApp")
        acc = (r.d.get("watch") or {}).get("accessories") or []
        watch_w = (f"Your year asks for {first_sentence(clean(acc[0]), 80).rstrip('.').lower()}; your current one may say something else." if acc else "Your watch either supports the year or works against it; one photo tells us which.")
        cons_w = []
        if r.M:
            cons_w.append(f"master {r.M}")
        if r.rel(r.P, r.D) in ("enemy", "mixed"):
            cons_w.append("a pair that pulls two ways")
        if len(r.missing) >= 3:
            cons_w.append(f"{len(r.missing)} missing numbers")
        cons = (join_and(cons_w).capitalize() + " are a lot to hold. Talk it through, live." if cons_w else "Bring your questions about the year and talk them through, live.")
        cards = [("Name Correction Consultation", name_w, self.WA["name"], "Book on WhatsApp", T.PINK, T.INK),
                 (mob[1], mob[2], mob[3], mob[4], T.LBLUE, T.INK),
                 ("Wristwatch Consultation", watch_w, self.WA["watch"], "Send a photo", T.ORANGE, T.INK),
                 ("Vedic Kundli Consultation", "No birth time or place was used here. Your birth chart and dasha can confirm the dates for big decisions.", LINKS["kundli"], "Book", T.NAVY, T.WHITE),
                 ("Numerology Consultation", cons, LINKS["numcons"], "Book", T.BERRY, T.WHITE),
                 ("Numerology Compatibility", "See how your numbers and your partner's meet, side by side.", LINKS["compat"], "Book", T.GREEN, T.WHITE)]
        ch = "".join(f'<a href="{h}" class="tile" style="background:{bg};color:{fg};display:flex;flex-direction:column;justify-content:space-between;min-height:196px">'
                     f'<div><div class="caps" style="font-size:10px;opacity:.8">{i + 1:02d}</div><div class="disp b" style="font-size:21px;margin:6px 0 8px;line-height:1.05">{t}</div>'
                     f'<div class="small">{w}</div></div><div class="caps" style="font-size:11px;margin-top:12px;text-decoration:underline;text-underline-offset:3px">{c} &#8594;</div></a>'
                     for i, (t, w, h, c, bg, fg) in enumerate(cards))
        inner = f"""
{self.head("Chapter 11 &#183; Going further", "When you are<br>ready for more", sub="This forecast reads your year from your date of birth and name. Some questions need more. These are the steps that matter most for your chart, in order. Tap any card to book or ask.")}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">{ch}</div>
<div class="small" style="margin-top:16px">Not sure where to start? Start with number 1, or <a href="{self.WA['talk']}" style="color:{T.COBALT};text-decoration:underline">message us on WhatsApp</a> and we will point you to the right one.</div>
"""
        self.pg.add(T.CREAM, inner)

    def one_page(self):
        r, T, Y = self.r, self.T, self.Y
        good, care = r.stretches("good"), r.stretches("care")
        acc = (r.d.get("watch") or {}).get("accessories") or []
        colours = r.py_lines(["colours"])
        fix = []
        if r.name_verdict() != "strong":
            fix.append("your name")
        if self.mob and (self.mob.get("clarity") or {}).get("change"):
            fix.append("your mobile number")
        b = r.d.get("bracelet") or {}
        rows = [("The year", f"Personal Year {r.PY}, {pl(r.PY)}. {r.frame['tag']}"),
                ("Your edge", f"A {PLANET[r.P]} {r.P} and a {PLANET[r.D]} {r.D}" + (f", with master {r.M}." if r.M else ".")),
                ("Support numbers", f"{join_and(r.support)}, in dates, names and numbers."),
                ("Best window", (good[0]["label"] + "." if good else "Your support dates.")),
                ("Protect", (join_and([c["label"] for c in care[:3]]) + "." if care else "No careful stretch this year.")),
                ("Money", first_sentence((r.py_lines(["money"]) or ["Plan early, sign inside your best window."])[0], 90)),
                ("People", first_sentence((r.py_lines(["relationship"]) or r.everyone("Listen to others") or ["Listen, speak kindly, keep your word."])[0], 90)),
                ("Mind and body", first_sentence((r.py_lines(["health"]) or r.everyone("Tuesdays"))[0], 90)),
                ("Wear", " ".join(x for x in [first_sentence(colours[0], 60) if colours else "", first_sentence(clean(acc[0]), 70) if acc else "", (b.get("gemstones", "") + ".") if b else ""] if x)),
                ("Fix first", (join_and(fix).capitalize() + "." if fix else "Nothing big: keep the timing and the practices."))]
        oneh = "".join(f'<div style="display:flex;gap:16px;padding:8px 0"><span class="disp b" style="font-size:20px;color:{T.BERRY};width:180px">{a}</span><span class="lead" style="flex:1">{b_}</span></div>' for a, b_ in rows)
        inner = f"""
{self.head("Keep this where you will see it", f"Your {Y}<br>on one page")}
<div class="ruled">{oneh}</div>
<div class="it" style="font-size:28px;color:{T.BERRY};margin-top:40px;text-align:center;padding:0 30px">Choosing the right time to act is what makes an action lucky.</div>
{self.L.petal_flower(T.PINK, 60, 610, 62, hole=T.CREAM)}
{self.L.blob(T.LBLUE, 260, 150, 195, 1135, "bumps")}
"""
        self.pg.add(T.CREAM, inner)

    def thanks(self):
        r, T = self.r, self.T
        contacts = [("WhatsApp", WA_NUM, LINKS["wa"]), ("Website", SITE, LINKS["site"]), ("Email", MAIL, LINKS["mail"])]
        ch = "".join(f'<a href="{h}" style="display:block;padding:18px 0;border-bottom:1.5px solid rgba(255,255,255,.5)"><div class="caps" style="font-size:10.5px;color:{T.PINK}">{a}</div>'
                     f'<div class="disp" style="font-size:30px;margin-top:6px">{b}</div></a>' for a, b, h in contacts)
        first = esc(r.first)
        inner = f"""
{self.L.blob(T.PINK, 290, 170, 175, 1110, "bumps")}
<div style="margin-top:90px">{self.L.plate("Thank you,", 64, -5, T.COBALT)}</div>
<div style="margin:-6px 0 0 50px">{self.L.plate(first + "!", self.L.fit(first + "!", 64, 560), 3, T.COBALT)}</div>
<div class="lead" style="margin-top:56px;width:600px;color:#E7ECF7;font-size:19px">Thank you for trusting us with your numbers. Keep the timing map close, keep a few practices going, and come back to these pages when the year asks a question.</div>
<div style="margin-top:36px;border-top:1.5px solid rgba(255,255,255,.5)">{ch}</div>
<div class="small" style="margin-top:44px;color:#C9D3EA;width:600px">About this reading: it follows Veshannastro's Vedic numerology method and the rulebook built from the sources our practice uses. It reads tendencies and timing and does not guarantee outcomes. For medical, legal or financial decisions, consult a qualified professional.<br><br>Prepared for {esc(r.name_full)}, born {r.dob_text}.</div>
{self.L.sparkle(T.PINK, 56, 600, 70)}
"""
        self.pg.add(T.COBALT, inner)


WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
