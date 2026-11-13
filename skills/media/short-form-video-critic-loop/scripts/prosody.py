#!/usr/bin/env python3
"""Prosody metrics for narration takes vs a reference narrator.
usage: uv run --with librosa --with numpy python prosody.py FILE [FILE ...]
Prints median pitch, 5-95% pitch range and SD (semitones), pauses/min (>=120 ms), mean pause, speech ratio."""
import sys, numpy as np, librosa

def analyze(path):
    y, sr = librosa.load(path, sr=16000, mono=True)
    f0, _, _ = librosa.pyin(y, fmin=60, fmax=350, sr=sr, frame_length=1024, hop_length=160)
    f = f0[~np.isnan(f0)]
    st = 12 * np.log2(f / np.median(f)) if len(f) else np.array([0])
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=160)[0]
    db = 20 * np.log10(rms + 1e-6); sil = db < np.percentile(db, 95) - 30
    pauses, run = [], 0
    for s in sil:
        if s: run += 1
        else:
            if run * 0.01 >= 0.12: pauses.append(run * 0.01)
            run = 0
    dur = len(y) / sr
    return dict(dur=round(dur, 2), median_hz=round(float(np.median(f)), 1) if len(f) else None,
                pitch_range_st=round(float(np.percentile(st, 95) - np.percentile(st, 5)), 1),
                pitch_sd_st=round(float(np.std(st)), 2), hi_180=round(float(np.mean(f > 180)), 2) if len(f) else 0,
                pauses_per_min=round(len(pauses) / dur * 60, 1), mean_pause=round(float(np.mean(pauses)), 2) if pauses else 0,
                speech_ratio=round(float((~sil).sum() * 0.01 / dur), 2))

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p.split('/')[-1], analyze(p))
