#!/usr/bin/env python3
"""Extract the hook (first ~6 s) of every TikTok in list_<handle>.json.

Per post: download video (<=720p), grab frames at 0.2/1.0/2.5 s -> OCR (Apple Vision on Mac, RapidOCR via ocr.py on Windows),
whisper the first 10 s (spoken hook), save a small 3-frame hook strip, delete the video.
Resumable: appends to hooks_raw.jsonl and skips ids already present.
Usage: extract_hooks.py <workdir> <handle> [<handle> ...] [--workers 6] [--platform tt|ig]  (ig reads list_ig_<handle>.json from ig_list_all.py, writes hooks_raw_ig.jsonl)
"""
import json, os, subprocess, sys, shutil, tempfile, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat  # noqa: E402
_plat.utf8_stdout()

W = Path(sys.argv[1]).expanduser()
args = sys.argv[2:]
workers = 6
platform = "tt"
if "--platform" in args:
    i = args.index("--platform"); platform = args[i + 1]; args = args[:i] + args[i + 2:]
if "--workers" in args:
    i = args.index("--workers"); workers = int(args[i + 1]); args = args[:i] + args[i + 2:]
handles = args
YTDLP, FFMPEG, FFPROBE, WHISPER = _plat.YTDLP, _plat.FFMPEG, _plat.FFPROBE, _plat.WHISPER
OCR = _plat.ocr_cmd(W)  # Mac: compiled Apple Vision binary; Windows/Linux: RapidOCR ocr.py in the social-scraper venv
MODEL = _plat.whisper_model("ggml-base.en.bin", "ggml-small.en.bin")
OUT = W / ("hooks_raw_ig.jsonl" if platform == "ig" else "hooks_raw.jsonl")
STRIPS = W / "hook_strips"; STRIPS.mkdir(exist_ok=True)
TMP = W / "_tmp"; TMP.mkdir(exist_ok=True)
lock = Lock()
done = set()
if OUT.exists():
    for l in OUT.open(encoding="utf-8"):
        try: done.add(json.loads(l)["id"])
        except Exception: pass


def run(cmd, timeout=180):
    return _plat.run(cmd, timeout=timeout)


def ocr(paths):
    r = run([*OCR, *map(str, paths)], timeout=300)
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
        j = json.loads((d / "w.json").read_text(encoding="utf-8", errors="replace"))
        segs = [{"s": s["offsets"]["from"] / 1000, "e": s["offsets"]["to"] / 1000, "t": s["text"].strip()} for s in j["transcription"]]
    except Exception:
        return [], ""
    first6 = " ".join(s["t"] for s in segs if s["s"] < 6).strip()
    return segs, first6


def process(handle, e):
    pid = e["id"]
    ig = platform == "ig"
    rec = {"id": pid, "handle": handle, "platform": platform,
           "url": e["url"] if ig else f"https://www.tiktok.com/@{handle}/video/{pid}",
           "views": e.get("views") if ig else e.get("view_count"), "likes": e.get("likes") if ig else e.get("like_count"),
           "comments": e.get("comments") if ig else e.get("comment_count"),
           "shares": e.get("shares") if ig else e.get("repost_count"), "saves": e.get("save_count"), "duration": e.get("duration"),
           "timestamp": e.get("timestamp"), "caption": (e.get("caption") or e.get("description") or e.get("title") or "").strip(),
           "track": e.get("track")}
    d = Path(tempfile.mkdtemp(dir=TMP))
    try:
        if ig:
            r = subprocess.CompletedProcess([], 0, "", "")
            if e.get("video_url"):
                try:
                    req = urllib.request.Request(e["video_url"], headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.instagram.com/"})
                    (d / "v.mp4").write_bytes(urllib.request.urlopen(req, timeout=120).read())
                except Exception as ex:
                    r = subprocess.CompletedProcess([], 1, "", str(ex))
            e = {**e, "thumbnails": [{"url": e.get("thumb_url")}] if e.get("thumb_url") else []}
        else:
            for attempt in range(2):  # TikTok sometimes fails once ("Unable to extract universal data"); a retry works
                r = run([YTDLP, "-q", "--no-warnings", "-S", "res:720,+size", "-o", str(d / "v.%(ext)s"), rec["url"]], timeout=240)
                if list(d.glob("v.*")): break
                time.sleep(4)
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
            rec["kind"] = ("slideshow" if e.get("kind") in ("carousel", "photo") else "unavailable") if ig else ("slideshow" if vids or list(d.glob("v.*")) else "unavailable")
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
        with OUT.open("a", encoding="utf-8") as fh: fh.write(json.dumps(rec) + "\n")
        done.add(pid)
        print(f"[{len(done)}] @{handle} {pid} {rec.get('kind')} views={rec['views']} | {(rec.get('spoken_hook') or '')[:60]}", flush=True)


jobs = []
for h in handles:
    for e in _plat.read_json(W / (f"list_ig_{h}.json" if platform == "ig" else f"list_{h}.json"))["entries"]:
        if platform == "ig" and not e.get("info_done"): continue  # wait for ig_media_info.py
        if e["id"] not in done: jobs.append((h, e))
print(f"{len(jobs)} to do, {len(done)} already done", flush=True)
with ThreadPoolExecutor(workers) as ex:
    list(ex.map(lambda a: process(*a), jobs))
print("ALL_DONE", len(done), flush=True)
