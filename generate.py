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

def _slug(s): return re.sub(r'[^a-zA-Z0-9]+', '_', s).strip('_')[:40]

def generate_report(full_name, dob, gender="", out_dir=".", book_cover=None, report_type="complete", extra=""):
    """dob accepts 'YYYY-MM-DD' or a datetime.date. Returns absolute PDF path.
    report_type: complete | snapshot | career | love | name | forecast | mobile | baby | business
    extra: the report's second input (mobile number, business name, or partner's name & DOB)."""
    if isinstance(dob, str):
        dob = datetime.strptime(dob.strip(), "%Y-%m-%d").date()
    r = N.compute(full_name, dob, gender, extra=extra, report_type=report_type)
    os.makedirs(out_dir, exist_ok=True)
    tag = "" if report_type == "complete" else f"_{report_type}"
    fname = f"VeshannAstro_Numerology{tag}_{_slug(full_name)}_{dob.isoformat()}.pdf"
    out_path = os.path.abspath(os.path.join(out_dir, fname))
    R.build_report(r, out_path, book_cover=book_cover, report_type=report_type)
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python3 generate.py "Full Name" YYYY-MM-DD [gender] [out_dir] [report_type]')
        print('  report_type: complete | snapshot | career | love | name | forecast')
        sys.exit(1)
    name = sys.argv[1]; dob = sys.argv[2]
    gender = sys.argv[3] if len(sys.argv) > 3 else ""
    out_dir = sys.argv[4] if len(sys.argv) > 4 else "."
    report_type = sys.argv[5] if len(sys.argv) > 5 else "complete"
    p = generate_report(name, dob, gender, out_dir, report_type=report_type)
    print("Report written to:", p)
