#!/usr/bin/env python3
"""Per-frame head-turn / gaze metrics (Windows/Linux port of facepose.swift, which uses macOS Vision).
Finds where the speaker looks away (reading notes). Same CLI and output as the Swift tool.

Frames: ffmpeg -i sdrN.mp4 -vf "fps=10,scale=360:-1" -q:v 4 frN/%05d.jpg
Run:    python facepose.py frN > pN.txt   ->  one line per frame: "00001.jpg yaw pitch nose gx gy open"   (frame i = t*10+1)
        no face found => the fields are -9.000.
Python: C:/Users/<you>/.hermes/tools/talking-head/.venv/Scripts/python.exe (mediapipe 1.x, opencv, numpy);
        model: ~/.hermes/tools/talking-head/models/face_landmarker.task (auto-downloaded if missing; env FACE_LANDMARKER_MODEL overrides).

Fields (largest face only):
  yaw, pitch  radians from MediaPipe's facial transformation matrix. yaw > 0 = face turned toward frame-RIGHT (same side
              as positive `nose`). Apple Vision's yaw has a different scale, so the old 0.38 yaw cut-off is only a start; calibrate.
  nose        (nose-bridge x - midpoint of the eyes' x) / eye distance. Positive = nose displaced toward frame-right. Same definition as
              the Swift tool, so the old threshold (> 0.12 = turned) is a reasonable start, but the landmark sets differ: calibrate.
  gx, gy      mean pupil position inside the eye box, 0..1 (gx left->right in the image, gy bottom->top, like Vision).
  open        eye-box height / width (blink / looking-down proxy).
Calibrate per shoot: print the values at 2-3 frames you KNOW are reading vs talking before trusting a threshold.
"""
import math, os, sys, urllib.request
from pathlib import Path

import numpy as np

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL = Path(os.environ.get("FACE_LANDMARKER_MODEL") or Path.home() / ".hermes/tools/talking-head/models/face_landmarker.task")

# MediaPipe face-mesh index sets (image-left / image-right eye, iris centres, nose-bridge ridge)
EYE_L = [33, 7, 163, 144, 145, 153, 154, 155, 133, 246, 161, 160, 159, 158, 157, 173]    # on the image-left side of the face
EYE_R = [263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]
IRIS_L, IRIS_R = 468, 473
NOSE_CREST = [168, 6, 197, 195, 5]


def landmarker():
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    opts = vision.FaceLandmarkerOptions(
        base_options=mpt.BaseOptions(model_asset_path=str(MODEL)),
        running_mode=vision.RunningMode.IMAGE, num_faces=3,
        output_facial_transformation_matrixes=True)
    return mp, vision.FaceLandmarker.create_from_options(opts)


def metrics(lm, mat):
    P = np.array([[p.x, p.y] for p in lm])                      # normalised image coords, y down
    ec_l, ec_r = P[EYE_L].mean(0), P[EYE_R].mean(0)
    d = abs(ec_r[0] - ec_l[0]) + 1e-6
    nose = (P[NOSE_CREST][:, 0].mean() - (ec_l[0] + ec_r[0]) / 2) / d
    yaw = pitch = -9.0
    if mat is not None:
        R = np.array(mat)[:3, :3]
        R = R / (np.linalg.norm(R[:, 0]) + 1e-9)                # strip the uniform scale
        # MediaPipe canonical space: +x right, +y up, +z toward the camera. Image-right turn => nose points to +x.
        yaw = math.atan2(R[0, 2], R[2, 2])
        pitch = math.atan2(-R[1, 2], math.hypot(R[0, 2], R[2, 2]))
    gx = gy = op = -9.0
    if len(lm) > 477:
        rel = []
        for eye, iris in ((EYE_L, IRIS_L), (EYE_R, IRIS_R)):
            xs, ys = P[eye][:, 0], P[eye][:, 1]
            w, h = xs.max() - xs.min() + 1e-6, ys.max() - ys.min() + 1e-6
            rel.append(((P[iris][0] - xs.min()) / w, 1 - (P[iris][1] - ys.min()) / h, h / w))   # y flipped: up = 1
        gx, gy, op = (sum(r[i] for r in rel) / 2 for i in range(3))
    return yaw, pitch, nose, gx, gy, op


def main(d):
    mp, fl = landmarker()
    files = sorted(f for f in os.listdir(d) if f.lower().endswith(".jpg"))
    for f in files:
        try:
            img = mp.Image.create_from_file(os.path.join(d, f))
        except Exception:
            continue
        res = fl.detect(img)
        vals = (-9.0,) * 6
        if res.face_landmarks:
            i = max(range(len(res.face_landmarks)), key=lambda k: np.ptp([p.x for p in res.face_landmarks[k]]))
            mats = res.facial_transformation_matrixes
            vals = metrics(res.face_landmarks[i], mats[i] if mats else None)
        print(f, "%.3f %.3f %.3f %.3f %.3f %.3f" % vals)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
