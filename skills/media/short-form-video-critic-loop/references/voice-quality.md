# Voice quality gate for re-voiced short-form narration

Use this before rendering when the narration is synthetic. The goal is to match the reference narrator. That voice may itself be AI, but it must sound good: animated, warm and fluid.

## Targets (measure the reference first)
Run `prosody.py` (librosa pyin + RMS):
- **median pitch**
- **pitch SD** in semitones
- **5–95% pitch range**
- **pauses per minute** (silences of 120 ms or more)
- **speech ratio**
- **wpm**

Also check spectral balance: centroid and band energy in low, mid, presence and air.

A good energetic male explainer narrator measured:
- median pitch about 115 Hz
- pitch SD 5.1–5.9 st, range 16–21 st, 10–16% of voiced frames above 180 Hz
- about 14 pauses per minute of about 0.25 s each, speech ratio about 0.90
- 150–180 wpm on the clean samples

Two failure shapes look different in the numbers:
- **Choppy TTS** (e.g. Edge neural voices, or scripts chopped into one-word sentences): about 45 pauses per minute, speech ratio about 0.74.
- **Flat clone** (one long whole-script generation): pitch SD about 4.3–4.5 st, range about 14 st, few pauses, about 225 wpm. It sounds like a run-on.

## Script for the ear (separate from on-screen text)
- Write in full flowing sentences with commas and connectors ("so", "and", "while"). Do not chop into one-word period fragments; that sounds robotic on every engine.
- Use question→answer beats the way the reference does ("Reason one? Volume.", "So why?"). Keep one real question in the hook.
- Spell numbers as words. Put the brand name in a plain sentence. If an engine mispronounces it, try a phonetic spelling (e.g. "Nocksee").
- Drop the comma before a CTA keyword ("Comment Noxy and I'll send you the link"). The comma produced a split pause.

## Generation (Voicebox desktop app, local HTTP API)
- **API:** server `http://localhost:17493`; `/openapi.json` lists the endpoints.
- **Profiles:** `GET /profiles`. To create one, POST `/profiles` `{name, language:'en', voice_type:'cloned', default_engine:'qwen'}`, then POST `/profiles/{id}/samples` as multipart with `file` and `reference_text` (an exact transcript).
- **Generate:** POST `/generate` `{profile_id, text, engine:'qwen', model_size:'1.7B', seed, normalize:true, max_chunk_chars}`. It returns an id immediately.
- **Poll:** status is in the `generations` table of `~/Library/Application Support/sh.voicebox.app/voicebox.db` (id, status, audio_path), or use `/generate/{id}/status`. Files land in `generations/`. A 40 s take takes minutes and jobs run serially.
- **Engines:** qwen (clone), qwen_custom_voice (presets), chatterbox / chatterbox_turbo (POST `/models/download {model_name}` first; check `/models/status`), kokoro, luxtts.
- **Clone from the single most animated reference clip,** not an average of many. Averaging five samples flattened the delivery. Keep the multi-sample profile as an A/B arm.
- **Generate per sentence or beat,** 3+ seeds each, rather than one whole-script take. Use `scripts/gen_lines.py` (queues lines × seeds × profiles and copies finished WAVs).
- **Pick and assemble with `scripts/pick_assemble.py`:**
  - It scores each take on Whisper word accuracy vs the script, pitch SD and share above 180 Hz, a pace penalty outside 150–235 wpm, a rising-ending penalty on statements, low-confidence words, a clipped onset (first 10 ms louder than −50 dB, which cuts consonants like the "Th" of "Three") and a too-short payoff line (under 0.9 s).
  - It trims with a 30 ms head pad and lets each tail ring about 110 ms with a curved fade. Gaps: about 0.22 s inside question→answer beats, 0.35–0.45 s between sentences, about 0.4 s or more before the payoff line. Then scale all gaps by about 0.65 (`GAPSCALE`); the unscaled gaps measured over-spaced (speech ratio 0.86 vs refs 0.90).
  - Fill gaps with band-limited room tone (about −60 dBFS measured after mastering). Digital-zero gaps sound spliced when the VO is heard dry.
  - Mastering: high-pass 70, a slight 3 kHz presence and 7 kHz air lift, gentle compression (ratio ≤1.8; heavier compression filled the pauses), loudnorm −14.
  - Apply critic-named swaps with `FORCE` and slow hyped lines with per-line `LTEMPO` (about 0.90–0.95). Forced takes skip the selection, so check their `on_db` and pitch in `picks.json` yourself.
  - Tighten the picker from the start:
    - **Pace:** start the pace penalty at 215 wpm with a steep slope, `(wpm-215)/15`.
    - **Register:** penalise a median pitch more than 2.5 st from the body (about 118 Hz). The hyped app or brand line otherwise wins at about 6 st high.
    - **Pre-roll:** prepend about 80 ms of room tone so the first consonant isn't clipped.
  - **CTA line:** the picker almost always takes it too fast (250–300 wpm). FORCE a take near 195 wpm or apply LTEMPO 0.88–0.92 before the critic sees it.
  - **Changing a line's wording:** remove that line's keys from `takes/jobs.json` and move its old WAVs out first. `gen_lines.py` skips keys already in jobs.json and re-copies the OLD audio for the new text.
  - **Run regeneration in the background** (background + notify). Voicebox processes one queue, so several lines × 5 seeds across videos outlasts a foreground timeout.
  - **Rewrite junctions that blur:** when Whisper keeps hearing a wrong word at a word junction on every seed (e.g. "the scale still" → "scales still"), rewrite the line rather than rolling more seeds.
  - **Digit transcripts:** Whisper writes numbers as digits ("2,500"), which deflates accuracy scores on number lines. Add digit→word mappings to the picker's normaliser, or judge those lines by ear and metrics.

## Per-line consistency (what kept takes from matching the reference)
- **Register jumps:** per-sentence generation can put one line about 6 st above the rest (e.g. a hyped app-pitch line at 167 Hz vs about 120 Hz). Compare per-line median pitch, and prefer a take within about 2 st of the body.
- **Pace jumps:** check per-line wpm, not just overall wpm. A 230+ wpm line next to 180 wpm lines sounds stitched. Slow it with per-line atempo instead of regenerating everything.
- **Number-only chapter beats get garbled.** "Two? Protein." was transcribed as "to protein" on every seed, and "Three? Time." had no question lift. Make the beats parallel and longer ("Reason one? Volume." / "Reason two? Protein." / "Reason three? Time."), and pick takes where the number rises and the answer word falls.
- **Very short payoff lines are thrown away** ("Pick the plate." came out 0.6–0.8 s at about 290 wpm). Give them a lead-in word ("So pick the plate.") and require 0.9 s or more.
- **The hook line is often the flattest.** Regenerate it with 6+ seeds and pick on pitch SD and share above 180 Hz.
- Typical voice-critic trajectory with this procedure: whole-script clone 5/10 → per-line single-ref clone 6.5 → parallel beats + swaps + room tone 7.5 ("good enough to use") → per-line tempo and hook regen for the last half point.

## Voice critic subagent
Give it a folder containing:
- the reference clips and the rejected baseline
- raw and mastered takes
- Whisper word JSONs with confidences
- `script.txt`, `prosody.txt`, the pitch-contour PNG and `prosody.py`

Tell it that it cannot literally hear, so it must judge from transcription, pitch contours, pause structure, per-sentence wpm, chunk-seam level jumps and clicks.

Ask for:
1. Good enough to use? YES/NO
2. As good as the reference? YES/NO plus a 0–10 score
3. Ranking of all takes, including the baseline
4. Timestamped problems
5. Specific fixes

Iterate until YES, then render, then run the video critic. Whisper spelling variants ("Noxie") are not proof of mispronunciation; check word confidence. From round 2, give the critic the previous take plus a list of the fixes applied and ask it to mark each FIXED/PARTIAL/NOT FIXED and to name exact replacement take filenames from the line-take folders; its filename-level swaps were the fastest gains. After the critic says YES, let the user audition the final take next to the old voice and a reference clip. The critic judges from measurements, and the user judges by ear.
