# Hook-bank mode: mine EVERY post of a creator for hooks

Use when the user wants "all of <creator>'s hooks", a hook bank / hook skill built from a creator, or hook patterns across a whole account (not just top-30 breakdowns). Output is a ranked, classified hook table + reusable templates, which then feeds a hook-writing skill.

## Procedure
`S=~/.hermes/skills/media/social-viral-analyzer/scripts`, `PY=~/.hermes/tools/social-scraper/.venv/bin/python`, `W=~/Desktop/Noxy/Noxy-<date>-<creator>-hooks`.

1. **Find every account.** web_search the creator name + TikTok/Instagram/YouTube; LinkedIn/link-in-bio pages list the handles. Creators often have an old account in a different niche (e.g. a comedy/meme era account with bigger raw views) - include it but tag the niche, because its hooks transfer differently.
2. **List all posts:** `$PY $S/list_all_tiktok.py <handle> $W` per handle, sequentially in one terminal call (background+notify if several; `&` in a foreground call is refused). Gives `list_<handle>.json` with views/likes/saves/captions for every post (550+ in one call).
3. **OCR binary (once, Mac):** `swiftc -O $S/ocr.swift -o ~/.hermes/tools/social-scraper/ocr`. On Windows skip this: `extract_hooks.py` uses `$S/ocr.py` (RapidOCR) when run with the venv python. macOS Vision OCR reads TikTok text hooks almost perfectly and is free/local - far cheaper than vision-reading hundreds of frames.
4. **Extract hooks:** test on 3 posts first (a `list_test.json` with 3 entries), then `python3 $S/extract_hooks.py $W <h1> <h2> --workers 6` as background+notify. Resumable (rerun skips done ids). ~60 posts/min. Videos are deleted after processing; only `hook_strips/<id>.jpg` (3 frames, 0-2.5 s) and `hooks_raw.jsonl` remain.
5. **Creator's own teaching (if they teach content):** pull their hook-tutorial YouTube transcripts with `yt-dlp --flat-playlist --print "%(id)s|%(view_count)s|%(title)s" https://www.youtube.com/@<handle>/videos`, then `yt-dlp --skip-download --write-auto-subs --sub-langs en --sub-format vtt -o "%(id)s" https://youtu.be/<id>` and strip tags + consecutive duplicate lines. Their stated framework explains WHY the hooks work and goes into the skill's rules.
6. **Table + batches:** `python3 $S/build_hook_table.py $W 8` -> `hooks_table.json` with `outlier` scores and `_batches/batch1..8.json`.
7. **Classify:** copy `templates/hook-classification-instructions.md` to `$W/_batches/INSTRUCTIONS.md`, fill in the account descriptions, then `delegate_task` 8 children (~100 rows each), each told to read INSTRUCTIONS.md, its batch file, and write `analysis<N>.json`. A fixed taxonomy in the instructions is what makes 8 children's labels aggregatable - don't let children invent types freely.
8. **Aggregate in Python, not by reading:** merge analyses with the table; per `hook_type` count, median outlier, % of posts with outlier >2; top templates by outlier; keyword frequency among winners vs flops. Then write the hook skill: rules (from the creator's framework + data), template bank grouped by type with real example + views, and a "how to generate a hook for the user's video" procedure.

## Pitfalls
- Rank by `outlier`, never raw views: an account's view level swings 10x across eras, so raw views just reward the peak era (and old meme accounts dwarf the current niche).
- Whisper on music-only intros returns `[Music]` / `(somber music)` or fake lyrics - the table builder drops bracketed/<3-word transcripts; children fall back to on-screen text.
- Instagram needs the scraper login (see SKILL.md); TikTok alone usually covers a creator's short-form catalog since most cross-post - say which platforms were covered.
