// macOS Vision OCR. Build once:  swiftc -O ocr.swift -o ~/.hermes/tools/social-scraper/ocr
// usage: ocr img1 img2 ... ; prints one JSON line per image {path, lines:[{t,y,h}]} sorted top->bottom
import Foundation
import Vision
import AppKit
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("{\"path\":\"\(path)\",\"lines\":[]}"); continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for o in (req.results ?? []) {
        if let c = o.topCandidates(1).first, c.confidence > 0.4 {
            let b = o.boundingBox
            lines.append(["t": c.string, "y": Double(1 - b.midY), "h": Double(b.height)])
        }
    }
    lines.sort { ($0["y"] as! Double) < ($1["y"] as! Double) }
    let data = try! JSONSerialization.data(withJSONObject: ["path": path, "lines": lines])
    print(String(data: data, encoding: .utf8)!)
}
