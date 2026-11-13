#!/usr/bin/env python3
"""Format-skill mode, step 7: merge the children's classifications with the table and compute the stats.

Usage: aggregate_format.py <workdir> [--hit 2.0] [--flop 0.7]
Reads format_table.json + _batches/analysis*.json (arrays of objects keyed by "id", see CLASSIFY_INSTRUCTIONS.md).
Writes merged.json (table row + classification per video; source of truth for hook-bank/transcript generation)
and stats.json + stats.md: per label (hook_type, topic_bucket, format, structure_type) and per device list
(hook_devices, structure_devices, visual_devices, voice_devices): n, median outlier, hit % (> --hit), flop %
(< --flop); plus buckets for length, wpm, cuts/10s, first-word time, text hook vs none, music-only, and the
creator's series line (rows where classification.series_line is true). Fresh posts are excluded from stats.
Reports ids missing from the children's output so you can re-run that batch.
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load, save  # noqa: E402

LABELS = ["hook_type", "topic_bucket", "format", "structure_type"]
DEVICES = ["hook_devices", "structure_devices", "visual_devices", "voice_devices"]


def bucket(v, edges, unit=""):
    if v is None:
        return "n/a"
    for lo, hi in zip(edges, edges[1:]):
        if lo <= v < hi:
            return f"{lo}-{hi}{unit}"
    return f">={edges[-1]}{unit}"


def stat(rows, hit, flop):
    o = [r["outlier"] for r in rows if r.get("outlier") is not None]
    if not o:
        return None
    return {"n": len(o), "median_outlier": round(statistics.median(o), 2),
            "hit_pct": round(100 * sum(x > hit for x in o) / len(o)), "flop_pct": round(100 * sum(x < flop for x in o) / len(o)),
            "examples": [r["id"] for r in sorted(rows, key=lambda r: -(r.get("outlier") or 0))[:3]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir"); ap.add_argument("--hit", type=float, default=2.0); ap.add_argument("--flop", type=float, default=0.7)
    a = ap.parse_args()
    W = Path(a.workdir).expanduser()
    table = load(W / "format_table.json") or sys.exit("format_table.json missing - run build_format_table.py")
    cls = {}
    for f in sorted((W / "_batches").glob("analysis*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for c in (data if isinstance(data, list) else data.values()):
            cls[str(c["id"])] = c
    merged = [{**t, "classification": cls.get(t["id"])} for t in table]
    save(W / "merged.json", merged)
    batched = {r["id"] for f in (W / "_batches").glob("batch*.json") for r in load(f, [])}
    missing = sorted(batched - set(cls))

    rows = [m for m in merged if not m["fresh"] and m.get("outlier") is not None]
    out = {"n_rows": len(rows), "n_classified": sum(1 for r in rows if r["classification"]), "missing_ids": missing,
           "overall": stat(rows, a.hit, a.flop), "labels": {}, "devices": {}, "buckets": {}}
    for lab in LABELS:
        g = defaultdict(list)
        for r in rows:
            if r["classification"] and r["classification"].get(lab):
                g[r["classification"][lab]].append(r)
        out["labels"][lab] = dict(sorted(((k, stat(v, a.hit, a.flop)) for k, v in g.items()),
                                         key=lambda kv: -kv[1]["median_outlier"]))
    for dev in DEVICES:
        g = defaultdict(list)
        for r in rows:
            for d in (r["classification"] or {}).get(dev) or []:
                g[d].append(r)
        out["devices"][dev] = dict(sorted(((k, stat(v, a.hit, a.flop)) for k, v in g.items() if len(v) >= 3),
                                          key=lambda kv: -kv[1]["median_outlier"]))
    bk = {"length_s": lambda r: bucket(r.get("duration"), [0, 15, 30, 45, 60, 90, 180], "s"),
          "wpm": lambda r: bucket(r.get("wpm"), [0, 120, 150, 180, 210, 240]),
          "cuts_per_10s": lambda r: bucket(r.get("cuts_per_10s"), [0, 1, 2, 4, 6, 10]),
          "first_word_s": lambda r: bucket(r.get("first_word_s"), [0, 0.3, 0.7, 1.5, 3], "s"),
          "text_hook": lambda r: "text hook" if r.get("on_screen_hook") else "no text hook",
          "music_only": lambda r: "music only" if r.get("music_only") else "speech",
          "series_line": lambda r: "opens with series line" if (r["classification"] or {}).get("series_line") else "no series line"}
    for name, fn in bk.items():
        g = defaultdict(list)
        for r in rows:
            g[fn(r)].append(r)
        out["buckets"][name] = {k: stat(v, a.hit, a.flop) for k, v in sorted(g.items())}
    save(W / "stats.json", out)

    md = [f"# Format stats ({out['n_rows']} posts, {out['n_classified']} classified; hit > {a.hit}x, flop < {a.flop}x)\n",
          f"Overall median outlier {out['overall']['median_outlier'] if out['overall'] else '-'}\n"]

    def table_md(title, d):
        md.append(f"\n## {title}\n\n| value | n | median outlier | hit % | flop % | top examples |\n|---|---|---|---|---|---|")
        for k, s in d.items():
            if s:
                md.append(f"| {k} | {s['n']} | {s['median_outlier']} | {s['hit_pct']} | {s['flop_pct']} | {', '.join(s['examples'])} |")
    for lab in LABELS:
        table_md(lab, out["labels"][lab])
    for dev in DEVICES:
        table_md(dev + " (n>=3)", out["devices"][dev])
    for name in bk:
        table_md(name, out["buckets"][name])
    (W / "stats.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"merged.json + stats.json + stats.md: {out['n_rows']} rows, {out['n_classified']} classified, "
          f"{len(missing)} batched ids missing from analysis*.json{': ' + ', '.join(missing[:10]) if missing else ''}")


if __name__ == "__main__":
    main()
