import Foundation
import Vision
import AppKit
// usage: ocr img1 img2 ... ; prints one JSON line per image
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("{\"path\":\"\(path)\",\"text\":[]}"); continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for o in (req.results ?? []) {
        if let c = o.topCandidates(1).first, c.confidence > 0.4 {
            let b = o.boundingBox
            lines.append(["t": c.string, "x": Double(b.minX), "y": Double(1 - b.maxY), "w": Double(b.width), "h": Double(b.height)])
        }
    }
    lines.sort { ($0["y"] as! Double) < ($1["y"] as! Double) }
    let data = try! JSONSerialization.data(withJSONObject: ["path": path, "lines": lines])
    print(String(data: data, encoding: .utf8)!)
}
