# Hook-to-demo and POV videos (Ikkimi brand account)

The user's chosen promo format: a silent UGC face + hook text (about 2–3 s) → the USER's own iPhone POV of his MacBook playing a famous anime scene with Ikkimi subtitles → hover a word → dictionary card → save → flashcard review → "it's called ikkimi.app 💻". 13–16 s, music + the scene's own line. **Brand/persona account only**, never the edit account (see `cta-marketing.md`).

Working files: builders in `~/IkkimiAssets/edits/hook-demo-01/` (`build_rezero_v4.py` is the approved one, `build_bc.py` is the same with new segments, `caption_renderer.py`, `hooks/`, `pov/sheet.py`). Research: `~/IkkimiAssets/research/hook-demo/` (`scenes_A/B.json`, `ugc_picks.json`) and `~/IkkimiAssets/research/lucy-hooks/`. Raw POV footage: `footage/pov-demo/raw/` (log every clip in CATALOG.md).

## 1. Scene list (what he films)
- **He wants the most viral, LATEST moment of a show.** Example: for Re:Zero he asked for Season 4, not the S1 classic. Check whether a newer season has aired (web search + jimaku entry list) before recommending an old scene. For a long-running show, offer both the iconic classic and the newest viral moment.
- **Verify every line and timestamp** with the `anime-scene-line-verification` skill (jimaku subtitle files). Give, per scene:
  - episode and cue time (about 10 s early)
  - the exact line (JP + EN)
  - the ONE word to hover
  - which service shows JP subs in Indonesia
- **When he names a service** ("give it to me in Netflix"), pull that service's own subtitle file and give its timestamps.
- **If he asks for a specific part of a scene** (e.g. "the confession part"), re-cue to that line and pick the hover word inside it.
- **Indonesia streaming facts (re-check, they change).**
  - Netflix ID has JP subs for: JJK, One Piece, Bleach, Dandadan, CSM, Kaiju 8, Sakamoto Days.
  - It does NOT for: Solo Leveling, Demon Slayer, AoT, Naruto, Black Clover, HxH, Haikyuu. Use Crunchyroll + Jimaku for those.
  - Official YouTube clips rarely have human JP captions. The Fragrant Flower confession `0P1Tg2ovSAM` does.
- **Filming tips to send with every shot list:**
  - Phone close enough that the laptop screen fills the frame (subtitles came out small from far away).
  - Hover exactly the listed word and hold still 2 s.
  - Press L to save, then open Review and film THAT card, so one word runs through the whole video.
  - Filming a screen with a phone sidesteps DRM.
- Put the list in the shot-list folder as `NN-BATCH-x-<shows>.md` and copy it to `edits/hook-demo-01/`.

## 2. Hooks (from the @lucy_japanese analysis; report `research/lucy-hooks/01-HOOK-REPORT.md`)
- **Use only the 3 proven lines, with their EXACT wording and matching face:**
  - `i WISH someone told me about this Japanese app earlier 🥺🇯🇵` + a shocked hand-over-mouth face
  - `Some people still use Duolingo to learn Japanese 🤢` + a cringe/disgust face (highest ceiling)
  - `"I use duolingo to learn japanese" 🤡` + a cringe face or mouthing the quote
- **Rewordings flop.** "…sooner" / "I WISH i found…" hit 0 of 8.
- **Never use:**
  - "how did you learn… in ONE month"
  - wdym / can't-believe
  - how-to / one-year
  - "3 years in chaos… I just find this now"
  - numbers in the hook
  - smirk, eye-roll or bored faces
  - chest-level text
- **Face clips:** `research/hook-demo/ugc_picks.json` (in/out seconds, text band per clip). Place text with `text.y`, not `text.band`.
  - The only strong cringe face is `5d95ad2e` 0.5–1.85 s. Slow it to about 0.62× so it fills about 2.2 s, and cut before the smile/zoom-out at about 1.9 s.
  - Skip clips with a visible chest logo (`a6e2c9e4`, `32bda428`, `be4ee553`).
- **Flag emoji (🇯🇵) and other multi-codepoint emoji:** this PIL has no raqm and draws them blank, so `caption_renderer.emojitile` routes them through the CoreText helper `edits/hook-demo-01/emoji_render` (compiled from `emoji_render.swift`). Burned-in flags now work; verify them on a frame. Mac only: the CoreText helper needs swiftc and these `edits/hook-demo-01/` files are not on the PC. On Windows, draw emoji with PIL `embedded_color=True` and Segoe UI Emoji (`seguiemj.ttf`) or paste a Twemoji PNG, and verify on a frame.

## 3. Edit (one serial builder; about 15 min per video)
1. **Copy the raw clip and tone-map it:**
   - Copy the raw `.MOV` to `footage/pov-demo/raw/`.
   - iPhone clips are 4K **HLG HDR** (bt2020/arib-std-b67), and a plain ffmpeg decode looks washed out. Tone-map with `avconvert -s <in> -p Preset1920x1080 -o <abs out> --replace`. It needs an absolute output path or it silently writes nothing.
2. **Find beats from the subtitle frames, not whisper.**
   - Make a contact sheet: `pov/sheet.py <clip> <fps> <out.jpg>` (PIL labels; the ffmpeg here has no drawtext).
   - Crop the subtitle band at several times and read it. Whisper timestamps on phone-recorded audio are coarse (1–2 s off), so set the scene in/out from when the subtitle line shows.
3. **Build the segments** (copy the latest builder and edit `SEG`):
   - hook → scene (about 3.5–6 s, ends on the payoff line) → hover (cards, ~1.15× speed) → cards (review) → end (landing page).
   - Captions are white rounded boxes, one per beat:
     - "you literally learn by watching anime 🤯" over the keyboard (y ≈ 1560) so it never covers the Ikkimi subtitle
     - "hover any word → instant meaning 👀" top
     - "and it turns them into flashcards 😭" top
     - "it's called ikkimi.app 💻" (the domain, double k)
4. **Camera:**
   - **No slow continuous push-ins** (the user calls them unnecessary zoom).
   - Hold wide and static, then do ONE short **speed-ramped punch-in** (ease-in-out quint over 0.4–0.5 s, 1.0→1.3/1.45) timed to the payoff word or the card appearing.
   - Use `zoompan` with an `on`-based expression, because crop's w/h are only evaluated once.
5. **Grade:**
   - Every POV segment: `eq=contrast=1.15:saturation=1.22:gamma=0.97` + S-curve `curves=all='0/0 0.25/0.2 0.5/0.5 0.75/0.8 1/1'` + `vibrance=0.1` + light unsharp.
   - The hook gets a lighter version.
   - No teal/orange + vignette (it looked dim and dirty).
6. **Audio:**
   - Use *worry (Instrumental Slowed)* (`~/Desktop/CONTENt ASSET/MUSIC 2/LONOWN_riserayss_-_worry_slowed.mp3`). Its first big hit is at 21.83 s; place it on the hook→POV cut.
   - Duck the music to 0.16 under the scene, where the phone-recorded scene line plays (highpass 90, gain ≈3.4).
   - loudnorm -14 LUFS / TP -1.5. Also render a NO_MUSIC twin.
7. **QA:**
   - Full decode and ebur128.
   - Run whisper on the scene window of the FINAL mix to prove the line is audible.
   - Make a 3 fps review sheet, plus full-res grabs of each caption/card frame.

## 4. Deliver
`~/Desktop/Ikkimi/Ikkimi-<date>-<show>-hook-demo[-vN]/`:
- `01-<show>.mp4` (music)
- `02-…_NO_MUSIC.mp4`
- `03-review-sheet.jpg`
- `04-edit-manifest.json`
- `POSTING-NOTES.md`: timeline, which file to post, the in-app sound start (≈0:19), and a caption ending with `it's called ikkimi.app (works in Chrome on your laptop 💻)` + `Comment "ANIME"…`
- `_preview.html`

Then the tested ZIP, MEDIA cards, the file tree and Finder. On revisions, make a new `-vN` folder and keep unchanged sections bit-identical (check framemd5 of the untouched span).

## "POV: learning Japanese" variant
Like hook-to-demo, but the scene is the main content: a 15–25 s run of the scene with Ikkimi subs and 1–2 quick hovers inside it, and no full save→flashcard tour. Pick scenes with several spoken lines in one continuous stretch (e.g. Naruto Pain 162 14:06–14:28, Rengoku, Erwin's speech, One Piece 278, the Fragrant Flower ep12 confession, the Re:Zero S4 ep13 "立ちなさい").
