#!/usr/bin/env python3
"""List EVERY reel of an Instagram creator (logged-in scraper profile required).

Usage: ig_reels_capture.py <handle> <workdir> [--scrolls 80] [--headed]
Writes <workdir>/list_ig_<handle>.json = {"profile": {...}, "entries": [...]}, one entry per reel:
  code, pk, views (play_count), likes, comments, timestamp, duration, caption, owner, coauthors, music, product_type
Method: opens the /reels/ tab in the persistent ig-profile and pages /api/v1/clips/user/ from inside the page
(same-origin, uses the session's csrftoken). `--scrolls` caps the number of 12-reel pages. Falls back to
capturing the API responses the tab itself fires while scrolling. Resumable: entries already in the file are kept.
The /reels/ tab also returns other creators' reels (tagged/collab/suggested): run ig_owner_pass.py afterwards.
Stops on 401/429 (rate limit) and keeps what it has.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import IG_HEADERS, IG_PROFILE, load, save  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

JS_PAGE = """async ([uid, maxId, headers]) => {
  const csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
  const body = new URLSearchParams({target_user_id: uid, page_size: '12', include_feed_video: 'true'});
  if (maxId) body.set('max_id', maxId);
  const r = await fetch('/api/v1/clips/user/', {method: 'POST', body,
      headers: {...headers, 'x-csrftoken': csrf, 'content-type': 'application/x-www-form-urlencoded'}});
  if (!r.ok) return {status: r.status};
  const j = await r.json();
  return {status: 200, items: (j.items || []).map(x => x.media), more: j.paging_info && j.paging_info.more_available,
          maxId: j.paging_info && j.paging_info.max_id};
}"""

JS_PROFILE = """async ([h, headers]) => {
  const r = await fetch('/api/v1/users/web_profile_info/?username=' + h, {headers});
  if (!r.ok) return {status: r.status};
  const u = (await r.json()).data.user;
  if (!u) return {status: 404};
  return {status: 200, id: u.id, followers: u.edge_followed_by.count, posts: u.edge_owner_to_timeline_media.count,
          full_name: u.full_name, bio: u.biography};
}"""


def norm(m):
    cm = m.get("clips_metadata") or {}
    mi = (cm.get("music_info") or {}).get("music_asset_info") or {}
    osi = cm.get("original_sound_info") or {}
    music = ({"type": "licensed", "title": mi.get("title"), "artist": mi.get("display_artist")} if mi else
             {"type": "original", "title": osi.get("original_audio_title"),
              "artist": (osi.get("ig_artist") or {}).get("username")} if osi else None)
    return {"code": m.get("code"), "pk": str(m.get("pk") or m.get("id", "").split("_")[0]),
            "views": m.get("play_count") or m.get("ig_play_count") or m.get("view_count"),
            "likes": m.get("like_count"), "comments": m.get("comment_count"), "timestamp": m.get("taken_at"),
            "duration": m.get("video_duration"), "caption": ((m.get("caption") or {}).get("text") or ""),
            "owner": (m.get("user") or m.get("owner") or {}).get("username"),
            "coauthors": [c.get("username") for c in (m.get("coauthor_producers") or [])],
            "music": music, "product_type": m.get("product_type")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handle"); ap.add_argument("workdir")
    ap.add_argument("--scrolls", type=int, default=80); ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    h = a.handle.lstrip("@"); W = Path(a.workdir).expanduser(); W.mkdir(parents=True, exist_ok=True)
    out = W / f"list_ig_{h}.json"
    old = load(out, {"entries": []})
    ents = {e["code"]: e for e in old.get("entries", []) if e.get("code")}
    if not IG_PROFILE.exists():
        sys.exit("[ig] no login profile - run ig_login.py first")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(IG_PROFILE), headless=not a.headed,
                                                   args=["--disable-blink-features=AutomationControlled"])
        if not any(c["name"] == "sessionid" and c["value"] for c in ctx.cookies("https://www.instagram.com")):
            ctx.close(); sys.exit("[ig] session expired - run ig_login.py again")
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        captured = []

        def on(r):
            if "/api/v1/clips/user" in r.url or "graphql/query" in r.url:
                try:
                    j = r.json()
                    for it in j.get("items", []):
                        if it.get("media"): captured.append(it["media"])
                    for e in (((j.get("data") or {}).get("xdt_api__v1__clips__user__connection_v2") or {})
                              .get("edges") or []):
                        if (e.get("node") or {}).get("media"): captured.append(e["node"]["media"])
                except Exception:
                    pass
        pg.on("response", on)
        pg.goto(f"https://www.instagram.com/{h}/reels/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        prof = pg.evaluate(JS_PROFILE, [h, IG_HEADERS])
        if prof.get("status") != 200:
            ctx.close(); sys.exit(f"[ig] profile lookup failed: HTTP {prof.get('status')} (404 = no such handle)")
        print(f"[ig] @{h} {prof.get('full_name')!r} followers={prof['followers']} posts={prof['posts']}", flush=True)

        max_id, pages, status = None, 0, 200
        while pages < a.scrolls:
            r = pg.evaluate(JS_PAGE, [prof["id"], max_id, IG_HEADERS])
            status = r.get("status")
            if status != 200:
                print(f"[ig] clips API HTTP {status} - {'rate limited, stopping' if status in (401, 429) else 'falling back to scroll capture'}", flush=True)
                break
            for m in r["items"]:
                e = norm(m); ents[e["code"]] = e
            pages += 1
            print(f"[ig] page {pages}: +{len(r['items'])} (total {len(ents)})", flush=True)
            if not r.get("more") or not r.get("maxId"):
                break
            max_id = r["maxId"]
            time.sleep(1.5 + (pages % 3) * 0.4)

        if status not in (200, 401, 429):  # fallback: scroll the tab and keep what it loads
            for i in range(a.scrolls):
                n = len(captured)
                pg.mouse.wheel(0, 6000); time.sleep(2.5)
                if i > 5 and len(captured) == n:
                    break
            for m in captured:
                e = norm(m); ents[e["code"]] = e
            print(f"[ig] scroll capture total {len(ents)}", flush=True)
        ctx.close()

    rows = sorted(ents.values(), key=lambda e: e.get("timestamp") or 0, reverse=True)
    save(out, {"profile": {k: prof.get(k) for k in ("id", "followers", "posts", "full_name", "bio")},
               "handle": h, "fetched_at": int(time.time()), "entries": rows})
    print(f"[ig] wrote {out} ({len(rows)} reels)")


if __name__ == "__main__":
    main()
