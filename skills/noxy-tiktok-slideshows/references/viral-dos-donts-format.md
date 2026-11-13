# Viral DOs and DONTs format (`viral-dos-donts`)

The user supplied a viral TikTok slideshow and approved its recreation as a THIRD female format. Their standing rule: when a batch has 2 or more female slideshows, exactly ONE of them uses this format. The original source slides are saved in `Finished-slides/dos-donts-belly-fat-20261008/reference/`. The first recreation is in the same folder. That user-reported virality is the reason for the test. It does not show that this format will outperform the others.

## Slide grammar (8 slides)
1. Cover: a dark, moody gym POV photo (legs on a leg press, feet on equipment). The hook is centered at a small size, about 60px, in TikTok Sans with a thin outline. It is NOT the Arial Black cover style. The default hook is `DOs and DONTs to lose belly fat.`
2. AI before/after: two separate Codex images placed side by side, 1080x1440 (3:4). A center line of text such as `Trust me ik ball`, then month labels on each half, for example `July 2026` and `October 2026`.
3. Reality check over a dark POV gym-floor photo: `First remember.` / one myth line / one truth line, for example spot reduction.
4 to 6 and 8. Alternating `Do.` / `Don't.` slides. A big label (82 to 90px), a 52 to 56px action line, and a 42 to 44px reason line. The text is offset and loosely placed like native TikTok text. Photos: berries on bedsheets, a yogurt bowl on black, socks next to dumbbells, a dim bed scene. The final slide can be a cheeky one like `Sleep in a plank position`. That was the original's ending, kept because it is a joke.
7. `DO.` track slide with Noxy. A Codex-generated hand holds a phone in a dark setting with a pure #00FF00 screen. Then `render.composite_screen` puts the REAL Noxy screenshot onto it (`assets/noxy-home-real.png`, the fox home screen). Text: `track your macros & progress` plus a casual body that ends `(I use Noxy)`. Never use an AI-redrawn app UI as the main version. Keep the text clear of the phone.

This format has no standalone `I also use Noxy` App Store card slide. Slide 7 is its CTA.

## Before/after realism (the v1 post FLOPPED, and the user blames an AI-looking image 2)
v1 failed with a warm, evenly lit studio look, a clean seam, crisp HD and a chiseled six-pack in the after. v2 (`Finished-slides/dos-donts-belly-fat-20261009-v2/`) fixed it as follows. Follow it every time:
- Prompt for an amateur iPhone mirror selfie: cool daylight plus a ceiling light, auto-HDR, slightly tilted, mirror smudges, a lived-in home (stair railing, frames, shoes on the floor, couch, shaggy rug), lint specks on the leggings, sweaty shiny skin.
- Before: a clearly soft belly with a pooch folding slightly over the waistband. After: flatter with only faint definition, NOT a six-pack or fitness model.
- Generate the before first, then make the after as an image edit of the before (`image_url` = the before) so the room and lighting match exactly.
- Wording that trips the safety filter: anything like 'pulling the waistband down'. Use 'hand resting on her hip'.
- Finish it like a repost: downscale to about 590px wide, JPEG quality ~58, upscale back, light unsharp mask and grain. The seam stays as a soft hard cut, not a white line.
- Check it before rendering: would a viewer clock it as AI? Reject it if it has a glossy studio look, perfect symmetry or a chiseled six-pack.
- Crop each half around the BODY, not the image center. A blind center crop of the after cut off the hand resting on her hip, and the user noticed. Choose the crop box per image (v2 used before x30-632, after x0-602 at full height, about 1080x1300 total), then check that both hands and the belly are fully in frame.

## Underperformance diagnosis and V2 direction (user, 2026-10-13)
The user says this format NEVER performs well and asked for an iteration. These are hypotheses from comparing our versions against the viral original. They are not measured causes.
- Slide 2 must pay off the belly promise. Use TORSO crops (chest to hips, no faces) with the belly visible in both halves, in a similar outfit type and light. Full-body shots of two obviously different people with the belly hidden under clothes give no payoff.
- Use myth-busting, contrarian tips (fat-burning teas and waist trainers, lifting won't make you bulky, salt and water puffiness, the lower belly goes last) instead of generic protein, walking and sleep advice.
- End on a joke slide to bait comments. Examples are `Sleep in a plank position` and `Laugh every day / Free ab workout`.
- Rotate the cover style. Repeating the leg-press POV makes repeat viewers recognise the post.
- Use dark, moody photos where the subject is still clearly lit. Avoid near-black photos.
- Keep the text tight: a big label, one action line of about 7 words max, and one reason line of about 16 words max.
The first build is `four-female-two-male-54/female-04-v2/`. Wait for performance feedback before replacing the rotation template entirely.
The user then said to change the hook too, and that the format's rules don't have to be followed strictly. The hook `DOs and DONTs to lose belly fat.` is no longer mandatory, and the earlier rule requiring user approval for variant hooks is lifted for this format. v3 (`female-04-v3/`) is v2 with the hook `things nobody tells you about losing belly fat`. Freely vary the hook, the slide grammar and the Do/Don't labels when it improves the post. Keep it weight-loss relevant and truthful.
The user then had the before/after `Trust me ik` slide REMOVED, believing it is the reason this format underperforms. The default for this format is now NO before/after slide: cover, then `First remember`, then Do/Don't slides, the Noxy slide and the joke ending, 7 slides in total. Current build: `female-04-v4/`. Do not bring a before/after back unless the user asks.

## Production per new package
- Copy `render.py` and `prep.py` from `dos-donts-belly-fat-20261008/` into a new batch folder, and write a new `slides.json`. The font is `assets/TikTokSans-VF.ttf` (OFL).
- Run in parallel: one subagent generates NEW before, after and green-screen phone images with Codex image gen. Change outfits, rooms and the phone setting (car, bed, gym bench, kitchen) every time. A second subagent sources NEW dark, moody Pinterest photos using queries that always include `aesthetic`. It returns a/b/c picks per slot and dHash-checks them against the library and previous viral packages.
- Vary the advice in every package. Keep the Do/Don't rhythm, but change the myth slide and the tips, for example protein, walking, sleep, alcohol, liquid calories, weekend portions, crash dieting, endless cardio. Do not repeat the first package's fruit, carbs, abs and plank set. Keep it clear and casual, with no dashes or semicolons.
- Hook: the exact approved string is `DOs and DONTs to lose belly fat.` Variants such as `DOs and DONTs to lose weight.` need user approval before use. Log every hook in `hook-rotation.json`.
- Caption: put the AI disclosure for the before/after in the caption and advise using TikTok's AI-generated content label. No on-image AI badge. Pinterest reuse rights are unverified.
- Delivery: a preview contact sheet plus a ZIP per package, the same as for other formats.
