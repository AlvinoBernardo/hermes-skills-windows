"""Shared drawing helpers for above-head overlay cards (copy into the clip's scratch dir as common.py).
Contract for parallel card subagents:
  - ev.json (written by the parent from cutwords) holds every beat time in CUT seconds.
  - each subagent writes card_<name>.py with  draw(t) -> None | RGBA (1080, 480),
    built with card_base() and returned via place(card, t, EV[show], EV[hide]).
  - render.py pastes every card layer at frame y=40; keep card height <= ~420 so it clears the hair.
  - previews: python3 card_preview.py card_<name> t1,t2,...
"""
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
def _first(*c):
    for p in c:
        if p and os.path.exists(os.path.expanduser(p)): return os.path.expanduser(p)
    return os.path.expanduser(c[1])
# TikTok Sans is bundled in the skill's assets/ (pass by path, no install). Skill dir differs per OS, so try each.
FONT = _first(os.environ.get("TIKTOKSANS_TTF"),
              "~/.hermes/skills/media/talking-head-tiktok-edit/assets/tiktoksans.ttf",
              os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes/skills/media/talking-head-tiktok-edit/assets/tiktoksans.ttf"))
# Emoji: Apple Color Emoji (macOS, bitmap strike 160 only) / Segoe UI Emoji (Windows, scalable COLR) / Noto Color Emoji (Linux)
EMO = _first("/System/Library/Fonts/Apple Color Emoji.ttc", "C:/Windows/Fonts/seguiemj.ttf",
             "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
EMO_SIZE = 109 if "Noto" in EMO else 160   # Apple: fixed bitmap size 160; Noto: fixed 109; Segoe is scalable
EV = json.load(open(os.path.join(HERE, "ev.json")))
WHITE, YELLOW, GREEN, RED, GREY = (255, 255, 255), (240, 251, 0), (0, 255, 0), (255, 77, 77), (200, 200, 205)
CARD_FILL = (18, 18, 22, 232)
_fc = {}
def font(size, wght=620):
    k = (size, wght)
    if k not in _fc:
        f = ImageFont.truetype(FONT, size); f.set_variation_by_axes([36, 100, wght, 0]); _fc[k] = f
    return _fc[k]
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def fade(im, a):
    if a >= 1: return im
    im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * max(0, a)))); return im
def pop(img, t, t0, d=0.14):
    """scale 0.82->1 + fade-in over d seconds starting at t0"""
    p = ease((t - t0) / d)
    if p >= 1: return img
    s = 0.82 + 0.18 * p
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
    return fade(im, p)
def put_pop(dst, full, t, t0, x, cy):
    """paste `full` popping in at t0, left edge x, vertically centred on cy"""
    if t < t0: return
    p = pop(full, t, t0)
    dst.alpha_composite(p, (x + (full.width - p.width) // 2, cy - p.height // 2))
_ec = {}
def emoji(ch, size):
    """Apple Color Emoji scaled by its MAX side (tall emoji like the phone overflow when scaled by width)"""
    k = (ch, size)
    if k not in _ec:
        f = ImageFont.truetype(EMO, EMO_SIZE)
        im = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox()); s = size / max(im.size)
        _ec[k] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return _ec[k]
_pc = {}
def pill(text, size, fg, bg):
    k = (text, size, fg, bg)
    if k not in _pc:
        f = font(size, 760); bb = f.getbbox(text)
        w, h = bb[2] - bb[0] + 44, size + 26
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg)
        d.text((22 - bb[0], (h - (bb[3] - bb[1])) // 2 - bb[1]), text, font=f, fill=fg)
        _pc[k] = im
    return _pc[k]
_lc = {}
def label(text, size, fill, wght=760):
    k = (text, size, fill, wght)
    if k not in _lc:
        f = font(size, wght); bb = f.getbbox(text)
        im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), text, font=f, fill=fill)
        _lc[k] = im
    return _lc[k]
def card_base(cw, ch, radius=34):
    """dark rounded card. Draw row backgrounds on a SEPARATE layer and alpha_composite
    (ImageDraw on the card REPLACES pixels and punches see-through holes)."""
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=radius, fill=CARD_FILL, outline=(255, 255, 255, 40), width=2)
    return im
_shc = {}
def place(card, t, t_show, t_hide, x=80, y=0):
    """full-width 1080x480 layer with card + soft shadow, popping in at t_show and out at t_hide.
    The blurred shadow is cached per card size (re-blurring every frame cost ~32 ms/frame)."""
    if not (t_show <= t < t_hide): return None
    a = ease((t - t_show) / 0.16) * ease((t_hide - t) / 0.12)
    s = 0.9 + 0.1 * a
    L = Image.new("RGBA", (W, 480), (0, 0, 0, 0))
    k = (card.width, card.height)
    if k not in _shc:
        sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((40, 46, 40 + card.width, 46 + card.height), radius=34, fill=(0, 0, 0, 120))
        _shc[k] = sh.filter(ImageFilter.GaussianBlur(16))
    L.alpha_composite(fade(_shc[k], a), (x - 40, y - 40))
    c = card if s >= 0.999 else card.resize((int(card.width * s), int(card.height * s)), Image.LANCZOS)
    L.alpha_composite(fade(c, a), (x + (card.width - c.width) // 2, y + (card.height - c.height) // 2))
    return L
def photo(path, w, h, radius=24, focus=(0.5, 0.35)):
    """cover-crop an image to w x h with rounded corners; focus = centre of interest in 0..1"""
    im = Image.open(path).convert("RGB"); s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x = int(min(max(0, im.width * focus[0] - w / 2), im.width - w)); y = int(min(max(0, im.height * focus[1] - h / 2), im.height - h))
    im = im.crop((x, y, x + w, y + h)).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    im.putalpha(m); return im
