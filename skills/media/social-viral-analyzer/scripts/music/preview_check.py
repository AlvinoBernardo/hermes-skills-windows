#!/usr/bin/env python3
"""File identity check: fingerprint each downloaded track against the Apple Music 30 s preview of the exact
recording Shazam matched (Apple id from Shazam hits). Writes preview_check.json."""
import json, urllib.request, sys
from pathlib import Path
sys.argv = ["x"]
D = Path(__file__).parent
exec(open(D / "fp.py", encoding="utf-8").read().split("if __name__")[0])
PV = D / "previews"; PV.mkdir(exist_ok=True)
cand = json.loads((D / "candidates.json").read_text(encoding="utf-8"))
st = json.loads((D / "slug_titles.json").read_text(encoding="utf-8"))
tl = json.loads((D / "tracklist.json").read_text(encoding="utf-8"))
tp = lambda s: LIB / f"{s[4:]}.mp3" if s.startswith("LIB:") else D / "tracks" / f"{s}.mp3"
ids = {}
for d in cand:
    for a in d["apple"]: ids.setdefault(d["title"], set()).add(a)
allids = sorted({a for v in ids.values() for a in v})
meta = {}
for i in range(0, len(allids), 100):
    j = json.loads(urllib.request.urlopen("https://itunes.apple.com/lookup?id=" + ",".join(allids[i:i + 100])).read())
    for r in j["results"]: meta[str(r["trackId"])] = r
out = {}
for t in tl:
    s = t["slug"]; p = tp(s)
    if not p.exists(): continue
    res = []
    for title in st.get(s, []):
        for a in sorted(ids.get(title, [])):
            m = meta.get(a)
            if not m or not m.get("previewUrl"): continue
            f = PV / f"{a}.m4a"
            if not f.exists(): f.write_bytes(urllib.request.urlopen(m["previewUrl"]).read())
            ix = index(p, s.replace(":", "_"))
            r = match(ix, hashes(peaks(load(f))))
            res.append({"apple_id": a, "apple": f"{m.get('trackName')} – {m.get('artistName')} ({m.get('collectionName')})",
                        "score": r["score"], "second": r.get("second"), "preview_at_song_s": r.get("song_pos_at_reel0_s")})
    best = max(res, key=lambda x: x["score"]) if res else None
    out[s] = {"best": best, "all": res}
    print(f"{s[:52]:52} " + (f"score {best['score']:>4} (2nd {best['second']}) at {best['preview_at_song_s']}s  <- {best['apple'][:60]}" if best else "no apple preview"), flush=True)
(D / "preview_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
