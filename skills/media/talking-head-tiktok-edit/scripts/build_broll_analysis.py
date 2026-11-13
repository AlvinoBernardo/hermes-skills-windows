# Reference: B-roll builder used for the "I analyzed all 793 of Mino Lee's TikToks" pre-shoot kit (Oct 26).
# Renders 1080x1920 30fps PIL->ffmpeg clips: thumbnail wall zoom-out + counter pill + highlight pass,
# terminal-style scroll of a real log with progress bar, OCR-box/typed-transcript/score demo, full-page scroll of an HTML report.
# Copy into a scratch dir and adapt paths (W0 = analysis _work dir, frames/ = crisp source frames, ocrbox = Vision OCR with x/w boxes).
#!/usr/bin/env python3
"""B-roll builder for the '793 Mino Lee videos' talking-head clip. Renders 1080x1920 30fps mp4s."""
import json, math, subprocess, sys, glob, os, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = Path(__file__).parent
W0 = Path.home() / "Desktop/Noxy/Noxy-2026-10-26-mino-lee-hooks/_work"
OUT = D / "out"; OUT.mkdir(exist_ok=True)
TT = str(Path(__file__).resolve().parent.parent / "assets/tiktoksans.ttf")   # bundled with the skill, pass by path
# monospace for the terminal clip: Menlo (macOS) -> Consolas (Windows) -> DejaVu Mono (Linux)
MENLO = next((f for f in ("/System/Library/Fonts/Menlo.ttc", "C:/Windows/Fonts/consola.ttf",
                          "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf") if os.path.exists(f)), "C:/Windows/Fonts/consola.ttf")
# social-scraper venv python (Playwright, RapidOCR): bin/ on macOS, Scripts/ on Windows
SS_PY = Path.home() / ".hermes/tools/social-scraper/.venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
# Vision OCR with boxes: compiled ./ocrbox (macOS, from ocrbox.swift) or ocrbox.py under RapidOCR (Windows/Linux)
OCRBOX = [str(D / "ocrbox")] if sys.platform == "darwin" else [str(SS_PY), str(D / "ocrbox.py")]
W, H, FPS = 1080, 1920, 30
YEL, GRN, RED, ORG = (240, 251, 0), (0, 255, 0), (255, 77, 77), (255, 122, 26)


def font(sz, wt=620, path=TT):
    f = ImageFont.truetype(path, sz)
    if path == TT:
        try: f.set_variation_by_axes([36, 100, wt, 0])
        except Exception: pass
    return f


def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def ease_io(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)


class Writer:
    def __init__(self, name, secs):
        self.n = int(secs * FPS); self.path = OUT / name
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                   "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", str(self.path)], stdin=subprocess.PIPE)
    def add(self, im): self.p.stdin.write(im.convert("RGB").tobytes())
    def close(self): self.p.stdin.close(); self.p.wait(); print("wrote", self.path)


def pill(d, cx, cy, text, fg, bg, sz=54, pad=(34, 16)):
    f = font(sz, 760); bb = d.textbbox((0, 0), text, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0, y0 = cx - tw / 2 - pad[0], cy - th / 2 - pad[1]
    d.rounded_rectangle([x0, y0, cx + tw / 2 + pad[0], cy + th / 2 + pad[1] + 6], radius=(th + 2 * pad[1]) / 2, fill=bg)
    d.text((cx - tw / 2 - bb[0], cy - th / 2 - bb[1] + 3), text, font=f, fill=fg)


def rows():
    R = json.load(open(W0 / "hooks_analyzed.json"))
    R.sort(key=lambda r: r.get("date") or "")
    return R


def proven(r):
    return (r["date"] or "") < "2026-10-19" and r["outlier"] >= 2 and (
        (r["handle"] == "mino.mp4" and r["views"] >= 40000) or (r["handle"] == "mino1ee" and r["views"] >= 1e6))


# ---------------------------------------------------------------- 1. wall of 793
def wall():
    R = rows(); cols, rws = 29, 28; tw, th, g = 36, 64, 1; S = 3
    gw, gh = cols * (tw + g), rws * (th + g); ox, oy = (W - gw) // 2, (H - gh) // 2 + 40
    big = Image.new("RGB", (W * S, H * S), (10, 10, 12)); hi = big.copy()
    dim_big = big.copy()
    pos = {}
    for i, r in enumerate(R):
        c, rr = i % cols, i // cols
        x, y = (ox + c * (tw + g)) * S, (oy + rr * (th + g)) * S
        p = W0 / "hook_strips" / f"{r['id']}.jpg"
        if p.exists():
            im = Image.open(p).convert("RGB"); fw = im.width if r.get("kind") == "slideshow" else im.width // 3
            im = im.crop((0, 0, fw, im.height))
            # cover-crop to 9:16
            tr = 9 / 16; ir = im.width / im.height
            if ir > tr: nw = int(im.height * tr); im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
            else: nh = int(im.width / tr); im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
            im = im.resize((tw * S, th * S), Image.LANCZOS)
        else:
            im = Image.new("RGB", (tw * S, th * S), (40, 40, 44))
        big.paste(im, (x, y)); pos[r["id"]] = (x, y)
        if proven(r):
            hi.paste(im, (x, y))
        else:
            dim_big.paste(Image.blend(im, Image.new("RGB", im.size, (10, 10, 12)), 0.78), (x, y))
    dh = ImageDraw.Draw(dim_big)
    for r in R:
        if proven(r):
            x, y = pos[r["id"]]; dim_big.paste(hi.crop((x, y, x + tw * S, y + th * S)), (x, y))
            dh.rectangle([x - 4, y - 4, x + tw * S + 3, y + th * S + 3], outline=GRN, width=5)
    small = big.resize((W, H), Image.LANCZOS); small_hi = dim_big.resize((W, H), Image.LANCZOS)
    small_hi.save(OUT / "mino_793_wall_163_highlighted.png"); small.save(OUT / "mino_793_wall.png")
    # zoom start: centred on the 'view jail' video tile
    fx, fy = pos.get("7665790023186402591", (W * S // 2, H * S // 2)); fx += tw * S / 2; fy += th * S / 2
    wtr = Writer("mino_793_wall_zoomout_7s.mp4", 7)
    for k in range(wtr.n):
        t = k / FPS
        if t < 2.4:
            z = 9.0 ** (1 - ease_io(t / 2.4))  # 9x -> 1x
            cw, ch = W * S / z, H * S / z
            cx = fx + (W * S / 2 - fx) * ease_io(t / 2.4); cy = fy + (H * S / 2 - fy) * ease_io(t / 2.4)
            x0 = min(max(cx - cw / 2, 0), W * S - cw); y0 = min(max(cy - ch / 2, 0), H * S - ch)
            fr = big.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        elif t < 3.4:
            fr = small.copy()
        else:
            fr = Image.blend(small, small_hi, ease((t - 3.4) / 0.5))
        d = ImageDraw.Draw(fr)
        if t < 3.4:
            n = int(793 * ease(min(1, max(0, (t - 0.2) / 2.6))))
            pill(d, W / 2, 150, f"{n} VIDEOS", (0, 0, 0), YEL, 64)
        else:
            a = ease((t - 3.4) / 0.35)
            if a < 1: pill(d, W / 2, 150, "793 VIDEOS", (0, 0, 0), YEL, 64)
            else: pill(d, W / 2, 150, "163 ACTUALLY WENT VIRAL", (0, 0, 0), GRN, 60)
        wtr.add(fr)
    wtr.close()


# ---------------------------------------------------------------- 2. terminal log
def terminal():
    lines = [l.rstrip("\n") for l in open(W0 / "extract.log") if l.startswith("[")]
    f = font(27, path=MENLO); fb = font(27, path=MENLO); lh = 36
    cw = f.getlength("M"); maxc = int((W - 80) / cw)
    top, bottom = 170, H - 260; vis = (bottom - top) // lh
    wtr = Writer("terminal_extract_793_hooks_6s.mp4", 6)
    pat = re.compile(r"^\[(\d+)\] (@\S+) (\d+) (\w+) views=(\d+) \| ?(.*)$")
    for k in range(wtr.n):
        t = k / FPS
        n = max(1, int(len(lines) * ease_io(min(1, max(0, (t - 0.2) / 5.0)))))
        fr = Image.new("RGB", (W, H), (11, 14, 20)); d = ImageDraw.Draw(fr)
        d.rectangle([0, 0, W, 110], fill=(28, 32, 40))
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse([36 + i * 44, 40, 64 + i * 44, 68], fill=c)
        d.text((190, 36), "hermes · extract_hooks.py · @mino.mp4 @mino1ee", font=font(30, path=MENLO), fill=(170, 176, 190))
        y = top
        for l in lines[max(0, n - vis):n]:
            m = pat.match(l); x = 40
            if not m:
                d.text((x, y), l[:maxc], font=f, fill=(200, 200, 200)); y += lh; continue
            num, h, pid, kind, views, hook = m.groups()
            parts = [(f"[{num}] ", (120, 128, 140)), (h + " ", ORG), (f"{int(views):,} views ", YEL), ("| " + hook, (235, 235, 235))]
            used = 0
            for s, col in parts:
                s = s[:maxc - used]
                if not s: break
                d.text((x, y), s, font=f, fill=col); x += f.getlength(s); used += len(s)
            y += lh
        # progress bar
        p = n / len(lines)
        d.rounded_rectangle([40, H - 200, W - 40, H - 160], radius=20, fill=(35, 40, 50))
        d.rounded_rectangle([40, H - 200, 40 + (W - 80) * p, H - 160], radius=20, fill=GRN if n == len(lines) else YEL)
        lab = f"{n}/793 videos" + ("  DONE" if n == len(lines) else "")
        d.text((40, H - 140), lab, font=font(36, 760), fill=(255, 255, 255))
        wtr.add(fr)
    wtr.close()


# ---------------------------------------------------------------- 3. OCR + transcript demo
def ocr_demo():
    src = D / "frames/viewjail_1.0.jpg"
    boxes = json.loads(subprocess.run(OCRBOX + [str(src)], capture_output=True, text=True).stdout)["lines"]
    im = Image.open(src).convert("RGB")
    bg = im.resize((W, H)).filter(ImageFilter.GaussianBlur(40)); bg = Image.blend(bg, Image.new("RGB", (W, H)), 0.6)
    fw, fh = 540, 960; fx, fy = (W - fw) // 2, 110
    frame = im.resize((fw, fh), Image.LANCZOS)
    mask = Image.new("L", (fw, fh), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, fw, fh], 34, fill=255)
    said = "\u201cThis is how to break out of every level of view jail.\u201d"
    wtr = Writer("ocr_transcribe_score_demo_6s.mp4", 6)
    fsay = font(46, 700)
    for k in range(wtr.n):
        t = k / FPS
        fr = bg.copy(); d = ImageDraw.Draw(fr)
        fr.paste(frame, (fx, fy), mask)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        for i, b in enumerate(boxes):
            a = ease((t - 0.5 - i * 0.18) / 0.25)
            if a <= 0: continue
            x0 = fx + b["x"] * fw - 6; y0 = fy + b["y"] * fh - 5; x1 = x0 + b["w"] * fw + 12; y1 = y0 + b["h"] * fh + 10
            dl.rectangle([x0, y0, x0 + (x1 - x0) * a, y1], fill=(240, 251, 0, 60), outline=YEL + (255,), width=4)
        fr = Image.alpha_composite(fr.convert("RGBA"), lay).convert("RGB"); d = ImageDraw.Draw(fr)
        if t > 0.4: pill(d, W / 2, fy + fh + 70, "1. READ THE TEXT ON SCREEN", (0, 0, 0), YEL, 44)
        if t > 2.0:
            pill(d, W / 2, fy + fh + 170, "2. TRANSCRIBE THE FIRST 3 SECONDS", (0, 0, 0), (255, 255, 255), 44)
            nchar = int(len(said) * min(1, (t - 2.2) / 1.3)) if t > 2.2 else 0
            txt = said[:nchar]; words = txt.split(" "); linesx, cur = [], ""
            for w_ in words:
                if fsay.getlength(cur + " " + w_) > W - 160: linesx.append(cur); cur = w_
                else: cur = (cur + " " + w_).strip()
            linesx.append(cur)
            for j, l in enumerate(linesx): d.text((80, fy + fh + 230 + j * 58), l, font=fsay, fill=(255, 255, 255))
        if t > 4.0:
            a = ease((t - 4.0) / 0.2)
            pill(d, W / 2, fy + fh + 420, "3. SCORE IT: 139x HIS NORMAL VIEWS", (0, 0, 0), GRN, int(44 * (0.8 + 0.2 * a)))
        wtr.add(fr)
    wtr.close()


# ---------------------------------------------------------------- 4. hook bank scroll
def bank_scroll():
    shot = D / "bank_full.png"
    if not shot.exists():
        subprocess.run([str(SS_PY), "-c", f"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={{'width':540,'height':960}},device_scale_factor=2,color_scheme='dark')
    pg.goto('{(Path.home() / "Desktop/Noxy/Noxy-2026-10-26-mino-lee-hooks/_preview.html").as_uri()}'); pg.add_style_tag(content=':root{{--foreground:#eeeeee;--muted-foreground:#9a9a9a;--card:#17171a;--border:#333338;--accent:#ff7a1a}} body{{background:#0d0d0f}}')
    pg.wait_for_timeout(800); pg.screenshot(path='{shot.as_posix()}',full_page=True); b.close()
"""], check=True)
    im = Image.open(shot).convert("RGB"); print("bank page", im.size)
    im.crop((0, 0, im.width, min(im.height, 7000))).save(OUT / "hook_bank_163_page_top.png")
    maxy = min(im.height - H, 5200)
    wtr = Writer("hook_bank_163_scroll_6s.mp4", 6)
    for k in range(wtr.n):
        t = k / FPS; y = maxy * ease_io(min(1, max(0, (t - 0.4) / 5.2)))
        fr = im.crop((0, int(y), W, int(y) + H)); wtr.add(fr)
    wtr.close()


if __name__ == "__main__":
    for name in (sys.argv[1:] or ["wall", "terminal", "ocr_demo", "bank_scroll"]):
        globals()[name]()
