"""Cross-platform lookups (Mac + Windows) shared by the scripts in this folder. Stdlib only.
Identical copies (plus ocr.py) live in mino-lee-hooks/scripts and yap-video-format/scripts - keep them in sync."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

WIN = os.name == "nt"
HOME = Path.home()
SS = HOME / ".hermes/tools/social-scraper"
IG_PROFILE = Path(os.environ.get("IG_PROFILE") or SS / "ig-profile")  # persistent logged-in Chromium profile
HERE = Path(__file__).resolve().parent


def utf8_stdout():
    """Windows pipes default to cp1252; OCR text / captions contain emoji and CJK."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


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
YTDLP = which("yt-dlp", HOME / ".local/bin/yt-dlp.exe", HOME / ".local/bin/yt-dlp",
              HOME / "AppData/Local/Microsoft/WinGet/Packages/yt-dlp.yt-dlp_Microsoft.Winget.Source_8wekyb3d8bbwe/yt-dlp.exe")
WHISPER = which("whisper-cli", HOME / "tools/whisper/Release/whisper-cli.exe", "/opt/homebrew/bin/whisper-cli")


def whisper_model(*names):
    """First existing ggml model; names default to small.en then base.en."""
    names = names or ("ggml-small.en.bin", "ggml-base.en.bin")
    for n in names:
        for d in (HOME / ".hermes/cache/whisper", SS / "models"):
            if (d / n).exists():
                return str(d / n)
    sys.exit("no whisper model (" + ", ".join(names) + ") in ~/.hermes/cache/whisper or " + str(SS / "models"))


def venv_python():
    return str(SS / (".venv/Scripts/python.exe" if WIN else ".venv/bin/python"))


def ocr_cmd(workdir=None):
    """Command prefix for the OCR helper (one JSON line per image on stdout).
    Order: $OCR_BIN, compiled Apple-Vision binary (<workdir>/tools/ocr or ~/.hermes/tools/social-scraper/ocr, Mac),
    else RapidOCR via ocr.py next to this file (Windows / Linux)."""
    if os.environ.get("OCR_BIN"):
        return [os.environ["OCR_BIN"]]
    for b in ([Path(workdir) / "tools/ocr"] if workdir else []) + [SS / "ocr"]:
        if b.exists() and not WIN:
            return [str(b)]
    py = venv_python() if Path(venv_python()).exists() else sys.executable
    return [py, str(HERE / "ocr.py")]


def sva_scripts():
    """Folder of social-viral-analyzer/scripts (fetch_tiktok.py etc.), wherever Hermes keeps skills on this OS."""
    cands = [HERE.parent.parent / "social-viral-analyzer/scripts"]
    for base in (os.environ.get("LOCALAPPDATA"), None):
        cands.append((Path(base) / "hermes" if base else HOME / ".hermes") / "skills/media/social-viral-analyzer/scripts")
    cands.append(HOME / ".hermes/skills/media/social-viral-analyzer/scripts")
    for c in cands:
        if (c / "fetch_tiktok.py").exists():
            return str(c)
    sys.exit("social-viral-analyzer/scripts/fetch_tiktok.py not found")


def run(cmd, timeout=180, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, **kw)


def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def need_login(ctx):
    if not any(c["name"] == "sessionid" for c in ctx.cookies("https://www.instagram.com")):
        ctx.close()
        sys.exit("[ig] not logged in - run social-viral-analyzer/scripts/ig_login.py (the user logs in in the visible window)")
