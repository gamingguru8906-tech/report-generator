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
    return re.sub(r'[^a-zA-Z0-9]+', '_', s or '').strip('_')[:32]

def generate_report(full_name, dob, gender="", out_dir=".", book_cover=None, report_type="complete", extra="",
                    birth_time="", birth_place="", focus_area="", email="", partner_name="", partner_dob="",
                    partner_birth_time="", partner_birth_place="", marriage_date="", current_issue="",
                    children="", main_question=""):
    """dob accepts 'YYYY-MM-DD' or a datetime.date. Returns absolute PDF path.
    report_type: complete_numerology plus focused service keys such as
    mobile_number_analysis, name_numerology, career_numerology and legacy aliases.
    extra: the report's second input (mobile number, business name, or partner's name & DOB)."""
    if isinstance(dob, str):
        dob = datetime.strptime(dob.strip(), "%Y-%m-%d").date()
    canonical_type = REPORT_ALIASES.get((report_type or "complete").strip(), (report_type or "complete").strip())
    if canonical_type == "premium_astrology_life_path":
        if not birth_time or not birth_place:
            raise ValueError("birth_time and birth_place are required for Premium Astrology Life Path reports")
        os.makedirs(out_dir, exist_ok=True)
        chart = AST.compute_chart(full_name, dob, birth_time, birth_place, gender=gender,
                                  focus_area=focus_area or extra or "general life path", email=email)
        fname = f"VeshannAstro_Astrology_Life_Path_{_slug(full_name)}_{dob.isoformat()}_{_slug_place(birth_place)}.pdf"
        out_path = os.path.abspath(os.path.join(out_dir, fname))
        AR.build_astrology_report(chart, out_path)
        return out_path
    if canonical_type == "premium_divorce_separation":
        if not birth_time or not birth_place:
            raise ValueError("birth_time and birth_place are required for Premium Divorce, Separation & Relationship Karma reports")
        os.makedirs(out_dir, exist_ok=True)
        chart = AST.compute_chart(full_name, dob, birth_time, birth_place, gender=gender,
                                  focus_area=focus_area or current_issue or "relationship crisis", email=email)
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
        fname = f"VeshannAstro_Divorce_Separation_Report_{_slug(full_name)}_{dob.isoformat()}_{_slug_place(birth_place)}.pdf"
        out_path = os.path.abspath(os.path.join(out_dir, fname))
        DR.build_divorce_report(chart, out_path, extra=report_extra)
        return out_path
    r = N.compute(full_name, dob, gender)
    report_type = _prepare_optional_data(r, canonical_type, extra)
    os.makedirs(out_dir, exist_ok=True)
    tag = "" if report_type == "complete_numerology" else f"_{report_type}"
    fname = f"VeshannAstro_Numerology{tag}_{_slug(full_name)}_{dob.isoformat()}.pdf"
    out_path = os.path.abspath(os.path.join(out_dir, fname))
    R.build_report(r, out_path, book_cover=book_cover, report_type=report_type)
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
