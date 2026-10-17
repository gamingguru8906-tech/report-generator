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


def main():
    try:
        # Volunteer to be the process the OOM killer picks, so it never
        # reaches for the web server instead.
        with open("/proc/self/oom_score_adj", "w") as fh:
            fh.write("1000")
    except Exception:
        pass
    kwargs = json.loads(sys.stdin.read())
    from generate import generate_report
    path = generate_report(**kwargs)
    print(f"[report_job] built {path} (peak {_rss_mb()} MB)", flush=True)
    print(MARKER + json.dumps({"path": path}), flush=True)


if __name__ == "__main__":
    main()
