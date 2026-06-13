# Veshann Astro — Report Backend · Deploy Guide

A standalone service that turns a paid order into a delivered PDF report. No work happens
until payment; then it generates, uploads, logs and emails — in seconds.

```
order.html (on your site)  →  POST /create-order  →  Razorpay Checkout  →  payment
                                                                              │
                                   Razorpay webhook  →  POST /razorpay-webhook
                                                                              │
                         generate PDF → Google Drive → Google Sheet row → email to customer
```

## What's in here
- `app.py` — the FastAPI backend (`/create-order`, `/razorpay-webhook`, `/health`).
- `numerology.py · content.py · pdfbuild_base.py · report.py · generate.py · fonts/` — the report engine.
- `order.html` — the customer order page, already styled to the Veshann Astro site. Host it on
  your site (or link it from your index). **Edit one line: `BACKEND_URL`.**
- `render.yaml · Procfile · requirements.txt · .env.example` — deployment config.

## One-time setup (≈ 20 minutes)

### 1. Razorpay
- Dashboard → Settings → **API Keys** → copy `Key ID` + `Key Secret`.
- Dashboard → Settings → **Webhooks** → Add webhook:
  - URL: `https://YOUR-RENDER-APP.onrender.com/razorpay-webhook`
  - Active event: **`order.paid`** (you can also tick `payment.captured`).
  - Set a secret → that's `RAZORPAY_WEBHOOK_SECRET`.

### 2. Google (Drive + Sheets)
- Google Cloud Console → create a **Service Account** → create a **JSON key** (download it).
- Enable **Google Drive API** and **Google Sheets API** for the project.
- In Drive (as veshannastro@gmail.com) make a folder "Numerology Reports", **Share** it with the
  service-account email (…iam.gserviceaccount.com) as **Editor** → copy the folder ID from its URL.
- Make a Google Sheet, **Share** it with the same service-account email as **Editor** → copy the
  sheet ID from its URL. First tab named `Orders`.
- Paste the *entire* JSON key as the value of `GOOGLE_SA_JSON`.

### 3. Gmail
- On veshannastro@gmail.com: enable **2-Step Verification**, then create a 16-char **App Password**
  → that's `SMTP_PASS`.

## Deploy on Render
1. Push this folder to a GitHub repo.
2. Render → **New → Web Service** → connect the repo. It reads `render.yaml` automatically
   (or set Build `pip install -r requirements.txt`, Start `uvicorn app:app --host 0.0.0.0 --port $PORT`).
3. Add the environment variables from `.env.example` (Render → Environment).
4. Deploy. Visit `https://YOUR-APP.onrender.com/health` → should return `{"ok": true}`.
5. Put that URL into `order.html` → `BACKEND_URL`, and into the Razorpay webhook.

## Set your price
`REPORT_AMOUNT_PAISE` is in paise. ₹499 = `49900`, ₹999 = `99900`.

## Test
- Razorpay **Test Mode** keys + the test card, or a real ₹1 order.
- Complete a payment from `order.html`. Within seconds you should see: a PDF in the Drive folder,
  a new row in the Sheet (`timestamp, order_id, name, dob, email, gender, drive_link, SENT`), and
  the email in the customer inbox.
- If nothing happens, check Render logs. The usual cause is the webhook not reaching the service,
  or `dob` missing from the order — `order.html` sends it, so keep that page as the entry point.

## Real book cover
Drop the cover image into this folder and set `BOOK_COVER_PATH=book_cover.jpg`. The live server can
fetch/embed it (the Amazon link is already wired and clickable in every report).

## Note on Render free tier
Free services sleep after inactivity, so the first request after a quiet spell takes ~30–50s to wake.
The webhook will still arrive and fulfil; if you want instant wakes, use a paid instance or a cron ping.

## Report tiers (product ladder)
The engine produces six report types from the same birth data. The order page shows them all with
live prices; `GET /products` returns the catalogue. Tune prices via env vars (paise; ₹199 = 19900).

| Product key | Report | ~Pages | Env var | Suggested |
|---|---|---|---|---|
| `complete` | Complete Numerology Report | 25 | `PRICE_COMPLETE` | ₹499 |
| `career`   | Career & Wealth Blueprint  | 9  | `PRICE_CAREER`   | ₹299 |
| `love`     | Love & Relationship Report | 7  | `PRICE_LOVE`     | ₹299 |
| `forecast` | The Year Ahead Forecast    | 8  | `PRICE_FORECAST` | ₹249 |
| `name`     | Name & Lo Shu Analysis     | 7  | `PRICE_NAME`     | ₹249 |
| `snapshot` | Numerology Snapshot (mini) | 9  | `PRICE_SNAPSHOT` | ₹199 |

The chosen product is stored in the Razorpay order notes and drives which report the webhook builds.
Use the cheaper tiers as entry products and upsell the Complete report (every report's last page already
links deeper services). To sell a single tier on a dedicated page, preselect it in `order.html`.


## Fonts (important — why there are no .ttf files to upload)
The report fonts (Cinzel, Cormorant Garamond, Jost — all open-source) are **generated at build
time**, not stored in the repo. So you do NOT upload any font files to GitHub. The Render build
command runs `python build_fonts.py`, which downloads and builds them into `fonts/` automatically.
A safety net in `app.py` also rebuilds them on first boot if missing.

Running locally? Just run `python build_fonts.py` once before generating reports.
