# Hook classification task (<CREATOR> TikTok hooks)

<!-- Copy to $W/_batches/INSTRUCTIONS.md and fill in the account descriptions (niche per handle, era, median views). -->

Accounts:
- `<handle1>` (<N> posts, <years>): <niche / format>. Account median ~<X> views.
- `<handle2>` ...

Each row in your batch file has: id, handle, url, views, likes, saves, date, duration, `outlier` (views / median of the ~30 posts around it on the same account; >2 = clear winner, <0.5 = flop), `pct_rank`, `on_screen_text` (macOS OCR of frames at 0.2s/1s/2.5s, " / " separated, may contain OCR typos and UI junk), `spoken_first_6s` (whisper transcript of the first ~6 s; may be song lyrics or garbage on music-only videos), `caption`, `strip` (absolute path to a 3-frame image of the first 2.5 s).

## For EVERY row, output one object:
```json
{"id": "...", "hook": "the exact hook as the viewer experiences it in the first ~3 s: cleaned spoken line and/or text hook, verbatim wording, typos fixed",
 "text_hook": "on-screen text hook only, cleaned (\"\" if none)",
 "hook_type": "one of the taxonomy keys below",
 "template": "reusable fill-in-the-blank version, e.g. 'how i [result] in [timeframe] ([constraint])'  ('' for non-transferable memes)",
 "keywords": ["emotion-trigger words/phrases doing the work, e.g. 'view jail', 'quit my 9-5', '$100k/month'"],
 "devices": ["any of: number, timeframe, money, personal_result, specific_identity, pain_callout, contrarian, curiosity_gap, stakes, negative_framing, list_count, value_promise, chapters_on_screen, reply_to_comment, trend_audio, pov, question, vulnerability, authority_proof, novelty"],
 "visual": "short note on the visual hook ONLY if you looked at the strip, else ''",
 "niche": "content_creation | business_money | self_improvement | relationships_life | comedy_meme | fitness | other",
 "quality_note": "1 short sentence: why it worked or why it flopped (relative to outlier)"}
```

## Taxonomy (hook_type) — use these keys; only if nothing fits use `other:<short_name>`
- `result_proof_howto` — "how i grew 200k followers in 1 year (working 90 min/day)"
- `howto_outcome` — "here's how to [outcome]" without a personal result
- `levels_tiers` — "every level of X", "the 3 levels of", "X at 100 / 1k / 10k"
- `explainer_nutshell` — "X in a nutshell", "the only video you need to understand X"
- `listicle_count` — "6 hooks in 60 seconds", "5 mistakes"
- `contrarian_hot_take` — "do NOT become the niche", "hashtags don't matter"
- `stop_doing_warning` — "stop doing X", "you're doing X wrong"
- `pain_callout_if_you` — "if you've been laying in bed scrolling for an hour..."
- `story_confession` — vulnerable first-person story opener
- `money_reveal` — "how much i made as a creator", "i made $26k today"
- `challenge_experiment` — "is it possible to...", "can i make X in 1 hour"
- `i_studied_n` — "i studied 500 hooks, here's..."
- `secret_nobody_tells` — "nobody talks about...", "the truth about..."
- `pov_day_in_life` — "POV:", "day in the life", vlog openers
- `question_hook` — direct question opener
- `reaction_reply` — reply-to-comment, react/roast someone else's content
- `rant_opinion` — strong emotional opinion
- `comedy_skit` — sketch / meme / character bit
- `trend_audio_meme` — lip-sync / trend audio / dubbed
- `series_episode` — "day 4 of road to $100k/month"
- `before_after_transformation` — then vs now
- `other:<name>`

## Rules
- Reconstruct the hook from `spoken_first_6s` + `on_screen_text` + `caption`. If spoken is clearly lyrics/junk, rely on on-screen text.
- Open the `strip` image (vision_analyze) for at least the 12 highest-`outlier` rows, the 5 lowest, and any ambiguous row; fill `visual` for those.
- Keep hook wording as close to verbatim as possible — this becomes a hook bank.
- Write a JSON array to the output path you were given (every row id present). Verify with `python3 -c "import json;d=json.load(open(PATH));print(len(d))"`.
- Return a short summary: count written + 5 observations on what separates winners from flops in your batch (cite ids/views).
