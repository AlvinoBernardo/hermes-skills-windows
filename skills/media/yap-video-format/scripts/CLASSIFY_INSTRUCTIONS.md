# Classify Aiden Johnston (@aidendjohnston) Instagram reels — format + hook + structure

Creator: Aiden Johnston, UT Austin CS freshman (class of 2030), Korean-American from Dallas, founder of the dating app Curate (@curatedating). Since ~Aug 2026 he runs a "day N of posting every day until @curatedating has 3,000 daily active users" series. He talks fast (~240-280 wpm), "yaps" to camera holding a mic, and says he edits every video with Claude Code (hook doc of 255 viral hooks, WhisperX rough cut, 2-3 word captions, b-roll pulled by an agent browser, hard cuts, a change every ~3 s).

The goal: build a skill that teaches someone to make viral "pure yapping" talking videos in his style. We need his format, hooks, structure, voice and devices per video.

## Your input
Your batch file `batchN.json` (path given in your task). Each row: id, date, views, outlier (= views / median views of the 30 surrounding posts; >2 = hit, >5 = big hit, <0.7 = flop), duration (s), wpm, cuts_per_10s (scene-change rate from ffmpeg, a rough edit-pace proxy), caption, full transcript (Whisper; names may be misspelled), OCR of first frames and two mid frames, `sheet` (12 frames across the whole video, 6x2 grid, left-to-right, top row then bottom row) and `hook_strip` (frames at 0.2 / 1.0 / 2.5 s).

**Look at BOTH images for every row** with vision_analyze (sheet = visual format, hook_strip = first-frame visual + on-screen text hook). Read the full transcript.

## Output
Write a JSON object keyed by id to `analysisN.json` (same folder as the batch). Per id:

```json
{
  "spoken_hook": "exact first sentence(s) he says, cleaned of whisper typos (max ~30 words)",
  "text_hook": "exact on-screen title/text in the first frame, or null",
  "first_frame_visual": "what is on screen at 0 s (e.g. 'him at desk + white title box', 'screenshot of a tweet full-frame', 'collage of his own day-N thumbnails')",
  "hook_type": "ONE of the taxonomy below",
  "hook_devices": ["any of: number, money, big_name, curiosity_gap, contrarian, personal_stakes, identity_callout, controversy_bait, self_deprecation, proof_shown, here's_how_promise, list_promise, story_open_in_media_res, question, chart_or_visual_reference"],
  "topic": "short topic",
  "topic_bucket": "ONE of: ai_tools_and_workflow, founder_journey_curate, dating_apps_and_dating, college_career_cs_quant, hackathons_and_builds, tech_news_and_people (commentary on famous founders/companies), self_improvement_philosophy, race_culture_stats_bait, school_life_vlog, other",
  "format": "ONE of: talking_head_mic (holds mic, talks to camera), talking_head_whiteboard, talking_head_plus_heavy_broll (>40% of frames are screenshots/b-roll overlays), screen_recording_voiceover, vlog_day_in_life, green_screen, skit, trend_or_meme, other",
  "setting": "e.g. dorm room with posters, home room with whiteboard, outdoors, event",
  "structure": ["ordered beats, 3-8 short labels, e.g. 'hook claim', 'context: GitHub repo blowing up', 'disclaimer', 'thing 1 + joke', 'thing 2', 'thing 3', 'takeaway', 'series CTA: day 84… Peace'"],
  "structure_type": "ONE of: numbered_list, story_chronological, explainer_breakdown, hot_take_argument, profile_breakdown_of_person, tutorial_system_walkthrough, announcement_cta, reaction_commentary, stat_then_twist_joke, vlog_update",
  "visual_devices": ["any of: captions_2_3_words_caps, title_box_top, numbered_section_labels, screenshot_popups, web_page_broll, app_screen_recording, code_terminal_broll, logos_popups, meme_image_popups, charts, whiteboard, zoom_punch_ins, speed_up_text, face_cam_only"],
  "voice_devices": ["any of: fast_delivery, dry_humor_one_liner, self_deprecating_joke, slang ('low-key', 'mogs', 'larp', 'cortisol', 'juice'), hyperbole, insider_jargon_explained, direct_address_you, rhetorical_question, callback_joke, abrupt_ending, absurd_cta_joke"],
  "humor_lines": ["the 1-3 best jokes / quotable lines, verbatim"],
  "payoff": "what the viewer gets (one sentence)",
  "cta": "verbatim ending / CTA, or null",
  "ai_mentioned": true,
  "series_tag": "day N text if the caption/ending uses the 'day N of posting' series, else null",
  "why": "one specific sentence on why it hit or flopped given its outlier"
}
```

## hook_type taxonomy (pick ONE)
- `bold_claim_reveal` — "I reverse engineered Hinge and here are the top 3 things I found"
- `personal_stakes_story` — "I burned 6 billion AI tokens and it got me a job interview at a $13B startup" / "I gave up a $3M salary"
- `famous_person_breakdown` — "Everyone knows Roy Lee… but a lot less is known about his co-founder"
- `controversial_stat` — "Asian women are the most sought after by men of every race except…"
- `you_are_doing_it_wrong` — "If you pay for Claude/ChatGPT you're wasting your money unless…"
- `here's_my_system` — "Every video on my page is edited by Claude Code, here's my whole system in 60s" / "Here's the AI stack I use"
- `here's_how_explainer` — "Here's how Facebook, Tinder, Uber grew from nothing"
- `chart_fear` — "This chart right here is why you're going to be homeless, jobless…"
- `quote_or_philosophy` — "Anxiety is simply intelligence minus courage"
- `question_hook` — opens on a question ("Why are there so many dating apps?")
- `announcement_or_contest` — "Calling all UT Austin students… win $10,000"
- `daily_update` — "Alright, day 36, classes, work…"
- `relatable_confession` — "I low-key started watching Your Lie in April…"
- `other`

Be consistent; don't invent new hook_type / format labels. If the video has no speech (music/meme), still fill what you can and set format accordingly.

When finished, reply with: the path of your analysis file, the number of ids written (must equal the batch size), and 5 bullet observations about patterns you noticed across your batch (hits vs flops), citing ids + outliers.
