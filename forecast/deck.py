"""The Personal Year Forecast as a 9:16 deck, for any date of birth, name and (optionally) mobile number.

build_html(data) -> (html, meta). `data` is data.mjs output. Every page reads from forecast.content.Reading,
so the same chart always produces the same pages, and nothing on a page is written for one customer only.
"""
import re

from .content import (MONTHS, PLANET, PM, PLANE_MEAN, BRING, REL_WORD, TIMES, Reading, clean, join_and, ordinal,
                      reduce, soft, first_sentence)
from .content import pl, Pl
from .looks import look_for
from .kit import (Pages, action_bar, asset, asterisk, blob, esc, heart, icon, petal_flower, photo, plate, ring,
                  scallop, sparkle, theme_ns, wa)
from .themes import theme_for

WA_NUM, SITE, MAIL = "+91 76469 52745", "veshannastro.co.in", "assist@veshannastro.co.in"
LINKS = {
    "compat": "https://rzp.io/rzp/GehUWdel",
    "numcons": "https://www.veshannastro.co.in/numerology-booking.html",
    "kundli": "https://www.veshannastro.co.in/vedic-kundli-booking.html",
    "site": "https://www.veshannastro.co.in",
    "wa": "https://wa.me/917646952745",
    "mail": "mailto:assist@veshannastro.co.in",
    "shop": "https://www.veshannastro.co.in/bracelet-fusion.html",
}
PLANET_LINE = {
    1: "The Sun is the planet of leadership, authority and the father. It wants to be seen, and it shines brightest when it leads.",
    2: "The Moon is the planet of the mind and the feelings. It is gentle and changeable, and strongest among people it trusts.",
    3: "Jupiter is the planet of knowledge, teachers and growth. It expands whatever it touches, including your commitments.",
    4: "Rahu is the planet of the unexpected and the unconventional. It brings sudden turns and rewards original thinking.",
    5: "Mercury is the planet of trade, speech and quick thinking. It moves fast and earns through people.",
    6: "Venus is the planet of love, beauty, comfort and the home. It draws people and money toward you.",
    7: "Ketu is the planet of insight, research and detachment. It looks inward and finds what others miss.",
    8: "Saturn is the planet of rules, patience and justice. It is slow, but what it builds tends to last.",
    9: "Mars is the planet of energy, courage and action. It fights for its people and hates waiting.",
}
PSY_TITLE = {1: "The Sun: how you<br>lead and shine", 2: "The Moon: how you<br>feel and care", 3: "Jupiter: how you<br>learn and grow",
             4: "Rahu: how you<br>break the mould", 5: "Mercury: how you<br>talk and trade", 6: "Venus: how you<br>love and attract",
             7: "Ketu: how you<br>think and see", 8: "Saturn: how you<br>work and earn", 9: "Mars: how you<br>fight and finish"}
MASTER = {11: "the master of intuition", 22: "the master builder", 33: "the master teacher"}
PY_SCENE = {1: "new starts, visibility and your name", 2: "family, home, intuition and caring work",
            3: "learning, speaking up and recognition", 4: "order, paperwork and steady effort",
            5: "people, travel and fresh openings", 6: "home, love, beauty and money that comes and goes",
            7: "study, health and time for yourself", 8: "work, money and responsibility", 9: "endings, big moves and health"}
PM_SHORT = {1: "start something visible", 2: "work through people", 3: "learn and present", 4: "put papers in order",
            5: "network and negotiate", 6: "home and family first", 7: "research and rest", 8: "carry responsibility",
            9: "finish and give"}
AREA_TITLES = {
    "career": ("Career and work", "What {Y} asks<br>of you at work"),
    "money": ("Money, property, investments", "Money in {Y}:<br>plan, then sign"),
    "relationships": ("Relationships, marriage, family", "Love and family<br>in {Y}"),
    "health": ("Health, sleep and mind", "Looking after<br>the one doing the work"),
}


def dots(items, cls="body"):
    return f'<ul class="dots {cls}">' + "".join(f'<li class="{p}">{t}</li>' for p, t in items) + "</ul>"


def plain(items, cls="body", pol="neutral"):
    return dots([(pol, t) for t in items], cls)


def plate_size(text, base, width=560):
    # Savate at weight 700: about 0.56 em per character
    est = len(str(text)) * base * 0.56 + 60
    return base if est <= width else max(28, int(base * width / est))


class Deck:
    def __init__(self, data):
        self.r = r = Reading(data)
        self.T = T = theme_ns(theme_for(r.P))
        self.L = look_for(T)
        self.pg = Pages(T, r.name_full, self.L)
        self.Y = r.Y
        self.mob = r.mobile
        Y = self.Y
        self.WA = {
            "name": wa(f"Hi, I read my {Y} Forecast. I would like to book the Name Correction Consultation."),
            "mobile": wa(f"Hi, I read my {Y} Forecast and the free reading of my mobile number. I would like to book the Mobile Number Correction Consultation."),
            "mobile_new": wa(f"Hi, I read my {Y} Forecast. I would like the free reading of my mobile number and the Mobile Number Correction Consultation."),
            "watch": wa(f"Hi, I read my {Y} Forecast. I would like to book the Wristwatch Consultation. I am sending a photo of my watch."),
            "compat": wa(f"Hi, I read my {Y} Forecast. I would like a Numerology Compatibility reading with my partner."),
            "talk": wa(f"Hi, I read my {Y} Forecast and would like to talk it through."),
        }

    # ── small builders ──
    def head(self, kicker, title, color=None, kclass="", size="t3", sub=None, subcolor=None):
        T = self.T
        k = f'<span class="kick {kclass}">{kicker}</span>' if kicker else ""
        s = f'<p class="lead" style="margin:12px 0 0;color:{subcolor or T.INK}">{sub}</p>' if sub else ""
        return (f'<div style="margin-bottom:22px">{k}<h2 class="disp {size}" style="color:{color or T.NAVY};margin-top:14px">{title}</h2>'
                f'<div class="accent" style="margin-top:16px"></div>{s}</div>')

    def panel(self, color, inner, text_color=None, pad="18px 20px", extra=""):
        return f'<div class="pnl" style="background:{color};color:{text_color or self.T.INK};padding:{pad};{extra}">{inner}</div>'

    def ptitle(self, t, color=None, size=19):
        return f'<div class="disp b" style="font-size:{size}px;color:{color or self.T.NAVY};margin:0 0 8px">{t}</div>'

    def rel_sentence(self, own, other, own_label, other_label):
        rel = self.r.rel(own, other)
        if own == other:
            return f"{other_label} carries the same number as {own_label}."
        return {"friend": f"{Pl(own)} counts {pl(other)} as a friend",
                "enemy": f"{Pl(own)} counts {pl(other)} as an enemy",
                "neutral": f"{Pl(own)} is neutral to {pl(other)}",
                "mixed": f"{Pl(own)} and {pl(other)} are both friends and rivals"}.get(rel, f"{Pl(own)} meets {pl(other)}")

    # ═══════════════ pages ═══════════════
    def cover(self):
        r, T = self.r, self.T
        custom = self.L.cover(self)
        if custom:
            ground, inner = custom
            self.pg.add(ground, inner, foot=False)
            return
        cells = ""
        for row in [[4, 9, 2], [3, 5, 7], [8, 1, 6]]:
            for d in row:
                on = r.cnt.get(d, 0)
                cells += (f'<div style="width:56px;height:56px;border-radius:10px;display:flex;align-items:center;justify-content:center;'
                          f'background:{T.NAVY if on else "rgba(57,75,113,.12)"};color:#fff;font-family:{T.display["family"]};font-size:28px;font-weight:500">'
                          f'{str(d) if on else ""}</div>')
        extra = f" &#183; Master {r.M}" if r.M else (f" &#183; Karmic {r.K}" if r.K else "")
        inner = f"""
{self.L.blob(T.LBLUE, 470, 470, 300, 640, "flower")}
<div class="abs" style="left:415px;top:755px;display:grid;grid-template-columns:repeat(3,56px);gap:10px">{cells}</div>
{self.L.asterisk(T.BERRY, 64, 600, 70, 12)}
{self.L.sparkle(T.WHITE, 46, 600, 520)}
{self.L.petal_flower(T.GREEN, 70, 70, 1110, hole=T.PINK)}
<div class="caps" style="color:{T.NAVY};opacity:.85">Veshannastro &#183; Vedic numerology</div>
<h1 class="disp" style="font-size:66px;color:{T.NAVY};margin-top:120px;line-height:.95">Personal<br>Year<br>Forecast</h1>
<div class="disp" style="font-size:150px;color:{T.WHITE};margin-top:6px;line-height:.9">{self.Y}</div>
<div class="accent" style="margin-top:26px;background:{T.NAVY}"></div>
<div class="caps" style="color:{T.NAVY};margin-top:24px;font-size:14px;line-height:1.7;width:330px">A private reading for<br>{esc(r.name_full)}<br>Born {r.dob_text}</div>
<div class="abs caps" style="left:50px;bottom:300px;color:{T.NAVY};font-size:12px;width:250px;line-height:1.8">Psychic {r.P} &#183; Destiny {r.D}<br>{"Name " + str(r.NT) + extra if r.NT else extra.strip(" &#183;")}<br>Personal Year {r.PY}</div>
<div class="abs caps" style="left:50px;bottom:210px;color:{T.BERRY_D};font-size:10.5px;width:240px;line-height:1.7">This edition is designed<br>for Mulank {r.P} &#183; {PLANET[r.P]}</div>
<div class="abs caps" style="left:415px;top:965px;width:190px;text-align:center;color:{T.NAVY};font-size:10.5px">Your birth-date grid</div>
"""
        self.pg.add(T.PINK, inner, foot=False)

    def letter(self):
        r, T, Y = self.r, self.T, self.Y
        relw = r.rel(r.P, r.D)
        master = f", with master {r.M} behind it" if r.M else ""
        if r.P == r.D:
            pair = f"Both are {r.P}, so {pl(r.P)}'s qualities arrive twice, strengths and cautions alike."
        elif relw == "friend":
            pair = "The two count each other as friends, so what you feel and what you do usually point the same way."
        elif relw == "enemy":
            pair = f"How those two get along decides how {Y} feels to you."
        elif relw == "mixed":
            pair = "The two are friends on some days and rivals on others, and that tension runs through your year."
        else:
            pair = "The two keep a polite distance, so you switch between them as life asks."
        prev = r.d["cycle"][0]
        inner = f"""
{self.L.scallop(T.ORANGE)}
{self.L.petal_flower(T.GREEN, 74, 50, 58, hole=T.CREAM)}
<h2 class="disp t2" style="color:{T.BERRY};margin-top:110px">Dear<br>{esc(r.first)},</h2>
<div style="width:560px;margin-top:30px" class="lead">
<p>This reading is built for one person and one year. Every number in it comes from your date of birth, {r.dob_text}, and the name you gave us. Change the birth date and every strength, caution and date in here changes with it.</p>
<p>{Y} is your Personal Year {r.PY}, {r.frame["gist"]}. It follows your Personal Year {prev["py"]} in {prev["year"]}, and what you do in it shapes the years after.</p>
<p>Your chart adds two layers: a {PLANET[r.P]} birth number, {r.P}, and a {PLANET[r.D]} destiny number, {r.D}{master}. {pair} This forecast shows where they help each other, where they pull apart, and what to do about it, month by month.</p>
<p>Even the look of these pages is chosen for you: this edition is designed for Mulank {r.P}, people born under {pl(r.P)}. Read it once from start to finish, then keep the timing map and the monthly pages close.</p>
</div>
<div style="margin-top:22px;display:flex;align-items:center;gap:16px">
{self.L.sparkle(T.PINK, 40)}
<div><img src="{asset("signature.png")}" style="height:52px;display:block"><div class="body" style="color:{T.NAVY};font-weight:700;margin-top:4px">Shashank Agrawal</div>
<div class="small">Founder, Veshannastro &#183; Author of <i>Numbers and Navgraha: Untold Secret of Numerology</i></div></div></div>
"""
        self.pg.add(T.CREAM, inner)

    def contents(self):
        T, Y = self.T, self.Y
        items = [("Your chart at a glance", "The whole chart in one look"),
                 ("How numerology reads you", "The method, worked out on your numbers"),
                 (f"Psychic {self.r.P} and Destiny {self.r.D}", f"{PLANET[self.r.P]}, {PLANET[self.r.D]}" + (f" and master {self.r.M}" if self.r.M else "")),
                 ("Your Lo Shu grid", "Planes, missing and repeated numbers"),
                 ("Your name", f"{esc(self.r.name_full)} in numbers"),
                 (f"{Y}, your {PLANET[self.r.PY]} year", f"The cycle, and what year {self.r.PY} asks"),
                 (f"{Y} by life area", "Career, money, love, health"),
                 ("Your timing map", "Windows, dates, month by month"),
                 (f"Practices for {Y}", "Habits, colours, bracelet"),
                 ("Your watch and your phone" if self.mob else "Your watch", "The things you carry daily"),
                 ("Going further", "Next steps chosen for your chart")]
        rows = "".join(f'<div style="display:flex;gap:18px;align-items:baseline"><span class="disp" style="font-size:24px;color:{T.BERRY};width:44px">{i + 1:02d}</span>'
                       f'<span style="flex:1"><span class="disp b" style="font-size:20px;color:{T.NAVY}">{t}</span><br><span class="small">{d}</span></span></div>'
                       for i, (t, d) in enumerate(items))
        inner = f"""
{self.L.blob(T.COBALT, 300, 180, 170, 1110, "bumps")}
{self.L.asterisk(T.BERRY, 120, 520, 110, 8)}
<h2 class="disp t1" style="color:{T.BERRY};margin-top:40px">Inside</h2>
<div class="lead" style="margin:14px 0 30px;color:{T.DEEP};width:420px">Eleven parts. The first five read who you are; the last six read {Y}.</div>
<div class="ruled" style="width:600px">{rows}</div>
"""
        self.pg.add(T.LBLUE, inner)

    def glance(self):
        r, T, Y = self.r, self.T, self.Y
        third = ((str(r.M), "Master number", MASTER[r.M].replace("the master of ", "").capitalize() if r.M == 11 else MASTER[r.M].capitalize(), T.LBLUE, T.INK) if r.M
                 else (str(r.K), "Karmic debt", "Read before reducing", T.LBLUE, T.INK) if r.K
                 else (str(len(r.missing)), "Missing numbers", join_and(r.missing) or "none", T.LBLUE, T.INK))
        sup = "&#8201;&#183;&#8201;".join(map(str, r.support))
        tiles = [(str(r.P), "Psychic number", PLANET[r.P], T.PINK, T.INK), (str(r.D), "Destiny number", PLANET[r.D], T.BERRY, T.WHITE),
                 third, (str(r.PY), f"Personal year {Y}", PLANET[r.PY], T.ORANGE, T.INK),
                 (str(r.NT or "-"), "Name number", f"{PLANET.get(r.NR, '')} ({r.NT} = {r.NR})" if r.NT else "", T.NAVY, T.WHITE),
                 (str(r.PN or "-"), "Personality", PLANET.get(reduce(r.PN), "") if r.PN else "", T.COBALT, T.WHITE),
                 (str(r.MN or "-"), "Maturity", PLANET.get(r.MN, "") if r.MN else "", T.GREEN, T.WHITE),
                 (sup, "Support numbers", f"For {r.P} and {r.D}", T.WHITE, T.INK)]
        th = "".join(f'<div class="tile" style="background:{bg};color:{fg};height:172px;padding:18px;display:flex;flex-direction:column;justify-content:space-between">'
                     f'<div class="num" style="font-size:{46 if len(v) > 3 else 58}px;white-space:nowrap">{v}</div><div><div class="body" style="font-weight:700">{l}</div>'
                     f'<div class="small" style="opacity:.85">{p}</div></div></div>' for v, l, p, bg, fg in tiles)
        full = [p for p in r.planes if p["state"] == "full"]
        empty = [p for p in r.planes if p["state"] == "missing"]
        reps = [f"{d} {TIMES.get(r.cnt[d], str(r.cnt[d]) + ' times')}" for d in range(1, 10) if r.cnt.get(d, 0) > 1]
        good = r.stretches("good")
        care = r.stretches("care")
        relw = r.rel(r.P, r.D)
        pair_txt = {"friend": f"A friendly pair: {pl(r.P)} and {pl(r.D)} work together.",
                    "enemy": f"An 'anti' pair: {pl(r.P)} and {pl(r.D)} do not count each other as friends.",
                    "neutral": f"A neutral pair: {pl(r.P)} and {pl(r.D)} keep their distance.",
                    "mixed": f"A mixed pair: {pl(r.P)} and {pl(r.D)} are friends and rivals."}.get(relw, "One planet, read twice.")
        if r.P == r.D:
            pair_txt = f"The same number twice: {pl(r.P)}'s qualities are doubled."
        facts = [("Missing from your birth date", (join_and(r.missing) + "." if r.missing else "None: every number is present.")
                  + (f" The {empty[0]['name'].lower()} plane ({'-'.join(map(str, empty[0]['digits']))}) is empty." if empty else "")),
                 ("Complete in your birth date", (join_and([f"The {p['name'].lower()} plane ({'-'.join(map(str, p['digits']))})" for p in full]) + "." if full else "No plane is complete; every line is partly filled or empty.")),
                 ("Repeated", (join_and(reps) + "." if reps else "No number repeats in your birth date.")),
                 (f"Your {r.P} and {r.D} together", pair_txt),
                 (f"Best window of {Y}", (good[0]["label"] + "." if good else "No single favourable stretch; use your support dates.")),
                 ("Windows to protect", (join_and([c["label"] for c in care[:3]]) + "." if care else "No careful stretch this year."))]
        fh = "".join(f'<div style="display:flex;gap:16px"><span class="small" style="width:190px;font-weight:700;color:{T.NAVY}">{a}</span>'
                     f'<span class="small" style="flex:1">{b}</span></div>' for a, b in facts)
        inner = f"""
{self.head("Chapter 1", "Your chart,<br>by the numbers")}
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">{th}</div>
<div class="ruled" style="margin-top:26px">{fh}</div>
{self.L.blob(T.PINK, 240, 130, 205, 1160, "bumps")}
"""
        self.pg.add(T.CREAM, inner)

    def statement(self):
        r, T, Y = self.r, self.T, self.Y
        rp = r.rel(r.P, r.PY)
        same = (f", the same planet as your destiny number" if r.PY == r.D else
                f", the same planet as your birth number" if r.PY == r.P else "")
        feel = {"friend": f"Your {PLANET[r.P]} birth number counts {pl(r.PY)} as a friend, so the year's mood suits you; the risk is coasting.",
                "enemy": f"Your {PLANET[r.P]} birth number counts {pl(r.PY)} as an enemy and may find the year slow or heavy. The answer is routine, not force.",
                "neutral": f"Your {PLANET[r.P]} birth number is neutral to {pl(r.PY)}: the year will feel the way you set it up.",
                "mixed": f"Your {PLANET[r.P]} birth number and {pl(r.PY)} are both friends and rivals, so the year pulls both ways."}.get(rp, "")
        if r.P == r.PY:
            feel = f"The year carries your own birth number, so {pl(r.P)}'s strengths and cautions are both turned up."
        good, care = r.stretches("good"), r.stretches("care")
        win = (f"Plan the big moves early, sign them inside {good[0]['label']}" if good else "Plan the big moves early, sign them on your support dates")
        win += (f", and give {join_and([c['label'] for c in care[:3]])} to preparation instead of decisions." if care else ".")
        s = r.support
        sw = join_and(s)
        one = len(s) == 1
        if r.support_missing:
            miss = r.support_missing
            sup = ((f"Your support number, {sw}, supports both sides of your chart" if one else
                    f"{'Two numbers' if len(s) == 2 else 'Your support numbers'}, {sw}, support both sides of your chart")
                   + f", and {join_and(miss)} {'is' if len(miss) == 1 else 'are'} missing from your birth date."
                   + f" Bringing {'it' if len(miss) == 1 else 'them'} in through your name, your phone number and your dates is the most useful adjustment you can make this year.")
        else:
            sup = (f"Your support number, {sw}, already sits in your birth date. Choosing it again in names, numbers and dates keeps the year on your side." if one else
                   f"Your support numbers, {sw}, already sit in your birth date. Choosing them again in names, numbers and dates keeps the year on your side.")
        title = f"{Y} ASKS<br>YOU {r.frame['verb']}"
        inner = f"""
{self.L.blob(T.PINK, 430, 430, 360, 760, "cloud")}
<div class="abs onblob" style="left:440px;top:930px">{self.L.plate(r.frame["plate"], self.L.fit(r.frame["plate"], 64, 240), -6, T.BERRY)}</div>
{self.L.sparkle(T.LBLUE, 50, 600, 80)}
<div class="caps" style="color:{T.LBLUE}">{Y} in one paragraph</div>
<h2 class="disp t2" style="margin-top:22px;line-height:1">{title}</h2>
<div class="lead" style="margin-top:30px;width:600px;color:#FBEFF6">
<p>The year belongs to {pl(r.PY)}{same}, so {PY_SCENE[r.PY]} come to the front. {feel}</p>
<p>{win}</p>
<p>{sup}</p></div>
"""
        self.pg.add(T.BERRY, inner)

    def method(self):
        r, T = self.r, self.T
        order = []
        if r.name_verdict() != "strong":
            order.append("name")
        if self.mob and (self.mob.get("clarity") or {}).get("change"):
            order.append("mobile number")
        order.append("the small daily things")
        last = (f"For you, the order is clear by the end of this forecast: {', then '.join(order)}." if len(order) > 1
                else "For you, the big pieces are already in place; the work this year is timing and the small daily things.")
        layers = [("Your birth date", "Fixed for life. It gives your psychic number, your destiny number and your Lo Shu grid.", T.PINK),
                  ("Your name", "Changeable. Each letter has a value; the total supports your birth numbers or rubs against them.", T.LBLUE),
                  ("What you carry", "Changeable. Your mobile number, your watch, your colours. Your phone sits on the same grid as your birth date.", T.ORANGE),
                  ("Time", "Moving. Every year and month carries a number for you. This forecast is mostly about this layer.", T.WHITE)]
        lay = "".join(f'<div class="tile" style="background:{bg};color:{T.INK}">{self.ptitle(t, T.NAVY, 20)}<div class="small">{d}</div></div>' for t, d, bg in layers)
        inner = f"""
<div style="margin-top:40px">{self.L.plate("How numerology", 46, -4, T.NAVY)}</div>
<div style="margin:-6px 0 0 60px">{self.L.plate("reads you", 46, 3, T.NAVY)}</div>
<div class="lead" style="margin-top:34px;width:600px">Vedic numerology treats each number from 1 to 9 as the signature of a planet. A number that is strong in your chart shows its planet's qualities in how you think, earn, love and decide. A missing number is not a curse: it is a quality you build on purpose.</div>
<div class="caps" style="margin:30px 0 14px;color:{T.LBLUE}">The four layers we read</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">{lay}</div>
<div class="lead" style="margin-top:24px;width:600px">You cannot change the day you were born. You can change the name you sign, the number you give your bank and the watch on your wrist. {last}</div>
{self.L.asterisk(T.PINK, 70, 590, 60, 20)}
"""
        self.pg.add(T.COBALT, inner)

    def planets_page(self):
        r, T = self.r, self.T
        rows = ""
        for d in range(1, 10):
            trait = first_sentence(r.planets[d]["trait"], 170)
            tag = "Yours" if d in (r.P, r.D) else ("Support" if d in r.support else "")
            tcol = T.BERRY if tag == "Yours" else T.GREEN
            rows += (f'<tr><td><span class="num" style="font-size:24px;color:{T.BERRY}">{d}</span></td><td>{PLANET[d]}</td>'
                     f'<td>{trait}{f" <b style=color:{tcol}>&#183; {tag}</b>" if tag else ""}</td></tr>')
        own = f"Your own numbers are {r.P} and {r.D}." if r.P != r.D else f"Your own number is {r.P}, twice."
        sup = (f" Your support numbers, {join_and(r.support)}, are the ones both of yours count as friends." if r.support_from_both
               else f" Your support numbers, {join_and(r.support)}, are friends of your birth number.")
        inner = f"""
{self.head("Nine numbers, nine planets", "What each number<br>brings", T.BERRY)}
<table class="t"><tr><th style="width:44px">No.</th><th style="width:80px">Planet</th><th>What it brings</th></tr>{rows}</table>
<div class="small" style="margin-top:18px">{own}{sup}</div>
{self.L.petal_flower(T.PINK, 60, 600, 62, hole=T.CREAM)}
"""
        self.pg.add(T.CREAM, inner)

    def worked(self):
        r, T, Y = self.r, self.T, self.Y
        d, m, y = r.dob["d"], r.dob["m"], r.dob["y"]
        digits = [int(c) for c in f"{d:02d}{m:02d}{y}"]
        comp = sum(digits)
        chain = [comp]
        while chain[-1] > 9:
            chain.append(sum(int(c) for c in str(chain[-1])))
        dsum = "+".join(map(str, digits)) + " = " + " &#8594; ".join(map(str, chain[:-1])) + (f" &#8594; " if len(chain) > 1 else "") + f"<b>{r.D}</b> ({PLANET[r.D]})"
        psy = f"{d} &#8594; " + (" + ".join(str(d)) + f" = <b>{r.P}</b>" if d > 9 else f"<b>{r.P}</b>") + f" ({PLANET[r.P]})"
        if d > 9 and sum(int(c) for c in str(d)) > 9:
            psy = f"{d} &#8594; {sum(int(c) for c in str(d))} &#8594; <b>{r.P}</b> ({PLANET[r.P]})"
        ysum = sum(int(c) for c in str(Y))
        pyraw = d + m + ysum
        pychain = [pyraw]
        while pychain[-1] > 9:
            pychain.append(sum(int(c) for c in str(pychain[-1])))
        pyw = f"{d} + {m} + {ysum} = " + " &#8594; ".join(map(str, pychain[:-1])) + (" &#8594; " if len(pychain) > 1 else "") + f"<b>{r.PY}</b>"
        rows = [("Psychic number (Mulank)", "Day of birth, reduced", psy),
                ("Destiny number (Bhagyank)", "Every digit of the full date", dsum)]
        if r.M:
            rm, rd, ry = reduce(m), reduce(d), reduce(sum(int(c) for c in str(y)))
            rows.append(("Master number", "Month, day and year reduced, then added", f"{rm} + {rd} + {ry} = <b>{r.M}</b>"))
        if r.K:
            rows.append(("Karmic debt", "Day of birth before reducing", f"<b>{r.K}</b>"))
        rows.append((f"Personal Year {Y}", "Day + month + digits of the year", pyw))
        jan, later = reduce(r.PY + 1), next((mm for mm in range(1, 13) if r.PY + mm > 9), 12)
        rows.append(("Personal months", "Personal year + calendar month",
                     f"January {r.PY}+1 = <b>{jan}</b>; {MONTHS[later - 1]} {r.PY}+{later} = {r.PY + later} &#8594; <b>{reduce(r.PY + later)}</b>"))
        if r.NT:
            parts = " + ".join(f"{p['word'].capitalize()} <b>{p['total']}</b>" for p in r.parts)
            rows.append(("Name number (Chaldean)", "Letter values, word by word", f"{parts} = <b>{r.NT}</b> &#8594; {r.NR}"))
        if r.PN:
            cons = [c for c in "".join(p["word"] for p in r.parts) if c not in "AEIOU"]
            VAL = {c: int(v) for v, s in r.d["chaldean"].items() for c in s}
            val = sum(VAL.get(c, 0) for c in cons)
            ch = [val]
            while ch[-1] > 9 and ch[-1] not in (11, 22, 33):
                ch.append(sum(int(c) for c in str(ch[-1])))
            show = " ".join(cons) if len(cons) <= 14 else " ".join(cons[:12]) + " &#8230;"
            rows.append(("Personality number", "Consonants only", f"{show} = " + " &#8594; ".join(map(str, ch[:-1])) + (" &#8594; " if len(ch) > 1 else "") + f"<b>{r.PN}</b>"))
        if r.MN:
            rows.append(("Maturity number", "Destiny + name number", f"{r.D} + {r.NR} = <b>{r.MN}</b>" if r.D + r.NR <= 9 else f"{r.D} + {r.NR} = {r.D + r.NR} &#8594; <b>{r.MN}</b>"))
        wr = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
        tiles = "".join(f'<div style="background:{bg};border-radius:10px;padding:10px 0;text-align:center"><div class="num" style="font-size:30px;color:{T.NAVY}">{v}</div>'
                        f'<div class="tiny" style="font-weight:700;color:{T.DEEP};letter-spacing:.08em">{ls}</div></div>'
                        for v, ls, bg in [(1, "AIJQY", T.PINK), (2, "BKR", T.LBLUE), (3, "CGLS", T.WHITE), (4, "DMT", T.PINK), (5, "EHNX", T.LBLUE),
                                          (6, "UVW", T.WHITE), (7, "OZ", T.PINK), (8, "FP", T.LBLUE)])
        through = [x for x in pychain if x in (11, 22, 33)]
        if r.PY == r.D:
            note = (f"Your {Y} working {'passes through ' + str(through[0]) + ' before it settles' if through else 'settles'} at {r.PY}, the same number as your destiny. "
                    f"{Y} repeats the pattern you were born with, so what happens in it tends to be about who you are, not just about what is going on around you.")
        elif r.PY == r.P:
            note = f"Your {Y} number is {r.PY}, the same as your birth number. Expect the year to test and reward the habits you were born with."
        else:
            note = (f"Your {Y} number, {r.PY}, is {REL_WORD.get(r.rel(r.P, r.PY), 'neutral')} to your birth number {r.P} "
                    f"and {REL_WORD.get(r.rel(r.D, r.PY), 'neutral')} to your destiny number {r.D}. That is the first clue to how the year will feel.")
        inner = f"""
{self.head("Every figure, shown", "Your numbers,<br>worked out")}
<table class="t"><tr><th>Number</th><th>How it is found</th><th>Your working</th></tr>{wr}</table>
<div class="caps" style="margin:22px 0 10px;color:{T.BERRY}">The Chaldean letter table</div>
<div style="display:grid;grid-template-columns:repeat(8,1fr);gap:7px">{tiles}</div>
{self.panel(T.PINK, self.ptitle("Notice this", T.BERRY_D) + f'<div class="small">{note}</div>', extra="margin-top:20px")}
"""
        self.pg.add(T.CREAM, inner)

    def pair_opener(self):
        r, T = self.r, self.T
        relw = r.rel(r.P, r.D)
        title = f"{Pl(r.P)},<br>twice" if r.P == r.D else f"{Pl(r.P)}<br>and {pl(r.D)}"
        tag = {"friend": "A pair that pulls together.", "enemy": "The pair you were born with.", "neutral": "Two numbers that keep their distance.",
               "mixed": "Friends on some days, rivals on others."}.get(relw, "One planet, read twice.")
        if r.P == r.D:
            tag = "One planet, read twice."
        mid = f", with master {r.M} between them" if r.M else (f", with a karmic {r.K} behind the day" if r.K else "")
        inner = f"""
{self.L.blob(T.PINK, 300, 300, 420, 120, "flower")}
<div class="abs num" style="left:{570 - 30 * len(str(r.P))}px;top:205px;font-size:120px;color:{T.NAVY}">{r.P}</div>
{self.L.blob(T.LBLUE, 240, 240, 60, 860, "disc")}
<div class="abs num" style="left:{180 - 28 * len(str(r.D))}px;top:930px;font-size:110px;color:{T.NAVY}">{r.D}</div>
<div style="margin-top:430px"><h2 class="disp t2">{title}</h2></div>
<div class="it" style="font-size:26px;color:{T.LBLUE};margin-top:18px">{tag}</div>
<div class="lead" style="width:330px;margin:24px 0 0 300px;color:#E7ECF7">Your psychic number is the day you were born: how you react and work before you have thought about it. Your destiny number is the whole date: the direction life keeps steering you in. Yours are {r.P} and {r.D}{mid}.</div>
<div class="abs caps" style="left:330px;bottom:120px;color:{T.WHITE};font-size:12px">Chapter 3 &#183; Psychic {r.P} and Destiny {r.D}</div>
"""
        self.pg.add(T.NAVY, inner)

    def psychic(self):
        r, T, Y = self.r, self.T, self.Y
        items = r.num_items("psychic")
        goods = [t for p, t in items if p == "good"]
        cares = [t for p, t in items if p in ("care", "mixed")]
        rp = r.rel(r.P, r.PY)
        helps = {"friend": f"{Pl(r.P)} counts the year's {PLANET[r.PY]} as a friend, so your natural way of working suits {Y}.",
                 "neutral": f"The year's {PLANET[r.PY]} is neutral to {pl(r.P)}: it neither carries you nor holds you back, so your habits decide the year.",
                 "enemy": f"In a {PLANET[r.PY]} year, your {PLANET[r.P]} side is the part of you that keeps the routine running when motivation dips.",
                 "mixed": f"{Pl(r.P)} and the year's {PLANET[r.PY]} are friends on good days; lean on that on the days things move."}.get(rp, "")
        if r.P == r.PY:
            helps = f"{Y} carries your own number, so your strengths are switched on all year."
        if goods:
            helps = first_sentence(goods[0], 120) + " " + helps
        pushes = {"enemy": f"{Pl(r.P)} counts {pl(r.PY)} as an enemy. When you catch yourself forcing results the year will not give quickly, that is the moment to slow down.",
                  "friend": "With the year on your side, the risk is too much of your own habit.",
                  "neutral": "Without the year's help, your habits show more.",
                  "mixed": "On the days the year rubs against you, keep decisions small."}.get(rp, "")
        if cares:
            pushes += " " + first_sentence(cares[0], 130)
        inner = f"""
{self.head(f"Psychic number {r.P}", PSY_TITLE[r.P], sub=PLANET_LINE[r.P])}
<div class="caps" style="color:{T.BERRY};margin-bottom:12px">What your rulebook says about {r.P}</div>
{dots(items)}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">
{self.panel(T.LBLUE, self.ptitle(f"Where {r.P} helps in {Y}", T.NAVY, 17) + f'<div class="small">{helps}</div>')}
{self.panel(T.PINK, self.ptitle(f"Where {r.P} pushes back", T.BERRY_D, 17) + f'<div class="small">{pushes}</div>')}
</div>
{self.L.ring(T.COBALT, 56, 610, 60)}
"""
        self.pg.add(T.CREAM, inner)

    def destiny(self):
        r, T, Y = self.r, self.T, self.Y
        extra_title = f", and<br>{MASTER[r.M]}" if r.M else (f"<br>and karmic {r.K}" if r.K else "")
        dname = "The Moon" if r.D == 2 else ("The Sun" if r.D == 1 else PLANET[r.D])
        title = f"{dname}{extra_title}" if (r.M or r.K) else f"{dname}: where<br>life steers you"
        kicker = f"Destiny number {r.D}" + (f" and master {r.M}" if r.M else (f" and karmic {r.K}" if r.K else ""))
        rd = r.rel(r.D, r.PY)
        if r.D == r.PY:
            ytxt = (f"{Y} is a {r.PY} year for a destiny-{r.D} person" + (f", with master {r.M} behind both" if r.M else "")
                    + ". The year turns up everything your destiny number is about, the strengths and the cautions.")
        else:
            ytxt = {"friend": f"{Pl(r.D)} counts the year's {PLANET[r.PY]} as a friend, so {Y} moves you in the direction you were already heading.",
                    "enemy": f"{Pl(r.D)} counts the year's {PLANET[r.PY]} as an enemy, so {Y} can feel like a detour from where you are heading. Treat it as a year of groundwork.",
                    "neutral": f"{Pl(r.D)} is neutral to the year's {PLANET[r.PY]}: {Y} neither speeds up nor slows down your direction; your choices do.",
                    "mixed": f"{Pl(r.D)} and the year's {PLANET[r.PY]} are friends and rivals, so expect {Y} to help and test your direction in turn."}.get(rd, "")
        body = f'<div class="caps" style="color:{T.NAVY};margin-bottom:10px">Destiny {r.D}</div>{dots(r.num_items("destiny"), "small")}'
        if r.M:
            body += f'<div class="caps" style="color:{T.NAVY};margin:14px 0 10px">Master {r.M}</div>{dots(r.num_items("master"), "small")}'
        if r.K and r.num_items("karmic"):
            body += f'<div class="caps" style="color:{T.NAVY};margin:14px 0 10px">Karmic debt {r.K}</div>{dots(r.num_items("karmic"), "small")}'
        inner = f"""
{self.head(kicker, title, T.BERRY)}
{body}
{self.panel(T.NAVY, self.ptitle(f"{Y} and your destiny", T.LBLUE, 17) + f'<div class="small">{ytxt}</div>', T.WHITE, extra="margin-top:14px")}
{self.L.heart(T.PINK, 54, 612, 62)}
"""
        self.pg.add(T.CREAM, inner)

    def pair(self):
        r, T = self.r, self.T
        relw = r.rel(r.P, r.D)
        pitems = r.num_items("pair")
        rel_items = [t for p, t in pitems if "remed" not in t.lower()]
        sub = rel_items[0] if rel_items else ""
        back = r.rel(r.D, r.P)
        lead = {"friend": f"{Pl(r.P)} ({r.P}) counts {pl(r.D)} ({r.D}) as a friend" + (", and the feeling is mutual." if back == "friend" else "."),
                "enemy": f"{Pl(r.P)} ({r.P}) counts {pl(r.D)} ({r.D}) as an enemy" + (", and the feeling is returned." if back == "enemy" else "."),
                "neutral": f"{Pl(r.P)} ({r.P}) is neutral to {pl(r.D)} ({r.D}).",
                "mixed": f"{Pl(r.P)} ({r.P}) and {pl(r.D)} ({r.D}) are friends and rivals at once."}.get(relw, "")
        if r.P == r.D:
            lead = f"Both your numbers are {r.P}, {pl(r.P)}."
        body = {"friend": "In daily life it shows as ease: what you feel and what you do usually point the same way. The risk is comfort; the pair works best with a clear goal in front of it.",
                "enemy": "In daily life it shows as a gap between what you know you should do and how you feel about doing it. When the two cooperate you are both reliable and kind, which is rare. When they fight, the result is overthinking, delays just before success, and feeling unseen for the work you do.",
                "neutral": f"In daily life the two keep out of each other's way: you switch between your {PLANET[r.P]} side and your {PLANET[r.D]} side as the moment needs, but neither rescues the other on a bad day.",
                "mixed": "On good days they push each other higher; on hard days they compete for the same space. Knowing which day it is helps."}.get(relw, "")
        if r.P == r.D:
            body = f"{Pl(r.P)}'s qualities arrive twice, so its strengths come easily and its cautions need watching twice as closely."

        def fcol(n, title, bg):
            row = r.rows[str(n)]
            rows = [("Friends", row["friend"]), ("Neutral", row["neutral"]), ("Enemies", row["enemy"]), ("Mixed", row["mixed"])]
            h = "".join(f'<div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1.5px solid rgba(255,255,255,.6)">'
                        f'<span class="small" style="font-weight:700">{a}</span><span class="small">{", ".join(map(str, b)) or "none"}</span></div>' for a, b in rows)
            return self.panel(bg, f'<div class="disp b" style="font-size:24px;margin-bottom:8px">{title}</div>{h}')
        sup = r.support
        one = len(sup) == 1
        if r.support_from_both:
            supline = f"{'It is the number' if one else 'They are the numbers'} both your {r.P} and your {r.D} count as friends"
        else:
            supline = f"{'It is a friend' if one else 'They are friends'} of your birth number {r.P}"
        miss = r.support_missing
        supline += (f", and {join_and(miss)} {'is' if len(miss) == 1 else 'are'} missing from your birth date." if miss
                    else (", and it already sits in your birth date." if one else ", and they already sit in your birth date."))
        supline += f" Whenever you can choose a number, a date, a name spelling or a phone number, choosing {join_and(sup)} feeds your chart."
        inner = f"""
{self.head("Read as a pair", f"Your {r.P} and {r.D}<br>together", sub=lead + (" " + sub if sub else ""))}
<div class="body">{body}</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px">
{fcol(r.P, f"{r.P} &#183; you", T.LBLUE)}
{fcol(r.D, f"{r.D} &#183; your destiny", T.PINK)}
</div>
{self.panel(T.ORANGE, f'<div class="disp b" style="font-size:34px;color:{T.DEEP}">{"Your support number" if len(sup) == 1 else "Your support numbers"}: {join_and(sup)}</div><div class="body" style="margin-top:8px">{supline}</div>', extra="margin-top:16px")}
"""
        self.pg.add(T.CREAM, inner)

    def pair_remedies(self):
        r, T = self.r, self.T
        items = [i for i in r.b["numbers"]["pair"]["items"] if "remedy" in (i.get("areas") or [])]
        if not items:
            return False
        marks = [self.L.heart(T.PINK, 46), self.L.petal_flower(T.BERRY, 46, hole=T.LBLUE), self.L.ring(T.COBALT, 46), self.L.sparkle(T.ORANGE, 46)]
        rows = ""
        for k, it in enumerate(items[:4]):
            areas = [a for a in it.get("areas", []) if a != "remedy"]
            title = {"love": "For relationships", "career": "For career, business or settling abroad", "health": "For health", "money": "For money"}.get(areas[0] if areas else "", "For this pair")
            import re as _re
            t = clean(it["say"])
            t = _re.sub(r"^If this (?:number )?combination brings (?:health )?struggles(?: in (?:career, business or settling abroad|[a-z ]+))?, ", "", t)
            t = _re.sub(r"^suggested remedies are ", "", t)
            t = _re.sub(r" (?:is|are) suggested, ", ", ", t)
            t = t[0].upper() + t[1:]
            rows += (f'<div style="display:flex;gap:20px;align-items:flex-start"><div style="flex:0 0 46px">{marks[k % 4]}</div>'
                     f'<div>{self.ptitle(title, T.BERRY, 21)}<div class="body">{t}</div></div></div>')
        inner = f"""
{self.L.blob(T.LBLUE, 310, 260, 165, 1040, "cloud")}
{self.head(f"For the {r.P} and {r.D} pair", "What your rulebook<br>prescribes", sub="If this pair shows up as struggle in one part of your life, these are the remedies your rulebook gives for it.")}
<div class="ruled" style="width:620px">{rows}</div>
<div class="small" style="margin-top:22px;width:420px">Choose the one that matches where the struggle shows. Regular practice matters more than doing everything at once.</div>
"""
        self.pg.add(T.CREAM, inner)
        return True

    def loshu(self):
        r, T = self.r, self.T
        palette = [T.COBALT, T.BERRY, T.GREEN, T.NAVY, T.ORANGE, T.COBALT, T.BERRY, T.GREEN, T.NAVY]
        cells = ""
        for row in [[4, 9, 2], [3, 5, 7], [8, 1, 6]]:
            for d in row:
                n = r.cnt.get(d, 0)
                if n:
                    txt = str(d) * n
                    fs = 62 if n <= 2 else (48 if n == 3 else 36)
                    cells += (f'<div style="background:{palette[d - 1]};border-radius:16px;height:150px;position:relative;color:#fff">'
                              f'<span class="caps" style="position:absolute;left:14px;top:12px;font-size:10px;opacity:.8">{d}</span>'
                              f'<div class="num" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:{fs}px">{txt}</div></div>')
                else:
                    cells += (f'<div style="border:2px dashed rgba(57,75,113,.35);border-radius:16px;height:150px;position:relative;color:{T.NAVY}">'
                              f'<span class="caps" style="position:absolute;left:14px;top:12px;font-size:10px;opacity:.7">{d}</span>'
                              f'<div class="caps" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;opacity:.75">missing</div></div>')
        dig = ", ".join(c for c in f'{r.dob["d"]:02d}{r.dob["m"]:02d}{r.dob["y"]}')
        n = len(r.missing)
        empty = [p for p in r.planes if p["state"] == "missing"]
        full = [p for p in r.planes if p["state"] == "full"]
        if n >= 4:
            say = f"{WORD_CAP(n)} missing numbers is more than average"
        elif n == 3:
            say = "Three missing numbers is about average"
        elif n:
            say = f"Only {WORD.get(n, n)} missing number{'s' if n > 1 else ''}: a well-filled grid"
        else:
            say = "No missing numbers at all: a rare, complete grid"
        if empty:
            p = empty[0]
            say += (f", and {join_and(p['digits'])} form one complete line: the {p['name'].lower()} plane. That single fact explains a lot about "
                    f"{PLANE_MEAN[p['name']].lower()}, and it shapes how you meet {self.Y}.")
        elif full:
            p = full[0]
            say += f". Your {p['name'].lower()} plane is complete: {PLANE_MEAN[p['name']].lower()} come naturally to you."
        else:
            say += ". No line of your grid is completely empty, and none is complete: each part of life is partly given and partly built."
        inner = f"""
<div style="margin-top:6px">{self.L.plate("Your", 54, -5, T.NAVY)}</div>
<div style="margin:-8px 0 0 40px">{self.L.plate("Lo Shu grid", 54, 3, T.NAVY)}</div>
<div class="lead" style="margin-top:28px;width:620px">A 3 by 3 square in which every row, column and diagonal adds up to 15. Each digit of your date of birth (zeros are skipped) sits in its own cell. Filled cells are qualities you were born with; empty cells are qualities you build.</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:26px;width:500px">{cells}</div>
<div class="abs" style="left:575px;top:600px;width:110px"><div class="caps" style="font-size:10.5px;color:{T.NAVY}">Your digits</div><div class="small" style="color:{T.DEEP}">{dig}</div>
<div class="caps" style="font-size:10.5px;color:{T.NAVY};margin-top:14px">Missing</div><div class="small" style="color:{T.DEEP}">{join_and(r.missing) or "none"}</div></div>
<div class="lead" style="margin-top:22px;width:620px">{say}</div>
{self.L.asterisk(T.BERRY, 80, 590, 70, 10)}
"""
        self.pg.add(T.PINK, inner)

    def planes_page(self):
        r, T = self.r, self.T
        sw = {"full": ("Complete", T.GREEN), "missing": ("Empty", T.ORANGE), "partial": ("Partly", T.NAVY)}
        rows = "".join(f'<tr><td>{p["name"]}</td><td>{" &#183; ".join(map(str, p["digits"]))}</td><td>{PLANE_MEAN[p["name"]]}</td>'
                       f'<td>{", ".join(map(str, p["present"])) or "none"}</td><td style="color:{sw[p["state"]][1]};font-weight:700">{sw[p["state"]][0]}</td></tr>'
                       for p in r.planes)
        pitems = r.b["loshu"]["items"]["planes"]
        panels = []
        for it in pitems[:2]:
            t = clean(it["say"])
            full = "complete" in t.lower() or it.get("polarity") == "good" or "is complete" in t
            name = next((p["name"] for p in r.planes if p["name"].lower() in t.lower()), "Plane")
            state = next((p["state"] for p in r.planes if p["name"] == name), "partial")
            col, tc, lab = ((T.GREEN, T.WHITE, "complete") if state == "full" else (T.ORANGE, T.DEEP, "empty") if state == "missing" else (T.LBLUE, T.NAVY, "partly filled"))
            panels.append(self.panel(col, self.ptitle(f"{name} plane: {lab}", T.WHITE if col == T.GREEN else T.DEEP, 18) + f'<div class="small">{t}</div>', tc if col == T.GREEN else T.INK))
        grid = f'<div style="display:grid;grid-template-columns:{"1fr 1fr" if len(panels) == 2 else "1fr"};gap:12px;margin-top:20px">{"".join(panels)}</div>' if panels else ""
        inner = f"""
{self.head("Rows, columns and diagonals", "The eight planes", sub="Each line of the grid governs one part of life. A line is complete when all three digits are present, and empty when none are.")}
<table class="t"><tr><th>Plane</th><th>Digits</th><th>Governs</th><th>You have</th><th>State</th></tr>{rows}</table>
{grid}
{self.L.petal_flower(T.PINK, 56, 610, 62, hole=T.CREAM)}
"""
        self.pg.add(T.CREAM, inner)

    def missing_page(self):
        r, T, Y = self.r, self.T, self.Y
        if not r.missing:
            return False
        texts = {}
        for it in r.b["loshu"]["items"]["missing"]:
            t = clean(it["say"])
            import re as _re
            m = _re.match(r"Missing (\d)", t)
            if m:
                texts.setdefault(int(m.group(1)), []).append(t)
        cols = [T.PINK, T.LBLUE, T.ORANGE, T.WHITE, T.LBLUE, T.PINK, T.WHITE, T.ORANGE]
        many = len(r.missing) > 4
        cards = ""
        for k, d in enumerate(r.missing):
            months = r.months_with_pm(d)
            mline = (f" Your {d} month{'s' if len(months) > 1 else ''} in {Y}: {join_and(months)}." if months else "")
            text = " ".join(texts.get(d, [])) or f"Missing {d} means {pl(d)}'s qualities do not arrive on their own."
            cards += (f'<div class="tile" style="background:{cols[k % len(cols)]};padding:{"14px 16px" if many else "18px"}">'
                      f'<div style="display:flex;align-items:baseline;gap:10px"><span class="num" style="font-size:{38 if many else 46}px;color:{T.NAVY}">{d}</span>'
                      f'<span class="caps" style="font-size:10.5px;color:{T.BERRY_D}">Missing &#183; {PLANET[d]}</span></div>'
                      f'<div class="small" style="margin-top:6px">{text}</div>'
                      f'<div class="small" style="margin-top:8px"><b style="color:{T.GREEN}">Bring it in:</b> {BRING[d]}{mline}</div></div>')
        empty = [p for p in r.planes if p["state"] == "missing"]
        if empty:
            p = empty[0]
            note = (f"Missing {join_and(p['digits'])} empty the {p['name'].lower()} line of your grid, the line of {PLANE_MEAN[p['name']].lower()}. "
                    f"In {Y} that line needs deliberate attention: build it with the habits above, one at a time.")
        else:
            note = (f"Missing numbers are qualities you build, not curses. Names, phone numbers and dates can bring them in; "
                    f"your support numbers, {join_and(r.support)}, matter most.")
        title = join_and(r.missing)
        inner = f"""
{self.head("Not born with them", title, T.BERRY, size="t3" if len(r.missing) <= 5 else "t4", sub="A missing number means its qualities do not arrive on their own, so you invite them. Each card gives your rulebook's reading and practical ways to bring the number in.")}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">{cards}</div>
{self.panel(T.NAVY, f'<div class="small">{note}</div>', T.WHITE, extra="margin-top:14px")}
"""
        self.pg.add(T.CREAM, inner)
        return True

    def repeated(self):
        r, T = self.r, self.T
        L = r.b["loshu"]["items"]
        rep = r.say(L["repeats"]) + [x for x in r.say(L["present"]) if x[0] != "neutral"]
        rep = [x for x in rep if not x[1].startswith("With ")]
        seen, rep2 = set(), []
        for p, t in rep:
            if t not in seen:
                seen.add(t)
                rep2.append((p, t))
        twice = [d for d in range(1, 10) if r.cnt.get(d, 0) > 1]
        once = [d for d in range(1, 10) if r.cnt.get(d, 0) == 1]
        cap = "; ".join(x for x in [
            (join_and(twice) + " " + (TIMES[r.cnt[twice[0]]] if len({r.cnt[d] for d in twice}) == 1 else "more than once")) if twice else "",
            (join_and(once) + " once") if once else ""] if x)
        yrows = ""
        for y in r.d.get("dobYogas", []):
            formed = " + ".join(map(str, y["present"])) + (", no " + ", ".join(map(str, y["absent"])) if y["absent"] else "")
            g = soft(y["good"] or "", y.get("areas"))
            c = soft(re.sub(r"^[A-Z][A-Za-z ]+ Yoga: ", "", y["care"] or ""), y.get("areas"))
            what = (g + (" " if g and c else "") + (f"Care: {c[0].lower() + c[1:]}" if c else "")).strip()
            ytitle = y["title"].split(" (")[0] if "Depression" in y["title"] else y["title"]
            yrows += f"<tr><td>{ytitle}</td><td>{formed}</td><td>{what}</td></tr>"
        ytable = (f'<div class="caps" style="color:{T.BERRY};margin:16px 0 10px">Yogas on your birth date</div>'
                  f'<table class="t"><tr><th>Yoga</th><th>Formed by</th><th>What it brings</th></tr>{yrows}</table>'
                  f'<div class="tiny" style="margin-top:10px">Birth-date yogas are fixed for life. Your name and mobile number can soften the difficult ones.</div>'
                  if yrows else '<div class="small" style="margin-top:16px">No birth-date yoga forms on your grid, so your name and mobile number carry more of the weight.</div>')
        inner = f"""
{self.head("Held in strength", "Repeated numbers<br>and your yogas")}
<div class="caps" style="color:{T.BERRY};margin-bottom:10px">{cap}</div>
{dots(rep2, "small")}
{ytable}
"""
        self.pg.add(T.LBLUE, inner)

    def name_open(self):
        r, T = self.r, self.T
        if not r.NT:
            return False
        VAL = {c: v for v, s in r.d["chaldean"].items() for c in s}
        bgs = [T.PINK, T.LBLUE, T.ORANGE, T.WHITE]
        rows = ""
        longest = max(len(p["word"]) for p in r.parts)
        tw = 52 if longest <= 11 else max(34, int(600 / longest) - 6)
        for k, p in enumerate(r.parts):
            tiles = "".join(f'<div style="background:{bgs[k % 4]};border-radius:10px;width:{tw}px;height:{int(tw * 1.3)}px;text-align:center;padding-top:6px">'
                            f'<div class="disp" style="font-size:{int(tw * .58)}px;color:{T.NAVY}">{c}</div><div class="caps" style="font-size:11px;color:{T.DEEP}">{VAL.get(c, "")}</div></div>'
                            for c in p["word"])
            rows += (f'<div style="display:flex;gap:6px;margin-top:{30 if k == 0 else 20}px;flex-wrap:wrap">{tiles}</div>'
                     f'<div class="body" style="margin-top:8px;color:#fff">{p["word"].capitalize()} = <b>{p["total"]}</b>, which reduces to <b>{p["root"]}</b> ({PLANET[p["root"]]})</div>')
        wb, wd = r.rel(r.P, r.NR), r.rel(r.D, r.NR)
        wword = {"friend": "friendly", "enemy": "unfriendly", "neutral": "neutral", "mixed": "mixed"}
        inner = f"""
<div style="margin-top:6px">{self.L.plate("Your", 56, -5, T.GREEN)}</div>
<div style="margin:-8px 0 0 40px">{self.L.plate("name", 56, 3, T.GREEN)}</div>
<div class="lead" style="margin-top:28px;width:620px;color:#EAF3EC">Your name is the one part of your chart you can change. In the Chaldean system each letter carries a value from 1 to 8; 9 is never given to a letter. A name is read word by word, then as a full total, then reduced to one digit.</div>
{rows}
<div style="display:flex;align-items:center;gap:20px;margin-top:30px">
<div class="num" style="font-size:120px;color:#fff">{r.NT}</div>
<div class="lead" style="color:#EAF3EC">Your full name number.<br>{r.NT} reduces to <b>{r.NR}</b>, {PLANET[r.NR]}: {wword.get(wb, "neutral")} with your birth number {r.P}, {wword.get(wd, "neutral")} with your destiny number {r.D}.</div></div>
{self.L.petal_flower(T.PINK, 84, 590, 66, hole=T.GREEN)}
"""
        self.pg.add(T.GREEN, inner)
        return True

    def name_meaning(self):
        r, T = self.r, self.T
        if not r.NT:
            return False
        nb = r.b["name"]
        lines = r.say(nb["items"] + nb.get("firstLetterItems", []))
        v = r.name_verdict()
        title = {"strong": "A name that<br>works for you", "mixed": "A good name,<br>with a catch", "weak": "A name working<br>below its strength"}[v]
        summary = {"strong": "In short: your name supports your birth numbers. Keep the spelling you use every day, and use it consistently.",
                   "mixed": "In short: your name helps you in some places and holds you back in others. A small correction in spelling can keep the help and remove the catch.",
                   "weak": "In short: the name you carry today is working below its strength. A name correction is the first thing we would change in your chart."}[v]
        goods = [x for x in lines if x[0] in ("good", "neutral")]
        cares = [x for x in lines if x[0] in ("care", "mixed")]
        body = dots(goods + cares, "small")
        inner = f"""
{self.head(f"What {r.NT} and {r.NR} mean", title, T.BERRY)}
{body}
{self.panel(T.LBLUE, f'<div class="small" style="font-weight:700;color:{T.NAVY}">{summary}</div>', extra="margin-top:14px")}
"""
        self.pg.add(T.CREAM, inner)
        return True

    def name_offer(self):
        r, T = self.r, self.T
        v = r.name_verdict()
        s = join_and(r.support)
        lead = {"strong": "Your name already works for you. A consultation checks the version you sign with, the one on your bank and the one people call you by, so all three carry the same strength.",
                "mixed": "If the catch on the last page sounds familiar, this is the gentle fix. In an online consultation we sit with your name and your birth numbers and adjust the spelling with you. Most of the time your name sounds the same; the numbers simply line up behind you.",
                "weak": "If the last page sounds familiar, this is the gentle fix. In an online consultation we sit with your name and your birth numbers and correct the spelling with you. Most of the time your name sounds the same; the numbers simply line up behind you instead of against you."}[v]
        inner = f"""
{self.L.blob(T.LBLUE, 560, 470, 80, 40, "cloud")}
<div class="abs onblob" style="left:150px;top:230px">{self.L.plate("A name that", 52, -5, T.NAVY)}</div>
<div class="abs onblob" style="left:190px;top:322px">{self.L.plate("works for you", 52, 3, T.NAVY)}</div>
<div style="margin-top:520px">
<div class="caps" style="color:{T.PINK}">Online, one to one</div>
<div class="disp t4" style="margin-top:8px">Name Correction Consultation</div>
<div class="body" style="margin-top:14px;color:#E7ECF7;width:610px">{lead}</div>
<div class="rule wh" style="margin:20px 0"></div>
{plain(["Your current name read word by word, with what helps and what clashes",
        f"A corrected spelling chosen with you, kept recognisable and moved toward {s}, your support number{'s' if len(r.support) > 1 else ''}",
        "Which version to use where: signature, bank, social media, nameplate",
        "How to start using it from the first day; your rulebook values use over paperwork"], "small")}
<div style="margin-top:22px">{action_bar("Book on WhatsApp", "Name Correction Consultation, online", self.WA["name"], "or book an online numerology consultation", LINKS["numcons"])}</div>
</div>
{self.L.sparkle(T.PINK, 50, 610, 1040)}
"""
        self.pg.add(T.COBALT, inner)

    def pers_mat(self):
        r, T, Y = self.r, self.T, self.Y
        if not (r.PN and r.MN):
            return False
        pit = r.num_items("personality")
        mit = r.num_items("maturity")
        pl = PLANET[reduce(r.PN)]
        lines = []
        if reduce(r.PN) in r.support:
            lines.append(("good", f"Your personality number {r.PN} is one of your support numbers, so your first impression is one of your strongest assets in {Y}: present, teach, speak."))
        else:
            rp = r.rel(reduce(r.PN), r.PY)
            lines.append(({"friend": "good", "enemy": "care"}.get(rp, "neutral"),
                          {"friend": f"Your personality number {r.PN} is friendly to the year's {r.PY}: people warm to you quickly in {Y}, so let them see you.",
                           "enemy": f"Your personality number {r.PN} sits uneasily with the year's {r.PY}: first impressions may take longer to land in {Y}, so let your work speak first.",
                           "neutral": f"Your personality number {r.PN} is neutral to the year: your first impression in {Y} will be what you make of it.",
                           "mixed": f"Your personality number {r.PN} and the year's {r.PY} pull both ways: some rooms will warm to you at once, others will need time."}.get(rp, "")))
        a0, a1 = r.ages_in_year()
        lines.append(("good", f"Your maturity number {r.MN} ({PLANET[r.MN]}) describes what life builds toward after your forties. "
                      + (f"You are already in that stretch, so {Y} is when its promises start to show." if a0 >= 40 else f"{Y} is part of the groundwork for it.")))
        for p, t in mit[1:2]:
            lines.append((p, t))
        sub = ("The personality number uses only the consonants and describes your first impression. The maturity number describes what life builds toward after your forties"
               + (", which is exactly where you are now." if a0 >= 40 else "."))
        inner = f"""
{self.head("Two more numbers from your name", f"Personality {r.PN},<br>Maturity {r.MN}", sub=sub)}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
{self.panel(T.PINK, f'<div class="num" style="font-size:64px;color:{T.NAVY}">{r.PN}</div><div class="caps" style="color:{T.BERRY_D};font-size:11px">Personality &#183; {pl}</div><div class="small" style="margin-top:8px">{pit[0][1] if pit else ""}</div>')}
{self.panel(T.NAVY, f'<div class="num" style="font-size:64px">{r.MN}</div><div class="caps" style="color:{T.LBLUE};font-size:11px">Maturity &#183; {PLANET[r.MN]}</div><div class="small" style="margin-top:8px">{mit[0][1] if mit else ""}</div>', T.WHITE)}
</div>
<div class="caps" style="color:{T.BERRY};margin:20px 0 10px">How these two show up in {Y}</div>
{dots(lines, "small")}
"""
        self.pg.add(T.CREAM, inner)
        return True


def WORD_CAP(n):
    from .content import WORD
    return WORD.get(n, str(n)).capitalize()


from .content import WORD  # noqa: E402  (used in loshu)
