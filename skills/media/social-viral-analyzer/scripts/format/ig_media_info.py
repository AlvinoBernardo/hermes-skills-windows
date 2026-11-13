#!/usr/bin/env python3
"""Per-reel media info + fresh MP4 download for every entry in list_ig_<handle>.json.

Usage: ig_media_info.py <handle> <workdir> [--limit N] [--no-video]
For each reel: GET /api/v1/media/<pk>/info/ inside the logged-in ig-profile, save the raw item to
media_info/<code>.json, then download video_versions[0] RIGHT AWAY to media/<code>.mp4 (IG CDN URLs expire
after ~2 days, so never store the URL for later). ~10 reels/min (3-5 s sleeps). Resumable: skips codes whose
media_info json AND mp4 exist. Stops on 401/429 and prints how many are left - rerun later.
Shares the profile lock with ig_reels_capture.py: run them one after another, not in parallel.
"""
import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import IG_HEADERS, IG_PROFILE, load, save  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

JS_INFO = """async ([pk, headers]) => {
  const r = await fetch('/api/v1/media/' + pk + '/info/', {headers});
  if (!r.ok) return {status: r.status};
  const j = await r.json();
  return {status: 200, item: (j.items || [])[0] || null};
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handle"); ap.add_argument("workdir")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args()
    h = a.handle.lstrip("@"); W = Path(a.workdir).expanduser()
    lst = load(W / f"list_ig_{h}.json")
    if not lst:
        sys.exit(f"[ig] {W / f'list_ig_{h}.json'} missing - run ig_reels_capture.py first")
    (W / "media_info").mkdir(parents=True, exist_ok=True); (W / "media").mkdir(exist_ok=True)

    def done(e):
        return (W / "media_info" / f"{e['code']}.json").exists() and (a.no_video or (W / "media" / f"{e['code']}.mp4").exists())
    todo = [e for e in lst["entries"] if not done(e)]
    if a.limit:
        todo = todo[: a.limit]
    print(f"[ig] {len(todo)} to do, {len(lst['entries']) - len(todo)} already done", flush=True)
    if not todo:
        return

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(IG_PROFILE), headless=True,
                                                   args=["--disable-blink-features=AutomationControlled"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000); time.sleep(3)
        n_ok = 0
        for i, e in enumerate(todo, 1):
            r = pg.evaluate(JS_INFO, [e["pk"], IG_HEADERS])
            if r.get("status") in (401, 429):
                print(f"[ig] HTTP {r['status']} - rate limited after {n_ok}; {len(todo) - i + 1} left, rerun later", flush=True)
                break
            it = r.get("item")
            if r.get("status") != 200 or not it:
                print(f"[ig] {e['code']}: HTTP {r.get('status')} / no item - skipped", flush=True)
                continue
            save(W / "media_info" / f"{e['code']}.json", it)
            got = "info"
            vv = it.get("video_versions") or []
            if vv and not a.no_video:
                url = max(vv, key=lambda v: v.get("width", 0) * v.get("height", 0))["url"]
                resp = ctx.request.get(url, timeout=120000)
                if resp.ok:
                    (W / "media" / f"{e['code']}.mp4").write_bytes(resp.body()); got = "info+mp4"
                else:
                    got = f"info (mp4 HTTP {resp.status})"
            n_ok += 1
            print(f"[ig] {i}/{len(todo)} {e['code']} {got}", flush=True)
            time.sleep(random.uniform(3, 5))
        ctx.close()


if __name__ == "__main__":
    main()
