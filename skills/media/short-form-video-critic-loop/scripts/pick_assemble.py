#!/usr/bin/env python3
"""Score every per-line take and assemble the best one per line into a mastered narration.
usage: uv run --with faster-whisper --with librosa --with numpy --with soundfile --with scipy \
         python pick_assemble.py INDIR[,INDIR2] PROFILE_PREFIX OUT.wav
Reads ./lines.json (same file as gen_lines.py; each line {id, text, gap, payoff?}).
Writes OUT.wav (48 kHz, -14 LUFS) and OUT.wav.picks.json (all scores, for the voice critic).

env (optional):
  FORCE='{"s12": "r2/7752ba_s12_31.wav"}'  force a critic-named take for a line
  LTEMPO='{"s12": 0.90}'                    per-line atempo for lines that run hyped/fast
  GAPSCALE=0.65                             scale every gap in lines.json (0.65 matched refs)

Score = 10*word accuracy + 1.2*pitch SD(st) + 4*share>180Hz - rising-ending penalty on statements
        - pace penalty outside 150-235 wpm - 2 if any word confidence < 0.35
        - 3 if the first 10 ms is louder than -50 dB (clipped onset) - 2 if a payoff line < 0.9 s.
Forced takes skip the choice but are still scored; check their on_db in picks.json.
Assembly: 110 ms tail ring-out with a curved fade, ~-70 dBFS band-limited room tone under the
whole VO (no digital-zero gaps), light EQ + 1.8:1 compression, loudnorm -14.
Adjust NUMS / ALIASES for the script at hand."""
import json, sys, os, re, glob, subprocess, difflib, tempfile
import numpy as np, librosa, soundfile as sf
from faster_whisper import WhisperModel
from scipy.signal import butter, sosfilt

DIRS, PREF, OUT = sys.argv[1].split(','), sys.argv[2], sys.argv[3]
FORCE = json.loads(os.environ.get('FORCE', '{}'))
LTEMPO = json.loads(os.environ.get('LTEMPO', '{}'))
GAPSCALE = float(os.environ.get('GAPSCALE', '1'))
lines = json.load(open('lines.json'))
m = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=6)
SR = 24000
NUMS = {'2': 'two', '3': 'three', '5': 'five', '6': 'six', '15': 'fifteen', '20': 'twenty', '35': 'thirtyfive', 'thirty-five': 'thirtyfive'}
ALIASES = {'noxie': 'noxy', 'knoxie': 'noxy', 'noxi': 'noxy', 'nocksee': 'noxy'}   # Whisper spelling variants

def toks(s):
    out = []
    for w in re.findall(r"[A-Za-z0-9'\-]+", s.lower()):
        w = NUMS.get(w, w).replace('-', '')
        out.append(ALIASES.get(w, w))
    return out

def trimmed(y, tail=0.03):
    _, idx = librosa.effects.trim(y, top_db=38)
    return y[max(0, idx[0] - int(0.03 * SR)):min(len(y), idx[1] + int(tail * SR))].copy()

report, chosen = {}, []
for ln in lines:
    lid = ln['id']
    cands = [FORCE[lid]] if lid in FORCE else sorted(sum([glob.glob(f'{d}/{PREF}_{lid}_*.wav') for d in DIRS], []))
    scored = []
    for c in cands:
        raw, _ = librosa.load(c, sr=SR, mono=True); y = trimmed(raw)
        segs, _ = m.transcribe(librosa.resample(y, orig_sr=SR, target_sr=16000).astype(np.float32), word_timestamps=True)
        ws = [w for s in segs for w in s.words]; heard = ' '.join(w.word for w in ws).strip()
        acc = difflib.SequenceMatcher(None, toks(ln['text']), toks(heard)).ratio()
        minp = min([w.probability for w in ws], default=0)
        f0, _, _ = librosa.pyin(y, fmin=60, fmax=350, sr=SR, frame_length=2048, hop_length=240)
        f = f0[~np.isnan(f0)]; st = 12 * np.log2(f / 112.0) if len(f) else np.zeros(1)
        sd = float(np.std(st)); hi = float(np.mean(f > 180)) if len(f) else 0.0
        med = float(np.median(f)) if len(f) else 0.0
        dur = len(y) / SR; wpm = len(toks(ln['text'])) / dur * 60
        tail = st[-25:] if len(st) > 40 else st
        rise = float(np.mean(tail[-8:]) - np.mean(tail[:8])) if len(tail) > 16 else 0.0
        pen_rise = 0 if ln['text'].strip().endswith('?') else max(0, rise - 1.0)
        pace_pen = max(0, wpm - 235) / 40 + max(0, 150 - wpm) / 40
        on_db = float(20 * np.log10(np.sqrt(np.mean(raw[:int(0.01 * SR)] ** 2)) + 1e-9))
        short_pen = 2 if (ln.get('payoff') and dur < 0.9) else 0
        score = (acc * 10 + sd * 1.2 + hi * 4 - pen_rise * 0.8 - pace_pen - (2 if minp < 0.35 else 0)
                 - (3 if on_db > -50 else 0) - short_pen)
        scored.append(dict(file=c, score=round(score, 2), acc=round(acc, 3), sd=round(sd, 2), hi=round(hi, 2), median_hz=round(med),
                           wpm=round(wpm), rise=round(rise, 1), minp=round(minp, 2), on_db=round(on_db, 1), dur=round(dur, 2), heard=heard))
    scored.sort(key=lambda d: -d['score']); report[lid] = scored; chosen.append((ln, scored[0]))

parts = []
for ln, best in chosen:
    raw, _ = librosa.load(best['file'], sr=SR, mono=True)
    y = trimmed(raw, tail=0.11)                                   # let the tail ring ~110 ms
    lt = LTEMPO.get(ln['id'])
    if lt:
        tf = tempfile.mktemp(suffix='.wav'); sf.write(tf, y, SR)
        y = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', tf, '-af', f'atempo={lt}', '-f', 'f32le',
                                                   '-ac', '1', '-ar', str(SR), '-']), np.float32).copy()
    fi, fo = int(0.01 * SR), int(0.09 * SR)
    y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    parts += [y, np.zeros(int(ln.get('gap', 0.3) * GAPSCALE * SR))]
voice = np.concatenate(parts)
tone = sosfilt(butter(2, [120, 4000], 'band', fs=SR, output='sos'), np.random.default_rng(3).standard_normal(len(voice)))
voice = voice + tone * 10 ** (-71 / 20) / (np.sqrt(np.mean(tone ** 2)) + 1e-12)   # measures ~-60 dBFS in gaps after mastering
sf.write(OUT + '.raw.wav', voice, SR)
af = ('highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=1.5,highshelf=f=7000:g=2.5,'
      'acompressor=threshold=-18dB:ratio=1.8:attack=10:release=150,loudnorm=I=-14:TP=-1.5:LRA=11')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + '.raw.wav', '-af', af, '-ar', '48000', OUT], check=True)
json.dump(report, open(OUT + '.picks.json', 'w'), indent=1)
for ln, b in chosen:
    print(ln['id'], os.path.basename(b['file']), {k: b[k] for k in ('score', 'sd', 'median_hz', 'wpm', 'on_db', 'dur')}, '|', b['heard'])
print('wrote', OUT)
