# Format classification task (<CREATOR> — full-video breakdown)

<!-- Copy to $W/_batches/INSTRUCTIONS.md. Fill in the creator block. Keep the taxonomies FIXED: that is what
     makes 4 children's labels aggregatable (aggregate_format.py groups on these exact keys). -->

## Creator
- `<handle>` (<platform>, <N> analyzed posts, <date range>): <niche, who they are, recurring series, set/look>.
- Account median ~<X> views. Their stated system (if they teach): <one line or "none">.

## Your input
Your batch file is a JSON array of rows: `id, url, views, outlier` (views / median of the 30 posts nearest
in date; >2 = hit, <0.7 = flop), `pct_rank, date, duration, caption, on_screen_hook` (OCR at 0.2/1/2.5 s,
may contain OCR typos + UI junk), `mid_text` (OCR at 25/50/75 %), `transcript` (FULL whisper transcript;
empty if `music_only`), `wpm, first_word_s, cuts_per_10s, longest_pause_s, sheet` (12 frames across the
whole video, timestamps burned in) and `strip` (hook frames 0.2/1/2.5 s). Both are absolute image paths.

## For EVERY row, output one object
```json
{"id": "...",
 "hook": "the hook as experienced in the first ~3 s, verbatim (spoken and/or text), typos fixed",
 "text_hook": "on-screen text hook only, cleaned (\"\" if none)",
 "hook_type": "<taxonomy key>",
 "topic_bucket": "<taxonomy key>",
 "format": "<taxonomy key>",
 "structure_type": "<taxonomy key>",
 "beats": ["3-7 short beats of the video in order, e.g. 'hook claim', 'receipt: screenshot', 'joke', 'cta'"],
 "hook_devices": ["..."], "structure_devices": ["..."], "visual_devices": ["..."], "voice_devices": ["..."],
 "series_line": false,
 "cta": "the call to action verbatim, or \"\"",
 "ending": "how it ends: loop | cta | punchline | cliffhanger | abrupt | recap",
 "template": "fill-in-the-blank version of the script shape, '' if not transferable",
 "why": "one specific sentence: why this hit or flopped relative to its outlier"}
```

## Taxonomies (use these keys; only if nothing fits use `other:<short_name>`)
- **hook_type:** `result_proof_howto`, `howto_outcome`, `levels_tiers`, `explainer_nutshell`, `listicle_count`,
  `contrarian_hot_take`, `stop_doing_warning`, `pain_callout_if_you`, `story_confession`, `money_reveal`,
  `challenge_experiment`, `i_studied_n`, `secret_nobody_tells`, `pov_day_in_life`, `question_hook`,
  `reaction_reply`, `rant_opinion`, `comedy_skit`, `trend_audio_meme`, `series_episode`, `before_after_transformation`
- **topic_bucket:** fill in 5-8 buckets for THIS creator before dealing the batches (e.g. `tools_apps`,
  `money_business`, `relationships`, `personal_story`, `industry_news`, `tutorial_skill`), plus `other`
- **format:** `talking_head`, `talking_head_broll`, `green_screen`, `screen_recording`, `text_over_broll`,
  `skit_multi_character`, `vlog_walk_talk`, `interview_street`, `slideshow`, `edit_montage`, `podcast_clip`
- **structure_type:** `claim_proof_cta`, `list_n_items`, `story_arc` (setup-conflict-payoff), `problem_solution`,
  `myth_vs_truth`, `tutorial_steps`, `rant_build`, `reaction_breakdown`, `comparison_tiers`, `single_joke`, `q_and_a`
- **hook_devices:** number, timeframe, money, personal_result, specific_identity, pain_callout, contrarian,
  curiosity_gap, stakes, negative_framing, list_count, value_promise, reply_to_comment, trend_audio, pov,
  question, vulnerability, authority_proof, novelty, visual_shock
- **structure_devices:** open_loop, receipts_proof, countdown, callback, pattern_interrupt, rule_of_three,
  twist, recap, chapter_cards, loop_ending, cliffhanger
- **visual_devices:** title_box, burned_captions, word_pop_captions, punch_in_zoom, pop_up_cards, screenshots,
  b_roll_cutaways, props, location_change, face_close_up, split_screen, green_screen_bg, emoji_stickers
- **voice_devices:** fast_delivery, deadpan, self_deprecation, rhetorical_questions, direct_address_you,
  catchphrase, slang, whisper_aside, character_voice, sarcasm, pause_for_punchline

## Rules
- Read the FULL transcript; structure, beats and CTA live in the middle and the end, not the first 6 s.
- Open `strip` AND `sheet` with vision_analyze for at least the 8 highest-outlier rows, the 4 lowest and any
  row whose format isn't obvious from text. For the rest, use the text fields.
- `series_line` = true when the video opens with the creator's recurring series line/intro.
- Don't copy identity jokes (race, sexuality) or personal facts into `template`; keep the technique only.
- Write a JSON array to the output path you were given (`_batches/analysis<N>.json`), every row id present.
  Verify with `python -c "import json;d=json.load(open(PATH,encoding='utf-8'));print(len(d))"`.
- Return a short summary: count written + 5 observations on what separates hits from flops in your batch (cite ids).
