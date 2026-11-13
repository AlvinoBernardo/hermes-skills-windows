"""IG/TikTok 'founder vlog' caption style (ref: igexport-Dd-_ELIhr7J / DeDzHf4Bfcx).
- TikTok Sans SemiBold, lowercase, 2-3 words per chunk, hard cuts (no pop/animation)
- white by default; whole chunk switches to yellow #F0FB00 or green #00FF00 on emphasis lines
- thin dark outline + soft shadow, centered on chest just under the face
- persistent 2-line title near top in white with black outline
"""
import json, re, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
# TikTok Sans ships with the skill (assets/); pass by path, no install needed on any OS. env TIKTOKSANS_TTF overrides.
FONT = os.environ.get("TIKTOKSANS_TTF") or str(__import__("pathlib").Path(__file__).resolve().parent.parent / "assets/tiktoksans.ttf")
SRC = os.environ.get("SRC", "cut2.mov")
OUT = os.environ.get("OUT", "final_ig_nomusic.mp4")
info = json.load(open("cut2.json"))
TOTAL = info["total"]; NF = int(TOTAL * FPS)

def font(size, wght):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([36, 100, wght, 0])
    return f

CAP = font(78, 620)
TITLE = font(60, 620)
WHITE, YELLOW, GREEN = (255, 255, 255), (240, 251, 0), (0, 255, 0)

TITLE_TEXT = ["2 tips to ship faster", "when you're vibe coding:"]
CAP_Y = 1250          # chunk center (chest, under chin)
CAP_Y_BROLL = 1640
TITLE_Y = 470         # title block center

# ---------- words -> chunks ----------
tr = json.load(open("cut2_transcript.json"))
words = [[w["word"].strip(), w["start"], w["end"]] for s in tr["segments"] for w in s["words"] if w["word"].strip()]
clean = []
for t, a, b in words:
    base = re.sub(r"[^\w']", "", t).lower()
    if base == "dude" or (base == "now" and 19.9 < a < 20.2):
        continue
    if base == "switch": t = t.replace("switch", "search")
    clean.append([t, a, b])

def norm(tok):
    keep_q = tok.endswith("?")
    t = re.sub(r"[.,!?]", "", tok)
    if t not in ("I", "ADE") and not t.startswith("I'"):
        t = t.lower()
    if t in ("orca", "dev"): t = t.capitalize()
    return t + ("?" if keep_q else "")

chunks, cur = [], []
for w in clean:
    cur.append(w); n = len(cur)
    if w[0][-1] in ",.?!" or n == 3 or (n == 2 and len(cur[0][0]) + len(cur[1][0]) > 14):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

# emphasis: phrase -> color (whole chunk recolors, like the reference)
EMPH = [("two tips", YELLOW), ("ship faster", YELLOW), ("voice dictation", GREEN), ("six agents", YELLOW),
        ("20", GREEN), ("agents", GREEN), ("use ADE", YELLOW), ("multiple panels", GREEN),
        ("Orca Dev", YELLOW), ("terminals", GREEN)]
caps = []
for i, c in enumerate(chunks):
    text = " ".join(norm(w[0]) for w in c)
    start = c[0][1]
    end = chunks[i + 1][0][1] if i + 1 < len(chunks) else TOTAL
    end = min(end, c[-1][2] + 0.5)
    col = WHITE
    for k, kc in EMPH:
        if re.search(r"\b" + re.escape(k) + r"\b", text):
            col = kc; break
    caps.append((start, end, text, col))

BR_IN, BR_OUT = 22.80, 25.92

def text_layer(text, f, fill, stroke, stroke_rgba, shadow_a, blur):
    bb = f.getbbox(text, stroke_width=stroke)
    pad = 30
    L = Image.new("RGBA", (bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.text((pad - bb[0], pad - bb[1]), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_rgba)
    sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, shadow_a), mask=L.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (L.width, L.height + 4), (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 3)); out.alpha_composite(L, (0, 0))
    return out

_cache = {}
def cap_img(text, col):
    k = (text, col)
    if k not in _cache:
        L = text_layer(text, CAP, col, 2, (0, 0, 0, 150), 150, 5)
        if L.width > 980:
            s = 980 / L.width
            L = L.resize((int(L.width * s), int(L.height * s)), Image.LANCZOS)
        _cache[k] = L
    return _cache[k]

def title_img():
    lines = [text_layer(t, TITLE, WHITE, 4, (0, 0, 0, 255), 90, 4) for t in TITLE_TEXT]
    lh = 74
    img = Image.new("RGBA", (max(l.width for l in lines), lh * (len(lines) - 1) + lines[-1].height), (0, 0, 0, 0))
    for i, l in enumerate(lines):
        img.alpha_composite(l, ((img.width - l.width) // 2, i * lh))
    return img
TIT = title_img()

# B-roll (same as previous edit: Orca screenshot card)
hero = Image.open("orca/readme-hero.jpg").convert("RGB")
bg = hero.resize((int(hero.width * 1920 / hero.height), 1920), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
bg = Image.eval(bg, lambda v: int(v * 0.45)).convert("RGBA")
def broll(t):
    k = (t - BR_IN) / (BR_OUT - BR_IN); k = k * k * (3 - 2 * k)
    cw_, ch_ = 1000, 1180
    src_w = int(hero.height * cw_ / ch_)
    x0 = int((hero.width - src_w) * (0.05 + 0.9 * k))
    crop = hero.crop((x0, 0, x0 + src_w, hero.height)).resize((cw_, ch_), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", crop.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, cw_ - 1, ch_ - 1), radius=36, fill=255)
    crop.putalpha(m)
    f = bg.copy(); f.alpha_composite(crop, ((W - cw_) // 2, 330))
    return f

cmd = ["ffmpeg", "-y", "-v", "error", "-i", SRC,
       "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-filter_complex",
       "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];"
       "[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,"
       "loudnorm=I=-14:TP=-1.5:LRA=7[a]",
       "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
       "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", OUT]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
blank = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for i in range(NF):
    t = i / FPS
    inb = BR_IN <= t < BR_OUT
    img = broll(t) if inb else blank.copy()
    if not inb:
        img.alpha_composite(TIT, ((W - TIT.width) // 2, TITLE_Y - TIT.height // 2))
    for a, b, txt, col in caps:
        if a <= t < b:
            L = cap_img(txt, col)
            cy = CAP_Y_BROLL if inb else CAP_Y
            img.alpha_composite(L, ((W - L.width) // 2, cy - L.height // 2))
            break
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait()
print("done", p.returncode)
for c in caps:
    print(f"{c[0]:6.2f}-{c[1]:6.2f}  {'Y' if c[3]==YELLOW else 'G' if c[3]==GREEN else ' '}  {c[2]}")
