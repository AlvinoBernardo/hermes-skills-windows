---
name: short-form-video-critic-loop
description: Use when critiquing a Reel draft for retention or voice.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, reels, tiktok, critique, subagent, music, retention]
    related_skills: [video, noxy-ai-fitness-videos, noxy-hook-demo, talking-head-tiktok-edit]
---

# Short-form video critic loop

## When to Use

Use when the user supplies reference reels and wants a recreation that a reviewer judges "ready to post" and "worthy of N views like the references". Use it whenever the user asks to critique and keep improving a draft. Format-specific skills (e.g. noxy-ai-fitness-videos) carry the look. This skill carries the loop and the retention rules. When the user reports a published video flopped, start from these rules rather than the flopped edit's spec. This is also the skill to use when the user asks for a check of where a finished video will lose viewers. It predicts drop points from the edit; it does not read real platform retention graphs, so say so.

**Brain-simulation requests:** if the user asks for the skill that "simulates the brain" to check retention, they mean Meta TRIBE v2 skills. None is installed. The hub's `meta-tribe-skill` was vetted and rejected, and the reasons are in `references/brain-model-retention.md`. Give that verdict and offer this loop instead of re-vetting from scratch.

## Procedure
1. **Analyze the references from real data, not memory.**
   - Transcribe with word timestamps: faster-whisper `small.en`. Decode to 16 kHz mono WAV with ffmpeg first, then pass a numpy array, because some PyAV builds reject faster-whisper's `metadata_errors` kwarg on direct mp4 input.
   - Make 1 fps contact sheets: `fps=1,scale=240:-1,tile=8x4`. This Homebrew ffmpeg may lack `drawtext`, so label in PIL instead.
   - Measure wpm, loudness, hook wording, CTA and list/number structure.
   - Look at full-res frames for caption font, size and y position.
2. **Match the benchmark the user actually states.** If they correct the target (e.g. 100k → 10k because the references get about 10k), ask the critic exactly that question.
3. **Build the draft with a data-driven renderer.** The script lives in `script.txt`. The shot plan anchors to spoken phrases, and narration is aligned with Whisper + difflib. Any re-voice then re-times every cut and caption automatically. Render a stills sheet first, inspect it, then do the full encode. Full-decode check and measure LUFS before calling a render done.
4. **Write the critic brief once** (`critic_brief.md`) and generate a per-version folder: contact sheets, first-3 s strip at 4 fps, plan.json, script, and the brief with paths substituted. Details are in `references/critic-brief.md`.
5. **Dispatch the critic** via `delegate_task` in the background, then end the turn with a one-line status. On return, implement every cheap fix and re-render. From round 2, append a "Round N context" listing the previous fixes for FIXED/PARTIAL/NOT FIXED marking.
6. **Stop** when both answers are YES and no blocker remains. One more polish round is worthwhile if it's cheap. Put the score history in POSTING.md and tell the user the scores are a model's judgment, not a view forecast.
7. **Deliver a copy-paste narration script file** whenever the user will re-voice (e.g. Voicebox). Include delivery notes and the exact re-render command.

## Voice gate (before the video critic)
A placeholder TTS voice is not deliverable. Users reject "very AI" narration even when the edit scores well. Run a separate VOICE critic subagent on candidate takes before rendering, and iterate until it says the best take sounds as good as the reference narrator. The procedure, metrics and Voicebox API are in `references/voice-quality.md`. Use `scripts/prosody.py` to measure takes, `scripts/gen_lines.py` to queue per-line Voicebox generations, and `scripts/pick_assemble.py` to pick the best take per line and master the result.

## Sound design
Alongside the music edit, add real SFX on picture events the renderer already knows: a pop on each circle or label, a whoosh on cards and cuts, a hit on the hook flash, a ding on key numbers, a stamp on "DONE" moments, ticking under clocks or stopwatches, a UI tap on the app card and a notification on the CTA. Mix them about 18–22 dB under the voice so they never mask words. Store sourced or synthesized SFX in the brand asset library and log them. The sourcing, alignment and mixing recipe is in `references/sfx-layer.md`.

Critics flag SFX that contradict the picture, so set the semantics up front:
- **Sound mood matches meaning:** reward sounds (coin, ding) go only on good or green numbers. Bad or red numbers and "+0.0 kg" get a bass hit or fail tone.
- **Sound lands on screen:** every cue must fire while its object is visible. A cue under a black card, before the graphic appears, reads as a mistake.
- **UI tap, not shutter:** use a UI tap or swoosh on an app card. A camera shutter implies a photo was taken.

## Retention rules critics enforce (apply before round 1)
- **Sound-off hook:** bold text in the top third for 0–2 s, with a visual change inside 2 s (before→after flash, true-scale comparison).
- **Curiosity:** the hook poses a question or open loop that the body pays off explicitly. Don't reveal the answer in the banner.
- **Comparisons:** show at true scale. Equal-size circles make the wrong item look bigger and contradict the point.
- **Shot length:** no static hold over 2.2 s. Every shown noun appears on its spoken word, so check that the pop time falls inside the shot window. Don't reuse a pose. Replace generic standing poses over key facts with a diagram (stopwatch, jars, versus labels).
- **Chapter cards:** 1.2–1.5 s each. Light title words left-to-right on a fixed stagger, not tied to speech. Draw the title baseline-aligned (PIL `anchor='ls'`), because centering per-word sprites makes lowercase words float. Keep big digits dim from the first frame.
- **Product proof:** real UI only, large (about 85–90% width), a push of 1.1× or less so text never crops at the edges, captions kept on.
- **CTA:** one ask only. Comment-keyword plus DM is lower effort than "search the App Store". Never claim the product is "free" (or any price) unless the user confirms it. App Store `formattedPrice: Free` does not settle it: a free download can still be a paid product, and the user's word wins. For Noxy, never say free. End about 0.5 s after the last word so it loops.
- **Claims:** keep them plausible and non-absolute ("most filling macro", not "most filling thing"). Avoid lines that read as permission to overeat. Hedge partial truths in both the voiceover and the card ("up to +240", "~1,070").
- **Numbers agree everywhere:** the hook, voiceover and graphics must use the same figures. A "-3 KG" hook followed by a bare "2 KG water" makes viewers ask about the third kilo. Say "two of those three kilos" and label it "2 OF 3 KG".
- **Every tease is paid off:** if the hook or line 2 promises something ("Sunday is the part that hurts", "the last one is hiding in the chicken"), the body must visibly deliver it. If it doesn't, rewrite the tease to match what is shown.
- **List promises get a visual:** while the voice says "three things you never count", show "#1 ??? / #2 ??? / #3 ???" slots with the teased slot pulsing. Back-to-back generic standing poses there are where viewers drop.
- **No micro-shots or repeated ideas:** a shot under about 0.5 s reads as a glitch. A term card, then a title, then a number card for the same word is too much, so drop the duplicate.
- **Product-proof rings:** ring only what the voiceover mentions, and check that each ring's time falls inside the shot window. A ring timed at the cut never shows.
- **Stamps and badges:** the text must fit inside its border. Suppress captions on that shot so they never overprint it.
- **Script:** don't copy reference lines verbatim; keep the format, change the wording. Point of view stays consistent (I vs you).

## Music
A flat looping bed reads as boring. Edit the music to the picture: put the track's drop on the hook flash, and use whooshes into section cards with a low-pass under the cards. The recipe is in `references/music-to-picture.md`.

## Image cutouts
When generating poses on a flat background and keying them out, follow `references/flat-bg-keying.md`.

## Batch mode
For a batch of several videos, run one voice critic per narration plus one video critic per draft, all in a single `delegate_task` fan-out. Group fixes by file: voice regeneration in the background, then shot-plan edits while it runs. A shared engine with per-video plan functions beats copying a renderer per video. Expect every round-1 draft to land around 7/10 even with the retention rules applied. Rules about promises, numbers and SFX semantics are the usual blockers.

Before a new batch for a brand, re-check the benchmark account's latest posts. The user tends to say "check what I posted" without giving view counts. The logged-out fallback is in `references/sfx-layer.md`.

## Pitfalls
- **A critic YES is not the user's taste.** Model critics converge on generic retention rules and will score edits 8/10 that the user then rejects. When the user has a taste-driven format (fan edits, aesthetics), get his reference edits first and judge drafts by a side-by-side grid against the reference (every 1-2 s) plus his notes. Use the critic loop only for technical QA (sync, loudness, text on faces, logos, broken frames).
- **Critic briefs carry user facts too:** never copy an old brief without re-checking its claims. A stale "the app is free" line in a brief can leak into a critic's suggestions.
- **zsh word-splitting:** zsh does not word-split a command stored in a variable (`R="uv run … python render.py"; $R out.mp4` fails with "no such file or directory"). Put multi-render loops in a bash script or a shell function.
- **Sliced edits:** when replacing a block of a renderer by slicing between two text markers, check that no helper function sat inside the slice. A deleted helper only fails at render time.
- **Long shells:** commands past the foreground timeout get promoted to background. Wait on the session instead of re-running them.
