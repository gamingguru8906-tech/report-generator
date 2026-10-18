# Personal Year Forecast (9:16 deck)

Every `personal_forecast` order is built here; anything that fails falls back to the classic report.

- `data.mjs` — runs the vendored Veshannastro brain (`engine/brain`) and mobile rulebook
  (`engine/mobile-numerology`) for one person and prints JSON.
- `content.py` — turns that JSON into the forecast's facts: support numbers, windows, months, verdicts.
- `deck.py`, `deck_year.py` — the 40–44 pages (mobile pages only when the order has a phone number).
- `kit.py`, `themes.py` — page kit and the design theme per Mulank (Rosette for all until new designs land).
- `render.mjs` — prints the HTML to PDF in headless Chromium (`@sparticuz/chromium`), shrinking any page
  whose text runs into the footer.
- `build.py` — `build_forecast(name, dob, year=None, phone=None, gender=None, out_dir=".")`.

Orders from October onward get next year's forecast. `FORECAST_DECK=off` switches the deck off.

The engines under `engine/` are copied from the whatsapp-agent repo (branch claude/sharp-thompson-8f33y1).
Re-copy them when the rulebook changes.

Install: `npm ci --omit=dev --prefix forecast` (the Render build command does this; the server also installs
it at boot if a deploy skipped it).
