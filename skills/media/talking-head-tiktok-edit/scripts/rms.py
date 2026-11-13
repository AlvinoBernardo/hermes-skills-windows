"""Print an RMS envelope (dBFS) to place cuts in dips / find word onsets / find a song section onset.
Usage (system python3):  python3 rms.py FILE START END WINDOW_S
  e.g. 20ms windows around a cut:   python3 rms.py sdr.mp4 23.2 24.4 0.02
       0.5s windows over a song:    python3 rms.py track.mp3 55 100 0.5
"""
import subprocess, numpy as np, sys
f, a, b, w = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-to", str(b), "-i", f,
                                  "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
n = int(16000 * w)
for i in range(len(x) // n):
    r = np.sqrt(np.mean(x[i*n:(i+1)*n] ** 2)); db = 20 * np.log10(r + 1e-9)
    print(f"{a+i*w:6.2f} {db:6.1f} " + "#" * int(max(0, db + 60)))
