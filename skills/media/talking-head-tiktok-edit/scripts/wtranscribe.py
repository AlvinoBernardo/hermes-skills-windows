"""Shared Whisper wrapper for snip.py / tcat.py (word timestamps from a float32 16 kHz mono array).

  transcribe(x, prompt=None, language="en") -> {"segments": [{"words": [{"word", "start", "end"}]}]}
  (the same shape mlx_whisper.transcribe(..., word_timestamps=True) returns, so callers don't care which engine ran)

Engine: mlx-whisper (large-v3-turbo) on macOS when it is importable; otherwise whisper.cpp `whisper-cli`
(Windows/Linux, CUDA build on the PC). Always runs with condition_on_previous_text=False (whisper-cli: -mc 0).
whisper.cpp token times are loose, so word start/end are snapped to the 10 ms RMS envelope (still only +-0.3 s: use snip/tcat to see WHICH words are there, and place real cuts with dips.py/rms.py).
CLI (full pass, writes the cutN_transcript.json that render_ig.py reads):
  python wtranscribe.py IN.mov OUT.json [--prompt="jargon only"] [--lang=en]
Overrides: WHISPER_CLI=<exe>, WHISPER_MODEL=<ggml .bin>.
Windows model order: ggml-large-v3-turbo / ggml-medium.en / ggml-small.en / ggml-small in ~/.hermes/cache/whisper.
"""
import json, os, shutil, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

HOME = Path.home()


def _cli():
    for c in (os.environ.get("WHISPER_CLI"), shutil.which("whisper-cli"), str(HOME / "tools/whisper/Release/whisper-cli.exe"),
              "/opt/homebrew/bin/whisper-cli"):
        if c and Path(c).exists() or (c and shutil.which(c)):
            return c
    sys.exit("whisper-cli not found (set WHISPER_CLI)")


def _model():
    if os.environ.get("WHISPER_MODEL"):
        return os.environ["WHISPER_MODEL"]
    d = HOME / ".hermes/cache/whisper"
    for n in ("ggml-large-v3-turbo.bin", "ggml-medium.en.bin", "ggml-small.en.bin", "ggml-small.bin"):
        if (d / n).exists():
            return str(d / n)
    sys.exit(f"no ggml whisper model in {d} (set WHISPER_MODEL)")


def _mlx():
    if sys.platform != "darwin":
        return None
    try:
        import mlx_whisper
        return mlx_whisper
    except ImportError:
        return None


def _cpp(x, prompt, language):
    model = _model()
    lang = language or ("en" if model.endswith(".en.bin") else "auto")
    if model.endswith(".en.bin"):
        lang = "en"
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        cmd = [_cli(), "-m", model, "-f", wav, "-l", lang, "-ojf", "-of", os.path.join(td, "w"), "-np", "-mc", "0", "-t", "4"]
        if prompt:
            cmd += ["--prompt", prompt]
        subprocess.run(cmd, capture_output=True, check=True)
        j = json.load(open(os.path.join(td, "w.json"), encoding="utf-8", errors="replace"))
    segs = []
    for s in j.get("transcription", []):
        words = []
        for tok in s.get("tokens", []):
            t = tok.get("text", "")
            if not t or t.startswith("[_") or t.startswith("<|"):
                continue
            a, b = tok["offsets"]["from"] / 1000, tok["offsets"]["to"] / 1000
            if t.startswith(" ") or not words:
                words.append({"word": t, "start": a, "end": b})
            else:  # sub-word continuation
                words[-1]["word"] += t; words[-1]["end"] = b
        segs.append({"words": [w for w in words if w["word"].strip()]})
    allw = [w for s in segs for w in s["words"]]
    for i, w in enumerate(allw):
        _snap(x, w, allw[i + 1]["start"] if i + 1 < len(allw) else None)
    return {"segments": segs}


def _env(x, i0, i1, hop=160):
    seg = x[i0 * hop:i1 * hop]; seg = seg[:len(seg) // hop * hop]
    return 20 * np.log10(np.sqrt(np.mean(seg.reshape(-1, hop) ** 2, axis=1)) + 1e-9) if len(seg) >= hop else np.array([])


def _snap(x, w, next_start, drop_db=22):
    """whisper.cpp token times run loose (a word may start at the previous word's end, or even sit on silence).
    Snap start/end to the 10 ms RMS envelope: first/last frame inside the word within drop_db of its peak;
    if the word's own range is silent, search up to the next word's start instead."""
    n = len(x) // 160
    i0, i1 = max(0, int(w["start"] * 100)), min(n, int(w["end"] * 100) + 1)
    db = _env(x, i0, i1)
    if len(db) and db.max() < -45 and next_start is not None:
        i0, i1 = i1, min(n, int(next_start * 100) + 1)
        db = _env(x, i0, i1)
    if len(db) < 2:
        return
    ok = np.nonzero(db > max(db.max() - drop_db, -55))[0]
    if len(ok):
        w["start"], w["end"] = (i0 + ok[0]) / 100, (i0 + ok[-1] + 1) / 100


def transcribe(x, prompt=None, language=None):
    mlx = _mlx()
    if mlx:
        kw = dict(path_or_hf_repo="mlx-community/whisper-large-v3-turbo", word_timestamps=True, condition_on_previous_text=False)
        if prompt: kw["initial_prompt"] = prompt
        if language: kw["language"] = language
        return mlx.transcribe(x, **kw)
    return _cpp(x, prompt, language)


def ffmpeg_pcm(f, a, b):
    """float32 mono 16 kHz samples of f[a:b] (seconds)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-to", str(b), "-i", f,
                          "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def split_prompt(argv):
    """pull an optional --prompt=TEXT out of argv -> (prompt, remaining args)"""
    p = None; rest = []
    for a in argv:
        if a.startswith("--prompt="): p = a.split("=", 1)[1]
        else: rest.append(a)
    return p, rest


if __name__ == "__main__":
    prompt, rest = split_prompt(sys.argv[1:])
    lang = next((a.split("=", 1)[1] for a in rest if a.startswith("--lang=")), None)
    rest = [a for a in rest if not a.startswith("--lang=")]
    if len(rest) != 2:
        sys.exit(__doc__)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", rest[0]],
                               capture_output=True, text=True).stdout.strip())
    res = transcribe(ffmpeg_pcm(rest[0], 0, dur), prompt=prompt, language=lang or "en")
    json.dump(res, open(rest[1], "w", encoding="utf-8"), ensure_ascii=False)
    print(" ".join(w["word"].strip() for sg in res["segments"] for w in sg["words"]))
