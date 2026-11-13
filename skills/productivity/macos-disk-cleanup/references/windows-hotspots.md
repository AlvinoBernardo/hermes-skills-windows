# Windows hotspots (verified on the user's Windows 11 PC; bash = git-bash, PowerShell via `-File`)

**Measure first, read-only:** `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <skill>/scripts/measure_windows.ps1 [-Deep]` — free space, known cache sizes, Recycle Bin (-Deep adds biggest profile / AppData\Local folders). ~15 s. Deletes nothing.

## ✅ Regenerating (safe, still ask first)
| Path | What | Clean |
|---|---|---|
| `%TEMP%` (`%LOCALAPPDATA%\Temp`), `C:\Windows\Temp` | Temp files (skip files in use) | Delete files older than ~1 day only |
| `%LOCALAPPDATA%\npm-cache` | npm cache | `npm cache clean --force` |
| `%LOCALAPPDATA%\uv\cache` | uv wheels/builds (7+ GB here) | `uv cache clean` (check `uv cache dir`) |
| `%LOCALAPPDATA%\pip\Cache` | pip cache | `pip cache purge` |
| `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache`, Edge twin | Browser cache (no logout) | Close the browser, then clear via browser settings |
| `%LOCALAPPDATA%\CrashDumps`, `...\Microsoft\Windows\WER` | Crash dumps | Delete |
| `%HERMES_HOME%\cache\scratch` (`%LOCALAPPDATA%\hermes\cache\scratch`) | Hermes temp | Only entries idle >60 min; spare in-use files |
| `%LOCALAPPDATA%\hermes\skills-backup-*`, `skills-replaced-*` | Safety copies of skills | Keep until the user confirms skills are fine |
| Recycle Bin | Already-deleted files (30+ GB here) | `Clear-RecycleBin -Force` — only after the user ok; it's their last chance to restore |
| Windows Update / component store | Superseded system files | `Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore` (admin shell; read-only report, says if cleanup is recommended). Clean via `cleanmgr /sagerun` or Settings → System → Storage → Temporary files. Never delete `WinSxS` by hand |

## 🟡 User data / ask
- `%USERPROFILE%\Downloads` — usually the biggest (100+ GB here). Categorise by extension (videos, installers `.exe/.msi`, models `.gguf`), flag secrets (keys, `.p12`, `.env`, adminsdk json) as must-keep.
- `%USERPROFILE%\.cache\huggingface`, `%USERPROFILE%\.cache\torch` — models; keep by default (TTS/ASR/CLIP may be in use).
- `%LOCALAPPDATA%\ms-playwright` — browsers agent tools need; keep.
- `node_modules`, game data, VMs / WSL (`wsl -l -v`, `%LOCALAPPDATA%\Packages\*\LocalState\ext4.vhdx`) — only on explicit ask.
- Storage Sense / Settings → System → Storage → Cleanup recommendations lists the same items with the OS's own safety rules; `cleanmgr` (Disk Cleanup) is the classic UI.

## Windows pitfalls
- Use `-File` for .ps1 (inline `$_` breaks in git-bash); in git-bash pass `C:/…` paths to native tools.
- `Get-ChildItem -Recurse` on big dirs is slow; measure targeted folders, not all of `C:\`.
- `du -sh` works in git-bash for single folders too.
