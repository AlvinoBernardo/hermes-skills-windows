# Format-skill mode: learn a creator's whole format and turn it into a skill

Use this when the user wants to copy a creator's *style*: hooks, structure, the way they explain things, the visual look and the edit. The output is a class-level skill (for example `yap-video-format`), plus the usual deliverable folder.

## Procedure
`PY=~/.hermes/tools/social-scraper/.venv/bin/python`. `WV=~/.hermes/cache/scratch/wv/bin/python` is the mlx-whisper venv; recreate it with `uv venv wv -p 3.11 && uv pip install -p wv mlx-whisper` if it was pruned. Scripts live in `yap-video-format/scripts/` (`full_analyze.py`, `ig_owner_pass.py`, `CLASSIFY_INSTRUCTIONS.md`) and `mino-lee-hooks/scripts/` (`ig_reels_capture.py`, `ig_media_info.py`). Copy them into `$W/tools/`.

1. **Verify the handle.** Check the bio, follower count and post count on the IG profile with the logged-in scraper profile (a headless Playwright persistent context, reading `meta[name=description]`). Web-search the creator to get their bio context and find their other platforms.
2. **List every reel.** Run `ig_reels_capture.py <h> $W --scrolls 80`, then `ig_media_info.py <h> $W` (about 10 per minute, resumable). Run each in `terminal(background=true, notify=true)` and run them one after another, because they share the profile lock.
3. **Filter by owner.** `ig_owner_pass.py $W <h>` writes `owners.json`. Drop reels whose owner isn't the creator, unless the creator is a coauthor.
4. **Do the full breakdown of each reel.** `$WV tools/full_analyze.py $W <h>` (needs `tools/ocr` built with `swiftc -O social-viral-analyzer/scripts/ocr.swift -o $W/tools/ocr`). It takes about 15 s per reel. For each reel it keeps the mp4 and produces:
   - a 12-frame sheet and a hook strip
   - OCR of the first frames and mid frames
   - the scene-cut rate
   - a full transcript with word timestamps, plus wpm, pauses and the first-word time

   It's resumable. Run it in the background with a `while pgrep -f ig_media_info` loop so it picks up the entries that finish later.
5. **Build the table.** Outlier = views / the median of the 30 neighbours by date. Mark posts under 7 days old as fresh and leave them out of the stats.
6. **Classify.** Write `_batches/INSTRUCTIONS.md` from `CLASSIFY_INSTRUCTIONS.md`: update the creator description and keep a FIXED taxonomy for hook_type, topic_bucket, format, structure_type and the device lists. Then send about 29 rows each to 4 `delegate_task` children. Each child views the sheet and hook strip for every row, reads the full transcript, and writes `analysisN.json`.
7. **Aggregate in Python.** Median outlier, hit % (>2x) and flop % (<0.7x) per label and per device, plus length buckets, wpm, cut rate, text hook vs none, and "opens with the series line". Spot-check 2-3 hits yourself with `vision_analyze` on a stacked hook-strip image to write the visual spec: title box, caption style, receipts, set.
8. **Write the skill:**
   - **SKILL.md:** about 10 data-backed rules, a procedure for planning the user's video in his preferred shape, brand guardrails, and pitfalls.
   - **references/:** format-spec, script-templates (one per winning structure, each with its source hit), voice-and-humor, hook-bank (generated), what-flops (stat tables), the creator's own stated system (if they describe one), and top transcripts (generated).
   - **assets/:** the CSV.
   - Generate hook-bank, transcripts and CSV with Python straight from `merged.json`; never retype them.
9. **Deliver.** Numbered copies of the skill files, the top 10 videos, `_preview.html` (rules, win/flop tables and every hit card with its embedded hook strip), POSTING-NOTES with 5 starter ideas built only from the user's real material, `_work/` for the raw data, and a ZIP that excludes `_work/media`.

## Pitfalls
- **Analyze the full video, not just the first 6 s.** Format and structure live in the middle and the ending. The hook-only pipeline (`extract_hooks.py`) misses beats, joke rhythm and CTAs.
- **Cast mlx-whisper timestamps with `float()` before `json.dumps`.** They're numpy types, and the dump crashes after the transcription work is already done.
- **Translate the creator's edit rules into the user's own edit preferences in the skill.** One example is "a change every 3 s" done with pop-up cards rather than punch-in zooms (see talking-head-tiktok-edit). Otherwise the skill silently overrides corrections the user has already made.
- **Don't put the creator's identity jokes (race, sexuality) or personal facts into the user's ideas.** Keep the technique and have the user supply his own angles; ask, don't guess.
- **Use outlier, not raw views.** One mega-hit dominates raw-view averages.
