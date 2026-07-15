"""Pre-render quality gate for Veshann Astro premium reports.

Walks the ReportLab story before the PDF is built and checks:
  - no broken values ("None", "undefined", "null", "[object Object]", "nan")
  - no fear-based / guaranteed-outcome language
  - no empty or ultra-thin sections (a section = kicker+h1 ... PageBreak)
  - required disclaimers present where the report covers sensitive topics

The gate NEVER raises during production fulfilment: it logs issues and lets
generation continue (missing a report entirely is worse for the customer than
an imperfect page). Callers can pass strict=True in tests to raise instead.
"""
from __future__ import annotations

import re

BAD_TOKENS = [
    re.compile(r"\[object Object\]"),
    re.compile(r"\bundefined\b"),
    re.compile(r"\bnull\b"),
    re.compile(r"\bNaN\b"),
    # bare Python None leaking into text as a VALUE ("house None", "Time: None"),
    # not the English word starting a sentence ("None of them requires fear")
    re.compile(r"(?:[:=]\s*|[a-z0-9]\s+)None(?![A-Za-z])(?!\s+of\b)"),
    re.compile(r"\{[a-z_]+\}"),                       # unformatted {placeholder}
]

FORBIDDEN_PHRASES = [
    re.compile(r"\bwill definitely\b", re.I),
    re.compile(r"\bdefinitely will\b", re.I),
    re.compile(r"\bguaranteed?\s+(?:to|outcome|result|success|divorce|marriage)\b", re.I),
    re.compile(r"\bthis proves\b", re.I),
    re.compile(r"\byou are cursed\b", re.I),
    re.compile(r"\bcertain (?:death|divorce|failure|ruin)\b", re.I),
    re.compile(r"\b100% (?:sure|certain|accurate)\b", re.I),
]

MIN_SECTION_CHARS = 350   # a premium section should never be a couple of lines


def _flowable_texts(f):
    """Yield text from a flowable, recursing into Panels/Tables/KeepTogether."""
    # Paragraph
    if hasattr(f, "text") and isinstance(getattr(f, "text"), str):
        yield f.text
    # Panel-style wrappers used in this codebase store children in .fl
    for attr in ("fl", "_content", "_flowables"):
        kids = getattr(f, attr, None)
        if isinstance(kids, (list, tuple)):
            for k in kids:
                yield from _flowable_texts(k)
    # Tables
    cells = getattr(f, "_cellvalues", None)
    if cells:
        for row in cells:
            for cell in row:
                if isinstance(cell, (list, tuple)):
                    for k in cell:
                        yield from _flowable_texts(k)
                else:
                    yield from _flowable_texts(cell)


def _strip_markup(txt: str) -> str:
    return re.sub(r"<[^>]+>", "", txt or "")


def audit_story(story, report_name="report", required_disclaimers=(), strict=False):
    """Audit a ReportLab story. Returns a list of issue strings."""
    issues = []
    sections = []          # list of (title, char_count)
    current_title = None
    current_chars = 0
    all_text_parts = []

    for f in story:
        texts = list(_flowable_texts(f))
        for t in texts:
            plain = _strip_markup(t)
            all_text_parts.append(plain)
            for rx in BAD_TOKENS:
                if rx.search(plain):
                    issues.append(f"[{report_name}] broken value {rx.pattern!r} in: {plain[:90]!r}")
            for rx in FORBIDDEN_PHRASES:
                if rx.search(plain):
                    issues.append(f"[{report_name}] forbidden phrase {rx.pattern!r} in: {plain[:90]!r}")
        # section boundary tracking: h1 style paragraphs start a section
        style_name = getattr(getattr(f, "style", None), "name", "")
        if style_name == "h1" and texts:
            if current_title is not None:
                sections.append((current_title, current_chars))
            current_title = _strip_markup(texts[0])
            current_chars = 0
        else:
            current_chars += sum(len(_strip_markup(t)) for t in texts)
    if current_title is not None:
        sections.append((current_title, current_chars))

    for title, chars in sections:
        if chars < MIN_SECTION_CHARS:
            issues.append(f"[{report_name}] thin section ({chars} chars): {title!r}")

    full_text = " ".join(all_text_parts).lower()
    for label, needle in required_disclaimers:
        if needle.lower() not in full_text:
            issues.append(f"[{report_name}] missing required disclaimer: {label}")

    for issue in issues:
        print("QUALITY GATE:", issue)
    if issues and strict:
        raise ValueError(f"Quality gate failed for {report_name}: {len(issues)} issue(s); first: {issues[0]}")
    return issues


def verify_pdf(path, min_pages=3, min_bytes=40_000, floor_bytes=12_000):
    """Post-render sanity check: the PDF exists and is a real, multi-page report.

    A report is considered valid if it rendered enough PAGES — that is the true
    signal that generation succeeded. Byte size alone is unreliable: a perfectly
    complete report can be small when the deployment is missing the background
    image / branded font files (the text still renders, just lighter), while an
    image-heavy report is large. So we accept the PDF when it has at least
    `min_pages` pages OR is comfortably large, and only reject genuine stubs
    (an error page or a single cover with almost nothing in it).
    """
    import os, re
    if not os.path.exists(path):
        raise FileNotFoundError(f"Report PDF was not written: {path}")
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:5] != b"%PDF-":
        raise ValueError(f"File is not a valid PDF: {path}")
    # count page objects (reportlab writes them un-nested, so this is reliable)
    pages = len(re.findall(rb"/Type\s*/Page(?![s])", data))
    if pages >= min_pages:
        return True
    if size >= min_bytes:
        return True
    raise ValueError(
        f"Report looks incomplete ({pages} page(s), {size} bytes): {path}")
