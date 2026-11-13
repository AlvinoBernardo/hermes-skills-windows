"""List every quiet dip (10 ms RMS windows) inside given time ranges, to place cuts at real pauses.
Usage (system python3):
  python3 dips.py SRC.mp4 THRESH_DB RANGE [RANGE ...]      e.g.  python3 dips.py sdr.mp4 -38 11.3-12.9 27.5-29.0
  python3 dips.py SRC.mp4 raw START END                    -> prints every 10 ms dB value (find onsets / tails)
Output per range: start-end(min dB) for each run of >=30 ms below THRESH. A join is safe only inside a dip
that is >= ~0.1 s long and <= about -44 dB; shorter/shallower gaps clip consonants.
The envelope is cached as <SRC>.env10.npy so repeated queries are instant.
"""
import subprocess, numpy as np, sys, os
src = sys.argv[1]; cache = src + ".env10.npy"
if os.path.exists(cache):
    e = np.load(cache)
else:
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32)
    x = x[: len(x) // 160 * 160].reshape(-1, 160)
    e = 20 * np.log10(np.sqrt(np.mean(x ** 2, axis=1)) + 1e-9); np.save(cache, e)
if sys.argv[2] == "raw":
    a, b = float(sys.argv[3]), float(sys.argv[4])
    print(" ".join(f"{e[i]:.0f}" for i in range(int(a * 100), int(b * 100)))); sys.exit()
thr = float(sys.argv[2])
for r in sys.argv[3:]:
    a, b = map(float, r.split("-")); i0, i1 = int(a * 100), int(b * 100); seg = e[i0:i1]; out = []; s = None
    for k, v in enumerate(seg):
        if v < thr and s is None: s = k
        if (v >= thr or k == len(seg) - 1) and s is not None:
            if k - s >= 3: out.append(f"{(i0 + s) / 100:.2f}-{(i0 + k) / 100:.2f}({seg[s:k].min():.0f})")
            s = None
    print(r, ":", " ".join(out) or "(no dip)")
