"""Bridge: hosted Razorpay Payment Pages -> automatic report fulfilment.

The live veshannastro.co.in numerology cards link to hosted Razorpay Payment
Pages (rzp.io/...). Those payments are NOT created by this backend, so they
carry no `source=veshann_report` tag — historically they were fulfilled by
hand. This module recognises them from the webhook payload and maps the
page's form answers (delivered in the payment's `notes`) onto a report order.

Live pages this is built against (July 2026):
  pl_T9SWt2cSiHAi7U  ₹999  Complete Numerology     notes: name, email, phone, date_of_birth
  pl_T97soQ0xCE8UrD  ₹299  Name/Mobile/Baby        notes: service, name, email, phone, date_of_birth
  pl_T9SMoVftvcrzMQ  ₹499  Forecast/Business       notes: service, name, email, phone, date_of_birth_(...)
  pl_T98DsqXf7Gtt8N  ₹299  Compatibility           notes: girls_name, girls_dob, boys_name, boys_dob, email, phone

Safety rules (this Razorpay account also takes consultation/shop payments):
  - a report is fulfilled ONLY when a customer date of birth AND email are
    found in the notes AND a product can be confidently resolved
  - resolution order: explicit page-id map -> compatibility field shape ->
    `service` dropdown keywords -> page title/description keywords -> amount
  - kill switch: set env PP_BRIDGE=off to disable the whole bridge
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime

# page-id -> product key (env-overridable, JSON). Used when the webhook
# payload exposes the payment page id (payment_link/page fields or notes).
DEFAULT_PAGE_MAP = {
    "pl_T9SWt2cSiHAi7U": "complete",
    "pl_T98DsqXf7Gtt8N": "love",
    # pl_T97soQ0xCE8UrD and pl_T9SMoVftvcrzMQ sell multiple products —
    # resolved via their `service` dropdown instead.
}

# fallback when only the amount is known (paise)
DEFAULT_AMOUNT_MAP = {99900: "complete", 49900: "forecast", 29900: "name"}

SERVICE_KEYWORDS = [
    ("mobile", "mobile"), ("phone", "mobile"),
    ("baby", "baby"),
    ("business", "business"), ("brand", "business"),
    ("forecast", "forecast"), ("year", "forecast"),
    ("compat", "love"), ("love", "love"), ("match", "love"),
    ("complete", "complete"), ("full", "complete"),
    ("palm", "palmistry"),
    ("name", "name"),          # last: "name" appears inside other labels
]

DESCRIPTION_KEYWORDS = [
    ("architecture of your life", "complete"),
    ("compatibility", "love"),
    ("year ahead", "forecast"),
    ("palmistry", "palmistry"),
    ("numerology report", None),   # recognised as ours, product via service/amount
]


def _env_json(name, default):
    try:
        raw = os.environ.get(name, "")
        return {**default, **json.loads(raw)} if raw else default
    except Exception:
        return default


def enabled() -> bool:
    return os.environ.get("PP_BRIDGE", "on").strip().lower() not in ("off", "0", "false", "no")


def normalize_notes(notes: dict) -> dict:
    """Lower-case keys, collapse punctuation to underscores, stringify values."""
    out = {}
    for k, v in (notes or {}).items():
        nk = re.sub(r"[^a-z0-9]+", "_", str(k).strip().lower()).strip("_")
        if v is None:
            continue
        sv = str(v).strip()
        if sv:
            out[nk] = sv
    return out


def parse_dob_any(text: str) -> str:
    """Parse a date in any common Indian/ISO format -> 'YYYY-MM-DD' or ''."""
    t = (text or "").strip()
    if not t:
        return ""
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""
    m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", t)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo > 12 and d <= 12:      # US-style slipped through
            d, mo = mo, d
        return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""
    for fmt in ("%d %b %Y", "%d %B %Y", "%b %d %Y", "%B %d %Y", "%d %b, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(re.sub(r"\s+", " ", t), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _find(n: dict, *patterns, exclude=()):
    """First value whose key matches any regex pattern and no exclude pattern."""
    for k, v in n.items():
        if any(re.search(p, k) for p in patterns) and not any(re.search(x, k) for x in exclude):
            return v
    return ""


def _service_product(n: dict) -> str:
    svc = _find(n, r"^service", r"report_type", r"^report$", r"which_report")
    if not svc:
        return ""
    low = svc.lower()
    for kw, product in SERVICE_KEYWORDS:
        if kw in low:
            return product
    return ""


def match_payment_page(notes: dict, entity: dict, products: dict):
    """Map a non-tagged payment to a report order.

    notes    – raw notes dict from the payment/order entity
    entity   – the payment entity (for email/contact/amount/description)
    products – app.PRODUCTS, to validate the resolved product key

    Returns an order dict (product, report_type, name, dob, email, gender,
    extra, phone) or None when this payment is not confidently one of ours.
    """
    if not enabled():
        return None
    n = normalize_notes(notes)
    if not n:
        return None

    email = _find(n, r"email") or (entity.get("email") or "")
    phone = _find(n, r"^phone", r"contact", r"whatsapp", r"mobile") or (entity.get("contact") or "")
    desc = (entity.get("description") or "").lower()

    # 1) compatibility page: unmistakable field shape
    girls_name = _find(n, r"girl.*name", r"bride.*name", r"her_name")
    boys_name = _find(n, r"boy.*name", r"groom.*name", r"his_name")
    if girls_name and boys_name:
        girls_dob = parse_dob_any(_find(n, r"girl.*dob", r"girl.*birth", r"bride.*dob"))
        boys_dob = parse_dob_any(_find(n, r"boy.*dob", r"boy.*birth", r"groom.*dob"))
        if not (girls_dob and email):
            return None
        extra = f"{boys_name} {boys_dob}".strip() if boys_dob else boys_name
        return {"product": "love", "name": girls_name, "dob": girls_dob, "email": email,
                "gender": "", "extra": extra, "phone": phone}

    # customer identity (required for every other product)
    name = _find(n, r"^name$", r"^full_name", r"^your_name", r"customer_name") \
        or _find(n, r"name", exclude=(r"business", r"brand", r"baby", r"partner", r"user"))
    dob = parse_dob_any(_find(n, r"date_of_birth", r"^dob", r"birth_date", r"_dob"))
    if not (name and dob and email):
        return None

    # 2..4) resolve product: page map -> service dropdown -> description -> amount
    page_map = _env_json("PP_PAGE_MAP", DEFAULT_PAGE_MAP)
    page_id = entity.get("payment_page") or entity.get("payment_link_id") or \
        _find(n, r"payment_page", r"^page_id")
    product = page_map.get(page_id, "") if page_id else ""
    if not product:
        product = _service_product(n)
    if not product:
        for kw, prod in DESCRIPTION_KEYWORDS:
            if kw in desc:
                if prod:
                    product = prod
                break
    if not product:
        amount_map = {int(k): v for k, v in _env_json(
            "PP_AMOUNT_MAP", {str(k): v for k, v in DEFAULT_AMOUNT_MAP.items()}).items()}
        product = amount_map.get(int(entity.get("amount") or 0), "")
    if not product or product not in products:
        return None

    # product-specific extra payload
    extra = ""
    if product == "mobile":
        extra = _find(n, r"number_to_analy", r"mobile_number", r"analy") or phone
    elif product == "business":
        extra = _find(n, r"business", r"brand", r"company", exclude=(r"dob", r"birth", r"date"))
    elif product == "baby":
        extra = _find(n, r"baby", r"prefer", r"letter")
    elif product in ("complete", "forecast") and phone:
        digits = re.sub(r"\D+", "", phone)[-10:]
        if len(digits) == 10:
            extra = f"mobile: {digits}"     # bonus mobile-energy section / free mobile reading in the forecast
    elif product == "palmistry":
        extra = _find(n, r"^extra", r"palm") or ""
        if not extra.lower().startswith("palm"):
            extra = "palm|" + "|".join(x for x in [
                ("dh:" + _find(n, r"dominant").lower()) if _find(n, r"dominant") else "",
            ] if x)
    gender = (_find(n, r"gender", r"^sex$") or "").lower()
    return {"product": product, "name": name, "dob": dob, "email": email,
            "gender": gender if gender in ("male", "female") else "",
            "extra": extra, "phone": phone}
