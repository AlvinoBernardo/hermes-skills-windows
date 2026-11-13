# Template port: a proven edit rebuilt on a different anime

Use this when he loves an edit (ours or a ref) but doesn't want a copy. Keep the template's song section, the timing of every cut and word, and its signature moves (sticker cut-outs, night grade, the heroine's own line in the song's pause, the font-cycling payoff word plus a memory inset). Rebuild every shot from a different anime of the SAME genre.

Worked example: `edits/14-bb-her-template/`. It is our edit 07 (JVKE 'her' on Fragrant Flower) rebuilt on Blue Box: 79 slots, 61.4 s. Scripts are in `work/`.

## Procedure
1. **Get the template's structure.**
   - If the template is one of our own edits, read its spec (`edits/07-ff-her-v2/work/spec_d3.json`: cuts, clips, words, insets, overlays, particles).
   - For a foreign ref, use ref_dissect. Its cut detection fails on text-heavy edits (on one it reported an 18.6 s "hold" where shots change every second), so read the cuts from the 1 fps sheet or a 4 fps strip instead.
2. **Write `work/slots.json`, one entry per slot.** Each entry has start, end, dur, the words on screen, and the flags sticker / night / words_behind_subject / transition. Add 3 template frames per slot at 20/50/80 % of the slot (`tframes/sNN_{20,50,80}.jpg`, cropped to the 16:9 band) and a `tframes/_all.jpg` overview.
   - Do the frame grabs in Python with a thread pool of at most 4. A bash `while read` over a text file that Windows Python wrote gets CRLF line endings into the filenames.
3. **Build the audio on the template's own timeline.**
   - If the master isn't on the machine, take the song segments from our own delivered render of the template. It's the same timeline, already mastered.
   - Replace only the dialogue block.
   - **Lip-sync the new line:** picture source time must equal audio source time. End the picture at the source's next cut and go black for the rest.
   - **Fill the pauses inside the line.** Add a wet-only reverb bloom of the song's last sung word under the line: noise IR with a ~1.25 s decay, low-passed at ~3.5 kHz, about -25 dB RMS. Never leave a stretch under about -40 dB, because a 1 s hole reads as a dropout on a phone.
   - Black before the payoff: about 0.5 s (0.74 s read as a freeze).
   - Put the payoff cut 0-1 frame BEFORE the drum hit.
   - Script: `work/make_audio_full.py` prints pause_db and pause_min20ms; check both.
4. **Optional quick test.** When he wants speed, render only the payoff section (~12 s) first. Use `work/build_spec.py` + `make_audio.py` as the small version.
5. **Pick shots.**
   - Brief: `PICK-FULL.md`, read on top of BRIEF.md (verified character looks, footage, rules).
   - Split the pickers by slot range: 3 at most on the PC, with a 15-20 min cap each.
   - Each picker CLIP image-searches with the 3 template frames of its slot. On a different anime this finds the same composition and mood, not the same shot.
   - Every pick gets verified by eye on 2 frames inside its window.
   - **No duplicate shots:** pickers read and append `picks/claims.jsonl` ({file, in, out, slot}) before they finalise a pick. Pre-claim the shots of any earlier test. After merging, run an overlap check on the assembled spec anyway: one pair still slipped through on edit 14.
   - The CLIP index needs `thumbs/` plus `clip/*/embeddings.npy`. Build both before dispatching the pickers (see `ikkimi-windows-pc` for the PC).
6. **Build the spec** (`work/build_spec_full.py`).
   - Keep the template's cut times, word timings, positions, transitions, sticker/matte flags, inset and particles.
   - Map every template font to a different face of the same role, and every accent colour to the new palette. Edit-14 map: Yellowtail -> Dancing Script 700, Montserrat 900 -> Archivo Black (scale_x x0.9), Abril Fatface -> Gloock, Playfair Italic -> Instrument Serif Italic, Cormorant -> Italiana, Sacramento -> Great Vibes, Fredoka -> Baloo 2. Colours: red/pink/cream -> blues, with navy strokes.
   - Then apply the rendering fixes below **before the first full render**.
7. **Render under `scripts/run_low.py`** (below-normal priority, half the CPUs; ~6 min for 61 s with fresh mattes). Then run `work/glitch_scan.py <mp4> <spec> <out.json>`. It does one gray decode at 192x108 and reports black frames, stray single frames, frozen runs, odd frames at cuts, and clip windows that run past their source shot. Inspect the cut strips it points at: zoom-blur and flash transitions also show up as odd frames.

## Rendering pitfalls (everything he called "rendering problems" on the first full draft)
- **Replacement fonts overflow the frame.**
  - The template's positions were set for narrower faces: 25 of 166 words ran off the edge (THANK, TRYING, "WAS LOOKING FOR" showing as "OOKING").
  - Measure every word, and every font-cycle variant, with PIL using the engine's size formula: font size = height x 1080 / (bbox height of "H" at 200 px / 200).
  - Shift words inward to stay inside 3-97 % of the width. Set `max_width: 0.94` only when a word is wider than the frame.
  - `text_width()` in `build_spec_full.py`.
  - **Skip scrolling words** (`x_to` / `y_to`, e.g. the sliding "LOOKING LOOKING LOOKING"). They leave the frame on purpose, and fitting them shrank the word to a tiny clipped strip.
- **Words that pop in 1-2 frames after a cut** ("LOVE" at 23.3) look like a lag. Snap any word whose start lands within 0.07 s after a cut onto the cut, and shift its `typing` times with it.
- **The template's look washes out the new anime.**
  - A lifted grade (gamma 0.92, lift, glow threshold 0.6-0.72, rgb_split) tuned for one show flattened Blue Box's pastel shots and blew the heroine's eyes to white.
  - Reset it: gamma 1.0, lift 0, contrast ~1.05, glow 0.16 @ 0.84, rgb_split 0.5.
  - Before the full render, check 5 bright shots as raw-source vs render pairs.
- **The template's word positions were set for ITS faces.** Check every slot's words against our frame, and move any word sitting on a face to the bottom band (y 0.84).
- **A black flash effect on clip 0 gives a black thumbnail.** Remove it and show the title from frame 0.
- **Sticker slots:** small figures in the source give a tiny cut-out, so zoom 1.3-1.55 onto the figure. Words that were white on the template's cream card disappear on white: recolour them to the palette accent with a dark stroke.
- **Small connector words:** give them a height floor of 0.12 and a 3 px dark stroke, or they're unreadable on a phone.
- **Payoff word:** drop thin script faces from the font cycle, because the weakest face can land on the key beat. Make it bigger, with a 3-frame flash plus a small shake on the hit. Keep it off her face, beside the inset.
- **Inset stills:** check each still at inset size, with its focus_x set on the faces. Default centre crops landed on a microwave and a chair.

## Text flicker (he called it "still a lot of rendering issues, stuff flickering for the text")
Four causes. Fix all of them in `build_spec_full.py` before the first render:
1. **1-frame text gaps at cuts.** Template times rounded to 3 decimals (word end 3.366, next start 3.367) fall inside a frame. The engine shows a word while start <= t < end, so at 19 cuts NO word was on screen for one frame, a blink on every cut.
   - Snap every word start/end, `typing` time and `cycle_times` value to whole frames: `round(t*30)/30 - 0.0005`.
   - Check: count frames where the number of active words drops to 0 for 1-2 frames. It must be 0.
2. **Behind-subject words the subject mostly hides.** Coverage over 0.5 (FOR 0.96, DREAM 0.89, TELL 0.84) reads as broken text. Coverage that jumps (std over 0.05: NEVER 0.26, TELL 0.23) reads as flicker.
   - `work/behind_fix.py` measures coverage per frame from the render's cached mattes.
   - Keep a word if its coverage mean is ≤ 0.30 and std ≤ 0.05. Otherwise search an (x, y) grid for a low-coverage spot that stays behind the subject.
   - If no spot works, put the word on top in the bottom band, or the top band if another word is already there.
   - Leave sticker slots and layered echo words (same text and start) alone.
3. **Mattes every 2nd frame with no smoothing.** The occlusion edge steps at 15 fps and rembg drops single frames.
   - Use `matte.reuse: "frame"` + `matte.temporal: 2`: an engine option added for edit 14 that takes the median of the raw mattes at f±2 inside the shot.
   - On sticker clips use `temporal: 1`.
4. **Flashing words.** Drop words that are on screen for fewer than 3 frames. Slow the payoff font cycle from 6 to 12 frames, because 6 reads as a strobe.

Also give slowed clips (speed < 0.98) on 24 fps anime `interp: "flow"`, or they stutter on repeated frames.
Tools: `work/flicker_metric.py spec a.mp4 b.mp4` (oscillation inside each behind-word box; it also picks up 24-to-30 fps judder, so confirm on 8-frame strips) and `work/glitch_scan.py`.
Note: the engine's `--start/--end` flags do NOT limit the rendered frames, so a test render is always the full length.
