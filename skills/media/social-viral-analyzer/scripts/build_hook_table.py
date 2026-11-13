#!/usr/bin/env python3
"""hooks_raw.jsonl -> hooks_table.json (clean hook text + performance scores) + _batches/batch{1..N}.json.

`outlier` = views / median of the ~30 posts around it (by date) on the SAME account - fair across account eras
(an account's views swing 10x over the years; raw views would just rank its peak era). >2 = winner, <0.5 = flop.
Usage: python3 build_hook_table.py <workdir> [n_batches=8]   (rows are dealt round-robin by views so every batch has winners and flops)
"""
import json, re, statistics, datetime, sys
from pathlib import Path

W = Path(sys.argv[1]).expanduser()
nb = int(sys.argv[2]) if len(sys.argv) > 2 else 8
rows = list({r["id"]: r for r in (json.loads(l) for l in open(W / "hooks_raw.jsonl", encoding="utf-8"))}.values())
NOISE = re.compile(r"^(tiktok|@\S+|\d{1,2}:\d{2}|capcut|.{0,2})$", re.I)

def ocr_text(r):
    o = r.get("ocr") or {}
    seen, out = set(), []
    for k in ("0.2", "1.0", "2.5", "cover"):
        for t in o.get(k, []):
            t = t.strip()
            if NOISE.match(t): continue
            key = re.sub(r"\W", "", t.lower())
            if key and key not in seen:
                seen.add(key); out.append(t)
    return " / ".join(out)[:400]

def spoken(r):
    s = (r.get("spoken_hook") or "").strip()
    if re.fullmatch(r"[\[\(].*[\]\)]", s) or len(s.split()) < 3: return ""   # '[Music]', '(somber music)'
    return s[:400]

by_acc = {}
for r in rows: by_acc.setdefault(r["handle"], []).append(r)
for acc, lst in by_acc.items():
    lst.sort(key=lambda r: r.get("timestamp") or 0)
    for i, r in enumerate(lst):
        nbv = [x.get("views") or 0 for x in lst[max(0, i - 15): i + 16] if x is not r]
        r["outlier"] = round((r.get("views") or 0) / max(statistics.median(nbv) if nbv else 1, 1), 2)
    allv = sorted(x.get("views") or 0 for x in lst)
    for r in lst:
        r["pct_rank"] = round(sum(1 for v in allv if v <= (r.get("views") or 0)) / len(allv), 3)

out = []
for r in rows:
    strip = W / "hook_strips" / f"{r['id']}.jpg"
    out.append({"id": r["id"], "handle": r["handle"], "url": r["url"], "kind": r.get("kind"),
                "date": datetime.date.fromtimestamp(r["timestamp"]).isoformat() if r.get("timestamp") else None,
                "views": r.get("views"), "likes": r.get("likes"), "saves": r.get("saves"), "shares": r.get("shares"),
                "duration": r.get("duration"), "outlier": r["outlier"], "pct_rank": r["pct_rank"],
                "on_screen_text": ocr_text(r), "spoken_first_6s": spoken(r), "caption": (r.get("caption") or "")[:200],
                "strip": str(strip) if strip.exists() else None})
out.sort(key=lambda r: -(r["views"] or 0))
json.dump(out, open(W / "hooks_table.json", "w", encoding="utf-8"), indent=1)
bd = W / "_batches"; bd.mkdir(exist_ok=True)
for i in range(nb):
    json.dump(out[i::nb], open(bd / f"batch{i + 1}.json", "w", encoding="utf-8"), indent=1)
print(len(out), "rows;", {a: len(l) for a, l in by_acc.items()}, "batches:", nb)
