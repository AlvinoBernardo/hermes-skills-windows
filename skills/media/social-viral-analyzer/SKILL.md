---
name: social-viral-analyzer
description: "Use when analyzing a creator's viral posts, hooks or format."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [macos, windows]
metadata:
  hermes:
    tags: [instagram, tiktok, competitor-research, viral, hooks, slideshows, reels]
    related_skills: [noxy-tiktok-slideshows, competitor-profiling, short-form-video-critic-loop]
---

# Social Viral Analyzer

Given an Instagram and/or TikTok handle: pull the **last 60 posts**, rank by **views**, download the **top 30** (videos and slideshows), turn each into contact sheets + hook frames + voiceover transcript, analyze them with vision, and deliver a report (HTML preview + MD + CSV) with patterns, winners-vs-flops and ideas to steal for Noxy.

## When to Use
- "Analyze @x's Instagram / TikTok", "what's going viral for <competitor>", "download their top posts and break them down".
- Defaults (user-confirmed): pool = 60 most recent posts, analyze top 30 by views. Do both platforms when the user gives a handle for each (same handle is often used on both - confirm it exists).
- **Hook-bank mode** - "analyze ALL of <creator>'s videos for hooks", "build a hook skill from <creator>": process every post (not top 30), hooks only (first ~6 s: OCR'd text hook + whispered spoken line), ranked by per-account outlier score. Follow `references/hook-bank-mode.md` (scripts `list_all_tiktok.py`, `ocr.swift`, `extract_hooks.py`, `build_hook_table.py`; child instructions in `templates/hook-classification-instructions.md`).
- **Format-skill mode**: use for "learn <creator>'s format / style / how he explains things, build me a skill". Process every post with FULL transcripts and full-video contact sheets (not just the first 6 s), classify hook + structure + visual + voice devices, then write a class-level style skill. Follow `references/format-skill-mode.md`. The first example built this way is `yap-video-format`.
- **Bare profile URL with no instruction:** ask which mode they want (full viral analysis / hook bank / quick look / learn their format). The user's usual intent is "learn their format and turn it into a skill", so list that option.
- **YouTube Shorts creators** (many anime/commentary 'senpai' creators are YouTube-first): see the YouTube Shorts section under Procedure.
- **Music mode**: use for "what background music does <creator> use / find music from their videos that fits mine". Read IG's music tag, then Shazam the baked-in original audio. Follow `references/music-identification.md`.
- Don't use for: making/editing videos (noxy-* skills), critiquing one draft (short-form-video-critic-loop).

## Prerequisites (installed on this Mac)
- `PY=~/.hermes/tools/social-scraper/.venv/bin/python` (Python 3.12 venv with Playwright + its chromium).
- `yt-dlp` at `~/.local/bin/yt-dlp` (`uv tool install "yt-dlp[default,curl-cffi]"`). Always `export PATH="$HOME/.local/bin:$PATH"` in the same `terminal` call.
- `ffmpeg`, `whisper-cli` (brew `whisper-cpp`), model `~/.hermes/tools/social-scraper/models/ggml-base.en.bin`.
- **Instagram only - one-time login** in the scraper's own browser profile `~/.hermes/tools/social-scraper/ig-profile` (never the user's Chrome). Start with `terminal(background=true, notify=true)`: `$PY $S/ig_login.py 900`. A Chromium window opens on the IG login page; the USER logs in (recommend a secondary account). Exits printing `LOGGED_IN`. Never type IG credentials yourself. Re-run when `fetch_instagram.py` says the session expired.
- TikTok profiles need no login. **TikTok SEARCH needs login**: logged out, it redirects to explore, and the tag API returns empty. One-time setup: `terminal(background=true)`: `$PY $S/tt_login.py 1200` opens a VISIBLE window in its own profile `tt-profile`; the user logs in and solves any slider. The script may print TIMEOUT even when login worked, so verify with a test search. Then run `$PY $S/tt_search.py out.json "q1" "q2" ... --scrolls 8 --headed`, which gives rows sorted by plays (url, author, plays, saves, dur, created, music_title/author, desc). Headless mode gets only page 1 (~24 results); headed gets about 50-120 per query. The Hermes `local=true` browser is HEADLESS, so the user can never see its tabs or solve CAPTCHAs in it; don't send them there.

## Prerequisites on Windows (this PC)
- `PY=C:/Users/<you>/.hermes/tools/social-scraper/.venv/Scripts/python.exe` (Playwright, shazamio, RapidOCR, scipy). Scripts live in `C:/Users/<you>/AppData/Local/hermes/skills/media/social-viral-analyzer/scripts` (`S=`).
- yt-dlp: `~/.local/bin/yt-dlp.exe` (`uv tool install yt-dlp`); ffmpeg/ffprobe on PATH; whisper-cli `C:/Users/<you>/tools/whisper/Release/whisper-cli.exe` (CUDA; wants 16 kHz mono WAV, the scripts already convert); models `~/.hermes/tools/social-scraper/models/ggml-base.en.bin` and `~/.hermes/cache/whisper/ggml-small.en.bin`. The scripts find all of these themselves (PATH, then these fallbacks).
- **OCR:** there's no `swiftc`. `scripts/ocr.py` (RapidOCR, same one-JSON-line-per-image contract as `ocr.swift`) replaces it: `extract_hooks.py` picks it automatically when run with `$PY`, or set `OCR_BIN`. `scripts/format/` has the format-skill-mode scripts (TikTok verified, IG untested).
- Use `$PY` for every script (the system python has no deps). The scripts read/write UTF-8 explicitly, because Windows defaults to cp1252 and captions have emoji/CJK.
- Logins (`ig_login.py`, `tt_login.py`) are done by the user in the visible window, same as on the Mac.
- After a Mac->PC skill refresh, check that `scripts/ocr.py`, `scripts/format/` and these lookups still exist: the Mac's sync can overwrite them.

## Procedure
`S=~/.hermes/skills/media/social-viral-analyzer/scripts`. Work dir per platform: `W=~/Desktop/Noxy/Noxy-<YYYY-MM-DD>-viral-<handle>/<platform>`.

1. **Fetch** (`terminal`, timeout 900, or background+notify to run both platforms in parallel):
   - `$PY $S/fetch_tiktok.py <handle> $W --pool 60 --top 30`
   - `$PY $S/fetch_instagram.py <handle> $W --pool 60 --top 30`
   Done when `$W/manifest.json` exists and the log shows one `#NN` line per top post. Each post is in `media/NN_<id>/` (`video.mp4`, or `slide_XX.jpg` + `audio.*`).
2. **Prep:** `$PY $S/prep_media.py $W` -> per post `sheet.jpg` (12 frames across the video, or all slides), `hook.jpg` (frames 0-3s, videos), `transcript.txt` (videos). Done when every top post prints `sheet=y`.
3. **Analyze each post with vision.** For 30 posts use `delegate_task` with 3 parallel children x 10 posts. Give each child absolute paths to `hook.jpg`/`sheet.jpg` (pass them as `images` when <=8, else paths for `vision_analyze`), plus transcript, caption and stats from the manifest. Each returns JSON keyed by post id: `hook` (exact on-screen text or first spoken line), `hook_type` (listicle, POV, relatable pain, before/after, "things I wish I knew", hot take, tutorial, skit...), `format` (talking head, green screen, text over b-roll, photo carousel, screen recording...), `topic`, `structure` (beats / slide flow), `cta`, `why` (one specific sentence). Under ~10 posts, `vision_analyze` the sheets yourself. Proven pattern: write `_batch{1,2,3}.json` (id, rank, stats, caption, transcript, absolute hook/sheet paths) and have each child write `_analysis{N}.json`; afterwards move them into `_analysis_raw/` and delete the batch files. Also check posting dates: an account's "last 60" can be months old (Cal AI's were Mar-Jun 2025) - say so in the summary. Spot-check one child read with `vision_analyze` before synthesizing.
4. **Synthesize** into `$W/analysis.json` (schema in `build_report.py` docstring): `summary`, 4-7 `patterns` each citing ranks as evidence, `winners_vs_flops` (top 5 vs the bottom of the 60 using `posts.csv`/manifest: kind, duration, slide count, weekday, caption length, hook style), 5-8 `ideas` adapted to Noxy. Obey user rules: never call Noxy "free"; slideshow ideas follow noxy-tiktok-slideshows conventions. Merge child outputs under `posts`.
5. **Report:** `$PY $S/build_report.py $W` -> `report.html` (self-contained, thumbnails embedded), `report.md`, `posts.csv`.
6. **Deliver** per standing preference: folder `~/Desktop/Noxy/Noxy-<date>-viral-<handle>/` with `tiktok/` and/or `instagram/` subfolders, a `_preview.html` (copy of the report, or a combined one) and `POSTING-NOTES.md` (the ideas list); tested ZIP as a `MEDIA:` card (leave `.mp4`s out if the ZIP would exceed ~500 MB and say so); file tree in the reply; `open` the folder in Finder; show the report via `::preview{file=...}`.

## YouTube Shorts creators (no script needed)
1. **Find the platform first.** A handle the user gives may be a YouTube channel, not TikTok. Probe all at once: `yt-dlp --flat-playlist --playlist-end 3 --print "%(title)s | %(view_count)s" https://www.youtube.com/@<handle>/shorts` (case-insensitive). If that returns titles, use YouTube; the creator's TikTok/IG handles are usually in a long video's description (web_search "<name> youtube").
2. **List everything in seconds:** `yt-dlp --flat-playlist --print "%(id)s\t%(view_count)s\t%(title)s" .../@<h>/shorts > <h>_shorts.tsv` (newest first; also `/videos`). Flat listing has NO upload dates; sub count: `--skip-download --playlist-end 1 --print "%(channel_follower_count)s"`.
3. **Sample, don't download all:** top 12 by views + ~5 around the median + ~5 newest (+ the top 5 of the newest 150 for big accounts, to see what works NOW). Per short: `-f 'bv*[height<=480]+ba/b[height<=480]/b'`, `--print` upload_date/duration/likes/comments, whisper transcript, 12-frame 4x3 sheet + hook strip. Comments: `--write-comments --extractor-args 'youtube:max_comments=30'`.
4. **Compare eras by row index blocks** of the tsv (median views per block of 150-500) and map indices to dates from sampled uploads: big old accounts often peaked years ago, so report 'then vs now' and say which format still works today.
5. One subagent per creator (15-min deadline in the brief) writes `research/<handle>/REPORT.md`: format, exact hooks with views, beat structure, winners vs flops, persona, ideas for the user's app, 3 transcripts. Spot-check one sheet yourself before synthesizing.

## Subagents and PC load (user preference, every run)
Fan out with subagents for speed (one per creator or per post batch), but the user works and games on this PC while they run and wants subagents cut back when it gets slow. Check load first (`nvidia-smi --query-gpu=utilization.gpu --format=csv`; high GPU = he's gaming); then cap at ~2-3 heavy children, put in every child's brief: wrap ffmpeg/whisper/yt-dlp batches in `python ~/IkkimiAssets/scripts/run_low.py --cpus 4 <cmd>` and run downloads/transcribes sequentially, never in parallel. Tell the user the count, the core cap and the ETA in one line.

## Pitfalls
- **Verify the handle first.** Brand handles often aren't the obvious one (`@calai` is a random person; Cal AI is `@calai.app`). Check nickname/bio/follower count on the profile before fetching, and tell the user which account you analyzed.
- **"Account is private or has embedding disabled"** from yt-dlp: the script falls back to capturing the profile page's own `item_list` (max ~25-35 posts). If both fail, report it to the user - don't loop.
- **TikTok listing:** `yt-dlp https://www.tiktok.com/@handle` fails ("Unable to extract secondary user ID"). The script reads `secUid` from the profile page via Playwright, then lists `tiktokuser:<secUid>` - 60 posts with views in one call. Profile-page scrolling only yields 25 (page 2 is bot-blocked) - don't revert to it.
- **TikTok slideshows:** yt-dlp gets only the audio; slides are scraped from `<img>` tags on `/photo/<id>` (`photomode` CDN URLs). gallery-dl's TikTok extractor 403s.
- **Whisper on music** writes fake lyrics. Slideshows skip transcription; transcripts under 6 words are dropped. For videos with only a song, ignore the transcript.
- **Instagram logged-out** = login wall; `web_profile_info` returns no user and gallery-dl/instaloader fail. Hermes' own browser can't borrow real Chrome cookies while Chrome is open - hence the dedicated profile.
- **IG views:** only Reels expose play counts. Photo/carousel views are *estimated* (likes x the account's median views/likes on reels), flagged `views_estimated`, starred in the report - mention this in the summary.
- **IG rate limits:** fetch paginates 12/request with 1-2 s sleeps. Max ~3 IG accounts back-to-back; on 401/429 stop and tell the user, don't loop.
- Small accounts may have fewer than 60 posts - report the real `pool_size`.
- **`fetch_instagram.py` says `profile 404` (even for @instagram) while the session cookies are fine:** the `/api/v1/users/web_profile_info` and `/api/v1/feed/user/` endpoints now 404 to page fetches. Fallback that works: `scripts/format/ig_reels_capture.py <handle> <W> --scrolls 120` (captures the /reels/ tab's own GraphQL: views/likes/comments for every reel, no timestamps), then `yt-dlp --write-info-json` per `https://www.instagram.com/reel/<code>/` (gives timestamp + caption), then hand-build `manifest.json` (`view_rank`, `dir`, `top_n`, `fetched_at`) for `prep_media.py`/`build_report.py`. `build_report.py` only cards posts with `view_rank <= top_n`.
- **UGC-persona accounts** (an app's fake-ish 'girl learning X' accounts, e.g. @lucy_japanese for Kiku): check the bio link and search the app name on TikTok - the brand usually runs 3+ look-alike accounts on one template; analyse them as a network and say so.
- **The IG `/reels/` tab capture also picks up other creators' reels** (tagged, collab and suggested ones; 4 of 120 in one run). Before computing any stats, run the owner check in `yap-video-format/scripts/ig_owner_pass.py`. Keep collabs where the creator is listed as a coauthor.
- **Shazam (shazamio) hangs with no error when rate-limited**, e.g. when several agents share the IP. Wrap `recognize` in `asyncio.wait_for(..., 40-75)`, run ONE sequential worker with 4 s gaps (parallel workers get throttled within minutes), use unique temp WAV names per worker, and fall back to the caption's `Song:` tag.
- **Measure aspect ratio before assuming 9:16.** Viral anime edits were almost all 1:1, 4:3 or 16:9 uploads (117 of 118). `ffprobe` the downloads, and don't pad frames to 9:16 in contact sheets or you'll misread black bars as an editing choice.
- **Song ID without Shazam:** TikTok's own matched song sits in `itemStruct.music.tt2dsp.tt_to_dsp_song_infos` (in the video page's `__UNIVERSAL_DATA_FOR_REHYDRATION__`, logged-out headless works). Platform 1 is an Apple Music id, so `https://itunes.apple.com/lookup?id=<id>` gives title/artist. It resolved about 35% of 'original sound' edits instantly. Use it first, and Shazam only for what's left, because Shazam throttles when several agents share the IP. Script: `~/IkkimiAssets/research/recent/dsp_match.py`.
- **Sound trend check:** `/music/x-<music_id>` on the logged-in tt-profile gives the total "N videos" (page text; the SSR music-detail is often missing) and `/api/music/item_list` (~120-150 posts, sorted by popularity, not date: count posts from the last 7 days as a lower-bound recency signal). Script: `~/IkkimiAssets/research/recent/tt_music_pages.py`.
- **TikTok Creative Center popular music** (ads.tiktok.com/.../popular/music) now redirects to the "TikTok One Creative Suite" trends page (hashtag/video only; songs need a login), and Hermes browsers get a 403. Use trendingtiktoksongs.com (a mirror of the CC popular and viral charts per country, curl works) and soundmatcha.com/tiktok (growth rates) instead. Those charts are mainstream; anime-edit sounds have to come from search data.
- **The TikTok secUid lister crashing with `Cannot read properties of undefined (reading 'user')`** means there's no TikTok account with that handle. Web-search the creator's real handles or go IG-only and say so; don't retry.

- **Shazam rate-limits when several agents share the IP**: shazamio then retries forever and ignores `asyncio.wait_for`. Run each recognition in its own subprocess with a hard `timeout=90`, one 12 s window per video, in priority order (newest/highest views/day first). Fall back to the TikTok music tag, `song:` in captions, and on-screen lyrics (vision). Searching a lyric fragment usually names the track.
- **TikTok comments without login:** opening the video page and clicking the comment icon shows nothing logged-out. Instead, from that page call `fetch('/api/comment/list/?aid=1988&aweme_id=<id>&count=50&cursor=0',{credentials:'include'})` via `page.evaluate`. It returns JSON comments (with digg_count) headless and logged-out; dedupe by text. Script (Mac only, not on the PC): `~/IkkimiAssets/research/marketing-cta/r1_data/tt_video.py out.json <urls...>` (stats + up to 100 comments per video).
- **Keyword search without login:** `/discover/<slug>` pages (e.g. `learn-japanese-with-anime-app`, `tenmin-app`) load their video lists client-side. Open them in Playwright and walk every `/api/` JSON response for objects with `stats`+`author`+`desc`; that gives ~25 ranked posts per slug. Generic slugs mix in unrelated viral noise, so filter by caption. Script (Mac only): `r1_data/tt_discover.py out.json <slug...>`.
- **`fetch_tiktok.py` crashing with `TypeError: 'NoneType' object is not subscriptable`** (on e.g. slaxeditz or duolingodeutschland) means yt-dlp returned `None` entries. Filter them out (`for e in [e for e in entries if e]`); the Mac has a patched copy at `r1_data/fetch_tiktok_local.py`.
- **Niche trend scan on Windows without TikTok login** (used for 'what language-app formats are viral this month'): `scripts/tt_discover.py out.json <slug...>` (logged-out /discover pages, ~60 posts/slug, run 3 processes in parallel) → keyword-regex filter on captions, because discover pages on this PC are flooded with Indonesian-region trending noise → `scripts/tt_recent.py <dir> --n 40 <handles...>` (~7 s/account, secUid + yt-dlp flat with views/dates) for account medians, outliers and posts/week → cluster by caption/app tags and report median, %≥100k and %≥1M per cluster, not just top hits. `/tag/<x>` pages return nothing logged-out. Strip CRLF from handle lists written on Windows (`sed -i 's/\r$//'`), or the JSON filenames break.
- **Instagram search when logged in:** `/api/v1/tags/web_info/` returns 404. `scripts/ig_disc.py out.json "kw:<keywords>" "tag:<tag>"` opens the keyword-search and tag pages in the ig-profile and captures their JSON (~124 posts/query, likes/comments/taken_at, no play counts). Download single reels with `yt-dlp --cookies-from-browser "chromium:<ig-profile>/Default"`.
- **Check the 'proven' hooks you inherit:** @lucy_japanese (the source of the hook-to-demo 'Lucy hooks') had a 278-view median and 0 of its last 40 posts over 100k in Nov 2026. Before calling a hook proven, re-check the source account's current stats.
- **Trend research ('what's viral now')**: rank by views/day over the last 30-60 days (weight the last 30 d higher), not all-time views. All-time giants are often stale sounds.

- **Short text-overlay promo videos (≤15 s, many posts)**: run OCR (`ocr.swift` on the Mac, `scripts/ocr.py` on Windows) on 2 fps frames and collapse consecutive identical caption lines to get each video's hook and caption-beat timeline with timestamps. That beats viewing 30 contact sheets; view only 5-8 sheets to describe visuals. Filter on line height >0.018 and y between 0.12 and 0.6 to drop app-UI text.
- **Check whether a "creator" is actually an app-promo farm** (caption ends "App name: X", tiny follower count, 1+ posts/day, one template) before calling its posts viral. Report the account median and outlier multiples, not raw views.

## Verification
- `manifest.json`: `pool_size` ~60 (or account total), `top_n` 30, every top post has non-null `sheet`.
- Spot-check 2 sheets with `vision_analyze` - text legible.
- `report.html` shows stats, patterns, ideas and one card per top post.
