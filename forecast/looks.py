"""Looks: how each theme draws its shapes, marks, plates, photo, page frame, footer and cover.

The pages (deck.py, deck_year.py) say *what* goes where (a feature shape behind a number, a decorative mark in
a corner, a pair of title plates, a band at the foot of the page). A look decides what that becomes:
Rosette draws flowers, clouds and sparkles; Daktilo draws matted prints and a manila folder; Dabba draws flat
square colour plates and giant lowercase words; Broadcast draws spines, tabs and shadowed capitals crossed by a
script phrase; Torn draws torn paper; Contour draws stacked contour-cut paper landscapes.
"""
import math
import os
import random

from . import kit
from .kit import esc
from .themes import ASSETS

PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
GRID = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]


def _rng(*seed):
    return random.Random("|".join(map(str, seed)))


class Look:
    """Rosette, the base design."""
    plate_em = 0.56        # average glyph width of a plate, in em (to fit long plates)

    def __init__(self, T):
        self.T = T

    # ── page ──
    def ground_css(self, ground, dark, n):
        return f"background:{ground}"

    def frame(self, ground, dark, n):
        return ""

    def footer(self, name, n, dark):
        return f'<div class="foot"><span>Veshannastro</span><span>{esc(name)} &#183; {n:02d}</span></div>'

    def extra_css(self):
        return ""

    def cover(self, deck):
        return None

    # ── fitting ──
    def fit(self, text, base, width=560):
        est = len(str(text)) * base * self.plate_em + 60
        return base if est <= width else max(26, int(base * width / est))

    # ── shapes and marks (Rosette draws them as they are) ──
    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        return kit.blob(color, w, h, x, y, kind, rot, opacity)

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return kit.asterisk(color, size, x, y, rot, spokes, sw)

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return kit.petal_flower(color, size, x, y, petals, hole)

    def sparkle(self, color, size, x=None, y=None):
        return kit.sparkle(color, size, x, y)

    def heart(self, color, size, x=None, y=None):
        return kit.heart(color, size, x, y)

    def ring(self, color, size, x=None, y=None, inner=None):
        return kit.ring(color, size, x, y, inner)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        return kit.scallop(color, side, width, count, height)

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        # Rosette keeps its approved sizes; `width` only narrows the other looks' plates
        return kit.plate(text, size, rot, color, bg)

    def icon(self, name, color, size=34, sw=1.6, x=None, y=None):
        return kit.icon(name, color, size, sw, x, y)

    def product(self, sku, w, h, x, y):
        p = os.path.join(ASSETS, "bracelets", sku + ".webp")
        return kit.photo("file://" + p, w, h, x, y) if os.path.exists(p) else None

    # ── helpers shared by the looks ──
    def _sq_photo(self, sku):
        p = os.path.join(ASSETS, "bracelets", "sq", sku + ".webp")
        return "file://" + p if os.path.exists(p) else None

    def grid_cells(self, counts, on_bg, off_border, fg, size=56, radius=10, font=None, empty_bg="transparent"):
        font = font or self.T.display["family"]
        cells = ""
        for row in GRID:
            for d in row:
                n = counts.get(d, 0)
                if n:
                    cells += (f'<div style="width:{size}px;height:{size}px;border-radius:{radius}px;display:flex;align-items:center;justify-content:center;'
                              f'background:{on_bg};color:{fg};font-family:{font};font-size:{int(size * .5)}px">{d}</div>')
                else:
                    cells += f'<div style="width:{size}px;height:{size}px;border-radius:{radius}px;border:1.5px dashed {off_border};background:{empty_bg}"></div>'
        return f'<div style="display:grid;grid-template-columns:repeat(3,{size}px);gap:{int(size * .18)}px">{cells}</div>'


# ════════════════════════════ Daktilo Dispatch (Mulank 8) ════════════════════════════
class Daktilo(Look):
    plate_em = 0.76
    BLACK, FOLDER_DARK, MAT = "#0B0B0C", "#1F2022", "#FFFFFF"

    def ground_css(self, ground, dark, n):
        return f"background:{self.BLACK}"

    def frame(self, ground, dark, n):
        fill = self.FOLDER_DARK if dark else ground
        tab = "#FFFAF6" if not dark else "#C9C2B8"
        label = "PERSONAL YEAR FORECAST"
        return (f'<svg class="frame" width="720" height="1280" viewBox="0 0 720 1280">'
                f'<path d="M12 34 Q12 24 22 24 L278 24 Q286 24 290 31 L302 52 L698 52 Q708 52 708 62 L708 1258 Q708 1268 698 1268 L22 1268 Q12 1268 12 1258 Z" fill="{fill}"/>'
                f'{self._seam(dark)}'
                f'<text x="34" y="44" font-family="Inconsolata" font-weight="700" font-size="13" letter-spacing="1.6" fill="{self.BLACK if not dark else tab}">{label}</text>'
                f'<text x="688" y="40" text-anchor="end" font-family="Inconsolata" font-size="11" letter-spacing="1.4" fill="rgba(255,250,246,.62)">FILE NO. VA-{{{{FILE}}}}</text>'
                f'</svg>')

    @staticmethod
    def _seam(dark):
        return "" if dark else '<path d="M12 52 L708 52" stroke="rgba(0,0,0,.06)" stroke-width="1"/>'

    def footer(self, name, n, dark):
        c = "rgba(255,250,246,.7)" if dark else "#151617"
        line = "rgba(255,250,246,.35)" if dark else "rgba(21,22,23,.55)"
        return (f'<div class="abs" style="left:34px;right:34px;bottom:46px;height:1px;background:{line};z-index:40"></div>'
                f'<div class="foot dk" style="color:{c}"><span>Veshannastro</span><span>{esc(name)}</span><span>{n:02d} / {{{{TOTAL}}}}</span></div>')

    def extra_css(self):
        T = self.T
        return f"""
.foot{{left:34px;right:34px;bottom:24px;opacity:1;font-size:10.5px;letter-spacing:.14em;font-weight:400}}
.kick{{background:{T.INK};color:#FFFAF6;border-radius:0;font-weight:700;letter-spacing:.16em;padding:5px 9px 4px}}
.kick.pk,.kick.wh{{background:{T.INK};color:#FFFAF6}}
.dark .kick{{background:#FFFAF6;color:{T.INK}}}
.accent{{width:120px;height:2px;border-radius:0;background:{T.INK}}}
.dark .accent{{background:#FFFAF6}}
.plate{{background:#FFFAF6;color:{T.INK};text-transform:uppercase;letter-spacing:-.01em;padding:6px 12px 4px;box-shadow:none}}
.lead{{font-size:16.5px;line-height:1.55}}.body{{font-size:14.6px;line-height:1.55}}.small{{font-size:13.4px;line-height:1.5}}
ul.dots li:before{{border-radius:0;width:8px;height:8px;top:.5em}}
ul.dots li.good:before{{background:{T.INK}}}
ul.dots li.care:before{{background:transparent;border:1.5px solid {T.INK}}}
ul.dots li.mixed:before{{background:linear-gradient(135deg,{T.INK} 50%,transparent 50%);border:1.5px solid {T.INK}}}
ul.dots li.neutral:before{{background:{T.INK};height:2px;top:.75em}}
ul.dots li.trait:before{{background:{T.INK};border-radius:50%}}
.dark ul.dots li:before{{background:#FFFAF6;border-color:#FFFAF6}}
.ruled>div{{border-bottom:1px solid {T.INK}}}.ruled>div:first-child{{border-top:1px solid {T.INK}}}
table.t td{{border-bottom:1px solid rgba(21,22,23,.5)}}
.bar{{background:{T.INK};color:#FFFAF6;border-radius:0}}
.bar .go{{color:#FFFAF6;text-decoration:underline;text-underline-offset:3px}}
.bar .alt{{color:#FFFAF6}}
.dark .bar{{background:#FFFAF6;color:{T.INK}}}.dark .bar .go,.dark .bar .alt{{color:{T.INK}}}
.tile{{border:1px solid rgba(21,22,23,.18)}}
mark,.hl{{background:#151617;color:#FFFAF6;padding:0 3px}}
"""

    # a matted documentary print (grey, grained), for every feature shape
    def _print(self, w, h, x, y, label=None, dark=False):
        cap = (f'<div class="abs caps" style="left:10px;bottom:-22px;font-size:10px;letter-spacing:.14em;color:{"#C9C2B8" if dark else "#151617"}">{label}</div>'
               if label else "")
        return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{self.MAT};padding:9px;'
                f'box-shadow:0 1px 3px rgba(0,0,0,.18)"><div style="width:100%;height:100%;'
                f'background:radial-gradient(120% 90% at 30% 20%,#E2DCD3 0%,#B9B2A8 55%,#8E877E 100%)"></div>{cap}</div>')

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        if kind == "bumps":
            return ""
        w, h = min(w, 720 - x - 40), min(h, 1220 - y)
        if kind in ("flower", "disc"):   # a print is opaque: keep it clear of the copy that Rosette lets run over its shapes
            h = int(h * .8)
        if w < 60 or h < 60:
            return ""
        return self._print(w, h, x, y)

    def _mark(self, x, y):
        if x is None:
            return f'<span style="display:inline-block;width:14px;height:14px;background:{self.T.INK};margin-top:6px"></span>'
        return ""

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._mark(x, y)

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._mark(x, y)

    def sparkle(self, color, size, x=None, y=None):
        return self._mark(x, y)

    def heart(self, color, size, x=None, y=None):
        return self._mark(x, y)

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._mark(x, y)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        return ""

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        s = self.fit(text, size, width or 600)
        return f'<div class="plate" style="font-size:{s}px">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        return (f'<div class="abs" style="left:{x + 40}px;top:{y + 20}px;width:{w - 80}px;height:{w - 80}px;background:#fff;padding:12px;box-shadow:0 2px 6px rgba(0,0,0,.35)">'
                f'<img src="{src}" style="width:100%;height:100%;object-fit:cover;display:block"></div>'
                f'<div class="abs caps" style="left:{x + 40}px;top:{y + w - 40}px;font-size:10.5px;color:#C9C2B8">EXHIBIT A &#183; THE BRACELET FOR YOUR NUMBER</div>')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        extra = f" &#183; MASTER {r.M}" if r.M else (f" &#183; KARMIC {r.K}" if r.K else "")
        cells = self.grid_cells(r.cnt, T.INK, "rgba(21,22,23,.45)", "#FFFAF6", size=50, radius=0, font="Montserrat")
        inner = f"""
<div class="abs caps" style="right:50px;top:84px;font-size:11.5px;letter-spacing:.14em">PRIVATE READING / {Y}</div>
<div style="margin-top:150px" class="disp" ><div style="font-size:84px;line-height:.9">WHAT DOES</div><div style="font-size:84px;line-height:.9">{Y} ASK</div>
<div style="font-size:84px;line-height:.9;text-align:right;padding-right:10px">OF YOU?</div></div>
<div class="abs" style="left:398px;top:610px;width:260px;background:#fff;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.2)">
<div style="background:#E9E3DA;padding:22px 0;display:flex;justify-content:center">{cells}</div></div>
<div class="abs" style="left:398px;top:900px;width:270px" class="small"><div class="small">A personal year forecast for <b>{esc(r.name_full)}</b>, born {r.dob_text}.</div>
<div class="small" style="margin-top:10px">Every figure in this file comes from that date and that name.</div></div>
<div class="abs" style="left:50px;top:640px;width:300px">
<div class="caps" style="font-size:11px;letter-spacing:.14em">THE NUMBERS ON FILE</div>
<div style="margin-top:10px;border-top:1px solid #151617">
{''.join(f'<div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #151617"><span class="small">{a}</span><span class="num" style="font-size:22px">{b}</span></div>' for a, b in [("Psychic number", r.P), ("Destiny number", r.D), ("Name number", r.NT or "-"), (f"Personal year {Y}", r.PY)] + ([("Master number", r.M)] if r.M else []))}
</div></div>
<div class="abs caps" style="left:50px;bottom:120px;font-size:11px;letter-spacing:.14em">FILE NO. VA-{{{{FILE}}}}</div>
<div class="abs small" style="left:50px;bottom:88px">This edition is designed for Mulank {r.P} &#183; {PLANET[r.P]}.</div>
"""
        return T.CREAM, inner


# ════════════════════════════ Dabba (Mulank 1) ════════════════════════════
class Dabba(Look):
    plate_em = 0.60
    PAIRS = None

    def _pair(self, n):
        T = self.T
        return [T.PINK, T.ORANGE, T.LBLUE, "#8DBF7F"][n % 4]

    def frame(self, ground, dark, n):
        c = self.T.ORANGE if dark else self._pair(n)
        return f'<div class="frame"><div style="position:absolute;right:0;top:0;width:26px;height:1280px;background:{c}"></div></div>'

    def extra_css(self):
        T = self.T
        return f"""
.kick{{background:{T.ORANGE};color:{T.INK};border-radius:0;font-weight:400;letter-spacing:.1em;padding:6px 10px 4px}}
.kick.pk{{background:{T.PINK};color:{T.INK}}}.kick.wh{{background:{T.WHITE};color:{T.INK}}}
.accent{{width:76px;height:8px;border-radius:0;background:{T.ORANGE}}}
.plate{{background:transparent !important;color:var(--pc,{T.INK});text-transform:lowercase;letter-spacing:-.03em;line-height:.86;padding:0;box-shadow:none}}
.dark .plate{{color:{T.CREAM}}}.dark .onblob .plate{{color:{T.INK}}}
.lead{{font-size:17px}}.body{{font-size:14.8px}}.small{{font-size:13.6px}}
ul.dots li:before{{border-radius:0}}
.bar{{background:{T.INK};color:{T.CREAM};border-radius:0}}.bar .go{{color:{T.ORANGE}}}.bar .alt{{color:{T.CREAM}}}
.dark .bar{{background:{T.CREAM};color:{T.INK}}}.dark .bar .go{{color:{T.COBALT}}}.dark .bar .alt{{color:{T.INK}}}
table.t td{{border-bottom:1.5px solid rgba(59,36,22,.35)}}
.ruled>div{{border-bottom:1.5px solid rgba(59,36,22,.35)}}.ruled>div:first-child{{border-top:1.5px solid rgba(59,36,22,.35)}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        if kind == "bumps":
            return f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{1280 - y}px;background:{color};z-index:-1"></div>'
        return f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color}"></div>'

    def _mark(self, color, size, x, y):
        if x is None:
            return f'<span style="display:inline-block;width:18px;height:18px;background:{color};margin-top:4px"></span>'
        return ""

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._mark(color, size, x, y)

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._mark(color, size, x, y)

    def sparkle(self, color, size, x=None, y=None):
        return self._mark(color, size, x, y)

    def heart(self, color, size, x=None, y=None):
        return self._mark(color, size, x, y)

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._mark(color, size, x, y)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        return ""

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        s = self.fit(text, round(size * 1.45), width or 620)
        return f'<div class="plate" style="font-size:{s}px;--pc:{color}">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        T = self.T
        return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{w}px;background:{T.PINK}"></div>'
                f'<img class="abs" src="{src}" style="left:{x + 60}px;top:{y + 60}px;width:{w - 120}px;height:{w - 120}px;object-fit:cover">')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        cells = self.grid_cells(r.cnt, T.INK, "rgba(59,36,22,.5)", T.CREAM, size=54, radius=0)
        extra = f"Master {r.M} &#183; " if r.M else (f"Karmic {r.K} &#183; " if r.K else "")
        size = 300 if len(str(Y)) == 4 else 260
        inner = f"""
<div class="abs" style="left:262px;top:0;width:236px;height:1280px;background:{T.PINK}"></div>
<div class="abs" style="left:0;top:1060px;width:262px;height:220px;background:{T.ORANGE}"></div>
<div class="abs" style="left:50px;top:70px;width:196px">
<div style="font-family:SourceSerif;font-size:31px;line-height:1.15">Personal Year Forecast</div>
<div class="body" style="margin-top:14px">A private reading for {esc(r.name_full)}, born {r.dob_text}</div></div>
<div class="abs" style="left:292px;top:330px">{cells}</div>
<div class="abs caps" style="left:292px;top:540px;font-size:11px;letter-spacing:.12em">your Lo Shu grid</div>
<div class="abs" style="left:524px;top:70px;width:150px">
<div class="small">Psychic {r.P}<br>Destiny {r.D}<br>{extra}{("Name " + str(r.NT) + "<br>") if r.NT else ""}Personal Year {r.PY}</div>
<div class="small" style="margin-top:22px">Designed for Mulank {r.P}, {PLANET[r.P]}.</div></div>
<div class="abs disp" style="left:34px;top:{1250 - size}px;font-size:{size}px;line-height:.8;letter-spacing:-.04em;color:{T.INK};white-space:nowrap">{Y}</div>
"""
        return T.CREAM, inner


# ════════════════════════════ Broadcast Cookbook (Mulank 2) ════════════════════════════
class Broadcast(Look):
    plate_em = 0.80

    def frame(self, ground, dark, n):
        T = self.T
        c = T.BERRY if dark else T.ORANGE
        return (f'<div class="frame"><div style="position:absolute;left:0;top:0;width:22px;height:1280px;background:{c}"></div>'
                f'<div style="position:absolute;left:22px;top:0;width:6px;height:1280px;background:linear-gradient(90deg,rgba(0,0,0,.18),rgba(0,0,0,0))"></div></div>')

    def extra_css(self):
        T = self.T
        return f"""
.kick{{background:{T.BERRY};color:{T.CREAM};border-radius:0;letter-spacing:.14em;padding:6px 11px 5px;font-weight:600}}
.kick.pk{{background:{T.BERRY};color:{T.CREAM}}}.kick.wh{{background:{T.CREAM};color:{T.BERRY}}}
.accent{{width:76px;height:5px;border-radius:0;background:{T.ORANGE}}}
.plate{{background:transparent !important;font-family:Corben;font-weight:700;text-transform:uppercase;letter-spacing:.005em;line-height:.95;padding:0;box-shadow:none;color:{T.INK}}}
.plate.cap{{text-shadow:var(--sh) var(--sh) 0 {T.BERRY}}}
.plate.scr{{font-family:Ballet;font-weight:400;text-transform:none;letter-spacing:0;line-height:.86;color:{T.BERRY};text-shadow:none;-webkit-text-stroke:.9px currentColor;padding-left:.12em}}
.dark .plate.cap{{color:{T.CREAM}}}.dark .plate.scr{{color:{T.ORANGE}}}
.dark .onblob .plate.cap{{color:{T.INK}}}.dark .onblob .plate.scr{{color:{T.BERRY}}}
ul.dots li:before{{border-radius:0}}
.bar{{background:{T.NAVY};color:{T.CREAM};border-radius:0;box-shadow:4px 4px 0 rgba(42,22,16,.18)}}.bar .go{{color:{T.ORANGE}}}.bar .alt{{color:{T.CREAM}}}
.dark .bar{{background:{T.CREAM};color:{T.INK}}}.dark .bar .go{{color:{T.BERRY}}}.dark .bar .alt{{color:{T.INK}}}
.pnl,.tile{{box-shadow:4px 4px 0 rgba(42,22,16,.12)}}
table.t td{{border-bottom:1.5px solid {T.RULE}}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        T = self.T
        if kind == "bumps":
            cols = [T.ORANGE, T.BERRY, T.LBLUE]
            tw = max(60, w // 3 - 6)
            return "".join(f'<div class="abs" style="left:{x + i * (tw + 8)}px;top:{1280 - 58}px;width:{tw}px;height:70px;background:{c};'
                           f'border-radius:12px 12px 0 0 !important"></div>' for i, c in enumerate(cols))
        if kind == "disc":
            return (f'<div class="abs round" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color};border-radius:50%;'
                    f'box-shadow:6px 6px 0 rgba(42,22,16,.18)"></div>')
        return f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color};box-shadow:7px 7px 0 rgba(42,22,16,.16)"></div>'

    def _tab(self, color, x, y):
        T = self.T
        if x is None:
            return f'<span style="display:inline-block;width:18px;height:18px;background:{T.ORANGE};box-shadow:3px 3px 0 {T.BERRY};margin-top:4px"></span>'
        if x < 360:
            return ""
        c = [T.BERRY, T.ORANGE, T.LBLUE, T.PINK][(y // 97) % 4]
        return f'<div class="abs" style="right:0;top:{y}px;width:30px;height:74px;background:{c};border-radius:10px 0 0 10px !important"></div>'

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._tab(color, x, y)

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._tab(color, x, y)

    def sparkle(self, color, size, x=None, y=None):
        return self._tab(color, x, y)

    def heart(self, color, size, x=None, y=None):
        return self._tab(color, x, y)

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._tab(color, x, y)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        T = self.T
        return "".join(f'<div class="abs" style="right:0;top:{140 + i * 96}px;width:30px;height:80px;background:{c};border-radius:10px 0 0 10px !important"></div>'
                       for i, c in enumerate([T.BERRY, T.ORANGE, T.LBLUE, T.PINK]))

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        w = width or 600
        if rot > 0:   # the second line of a pair: one looping script phrase that crosses the capitals' baseline
            s = min(round(size * 2.1), int(w / max(1, len(str(text)) * 0.40)))
            return f'<div class="plate scr" style="font-size:{s}px;margin-top:-{int(s * .04)}px;transform:rotate(-4deg)">{str(text).lower()}</div>'
        s = self.fit(text, size, w)
        return f'<div class="plate cap" style="font-size:{s}px;--sh:{max(2, round(s * .065))}px">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        return (f'<img class="abs" src="{src}" style="left:{x + 30}px;top:{y + 10}px;width:{w - 60}px;height:{w - 60}px;object-fit:cover;'
                f'box-shadow:9px 9px 0 rgba(0,0,0,.25)">')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        cells = self.grid_cells(r.cnt, T.PINK, "rgba(251,244,230,.45)", T.INK, size=52, radius=0, font="Corben")
        extra = f" &#183; Master {r.M}" if r.M else (f" &#183; Karmic {r.K}" if r.K else "")
        inner = f"""
<div class="abs" style="left:0;top:0;width:70px;height:1280px;background:{T.ORANGE}"></div>
<div class="abs" style="left:70px;top:0;width:8px;height:1280px;background:linear-gradient(90deg,rgba(0,0,0,.25),rgba(0,0,0,0))"></div>
<div class="abs caps" style="left:47px;top:1180px;transform:rotate(-90deg);transform-origin:0 0;white-space:nowrap;font-family:Newsreader;font-size:17px;letter-spacing:.2em;color:{T.NAVY}">Personal year {Y} &#183; Mulank {r.P}</div>
<div class="abs" style="left:112px;top:96px;width:570px">
<div style="font-family:Ballet;font-size:130px;line-height:.8;color:{T.ORANGE}">the</div>
<div style="font-family:Corben;font-weight:700;font-size:86px;line-height:.92;color:{T.CREAM};text-shadow:6px 6px 0 {T.BERRY};margin-top:-18px">PERSONAL<br>YEAR</div>
<div style="font-family:Ballet;font-size:128px;line-height:.8;color:{T.ORANGE};margin:-22px 0 0 60px;transform:rotate(-5deg);position:relative;z-index:2">forecast</div>
<div style="font-family:Corben;font-weight:700;font-size:150px;line-height:.9;color:{T.CREAM};text-shadow:8px 8px 0 {T.BERRY};margin-top:14px">{Y}</div>
</div>
<div class="abs" style="left:450px;top:860px">{cells}</div>
<div class="abs" style="left:450px;top:1060px;width:200px;font-family:Newsreader;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{T.PINK}">Your Lo Shu grid</div>
<div class="abs" style="left:112px;top:870px;width:300px;color:{T.CREAM}">
<div style="font-family:Newsreader;font-size:17px;line-height:1.5">A private reading for {esc(r.name_full)}, born {r.dob_text}.</div>
<div style="font-family:Newsreader;font-size:14px;line-height:1.6;margin-top:16px;color:{T.PINK}">Psychic {r.P} &#183; Destiny {r.D}{extra}<br>{("Name " + str(r.NT) + " &#183; ") if r.NT else ""}Personal Year {r.PY}</div>
<div class="kick" style="margin-top:22px">Designed for Mulank {r.P} &#183; {PLANET[r.P]}</div></div>
"""
        return T.NAVY, inner


# ════════════════════════════ Torn (Mulank 4) ════════════════════════════
def _torn_rect(x, y, w, h, rng, amp=5, step=14):
    """A rough rectangle with torn edges, as SVG polygon points."""
    pts = []
    def run(x0, y0, x1, y1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
        nx, ny = (y1 - y0), -(x1 - x0)
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L, ny / L
        for i in range(n):
            t = i / n
            j = rng.uniform(-amp, amp) + (rng.uniform(-amp * 2.2, amp * 2.2) if rng.random() < .08 else 0)
            pts.append((x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j))
    run(x, y, x + w, y); run(x + w, y, x + w, y + h); run(x + w, y + h, x, y + h); run(x, y + h, x, y)
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def _torn_round(cx, cy, rx, ry, rng, amp=0.06, n=56):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rng.uniform(-amp, amp)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def _torn_clip(rng, amp=3, n=22):
    """A clip-path polygon (percent across, px deep) that tears the top and bottom edge of any box."""
    top = [f"{i * 100 / n:.1f}% {rng.uniform(0, amp):.1f}px" for i in range(n + 1)]
    bot = [f"{100 - i * 100 / n:.1f}% calc(100% - {rng.uniform(0, amp):.1f}px)" for i in range(n + 1)]
    return "polygon(" + ",".join(top + bot) + ")"


class Torn(Look):
    plate_em = 0.48
    EDGE = "#F7F3EA"

    def _piece(self, pts_paper, pts_edge, color, extra=""):
        return (f'<polygon points="{pts_edge}" fill="{self.EDGE}"/>'
                f'<polygon points="{pts_paper}" fill="{color}" {extra}/>')

    def frame(self, ground, dark, n):
        T = self.T
        rng = _rng("frame", n)
        papers = [T.KRAFT, T.LBLUE, T.PINK, T.CREAM] if not dark else ["#2A2B2F", "#3A3B40", T.KRAFT]
        a, b = rng.sample(papers, 2)
        w1 = rng.randint(170, 300)
        w2 = rng.randint(160, 280)
        s = ""
        s += self._piece(_torn_rect(-20, -20, w1, 52 + rng.randint(0, 10), rng), _torn_rect(-22, -22, w1 + 4, 58 + rng.randint(0, 10), rng), a)
        s += self._piece(_torn_rect(720 - w2, 1238 - rng.randint(0, 10), w2 + 30, 70, rng), _torn_rect(718 - w2, 1234 - rng.randint(0, 8), w2 + 34, 78, rng), b)
        if n % 2:
            s += self._piece(_torn_rect(696, 260 + rng.randint(0, 300), 40, 260, rng, amp=4), _torn_rect(692, 256 + rng.randint(0, 300), 46, 268, rng, amp=4), a)
        return f'<svg class="frame" width="720" height="1280" viewBox="0 0 720 1280">{s}</svg>'

    def extra_css(self):
        T = self.T
        rng = _rng("css")
        return f"""
.kick{{background:{T.ORANGE};color:{T.INK};border-radius:0;font-weight:700;letter-spacing:.12em;padding:7px 12px 6px;clip-path:{_torn_clip(rng, 2.5, 14)}}}
.kick.pk{{background:{T.PINK}}}.kick.wh{{background:{T.CREAM}}}
.accent{{width:90px;height:7px;border-radius:0;background:{T.KRAFT};clip-path:{_torn_clip(rng, 2, 10)}}}
.plate{{background:{T.CREAM};color:{T.INK};text-transform:uppercase;letter-spacing:.005em;line-height:1;padding:12px 22px 10px;box-shadow:2px 3px 0 rgba(0,0,0,.18);clip-path:{_torn_clip(rng, 4, 18)}}}
.plate.k{{background:{T.KRAFT}}}.plate.b{{background:{T.LBLUE}}}.plate.y{{background:{T.ORANGE}}}
.pnl,.tile{{clip-path:{_torn_clip(rng, 3.5, 26)}}}
ul.dots li:before{{border-radius:0;transform:rotate(8deg)}}
.bar{{background:{T.NAVY};color:{T.CREAM};border-radius:0;clip-path:{_torn_clip(rng, 3, 24)}}}.bar .go{{color:{T.ORANGE}}}.bar .alt{{color:{T.CREAM}}}
.dark .bar{{background:{T.CREAM};color:{T.INK}}}.dark .bar .go{{color:{T.BERRY}}}.dark .bar .alt{{color:{T.INK}}}
table.t td{{border-bottom:1.5px solid rgba(20,20,22,.28)}}
.ruled>div{{border-bottom:1.5px solid rgba(20,20,22,.28)}}.ruled>div:first-child{{border-top:1.5px solid rgba(20,20,22,.28)}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        rng = _rng("blob", x, y, w, h)
        if kind == "bumps":
            pts = _torn_rect(x - 20, y + 40, w + 120, 200, rng, amp=6)
            edge = _torn_rect(x - 24, y + 34, w + 128, 210, rng, amp=6)
            c = self.T.KRAFT
        elif kind in ("disc", "flower"):
            pts = _torn_round(x + w / 2, y + h / 2, w / 2 - 4, h / 2 - 4, rng)
            edge = _torn_round(x + w / 2, y + h / 2, w / 2, h / 2, rng, amp=.07)
            c = color
        else:
            pts = _torn_rect(x, y, w, h, rng, amp=7)
            edge = _torn_rect(x - 5, y - 5, w + 10, h + 10, rng, amp=7)
            c = color
        return (f'<svg class="abs" style="left:0;top:0;overflow:visible" width="720" height="1280" viewBox="0 0 720 1280">'
                f'<polygon points="{edge}" fill="{self.EDGE}" transform="translate(3 4)" opacity=".35" style="fill:#000"/>'
                f'{self._piece(pts, edge, c)}</svg>')

    def _tape(self, x, y, size, seed):
        if x is None:
            return f'<span style="display:inline-block;width:20px;height:20px;background:{self.T.ORANGE};transform:rotate(-6deg);margin-top:4px"></span>'
        rng = _rng("tape", x, y, seed)
        w, h = int(size * 1.7), int(size * .55)
        x = min(x, 720 - w - 8)
        return (f'<div class="abs" style="left:{x}px;top:{y + size // 3}px;width:{w}px;height:{h}px;background:rgba(232,220,192,.78);'
                f'transform:rotate({rng.uniform(-14, 14):.1f}deg);box-shadow:0 1px 2px rgba(0,0,0,.12)"></div>')

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._tape(x, y, size, "a")

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._tape(x, y, size, "p")

    def sparkle(self, color, size, x=None, y=None):
        return self._tape(x, y, size, "s")

    def heart(self, color, size, x=None, y=None):
        return self._tape(x, y, size, "h")

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._tape(x, y, size, "r")

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        rng = _rng("scallop")
        return (f'<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">'
                f'{self._piece(_torn_rect(676, -20, 80, 1320, rng, amp=6), _torn_rect(670, -24, 90, 1330, rng, amp=6), self.T.KRAFT)}</svg>')

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        s = self.fit(text, round(size * 1.12), width or 600)
        kind = ["", "k", "b", "y"][len(str(text)) % 4]
        return f'<div class="plate {kind}" style="font-size:{s}px;transform:rotate({rot * .5:.1f}deg)">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        rng = _rng("photo", sku)
        return (f'<div class="abs" style="left:{x + 30}px;top:{y + 10}px;width:{w - 60}px;height:{w - 60}px;background:{self.EDGE};'
                f'clip-path:{_torn_clip(rng, 9, 20)};transform:rotate(-2deg)"><img src="{src}" style="width:100%;height:100%;object-fit:cover;'
                f'clip-path:{_torn_clip(rng, 9, 20)};transform:scale(.97)"></div>')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        rng = _rng("cover", r.P)
        cells = self.grid_cells(r.cnt, T.INK, "rgba(20,20,22,.55)", T.CREAM, size=58, radius=0, font="Anton", empty_bg="rgba(198,164,124,.32)")
        extra = f" &#183; Master {r.M}" if r.M else (f" &#183; Karmic {r.K}" if r.K else "")
        svg = ('<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">'
               + self._piece(_torn_rect(-30, -30, 520, 600, rng, amp=9), _torn_rect(-34, -34, 528, 610, rng, amp=9), T.KRAFT)
               + self._piece(_torn_rect(250, 150, 520, 560, rng, amp=9), _torn_rect(244, 144, 532, 572, rng, amp=9), T.LBLUE)
               + self._piece(_torn_rect(40, 760, 330, 330, rng, amp=7), _torn_rect(34, 754, 342, 342, rng, amp=7), T.CREAM)
               + self._piece(_torn_rect(400, 1120, 360, 200, rng, amp=7), _torn_rect(394, 1114, 372, 212, rng, amp=7), T.PINK)
               + '</svg>')
        inner = f"""
{svg}
<div class="abs" style="left:290px;top:244px;width:400px">
<div class="disp" style="font-size:96px;line-height:.95;text-transform:uppercase;color:{T.INK}">Personal<br>year<br>forecast</div>
<div style="font-family:Newsreader;font-size:19px;line-height:1.45;margin-top:22px;color:{T.INK}">A private reading for {esc(r.name_full)}.<br>Born {r.dob_text}.</div></div>
<div class="abs" style="left:300px;top:676px;padding:12px 20px 10px;background:{T.ORANGE};clip-path:{_torn_clip(rng, 3, 14)};transform:rotate(-2deg)">
<span class="caps" style="font-size:13px;letter-spacing:.14em;font-weight:700">{Y} &#183; designed for Mulank {r.P} &#183; {PLANET[r.P]}</span></div>
<div class="abs" style="left:46px;top:40px"><div class="disp" style="font-size:190px;line-height:.9;color:{T.INK}">{Y}</div></div>
<div class="abs" style="left:108px;top:800px">{cells}</div>
<div class="abs caps" style="left:108px;top:1014px;font-size:11px;letter-spacing:.14em;font-weight:700">Your Lo Shu grid</div>
<div class="abs" style="left:150px;top:742px;width:120px;height:34px;background:rgba(232,220,192,.8);transform:rotate(-8deg)"></div>
<div class="abs" style="left:440px;top:880px;width:240px;font-family:Newsreader;font-size:16px;line-height:1.6;color:{T.INK}">Psychic {r.P} &#183; Destiny {r.D}{extra}<br>{("Name " + str(r.NT) + " &#183; ") if r.NT else ""}Personal Year {r.PY}</div>
"""
        return T.CREAM, inner


# ════════════════════════════ Contour Stack (Mulank 7) ════════════════════════════
def _wave(x0, x1, base, amp, phase, waves, bottom):
    """A wavy band from x0 to x1 whose top edge undulates around `base`, closed down to `bottom`."""
    n = 48
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = base + amp * math.sin(phase + waves * 2 * math.pi * i / n) + amp * .35 * math.sin(phase * 1.7 + waves * 4.3 * math.pi * i / n)
        pts.append((x, y))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts[1:])
    return d + f" L{x1:.1f},{bottom} L{x0:.1f},{bottom} Z"


def _rings(cx, cy, R, layers, colors, rng):
    out = []
    for i in range(layers):
        r = R * (1 - i / (layers + .6))
        ph = rng.uniform(0, 6.28)
        pts = []
        for k in range(73):
            a = 2 * math.pi * k / 72
            rr = r * (1 + .06 * math.sin(5 * a + ph) + .03 * math.sin(9 * a + ph * 2))
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        out.append(f'<path d="{d}" fill="rgba(0,0,0,.16)" transform="translate(0 5)"/><path d="{d}" fill="{colors[i % len(colors)]}"/>')
    return "".join(out)


class Contour(Look):
    plate_em = 0.40
    GREENS = ["#AFD472", "#87C540", "#C4DE8E", "#6DAB26"]

    def _layers(self):
        T = self.T
        return [self.GREENS[2], self.GREENS[0], self.GREENS[1], T.ORANGE]

    def _land(self, x0, x1, top, bottom, seed, layers=4):
        rng = _rng("land", seed)
        cols = self._layers()
        s = ""
        span = bottom - top
        for i in range(layers):
            base = top + span * i / (layers + .4)
            d = _wave(x0, x1, base, rng.uniform(8, 18), rng.uniform(0, 6.28), rng.uniform(1.2, 2.4), bottom)
            s += f'<path d="{d}" fill="rgba(31,42,20,.20)" transform="translate(0 -6)"/><path d="{d}" fill="{cols[i % len(cols)]}"/>'
        return s

    def extra_css(self):
        T = self.T
        return f"""
.kick{{background:#AFD472;color:{T.INK};border-radius:8px;font-family:Smooch;font-weight:800;font-size:15px;letter-spacing:.06em;padding:4px 11px 3px;box-shadow:inset 0 -3px 0 rgba(31,42,20,.18)}}
.kick.pk{{background:{T.ORANGE};color:{T.INK}}}.kick.wh{{background:{T.WHITE};color:{T.INK}}}
.accent{{width:76px;height:7px;border-radius:4px;background:#87C540}}
.plate{{background:transparent;color:var(--pc,{T.INK});text-transform:uppercase;letter-spacing:.01em;line-height:.86;padding:0;box-shadow:none}}
.dark .plate{{color:{T.CREAM}}}.dark .onblob .plate{{color:{T.INK}}}
.pnl,.tile{{box-shadow:inset 0 -4px 0 rgba(31,42,20,.16)}}
ul.dots li:before{{border-radius:3px}}
.bar{{background:{T.WHITE};color:{T.INK};border-radius:12px;box-shadow:inset 0 -4px 0 #87C540}}.bar .go{{color:{T.BERRY}}}.bar .alt{{color:{T.COBALT}}}
table.t th{{font-family:Smooch;font-weight:800;font-size:15px;letter-spacing:.04em;text-transform:uppercase}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        rng = _rng("cblob", x, y, w, h)
        if kind == "bumps":
            return (f'<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">'
                    f'{self._land(-10, 730, min(y, 1150) - 10, 1290, (x, y))}</svg>')
        if kind in ("disc", "flower"):
            R = min(w, h) / 2
            cols = [self.T.ORANGE, self.GREENS[1], self.GREENS[0], self.GREENS[2], self.T.PINK]
            return (f'<svg class="abs" style="left:0;top:0;overflow:visible" width="720" height="1280" viewBox="0 0 720 1280">'
                    f'{_rings(x + w / 2, y + h / 2, R, 5, cols, rng)}</svg>')
        # cloud: a hill of stacked paper inside the box
        s = self._land(x, x + w, y, y + h, (x, y, "h"), layers=4)
        clip = f'<clipPath id="c{x}{y}"><rect x="{x}" y="{y - 20}" width="{w}" height="{h + 20}" rx="26"/></clipPath>'
        return (f'<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280"><defs>{clip}</defs>'
                f'<g clip-path="url(#c{x}{y})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{self.T.PINK}"/>{s}</g></svg>')

    def _mark(self, x, y, size, seed):
        T = self.T
        if x is None:
            return f'<span style="display:inline-block;width:20px;height:20px;border-radius:5px;background:#87C540;box-shadow:inset 0 -3px 0 rgba(31,42,20,.2);margin-top:4px"></span>'
        rng = _rng("cm", x, y, seed)
        R = size / 2
        return (f'<svg class="abs" style="left:{x}px;top:{y}px;overflow:visible" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
                f'{_rings(R, R, R, 3, [T.ORANGE, self.GREENS[1], self.GREENS[2]], rng)}</svg>')

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._mark(x, y, size, "a")

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._mark(x, y, size, "p")

    def sparkle(self, color, size, x=None, y=None):
        return self._mark(x, y, size, "s")

    def heart(self, color, size, x=None, y=None):
        return self._mark(x, y, size, "h")

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._mark(x, y, size, "r")

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        rng = _rng("cscal")
        cols = self._layers()
        s = ""
        for i in range(4):
            xb = 720 - 70 + i * 16
            n = 48
            pts = []
            ph = rng.uniform(0, 6.28)
            for k in range(n + 1):
                yy = 1280 * k / n
                pts.append((xb + 10 * math.sin(ph + 2.2 * 2 * math.pi * k / n), yy))
            d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " L740,1280 L740,0 Z"
            s += f'<path d="{d}" fill="rgba(31,42,20,.2)" transform="translate(-5 0)"/><path d="{d}" fill="{cols[i]}"/>'
        return f'<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">{s}</svg>'

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        s = self.fit(text, round(size * 1.4), width or 620)
        return f'<div class="plate" style="font-size:{s}px;--pc:{color}">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        return (f'<div class="abs" style="left:{x + 40}px;top:{y + 10}px;width:{w - 80}px;height:{w - 80}px;border-radius:34px;overflow:hidden;'
                f'box-shadow:inset 0 -6px 0 rgba(31,42,20,.2),0 8px 0 rgba(31,42,20,.22)"><img src="{src}" style="width:100%;height:100%;object-fit:cover"></div>')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        cells = self.grid_cells(r.cnt, T.INK, "rgba(31,42,20,.4)", T.CREAM, size=50, radius=10, font="Smooch")
        extra = f" &#183; Master {r.M}" if r.M else (f" &#183; Karmic {r.K}" if r.K else "")
        rng = _rng("ccover", r.P)
        cols = self._layers()
        land = ""
        for i in range(5):
            # diagonal bands rising from the lower left to the upper right
            n, pts = 48, []
            ph = rng.uniform(0, 6.28)
            for k in range(n + 1):
                x = -20 + 760 * k / n
                yy = 980 - 520 * k / n + i * 70 + 26 * math.sin(ph + 2.4 * math.pi * k / n)
                pts.append((x, yy))
            d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " L740,1300 L-20,1300 Z"
            c = (cols + [T.BERRY])[i % 5]
            land += f'<path d="{d}" fill="rgba(31,42,20,.22)" transform="translate(0 -7)"/><path d="{d}" fill="{c}"/>'
        inner = f"""
<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">{land}</svg>
<div class="disp" style="font-size:150px;line-height:.82;margin-top:36px">Personal<br>year<br>forecast</div>
<div class="disp" style="font-size:230px;line-height:.8;margin-top:6px;color:{T.BERRY}">{Y}</div>
<div style="font-family:Rubik;font-weight:500;font-size:21px;line-height:1.35;margin-top:22px;width:420px">A private reading for {esc(r.name_full)}</div>
<div style="font-family:Rubik;font-size:15px;margin-top:6px">Born {r.dob_text}</div>
<div class="kick" style="margin-top:18px">Mulank {r.P} &#183; {PLANET[r.P]} edition</div>
<div class="abs" style="left:440px;top:930px;background:{T.WHITE};border-radius:22px;padding:20px 22px 24px;box-shadow:inset 0 -5px 0 rgba(31,42,20,.18),0 6px 0 rgba(31,42,20,.2)">
{cells}<div class="caps" style="font-size:10.5px;letter-spacing:.12em;margin-top:12px;text-align:center">Your Lo Shu grid</div></div>
<div class="abs" style="left:50px;top:1110px;font-family:Rubik;font-weight:500;font-size:15px;line-height:1.5;color:{T.INK};background:{T.WHITE};border-radius:12px;padding:10px 14px;box-shadow:inset 0 -4px 0 rgba(31,42,20,.16)">Psychic {r.P} &#183; Destiny {r.D}{extra}<br>{("Name " + str(r.NT) + " &#183; ") if r.NT else ""}Personal Year {r.PY}</div>
"""
        return T.CREAM, inner


LOOKS = {"Rosette": Look, "Daktilo": Daktilo, "Dabba": Dabba, "Broadcast": Broadcast, "Torn": Torn, "Contour": Contour}


def look_for(T):
    return LOOKS[T.look](T)
