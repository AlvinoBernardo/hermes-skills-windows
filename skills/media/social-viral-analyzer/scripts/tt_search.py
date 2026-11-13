"""TikTok video search via the logged-in scraper profile (run tt_login.py once first).
Usage: tt_search.py <out.json> "<query>" ["<query>" ...] [--scrolls 10] [--headed]
Captures /api/search/item/full/ only (ignores explore prefetch). Writes rows sorted by plays:
id,url,author,followers,plays,likes,shares,comments,saves,dur,created(date),music_title,music_author,music_original,music_id,desc,query"""
import json, sys, time, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
PROFILE = Path.home() / ".hermes/tools/social-scraper/tt-profile"
args = sys.argv[1:]; out = args.pop(0)
scrolls = 10; headed = False
if "--scrolls" in args: i = args.index("--scrolls"); scrolls = int(args[i+1]); del args[i:i+2]
if "--headed" in args: args.remove("--headed"); headed = True
rows = {}
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=not headed, viewport={"width": 1200, "height": 850},
                                               args=["--disable-blink-features=AutomationControlled"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    cur = {"q": None}
    def on(r):
        if "/api/search/item/full/" not in r.url: return
        try:
            for it in r.json().get("item_list") or []:
                m = it.get("music") or {}; s = it.get("stats") or {}; a = it.get("author") or {}
                rid = it["id"]
                if rid in rows: rows[rid]["query"] += " | " + cur["q"]; continue
                rows[rid] = dict(id=rid, url=f"https://www.tiktok.com/@{a.get('uniqueId')}/video/{rid}", author=a.get("uniqueId"),
                    followers=(it.get("authorStats") or {}).get("followerCount"), plays=s.get("playCount"), likes=s.get("diggCount"),
                    shares=s.get("shareCount"), comments=s.get("commentCount"), saves=int(s.get("collectCount") or 0),
                    dur=(it.get("video") or {}).get("duration"),
                    created=datetime.date.fromtimestamp(int(it.get("createTime") or 0)).isoformat(),
                    music_title=m.get("title"), music_author=m.get("authorName"), music_original=m.get("original"),
                    music_id=m.get("id"), desc=it.get("desc", ""), query=cur["q"])
        except Exception as e: print("parse err", e, flush=True)
    pg.on("response", on)
    for q in args:
        cur["q"] = q; n0 = len(rows)
        pg.goto("https://www.tiktok.com/search/video?q=" + q.replace(" ", "%20"), wait_until="domcontentloaded", timeout=60000)
        time.sleep(7)
        if pg.locator("text=Drag the slider").count(): print("CAPTCHA on", q, flush=True); time.sleep(20)
        for _ in range(scrolls): pg.mouse.move(600, 500); pg.mouse.wheel(0, 5000); time.sleep(2.2)
        print(f"{q!r}: +{len(rows)-n0} (total {len(rows)})", flush=True); time.sleep(2)
    ctx.close()
lst = sorted(rows.values(), key=lambda r: -(r["plays"] or 0))
json.dump(lst, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", out, len(lst))
