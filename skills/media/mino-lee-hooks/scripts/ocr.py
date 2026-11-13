#!/usr/bin/env python3
"""Cross-platform stand-in for ocr.swift (Apple Vision) - RapidOCR on onnxruntime, local and free.

Usage: ocr.py <image> [<image> ...]      (run with the social-scraper venv python, see SKILL.md)
Prints ONE JSON line per image, same contract as the Swift binary (t / y / h) plus conf and box:
  {"path": "<as given>", "lines": [{"t": "text", "y": 0.12, "h": 0.04, "conf": 0.97, "box": [x, y, w, h]}, ...]}
y = vertical centre and h = height, normalised 0-1, origin TOP-left; box is [x, y, w, h] normalised.
Lines are sorted top to bottom. Detections under 0.5 confidence are dropped (Swift used 0.4).
Same engine/output as social-viral-analyzer/scripts/ocr.py.
"""
import json
import logging
import sys

MIN_CONF = 0.5


def main(paths):
    from PIL import Image
    from rapidocr import RapidOCR

    logging.getLogger("RapidOCR").setLevel(logging.ERROR)
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
                xs = [float(pt[0]) for pt in box]
                ys = [float(pt[1]) for pt in box]
                x0, y0 = min(xs) / w, min(ys) / h
                bw, bh = max(xs) / w - x0, max(ys) / h - y0
                lines.append({"t": txt.strip(), "y": round(y0 + bh / 2, 4), "h": round(bh, 4),
                              "conf": round(float(sc), 3), "box": [round(x0, 4), round(y0, 4), round(bw, 4), round(bh, 4)]})
            lines.sort(key=lambda d: (round(d["y"], 2), d["box"][0]))
        except Exception as e:  # keep one output line per input, like the Swift tool
            print(f"ocr: {p}: {e}", file=sys.stderr)
        print(json.dumps({"path": p, "lines": lines}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows pipes default to cp1252
    except Exception:
        pass
    main(sys.argv[1:])
