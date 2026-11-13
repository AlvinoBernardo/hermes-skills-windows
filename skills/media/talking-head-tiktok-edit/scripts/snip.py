"""Re-transcribe short padded snippets to expose stutters/restarts that full-pass Whisper hides.
Usage (python with numpy; Mac: the mlx-whisper venv, PC: the talking-head venv):
  python snip.py [--prompt="Umm, uh, I- I mean, the the."] FILE:START:END [FILE:START:END ...]
Prints words with SOURCE-file timestamps. 0.5s of silence is padded on each side so Whisper
does not merge a cut-off word into its neighbour. Engine: see wtranscribe.py (mlx-whisper or whisper-cli).
--prompt= is the disfluency pass from the stutter gate (makes Whisper print "Your re- / Your reputation").
Windows: drive-letter paths work (C:/x/sdr.mp4:9.0:10.5) because the last two ':' fields are split off from the right.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wtranscribe import transcribe, ffmpeg_pcm, split_prompt

PROMPT, ARGS = split_prompt(sys.argv[1:])

def snip(f, a, b):
    x = ffmpeg_pcm(f, a, b); pad = np.zeros(8000, np.float32)
    x = np.concatenate([pad, x, pad])
    r = transcribe(x, prompt=PROMPT)
    print(f, a, b, "|", " ".join(f"{w['word'].strip()}[{w['start']-0.5+a:.2f}]"
                                 for s in r["segments"] for w in s["words"]))

for arg in ARGS:
    f, a, b = arg.rsplit(":", 2); snip(f, float(a), float(b))
