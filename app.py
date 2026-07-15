"""
Veshann Astro — Numerology Report Backend (standalone)
======================================================
A small FastAPI service that runs on Render and does everything AFTER payment:

  Browser (order page on your site)
      │  POST /create-order   (name, email, dob, gender)
      ▼
  This backend  ──► creates a Razorpay Order (with the customer's details
                    stored in the order's `notes`, tamper-proof on the server)
      │  returns { order_id, key_id, amount }
      ▼
  Browser opens Razorpay Checkout against that order_id and pays
      │
      ▼
  Razorpay  ──► POST /razorpay-webhook  (event: order.paid)
      │
      ▼
  This backend: generate 25-page PDF → upload to Google Drive
                → log row in Google Sheet → email PDF to customer.

The customer gets their report within seconds; the 1-hour promise has huge headroom.

Run:  uvicorn app:app --host 0.0.0.0 --port $PORT
"""
import os, json, hmac, hashlib, base64, datetime, threading

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure brand fonts exist before the report engine imports & registers them.
# On Render the build step already ran build_fonts.py (this then no-ops); this is a safety net.
try:
    import build_fonts; build_fonts.main()
except Exception as _e:
    print("font build warning:", _e)

from generate import generate_report

# ───────────────────────── CONFIG (set as Render env vars) ─────────────────────────
RAZORPAY_KEY_ID         = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET     = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
REPORT_AMOUNT_PAISE     = int(os.environ.get("REPORT_AMOUNT_PAISE", "49900"))  # legacy default
ADMIN_TOKEN             = os.environ.get("ADMIN_TOKEN", "")  # protects /admin/* diagnostic + recovery tools

# Product catalogue: key -> (report_type, price in paise, customer-facing label)
# Prices match the live veshannastro.co.in cards (paise: ₹250 = 25000). Override via env vars.
PRODUCTS = {
    "complete": ("complete_numerology", int(os.environ.get("PRICE_COMPLETE", "99900")), "Complete Numerology Report (25 pages)"),
    "name":     ("name_numerology",     int(os.environ.get("PRICE_NAME",     "25000")), "Name Numerology Report"),
    "mobile":   ("mobile_number_analysis", int(os.environ.get("PRICE_MOBILE", "25000")), "Mobile Number Analysis"),
    "forecast": ("personal_forecast",   int(os.environ.get("PRICE_FORECAST", "49900")), "Personal Year Forecast"),
    "love":     ("relationship_compatibility", int(os.environ.get("PRICE_LOVE", "25000")), "Numerology Compatibility"),
    "baby":     ("baby_name_report",    int(os.environ.get("PRICE_BABY",     "25000")), "Baby Name Report"),
    "business": ("business_name_report", int(os.environ.get("PRICE_BUSINESS", "49900")), "Business Name Report"),
    # extra tiers the engine also supports (not shown on the live site by default):
    "snapshot": ("snapshot", int(os.environ.get("PRICE_SNAPSHOT", "19900")), "Numerology Snapshot (mini report)"),
    "career":   ("career_numerology",   int(os.environ.get("PRICE_CAREER",   "29900")), "Career Numerology Report"),
    "money":    ("money_numerology",    int(os.environ.get("PRICE_MONEY",    "29900")), "Money Numerology Report"),
    "house":    ("house_number_analysis", int(os.environ.get("PRICE_HOUSE",  "25000")), "House Number Analysis"),
    "vehicle":  ("vehicle_number_analysis", int(os.environ.get("PRICE_VEHICLE", "25000")), "Vehicle Number Analysis"),
    "astrology_life_path": ("premium_astrology_life_path", 199900, "Premium Astrology Life Path Report"),
    "divorce_separation_report": ("premium_divorce_separation", 199900, "Premium Divorce, Separation & Relationship Karma Report"),
    "palmistry": ("premium_palmistry", int(os.environ.get("PRICE_PALMISTRY", "149900")), "Premium Palmistry Analysis Report"),
}

_DONE = set()   # in-memory idempotency guard against duplicate webhook deliveries

GOOGLE_SA_JSON  = os.environ.get("GOOGLE_SA_JSON")          # full service-account JSON string
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")
SHEET_ID        = os.environ.get("SHEET_ID", "")
SHEET_TAB       = os.environ.get("SHEET_TAB", "Orders")

BREVO_API_KEY   = os.environ.get("BREVO_API_KEY", "")
BREVO_FROM_EMAIL= os.environ.get("BREVO_FROM_EMAIL", "veshannastro@gmail.com")
BREVO_FROM_NAME = os.environ.get("BREVO_FROM_NAME", "Veshannastro")

BOOK_COVER = os.environ.get("BOOK_COVER_PATH") or None     # optional real Amazon cover
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS",
    "https://veshannastro.co.in,https://www.veshannastro.co.in").split(",")
OUT_DIR = "/tmp/reports"
_fulfilled: set = set()   # dedup: payment_ids already processed this session

app = FastAPI(title="Veshann Astro Report Backend")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])

# ───────────────────────── Razorpay order creation ─────────────────────────
@app.get("/health")
def health(): return {"ok": True, "service": "veshann-report-backend"}

@app.on_event("startup")
def _normalise_sheet_header():
    """Fix the Orders header to the clean 24-column layout as soon as the
    service boots, so it is corrected on deploy rather than on the next order."""
    try:
        ensure_header(_google_creds())
    except Exception as e:
        print(f"[startup] sheet header ensure skipped: {e!r}")

@app.get("/products")
def products():
    """Lets the order page render the catalogue + live prices."""
    return {k: {"report_type": rt, "amount": amt, "label": lbl}
            for k, (rt, amt, lbl) in PRODUCTS.items()}

@app.post("/create-order")
async def create_order(request: Request):
    """Called by your order page. Stores customer details in the order notes."""
    data = await request.json()
    name  = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    dob   = (data.get("dob") or "").strip()      # YYYY-MM-DD from the <input type=date>
    gender= (data.get("gender") or "").strip()
    extra = (data.get("extra") or "").strip()      # mobile no. / business name / partner details
    birth_time = (data.get("birth_time") or "").strip()
    birth_place = (data.get("birth_place") or "").strip()
    focus_area = (data.get("focus_area") or "").strip()
    partner_name = (data.get("partner_name") or "").strip()
    partner_dob = (data.get("partner_dob") or "").strip()
    partner_birth_time = (data.get("partner_birth_time") or "").strip()
    partner_birth_place = (data.get("partner_birth_place") or "").strip()
    marriage_date = (data.get("marriage_date") or "").strip()
    current_issue = (data.get("current_issue") or "").strip()
    children = (data.get("children") or "").strip()
    main_question = (data.get("main_question") or "").strip()
    product = (data.get("product") or "complete").strip()
    if product not in PRODUCTS:
        product = "complete"
    report_type, amount, label = PRODUCTS[product]
    if not (name and email and dob):
        raise HTTPException(400, "name, email and dob are required")
    if report_type == "premium_astrology_life_path" and not (birth_time and birth_place and focus_area):
        raise HTTPException(400, "birth_time, birth_place and focus_area are required for this report")
    if report_type == "premium_divorce_separation" and not (birth_time and birth_place and partner_name and partner_dob and current_issue and main_question):
        raise HTTPException(400, "birth_time, birth_place, partner_name, partner_dob, current_issue and main_question are required for this report")
    if report_type == "premium_palmistry" and not extra.lower().startswith("palm"):
        raise HTTPException(400, "palm observation data is required for this report")
    payload = {
        "amount": amount, "currency": "INR",
        "receipt": f"num-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": {"name": name, "email": email, "dob": dob, "birth_time": birth_time,
                  "birth_place": birth_place, "gender": gender, "focus_area": focus_area,
                  "partner_name": partner_name, "partner_dob": partner_dob,
                  "partner_birth_time": partner_birth_time, "partner_birth_place": partner_birth_place,
                  "marriage_date": marriage_date, "current_issue": current_issue,
                  "children": children, "main_question": main_question,
                  "extra": extra, "product": product, "report_type": report_type,
                  "source": "veshann_report"},
    }
    resp = requests.post("https://api.razorpay.com/v1/orders", json=payload,
                         auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET), timeout=20)
    if resp.status_code >= 300:
        raise HTTPException(502, f"razorpay order failed: {resp.text}")
    order = resp.json()
    return JSONResponse({"order_id": order["id"], "amount": order["amount"],
                         "currency": order["currency"], "key_id": RAZORPAY_KEY_ID,
                         "label": label})

# ───────────────────────── Webhook → fulfilment ─────────────────────────
@app.post("/razorpay-webhook")
async def webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise HTTPException(400, "bad signature")
    evt = json.loads(raw)
    event = evt.get("event", "")
    payload = evt.get("payload", {})
    notes, order_id = {}, ""
    # prefer order notes (set server-side); fall back to payment notes
    if "order" in payload:
        ent = payload["order"]["entity"]; notes = ent.get("notes", {}) or {}; order_id = ent.get("id", "")
    if not notes and "payment" in payload:
        ent = payload["payment"]["entity"]; notes = ent.get("notes", {}) or {}; order_id = ent.get("order_id", "") or ent.get("id", "")
    print(f"[webhook] event={event} order={order_id} source={notes.get('source')} "
          f"product={notes.get('product')} email={notes.get('email')} dob={notes.get('dob')}")
    # Only act on orders THIS report page created (tagged source=veshann_report with a known product).
    # This makes the backend safely ignore your live-consultation bookings on the same Razorpay account.
    is_report = notes.get("source") == "veshann_report" and notes.get("product") in PRODUCTS

    # Hosted Razorpay Payment Pages (rzp.io links on veshannastro.co.in) carry no
    # source tag — recognise them from their form-answer notes and fulfil automatically.
    if event in ("order.paid", "payment.captured") and not is_report:
        pay_ent = (payload.get("payment") or {}).get("entity", {})
        mapped = None
        try:
            import payment_pages as PP
            mapped = PP.match_payment_page(notes or pay_ent.get("notes") or {}, pay_ent, PRODUCTS)
        except Exception as e:
            print(f"[webhook] payment-page match error: {e!r}")
        if mapped:
            dedup_key = order_id or pay_ent.get("id", "")
            if dedup_key and (dedup_key in _DONE or dedup_key in _fulfilled):
                print(f"[webhook] {dedup_key} already handled — skipping duplicate")
                return {"status": "ok", "dedup": True}
            if dedup_key:
                _DONE.add(dedup_key)
            report_type = PRODUCTS[mapped["product"]][0]
            print(f"[webhook] payment-page order matched: product={mapped['product']} "
                  f"email={mapped['email']} dob={mapped['dob']} order={dedup_key}")
            threading.Thread(target=_safe_fulfil, daemon=True, args=(
                mapped["name"], mapped["dob"], mapped["email"], mapped["gender"],
                dedup_key, report_type, mapped["extra"])).start()
            return {"status": "ok", "payment_page": True}

    if event in ("order.paid", "payment.captured") and is_report and notes.get("email") and notes.get("dob"):
        dedup_key = order_id or notes.get("email", "")
        # _fulfilled is also checked so a /trigger-report call from the booking
        # page and this webhook never both send the same report
        if dedup_key and (dedup_key in _DONE or dedup_key in _fulfilled):
            print(f"[webhook] {dedup_key} already handled — skipping duplicate")
            return {"status": "ok", "dedup": True}
        if dedup_key:
            _DONE.add(dedup_key)
        report_type = notes.get("report_type") or PRODUCTS[notes["product"]][0]
        threading.Thread(target=_safe_fulfil, daemon=True, args=(
            notes.get("name", "Customer"), notes["dob"], notes["email"],
            notes.get("gender", ""), order_id, report_type, notes.get("extra", ""),
            notes.get("birth_time", ""), notes.get("birth_place", ""), notes.get("focus_area", ""),
            notes.get("partner_name", ""), notes.get("partner_dob", ""),
            notes.get("partner_birth_time", ""), notes.get("partner_birth_place", ""),
            notes.get("marriage_date", ""), notes.get("current_issue", ""),
            notes.get("children", ""), notes.get("main_question", ""))).start()
    return {"status": "ok"}

def _safe_fulfil(name, dob, email, gender="", order_id="", report_type="complete", extra="",
                 birth_time="", birth_place="", focus_area="", partner_name="", partner_dob="",
                 partner_birth_time="", partner_birth_place="", marriage_date="", current_issue="",
                 children="", main_question=""):
    try:
        fulfil_order(name, dob, email, gender, order_id, report_type, extra,
                     birth_time, birth_place, focus_area, partner_name, partner_dob,
                     partner_birth_time, partner_birth_place, marriage_date, current_issue,
                     children, main_question)
    except _LoggedFailure as e:
        # Failure is already visible on the order's own Sheet row (status=FAILED).
        print("FULFILMENT ERROR (logged on order row):", repr(e))
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("FULFILMENT ERROR:", repr(e)); print(tb)
        # Make the failure VISIBLE in the sheet instead of vanishing into logs.
        try:
            creds = _google_creds()
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            append_to_sheet(
                [ts, order_id, name, _fmt_dob(dob), email, gender, report_type, extra,
                 birth_time, birth_place, focus_area, partner_name, _fmt_dob(partner_dob),
                 partner_birth_time, partner_birth_place, marriage_date, current_issue,
                 children, main_question, "", "ERROR", ts, "ERROR: " + repr(e)[:300],
                 PIPELINE_VERSION], creds)
        except Exception as e2:
            print("could not log ERROR row:", repr(e2))

# ───────────────────────── Pipeline pieces ─────────────────────────
def _google_creds():
    from google.oauth2 import service_account
    info = json.loads(GOOGLE_SA_JSON)
    return service_account.Credentials.from_service_account_info(info, scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"])

def upload_to_drive(pdf_path, creds):
    """Upload PDF to Google Drive folder.
    The target folder must be a Shared Drive OR the service account must be
    granted 'Content manager' / 'Contributor' role on a Shared Drive.
    For a regular My Drive folder: share it with the service account as Editor
    AND enable 'supportsAllDrives' so the API accepts the parent correctly.
    We use the multipart upload with supportsAllDrives=True which works for
    both regular shared folders and Shared Drives."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    drive = build("drive", "v3", credentials=creds)
    meta = {"name": os.path.basename(pdf_path)}
    if DRIVE_FOLDER_ID: meta["parents"] = [DRIVE_FOLDER_ID]
    f = drive.files().create(
        body=meta, fields="id",
        media_body=MediaFileUpload(pdf_path, mimetype="application/pdf"),
        supportsAllDrives=True
    ).execute()
    fid = f["id"]
    drive.permissions().create(
        fileId=fid,
        body={"role": "reader", "type": "anyone"},
        supportsAllDrives=True
    ).execute()
    return f"https://drive.google.com/file/d/{fid}/view"

def append_to_sheet(row, creds):
    from googleapiclient.discovery import build
    build("sheets", "v4", credentials=creds).spreadsheets().values().append(
        spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!A1", valueInputOption="RAW",
        insertDataOption="INSERT_ROWS", body={"values": [row]}).execute()

# ─────────── Status lifecycle + durable idempotency (Sheet-backed) ───────────
# Row layout (backwards compatible — legacy rows ended at U="SENT"):
#   A..S = ts, order_id, name, dob, email, gender, report_type, extra,
#          birth_time, birth_place, focus_area, partner_* (4), marriage_date,
#          current_issue, children, main_question
#   T = report URL (Drive link)   U = status   V = status timestamp
#   W = error message             X = pipeline version
PIPELINE_VERSION = "report-pipeline-v3-studio-fieldnotes-2026-07-15"
TERMINAL_STATUSES = {"SENT", "DELIVERED"}

class _LoggedFailure(Exception):
    """Failure already recorded on the order's own Sheet row."""

def _now_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _sheets(creds):
    from googleapiclient.discovery import build
    return build("sheets", "v4", credentials=creds).spreadsheets()

# One clean header for all 24 columns the pipeline writes (A..X).
SHEET_HEADERS = [
    "Timestamp", "Order ID", "Name", "DOB", "Email", "Gender", "Report Type", "Extra",
    "Birth Time", "Birth Place", "Focus Area", "Partner Name", "Partner DOB",
    "Partner Birth Time", "Partner Birth Place", "Marriage Date", "Current Issue",
    "Children", "Main Question", "Report URL", "Status", "Status Time", "Error", "Pipeline",
]
_HEADER_ENSURED = False
def ensure_header(creds):
    """Make row 1 a correct 24-column header (once per process). Self-healing:
    if the header is missing or mislabelled it is rewritten in place."""
    global _HEADER_ENSURED
    if _HEADER_ENSURED or not creds:
        return
    try:
        rng = f"{SHEET_TAB}!A1:X1"
        cur = _sheets(creds).values().get(spreadsheetId=SHEET_ID, range=rng).execute().get("values", [])
        cur0 = cur[0] if cur else []
        if cur0[:len(SHEET_HEADERS)] != SHEET_HEADERS:
            _sheets(creds).values().update(
                spreadsheetId=SHEET_ID, range=rng, valueInputOption="RAW",
                body={"values": [SHEET_HEADERS]}).execute()
            print("[sheet] header row normalised to 24 columns")
        _HEADER_ENSURED = True
    except Exception as e:
        print(f"[sheet] ensure_header failed (continuing): {e!r}")

def _fmt_dob(dob):
    """Render a DOB as clean, unambiguous text ('24 August 1991') for the sheet,
    so USER_ENTERED-style date coercion can never turn it into a serial number."""
    s = str(dob or "").strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%d %B %Y")
        except Exception:
            pass
    return s

def append_status_row(row, creds):
    """Append a row and return its 1-based row index (from updatedRange)."""
    ensure_header(creds)
    resp = _sheets(creds).values().append(
        spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!A1", valueInputOption="RAW",
        insertDataOption="INSERT_ROWS", body={"values": [row]}).execute()
    rng = resp.get("updates", {}).get("updatedRange", "")   # e.g. Orders!A17:X17
    try:
        return int("".join(ch for ch in rng.split("!")[1].split(":")[0] if ch.isdigit()))
    except Exception:
        return None

def update_status_cells(row_idx, creds, status, link=None, error=None):
    """Update T (link), U (status), V (timestamp), W (error) on an order row."""
    if not row_idx:
        return
    values = [[("" if link is None else link), status, _now_ts(),
               ("" if error is None else str(error)[:300])]]
    _sheets(creds).values().update(
        spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!T{row_idx}:W{row_idx}",
        valueInputOption="RAW", body={"values": values}).execute()
    print(f"[fulfil] row={row_idx} status={status}" + (f" link={link}" if link else "")
          + (f" error={error}" if error else ""))

def _already_fulfilled_in_sheet(order_id, creds):
    """Durable dedup: True if this order_id already has a terminal-status row.
    Survives redeploys (unlike the in-memory _DONE/_fulfilled sets)."""
    if not order_id:
        return False
    try:
        got = _sheets(creds).values().get(
            spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!B:U").execute().get("values", [])
        for r in got:
            if r and r[0] == order_id:
                status = (r[19] if len(r) > 19 else "").strip().upper()
                if status in TERMINAL_STATUSES:
                    return True
        return False
    except Exception as e:
        print(f"[fulfil] dedup check failed (continuing): {e!r}")
        return False

def send_email(to_email, name, pdf_path, report_type="Numerology Report"):
    with open(pdf_path, "rb") as fh:
        pdf_b64 = base64.b64encode(fh.read()).decode("utf-8")

    label = report_type.replace("_", " ").title()

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400&display=swap');
    body {{ margin:0; padding:0; background-color:#0a0a0f; font-family:'Jost',Arial,sans-serif; color:#e8e0d0; }}
    .wrapper {{ max-width:600px; margin:0 auto; background-color:#0d0d18; border:1px solid #2a2040; }}
    .header {{ background:linear-gradient(135deg,#0d0d18 0%,#1a1030 50%,#0d0d18 100%); text-align:center; padding:48px 40px 32px; border-bottom:1px solid #c9a84c33; }}
    .brand {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:28px; font-weight:600; letter-spacing:4px; color:#c9a84c; text-transform:uppercase; margin:0 0 6px; }}
    .brand-sub {{ font-size:11px; font-weight:300; letter-spacing:3px; color:#8a7a9a; text-transform:uppercase; }}
    .star-divider {{ color:#c9a84c; font-size:18px; letter-spacing:8px; margin:20px 0 0; opacity:0.6; }}
    .body {{ padding:48px 48px 40px; }}
    .greeting {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:26px; font-style:italic; color:#c9a84c; margin:0 0 28px; line-height:1.3; }}
    .para {{ font-size:15px; font-weight:300; line-height:1.9; color:#c8bfb0; margin:0 0 22px; }}
    .highlight-box {{ border-left:2px solid #c9a84c; background:#ffffff08; padding:18px 24px; margin:32px 0; font-family:'Cormorant Garamond',Georgia,serif; font-size:17px; font-style:italic; color:#d4c9a8; line-height:1.7; }}
    .attachment-note {{ background:#1a1030; border:1px solid #c9a84c44; border-radius:2px; padding:20px 24px; margin:32px 0; }}
    .attachment-icon {{ font-size:24px; margin-bottom:8px; }}
    .attachment-text {{ font-size:13px; font-weight:300; color:#a09080; line-height:1.6; }}
    .attachment-text strong {{ display:block; color:#c9a84c; font-weight:400; font-size:14px; margin-bottom:3px; }}
    .closing {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:18px; font-style:italic; color:#c9a84c; margin:36px 0 6px; }}
    .signature {{ font-size:13px; font-weight:300; letter-spacing:2px; color:#6a5f7a; text-transform:uppercase; }}
    .footer {{ border-top:1px solid #c9a84c22; padding:28px 48px; text-align:center; background:#08080f; }}
    .footer-text {{ font-size:11px; font-weight:300; color:#4a4060; line-height:1.8; letter-spacing:0.5px; }}
    .footer-text a {{ color:#6a5a8a; text-decoration:none; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="brand">Veshannastro</div>
      <div class="brand-sub">Vedic Astrology &amp; Numerology</div>
      <div class="star-divider">✦ ✦ ✦</div>
    </div>
    <div class="body">
      <div class="greeting">Namaste, {name} 🙏</div>
      <p class="para">
        The cosmos has been consulted, the planets have spoken, and your personal report is now ready.
        It is with deep gratitude and reverence that I place this reading into your hands — knowing
        that every chart is a unique story written in the language of the stars.
      </p>
      <p class="para">
        Thank you, from the bottom of my heart, for trusting Veshannastro with something as sacred
        as your numbers. This is not just a report — it is a mirror of your soul's journey, your
        strengths, your dharma, and the divine timing that governs your life.
      </p>
      <div class="highlight-box">
        "The stars do not compel — they impel. You hold the power to shape your destiny,
        and this report is your cosmic compass."
      </div>
      <p class="para">
        Your <strong style="color:#c9a84c;font-weight:400;">{label}</strong> is attached to this
        email as a PDF. Please save it somewhere safe — you may find yourself returning to its
        wisdom at different chapters of your life.
      </p>
      <div class="attachment-note">
        <div class="attachment-icon">📜</div>
        <div class="attachment-text">
          <strong>Your Report is Attached</strong>
          Open the PDF attached to this email to access your complete {label}.
        </div>
      </div>
      <p class="para">
        If you have any questions, feel free to reply to this email or reach out on WhatsApp.
        I am always here to help you navigate the celestial wisdom within your chart.
      </p>
      <p class="para">
        May this reading bring you clarity, peace, and a deeper understanding of the magnificent
        soul that you are. Wishing you light, love, and cosmic abundance always. 🌙⭐
      </p>
      <div class="closing">With gratitude &amp; starlight,</div>
      <div class="signature">Veshannastro</div>
    </div>
    <div class="footer">
      <p class="footer-text">
        &copy; 2025 Veshannastro &middot; Vedic Astrology &amp; Numerology<br>
        <a href="https://veshannastro.co.in">veshannastro.co.in</a> &middot; Delhi, India<br><br>
        This report was prepared exclusively for {name} and is intended for personal use only.
      </p>
    </div>
  </div>
</body>
</html>"""

    payload = {
        "sender":      {"name": BREVO_FROM_NAME, "email": BREVO_FROM_EMAIL},
        "to":          [{"email": to_email, "name": name}],
        "subject":     f"Your {label} is Ready, {name}",
        "htmlContent": html_body,
        "attachment":  [{"name": os.path.basename(pdf_path), "content": pdf_b64}],
    }
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
        json=payload, timeout=30
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"Brevo error {resp.status_code}: {resp.text}")

def fulfil_order(name, dob, email, gender="", order_id="", report_type="complete", extra="",
                 birth_time="", birth_place="", focus_area="", partner_name="", partner_dob="",
                 partner_birth_time="", partner_birth_place="", marriage_date="", current_issue="",
                 children="", main_question=""):
    # 0. Sheet credentials + durable idempotency check (survives redeploys).
    creds, row_idx = None, None
    try:
        creds = _google_creds()
    except Exception as cred_err:
        print(f"[fulfil] WARNING: no Sheet credentials, running without status log: {cred_err!r}")
    if creds and _already_fulfilled_in_sheet(order_id, creds):
        print(f"[fulfil] order={order_id} already has a terminal Sheet row — skipping duplicate")
        return "duplicate-skipped"

    # 1. RECEIVED — the order gets its own row immediately, before any work.
    if creds:
        try:
            row_idx = append_status_row(
                [_now_ts(), order_id, name, _fmt_dob(dob), email, gender, report_type, extra,
                 birth_time, birth_place, focus_area, partner_name, _fmt_dob(partner_dob),
                 partner_birth_time, partner_birth_place, marriage_date, current_issue,
                 children, main_question, "", "RECEIVED", _now_ts(), "", PIPELINE_VERSION],
                creds)
        except Exception as e:
            print(f"[fulfil] could not append RECEIVED row: {e!r}")

    def _fail(stage, exc):
        print(f"[fulfil] order={order_id} FAILED at {stage}: {exc!r}")
        if creds and row_idx:
            try:
                update_status_cells(row_idx, creds, "FAILED", error=f"{stage}: {exc}")
                raise _LoggedFailure(f"{stage}: {exc}") from exc
            except _LoggedFailure:
                raise
            except Exception as e2:
                print(f"[fulfil] could not mark FAILED: {e2!r}")
        raise exc

    # 2. GENERATING → GENERATED
    if creds and row_idx:
        update_status_cells(row_idx, creds, "GENERATING")
    try:
        pdf = generate_report(name, dob, gender=gender, out_dir=OUT_DIR,
                              book_cover=BOOK_COVER, report_type=report_type, extra=extra,
                              birth_time=birth_time, birth_place=birth_place,
                              focus_area=focus_area, email=email,
                              partner_name=partner_name, partner_dob=partner_dob,
                              partner_birth_time=partner_birth_time, partner_birth_place=partner_birth_place,
                              marriage_date=marriage_date, current_issue=current_issue,
                              children=children, main_question=main_question)
    except Exception as e:
        _fail("generate", e)
    if creds and row_idx:
        update_status_cells(row_idx, creds, "GENERATED")

    # 3. Drive upload — optional, skipped gracefully if service account has no quota
    link = "N/A"
    if creds:
        try:
            link = upload_to_drive(pdf, creds)
        except Exception as drive_err:
            print(f"Drive upload skipped: {drive_err}")

    # 4. Email delivery → DELIVERED
    try:
        send_email(email, name, pdf, report_type=report_type)
    except Exception as e:
        _fail("email", e)
    try:
        send_email("veshannastro@gmail.com", name, pdf, report_type=report_type)  # backup copy
    except Exception as e:
        print(f"[fulfil] backup-copy email failed (customer copy already sent): {e!r}")
    if creds and row_idx:
        update_status_cells(row_idx, creds, "DELIVERED", link=link)
    print(f"Fulfilled {order_id} ({report_type}) for {email}: {link} [{PIPELINE_VERSION}]")
    return link

# ───────────────────────── Palm photo upload (before payment) ─────────────────────────
PALM_UPLOAD_DIR = os.environ.get("PALM_UPLOAD_DIR", "/tmp/palm_uploads")
_PALM_MAX_BYTES = 8 * 1024 * 1024   # 8 MB per photo

def _save_palm_image(b64_data: str, dest_path: str):
    """Decode a base64/data-URL image, verify it IS an image, save as JPEG."""
    if "," in b64_data[:80] and b64_data.lstrip().lower().startswith("data:"):
        b64_data = b64_data.split(",", 1)[1]
    raw = base64.b64decode(b64_data, validate=False)
    if len(raw) > _PALM_MAX_BYTES:
        raise ValueError("image exceeds 8 MB limit")
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(raw))
    im.verify()                       # reject non-images
    im = Image.open(BytesIO(raw)).convert("RGB")
    im.thumbnail((1600, 1600))        # normalise size for storage/PDF embedding
    im.save(dest_path, "JPEG", quality=88)

@app.post("/upload-palm")
async def upload_palm(request: Request):
    """Called by the booking page BEFORE payment. Accepts JSON
    {left: <base64/dataURL>, right: <base64/dataURL>} (either side optional,
    at least one required). Stores photos under a random upload id that the
    page then packs into the order's `extra` field. Photos are also backed up
    to Drive (best-effort) so fulfilment survives an instance restart."""
    import secrets
    data = await request.json()
    left, right = data.get("left") or "", data.get("right") or ""
    if not (left or right):
        raise HTTPException(400, "at least one palm photo is required")
    upload_id = secrets.token_urlsafe(12).replace("-", "x").replace("_", "y")
    dest = os.path.join(PALM_UPLOAD_DIR, upload_id)
    os.makedirs(dest, exist_ok=True)
    saved = {}
    try:
        if left:
            _save_palm_image(left, os.path.join(dest, "left.jpg")); saved["left"] = True
        if right:
            _save_palm_image(right, os.path.join(dest, "right.jpg")); saved["right"] = True
    except Exception as e:
        raise HTTPException(400, f"could not read palm photo: {e}")
    # best-effort Drive backup so photos survive redeploys until fulfilment
    try:
        creds = _google_creds()
        for side in saved:
            _upload_palm_to_drive(os.path.join(dest, f"{side}.jpg"), f"palm_{upload_id}_{side}.jpg", creds)
    except Exception as e:
        print(f"palm Drive backup skipped: {e}")
    return {"upload_id": upload_id, "saved": sorted(saved)}

def _upload_palm_to_drive(path, name, creds):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    drive = build("drive", "v3", credentials=creds)
    meta = {"name": name}
    if DRIVE_FOLDER_ID:
        meta["parents"] = [DRIVE_FOLDER_ID]
    drive.files().create(body=meta, fields="id",
                         media_body=MediaFileUpload(path, mimetype="image/jpeg"),
                         supportsAllDrives=True).execute()

# ───────────────────────── Direct report trigger (belt-and-suspenders) ─────────────────────────
@app.post("/trigger-report")
async def trigger_report(request: Request):
    """Called directly from the booking page after payment succeeds.
    Acts as a belt-and-suspenders backup — the Razorpay webhook also fires.
    We deduplicate by payment_id stored in a simple in-memory set (resets on redeploy, which is fine)."""
    data = await request.json()
    payment_id = (data.get("payment_id") or "").strip()
    name       = (data.get("name") or "").strip()
    email      = (data.get("email") or "").strip()
    dob        = (data.get("dob") or "").strip()
    gender     = (data.get("gender") or "").strip()
    report_type= (data.get("report_type") or "complete").strip()
    extra      = (data.get("extra") or "").strip()
    birth_time = (data.get("birth_time") or "").strip()
    birth_place= (data.get("birth_place") or "").strip()
    focus_area = (data.get("focus_area") or "").strip()
    partner_name = (data.get("partner_name") or "").strip()
    partner_dob = (data.get("partner_dob") or "").strip()
    partner_birth_time = (data.get("partner_birth_time") or "").strip()
    partner_birth_place = (data.get("partner_birth_place") or "").strip()
    marriage_date = (data.get("marriage_date") or "").strip()
    current_issue = (data.get("current_issue") or "").strip()
    children = (data.get("children") or "").strip()
    main_question = (data.get("main_question") or "").strip()
    order_id   = (data.get("order_id") or payment_id).strip()

    if not (name and email and dob):
        raise HTTPException(400, "name, email and dob are required")
    if payment_id in _fulfilled or (order_id and (order_id in _fulfilled or order_id in _DONE)):
        return JSONResponse({"status": "already_fulfilled"})
    _fulfilled.add(payment_id)
    if order_id:
        _fulfilled.add(order_id)

    threading.Thread(
        target=_safe_fulfil,
        args=(name, dob, email, gender, order_id, report_type, extra, birth_time, birth_place, focus_area,
              partner_name, partner_dob, partner_birth_time, partner_birth_place, marriage_date,
              current_issue, children, main_question),
        daemon=True
    ).start()
    return JSONResponse({"status": "triggered"})

# ───────────────────────── Admin tools (diagnose + recover) ─────────────────────────
def _check_admin(token):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(403, "bad or missing admin token")

@app.get("/admin/selftest")
def admin_selftest(token: str = ""):
    """Checks each piece of the pipeline independently and reports pass/fail.
    Open: https://<your-app>/admin/selftest?token=YOUR_ADMIN_TOKEN"""
    _check_admin(token)
    out = {"env": {
        "RAZORPAY_WEBHOOK_SECRET": bool(RAZORPAY_WEBHOOK_SECRET),
        "GOOGLE_SA_JSON": bool(GOOGLE_SA_JSON), "DRIVE_FOLDER_ID": bool(DRIVE_FOLDER_ID),
        "SHEET_ID": bool(SHEET_ID), "BREVO_API_KEY": bool(BREVO_API_KEY),
        "BREVO_FROM_EMAIL": BREVO_FROM_EMAIL,
    }}
    try:
        creds = _google_creds(); out["google_creds"] = "ok"
    except Exception as e:
        out["google_creds"] = f"FAIL: {e}"; return out
    try:
        from googleapiclient.discovery import build
        build("drive", "v3", credentials=creds).files().list(
            q=f"'{DRIVE_FOLDER_ID}' in parents", pageSize=1, fields="files(id)").execute()
        out["drive_folder"] = "ok"
    except Exception as e:
        out["drive_folder"] = f"FAIL (share the folder with the service-account email as Editor): {e}"
    try:
        append_to_sheet(["SELFTEST", "-", "-", "-", "-", "-", "-", "-", datetime.datetime.now().strftime("%H:%M:%S")], creds)
        out["sheet_append"] = "ok (a SELFTEST row was added — you can delete it)"
    except Exception as e:
        out["sheet_append"] = f"FAIL (share the sheet with the service-account email as Editor): {e}"
    try:
        if not BREVO_API_KEY:
            raise ValueError("BREVO_API_KEY is not set")
        resp = requests.get(
            "https://api.brevo.com/v3/account",
            headers={"api-key": BREVO_API_KEY}, timeout=5)
        if resp.status_code == 200:
            out["brevo_key"] = "ok — account: " + resp.json().get("email", "verified")
        else:
            raise ValueError(f"Brevo rejected the API key (HTTP {resp.status_code})")
    except Exception as e:
        out["brevo_key"] = f"FAIL: {e}"
    return out

@app.post("/admin/fulfil")
async def admin_fulfil(request: Request):
    """Manually generate + deliver a report (recover a paid order, or test the pipeline).
    POST JSON: {token, name, dob (YYYY-MM-DD), email, gender?, report_type?}"""
    data = await request.json()
    _check_admin(data.get("token", ""))
    if not (data.get("name") and data.get("dob") and data.get("email")):
        raise HTTPException(400, "name, dob (YYYY-MM-DD) and email are required")
    try:
        link = fulfil_order(data["name"], data["dob"], data["email"],
                            data.get("gender", ""), data.get("order_id", "manual"),
                            data.get("report_type", "complete"), data.get("extra", ""),
                            data.get("birth_time", ""), data.get("birth_place", ""),
                            data.get("focus_area", ""), data.get("partner_name", ""),
                            data.get("partner_dob", ""), data.get("partner_birth_time", ""),
                            data.get("partner_birth_place", ""), data.get("marriage_date", ""),
                            data.get("current_issue", ""), data.get("children", ""),
                            data.get("main_question", ""))
        return {"status": "sent", "drive_link": link}
    except Exception as e:
        import traceback
        return JSONResponse({"status": "error", "error": repr(e),
                             "trace": traceback.format_exc()[-1800:]}, status_code=500)
