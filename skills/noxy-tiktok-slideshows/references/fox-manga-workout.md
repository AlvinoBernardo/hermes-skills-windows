# Fox manga workout format (male @noxy.app default)

## Format details: `fox-manga-workout` (user: remember across all sessions, 2026-10-16)
This is the DEFAULT format for every male @noxy.app slideshow. It recreates the viral manga workout carousels of @deinfitnessmangae (1.8M), @manga.form (239k on 4.5k followers) and @nexofit.us (180k). Those accounts promote workout apps. Noxy is a calorie tracker, so the workout is the hook people save, and a kitchen/calories slide bridges to the real Noxy screen. Reference downloads and stats: `~/Desktop/Noxy/Noxy-2026-10-16-viral-fitness-manga/`. Re-check those three accounts for new posts and variants when looking for fresh ideas.

Full recipe, critic lessons, music and caption rules are in the `noxy-ai-fitness-videos` skill, section "Manga workout slideshow format". Kit: `~/Desktop/Noxy/Noxy-2026-10-16-Fox-Manga-Abs-Slideshow/_source/render.py` + `slides.json`. Reference analysis: `ANALYSIS.md` there.

NO FIXED SLIDE COUNT (user correction, 2026-10-16). The first sample's 10-slide structure is ONE variant, not the rule. The reference accounts change length and structure from post to post. Measured slide counts of their top posts:
- @deinfitnessmangae: 2 slides (1.8M, 681k, 506k, 397k, 336k), 5 slides (602k), 10 slides (1.6M).
- @manga.form: 9-11 slides.
- @nexofit.us: 5-14 slides.

Pick the variant that fits the topic, and rotate variants across posts. Never repeat the previous variant. Log each post in `Finished-slides/male-format-rotation.json` `variant_history`.
LENGTH RULE: the user rejected a 3-slide poster as too short. Every @noxy.app fox post runs about 7 to 12 slides, even though the reference accounts' 2-slide posters go viral for them.
- **A. Poster (2 to 3 slides): RETIRED.** Cover plus one 6 to 8 exercise poster. Do not use it. Its topic fits variant E instead (cover, how-to, one move per slide, app, closer).
- **B. Muscle-by-muscle (expand to 7+ slides):** a cover with a colour-coded muscle map ("BEST PUSH WORKOUT"), then one muscle per slide with 2 exercises, a muscle callout and a script-style headline (CHEST / TRICEPS / SHOULDERS / ABS).
- **C. Step guide (9-11 slides):** cover, muscle map, STEP grids, kitchen bridge, app, plan, closer. This is the manga.form style and the first sample's structure.
- **D. Day split (7-8 slides):** a cover with a visual comparison ("1 month to 5 years" consistency silhouettes, "WHICH ONE DO YOU PREFER? cardio vs gym"), then one day per slide. Noxy can add a MEALS page per day (nexofit's 14-slide version alternates workout and meals). The app goes in the middle of the carousel, not the last slide.
- **E. One move per slide (7-12 slides):** a cover, a "how to do it" text slide, then one exercise per slide with name, time or reps, and a 2-frame drawing. nexofit's stretches post used this.

Hooks are short and visual. Cover devices: a muscle map, a comparison (A vs B, a timeline), or a single strong pose. A plain generic phrase (FULL HOME WORKOUT FOR BEGINNERS) only works for the big reference accounts; for @noxy.app, add a challenge or curiosity line that ties to the comment prompt (`can't do 1 push up?`, manga.form's `even if you can't do 1 push-up`, a hardest-muscle question). Keep cover sub lines short, because a long line collides with the fox and the renderer's overlap assert fails. App placement (user, 2026-10-20): the Noxy slide goes in the MIDDLE of the carousel (e.g. slide 7 of 12, after move 4 of 8), never second to last or last. The user said the end placement was "too far in the back". Noxy must always appear ON a slide with the real screen.

The first sample's 10 slides (variant C) for reference:
- Cover: huge Anton headline in black plus a coloured line, with the fox showing the colour-coded muscle map.
- Muscle map.
- STEP 1-4 2x2 exercise grids with sets x reps, one accent colour per step.
- "THE PART EVERYONE SKIPS: THE KITCHEN" with concrete numbers.
- The fox holding the REAL Noxy screen, with a zoomed inset circling kcal and protein.
- A weekly plan whose sets and minutes add up.
- "SAVE THIS. / DAY 1" with a number comment prompt.

Rules:
- Music (from reference metadata, 2026-10-20): top reference posts use reposted "original sound" edits (Originalton/som original), the "Original invincible sound" (Invincible theme edit, 1.6M and 602k posts) and "SLAY!" (phonk, 264k). Recommend: search "invincible" in TikTok sounds first, then a dark beat-only phonk like SLAY!. If @noxy.app is a Business account, only the Commercial Music Library is available, so suggest an epic orchestral or phonk track from it. Title field blank, as in all the references.
- Always use the approved Noxy fox redrawn in manga ink style (`gen/cover-fist.png` is the style anchor), never a human.
- Keep text out of the right ~15% of the slide (TikTok's buttons).
- Never call Noxy free.
- Add TikTok's AI label.
- Title field blank. Caption in manga.form style with a number comment prompt and 4-5 hashtags.
- Next topic ideas (untested): hit every muscle at home, a starting test ("comment your number"), a 4-week belly-fat plan, "3 muscles that make you look lean in a t-shirt".

Critique every new manga package with an independent Claude critic until it gets YES/YES. The PARENT owns this gate; a delegated builder's self-check does not satisfy it. Supply current slides, actual reference images, caption, and the fixed account-style/Noxy-placement rules. Treat the ~10k craft judgment as subjective, not a prediction. Use the read-only review and fix loop in `templates/batch_brief_and_worker_prompt.md`. A delivery may be assembled as a draft while critics run, but update completion ledgers only after final review and archive verification.

## Emily manga workout (`emily-manga-workout`, @EmilyF1tness ONLY)
The fox manga grammar redrawn with Emily's illustrated Korean girl in BLACK AND WHITE manga ink, colour only on the working muscle highlights and accents, on female-searched topics (hourglass muscles, glutes at home, wall pilates, posture). Never for Emma (no AI for Emma). New and untested until the user reports results: say so in POSTING.txt. Same variant menu (B to E, no A), same middle-of-carousel real Noxy slide, same `SAVE THIS. / START MONDAY` closer, same parent critic loop as the fox.

Character consistency (do this BEFORE spawning workers):
1. The parent generates ONE shared ink anchor and saves it to `<batch>/_shared/emily-manga-anchor.png` (plus a front/side/back turnaround), then every worker passes it as `image_url` for every panel. Independent workers each redrawing from the colour anchors drift into different girls across posts.
2. Working anchor call: `image_url` = colour identity anchor `four-female-two-male-60/emily-02/_source/gen/cover-v2.png`, `reference_image_urls` = [fox ink anchor `Noxy-2026-10-16-Fox-Manga-Abs-Slideshow/_source/gen/cover-fist.png`, `four-female-two-male-59/emily-02-v2/_source/gen/lift.png`], portrait. Prompt: redraw the SAME young Korean woman as a black and white manga ink illustration in the exact ink style of the fox reference (clean linework, fine cross hatching, white and grey only, plain pale grey paper, no text), dark brown low ponytail with soft side parted face framing strands, soft features, stud earrings, fitted short sleeve crew neck t-shirt, high waisted full length black leggings, white trainers, no cleavage, full body, one flat coral (#E0453A) muscle highlight with hatching on top, family-friendly fitness guide illustration. It passed the safety filter first try and matched the identity. A batch reference anchor: `Finished-slides/emily-manga-61/_shared/`.
3. Workers reference the anchor + ink anchor + colour identity anchor (+ turnaround for side/back views).

Look: soft blush pink flat field (around RGB 246,218,224) instead of lavender, re-papered with `rebg()`. Anton style headline, black line + deep raspberry/red line measured >= 3:1 on the pink. Colour-coded muscle map on B covers (3 distinct colours, back or 3/4 back view so glutes, delts and back all show). Kitchen bridge is first person: `THE PART EVERYONE SKIPS: WHAT I EAT`, a day of eating with grams, kcal and protein totals computed in code, never a personal weight-loss result. Emily holds a #00FF00 phone (close medium shot), real `noxy-home-real.png` composited, zoomed inset, `search Noxy on the App Store` pill. Canvas 1080x1440: convert the 1080x1620 male kits and retune layouts.
Copy: hourglass topics frame wider shoulders, back and rounder glutes as making the waist LOOK smaller by contrast. No spot reduction (`flat belly`, `lose belly fat`, `shrink your waist`). Inspect form before layout: hip thrusts and wall bridges need hips clearly lifted; Pilates frames must visibly differ and show the wall. For side-lying leg raises, trace which hip owns each leg: the TOP leg must lift, with shoulders and hips stacked. A near bent leg and a far lifted straight leg can depict the wrong movement despite plausible anatomy. Check covers against entry-level copy too; a loaded bridge does not illustrate a bodyweight start.

## Variant D kit (day split, batch 59 male-02)
Renderer with `day` (header cell + 5 exercise cells in a 2x3 grid, auto muscle callouts), `cover` (3-fox MONTH 1 / MONTH 6 / YEAR 1 lineup), `week`, `app`, `cta` kinds: `Finished-slides/four-female-two-male-59/male-02/_source/render.py` + `slides.json`. Lessons:
- Generate ONE panel per exercise (square request, parallel tool_call batch) with the red muscle highlight, then auto-crop the ink and fit into cells. Batch calls run in parallel, about 1 min for 7.
- Muscle callouts: detect the red highlight by hue (g < 0.27r, b < 0.33r) plus opening and largest blobs. A plain r-g threshold also catches dark orange fur shading and the leader lines then point at wrists, ears or shoes.
- Check form per panel at full size: RDL and one-arm row came back barely hinged on the first try; prompt "torso almost parallel to the floor, flat back like a table top".
- A 3-fox progression cover needs "skinny untrained" vs "much bigger" wording, side profile, red only on upper arm and shoulder, or the three look the same.
- Avoid rep ranges with hyphens (no dashes rule): use fixed reps like 3 x 10. Wrap header notes so they never run into the 01 column on the same baseline.
- Incline press first came back as a near upright seat with an overhead press. Fix: pass the flat DB bench press panel as a reference image and prompt "like the flat bench press reference but the backrest raised LOW, about 30 degrees, still mostly lying back, dumbbells above the upper chest". Label it DB BENCH PRESS when the art shows dumbbells.
- 3:4 day grid: end the bottom row at y 1390 (ROW = 30-468, 478-930, 940-1390) so the last cue line clears TikTok's caption overlay. Split long header notes into separate entries rather than leaving a one word orphan.
- Week slide copy must match the table: if Sunday is rest, say WALK 3. REST 1., not JUST WALK.
- App slide: put a white `search Noxy on the App Store` pill (red magnifier, hard drop) right under the real screen inset, keep it clear of the fox's hand and above H-120.

## Variant B kit (muscle by muscle, batch 60 male-01, 9 slides)
Kit: `Finished-slides/four-female-two-male-60/male-01/_source/render.py` + `slides.json` (kinds cover muscle-map / vshape / muscle / kitchen / app / week / closer, 1080x1620 lavender). Lessons:
- Muscle headline in Knewave (OFL brush font, `_source/fonts/`) with a swoosh underline in the muscle's map colour. Cover map colours: side delts blue, lats yellow, arms red; detect by hue and aim each legend leader at the blob on the viewer's left.
- `muscle` rows: text block top left, art placed by silhouette at the largest scale clearing all text and earlier art; row 1 art may rise beside the header. Mirror (`flip`) a panel when the red muscle faces away from open space, so the callout sits beside it instead of crossing the face.
- Callout search must reject leader lines that pass through any text box (a LATS line once crossed the reps).
- image_generate with an image_url returns the anchor's 941x1672 portrait even when square is requested. Local tools take ONE entry per tool_call; issue parallel tool_call invocations instead.
- App phone: "CLOSE MEDIUM SHOT from the waist up ... phone about as tall as his head including the ears" gives a phone big enough for the real screen. Drop the phone to inset pointer line: it crossed the real screen.

## Variant E kit (one move per slide, batch 59 male-01-v2, 12 slides)
Kit: `Finished-slides/four-female-two-male-59/male-01-v2/_source/render.py` (kinds cover / howto / move / app / closer). The user rejected the 3-slide poster as TOO SHORT; this 12-slide version replaced it. Lessons:
- Generate ONE image per exercise holding BOTH frames ("the SAME fox TWICE ... stacked one above the other" in portrait for floor moves, "side by side" in landscape for standing moves) with the red muscle highlight; it keeps the two frames consistent. `split_frames` cuts on the widest empty band.
- Ask for an obvious difference ("The difference between the two drawings must be obvious") and compare frames at phone size. Chair dips need visibly lower hips; superman lifts need visible clearance; mountain climbers read better as plank then knee-in than opposite knees in side view. For scapular pulls, verify visible shoulder depression with straight elbows; labels alone cannot establish motion. If reversed frames illustrate a slower lowering phase, state the tempo and direction explicitly rather than presenting identical art as a new movement. Trace every readiness test back to a trained step or explain the new transition; do not suddenly require an unsupported hang after only feet-supported practice.
- Plank frame 1 "knees down" doubles as the easier version.
- Layout: pack the 2 frames by SILHOUETTE (stacked, diagonal stagger both ways, side by side), take the biggest scale where the foxes don't touch, and fall back to the next arrangement if labels or callout don't fit. Paste each frame with its dilated silhouette as alpha, never the paper rectangle, or a staggered frame cuts the other's feet.
- Frame labels (1 UP / 2 DOWN) must be nearer their own fox than the other (distance transform per frame), or a 2 label floats beside frame 1. Aim the red callout at the red blob centroid, penalise leader lines crossing ink.
- Put reps inline right of the last title line when it fits (saves ~90 px for art); 2-line titles (MOUNTAIN CLIMBERS) at ~124 px.
- vision_analyze refuses a 4th load of the same file: copy preview.jpg to a new scratch name per review round.
- End the cues + EASIER block at about H-215 (`block_top = H - 215 - block_h`), not H-160, because a long TikTok caption covers anything lower.
- Closer: `SAVE THIS. / START MONDAY` over the week table, not `DAY 1`. Do not repeat the red comment prompt in the sub lines.
- Run the kit as `env -u PYTHONPATH -u PYTHONHOME /usr/bin/python3 render.py` (needs scipy; Windows: `C:/Users/<you>/IkkimiAssets/engine/.venv/Scripts/python.exe render.py`). An inherited PYTHONPATH from the agent's own Python makes numpy fail to import.

## Shared kit lessons (from the retired variant A build; reused by E)
Kit: `Finished-slides/four-female-two-male-59/male-01/_source/render.py` (kinds cover / poster / app, 1080x1620). The lavender background, `rebg()`, contrast colours and App Store card below apply to every variant.
- Generate each exercise as its OWN image (anchor `cover-fist.png` as image_url), not a grid. Panels then place art by SILHOUETTE: largest scale whose ink mask clears the label boxes (name row and reps line as separate boxes), so tall poses sit beside short labels. Short names (LUNGES not REVERSE LUNGES) give tall poses more room.
- Put art on white panels by dividing out the generated paper colour (multiply blend): no keying, shadows survive. Redraw labels after pasting the art rectangle.
- Nothing important in the bottom ~70 px of a 2:3 slide: TikTok's caption covers it. Put the rest/frequency tip under the title.
- Green screen: food (broccoli) is green too. Restrict screen detection to a phone region, and only fix spill where the screen mask is below 250, otherwise the real screen's green HP bar turns grey and a green fringe stays.
- "Superman hold, lying face down" with the base prompt was rejected (sexual). A standalone family-friendly prompt ("on his stomach on an exercise mat, arms reaching forward like a flying superhero") passed. Bird dog came back with arm and leg on the same side; check it.
- Medium-shot fox holding a big phone passed when worded "family-friendly cartoon mascot"; a full-body prompt made the phone too small for the real screen.
- Critic fixes (v2): use a flat soft lavender background like the references (`BG = (200,195,240)`), not pale grey. When the fox sits directly on the background, do NOT multiply-repaper the whole art, because that tints fur, cream and white trainers lavender. Use `rebg()` in the male-01 render.py instead. It floods neutral near-paper pixels from the border, adds big enclosed paper gaps, plus a 2px neutral outline band, and multiplies only those pixels. The fox keeps its colour, with 0 grey halos and no seams. Panels on white still use `repaper`.
- Contrast on lavender: brand orange #e87545 is only 1.8:1 and the old red (227,38,43) 2.7:1. Use red (206,24,32) at 3.3:1 and burnt orange (194,64,16) at 3.1:1 for headline text.
- Cover hook: black FULL / HOME / WORKOUT, then a red underlined audience qualifier (`FOR BEGINNERS`), as on the reference covers. If any move uses a chair, say "no gym needed", never "no equipment".
- Slide 3 App Store card: crop the REAL icon from `Screenshot_48f50a.jpg` at (63,218,411,566), round its mask, and typeset "search Noxy / on the App Store" on a white card placed left of the phone. Do not draw a fake Get button. The renderer asserts that no text sits in the bottom 150 px.
- Head room: a per-exercise `clear` px value pads the label mask so the silhouette placer keeps fox heads off the labels.

## Emily manga workout (`emily-manga-workout`, @EmilyF1tness ONLY, new test 2026-10-22)
The fox manga grammar redrawn with Emily's Korean girl, for female-searched topics. Never for Emma (in her `excluded_formats`). Untested until the user reports results. First builds: `Finished-slides/emily-manga-61/` (emily-01 variant B `3 MUSCLES THAT GIVE YOU AN HOURGLASS SHAPE`, 9 slides; emily-02 variant E `WALL PILATES FOR BEGINNERS`, 12 slides; both 1080x1440). Critic 8/10 each.
- **One shared character anchor first.** Before spawning workers, the parent generates `_shared/emily-manga-anchor.png` (front, fist raised) + `_shared/emily-manga-turnaround.png` (front/side/back, pure ink) from `four-female-two-male-60/emily-02/_source/gen/cover-v2.png` + `cover-fist.png` ink anchor. Every worker passes the shared anchor as `image_url` so both posts show the same girl.
- Style: black and white manga ink, colour ONLY on the working muscle; blush pink field around (246,218,224) with `rebg()`; raspberry headline line (~(190,20,60)) for >=3:1 contrast; modest t-shirt + high-waisted leggings. No safety refusals occurred with "family-friendly fitness guide illustration" wording.
- Hourglass topic: frame it as glutes + side delts + back making the waist LOOK smaller by contrast ("same waist. it just LOOKS smaller"), never waist shrinking. Back-view cover map (side delts blue, back teal, glutes red). The red glutes on the cover were flagged as the most body-focused image: ask for a smaller, anatomical glute shape.
- Form traps: one-arm dumbbell row came back with knee and pulling arm on the SAME side and the shin floating; prompt "far-side knee and hand on the bench, shin flat along the bench, near-side foot on the floor, near-side arm pulls". Wall glute bridge needs "feet flat on the wall, hips clearly lifted"; wall sit coral landed on the hamstrings until the prompt said front thighs.
- Generated sizes vary (1024x1536, 1536x1024, 941x1672) even with image_url: fit by silhouette, never assume a fixed size.
- The figure inherits the anchor's curvy proportions; the critic warned about bust/hip exaggeration drawing "AI fan service" comments. Ask for an athletic, natural build in future generations.
- App slide copy: the real screen shows 1,422 kcal and 54 g of 135 g protein. Never headline "how I know I HIT my protein" or a gram target that differs (128 g); use "how I track my protein" and tag the inset "my day so far" when the kitchen day total differs.

## Batch61 fox lessons
- D cover comparison (BRO SPLIT vs PUSH PULL LEGS): generate each fox separately; one two-fox generation coloured the wrong muscles on the second fox. The critic suggested a visibly different physique or mood for the losing side.
- Callout labels must match the red blob (hammer curl was labelled FOREARMS while the red sat on the upper arm). D grid right-column cues fit about 24 characters.
- Phone prompt: ask for a margin on both sides so the arm is not cut at the image edge.
- E kickback: describe the start frame as an "upside down L" (upper arm horizontal against the ribs, forearm vertical) or it reads as a row. One-line titles roughly double the art size. A two-line callout label + `max_scale` cap keeps leader lines off the fox.
- Critic flagged the bigger arms post as borderline for 10k because it lacks a challenge/test device ("do this test", "can't do 1 push up"). Prefer a test or challenge hook line for E posts.
