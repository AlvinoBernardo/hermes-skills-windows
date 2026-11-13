#!/usr/bin/env python3
"""Fill video_url / caption / timestamp / duration for IG entries via /api/v1/media/<pk>/info/ from inside the
logged-in scraper profile (one request every ~2-3.5 s). Resumable; stops cleanly on 401/429 (re-run later).
Usage: ig_media_info.py <handle> <out_dir> [--limit N]
"""
import json, sys, time, random
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat  # noqa: E402
_plat.utf8_stdout()

PROFILE = _plat.IG_PROFILE  # ~/.hermes/tools/social-scraper/ig-profile (override: IG_PROFILE env)
HDR = {"x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest"}
handle = sys.argv[1].lstrip("@"); out = Path(sys.argv[2]).expanduser()
limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10 ** 6
f = out / f"list_ig_{handle}.json"; st = json.loads(f.read_text(encoding="utf-8"))
todo = [e for e in st["entries"] if not e.get("info_done") and e.get("pk")][:limit]
print(f"[ig] {len(todo)} to fetch", flush=True)


def best(c):
    return max(c, key=lambda x: (x.get("width") or 0) * (x.get("height") or 0))["url"] if c else None


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=True, args=["--disable-blink-features=AutomationControlled"])
    _plat.need_login(ctx)
    pg = ctx.new_page(); pg.goto(f"https://www.instagram.com/{handle}/reels/", wait_until="domcontentloaded", timeout=60000); time.sleep(4)
    fails = 0
    for i, e in enumerate(todo):
        r = pg.evaluate("async ([pk,hd])=>{const f=await fetch('/api/v1/media/'+pk+'/info/',{headers:hd});if(!f.ok)return {err:f.status};return await f.json()}", [str(e["pk"]), HDR])
        if r.get("err"):
            fails += 1
            print(f"[ig] HTTP {r['err']} on {e['id']}", flush=True)
            if r["err"] in (401, 429) or fails >= 5:
                print("[ig] STOPPED (rate limit) - re-run later to resume", flush=True); break
            continue
        it = (r.get("items") or [{}])[0]
        cap = it.get("caption"); cap = (cap.get("text") if isinstance(cap, dict) else cap) or ""
        e.update(video_url=best(it.get("video_versions") or []) or e.get("video_url"), caption=cap or e.get("caption", ""),
                 timestamp=it.get("taken_at") or e.get("timestamp"), duration=it.get("video_duration") or e.get("duration"),
                 kind={1: "photo", 2: "video", 8: "carousel"}.get(it.get("media_type"), e.get("kind")),
                 views=it.get("play_count") or it.get("ig_play_count") or e.get("views"), likes=it.get("like_count") or e.get("likes"),
                 comments=it.get("comment_count") or e.get("comments"), info_done=True)
        if i % 10 == 0:
            f.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8"); print(f"[ig] info {i + 1}/{len(todo)}", flush=True)
        time.sleep(2.0 + random.random() * 1.5)
    ctx.close()
f.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
print("[ig] INFO_DONE", sum(1 for e in st["entries"] if e.get("info_done")), "/", len(st["entries"]), flush=True)
