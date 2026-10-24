"""The WhatsApp summary card: one 9:16 image that says the year in a glance.

    build_card(data, png_path) -> facts

It reads the same brain data as the PDF (so it never disagrees with it) and is drawn in the same design as the
person's report (by Mulank). Facts: the year's theme, three things to do, the three best months, the lucky (support)
numbers and the colour to wear. The same facts are what Kamala reads out in the voice note.
"""
import json
import os
import shutil
import subprocess
import tempfile

from .content import first_sentence, pl
from .kit import esc

HERE = os.path.dirname(os.path.abspath(__file__))

RANK = {"fav": 3, "fav_part": 2, "steady": 1, "mixed": 0, "careful_part": -1, "careful": -2}


def summary_facts(r):
    """The card's facts from a Reading (forecast.content.Reading)."""
    dos = [first_sentence(t, 84) for t in r.py_lines(["do"])]
    if len(dos) < 3:
        dos += [first_sentence(t, 84) for t in r.everyone()]
    seen, three = set(), []
    for d in dos:
        if d and d.lower() not in seen:
            seen.add(d.lower())
            three.append(d)
        if len(three) == 3:
            break
    best = sorted(r.months, key=lambda m: (-RANK.get(m["state"], 0), -(len(m["good"]) - len(m["care"])), m["m"]))[:3]
    best = sorted(best, key=lambda m: m["m"])
    colours = r.py_lines(["colours"])
    return {
        "first": r.first, "name": r.name_full, "year": r.Y, "personal_year": r.PY, "planet": pl(r.PY),
        "theme": r.frame["tag"], "gist": r.frame["gist"], "dos": three,
        "best_months": [m["name"] for m in best], "lucky_numbers": [int(n) for n in r.support],
        "colour": first_sentence(colours[0], 72) if colours else "",
    }


def card_html(data):
    from .deck import Deck
    from .deck_year import YearPages

    class CardDeck(Deck, YearPages):
        pass

    k = CardDeck(data)
    r, T, Y, L = k.r, k.T, k.Y, k.L
    f = summary_facts(r)
    dos = "".join(
        f'<div style="display:flex;gap:16px;align-items:flex-start;padding:17px 0;border-bottom:1.5px solid {T.RULE}">'
        f'<span class="num" style="font-size:48px;color:{T.BERRY};width:40px;flex:none">{i}</span>'
        f'<span class="lead" style="font-size:24px;line-height:1.38">{esc(t)}</span></div>' for i, t in enumerate(f["dos"], 1))
    months = "".join(f'<span class="disp b" style="display:inline-block;background:{T.PINK};color:{T.INK};font-size:26px;padding:12px 22px;margin:0 12px 12px 0">{esc(m)}</span>'
                     for m in f["best_months"])
    nums = "&#8201;&#183;&#8201;".join(str(n) for n in f["lucky_numbers"]) or str(r.PY)
    inner = f"""
{k.head("For " + esc(f["first"]), f"Your {Y}<br>at a glance")}
<div class="disp" style="font-size:56px;line-height:1.05;color:{T.BERRY};margin:10px 0 10px">{esc(f["theme"])}</div>
<div class="lead" style="font-size:21px;opacity:.85">Personal Year {r.PY}, {esc(f["planet"])}: {esc(f["gist"])}.</div>
<div class="caps" style="font-size:15px;letter-spacing:.14em;margin:44px 0 6px;color:{T.NAVY}">Three things to do</div>
<div>{dos}</div>
<div class="caps" style="font-size:15px;letter-spacing:.14em;margin:40px 0 14px;color:{T.NAVY}">Your best months</div>
<div>{months}</div>
<div style="display:flex;gap:16px;margin-top:26px">
  <div class="tile" style="flex:1;background:{T.NAVY};color:{T.WHITE};padding:24px 24px">
    <div class="small" style="opacity:.85;font-size:16px">Lucky numbers</div><div class="num" style="font-size:{68 if len(f["lucky_numbers"]) <= 3 else 50}px;margin-top:10px;white-space:nowrap">{nums}</div></div>
  <div class="tile" style="flex:1.4;background:{T.LBLUE};color:{T.INK};padding:24px 24px">
    <div class="small" style="opacity:.85;font-size:16px">Wear</div><div class="lead" style="font-size:22px;margin-top:10px;line-height:1.35">{esc(f["colour"] or "Your report lists your colours.")}</div></div>
</div>
<div class="small" style="margin-top:40px;opacity:.8;font-size:16px">Your full report is in the PDF. Questions? Reply on WhatsApp, +91 76469 52745.</div>
{L.sparkle(T.PINK, 54, 610, 64)}
{L.blob(T.LBLUE, 300, 150, 470, 1150, "bumps")}
"""
    k.pg.add(T.CREAM, inner, foot=False)
    return k.pg.html(f"Your {Y} at a glance"), f


def _node():
    exe = shutil.which("node")
    if not exe:
        raise RuntimeError("node is not installed on this server")
    return exe


def build_card(data, png_path, timeout=240):
    """Writes the card PNG (1080 x 1920) and returns its facts. Raises on failure (the PDF never depends on it)."""
    html, facts = card_html(data)
    tmp = tempfile.mkdtemp(prefix="card_")
    try:
        hp = os.path.join(tmp, "card.html")
        with open(hp, "w", encoding="utf-8") as fh:
            fh.write(html)
        p = subprocess.run([_node(), os.path.join(HERE, "card.mjs"), hp, png_path], capture_output=True, text=True,
                           timeout=timeout, cwd=HERE)
        line = (p.stdout.strip().splitlines() or [""])[-1]
        res = json.loads(line) if line.startswith("{") else {}
        if not res.get("ok") or not os.path.exists(png_path):
            raise RuntimeError(f"card render failed: {(res.get('error') or p.stderr or p.stdout)[-400:]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return facts
