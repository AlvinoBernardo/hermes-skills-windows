---
name: macos-disk-cleanup
description: Use when the Mac or Windows PC is low on storage. Audit, explain, delete.
version: 1.1.0
platforms: [macos, windows]
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [macos, storage, disk, cleanup, xcode]
    related_skills: [noxy-tiktok-slideshows, ios-simulator-marketing-capture]
---

# macOS disk cleanup (app developer + content creator Mac)

## When to Use
The user says storage is full or low, asks what's taking up space, or asks what else they can delete.

The user builds iOS apps (Xcode, AI coding agents) and makes marketing videos and slideshows. Most of the space goes to developer leftovers, then raw media. Games and Hermes are minor (Hermes is about 15–18 GB).

## Procedure

1. **Measure first.** Run `df -h /System/Volumes/Data` (the Data volume is the real number; `/` shows only the sealed system). Then run `du -sh ~/* ~/.[!.]* | sort -rh`, then drill into the known hotspots in one batch (see `references/hotspots.md`). Record free kB before and after deleting so you can report real GB freed.
2. **Present in plain language, as tables.** Use these columns: What | Size | What it is | If deleted | My pick. Split into ✅ safe (regenerates, nothing lost) and 🟡 your stuff (you decide). The user asked repeatedly to have it broken down, so the first presentation must already say what each thing *is* and what they lose. Never give just names and sizes.
3. **Ask before deleting anything.** Use clarify with multi-select options. Nothing is deleted without an explicit pick. Do exactly what was picked: an item they didn't mention is NOT approved, so list it afterwards as "not touched".
4. **Delete in one batched terminal call.** Print a line per item and the GB freed. Calls that may run longer than 600 s auto-background, so wait for the completion notification instead of re-running.
5. **Report.** Give GB freed this round, total free now vs. at the start, what was kept and why, and any leftover decision.

## Always-on rules

- **Flag secrets as must-keep, never delete them.** Before any Downloads purge, list secret files explicitly and exclude them: Apple `AuthKey_*.p8` / `SubscriptionKey_*.p8` (Apple lets you download each one only once), `*firebase-adminsdk*.json`, `api-keys*.csv`, `.p12`, `.mobileprovision` and pricing CSVs.
- **Desktop/Noxy/Finished-slides holds the slideshow batching system.** It contains `.md` notes, `.json` (for example the male-format-rotation file), `.py` scripts, `.html` previews and fonts. Delete only media (`png/jpg/jpeg/webp/heic/gif/mp4/mov/zip/psd`) via `find -type f \( -iname ... \) -delete`, then `find -type d -empty -delete`. Never `rm -rf` the folder.
- **Simulators:** delete by last-used date (folder mtime older than ~2 weeks) and never the Booted one. Use `xcrun simctl delete <udid>`, not rm. Show which app (Noxy/Ikkimi/…) each simulator holds, because they hold test data and footage setups.
- **Xcode Archives:** keep the newest archive per app (they're needed for crash symbolication) and delete the rest.
- **Local AI model caches:** check which model the app actually uses before deleting (see `references/hotspots.md`, OpenWhispr). Keep HuggingFace TTS models by default, since they may power the Noxy voiceovers.
- **The user's standing "don't delete" choices** (ask again only if they bring it up): `node_modules`, Claude Desktop Cowork VM (`~/Library/Application Support/Claude/vm_bundles`), game data (Lunar Client, Roblox). Never touch Cursor `User/globalStorage` (chat history and state).
- Clearing `~/Library/Caches/<app>` does not log the user out, because logins live in Keychain and Application Support. Say so up front, since the user worries about it.

## Pitfalls

- Don't grep all of `~/Library/Application Support` for a string. It runs for minutes; scope it to the one app's directory.
- Use `LC_ALL=C` with grep/sort on binary or leveldb files, or sort dies with "Illegal byte sequence".
- When checking whether Downloads videos are backed up elsewhere, a same-size match against the asset libraries and Desktop is a quick proxy. Phone or iCloud copies can't be verified from the Mac, so ask the user.

See `references/hotspots.md` for paths, typical sizes and the exact clean commands.

## On Windows (this PC)
Same workflow (measure → table → ask → delete → report), different paths. The Mac-specific parts above (Xcode, simulators, `~/Library`, `df /System/Volumes/Data`) do not apply. Measure with `scripts/measure_windows.ps1` (read-only; run via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`), then see `references/windows-hotspots.md` for TEMP, npm/uv/pip/HF caches, Hermes `cache/scratch`, Recycle Bin, Storage Sense/`cleanmgr` and `DISM /AnalyzeComponentStore`. Nothing is deleted without the user's explicit pick; the secrets/"don't delete" rules above still apply (Downloads is the biggest item on this PC).
