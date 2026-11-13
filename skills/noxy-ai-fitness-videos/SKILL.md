---
name: noxy-ai-fitness-videos
description: Use when creating Noxy AI fox fitness-explainer videos.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [noxy, video, fox, fitness, tts]
    related_skills: [video, image, codex-image-generation]
---

# Noxy AI fox fitness explainers

## On Windows (this PC)
- **Project root:** `~/Desktop/Noxy` on the Mac is `C:/Users/<you>/Desktop/Noxy` here. Every `~/...` path in this skill or its references is a Mac path: replace `~` with `C:/Users/<you>`, or better `Path.home()`. The Mac's Noxy library (photo library, Finished-slides, References, rotation JSONs, approved assets, `_source` kits) is NOT on this PC yet. Create `Desktop/Noxy` on first use, and ask the user to copy the folder from the Mac before any step that needs history, hashes or approved assets. Say so plainly instead of guessing.
- **Mac-only assets:** the fox character package, `_source` renderers (`engine.py`, `plans.py`, `render.py`, `reference_edit.py`, `voice/*.py`), `~/NoxyAssets` (references, `sfx/mixkit`, fitswithred) and the Voicebox "Noxy APP" clone profile are not on this PC. Copy them from the Mac or rebuild; until then only the style rules here apply.
- **Voicebox** has a free Windows build (MSI with CUDA, voicebox.sh/download). Not installed here yet. Same local API at `localhost:17493`; on Windows the data dir should be under `%APPDATA%/sh.voicebox.app/` (unverified) instead of `~/Library/Application Support/sh.voicebox.app/`. Re-create the clone profile from the reference samples. No Qwen3-TTS weights are in this PC's HuggingFace cache. Hermes's own `text_to_speech` tool (Edge) works as the free fallback, but the user rejected plain Edge voices for delivered samples.
- **Fonts:** Avenir Heavy = `engine/fonts/Montserrat[wght].ttf` at weight 800 or `Poppins-ExtraBold.ttf`; Arial Italic = `C:/Windows/Fonts/ariali.ttf` (identical). Re-measure stroked glyph bounds: bearings differ.
- **Python/tools:** engine venv `C:/Users/<you>/IkkimiAssets/engine/.venv/Scripts/python.exe` has PIL, numpy, scipy, cv2, librosa, pyloudnorm, soundfile, rembg; no `parselmouth` (pitch scoring: `librosa.pyin` or `uv pip install --python <engine venv> praat-parselmouth`, ask first). ffmpeg/ffprobe on PATH (Hermes's bundled ffmpeg has no `drawtext`); `whisper-cli` + model `~/.hermes/cache/whisper/ggml-small.bin`; Playwright is in `~/.hermes/tools/social-scraper/.venv`. Run render loops in Python or bash (git-bash is bash, so the zsh word-splitting caveat doesn't apply, but Windows Python writes `\r\n` into list files: loop in Python). Light jobs only; use `IkkimiAssets/scripts/run_low.py` for renders (see `ikkimi-windows-pc`).
- "Open in Finder" = `explorer.exe`, or print the path.

## When to Use

Use for the user's recurring illustrated fox fitness/nutrition videos, character poses, narration auditions and reference-format recreation.

Load the video, image and codex-image-generation skills as applicable.

## Character direction

Use a FOX, not a faceless human, for this specific format. The user explicitly corrected the initial orange human concept. Their three reference videos show red faceless muscular humans, but only the 2D comic/cel-shaded medium, lavender field and readable fitness poses should carry over. Do not mistake reference species for the requested mascot.

Character package: `~/Desktop/Noxy/Noxy-2026-10-14-Fox-Fitness-Character/`. Main `01-fox-character.png`, cutout `02-fox-transparent.png`, guide `03-character-guide.md`. The user approved this fox design and requested a video built around him. Preserve this character as the identity anchor. Voice selection remains a separate decision. Consult `~/NoxyAssets/CATALOG.md` for later revisions before reusing it.

Current concept: adult anthropomorphic orange fox, athletic muscular body, black-tipped upright ears, cream muzzle and chest, friendly expressive brown eyes, one cream-tipped tail, charcoal joggers, black wristbands and off-white trainers. This character format is separate from the approved Korean slideshow character and the pre-existing simpler Noxy fox art.

## Sources and continuity

Original reference videos, exact durations, hashes and sampled contact sheets are retained under `~/NoxyAssets/references/ai-fitness-explainer/`. Initial human draft is superseded and archived in `character-drafts/initial-human-concept-superseded/`; never use it as the intended mascot. Performance is user-reported, not independently verified analytics.

Approve the character before producing the full video. For new poses, provide the selected character IMAGE as an identity reference and preserve ears, muzzle, one tail, outfit and 2D linework. Text alone does not guarantee identity consistency. Create original scripts and audio rather than copying reference media assets.

Inspect generated anatomy and transparent exports. Native generation dimensions may differ from requested geometry; retain the original and provenance, and report resampling honestly. The flat lavender background can be keyed from this orange/cream/charcoal subject, but inspect ears, tail tips, fingers and shoes on a contrasting background to catch fringe or holes.

## Free voice generation

The user requires a FREE text-to-speech option and has chosen the Voicebox desktop app for this format. They clarified that by the 'guy voice' they mean the ACTUAL NARRATOR OF THE RED-CHARACTER REFERENCE VIDEOS, not Edge's Guy preset. They want to provide a reference audio sample to Voicebox; do not steer them back to Ryan or require a preset workflow. Extracted source excerpt and matching transcript: `~/Desktop/Noxy/Noxy-2026-10-14-Red-Character-Voice-Sample/01-red-character-reference.wav` and `02-reference-transcript.txt`. This is 11.7 seconds from 3.58–15.28 of the third video, mono 24kHz PCM16, no speed/pitch change, no source separation; source sentence boundaries and the final sample were transcribed to verify complete words. For reference-audio cloning use Qwen TTS 1.7B (Base), not CustomVoice. No clone has been generated, no source voice identity identified and no rights/permission verified; extraction does not establish permission to clone or publish. Prior Edge TTS samples are alternatives, not the selected production workflow. Earlier preset-only fallback, NOT the user's current sample-cloning workflow: Qwen CustomVoice 1.7B with English preset Ryan was suggested for a rhythmic male narrator; Aiden is another English male preset. CustomVoice uses preset voices and delivery instructions, whereas plain Qwen TTS maps to the Base/cloning model. Do not revert to the preset path unless the user chooses that alternative. Neither Ryan nor Aiden has been approved. Verify current Voicebox preset/model documentation and the official Qwen model card before giving setup details; no app settings have been changed. Do not default to paid ElevenLabs or silently change Hermes's global voice settings. Voice audition package: `~/Desktop/Noxy/Noxy-2026-10-14-Fox-Voice-Auditions/`. `01-guy.mp3` uses `en-US-GuyNeural`; `02-andrew.mp3` uses `en-US-AndrewNeural`, both +4% rate and unchanged pitch. Voice choice is pending user feedback. The package includes the identical script, native audio, normalized deliverables and generation settings.

Voicebox personality text for the red-character narrator: `03-voicebox-personality.txt` in the voice-sample folder (under Voicebox's 2,000-char personality limit). It was derived from transcripts of all 3 references: short declarative lines, one-line hook, numbered beats, one visual analogy, CTA ending, about 165-237 wpm, animated pitch. Personality only changes the WORDS (LLM rewrite via Compose / Speak in character); it does not control prosody. Fix rhythm/accent issues through reference audio quality, an exact reference transcript, additional samples, and punctuation in the script.

Additional clone samples 07-10 (A/B from video 1, C/D from video 2; 15-21.5 s each, median pitch about 109-118 Hz) and matching transcripts are in the same voice-sample folder. Whisper verified each transcript and cut boundaries. Voicebox should use these instead of sample 01 (video 3, about 147 Hz and fast). Before overwriting an existing `_preview.html`, read it and add to it rather than replacing it.

First Voicebox clone render review: measured about 249 wpm (refs 166-188 for videos 1-2), shorter pauses than the refs, median pitch 151 Hz (it matches the video-3 sample, which is higher and faster than videos 1-2 at about 112 Hz), -20.4 LUFS against the refs' -14. Qwen also turned short fragments like "A handful here." into rising questions. Check every render for a wrong or mismatched hook (the user once pasted the reference video's hook over the script opening), audio-only hooks that rely on visuals ("this guy"), pace and normalization. For audio-first scripts, use periods instead of commas and no mid-list question marks.

Generate per-task stock-voice auditions through an isolated `uv tool run --from 'edge-tts==7.3.1' edge-tts --voice VOICE --text TEXT --rate=+4% --write-media OUTPUT.mp3`. Verify voice IDs through `edge_tts.list_voices()`. If an older installed client gives HTTP 403, compare its version with the current package release before assuming service access is unavailable. Updating only the isolated client from 7.2.7 to 7.3.1 restored actual synthesis here; do not patch auth tokens or change global packages. Recheck future package versions when troubleshooting instead of assuming this pin always works.

Verify nonempty audio by full ffmpeg decode, duration and signal/peak checks. Match comparison loudness, keep raw sources, and let the user audition the actual files. Provider style tags are not a substitute for listening. Free online access is not an unlimited-availability guarantee or a blanket publication license; do not make those promises.

## Imagegen + supplied-narration sample pipeline

When the user supplies a WAV and asks for an imagegen sample, produce an actual playable video, not just a scene plan or still image. Preserve the original audio byte-for-byte in the package and Noxy library, transcribe with word timestamps, and use the approved fox image as the direct reference for every new pose. Distinguish a motion-comic edit (pose cuts, animated props/diagrams, idle movement) from true generative character motion or lip sync; do not imply one is the other.

Reusable verified template: `~/Desktop/Noxy/Noxy-2026-10-14-Fox-Healthy-Eating-Sample/_source/render.py` and `test_render.py`. This rendered the supplied 43.95-second voiceover to 1080×1920/30fps with ten scenes. Treat duration, scene starts, narration paths and events as task-specific data that must be updated, not universal defaults. Tests cover caption conservation/glyph bounds, transparent asset presence, actual silhouette collisions, audio tail preservation and actual codec output. Final encode is fully decoded and measured before promotion to the deliverable filename.

Generate four consistent full-body reaction/teaching/food/phone poses on uniform lavender plus a food sprite sheet. Key purple backgrounds adaptively from sampled edge chroma; inspect resulting cutouts on cream. Sprite grids may not be evenly spaced despite the prompt: inspect actual empty gutters before cropping, especially rims, straws and garnishes. Preserve native images and generation receipts. Do not fabricate app screenshots; show the phone back or use real app capture.

Use large readable 80–88px word-highlight captions at1080, grouped in2–3 words, timed to the supplied speech. Measure actual stroked glyph bounds, not only advances; Avenir Heavy has negative bearings. Check overlays against the character's actual alpha silhouette rather than forcing excessively small characters to avoid bounding-box overlap. Inspect a real encoded contact sheet, not only source stills.

For normalization, reserve AAC peak headroom and verify decoded output. FFmpeg loudnorm/resample can leave a timestamp discontinuity near the tail; rebase with `asetpts=N/SR/TB` after resampling and before padding/output duration. Confirm all original audio samples are retained. A voice-only preview is useful while assessing new narration, but do not turn that into a permanent no-music preference.

## Reference-faithful editing (latest user correction)

The user responded to the first healthy-eating sample by resending the same three red-character videos and asking to follow their editing style. Do not mistake a polished infographic template for this reference style. The first sample's large headlines, pill badges, numbered UI, checklist tiles, floating presenter and yellow karaoke captions are not the requested grammar.

Inspect original frames and short transition sequences, not just a tiny full-storyboard image. In these references use: a flat muted lavender field (sampled around RGB 141,135,174); large standalone character/action illustrations alternating full/medium/thigh-up framing; white Arial-like italic captions, usually 2–3 words, at about 69% frame height, thin dark edge/shadow, no word-color highlight; brief dissolves between some poses, direct noun/section cuts and modest 2–3% camera pushes. The third reference has black chapter cards: a large condensed bright #number flashes, dims almost black, and leaves a short white italic title centered over it. Do not carry over the source character, logos, footage, script or music.

Revision renderer and reusable spec: `~/Desktop/Noxy/Noxy-2026-10-14-Fox-Reference-Edit/_source/reference_edit.py`, `test_reference_edit.py`, `EDIT-SPEC.md`, `shot-list.json`. The revised caption is 64px Arial Italic centered at y=1320 on 1080×1920, not the older 80–88px Avenir Heavy style. This is specific to the red-character video style and does not change slideshow cover-font rules. Caption grouping conserves supplied speech; black chapter cards show section titles instead of a duplicate lower subtitle.

New consistent action cutouts `cook.png`, `sip.png`, and object `wallet.png` are in that revision's `_source/cutouts/`; native generations and request IDs are preserved. Reuse the approved fox as image reference. Intentional lower-body medium-shot crops are acceptable, but a full-body scene must preserve complete ears, hands, tail and shoes: check actual rendered borders rather than assuming the fit box guarantees clearance. Keep the earlier sample unchanged for comparison. Do not treat the new revision as user-approved until feedback.

## Proven recreation pipeline ("Lose 10 kg — 5 things", 2026-10-15)

The previous Reference-Edit fox video FLOPPED (user report). The user wants the approved fox reused and every draft judged by a Claude critic subagent ("ready to post on Instagram?" + "worthy of ~10k views like the references?"), iterating until both are YES. Package: `~/Desktop/Noxy/Noxy-2026-10-15-Fox-Lose-10kg-5-Things/`; renderer `_source/render.py` auto-aligns ANY narration to `script.txt` via faster-whisper (small.en), so a Voicebox take re-times everything. Always give the user a copy-paste Voicebox script file.

What the critic rewarded/punished (apply up front):
- Sound-off hook text in the top third for 0–2 s plus a visual change inside 2 s (chubby→lean fox with a 2-frame white flash); a spoken open loop that the body pays off later ("number five is the one everyone quits").
- Chapter cards ≤1.5 s, title words lit left-to-right on a fixed 0.12 s stagger (NOT tied to speech), drawn baseline-aligned (`anchor='ls'`); per-sprite centering made lowercase words float.
- Every shown noun must appear on its spoken word (check that the pop falls inside the shot window). No static hold >2.2 s. Avoid reusing a pose.
- Product proof = real App Store screenshots (iTunes lookup API `screenshotUrls`, swap `320x480bb`→`1290x2796bb`), large (~88% width), gentle push ≤1.1× so text never crops at the edges. Never fake UI.
- One CTA only ("Comment NOXY and I'll send you the link"). NEVER say Noxy is "free" anywhere: voiceover, end card, app-card subtitle or caption. The user says it is not free, even though the App Store lookup reports price 0, so do not use that lookup to justify the claim. End about 0.5 s after the last word, with the full fox in frame. The script must not copy the reference lines verbatim.
- Mix: final loudnorm −14 LUFS, stereo. The user found a flat looping phonk bed boring ("make it more interesting"). Edit the music to the picture: start the track so its stop→drop lands on the 2-frame before/after flash, with a sub-boom on the flash, a rising whoosh into each chapter card, a 380 Hz low-pass under the cards, gain about 0.32 with a sidechain duck. Presets `trap-drop` (default, trap_dance_hype_beat drop 14.22 s), `phonk-drop` (phonk_577761, 7.38 s) and `pop-drop` (upbeat_trending, 12.38 s) are in render.py `TRACKS`. Render the alternates audio-only with `--video-from`.

Video 2 (`Noxy-2026-10-15-Fox-Muffin-vs-Plate/`) took 6→8.5/10 over 5 rounds. Lessons for later topics:
- Familiar nutrition topics need a sharper hook twist: "This one muffin has the same calories as this entire plate" at true scale.
- The side-by-side comparison must land by about 1.2 s even before the voice reaches the noun.
- Use a visual time-jump (clock, "1 HOUR LATER") instead of two similar poses in a row.
- One graphic should not be held more than about 2.5 s; split it with a cutaway and return.
- The CTA should be big and in the top third ("COMMENT / NOXY" at about 190 px).
- On-screen overlay order must match the voiceover order.
- Keep chapter digits dim from frame 0.
- When editing render.py by string slicing, check that helper functions (e.g. `versus`) were not deleted between the slice markers.

Imagegen: shirtless 'heavier/fat fox' prompts are rejected (safety: sexual). Use "family-friendly cartoon mascot… chubby, snug grey t-shirt". Medium-shot prompts of the shirtless fox can also be rejected; full-body plus family-friendly wording passes. Key cutouts with top/side-only edge sampling (poses touch the bottom edge), remove enclosed lavender holes, and strip purple floor shadows in the bottom 14%.

## Voice quality loop (user requirement, all sessions)

The user judges the Edge TTS placeholder (Andrew +26%) and plain TTS as "very AI" and unacceptable. The reference narrator is also obviously AI, but it sounds GOOD: animated, about 115 Hz male, wide pitch movement (16–21 semitone range, SD about 5.2 st), fluid connected phrasing with few long pauses (speech ratio about 0.90–0.98) and about 166–237 wpm. Edge Andrew measured 4.85 st SD but a 0.72 speech ratio and 48 pauses/min, so its choppy, period-heavy delivery is a big part of what sounds robotic.

Workflow:
1. Generate several candidate takes before rendering any video. Voicebox runs locally with an HTTP API at `localhost:17493` (OpenAPI at `/openapi.json`). The clone profile "Noxy APP" (`2d694518-1805-4178-99cf-770c741beaa5`) holds five reference-video samples. POST `/generate` with `{profile_id, text, engine:'qwen', model_size:'1.7B', seed}`, then poll the `generations` table in `~/Library/Application Support/sh.voicebox.app/voicebox.db` or `/generate/{id}/status`; outputs land in `generations/`. Engines include qwen (clone), qwen_custom_voice (presets), chatterbox / chatterbox_turbo (download via POST `/models/download`), kokoro and luxtts. Generation of about 40 s takes minutes on the M5.
2. Write the VO script for the EAR: flowing sentences with commas and connectors ("Number one is volume.", "so", "and", "while"). Do NOT chop it into one-word period fragments; those made every engine sound robotic. Keep on-screen captions separate from the spoken text.
3. Measure each take with `~/.hermes/cache/scratch/voice/prosody.py` (pitch SD/range, pauses/min, speech ratio, wpm) against the reference samples 07–10, and Whisper-check the words.
4. Then spawn a SEPARATE critic subagent to judge the voice only: does it sound good, does it sound too AI, how does it compare with the reference narrator, any mispronunciations ("Noxy" = NOK-see), questions in the wrong place, wrong pace. Give it the audio paths and spectrogram/prosody numbers; it should listen via transcription plus metrics, not assume. Iterate (seed, engine, script phrasing, reference samples, light post-processing such as EQ/compression) until the critic says it is good enough. Only then render the video, then run the video critic.
5. Never ship the Edge placeholder as final, and never claim a voice is good without the critic pass plus measurements.

Proven recipe (muffin video, voice critic 5→6.5→7.5→8/10):
- Voicebox profile "Noxy APP (REF-B single, Hermes test)" (`7752ba51-0c70-4d2f-a9a0-6740d7e82c15`) is cloned from sample 08 (Ferrari) only. A single animated reference beat the 5-sample average.
- Generate per LINE (13 lines), 3–6 seeds each. Scripts: `~/Desktop/Noxy/Noxy-2026-10-15-Fox-Muffin-vs-Plate/_source/voice/` (`gen_lines.py`, `pick_assemble.py`, `lines.json`, `prosody.py`). The picker scores Whisper accuracy, pitch SD, share of frames above 180 Hz, rising-statement penalty, pace, onset clipping (first 10 ms must be quieter than −50 dB) and minimum length for short payoff lines.
- Assemble with designed inter-line gaps ×0.65 and INTRACAP=0.24 (caps silences inside a line), a 110 ms tail ring-out, room tone at about −71 dBFS (≈ −62 measured; never digital-zero gaps), EQ plus 1.8:1 compression to −14 LUFS, and a global atempo of 1.05 for about 176 wpm.
- Chapter beats read best as "Reason one? Volume." (rise on the number, fall on the noun). Bare "Two? Protein." is heard as "to protein".
- Avoid starting consecutive lines with "So". Short payoff lines ("So pick the plate.") need at least 0.9 s.
- Whisper spells Noxy as "Noxie"; that is spelling, not mispronunciation.
- Whisper hallucinates words ("to the channel") in silent tails, so check RMS before believing it.
- A full 13-line × 3-seed × 2-profile batch takes about 20 min on the M5.
- Critic subagents cannot hear audio. They judge from transcripts, pitch, pauses and spectra, so always give the user an A/B pack (new vs old vs reference) for the final ear test.

## Session lessons (fox video series, 2026-10-15)

- Reuse the approved fox only. The earlier Reference-Edit video flopped; the recreated format (hook visual change in under 2 s, sound-off hook text, numbered dim chapter cards, food circles popping on spoken words, real app proof, single CTA) scored 8–8.5/10 with the critic after 4–5 rounds.
- The user wants every deliverable critiqued by a Claude subagent with two YES/NO questions (ready to post on Instagram? worthy of ~10k views like the references?) and iteration until both are YES. Report the score table honestly, since the scores are a model's judgment.
- NEVER say Noxy is free.
- Music must be edited to the picture (drop on the flash, whooshes, low-pass under cards), not a flat loop.
- Deliver a copy-paste Voicebox script file plus a renderer that auto-re-times to any narration.
- In zsh, a command stored in a variable like `$R` is not word-split; use a bash script or function for render loops.

## Next-batch requirements (user feedback after the first two videos)

- **Voice:** the user rejected the placeholder voice ("the voice is still shit"). The Edge `en-US-AndrewNeural` +26% narration is not acceptable for delivered samples. For the next batch, before rendering, either (a) make a much better narration and A/B it against the reference narrator, or (b) render with the user's Voicebox clone. A Qwen3-TTS 1.7B CustomVoice model is already cached in `~/.cache/huggingface/hub`, and a local Base/clone model with samples 07–10 may be worth testing. Listen to and measure (wpm, pitch, LUFS, question-intonation) every take before using it. Do not ship TTS just because it is synced.
- **Sound effects:** the user wants real SFX in the edit, not just music-bed whooshes. Add them on the picture events the renderer already knows: pop/bubble on each food circle and label pop, whoosh/swish on cuts and chapter cards, a deep hit or riser on the hook flash, a ding/cash-register sound on numbers (500 kcal, 35 g), a stamp thud on "DONE", ticking under the clock or stopwatch, a camera-shutter or UI tap on the app card, and a click/notification on the CTA. Use royalty-free sources (Pixabay or similar) or synthesize. Keep SFX under the voice (about −18 to −22 dB relative) so they never mask words. Save the SFX to `~/NoxyAssets/sfx/` and log them in the catalog.
- Both points apply to every future batch of these fox videos. They were noted, not acted on, when the user said them.

## Batch 2 lessons (2026-10-16, 3 videos, all critic 8/10)

- **Benchmark account is @fitswithred** (Instagram, 153K): the red-character source of the format. Its latest reels are in `~/NoxyAssets/references/fitswithred/`, fetched with logged-out `yt-dlp https://www.instagram.com/reel/ID/`. The profile page shows the grid logged-out via Playwright (`a[href*="/reel/"]`). Hermes' browser tool fails while the user's Chrome is open (use_real_profile lock), and the social-scraper IG session expires. Their newest reels add black term cards ("NEAT"), comic halftone promo cards with starbursts and Bangers lettering, and a yellow halftone "COMMENT 'SCALE'" end card. Copy these for the Noxy app card and CTA (Bangers font, OFL, in `_source/fonts/`).
- **Reusable engine:** `~/Desktop/Noxy/Noxy-2026-10-16-Fox-Batch-2/_source/`. `engine.py` (graphics, SFX layer, comic cards) plus `plans.py` (per-video shot list and auto SFX cues from picture events), and `base.py` (the muffin renderer). A new video = a new `build()` branch plus `scripts-for-render/<name>/script.txt`. Renders in about 30 s.
- **SFX:** 32 Mixkit free SFX in `~/NoxyAssets/sfx/mixkit/` with `onsets.json`; align to `peak_t` for hits and whooshes. Mixed at SFX_DB −15, a median 21 dB under the voice. Critic rules: coin/reward sounds ONLY on good (green) numbers; bad numbers get a bass hit or fail tone; no reward sound on "+0.0 KG"; no camera shutter on a UI card (use a swoosh plus click).
- **Video critic recurring asks:** visible change by about 0.8 s; no static hold over ~2.5 s (split with a fox plus a top-third TAG, e.g. "NOT A DIET FAIL. / A WEEKEND FAIL." or "DON'T QUIT"); chapter cards 1.25–1.45 s; never let a payoff shot run under ~0.6 s after a card; a promise line must be paid off ("Sunday is the part that hurts" failed); numbers must reconcile ("-3 kg" vs "two kilos of water" got flagged); hedge claims ("up to 240"); the hook comparison should be at true relative scale from frame 0; don't reuse a pose. Tags sit at y≈110–150 so they clear the ears.
- **Phrase lookup pitfall:** `T('three kilos')` matched the hook's earlier "three kilos". Always pass `after=I(...)` for repeated phrases, and check plan.json times against words.json.
- **Voice pipeline fixes:** `pick_assemble.py` now penalises >215 wpm (/15) and median pitch more than 2 st off 118 Hz (×3/st), prints each line's final length (verify LTEMPO actually applied), and supports `LSKIP`. NEVER trim the head of a line starting with a nasal: trimming 0.18 s turned "Noxy" into "Oxy". CTA "Comment Noxy…" seed 19 (~197 wpm) beat the fast seed 7. Split a question+answer line into two generations ("So two of those three kilos?" / "Mostly water.") and FORCE a take that rises; the picker treats question lines poorly. Once a take is approved, lock picks with FORCE before changing scorer weights. Voice critics took 2–4 rounds per narration (7 → 8/10).
- Old critic briefs said "Noxy is genuinely free". That is WRONG; never reuse that line.

## Manga workout slideshow format (2026-10-16)

The user asked for a recreation of @manga.form, @nexofit.us and @deinfitnessmangae, which are workout-app accounts. Each one's winners are photo-mode carousels:
- @deinfitnessmangae: 1.8M views.
- @manga.form: 239k views with 4.5k followers.
- @nexofit.us: 180k views.

**The format:** huge Anton headline (black line plus coloured line); a manga ink character with the working muscle in one flat colour on pale grey; STEP 1-4 2x2 exercise grids with sets x reps; a weekly plan; app on a phone mid-carousel; closer "SAVE THIS / DAY 1" with a number comment prompt. Saves run 35-90% of likes.

**Slide count and structure vary by post; there is NO fixed 10-slide rule (user correction).** The variant menu (A poster 2 slides, B muscle-by-muscle 5-6, C step guide 9-11, D day split 7-8, E one move per slide 7-12) is in the noxy-tiktok-slideshows skill. render.py takes any number of slides from slides.json. Add new slide kinds (poster list, single-muscle page, day page, single-move page) as needed instead of forcing the 10-slide plan.

**First sample (variant C) Noxy adaptation:** abs workout, then "THE PART EVERYONE SKIPS: THE KITCHEN" with numbers, then the real app screen. Kit: `~/Desktop/Noxy/Noxy-2026-10-16-Fox-Manga-Abs-Slideshow/_source/render.py` + `slides.json`. Fonts: Anton, Oswald and Inter (OFL). The approved fox is redrawn in manga ink style (`gen/cover-fist.png` is the style anchor). Pass the anchor plus the manga.form grid slide as references for the 2x2 sheets.

Critic lessons (6.5 → 8/10):
- Weekly plan sets/minutes must add up ("pick any 2 moves from each step").
- Keep text away from the right ~15% of the slide, where TikTok's buttons sit.
- On the app slide, magnify the real card in an inset with the numbers circled; a small phone is unreadable.
- The cover needs the colour-coded muscle map.
- Flat colour blocks look like stickers. Re-tint them with shading and hatching (`inkify`, morphological opening to remove fur speckles).
- Check that the exercise poses are right, especially bicycle crunch twist, shoulders lifted for heel taps, and hips up for side plank. Regenerate single panels and paste them into the grid instead of regenerating the whole grid.
- A muscular fox may draw "furry" comments.

Music (checked against the reference posts' audio): every winner uses an in-app TikTok "original sound". These are dark, slowed phonk/orchestral beds or anime and motivational voice clips: "Original invincible sound" (Invincible: "Don't forget, I'm invincible", 1.6M), "Do it kakarot" (163k), "Kingdom Beat - TikTok Version" (115k), and gym-speech edits (239k, 234k; contain profanity). For Noxy, recommend clean, beat-only or clean-voice hype sounds picked IN-APP; avoid explicit speeches on a brand account. Business accounts are limited to the Commercial Music Library. Library fallback: the phonk_brazilian_MondaMusic bed.

Title/caption (checked against the reference posts): every reference slideshow leaves TikTok's TITLE field EMPTY. The cover headline does that job. The caption follows manga.form's style: one casual lowercase line, a number comment prompt, "tracking mine in Noxy" (tag Noxy's account if it exists), and 4-5 hashtags. Sample: "16 moves, 4 steps, and the part everyone skips 💀 save this for your next ab day and comment your hollow hold time 👇 tracking mine in Noxy #abs #absworkout #homeworkout #gymtok #calorietracker".

## Delivery

Use one tidy dated folder under `~/Desktop/Noxy/`, numbered images, `_preview`, `POSTING.md`, and source/guide files. Deliver an inline preview plus a tested ZIP and a short file tree. Open the folder in Finder (Windows: `explorer.exe`). Save reference assets by copy and checksum without moving the user's originals. Do not treat a request to create a character as approval to render or post the full video.
