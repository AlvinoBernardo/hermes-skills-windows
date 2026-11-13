#!/usr/bin/env python3
"""Prep downloaded posts for vision analysis: contact sheets + hook frames + transcripts.

Usage: prep_media.py <out_dir> [--whisper-model PATH]
For each media/<rank>_<id>/ in manifest top_n:
  video     -> hook.jpg (frames at 0, 0.5, 1, 1.5, 2, 3s, 2x3 grid), sheet.jpg (12 frames evenly over the clip, 4x3), transcript.txt
  slideshow -> sheet.jpg (all slides, up to 4 per row), transcript.txt of the audio if a voiceover exists (usually just music)
Updates manifest.json with sheet/hook/transcript paths. Uses ffmpeg + whisper-cli.
"""
import argparse, json, shutil, subprocess
from pathlib import Path

HOME = Path.home()


def _which(name, *fallbacks):
    p = shutil.which(name)
    return p or next((str(f) for f in fallbacks if Path(f).exists()), name)


FF = _which("ffmpeg", "/opt/homebrew/bin/ffmpeg")
FP = _which("ffprobe", "/opt/homebrew/bin/ffprobe")
WH = _which("whisper-cli", HOME / "tools/whisper/Release/whisper-cli.exe", "/opt/homebrew/bin/whisper-cli")
MODEL = next((m for m in (HOME / ".hermes/tools/social-scraper/models/ggml-base.en.bin",
                          HOME / ".hermes/cache/whisper/ggml-base.en.bin",
                          HOME / ".hermes/cache/whisper/ggml-small.en.bin") if m.exists()),
             HOME / ".hermes/tools/social-scraper/models/ggml-base.en.bin")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def dur(f):
    r = run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)])
    try: return float(r.stdout.strip())
    except ValueError: return 0.0


def grid(frames, out, cols, w=360):
    tmp = out.parent / "_frames"; tmp.mkdir(exist_ok=True)
    for i, f in enumerate(frames):
        run([FF, "-y", "-v", "error", "-i", str(f), "-vf", f"scale={w}:-2", str(tmp / f"f{i:03d}.jpg")])
    rows = (len(frames) + cols - 1) // cols
    run([FF, "-y", "-v", "error", "-framerate", "1", "-i", str(tmp / "f%03d.jpg"),
         "-vf", f"scale={w}:{int(w*16/9)}:force_original_aspect_ratio=decrease,pad={w}:{int(w*16/9)}:(ow-iw)/2:(oh-ih)/2,tile={cols}x{rows}:padding=6:color=white",
         "-frames:v", "1", "-q:v", "3", str(out)])
    shutil.rmtree(tmp)


def frames_at(video, times, d):
    out = []
    for i, t in enumerate(times):
        f = d / f"_t{i:02d}.jpg"
        run([FF, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(f)])
        if f.exists(): out.append(f)
    return out


def transcribe(src, d):
    if not MODEL.exists(): return None
    wav = d / "_a.wav"
    run([FF, "-y", "-v", "error", "-i", str(src), "-ac", "1", "-ar", "16000", str(wav)])
    if not wav.exists(): return None
    run([WH, "-m", str(MODEL), "-f", str(wav), "-nt", "-otxt", "-of", str(d / "transcript")])
    wav.unlink(missing_ok=True)
    t = d / "transcript.txt"
    return t.read_text(encoding="utf-8").strip() if t.exists() else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); a = ap.parse_args()
    out = Path(a.out).expanduser(); man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    for x in man["posts"]:
        if not x.get("dir"): continue
        d = out / x["dir"]
        vids = list(d.glob("video.*"))
        if vids:
            v = vids[0]; L = dur(v) or (x.get("duration") or 10)
            x["duration"] = round(L, 1)
            hook = frames_at(v, [t for t in (0.05, 0.5, 1, 1.5, 2, 3) if t < L], d)
            grid(hook, d / "hook.jpg", 3); [f.unlink() for f in hook]
            n = 12; sheet = frames_at(v, [L * (i + 0.5) / n for i in range(n)], d)
            grid(sheet, d / "sheet.jpg", 4); [f.unlink() for f in sheet]
            x["hook_sheet"] = str((d / "hook.jpg").relative_to(out))
            txt = transcribe(v, d)
        else:
            slides = sorted(d.glob("slide_*.jpg"))
            if slides: grid(slides, d / "sheet.jpg", min(4, len(slides)))
            # slideshow audio is almost always a trending song; whisper turns it into fake "lyrics" - skip
            txt = None
        x["sheet"] = str((d / "sheet.jpg").relative_to(out)) if (d / "sheet.jpg").exists() else None
        # whisper hallucinates on music-only audio; keep only transcripts with real words
        x["transcript"] = txt if txt and len(txt.split()) >= 6 and "[Music]" not in txt[:20] else None
        print(f"prep #{x['view_rank']:02d} {x.get('kind')} sheet={'y' if x['sheet'] else 'n'} transcript={len((x['transcript'] or '').split())}w", flush=True)
    (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
