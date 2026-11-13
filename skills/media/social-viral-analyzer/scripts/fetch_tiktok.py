#!/usr/bin/env python3
"""Fetch the last N TikTok posts of a profile, rank by views, download the top K.

Usage: fetch_tiktok.py <handle> <out_dir> [--pool 60] [--top 30]
Writes <out_dir>/manifest.json and <out_dir>/media/<rank>_<id>/ (video.mp4 or slide_XX.jpg + audio.m4a).
Run with the social-scraper venv python (needs playwright); yt-dlp must be on PATH.
"""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
YTDLP = shutil.which("yt-dlp") or next((str(c) for c in (Path.home() / ".local/bin/yt-dlp.exe", Path.home() / ".local/bin/yt-dlp") if c.exists()), "yt-dlp")


def new_page(p):
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    return b, b.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US").new_page()


def get_secuid(pg, handle):
    pg.goto(f"https://www.tiktok.com/@{handle}", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    return pg.evaluate("""()=>{const d=JSON.parse(document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__').textContent);
      const u=d.__DEFAULT_SCOPE__['webapp.user-detail'].userInfo; return {secUid:u.user.secUid, followers:u.stats.followerCount, nick:u.user.nickname}}""")


def page_capture(pg, handle):
    items = {}
    def on(r):
        if "/api/post/item_list" in r.url:
            try:
                for it in r.json().get("itemList", []): items[it["id"]] = it
            except Exception: pass
    pg.on("response", on)
    pg.goto(f"https://www.tiktok.com/@{handle}", wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    for _ in range(12):
        pg.mouse.move(640, 500); pg.mouse.wheel(0, 5000); time.sleep(3)
    pg.remove_listener("response", on)
    out = []
    for it in items.values():
        s = it.get("stats", {})
        out.append({"id": it["id"], "timestamp": it.get("createTime"), "duration": (it.get("video") or {}).get("duration"),
                    "description": it.get("desc"), "view_count": s.get("playCount"), "like_count": s.get("diggCount"),
                    "comment_count": s.get("commentCount"), "repost_count": s.get("shareCount"),
                    "save_count": int(s.get("collectCount") or 0), "track": (it.get("music") or {}).get("title")})
    return out


def slide_urls(pg, url):
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    srcs = pg.eval_on_selector_all("img", "e=>e.filter(i=>i.naturalWidth>500 && i.src.includes('photomode')).map(i=>i.src)")
    seen, out = set(), []
    for s in srcs:
        key = s.split("~")[0].split("?")[0]
        if key not in seen:
            seen.add(key); out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handle"); ap.add_argument("out")
    ap.add_argument("--pool", type=int, default=60); ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()
    handle = a.handle.lstrip("@")
    out = Path(a.out).expanduser(); (out / "media").mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        b, pg = new_page(p)
        prof = get_secuid(pg, handle)
        print(f"[tt] @{handle} secUid ok, followers={prof['followers']}", flush=True)
        r = subprocess.run([YTDLP, "--flat-playlist", "--playlist-end", str(a.pool), "-J", f"tiktokuser:{prof['secUid']}"],
                           capture_output=True, text=True, timeout=300)
        entries = (json.loads(r.stdout) or {}).get("entries", []) if r.stdout.strip() not in ("", "null") else []
        if not entries:
            # Fallback (account has embedding disabled): capture the profile page's own item_list responses.
            print(f"[tt] yt-dlp listing failed ({r.stderr.strip().splitlines()[-1][:120] if r.stderr.strip() else '?'}) - falling back to page capture", flush=True)
            entries = page_capture(pg, handle)
            if not entries:
                sys.exit("[tt] listing failed on both methods")
            print(f"[tt] page capture got {len(entries)} posts (TikTok usually caps this at ~25-35)", flush=True)
        posts = []
        for e in entries:
            posts.append({"platform": "tiktok", "id": e["id"], "url": f"https://www.tiktok.com/@{handle}/video/{e['id']}",
                          "timestamp": e.get("timestamp"), "duration": e.get("duration"), "caption": e.get("description") or e.get("title") or "",
                          "views": e.get("view_count") or 0, "likes": e.get("like_count") or 0, "comments": e.get("comment_count") or 0,
                          "shares": e.get("repost_count") or 0, "saves": e.get("save_count") or 0, "sound": e.get("track")})
        print(f"[tt] listed {len(posts)} posts", flush=True)
        ranked = sorted(posts, key=lambda x: x["views"], reverse=True)
        for i, x in enumerate(ranked, 1): x["view_rank"] = i
        top = ranked[: a.top]

        for x in top:
            d = out / "media" / f"{x['view_rank']:02d}_{x['id']}"; d.mkdir(exist_ok=True)
            if any(d.glob("video.*")) or any(d.glob("slide_*")):
                x["kind"] = "video" if any(d.glob("video.*")) else "slideshow"; continue
            subprocess.run([YTDLP, "-q", "--no-warnings", "-o", str(d / "dl.%(ext)s"), x["url"]], timeout=300)
            got = list(d.glob("dl.*"))
            vid = [g for g in got if g.suffix in (".mp4", ".webm", ".mov")]
            if vid:
                vid[0].rename(d / f"video{vid[0].suffix}"); x["kind"] = "video"
            else:
                for g in got: g.rename(d / f"audio{g.suffix}")
                x["kind"] = "slideshow"
                urls = slide_urls(pg, x["url"].replace("/video/", "/photo/"))
                for j, u in enumerate(urls, 1):
                    resp = pg.request.get(u, headers={"Referer": "https://www.tiktok.com/"})
                    if resp.ok: (d / f"slide_{j:02d}.jpg").write_bytes(resp.body())
                x["slides"] = len(urls)
            x["dir"] = str(d.relative_to(out))
            print(f"[tt] #{x['view_rank']:02d} {x['kind']:9s} {x['views']:>10,} views  {x['id']}", flush=True)
            time.sleep(1.5)
        b.close()

    meta = {"platform": "tiktok", "handle": handle, "followers": prof["followers"], "fetched_at": int(time.time()),
            "pool_size": len(posts), "top_n": len(top), "rank_metric": "views", "posts": ranked}
    (out / "manifest.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[tt] done -> {out/'manifest.json'}")


if __name__ == "__main__":
    main()
