"""One-time TikTok login into the scraper's dedicated browser profile (for TikTok SEARCH, which is blocked logged-out).
Usage: tt_login.py [timeout_seconds]   (social-scraper venv python)
Opens a VISIBLE window; the user logs in, then solves any slider CAPTCHA on the search page.
Prints LOGGED_IN, then SEARCH_OK once a search returns videos. Exit 0 on SEARCH_OK."""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path.home() / ".hermes/tools/social-scraper/tt-profile"
timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 900
got = {"n": 0}
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=False,
        viewport={"width": 1200, "height": 850}, args=["--disable-blink-features=AutomationControlled"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    def on(r):
        if "/api/search/" in r.url and "item" in r.url:
            try: got["n"] += len(r.json().get("item_list") or r.json().get("data") or [])
            except Exception: pass
    pg.on("response", on)
    pg.bring_to_front()
    pg.goto("https://www.tiktok.com/login")
    t0 = time.time(); logged = False
    while time.time() - t0 < timeout:
        if not logged and any(c["name"] == "sessionid" and c["value"] for c in ctx.cookies("https://www.tiktok.com")):
            logged = True; print("LOGGED_IN", flush=True); time.sleep(2)
            pg.goto("https://www.tiktok.com/search/video?q=black%20clover%20edit")
        if logged and got["n"] > 0:
            print("SEARCH_OK", got["n"], flush=True); time.sleep(3); ctx.close(); sys.exit(0)
        time.sleep(2)
    print("TIMEOUT logged=%s" % logged, flush=True); ctx.close(); sys.exit(1)
