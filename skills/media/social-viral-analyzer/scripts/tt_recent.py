#!/usr/bin/env python3
"""List the most recent N posts of TikTok handles with views + dates.
Usage: tt_recent.py <outdir> --n 40 handle1 handle2 ...
Writes <outdir>/acc_<handle>.json {handle, profile, entries:[{id,ts,views,likes,comments,shares,saves,dur,desc,track,url}]}
"""
import sys, json, subprocess, time, argparse
from pathlib import Path
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from fetch_tiktok import new_page, get_secuid, YTDLP
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--n", type=int, default=40); ap.add_argument("handles", nargs="+")
a = ap.parse_args()
O = Path(a.out); O.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b, pg = new_page(p)
    for h in a.handles:
        h = h.strip().lstrip("@")
        f = O / f"acc_{h}.json"
        if f.exists():
            print("skip", h); continue
        try:
            prof = get_secuid(pg, h)
        except Exception as e:
            print("NOACCOUNT", h, str(e)[:80], flush=True)
            json.dump({"handle": h, "error": "noaccount"}, open(f, "w", encoding="utf-8")); continue
        r = subprocess.run([YTDLP, "--flat-playlist", "-J", "--playlist-end", str(a.n), f"tiktokuser:{prof['secUid']}"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        try:
            d = json.loads(r.stdout) if r.stdout.strip() not in ("", "null") else {}
        except Exception:
            d = {}
        ents = []
        for e in [e for e in (d.get("entries") or []) if e]:
            ents.append({"id": e.get("id"), "ts": e.get("timestamp"), "views": e.get("view_count"), "likes": e.get("like_count"),
                         "comments": e.get("comment_count"), "shares": e.get("repost_count"), "saves": e.get("save_count"),
                         "dur": e.get("duration"), "desc": (e.get("description") or e.get("title") or "")[:400],
                         "track": e.get("track"), "url": e.get("url") or e.get("webpage_url")})
        json.dump({"handle": h, "profile": prof, "entries": ents}, open(f, "w", encoding="utf-8"), ensure_ascii=False)
        print("OK", h, prof.get("followers"), prof.get("nick"), len(ents), r.stderr[-150:].replace("\n", " ") if not ents else "", flush=True)
    b.close()
