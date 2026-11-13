#!/usr/bin/env python3
"""Extract the hook (first ~6 s) of every TikTok in <workdir>/list_<handle>.json.

Per post: download video (<=720p), frames at 0.2/1.0/2.5 s -> OCR (macOS Vision binary, or RapidOCR via ocr.py on Windows),
whisper the first 12 s (spoken hook), save a small 3-frame strip to hook_strips/<id>.jpg, DELETE the video.
Slideshows: OCR the cover thumbnail. Resumable: appends to hooks_raw.jsonl, skips ids already present.
Usage (Mac: system python3; needs yt-dlp, ffmpeg, whisper-cli, the compiled ocr binary.
Windows: run with the social-scraper venv python, which has RapidOCR for ocr.py):
  python3 extract_hooks.py <workdir> <handle> [<handle> ...] [--workers 6]
Speed: ~60 posts/min with 6 workers on an M-series Mac (~13 min for 800 posts, ~30 MB of strips).
"""
import json, os, subprocess, sys, shutil, tempfile, urllib.request
for _s in (sys.stdout, sys.stderr):  # Windows pipes default to cp1252; OCR text has emoji/CJK
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

W = Path(sys.argv[1]).expanduser()
args = sys.argv[2:]
workers = 6
if "--workers" in args:
    i = args.index("--workers"); workers = int(args[i + 1]); args = args[:i] + args[i + 2:]
handles = [a.lstrip("@") for a in args]
HOME = Path.home()


def _which(name, *fallbacks):
    p = shutil.which(name)
    return p or next((str(f) for f in fallbacks if Path(f).exists()), name)


YTDLP = _which("yt-dlp", HOME / ".local/bin/yt-dlp.exe", HOME / ".local/bin/yt-dlp")
FFMPEG = _which("ffmpeg", "/opt/homebrew/bin/ffmpeg")
FFPROBE = _which("ffprobe", "/opt/homebrew/bin/ffprobe")
WHISPER = _which("whisper-cli", HOME / "tools/whisper/Release/whisper-cli.exe", "/opt/homebrew/bin/whisper-cli")
_SS = HOME / ".hermes/tools/social-scraper"
if os.environ.get("OCR_BIN"):
    OCR = [os.environ["OCR_BIN"]]
elif os.name != "nt" and (_SS / "ocr").exists():  # compiled ocr.swift (Apple Vision)
    OCR = [str(_SS / "ocr")]
else:  # RapidOCR stand-in with the same JSON contract; sys.executable must be the social-scraper venv python
    OCR = [sys.executable, str(Path(__file__).resolve().parent / "ocr.py")]
MODEL = next((str(m) for m in (_SS / "models/ggml-base.en.bin", HOME / ".hermes/cache/whisper/ggml-base.en.bin",
              HOME / ".hermes/cache/whisper/ggml-small.en.bin") if m.exists()), str(_SS / "models/ggml-base.en.bin"))
OUT = W / "hooks_raw.jsonl"
STRIPS = W / "hook_strips"; STRIPS.mkdir(parents=True, exist_ok=True)
TMP = W / "_tmp"; TMP.mkdir(exist_ok=True)
lock = Lock()
done = set()
if OUT.exists():
    for l in OUT.open():
        try: done.add(json.loads(l)["id"])
        except Exception: pass


def run(cmd, timeout=180):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def ocr(paths):
    r = run([*OCR, *map(str, paths)], timeout=600)
    res = {}
    for l in r.stdout.splitlines():
        try:
            d = json.loads(l); res[d["path"]] = d.get("lines", [])
        except Exception: pass
    return [res.get(str(p), []) for p in paths]


def whisper(video, d):
    wav = d / "a.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-i", str(video), "-t", "12", "-ac", "1", "-ar", "16000", str(wav)])
    if not wav.exists(): return [], ""
    run([WHISPER, "-m", MODEL, "-f", str(wav), "-oj", "-of", str(d / "w"), "-np", "-t", "2"], timeout=240)
    try:
        j = json.load(open(d / "w.json", encoding="utf-8"))
        segs = [{"s": s["offsets"]["from"] / 1000, "e": s["offsets"]["to"] / 1000, "t": s["text"].strip()} for s in j["transcription"]]
    except Exception:
        return [], ""
    return segs, " ".join(s["t"] for s in segs if s["s"] < 6).strip()


def process(handle, e):
    pid = e["id"]
    rec = {"id": pid, "handle": handle, "url": f"https://www.tiktok.com/@{handle}/video/{pid}",
           "views": e.get("view_count"), "likes": e.get("like_count"), "comments": e.get("comment_count"),
           "shares": e.get("repost_count"), "saves": e.get("save_count"), "duration": e.get("duration"),
           "timestamp": e.get("timestamp"), "caption": (e.get("description") or e.get("title") or "").strip(),
           "track": e.get("track")}
    d = Path(tempfile.mkdtemp(dir=TMP))
    try:
        r = run([YTDLP, "-q", "--no-warnings", "-S", "res:720,+size", "-o", str(d / "v.%(ext)s"), rec["url"]], timeout=240)
        vids = [p for p in d.glob("v.*") if p.suffix in (".mp4", ".webm", ".mov", ".mkv")]
        has_video = False
        if vids:
            pr = run([FFPROBE, "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(vids[0])])
            has_video = "video" in pr.stdout
        if has_video:
            v = vids[0]; frames = []
            for i, t in enumerate((0.2, 1.0, 2.5)):
                f = d / f"f{i}.jpg"
                run([FFMPEG, "-y", "-loglevel", "error", "-ss", str(t), "-i", str(v), "-frames:v", "1", "-vf", "scale=-2:960", str(f)])
                if f.exists(): frames.append(f)
            o = ocr(frames) if frames else []
            rec["ocr"] = {str(t): [x["t"] for x in lines] for t, lines in zip((0.2, 1.0, 2.5), o)}
            if frames:
                ins = []
                for f in frames: ins += ["-i", str(f)]
                run([FFMPEG, "-y", "-loglevel", "error", *ins, "-filter_complex",
                     "".join(f"[{i}:v]scale=-2:480[s{i}];" for i in range(len(frames))) + "".join(f"[s{i}]" for i in range(len(frames))) + f"hstack=inputs={len(frames)}",
                     str(STRIPS / f"{pid}.jpg")])
            segs, first6 = whisper(v, d)
            rec["kind"] = "video"; rec["speech_segments"] = segs; rec["spoken_hook"] = first6
        else:
            rec["kind"] = "slideshow" if list(d.glob("v.*")) else "unavailable"
            thumbs = e.get("thumbnails") or []
            if thumbs:
                f = d / "cover.jpg"
                try:
                    req = urllib.request.Request(thumbs[-1]["url"], headers={"User-Agent": "Mozilla/5.0"})
                    f.write_bytes(urllib.request.urlopen(req, timeout=30).read())
                    rec["ocr"] = {"cover": [x["t"] for x in ocr([f])[0]]}
                    shutil.copy(f, STRIPS / f"{pid}.jpg")
                except Exception as ex:
                    rec["cover_err"] = str(ex)[:100]
            if rec["kind"] == "unavailable": rec["dl_err"] = (r.stderr or "")[-200:]
    except Exception as ex:
        rec["kind"] = rec.get("kind", "error"); rec["err"] = str(ex)[:200]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    with lock:
        with OUT.open("a") as fh: fh.write(json.dumps(rec) + "\n")
        done.add(pid)
        print(f"[{len(done)}] @{handle} {pid} {rec.get('kind')} views={rec['views']} | {(rec.get('spoken_hook') or '')[:60]}", flush=True)


jobs = []
for h in handles:
    for e in json.load(open(W / f"list_{h}.json", encoding="utf-8"))["entries"]:
        if e["id"] not in done: jobs.append((h, e))
print(f"{len(jobs)} to do, {len(done)} already done", flush=True)
with ThreadPoolExecutor(workers) as ex:
    list(ex.map(lambda a: process(*a), jobs))
shutil.rmtree(TMP, ignore_errors=True)
print("ALL_DONE", len(done), flush=True)
