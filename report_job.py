"""Builds ONE report PDF in its own process.

app.py runs this as a child process instead of building the PDF inside the web
server. The free Render instance has 512 MB for everything; if a build ever
pushes past that, the kernel kills this child (it volunteers to be killed
first via oom_score_adj) and the web server stays up to mark the order FAILED
and alert the owner. Previously the whole server was killed mid-order, the
customer email never went out, and the Sheet row was left on GENERATED.

Protocol: JSON keyword arguments for generate_report() on stdin; on success
the last stdout line is  __REPORT_PDF__{"path": "/abs/path.pdf"}
"""
import json
import sys

MARKER = "__REPORT_PDF__"


def _rss_mb():
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmHWM"):
                    return int(line.split()[1]) // 1024
    except Exception:
        pass
    return -1


FORECAST_TYPES = {"personal_forecast", "forecast", "personal_year_forecast"}


def _is_forecast(report_type):
    import os
    if os.environ.get("FORECAST_DECK", "on").strip().lower() in ("off", "0", "false", "no"):
        return False
    return (report_type or "").strip() in FORECAST_TYPES


def _phone_from(kwargs):
    import re
    for v in (kwargs.get("phone"), kwargs.get("extra")):
        d = re.sub(r"\D+", "", str(v or ""))
        if len(d) >= 10:
            return d[-10:]
    return None


def _forecast_deck(kwargs):
    import time
    t0 = time.time()
    try:
        from forecast.build import build_forecast
        path, meta = build_forecast(kwargs.get("full_name") or "Customer", kwargs.get("dob"),
                                    phone=_phone_from(kwargs), gender=(kwargs.get("gender") or "").lower() or None,
                                    out_dir=kwargs.get("out_dir") or ".")
        print(f"[report_job] forecast deck: {meta.get('pages')} pages, Mulank {meta.get('mulank')}, "
              f"theme {meta.get('theme')}, mobile={meta.get('mobile')}, overflow={len(meta.get('overflow') or [])}, "
              f"{time.time() - t0:.1f}s (peak {_rss_mb()} MB)", flush=True)
        return path
    except Exception as e:
        print(f"[report_job] forecast deck FAILED, sending the classic forecast instead: {e!r}", flush=True)
        return None


def main():
    try:
        # Volunteer to be the process the OOM killer picks, so it never
        # reaches for the web server instead.
        with open("/proc/self/oom_score_adj", "w") as fh:
            fh.write("1000")
    except Exception:
        pass
    kwargs = json.loads(sys.stdin.read())
    path = None
    if _is_forecast(kwargs.get("report_type")):
        # The Personal Year Forecast deck. Built before anything heavy is imported, because headless
        # Chromium needs most of the 512 MB. Any failure falls back to the classic report below.
        path = _forecast_deck(kwargs)
    if not path:
        from generate import generate_report
        path = generate_report(**kwargs)
    print(f"[report_job] built {path} (peak {_rss_mb()} MB)", flush=True)
    print(MARKER + json.dumps({"path": path}), flush=True)


if __name__ == "__main__":
    main()
