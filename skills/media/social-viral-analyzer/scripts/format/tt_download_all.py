#!/usr/bin/env python3
"""Download every TikTok video in list_<handle>.json (from list_all_tiktok.py) for format-skill mode.

Usage: tt_download_all.py <handle> <workdir> [--workers 3] [--limit N] [--max-height 720]
-> <workdir>/media/<id>.mp4. Slideshows (photo posts) come down as audio only: they are recorded in
media/_skipped.json and skipped by full_analyze.py. Resumable (existing mp4s are skipped).
No login needed (TikTok profiles are public).
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import FFPROBE, YTDLP, load, run, save  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handle"); ap.add_argument("workdir")
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-height", type=int, default=720)
    a = ap.parse_args()
    h = a.handle.lstrip("@"); W = Path(a.workdir).expanduser(); M = W / "media"; M.mkdir(parents=True, exist_ok=True)
    lst = load(W / f"list_{h}.json") or sys.exit(f"list_{h}.json missing - run list_all_tiktok.py first")
    skipped = load(M / "_skipped.json", {})
    todo = [e for e in lst["entries"] if not (M / f"{e['id']}.mp4").exists() and e["id"] not in skipped]
    if a.limit:
        todo = todo[: a.limit]
    print(f"[tt] {len(todo)} to download", flush=True)
    lock = Lock(); n = [0]

    def one(e):
        vid = e["id"]; url = f"https://www.tiktok.com/@{h}/video/{vid}"
        tmpl = str(M / f"{vid}.%(ext)s")
        r = run([YTDLP, "-q", "--no-warnings", "-f", f"b[height<={a.max_height}]/bv*[height<={a.max_height}]+ba/b",
                 "--merge-output-format", "mp4", "-o", tmpl, url], timeout=300)
        mp4 = M / f"{vid}.mp4"
        has_video = mp4.exists() and "video" in run([FFPROBE, "-v", "error", "-show_entries", "stream=codec_type",
                                                    "-of", "csv=p=0", mp4]).stdout
        with lock:
            n[0] += 1
            if not has_video:
                for f in M.glob(f"{vid}.*"):
                    f.unlink()
                skipped[vid] = "no video stream (slideshow?)" if r.returncode == 0 else (r.stderr or "")[-200:]
                print(f"[tt] {n[0]}/{len(todo)} {vid} skipped: {skipped[vid][:80]}", flush=True)
            else:
                print(f"[tt] {n[0]}/{len(todo)} {vid} ok", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(one, todo))
    save(M / "_skipped.json", skipped)
    print(f"[tt] done: {len(list(M.glob('*.mp4')))} mp4s, {len(skipped)} skipped")


if __name__ == "__main__":
    main()
