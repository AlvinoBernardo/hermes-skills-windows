#!/usr/bin/env python3
"""Tile images onto A4 pages (300 dpi) to save paper.
Usage: contact_sheet.py OUT.pdf img1 img2 ... [--cols 2 --rows 3]
Writes a multi-page PDF plus OUT_dir/_preview.png (first page)."""
import argparse, os
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("out"); p.add_argument("images", nargs="+")
p.add_argument("--cols", type=int, default=2); p.add_argument("--rows", type=int, default=3)
a = p.parse_args()
W, H, m, g = 2480, 3508, 90, 50
cw = (W - 2*m - (a.cols-1)*g) // a.cols
ch = (H - 2*m - (a.rows-1)*g) // a.rows
per = a.cols * a.rows
pages = []
for start in range(0, len(a.images), per):
    page = Image.new("RGB", (W, H), "white")
    for i, f in enumerate(a.images[start:start+per]):
        im = Image.open(f).convert("RGB")
        s = min(cw/im.width, ch/im.height)
        im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)
        c, r = i % a.cols, i // a.cols
        page.paste(im, (m + c*(cw+g) + (cw-im.width)//2, m + r*(ch+g) + (ch-im.height)//2))
    pages.append(page)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
pages[0].save(a.out, resolution=300, save_all=True, append_images=pages[1:])
prev = os.path.join(os.path.dirname(os.path.abspath(a.out)), "_preview.png")
pages[0].resize((620, 877)).save(prev)
print(a.out, f"{len(pages)} page(s)", prev)
