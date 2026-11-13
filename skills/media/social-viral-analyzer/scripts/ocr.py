#!/usr/bin/env python3
"""Cross-platform stand-in for the macOS `ocr` binary (ocr.swift / Apple Vision).

Usage: ocr.py <image> [<image> ...]   (run with the social-scraper venv python)
Prints ONE JSON line per image, same contract as the Swift binary:
  {"path": "<image as given>", "lines": [{"t": "text", "conf": 0.97, "box": [x, y, w, h]}, ...]}
box is normalised 0-1, origin top-left; lines are sorted top-to-bottom, then left-to-right.
Engine: RapidOCR (PaddleOCR models on onnxruntime, local + free). Low-confidence junk (<0.5) is dropped.
"""
import json
import logging
import sys

from rapidocr import RapidOCR

logging.getLogger("RapidOCR").setLevel(logging.ERROR)
from PIL import Image

MIN_CONF = 0.5


def main(paths):
    eng = RapidOCR()
    logging.getLogger("RapidOCR").setLevel(logging.ERROR)
    for p in paths:
        lines = []
        try:
            w, h = Image.open(p).size
            r = eng(p)
            boxes = r.boxes if r.boxes is not None else []
            for box, txt, sc in zip(boxes, r.txts or [], r.scores or []):
                if not txt.strip() or float(sc) < MIN_CONF:
                    continue
                xs = [float(pt[0]) for pt in box]; ys = [float(pt[1]) for pt in box]
                x0, y0 = min(xs) / w, min(ys) / h
                lines.append({"t": txt.strip(), "conf": round(float(sc), 3),
                              "box": [round(x0, 4), round(y0, 4), round(max(xs) / w - x0, 4), round(max(ys) / h - y0, 4)]})
            lines.sort(key=lambda d: (round(d["box"][1], 2), d["box"][0]))
        except Exception as e:  # keep one line per input, like the Swift tool
            print(f"ocr: {p}: {e}", file=sys.stderr)
        print(json.dumps({"path": p, "lines": lines}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
