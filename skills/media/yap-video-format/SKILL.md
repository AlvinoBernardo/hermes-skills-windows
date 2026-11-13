---
name: yap-video-format
description: "Use when scripting talking-head yap or 48 Laws videos."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, windows]
metadata:
  hermes:
    tags: [talking-head, yapping, reels, tiktok, scripting, hooks, aiden-johnston, viral, format]
    related_skills: [talking-head-tiktok-edit, mino-lee-hooks, social-viral-analyzer, short-form-video-critic-loop]
---

# Yap Video Format (Aiden Johnston playbook)

How to make viral videos that are **just you talking**. It's reverse-engineered from all 116 reels of **Aiden Johnston, @aidendjohnston on Instagram** (9.9k followers). He's a UT Austin CS freshman and the founder of the Curate dating app, posting "day N of posting every day until @curatedating has 3,000 DAU". His reels ran from Jun 23 to Oct 28 2026. His median is about 6.7k views, and 21 reels went over 2x that, peaking at 989k. He says every video is edited by Claude Code.

**The format, in one line:** a fast-talking smart kid in a dorm holds a tiny mic and explains one specific, slightly edgy thing like he's telling his friends. It has a white title box on top, 2-3 word ALL-CAPS captions, a real screenshot or receipt popping in every few seconds, a joke every ~10 s, and an anticlimax or absurd punchline at the end, then "Peace."

## When to Use
- "Make me a video like Aiden Johnston", "write a yap video about X", "turn this idea into a talking-head reel", "what should I say in this video", "plan my next talking video".
- The user's personal-brand talking-head videos (founder / vibe-coding / AI). Noxy explainer ideas can borrow the structure, but Noxy has its own skills.
- Pair with `mino-lee-hooks` for extra hook options, and with `talking-head-tiktok-edit` for the actual edit after he films.
- Explainer series where he teaches a book concept (48 Laws of Power, one law per video): use **his own shape** in `references/explainer-series-voice.md` instead of the Aiden kit. Always-on rules for that series:
  - The example is a famous real person, **never the book's own story**.
  - Use dead-simple words.
  - The takeaway is cunning and long-game.
  - Deliver in the **teleprompter layout**: labelled beats, one short line each, bold punch words. Never a prose block.
  - Music is "La Maritza" (lalala part).
- Don't use for: editing footage (talking-head-tiktok-edit), slideshows (noxy-tiktok-slideshows), or analyzing another creator (social-viral-analyzer).

## Files
- `references/format-spec.md`: **the look and sound.** Set, wardrobe, mic, title box, captions, pop-up receipts, pacing, music, ending. Read it before any edit.
- `references/script-templates.md`: **start here when writing.** 7 proven video structures with beat-by-beat templates and the original hit each one came from.
- `references/voice-and-humor.md`: how he talks, joke types, slang, and the lines that made the hits work.
- `references/hook-bank.md`: every hook from all 116 reels. The 21 proven ones (2x or more) are ranked, then the rest are grouped by type.
- `references/what-flops.md`: data on what killed reach. Check every plan against it.
- `references/explainer-series-voice.md`: **the user's own format** for book-lesson series (48 Laws): "You should never X, because if you do Y", then "A great example of this is a guy named…", then a sharp takeaway. Includes the rejected versions.
- `references/his-ai-system.md`: his own AI content and agent setup in his words, mapped to what the user already has here.
- `references/top-transcripts.md`: full transcripts of his 15 biggest outliers. Read 2-3 that match the chosen template to get the rhythm.
- `assets/aiden_reels_all.csv`: all 116 reels (hook, type, format, structure, devices, humor, why, transcript, stats). Use it for custom filtering.
- `scripts/`: the refresh pipeline (see Refresh).

## The 10 rules (data + his own words)
1. **The first sentence is the whole video's promise, with stakes.** Use a huge number, a famous name or brand, a forbidden topic, or "you're losing money". "I reverse engineered Hinge and here are the top three things I found" (37x). "I gave up a pretty decent shot at a $3 million a year salary" (34x). "Everyone knows Roy Lee… but a lot less is known about his co-founder" (167x).
2. **Never open on the series or the diary.** The 35 videos that opened with a day-N update had a median of 0.81x and **zero hits**. "Day N of posting until X" goes at the END as the sign-off, never in the first 10 s.
3. **Talk about the viewer's world, not your product.** The 45 founder-journey/Curate posts had a median of 0.84x (7% hits). Career/CS/quant posts had 2.7x (57% hits), race/dating-stat bait 12.8x, and AI workflow 1.17x with the biggest absolute hits. Put the product in only as proof or a punchline ("as the founder of a dating app, this is hilarious to me").
4. **Show a receipt within 1-2 s.** A token-usage chart, an app logo, a GitHub repo, a whiteboard of stats, an IG profile card. Hooks that reference a chart or visual prop had a 2.24x median with 57% hits. "To establish credibility, here's my AI usage in the last 30 days."
5. **Go long when there's substance: 60-120 s.** 60-90 s reels had a 1.37x median (33% hits) and 90 s+ had 1.61x (44%). Under 60 s it was 0.91-0.94x (6-11%). Density matters, not shortness. He talks at about 240-280 wpm with zero dead air (median first word at 0.0 s).
6. **Use a numbered or list skeleton for value videos.** "Number one… thing two… thing three". On-screen numbered section labels had a 3.4x median. Tutorial/system walkthroughs: 1.73x, 50% hits.
7. **Put a joke every ~10 seconds,** mostly dry, deflating one-liners right after a big claim ("Yes, five is a larger number than two"). End on an **anticlimax or absurd CTA**: "Comment real on this video and nothing will happen because I am too cheap for ManyChat". Absurd-CTA videos had a 2.08x median with 56% hits.
8. **Be edgy but defensible.** Use a rage-bait title, then make an actual argument. "Why every company should be abusing child labor" → hire smart minors at $10/hr because AI levels the field (3.05x; the same idea worded softly did 1.53x). Controversy-bait hooks: 37% hits and 0% flops.
9. **Always show a title box.** Videos with an on-screen text hook: 1.10x median, 22% hits. Without one: 0.96x, 9% hits. The title is a shorter, punchier restatement or a POV/identity line ("If you're watching this video, you're not gonna make it in quant").
10. **Something changes on screen about every 3 s** (his rule). In this user's edits that change comes from pop-up cards, screenshots and caption swaps, **not** jump-cut zooms (the user hates random punch-ins; see talking-head-tiktok-edit).

## Procedure: plan a yap video for the user
1. **Get the raw material.** Ask for (or pull from context) the topic, what actually happened or what he knows, and every real number (tokens, $, users, hours, views). Never invent stats or results. Mark unknowns `[real number]`.
2. **Pick the template** from `script-templates.md` that honestly fits the material, then a hook family from `hook-bank.md` (and `mino-lee-hooks` if he wants more options). Run through `what-flops.md`. If the idea is a diary update, find the one viewer-relevant angle in it and lead with that, or tell him it's a low-reach post.
3. **Write the kit in the user's preferred shape.** By default he doesn't follow word-for-word scripts ("it's not my personality"), so give talking points. When he asks for "the full script", write it word for word, built from HIS draft lines and phrasing, and follow these rules:
   - **Keep his backstory beat.** Don't jump straight from the hook to the fix. He wants a short "how I found this" story first (what kept going wrong, plus his current real example), because a straight-to-the-point script loses his voice.
   - **Use his exact wording for the key artifact** (his prompt, his quote, his rule), even if it's clunky. It goes on screen as a card, so it has to match what he says.
   - **Never add lines he wouldn't say.** That includes jokes that roast or name his friends, and invented reactions. When he cuts a line, delete it; don't reword it. Offer jokes as optional 🃏 slots he can drop.
   - **Never guess what a screenshot or chat he mentions says.** Write the beat as `[what the screenshot says]` and wait for the image. A guessed detail becomes a script line built on something that didn't happen.
   - **When he dictates a skeleton sentence ("you should never…, a great example of this is a guy that…"), copy that exact shape and wording.** Don't fit his content into an Aiden template or your own outline. He rejects scripts that "aren't my style" even when the content is right.
   - **Blur friends' names.** Friends in chat screenshots stay anonymous in the script ("my friend") and get blurred on screen.

   The kit (talking-points mode) contains:
   - **Hook, word for word** (one breath, ≤ 20 words) plus 2 alternates, each with its source hit and outlier.
   - **On-screen title box text** (≤ 8 words, lowercase or sentence case).
   - **First-frame receipt**: what pops in by 1-2 s, with the asset path or how to get it.
   - **Beats as short bullets** in his own words: one fact or number per bullet, a 🃏 joke slot every 2-3 bullets with a suggested line, and the receipt or card for each beat.
   - **Ending**: anticlimax or punchline, then the series line, then "Peace." The user prefers jumping from the last content line straight to "Peace", so put the series line only on series posts.
   - **Target length** (60-100 s for list or story videos; 20-40 s for a stat-plus-twist bit) and the template name.
4. **After he films:** edit with `talking-head-tiktok-edit` using the spec in `format-spec.md`: title box, 2-3 word captions, pop-up receipts every ~3 s, no punch-in zooms, music under. Then run `short-form-video-critic-loop` if he wants a critique.
5. **Brand guardrails:**
   - Personal-brand assets live in `~/PersonalBrandAssets/` and Noxy assets in `~/NoxyAssets/`.
   - Never call Noxy "free".
   - Aiden's race/sexuality bait is his. Suggest identity hooks the user can own (founder, vibe coder, calorie/fitness app, his real stats — ask, don't guess) and flag anything that could read as racist rather than funny.

## Pitfalls
- **Same format ≠ same result.** "I reverse engineered Hinge" did 417k views (37x). The identical Tinder remake two days later did 7k (0.54x). His own research video says content explains <5% of reach. Re-skin the topic and the angle each time, and never promise a repeat will hit.
- **Self-deprecation as the *hook* underperforms** (0.90x). It works inside the video as a joke after a flex, not as the opener.
- **Question hooks are weak** (0.72x, 50% flops) unless the question is a genuinely confusing social situation that begs for comments ("What does it mean when… are you bisexual?", 13x).
- **Local or niche asks kill reach.** "Calling all UT Austin students… win $10,000" got 1.61x at best, and recruiting posts 0.76-0.88x.
- **Recency:** posts under 7 days old have falsely low outliers. Exclude them from stats.
- **IG reels tab capture includes other creators' reels** (tagged or suggested). Filter by owner with `scripts/ig_owner_pass.py`. 4 of 120 were not his.

## Refresh / re-run on another yapper
Follow `social-viral-analyzer/references/format-skill-mode.md`. That's the full pipeline, and it uses this skill's `scripts/` (`full_analyze.py`, `ig_owner_pass.py`, `CLASSIFY_INSTRUCTIONS.md`). When refreshing Aiden, regenerate `hook-bank.md`, `top-transcripts.md` and the CSV from the new `merged.json`, then re-check the rule stats in SKILL.md and `what-flops.md`.

## On Windows (this PC)
- Interpreter for the scripts: `PY=C:/Users/<you>/.hermes/tools/social-scraper/.venv/Scripts/python.exe` (playwright, rapidocr, Pillow). Replaces both `~/.../social-scraper/.venv/bin/python` and the mlx-whisper `$WV` venv (mlx is Mac-only).
- `scripts/full_analyze.py` uses mlx-whisper when importable (Mac), else `whisper-cli` (CUDA, ggml-small.en from `~/.hermes/cache/whisper/`) with token-level word timings; `ocr.py` (RapidOCR, in this folder) replaces the Swift `tools/ocr`; `_plat.py` finds ffmpeg/ffprobe/yt-dlp/whisper-cli/models. Run in place, no `swiftc`, no copy to `$W/tools/`: `$PY <skill>/scripts/full_analyze.py $W <handle>`; same for `ig_owner_pass.py $W <handle>`. Use background + notify for real runs and keep `--workers` low, the user works on the PC.
- The IG scripts (`ig_reels_capture.py`, `ig_media_info.py` in `mino-lee-hooks/scripts/`, and `ig_owner_pass.py`) need the user to run `social-viral-analyzer/scripts/ig_login.py` once in the visible window; until then they exit with "not logged in". Don't log in for him.
- The PC also has its own rebuild of this pipeline in `social-viral-analyzer/scripts/format/` (`ig_reels_capture`, `ig_media_info`, `ig_owner_pass`, `tt_download_all`, `full_analyze`, `build_format_table`, `aggregate_format`); it writes `analysis/<id>.json` instead of `full_raw.jsonl`. Either set works; don't mix their outputs in one workdir.
- Verified on the PC: `full_analyze.py` on a generated 15 s speech clip (OCR, 12-frame sheet, hook strip, cuts, whisper-cli transcript, WPM) and `ig_owner_pass.py` reaching the login check. Not run: anything logged in to Instagram.

## Verification
- Every plan names its template and source hit with its outlier, has a word-for-word hook, a title box, a receipt by 1-2 s, joke slots, an ending, and no invented numbers or invented screenshot contents.
- Every claimed number ("2 billion tokens") has a matching real screenshot requested from the user. A generated counter is only a placeholder until the real proof arrives.
- When refreshing: the analysis count equals the owner-filtered reel count, and every row has a `hook_type` from the taxonomy.
