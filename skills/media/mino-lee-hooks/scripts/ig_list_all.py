#!/usr/bin/env python3
"""List EVERY post of an Instagram profile (logged-in scraper profile) -> list_ig_<handle>.json.

Usage: ig_list_all.py <handle> <out_dir> [--max 2000]
Paginates /api/v1/feed/user/ 12 at a time with 1.5-3 s sleeps; stops cleanly on 401/429 and saves what it has
(re-run resumes from the saved max_id). Each entry: code, url, kind, timestamp, duration, caption, views, likes,
comments, video_url, thumb_url.
"""
import json, sys, time, random
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat  # noqa: E402
_plat.utf8_stdout()

PROFILE = _plat.IG_PROFILE  # ~/.hermes/tools/social-scraper/ig-profile (override: IG_PROFILE env)
HDR = {"x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest"}
handle = sys.argv[1].lstrip("@"); out = Path(sys.argv[2]).expanduser(); out.mkdir(parents=True, exist_ok=True)
mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 2000
f = out / f"list_ig_{handle}.json"
state = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"handle": handle, "entries": [], "next_max_id": None, "done": False}


def best(c):
    return max(c, key=lambda x: x.get("width", 0) * x.get("height", 0))["url"] if c else None


def norm(it):
    kind = {1: "photo", 2: "video", 8: "carousel"}[it["media_type"]]
    vv = it.get("video_versions") or []
    return {"id": it["code"], "pk": it.get("pk"), "url": f"https://www.instagram.com/reel/{it['code']}/", "kind": kind,
            "product_type": it.get("product_type"), "timestamp": it.get("taken_at"), "duration": it.get("video_duration"),
            "caption": ((it.get("caption") or {}).get("text") or ""),
            "views": it.get("play_count") or it.get("ig_play_count") or it.get("view_count") or 0,
            "likes": it.get("like_count") or 0, "comments": it.get("comment_count") or 0,
            "shares": it.get("reshare_count") or 0,
            "video_url": best(vv), "thumb_url": best(it.get("image_versions2", {}).get("candidates", []))}


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=True, args=["--disable-blink-features=AutomationControlled"])
    _plat.need_login(ctx)
    pg = ctx.new_page()
    pg.goto(f"https://www.instagram.com/{handle}/", wait_until="domcontentloaded", timeout=60000); time.sleep(4)
    u = pg.evaluate("async ([h,hd])=>{const r=await fetch('/api/v1/users/web_profile_info/?username='+h,{headers:hd});if(!r.ok)return {err:r.status};const u=(await r.json()).data.user;return {id:u.id,followers:u.edge_followed_by.count,posts:u.edge_owner_to_timeline_media.count}}", [handle, HDR])
    if u.get("err"): sys.exit(f"[ig] profile {u['err']}")
    state.update(user_id=u["id"], followers=u["followers"], total_posts=u["posts"])
    print(f"[ig] @{handle} followers={u['followers']} posts={u['posts']} have={len(state['entries'])}", flush=True)
    seen = {e["id"] for e in state["entries"]}
    while not state["done"] and len(state["entries"]) < mx:
        q = f"/api/v1/feed/user/{u['id']}/?count=12" + (f"&max_id={state['next_max_id']}" if state["next_max_id"] else "")
        r = pg.evaluate("async ([q,hd])=>{const f=await fetch(q,{headers:hd});if(!f.ok)return {err:f.status};return await f.json()}", [q, HDR])
        if r.get("err"):
            print(f"[ig] stopped: HTTP {r['err']} - saved {len(state['entries'])}; re-run later to resume", flush=True); break
        for it in r.get("items", []):
            e = norm(it)
            if e["id"] not in seen: state["entries"].append(e); seen.add(e["id"])
        state["next_max_id"] = r.get("next_max_id"); state["done"] = not r.get("more_available")
        f.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        print(f"[ig] {len(state['entries'])}/{u['posts']}", flush=True)
        time.sleep(1.5 + random.random() * 1.5)
    ctx.close()
f.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
print("[ig] LIST_DONE" if state["done"] else "[ig] LIST_PARTIAL", len(state["entries"]), flush=True)
