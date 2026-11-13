#!/usr/bin/env python3
"""Fallback IG lister: open the profile's /reels/ tab in the logged-in scraper profile and capture the
GraphQL/API responses the page itself makes while scrolling (looks like a normal visitor; works when
web_profile_info returns 429). Writes/merges list_ig_<handle>.json (same schema as ig_list_all.py).

Usage: ig_reels_capture.py <handle> <out_dir> [--scrolls 400] [--headful]
"""
import json, sys, time, random
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat  # noqa: E402
_plat.utf8_stdout()

PROFILE = _plat.IG_PROFILE  # ~/.hermes/tools/social-scraper/ig-profile (override: IG_PROFILE env)
handle = sys.argv[1].lstrip("@"); out = Path(sys.argv[2]).expanduser()
scrolls = int(sys.argv[sys.argv.index("--scrolls") + 1]) if "--scrolls" in sys.argv else 400
f = out / f"list_ig_{handle}.json"
state = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"handle": handle, "entries": []}
byid = {e["id"]: e for e in state["entries"]}


def best(c):
    return max(c, key=lambda x: (x.get("width") or 0) * (x.get("height") or 0))["url"] if c else None


def walk(o, acc):
    if isinstance(o, dict):
        if "code" in o and ("media_type" in o or "video_versions" in o or "play_count" in o) and isinstance(o.get("code"), str):
            acc.append(o)
        for v in o.values(): walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)


def norm(it):
    vv = it.get("video_versions") or []
    cap = it.get("caption")
    cap = (cap.get("text") if isinstance(cap, dict) else cap) or ""
    mt = it.get("media_type")
    return {"id": it["code"], "pk": it.get("pk"), "url": f"https://www.instagram.com/reel/{it['code']}/",
            "kind": {1: "photo", 2: "video", 8: "carousel"}.get(mt, "video"), "product_type": it.get("product_type"),
            "timestamp": it.get("taken_at"), "duration": it.get("video_duration"), "caption": cap,
            "views": it.get("play_count") or it.get("ig_play_count") or it.get("view_count") or 0,
            "likes": it.get("like_count") or 0, "comments": it.get("comment_count") or 0, "shares": it.get("reshare_count") or 0,
            "video_url": best(vv), "thumb_url": best((it.get("image_versions2") or {}).get("candidates") or [])}


def merge(e):
    old = byid.get(e["id"])
    if old:
        for k, v in e.items():
            if v not in (None, "", 0) and old.get(k) in (None, "", 0): old[k] = v
    else:
        byid[e["id"]] = e


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless="--headful" not in sys.argv,
                                               viewport={"width": 1280, "height": 1000},
                                               args=["--disable-blink-features=AutomationControlled"])
    _plat.need_login(ctx)
    pg = ctx.new_page()
    hits = {"n": 0}

    def on(r):
        u = r.url
        if ("graphql" in u or "/api/v1/" in u) and r.request.resource_type in ("xhr", "fetch"):
            try: j = r.json()
            except Exception: return
            acc = []; walk(j, acc)
            for it in acc: merge(norm(it))
            if acc: hits["n"] += 1
    pg.on("response", on)
    pg.goto(f"https://www.instagram.com/{handle}/reels/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(7)
    last, stale = 0, 0
    for i in range(scrolls):
        pg.mouse.move(640, 600); pg.mouse.wheel(0, 2500 + random.randint(0, 1500))
        time.sleep(1.6 + random.random() * 1.6)
        n = len(byid)
        if i % 10 == 0:
            print(f"[ig] scroll {i}: {n} reels (responses {hits['n']})", flush=True)
            f.write_text(json.dumps({**state, "entries": list(byid.values())}, ensure_ascii=False), encoding="utf-8")
        stale = stale + 1 if n == last else 0; last = n
        if stale >= 25:
            print("[ig] no new reels for 25 scrolls - end of feed or blocked", flush=True); break
    # also grab the html-embedded first page
    ctx.close()
state["entries"] = list(byid.values())
f.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
print("[ig] CAPTURE_DONE", len(state["entries"]), "with views:", sum(1 for e in state["entries"] if e["views"]), flush=True)
