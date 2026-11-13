#!/usr/bin/env python3
"""Extra rate-shifted signatures (undo slowed/sped audio) for unidentified reels -> appended into sigs.json."""
import asyncio, json, subprocess, sys
from pathlib import Path
from shazamio import Shazam
from shazamio.converter import Converter
D = Path(__file__).parent.resolve(); W = D / "sigwav"; W.mkdir(exist_ok=True)
sel = json.loads((D / "latest90.json").read_text(encoding="utf-8")); st = json.loads((D / "reels.json").read_text(encoding="utf-8"))
ranks = [int(x) for x in sys.argv[1].split(",")]
sigs = json.loads((D / "sigs.json").read_text(encoding="utf-8"))


async def main():
    sh = Shazam()
    for r in ranks:
        c = sel[r - 1]; dur = float(st[c]["duration"] or 30)
        stem = D / "sep/htdemucs" / c / "no_vocals.wav"
        for rate in (1.15, 0.87, 1.07, 0.93):
            for s in (round(dur * 0.2, 1), round(dur * 0.6, 1)):
                kind = f"stem_r{rate}"
                if any(it["kind"] == kind and it["start"] == s for it in sigs[c]["items"]): continue
                w = W / f"{c}_{kind}_{s}.wav"
                subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", f"{s}", "-t", "14", "-i", str(stem),
                                "-af", f"aresample=44100,asetrate={int(44100*rate)},aresample=16000", "-ac", "1", "-t", "12", str(w)])
                sig = await sh.core_recognizer.recognize_path(value=str(w))
                body = Converter.data_search(sig.timezone, sig.signature.uri, sig.signature.samples, sig.timestamp)
                sigs[c]["items"].append({"kind": kind, "start": s, "body": body}); w.unlink(missing_ok=True)
        print(r, c, len(sigs[c]["items"]), flush=True)
    (D / "sigs.json").write_text(json.dumps(sigs), encoding="utf-8")

asyncio.run(main())
