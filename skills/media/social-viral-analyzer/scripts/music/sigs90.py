#!/usr/bin/env python3
"""Local Shazam signatures (no network) for the demucs no_vocals stem of each reel.
Windows: 12 s every 10 s across the reel (stem) + 2 raw-mix windows. Out: sigs.json {code: {duration, items}}
Usage: sigs90.py <dir>   (skips reels whose stem isn't ready yet; re-run to add)"""
import asyncio, json, subprocess, sys
from pathlib import Path
from shazamio import Shazam
from shazamio.converter import Converter

D = Path(sys.argv[1]).resolve(); W = D / "sigwav"; W.mkdir(exist_ok=True)
sel = json.loads((D / "latest90.json").read_text(encoding="utf-8")); st = json.loads((D / "reels.json").read_text(encoding="utf-8"))
OUT = D / "sigs.json"; out = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}


def cut(src, s, dst):
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", f"{s:.2f}", "-t", "12", "-i", str(src),
                    "-ac", "1", "-ar", "16000", str(dst)])


async def main():
    sh = Shazam(); n = 0
    for code in sel:
        if code in out: continue
        stem = D / "sep/htdemucs" / code / "no_vocals.wav"
        if not stem.exists(): continue
        dur = float(st[code].get("duration") or 30)
        starts = [float(s) for s in range(0, max(1, int(dur - 8)), 10)]
        items = []
        for kind, src, ss in [("stem", stem, starts), ("raw", D / "audio" / f"{code}.m4a", [1.0, round(dur * 0.5, 1)])]:
            for s in ss:
                if s + 5 > dur: continue
                w = W / f"{code}_{kind}_{s}.wav"; cut(src, s, w)
                try:
                    sig = await sh.core_recognizer.recognize_path(value=str(w))
                    body = Converter.data_search(sig.timezone, sig.signature.uri, sig.signature.samples, sig.timestamp)
                    items.append({"kind": kind, "start": s, "body": body})
                except Exception as e:
                    print("sigfail", code, kind, s, str(e)[:60])
                w.unlink(missing_ok=True)
        out[code] = {"duration": dur, "items": items}; n += 1
        OUT.write_text(json.dumps(out), encoding="utf-8")
        print(code, len(items), flush=True)
    print("SIGS", len(out), "new", n)

asyncio.run(main())
