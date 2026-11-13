// Per-frame head-turn / gaze metrics with macOS Vision, to find where the speaker looks away (reading notes).
// Build: swiftc -O facepose.swift -o facepose
// Frames: ffmpeg -i sdrN.mp4 -vf "fps=10,scale=360:-1" -q:v 4 frN/%05d.jpg
// Run:   ./facepose frN 2>/dev/null > pN.txt   -> "00001.jpg yaw pitch nose gx gy open" (frame i = t*10+1)
// IMG_1467 calibration: reading/turned to notes => nose > 0.12 or yaw > 0.38; facing the lens => nose < 0.10, yaw < 0.2.
// Calibrate per shoot: print the values at 2-3 frames you KNOW are reading vs talking before trusting the threshold.
import Vision
import AppKit
let dir = CommandLine.arguments[1]
let files = try! FileManager.default.contentsOfDirectory(atPath: dir).filter{$0.hasSuffix(".jpg")}.sorted()
func c(_ r: VNFaceLandmarkRegion2D) -> (Double, Double) { let p = r.normalizedPoints; return (p.map{Double($0.x)}.reduce(0,+)/Double(p.count), p.map{Double($0.y)}.reduce(0,+)/Double(p.count)) }
for f in files {
  let url = URL(fileURLWithPath: dir + "/" + f)
  guard let img = NSImage(contentsOf: url), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
  let r1 = VNDetectFaceRectanglesRequest(); r1.revision = VNDetectFaceRectanglesRequestRevision3
  let r2 = VNDetectFaceLandmarksRequest()
  let h = VNImageRequestHandler(cgImage: cg, options: [:])
  try? h.perform([r1, r2])
  var yaw = -9.0, pitch = -9.0
  if let o = (r1.results ?? []).max(by: {$0.boundingBox.width < $1.boundingBox.width}) { yaw = o.yaw?.doubleValue ?? -9; pitch = o.pitch?.doubleValue ?? -9 }
  var nose = -9.0, gx = -9.0, gy = -9.0, open = -9.0
  if let o = (r2.results ?? []).max(by: {$0.boundingBox.width < $1.boundingBox.width}), let lm = o.landmarks, let le = lm.leftEye, let re = lm.rightEye, let n = lm.noseCrest {
    let a = c(le), b = c(re), nc = c(n); let d = abs(a.0 - b.0) + 1e-6
    nose = (nc.0 - (a.0 + b.0) / 2) / d
    if let lp = lm.leftPupil, let rp = lm.rightPupil {
      func rel(_ p: VNFaceLandmarkRegion2D, _ e: VNFaceLandmarkRegion2D) -> (Double, Double, Double) {
        let pp = p.normalizedPoints[0]; let xs = e.normalizedPoints.map{Double($0.x)}; let ys = e.normalizedPoints.map{Double($0.y)}
        return ((Double(pp.x)-xs.min()!)/(xs.max()!-xs.min()!+1e-6), (Double(pp.y)-ys.min()!)/(ys.max()!-ys.min()!+1e-6), (ys.max()!-ys.min()!)/(xs.max()!-xs.min()!+1e-6))
      }
      let p = rel(lp, le), q = rel(rp, re); gx = (p.0 + q.0) / 2; gy = (p.1 + q.1) / 2; open = (p.2 + q.2) / 2
    }
  }
  print(f, String(format: "%.3f %.3f %.3f %.3f %.3f %.3f", yaw, pitch, nose, gx, gy, open))
}
