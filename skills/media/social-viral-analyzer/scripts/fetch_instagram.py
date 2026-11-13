#!/usr/bin/env python3
"""Fetch the last N Instagram posts of a profile (logged-in profile required), rank, download top K.

Usage: fetch_instagram.py <handle> <out_dir> [--pool 60] [--top 30]
Requires a prior one-time login via ig_login.py (persistent profile at ~/.hermes/tools/social-scraper/ig-profile).
Ranking: reels by real play count. Photos/carousels expose no public views, so their views are ESTIMATED
as likes x (median views/likes ratio of this account's reels) and flagged views_estimated=true.
"""
import argparse, json, statistics, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path.home() / ".hermes/tools/social-scraper/ig-profile"
H = {"x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest"}

JS_FEED = """async ([h, pool, headers]) => {
  const r = await fetch('/api/v1/users/web_profile_info/?username=' + h, {headers});
  if (!r.ok) return {error: 'profile ' + r.status};
  const u = (await r.json()).data.user;
  let items = [], maxId = null, more = true, guard = 0;
  while (more && items.length < pool && guard++ < 12) {
    const q = '/api/v1/feed/user/' + u.id + '/?count=12' + (maxId ? '&max_id=' + maxId : '');
    const f = await fetch(q, {headers});
    if (!f.ok) return {error: 'feed ' + f.status, items, followers: u.edge_followed_by.count};
    const j = await f.json(); items = items.concat(j.items || []); more = j.more_available; maxId = j.next_max_id;
    await new Promise(s => setTimeout(s, 1200 + Math.random() * 800));
  }
  return {followers: u.edge_followed_by.count, items: items.slice(0, pool)};
}"""


def best(cands):
    return max(cands, key=lambda c: c.get("width", 0) * c.get("height", 0))["url"] if cands else None


def norm(it, handle):
    kind = {1: "photo", 2: "video", 8: "carousel"}[it["media_type"]]
    media = []
    for m in (it.get("carousel_media") or [it]):
        if m.get("video_versions"): media.append(("mp4", best(m["video_versions"])))
        else: media.append(("jpg", best(m.get("image_versions2", {}).get("candidates", []))))
    views = it.get("play_count") or it.get("ig_play_count") or it.get("view_count") or 0
    return {"platform": "instagram", "id": it["code"], "url": f"https://www.instagram.com/p/{it['code']}/",
            "kind": "video" if kind == "video" else "slideshow" if kind == "carousel" else "photo",
            "product_type": it.get("product_type"), "timestamp": it.get("taken_at"),
            "duration": it.get("video_duration"), "caption": ((it.get("caption") or {}).get("text") or ""),
            "views": views, "likes": it.get("like_count") or 0, "comments": it.get("comment_count") or 0,
            "shares": it.get("reshare_count") or 0, "saves": 0, "views_estimated": False,
            "sound": ((it.get("clips_metadata") or {}).get("music_info") or {}).get("music_asset_info", {}).get("title"),
            "_media": media}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handle"); ap.add_argument("out")
    ap.add_argument("--pool", type=int, default=60); ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()
    handle = a.handle.lstrip("@")
    out = Path(a.out).expanduser(); (out / "media").mkdir(parents=True, exist_ok=True)
    if not PROFILE.exists():
        sys.exit("[ig] no login profile - run ig_login.py first")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=True,
                                                   args=["--disable-blink-features=AutomationControlled"])
        if not any(c["name"] == "sessionid" for c in ctx.cookies("https://www.instagram.com")):
            sys.exit("[ig] session expired - run ig_login.py again")
        pg = ctx.new_page()
        pg.goto(f"https://www.instagram.com/{handle}/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        res = pg.evaluate(JS_FEED, [handle, a.pool, H])
        if res.get("error") and not res.get("items"):
            sys.exit(f"[ig] {res['error']}")
        posts = [norm(it, handle) for it in res["items"]]
        print(f"[ig] @{handle} listed {len(posts)} posts (followers={res['followers']})", flush=True)

        ratios = [x["views"] / x["likes"] for x in posts if x["views"] and x["likes"]]
        ratio = statistics.median(ratios) if ratios else None
        for x in posts:
            if not x["views"]:
                x["views_estimated"] = True
                x["views"] = int(x["likes"] * ratio) if ratio else x["likes"]
        ranked = sorted(posts, key=lambda x: x["views"], reverse=True)
        for i, x in enumerate(ranked, 1): x["view_rank"] = i
        top = ranked[: a.top]

        for x in top:
            d = out / "media" / f"{x['view_rank']:02d}_{x['id']}"; d.mkdir(exist_ok=True)
            vids = [m for m in x["_media"] if m[0] == "mp4"]
            for j, (ext, url) in enumerate(x["_media"], 1):
                if not url: continue
                name = "video.mp4" if (x["kind"] == "video" and ext == "mp4") else f"slide_{j:02d}.{ext}"
                if (d / name).exists(): continue
                r = ctx.request.get(url)
                if r.ok: (d / name).write_bytes(r.body())
            if x["kind"] == "photo": x["kind"] = "slideshow"
            x["slides"] = len(x["_media"]) if x["kind"] == "slideshow" else None
            x["dir"] = str(d.relative_to(out))
            print(f"[ig] #{x['view_rank']:02d} {x['kind']:9s} {x['views']:>10,} {'est.' if x['views_estimated'] else 'views'} {x['id']}", flush=True)
            time.sleep(1.5)
        ctx.close()

    for x in ranked: x.pop("_media", None)
    meta = {"platform": "instagram", "handle": handle, "followers": res["followers"], "fetched_at": int(time.time()),
            "pool_size": len(posts), "top_n": len(top), "rank_metric": "views (reel plays; non-reels estimated)",
            "views_per_like_ratio": ratio, "posts": ranked}
    (out / "manifest.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[ig] done -> {out/'manifest.json'}")


if __name__ == "__main__":
    main()
