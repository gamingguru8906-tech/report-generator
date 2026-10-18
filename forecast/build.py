"""Builds the Personal Year Forecast PDF for one order.

    build_forecast(name, dob, year=None, phone=None, gender=None, out_dir=".") -> (pdf_path, info)

Steps: the brain's data for the person (node data.mjs), the deck HTML (deck.py + deck_year.py), and the PDF
(node render.mjs, headless Chromium). Raises ForecastError with a readable reason if any step fails, so the
caller can fall back to the classic report and the customer is never left waiting.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


class ForecastError(RuntimeError):
    pass


def forecast_year(today=None):
    """Orders from October onward get next year's forecast."""
    today = today or datetime.date.today()
    return today.year + 1 if today.month >= 10 else today.year


def clean_phone(phone):
    d = re.sub(r"\D+", "", str(phone or ""))
    if len(d) == 12 and d.startswith("91"):
        d = d[2:]
    elif len(d) == 11 and d.startswith("0"):
        d = d[1:]
    return d if re.fullmatch(r"[6-9]\d{9}", d) else None


def _node():
    exe = shutil.which("node")
    if not exe:
        raise ForecastError("node is not installed on this server")
    return exe


def brain_data(name, dob_iso, year, phone=None, gender=None, concern=None, timeout=120):
    payload = {"name": name, "dob": dob_iso, "year": int(year)}
    if phone:
        payload["phone"] = phone
    if gender:
        payload["gender"] = gender
    if concern:
        payload["concern"] = concern
    p = subprocess.run([_node(), os.path.join(HERE, "data.mjs")], input=json.dumps(payload), capture_output=True,
                       text=True, timeout=timeout, cwd=HERE)
    if p.returncode != 0:
        raise ForecastError(f"brain data failed: {(p.stderr or p.stdout)[-600:]}")
    try:
        d = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e:
        raise ForecastError(f"brain data unreadable: {e!r}: {p.stdout[-300:]}")
    if not d.get("ok"):
        raise ForecastError(f"brain data refused the input: {d.get('error')}")
    return d


def build_html(data):
    from .deck import Deck
    from .deck_year import YearPages

    class ForecastDeck(Deck, YearPages):
        pass

    k = ForecastDeck(data)
    k.pg.subs = {"{{FILE}}": f"{k.r.P:02d}-{k.Y}"}
    k.cover(); k.letter(); k.contents(); k.glance(); k.statement(); k.method(); k.planets_page(); k.worked()
    k.pair_opener(); k.psychic(); k.destiny(); k.pair(); k.pair_remedies()
    k.loshu(); k.planes_page(); k.missing_page(); k.repeated()
    if k.name_open():
        k.name_meaning(); k.name_offer(); k.pers_mat()
    k.year_open(); k.year_rules(); k.asks()
    for area in ("career", "money", "relationships", "health"):
        k.area_page(area)
    k.timing_map(); k.stretches_page(); k.month_pages()
    k.practices(); k.bracelet(); k.tracker()
    k.watch_page(); k.watch_offer()
    k.mobile_pages()
    k.further(); k.one_page(); k.thanks()
    title = f"Personal Year Forecast {k.Y} for {k.r.name_full}"
    meta = {"pages": len(k.pg.slides), "year": k.Y, "mulank": k.r.P, "theme": k.T.id, "mobile": bool(k.mob)}
    return k.pg.html(title), meta


def render_pdf(html_path, pdf_path, timeout=540):
    p = subprocess.run([_node(), os.path.join(HERE, "render.mjs"), html_path, pdf_path], capture_output=True, text=True,
                       timeout=timeout, cwd=HERE)
    line = (p.stdout.strip().splitlines() or [""])[-1]
    try:
        res = json.loads(line)
    except Exception:
        raise ForecastError(f"renderer gave no result (exit {p.returncode}): {(p.stderr or p.stdout)[-600:]}")
    if not res.get("ok") or not os.path.exists(pdf_path):
        raise ForecastError(f"renderer failed: {res.get('error', '')[-600:]}")
    return res


def _slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_") or "Customer"


def build_forecast(name, dob, year=None, phone=None, gender=None, out_dir=".", concern=None, keep_html=False):
    if isinstance(dob, (datetime.date, datetime.datetime)):
        dob_iso = dob.strftime("%Y-%m-%d")
    else:
        dob_iso = str(dob).strip()
    year = int(year or forecast_year())
    phone = clean_phone(phone)
    if phone and not concern:
        # the mobile number is read against what the year is about (the personal year's own themes)
        from .content import PY_FRAME, reduce
        y_, m_, d_ = (int(x) for x in dob_iso.split("-"))
        concern = PY_FRAME[reduce(d_ + m_ + sum(int(c) for c in str(year)))]["concern"]
    data = brain_data(name, dob_iso, year, phone=phone, gender=gender, concern=concern)
    html, meta = build_html(data)
    os.makedirs(out_dir, exist_ok=True)
    fname = f"VeshannAstro_{year}_Forecast_{_slug(name)}.pdf"
    pdf_path = os.path.abspath(os.path.join(out_dir, fname))
    tmp = tempfile.mkdtemp(prefix="forecast_")
    html_path = os.path.join(tmp, "forecast.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    try:
        res = render_pdf(html_path, pdf_path)
    finally:
        if not keep_html:
            shutil.rmtree(tmp, ignore_errors=True)
    meta.update({"render_ms": res.get("ms"), "fit": res.get("fit"), "overflow": res.get("overflow"), "html": html_path if keep_html else None})
    return pdf_path, meta
