#!/usr/bin/env python3
"""Full-video breakdown of every reel/TikTok in <workdir>/media/*.mp4 (format-skill mode, step 4).

Usage: full_analyze.py <workdir> <handle> [--workers 2] [--model PATH] [--limit N] [--lang en]
Run with the social-scraper venv python (needs Pillow). Per video writes analysis/<id>.json and:
  sheets/<id>.jpg   12 frames across the whole video (4x3 grid, timestamps burned in)
  strips/<id>.jpg   hook strip: frames at 0.2 / 1.0 / 2.5 s
JSON: duration, size, aspect, ocr_hook {0.2,1.0,2.5: [lines]}, ocr_mid {25%,50%,75%: [lines]},
      cuts (scene-change times), cuts_per_10s, transcript (full text), segments, words [{w,s,e}],
      n_words, wpm (over the speaking span), first_word_s, pauses (gaps >= 0.6 s), longest_pause_s,
      speech_ratio, music_only (True when whisper found < 6 real words).
OCR: Apple Vision `ocr` binary on the Mac, scripts/ocr.py (RapidOCR) elsewhere - same output.
Whisper: whisper-cli (Metal on Mac, CUDA on the PC) with ggml-small.en by default; word timing from -ojf tokens.
Resumable: skips ids that already have analysis/<id>.json. Ignores media/_* files.
~10-15 s per reel. To follow a still-running ig_media_info.py, loop it:
  while pgrep -f ig_media_info >/dev/null; do $PY full_analyze.py $W h; sleep 60; done; $PY full_analyze.py $W h
"""
import argparse
import json
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import FFMPEG, FFPROBE, WHISPER, ocr_cmd, run, save, whisper_model  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

BRACKET = re.compile(r"^\s*[\[\(].*[\]\)]\s*$")


def probe(v):
    r = run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
             "-of", "json", v])
    j = json.loads(r.stdout or "{}")
    s = (j.get("streams") or [{}])[0]
    return float((j.get("format") or {}).get("duration") or 0), s.get("width"), s.get("height")


def grab(v, t, out, w=360):
    run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", v, "-frames:v", "1", "-vf", f"scale={w}:-2",
         "-q:v", "3", out], timeout=60)
    return Path(out) if Path(out).exists() else None


def font(sz):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def grid(frames, labels, out, cols):
    ims = [Image.open(f).convert("RGB") for f in frames]
    if not ims:
        return
    w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), (0, 0, 0)); d = ImageDraw.Draw(sheet); f = font(max(14, w // 14))
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(im.resize((w, h)), (x, y))
        d.text((x + 6, y + 4), lab, font=f, fill="yellow", stroke_width=2, stroke_fill="black")
    sheet.save(out, quality=85)


def ocr(paths):
    if not paths:
        return []
    r = run([*ocr_cmd(), *map(str, paths)], timeout=300)
    res = {}
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line); res[Path(d["path"]).name] = [x["t"] for x in d.get("lines", [])]
        except Exception:
            pass
    return [res.get(Path(p).name, []) for p in paths]


def cuts(v):
    r = run([FFMPEG, "-hide_banner", "-i", v, "-vf", "scale=320:-2,select='gt(scene,0.3)',showinfo", "-an",
             "-f", "null", "-"], timeout=600)
    return [round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def transcribe(v, d, model, lang):
    wav = d / "a.wav"
    run([FFMPEG, "-v", "error", "-y", "-i", v, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav], timeout=300)
    if not wav.exists():
        return None
    run([WHISPER, "-m", model, "-f", wav, "-l", lang, "-ojf", "-of", d / "w", "-np"], timeout=900)
    try:
        j = json.loads((d / "w.json").read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    segs, words = [], []
    for s in j.get("transcription", []):
        segs.append({"s": float(s["offsets"]["from"]) / 1000, "e": float(s["offsets"]["to"]) / 1000,
                     "t": s["text"].strip()})
        for tok in s.get("tokens", []):
            t = tok.get("text", "")
            if not t or t.startswith("[_") or t.startswith("<|"):
                continue
            ts, te = float(tok["offsets"]["from"]) / 1000, float(tok["offsets"]["to"]) / 1000
            if t.startswith(" ") or not words:
                words.append({"w": t.strip(), "s": ts, "e": te})
            else:  # sub-word continuation
                words[-1]["w"] += t; words[-1]["e"] = te
    words = [w for w in words if w["w"] and not BRACKET.match(w["w"])]
    return segs, words


def analyze(v, W, model, lang):
    vid = v.stem
    dur, wd, ht = probe(v)
    if not dur:
        return {"id": vid, "error": "unreadable video"}
    with tempfile.TemporaryDirectory(dir=W / "_tmp") as td:
        d = Path(td)
        hook_t = [t for t in (0.2, 1.0, 2.5) if t < dur]
        hook = [grab(v, t, d / f"h{i}.jpg") for i, t in enumerate(hook_t)]
        mid_t = [dur * p for p in (0.25, 0.5, 0.75)]
        mid = [grab(v, t, d / f"m{i}.jpg") for i, t in enumerate(mid_t)]
        sheet_t = [dur * (i + 0.5) / 12 for i in range(12)]
        sheet = [grab(v, t, d / f"s{i:02d}.jpg", 320) for i, t in enumerate(sheet_t)]
        grid([f for f in hook if f], [f"{t:.1f}s" for t, f in zip(hook_t, hook) if f], W / "strips" / f"{vid}.jpg", 3)
        grid([f for f in sheet if f], [f"{t:.1f}s" for t, f in zip(sheet_t, sheet) if f], W / "sheets" / f"{vid}.jpg", 4)
        o = ocr([f for f in hook + mid if f])
        o_hook, o_mid = o[: len([f for f in hook if f])], o[len([f for f in hook if f]):]
        c = cuts(v)
        tr = transcribe(v, d, model, lang)
    segs, words = tr if tr else ([], [])
    rec = {"id": vid, "duration": round(dur, 2), "width": wd, "height": ht,
           "aspect": round(wd / ht, 3) if wd and ht else None,
           "ocr_hook": {f"{t:.1f}": x for t, x in zip(hook_t, o_hook)},
           "ocr_mid": {f"{int(p * 100)}%": x for p, x in zip((0.25, 0.5, 0.75), o_mid)},
           "cuts": c, "cuts_per_10s": round(len(c) / dur * 10, 2),
           "sheet": str(W / "sheets" / f"{vid}.jpg"), "strip": str(W / "strips" / f"{vid}.jpg")}
    if len(words) >= 6:
        span = max(words[-1]["e"] - words[0]["s"], 0.1)
        gaps = [(round(b["s"] - a["e"], 2), round(a["e"], 2)) for a, b in zip(words, words[1:]) if b["s"] - a["e"] >= 0.6]
        talk = sum(w["e"] - w["s"] for w in words)
        rec.update({"music_only": False, "transcript": " ".join(s["t"] for s in segs).strip(), "segments": segs,
                    "words": words, "n_words": len(words), "wpm": round(len(words) / span * 60, 1),
                    "first_word_s": round(words[0]["s"], 2), "pauses": [{"gap": g, "at": t} for g, t in gaps],
                    "longest_pause_s": max([g for g, _ in gaps], default=0), "speech_ratio": round(min(talk / dur, 1), 3)})
    else:
        rec.update({"music_only": True, "transcript": "", "segments": segs, "words": words, "n_words": len(words)})
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir"); ap.add_argument("handle")
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--model")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    W = Path(a.workdir).expanduser()
    for sub in ("analysis", "sheets", "strips", "_tmp"):
        (W / sub).mkdir(parents=True, exist_ok=True)
    model = a.model or whisper_model()
    vids = sorted(p for p in (W / "media").glob("*.mp4") if not p.name.startswith("_"))
    todo = [v for v in vids if not (W / "analysis" / f"{v.stem}.json").exists()]
    if a.limit:
        todo = todo[: a.limit]
    print(f"[fa] @{a.handle.lstrip('@')}: {len(todo)} to analyze, {len(vids) - len(todo)} done, model {Path(model).name}", flush=True)
    lock = Lock(); n = [0]

    def one(v):
        try:
            rec = analyze(v, W, model, a.lang)
        except Exception as e:  # keep going; the id is retried on the next run
            print(f"[fa] {v.stem} FAILED: {e}", flush=True); return
        save(W / "analysis" / f"{v.stem}.json", rec)
        with lock:
            n[0] += 1
            print(f"[fa] {n[0]}/{len(todo)} {v.stem} {rec.get('duration')}s cuts/10s={rec.get('cuts_per_10s')} "
                  f"wpm={rec.get('wpm', '-')} words={rec.get('n_words', 0)} hook={' / '.join(sum(rec.get('ocr_hook', {}).values(), []))[:60]!r}",
                  flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(one, todo))
    print("[fa] ALL_DONE", len(list((W / "analysis").glob("*.json"))))


if __name__ == "__main__":
    main()
