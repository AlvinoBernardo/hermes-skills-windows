#!/usr/bin/env python3
"""Usage: build_table.py <workdir> [n_batches=8] [suffix e.g. _ig]
hooks_raw<sfx>.jsonl -> hooks_table<sfx>.json: clean hook text + performance scores, split into batches for analysis."""
import json, re, statistics, datetime, sys
from pathlib import Path

W = Path(sys.argv[1]).expanduser()
nb = int(sys.argv[2]) if len(sys.argv) > 2 else 8
sfx = sys.argv[3] if len(sys.argv) > 3 else ""  # e.g. "_ig" -> hooks_raw_ig.jsonl / hooks_table_ig.json / _batches_ig/
rows = [json.loads(l) for l in open(W / f"hooks_raw{sfx}.jsonl", encoding="utf-8")]
rows = list({r["id"]: r for r in rows}.values())

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
    if re.fullmatch(r"[\[\(].*[\]\)]", s) or len(s.split()) < 3: return ""
    return s[:400]

# performance: views vs the median of the 30 nearest posts by date on the same account
by_acc = {}
for r in rows: by_acc.setdefault(r["handle"], []).append(r)
for acc, lst in by_acc.items():
    lst.sort(key=lambda r: r.get("timestamp") or 0)
    for i, r in enumerate(lst):
        nb_views = [x.get("views") or 0 for x in lst[max(0, i - 15): i + 16] if x is not r]
        med = statistics.median(nb_views) if nb_views else 1
        r["local_median"] = med
        r["outlier"] = round((r.get("views") or 0) / max(med, 1), 2)
    allv = sorted(x.get("views") or 0 for x in lst)
    for r in lst:
        r["pct_rank"] = round(sum(1 for v in allv if v <= (r.get("views") or 0)) / len(allv), 3)

out = []
for r in rows:
    out.append({"id": r["id"], "handle": r["handle"], "url": r["url"], "kind": r.get("kind"),
                "date": datetime.date.fromtimestamp(r["timestamp"]).isoformat() if r.get("timestamp") else None,
                "views": r.get("views"), "likes": r.get("likes"), "saves": r.get("saves"), "shares": r.get("shares"),
                "duration": r.get("duration"), "outlier": r["outlier"], "pct_rank": r["pct_rank"],
                "on_screen_text": ocr_text(r), "spoken_first_6s": spoken(r), "caption": (r.get("caption") or "")[:200],
                "strip": str(W / "hook_strips" / f"{r['id']}.jpg") if (W / "hook_strips" / f"{r['id']}.jpg").exists() else None})
out.sort(key=lambda r: -(r["views"] or 0))
json.dump(out, open(W / f"hooks_table{sfx}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bd = W / f"_batches{sfx}"; bd.mkdir(exist_ok=True)
for i in range(nb):
    json.dump(out[i::nb], open(bd / f"batch{i + 1}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(len(out), "rows;", {a: len(l) for a, l in by_acc.items()}, "batches:", nb)
