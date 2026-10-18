"""Page kit for the forecast deck: theme CSS, flat marks and shapes, plates, action bars, the slide wrapper.

Pages are 720 x 1280 px (9:16). Grounds rotate through the theme's colours; display words use the theme's
display face, reading copy its reading face. Every mark and shape is a flat vector drawn here.
"""
import html
import math
import os
from types import SimpleNamespace
from urllib.parse import quote

from .themes import ASSETS

WA_NUMBER = "917646952745"


def esc(s):
    return html.escape(str(s), quote=False)


def asset(*p):
    return "file://" + os.path.join(ASSETS, *p)


def theme_ns(theme):
    return SimpleNamespace(**{k: v for k, v in theme.items()})


def _faces(fam):
    return [f'@font-face{{font-family:{fam["family"]};src:url({asset("fonts", f)});font-weight:{w};font-style:{s}}}'
            for f, w, s in fam["files"]]


def css(T, extra=""):
    Y = T.type
    faces = _faces(T.display) + _faces(T.body)
    for fam in T.extra_fonts:
        faces += _faces(fam)
    # arrows, thin spaces and ticks that a theme's faces lack come from Savate, which has them
    faces.append(f'@font-face{{font-family:VAFallback;src:url({asset("fonts", "Savate-450.ttf")});unicode-range:U+2009,U+2190-2199,U+2713}}')
    D, B = T.display["family"], T.body["family"]
    IT = Y["it_family"] or D
    CAPS = Y["caps_family"] or B
    s = Y["scale"]
    sizes = "".join(f".t{i}{{font-size:{round(px * s)}px}}" for i, px in enumerate([84, 60, 46, 34, 25, 19], 1))
    return "\n".join(faces) + f"""
@page{{size:720px 1280px;margin:0}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{font-family:{B},VAFallback,sans-serif;color:{T.INK};-webkit-print-color-adjust:exact;print-color-adjust:exact;font-synthesis:none}}
a{{color:inherit;text-decoration:none}}
p{{margin:0 0 12px}}
.slide{{width:720px;height:1280px;position:relative;overflow:hidden;break-after:page;page-break-after:always;padding:58px 50px 78px;isolation:isolate}}
.dark{{color:#fff}}
.slide:after{{content:"";position:absolute;inset:0;background:url({asset(T.grain)}) repeat;background-size:{T.grain_size}px {T.grain_size}px;pointer-events:none;z-index:50}}
.disp{{font-family:{D},VAFallback;font-weight:{Y["disp_w"]};line-height:{Y["lh"]};letter-spacing:{Y["track"]};text-transform:{Y["case"]};margin:0}}
.disp.b{{font-weight:{Y["disp_bw"]}}}
{sizes}
.kick{{display:inline-block;font:600 11.5px {CAPS},VAFallback;letter-spacing:.14em;text-transform:uppercase;background:{T.LBLUE};color:{T.NAVY};padding:5px 10px 4px;border-radius:5px}}
.kick.pk{{background:{T.PINK};color:{T.BERRY_D}}}.kick.wh{{background:#fff;color:{T.NAVY}}}
.caps{{font-family:{CAPS},VAFallback;font-weight:{Y["caps_w"]};font-size:13px;letter-spacing:.16em;text-transform:uppercase}}
.lead{{font-size:17.5px;line-height:1.55}}
.body{{font-size:15.2px;line-height:1.56}}
.small{{font-size:13.8px;line-height:1.52}}
.tiny{{font-size:11.2px;line-height:1.45}}
.it{{font-family:{IT},VAFallback;font-style:{Y["it_style"]};font-weight:{Y["it_w"]}}}
.plate{{display:inline-block;position:relative;z-index:2;background:#fff;color:{T.NAVY};font-family:{D},VAFallback;font-weight:{Y["plate_w"]};line-height:1;padding:14px 30px 20px;box-shadow:0 1px 0 rgba(0,0,0,.04)}}
.rule{{height:1.5px;background:{T.RULE};border:0;margin:0}}
.rule.wh{{background:rgba(255,255,255,.55)}}
.accent{{width:76px;height:6px;border-radius:3px;background:{T.LBLUE}}}
.abs{{position:absolute}}
.tile{{border-radius:14px;padding:22px 24px}}
.pnl{{border-radius:14px}}
.foot{{position:absolute;left:50px;right:50px;bottom:28px;display:flex;justify-content:space-between;font-family:{CAPS},VAFallback;font-weight:600;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;opacity:.55;z-index:40}}
ul.dots{{list-style:none;margin:0;padding:0}}
ul.dots li{{position:relative;padding-left:20px;margin:0 0 7px}}
ul.dots li:before{{content:"";position:absolute;left:2px;top:.55em;width:9px;height:9px;border-radius:50%;background:var(--dot,{T.PINK})}}
ul.dots li.good{{--dot:{T.GREEN}}}ul.dots li.care{{--dot:{T.ORANGE}}}ul.dots li.mixed{{--dot:{T.BERRY}}}ul.dots li.neutral{{--dot:{T.LBLUE}}}ul.dots li.trait{{--dot:{T.COBALT}}}
.ruled>div{{padding:12px 0;border-bottom:1.5px solid {T.RULE}}}
.ruled>div:first-child{{border-top:1.5px solid {T.RULE}}}
.bar{{display:flex;align-items:center;justify-content:space-between;gap:14px;background:#fff;border-radius:12px;padding:14px 18px;color:{T.INK}}}
.bar .go{{font-family:{CAPS},VAFallback;font-weight:700;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:{T.CTA};white-space:nowrap}}
.bar .what{{font-size:13.2px;line-height:1.35}}
.bar .alt{{font-size:12px;color:{T.NAVY};text-decoration:underline;text-underline-offset:3px;white-space:nowrap}}
table.t{{width:100%;border-collapse:collapse;font-size:13.6px;line-height:1.42}}
table.t th{{background:{T.TH_BG};color:{T.TH_FG};text-align:left;font-family:{CAPS},VAFallback;font-weight:700;font-size:12px;padding:8px 11px;letter-spacing:.02em}}
table.t td{{padding:8px 11px;border-bottom:1.5px solid {T.RULE};vertical-align:top}}
table.t td:first-child{{font-weight:700;color:{T.DEEP}}}
.num{{font-family:{D},VAFallback;font-weight:{Y["num_w"]};line-height:.9}}
.frame{{position:absolute;inset:0;z-index:-1;pointer-events:none}}
{".slide *:not(.round){border-radius:0 !important}" if T.square else ""}
""" + extra


# ── shapes ──
def _flower_circles(n=8, R=0.31, r=0.19):
    out = [f'<circle cx="0.5" cy="0.5" r="{R + 0.02}"/>']
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        out.append(f'<circle cx="{0.5 + R * math.cos(a):.4f}" cy="{0.5 + R * math.sin(a):.4f}" r="{r}"/>')
    return "".join(out)


def _cloud_circles():
    return ('<circle cx="0.27" cy="0.42" r="0.24"/><circle cx="0.53" cy="0.30" r="0.29"/>'
            '<circle cx="0.78" cy="0.45" r="0.22"/><circle cx="0.16" cy="0.68" r="0.16"/>'
            '<circle cx="0.86" cy="0.70" r="0.14"/><rect x="0.14" y="0.45" width="0.72" height="0.4"/>'
            '<circle cx="0.5" cy="0.72" r="0.2"/>')


def _pos(x, y):
    return f"position:absolute;left:{x}px;top:{y}px;" if x is not None else ""


def asterisk(color, size, x=None, y=None, rot=0, spokes=8, sw=None):
    sw = sw or size * 0.16
    c = size / 2
    lines = []
    for i in range(spokes // 2):
        a = math.pi * i / (spokes // 2)
        dx, dy = (c - sw / 2) * math.cos(a), (c - sw / 2) * math.sin(a)
        lines.append(f'<line x1="{c - dx:.1f}" y1="{c - dy:.1f}" x2="{c + dx:.1f}" y2="{c + dy:.1f}"/>')
    cls = ' class="abs"' if x is not None else ""
    return (f'<svg{cls} style="{_pos(x, y)}transform:rotate({rot}deg)" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<g stroke="{color}" stroke-width="{sw:.1f}" stroke-linecap="round">{"".join(lines)}</g></svg>')


def petal_flower(color, size, x=None, y=None, petals=8, hole=None):
    c = size / 2
    pr = size * 0.17
    R = size * 0.30
    parts = []
    for i in range(petals):
        a = 2 * math.pi * i / petals
        parts.append(f'<ellipse cx="{c + R * math.cos(a):.1f}" cy="{c + R * math.sin(a):.1f}" rx="{pr * 1.25:.1f}" ry="{pr * .8:.1f}" '
                     f'transform="rotate({math.degrees(a):.0f} {c + R * math.cos(a):.1f} {c + R * math.sin(a):.1f})"/>')
    parts.append(f'<circle cx="{c}" cy="{c}" r="{size * .22:.1f}"/>')
    hole_svg = f'<circle cx="{c}" cy="{c}" r="{size * .09:.1f}" fill="{hole}"/>' if hole else ""
    cls = ' class="abs"' if x is not None else ""
    return (f'<svg{cls} style="{_pos(x, y)}" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<g fill="{color}">{"".join(parts)}</g>{hole_svg}</svg>')


def sparkle(color, size, x=None, y=None):
    s = size
    c = s / 2
    k = s * 0.12
    d = (f"M{c},0 C{c + k},{c - k} {c + k},{c - k} {s},{c} C{c + k},{c + k} {c + k},{c + k} {c},{s} "
         f"C{c - k},{c + k} {c - k},{c + k} 0,{c} C{c - k},{c - k} {c - k},{c - k} {c},0Z")
    cls = ' class="abs"' if x is not None else ""
    return f'<svg{cls} style="{_pos(x, y)}" width="{s}" height="{s}" viewBox="0 0 {s} {s}"><path d="{d}" fill="{color}"/></svg>'


def heart(color, size, x=None, y=None):
    cls = ' class="abs"' if x is not None else ""
    return (f'<svg{cls} style="{_pos(x, y)}" width="{size}" height="{size}" viewBox="0 0 100 100"><path fill="{color}" '
            f'd="M50 88 C20 66 4 50 4 31 C4 16 16 6 29 6 C39 6 46 12 50 20 C54 12 61 6 71 6 C84 6 96 16 96 31 C96 50 80 66 50 88Z"/></svg>')


def ring(color, size, x=None, y=None, inner=None):
    cls = ' class="abs"' if x is not None else ""
    inner_c = f'<circle cx="50" cy="50" r="22" fill="{inner}"/>' if inner else ""
    return (f'<svg{cls} style="{_pos(x, y)}" width="{size}" height="{size}" viewBox="0 0 100 100">'
            f'<circle cx="50" cy="50" r="40" fill="none" stroke="{color}" stroke-width="13"/>{inner_c}</svg>')


def blob(color, w, h, x, y, kind="cloud", rot=0, opacity=1):
    if kind == "cloud":
        inner = _cloud_circles().replace("<circle", f'<circle fill="{color}"').replace("<rect", f'<rect fill="{color}"')
        return (f'<svg class="abs" style="left:{x}px;top:{y}px;opacity:{opacity};transform:rotate({rot}deg)" width="{w}" height="{h}" '
                f'viewBox="0 0 1 1" preserveAspectRatio="none">{inner}</svg>')
    if kind == "flower":
        inner = _flower_circles().replace("<circle", f'<circle fill="{color}"')
        return (f'<svg class="abs" style="left:{x}px;top:{y}px;opacity:{opacity};transform:rotate({rot}deg)" width="{w}" height="{h}" '
                f'viewBox="0 0 1 1">{inner}</svg>')
    if kind == "disc":
        return f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color};border-radius:50%;opacity:{opacity}"></div>'
    if kind == "bumps":
        n = 4
        r = w / (n * 2) * 1.25
        parts = []
        for i in range(n):
            cx = r + i * (w - 2 * r) / (n - 1)
            parts.append(f'<circle cx="{cx:.0f}" cy="{h}" r="{r * (1 if i % 2 == 0 else .82):.0f}" fill="{color}"/>')
        return f'<svg class="abs" style="left:{x}px;top:{y}px" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(parts)}</svg>'
    raise ValueError(kind)


def scallop(color, side="right", width=52, count=12, height=1280):
    r = height / count / 2
    parts = []
    for i in range(count + 1):
        cy = r + i * 2 * r - r
        cx = width - r if side == "right" else r
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{color}"/>')
    rect_x = width - r if side == "right" else 0
    parts.append(f'<rect x="{rect_x:.0f}" y="0" width="{r:.0f}" height="{height}" fill="{color}"/>')
    pos = "right:0" if side == "right" else "left:0"
    return f'<svg class="abs" style="{pos};top:0" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'


def photo(src, w, h, x, y):
    """A pre-cut picture (the shape is baked into the image, so the printer never clips a large photo)."""
    return f'<img class="abs" src="{src}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'


def plate(text, size, rot, color, bg="#FFFFFF"):
    return (f'<div class="plate" style="font-size:{size}px;transform:rotate({rot}deg);color:{color};background:{bg}">'
            f'{text}</div>')


def wa(text):
    return f"https://wa.me/{WA_NUMBER}?text=" + quote(text)


def action_bar(go, what, href, alt=None, alt_href=None):
    alt_html = f'<a class="alt" href="{alt_href}">{alt}</a>' if alt else ""
    return (f'<div class="bar"><a href="{href}" style="display:flex;gap:16px;align-items:center;flex:1">'
            f'<span class="go">{go} &#8594;</span><span class="what">{what}</span></a>{alt_html}</div>')


ICONS = {
    "phone": '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>',
}


def icon(name, color, size=34, sw=1.6, x=None, y=None):
    cls = ' class="abs"' if x is not None else ""
    return (f'<svg{cls} style="{_pos(x, y)}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


class Pages:
    """Collects slides; the look draws each page's frame and footer."""

    def __init__(self, T, foot_name, look=None):
        self.T = T
        self.foot_name = foot_name
        self.look = look
        self.slides = []
        self.dark = {T.NAVY, T.COBALT, T.BERRY, T.GREEN}

    def add(self, ground, inner, foot=True):
        n = len(self.slides) + 1
        dark = ground in self.dark
        L = self.look
        frame = L.frame(ground, dark, n) if L else ""
        if foot:
            f = (L.footer(self.foot_name, n, dark) if L else
                 f'<div class="foot"><span>Veshannastro</span><span>{esc(self.foot_name)} &#183; {n:02d}</span></div>')
        else:
            f = ""
        bg = L.ground_css(ground, dark, n) if L else f"background:{ground}"
        self.slides.append(f'<section class="slide{" dark" if dark else ""}" style="{bg}">{frame}{inner}{f}</section>')

    def html(self, title):
        extra = self.look.extra_css() if self.look else ""
        body = "".join(self.slides).replace("{{TOTAL}}", f"{len(self.slides):02d}")
        for a, b in getattr(self, "subs", {}).items():
            body = body.replace(a, b)
        return (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><style>{css(self.T, extra)}</style></head>'
                f'<body>{body}</body></html>')
