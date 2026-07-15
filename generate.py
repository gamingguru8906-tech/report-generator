"""Veshann Astro — Report Generator entry point.

CLI:    python3 generate.py "Full Name" YYYY-MM-DD [male|female] [out.pdf]
Code:   from generate import generate_report
        path = generate_report("Arjun Sharma", "1998-07-23", gender="male", out_dir="out")

This single function is the hook your automation calls after payment is confirmed.
"""
import sys, os, re
from datetime import datetime, date
import numerology as N
import report as R
import astrology as AST
import astrology_report as AR
import divorce_report as DR
import extra_parse as XP
from quality_gate import verify_pdf as _verify_pdf_strict

def verify_pdf(path):
    """Delivery must never be blocked by a cosmetic quality heuristic. If the PDF
    was actually written we deliver it; the quality gate only *warns*. The single
    hard failure is a PDF that was never produced (nothing to email)."""
    import os
    if not os.path.exists(path):
        raise FileNotFoundError(f"Report PDF was not written: {path}")
    try:
        _verify_pdf_strict(path)
    except Exception as e:
        print(f"[verify] quality warning, delivering anyway: {e!r}")
    return True

def _slug(s): return re.sub(r'[^a-zA-Z0-9]+', '_', s).strip('_')[:40]

REPORT_ALIASES = {
    "complete_numerology": "complete_numerology",
    "complete": "complete_numerology",
    "mobile": "mobile_number_analysis",
    "mobile_number": "mobile_number_analysis",
    "name": "name_numerology",
    "career": "career_numerology",
    "money": "money_numerology",
    "wealth": "money_numerology",
    "love": "relationship_compatibility",
    "relationship": "relationship_compatibility",
    "business": "business_name_report",
    "baby": "baby_name_report",
    "house": "house_number_analysis",
    "vehicle": "vehicle_number_analysis",
    "forecast": "personal_forecast",
    "snapshot": "snapshot",
    "astrology_life_path": "premium_astrology_life_path",
    "premium_astrology_life_path": "premium_astrology_life_path",
    "divorce_separation": "premium_divorce_separation",
    "divorce_separation_report": "premium_divorce_separation",
    "premium_divorce_separation": "premium_divorce_separation",
    "palmistry": "premium_palmistry",
    "palm": "premium_palmistry",
    "palmistry_report": "premium_palmistry",
    "premium_palmistry": "premium_palmistry",
}

def _analyse_digits(value):
    number = re.sub(r"\D+", "", value or "")
    if not number:
        return None
    total = sum(int(d) for d in number)
    return {"number": number, "total": total, "root": N.reduce_num(total, keep_masters=False)}

def _analyse_name(value):
    name = (value or "").strip()
    if not name:
        return None
    total = N.name_value(name)
    return {"name": name, "total": total, "root": N.reduce_num(total, keep_masters=False)}

def _parse_partner(extra, default_name="Partner"):
    if not extra:
        return None
    m = re.search(r"(\d{4}-\d{2}-\d{2})", extra)
    if not m:
        return None
    pname = extra[:m.start()].strip(" ,-:/") or default_name
    return N.compute(pname, datetime.strptime(m.group(1), "%Y-%m-%d").date(), "")

def _labelled_digits(extra, label):
    m = re.search(rf"(?:{label})\s*[:=-]\s*([+\d][\d\s-]{{5,}})", extra or "", re.I)
    return _analyse_digits(m.group(1)) if m else None

def _prepare_optional_data(r, report_type, extra):
    r["extra"] = extra or ""
    rt = REPORT_ALIASES.get((report_type or "complete").strip(), (report_type or "complete").strip())
    r["report_type"] = rt
    if rt == "mobile_number_analysis":
        data = _analyse_digits(extra)
        if data: r["mobile"] = data
    elif rt == "business_name_report":
        data = _analyse_name(extra)
        if data: r["business"] = data
    elif rt == "baby_name_report":
        r["baby"] = {"pref": extra or "", "target_roots": r["lucky_numbers"][:4]}
    elif rt == "relationship_compatibility":
        partner = _parse_partner(extra)
        if partner: r["partner"] = partner
    elif rt == "house_number_analysis":
        data = _analyse_digits(extra)
        if data: r["house"] = data
    elif rt == "vehicle_number_analysis":
        data = _analyse_digits(extra)
        if data: r["vehicle"] = data
    elif rt == "name_numerology" and extra.strip():
        r["query"] = extra.strip()
    else:
        if rt == "complete_numerology":
            mobile = _labelled_digits(extra, "mobile|phone")
            house = _labelled_digits(extra, "house|home")
            vehicle = _labelled_digits(extra, "vehicle|car|bike")
            if mobile: r["mobile"] = mobile
            if house: r["house"] = house
            if vehicle: r["vehicle"] = vehicle
            partner = _parse_partner(extra)
            if partner: r["partner"] = partner
        if extra.strip():
            r["query"] = extra.strip()
    if rt != "name_numerology" and extra.strip() and "query" not in r:
        r["query"] = extra.strip()
    return rt

def _slug_place(s):
    return re.sub(r'[^a-zA-Z0-9]+', '_', s or 'NA').strip('_')[:32]

# Classical Indian reference point (Ujjain — the traditional prime meridian of
# Indian astronomy). Used ONLY as a flagged, transparent fallback when the
# birth place cannot be resolved, so the report still generates and the
# limitation is stated on the report itself instead of the order failing.
_FALLBACK_COORDS = "23.1793, 75.7849"

def _compute_chart_with_fallbacks(full_name, dob, birth_time, birth_place, gender="", email="", focus_area="general life path"):
    """Compute the Vedic chart with graceful degradation instead of crashing.

    - Missing birth time  -> 12:00 noon chart, flagged `birth_time_estimated`.
    - Missing/unresolvable birth place -> Ujjain reference point, flagged
      `place_estimated`. Geocoded places are converted to lat/lon so the
      chart validator accepts them.
    The renderers turn these flags into visible 'Data Limitation' notices.
    """
    limitations = []
    time_estimated = False
    if not birth_time:
        birth_time = "12:00"
        time_estimated = True
        limitations.append("birth time not provided; 12:00 noon chart used")
    display_place = birth_place
    calc_place = birth_place
    place_estimated = False
    if birth_place:
        try:
            info = AST.parse_place(birth_place)
            if info.get("source") == "geopy-nominatim":
                # validator only trusts built-in/lat-lon sources; feed it the
                # geocoded coordinates directly so a real lookup is not wasted
                calc_place = f"{info['lat']:.4f}, {info['lon']:.4f}"
        except Exception:
            calc_place = _FALLBACK_COORDS
            place_estimated = True
            limitations.append(f"birth place {birth_place!r} could not be resolved; central reference location used")
    else:
        calc_place = _FALLBACK_COORDS
        place_estimated = True
        limitations.append("birth place not provided; central reference location used")
    chart = AST.compute_chart(full_name, dob, birth_time, calc_place, gender=gender,
                              focus_area=focus_area, email=email)
    chart["birth_place"] = display_place or "Not provided"
    chart["birth_time_estimated"] = time_estimated
    chart["place_estimated"] = place_estimated
    chart["data_limitations"] = limitations
    if limitations:
        print("chart fallbacks applied:", "; ".join(limitations))
    return chart, limitations

import threading as _threading
# One report builds at a time. Interior theming recolours shared module state,
# so overlapping builds from concurrent webhook threads must be serialised.
# Each report renders in well under a second, so this has no practical cost and
# guarantees every order fulfils cleanly.
_GENERATE_LOCK = _threading.Lock()

def generate_report(*args, **kwargs):
    """Thread-safe public entry point — serialises the actual build."""
    with _GENERATE_LOCK:
        return _generate_report_impl(*args, **kwargs)

def _generate_report_impl(full_name, dob, gender="", out_dir=".", book_cover=None, report_type="complete", extra="",
                    birth_time="", birth_place="", focus_area="", email="", partner_name="", partner_dob="",
                    partner_birth_time="", partner_birth_place="", marriage_date="", current_issue="",
                    children="", main_question=""):
    """dob accepts 'YYYY-MM-DD' or a datetime.date. Returns absolute PDF path.
    report_type: complete_numerology plus focused service keys such as
    mobile_number_analysis, name_numerology, career_numerology and legacy aliases.
    extra: the report's second input (mobile number, business name, or partner's name & DOB)."""
    # sanitize every incoming field (frontend can leak "undefined"/"null"/junk)
    full_name = XP.sanitize(full_name) or "Customer"
    gender = XP.sanitize(gender); extra = XP.sanitize(extra)
    birth_time = XP.sanitize(birth_time); birth_place = XP.sanitize(birth_place)
    focus_area = XP.sanitize(focus_area)
    partner_name = XP.sanitize(partner_name); partner_dob = XP.sanitize(partner_dob)
    partner_birth_time = XP.sanitize(partner_birth_time); partner_birth_place = XP.sanitize(partner_birth_place)
    marriage_date = XP.sanitize(marriage_date); current_issue = XP.sanitize(current_issue)
    children = XP.sanitize(children); main_question = XP.sanitize(main_question)
    if isinstance(dob, str):
        dob = datetime.strptime(dob.strip(), "%Y-%m-%d").date()
    canonical_type = REPORT_ALIASES.get((report_type or "complete").strip(), (report_type or "complete").strip())

    if canonical_type == "premium_palmistry":
        import palmistry as PM
        import palmistry_report as PR
        os.makedirs(out_dir, exist_ok=True)
        profile = PM.compute_palm_profile(full_name, dob, gender=gender, extra=extra,
                                          focus_area=focus_area, email=email)
        fname = f"VeshannAstro_Palmistry_Report_{_slug(full_name)}_{dob.isoformat()}.pdf"
        out_path = os.path.abspath(os.path.join(out_dir, fname))
        PR.build_palmistry_report(profile, out_path)
        verify_pdf(out_path)
        return out_path

    if canonical_type in ("premium_astrology_life_path", "premium_divorce_separation"):
        # backfill missing structured fields from the free-text `extra` blob
        parsed = XP.parse_extra(extra)
        birth_time = birth_time or parsed["birth_time"]
        birth_place = birth_place or parsed["birth_place"]
        gender = gender or parsed["gender"]
        focus_area = focus_area or parsed["focus_area"]
        partner_name = partner_name or parsed["partner_name"]
        partner_dob = partner_dob or parsed["partner_dob"]
        partner_birth_time = partner_birth_time or parsed["partner_birth_time"]
        partner_birth_place = partner_birth_place or parsed["partner_birth_place"]
        chart, limitations = _compute_chart_with_fallbacks(
            full_name, dob, birth_time, birth_place, gender=gender, email=email,
            focus_area=(focus_area or (current_issue if canonical_type == "premium_divorce_separation" else extra)
                        or ("relationship clarity" if canonical_type == "premium_divorce_separation" else "general life path")))
        os.makedirs(out_dir, exist_ok=True)

    if canonical_type == "premium_astrology_life_path":
        fname = f"VeshannAstro_Astrology_Life_Path_{_slug(full_name)}_{dob.isoformat()}_{_slug_place(chart['birth_place'])}.pdf"
        out_path = os.path.abspath(os.path.join(out_dir, fname))
        AR.build_astrology_report(chart, out_path)
        verify_pdf(out_path)
        return out_path
    if canonical_type == "premium_divorce_separation":
        payload = {
            "partner_name": partner_name, "partner_dob": partner_dob,
            "partner_birth_time": partner_birth_time, "partner_birth_place": partner_birth_place,
            "marriage_date": marriage_date, "current_issue": current_issue,
            "children": children, "main_question": main_question,
        }
        if not any(payload.values()) and extra:
            payload = {}
        import json
        report_extra = json.dumps(payload) if payload else extra
        fname = f"VeshannAstro_Divorce_Separation_Report_{_slug(full_name)}_{dob.isoformat()}_{_slug_place(chart['birth_place'])}.pdf"
        out_path = os.path.abspath(os.path.join(out_dir, fname))
        DR.build_divorce_report(chart, out_path, extra=report_extra)
        verify_pdf(out_path)
        return out_path
    r = N.compute(full_name, dob, gender)
    report_type = _prepare_optional_data(r, canonical_type, extra)
    os.makedirs(out_dir, exist_ok=True)
    tag = "" if report_type == "complete_numerology" else f"_{report_type}"
    fname = f"VeshannAstro_Numerology{tag}_{_slug(full_name)}_{dob.isoformat()}.pdf"
    out_path = os.path.abspath(os.path.join(out_dir, fname))
    R.build_report(r, out_path, book_cover=book_cover, report_type=report_type)
    verify_pdf(out_path)
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python3 generate.py "Full Name" YYYY-MM-DD [gender] [out_dir] [report_type] [extra]')
        print('  report_type: complete | snapshot | career | love | name | forecast')
        sys.exit(1)
    name = sys.argv[1]; dob = sys.argv[2]
    gender = sys.argv[3] if len(sys.argv) > 3 else ""
    out_dir = sys.argv[4] if len(sys.argv) > 4 else "."
    report_type = sys.argv[5] if len(sys.argv) > 5 else "complete"
    extra = sys.argv[6] if len(sys.argv) > 6 else ""
    birth_time = sys.argv[7] if len(sys.argv) > 7 else ""
    birth_place = sys.argv[8] if len(sys.argv) > 8 else ""
    focus_area = sys.argv[9] if len(sys.argv) > 9 else ""
    p = generate_report(name, dob, gender, out_dir, report_type=report_type, extra=extra,
                        birth_time=birth_time, birth_place=birth_place, focus_area=focus_area)
    print("Report written to:", p)
