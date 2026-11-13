#!/usr/bin/env python3
"""Logged-out TikTok keyword discovery: open /discover/<slug> (and /tag/<tag>) pages, capture every /api/ JSON item.
Usage: tt_discover.py out.json slug1 tag:learnjapanese ...
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from fetch_tiktok import new_page
from playwright.sync_api import sync_playwright

out = Path(sys.argv[1]); slugs = sys.argv[2:]
rows = json.load(open(out, encoding="utf-8")) if out.exists() else {}

def walk(o, acc):
    if isinstance(o, dict):
        if "stats" in o and "author" in o and "desc" in o and "id" in o:
            acc.append(o)
        for v in o.values(): walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)

with sync_playwright() as p:
    b, pg = new_page(p)
    for s in slugs:
        got = []
        def on(r):
            if "/api/" in r.url or "tiktok.com" in r.url:
                try:
                    if "json" in (r.headers.get("content-type") or ""):
                        walk(r.json(), got)
                except Exception: pass
        pg.on("response", on)
        url = f"https://www.tiktok.com/tag/{s[4:]}" if s.startswith("tag:") else f"https://www.tiktok.com/discover/{s}"
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=60000); time.sleep(6)
            try:
                d = json.loads(pg.evaluate("document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__')?.textContent || '{}'"))
                walk(d, got)
            except Exception: pass
            for _ in range(6):
                pg.mouse.move(640, 500); pg.mouse.wheel(0, 5000); time.sleep(2.5)
        except Exception as e:
            print("ERR", s, str(e)[:100])
        pg.remove_listener("response", on)
        n = 0
        for it in got:
            a = it["author"] if isinstance(it["author"], dict) else {"uniqueId": it["author"]}
            st = it.get("stats") or {}
            k = str(it["id"])
            if k in rows: rows[k]["queries"] = sorted(set(rows[k]["queries"] + [s])); continue
            rows[k] = {"id": k, "author": a.get("uniqueId"), "followers": (it.get("authorStats") or {}).get("followerCount"),
                       "views": st.get("playCount"), "likes": st.get("diggCount"), "saves": int(st.get("collectCount") or 0),
                       "comments": st.get("commentCount"), "shares": st.get("shareCount"), "ts": it.get("createTime"),
                       "dur": (it.get("video") or {}).get("duration"), "desc": (it.get("desc") or "")[:300],
                       "music": (it.get("music") or {}).get("title"), "photo": bool(it.get("imagePost")), "queries": [s]}
            n += 1
        print(s, "items", len(got), "new", n, flush=True)
    b.close()
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("total", len(rows))
