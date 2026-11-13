#!/usr/bin/env python3
"""POST remaining local signatures to Shazam from THIS machine's IP (fallback when cloud browser is 429'd)."""
import json, time, uuid, urllib.request, urllib.error, sys
from pathlib import Path
D = Path(__file__).parent
sigs = json.loads((D / "sigs.json").read_text(encoding="utf-8")); RES = D / "shz_browser.json"
res = json.loads(RES.read_text(encoding="utf-8")) if RES.exists() else {}
only = set(sys.argv[1:])


def post(body):
    url = (f"https://amp.shazam.com/discovery/v5/en-US/US/iphone/-/tag/{str(uuid.uuid4()).upper()}/{str(uuid.uuid4()).upper()}"
           "?sync=true&webv3=true&sampling=true&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3")
    rq = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"})
    try:
        j = json.loads(urllib.request.urlopen(rq, timeout=20).read())
    except urllib.error.HTTPError as e:
        return {"error": f"http {e.code}"}
    except Exception as e:
        return {"error": f"http 0 {e}"}
    t = j.get("track") or {}
    m = (j.get("matches") or [{}])[0] if j.get("matches") else {}
    apple = next((a.get("id") for a in ((t.get("hub") or {}).get("actions") or []) if a.get("type") == "applemusicplay"), None)
    return {"title": t.get("title"), "artist": t.get("subtitle"), "key": t.get("key"), "apple_id": apple,
            "song_offset_s": m.get("offset"), "timeskew": m.get("timeskew"), "frequencyskew": m.get("frequencyskew")}


n = 0
for code, v in sigs.items():
    if only and code not in only: continue
    for it in v["items"]:
        k = f"{code}|{it['kind']}|{it['start']}"
        if k in res and not res[k].get("error"): continue
        h = post(it["body"]); h.update(code=code, kind=it["kind"], start=it["start"])
        print(k, h.get("title"), h.get("artist"), h.get("error") or "", flush=True)
        if h.get("error"):
            if "429" in h["error"]: print("RATE_LIMITED"); RES.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8"); sys.exit(3)
        else:
            res[k] = h; n += 1
        RES.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(2.5)
print("LOCAL_DONE", n)
