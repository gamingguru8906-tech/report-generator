# Personal Year Forecast (9:16 deck)

Every `personal_forecast` order is built here; anything that fails falls back to the classic report.

- `data.mjs` — runs the vendored Veshannastro brain (`engine/brain`) and mobile rulebook
  (`engine/mobile-numerology`) for one person and prints JSON.
- `content.py` — turns that JSON into the forecast's facts: support numbers, windows, months, verdicts.
- `deck.py`, `deck_year.py`, `deck_more.py` — the 47–51 pages (mobile pages only when the order has a phone number).
- `framework.py` — the 12-parameter framework's calculations and reading tables for the Vedic sun sign (Swiss Ephemeris,
  Lahiri, with the solar month), the five elements (Earth 2, 5, 8 · Fire 1, 9 · Wood 3, 4 · Metal 6, 7 · Water 2), the
  four pinnacles (11 and 22 kept) and the life graph (DDMM x YYYY, life-need line): one page draws the whole life,
  birth to 90, with every peak and dip named and the forecast decade shaded; the next zooms into that decade (age on
  1 January of the forecast year, ten years on), with the nearest turns either side drawn faintly. Edit the meanings there.
- `kit.py` — page kit (CSS, shapes, plates, icons) shared by every design.
- `themes.py` — colours, fonts, paper and type settings per design, and which Mulank gets which design.
- `looks.py` — how each design draws its shapes, marks, title plates, page frame, footer and cover.

## Designs by Mulank (psychic number = day of birth reduced)

| Mulank | Design | Look |
|---|---|---|
| 1 | Dabba | warm field, colour in pairs, square plates, giant lowercase Bagel words, serif print |
| 2 | Broadcast Cookbook | plum and mustard, spine strip and index tabs, shadowed Corben caps crossed by Ballet script, Bodoni titles |
| 4 | Torn | torn-paper collage in kraft, dusty blue, rose and cream, Anton capitals, Newsreader copy |
| 7 | Contour Stack | stacked contour-cut paper landscapes, Smooch Sans capitals, Rubik copy |
| 8 | Daktilo Dispatch | case file: cream manila folders on black, Montserrat capitals, Inconsolata memo copy |
| 3 | Imperial Cabinet | flat parchment, lavender and amber stages, imperial-purple silk with a cloud-scroll pattern, a caption strip at every foot, purple seams and square seals; Castoro Titling over Gantari, Castoro italic |
| 5 | Foxglove | pearly dawn-sky washes, cream plates with a double moss keyline, gilt oval medallions, foxglove stalks and pink ribbon labels; Rosarivo titles, Gentium Book Plus reading |
| 6 | Rosette (base) | pink flowers, clouds and sparkles, Savate and Albert |
| 9 | Cobalt & Cream | warm cream paper, deep cobalt act breaks, sharp paper plates with left seams and hairline ledgers, flat screenprint leaves and suns; Tiro Bangla, Source Sans 3, Jaini Purva eyebrows |

To change who gets what, edit `THEME_FOR_MULANK` in `themes.py`; any Mulank not listed gets Rosette. Imperial Cabinet,
Foxglove and Cobalt & Cream (31 Oct 2026) follow the owner's Gamma references of the same names: their colours, type
pairings and container styles, redrawn in code.
A new design needs a theme dict in `themes.py` and a `Look` subclass in `looks.py` (start from an existing one).
Fonts are static open-licence woff2 files from Fontsource under `assets/fonts/`; shapes and paper textures are
drawn in code, so no third-party images are used.
- `render.mjs` — prints the HTML to PDF in headless Chromium (`@sparticuz/chromium`), shrinking any page
  whose text runs into the footer.
- `build.py` — `build_forecast(name, dob, year=None, phone=None, gender=None, out_dir=".")`.

Orders from October onward get next year's forecast. `FORECAST_DECK=off` switches the deck off.

The engines under `engine/` are copied from the whatsapp-agent repo (branch claude/sharp-thompson-8f33y1).
Re-copy them when the rulebook changes.

Install: `npm ci --omit=dev --prefix forecast` (the Render build command does this; the server also installs
it at boot if a deploy skipped it).
