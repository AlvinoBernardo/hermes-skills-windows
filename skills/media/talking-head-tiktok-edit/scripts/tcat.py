"""Transcribe concatenated source ranges to verify a planned cut BEFORE rendering it.
Usage (python with numpy; Mac: the mlx-whisper venv, PC: the talking-head venv):
  python tcat.py [--prompt=TEXT] FILE:a:b+FILE:c:d [FILE:a:b ...]
Each arg = one test; '+' joins ranges in order, padded with 0.5s silence each side.
Example: python tcat.py sdr.mp4:9.0:10.55+sdr.mp4:12.24:13.6   -> 'stuck in your room you would think that the fly just'
If a word is missing (cut swallowed it) or doubled (restart left in), move the cut to another RMS dip and re-test.
Windows: drive-letter paths work (C:/x/sdr.mp4:9.0:10.5) because the last two ':' fields are split off from the right.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wtranscribe import transcribe, ffmpeg_pcm, split_prompt

PROMPT, ARGS = split_prompt(sys.argv[1:])

for spec in ARGS:
    parts = [p.rsplit(":", 2) for p in spec.split("+")]
    pad = np.zeros(8000, np.float32)
    x = np.concatenate([pad] + [ffmpeg_pcm(f, float(a), float(b)) for f, a, b in parts] + [pad])
    r = transcribe(x, prompt=PROMPT, language="en")
    print(spec, "|", " ".join(w["word"].strip() for s in r["segments"] for w in s["words"]))
