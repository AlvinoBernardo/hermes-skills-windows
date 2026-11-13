#!/usr/bin/env python3
"""Format-skill mode, step 5: merge list + owners + full_analyze output into one table and deal batches.

Usage: build_format_table.py <workdir> <handle> [n_batches=4] [--fresh-days 7] [--transcript-chars 2500]
Inputs (any platform): list_ig_<h>.json (ig_reels_capture.py) or list_<h>.json (list_all_tiktok.py),
owners.json (IG, optional), analysis/<id>.json. Output:
  format_table.json  one row per analyzed video: id, url, views, likes, date, age_days, duration, outlier
                     (views / median of the 30 posts nearest in date), fresh (< fresh-days old: excluded
                     from stats and batches), pct_rank, on_screen_hook, mid_text, transcript, wpm,
                     first_word_s, cuts_per_10s, longest_pause_s, music_only, sheet, strip
  _batches/batch<N>.json   non-fresh rows dealt round-robin by outlier so each batch has hits and flops
Then copy CLASSIFY_INSTRUCTIONS.md to _batches/INSTRUCTIONS.md and fill in the creator description.
"""
import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load, rolling_outlier, save  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir"); ap.add_argument("handle"); ap.add_argument("n_batches", nargs="?", type=int, default=4)
    ap.add_argument("--fresh-days", type=float, default=7); ap.add_argument("--transcript-chars", type=int, default=2500)
    a = ap.parse_args()
    W = Path(a.workdir).expanduser(); h = a.handle.lstrip("@")
    ig = load(W / f"list_ig_{h}.json"); tt = load(W / f"list_{h}.json")
    if not (ig or tt):
        sys.exit("no list_ig_<h>.json or list_<h>.json in workdir")
    owners = load(W / "owners.json", {})
    rows = []
    if ig:
        for e in ig["entries"]:
            if owners.get(e["code"], {}).get("keep") is False:
                continue
            rows.append({"id": e["code"], "platform": "instagram", "url": f"https://www.instagram.com/reel/{e['code']}/",
                         "views": e.get("views"), "likes": e.get("likes"), "comments": e.get("comments"),
                         "timestamp": e.get("timestamp"), "caption": e.get("caption") or "", "music": e.get("music")})
    if tt:
        for e in tt["entries"]:
            rows.append({"id": str(e["id"]), "platform": "tiktok", "url": f"https://www.tiktok.com/@{h}/video/{e['id']}",
                         "views": e.get("view_count"), "likes": e.get("like_count"), "comments": e.get("comment_count"),
                         "saves": e.get("save_count"), "timestamp": e.get("timestamp"),
                         "caption": (e.get("description") or e.get("title") or ""), "music": e.get("track")})
    # outlier over the WHOLE account (also posts we couldn't analyze), so the neighbour medians are honest
    rolling_outlier(rows)
    now = time.time(); table = []
    for r in rows:
        an = load(W / "analysis" / f"{r['id']}.json")
        if not an or an.get("error"):
            continue
        age = (now - r["timestamp"]) / 86400 if r.get("timestamp") else None
        hook = [t for k in sorted(an.get("ocr_hook", {})) for t in an["ocr_hook"][k]]
        mid = [t for k in sorted(an.get("ocr_mid", {})) for t in an["ocr_mid"][k]]
        dedup = lambda xs: " / ".join(dict.fromkeys(xs))  # noqa: E731
        table.append({**{k: r.get(k) for k in ("id", "platform", "url", "views", "likes", "comments", "saves",
                                               "outlier", "caption", "music")},
                      "date": datetime.fromtimestamp(r["timestamp"], timezone.utc).strftime("%Y-%m-%d") if r.get("timestamp") else None,
                      "age_days": round(age, 1) if age is not None else None,
                      "fresh": age is not None and age < a.fresh_days,
                      "duration": an.get("duration"), "aspect": an.get("aspect"),
                      "on_screen_hook": dedup(hook), "mid_text": dedup(mid),
                      "transcript": (an.get("transcript") or "")[: a.transcript_chars],
                      "wpm": an.get("wpm"), "first_word_s": an.get("first_word_s"), "n_words": an.get("n_words"),
                      "cuts_per_10s": an.get("cuts_per_10s"), "longest_pause_s": an.get("longest_pause_s"),
                      "speech_ratio": an.get("speech_ratio"), "music_only": an.get("music_only"),
                      "sheet": an.get("sheet"), "strip": an.get("strip")})
    scored = sorted([t for t in table if not t["fresh"] and t["outlier"] is not None], key=lambda t: -t["outlier"])
    for i, t in enumerate(scored):
        t["pct_rank"] = round(1 - i / max(len(scored) - 1, 1), 3)
    save(W / "format_table.json", table)
    n = max(1, a.n_batches); B = W / "_batches"; B.mkdir(exist_ok=True)
    for i in range(n):
        save(B / f"batch{i + 1}.json", scored[i::n])
    fresh = sum(t["fresh"] for t in table)
    print(f"format_table.json: {len(table)} analyzed rows ({len(rows)} listed), {fresh} fresh (excluded), "
          f"{len(scored)} dealt into {n} batches of ~{len(scored) // n}")
    if scored:
        print("top 5 by outlier:", ", ".join(f"{t['id']} x{t['outlier']}" for t in scored[:5]))


if __name__ == "__main__":
    main()
