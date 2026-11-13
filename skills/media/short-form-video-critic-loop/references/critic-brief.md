# Critic brief template

The brief must contain:
- **Role:** a harsh, experienced Reels/TikTok strategist.
- **Benchmark:** each reference's duration, hook line, structure, CTA and wpm, plus the visual grammar (background, caption style and position, card style). Give the path to reference contact sheets and `transcripts.txt`.
- **Draft:** the video path, 1 fps sheets (8×4, frame = seconds), `plan.json` (shot and caption timings) and `script.txt`.
- **Voice note:** if the narration is a TTS placeholder to be re-voiced, judge words and pacing and list TTS issues separately. Don't fail the draft only for TTS.
- **Domain plausibility ranges** for any factual or nutrition claims, with a request to flag misleading ones.
- **Non-negotiables** the critic must not spend fixes on: an approved character design, the deliberately mirrored reference format (judge execution), CTA automation the user will set up, real app screenshots.
- **Method:** view at least 10 full-resolution frames via `ffmpeg -ss T -i VIDEO -frames:v 1`, including 0–3 s, a section card, the list or comparison, and the ending. Write only inside the critic folder.
- **Output** (under 500 words, verdict lines first):
  1. Ready to post? YES/NO
  2. Worthy of ~N views like the references? YES/NO plus a 0–10 score
  3. Ranked issues with timestamp, problem and EXACT fix
  4. What to keep

Round N appendix: the previous verdict and score, the numbered fixes applied, and "mark each FIXED/PARTIAL/NOT FIXED, then judge fresh". State only MEASURED numbers (e.g. LUFS). Critics check them.

A typical score trajectory is 5–6 → 7 → 7.5 → 7.8 over four rounds. Applying the SKILL.md retention rules up front starts round 1 higher.
