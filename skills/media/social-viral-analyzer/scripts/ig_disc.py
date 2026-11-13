#!/usr/bin/env python3
"""IG keyword/tag discovery by opening pages in the logged-in scraper profile and capturing every JSON response.
Usage: ig_disc.py out.json "kw:learn japanese app" "tag:learnjapanese" ...
"""
import sys, json, time, os, urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
PROF = os.path.expanduser("~/.hermes/tools/social-scraper/ig-profile")
out = Path(sys.argv[1]); qs = sys.argv[2:]
rows = json.load(open(out, encoding="utf-8")) if out.exists() else {}
def walk(o, acc):
    if isinstance(o, dict):
        if "code" in o and "user" in o and ("play_count" in o or "like_count" in o or "taken_at" in o): acc.append(o)
        for v in o.values(): walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)
with sync_playwright() as p:
    c = p.chromium.launch_persistent_context(PROF, headless=True, viewport={"width": 1280, "height": 900})
    pg = c.new_page()
    for q in qs:
        got = []
        def on(r):
            try:
                if "json" in (r.headers.get("content-type") or "") or "graphql" in r.url or "/api/" in r.url:
                    walk(r.json(), got)
            except Exception: pass
        pg.on("response", on)
        kind, val = q.split(":", 1)
        url = (f"https://www.instagram.com/explore/search/keyword/?q={urllib.parse.quote(val)}" if kind == "kw"
               else f"https://www.instagram.com/explore/tags/{val}/")
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=60000); time.sleep(6)
            for _ in range(5):
                pg.mouse.move(640, 500); pg.mouse.wheel(0, 4000); time.sleep(2.5)
        except Exception as e: print("ERR", q, str(e)[:80])
        pg.remove_listener("response", on)
        n = 0
        for m in got:
            k = m["code"]; cap = ((m.get("caption") or {}).get("text") or "")[:300] if isinstance(m.get("caption"), dict) else ""
            u = m.get("user") or {}
            if k not in rows:
                rows[k] = {"code": k, "user": u.get("username"), "views": m.get("play_count") or m.get("ig_play_count") or m.get("view_count"),
                           "likes": m.get("like_count"), "comments": m.get("comment_count"), "ts": m.get("taken_at"),
                           "type": m.get("product_type") or m.get("media_type"), "caption": cap, "q": [q]}; n += 1
            else:
                rows[k]["q"] = sorted(set(rows[k]["q"] + [q]))
                for f in ("views", "likes", "ts"):
                    if rows[k].get(f) is None:
                        rows[k][f] = {"views": m.get("play_count") or m.get("ig_play_count"), "likes": m.get("like_count"), "ts": m.get("taken_at")}[f]
        print(q, "items", len(got), "new", n, flush=True); time.sleep(2)
    c.close()
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("total", len(rows))
