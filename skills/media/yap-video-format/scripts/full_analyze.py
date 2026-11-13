#!/usr/bin/env python3
"""Full-video breakdown of every IG reel in list_ig_<handle>.json (needs info_done/video_url).

Per reel: download -> media/<id>.mp4 (kept), OCR frames 0.2/1/2.5 s, 12-frame contact sheet,
hook strip, scene-cut count (edit pace), full transcript with word timestamps
(WPM, pauses). Writes full_raw.jsonl (resumable).
Whisper: mlx-whisper if importable (Mac), else whisper-cli (CUDA on the Windows PC) with ggml-small.en.
OCR: Apple Vision binary on Mac, RapidOCR ocr.py elsewhere (via _plat.py).
Usage: Mac     ~/.hermes/cache/scratch/wv/bin/python full_analyze.py <workdir> <handle>
       Windows C:/Users/<you>/.hermes/tools/social-scraper/.venv/Scripts/python.exe full_analyze.py <workdir> <handle>
"""
import json, re, sys, urllib.request, statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat  # noqa: E402
_plat.utf8_stdout()

W = Path(sys.argv[1]).expanduser(); H = sys.argv[2]
OCR = _plat.ocr_cmd(W)
FFMPEG, FFPROBE = _plat.FFMPEG, _plat.FFPROBE
MED = W / "media"; SH = W / "sheets"; HK = W / "hook_strips"
for d in (MED, SH, HK): d.mkdir(exist_ok=True)
OUT = W / "full_raw.jsonl"
done = set()
if OUT.exists():
    for l in OUT.open(encoding="utf-8"):
        try: done.add(json.loads(l)["id"])
        except Exception: pass

try:
    import mlx_whisper
    MODEL = "mlx-community/whisper-large-v3-turbo"
except ImportError:  # Windows / Linux: whisper-cli
    mlx_whisper = None
    MODEL = _plat.whisper_model("ggml-small.en.bin", "ggml-base.en.bin")
BRACKET = re.compile(r"^\s*[\[\(].*[\]\)]\s*$")


def run(cmd, timeout=300):
    return _plat.run(cmd, timeout=timeout)


def transcribe(wav, tmp, pid):
    """-> (full text, [{w,s,e}]) ; mlx-whisper on Mac, whisper-cli -ojf token timings elsewhere."""
    if mlx_whisper:
        tr = mlx_whisper.transcribe(str(wav), path_or_hf_repo=MODEL, word_timestamps=True, language="en", condition_on_previous_text=False)
        words = [{"w": w["word"].strip(), "s": round(float(w["start"]), 2), "e": round(float(w["end"]), 2)} for s in tr["segments"] for w in s.get("words", [])]
        return " ".join(s["text"].strip() for s in tr["segments"]).strip(), words
    base = tmp / f"{pid}_w"
    run([_plat.WHISPER, "-m", MODEL, "-f", str(wav), "-l", "en", "-ojf", "-of", str(base), "-np"], timeout=900)
    j = json.loads(Path(str(base) + ".json").read_text(encoding="utf-8", errors="replace"))
    words, text = [], []
    for seg in j.get("transcription", []):
        text.append(seg["text"].strip())
        for tok in seg.get("tokens", []):
            t = tok.get("text", "")
            if not t or t.startswith("[_") or t.startswith("<|"): continue
            ts, te = float(tok["offsets"]["from"]) / 1000, float(tok["offsets"]["to"]) / 1000
            if t.startswith(" ") or not words: words.append({"w": t.strip(), "s": round(ts, 2), "e": round(te, 2)})
            else: words[-1]["w"] += t; words[-1]["e"] = round(te, 2)  # sub-word continuation
    words = [w for w in words if w["w"] and not BRACKET.match(w["w"])]
    return " ".join(text).strip(), words


def ocr(paths):
    r = run([*OCR, *map(str, paths)]); res = {}
    for l in r.stdout.splitlines():
        try: d = json.loads(l); res[d["path"]] = [x["t"] for x in d.get("lines", [])]
        except Exception: pass
    return [res.get(str(p), []) for p in paths]


def dur(v):
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)])
    try: return float(r.stdout.strip())
    except Exception: return None


entries = _plat.read_json(W / f"list_ig_{H}.json")["entries"]
todo = [e for e in entries if e.get("info_done") and e["id"] not in done]
print(len(todo), "to do", flush=True)
for n, e in enumerate(todo, 1):
    pid = e["id"]; rec = {k: e.get(k) for k in ("id", "url", "kind", "product_type", "timestamp", "duration", "caption", "views", "likes", "comments", "shares")}
    v = MED / f"{pid}.mp4"
    try:
        if not v.exists() and e.get("video_url"):
            req = urllib.request.Request(e["video_url"], headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.instagram.com/"})
            v.write_bytes(urllib.request.urlopen(req, timeout=180).read())
        if not v.exists() or v.stat().st_size < 1000:
            rec["kind"] = rec.get("kind") or "no_video"; raise RuntimeError("no video")
        D = dur(v) or e.get("duration") or 0; rec["duration"] = D
        tmp = W / "_tmp"; tmp.mkdir(exist_ok=True)
        fr = []
        for i, t in enumerate((0.2, 1.0, 2.5)):
            f = tmp / f"{pid}_f{i}.jpg"; run([FFMPEG, "-y", "-loglevel", "error", "-ss", str(t), "-i", str(v), "-frames:v", "1", "-vf", "scale=-2:960", str(f)])
            if f.exists(): fr.append(f)
        rec["ocr"] = dict(zip(("0.2", "1.0", "2.5"), ocr(fr)))
        if fr:
            ins = sum((["-i", str(f)] for f in fr), [])
            run([FFMPEG, "-y", "-loglevel", "error", *ins, "-filter_complex", "".join(f"[{i}:v]scale=-2:480[s{i}];" for i in range(len(fr))) + "".join(f"[s{i}]" for i in range(len(fr))) + f"hstack=inputs={len(fr)}", str(HK / f"{pid}.jpg")])
        # 12-frame contact sheet (4x3) with timestamps in filename order
        step = max(D / 12, 0.1)
        run([FFMPEG, "-y", "-loglevel", "error", "-i", str(v), "-vf", f"fps=1/{step:.3f},scale=270:-2,tile=6x2", "-frames:v", "1", str(SH / f"{pid}.jpg")])
        # mid-video OCR (caption style / overlays)
        mids = []
        for i, t in enumerate((D * 0.33, D * 0.66)):
            f = tmp / f"{pid}_m{i}.jpg"; run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1", "-vf", "scale=-2:960", str(f)])
            if f.exists(): mids.append(f)
        rec["ocr_mid"] = ocr(mids)
        # scene cuts
        r = run([FFMPEG, "-i", str(v), "-vf", "select='gt(scene,0.30)',showinfo", "-an", "-f", "null", "-"], timeout=600)
        cuts = [float(x.split("pts_time:")[1].split()[0]) for x in r.stderr.splitlines() if "pts_time:" in x]
        rec["cuts"] = cuts; rec["cuts_per_10s"] = round(len(cuts) / D * 10, 2) if D else None
        # transcript
        wav = tmp / f"{pid}.wav"; run([FFMPEG, "-y", "-loglevel", "error", "-i", str(v), "-ac", "1", "-ar", "16000", str(wav)])
        rec["transcript"], words = transcribe(wav, tmp, pid)
        rec["words"] = words
        if len(words) > 5:
            span = words[-1]["e"] - words[0]["s"]
            rec["wpm"] = round(len(words) / span * 60) if span > 0 else None
            gaps = [b["s"] - a["e"] for a, b in zip(words, words[1:])]
            rec["first_word_at"] = words[0]["s"]; rec["pauses_over_0.6s"] = sum(g > 0.6 for g in gaps)
            rec["hook_spoken"] = " ".join(w["w"] for w in words if w["s"] < 4.0)
        for f in list(tmp.glob(f"{pid}*")): f.unlink()
    except Exception as ex:
        rec["err"] = str(ex)[:200]
    with OUT.open("a", encoding="utf-8") as fh: fh.write(json.dumps(rec, default=float) + "\n")
    print(f"[{n}/{len(todo)}] {pid} views={rec.get('views')} dur={rec.get('duration')} wpm={rec.get('wpm')} | {(rec.get('hook_spoken') or '')[:70]}", flush=True)
print("ALL_DONE", flush=True)
