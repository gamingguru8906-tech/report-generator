"""Veshann Astro — palmistry analysis engine.

Calculation-first in spirit: this engine works ONLY from what the customer
actually provided — the guided self-observation answers from the booking page
and the uploaded palm photographs. It never pretends to have machine-read a
palm image; photos are quality-checked, embedded for reference, and flagged
for human review. Missing observations degrade to honest 'unknown' readings.

The booking page packs the palm inputs into the order's `extra` field in a
compact pipe format (Razorpay notes values are limited to 256 chars):

    palm|dh:right|hs:fire|ll:long_curved|hd:sloping|ht:ends_index|ft:faint|up:<upload_id>|fc:career

JSON ({"dominant_hand": ...}) is also accepted for direct API callers.
"""
from __future__ import annotations

import json
import os
import re

import palm_content as PC

UPLOAD_DIR = os.environ.get("PALM_UPLOAD_DIR", "/tmp/palm_uploads")

_FIELD_MAP = {
    "dh": "dominant_hand", "hs": "hand_shape", "ll": "life_line",
    "hd": "head_line", "ht": "heart_line", "ft": "fate_line",
    "up": "upload_id", "fc": "focus_area",
}
_KEYS = set(_FIELD_MAP.values())


def parse_palm_extra(extra: str) -> dict:
    """Parse the palm payload from `extra`. Accepts pipe format, JSON, or
    loose labelled text. Never raises; unknown fields come back ''. """
    out = {k: "" for k in _KEYS}
    txt = (extra or "").strip()
    if not txt:
        return out
    if txt.startswith("{"):
        try:
            data = json.loads(txt)
            for k in _KEYS:
                if data.get(k):
                    out[k] = str(data[k]).strip().lower() if k != "upload_id" else str(data[k]).strip()
            return out
        except Exception:
            pass
    if txt.lower().startswith("palm"):
        for part in txt.split("|")[1:]:
            if ":" not in part:
                continue
            k, _, v = part.partition(":")
            field = _FIELD_MAP.get(k.strip().lower())
            if field and v.strip():
                out[field] = v.strip() if field == "upload_id" else v.strip().lower()
        return out
    # loose text fallback: "dominant hand right, heart line ends under index..."
    m = re.search(r"\b(left|right)\b[- ]?hand", txt, re.I) or re.search(r"hand\s*[:=-]?\s*(left|right)", txt, re.I)
    if m:
        out["dominant_hand"] = m.group(1).lower()
    for shape in PC.HAND_SHAPE:
        if re.search(rf"\b{shape}\b", txt, re.I):
            out["hand_shape"] = shape
            break
    return out


def photo_paths(upload_id: str) -> dict:
    """Locate stored palm photos for an upload id. Returns {'left': path|None, 'right': path|None}."""
    out = {"left": None, "right": None}
    if not upload_id or not re.fullmatch(r"[A-Za-z0-9_-]{4,64}", upload_id):
        return out
    base = os.path.join(UPLOAD_DIR, upload_id)
    for side in ("left", "right"):
        for ext in (".jpg", ".jpeg", ".png"):
            p = os.path.join(base, side + ext)
            if os.path.exists(p):
                out[side] = p
                break
    return out


def assess_photo(path: str) -> dict:
    """Basic, honest image quality assessment via Pillow. Returns
    {ok, notes: [..], width, height}. Never raises."""
    result = {"ok": False, "notes": [], "width": 0, "height": 0}
    if not path:
        result["notes"].append("photo not provided")
        return result
    try:
        from PIL import Image, ImageStat
        with Image.open(path) as im:
            im = im.convert("L")
            result["width"], result["height"] = im.size
            mean = ImageStat.Stat(im).mean[0]
            if min(im.size) < 500:
                result["notes"].append("low resolution — fine line detail is limited")
            if mean < 60:
                result["notes"].append("image is dark — some features may be under-read")
            elif mean > 215:
                result["notes"].append("image is over-bright — line depth is hard to judge")
            result["ok"] = not result["notes"]
            if result["ok"]:
                result["notes"].append("adequate for major-line review")
    except Exception as e:
        result["notes"].append(f"photo could not be opened ({type(e).__name__})")
    return result


def compute_palm_profile(full_name, dob, gender="", extra="", focus_area="", email=""):
    """Build the palmistry profile dict consumed by palmistry_report.py."""
    from datetime import datetime, date
    if isinstance(dob, str):
        dob = datetime.strptime(dob.strip()[:10], "%Y-%m-%d").date()
    data = parse_palm_extra(extra)
    dominant = data["dominant_hand"] if data["dominant_hand"] in ("left", "right") else ""
    photos = photo_paths(data["upload_id"])
    quality = {side: assess_photo(p) for side, p in photos.items()}

    provided = [k for k in ("hand_shape", "life_line", "head_line", "heart_line", "fate_line") if data[k]]
    limitations = []
    if not dominant:
        limitations.append("Dominant hand was not specified; the reading treats observations as belonging to the active hand.")
    if not photos["left"] and not photos["right"]:
        limitations.append("No palm photographs were available at generation time; the reading rests on your guided observations alone.")
    else:
        for side in ("left", "right"):
            if photos[side] and not quality[side]["ok"]:
                limitations.append(f"{side.title()} palm photo: " + "; ".join(quality[side]["notes"]) + ".")
            if not photos[side]:
                limitations.append(f"{side.title()} palm photo was not provided; dominant/non-dominant comparison is limited.")
    missing = [k.replace("_", " ") for k in ("hand_shape", "life_line", "head_line", "heart_line", "fate_line") if not data[k]]
    if missing:
        limitations.append("Not observed/selected: " + ", ".join(missing) + " — those sections give the balanced range of meanings instead of a specific verdict.")

    return {
        "name": (full_name or "Customer").strip(),
        "dob": dob, "gender": gender, "email": email,
        "focus_area": (focus_area or data["focus_area"] or "general life patterns"),
        "dominant_hand": dominant,
        "hand_shape": data["hand_shape"],
        "life_line": data["life_line"], "head_line": data["head_line"],
        "heart_line": data["heart_line"], "fate_line": data["fate_line"],
        "upload_id": data["upload_id"], "photos": photos, "photo_quality": quality,
        "provided_count": len(provided), "limitations": limitations,
        "shape_profile": PC.HAND_SHAPE.get(data["hand_shape"]),
        "life_profile": PC.line_reading(PC.LIFE_LINE, data["life_line"]),
        "head_profile": PC.line_reading(PC.HEAD_LINE, data["head_line"]),
        "heart_profile": PC.line_reading(PC.HEART_LINE, data["heart_line"]),
        "fate_profile": PC.line_reading(PC.FATE_LINE, data["fate_line"]),
    }
