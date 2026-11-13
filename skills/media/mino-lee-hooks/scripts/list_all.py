"""Usage (run from the workdir): list_all.py <handle>  -> list_<handle>.json (secUid via playwright + yt-dlp flat playlist).
Run with the social-scraper venv python (needs playwright)."""
import sys, json, subprocess, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat
_plat.utf8_stdout()
sys.path.insert(0, _plat.sva_scripts())
from fetch_tiktok import new_page, get_secuid
YTDLP = _plat.YTDLP
from playwright.sync_api import sync_playwright
h = sys.argv[1]
with sync_playwright() as p:
    b, pg = new_page(p)
    prof = get_secuid(pg, h); b.close()
print(h, prof, flush=True)
r = _plat.run([YTDLP, "--flat-playlist", "-J", f"tiktokuser:{prof['secUid']}"], timeout=900)
d = json.loads(r.stdout) if r.stdout.strip() not in ("", "null") else {}
ents = d.get("entries", [])
print("entries", len(ents), r.stderr[-300:])
json.dump({"profile": prof, "entries": ents}, open(f"list_{h}.json", "w", encoding="utf-8"), ensure_ascii=False)
