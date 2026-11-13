#!/usr/bin/env python3
"""List EVERY post of a TikTok account (no pool limit) with views/likes/saves/captions.

Usage: $PY list_all_tiktok.py <handle> <workdir>   -> <workdir>/list_<handle>.json  {profile, entries}
Run with the social-scraper venv python; yt-dlp on PATH. ~1-3 min for ~550 posts.
Run several handles sequentially in one terminal call (or one background job) - not with '&'.
"""
import sys, json, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_tiktok import new_page, get_secuid, YTDLP
from playwright.sync_api import sync_playwright

h = sys.argv[1].lstrip("@")
W = Path(sys.argv[2]).expanduser(); W.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b, pg = new_page(p)
    prof = get_secuid(pg, h); b.close()
print(h, prof, flush=True)
r = subprocess.run([YTDLP, "--flat-playlist", "-J", f"tiktokuser:{prof['secUid']}"], capture_output=True, text=True, timeout=900)
d = json.loads(r.stdout) if r.stdout.strip() not in ("", "null") else {}
ents = d.get("entries", [])
print("entries", len(ents), r.stderr[-300:])
json.dump({"profile": prof, "entries": ents}, open(W / f"list_{h}.json", "w", encoding="utf-8"))
