#!/usr/bin/env python3
"""Capture newest @minolee.mp4 reels from the /reels/ tab, then per reel: /api/v1/media/<pk>/info/
(music tag, owner, date, video url) and download the audio straight away (CDN urls expire).
Usage: fetch90.py <out_dir> [--want 110] [--scrolls 25]
"""
import json, sys, time, random, subprocess, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path.home() / ".hermes/tools/social-scraper/ig-profile"
HDR = {"x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest"}
HANDLE = "minolee.mp4"
out = Path(sys.argv[1]).expanduser(); out.mkdir(parents=True, exist_ok=True)
(out / "audio").mkdir(exist_ok=True)
want = int(sys.argv[sys.argv.index("--want") + 1]) if "--want" in sys.argv else 110
scrolls = int(sys.argv[sys.argv.index("--scrolls") + 1]) if "--scrolls" in sys.argv else 25
f = out / "reels.json"
state = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def walk(o, acc):
    if isinstance(o, dict):
        if isinstance(o.get("code"), str) and ("media_type" in o or "video_versions" in o or "play_count" in o) and o.get("pk"):
            acc.append(o)
        for v in o.values(): walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)


def best(c):
    return max(c, key=lambda x: (x.get("width") or 0) * (x.get("height") or 0))["url"] if c else None


order = []
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=True, viewport={"width": 1280, "height": 1000},
                                               args=["--disable-blink-features=AutomationControlled"])
    pg = ctx.new_page()

    def on(r):
        u = r.url
        if ("graphql" in u or "/api/v1/" in u) and r.request.resource_type in ("xhr", "fetch"):
            try: j = r.json()
            except Exception: return
            acc = []; walk(j, acc)
            for it in acc:
                code = it["code"]
                if code not in state:
                    state[code] = {"id": code, "pk": str(it["pk"]).split("_")[0], "url": f"https://www.instagram.com/reel/{code}/",
                                   "tab_views": it.get("play_count") or it.get("view_count") or 0}
                    order.append(code)
    pg.on("response", on)
    pg.goto(f"https://www.instagram.com/{HANDLE}/reels/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(7)
    if "accounts/login" in pg.url:
        print("NOT_LOGGED_IN", flush=True); ctx.close(); sys.exit(2)
    stale = 0
    for i in range(scrolls * 10):
        pg.mouse.move(640, 600); pg.mouse.wheel(0, 2500 + random.randint(0, 1500))
        time.sleep(1.6 + random.random() * 1.4)
        n = len(state)
        print(f"[cap] scroll {i}: {n}", flush=True) if i % 5 == 0 else None
        if n >= want: break
        stale = stale + 1 if i and n == prev else 0
        prev = n
        if stale >= 20: print("[cap] stalled", flush=True); break
    f.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    print("[cap] captured", len(state), flush=True)

    todo = [k for k in state if not state[k].get("info_done")]
    fails = 0
    for i, code in enumerate(todo):
        e = state[code]
        r = pg.evaluate("async ([pk,hd])=>{const f=await fetch('/api/v1/media/'+pk+'/info/',{headers:hd});if(!f.ok)return {err:f.status};return await f.json()}", [e["pk"], HDR])
        if r.get("err"):
            fails += 1; print(f"[info] HTTP {r['err']} {code}", flush=True)
            if r["err"] in (401, 429) or fails >= 5: print("[info] STOPPED rate limit", flush=True); break
            continue
        it = (r.get("items") or [{}])[0]
        cap = it.get("caption"); cap = (cap.get("text") if isinstance(cap, dict) else cap) or ""
        cm = it.get("clips_metadata") or {}
        mi = (cm.get("music_info") or {}).get("music_asset_info") or {}
        osi = cm.get("original_sound_info") or {}
        e.update(owner=(it.get("user") or {}).get("username"),
                 coauthors=[c.get("username") for c in (it.get("coauthor_producers") or [])],
                 timestamp=it.get("taken_at"), duration=it.get("video_duration"), caption=cap,
                 views=it.get("play_count") or it.get("ig_play_count") or e.get("tab_views"),
                 likes=it.get("like_count"), media_type=it.get("media_type"),
                 pinned=bool(it.get("timeline_pinned_user_ids") or it.get("clips_tab_pinned_user_ids")),
                 ig_music_title=mi.get("title"), ig_music_artist=mi.get("display_artist"),
                 ig_original_audio=(osi.get("original_audio_title") if osi else None),
                 ig_original_audio_owner=((osi.get("ig_artist") or {}).get("username") if osi else None),
                 audio_type=cm.get("audio_type"),
                 video_url=best(it.get("video_versions") or []), info_done=True)
        # download audio now
        a = out / "audio" / f"{code}.m4a"
        if e["video_url"] and not a.exists():
            try:
                req = urllib.request.Request(e["video_url"], headers={"Referer": "https://www.instagram.com/", "User-Agent": "Mozilla/5.0"})
                tmp = out / "audio" / f"{code}.mp4"
                tmp.write_bytes(urllib.request.urlopen(req, timeout=60).read())
                subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(tmp), "-vn", "-c:a", "copy", str(a)], check=False)
                tmp.unlink(missing_ok=True)
            except Exception as ex:
                print("[dl] fail", code, ex, flush=True)
        e["audio"] = str(a) if a.exists() else None
        if i % 10 == 0:
            f.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8"); print(f"[info] {i+1}/{len(todo)}", flush=True)
        time.sleep(2.0 + random.random() * 1.5)
    ctx.close()
f.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
print("DONE", len(state), "info:", sum(1 for v in state.values() if v.get("info_done")),
      "audio:", sum(1 for v in state.values() if v.get("audio")), flush=True)
