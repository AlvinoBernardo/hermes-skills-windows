#!/usr/bin/env python3
"""iPhone HDR (HLG / Dolby Vision 8.4, HEVC 10-bit, rotated) -> 1080x1920 SDR bt709 mp4, 30 fps. Pipeline step 2.
Usage: python hdr2sdr.py IN.MOV OUT.mp4 [--ffmpeg]

macOS:   uses `avconvert -p Preset1920x1080` (proper tonemap, ~9 s) unless --ffmpeg is given.
Windows/Linux (or --ffmpeg): ffmpeg zscale + mobius tonemap (the winget/gpl ffmpeg has zscale+tonemap; Hermes's bundled
         ffmpeg may not: check `ffmpeg -filters | grep zscale`). Rotation is applied automatically from the display matrix.
SDR input (transfer not HLG/PQ) skips the tonemap and is only rotated/scaled/fps-normalised.
Only checked on a synthetic HLG clip, NOT on real iPhone footage: compare one frame against the source and, if it is dark/flat,
try HDR_TONEMAP=reinhard:param=0.5 or hable. The skill's grade step (eq contrast/saturation) sits on top.
On the PC run big 4K files through IkkimiAssets/scripts/run_low.py so the machine stays usable.
"""
import json, os, shutil, subprocess, sys

HDR_TRC = {"arib-std-b67": "hlg", "smpte2084": "pq"}


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "json", f], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["streams"][0].get("color_transfer", "")
    except Exception:
        return ""


def main(src, dst, force_ffmpeg=False):
    if sys.platform == "darwin" and not force_ffmpeg and shutil.which("avconvert"):
        subprocess.run(["avconvert", "-s", src, "-p", "Preset1920x1080", "-o", dst, "--replace"], check=True)
        return
    trc = probe(src)
    fit = "scale=1080:1920:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,fps=30"
    if trc in HDR_TRC:
        # npl=100 maps HLG/PQ reference white to SDR white; desat=0 avoids greying the colours.
        # mobius keeps midtones (hable darkened a synthetic HLG round-trip by ~30%): override with HDR_TONEMAP=hable etc.
        tm = os.environ.get("HDR_TONEMAP", "mobius:param=0.3")
        vf = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=" + tm + ":desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p," + fit)
    else:
        vf = fit + ",format=yuv420p"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", vf, "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                    "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", dst], check=True)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 2:
        sys.exit(__doc__)
    main(a[0], a[1], "--ffmpeg" in sys.argv)
