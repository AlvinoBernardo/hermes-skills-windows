# Disk hotspots and clean commands

## ✅ Regenerating (safe)
| Path | What | Clean |
|---|---|---|
| `~/Library/Developer/Xcode/DerivedData` | Xcode build cache | `rm -rf .../DerivedData/*` |
| `~/Library/Developer/XcodeBuildMCP/workspaces` | Build caches from AI agents (DerivedData twin, often 20 GB+) | `rm -rf .../workspaces/*` |
| `~/Library/Developer/Xcode/iOS DeviceSupport` | One folder per iOS version the phone ran | Keep the newest version only (case-match on its version string) |
| `~/Library/Developer/Xcode/Archives` | Every App Store upload | Keep newest per app: group `*/*.xcarchive` by first word of the name, sort by mtime, then rmtree the rest and remove empty date dirs |
| `~/.npm/_cacache` | npm cache | `npm cache clean --force` |
| `~/.cache/uv` | Python pkgs | `uv cache clean` |
| `~/Library/Caches/{com.spotify.client,com.canva.affinity,Google,org.swift.swiftpm,Codex,*ShipIt}` | App caches | `rm -rf <dir>/*`. Skip `ms-playwright*` because agent tools need those browsers |
| `~/.hermes/cache/scratch` | Hermes temp | `find ... -mindepth 1 -maxdepth 1 -mmin +60 -exec rm -rf {} +` (spares in-use files) |
| `Desktop/Noxy/*.zip` whose same-named folder exists | Delivery ZIP duplicates | `for z in *.zip; do [ -d "${z%.zip}" ] && rm "$z"; done` |

## 🟡 User data / ask
- `~/Library/Developer/CoreSimulator/Devices` is often 60–100 GB. List the devices with `xcrun simctl list devices -j`. For each one, read its size, the folder mtime (last used), its state, and the apps in `data/Containers/Bundle/Application/*/*.app`.
- Simulator runtimes (`xcrun simctl runtime list`) are about 8 GB each and live in system volumes.
- `~/Downloads`: categorize by extension (videos, `.dmg/.pkg` installers, `.gguf` models, folders with keyboard-mash names = test exports, `(1)`/`(2)` duplicates). Keep music `mp3/webm`, because they're used for edits.
- `Desktop/Noxy/Video-drafts`: drafts. The finals live in the dated `Noxy-<date>-*` folders.
- `Desktop/youtube video/episode N`: raw screen recordings.
- `~/.cache/huggingface/hub`: TTS/ASR models (Qwen3-TTS, Chatterbox, Kokoro, Whisper). Keep by default.
- `~/Library/Application Support/Claude/vm_bundles` (Cowork VM, ~11 GB) re-downloads when needed. The user declined deleting it.

## OpenWhispr: find the active model before deleting
Models: `~/.cache/openwhispr/models/*.gguf`. Settings are in the Electron localStorage leveldb (an append-only log, so the LAST occurrence per key wins):
```
cd ~/Library/Application\ Support/open-whispr/Local\ Storage/leveldb
LC_ALL=C grep -aboiE '(noteFormatting|dictationAgent|cleanup|chatAgent|translation)Model.{0,3}(qwen[^_]*|llama[^_]*)' 000003.log *.ldb | LC_ALL=C tr -cd '[:print:]\n'
```
Delete only the models that no key's last value points to. The speech model in `whisper-models/` is separate, so keep it.
