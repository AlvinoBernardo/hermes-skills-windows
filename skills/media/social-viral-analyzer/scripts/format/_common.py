"""Shared helpers for format-skill mode (Mac + Windows). Stdlib only, except where noted."""
import json
import os
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SS = HOME / ".hermes/tools/social-scraper"
IG_PROFILE = SS / "ig-profile"
SCRIPTS = Path(__file__).resolve().parent.parent  # social-viral-analyzer/scripts
IG_HEADERS = {"x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest"}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def venv_python():
    return str(SS / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python"))


def which(name, *fallbacks):
    p = shutil.which(name)
    if p:
        return p
    for f in fallbacks:
        if Path(f).exists():
            return str(f)
    return name


FFMPEG = which("ffmpeg", "/opt/homebrew/bin/ffmpeg")
FFPROBE = which("ffprobe", "/opt/homebrew/bin/ffprobe")
YTDLP = which("yt-dlp", HOME / ".local/bin/yt-dlp.exe", HOME / ".local/bin/yt-dlp")
WHISPER = which("whisper-cli", HOME / "tools/whisper/Release/whisper-cli.exe", "/opt/homebrew/bin/whisper-cli")
WHISPER_MODELS = [HOME / ".hermes/cache/whisper/ggml-small.en.bin", SS / "models/ggml-small.en.bin",
                  SS / "models/ggml-base.en.bin"]


def whisper_model():
    for m in WHISPER_MODELS:
        if m.exists():
            return str(m)
    sys.exit("no whisper model found in " + ", ".join(map(str, WHISPER_MODELS)))


def ocr_cmd():
    """Compiled Apple-Vision `ocr` binary if present (Mac), else the RapidOCR stand-in (same JSON contract)."""
    if os.environ.get("OCR_BIN"):
        return [os.environ["OCR_BIN"]]
    if (SS / "ocr").exists():
        return [str(SS / "ocr")]
    return [venv_python(), str(SCRIPTS / "ocr.py")]


def run(cmd, timeout=600, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, **kw)


def load(p, default=None):
    p = Path(p)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def save(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    tmp.replace(p)


def rolling_outlier(rows, key_views="views", key_time="timestamp", window=30):
    """outlier = views / median views of the `window` posts nearest in date (excluding itself)."""
    rs = sorted([r for r in rows if r.get(key_views) is not None and r.get(key_time)], key=lambda r: r[key_time])
    half = window // 2
    for i, r in enumerate(rs):
        lo, hi = max(0, i - half), min(len(rs), i + half + 1)
        if hi - lo < window + 1:  # pad at the edges so every post gets ~window neighbours
            lo, hi = max(0, min(lo, len(rs) - window - 1)), min(len(rs), max(hi, window + 1))
        nb = [x[key_views] for j, x in enumerate(rs[lo:hi], lo) if j != i and x[key_views] is not None]
        med = statistics.median(nb) if nb else None
        r["neighbour_median"] = med
        r["outlier"] = round(r[key_views] / med, 3) if med else None
    return rs
