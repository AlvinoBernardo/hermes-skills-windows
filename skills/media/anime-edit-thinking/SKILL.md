---
name: anime-edit-thinking
description: "Use when planning an anime edit: refs to story to beats."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [anime, edits, storyboard, creative-process, ikkimi]
    related_skills: [ikkimi-anime-edits, anime-edit-engine]
---

# How an anime editor thinks (the user's own process)

The user used to be an anime editor, and this is how he works. This skill decides WHAT to make; `ikkimi-anime-edits` is how to execute it. A technically clean edit made without it comes back as "decent but it doesn't hit hard".

## When to Use
Before shot picking or rendering on any anime edit: when he sends references, gives a story idea, or says a draft doesn't hit. Also on every draft before it's shown (the QA gate, step 6).

## 0. Original mode (no ref to copy)
When he wants an edit without copying a ref, use `references/editor-brain.md` (concept card -> per-genre grammar -> our signature look). Refs then only update the grammar; they are never rebuilt.

## 1. Watch the refs as a fan, then as an editor
For each reference, write three things in BRIEF.md:
- **What I like:** the moment you'd replay. Name it concretely ("the vow over a held face, then the drop", "one giant word per beat", "Asta crashing in on 'Frozen'").
- **Why it works:** contrast (quiet/loud, blue/red, still/flicker), a payoff, or a lyric that matches the action literally.
- **What I'd change:** what's generic or what everyone already does.
Choose the copy level from his wording (see `ikkimi-anime-edits`). "Recreate it" means 1:1 with small differences: copy the ref's shots on the same beats, and name the key moments that must land there. When he calls a rebuild "completely copying", do a **template port** instead. Keep a proven edit's song section, timing and signature moves, and rebuild it on a different anime of the same genre (`ikkimi-anime-edits/references/template-port.md`). Write each slot's JOB (who, shot size, mood, brightness, motion, the literal lyric), not a shot ID. The new show's own versions of the key moments go on the same beats. Only when he asks for an original take: steal the 2-3 strongest *ideas*, not their surface, and pull the best idea from each ref into ONE edit.

## 2. Story first (storyboard), then the song
A hype edit that hits is a tiny story with a turn, not a montage. Write 3-5 beats in plain words before touching footage. When he gives an idea as a story, that IS the spec. Example (BC S2 ep 4):
1. **Vow:** Nacht 「今ここで、限界を超える！」 over his face.
2. **Attempt:** he throws everything at the devils; fast, escalating cuts.
3. **Failure:** impaled, battered, then kneeling and looking down (a held shot).
4. **Turn:** on the payoff lyric ("Frozen inside"), Asta crashes in swinging his sword.
5. **Release:** Devil Union hits through the loud part; end on the strongest face and stop.
Setup -> failure -> rescue is what makes it hit. **The turn shot must be the moment fans expect** (find it in the refs, then CLIP-search for it with those ref frames). A "close enough" shot from the same scene kills the payoff.

## 3. The song serves the story
- Pick ONE continuous section whose energy curve already fits the storyboard: a big hit at or near the start, a thinner bar for the failure, the payoff lyric for the turn. Start on a phrase start; an entry mid-phrase sounds random.
- **No mid-song splices, filter sweeps or muffle effects.** He hears them as random transitions.
- The lyric should comment on the image literally at the key moment.
- A trending sound is a bonus, not the reason.
- Dialogue: lay it over the song or drop it into a real gap; never stop the music for it. A plain duck still leaves the song's own vocal under the line (two voices at once). Instead, low-pass the bed to ~400 Hz at about -10 dB under the line, go near-silent for the last ~0.15 s, then switch to full range on the attack of the next hit (a 4 ms crossfade). That gives a real 6-8 dB step into the drop. A short dramatic pause between the two halves of the vow helps too. Take the line from the cleanest source, high/low-pass it lightly (110 Hz / 11 kHz), and set its level by its peak; a quiet fan rip pushed up 10 dB sounds cheap. Recipe: `edits/10-bc-refmix/work/v2/make_audio_v4.py`.

## 4. Map beats to the music
- **The first second must hit:** music already playing, text on screen, motion or a flash. A dry line over a still face is not a hook.
- **Hitting hard = contrast + timing:** a hold (still, dark) right before the hit, then flash + shake + fastest cuts ON it. Constant intensity hits nothing.
- **Land each hit on the measured sung attack**, from raw onset peaks of the song: the syllable onset and the downbeat after it. lrclib line times and beat-grid guesses run 0.1-0.3 s early or late, and a cut 0.3 s before the vocal lands on nothing.
- Escalate the cut speed toward each payoff; flicker bursts at climaxes only.
- Colour tells the story: cold blue while fighting, desaturated while losing, red/magenta when the hero arrives.
- Text belongs on screen: lyric words through the song (bottom band y ~0.84 when a face fills the centre), small typed Japanese on the dialogue, and its English meaning in the black bar under the picture (never on the footage). Keep the payoff shot itself clear of big text.

### Sad / score-music edits (Reze 'in the pool', edit 11)
"Don't fully copy it" = original-take mode: keep the refs' spirit, change the order, the drop shot and the ending. The user rejected three drafts as "doesn't hit": draft1 cut at random, draft2 put every cut on an accent, draft3 used a uniform 0.8-1.6 s cadence. What fixed it:
- **Breath before the drop.** Dialogue/text ends, then ≥0.7 s of empty black + silence, then a hard cut to a bright face whose motion starts on the hit.
- **Pulse and hold.** 1-beat cuts while each 8-beat swell rises, then one iconic image held ~3.2 s while it falls (TT ref: underwater hands, festival walk, kiss). A flat cadence hits nothing even when it's on the beat.
- **Joy first, one turn.** Keep the montage happy (memories). Make ONE hard cut to the loss where the music thins, then black while the song fades. Scattered sad shots and a 10-beat death sequence kill it.
- **Make the drop answer the last line.** "I never went to school either" → the school pool/classroom on the drop.
- **Motion and brightness.** Shots that move and read instantly, with the motion peaking just after the cut, and a bright saturated grade. No added zoom punches. Flashes go only on a couple of section downbeats, decaying FROM the cut frame. Cut ~2 frames early (the TT ref leads by ~2.5 f).
- **When he says it still doesn't hit, do the deep ref analysis.** He asked for 2 independent subagents on the same question, using ref-vs-ours per-beat sheets and a music swell map. They agreed, which made the fix trustworthy. Cap them at ~20 min with a time check; he complained at ~28 min.
- **Dialogue edits with a translation:** JP + EN both typed live over the spoken span (EN word-by-word, finishing with the JP), in the black bar under the picture.

## 5. Make it yours (without touching what hits)
In the default 1:1 mode, never change the order, section, cut times or key shots: those are what he feels, and changing them is why free-styled versions failed. Make it ours only on the surface: a different text font + colour, our own last ~2 s, no ref credit card, our grade. "Different font" means a different typeface with the ref's own treatment kept (blend mode, opacity, size, placement). Swapping the ref's designed blend for a stock gradient fill is what reads as a cheap default font. That is enough for viewers and the ref's fans to see a different video. Never alter the ref's actual file (mirror/crop/speed/noise) to dodge duplicate detection; rebuild from source. Change order, colour arc or section only when he asks for an original take.

## 6. QA gate: an independent subagent before every show
After each render, before the user sees it, spawn ONE subagent with `templates/qa-brief.md` (fill in the paths, the storyboard and his past complaints). If he asks to see the draft before the QA returns, show it right away with a short known-issues list, then fold the QA notes and his notes into one fix render. It reviews as a harsh TikTok editor: the hook, the audio (levels, clipping, harshness, unmusical joins, dialogue intelligibility), lyric word timing, the payoff shot, text legibility/placement and every cut (duplicates, logos, burned subs). Fix everything it flags, then show, and re-run the QA on the fixed draft. His notes still outrank it.
- **Sanity-check the critic's measurements before applying them.** A subagent's own beat tracking can lock onto subdivisions (it reported 126 BPM on a 95.7 BPM song and asked to 'snap' every cut off the real beat). Give it the song's verified BPM in the brief, and reject grid-based fixes that contradict it. Its timing of individual words, from onsets plus ref alignment, was reliable.

## Diagnosing his feedback
- **Lip-sync is non-negotiable.** A spoken line must play over the exact shot it came from, at the same offset: take the picture from the same source as the audio and crop or zoom past burned subs or watermarks (GnAvZxYm4H4: zoom 1.27, focus_y 0.40, no Ken Burns, which would crop the mouth). Never lay a line over a 'similar' face from a twixtor pack; he spotted it instantly ("the mouth doesn't even sync up"). If you trim dead air from the audio, cut the picture at the same points. The QA brief must check mouth vs RMS on every dialogue shot.
- "Decent but doesn't hit hard" = no story turn and flat intensity. Fix the storyboard and the contrast, not the effects.
- "Sound quality is shit" = check the dialogue source and its gain, filter artefacts and the limiter gain first.
- "Music transition too random" = an entry mid-phrase, a splice or a sweep. Move to one continuous phrase-aligned section.
- "Font looks like shit" = the text treatment is generic: a stock face with a plain or gradient fill and a soft shadow. Mock 4-6 face + treatment options on clean frames (the ref's blend first), pick the best, re-render, and send the options sheet with the video.
