# Hook classification task (Mino Lee TikTok hooks)

Mino Lee is a short-form creator. Two TikTok accounts:
- `mino.mp4` (557 posts, 2022-2026): talking-head content-creation / personal-brand / business / creator-life advice, plus some vlog/story/relationship posts. Account median ~13k views.
- `mino1ee` (236 posts, 2020-2026): older comedy / meme / skit / "reply to comment" / gym-humor / productivity content. Median ~265k views.

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
- `result_proof_howto` — "how i grew 200k followers in 1 year (working 90 min/day)" — personal result + how
- `howto_outcome` — "here's how to / this is how to [outcome]" without a personal result
- `levels_tiers` — "every level of X", "the 3 levels of", "X at 100 / 1k / 10k"
- `explainer_nutshell` — "X in a nutshell", "the only video you need to understand X", "X explained"
- `listicle_count` — "3 things / 6 hooks in 60 seconds / 5 mistakes"
- `contrarian_hot_take` — "do NOT become the niche", "hashtags don't matter", "X is bullsh*t"
- `stop_doing_warning` — "stop doing X", "if you're X, don't...", "you're doing X wrong"
- `pain_callout_if_you` — "if you've been laying in bed scrolling for an hour...", "if you're stuck at 300 views..."
- `story_confession` — vulnerable first-person story opener: "I can't afford rent so I started resenting her"
- `money_reveal` — "how much i made as a creator", "i made $26k today", "my business made $219k last month"
- `challenge_experiment` — "is it possible to...", "can i make X in 1 hour", "i tried X for 7 days"
- `i_studied_n` — "i studied 500 hooks / 1000 creators, here's..."
- `secret_nobody_tells` — "nobody talks about...", "the secret...", "the truth about..."
- `pov_day_in_life` — "POV:", "day in the life", vlog openers
- `question_hook` — direct question opener "what if...", "why do...", "are you..."
- `reaction_reply` — reply-to-comment, react to someone else's content / student roast
- `rant_opinion` — "little angry rant", strong emotional opinion
- `comedy_skit` — sketch/meme/POV comedy, character bits
- `trend_audio_meme` — lip-sync / trend audio / dubbed / song
- `series_episode` — "day 4 of road to $100k/month"
- `before_after_transformation` — then vs now
- `other:<name>`

## Rules
- Use `spoken_first_6s` + `on_screen_text` + `caption` to reconstruct the hook. If spoken is clearly song lyrics or junk, rely on on-screen text.
- Open the `strip` image (vision_analyze, or look at it directly if attached) for at least the 12 rows in your batch with the highest `outlier`, the 5 with the lowest, and any row where the text is ambiguous. Fill `visual` for those.
- Keep the hook wording as close to verbatim as possible — this becomes a hook bank.
- Write your result as a JSON array to the output path you were given (valid JSON, every row id present). Verify with `python3 -c "import json;d=json.load(open(PATH));print(len(d))"`.
- Then return a short summary: count written, and 5 observations about what separates the winners from the flops in your batch (cite ids/views).
