#!/usr/bin/env python3
"""OCR with boxes (Windows/Linux port of ocrbox.swift, which uses macOS Vision).
Usage: python ocrbox.py img1 img2 ...   -> one JSON line per image:
  {"path": "...", "lines": [{"t": "text", "x": 0.1, "y": 0.2, "w": 0.3, "h": 0.05, "conf": 0.97}, ...]}
x,y,w,h are normalised 0-1, origin TOP-left (same as the Swift tool: y = 1 - maxY); lines sorted top to bottom.
Engine: RapidOCR (ONNX). Run with a venv that has rapidocr + pillow, e.g.
  C:/Users/<you>/.hermes/tools/social-scraper/.venv/Scripts/python.exe ocrbox.py img.jpg
Lines at confidence <= 0.4 are dropped (same cut as the Swift tool). Same engine as social-viral-analyzer/scripts/ocr.py (which uses box=[x,y,w,h]).
"""
import json, logging, sys

from PIL import Image


def main(paths):
    from rapidocr import RapidOCR
    logging.getLogger("RapidOCR").setLevel(logging.ERROR)
    eng = RapidOCR()
    logging.getLogger("RapidOCR").setLevel(logging.ERROR)
    for p in paths:
        lines = []
        try:
            w, h = Image.open(p).size
            r = eng(p)
            for box, txt, sc in zip(r.boxes if r.boxes is not None else [], r.txts or [], r.scores or []):
                if not txt.strip() or float(sc) <= 0.4:
                    continue
                xs = [float(pt[0]) for pt in box]; ys = [float(pt[1]) for pt in box]
                lines.append({"t": txt.strip(), "x": min(xs) / w, "y": min(ys) / h, "w": (max(xs) - min(xs)) / w,
                              "h": (max(ys) - min(ys)) / h, "conf": round(float(sc), 3)})
            lines.sort(key=lambda d: d["y"])
        except Exception as e:  # one line per input, like the Swift tool
            print(f"ocrbox: {p}: {e}", file=sys.stderr)
        print(json.dumps({"path": p, "lines": lines}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
