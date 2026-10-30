"""Looks: how each theme draws its shapes, marks, plates, photo, page frame, footer and cover.

The pages (deck.py, deck_year.py) say *what* goes where (a feature shape behind a number, a decorative mark in
a corner, a pair of title plates, a band at the foot of the page). A look decides what that becomes:
Rosette draws flowers, clouds and sparkles; Daktilo draws matted prints and a manila folder; Dabba draws flat
square colour plates and giant lowercase words; Broadcast draws spines, tabs and shadowed capitals crossed by a
script phrase; Torn draws torn paper; Contour draws stacked contour-cut paper landscapes; Foxglove draws
double-keyline cream plates, gilt medallions and foxglove stalks on a pearly sky; Imperial draws flat stages, square
seals, purple seams and a caption strip on silk; Cobalt draws sharp paper plates with left seams and flat screenprint
leaves and suns.
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


# ════════════════════════════ Foxglove (Mulank 5) ════════════════════════════
def _svg_uri(svg):
    from urllib.parse import quote
    return "url(\"data:image/svg+xml," + quote(svg) + "\")"


def _sprig(h, pink, berry, leaf, rng, bells=6, ratio=.42):
    """A foxglove stalk h px tall, drawn flat in a box about h*ratio wide: stem, two leaves, bells down one side."""
    w = h * ratio
    sx = w * .38
    s = (f'<path d="M{sx:.1f} {h:.1f} C{sx + w * .08:.1f} {h * .6:.1f} {sx - w * .06:.1f} {h * .32:.1f} {sx + w * .1:.1f} {h * .04:.1f}" '
         f'fill="none" stroke="{leaf}" stroke-width="{max(1.4, h * .012):.1f}" stroke-linecap="round"/>')
    s += (f'<ellipse cx="{sx - w * .14:.1f}" cy="{h * .9:.1f}" rx="{w * .26:.1f}" ry="{h * .045:.1f}" fill="{leaf}" transform="rotate(-28 {sx - w * .14:.1f} {h * .9:.1f})"/>'
          f'<ellipse cx="{sx + w * .2:.1f}" cy="{h * .84:.1f}" rx="{w * .24:.1f}" ry="{h * .04:.1f}" fill="{leaf}" opacity=".85" transform="rotate(24 {sx + w * .2:.1f} {h * .84:.1f})"/>')
    for i in range(bells):
        t = i / max(1, bells - 1)
        cy = h * (.66 - .58 * t)
        bw, bh = w * (.36 - .16 * t), h * (.085 - .035 * t)
        cx = sx + w * .06 + bw * .55 + rng.uniform(-1.5, 1.5)
        rot = 18 + rng.uniform(-6, 6)
        s += (f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"><ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{bw / 2:.1f}" ry="{bh / 2:.1f}" fill="{pink}"/>'
              f'<ellipse cx="{cx + bw * .3:.1f}" cy="{cy:.1f}" rx="{bw * .14:.1f}" ry="{bh * .3:.1f}" fill="{berry}" opacity=".55"/></g>')
    s += f'<circle cx="{sx + w * .1:.1f}" cy="{h * .035:.1f}" r="{max(1.5, h * .014):.1f}" fill="{leaf}"/>'
    return s, w


class Foxglove(Look):
    plate_em = 0.50

    def _key(self, dark):
        return "rgba(235,216,162,.55)" if dark else self.T.KEY

    def ground_css(self, ground, dark, n):
        if dark:
            return f"background:radial-gradient(120% 55% at 50% -5%,rgba(255,255,255,.09),rgba(255,255,255,0) 62%),{ground}"
        return ("background:radial-gradient(130% 55% at 12% -6%,rgba(255,255,255,.7),rgba(255,255,255,0) 60%),"
                "radial-gradient(85% 42% at 104% 104%,rgba(235,216,162,.5),rgba(235,216,162,0) 70%),"
                f"radial-gradient(70% 38% at -4% 100%,rgba(222,152,180,.28),rgba(222,152,180,0) 70%),{ground}")

    def frame(self, ground, dark, n):
        k = self._key(dark)
        return (f'<svg class="frame" width="720" height="1280" viewBox="0 0 720 1280"><g fill="none" stroke="{k}">'
                f'<rect x="16" y="16" width="688" height="1248" rx="20" stroke-width="1.3"/>'
                f'<rect x="22" y="22" width="676" height="1236" rx="15" stroke-width=".7"/></g></svg>')

    def footer(self, name, n, dark):
        return f'<div class="foot fx"><span>Veshannastro</span><span>{esc(name)}</span><span>{n:02d}</span></div>'

    def extra_css(self):
        T = self.T
        rule = _svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" width="150" height="10" viewBox="0 0 150 10"><path d="M0 5H62M88 5H150" stroke="{T.GOLD}" stroke-width="1.2"/>'
                        f'<path d="M75 0.5L80 5 75 9.5 70 5Z" fill="{T.GOLD}"/><circle cx="66" cy="5" r="1.4" fill="{T.GOLD}"/><circle cx="84" cy="5" r="1.4" fill="{T.GOLD}"/></svg>')
        rule_d = _svg_uri('<svg xmlns="http://www.w3.org/2000/svg" width="150" height="10" viewBox="0 0 150 10"><path d="M0 5H62M88 5H150" stroke="#EBD8A2" stroke-width="1.2"/>'
                          '<path d="M75 0.5L80 5 75 9.5 70 5Z" fill="#EBD8A2"/><circle cx="66" cy="5" r="1.4" fill="#EBD8A2"/><circle cx="84" cy="5" r="1.4" fill="#EBD8A2"/></svg>')
        return f"""
.fx-cloud circle{{fill:#FFFFFF;opacity:.55}}.dark .fx-cloud circle{{opacity:.08}}
.num{{line-height:1.08}}
.foot.fx{{left:58px;right:58px;bottom:32px;font-family:Gentium;font-style:italic;font-weight:400;text-transform:none;letter-spacing:.03em;font-size:12.5px;opacity:.72}}
.kick{{background:{T.PINK};color:{T.BERRY_D};border-radius:0;font-weight:700;font-size:10.5px;letter-spacing:.2em;padding:6px 19px 5px;clip-path:polygon(0 0,100% 0,calc(100% - 9px) 50%,100% 100%,0 100%,9px 50%)}}
.kick.pk{{background:{T.ORANGE};color:{T.GOLD}}}.kick.wh{{background:{T.WHITE};color:{T.BERRY_D}}}
.accent{{width:150px;height:10px;border-radius:0;background:{rule} no-repeat left center}}
.dark .accent{{background:{rule_d} no-repeat left center}}
.caps{{letter-spacing:.18em}}
.plate{{background:{T.WHITE};color:{T.INK};border:1.2px solid {T.KEY};outline:.8px solid {T.KEY};outline-offset:-7px;border-radius:16px;padding:16px 32px 18px;box-shadow:0 14px 28px -22px rgba(47,58,42,.55)}}
.plate.sig{{background:transparent;border:0;outline:0;box-shadow:none;border-radius:0;padding:0 0 0 8px;font-style:italic;color:{T.BERRY_D}}}
.dark .plate.sig{{color:{T.ORANGE}}}.dark .onblob .plate.sig{{color:{T.BERRY_D}}}
.pnl,.tile{{border:1.2px solid rgba(119,147,99,.6);outline:.8px solid rgba(119,147,99,.42);outline-offset:-6px;border-radius:16px}}
.dark .pnl,.dark .tile{{border-color:rgba(235,216,162,.55);outline-color:rgba(235,216,162,.35)}}
ul.dots li:before{{border-radius:1px;width:8px;height:8px;transform:rotate(45deg);top:.6em}}
ul.dots li.neutral{{--dot:{T.KEY}}}ul.dots li.care{{--dot:#C98A3A}}
.ruled>div{{border-bottom:1px solid {T.RULE}}}.ruled>div:first-child{{border-top:1px solid {T.RULE}}}
table.t th{{background:{T.TH_BG};color:{T.TH_FG};font-family:Gentium;font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:11px}}
table.t td{{border-bottom:1px solid {T.RULE}}}table.t td:first-child{{color:{T.BERRY_D}}}
.bar{{background:{T.WHITE};border:1.2px solid {T.KEY};outline:.8px solid {T.KEY};outline-offset:-6px;border-radius:16px}}
.bar .go{{font-family:Gentium;font-style:italic;font-weight:700;text-transform:none;letter-spacing:.01em;font-size:15px;color:{T.CTA}}}
.bar .alt{{color:{T.COBALT}}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        T = self.T
        rng = _rng("fox", x, y, w, h)
        if kind == "bumps":
            # a bank of painted morning cloud along the foot of the page
            s = ""
            cx = x - 70
            while cx < x + w + 90:
                r = rng.uniform(34, 62)
                s += f'<circle cx="{cx:.0f}" cy="{1262 - r * .35:.0f}" r="{r:.0f}"/>'
                cx += r * 1.15
            return f'<svg class="abs fx-cloud" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">{s}</svg>'
        if kind in ("disc", "flower"):
            # an oval medallion with a gilt rim and an inner keyline
            cx, cy = x + w / 2, y + h / 2
            rx = min(w / 2 * .92, 692 - cx, cx - 28)
            ry = min(h / 2, cy - 30, 1236 - cy)
            return (f'<svg class="abs" style="left:0;top:0;overflow:visible" width="720" height="1280" viewBox="0 0 720 1280">'
                    f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{color}" stroke="{T.GOLD}" stroke-width="3"/>'
                    f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx - 9:.0f}" ry="{ry - 9:.0f}" fill="none" stroke="{T.GOLD}" stroke-width=".9" opacity=".7"/></svg>')
        # a painted cartouche: a soft plate with a double keyline
        return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color};border-radius:{min(48, h // 4)}px;'
                f'border:1.2px solid rgba(119,147,99,.7);outline:.8px solid rgba(119,147,99,.5);outline-offset:-8px;opacity:{opacity}"></div>')

    def _inline(self, svg, size):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:inline-block;vertical-align:top">{svg}</svg>'

    def _place(self, svg, w, h, x, y):
        x = min(x, 700 - w)
        return f'<svg class="abs" style="left:{x:.0f}px;top:{y:.0f}px;overflow:visible" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">{svg}</svg>'

    def _sprig_mark(self, size, x, y, seed):
        T = self.T
        h = size * 1.9 if x is not None else size
        svg, w = _sprig(h, "#DE98B4", T.BERRY_D, T.COBALT, _rng("sprig", seed, x, y), bells=6 if x is not None else 4)
        if x is None:
            return self._inline(f'<g transform="translate({(size - w) / 2:.1f} 0)">{svg}</g>', size)
        return self._place(svg, w, h, x, y - size * .4)

    def _star(self, size, x, y):
        c, r = size / 2, size / 2
        d = (f"M{c} {c - r} Q{c + r * .12} {c - r * .12} {c + r} {c} Q{c + r * .12} {c + r * .12} {c} {c + r} "
             f"Q{c - r * .12} {c + r * .12} {c - r} {c} Q{c - r * .12} {c - r * .12} {c} {c - r}Z")
        svg = f'<path d="{d}" fill="{self.T.GOLD}"/><circle cx="{c}" cy="{c}" r="{size * .06:.1f}" fill="#FBF8EF"/>'
        return self._inline(svg, size) if x is None else self._place(svg, size, size, x, y)

    def _medal(self, size, x, y):
        c = size / 2
        svg = (f'<ellipse cx="{c}" cy="{c}" rx="{size * .36:.1f}" ry="{size * .46:.1f}" fill="none" stroke="{self.T.GOLD}" stroke-width="{max(1.5, size * .05):.1f}"/>'
               f'<ellipse cx="{c}" cy="{c}" rx="{size * .25:.1f}" ry="{size * .34:.1f}" fill="#DE98B4" opacity=".75"/>')
        return self._inline(svg, size) if x is None else self._place(svg, size, size, x, y)

    def _bell(self, size, x, y):
        c = size / 2
        svg = (f'<path d="M{c} {size * .08} C{size * .22} {size * .12} {size * .16} {size * .55} {size * .1} {size * .86} '
               f'Q{c} {size * .98} {size * .9} {size * .86} C{size * .84} {size * .55} {size * .78} {size * .12} {c} {size * .08}Z" fill="#DE98B4"/>'
               f'<ellipse cx="{c}" cy="{size * .84:.1f}" rx="{size * .3:.1f}" ry="{size * .07:.1f}" fill="{self.T.BERRY_D}" opacity=".5"/>')
        return self._inline(svg, size) if x is None else self._place(svg, size, size, x, y)

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._sprig_mark(size, x, y, "a")

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._sprig_mark(size, x, y, "p")

    def sparkle(self, color, size, x=None, y=None):
        return self._star(size, x, y)

    def heart(self, color, size, x=None, y=None):
        return self._bell(size, x, y)

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._medal(size, x, y)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        # a tall foxglove along the right edge instead of a scalloped border
        svg, w = _sprig(560, "#DE98B4", self.T.BERRY_D, self.T.COBALT, _rng("scallop-fox"), bells=9)
        return f'<svg class="abs" style="left:{700 - w:.0f}px;top:690px;overflow:visible" width="{w:.0f}" height="560" viewBox="0 0 {w:.0f} 560">{svg}</svg>'

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        if rot > 0:   # the second line of a pair: the italic line that signs the title off
            s = self.fit(text, round(size * 1.08), width or 600)
            return f'<div class="plate sig" style="font-size:{s}px">{text}</div>'
        s = self.fit(text, size, width or 560)
        return f'<div class="plate" style="font-size:{s}px">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        ww = w - 140
        return (f'<div class="abs round" style="left:{x + 70}px;top:{y}px;width:{ww}px;height:{int(ww * 1.12)}px;border-radius:50%;overflow:hidden;'
                f'border:7px double {self.T.GOLD};box-shadow:0 18px 30px -20px rgba(47,58,42,.6)"><img src="{src}" style="width:100%;height:100%;object-fit:cover"></div>')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        cells = self.grid_cells(r.cnt, T.COBALT, "rgba(119,147,99,.6)", T.WHITE, size=46, radius=12, font="Rosarivo", empty_bg="rgba(251,248,239,.6)")
        extra = f" &#183; Master {r.M}" if r.M else (f" &#183; Karmic {r.K}" if r.K else "")
        rng = _rng("foxcover", r.P)
        left, lw = _sprig(600, "#DE98B4", T.BERRY_D, T.COBALT, rng, bells=11, ratio=.2)
        right, rw = _sprig(500, "#E7A9C1", T.BERRY_D, T.COBALT, rng, bells=9, ratio=.2)
        small, sw_ = _sprig(260, "#C9B6DE", T.BERRY_D, T.COBALT, rng, bells=7, ratio=.2)
        clouds = ""
        cx = -40
        while cx < 780:
            rr = rng.uniform(46, 80)
            clouds += f'<circle cx="{cx:.0f}" cy="{1215 - rr * .3:.0f}" r="{rr:.0f}" fill="#FFFFFF" opacity=".6"/>'
            cx += rr * 1.1
        inner = f"""
<div class="abs" style="left:0;top:0;width:720px;height:1280px;background:linear-gradient(180deg,#F2D9E4 0%,#E6DCEF 34%,#F3E6CB 72%,#E6EDD6 100%)"></div>
<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">{clouds}
<g transform="translate(30 640)">{left}</g><g transform="translate({690:.0f} 730) scale(-1 1)">{right}</g>
<g transform="translate(118 1000)">{small}</g></svg>
<div class="abs" style="left:118px;top:150px;width:484px;padding:40px 36px 36px;background:{T.WHITE};border:1.3px solid {T.KEY};outline:.8px solid {T.KEY};outline-offset:-8px;border-radius:24px;text-align:center;box-shadow:0 26px 50px -34px rgba(47,58,42,.7)">
<span class="kick">Personal Year &#183; {Y}</span>
<div class="disp" style="font-size:58px;line-height:1.02;color:{T.INK};margin-top:22px">Personal Year<br>Forecast</div>
<div class="accent" style="margin:20px auto 0"></div>
<div class="num" style="font-size:132px;line-height:1;color:{T.GOLD};margin-top:14px">{Y}</div>
<div class="it" style="font-size:22px;color:{T.BERRY_D};margin-top:16px;line-height:1.3">A private reading for<br>{esc(r.name_full)}</div>
<div class="small" style="margin-top:8px;color:{T.INK}">Born {r.dob_text}</div></div>
<div class="abs" style="left:236px;top:862px;padding:22px 26px 18px;background:rgba(251,248,239,.92);border:1.2px solid {T.KEY};outline:.8px solid {T.KEY};outline-offset:-6px;border-radius:18px;text-align:center">
{cells}<div class="caps" style="font-size:10px;margin-top:12px;color:{T.COBALT}">Your Lo Shu grid</div></div>
<div class="abs it" style="left:0;width:720px;top:1124px;text-align:center;font-size:17px;color:{T.INK}">Psychic {r.P} &#183; Destiny {r.D}{extra} &#183; {("Name " + str(r.NT) + " &#183; ") if r.NT else ""}Personal Year {r.PY}</div>
<div class="abs caps" style="left:0;width:720px;top:1166px;text-align:center;font-size:10.5px;color:{T.BERRY_D}">Designed for Mulank {r.P} &#183; {PLANET[r.P]}</div>
"""
        return T.LBLUE, inner


# ════════════════════════════ Imperial Cabinet (Mulank 3) ════════════════════════════
_SILK = ('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="132" viewBox="0 0 200 132"><g fill="none" stroke="#FFFFFF" stroke-opacity=".075" stroke-width="2" stroke-linecap="round">'
         '<path d="M18 74c0-16 13-26 27-26 12 0 21 8 21 19 0 9-7 15-15 15-7 0-12-5-12-11 0-5 4-8 8-8"/>'
         '<path d="M66 67c6-18 28-26 45-17 12 6 16 19 10 29"/><path d="M121 79c4 9 15 13 24 9 8-4 10-13 6-19-3-5-10-6-13-2"/>'
         '<path d="M2 90c20 6 44 6 66-2s50-8 72 0 44 8 58 2"/>'
         '<path d="M118 20c0-10 8-16 17-16 7 0 13 5 13 12 0 5-4 9-9 9-4 0-7-3-7-7"/><path d="M148 14c8-6 22-6 30 4"/>'
         '<path d="M22 124c8-9 22-10 31-2"/></g></svg>')


class Imperial(Look):
    plate_em = 0.70
    STRIP = 54

    def ground_css(self, ground, dark, n):
        if dark:
            return f"background-color:{ground};background-image:{_svg_uri(_SILK)};background-size:200px 132px"
        return f"background:{ground}"

    def frame(self, ground, dark, n):
        T = self.T
        strip = T.PINK if dark else T.NAVY
        return (f'<div class="frame"><div style="position:absolute;left:0;right:0;bottom:0;height:{self.STRIP}px;background:{strip}"></div>'
                f'<div style="position:absolute;left:50px;right:50px;top:34px;height:1px;background:{"rgba(253,191,104,.35)" if dark else "rgba(80,19,69,.28)"}"></div></div>')

    def footer(self, name, n, dark):
        c = self.T.NAVY if dark else self.T.GOLD
        return (f'<div class="foot im" style="color:{c}"><span>Obj. {n:02d} &#183; Veshannastro</span>'
                f'<span>{esc(name)} &#183; Personal Year Forecast</span></div>')

    def extra_css(self):
        T = self.T
        return f"""
.foot.im{{left:50px;right:50px;bottom:20px;opacity:1;font-family:Gantari;font-weight:600;font-size:10.5px;letter-spacing:.16em}}
.kick{{background:transparent;color:{T.NAVY};border-radius:0;padding:0 0 6px;border-bottom:2.5px solid {T.NAVY};font-weight:600;font-size:11.5px;letter-spacing:.22em}}
.kick.pk,.kick.wh{{background:transparent;color:{T.NAVY}}}
.dark .kick,.dark .kick.pk,.dark .kick.wh{{color:{T.GOLD};border-color:{T.GOLD}}}
.accent{{width:96px;height:2.5px;border-radius:0;background:{T.NAVY}}}.dark .accent{{background:{T.GOLD}}}
.caps{{letter-spacing:.2em}}
.plate{{background:{T.NAVY};color:{T.GOLD};letter-spacing:.06em;padding:14px 26px 10px;box-shadow:none}}
.plate.sig{{background:transparent;color:{T.NAVY};font-family:Castoro;font-style:italic;letter-spacing:0;padding:0 0 0 4px}}
.dark .plate{{background:{T.GOLD};color:{T.NAVY}}}.dark .plate.sig{{background:transparent;color:{T.GOLD}}}.dark .onblob .plate.sig{{color:{T.NAVY}}}
.pnl,.tile{{border-top:3px solid {T.NAVY};box-shadow:inset 0 0 0 1px rgba(80,19,69,.16)}}
.dark .pnl,.dark .tile{{border-top-color:{T.GOLD}}}
ul.dots li:before{{border-radius:0;width:7px;height:7px;transform:rotate(45deg);top:.62em}}
ul.dots li.neutral{{--dot:{T.RULE}}}ul.dots li.care{{--dot:#C98A2E}}
.ruled>div{{border-bottom:2.5px solid {T.NAVY}}}.ruled>div:first-child{{border-top:2.5px solid {T.NAVY}}}
.dark .ruled>div{{border-color:rgba(253,191,104,.6)}}
table.t th{{background:{T.NAVY};color:{T.GOLD};font-weight:600;letter-spacing:.14em;text-transform:uppercase;font-size:11px}}
table.t td{{border-bottom:2px solid rgba(80,19,69,.3)}}
.bar{{background:{T.NAVY};color:{T.CREAM};border-radius:0}}.bar .go{{color:{T.GOLD}}}.bar .alt{{color:{T.CREAM}}}
.dark .bar{{background:{T.GOLD};color:{T.NAVY}}}.dark .bar .go,.dark .bar .alt{{color:{T.NAVY}}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        T = self.T
        if kind == "bumps":
            return ""   # the caption strip already holds the foot of every page
        if kind in ("disc", "flower"):
            # a square seal on its own stage, with an inner frame
            s = int(min(w, h) * .9)
            sx, sy = int(x + (w - s) / 2), int(y + (h - s) / 2)
            return (f'<div class="abs" style="left:{sx}px;top:{sy}px;width:{s}px;height:{s}px;background:{color};border:3px solid {T.NAVY};'
                    f'outline:1px solid {T.NAVY};outline-offset:-11px"></div>')
        h = min(h, 1280 - self.STRIP - 6 - y)
        if h < 40:
            return ""
        return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color};'
                f'box-shadow:inset 0 0 0 1px rgba(80,19,69,.22);outline:1px solid rgba(80,19,69,.3);outline-offset:-12px;opacity:{opacity}"></div>'
                + self._lozenge(26, x + w - 46, y + h - 46))

    def _lozenge(self, size, x, y, color=None):
        T = self.T
        c = size / 2
        k = size * .42
        svg = (f'<path d="M{c} {c - k} L{c + k} {c} L{c} {c + k} L{c - k} {c}Z" fill="{color or T.ORANGE}" stroke="{T.NAVY}" stroke-width="{max(1.2, size * .03):.1f}"/>'
               f'<path d="M{c} {c - k * .55} L{c + k * .55} {c} L{c} {c + k * .55} L{c - k * .55} {c}Z" fill="none" stroke="{T.NAVY}" stroke-width="{max(.8, size * .018):.1f}"/>')
        if x is None:
            return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:inline-block;vertical-align:top">{svg}</svg>'
        return f'<svg class="abs" style="left:{min(x, 680 - size)}px;top:{y}px" width="{size}" height="{size}" viewBox="0 0 {size} {size}">{svg}</svg>'

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._lozenge(size * .8, x, y)

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._lozenge(size * .8, x, y, self.T.PINK)

    def sparkle(self, color, size, x=None, y=None):
        return self._lozenge(size * .7, x, y, self.T.GOLD)

    def heart(self, color, size, x=None, y=None):
        return self._lozenge(size * .7, x, y, self.T.PINK)

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._lozenge(size * .7, x, y, self.T.LBLUE)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        # a narrow lavender stage down the right edge, like the side of a display case
        T = self.T
        return f'<div class="abs" style="right:0;top:0;width:34px;height:{1280 - self.STRIP}px;background:{T.PINK};box-shadow:inset 1px 0 0 rgba(80,19,69,.3)"></div>'

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        if rot > 0:
            s = self.fit(text, round(size * 1.05), width or 600)
            return f'<div class="plate sig" style="font-size:{s}px">{text}</div>'
        s = self.fit(text, round(size * .86), width or 600)
        return f'<div class="plate" style="font-size:{s}px">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        T = self.T
        ww = w - 80
        return (f'<div class="abs" style="left:{x + 40}px;top:{y}px;width:{ww}px;height:{ww}px;background:{T.PINK};padding:34px">'
                f'<img src="{src}" style="width:100%;height:100%;object-fit:cover;display:block"></div>'
                f'<div class="abs caps" style="left:{x + 40}px;top:{y + ww}px;width:{ww}px;background:{T.NAVY};color:{T.GOLD};font-size:10.5px;padding:9px 14px">'
                f'Obj. &#183; the bracelet for your number</div>')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        cells = self.grid_cells(r.cnt, T.NAVY, "rgba(80,19,69,.45)", T.GOLD, size=52, radius=0, font="CastoroTitling")
        roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX"}[r.P]
        rows = [("Psychic number", r.P), ("Destiny number", r.D)] + ([("Name number", r.NT)] if r.NT else []) + \
               ([("Master number", r.M)] if r.M else ([("Karmic number", r.K)] if r.K else [])) + [(f"Personal year {Y}", r.PY)]
        ledger = "".join(f'<div style="display:flex;justify-content:space-between;align-items:baseline;padding:10px 0;border-bottom:2px solid rgba(253,191,104,.55)">'
                         f'<span class="caps" style="font-size:10.5px;color:#F3E8D2">{a}</span><span class="num" style="font-size:30px;color:{T.GOLD}">{b}</span></div>' for a, b in rows)
        inner = f"""
<div class="abs caps" style="left:50px;top:58px;font-size:11px;color:{T.GOLD}">Veshannastro &#183; Vedic numerology</div>
<div class="abs" style="left:598px;top:112px;width:72px;height:430px;border:2px solid {T.GOLD};outline:1px solid {T.GOLD};outline-offset:-7px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px">
<div class="num" style="font-size:40px;color:{T.GOLD}">{roman}</div>
<div class="caps" style="writing-mode:vertical-rl;font-size:12px;letter-spacing:.42em;color:{T.GOLD}">Mulank {r.P}</div></div>
<div class="abs" style="left:50px;top:200px;width:520px">
<div class="disp" style="font-size:62px;line-height:1.04;color:{T.GOLD}">Personal year<br>forecast</div>
<div class="num" style="font-size:176px;line-height:.95;color:{T.GOLD};margin-top:20px">{Y}</div>
<div class="accent" style="margin-top:24px"></div>
<div class="it" style="font-size:26px;line-height:1.3;color:#F3E8D2;margin-top:22px">A private reading for {esc(r.name_full)}</div>
<div class="body" style="color:#E6DDE2;margin-top:6px">Born {r.dob_text}</div></div>
<div class="abs" style="left:50px;top:820px;width:290px;background:{T.ORANGE};padding:26px 0 0;display:flex;flex-direction:column;align-items:center">
{cells}<div class="caps" style="align-self:stretch;margin-top:24px;background:{T.NAVY};color:{T.GOLD};font-size:10px;padding:8px 14px;box-shadow:inset 0 0 0 1px rgba(253,191,104,.35)">Obj. 00 &#183; your Lo Shu grid</div></div>
<div class="abs" style="left:384px;top:820px;width:286px;border-top:2px solid rgba(253,191,104,.55)">{ledger}</div>
<div class="abs caps" style="left:50px;bottom:20px;font-size:10.5px;color:{T.NAVY}">Designed for Mulank {r.P} &#183; {PLANET[r.P]} &#183; {Y}</div>
"""
        return T.NAVY, inner


# ════════════════════════════ Cobalt & Cream (Mulank 9) ════════════════════════════
def _leaf(cx, cy, length, width, angle, fill, line):
    """A flat screenprint leaf with a thin dark outline and a centre vein."""
    return (f'<g transform="rotate({angle:.1f} {cx:.1f} {cy:.1f})"><path d="M{cx:.1f} {cy - length / 2:.1f} '
            f'Q{cx + width:.1f} {cy:.1f} {cx:.1f} {cy + length / 2:.1f} Q{cx - width:.1f} {cy:.1f} {cx:.1f} {cy - length / 2:.1f}Z" '
            f'fill="{fill}" stroke="{line}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M{cx:.1f} {cy - length / 2 + 6:.1f} L{cx:.1f} {cy + length / 2 - 4:.1f}" stroke="{line}" stroke-width="1.1" opacity=".8"/></g>')


class Cobalt(Look):
    plate_em = 0.52

    def frame(self, ground, dark, n):
        c = self.T.ORANGE if dark else self.T.COBALT
        return f'<div class="frame"><div style="position:absolute;left:0;top:0;width:6px;height:1280px;background:{c}"></div></div>'

    def footer(self, name, n, dark):
        line = "rgba(249,245,234,.35)" if dark else self.T.RULE
        return (f'<div class="abs" style="left:50px;right:50px;bottom:54px;height:1px;background:{line};z-index:40"></div>'
                f'<div class="foot cb"><span>Veshannastro</span><span>{esc(name)}</span><span>{n:02d}</span></div>')

    def extra_css(self):
        T = self.T
        return f"""
.foot.cb{{left:50px;right:50px;bottom:28px;opacity:.75;font-weight:600;font-size:10.5px;letter-spacing:.16em}}
.kick{{background:transparent;color:{T.COBALT};border-radius:0;padding:0;font-family:Jaini;font-weight:400;font-size:18px;letter-spacing:.06em}}
.kick.pk{{background:transparent;color:{T.BERRY}}}.kick.wh{{background:transparent;color:{T.COBALT}}}
.dark .kick,.dark .kick.pk,.dark .kick.wh{{color:{T.ORANGE}}}
.accent{{width:64px;height:2px;border-radius:0;background:{T.COBALT}}}.dark .accent{{background:{T.ORANGE}}}
.plate{{background:{T.PAPER};color:{T.COBALT};border-left:5px solid {T.COBALT};padding:12px 24px 12px;box-shadow:none}}
.plate.sig{{background:transparent;border:0;padding:0 0 0 6px;font-style:italic;color:{T.COBALT}}}
.dark .plate{{background:{T.CREAM};color:{T.NAVY};border-left-color:{T.ORANGE}}}.dark .plate.sig{{background:transparent;color:{T.ORANGE}}}.dark .onblob .plate.sig{{color:{T.NAVY}}}
.pnl,.tile{{border-left:4px solid {T.COBALT};box-shadow:inset 0 0 0 1px rgba(42,36,32,.07)}}
.dark .pnl,.dark .tile{{border-left-color:{T.ORANGE}}}
ul.dots li:before{{border-radius:0;width:8px;height:8px;top:.55em}}
ul.dots li.neutral{{--dot:#7E93B5}}
.ruled>div{{border-bottom:1px solid {T.RULE}}}.ruled>div:first-child{{border-top:1px solid {T.RULE}}}
.dark .ruled>div{{border-color:rgba(249,245,234,.28)}}
table.t{{font-variant-numeric:tabular-nums lining-nums}}
table.t th{{background:{T.COBALT};color:{T.CREAM};text-transform:uppercase;letter-spacing:.1em;font-size:11px;font-weight:600}}
table.t td{{border-bottom:1px solid {T.RULE}}}table.t td:first-child{{color:{T.COBALT}}}
.num{{font-variant-numeric:lining-nums tabular-nums}}
.bar{{background:{T.COBALT};color:{T.CREAM};border-radius:0}}.bar .go{{color:{T.ORANGE}}}.bar .alt{{color:{T.CREAM}}}
.dark .bar{{background:{T.CREAM};color:{T.INK}}}.dark .bar .go{{color:{T.COBALT}}}.dark .bar .alt{{color:{T.NAVY}}}
"""

    def blob(self, color, w, h, x, y, kind="cloud", rot=0, opacity=1):
        T = self.T
        L = T.LINE
        rng = _rng("cob", x, y, w, h)
        if kind == "bumps":
            cols = [T.GREEN, T.COBALT, T.ORANGE, T.GREEN, T.BERRY]
            s = ""
            n = 6
            for i in range(n):
                cx = x - 40 + (w + 80) * i / (n - 1)
                s += _leaf(cx, 1250, rng.uniform(110, 150), rng.uniform(26, 34), rng.uniform(-38, 38), cols[i % len(cols)], L)
            return f'<svg class="abs" style="left:0;top:0" width="720" height="1280" viewBox="0 0 720 1280">{s}</svg>'
        if kind in ("disc", "flower"):
            cx, cy = x + w / 2, y + h / 2
            R = min(min(w, h) / 2, 704 - cx, cx - 16, cy - 24)
            rays = ""
            if kind == "flower":
                for k in range(12):
                    a = 360 * k / 12
                    rays += (f'<rect x="{cx - 5:.1f}" y="{cy - R - 2:.1f}" width="10" height="{R * .2:.1f}" fill="{T.ORANGE}" stroke="{L}" stroke-width="1.4" '
                             f'transform="rotate({a:.0f} {cx:.1f} {cy:.1f})"/>')
                R *= .82
            return (f'<svg class="abs" style="left:0;top:0;overflow:visible" width="720" height="1280" viewBox="0 0 720 1280">{rays}'
                    f'<circle cx="{cx + 7:.1f}" cy="{cy + 7:.1f}" r="{R:.1f}" fill="none" stroke="{T.ORANGE}" stroke-width="2.4"/>'
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="{color}" stroke="{L}" stroke-width="2"/></svg>')
        # a flat printed block with thin linework, slightly off register
        return (f'<div class="abs" style="left:{x + 8}px;top:{y + 8}px;width:{w}px;height:{h}px;border:2px solid {T.ORANGE}"></div>'
                f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color};border:1.6px solid {L};opacity:{opacity}"></div>')

    def _place(self, svg, size, x, y):
        if x is None:
            return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:inline-block;vertical-align:top">{svg}</svg>'
        return f'<svg class="abs" style="left:{min(x, 690 - size)}px;top:{y}px;overflow:visible" width="{size}" height="{size}" viewBox="0 0 {size} {size}">{svg}</svg>'

    def _sprig(self, size, x, y):
        T = self.T
        c = size / 2
        svg = (f'<path d="M{c} {size * .95} Q{c - 2} {c} {c + 2} {size * .08}" stroke="{T.LINE}" stroke-width="1.6" fill="none"/>'
               + _leaf(c - size * .17, size * .52, size * .42, size * .13, -40, T.GREEN, T.LINE)
               + _leaf(c + size * .17, size * .36, size * .4, size * .12, 40, T.COBALT, T.LINE)
               + _leaf(c, size * .14, size * .26, size * .09, 0, T.ORANGE, T.LINE))
        return self._place(svg, size, x, y)

    def _sun(self, size, x, y, fill=None):
        T = self.T
        c = size / 2
        rays = "".join(f'<rect x="{c - size * .035:.1f}" y="{size * .02:.1f}" width="{size * .07:.1f}" height="{size * .16:.1f}" fill="{T.ORANGE}" stroke="{T.LINE}" stroke-width="1.1" '
                       f'transform="rotate({360 * k / 8:.0f} {c} {c})"/>' for k in range(8))
        svg = rays + f'<circle cx="{c}" cy="{c}" r="{size * .27:.1f}" fill="{fill or T.ORANGE}" stroke="{T.LINE}" stroke-width="1.4"/>'
        return self._place(svg, size, x, y)

    def _dot(self, size, x, y, fill):
        c = size / 2
        svg = (f'<circle cx="{c + 3}" cy="{c + 3}" r="{size * .32:.1f}" fill="none" stroke="{self.T.ORANGE}" stroke-width="1.6"/>'
               f'<circle cx="{c}" cy="{c}" r="{size * .32:.1f}" fill="{fill}" stroke="{self.T.LINE}" stroke-width="1.4"/>')
        return self._place(svg, size, x, y)

    def asterisk(self, color, size, x=None, y=None, rot=0, spokes=8, sw=None):
        return self._sprig(size, x, y)

    def petal_flower(self, color, size, x=None, y=None, petals=8, hole=None):
        return self._sprig(size, x, y)

    def sparkle(self, color, size, x=None, y=None):
        return self._sun(size, x, y)

    def heart(self, color, size, x=None, y=None):
        return self._dot(size, x, y, self.T.BERRY)

    def ring(self, color, size, x=None, y=None, inner=None):
        return self._dot(size, x, y, self.T.COBALT)

    def scallop(self, color, side="right", width=52, count=12, height=1280):
        T = self.T
        rng = _rng("cobscal")
        s = "".join(_leaf(706, 120 + i * 150 + rng.uniform(-14, 14), 120, 28, rng.uniform(-20, 20) + (30 if i % 2 else -30),
                          [T.GREEN, T.COBALT, T.ORANGE, T.BERRY][i % 4], T.LINE) for i in range(8))
        return f'<svg class="abs" style="left:0;top:0;overflow:visible" width="720" height="1280" viewBox="0 0 720 1280">{s}</svg>'

    def plate(self, text, size, rot, color, bg="#FFFFFF", width=None):
        if rot > 0:
            s = self.fit(text, round(size * 1.06), width or 600)
            return f'<div class="plate sig" style="font-size:{s}px">{text}</div>'
        s = self.fit(text, size, width or 580)
        return f'<div class="plate" style="font-size:{s}px">{text}</div>'

    def product(self, sku, w, h, x, y):
        src = self._sq_photo(sku)
        if not src:
            return None
        T = self.T
        ww = w - 100
        return (f'<div class="abs" style="left:{x + 50}px;top:{y}px;width:{ww}px;background:{T.PAPER};border-left:5px solid {T.COBALT};padding:18px 18px 14px">'
                f'<img src="{src}" style="width:100%;height:{ww - 36}px;object-fit:cover;display:block">'
                f'<div class="kick" style="margin-top:12px;font-size:16px">The bracelet for your number</div></div>')

    def cover(self, deck):
        r, T, Y = deck.r, self.T, deck.Y
        L = T.LINE
        cells = self.grid_cells(r.cnt, T.COBALT, "rgba(31,78,140,.45)", T.CREAM, size=46, radius=0, font="Tiro")
        rng = _rng("cobcover", r.P)
        art = (f'<circle cx="566" cy="232" r="118" fill="{T.ORANGE}" stroke="{L}" stroke-width="2"/>'
               f'<circle cx="574" cy="240" r="118" fill="none" stroke="{T.CREAM}" stroke-width="1.6" opacity=".55"/>'
               f'<circle cx="470" cy="380" r="54" fill="{T.PINK}" stroke="{L}" stroke-width="2"/>'
               + _leaf(640, 420, 210, 46, 28, T.GREEN, L) + _leaf(520, 470, 180, 40, -36, "#2E8A62", L)
               + _leaf(690, 300, 160, 34, 62, T.BERRY, L) + _leaf(430, 250, 120, 28, -64, T.GREEN, L)
               + f'<path d="M380 520 Q520 440 700 520" fill="none" stroke="{T.CREAM}" stroke-width="2" opacity=".6"/>')
        stats = [("Psychic", r.P), ("Destiny", r.D)] + ([("Name", r.NT)] if r.NT else []) + [(f"Year {Y}", r.PY)]
        seams = [T.COBALT, T.GREEN, T.BERRY, T.ORANGE]
        plates = "".join(f'<div style="flex:1;background:{T.PAPER};border-left:4px solid {seams[i % 4]};padding:12px 14px 10px">'
                         f'<div class="num" style="font-size:44px;color:{T.COBALT}">{v}</div>'
                         f'<div class="caps" style="font-size:10px;margin-top:8px;padding-top:6px;border-top:1px solid {T.RULE};color:{T.INK}">{k}</div></div>'
                         for i, (k, v) in enumerate(stats))
        extra = f"Master number {r.M}. " if r.M else (f"Karmic number {r.K}. " if r.K else "")
        inner = f"""
<div class="abs" style="left:0;top:0;width:720px;height:600px;background:{T.COBALT}"></div>
<svg class="abs" style="left:0;top:0" width="720" height="600" viewBox="0 0 720 600">{art}</svg>
<div class="abs" style="left:50px;top:70px;width:380px">
<div class="kick" style="color:{T.ORANGE}">Mulank {r.P} &#183; {PLANET[r.P]} edition</div>
<div class="disp" style="font-size:66px;line-height:1.0;color:{T.CREAM};margin-top:22px">Personal<br>Year<br>Forecast</div>
<div style="width:64px;height:2px;background:{T.ORANGE};margin-top:26px"></div>
<div class="body" style="color:#E3EAF5;margin-top:18px;width:300px">A private reading for {esc(r.name_full)}, born {r.dob_text}.</div></div>
<div class="abs num" style="left:44px;top:600px;font-size:210px;line-height:1;color:{T.COBALT}">{Y}</div>
<div class="abs" style="left:50px;top:850px;width:620px;display:flex;gap:10px">{plates}</div>
<div class="abs" style="left:50px;top:1000px;width:330px">
<div class="kick">The numbers behind this file</div>
<div class="small" style="margin-top:8px;color:{T.INK}">{extra}Every figure in this forecast comes from that date of birth and that name.</div>
<div class="caps" style="font-size:10px;margin-top:16px;color:{T.COBALT}">Designed for Mulank {r.P} &#183; {PLANET[r.P]}</div></div>
<div class="abs" style="left:430px;top:986px;background:{T.PAPER};border-left:4px solid {T.COBALT};padding:18px 20px 14px">
{cells}<div class="caps" style="font-size:10px;margin-top:10px;color:{T.COBALT}">Your Lo Shu grid</div></div>
"""
        return T.CREAM, inner


LOOKS = {"Rosette": Look, "Daktilo": Daktilo, "Dabba": Dabba, "Broadcast": Broadcast, "Torn": Torn, "Contour": Contour,
         "Foxglove": Foxglove, "Imperial": Imperial, "Cobalt": Cobalt}


def look_for(T):
    return LOOKS[T.look](T)
