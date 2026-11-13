# Real SFX layer + benchmark refresh

## Sourcing (free, commercial use, no attribution)
Mixkit free sound effects. Category pages are `https://mixkit.co/free-sound-effects/<cat>/` (some redirect to `/discover/<cat>/`; use `curl -L`). Useful categories: pop, whoosh, swoosh, ding, click, notification, impact, hit, money, game, cartoon, clock, tick, camera-shutter, riser, bubble.

Scrape each item's ID and title with:
- `data-audio-player-preview-url-value="https://assets.mixkit.co/active_storage/sfx/<ID>/` paired with
- `item-grid-card__title` h2 text.

Download with `https://assets.mixkit.co/active_storage/sfx/<ID>/<ID>-preview.mp3`. The `?q=` search pages ignore the query, so use category pages only.

A working palette for comic explainers:
- pop_hard 2364, pop_long 2358
- swoosh_small 166, swoosh_fast 3115, whoosh_air 1489
- hit_short_bass 2299, impact_whoosh_deep 1143
- coin_game 2069, ding_confirm 2867, ding_correct 2870
- tick_fast_clock 1063, click_classic 1117, notif_bubble_pop 2357, notif_positive 951
- fail_low_tone 2876, boing 2894, thud_wood 2182

The Noxy copy lives in `~/NoxyAssets/sfx/mixkit/` with `onsets.json`.

## Alignment
1. Precompute per file (`onsets.json`, cast to float before json.dump):
   - `onset`: the first point where the 5 ms envelope exceeds 10% of the peak.
   - `peak_t`: the time of the maximum.
2. Cue list entry: `{sfx, t, db, align:'onset'|'peak_t', len?}`.
   - Start each file at `t - ref`.
   - Use `peak_t` for whooshes, hits and shutters, so the swell builds into the cut.
   - Use `onset` for pops and dings.
   - `len` truncates long loops (ticks) with an 80 ms fade.
3. Normalise each file to peak 1, then apply `db` plus a global offset of about −15 dB.
4. Generate cues from the shot plan automatically:
   - **Every cut:** an alternating swoosh at −9.
   - **Chapter card:** a whoosh plus bass hit.
   - **Hook flash:** a bass hit plus deep impact.
   - **Food or item pop:** a pop.
   - **Good number:** a coin.
   - **Bad number:** a bass hit plus a short tick.
   - **Stamp:** a wood thud plus bass hit.
   - **App card:** a swoosh plus UI click, then a ding per ring.
   - **CTA:** a notification plus pop.
5. De-duplicate the same sound within 90 ms.

## Mix
ffmpeg `amix=inputs=3:normalize=0` of:
- the voice: loudnorm −14
- the music bed: gain about 0.30, sidechain-ducked by the voice
- the SFX wav

Then run a final loudnorm −14 / TP −1.5.

Verify against loudnormed voice in 100 ms windows. Target a median SFX−voice of about −21 dB, with only about 10% of windows above −10 dB. The loudest hits should fall in voice gaps.

## Benchmark refresh when Instagram is logged out
The Hermes browser can't attach while the user's Chrome holds the profile lock. `web_profile_info` needs login (401). Use instead:
- **Grid:** headless Playwright on the profile URL. The logged-out page still renders the 12 latest grid links (`a[href*="/reel/"]`, `img.alt` holds the date).
- **Reels:** `uvx yt-dlp -o "%(upload_date)s_%(id)s.%(ext)s" --write-info-json https://www.instagram.com/reel/<id>/` works logged-out for public reels. It gives the caption, like_count and comment_count, but view_count is null (hidden likes show as a constant).
- **Analysis:** whisper transcripts, plus 16-frame `tile=8x2` sheets and a few full-res keyframes to read new style moves (e.g. comic halftone promo cards, a yellow "COMMENT 'X'" end card).

For real view counts, use the social-viral-analyzer login flow.