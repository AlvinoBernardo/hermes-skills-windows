# QA subagent brief (fill the <> parts; pass as the delegate_task context)

Goal: act as a harsh, experienced TikTok anime editor and QA this draft. Find everything that would make it NOT hit hard or look/sound amateur, with exact timestamps and concrete fixes. Don't modify files except your report and QA images under <draft_dir>/qa/.

Environment: <OS/shell notes, the engine python path, ffmpeg, whisper-cli + model path (16 kHz mono s16 WAV), the contact-sheet helper `edits/<edit>/work/isheet.py <video> <out.jpg> <step> <t0> <t1>` (crops the 16:9 picture out of 1080x1920); view sheets with vision_analyze, at most ~25 tiles each>.

Video: <path> (<duration>, 30 fps). Audio master: <path>.
Song: <title, version/speed, section>. Verified tempo: <BPM, beat period, first beat>. Use THIS grid for beat checks; if your own tracker disagrees, it's locking onto subdivisions.
Previous QA report (when re-checking a fixed draft): <path>. Verify each listed fix landed.
Note: the sheet helper crops away the black bars, so grab full 9:16 frames (ffmpeg -ss T -frames:v 1) to check bar subtitles.
References the user loves: <paths + one line each on what he likes in them>.
Intended storyboard: <beat-by-beat with edit timestamps>.
User's past complaints (must not repeat): <list>.

Check and report:
1. The first 3 s as a hook (frames at 8 fps).
2. Audio: RMS per 0.1 s, dialogue vs bed level, sample peak/clipping, harshness, abrupt or unmusical joins, dialogue intelligibility (whisper on the dialogue window).
3. Every lyric word on screen when sung (whisper + onsets); flag >0.1 s off.
4. The payoff/turn shot: is it the intended moment, clearly visible, not covered by text?
5. Text legibility and placement on a phone: not over faces, and not clipped at the frame edges. Check every word's box, including each face in a font cycle (wide faces overflow). Connector words must stay readable at phone size.
5b. Text stability (motion, not stills): 8-consecutive-frame strips at a few behind-subject words and at 5 cuts where the words change. Flag frames where no word is on screen between two words, words on screen for under 3 frames, letters that pop in and out as the subject moves over them, and words mostly hidden behind a character. A 1 fps sheet cannot show any of these.
6. Every cut (4 fps sheet of the whole video): wrong character, duplicates (the same shot twice), black frames (frame 0 especially: it is the thumbnail), logos/watermarks, burned subs, weak shots. Run `edits/14-bb-her-template/work/glitch_scan.py <mp4> <spec> <out.json>` for stray, frozen and odd frames at cuts.
7. Rendering damage: pair raw-source and render frames for 4-5 bright shots. Look for blown-out whites or eyes, washed-out contrast, colour shifts, and a tiny sticker cut-out.
8. Would it hit as hard as the refs? The 5 highest-impact fixes.

PC load (the user works on this machine while you run): ffmpeg with `-threads 2`, at most 2 ffmpeg processes at once, sheets at 2-4 fps rather than full-res loops.

Output: write <draft_dir>/qa/QA-REPORT.md and return a prioritized list (timestamp, problem, concrete fix such as 'move word X to y 0.2', 'shift cut at 6.95 to 7.0', 'lower dialogue 3 dB').
