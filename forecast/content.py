"""Turns the brain's data for one person (data.mjs output) into everything the forecast pages say.

Rule lines are quoted from the Veshannastro brain and rulebook (the "say" / "text" of approved rules).
Joining sentences (how two numbers meet, what a month is for, which dates help) are worked out here from
the same numbers, so every forecast reads as one argument about one person.
"""
import calendar
import re
from datetime import date

PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MON = [m[:3] for m in MONTHS]
WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
TIMES = {1: "once", 2: "twice", 3: "three times", 4: "four times", 5: "five times", 6: "six times"}


def pl(n):
    """A planet as a noun: the Sun and the Moon take 'the'."""
    return {1: "the Sun", 2: "the Moon"}.get(n, PLANET.get(n, ""))


def Pl(n):
    s = pl(n)
    return s[:1].upper() + s[1:]


def clean(t):
    t = re.sub(r"\s+[—–]\s+", ", ", str(t or ""))
    return t.replace("—", ", ").replace("–", " to ").strip()


def join_and(xs):
    xs = [str(x) for x in xs]
    if not xs:
        return ""
    if len(xs) == 1:
        return xs[0]
    return ", ".join(xs[:-1]) + " and " + xs[-1]


def ordinal(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def reduce(n):
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


# ── what each personal year and month is for (from the personal-year rule themes) ──
PY_FRAME = {
    1: dict(verb="TO BEGIN,<br>AND TO BE SEEN.", plate="BEGIN", tag="Begin, show up, be seen.", cycle="Seeds",
            focus=["career", "money"], concern="career, money and work",
            gist="a year of new beginnings, visibility and name"),
    2: dict(verb="TO BUILD,<br>NOT TO START.", plate="BUILD", tag="Build, partner, nurture.", cycle="Partnership",
            focus=["money", "relationships"], concern="money, property and family",
            gist="a Moon year of routine, partnership, home and property"),
    3: dict(verb="TO GROW,<br>AND TO SPEAK UP.", plate="GROW", tag="Learn, speak, grow.", cycle="Recognition",
            focus=["career", "money"], concern="career, money and work",
            gist="a year of advancement, learning and recognition"),
    4: dict(verb="TO ORDER,<br>AND TO ENDURE.", plate="ORDER", tag="Organise, endure, let go.", cycle="Foundation",
            focus=["money", "career"], concern="money, career and work",
            gist="a Rahu year of order, effort and careful money"),
    5: dict(verb="TO MOVE,<br>AND TO MEET.", plate="MOVE", tag="Move, meet, expand.", cycle="Movement",
            focus=["career", "money"], concern="career, money and travel",
            gist="a Mercury year of fresh air, networking and growth"),
    6: dict(verb="TO CARE FOR<br>HOME AND MONEY.", plate="HOME", tag="Home, love, balance.", cycle="Home",
            focus=["relationships", "money"], concern="money, marriage and family",
            gist="a Venus year of home, love and careful spending"),
    7: dict(verb="TO SLOW DOWN,<br>AND TO LEARN.", plate="LEARN", tag="Learn, reflect, restore.", cycle="Reflection",
            focus=["health", "career"], concern="career, health and studies",
            gist="a Ketu year of learning, introspection and health"),
    8: dict(verb="TO EARN,<br>WITH RESTRAINT.", plate="EARN", tag="Earn, endure, win the day.", cycle="Reward",
            focus=["money", "career"], concern="money, career and work",
            gist="a Saturn year of earning, restraint and steady effort"),
    9: dict(verb="TO FINISH,<br>AND TO CHANGE.", plate="CHANGE", tag="Finish, release, change.", cycle="Release",
            focus=["career", "health"], concern="career, health and family",
            gist="a Mars year of endings, big change and patience"),
}

PM = {
    1: ("Start and be seen", "Begin what you want to be known for, and let people see it."),
    2: ("Partner and listen", "Work through people: agree, cooperate, and listen before you push."),
    3: ("Learn, speak, grow", "Learn something, present your ideas, and ask for the next step."),
    4: ("Organise and endure", "Put papers, accounts and plans in order, and keep going on the slow days."),
    5: ("Trade and talk", "Meet people, negotiate, and keep money moving, with care."),
    6: ("Home and beauty", "Home, family and comfort come first; spend on what lasts."),
    7: ("Reflect and study", "Research, rest and think; this month rewards depth over speed."),
    8: ("Responsibility and reward", "Carry the extra weight well; what you finish now pays back."),
    9: ("Finish and release", "Close what is pending, give generously, keep disagreements brief."),
}

PLANE_MEAN = {"Mental": "Thinking, memory, analysis", "Emotional": "Feeling, expressing, inner calm",
              "Practical": "Physical work, being grounded", "Thought": "Planning and vision", "Will": "Determination",
              "Action": "Turning plans into action", "Silver": "Inner strength, intuition", "Golden": "Prosperity, material success"}

# Practical ways to bring a missing number in (planet qualities and the rulebook's own practices).
BRING = {
    1: "Begin the day with morning sunlight and a fixed wake-up time. Respect your father and seniors openly. Take the lead on one small thing each week.",
    2: "Sleep and wake on time, and keep the night for rest. Say other people's feelings out loud before you answer them. Time near water calms you.",
    3: "Learn with a teacher, not alone. Respect teachers and elders openly. Keep a weekly study hour; wear yellow on days you need confidence.",
    4: "Write plans down and keep lists. Keep money matters in writing and on time. Avoid shortcuts and unplanned decisions.",
    5: "Speak up and ask for what is owed to you. Keep a small side skill or income; 5 is the number of trade. Keep plants and green around your workspace.",
    6: "Keep your home clean and beautiful, with fresh flowers. Spend on what lasts and save in gold or silver. Make time for music, art and your partner.",
    7: "Take ten quiet minutes a day: prayer, reading or a walk alone. Build your own steady circle. Study and research go better in the mornings.",
    8: "Keep your word and keep time; the slow way is the safe way for you. Avoid shortcuts with money. Serve elders and the people who work for you.",
    9: "Move every day: a sport, a run or a brisk walk. Put anger into work, not words. Help younger people, and finish what you start.",
}

REL_WORD = {"friend": "a friend", "neutral": "neutral", "enemy": "an enemy", "mixed": "both friend and rival"}
AREA_BUCKETS = {
    "career": {"career", "business", "work", "fame", "education", "legal", "intellect", "image", "communication", "travel"},
    "money": {"money", "property", "business", "luck"},
    "relationships": {"love", "marriage", "family", "relationships", "relationship", "social", "children", "home"},
    "health": {"health", "mind", "emotions", "body", "energy", "temperament", "temper", "safety"},
}


def relation(rows, own, other):
    row = rows.get(str(own)) or {}
    for k in ("friend", "neutral", "enemy", "mixed"):
        if other in row.get(k, []):
            return k
    return None


class Reading:
    """Everything the deck needs, computed once."""

    def __init__(self, d, gender=None):
        self.d = d
        self.gender = (gender or d["input"].get("gender") or "").lower() or None
        b = d["brain"]
        self.b = b
        self.name_full = d["input"]["name"]
        self.first = self.name_full.split()[0] if self.name_full else "Friend"
        self.dob = d["dob"]
        self.Y = d["input"]["year"]
        self.P, self.D, self.M, self.K = d["psychic"], d["destiny"], d["master"], d["karmic"]
        self.PY = d["personalYear"]
        self.rows = d["relations"]
        self.planets = {int(k): v for k, v in d["planets"].items()}
        nm = d["name"] or {}
        self.NT, self.NR = nm.get("total"), nm.get("root")
        self.parts = nm.get("parts") or []
        self.PN, self.MN = d["personality"], d["maturity"]
        self.cnt = {int(k): v for k, v in b["loshu"]["counts"].items()}
        self.missing = list(b["loshu"]["missing"])
        self.present = [n for n in range(1, 10) if self.cnt.get(n)]
        self.planes = b["loshu"]["planes"]
        self.frame = PY_FRAME[self.PY]
        self.age_ids = {a["id"] for a in d.get("ageItems", [])}
        self.dob_date = date(self.dob["y"], self.dob["m"], self.dob["d"])
        self.dob_text = f'{self.dob["d"]} {MONTHS[self.dob["m"] - 1]} {self.dob["y"]}'
        self._support()
        self._months()

    # ── numbers ──
    def rel(self, own, other):
        return relation(self.rows, own, other)

    def friends(self, n):
        return (self.rows.get(str(n)) or {}).get("friend", [])

    def _support(self):
        fp, fd = set(self.friends(self.P)), set(self.friends(self.D))
        both = sorted(fp & fd - {self.P, self.D}) or sorted(fp & fd)
        self.support_from_both = bool(both)
        self.support = both if both else sorted(fp - {self.P})[:2]
        self.support_missing = [n for n in self.support if n in self.missing]

    def pl(self, n):
        return PLANET.get(reduce(n) if n else n, "")

    # ── rule lines ──
    def say(self, items, drop_age=True):
        out = []
        for it in items or []:
            if drop_age and it.get("id") in self.age_ids:
                continue
            t = clean(it["say"])
            if self.gender == "female" and t.startswith("For men:"):
                continue
            if self.gender == "male" and t.startswith("For women:"):
                continue
            s = soft(t, it.get("areas"))
            if s != t and (s.startswith("Linked with strain") or s == "Needs care." or s.endswith(":")):
                continue
            out.append((it.get("polarity") or "neutral", s))
        return out

    def num_items(self, key):
        n = self.b["numbers"].get(key)
        return self.say(n["items"]) if n else []

    def all_lines(self):
        """Every person-level rule line with its areas, for the life-area pages."""
        b = self.b
        src = []
        for k in ("psychic", "destiny", "master", "karmic", "pair", "personality", "maturity"):
            n = b["numbers"].get(k)
            if n:
                src += [(k, i) for i in n["items"]]
        for k, items in b["loshu"]["items"].items():
            src += [("loshu-" + k, i) for i in items]
        if b.get("name"):
            src += [("name", i) for i in b["name"]["items"]]
        out, seen = [], set()
        for k, i in src:
            if i["id"] in seen or i["id"] in self.age_ids:
                continue
            seen.add(i["id"])
            t = clean(i["say"])
            if t.startswith("With ") and " in your birth date, this number shapes" in t:
                continue
            if t.startswith("If "):
                continue
            if self.gender == "female" and t.startswith("For men:"):
                continue
            if self.gender == "male" and t.startswith("For women:"):
                continue
            s = soft(t, i.get("areas"))
            if s != t and (s.startswith("Linked with strain") or s == "Needs care."):
                continue
            out.append({"src": k, "pol": i.get("polarity") or "neutral", "text": s, "areas": set(i.get("areas") or [])})
        return out

    def area_lines(self, bucket, pols, limit=4, exclude_src=()):
        keys = AREA_BUCKETS[bucket]
        got = [l for l in self.all_lines() if l["areas"] & keys and l["pol"] in pols and l["src"] not in exclude_src]
        # personal numbers first, grid lines after
        order = {"psychic": 0, "destiny": 1, "master": 2, "maturity": 3, "personality": 4, "name": 5}
        got.sort(key=lambda l: order.get(l["src"], 6))
        return got[:limit]

    # ── personal-year rules ──
    def py_lines(self, cats=None, which="year"):
        items = self.d["pyRules"][which]
        out = []
        for i in items:
            if cats and i.get("cat") not in cats:
                continue
            t = clean(i["text"])
            if "sexual" in t or "Rahu sits" in t:
                continue
            out.append(t)
        return out

    def everyone(self, contains=None):
        out = [clean(i["text"]) for i in self.d["pyRules"]["everyone"]]
        return [t for t in out if not contains or contains.lower() in t.lower()]

    # ── timing ──
    def _months(self):
        Y = self.Y
        good, care = set(), set()
        self.windows = []
        seen = set()
        for t in self.d.get("timing", []):
            key = (t["polarity"], str(t["period"]))
            if key in seen:
                continue
            seen.add(key)
            days = set()
            p = t["period"]
            if p.get("month"):
                for m in p["month"]:
                    for dd in range(1, calendar.monthrange(Y, m)[1] + 1):
                        days.add((m, dd))
            for (m1, d1), (m2, d2) in p.get("dateIn", []):
                cur = date(Y, m1, d1)
                end = date(Y, m2, d2) if (m2, d2) >= (m1, d1) else date(Y, 12, 31)
                while cur <= end:
                    days.add((cur.month, cur.day))
                    cur = date.fromordinal(cur.toordinal() + 1)
                if (m2, d2) < (m1, d1):
                    cur, end = date(Y, 1, 1), date(Y, m2, d2)
                    while cur <= end:
                        days.add((cur.month, cur.day))
                        cur = date.fromordinal(cur.toordinal() + 1)
            (good if t["polarity"] == "good" else care).update(days)
            self.windows.append({"pol": t["polarity"], "say": clean(t["say"]), "label": self._period_label(p), "days": days})
        self.good_days, self.care_days = good, care
        self.months = []
        for m in range(1, 13):
            n = calendar.monthrange(Y, m)[1]
            g = [dd for dd in range(1, n + 1) if (m, dd) in good and (m, dd) not in care]
            c = [dd for dd in range(1, n + 1) if (m, dd) in care and (m, dd) not in good]
            both = [dd for dd in range(1, n + 1) if (m, dd) in care and (m, dd) in good]
            pm = reduce(self.PY + m)
            if both or (g and c):
                state, tag = "mixed", "mixed"
            elif len(g) == n:
                state, tag = "fav", "favourable"
            elif g:
                state, tag = "fav_part", self._part_tag("best", g, n)
            elif len(c) == n:
                state, tag = "careful", "careful"
            elif c:
                state, tag = "careful_part", self._part_tag("careful", c, n)
            else:
                state, tag = "steady", "steady"
            self.months.append({"m": m, "name": MONTHS[m - 1], "short": MON[m - 1], "pm": pm, "state": state, "tag": tag,
                                "good": g, "care": c, "both": both, "days": n})

    @staticmethod
    def _part_tag(word, ds, n):
        a, z = min(ds), max(ds)
        if a == 1:
            return f"{word} to {ordinal(z)}"
        if z == n:
            return f"{word} from {ordinal(a)}"
        return f"{word} {a} to {z}"

    @staticmethod
    def _period_label(p):
        if p.get("month"):
            return join_and([MONTHS[m - 1] for m in p["month"]])
        parts = []
        for (m1, d1), (m2, d2) in p.get("dateIn", []):
            if d1 == 1 and d2 == calendar.monthrange(2027, m2)[1] and m1 == m2:
                parts.append(MONTHS[m1 - 1])
            elif d1 == 1 and m2 > m1 and d2 == calendar.monthrange(2027, m2)[1]:
                parts.append(f"{MONTHS[m1 - 1]} and {MONTHS[m2 - 1]}" if m2 == m1 + 1 else f"{MONTHS[m1 - 1]} to {MONTHS[m2 - 1]}")
            else:
                parts.append(f"{d1} {MON[m1 - 1]} to {d2} {MON[m2 - 1]}")
        return join_and(parts)

    def stretches(self, pol):
        """Continuous runs of favourable (or careful) days, longest first."""
        days = sorted(self.good_days - self.care_days if pol == "good" else self.care_days - self.good_days)
        runs, cur = [], []
        for m, dd in days:
            o = date(self.Y, m, dd).toordinal()
            if cur and o == cur[-1] + 1:
                cur.append(o)
            else:
                if cur:
                    runs.append(cur)
                cur = [o]
        if cur:
            runs.append(cur)
        out = []
        for r in runs:
            a, z = date.fromordinal(r[0]), date.fromordinal(r[-1])
            out.append({"start": a, "end": z, "len": len(r), "label": self.range_label(a, z),
                        "pms": sorted({reduce(self.PY + x) for x in range(a.month, z.month + 1)})})
        return sorted(out, key=lambda x: -x["len"])

    @staticmethod
    def range_label(a, z):
        if a.day == 1 and z.day == calendar.monthrange(z.year, z.month)[1]:
            if a.month == z.month:
                return MONTHS[a.month - 1]
            sep = " and " if z.month == a.month + 1 else " to "
            return f"{MONTHS[a.month - 1]}{sep}{MONTHS[z.month - 1]}"
        if a.month == z.month:
            return f"{a.day} to {z.day} {MONTHS[a.month - 1]}"
        return f"{a.day} {MONTHS[a.month - 1]} to {z.day} {MONTHS[z.month - 1]}"

    def support_dates(self):
        return [(dd, reduce(dd)) for dd in range(1, 32) if reduce(dd) in self.support]

    def best_dates(self):
        """Support dates that fall inside a favourable stretch, by month."""
        out = []
        for m in self.months:
            ds = [dd for dd in m["good"] if reduce(dd) in self.support]
            if ds:
                out.append((m["name"], ds))
        return out

    def months_with_pm(self, n):
        return [m["name"] for m in self.months if m["pm"] == n]

    # ── age ──
    def age_lines(self):
        return self.d.get("ageItems", [])

    def ages_in_year(self):
        a = self.Y - self.dob["y"]
        return a - 1, a

    # ── name verdict ──
    def name_verdict(self):
        nb = self.b.get("name") or {}
        items = nb.get("items", [])
        care = [i for i in items if i.get("polarity") == "care" and i["id"] not in self.age_ids]
        good = [i for i in items if i.get("polarity") == "good"]
        with_birth = nb.get("withBirth")
        clash = any("clash" in (i.get("say") or "").lower() for i in care)
        if with_birth == "unfriendly" or len(care) > len(good) or clash:
            return "weak"
        if care:
            return "mixed"
        return "strong"

    # ── mobile ──
    @property
    def mobile(self):
        m = self.d.get("mobile")
        return m if m and not m.get("error") else None


# ── softening for lines that name medical or intimate specifics (kept at the level of the life area) ──
_SENSITIVE = re.compile(r"sperm|sexual|affair|diabet|urin|bone|kidney|cancer|\bdeath\b|\bdie\b|accident|surger|miscarr|two marriages|"
                        r"abortion|impoten|infertil|suicid|paraly|piles|tumou?r|operation|physical relation|unwanted physical", re.I)
_AREA_WORD = {"relationship": "relationships", "relationships": "relationships", "love": "love", "marriage": "marriage",
              "education": "studies", "health": "health", "money": "money", "family": "family", "career": "career",
              "business": "business", "mind": "peace of mind", "legal": "legal matters", "travel": "travel",
              "home": "home", "personality": "how you come across", "government": "dealings with government"}


def soft(text, areas=()):
    text = clean(text)
    if not text or not _SENSITIVE.search(text):
        return text
    keep = [s for s in re.split(r"(?<=[.!?])\s+", text) if s and not _SENSITIVE.search(s)]
    if keep:
        return " ".join(keep)
    words = []
    for a in areas or []:
        w = _AREA_WORD.get(a)
        if w and w not in words:
            words.append(w)
    return f"Linked with strain in {join_and(words)}." if words else "Needs care."


def first_sentence(t, limit=150):
    """The first sentence; if it is long, cut at a clause break (never mid-phrase)."""
    t = clean(t)
    s = re.split(r"(?<=[.!?])\s+", t)[0]
    if len(s) > limit:
        breaks = [m.start() for m in re.finditer(r"[,;:] ", s) if limit * 0.45 <= m.start() <= limit]
        if breaks:
            s = s[:breaks[-1]].rstrip() + "."
    return s


_CARE_CUE = re.compile(r"\bbut\b|\bmay\b|take care|can make|careful|avoid|prone|struggl|loss|neglect|bitter|insecure|blamed|"
                       r"swings|slip|problem|hurdle|obstacle|difficult|\bweak|\bless\b|lack|over-|overthink|anger|temper|stubborn|"
                       r"dominat|ego|delay|suspicio|jealous|lonely|depress|anxi|stress|clash|unfavourable|unlucky|guard against", re.I)


def care_part(t, limit=150):
    """The sentence of a line that carries its caution (or None if it has none)."""
    for s in re.split(r"(?<=[.!?])\s+", clean(t)):
        if _CARE_CUE.search(s):
            return first_sentence(s, limit)
    return None
