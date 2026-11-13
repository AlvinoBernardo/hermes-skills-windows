import json, time, random, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plat
_plat.utf8_stdout()
# Usage: ig_owner_pass.py <workdir> <handle>   (writes owners.json; needs the logged-in scraper profile)
P = _plat.IG_PROFILE; W = Path(sys.argv[1]).expanduser(); H = sys.argv[2].lstrip("@")
HDR = {"x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest"}
st = _plat.read_json(W/f"list_ig_{H}.json"); out = {}
with sync_playwright() as p:
    c = p.chromium.launch_persistent_context(str(P), headless=True, args=["--disable-blink-features=AutomationControlled"])
    _plat.need_login(c)
    pg = c.new_page(); pg.goto(f"https://www.instagram.com/{H}/reels/", wait_until="domcontentloaded", timeout=60000); time.sleep(4)
    for e in st["entries"]:
        r = pg.evaluate("async ([pk,hd])=>{const f=await fetch('/api/v1/media/'+pk+'/info/',{headers:hd});if(!f.ok)return {err:f.status};const j=await f.json();const it=(j.items||[{}])[0];return {u:(it.user||{}).username, co:(it.coauthor_producers||[]).map(x=>x.username)}}", [str(e["pk"]), HDR])
        if r.get("err") in (401, 429): print("rate", r); break
        out[e["id"]] = r; time.sleep(1.5 + random.random())
    c.close()
json.dump(out, open(W/"owners.json", "w", encoding="utf-8"), indent=0)
from collections import Counter; print(Counter(v.get("u") for v in out.values()))
print([ (k,v) for k,v in out.items() if v.get("u")!=H])
