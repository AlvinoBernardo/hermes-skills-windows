#!/usr/bin/env python3
"""Windows/Linux stand-in for the Mac-only Apple Vision `ugc_frames/_face.swift`.

Finds the face in each image and prints brow / eye / jaw y (pixels) plus the hook-text band
the noxy-hook-demo skill wants: forehead band 170..(brow-25) if it fits, else jaw+30..1480.

Usage:  python face_band.py frame1.jpg [frame2.jpg ...]      -> one JSON line per image
Needs opencv-python (cv2 with CascadeClassifier + cv2.data.haarcascades) and numpy:
the Ikkimi engine venv has both (C:/Users/<you>/IkkimiAssets/engine/.venv/Scripts/python.exe).
Haar is coarser than Vision: brow is estimated from the eyes, jaw from the face box. ALWAYS eyeball the
result on a frame before trusting it (draw the band; hook text must never cover eyes).
"""
import json
import sys

import cv2
import numpy as np


def face_metrics(path):
    try:
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)  # unicode-safe on Windows
    except OSError:
        img = None
    if img is None:
        return {"path": path, "error": "unreadable"}
    h, w = img.shape[:2]
    g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    hc = cv2.data.haarcascades
    fc = cv2.CascadeClassifier(hc + "haarcascade_frontalface_default.xml")
    ec = cv2.CascadeClassifier(hc + "haarcascade_eye.xml")
    faces = fc.detectMultiScale(g, 1.1, 5, minSize=(max(40, w // 10), max(40, w // 10)))
    if len(faces) == 0:  # profile / tilted fallback
        faces = cv2.CascadeClassifier(hc + "haarcascade_profileface.xml").detectMultiScale(g, 1.1, 4)
    if len(faces) == 0:
        return {"path": path, "size": [w, h], "face": None}
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    eyes = ec.detectMultiScale(g[y:y + fh // 2 + fh // 8, x:x + fw], 1.1, 5, minSize=(fw // 8, fw // 8))
    if len(eyes):
        eye_y = y + float(np.mean([ey + eh / 2 for ex, ey, ew, eh in eyes]))
        eye_h = float(np.mean([eh for ex, ey, ew, eh in eyes]))
    else:
        eye_y, eye_h = y + fh * 0.38, fh * 0.2
    brow_y = eye_y - eye_h * 0.7
    jaw_y = y + fh
    band = (170, int(brow_y - 25)) if brow_y - 25 - 170 >= 120 else (int(jaw_y + 30), 1480)
    return {"path": path, "size": [w, h], "face": [int(x), int(y), int(fw), int(fh)],
            "eye_y": round(eye_y), "brow_y": round(brow_y), "jaw_y": round(jaw_y),
            "text_band": list(band), "n_eyes": int(len(eyes))}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        print(json.dumps(face_metrics(p)), flush=True)
