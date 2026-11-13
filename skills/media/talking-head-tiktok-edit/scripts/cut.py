"""Cut + grade a single SDR talking-head file into cut.mov and write cut.json (segment offsets).
Edit SEG (source seconds), run with system python3. Each segment gets 40ms audio fades; the
video gets a 0.2s fade-out at the end (end before the hand covers the lens).
"""
import subprocess, json, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else "sdr.mp4"
SEG = [(1.06, 7.40), (8.90, 16.05)]  # <- edit: (start, end) in source seconds
G = "eq=contrast=1.10:saturation=1.22:gamma=0.97,colorbalance=rm=-0.02:bm=0.03:bs=-0.02,unsharp=5:5:0.5"
fc = []
for i, (a, b) in enumerate(SEG):
    d = b - a
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30[v{i}]")
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={d-0.04:.3f}:d=0.04[a{i}]")
tot = sum(b - a for a, b in SEG)
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(SEG))) + f"concat=n={len(SEG)}:v=1:a=1[vc][a]")
fc.append(f"[vc]{G},fade=t=out:st={tot-0.2:.3f}:d=0.2[v]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "cut.mov"], check=True)
off = []; o = 0
for a, b in SEG: off.append((a, b, o)); o += b - a
json.dump({"total": tot, "segs": off}, open("cut.json", "w")); print(tot, off)
