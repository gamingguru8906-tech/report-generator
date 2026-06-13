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
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

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

# Product catalogue: key -> (report_type, price in paise, customer-facing label)
# Prices are starting suggestions — tune freely (paise: ₹199 = 19900).
PRODUCTS = {
    "complete": ("complete", int(os.environ.get("PRICE_COMPLETE", "49900")), "Complete Numerology Report (25 pages)"),
    "snapshot": ("snapshot", int(os.environ.get("PRICE_SNAPSHOT", "19900")), "Numerology Snapshot (mini report)"),
    "career":   ("career",   int(os.environ.get("PRICE_CAREER",   "29900")), "Career & Wealth Numerology Blueprint"),
    "love":     ("love",     int(os.environ.get("PRICE_LOVE",     "29900")), "Love & Relationship Numerology Report"),
    "name":     ("name",     int(os.environ.get("PRICE_NAME",     "24900")), "Name & Lo Shu Numerology Analysis"),
    "forecast": ("forecast", int(os.environ.get("PRICE_FORECAST", "24900")), "The Year Ahead Numerology Forecast"),
}

GOOGLE_SA_JSON  = os.environ.get("GOOGLE_SA_JSON")          # full service-account JSON string
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")
SHEET_ID        = os.environ.get("SHEET_ID", "")
SHEET_TAB       = os.environ.get("SHEET_TAB", "Orders")

SMTP_HOST = "smtp.gmail.com"; SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER", "veshannastro@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS")                    # 16-char Gmail app password

BOOK_COVER = os.environ.get("BOOK_COVER_PATH") or None     # optional real Amazon cover
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS",
    "https://veshannastro.co.in,https://www.veshannastro.co.in").split(",")
OUT_DIR = "/tmp/reports"

app = FastAPI(title="Veshann Astro Report Backend")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])

# ───────────────────────── Razorpay order creation ─────────────────────────
@app.get("/health")
def health(): return {"ok": True, "service": "veshann-report-backend"}

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
    product = (data.get("product") or "complete").strip()
    if product not in PRODUCTS:
        product = "complete"
    report_type, amount, label = PRODUCTS[product]
    if not (name and email and dob):
        raise HTTPException(400, "name, email and dob are required")
    payload = {
        "amount": amount, "currency": "INR",
        "receipt": f"num-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "notes": {"name": name, "email": email, "dob": dob, "gender": gender,
                  "product": product, "report_type": report_type},
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
    if event in ("order.paid", "payment.captured") and notes.get("email") and notes.get("dob"):
        report_type = notes.get("report_type") or PRODUCTS.get(notes.get("product",""), ("complete",))[0]
        threading.Thread(target=_safe_fulfil, daemon=True, args=(
            notes.get("name", "Customer"), notes["dob"], notes["email"],
            notes.get("gender", ""), order_id, report_type)).start()
    return {"status": "ok"}

def _safe_fulfil(*a):
    try: fulfil_order(*a)
    except Exception as e: print("FULFILMENT ERROR:", repr(e))

# ───────────────────────── Pipeline pieces ─────────────────────────
def _google_creds():
    from google.oauth2 import service_account
    info = json.loads(GOOGLE_SA_JSON)
    return service_account.Credentials.from_service_account_info(info, scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"])

def upload_to_drive(pdf_path, creds):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    drive = build("drive", "v3", credentials=creds)
    meta = {"name": os.path.basename(pdf_path)}
    if DRIVE_FOLDER_ID: meta["parents"] = [DRIVE_FOLDER_ID]
    f = drive.files().create(body=meta, fields="id",
        media_body=MediaFileUpload(pdf_path, mimetype="application/pdf")).execute()
    fid = f["id"]
    drive.permissions().create(fileId=fid, body={"role": "reader", "type": "anyone"}).execute()
    return f"https://drive.google.com/file/d/{fid}/view"

def append_to_sheet(row, creds):
    from googleapiclient.discovery import build
    build("sheets", "v4", credentials=creds).spreadsheets().values().append(
        spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!A1", valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS", body={"values": [row]}).execute()

def send_email(to_email, name, pdf_path):
    import smtplib
    msg = MIMEMultipart()
    msg["From"] = f"Veshann Astro <{SMTP_USER}>"; msg["To"] = to_email
    msg["Subject"] = "Your Veshann Astro Premium Numerology Report"
    body = (f"Namaste {name},\n\nThank you for trusting Veshann Astro. Your personalised "
            "Premium Numerology Report is attached.\n\nIt decodes your Life Path, Destiny, Soul Urge, "
            "Lo Shu grid, karmic pattern, life cycles, a 90-day career & luck roadmap and personalised "
            "remedies — built on the authentic Chaldean–Vedic system.\n\nFor a deeper live consultation, "
            "visit veshannastro.co.in.\n\nWith cosmic regards,\nTeam Veshann Astro\n@veshann.astro")
    msg.attach(MIMEText(body, "plain"))
    with open(pdf_path, "rb") as fh:
        part = MIMEBase("application", "pdf"); part.set_payload(fh.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(pdf_path)}"')
    msg.attach(part)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(); s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)

def fulfil_order(name, dob, email, gender="", order_id="", report_type="complete"):
    pdf = generate_report(name, dob, gender=gender, out_dir=OUT_DIR,
                          book_cover=BOOK_COVER, report_type=report_type)
    creds = _google_creds()
    link = upload_to_drive(pdf, creds)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    append_to_sheet([ts, order_id, name, dob, email, gender, report_type, link, "SENT"], creds)
    send_email(email, name, pdf)
    print(f"Fulfilled {order_id} ({report_type}) for {email}: {link}")
    return link
