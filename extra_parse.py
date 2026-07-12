"""Robust parsing of the free-text `extra` field sent by the booking pages.

The booking page sometimes sends structured fields (birth_time, birth_place ...)
and sometimes packs everything into one `extra` string, e.g.:

    "Birth time: 7:45 PM, Place: Bhopal, MP. Gender male. Focus: career"
    "partner: Ritu Sharma 1991-03-02, married 2015, issue: constant conflict"
    '{"birth_time":"19:45","birth_place":"Bhopal"}'

This module extracts what it can WITHOUT inventing anything. Every function
returns empty strings for fields it cannot find, so callers can decide how to
degrade gracefully.
"""
from __future__ import annotations

import json
import re

# Strings the JS frontend can leak into any field. Treated as empty.
_JUNK_VALUES = {"undefined", "null", "none", "nan", "[object object]", "n/a", "na", "-", "--"}


def sanitize(value) -> str:
    """Normalise one incoming form value: trim, drop frontend junk tokens."""
    if value is None:
        return ""
    txt = str(value).strip()
    if txt.lower() in _JUNK_VALUES:
        return ""
    # kill embedded junk artefacts like "undefined undefined"
    txt = re.sub(r"\[object Object\]", "", txt)
    txt = re.sub(r"\b(?:undefined|null|NaN)\b", "", txt).strip(" ,;:-")
    return txt.strip()


def sanitize_fields(**fields) -> dict:
    return {k: sanitize(v) for k, v in fields.items()}


# ── time ────────────────────────────────────────────────────────────────────
_TIME_RE = re.compile(
    r"(?<!\d)(\d{1,2})\s*[:.∶]\s*(\d{2})\s*(a\.?m\.?|p\.?m\.?)?", re.I)
_TIME_LABELLED_RE = re.compile(
    r"(?:birth\s*time|time\s*of\s*birth|tob|time|janam\s*samay)\s*[:=-]?\s*"
    r"(\d{1,2})(?:\s*[:.∶]\s*(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)?", re.I)


def _to_24h(hh: str, mm: str | None, ampm: str | None) -> str:
    h = int(hh)
    m = int(mm) if mm else 0
    if not (0 <= m <= 59):
        return ""
    tag = (ampm or "").lower().replace(".", "")
    if tag.startswith("p") and h != 12:
        h += 12
    elif tag.startswith("a") and h == 12:
        h = 0
    if not (0 <= h <= 23):
        return ""
    return f"{h:02d}:{m:02d}"


def extract_birth_time(text: str) -> str:
    """Find a birth time in free text. Returns 'HH:MM' (24h) or ''."""
    text = text or ""
    m = _TIME_LABELLED_RE.search(text)
    if m:
        out = _to_24h(m.group(1), m.group(2), m.group(3))
        if out:
            return out
    m = _TIME_RE.search(text)
    if m:
        # Avoid matching the time part of a date like 1990-05-14
        out = _to_24h(m.group(1), m.group(2), m.group(3))
        if out:
            return out
    return ""


# ── place ───────────────────────────────────────────────────────────────────
_PLACE_LABELLED_RE = re.compile(
    r"(?:birth\s*place|place\s*of\s*birth|pob|place|city|born\s+(?:in|at))\s*[:=-]?\s*"
    r"([A-Za-z][A-Za-z .]*(?:,\s*[A-Za-z .]+){0,2})", re.I)


def extract_birth_place(text: str) -> str:
    """Find a birth place in free text. Returns the raw place string or ''."""
    text = text or ""
    m = _PLACE_LABELLED_RE.search(text)
    if m:
        place = m.group(1).strip(" .,-")
        # trim trailing labels/connectors that got swallowed ("Bhopal Gender male", "kolkata at 11:20")
        place = re.split(r"\b(?:gender|focus|male|female|time|dob|partner|at|on|around|near)\b",
                         place, flags=re.I)[0].strip(" .,-")
        if len(place) >= 3:
            return place
    # fall back: known city name appearing anywhere
    try:
        from astrology import PLACE_DB
        low = text.lower()
        for city in sorted(PLACE_DB, key=len, reverse=True):
            if re.search(rf"\b{re.escape(city)}\b", low):
                return city.title()
    except Exception:
        pass
    return ""


# ── gender / focus ──────────────────────────────────────────────────────────
def extract_gender(text: str) -> str:
    m = re.search(r"\b(male|female|man|woman|m|f)\b", text or "", re.I)
    if not m:
        return ""
    g = m.group(1).lower()
    if g in ("male", "man", "m"):
        return "male"
    if g in ("female", "woman", "f"):
        return "female"
    return ""


def extract_focus_area(text: str) -> str:
    m = re.search(r"(?:focus(?:\s*area)?|concern|question|about)\s*[:=-]\s*([^,.;\n]{3,80})",
                  text or "", re.I)
    if m:
        return m.group(1).strip()
    for kw in ("career", "marriage", "relationship", "money", "wealth", "health",
               "business", "education", "children", "foreign", "job"):
        if re.search(rf"\b{kw}\b", text or "", re.I):
            return kw
    return ""


# ── partner details ─────────────────────────────────────────────────────────
_DOB_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_DOB_DMY_RE = re.compile(r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?!\d)")


def extract_dob(text: str) -> str:
    """Return an ISO date found in text, accepting YYYY-MM-DD or DD/MM/YYYY."""
    m = _DOB_RE.search(text or "")
    if m:
        return m.group(1)
    m = _DOB_DMY_RE.search(text or "")
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"
    return ""


def extract_partner(text: str) -> dict:
    """Extract partner name/DOB from a labelled or loose phrase."""
    out = {"partner_name": "", "partner_dob": ""}
    text = text or ""
    m = re.search(r"partner(?:\s*name)?\s*[:=-]\s*([A-Za-z][A-Za-z .]{1,40})", text, re.I)
    if m:
        name = re.split(r"\b(?:dob|born|birth|\d)", m.group(1), flags=re.I)[0].strip(" .,-")
        if len(name) >= 2:
            out["partner_name"] = name
    dob = extract_dob(re.sub(r"^.*?partner", "", text, flags=re.I | re.S) if "partner" in text.lower() else text)
    if dob:
        out["partner_dob"] = dob
    return out


# ── top-level ───────────────────────────────────────────────────────────────
def parse_extra(extra: str) -> dict:
    """Parse a messy `extra` blob into structured fields. Never raises.

    Returns a dict with keys: birth_time, birth_place, gender, focus_area,
    partner_name, partner_dob, partner_birth_time, partner_birth_place,
    raw (the cleaned original text). Missing values are ''.
    """
    out = {"birth_time": "", "birth_place": "", "gender": "", "focus_area": "",
           "partner_name": "", "partner_dob": "", "partner_birth_time": "",
           "partner_birth_place": "", "raw": ""}
    extra = sanitize(extra)
    out["raw"] = extra
    if not extra:
        return out
    # JSON payloads pass straight through
    if extra.lstrip().startswith("{"):
        try:
            data = json.loads(extra)
            for k in list(out):
                if k != "raw" and data.get(k):
                    out[k] = sanitize(data[k])
            if not any(out[k] for k in out if k != "raw"):
                pass  # fall through to text scan below on the raw string
            else:
                return out
        except Exception:
            pass
    # split into client part vs partner part so times/places don't cross over
    lower = extra.lower()
    idx = lower.find("partner")
    client_part, partner_part = (extra, "") if idx < 0 else (extra[:idx], extra[idx:])

    out["birth_time"] = extract_birth_time(client_part)
    out["birth_place"] = extract_birth_place(client_part)
    out["gender"] = extract_gender(client_part)
    out["focus_area"] = extract_focus_area(extra)
    partner = extract_partner(partner_part or extra)
    out.update({k: v for k, v in partner.items() if v})
    if partner_part:
        out["partner_birth_time"] = extract_birth_time(partner_part)
        out["partner_birth_place"] = extract_birth_place(partner_part)
    return out
