"""Find exact word boxes in a screenshot (tweets, docs) for highlight markers.
Usage: python3 words_box.py IMG x0 y0 x1 y1   -> prints each text line's y-range and word x-ranges (source px).
Dark text on a light background; a column gap of more than 9px splits words (2x screenshots). Short words can merge, so count from the line end.
"""
import sys, numpy as np
from PIL import Image
f = sys.argv[1]; x0, y0, x1, y1 = map(int, sys.argv[2:6])
a = np.asarray(Image.open(f).convert("L").crop((x0, y0, x1, y1))) < 120
rows = a.any(1); lines = []; inl = False
for y, r in enumerate(rows):
    if r and not inl: s = y; inl = True
    if not r and inl: lines.append((s, y)); inl = False
if inl: lines.append((s, len(rows)))
for (s, e) in lines:
    if e - s < 12: continue
    cols = a[s:e].any(0); words = []; inw = False; gap = 0
    for x, c in enumerate(cols):
        if c:
            if not inw: ws = x; inw = True
            gap = 0; we = x
        elif inw:
            gap += 1
            if gap > 9: words.append((ws, we)); inw = False
    if inw: words.append((ws, we))
    print(f"line y {s+y0}-{e+y0}:", " ".join(f"{i}:{w[0]+x0}-{w[1]+x0}" for i, w in enumerate(words)))
