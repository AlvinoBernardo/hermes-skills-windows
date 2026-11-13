"""One-time Instagram login into the scraper's dedicated browser profile.
Usage: ig_login.py [timeout_seconds]   (run with the social-scraper venv python)
Opens a visible window on the IG login page; the user logs in. Prints LOGGED_IN and exits 0
once a `sessionid` cookie exists, TIMEOUT / exit 1 otherwise."""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path.home() / ".hermes/tools/social-scraper/ig-profile"
timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 600
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=False,
        viewport={"width": 1100, "height": 850}, args=["--disable-blink-features=AutomationControlled"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.goto("https://www.instagram.com/accounts/login/")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if any(c["name"] == "sessionid" and c["value"] for c in ctx.cookies("https://www.instagram.com")):
            print("LOGGED_IN", flush=True); time.sleep(3); ctx.close(); sys.exit(0)
        time.sleep(2)
    print("TIMEOUT", flush=True); ctx.close(); sys.exit(1)
