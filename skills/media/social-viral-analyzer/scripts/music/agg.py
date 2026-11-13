#!/usr/bin/env python3
"""Aggregate browser Shazam hits per reel -> agg.json + console table."""
import json, collections, datetime, statistics
from pathlib import Path
D = Path(__file__).parent
st = json.loads((D / "reels.json").read_text(encoding="utf-8")); sel = json.loads((D / "latest90.json").read_text(encoding="utf-8"))
res = json.loads((D / "shz_browser.json").read_text(encoding="utf-8"))
sigs = json.loads((D / "sigs.json").read_text(encoding="utf-8"))
by = collections.defaultdict(list)
for k, v in res.items():
    by[v["code"]].append(v)
# local median views for outlier
views = [st[c].get("views") or 0 for c in sel]
med = statistics.median(views)
agg = {}
for i, c in enumerate(sel):
    hs = by.get(c, [])
    cnt = collections.Counter()
    info = {}
    for h in hs:
        if h.get("title"):
            k = (h["title"], h["artist"]); cnt[k] += 1
            info.setdefault(k, []).append({"start": h["start"], "kind": h["kind"], "off": h.get("song_offset_s"),
                                           "key": h.get("key"), "apple_id": h.get("apple_id"), "skew": h.get("timeskew")})
    nwin = len(sigs.get(c, {}).get("items", []))
    tracks = []
    for k, n in cnt.most_common():
        tracks.append({"title": k[0], "artist": k[1], "windows": n, "hits": info[k],
                       "confidence": "high" if n >= 2 else "single"})
    e = st[c]
    agg[c] = {"rank": i + 1, "code": c, "url": e["url"], "date": datetime.datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d"),
              "views": e.get("views"), "outlier": round((e.get("views") or 0) / med, 2), "duration": e.get("duration"),
              "caption": (e.get("caption") or "")[:120].replace("\n", " "), "n_windows": nwin, "n_queried": len(hs),
              "tracks": tracks}
(D / "agg.json").write_text(json.dumps(agg, ensure_ascii=False, indent=1), encoding="utf-8")
print("median views", med)
for c, a in agg.items():
    t = " | ".join(f"{x['title']} – {x['artist']} ({x['windows']})" for x in a["tracks"]) or "—"
    print(f"{a['rank']:>2} {a['date']} {a['views'] or 0:>9} {a['n_queried']}/{a['n_windows']}  {t}")
