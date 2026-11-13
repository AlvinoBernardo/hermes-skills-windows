#!/usr/bin/env python3
"""Local landmark fingerprint check (Shazam-style peak pairs) of a reel's music stem against full tracks.
For every (track, reel) in tracklist.json: count hashes that agree on one time offset. Also negatives.
Writes fp.json. Usage: fp.py [--rates]"""
import json, pickle, random, sys, subprocess
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.ndimage import maximum_filter

D = Path(__file__).parent; C = D / "fp_cache"; C.mkdir(exist_ok=True)
LIB = Path.home() / "PersonalBrandAssets/music"
SR, NFFT, HOP = 11025, 1024, 256
FR = SR / HOP


def load(path, rate=1.0):
    af = ["-af", f"asetrate={int(44100*rate)},aresample=44100"] if rate != 1.0 else []
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), *af, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def peaks(y):
    if len(y) < NFFT * 4: return np.zeros((0, 2), int)
    win = np.hanning(NFFT).astype(np.float32)
    n = 1 + (len(y) - NFFT) // HOP
    fr = np.lib.stride_tricks.as_strided(y, (n, NFFT), (y.strides[0] * HOP, y.strides[0])) * win
    S = np.log(np.abs(np.fft.rfft(fr, axis=1)).T[:400] + 1e-6)  # up to ~4.3 kHz
    S = S - S.mean(axis=1, keepdims=True)
    mx = maximum_filter(S, size=(21, 21))
    pk = np.argwhere((S == mx) & (S > 1.0))  # (f, t)
    # density cap: keep top ~25 per second
    if len(pk):
        vals = S[pk[:, 0], pk[:, 1]]
        sec = (pk[:, 1] / FR).astype(int)
        keep = []
        for s in np.unique(sec):
            idx = np.where(sec == s)[0]
            keep.extend(idx[np.argsort(-vals[idx])[:25]])
        pk = pk[np.sort(np.array(keep))]
    return pk[np.argsort(pk[:, 1])]


def hashes(pk):
    out = []
    t = pk[:, 1]; f = pk[:, 0]
    for i in range(len(pk)):
        c = 0
        for j in range(i + 1, min(i + 40, len(pk))):
            dt = t[j] - t[i]
            if dt < 1: continue
            if dt > 64: break
            df = f[j] - f[i]
            if abs(df) > 80: continue
            out.append(((int(f[i]) << 16) | ((int(df) + 128) << 7) | int(dt), int(t[i])))
            c += 1
            if c >= 6: break
    return out


def index(path, key):
    p = C / f"{key}.pkl"
    if p.exists(): return pickle.loads(p.read_bytes())
    ix = defaultdict(list)
    for h, t in hashes(peaks(load(path))): ix[h].append(t)
    ix = dict(ix); p.write_bytes(pickle.dumps(ix)); return ix


def match(ix, q):
    offs = Counter()
    tq = defaultdict(list)
    for h, t in q:
        for tt in ix.get(h, ()):
            o = tt - t; offs[o] += 1; tq[o].append(t)
    if not offs: return {"score": 0}
    # merge +-1 frame
    best_o, _ = offs.most_common(1)[0]
    sc = offs[best_o - 1] + offs[best_o] + offs[best_o + 1]
    ts = sorted(tq[best_o - 1] + tq[best_o] + tq[best_o + 1])
    return {"score": sc, "song_pos_at_reel0_s": round(best_o / FR, 2), "reel_from_s": round(ts[0] / FR, 1), "reel_to_s": round(ts[-1] / FR, 1),
            "second": sorted(offs.values())[-4] if len(offs) > 3 else 0}


if __name__ == "__main__":
    sel = json.loads((D / "latest90.json").read_text(encoding="utf-8")); r2c = {i + 1: c for i, c in enumerate(sel)}
    tl = json.loads((D / "tracklist.json").read_text(encoding="utf-8"))
    tp = lambda s: LIB / f"{s[4:]}.mp3" if s.startswith("LIB:") else D / "tracks" / f"{s}.mp3"
    rates = [1.0, 0.97, 1.03] if "--rates" in sys.argv else [1.0]
    qcache = {}

    def q(r, rate):
        k = (r, rate)
        if k not in qcache:
            qcache[k] = hashes(peaks(load(D / "sep/htdemucs" / r2c[r] / "no_vocals.wav", rate)))
        return qcache[k]
    out = {}
    for t in tl:
        p = tp(t["slug"])
        if not p.exists(): continue
        ix = index(p, t["slug"].replace(":", "_"))
        for r in t["reels"]:
            best = None
            for rate in rates:
                m = match(ix, q(r, rate)); m["rate"] = rate
                if best is None or m["score"] > best["score"]: best = m
            out[f"{t['slug']}|{r}"] = {"slug": t["slug"], "reel": r, **best}
            print(f"{t['slug'][:48]:48} reel {r:>2}: score {best['score']:>4} (2nd-best offset {best.get('second')}) "
                  f"rate {best['rate']} song@{best.get('song_pos_at_reel0_s')} reel {best.get('reel_from_s')}-{best.get('reel_to_s')}", flush=True)
    random.seed(2); neg = []
    slugs = [t["slug"] for t in tl if tp(t["slug"]).exists()]
    for r in sorted({r for t in tl for r in t["reels"]})[::2]:
        pos = {t["slug"] for t in tl if r in t["reels"]}
        for s in random.sample([x for x in slugs if x not in pos], 4):
            m = match(index(tp(s), s.replace(":", "_")), q(r, 1.0)); neg.append({"slug": s, "reel": r, "score": m["score"]})
    out["_neg"] = neg
    ns = sorted(n["score"] for n in neg)
    print("NEG scores top:", ns[-10:], "n", len(ns), "median", ns[len(ns) // 2])
    (D / "fp.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
