---
name: mino-lee-hooks
description: "Use when the user needs a hook for a video or slideshow."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, windows]
metadata:
  hermes:
    tags: [hooks, tiktok, reels, scripting, viral, mino-lee, talking-head]
    related_skills: [talking-head-tiktok-edit, noxy-tiktok-slideshows, noxy-ai-fitness-videos, social-viral-analyzer, short-form-video-critic-loop]
---

# Mino Lee Hook Bank

Writes ranked, ready-to-film hooks from a bank built out of Mino Lee's **talking videos** that built his personal brand. That's 1,139 videos in total:
- **Instagram @minolee.mp4**: all 681 reels (Jul 2022 to Oct 2026, 171M views). 600 of them are talking videos.
- **TikTok @mino.mp4**: 539 talking videos.

For each video, the first 3 s were OCR'd and transcribed, then classified by hook type and format, and scored against the posts around it. The bank also draws on his own hook teaching from 4 YouTube lessons.

**The user does NOT want skits analyzed.** Skits, memes, lip-syncs, music montages, a paid ad and the whole @mino1ee comedy account (236 TikToks) are excluded from the bank, the formulas and the stats. Never suggest skit or meme formulas from him.

## When to Use
- "Give me a hook for my video about X", "write hooks for this script", "what should I say in the first 3 seconds", "fix this hook".
- Any talking-head video, Reel, TikTok or slideshow cover text, for either brand (personal brand founder videos or Noxy).
- Don't use for: full scripts beyond the first ~10 s (use the brand's video skill), or analyzing a new creator (use social-viral-analyzer, or the scripts here).

## Files
- `references/reused-hooks.md`: **for "proven hooks" requests.** The phrases he reused across many videos, with uses-to-viral counts, examples and misses, and the one-hit wonders to avoid.
- `references/hook-formulas.md`: **start here.** The 28 proven formulas ranked by outlier, tagged IG/TT. Each has the original hook, its stats, a fill-in template and brand examples.
- `references/hook-bank.md`: all 229 proven talking hooks word for word, grouped by hook type, with links: 116 IG, 113 TT. "Proven" means at least 2x the account's local median, plus at least 200k views on IG (median there is about 89k) or 40k on TT.
- `references/mino-framework.md`: his own rules. Copy, then understand the keywords, then maximize. Demand, value per second and social proof. The 6-point hook checklist.
- `references/what-flops.md`: a stats table by hook type, plus the patterns that reliably flop. Check every draft against it.
- `references/mino-music.md`: the background music he uses on his talking reels (Shazam-identified), ranked by reuse, with best outlier and the start offsets he uses. Use it when the user asks for "music like Mino's".
- `assets/mino_hooks_all.csv`: all 1,139 talking videos (platform, hook, text hook, format, type, template, devices, views, outlier, url) for custom filtering in python.
- `scripts/`: the extraction pipeline. Re-run it to refresh this bank or to build one for another creator (see Refresh).

## Procedure (giving the user a hook)
1. **Get the real payoff.** You need:
   - what the video actually delivers (the tip, story, result or number)
   - the brand (personal brand vs Noxy; check the right asset library per memory)
   - the format (talking head, slideshow cover, skit, b-roll + text)
   - any true proof numbers

   If the user gives only a topic, ask for 1-3 sentences of the actual content, or the script. Mino's rule: hooks written without the script come out vague. Never invent results (followers, $, kg lost). Leave `[your real number]` placeholders instead.
2. **Pick 3-4 formula families** from `hook-formulas.md` that honestly fit the payoff. Ask which platform the post is mainly for. For Instagram, favour live challenges, life stories, guilty-pleasure defenses and pain callouts. For TikTok, favour tactic + proof. This is hook/video alignment: a hook that lies wins the first 3 s but kills retention. Prefer the top tier:
   - definitive explainer
   - ladder / levels
   - fear callout, then flip
   - specific tactic + "every single time"
   - quotable rule + big proof
   - contrarian "the reason your X..."
   - confession where a good thing brings a bad emotion
3. **Write 10 variations.** Run each through the checklist in `mino-framework.md`:
   - clarity: understood in one read, simple words
   - niche keywords that trigger emotion ("view jail", "f*ck-you money", "lock in")
   - specificity and numbers
   - novelty (the "purple cow": something that stands out)
   - alignment with what the video delivers
   - value per second: big value, short time
   - proof, or "I know you're probably thinking", in sentence 2
   - a first-frame visual

   Drop any variation that matches a pattern in `what-flops.md`.
4. **Read each one aloud** (Mino says 5 times). The spoken hook should land in about 3 s, roughly 8-16 words. The on-screen text hook can be a shorter, punchier version.
5. **Deliver the top 3-5, ranked.** For each give:
   - **Spoken hook** (first sentence) + **sentence 2** (proof or relatability)
   - **On-screen text hook** (what goes on the cover or first frame)
   - **First-frame visual** (what's in shot at 0 s: prop, proof screenshot, costume, setting)
   - **Based on:** the Mino original, its views and its outlier (e.g. "how to escape every level of view jail": 3.8M, 139x)

   Then add one line on why #1 is the pick, and offer more variations of the winning family. If the user wants to see a source video ("which one?"), download it and send it as a MEDIA file: TikTok via yt-dlp, Instagram via `video_url` in `list_ig_minolee.mp4.json` (in the analysis `_work` dir).

## Brand rules that still apply
- Never call Noxy "free" anywhere (hook, text, CTA).
- Noxy slideshow covers: 80px Arial Black hook text; wrap to 3 rows rather than shrink. Male @noxy.app slideshows use the fox manga workout format (see noxy-tiktok-slideshows). This skill only supplies the words.
- Noxy fox videos: the hook voice still goes through the voice critic loop (noxy-ai-fitness-videos).

## Key findings (why these formulas)
- **Instagram (600 talking reels):**
  - `challenge_experiment` ("is it possible to [X] in [tiny time]?") is the best type by far: 2.16x median, 52% beat 2x, 2% flop. It produced 9 of the top 15 reels (up to 5.8M views).
  - On IG a curiosity gap gets 1.77x vs 0.86x without, stakes 1.37x vs 0.90x, novelty 1.29x vs 0.90x. Numbers alone do NOT help on IG (0.86x vs 1.01x).
  - The biggest IG hits are broad life content (challenges, the girlfriend and parents POVs, slump fixes, guilty pleasures defended) more than creator tactics.
- **TikTok (539 talking videos):** see the next bullets.
- **Best and worst hook types on mino.mp4**, by median outlier:
  - `result_proof_howto` 1.98x, and 48% of those posts beat 2x
  - `money_reveal` 1.78x
  - `howto_outcome` 1.37x
  - worst: `series_episode` ("day 47 of...") at 0.74x, with a 3% hit rate
  - `story_confession` has a 0.64x median but produced 3 of the top 6 videos: high risk, high ceiling (what-flops explains the difference)
- **Devices that lift the median outlier** (with vs without):
  - curiosity gap 1.96x vs 0.90x
  - number 1.77x vs 0.84x
  - authority proof 1.74x vs 0.87x
  - value promise 1.58x vs 0.85x
  - personal result 1.56x vs 0.91x
  - on-screen chapters 1.49x
  - Question openers (0.80x) and vulnerability alone (0.79x) do worse.
- **Length:** 30-60 s videos had the best hit rate (35% beat 2x). Under 30 s was worst (13%) for talking-head advice.
- **Text hook:** videos without an on-screen text hook had a 7% hit rate, vs 27% with one. Always give a text hook.
- **When the user asks for "proven" hooks, he means REUSED hooks:** phrases Mino used on several different videos that went viral most of the time. Not broad categories, and not a single viral video. See `references/reused-hooks.md`. The top 3 are:
  1. "Is it possible to [X] in just [Y]?": 16 of 26 uses went viral, across ~20 challenges.
  2. "I don't know who needs to hear this, but [belief] is not going to make you [goal]": 7 of 10, 8 topics.
  3. "Here's how I [X] so [result] every single time": 5 of 9, 6 topics, mostly TikTok.
  - Always show the uses-to-viral count, and show examples, including misses.
  - Cross-posts and reposts of the same script are not separate uses.
  - The "afraid people will judge you" hook is a one-hit wonder (1 of 5). I wrongly featured it once.
- **Hook types** (broad categories), ranked by viral rate across all 1,139 talking videos (types with n ≥ 20):
  - challenge: 48%
  - money reveal: 38%
  - proof how-to: 38%
  - "day N" series is the worst: 7/100
- **Repeats decay on both platforms.** Re-running a winning hook back-to-back fades fast (on IG the $402k money reveal went 3.4x → 0.39x). Re-skin the topic and visual every time.

## Refresh / analyze another creator
Set `W=<workdir>`. Mac: copy `scripts/*` into `$W/tools/` and compile the OCR helper once: `swiftc -O $W/tools/ocr.swift -o $W/tools/ocr`. Windows: no compile and no copy, run the scripts in place (see "On Windows (this PC)" below). Scripts resolve yt-dlp / ffmpeg / whisper-cli / models / the IG profile through `scripts/_plat.py`, so keep `_plat.py` and `ocr.py` next to them.
1. **List posts.** From `$W`, run `~/.hermes/tools/social-scraper/.venv/bin/python $W/tools/list_all.py <handle>`. It writes `list_<handle>.json`, the full post list via secUid + yt-dlp (~550 posts in ~2 min).
2. **Extract hooks.** Run `python3 $W/tools/extract_hooks.py $W <handle> [<handle2>] --workers 6` in the background (`terminal(background=true, notify=true)`); it does ~60 posts/min and is resumable. For each post it:
   - downloads the video
   - OCRs frames at 0.2, 1 and 2.5 s (macOS Vision on Mac, RapidOCR `ocr.py` on Windows)
   - runs whisper on the first 12 s
   - saves a 3-frame strip
   - deletes the video
3. **Score.** `python3 $W/tools/build_table.py $W 8` writes `hooks_table.json` and splits it into 8 batches. `outlier` = views / median of the 30 surrounding posts on the same account.
4. **Classify** with 8 parallel `delegate_task` children using `scripts/CLASSIFY_INSTRUCTIONS.md` (taxonomy + output schema). About 5 min total.
5. **Merge and aggregate** in python (type, device and duration stats), then regenerate `hook-bank.md` and the CSV. Keep only talking formats: `format` in talking_head / voiceover_broll / vlog_story / screen_tutorial. Drop comedy_skit and trend_audio_meme hook types, plus any ad.

**Instagram (all reels):** this needs the scraper login (`ig_login.py` from social-viral-analyzer; the user logs in in the Chromium window). `web_profile_info` and `/feed/user/` returned **429 immediately** on a fresh login, so `ig_list_all.py` is only a fallback. Use these instead, all run with the social-scraper venv python:
1. `ig_reels_capture.py <handle> $W --scrolls 600` scrolls the `/reels/` tab and captures the page's own GraphQL responses. This got 681 reels with views and pk in ~12 min, and stops after 25 scrolls with nothing new. It gives no captions, video URLs or dates.
2. `ig_media_info.py <handle> $W` calls `/api/v1/media/<pk>/info/` once every 2-3.5 s. That fills video_url, caption, date and duration; it is resumable and took ~45 min for 681 with no 429.
3. `extract_hooks.py $W <handle> --platform ig --workers 4` processes only entries with `info_done`, so you can run it repeatedly while step 2 is still going.
4. `build_table.py $W 8 _ig` (pass an ABSOLUTE `$W`, or the strip paths come out relative).
5. Classify with `_batches_ig/INSTRUCTIONS.md`, which adds the required `format` field.

The persistent profile is locked while one script runs, so run the IG scripts one after another, never in parallel.

## On Windows (this PC)
- **Interpreter for everything:** `PY=C:/Users/<you>/.hermes/tools/social-scraper/.venv/Scripts/python.exe` (py3.12; has playwright, rapidocr, onnxruntime, Pillow). Use it in place of `~/.hermes/tools/social-scraper/.venv/bin/python` and `python3`. Run from the terminal tool (git-bash) with `C:/...` paths; put `ffmpeg`/`ffprobe`/`yt-dlp`/`whisper-cli` on PATH or let `_plat.py` find them (`~/.local/bin/yt-dlp.exe`, `C:/Users/<you>/tools/whisper/Release/whisper-cli.exe`). Whisper models: `~/.hermes/cache/whisper/` or `~/.hermes/tools/social-scraper/models/` (`extract_hooks.py` wants `ggml-base.en.bin`, falls back to `ggml-small.en.bin`).
- **OCR:** `scripts/ocr.py` is the Python port of `ocr.swift` (RapidOCR, same one-JSON-line-per-image contract plus `conf`/`box`). Test: `$PY scripts/ocr.py some.png`. `extract_hooks.py` picks it automatically; `OCR_BIN=<path>` overrides.
- **Refresh:** same steps as above with `$PY` and no `swiftc`/copy: `cd $W && $PY <skill>/scripts/list_all.py <handle>`, then `$PY <skill>/scripts/extract_hooks.py $W <handle> --workers 3` (3 not 6, the user is working on the PC; run it background + notify), then `build_table.py`. `list_all.py` imports `fetch_tiktok.py` from `social-viral-analyzer/scripts` (found automatically). TikTok downloads occasionally fail once ("Unable to extract universal data"); `extract_hooks.py` retries once.
- **Instagram:** the user must run `social-viral-analyzer/scripts/ig_login.py` once in the visible window (profile `~/.hermes/tools/social-scraper/ig-profile`, not created until then). Without it the IG scripts exit with "not logged in". Chromium for playwright is already installed. Do NOT log in for him.
- Verified on the PC: `ocr.py` on a generated image, `extract_hooks.py --platform ig` on a local `file://` video (OCR + whisper + strip), `build_table.py`, `list_all.py` import path, IG scripts reach the login check. Not run: real TikTok/IG listing or any logged-in IG call.

## Pitfalls
- **`ig_reels_capture.py` also captures reels from OTHER accounts** (the suggested reels that Instagram loads on the /reels/ tab). On @lucy_japanese, 4 of 227 were foreign: a Kobe speech from @mindempirex_, an ad, and others. Before any analysis, check the owner (caption mentions such as "Follow @x", or an off-topic niche), drop the foreign posts, and recompute outliers. Never conclude "the account changed/was sold" from off-niche posts without checking who owns them.
- Use `outlier`, not raw views. mino.mp4's median moved from ~5k to ~30k over the years, and mino1ee's 2021 meme era gets millions. Posts under ~7 days old have falsely low outliers, so exclude them.
- Whisper writes fake lyrics on music-only meme videos. Trust the on-screen text there.
- OCR returns UI junk ("TikTok", handles, timestamps). `build_table.py` filters most of it.
- Instagram is now included (all 681 @minolee.mp4 reels). Some formats win on one platform and flop on the other: challenges are the #1 type on IG but only 0.76x on TikTok, and the "apparently if you [weird hack]" hook got 26x on IG (caffeine nap) but 0.1x on TT (creatine). Always say which platform a source hook came from.
- Hooks are templates, not scripts to paste. Swap in the user's niche keywords and REAL proof. Putting Mino's numbers ("100k in a month") on the user's video is lying and breaks alignment.

## Verification
- Each delivered hook names its source formula and stats from the bank, and includes spoken hook, text hook and visual.
- No invented numbers, and no "free" for Noxy.
- When refreshing: the `hooks_table.json` row count equals the listed post count, and every row has a `hook_type`.
