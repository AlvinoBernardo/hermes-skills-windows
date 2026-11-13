#!/usr/bin/env python3
"""Combine Shazam consensus + local fingerprint + Apple-preview identity into a final verdict per reel and per track."""
import json, statistics
from pathlib import Path
D = Path(__file__).parent
sel = json.loads((D / "latest90.json").read_text(encoding="utf-8")); st = json.loads((D / "reels.json").read_text(encoding="utf-8"))
agg = json.loads((D / "agg.json").read_text(encoding="utf-8")); r2a = {v["rank"]: v for v in agg.values()}
fp = json.loads((D / "fp.json").read_text(encoding="utf-8")); pc = json.loads((D / "preview_check.json").read_text(encoding="utf-8"))
tl = json.loads((D / "tracklist.json").read_text(encoding="utf-8")); titles = json.loads((D / "slug_titles.json").read_text(encoding="utf-8"))


def consistent_pairs(hits):
    hs = sorted([h for h in hits if h["off"] is not None and h["kind"] in ("stem", "raw")], key=lambda h: h["start"])
    n = 0
    for a, b in zip(hs, hs[1:]):
        if b["start"] - a["start"] > 0 and abs((b["off"] - a["off"]) - (b["start"] - a["start"])) <= 1.5: n += 1
    return n


pairs = []
for t in tl:
    s = t["slug"]
    pcb = (pc.get(s) or {}).get("best") or {}
    for r in t["reels"]:
        a = r2a[r]
        hits = [h for tr in a["tracks"] if tr["title"] in titles.get(s, []) for h in tr["hits"]]
        f = fp.get(f"{s}|{r}", {})
        fps, sec = f.get("score", 0), f.get("second", 0)
        fp_ok = fps >= 15 and fps >= 2 * max(sec, 1)
        n, cp = len(hits), consistent_pairs(hits)
        shz_ok = n >= 3 and cp >= 1
        shz_likely = n >= 2 and cp >= 1
        id_ok = (pcb.get("score", 0) >= 100) or fp_ok
        if (fp_ok or shz_ok) and id_ok: v = "VERIFIED"
        elif (shz_likely or (n >= 2)) and (id_ok or pcb.get("score", 0) >= 25): v = "LIKELY"
        else: v = "UNCONFIRMED"
        pairs.append({"slug": s, "reel": r, "verdict": v, "shazam_windows": n, "shazam_consistent_pairs": cp,
                      "fp_score": fps, "fp_second": sec, "fp_song_pos_at_reel0": f.get("song_pos_at_reel0_s"),
                      "file_preview_score": pcb.get("score"), "apple": pcb.get("apple")})
(D / "final_pairs.json").write_text(json.dumps(pairs, ensure_ascii=False, indent=1), encoding="utf-8")
order = {"VERIFIED": 0, "LIKELY": 1, "UNCONFIRMED": 2}
for p in sorted(pairs, key=lambda p: (order[p["verdict"]], p["slug"])):
    print(f"{p['verdict']:11} {p['slug'][:50]:50} r{p['reel']:>2} shz {p['shazam_windows']}/{p['shazam_consistent_pairs']} fp {p['fp_score']}/{p['fp_second']} file {p['file_preview_score']}")
